#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_seguranca_nuvem.py
Testes automatizados para o Estudo 21: Seguranca-em-Nuvem
"""

import ipaddress
import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402

CONTA = "111122223333"


def lista(v):
    return v if isinstance(v, list) else [v]


def curinga(padrao, valor, sem_caixa=False):
    rx = "^" + "".join(".*" if c == "*" else "." if c == "?" else re.escape(c) for c in padrao) + "$"
    return re.match(rx, valor, re.S | (re.I if sem_caixa else 0)) is not None


def condicao_ok(cond, ctx):
    for op, pares in (cond or {}).items():
        for chave, valores in pares.items():
            vals = [str(v) for v in lista(valores)]
            presente = chave in ctx
            negado = op in ("StringNotEquals", "NotIpAddress")
            if not presente:
                if not negado:
                    return False
                continue
            atual = str(ctx[chave])
            if op == "StringEquals" or op == "Bool":
                ok = atual.lower() in [v.lower() for v in vals] if op == "Bool" else atual in vals
            elif op == "StringNotEquals":
                ok = atual not in vals
            elif op == "StringLike":
                ok = any(curinga(v, atual) for v in vals)
            elif op in ("IpAddress", "NotIpAddress"):
                dentro = any(ipaddress.ip_address(atual) in ipaddress.ip_network(v, strict=False) for v in vals)
                ok = dentro if op == "IpAddress" else not dentro
            else:
                raise ValueError(op)
            if not ok:
                return False
    return True


def casa_acao(st, acao):
    if "Action" in st:
        return any(curinga(a, acao, True) for a in lista(st["Action"]))
    return not any(curinga(a, acao, True) for a in lista(st["NotAction"]))


def casa_recurso(st, recurso):
    if "Resource" in st:
        return any(curinga(r, recurso) for r in lista(st["Resource"]))
    return not any(curinga(r, recurso) for r in lista(st["NotResource"]))


def casa_principal(st, quem):
    p = st.get("Principal")
    if p == "*":
        return True
    alvos = lista(p.get("AWS", [])) if isinstance(p, dict) else []
    for a in alvos:
        if a == "*":
            return True
        if quem != "anonimo" and (a == quem or a == f"arn:aws:iam::{CONTA}:root" and quem.startswith(f"arn:aws:iam::{CONTA}:")):
            return True
    return False


def publico(st):
    p = st.get("Principal")
    return p == "*" or (isinstance(p, dict) and "*" in lista(p.get("AWS", [])))


def bucket_de(recurso):
    return recurso.split(":::", 1)[1].split("/", 1)[0]


def avaliar(d, politicas, bpa, req):
    """Mesma conta: negação explícita > permissão (identidade ou recurso) > negação implícita."""
    ctx = req["contexto"]
    quem = req["principal"]
    cands = []
    if quem != "anonimo":
        papel = quem.split("/")[-1]
        for i, st in enumerate(politicas.get("identidade:" + papel, {"Statement": []})["Statement"]):
            cands.append(("identidade:" + papel, i, st))
    b = bucket_de(req["recurso"])
    for i, st in enumerate(politicas.get("bucket:" + b, {"Statement": []})["Statement"]):
        if not casa_principal(st, quem):
            continue
        if st["Effect"] == "Allow" and publico(st) and bpa.get(b) and quem == "anonimo":
            continue  # RestrictPublicBuckets: permissão pública ignorada para quem é de fora
        cands.append(("bucket:" + b, i, st))
    aplic = [(o, i, st) for o, i, st in cands
             if casa_acao(st, req["acao"]) and casa_recurso(st, req["recurso"]) and condicao_ok(st.get("Condition"), ctx)]
    negs = [(o, i) for o, i, st in aplic if st["Effect"] == "Deny"]
    if negs:
        return {"decisao": "negado_explicito", "por": [f"{o}#{i}" for o, i in negs]}
    perms = [(o, i) for o, i, st in aplic if st["Effect"] == "Allow"]
    if perms:
        return {"decisao": "permitido", "por": [f"{o}#{i}" for o, i in perms]}
    return {"decisao": "negado_implicito", "por": []}


def auditar(d, nome, politica):
    meta = d["buckets"].get(nome.split(":", 1)[1], {}) if nome.startswith("bucket:") else {}
    achados = []
    tem_tls = False
    for i, st in enumerate(politica["Statement"]):
        acoes = [a.lower() for a in lista(st.get("Action", []))]
        if st["Effect"] == "Deny" and st.get("Condition", {}).get("Bool", {}).get("aws:SecureTransport") in ("false", False):
            tem_tls = True
        if st["Effect"] != "Allow":
            continue
        if nome.startswith("bucket:") and publico(st) and not st.get("Condition"):
            achados.append([i, "publico", "info" if meta.get("publico_intencional") and all(a == "s3:getobject" for a in acoes) else "alta"])
        if "*" in acoes or any(a.endswith(":*") for a in acoes):
            achados.append([i, "acao_curinga", "alta"])
        if "Resource" in st and "*" in lista(st["Resource"]):
            achados.append([i, "recurso_curinga", "media"])
        if "NotAction" in st or "NotResource" in st:
            achados.append([i, "negacao_invertida", "media"])
        if "iam:passrole" in acoes and "*" in lista(st.get("Resource", [])):
            achados.append([i, "passrole_curinga", "alta"])
    if nome.startswith("bucket:") and not tem_tls:
        achados.append([None, "sem_tls", "media"])
    return achados


class TestSegurancaNuvem(unittest.TestCase):
    """Valida a estrutura, o conteúdo, o avaliador de políticas e a compilação do estudo Seguranca-em-Nuvem."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "seguranca_em_nuvem_body.html"
        self.compiled_path = self.root / "Seguranca-em-Nuvem" / "treinamento-seguranca-em-nuvem.html"
        self.portal_path = self.root / "index.html"

    def _dados(self):
        body = self.body_path.read_text(encoding="utf-8")
        m = re.search(r'<script type="application/json" id="nv-dados">(.*?)</script>', body, re.S)
        self.assertIsNotNone(m, "Bloco JSON #nv-dados ausente no body")
        return json.loads(m.group(1))

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        termos = [
            "responsabilidade compartilhada", "IaaS", "PaaS", "SaaS", "AWS", "Azure", "GCP", "Effect", "Principal",
            "Action", "Resource", "Condition", "negação explícita", "negação implícita", "Block Public Access",
            "aws:SecureTransport", "IMDSv2", "SSRF", "169.254.169.254", "http-tokens required", "Capital One",
            "CSPM", "CWPP", "CNAPP", "CIS", "Access Analyzer", "mínimo privilégio", "Estudo 12",
        ]
        for termo in termos:
            self.assertIn(termo, content, f"Termo obrigatório ausente: {termo}")

    def test_motor_basico(self):
        self.assertTrue(curinga("s3:Get*", "s3:getobject", True))
        self.assertFalse(curinga("s3:Get*", "s3:getobject"))
        self.assertTrue(curinga("arn:aws:s3:::b/*", "arn:aws:s3:::b/2026/nf.pdf"))
        self.assertFalse(curinga("arn:aws:s3:::b/*", "arn:aws:s3:::b"))
        self.assertTrue(condicao_ok({"StringNotEquals": {"aws:SourceVpce": "vpce-1"}}, {}), "negada com chave ausente é verdadeira")
        self.assertFalse(condicao_ok({"Bool": {"aws:MultiFactorAuthPresent": "true"}}, {}))
        self.assertTrue(condicao_ok({"IpAddress": {"aws:SourceIp": "203.0.113.0/24"}}, {"aws:SourceIp": "203.0.113.9"}))

    def test_dados_validos(self):
        d = self._dados()
        self.assertTrue(d["conta"] == CONTA)
        for nome, pol in list(d["politicas"].items()) + list(d["corrigidas"].items()):
            with self.subTest(politica=nome):
                self.assertEqual(pol["Version"], "2012-10-17")
                for st in pol["Statement"]:
                    self.assertIn(st["Effect"], ("Allow", "Deny"))
                    self.assertTrue(("Action" in st) != ("NotAction" in st))
                    self.assertTrue(("Resource" in st) != ("NotResource" in st))
                    if nome.startswith("bucket:"):
                        self.assertIn("Principal", st)
        for r in d["requisicoes"]:
            ip = r["contexto"].get("aws:SourceIp")
            if ip:
                self.assertTrue(re.fullmatch(r"(10\.\d+\.\d+\.\d+|192\.0\.2\.\d+|198\.51\.100\.\d+|203\.0\.113\.\d+)", ip), ip)

    def test_estado_inicial(self):
        d = self._dados()
        for r in d["requisicoes"]:
            with self.subTest(req=r["id"]):
                self.assertEqual(avaliar(d, d["politicas"], d["bpa_inicial"], r)["decisao"], r["esperado_inicial"])
        notas = auditar(d, "bucket:ipestore-notas-fiscais", d["politicas"]["bucket:ipestore-notas-fiscais"])
        self.assertIn("alta", [a[2] for a in notas], "bucket de notas público por engano")
        app = auditar(d, "identidade:app-loja", d["politicas"]["identidade:app-loja"])
        self.assertTrue({"acao_curinga", "recurso_curinga"} <= {a[1] for a in app})
        imgs = auditar(d, "bucket:ipestore-imagens-produtos", d["politicas"]["bucket:ipestore-imagens-produtos"])
        self.assertIn(["info"], [[a[2]] for a in imgs if a[1] == "publico"], "público de propósito vira informação")

    def test_estado_corrigido(self):
        d = self._dados()
        for r in d["requisicoes"]:
            with self.subTest(req=r["id"]):
                self.assertEqual(avaliar(d, d["corrigidas"], d["bpa_inicial"], r)["decisao"], r["esperado_corrigido"])
        for nome, pol in d["corrigidas"].items():
            self.assertNotIn("alta", [a[2] for a in auditar(d, nome, pol)], nome)
        # Alternativa válida para o bucket de notas: ligar o Block Public Access só nele
        bpa = dict(d["bpa_inicial"], **{"ipestore-notas-fiscais": True})
        r1 = next(r for r in d["requisicoes"] if r["id"] == "r1")
        r2 = next(r for r in d["requisicoes"] if r["id"] == "r2")
        self.assertEqual(avaliar(d, d["politicas"], bpa, r1)["decisao"], "negado_implicito")
        self.assertEqual(avaliar(d, d["politicas"], bpa, r2)["decisao"], "permitido")

    def test_simulador_estrutura(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        for marcador in ("nv-lab", 'id="nv-dados"', "nv-missoes", "nv-buckets", "nv-editor", "nv-auditoria",
                         "nv-requisicoes", "aplicarPoliticaNuvem", "alternarBpaNuvem", "restaurarNuvem"):
            self.assertIn(marcador, content, marcador)
        ini = content.index("var NV = JSON.parse")
        motor = content[ini:content.index("</script>", ini)]
        self.assertNotIn("innerHTML", motor)
        self.assertNotIn("eval(", motor)

    def test_componentes_pedagogicos(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        self.assertIn('class="callout', content)
        self.assertIn('class="terminal-box', content)
        self.assertIn('class="diagram-svg-wrap', content)
        self.assertNotIn('<pre class="mermaid"', content)
        self.assertEqual(content.count('class="checklist-item"'), 7)
        self.assertGreaterEqual(content.count('class="quiz-item"'), 6)
        self.assertIn('class="facts-grid', content)
        self.assertIn('initChecklist("seguranca-nuvem")', content)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn("Seguranca-em-Nuvem/treinamento-seguranca-em-nuvem.html", content)
        self.assertIn('data-slug="Seguranca-em-Nuvem"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)


if __name__ == "__main__":
    unittest.main()
