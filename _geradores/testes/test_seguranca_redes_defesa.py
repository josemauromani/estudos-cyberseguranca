#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_seguranca_redes_defesa.py
Testes automatizados para o Estudo 07: Seguranca-de-Redes-Defesa
"""

import unittest
from pathlib import Path


class TestSegurancaRedesDefesa(unittest.TestCase):
    """Valida a estrutura, conteúdo e compilação do estudo Seguranca-de-Redes-Defesa."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "seguranca_de_redes_defesa_body.html"
        self.compiled_path = self.root / "Seguranca-de-Redes-Defesa" / "treinamento-seguranca-de-redes-defesa.html"
        self.portal_path = self.root / "index.html"

    def test_body_and_compiled_files_exist(self):
        """Verifica se o fragmento body e o treinamento final compilado existem."""
        self.assertTrue(self.body_path.exists(), "O arquivo _geradores/seguranca_de_redes_defesa_body.html deve existir.")
        self.assertTrue(self.compiled_path.exists(), "O arquivo Seguranca-de-Redes-Defesa/treinamento-seguranca-de-redes-defesa.html deve existir.")

    def test_teoria_e_conceitos_fundamentais(self):
        """Verifica se os conceitos obrigatórios de IDS, IPS, Snort, Suricata, WAF, WireGuard, IPsec e mTLS estão presentes."""
        self.assertTrue(self.compiled_path.exists())
        content = self.compiled_path.read_text(encoding="utf-8")

        termos_obrigatorios = [
            "IDS",
            "IPS",
            "Snort",
            "Suricata",
            "WAF",
            "Core Rule Set",
            "WireGuard",
            "IPsec",
            "IKEv2",
            "mTLS",
            "Reverse Proxy",
        ]
        for termo in termos_obrigatorios:
            self.assertIn(termo, content, f"O termo obrigatório '{termo}' deve estar presente no conteúdo.")

    def test_simulador_lab_regras_ids_ips(self):
        """Verifica se o simulador interativo de regras Snort/Suricata vs tráfego está estruturado no HTML."""
        self.assertTrue(self.compiled_path.exists())
        content = self.compiled_path.read_text(encoding="utf-8")

        self.assertIn("ids-lab", content)
        self.assertIn("avaliarPayloadRegrasIds", content)
        self.assertIn("injetarCenarioTrafego", content)
        self.assertIn("alternarModoIdsIps", content)

    def test_componentes_pedagogicos(self):
        """Verifica a presença de checklists, quizzes e callouts padronizados."""
        self.assertTrue(self.compiled_path.exists())
        content = self.compiled_path.read_text(encoding="utf-8")

        self.assertIn('class="callout', content)
        self.assertIn('class="checklist', content)
        self.assertIn('class="quiz-item', content)
        self.assertIn('class="facts-grid', content)
        self.assertTrue(
            "initChecklist('seguranca-redes-defesa')" in content or 'initChecklist("seguranca-redes-defesa")' in content,
            "Chamada initChecklist('seguranca-redes-defesa') deve estar presente no script."
        )

    def test_integracao_com_portal_index(self):
        """Verifica se o portal index.html aponta Seguranca-de-Redes-Defesa como Disponível com link ativo."""
        self.assertTrue(self.portal_path.exists())
        content = self.portal_path.read_text(encoding="utf-8")

        self.assertIn("Seguranca-de-Redes-Defesa/treinamento-seguranca-de-redes-defesa.html", content)
        self.assertIn('data-slug="Seguranca-de-Redes-Defesa"', content)
        self.assertIn("/ 28", content)
        self.assertIn("Módulos Compilados", content)


if __name__ == "__main__":
    unittest.main()
