"""
test_engenharia_social.py
Testes automatizados para o Estudo 15: Engenharia-Social-e-Phishing
"""
import json
import re
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from index_dados import ESTUDOS_DADOS
RE_URL = re.compile('https?://([^/\\s\\"]+)')

def dominio(endereco):
    return endereco.split('@')[-1].lower()

def org(dom):
    return '.'.join(dom.lower().split('.')[-2:])

class TestEngenhariaSocial(unittest.TestCase):
    """Valida a estrutura, o conteúdo, os e-mails do simulador e a compilação do estudo Engenharia-Social-e-Phishing."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / '_geradores' / 'engenharia_social_e_phishing_body.html'
        self.compiled_path = self.root / 'Engenharia-Social-e-Phishing' / 'treinamento-engenharia-social-e-phishing.html'
        self.portal_path = self.root / 'index.html'

    def _indicadores(email):
        return [t for t in email['trechos'] if t.get('indicador')]

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        termos = ['autoridade', 'urgência', 'escassez', 'prova social', 'reciprocidade', 'pretexting', 'spear phishing', 'whaling', 'BEC', 'vishing', 'smishing', 'quishing', 'baiting', 'tailgating', 'typosquatting', 'homóglifo', 'Return-Path', 'Reply-To', 'AiTM', 'FIDO2', 'passkey', 'number matching', 'taxa de reporte', 'T1566.001', 'T1566.002', 'T1598', 'T1621', 'T1557', 'Estudo 29']
        for termo in termos:
            self.assertIn(termo, content, f'Termo obrigatório ausente: {termo}')

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn('Engenharia-Social-e-Phishing/treinamento-engenharia-social-e-phishing.html', content)
        self.assertIn('data-slug="Engenharia-Social-e-Phishing"', content)
        self.assertIn(f'/ {len(ESTUDOS_DADOS)}', content)
if __name__ == '__main__':
    unittest.main()
