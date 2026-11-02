#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Estrutura do portal (T9): barra superior, menu lateral com seis visões, catálogo
como tela inicial, cartões novos e o contrato de marcação lido pelo JS do portal (T10)."""

import re
import sys
import tempfile
import unittest
from html import escape
from pathlib import Path

GERADORES_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GERADORES_DIR))

from index_dados import ESTUDOS_DADOS, NIVEIS, TRILHAS  # noqa: E402

from build_index import contar_secoes, gerar_index_html  # noqa: E402
from contrato import extrair_secoes  # noqa: E402

INDEX_CSS = GERADORES_DIR / "index.css"


def _cartao(html, slug):
    """Tag de abertura do cartão do catálogo do módulo."""
    m = re.search(rf'<a class="mc[^"]*" id="estudo-{re.escape(slug)}"[^>]*>', html)
    return m.group(0) if m else None


class TestPortal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as tmp:
            cls.html = gerar_index_html(output_path=Path(tmp) / "index.html").read_text(encoding="utf-8")

    # ---- Testes do brief (verbatim) -------------------------------------
    def test_menu_com_seis_visoes(self):
        self.assertEqual(re.findall(r'<a [^>]*data-view="(\w+)"', self.html),
                         ["catalogo", "rotas", "certificacoes", "necessidades", "vaga", "progresso"])

    def test_so_catalogo_visivel_na_carga(self):
        visiveis = re.findall(r'<section class="view" data-view="(\w+)">', self.html)
        self.assertEqual(visiveis, ["catalogo"])

    def test_um_cartao_por_modulo_com_total_de_secoes(self):
        for slug in ESTUDOS_DADOS:
            self.assertRegex(self.html, rf'data-slug="{slug}"[^>]*data-secoes="{contar_secoes(slug)}"')

    def test_textos_que_os_testes_de_modulo_exigem(self):
        self.assertIn("Módulos Compilados", self.html)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", self.html)

    def test_abas_antigas_removidas(self):
        for velho in ("switchTab(", 'data-facet="', "Estudo Concluído"):
            self.assertNotIn(velho, self.html)

    def test_sem_google_fonts_e_com_tokens(self):
        self.assertNotIn("fonts.googleapis.com", self.html)
        self.assertIn("--tipo-teoria", self.html)

    def test_index_css_nao_declara_tokens(self):
        self.assertNotRegex(INDEX_CSS.read_text(encoding="utf-8"), r"^\s*--ground\s*:", re.M)

    # ---- Contrato de marcação para T10 ---------------------------------
    def test_visoes_ocultas_com_hidden(self):
        ocultas = re.findall(r'<section class="view" data-view="(\w+)" hidden>', self.html)
        self.assertEqual(ocultas, ["rotas", "certificacoes", "necessidades", "vaga", "progresso"])

    def test_menu_lateral_e_botao_da_gaveta(self):
        self.assertRegex(self.html, r'<nav class="menu-lateral" [^>]*aria-label="[^"]+"')
        self.assertRegex(self.html, r'<button class="menu-toggle" [^>]*aria-expanded="false"')
        self.assertLess(self.html.index('class="menu-toggle"'), self.html.index('class="menu-lateral"'))
        nav = self.html[self.html.index('<nav class="menu-lateral"'):self.html.index("</nav>")]
        self.assertIn('data-view="catalogo" aria-current="page"', nav)
        self.assertEqual(nav.count("aria-current"), 1)

    def test_fontes_e_tokens_embutidos_antes_do_css_do_portal(self):
        i_fonte = self.html.index("@font-face")
        i_token = self.html.index("--tipo-teoria:")
        i_portal = self.html.index(".menu-lateral")
        self.assertLess(i_fonte, i_token)
        self.assertLess(i_token, i_portal)

    def test_controles_do_catalogo(self):
        catalogo = self.html[self.html.index('<section class="view" data-view="catalogo">'):
                             self.html.index('<section class="view" data-view="rotas"')]
        self.assertRegex(catalogo, r'<div id="continuar"[^>]*></div>')
        self.assertEqual(re.findall(r'<button [^>]*data-grupo="(\w+)"', catalogo),
                         ["trilha", "nivel", "perfil", "nist"])
        self.assertIn('class="seg agrupar"', catalogo)
        self.assertRegex(catalogo, r'<input type="checkbox" id="so-pendentes"')
        self.assertIn('id="grupos"', catalogo)
        self.assertIn("Agrupar por", catalogo)
        self.assertIn("Só não concluídos", catalogo)
        self.assertRegex(self.html, r'<input type="search" id="busca"')

    def test_cartao_tem_todos_os_atributos_do_contrato(self):
        ordem = list(ESTUDOS_DADOS)
        for slug, d in ESTUDOS_DADOS.items():
            tag = _cartao(self.html, slug)
            with self.subTest(slug=slug):
                self.assertIsNotNone(tag)
                self.assertIn(f'data-trilha="{d["trilha"]}"', tag)
                self.assertIn(f'data-nivel="{d["nivel"]}"', tag)
                self.assertIn(f'data-perfis="{escape("|".join(d["carreiras"]))}"', tag)
                self.assertIn(f'data-nist="{escape(d["nist"])}"', tag)
                self.assertIn(f'data-secoes="{contar_secoes(slug)}"', tag)
                busca = re.search(r'data-busca="([^"]*)"', tag).group(1)
                self.assertEqual(busca, busca.lower())
                self.assertIn(escape(d["titulo"].lower()), busca)
        self.assertEqual(self.html.count('<a class="mc'), len(ordem))

    def test_conteudo_do_cartao(self):
        slug = "Threat-Hunting"
        d = ESTUDOS_DADOS[slug]
        n = list(ESTUDOS_DADOS).index(slug) + 1
        ini = self.html.index(_cartao(self.html, slug))
        cartao = self.html[ini:self.html.index("</a>", ini)]
        self.assertIn(f"Estudo {n:02d}", cartao)
        self.assertIn(f"⏱ {d['tempo_minutos']} min", cartao)
        self.assertIn(escape(d["titulo"]), cartao)
        self.assertIn(escape(d["subtitulo"]), cartao)
        self.assertIn(escape(NIVEIS[d["nivel"]]), cartao)
        self.assertIn(f"NIST {escape(d['nist'])}", cartao)
        self.assertIn(f"🧪 {escape(d['simulador_nome'])}", cartao)
        self.assertRegex(cartao, r'<span class="mc-status"[^>]*></span>')
        self.assertNotIn("Responde a", cartao)
        self.assertNotIn("<li>", cartao)
        self.assertNotIn("checkbox", cartao)

    def test_catalogo_agrupado_por_trilha_sem_js(self):
        grupos = self.html[self.html.index('id="grupos"'):self.html.index('<section class="view" data-view="rotas"')]
        trilhas = re.findall(r'<div class="grupo" data-trilha="(\d+)"', grupos)
        self.assertEqual(trilhas, [str(t) for t in TRILHAS])
        for tid, info in TRILHAS.items():
            ini = grupos.index(f'<div class="grupo" data-trilha="{tid}"')
            fim = grupos.find('<div class="grupo" ', ini + 1)
            bloco = grupos[ini:fim if fim != -1 else len(grupos)]
            slugs = [s for s, d in ESTUDOS_DADOS.items() if d["trilha"] == tid]
            with self.subTest(trilha=tid):
                self.assertIn(f"Trilha {tid}", bloco)
                self.assertIn(escape(info["nome"]), bloco)
                self.assertIn(f"0 de {len(slugs)} concluídos", bloco)
                self.assertEqual(re.findall(r'<a class="mc[^"]*" id="estudo-([^"]+)"', bloco), slugs)

    def test_progresso_global_no_menu(self):
        ini = self.html.index('id="progresso-global"')
        bloco = self.html[ini:self.html.index("</aside>", ini)]
        self.assertIn("Módulos Compilados", bloco)
        self.assertRegex(bloco, rf"\d+ / {len(ESTUDOS_DADOS)}")
        self.assertIn(f"de {len(ESTUDOS_DADOS)} concluídos", bloco)

    def test_visoes_especiais_com_conteudo(self):
        def visao(nome):
            ini = self.html.index(f'<section class="view" data-view="{nome}"')
            fim = self.html.find('<section class="view" ', ini + 1)
            return self.html[ini:fim if fim != -1 else self.html.index("</main>")]

        self.assertIn('id="secao-rota-sugerida"', visao("rotas"))
        cert = visao("certificacoes")
        self.assertIn('id="secao-cert-painel"', cert)
        self.assertIn('id="secao-certificacoes"', cert)
        self.assertIn('id="secao-necessidades"', visao("necessidades"))
        self.assertIn('id="secao-rota-vaga"', visao("vaga"))
        prog = visao("progresso")
        for slug in ESTUDOS_DADOS:
            self.assertIn(f'<input type="checkbox" data-slug="{slug}"', prog)
        self.assertIn("Disponível", prog)

    def test_contar_secoes_bate_com_o_corpo(self):
        corpo = (GERADORES_DIR / "threat_hunting_body.html").read_text(encoding="utf-8")
        self.assertEqual(contar_secoes("Threat-Hunting"), len(extrair_secoes(corpo)))
        self.assertGreater(contar_secoes("Threat-Hunting"), 0)
        self.assertEqual(contar_secoes("Slug-Que-Nao-Existe"), 0)

    def test_sem_js_antigo(self):
        for velho in ("setSubFilter(", "filter-subpanel", "toggleDone(", "focarEstudo("):
            self.assertNotIn(velho, self.html)


class TestPortalCss(unittest.TestCase):
    def setUp(self):
        self.css = INDEX_CSS.read_text(encoding="utf-8")

    def test_cor_de_cada_trilha_via_token(self):
        for tid, info in TRILHAS.items():
            with self.subTest(trilha=tid):
                self.assertIn(f'[data-trilha="{tid}"]', self.css)
                self.assertIn(f"var(--t{tid}-{info['cor_nome']})", self.css)

    def test_views_ocultas_respeitam_hidden(self):
        self.assertRegex(self.css, r"\.view\[hidden\]\s*\{[^}]*display:\s*none")


if __name__ == "__main__":
    unittest.main()
