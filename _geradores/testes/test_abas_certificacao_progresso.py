#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testes das abas "Por Certificação" e "Meu Progresso" do portal."""

import re
import sys
import tempfile
import unittest
from pathlib import Path

GERADORES_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GERADORES_DIR))

from index_dados import CERTIFICACOES, ESTUDOS_DADOS  # noqa: E402

from build_index import gerar_index_html, render_filtros_certificacao, render_painel_certificacoes  # noqa: E402


def numero(slug):
    return list(ESTUDOS_DADOS).index(slug) + 1


class TestAbasCertificacaoProgresso(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as tmp:
            cls.html = gerar_index_html(output_path=Path(tmp) / "index.html").read_text(encoding="utf-8")

    def test_abas_novas(self):
        self.assertIn('data-facet="certs" onclick="switchTab(\'certs\')">Por Certificação</button>', self.html)
        self.assertIn('data-facet="progresso" onclick="switchTab(\'progresso\')">Meu Progresso</button>', self.html)
        self.assertIn('<div class="filter-subpanel" data-panel="certs"', self.html)
        self.assertIn('<div class="filter-subpanel" data-panel="progresso"', self.html)
        for valor in ("concluidos", "a_estudar"):
            self.assertIn(f'data-value="{valor}"', self.html)

    def test_botoes_das_certificacoes(self):
        botoes = render_filtros_certificacao(CERTIFICACOES)
        self.assertIn('data-value="all"', botoes)
        for c in CERTIFICACOES:
            self.assertIn(f'data-value="{c["sigla"]}"', botoes)

    def test_cards_marcam_as_certificacoes(self):
        for slug in ESTUDOS_DADOS:
            esperado = [c["sigla"] for c in CERTIFICACOES if slug in c["modulos"]]
            m = re.search(rf'id="estudo-{re.escape(slug)}"[^>]*?data-certs="([^"]*)"', self.html, re.S)
            with self.subTest(slug=slug):
                self.assertIsNotNone(m)
                self.assertEqual(m.group(1).split(), esperado)

    def test_painel_da_certificacao_em_ordem_numerica_com_link(self):
        status = {s: {"disponivel": True, "caminho_relativo": f"{s}/x.html"} for s in ESTUDOS_DADOS}
        painel = render_painel_certificacoes(CERTIFICACOES, status)
        self.assertIn('id="secao-cert-painel"', painel)
        for c in CERTIFICACOES:
            bloco = re.search(rf'<div class="rota-sugerida" data-rota="{re.escape(c["sigla"])}".*?</ol>', painel, re.S)
            with self.subTest(cert=c["sigla"]):
                self.assertIsNotNone(bloco)
                passos = re.findall(r'<li class="rota-passo" data-slug="([^"]+)"', bloco.group(0))
                self.assertEqual(passos, sorted(c["modulos"], key=numero))
                self.assertIn(c["orgao"], bloco.group(0))
                self.assertIn('class="rota-progresso-texto"', bloco.group(0))
                self.assertIn('class="rota-proximo"', bloco.group(0))

    def test_painel_da_certificacao_comeca_oculto(self):
        self.assertIn('<section class="rota-sugerida-section" id="secao-cert-painel" hidden', self.html)
        self.assertLess(self.html.index('id="secao-cert-painel"'), self.html.index('id="secao-catalogo"'))

    def test_javascript_dos_filtros(self):
        self.assertIn("currentFacet === 'certs'", self.html)
        self.assertIn("currentFacet === 'progresso'", self.html)
        self.assertIn("data-certs", self.html)
        self.assertIn('id="no-results-texto"', self.html)
        self.assertIn("ainda não marcou nenhum módulo como concluído", self.html)


if __name__ == "__main__":
    unittest.main()
