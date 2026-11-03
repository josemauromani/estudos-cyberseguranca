#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Visão "Glossário" do portal: marcação gerada e comportamento (roteamento por hash, busca) no Chrome."""

import re
import sys
import tempfile
import unittest
from pathlib import Path

TESTES = Path(__file__).resolve().parent
GERADORES = TESTES.parent
sys.path.insert(0, str(GERADORES))
sys.path.insert(0, str(TESTES))

from build_index import gerar_index_html, modulos_por_termo, render_glossario  # noqa: E402
from glossario import carregar_glossario  # noqa: E402
from navegador import CHROME, executar  # noqa: E402

GLOSSARIO = carregar_glossario()
CINCO = ["Fundamentos-Ciber", "Criptografia-Pratica", "Autenticacao-e-IAM",
         "Seguranca-em-APIs", "SOAR-e-Automacao-de-Resposta"]


def verbete_falso(id_, termo, **extra):
    v = {"id": id_, "termo": termo, "categoria": "Teste", "significado": "Texto de teste.",
         "explicacao": "", "historico": "", "variacoes": [], "relacionados": [], "referencias": []}
    v.update(extra)
    return v


class TestGlossarioPortal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as tmp:
            cls.html = gerar_index_html(output_path=Path(tmp) / "index.html").read_text(encoding="utf-8")

    def cartao(self, id_):
        m = re.search(rf'<article class="verbete" id="g-{id_}".*?</article>', self.html, re.S)
        self.assertIsNotNone(m)
        return m.group(0)

    def test_menu_e_visao(self):
        self.assertIn('<a href="#v-glossario" data-view="glossario">📖 Glossário <span class="n">1</span></a>', self.html)
        self.assertIn('<section class="view" data-view="glossario" hidden>', self.html)

    def test_verbete_hmac_completo(self):
        c = self.cartao("hmac")
        ordem = ["HMAC", "Criptografia", "Hash-based Message Authentication Code",
                 "<dt>Significado", "<dt>Explicação", "<dt>Histórico", "<dt>Variações",
                 "<dt>Referências", "<dt>Aparece em"]
        pos = -1
        for item in ordem:
            novo = c.find(item, pos + 1)
            self.assertGreater(novo, pos, item)
            pos = novo
        self.assertNotIn("<dt>Relacionados", c)
        self.assertNotIn("<dt>Termo em inglês", c)
        self.assertIn('target="_blank" rel="noopener"', c)

    def test_verbete_sem_categoria(self):
        html = render_glossario([{"id": "x", "termo": "X", "significado": "y"}], {}, {})
        self.assertNotIn("verbete-cat", html)

    def test_aparece_em_cinco_modulos(self):
        mods = modulos_por_termo(GLOSSARIO)["hmac"]
        self.assertEqual(set(mods), set(CINCO))
        from index_dados import ESTUDOS_DADOS
        self.assertEqual(mods, [s for s in ESTUDOS_DADOS if s in CINCO])
        self.assertEqual(len(re.findall(r'data-slug="', self.cartao("hmac"))), 5)

    def test_letras(self):
        self.assertRegex(self.html, r'<a [^>]*href="#v-glossario/letra-h"[^>]*>H</a>')
        self.assertIn('<h2 id="g-letra-h">', self.html)
        self.assertRegex(self.html, r'<span [^>]*aria-disabled="true"[^>]*>A</span>')

    def test_ordem_ignora_acento(self):
        vs = [verbete_falso("etica", "Ética"), verbete_falso("escopo", "Escopo"),
              verbete_falso("exploit", "Exploit")]
        h = render_glossario(vs, {}, {})
        ids = re.findall(r'<article class="verbete" id="g-(\w+)"', h)
        self.assertEqual(ids, ["escopo", "etica", "exploit"])
        self.assertEqual(len(re.findall(r'<section class="glossario-grupo" data-letra="', h)), 1)
        self.assertIn('data-letra="E"', h)

    def test_relacionado_vira_link(self):
        vs = [verbete_falso("a-um", "Aum", relacionados=["b-dois"]),
              verbete_falso("b-dois", "Bdois", relacionados=["a-um"])]
        h = render_glossario(vs, {}, {})
        self.assertIn('href="#v-glossario/b-dois"', h)
        self.assertIn('href="#v-glossario/a-um"', h)


