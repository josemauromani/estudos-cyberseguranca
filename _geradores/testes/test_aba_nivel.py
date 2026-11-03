#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testes do nível dos módulos: dados, selo no cartão e agrupamento "Nível" do catálogo."""

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
AVANCADOS = {14, 19, 20, 23, 24, 39, 46, 47, 48, 49, 50, 51, 52, 53, 60}


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

    def test_agrupar_por_nivel(self):
        """A aba "Por Nível" virou o botão "Nível" da barra "Agrupar por" do catálogo."""
        self.assertRegex(self.html, r'<button type="button" data-grupo="nivel"[^>]*>Nível</button>')
        for chave in NIVEIS:
            self.assertIn(f'data-nivel="{chave}"', self.html)

    def test_cards_com_nivel_e_selo(self):
        for slug, d in ESTUDOS_DADOS.items():
            m = re.search(rf'id="estudo-{re.escape(slug)}"[^>]*?data-nivel="([^"]*)"', self.html, re.S)
            with self.subTest(slug=slug):
                self.assertIsNotNone(m)
                self.assertEqual(m.group(1), d["nivel"])
        self.assertEqual(self.html.count('class="tag tag-nivel"'), len(ESTUDOS_DADOS))

    def test_css_colore_grupos_de_nivel(self):
        css = (GERADORES_DIR / "index.css").read_text(encoding="utf-8")
        for chave in NIVEIS:
            self.assertIn(f'.grupo[data-nivel="{chave}"]', css)


if __name__ == "__main__":
    unittest.main()
