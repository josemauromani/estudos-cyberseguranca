#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_reconhecimento_osint.py
Testes automatizados para o Estudo 11: Reconhecimento-e-OSINT
"""

import unittest
from pathlib import Path


class TestReconhecimentoOsint(unittest.TestCase):
    """Valida a estrutura, conteúdo e compilação do estudo Reconhecimento-e-OSINT."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "reconhecimento_e_osint_body.html"
        self.compiled_path = self.root / "Reconhecimento-e-OSINT" / "treinamento-reconhecimento-e-osint.html"
        self.portal_path = self.root / "index.html"

    def test_body_and_compiled_files_exist(self):
        """Verifica se o fragmento body e o treinamento final compilado existem."""
        self.assertTrue(self.body_path.exists(), "O arquivo _geradores/reconhecimento_e_osint_body.html deve existir.")
        self.assertTrue(self.compiled_path.exists(), "O arquivo Reconhecimento-e-OSINT/treinamento-reconhecimento-e-osint.html deve existir.")

    def test_teoria_e_conceitos_fundamentais(self):
        """Verifica se os conceitos obrigatórios de OSINT, passivo/ativo, WHOIS, DNS, CT Logs e Shodan estão presentes."""
        self.assertTrue(self.compiled_path.exists())
        content = self.compiled_path.read_text(encoding="utf-8")

        termos_obrigatorios = [
            "OSINT",
            "Reconhecimento Passivo",
            "Reconhecimento Ativo",
            "WHOIS",
            "DNS",
            "Certificate Transparency",
            "Google Dorks",
            "Shodan",
            "Subdomain Takeover",
            "ExifTool",
        ]
        for termo in termos_obrigatorios:
            self.assertIn(termo, content, f"O termo obrigatório '{termo}' deve estar presente no conteúdo.")

    def test_simulador_lab_terminal_osint(self):
        """Verifica se o simulador interativo de terminal OSINT está estruturado no HTML."""
        self.assertTrue(self.compiled_path.exists())
        content = self.compiled_path.read_text(encoding="utf-8")

        self.assertIn("osint-lab", content)
        self.assertIn("executarComandoOsint", content)
        self.assertIn("whois", content)
        self.assertIn("dig", content)
        self.assertIn("crtsh", content)
        self.assertIn("shodan", content)

    def test_componentes_pedagogicos(self):
        """Verifica a presença de checklists, quizzes e callouts padronizados."""
        self.assertTrue(self.compiled_path.exists())
        content = self.compiled_path.read_text(encoding="utf-8")

        self.assertIn('class="callout', content)
        self.assertIn('class="checklist', content)
        self.assertIn('class="quiz-item', content)
        self.assertIn('class="facts-grid', content)
        self.assertTrue(
            "initChecklist('reconhecimento-osint')" in content or 'initChecklist("reconhecimento-osint")' in content,
            "Chamada initChecklist('reconhecimento-osint') deve estar presente no script."
        )

    def test_integracao_com_portal_index(self):
        """Verifica se o portal index.html aponta Reconhecimento-e-OSINT como Disponível com link ativo."""
        self.assertTrue(self.portal_path.exists())
        content = self.portal_path.read_text(encoding="utf-8")

        self.assertIn("Reconhecimento-e-OSINT/treinamento-reconhecimento-e-osint.html", content)
        self.assertIn('data-slug="Reconhecimento-e-OSINT"', content)
        self.assertIn("/ 28", content)


if __name__ == "__main__":
    unittest.main()
