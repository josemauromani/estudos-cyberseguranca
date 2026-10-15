#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_segmentacao_firewall.py
Testes automatizados para o Estudo 05: Segmentacao-e-Firewall
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402


class TestSegmentacaoFirewall(unittest.TestCase):
    """Valida a estrutura, conteúdo e compilação do estudo Segmentacao-e-Firewall."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "segmentacao_e_firewall_body.html"
        self.compiled_path = self.root / "Segmentacao-e-Firewall" / "treinamento-segmentacao-e-firewall.html"
        self.portal_path = self.root / "index.html"

    def test_body_and_compiled_files_exist(self):
        """Verifica se o fragmento body e o treinamento final compilado existem."""
        self.assertTrue(self.body_path.exists(), "O arquivo _geradores/segmentacao_e_firewall_body.html deve existir.")
        self.assertTrue(self.compiled_path.exists(), "O arquivo Segmentacao-e-Firewall/treinamento-segmentacao-e-firewall.html deve existir.")

    def test_teoria_e_conceitos_fundamentais(self):
        """Verifica se os conceitos obrigatórios de DMZ, VLANs, Stateful, conntrack, Default Drop e First-Match estão presentes."""
        self.assertTrue(self.compiled_path.exists())
        content = self.compiled_path.read_text(encoding="utf-8")

        termos_obrigatorios = [
            "DMZ",
            "VLAN",
            "802.1Q",
            "Trunk",
            "Stateful",
            "Stateless",
            "conntrack",
            "Default Drop",
            "First-Match",
            "Rule Shadowing",
            "NGFW",
        ]
        for termo in termos_obrigatorios:
            self.assertIn(termo, content, f"O termo obrigatório '{termo}' deve estar presente no conteúdo.")

    def test_simulador_lab_firewall(self):
        """Verifica se o simulador interativo de filtragem de pacotes está estruturado no HTML."""
        self.assertTrue(self.compiled_path.exists())
        content = self.compiled_path.read_text(encoding="utf-8")

        self.assertIn("firewall-lab", content)
        self.assertIn("avaliarPacoteFirewall", content)
        self.assertIn("injetarPacoteCenario", content)
        self.assertIn("reordenarRegra", content)
        self.assertIn("conntrack", content.lower())

    def test_componentes_pedagogicos(self):
        """Verifica a presença de checklists, quizzes e callouts padronizados."""
        self.assertTrue(self.compiled_path.exists())
        content = self.compiled_path.read_text(encoding="utf-8")

        self.assertIn('class="callout', content)
        self.assertIn('class="checklist', content)
        self.assertIn('class="quiz-item', content)
        self.assertIn('class="facts-grid', content)
        self.assertTrue(
            "initChecklist('segmentacao-firewall')" in content or 'initChecklist("segmentacao-firewall")' in content,
            "Chamada initChecklist('segmentacao-firewall') deve estar presente no script."
        )

    def test_integracao_com_portal_index(self):
        """Verifica se o portal index.html aponta Segmentacao-e-Firewall como Disponível com link ativo."""
        self.assertTrue(self.portal_path.exists())
        content = self.portal_path.read_text(encoding="utf-8")

        self.assertIn("Segmentacao-e-Firewall/treinamento-segmentacao-e-firewall.html", content)
        self.assertIn('data-slug="Segmentacao-e-Firewall"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)
        self.assertIn("Módulos Compilados", content)


if __name__ == "__main__":
    unittest.main()
