#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_ataques_ad.py
Testes automatizados para o Estudo 39: Ataques-e-Defesa-no-AD
"""

import itertools
import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402

GUID_GET_CHANGES = "1131f6aa-9c07-11d1-f79f-00c04fc2dcd2"
GUID_GET_CHANGES_ALL = "1131f6ad-9c07-11d1-f79f-00c04fc2dcd2"
TECNICAS = {"T1558.003", "T1550.002", "T1003.006"}
RESPOSTAS = {"kerberoasting", "pth", "dcsync", "normal"}
OFENSIVOS = ["Invoke-Kerberoast", "sekurlsa::", "lsadump::", "Rubeus.exe", "secretsdump", "GetUserSPNs", "Invoke-Mimikatz"]


def caminhos(d, removidas=frozenset()):
    """Todos os caminhos simples (listas de ids de arestas) do início até o alvo."""
    saidas = {}
    for a in d["arestas"]:
        if a["id"] not in removidas:
            saidas.setdefault(a["de"], []).append(a)
    achados = []

    def dfs(no, visitados, trilha):
        if no == d["alvo"]:
            achados.append(list(trilha))
            return
        for a in saidas.get(no, []):
            if a["para"] not in visitados:
                dfs(a["para"], visitados | {a["para"]}, trilha + [a["id"]])

    dfs(d["inicio"], {d["inicio"]}, [])
    return achados


def removidas_por(d, ids):
    mit = {m["id"]: m for m in d["mitigacoes"]}
    return frozenset(a for i in ids for a in mit[i]["remove"])


def classificar(ev, dcs):
    """Regras de campo que o aluno deve aprender (espelham as explicações)."""
    c = ev["campos"]
    if ev["evento"] == 4769:
        servico = c["ServiceName"]
        if c["TicketEncryptionType"] == "0x17" and not servico.endswith("$") and servico != "krbtgt":
            return "kerberoasting"
        return "normal"
    if ev["evento"] == 4624:
        if c["LogonType"] == "9" and c["LogonProcessName"].strip() == "seclogo":
            return "pth"
        local = c["TargetDomainName"].upper() != "CORP"
        if c["LogonType"] == "3" and c["AuthenticationPackageName"] == "NTLM" and local:
            return "pth"
        return "normal"
    if ev["evento"] == 4662:
        replica = GUID_GET_CHANGES_ALL in c["Properties"]
        if replica and c["SubjectUserName"] not in dcs:
            return "dcsync"
        return "normal"
    raise AssertionError("evento inesperado: %s" % ev["evento"])


class TestAtaquesAD(unittest.TestCase):
    """Valida a estrutura, o conteúdo, o grafo, os eventos e a compilação do estudo Ataques-e-Defesa-no-AD."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "ataques_e_defesa_no_ad_body.html"
        self.compiled_path = self.root / "Ataques-e-Defesa-no-AD" / "treinamento-ataques-e-defesa-no-ad.html"
        self.portal_path = self.root / "index.html"

    def _dados(self):
        body = self.body_path.read_text(encoding="utf-8")
        m = re.search(r'<script type="application/json" id="aa-dados">(.*?)</script>', body, re.S)
        self.assertIsNotNone(m, "Bloco JSON #aa-dados ausente no body")
        return json.loads(m.group(1))

    # ----------------------------------------------------------------- arquivos
    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        termos = [
            "BloodHound", "grafo", "MemberOf", "AdminTo", "HasSession", "GenericAll", "Kerberoasting", "SPN",
            "Pass-the-Hash", "NTLM", "DCSync", "krbtgt", "Golden Ticket", "duas vezes", "4769", "0x17", "4624",
            "tipo 9", "4662", GUID_GET_CHANGES, GUID_GET_CHANGES_ALL, "gMSA", "AES", "LAPS", "Protected Users",
            "tiering", "Tier 0", "T1558.003", "T1550.002", "T1003.006", "Estudo 38", "Estudo 40",
        ]
        for termo in termos:
            self.assertIn(termo, content, f"Termo obrigatório ausente: {termo}")

    def test_sem_comandos_ofensivos(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        for termo in OFENSIVOS:
            self.assertNotIn(termo, content, f"O módulo é defensivo: {termo}")

    # -------------------------------------------------------------------- grafo
    def test_grafo_valido(self):
        d = self._dados()
        nos = [n["id"] for n in d["nos"]]
        self.assertEqual(len(nos), len(set(nos)))
        self.assertIn(d["inicio"], nos)
        self.assertIn(d["alvo"], nos)
        ids = [a["id"] for a in d["arestas"]]
        self.assertEqual(len(ids), len(set(ids)))
        for a in d["arestas"]:
            with self.subTest(aresta=a["id"]):
                self.assertIn(a["de"], nos)
                self.assertIn(a["para"], nos)
                self.assertIn(a["tipo"], d["tipos_aresta"])
                self.assertTrue(a["explicacao"].strip())
                if "tecnica" in a:
                    self.assertIn(a["tecnica"], TECNICAS)
        for n in d["nos"]:
            self.assertTrue(n["nome"].strip() and n["tipo"] in d["tipos_no"], n["id"])

    def test_caminhos_abertos(self):
        d = self._dados()
        todos = caminhos(d)
        self.assertGreaterEqual(len(todos), 3)
        tec = {a["id"]: a.get("tecnica") for a in d["arestas"]}
        usadas = {tec[e] for c in todos for e in c} - {None}
        self.assertEqual(usadas, TECNICAS, "cada técnica abre algum caminho")
        self.assertEqual(min(len(c) for c in todos), d["passos_mais_curto"])
        self.assertEqual(len(todos), d["total_caminhos"])

    def test_mitigacoes_e_conjunto_minimo(self):
        d = self._dados()
        arestas = {a["id"] for a in d["arestas"]}
        for m in d["mitigacoes"]:
            with self.subTest(mitigacao=m["id"]):
                self.assertTrue(set(m["remove"]) <= arestas)
                self.assertEqual(m["efeito"] == "reduz", not m["remove"], "reduz <=> não remove aresta")
                self.assertTrue(m["nome"].strip() and m["explicacao"].strip())
        ids = [m["id"] for m in d["mitigacoes"]]
        self.assertEqual(caminhos(d, removidas_por(d, ids)), [], "todas juntas fecham tudo")
        for i in ids:
            self.assertTrue(caminhos(d, removidas_por(d, [i])), f"{i} sozinha não pode fechar tudo")
        minimos = None
        for k in range(1, len(ids) + 1):
            achados = [sorted(c) for c in itertools.combinations(ids, k) if not caminhos(d, removidas_por(d, c))]
            if achados:
                minimos = sorted(achados)
                break
        self.assertEqual(minimos, sorted(sorted(c) for c in d["conjuntos_minimos"]))

    # ------------------------------------------------------------------ eventos
    def test_eventos_coerentes(self):
        d = self._dados()
        evs = d["eventos"]
        self.assertGreaterEqual(len(evs), 8)
        respostas = [e["resposta"] for e in evs]
        self.assertTrue(set(respostas) <= RESPOSTAS)
        self.assertEqual(set(respostas), RESPOSTAS)
        self.assertGreaterEqual(respostas.count("normal"), 3, "eventos normais parecidos como distratores")
        for e in evs:
            with self.subTest(evento=e["id"]):
                self.assertEqual(classificar(e, set(d["controladores"])), e["resposta"])
                self.assertTrue(e["explicacao"].strip())
        for evento in (4769, 4624, 4662):
            tipos = {e["resposta"] for e in evs if e["evento"] == evento}
            self.assertIn("normal", tipos, f"{evento} precisa de um distrator normal")
            self.assertGreaterEqual(len(tipos), 2)

    # ---------------------------------------------------------------- compilado
    def test_simulador_estrutura(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        for marcador in ("aa-lab", 'id="aa-dados"', "aa-missoes", "aa-caminho", "aa-mitigacoes", "aa-status",
                         "aa-eventos", "escolherArestaAtaquesAD", "voltarCaminhoAtaquesAD",
                         "alternarMitigacaoAtaquesAD", "classificarEventoAtaquesAD", "restaurarAtaquesAD"):
            self.assertIn(marcador, content, marcador)
        ini = content.index("var AA = JSON.parse")
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
        self.assertIn('initChecklist("ataques-ad")', content)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn("Ataques-e-Defesa-no-AD/treinamento-ataques-e-defesa-no-ad.html", content)
        self.assertIn('data-slug="Ataques-e-Defesa-no-AD"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)


if __name__ == "__main__":
    unittest.main()
