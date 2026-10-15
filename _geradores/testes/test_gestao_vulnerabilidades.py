#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_gestao_vulnerabilidades.py
Testes automatizados para o Estudo 09: Gestao-de-Vulnerabilidades
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402


class TestGestaoVulnerabilidades(unittest.TestCase):
    """Valida a estrutura, conteúdo e compilação do estudo Gestao-de-Vulnerabilidades."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "gestao_de_vulnerabilidades_body.html"
        self.compiled_path = self.root / "Gestao-de-Vulnerabilidades" / "treinamento-gestao-de-vulnerabilidades.html"
        self.portal_path = self.root / "index.html"

    def test_body_and_compiled_files_exist(self):
        """Verifica se o fragmento body e o treinamento final compilado existem."""
        self.assertTrue(self.body_path.exists(), "O arquivo _geradores/gestao_de_vulnerabilidades_body.html deve existir.")
        self.assertTrue(self.compiled_path.exists(), "O arquivo Gestao-de-Vulnerabilidades/treinamento-gestao-de-vulnerabilidades.html deve existir.")

    def test_teoria_e_conceitos_fundamentais(self):
        """Verifica se os conceitos obrigatórios de CVE, CVSS v3.1, CVSS v4.0, EPSS e CISA KEV estão presentes."""
        self.assertTrue(self.compiled_path.exists())
        content = self.compiled_path.read_text(encoding="utf-8")

        termos_obrigatorios = [
            "CVE",
            "CVSS",
            "CVSS v3.1",
            "CVSS v4.0",
            "EPSS",
            "CISA KEV",
            "Base Score",
            "Exploitability",
            "Attack Vector",
            "Attack Complexity",
            "Privileges Required",
            "User Interaction",
            "Scope",
        ]
        for termo in termos_obrigatorios:
            self.assertIn(termo, content, f"O termo obrigatório '{termo}' deve estar presente no conteúdo.")

    def test_simulador_lab_calculadora_cvss(self):
        """Verifica se o simulador interativo de cálculo de score CVSS e priorização está estruturado no HTML."""
        self.assertTrue(self.compiled_path.exists())
        content = self.compiled_path.read_text(encoding="utf-8")

        self.assertIn("cvss-lab", content)
        self.assertIn("calcularScoreCvss", content)
        self.assertIn("gerarStringVetorCvss", content)
        self.assertIn("carregarCenarioCve", content)

    def test_componentes_pedagogicos(self):
        """Verifica a presença de checklists, quizzes e callouts padronizados."""
        self.assertTrue(self.compiled_path.exists())
        content = self.compiled_path.read_text(encoding="utf-8")

        self.assertIn('class="callout', content)
        self.assertIn('class="checklist', content)
        self.assertIn('class="quiz-item', content)
        self.assertIn('class="facts-grid', content)
        self.assertTrue(
            "initChecklist('gestao-vulnerabilidades')" in content or 'initChecklist("gestao-vulnerabilidades")' in content,
            "Chamada initChecklist('gestao-vulnerabilidades') deve estar presente no script."
        )

    def test_integracao_com_portal_index(self):
        """Verifica se o portal index.html aponta Gestao-de-Vulnerabilidades como Disponível com link ativo."""
        self.assertTrue(self.portal_path.exists())
        content = self.portal_path.read_text(encoding="utf-8")

        self.assertIn("Gestao-de-Vulnerabilidades/treinamento-gestao-de-vulnerabilidades.html", content)
        self.assertIn('data-slug="Gestao-de-Vulnerabilidades"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)
        self.assertIn("Módulos Compilados", content)


if __name__ == "__main__":
    unittest.main()
