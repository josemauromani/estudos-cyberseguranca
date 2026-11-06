"""
test_forense_digital.py
Testes automatizados para o Estudo 19: Forense-Digital
"""
import hashlib
import ipaddress
import json
import re
import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from index_dados import ESTUDOS_DADOS
FUSOS = {'UTC': 0, 'UTC-3': 3}
FMT = '%Y-%m-%d %H:%M:%S'

def utc(evento):
    """Normaliza o horário armazenado para UTC (espelhado no JavaScript)."""
    t = datetime.strptime(evento['ts_armazenado'], FMT)
    return t + timedelta(hours=FUSOS[evento['fuso']])

class TestForenseDigital(unittest.TestCase):
    """Valida a estrutura, o conteúdo, a timeline, a integridade e a compilação do estudo Forense-Digital."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / '_geradores' / 'forense_digital_body.html'
        self.compiled_path = self.root / 'Forense-Digital' / 'treinamento-forense-digital.html'
        self.portal_path = self.root / 'index.html'

    def _pergunta(self, d, pid):
        return next((p for p in d['perguntas'] if p['id'] == pid))

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        termos = ['ISO/IEC 27037', 'RFC 3227', 'ordem de volatilidade', 'cadeia de custódia', '158-A', 'Lei 13.964/2019', 'bloqueador de escrita', 'SHA-256', 'E01', 'Prefetch', 'Amcache', 'Shimcache', '$MFT', '$STANDARD_INFORMATION', '$FILE_NAME', 'timestomping', 'T1070.006', '$UsnJrnl', 'LNK', 'Registro', 'T1547.001', '7045', 'Plaso', 'Timesketch', 'Volatility', 'UTC', 'BitLocker']
        for termo in termos:
            self.assertIn(termo, content, f'Termo obrigatório ausente: {termo}')

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn('Forense-Digital/treinamento-forense-digital.html', content)
        self.assertIn('data-slug="Forense-Digital"', content)
        self.assertIn(f'/ {len(ESTUDOS_DADOS)}', content)
if __name__ == '__main__':
    unittest.main()
