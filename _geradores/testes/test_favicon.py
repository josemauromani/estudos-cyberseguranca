"""
test_favicon.py
Todas as páginas declaram um ícone embutido, para o navegador não pedir /favicon.ico (404 no site publicado).
"""
import unittest
from pathlib import Path

class TestFavicon(unittest.TestCase):

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent

    def _paginas(self):
        return [self.root / 'index.html'] + sorted(self.root.glob('*/treinamento-*.html'))

    def test_todas_as_paginas_tem_icone_embutido(self):
        paginas = self._paginas()
        catalogo = [linha.split('|') for linha in (self.root / '_geradores' / 'estudos.txt').read_text(encoding='utf-8').splitlines() if linha.strip() and (not linha.startswith('#'))]
        compilados = [c for c in catalogo if (self.root / c[2] / c[3]).exists()]
        self.assertEqual(len(paginas), 1 + len(compilados), 'portal + módulos do catálogo já compilados, sem páginas avulsas')
        for p in paginas:
            with self.subTest(pagina=p.parent.name if p.name != 'index.html' else 'portal'):
                html = p.read_text(encoding='utf-8')
                cabeca = html[:html.index('</head>')]
                self.assertIn('<link rel="icon" href="data:image/svg+xml,', cabeca)
if __name__ == '__main__':
    unittest.main()
