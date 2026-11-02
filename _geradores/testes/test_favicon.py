#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
        return [self.root / "index.html"] + sorted(self.root.glob("*/treinamento-*.html"))

    def test_todas_as_paginas_tem_icone_embutido(self):
        paginas = self._paginas()
        self.assertEqual(len(paginas), 46, "portal + 45 módulos")
        for p in paginas:
            with self.subTest(pagina=p.parent.name if p.name != "index.html" else "portal"):
                html = p.read_text(encoding="utf-8")
                cabeca = html[:html.index("</head>")]
                self.assertIn('<link rel="icon" href="data:image/svg+xml,', cabeca)


if __name__ == "__main__":
    unittest.main()
