"""
test_redes_protocolos.py
Testes automatizados para o Estudo 02: Redes-e-Protocolos
"""
import ipaddress
import re
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from index_dados import ESTUDOS_DADOS

class TestRedesProtocolos(unittest.TestCase):
    """Valida a estrutura, conteúdo e compilação do estudo Redes-e-Protocolos."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / '_geradores' / 'redes_e_protocolos_body.html'
        self.compiled_path = self.root / 'Redes-e-Protocolos' / 'treinamento-redes-e-protocolos.html'
        self.portal_path = self.root / 'index.html'

    def test_body_and_compiled_files_exist(self):
        """Verifica se o fragmento body e o treinamento final compilado existem."""
        self.assertTrue(self.body_path.exists(), 'O arquivo _geradores/redes_e_protocolos_body.html deve existir.')
        self.assertTrue(self.compiled_path.exists(), 'O arquivo Redes-e-Protocolos/treinamento-redes-e-protocolos.html deve existir.')

    def test_teoria_e_conceitos_fundamentais(self):
        """Verifica se os conceitos obrigatórios da pilha TCP/IP e protocolos estão presentes."""
        self.assertTrue(self.compiled_path.exists())
        content = self.compiled_path.read_text(encoding='utf-8')
        termos_obrigatorios = ['TCP/IP', 'Modelo OSI', 'Encapsulamento', 'Handshake', 'IPv4', 'IPv6', 'DNS', 'ARP', 'SYN', 'ACK', 'FIN', 'RST']
        for termo in termos_obrigatorios:
            self.assertIn(termo, content, f"O termo obrigatório '{termo}' deve estar presente no conteúdo.")

    def test_integracao_com_portal_index(self):
        """Verifica se o portal index.html aponta Redes-e-Protocolos como Disponível com link ativo."""
        self.assertTrue(self.portal_path.exists())
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn('Redes-e-Protocolos/treinamento-redes-e-protocolos.html', content)
        self.assertIn('data-slug="Redes-e-Protocolos"', content)
        self.assertIn(f'/ {len(ESTUDOS_DADOS)}', content)
        self.assertIn('Módulos Compilados', content)

    def _body(self):
        return self.body_path.read_text(encoding='utf-8')

    def test_questoes_e_referencias_novas(self):
        body = self._body()
        self.assertGreaterEqual(body.count('class="quiz-item"'), 5)
        m = re.search('id="fatos-essenciais".*?</section>', body, re.S)
        for termo in ['RFC 4632', 'RFC 1918', 'RFC 9110', 'IEEE 802.11', 'WPA3']:
            self.assertIn(termo, m.group(0))
if __name__ == '__main__':
    unittest.main()
