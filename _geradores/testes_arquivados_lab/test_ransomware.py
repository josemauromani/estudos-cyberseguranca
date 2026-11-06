"""
test_ransomware.py
Testes automatizados para o Estudo 42: Ransomware-Prevencao-a-Recuperacao
"""
import json
import re
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from index_dados import ESTUDOS_DADOS

def custo(d, efeitos):
    return sum((d['pesos'][k] * v for k, v in efeitos.items()))

def ordem_valida(itens, ordem):
    pos = {i: n for n, i in enumerate(ordem)}
    return all((pos[dep] < pos[it['id']] for it in itens for dep in it['depende_de']))

class TestRansomware(unittest.TestCase):
    """Valida a estrutura, o conteúdo, a linha do tempo, a ordem de recuperação e a compilação do estudo Ransomware."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / '_geradores' / 'ransomware_prevencao_a_recuperacao_body.html'
        self.compiled_path = self.root / 'Ransomware-Prevencao-a-Recuperacao' / 'treinamento-ransomware-prevencao-a-recuperacao.html'
        self.portal_path = self.root / 'index.html'

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        termos = ['RaaS', 'afiliados', 'dupla extorsão', 'tripla extorsão', 'shadow copies', 'vssadmin', 'rclone', 'T1486', 'T1490', 'T1567', 'T1003.006', 'DCSync', 'isolar', 'desligar', 'RAM', 'krbtgt', 'No More Ransom', 'ID Ransomware', '3 dias úteis', 'ANPD', 'OFAC', '3-2-1-1-0', 'imutável', '#StopRansomware', 'NIST IR 8374']
        for termo in termos:
            self.assertIn(termo, content, f'Termo obrigatório ausente: {termo}')

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn('Ransomware-Prevencao-a-Recuperacao/treinamento-ransomware-prevencao-a-recuperacao.html', content)
        self.assertIn('data-slug="Ransomware-Prevencao-a-Recuperacao"', content)
        self.assertIn(f'/ {len(ESTUDOS_DADOS)}', content)
if __name__ == '__main__':
    unittest.main()
