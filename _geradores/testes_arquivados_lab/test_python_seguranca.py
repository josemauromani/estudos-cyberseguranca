"""
test_python_seguranca.py
Testes automatizados para o Estudo 35: Python-para-Seguranca
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from index_dados import ESTUDOS_DADOS

def literal_regex(p):
    barras_finais = len(p) - len(p.rstrip('\\'))
    if '\n' not in p and barras_finais % 2 == 0:
        if '"' not in p:
            return 'r"' + p + '"'
        if "'" not in p:
            return "r'" + p + "'"
    return json.dumps(p, ensure_ascii=False)

def literal_texto(s):
    if '"' in s and "'" not in s and ('\\' not in s) and ('\n' not in s):
        return "'" + s + "'"
    return json.dumps(s, ensure_ascii=False)

def grupos(p):
    return re.findall('\\(\\?P<([A-Za-z_]\\w*)>', p)

def executar_script(d, codigo):
    with tempfile.TemporaryDirectory() as pasta:
        for nome, linhas in d['logs'].items():
            Path(pasta, nome).write_text('\n'.join(linhas) + '\n', encoding='utf-8')
        Path(pasta, 'detector.py').write_text(codigo, encoding='utf-8')
        amb = {k: v for k, v in os.environ.items() if k != 'ABUSEIPDB_KEY'}
        amb['PYTHONIOENCODING'] = 'utf-8'
        r = subprocess.run([sys.executable, '-I', 'detector.py'], cwd=pasta, capture_output=True, text=True, encoding='utf-8', env=amb, timeout=30)
        if r.returncode != 0:
            raise AssertionError('o script gerado falhou:\n' + r.stderr)
        return r.stdout

class TestPythonSeguranca(unittest.TestCase):
    """Valida a estrutura, o conteúdo, o gerador de código, os logs e a compilação do estudo Python-para-Seguranca."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / '_geradores' / 'python_para_seguranca_body.html'
        self.compiled_path = self.root / 'Python-para-Seguranca' / 'treinamento-python-para-seguranca.html'
        self.portal_path = self.root / 'index.html'

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        termos = ['re.search', 're.match', 're.finditer', 're.compile', '(?P&lt;', 'quantificador', 'âncora', 'Counter', 'most_common', 'requests', 'timeout', 'raise_for_status', '429', 'Retry-After', 'variável de ambiente', 'AbuseIPDB', 'VirusTotal', 'JSON', 'CSV', 'T1059.006', 'invalid user', 'Estudo 34', 'web-loja01']
        for termo in termos:
            self.assertIn(termo, content, f'Termo obrigatório ausente: {termo}')

    def test_literais_seguros(self):
        for p in ['a"b', "a'b", 'a"\'b', 'fim\\', 'fim\\\\', 'simples']:
            with self.subTest(padrao=p):
                self.assertEqual(eval(literal_regex(p)), p)
        for s in ['" 404 ', 'Failed password', 'a\'b"c']:
            self.assertEqual(eval(literal_texto(s)), s)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn('Python-para-Seguranca/treinamento-python-para-seguranca.html', content)
        self.assertIn('data-slug="Python-para-Seguranca"', content)
        self.assertIn(f'/ {len(ESTUDOS_DADOS)}', content)
if __name__ == '__main__':
    unittest.main()
