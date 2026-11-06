"""
test_pci_dss.py
Testes automatizados para o Estudo 31: PCI-DSS
"""
import json
import re
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from index_dados import ESTUDOS_DADOS
ARQUITETURAS = ['proprio', 'javascript', 'iframe']
CATEGORIAS = {'cde', 'conectado', 'fora', 'terceiro'}
EM_ESCOPO = {'cde', 'conectado'}

def saq(arquitetura, sistemas):
    proprios_com_pan = [s for s in sistemas if not s['terceiro'] and s['por_arquitetura'][arquitetura['id']]['pan']]
    if proprios_com_pan:
        return 'D'
    return 'A-EP' if arquitetura['captura_no_site'] else 'A'

class TestPciDss(unittest.TestCase):
    """Valida a estrutura, o conteúdo, a regra de escopo e a compilação do estudo PCI-DSS."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / '_geradores' / 'pci_dss_body.html'
        self.compiled_path = self.root / 'PCI-DSS' / 'treinamento-pci-dss.html'
        self.portal_path = self.root / 'index.html'

    def _categorias(self, d, arq_id):
        return {s['id']: classificar(s, s['por_arquitetura'][arq_id]) for s in d['sistemas']}

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        termos = ['PCI DSS v4.0.1', 'PCI SSC', '31/03/2025', 'PAN', 'SAD', 'CVV2', 'tokenização', 'truncamento', 'mascaramento', '3.5.1.1', 'CDE', 'segmentação', '11.4.5', '12.5.2', '12.8', 'TPSP', 'SAQ A-EP', 'SAQ D', 'B-IP', 'C-VT', 'P2PE', 'ROC', 'AOC', 'QSA', 'ISA', 'ASV', 'abordagem definida', 'abordagem customizada', '12.3.1', '8.4.2', '8.3.6', '5.4.1', '6.4.3', '11.6.1', '10.4.1.1', 'Nível 1']
        for termo in termos:
            self.assertIn(termo, content, f'Termo obrigatório ausente: {termo}')

    def test_doze_requisitos_e_seis_objetivos(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        numeros = sorted((int(n) for n in re.findall('data-requisito="(\\d+)"', content)))
        self.assertEqual(numeros, list(range(1, 13)))
        self.assertEqual(len(set(re.findall('data-objetivo="(\\d+)"', content))), 6)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn('PCI-DSS/treinamento-pci-dss.html', content)
        self.assertIn('data-slug="PCI-DSS"', content)
        self.assertIn(f'/ {len(ESTUDOS_DADOS)}', content)
if __name__ == '__main__':
    unittest.main()
