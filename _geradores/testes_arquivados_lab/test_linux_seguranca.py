"""
test_linux_seguranca.py
Testes automatizados para o Estudo 34: Linux-para-Seguranca
"""
import ipaddress
import json
import re
import sys
import unittest
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from index_dados import ESTUDOS_DADOS
RE_FALHA = re.compile('Failed password for (?:invalid user )?\\S+ from (\\S+) port')
RE_SUCESSO = re.compile('Accepted password for (\\S+) from (\\S+) port')

class TestLinuxSeguranca(unittest.TestCase):
    """Valida a estrutura, o conteúdo, o sistema de arquivos e a compilação do estudo Linux-para-Seguranca."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / '_geradores' / 'linux_para_seguranca_body.html'
        self.compiled_path = self.root / 'Linux-para-Seguranca' / 'treinamento-linux-para-seguranca.html'
        self.portal_path = self.root / 'index.html'

    def _auth(self, d):
        return d['fs']['/var/log/auth.log']['conteudo'].split('\n')

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        termos = ['FHS', '/etc/passwd', '/etc/shadow', 'SUID', 'SGID', 'sticky bit', 'umask', 'chmod', 'sudoers', 'NOPASSWD', 'GTFOBins', 'auth.log', '/var/log/secure', 'journalctl', 'ps aux', 'ss -tlnp', 'lsof', 'crontab', '/etc/cron.d', 'systemd', 'authorized_keys', 'yescrypt', 'T1548.001', 'T1053.003', 'T1110', 'T1543.002', 'T1098.004']
        for termo in termos:
            self.assertIn(termo, content, f'Termo obrigatório ausente: {termo}')

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn('Linux-para-Seguranca/treinamento-linux-para-seguranca.html', content)
        self.assertIn('data-slug="Linux-para-Seguranca"', content)
        self.assertIn(f'/ {len(ESTUDOS_DADOS)}', content)
if __name__ == '__main__':
    unittest.main()
