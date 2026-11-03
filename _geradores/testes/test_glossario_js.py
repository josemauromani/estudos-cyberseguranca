"""Testes do tooltip do glossário (initGlossario do base.js) num módulo compilado, no Chrome headless."""

import sys
import tempfile
import unittest
from pathlib import Path

TESTES = Path(__file__).resolve().parent
GERADORES = TESTES.parent
sys.path.insert(0, str(GERADORES))
sys.path.insert(0, str(TESTES))

from montar import montar_treinamento  # noqa: E402
from navegador import CHROME, executar  # noqa: E402
import test_base_js  # noqa: E402

PRELUDIO = """
  const d = document.querySelector('dfn.glossario[data-termo="hmac"]');
  const pop = () => document.getElementById('glossario-pop');
  const visivel = () => !!pop() && !pop().hasAttribute('hidden');
"""


@unittest.skipUnless(CHROME, "Chrome não encontrado")
class TestGlossarioJs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as tmp:
            saida = Path(tmp) / "x.html"
            montar_treinamento(GERADORES / "fundamentos_ciber_body.html", saida)
            cls.html = saida.read_text(encoding="utf-8")

    def rodar(self, script, **kw):
        r = executar(self.html, PRELUDIO + script, **kw)
        self.assertEqual(r["erros"], [])
        return r["saida"]

    def test_title_removido(self):
        s = self.rodar("__fim(document.querySelector('dfn.glossario').hasAttribute('title'));")
        self.assertFalse(s)

    def test_foco_abre_e_esc_fecha(self):
        s = self.rodar("""
          d.focus();
          const aberto = {vis: visivel(),
            titulo: document.querySelector('.glossario-pop-titulo').textContent,
            texto: document.querySelector('.glossario-pop-texto').textContent,
            desc: d.getAttribute('aria-describedby'),
            href: document.querySelector('a.glossario-pop-link').getAttribute('href')};
          d.dispatchEvent(new KeyboardEvent('keydown', {key: 'Tab', bubbles: true, cancelable: true}));
          const noLink = document.activeElement === document.querySelector('a.glossario-pop-link');
          d.focus();
          d.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape', bubbles: true}));
          __fim({aberto, noLink, vis: visivel(), desc: d.getAttribute('aria-describedby'),
            foco: document.activeElement === d});""")
        self.assertTrue(s["aberto"]["vis"])
        self.assertEqual(s["aberto"]["titulo"], "HMAC · Criptografia")
        self.assertIn("chave secreta", s["aberto"]["texto"])
        self.assertEqual(s["aberto"]["desc"], "glossario-pop")
        self.assertTrue(s["aberto"]["href"].endswith("index.html#v-glossario/hmac"))
        self.assertTrue(s["noLink"])
        self.assertFalse(s["vis"])
        self.assertIsNone(s["desc"])
        self.assertTrue(s["foco"])

    def test_shift_tab_no_link_volta_ao_termo(self):
        s = self.rodar("""
          d.focus();
          const l = document.querySelector('a.glossario-pop-link');
          l.focus();
          l.dispatchEvent(new KeyboardEvent('keydown', {key: 'Tab', shiftKey: true, bubbles: true, cancelable: true}));
          __fim(document.activeElement === d);""")
        self.assertTrue(s)

    def test_mouse_abre_com_atraso(self):
        s = self.rodar("""
          d.dispatchEvent(new MouseEvent('mouseenter'));
          const antes = visivel();
          setTimeout(() => {
            const depois = visivel();
            d.dispatchEvent(new MouseEvent('mouseleave'));
            setTimeout(() => __fim({antes, depois, fechou: !visivel()}), 300);
          }, 200);""")
        self.assertFalse(s["antes"])
        self.assertTrue(s["depois"])
        self.assertTrue(s["fechou"])

    def test_toque_abre_e_fora_fecha(self):
        s = self.rodar("""
          d.click();
          const aberto = visivel();
          document.body.click();
          __fim({aberto, fechado: !visivel()});""")
        self.assertTrue(s["aberto"])
        self.assertTrue(s["fechado"])

    def test_borda_direita_no_celular(self):
        s = self.rodar("""
          d.style.position = 'fixed'; d.style.right = '0'; d.style.top = '100px';
          d.focus();
          const r = pop().getBoundingClientRect();
          __fim({left: r.left, right: r.right, w: innerWidth});""", largura=360)
        self.assertGreaterEqual(s["left"], 16)
        self.assertLessEqual(s["right"], s["w"] - 16)

    def test_vira_para_cima_sem_espaco(self):
        s = self.rodar("""
          d.style.position = 'fixed'; d.style.bottom = '0';
          d.focus();
          __fim({pop: pop().getBoundingClientRect().bottom, termo: d.getBoundingClientRect().top});""")
        self.assertLessEqual(s["pop"], s["termo"])

    def test_sem_dados_nao_cria_popover(self):
        r = executar(test_base_js.pagina_fixture(), "__fim(!!document.getElementById('glossario-pop'));")
        self.assertEqual(r["erros"], [])
        self.assertFalse(r["saida"])


if __name__ == "__main__":
    unittest.main()
