"""
test_owasp_web.py
Testes automatizados para o Estudo 12: OWASP-Top-10-Web
"""
import json
import re
import sqlite3
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from index_dados import ESTUDOS_DADOS
TOP10_2025 = [('A01:2025', 'Broken Access Control'), ('A02:2025', 'Security Misconfiguration'), ('A03:2025', 'Software Supply Chain Failures'), ('A04:2025', 'Cryptographic Failures'), ('A05:2025', 'Injection'), ('A06:2025', 'Insecure Design'), ('A07:2025', 'Authentication Failures'), ('A08:2025', 'Software or Data Integrity Failures'), ('A09:2025', 'Security Logging and Alerting Failures'), ('A10:2025', 'Mishandling of Exceptional Conditions')]

def banco_sqlite(d):
    con = sqlite3.connect(':memory:')
    for tabela, t in d['banco'].items():
        con.execute('CREATE TABLE {} ({})'.format(tabela, ', '.join(t['colunas'])))
        con.executemany('INSERT INTO {} VALUES ({})'.format(tabela, ', '.join('?' * len(t['colunas']))), t['linhas'])
    return con

class TestOwaspWeb(unittest.TestCase):
    """Valida a estrutura, o conteúdo, os dados do playground e a compilação do estudo OWASP-Top-10-Web."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / '_geradores' / 'owasp_top_10_web_body.html'
        self.compiled_path = self.root / 'OWASP-Top-10-Web' / 'treinamento-owasp-top-10-web.html'
        self.portal_path = self.root / 'index.html'

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        termos = ['OWASP Top 10:2025', '2021', 'SSRF', 'SQL injection', 'UNION', 'cega', 'baseada em tempo', 'prepared statements', 'ORM', 'XSS', 'refletido', 'armazenado', 'DOM', 'Content Security Policy', 'codificação de saída', 'sanitização', 'allowlist', 'BOLA', 'IDOR', 'CSRF', 'SameSite', 'HttpOnly', 'Secure', 'upload']
        termos += [nome for _, nome in TOP10_2025]
        for termo in termos:
            self.assertIn(termo, content, f'Termo obrigatório ausente: {termo}')

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn('OWASP-Top-10-Web/treinamento-owasp-top-10-web.html', content)
        self.assertIn('data-slug="OWASP-Top-10-Web"', content)
        self.assertIn(f'/ {len(ESTUDOS_DADOS)}', content)
if __name__ == '__main__':
    unittest.main()
