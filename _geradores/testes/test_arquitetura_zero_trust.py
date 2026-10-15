#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_arquitetura_zero_trust.py
Testes automatizados para o Estudo 08: Arquitetura-Zero-Trust
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402


class TestArquiteturaZeroTrust(unittest.TestCase):
    """Valida a estrutura, conteúdo e compilação do estudo Arquitetura-Zero-Trust."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "arquitetura_zero_trust_body.html"
        self.compiled_path = self.root / "Arquitetura-Zero-Trust" / "treinamento-arquitetura-zero-trust.html"
        self.portal_path = self.root / "index.html"

    def test_body_and_compiled_files_exist(self):
        """Verifica se o fragmento body e o treinamento final compilado existem."""
        self.assertTrue(self.body_path.exists(), "O arquivo _geradores/arquitetura_zero_trust_body.html deve existir.")
        self.assertTrue(self.compiled_path.exists(), "O arquivo Arquitetura-Zero-Trust/treinamento-arquitetura-zero-trust.html deve existir.")

    def test_teoria_e_conceitos_fundamentais(self):
        """Verifica se os conceitos obrigatórios de NIST SP 800-207, PDP, PEP, ZTNA e Microsegmentação estão presentes."""
        self.assertTrue(self.compiled_path.exists())
        content = self.compiled_path.read_text(encoding="utf-8")

        termos_obrigatorios = [
            "NIST SP 800-207",
            "Never Trust, Always Verify",
            "Assume Breach",
            "PDP",
            "PEP",
            "Policy Engine",
            "ZTNA",
            "Microsegmentação",
            "Postura do Dispositivo",
            "SDP",
        ]
        for termo in termos_obrigatorios:
            self.assertIn(termo, content, f"O termo obrigatório '{termo}' deve estar presente no conteúdo.")

    def test_simulador_lab_zero_trust(self):
        """Verifica se o simulador interativo de motor de decisão PDP/PEP está estruturado no HTML."""
        self.assertTrue(self.compiled_path.exists())
        content = self.compiled_path.read_text(encoding="utf-8")

        self.assertIn("zero-trust-lab", content)
        self.assertIn("avaliarDecisaoZeroTrust", content)
        self.assertIn("injetarCenarioZeroTrust", content)
        self.assertIn("calcularScoreRisco", content)

    def test_componentes_pedagogicos(self):
        """Verifica a presença de checklists, quizzes e callouts padronizados."""
        self.assertTrue(self.compiled_path.exists())
        content = self.compiled_path.read_text(encoding="utf-8")

        self.assertIn('class="callout', content)
        self.assertIn('class="checklist', content)
        self.assertIn('class="quiz-item', content)
        self.assertIn('class="facts-grid', content)
        self.assertTrue(
            "initChecklist('arquitetura-zero-trust')" in content or 'initChecklist("arquitetura-zero-trust")' in content,
            "Chamada initChecklist('arquitetura-zero-trust') deve estar presente no script."
        )

    def test_integracao_com_portal_index(self):
        """Verifica se o portal index.html aponta Arquitetura-Zero-Trust como Disponível com link ativo."""
        self.assertTrue(self.portal_path.exists())
        content = self.portal_path.read_text(encoding="utf-8")

        self.assertIn("Arquitetura-Zero-Trust/treinamento-arquitetura-zero-trust.html", content)
        self.assertIn('data-slug="Arquitetura-Zero-Trust"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)
        self.assertIn("Módulos Compilados", content)


if __name__ == "__main__":
    unittest.main()
