#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_pci_dss.py
Testes automatizados para o Estudo 31: PCI-DSS
"""

import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402

ARQUITETURAS = ["proprio", "javascript", "iframe"]
CATEGORIAS = {"cde", "conectado", "fora", "terceiro"}
EM_ESCOPO = {"cde", "conectado"}


def classificar(sistema, attrs):
    """Regra única do simulador (espelhada no JavaScript)."""
    if sistema["terceiro"]:
        return "terceiro"
    if attrs["pan"]:
        return "cde"
    if attrs["impacta"] or not attrs["segmentado"]:
        return "conectado"
    return "fora"


def saq(arquitetura, sistemas):
    proprios_com_pan = [s for s in sistemas
                        if not s["terceiro"] and s["por_arquitetura"][arquitetura["id"]]["pan"]]
    if proprios_com_pan:
        return "D"
    return "A-EP" if arquitetura["captura_no_site"] else "A"


class TestPciDss(unittest.TestCase):
    """Valida a estrutura, o conteúdo, a regra de escopo e a compilação do estudo PCI-DSS."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "pci_dss_body.html"
        self.compiled_path = self.root / "PCI-DSS" / "treinamento-pci-dss.html"
        self.portal_path = self.root / "index.html"

    def _dados(self):
        body = self.body_path.read_text(encoding="utf-8")
        m = re.search(r'<script type="application/json" id="pci-dados">(.*?)</script>', body, re.S)
        self.assertIsNotNone(m, "Bloco JSON #pci-dados ausente no body")
        return json.loads(m.group(1))

    def _categorias(self, d, arq_id):
        return {s["id"]: classificar(s, s["por_arquitetura"][arq_id]) for s in d["sistemas"]}

    # ----------------------------------------------------------------- arquivos
    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        termos = [
            "PCI DSS v4.0.1", "PCI SSC", "31/03/2025", "PAN", "SAD", "CVV2", "tokenização", "truncamento",
            "mascaramento", "3.5.1.1", "CDE", "segmentação", "11.4.5", "12.5.2", "12.8", "TPSP",
            "SAQ A-EP", "SAQ D", "B-IP", "C-VT", "P2PE", "ROC", "AOC", "QSA", "ISA", "ASV",
            "abordagem definida", "abordagem customizada", "12.3.1", "8.4.2", "8.3.6", "5.4.1",
            "6.4.3", "11.6.1", "10.4.1.1", "Nível 1",
        ]
        for termo in termos:
            self.assertIn(termo, content, f"Termo obrigatório ausente: {termo}")

    def test_doze_requisitos_e_seis_objetivos(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        numeros = sorted(int(n) for n in re.findall(r'data-requisito="(\d+)"', content))
        self.assertEqual(numeros, list(range(1, 13)))
        self.assertEqual(len(set(re.findall(r'data-objetivo="(\d+)"', content))), 6)

    # -------------------------------------------------------------------- dados
    def test_arquiteturas_e_sistemas_validos(self):
        d = self._dados()
        self.assertEqual([a["id"] for a in d["arquiteturas"]], ARQUITETURAS)
        for a in d["arquiteturas"]:
            for campo in ("nome", "descricao", "explicacao_saq"):
                self.assertTrue(a[campo].strip(), campo)
            self.assertIsInstance(a["captura_no_site"], bool)
        self.assertGreaterEqual(len(d["sistemas"]), 10)
        ids = [s["id"] for s in d["sistemas"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreaterEqual(sum(1 for s in d["sistemas"] if s["terceiro"]), 1)
        for s in d["sistemas"]:
            with self.subTest(sistema=s["id"]):
                self.assertTrue(s["nome"].strip())
                self.assertEqual(set(s["por_arquitetura"]), set(ARQUITETURAS))
                for arq, attrs in s["por_arquitetura"].items():
                    self.assertTrue(attrs["descricao"].strip(), arq)
                    self.assertTrue(attrs["motivo"].strip(), arq)
                    for campo in ("pan", "impacta", "segmentado"):
                        self.assertIsInstance(attrs[campo], bool, f"{arq}.{campo}")
        self.assertEqual(set(d["saq_opcoes"]), {"A", "A-EP", "B", "B-IP", "C", "C-VT", "P2PE", "D"})

    def test_saq_de_cada_arquitetura_segue_a_regra(self):
        d = self._dados()
        esperado = {"proprio": "D", "javascript": "A-EP", "iframe": "A"}
        for a in d["arquiteturas"]:
            with self.subTest(arquitetura=a["id"]):
                self.assertEqual(saq(a, d["sistemas"]), esperado[a["id"]])
                self.assertEqual(a["saq"], esperado[a["id"]])

    def test_escopo_encolhe_com_a_tokenizacao(self):
        d = self._dados()
        em_escopo = {}
        for arq in ARQUITETURAS:
            cats = self._categorias(d, arq)
            em_escopo[arq] = sum(1 for c in cats.values() if c in EM_ESCOPO)
        self.assertGreater(em_escopo["proprio"], em_escopo["javascript"])
        self.assertGreater(em_escopo["javascript"], em_escopo["iframe"])
        self.assertGreaterEqual(list(self._categorias(d, "proprio").values()).count("cde"), 4)
        self.assertNotIn("cde", self._categorias(d, "javascript").values())
        self.assertNotIn("cde", self._categorias(d, "iframe").values())

    def test_casos_pedagogicos(self):
        d = self._dados()
        todas = set()
        rede_plana = False
        for arq in ARQUITETURAS:
            todas |= set(self._categorias(d, arq).values())
            for s in d["sistemas"]:
                a = s["por_arquitetura"][arq]
                if not s["terceiro"] and not a["pan"] and not a["impacta"] and not a["segmentado"]:
                    rede_plana = True
        self.assertEqual(todas, CATEGORIAS)
        self.assertTrue(rede_plana, "deve haver sistema em escopo só por falta de segmentação")

    # ---------------------------------------------------------------- compilado
    def test_simulador_estrutura(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        for marcador in ("pci-lab", 'id="pci-dados"', "pci-sistemas", "pci-resumo", "pci-saq",
                         "selecionarArquiteturaPCI", "alternarModoPCI", "conferirEscopoPCI", "restaurarPCI"):
            self.assertIn(marcador, content, marcador)
        ini = content.index("var PCI = JSON.parse")
        motor = content[ini:content.index("</script>", ini)]
        self.assertNotIn("innerHTML", motor)

    def test_componentes_pedagogicos(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        self.assertIn('class="callout', content)
        self.assertIn('class="diagram-svg-wrap', content)
        self.assertNotIn('<pre class="mermaid"', content)
        self.assertEqual(content.count('class="checklist-item"'), 7)
        self.assertGreaterEqual(content.count('class="quiz-item"'), 6)
        self.assertIn('class="facts-grid', content)
        self.assertIn('initChecklist("pci-dss")', content)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn("PCI-DSS/treinamento-pci-dss.html", content)
        self.assertIn('data-slug="PCI-DSS"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)


if __name__ == "__main__":
    unittest.main()
