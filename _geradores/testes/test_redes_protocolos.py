#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_redes_protocolos.py
Testes automatizados para o Estudo 02: Redes-e-Protocolos
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402


class TestRedesProtocolos(unittest.TestCase):
    """Valida a estrutura, conteúdo e compilação do estudo Redes-e-Protocolos."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "redes_protocolos_body.html"
        self.compiled_path = self.root / "Redes-e-Protocolos" / "treinamento-redes-e-protocolos.html"
        self.portal_path = self.root / "index.html"

    def test_body_and_compiled_files_exist(self):
        """Verifica se o fragmento body e o treinamento final compilado existem."""
        self.assertTrue(self.body_path.exists(), "O arquivo _geradores/redes_protocolos_body.html deve existir.")
        self.assertTrue(self.compiled_path.exists(), "O arquivo Redes-e-Protocolos/treinamento-redes-e-protocolos.html deve existir.")

    def test_teoria_e_conceitos_fundamentais(self):
        """Verifica se os conceitos obrigatórios da pilha TCP/IP e protocolos estão presentes."""
        self.assertTrue(self.compiled_path.exists())
        content = self.compiled_path.read_text(encoding="utf-8")

        termos_obrigatorios = [
            "TCP/IP",
            "Modelo OSI",
            "Encapsulamento",
            "Handshake",
            "IPv4",
            "IPv6",
            "DNS",
            "ARP",
            "SYN",
            "ACK",
            "FIN",
            "RST",
        ]
        for termo in termos_obrigatorios:
            self.assertIn(termo, content, f"O termo obrigatório '{termo}' deve estar presente no conteúdo.")

    def test_simulador_inspetor_pacotes_interativo(self):
        """Verifica se o simulador de cabeçalhos e probe de portas está estruturado no HTML."""
        self.assertTrue(self.compiled_path.exists())
        content = self.compiled_path.read_text(encoding="utf-8")

        self.assertIn("packet-inspector", content)
        self.assertIn("simularHandshake", content)
        self.assertIn("testarPorta", content)
        self.assertIn("Visualizador de Cabeçalho", content)

    def test_componentes_pedagogicos(self):
        """Verifica a presença de checklists, quizzes e callouts padronizados."""
        self.assertTrue(self.compiled_path.exists())
        content = self.compiled_path.read_text(encoding="utf-8")

        self.assertIn('class="callout', content)
        self.assertIn('class="checklist', content)
        self.assertIn('class="quiz-item', content)
        self.assertIn('class="facts-grid', content)
        self.assertIn("initChecklist('redes-protocolos')", content)

    def test_integracao_com_portal_index(self):
        """Verifica se o portal index.html aponta Redes-e-Protocolos como Disponível com link ativo."""
        self.assertTrue(self.portal_path.exists())
        content = self.portal_path.read_text(encoding="utf-8")

        self.assertIn("Redes-e-Protocolos/treinamento-redes-e-protocolos.html", content)
        self.assertIn('data-slug="Redes-e-Protocolos"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)
        self.assertIn("Módulos Compilados", content)


if __name__ == "__main__":
    unittest.main()