@unittest.skipUnless(CHROME, "Chrome não encontrado")
class TestGlossarioPortalJs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as tmp:
            cls.portal = gerar_index_html(output_path=Path(tmp) / "index.html").read_text(encoding="utf-8")

    def rodar(self, script, hash_=None):
        antes = f"history.replaceState(null,'','{hash_}')" if hash_ else ""
        r = executar(self.portal, script, script_antes=antes)
        self.assertEqual(r["erros"], [])
        return r["saida"]

    def test_hash_abre_verbete(self):
        s = self.rodar("""
          const v = document.querySelector('section.view[data-view="glossario"]');
          const g = document.getElementById('g-hmac');
          const r = g.getBoundingClientRect();
          __fim({visivel: !v.hidden, destaque: g.classList.contains('destaque'),
                 naJanela: r.top >= 0 && r.top < window.innerHeight});
        """, "#v-glossario/hmac")
        self.assertEqual(s, {"visivel": True, "destaque": True, "naJanela": True})

    def test_hash_inexistente(self):
        s = self.rodar("""
          const v = document.querySelector('section.view[data-view="glossario"]');
          __fim({visivel: !v.hidden, y: window.scrollY, dest: document.querySelectorAll('.verbete.destaque').length});
        """, "#v-glossario/nao-existe")
        self.assertEqual(s, {"visivel": True, "y": 0, "dest": 0})

    def test_hash_antigo_continua(self):
        s = self.rodar("""
          __fim(!document.querySelector('section.view[data-view="rotas"]').hidden);
        """, "#v-rotas")
        self.assertIs(s, True)

    def test_busca(self):
        s = self.rodar("""
          const b = document.getElementById('busca-glossario');
          const g = document.getElementById('g-hmac');
          const grupo = g.closest('.glossario-grupo');
          const vazio = document.querySelector('.glossario-vazio');
          const digitar = t => { b.value = t; b.dispatchEvent(new Event('input', {bubbles: true})); };
          digitar('autenticação');
          const a = {hmac: !g.hidden, vazio: vazio.hidden};
          digitar('xyz');
          __fim({a: a, hmac: !g.hidden, grupo: !grupo.hidden, vazio: vazio.hidden});
        """, "#v-glossario")
        self.assertEqual(s, {"a": {"hmac": True, "vazio": True}, "hmac": False, "grupo": False, "vazio": False})

    def test_clique_na_letra_mantem_glossario(self):
        s = self.rodar("""
          document.querySelector('.glossario-letras a[href$="letra-h"]').click();
          setTimeout(() => {
            const v = document.querySelector('section.view[data-view="glossario"]');
            const h = document.getElementById('g-letra-h').getBoundingClientRect();
            __fim({visivel: !v.hidden, hash: location.hash, dest: document.querySelectorAll('.destaque').length,
                   noTopo: h.top >= 0 && h.top < window.innerHeight});
          }, 50);
        """, "#v-glossario")
        self.assertEqual(s, {"visivel": True, "hash": "#v-glossario/letra-h", "dest": 0, "noTopo": True})

    def test_ancora_limpa_filtro_ativo(self):
        s = self.rodar("""
          const b = document.getElementById('busca-glossario');
          b.value = 'xyz'; b.dispatchEvent(new Event('input', {bubbles: true}));
          location.hash = '#v-glossario/hmac';
          setTimeout(() => {
            const g = document.getElementById('g-hmac');
            __fim({campo: b.value, visivel: !g.hidden && g.offsetParent !== null,
                   destaque: g.classList.contains('destaque')});
          }, 50);
        """, "#v-glossario")
        self.assertEqual(s, {"campo": "", "visivel": True, "destaque": True})


if __name__ == "__main__":
    unittest.main()
