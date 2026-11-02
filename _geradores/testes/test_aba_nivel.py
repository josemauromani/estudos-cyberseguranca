#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testes da aba "Por Nível": nível de cada módulo, selo no card e filtro."""

import re
import sys
import tempfile
import unittest
from pathlib import Path

GERADORES_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GERADORES_DIR))

from index_dados import ESTUDOS_DADOS, NIVEIS  # noqa: E402

from build_index import gerar_index_html  # noqa: E402

INICIANTES = {1, 2, 3, 4, 5, 15, 27, 32, 33, 34, 37, 38}
AVANCADOS = {14, 19, 20, 23, 24, 39, 46, 47, 48, 49, 50, 51, 52, 53}


def numero(slug):
    return list(ESTUDOS_DADOS).index(slug) + 1


class TestNivelDosModulos(unittest.TestCase):
    def test_niveis_definidos(self):
        self.assertEqual(list(NIVEIS), ["iniciante", "intermediario", "avancado"])

    def test_todo_modulo_tem_nivel_valido(self):
        for slug, d in ESTUDOS_DADOS.items():
            with self.subTest(slug=slug):
                self.assertIn(d.get("nivel"), NIVEIS)

    def test_classificacao_aprovada(self):
        for slug, d in ESTUDOS_DADOS.items():
            n = numero(slug)
            esperado = "iniciante" if n in INICIANTES else "avancado" if n in AVANCADOS else "intermediario"
            with self.subTest(modulo=n):
                self.assertEqual(d["nivel"], esperado)


class TestHtmlDoNivel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as tmp:
            cls.html = gerar_index_html(output_path=Path(tmp) / "index.html").read_text(encoding="utf-8")

    def test_aba_e_botoes(self):
        self.assertIn('data-facet="nivel" onclick="switchTab(\'nivel\')">Por Nível</button>', self.html)
        self.assertIn('<div class="filter-subpanel" data-panel="nivel"', self.html)
        for chave in NIVEIS:
            self.assertIn(f'data-value="{chave}"', self.html)

    def test_cards_com_nivel_e_selo(self):
        for slug, d in ESTUDOS_DADOS.items():
            m = re.search(rf'id="estudo-{re.escape(slug)}"[^>]*?data-nivel="([^"]*)"', self.html, re.S)
            with self.subTest(slug=slug):
                self.assertIsNotNone(m)
                self.assertEqual(m.group(1), d["nivel"])
        self.assertEqual(self.html.count('class="badge badge-nivel'), len(ESTUDOS_DADOS))

    def test_javascript_filtra_por_nivel(self):
        self.assertIn("currentFacet === 'nivel'", self.html)


if __name__ == "__main__":
    unittest.main()
