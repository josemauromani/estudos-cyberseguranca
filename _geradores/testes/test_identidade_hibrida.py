#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_identidade_hibrida.py
Testes automatizados para o Estudo 41: Identidade-Hibrida-e-Nuvem
"""

import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402

INTERATIVOS = {"mfa", "mfa_resistente"}


def satisfaz(req, t):
    if req == "dispositivo_conforme":
        return t["dispositivo_conforme"]
    if t["cliente"] == "legado":
        return False
    if req == "mfa":
        return any(m in t["metodos"] for m in ("app", "fido2", "sms"))
    if req == "mfa_resistente":
        return "fido2" in t["metodos"]
    raise ValueError(req)


def aplica(d, p, t):
    u = d["usuarios"][t["usuario"]]
    marcas = set(u["grupos"]) | {t["usuario"]}
    inc, exc = p["usuarios"]["incluir"], p["usuarios"]["excluir"]
    if not ("todos" in inc or marcas & set(inc)):
        return False
    if marcas & set(exc):
        return False
    if "todas" not in p["apps"] and t["app"] not in p["apps"]:
        return False
    c = p["condicoes"]
    if c["local"] == "fora_confiavel" and t["local"] == "confiavel":
        return False
    for chave, campo in (("risco", "risco"), ("plataformas", "plataforma"), ("clientes", "cliente")):
        if c[chave] and t[campo] not in c[chave]:
            return False
    return True


def efeito(p, t):
    """Resultado de uma política sozinha: bloqueado, mfa_resistente, mfa ou concedido."""
    ctl = p["controle"]
    if ctl["tipo"] == "bloquear":
        return "bloqueado"
    reqs = ctl["requisitos"]
    ok = [r for r in reqs if satisfaz(r, t)]
    if ctl["operador"] == "todos":
        if len(ok) != len(reqs):
            return "bloqueado"
        return "mfa_resistente" if "mfa_resistente" in reqs else "mfa" if "mfa" in reqs else "concedido"
    # "um dos controles": o que não pede interação vence; depois o MFA mais simples disponível
    if any(r not in INTERATIVOS for r in ok):
        return "concedido"
    if "mfa" in ok:
        return "mfa"
    if "mfa_resistente" in ok:
        return "mfa_resistente"
    return "bloqueado"


ORDEM = ["concedido", "mfa", "mfa_resistente", "bloqueado"]


def avaliar(d, politicas, t):
    ativas = [p for p in politicas if p["estado"] == "ativa" and aplica(d, p, t)]
    relat = [[p["id"], efeito(p, t)] for p in politicas if p["estado"] == "relatorio" and aplica(d, p, t)]
    res = "concedido"
    decisivas = []
    for p in ativas:
        e = efeito(p, t)
        if ORDEM.index(e) > ORDEM.index(res):
            res, decisivas = e, [p["id"]]
        elif e == res and e != "concedido":
            decisivas.append(p["id"])
    return {"resultado": res, "aplicadas": [p["id"] for p in ativas], "decisivas": decisivas, "relatorio": relat}


def politicas_corrigidas(d):
    ps = json.loads(json.dumps(d["politicas"]))
    for p in ps:
        for k, v in d["correcao"].get(p["id"], {}).items():
            if k == "excluir":
                p["usuarios"]["excluir"] = v
            else:
                p[k] = v
    return ps


class TestIdentidadeHibrida(unittest.TestCase):
    """Valida a estrutura, o conteúdo, o avaliador de acesso condicional e a compilação do estudo 41."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "identidade_hibrida_e_nuvem_body.html"
        self.compiled_path = self.root / "Identidade-Hibrida-e-Nuvem" / "treinamento-identidade-hibrida-e-nuvem.html"
        self.portal_path = self.root / "index.html"

    def _dados(self):
        body = self.body_path.read_text(encoding="utf-8")
        m = re.search(r'<script type="application/json" id="ca-dados">(.*?)</script>', body, re.S)
        self.assertIsNotNone(m, "Bloco JSON #ca-dados ausente no body")
        return json.loads(m.group(1))

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        termos = [
            "Entra Connect", "PHS", "PTA", "federação", "AD FS", "acesso condicional", "atribuições", "condições",
            "controles", "somente relatório", "conta de emergência", "dispositivo em conformidade", "risco de entrada",
            "FIDO2", "passkey", "number matching", "PIM", "password spraying", "consent phishing", "OAuth",
            "autenticação legada", "T1110.003", "T1528", "T1539", "Tier 0", "Estudo 40", "Estudo 39",
        ]
        for termo in termos:
            self.assertIn(termo, content, f"Termo obrigatório ausente: {termo}")

    def test_dados_validos(self):
        d = self._dados()
        grupos = {g for u in d["usuarios"].values() for g in u["grupos"]}
        apps = set(d["apps"])
        for p in d["politicas"]:
            with self.subTest(politica=p["id"]):
                self.assertIn(p["estado"], ("ativa", "relatorio", "desativada"))
                for g in p["usuarios"]["incluir"] + p["usuarios"]["excluir"]:
                    self.assertTrue(g == "todos" or g in grupos or g in d["usuarios"], g)
                self.assertTrue(p["apps"] == ["todas"] or set(p["apps"]) <= apps)
                self.assertIn(p["controle"]["tipo"], ("bloquear", "conceder"))
                if p["controle"]["tipo"] == "conceder":
                    self.assertTrue(p["controle"]["requisitos"])
        for t in d["tentativas"]:
            with self.subTest(tentativa=t["id"]):
                self.assertIn(t["usuario"], d["usuarios"])
                self.assertIn(t["app"], apps)
                self.assertTrue(re.fullmatch(r"(10\.\d+\.\d+\.\d+|192\.0\.2\.\d+|198\.51\.100\.\d+|203\.0\.113\.\d+)", t["ip"]))

    def test_estado_inicial_tem_as_falhas(self):
        d = self._dados()
        r = {t["id"]: avaliar(d, d["politicas"], t) for t in d["tentativas"]}
        for t in d["tentativas"]:
            with self.subTest(tentativa=t["id"]):
                self.assertEqual(r[t["id"]]["resultado"], t["esperado_inicial"])
        self.assertEqual(r["t2"]["resultado"], "concedido", "o spraying por IMAP passa sem MFA")
        self.assertEqual(r["t8"]["resultado"], "bloqueado", "a conta de emergência fica trancada")
        self.assertTrue(any(x[0] == "P3" and x[1] == "bloqueado" for x in r["t3"]["relatorio"]),
                        "o modo somente relatório mostra o efeito antes de ativar")

    def test_estado_corrigido(self):
        d = self._dados()
        ps = politicas_corrigidas(d)
        r = {t["id"]: avaliar(d, ps, t) for t in d["tentativas"]}
        for t in d["tentativas"]:
            with self.subTest(tentativa=t["id"]):
                self.assertEqual(r[t["id"]]["resultado"], t["esperado_corrigido"])
        self.assertEqual(r["t4"]["resultado"], "mfa_resistente")
        self.assertNotEqual(r["t8"]["resultado"], "bloqueado")
        self.assertTrue({"mfa", "mfa_resistente", "bloqueado"} <= {r[x]["resultado"] for x in r})

    def test_bloquear_vence(self):
        d = self._dados()
        t = dict(d["tentativas"][0])
        base = {"usuarios": {"incluir": ["todos"], "excluir": []}, "apps": ["todas"],
                "condicoes": {"local": "qualquer", "risco": [], "plataformas": [], "clientes": []}, "estado": "ativa"}
        mfa = dict(base, id="X1", controle={"tipo": "conceder", "requisitos": ["mfa"], "operador": "todos"})
        blq = dict(base, id="X2", controle={"tipo": "bloquear", "requisitos": [], "operador": "todos"})
        self.assertEqual(avaliar(d, [mfa, blq], t)["resultado"], "bloqueado")
        self.assertEqual(avaliar(d, [mfa], t)["resultado"], "mfa")
        self.assertEqual(avaliar(d, [], t)["resultado"], "concedido", "sem política aplicável, só a senha")
        um = dict(base, id="X3", controle={"tipo": "conceder", "requisitos": ["mfa", "dispositivo_conforme"], "operador": "um"})
        t2 = dict(t, dispositivo_conforme=True)
        self.assertEqual(avaliar(d, [um], t2)["resultado"], "concedido", "dispositivo conforme dispensa o MFA no 'um'")

    def test_simulador_estrutura(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        for marcador in ("ca-lab", 'id="ca-dados"', "ca-missoes", "ca-politicas", "ca-editor", "ca-tentativas",
                         "avaliarAcessoCondicional", "alterarPoliticaAcesso", "criarPoliticaAcesso", "restaurarAcesso"):
            self.assertIn(marcador, content, marcador)
        ini = content.index("var CA = JSON.parse")
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
        self.assertIn('initChecklist("identidade-hibrida")', content)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn("Identidade-Hibrida-e-Nuvem/treinamento-identidade-hibrida-e-nuvem.html", content)
        self.assertIn('data-slug="Identidade-Hibrida-e-Nuvem"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)


if __name__ == "__main__":
    unittest.main()
