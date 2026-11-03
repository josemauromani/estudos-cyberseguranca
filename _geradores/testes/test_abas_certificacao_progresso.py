#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testes das visões "Por certificação" e "Meu progresso" do portal."""

import re
import sys
import tempfile
import unittest
from pathlib import Path

GERADORES_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GERADORES_DIR))

from index_dados import CERTIFICACOES, ESTUDOS_DADOS  # noqa: E402

from build_index import gerar_index_html, render_painel_certificacoes  # noqa: E402


def numero(slug):
    return list(ESTUDOS_DADOS).index(slug) + 1


def visao(html, nome):
    """Trecho do HTML da visão <section class="view" data-view="nome">."""
    ini = html.index(f'<section class="view" data-view="{nome}"')
    fim = html.find('<section class="view" ', ini + 1)
    return html[ini:fim if fim != -1 else html.index("</main>")]


class TestAbasCertificacaoProgresso(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as tmp:
            cls.html = gerar_index_html(output_path=Path(tmp) / "index.html").read_text(encoding="utf-8")

    def test_visoes_no_menu(self):
        self.assertRegex(self.html, r'<a href="#v-certificacoes" data-view="certificacoes">[^<]*Por certificação')
        self.assertRegex(self.html, r'<a href="#v-progresso" data-view="progresso">[^<]*Meu progresso')

    def test_meu_progresso_lista_todos_com_checkbox(self):
        prog = visao(self.html, "progresso")
        for slug in ESTUDOS_DADOS:
            self.assertIn(f'<input type="checkbox" data-slug="{slug}"', prog)
        self.assertIn(f"0 de {len(ESTUDOS_DADOS)} concluídos", prog)
        self.assertIn('id="zerar-progresso"', prog)

    def test_um_painel_por_certificacao_na_visao(self):
        cert = visao(self.html, "certificacoes")
        for c in CERTIFICACOES:
            self.assertIn(f'<div class="rota-sugerida" data-rota="{c["sigla"]}"', cert)

    def test_cards_marcam_as_certificacoes(self):
        for slug in ESTUDOS_DADOS:
            esperado = [c["sigla"] for c in CERTIFICACOES if slug in c["modulos"]]
            m = re.search(rf'id="estudo-{re.escape(slug)}"[^>]*?data-certs="([^"]*)"', self.html, re.S)
            with self.subTest(slug=slug):
                self.assertIsNotNone(m)
                # Separador "|", como em data-perfis: siglas como "ITIL 4 F" têm espaço.
                self.assertEqual([x for x in m.group(1).split("|") if x], esperado)

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

    def test_painel_e_matriz_na_visao_certificacoes(self):
        cert = visao(self.html, "certificacoes")
        self.assertIn('<section class="rota-sugerida-section" id="secao-cert-painel"', cert)
        self.assertIn('id="secao-certificacoes"', cert)
        self.assertIn('<section class="view" data-view="certificacoes" hidden>', self.html)


if __name__ == "__main__":
    unittest.main()
