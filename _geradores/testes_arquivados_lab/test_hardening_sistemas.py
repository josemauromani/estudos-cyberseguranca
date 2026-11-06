"""
test_hardening_sistemas.py
Testes automatizados para o Estudo 06: Hardening-Sistemas
"""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from index_dados import ESTUDOS_DADOS

class TestHardeningSistemas(unittest.TestCase):
    """Valida a estrutura, conteúdo e compilação do estudo Hardening-Sistemas."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / '_geradores' / 'hardening_sistemas_body.html'
        self.compiled_path = self.root / 'Hardening-Sistemas' / 'treinamento-hardening-sistemas.html'
        self.portal_path = self.root / 'index.html'

    def test_body_and_compiled_files_exist(self):
        """Verifica se o fragmento body e o treinamento final compilado existem."""
        self.assertTrue(self.body_path.exists(), 'O arquivo _geradores/hardening_sistemas_body.html deve existir.')
        self.assertTrue(self.compiled_path.exists(), 'O arquivo Hardening-Sistemas/treinamento-hardening-sistemas.html deve existir.')

    def test_teoria_e_conceitos_fundamentais(self):
        """Verifica se os conceitos obrigatórios de CIS Benchmarks, sshd, sysctl, SELinux, LSASS e Windows hardening estão presentes."""
        self.assertTrue(self.compiled_path.exists())
        content = self.compiled_path.read_text(encoding='utf-8')
        termos_obrigatorios = ['CIS Benchmarks', 'Nível 1', 'Nível 2', 'sshd_config', 'PermitRootLogin', 'sysctl.conf', 'tcp_syncookies', 'ASLR', 'SELinux', 'AppArmor', 'LSASS', 'Credential Guard', 'SMBv1']
        for termo in termos_obrigatorios:
            self.assertIn(termo, content, f"O termo obrigatório '{termo}' deve estar presente no conteúdo.")

    def test_integracao_com_portal_index(self):
        """Verifica se o portal index.html aponta Hardening-Sistemas como Disponível com link ativo."""
        self.assertTrue(self.portal_path.exists())
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn('Hardening-Sistemas/treinamento-hardening-sistemas.html', content)
        self.assertIn('data-slug="Hardening-Sistemas"', content)
        self.assertIn(f'/ {len(ESTUDOS_DADOS)}', content)
        self.assertIn('Módulos Compilados', content)
if __name__ == '__main__':
    unittest.main()
