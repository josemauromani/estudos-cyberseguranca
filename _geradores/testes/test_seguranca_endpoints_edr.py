#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_seguranca_endpoints_edr.py
Testes automatizados para o Estudo 10: Seguranca-em-Endpoints-EDR
"""

import unittest
from pathlib import Path


class TestSegurancaEndpointsEdr(unittest.TestCase):
    """Valida a estrutura, conteúdo e compilação do estudo Seguranca-em-Endpoints-EDR."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "seguranca_em_endpoints_edr_body.html"
        self.compiled_path = self.root / "Seguranca-em-Endpoints-EDR" / "treinamento-seguranca-em-endpoints-edr.html"
        self.portal_path = self.root / "index.html"

    def test_body_and_compiled_files_exist(self):
        """Verifica se o fragmento body e o treinamento final compilado existem."""
        self.assertTrue(self.body_path.exists(), "O arquivo _geradores/seguranca_em_endpoints_edr_body.html deve existir.")
        self.assertTrue(self.compiled_path.exists(), "O arquivo Seguranca-em-Endpoints-EDR/treinamento-seguranca-em-endpoints-edr.html deve existir.")

    def test_teoria_e_conceitos_fundamentais(self):
        """Verifica se os conceitos obrigatórios de EPP, EDR, XDR, Sysmon, auditd e parent-child estão presentes."""
        self.assertTrue(self.compiled_path.exists())
        content = self.compiled_path.read_text(encoding="utf-8")

        termos_obrigatorios = [
            "EPP",
            "EDR",
            "XDR",
            "Sysmon",
            "Event ID 1",
            "Event ID 3",
            "Event ID 10",
            "auditd",
            "Parent-Child",
            "LSASS",
            "LOLBins",
            "Isolamento",
        ]
        for termo in termos_obrigatorios:
            self.assertIn(termo, content, f"O termo obrigatório '{termo}' deve estar presente no conteúdo.")

    def test_simulador_lab_telemetria_edr(self):
        """Verifica se o simulador interativo de telemetria e contenção EDR está estruturado no HTML."""
        self.assertTrue(self.compiled_path.exists())
        content = self.compiled_path.read_text(encoding="utf-8")

        self.assertIn("edr-lab", content)
        self.assertIn("carregarCenarioEdr", content)
        self.assertIn("isolarHostRede", content)
        self.assertIn("finalizarProcesso", content)
        self.assertIn("inspecionarEvento", content)

    def test_componentes_pedagogicos(self):
        """Verifica a presença de checklists, quizzes e callouts padronizados."""
        self.assertTrue(self.compiled_path.exists())
        content = self.compiled_path.read_text(encoding="utf-8")

        self.assertIn('class="callout', content)
        self.assertIn('class="checklist', content)
        self.assertIn('class="quiz-item', content)
        self.assertIn('class="facts-grid', content)
        self.assertTrue(
            "initChecklist('seguranca-endpoints-edr')" in content or 'initChecklist("seguranca-endpoints-edr")' in content,
            "Chamada initChecklist('seguranca-endpoints-edr') deve estar presente no script."
        )

    def test_integracao_com_portal_index(self):
        """Verifica se o portal index.html aponta Seguranca-em-Endpoints-EDR como Disponível com link ativo."""
        self.assertTrue(self.portal_path.exists())
        content = self.portal_path.read_text(encoding="utf-8")

        self.assertIn("Seguranca-em-Endpoints-EDR/treinamento-seguranca-em-endpoints-edr.html", content)
        self.assertIn('data-slug="Seguranca-em-Endpoints-EDR"', content)
        self.assertIn("/ 28", content)


if __name__ == "__main__":
    unittest.main()
