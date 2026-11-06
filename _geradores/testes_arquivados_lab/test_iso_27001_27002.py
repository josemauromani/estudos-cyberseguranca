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
from index_dados import ESTUDOS_DADOS
TEMAS = {'5': ('Organizacionais', 37), '6': ('Pessoas', 8), '7': ('Físicos', 14), '8': ('Tecnológicos', 34)}
NOVOS_2022 = {'5.7', '5.23', '5.30', '7.4', '8.9', '8.10', '8.11', '8.12', '8.16', '8.23', '8.28'}

class TestIso27001e27002(unittest.TestCase):
    """Valida a estrutura, o conteúdo e a compilação do estudo ISO-27001-e-27002."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / '_geradores' / 'iso_27001_e_27002_body.html'
        self.compiled_path = self.root / 'ISO-27001-e-27002' / 'treinamento-iso-27001-e-27002.html'
        self.portal_path = self.root / 'index.html'

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists(), '_geradores/iso_27001_e_27002_body.html deve existir.')
        self.assertTrue(self.compiled_path.exists(), 'ISO-27001-e-27002/treinamento-iso-27001-e-27002.html deve existir.')

    def test_sgsi_distingue_cis_controls_de_benchmarks(self):
        body = self.body_path.read_text(encoding='utf-8')
        m = re.search('<section[^>]*id="sgsi".*?</section>', body, re.S)
        self.assertIsNotNone(m)
        sec = m.group(0)
        for termo in ('CIS Controls', 'CIS Benchmarks', 'Estudo 06'):
            self.assertIn(termo, sec)

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        termos = ['ISO/IEC 27001:2022', 'ISO/IEC 27002:2022', 'SGSI', 'PDCA', '6.1.3', 'Declaração de Aplicabilidade', 'Anexo A', '93 controles', 'Emenda 1:2024', '31/10/2025', 'Fase 1', 'Fase 2', 'CIS Controls v8.1', 'IG1', 'IG2', 'IG3', 'NIST SP 800-53 Rev. 5', '800-53B', 'crosswalk']
        for termo in termos:
            self.assertIn(termo, content, f'Termo obrigatório ausente: {termo}')

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn('ISO-27001-e-27002/treinamento-iso-27001-e-27002.html', content)
        self.assertIn('data-slug="ISO-27001-e-27002"', content)
        self.assertIn(f'/ {len(ESTUDOS_DADOS)}', content)
if __name__ == '__main__':
    unittest.main()
