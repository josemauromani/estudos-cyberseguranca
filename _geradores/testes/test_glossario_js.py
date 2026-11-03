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

    def test_tab_no_link_vai_ao_proximo_tabulavel_do_termo(self):
        s = self.rodar("""
          const SEL = 'a[href], button:not([disabled]), input:not([disabled]), select, textarea, [tabindex]:not([tabindex="-1"])';
          const ev = (el, o) => el.dispatchEvent(new KeyboardEvent('keydown', Object.assign({bubbles: true, cancelable: true}, o)));
          const p = pop();
          const lista = Array.from(document.querySelectorAll(SEL)).filter((e) => !p.contains(e) && e.getClientRects().length);
          const esperado = lista.find((e) => d.compareDocumentPosition(e) & Node.DOCUMENT_POSITION_FOLLOWING && !d.contains(e));
          d.focus();
          ev(d, {key: 'Tab'});
          const link = document.querySelector('a.glossario-pop-link');
          const noLink = document.activeElement === link;
          ev(link, {key: 'Tab'});
          const ehTermo = esperado.matches('dfn.glossario');
          __fim({tem: !!esperado, noLink, certo: document.activeElement === esperado, ehTermo,
                 oculto: !visivel(), descDoTermo: d.getAttribute('aria-describedby'),
                 descDoProximo: esperado.getAttribute('aria-describedby')});""")
        self.assertTrue(s["tem"])
        self.assertTrue(s["noLink"])
        self.assertTrue(s["certo"])
        # O popover do termo de origem fecha.
        self.assertIsNone(s["descDoTermo"])
        if s["ehTermo"]:
            # O próximo tabulável é outro termo do glossário: o popover abre para ele.
            self.assertFalse(s["oculto"])
            self.assertEqual(s["descDoProximo"], "glossario-pop")
        else:
            self.assertTrue(s["oculto"])

    def test_esc_fecha_popover_de_hover_com_foco_fora(self):
        s = self.rodar("""
          d.dispatchEvent(new MouseEvent('mouseenter', {bubbles: false}));
          setTimeout(() => {
            const abriu = visivel();
            document.body.setAttribute('tabindex', '-1');
            document.body.focus();
            document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape', bubbles: true}));
            __fim({abriu, oculto: !visivel(), foco: document.activeElement === d});
          }, 300);""")
        self.assertTrue(s["abriu"])
        self.assertTrue(s["oculto"])
        self.assertFalse(s["foco"])

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

    def test_margens_apos_reabrir_em_outro_termo(self):
        s = self.rodar("""
          const todos = Array.from(document.querySelectorAll('dfn.glossario'));
          const b = todos.find((x) => x !== d) || d;
          [d, b].forEach((x) => { x.style.position = 'fixed'; x.style.top = '100px'; });
          const medidas = [];
          const abrir = (x, lado) => {
            x.style.left = lado === 'esq' ? '0' : 'auto';
            x.style.right = lado === 'esq' ? 'auto' : '0';
            x.focus();
            const r = pop().getBoundingClientRect();
            medidas.push({left: r.left, right: r.right});
          };
          abrir(d, 'dir'); abrir(b, 'esq'); abrir(d, 'dir');
          // Estado antigo: o popover ficou com left alto do uso anterior (Chrome headless não passa de ~500 px).
          d.blur(); pop().style.left = (innerWidth - 100) + 'px'; abrir(d, 'dir');
          __fim({medidas, w: innerWidth, n: todos.length});""", largura=360)
        for m in s["medidas"]:
            self.assertGreaterEqual(m["left"], 16)
            self.assertLessEqual(m["right"], s["w"] - 16)

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
