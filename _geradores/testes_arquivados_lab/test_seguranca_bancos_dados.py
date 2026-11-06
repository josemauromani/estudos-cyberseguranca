"""
test_seguranca_bancos_dados.py
Testes automatizados para o Estudo 30: Seguranca-de-Bancos-de-Dados
"""
import json
import re
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from index_dados import ESTUDOS_DADOS
PRIVS = {'SELECT', 'INSERT', 'UPDATE', 'DELETE'}

class TestSegurancaBancosDados(unittest.TestCase):
    """Valida a estrutura, o conteúdo e a compilação do estudo Seguranca-de-Bancos-de-Dados."""

    def _permitida(politica, role, acao, tabela):
        return acao in politica.get(role, {}).get(tabela, [])

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        termos = ['ACID', 'DDL', 'DML', 'DCL', 'GRANT', 'REVOKE', 'PUBLIC', 'PostgreSQL 15', 'Row-Level Security', 'CREATE POLICY', 'pgAudit', 'SQL Server Audit', 'Database Activity Monitoring', 'TDE', 'pgcrypto', 'Dynamic Data Masking', 'prepared statements', 'CIS Benchmarks', 'scram-sha-256', 'OWASP']
        for termo in termos:
            self.assertIn(termo, content, f'Termo obrigatório ausente: {termo}')
if __name__ == '__main__':
    unittest.main()
