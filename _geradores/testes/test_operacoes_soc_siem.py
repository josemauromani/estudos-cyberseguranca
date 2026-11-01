#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_operacoes_soc_siem.py
Testes automatizados para o Estudo 16: Operacoes-SOC-e-SIEM

As regras Sigma ficam no JSON do módulo como objetos (o simulador gera o YAML
para edição). Este teste avalia essas regras em Python, com o mesmo subconjunto
do JavaScript, para validar os eventos, os alertas esperados e as missões.
"""

import copy
import fnmatch
import ipaddress
import json
import re
import sys
import unittest
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402

MODIFICADORES = {"contains", "startswith", "endswith", "all"}


# ------------------------------------------------------------- avaliador Sigma
def campo(evento, nome):
    for k, v in evento["campos"].items():
        if k.lower() == nome.lower():
            return v
    return None


def casa_valor(valor_evento, esperado, mods):
    if valor_evento is None:
        return False
    a = str(valor_evento).lower()
    b = str(esperado).lower()
    if "contains" in mods:
        return b in a
    if "startswith" in mods:
        return a.startswith(b)
    if "endswith" in mods:
        return a.endswith(b)
    return fnmatch.fnmatchcase(a, b) if "*" in b or "?" in b else a == b


def casa_selecao(evento, selecao):
    for chave, esperado in selecao.items():
        nome, *mods = chave.split("|")
        assert set(mods) <= MODIFICADORES, mods
        valores = esperado if isinstance(esperado, list) else [esperado]
        testes = [casa_valor(campo(evento, nome), v, mods) for v in valores]
        if not (all(testes) if "all" in mods else any(testes)):
            return False
    return True


def avaliar_condicao(cond, resultados):
    tokens = re.findall(r"\(|\)|[^\s()]+", cond)
    pos = [0]

    def ver():
        return tokens[pos[0]].lower() if pos[0] < len(tokens) else None

    def pegar():
        t = tokens[pos[0]]
        pos[0] += 1
        return t

    def expr_or():
        v = expr_and()
        while ver() == "or":
            pegar()
            v = expr_and() or v
        return v

    def expr_and():
        v = expr_not()
        while ver() == "and":
            pegar()
            v = expr_not() and v
        return v

    def expr_not():
        if ver() == "not":
            pegar()
            return not expr_not()
        return primario()

    def primario():
        t = pegar()
        if t == "(":
            v = expr_or()
            assert pegar() == ")"
            return v
        if t.lower() in ("1", "all") and ver() == "of":
            pegar()
            alvo = pegar()
            nomes = list(resultados) if alvo == "them" else [n for n in resultados if fnmatch.fnmatchcase(n, alvo)]
            assert nomes, alvo
            vals = [resultados[n] for n in nomes]
            return any(vals) if t == "1" else all(vals)
        return resultados[t]

    v = expr_or()
    assert pos[0] == len(tokens), cond
    return v


def regra_casa(regra, evento):
    for k, v in regra["logsource"].items():
        if evento["logsource"].get(k) != v:
            return False
    det = regra["deteccao"]
    resultados = {nome: casa_selecao(evento, sel) for nome, sel in det.items() if nome != "condition"}
    return avaliar_condicao(det["condition"], resultados)


def disparos(d, regra):
    return [e["id"] for e in d["eventos"] if regra_casa(regra, e)]


class TestOperacoesSocSiem(unittest.TestCase):
    """Valida a estrutura, o conteúdo, os eventos, as regras e a compilação do estudo Operacoes-SOC-e-SIEM."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "operacoes_soc_e_siem_body.html"
        self.compiled_path = self.root / "Operacoes-SOC-e-SIEM" / "treinamento-operacoes-soc-e-siem.html"
        self.portal_path = self.root / "index.html"

    def _dados(self):
        body = self.body_path.read_text(encoding="utf-8")
        m = re.search(r'<script type="application/json" id="soc-dados">(.*?)</script>', body, re.S)
        self.assertIsNotNone(m, "Bloco JSON #soc-dados ausente no body")
        return json.loads(m.group(1))

    def _regra(self, d, rid):
        return next(r for r in d["regras"] if r["id"] == rid)

    def _evento(self, d, eid):
        return next(e for e in d["eventos"] if e["id"] == eid)

    # ----------------------------------------------------------------- arquivos
    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        termos = [
            "N1", "N2", "N3", "MTTD", "MTTA", "MTTR", "falso positivo", "falso negativo",
            "ECS", "CEF", "LEEF", "OCSF", "normalização", "enriquecimento", "correlação", "retenção",
            "4624", "4625", "4688", "4720", "4732", "1102", "Sysmon", "LogonType",
            "Sigma", "logsource", "detection", "condition", "falsepositives", "pySigma", "sigma-cli",
            "Kibana Query Language", "Kusto Query Language", "SPL",
            "T1110", "T1078", "T1059.001", "T1136.001", "T1098", "T1070.001", "10.4.1.1",
        ]
        for termo in termos:
            self.assertIn(termo, content, f"Termo obrigatório ausente: {termo}")

    # -------------------------------------------------------------------- dados
    def test_eventos_validos(self):
        d = self._dados()
        eventos = d["eventos"]
        self.assertGreaterEqual(len(eventos), 40)
        ids = [e["id"] for e in eventos]
        self.assertEqual(len(ids), len(set(ids)))
        tss = [e["ts"] for e in eventos]
        self.assertEqual(tss, sorted(tss), "eventos devem estar em ordem cronológica")
        for e in eventos:
            with self.subTest(evento=e["id"]):
                self.assertRegex(e["ts"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$")
                self.assertIn("Computer", e["campos"])
                self.assertIn("EventID", e["campos"])
                self.assertIsInstance(e["malicioso"], bool)
                ip = campo(e, "IpAddress")
                if ip and ip != "-":
                    end = ipaddress.ip_address(ip)
                    doc = any(end in ipaddress.ip_network(r) for r in ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24"))
                    self.assertTrue(end.is_private or doc, f"IP real no dataset: {ip}")
        self.assertTrue(any(e["malicioso"] for e in eventos))
        self.assertTrue(any(not e["malicioso"] for e in eventos))

    def test_regras_padrao_disparam_onde_esperado(self):
        d = self._dados()
        for r in d["regras"]:
            with self.subTest(regra=r["id"]):
                self.assertTrue(r["titulo"].strip())
                self.assertIn(r["nivel"], ("informational", "low", "medium", "high", "critical"))
                self.assertIn("condition", r["deteccao"])
                self.assertEqual(sorted(disparos(d, r)), sorted(r["esperado"]))
                self.assertTrue(r["esperado"], "toda regra padrão deve disparar ao menos uma vez")

    def test_regra_ruidosa_e_ajuste_da_missao(self):
        d = self._dados()
        ruidosa = self._regra(d, d["missoes"]["regra_ruidosa"])
        hits = [self._evento(d, i) for i in disparos(d, ruidosa)]
        self.assertEqual(sum(1 for e in hits if not e["malicioso"]), 1, "a regra ruidosa tem 1 falso positivo")
        self.assertEqual(sum(1 for e in hits if e["malicioso"]), 1)
        ajustada = copy.deepcopy(ruidosa)
        ajustada["deteccao"] = d["missoes"]["solucao_deteccao"]
        hits_aj = [self._evento(d, i) for i in disparos(d, ajustada)]
        self.assertEqual([e["malicioso"] for e in hits_aj], [True])

    def test_respostas_das_missoes_derivam_dos_dados(self):
        d = self._dados()
        falhas = Counter(campo(e, "IpAddress") for e in d["eventos"] if campo(e, "EventID") == 4625)
        ip, n = falhas.most_common(1)[0]
        self.assertGreaterEqual(n, 20)
        self.assertEqual(d["missoes"]["ip"], ip)
        sucesso = [e for e in d["eventos"] if campo(e, "EventID") == 4624 and campo(e, "IpAddress") == ip]
        self.assertEqual(len(sucesso), 1)
        self.assertEqual(d["missoes"]["conta"], campo(sucesso[0], "TargetUserName"))

    def test_todo_evento_alertado_tem_nota_e_ha_atraso_de_deteccao(self):
        d = self._dados()
        alertados = {i for r in d["regras"] for i in disparos(d, r)}
        for i in alertados:
            self.assertTrue(self._evento(d, i).get("nota", "").strip(), f"evento {i} alerta e precisa de nota")
        primeiro_malicioso = min(e["ts"] for e in d["eventos"] if e["malicioso"])
        primeiro_alerta = min(self._evento(d, i)["ts"] for i in alertados if self._evento(d, i)["malicioso"])
        self.assertLess(primeiro_malicioso, primeiro_alerta, "a força bruta deve passar sem alerta (gancho do MTTD)")

    # ---------------------------------------------------------------- compilado
    def test_simulador_estrutura(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        for marcador in ("soc-lab", 'id="soc-dados"', "soc-busca", "soc-resultados", "soc-regras", "soc-fluxo",
                         "soc-alertas", "soc-missoes", "executarBuscaSoc", "aplicarRegraSigma",
                         "reproduzirFluxoSoc", "pausarFluxoSoc", "triarAlertaSoc", "verificarMissaoSoc", "restaurarSoc"):
            self.assertIn(marcador, content, marcador)
        ini = content.index("var SOC = JSON.parse")
        motor = content[ini:content.index("</script>", ini)]
        self.assertNotIn("innerHTML", motor)

    def test_componentes_pedagogicos(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        self.assertIn('class="callout', content)
        self.assertIn('class="terminal-box', content)
        self.assertIn('class="diagram-svg-wrap', content)
        self.assertNotIn('<pre class="mermaid"', content)
        self.assertEqual(content.count('class="checklist-item"'), 7)
        self.assertGreaterEqual(content.count('class="quiz-item"'), 6)
        self.assertIn('class="facts-grid', content)
        self.assertIn('initChecklist("operacoes-soc-siem")', content)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn("Operacoes-SOC-e-SIEM/treinamento-operacoes-soc-e-siem.html", content)
        self.assertIn('data-slug="Operacoes-SOC-e-SIEM"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)


if __name__ == "__main__":
    unittest.main()
