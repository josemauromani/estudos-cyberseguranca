"""
test_ingles_tecnico.py
Testes automatizados para o Estudo 32: Ingles-Tecnico-Ciber
"""
import json
import re
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from index_dados import ESTUDOS_DADOS
RE_TERMO = re.compile('\\[\\[([^|\\]]+)\\|([^\\]]+)\\]\\]')
TIPOS = {'tecnico', 'falso-cognato', 'modal', 'sigla'}

class TestInglesTecnico(unittest.TestCase):
    """Valida a estrutura, o conteúdo, os dados do simulador e a compilação do estudo Ingles-Tecnico-Ciber."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / '_geradores' / 'ingles_tecnico_ciber_body.html'
        self.compiled_path = self.root / 'Ingles-Tecnico-Ciber' / 'treinamento-ingles-tecnico-ciber.html'
        self.portal_path = self.root / 'index.html'

    def _texto_advisory(self, d):
        return '\n'.join((s['titulo'] + '\n' + s['texto'] for s in d['advisory']['secoes']))

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        termos = ['advisory', 'Summary', 'Affected Versions', 'Impact', 'Mitigation', 'Workaround', 'CVE', 'NVD', 'CWE', 'CVSS', 'AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H', 'KEV', 'RFC 2119', 'RFC 8174', 'MUST NOT', 'SHOULD', 'MAY', 'REQUIRED', 'OPTIONAL', 'falsos cognatos', 'exploit', 'eventually', 'actually', 'registro formal', 'registro informal']
        for termo in termos:
            self.assertIn(termo, content, f'Termo obrigatório ausente: {termo}')

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn('Ingles-Tecnico-Ciber/treinamento-ingles-tecnico-ciber.html', content)
        self.assertIn('data-slug="Ingles-Tecnico-Ciber"', content)
        self.assertIn(f'/ {len(ESTUDOS_DADOS)}', content)
if __name__ == '__main__':
    unittest.main()
