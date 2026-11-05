#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_iso_27001_27002.py
Testes automatizados para o Estudo 26: ISO-27001-e-27002
"""

import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402

TEMAS = {"5": ("Organizacionais", 37), "6": ("Pessoas", 8), "7": ("Físicos", 14), "8": ("Tecnológicos", 34)}
NOVOS_2022 = {"5.7", "5.23", "5.30", "7.4", "8.9", "8.10", "8.11", "8.12", "8.16", "8.23", "8.28"}


class TestIso27001e27002(unittest.TestCase):
    """Valida a estrutura, o conteúdo e a compilação do estudo ISO-27001-e-27002."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "iso_27001_e_27002_body.html"
        self.compiled_path = self.root / "ISO-27001-e-27002" / "treinamento-iso-27001-e-27002.html"
        self.portal_path = self.root / "index.html"

    def _dados(self):
        body = self.body_path.read_text(encoding="utf-8")
        m = re.search(r'<script type="application/json" id="soa-dados">(.*?)</script>', body, re.S)
        self.assertIsNotNone(m, "Bloco JSON #soa-dados ausente no body")
        return json.loads(m.group(1))

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists(), "_geradores/iso_27001_e_27002_body.html deve existir.")
        self.assertTrue(self.compiled_path.exists(), "ISO-27001-e-27002/treinamento-iso-27001-e-27002.html deve existir.")

    def test_sgsi_distingue_cis_controls_de_benchmarks(self):
        body = self.body_path.read_text(encoding="utf-8")
        m = re.search(r'<section[^>]*id="sgsi".*?</section>', body, re.S)
        self.assertIsNotNone(m)
        sec = m.group(0)
        for termo in ("CIS Controls", "CIS Benchmarks", "Estudo 06"):
            self.assertIn(termo, sec)

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        termos = [
            "ISO/IEC 27001:2022",
            "ISO/IEC 27002:2022",
            "SGSI",
            "PDCA",
            "6.1.3",
            "Declaração de Aplicabilidade",
            "Anexo A",
            "93 controles",
            "Emenda 1:2024",
            "31/10/2025",
            "Fase 1",
            "Fase 2",
            "CIS Controls v8.1",
            "IG1",
            "IG2",
            "IG3",
            "NIST SP 800-53 Rev. 5",
            "800-53B",
            "crosswalk",
        ]
        for termo in termos:
            self.assertIn(termo, content, f"Termo obrigatório ausente: {termo}")

    def test_anexo_a_tem_93_controles_em_4_temas(self):
        controles = self._dados()["controles"]
        self.assertEqual(len(controles), 93)
        ids = [c["id"] for c in controles]
        self.assertEqual(len(set(ids)), 93, "ids duplicados")
        for prefixo, (tema, total) in TEMAS.items():
            with self.subTest(tema=tema):
                do_tema = [c for c in controles if c["id"].split(".")[0] == prefixo]
                self.assertEqual(len(do_tema), total)
                self.assertTrue(all(c["tema"] == tema for c in do_tema))
                self.assertEqual([c["id"] for c in do_tema], [f"{prefixo}.{n}" for n in range(1, total + 1)])
                self.assertTrue(all(c["nome"].strip() for c in do_tema))

    def test_controles_novos_de_2022_marcados(self):
        controles = self._dados()["controles"]
        self.assertEqual({c["id"] for c in controles if c.get("novo")}, NOVOS_2022)

    def test_crosswalk_tem_15_entradas_completas(self):
        dados = self._dados()
        ids = {c["id"] for c in dados["controles"]}
        cross = dados["crosswalk"]
        self.assertEqual(len(cross), 15)
        for entrada in cross:
            with self.subTest(controle=entrada.get("id")):
                self.assertIn(entrada["id"], ids)
                self.assertTrue(entrada["cis"].strip())
                self.assertTrue(entrada["nist"].strip())
                self.assertRegex(entrada["nist"], r"\b[A-Z]{2}-\d+")

    def test_regras_de_coerencia_apontam_para_controles_existentes(self):
        dados = self._dados()
        ids = {c["id"] for c in dados["controles"]}
        self.assertGreaterEqual(len(dados["regras"]), 4)
        for regra in dados["regras"]:
            with self.subTest(controle=regra.get("id")):
                self.assertIn(regra["id"], ids)
                self.assertTrue(regra["motivo"].strip())
        for chave in ("5.23", "6.7", "8.28", "5.34"):
            self.assertIn(chave, {r["id"] for r in dados["regras"]})

    def test_simulador_estrutura(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        for marcador in ("soa-lab", 'id="soa-dados"', "renderizarSoA", "copiarSoACSV", "cs_soa_iso27001", "soa-resumo", "soa-alertas"):
            self.assertIn(marcador, content, marcador)
        ini = content.index("var SOA = JSON.parse")
        motor = content[ini:content.index("</script>", ini)]
        self.assertNotIn("innerHTML", motor)

    def test_componentes_pedagogicos(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        self.assertIn('class="callout', content)
        self.assertEqual(content.count('class="checklist-item"'), 7)
        self.assertGreaterEqual(content.count('class="quiz-item"'), 5)
        self.assertIn('class="facts-grid', content)
        self.assertIn('initChecklist("iso-27001-27002")', content)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn("ISO-27001-e-27002/treinamento-iso-27001-e-27002.html", content)
        self.assertIn('data-slug="ISO-27001-e-27002"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)


if __name__ == "__main__":
    unittest.main()
