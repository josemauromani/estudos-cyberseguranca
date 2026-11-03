"""Testes da marcação automática de termos (glossario.marcar_termos)."""

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from glossario import marcar_termos

V = {"id": "hmac", "termo": "HMAC", "significado": "Código <strong>com</strong> chave.",
     "variacoes": ["HMAC-SHA256"]}
P = {"id": "integridade", "termo": "Integridade", "significado": "Dado não alterado."}
SO_HMAC = {"id": "hmac", "termo": "HMAC", "significado": "x"}
RAIZ = Path(__file__).resolve().parent.parent.parent


def sec(corpo, sid="s1"):
    return f'<section class="study-section" id="{sid}" data-tipo="teoria"><h2>T</h2>{corpo}</section>'


class TestMarcarTermos(unittest.TestCase):
    def test_marca_primeira_ocorrencia_por_secao(self):
        html, ids = marcar_termos(sec("<p>HMAC e HMAC</p>") + sec("<p>HMAC</p>", "s2"), [V])
        self.assertEqual(html.count("<dfn"), 2)
        self.assertEqual(ids, ["hmac"])

    def test_saida_exata(self):
        html, _ = marcar_termos(sec("<p>Use HMAC.</p>"), [V])
        self.assertIn('<dfn class="glossario" data-termo="hmac" tabindex="0" '
                      'title="Código com chave.">HMAC</dfn>.', html)

    def test_title_escapado(self):
        v = {"id": "x", "termo": "XX", "significado": 'a "b" & <em>c</em>'}
        html, _ = marcar_termos(sec("<p>XX</p>"), [v])
        self.assertIn('title="a &quot;b&quot; &amp; c"', html)

    def test_contextos_ignorados(self):
        casos = [
            "<pre>HMAC</pre>", "<code>HMAC</code>", "<kbd>HMAC</kbd>", "<samp>HMAC</samp>",
            '<script>var a="HMAC"</script>', "<style>/*HMAC*/</style>",
            "<svg><text>HMAC</text></svg>", "<textarea>HMAC</textarea>", "<h3>HMAC</h3>",
            '<a href="#">HMAC</a>', "<button>HMAC</button>", "<label>HMAC</label>",
            '<div class="terminal-box x"><p>HMAC</p></div>', '<pre class="mermaid">HMAC</pre>',
        ]
        for caso in casos:
            with self.subTest(caso=caso):
                html, ids = marcar_termos(sec(caso), [V])
                self.assertNotIn("<dfn", html)
                self.assertEqual(ids, [])
                self.assertEqual(html, sec(caso))

    def test_ignorado_nao_consome_a_ocorrencia(self):
        html, _ = marcar_termos(sec("<code>HMAC</code><p>HMAC</p>"), [V])
        self.assertEqual(html.count("<dfn"), 1)
        self.assertIn("<p><dfn", html)

    def test_atributo_nao_marca(self):
        html, _ = marcar_termos(sec('<p title="HMAC">x</p>'), [V])
        self.assertNotIn("<dfn", html)

    def test_fora_de_secao_nao_marca(self):
        html, ids = marcar_termos("<p>HMAC</p>", [V])
        self.assertNotIn("<dfn", html)
        self.assertEqual(ids, [])

    def test_sigla_diferencia_caixa(self):
        html, _ = marcar_termos(sec("<p>hmac</p>"), [V])
        self.assertNotIn("<dfn", html)

    def test_palavra_nao_diferencia_caixa(self):
        html, _ = marcar_termos(sec("<p>a integridade</p>"), [P])
        self.assertRegex(html, r"<dfn [^>]*>integridade</dfn>")

    def test_fronteira(self):
        for txt in ("HMACs", "XHMAC", "HMAC_x", "pré-HMAC", "HMAC-SHA1", "éHMAC", "HMAC9"):
            with self.subTest(txt=txt):
                html, _ = marcar_termos(sec(f"<p>{txt}</p>"), [SO_HMAC])
                self.assertNotIn("<dfn", html)

    def test_variacao_mais_longa_vence(self):
        html, _ = marcar_termos(sec("<p>HMAC-SHA256</p>"), [V])
        self.assertRegex(html, r"<dfn [^>]*>HMAC-SHA256</dfn>")
        self.assertEqual(html.count("<dfn"), 1)

    def test_pontuacao(self):
        for txt in ("(HMAC)", "HMAC,", "HMAC.", "assinaturas/HMAC", "HMAC"):
            with self.subTest(txt=txt):
                html, ids = marcar_termos(sec(f"<p>{txt}</p>"), [V])
                self.assertEqual(html.count("<dfn"), 1)
                self.assertEqual(ids, ["hmac"])

    def test_dentro_de_formatacao(self):
        html, _ = marcar_termos(sec("<p>use <strong>HMAC</strong></p>"), [V])
        self.assertIn('<strong><dfn class="glossario"', html)

    def test_entidades_preservadas(self):
        entrada = sec("<p>A &amp; B&nbsp;HMAC &#8212; &lt;x&gt;</p>")
        html, _ = marcar_termos(entrada, [V])
        self.assertIn("<dfn", html)
        self.assertEqual(re.sub(r"<dfn[^>]*>|</dfn>", "", html), entrada)

    def test_entidade_sem_ponto_e_virgula_preservada(self):
        entrada = sec("<p>MITRE ATT&CK e\n  &amp x &#65 HMAC</p>")
        html, _ = marcar_termos(entrada, [V])
        self.assertEqual(re.sub(r"<dfn[^>]*>|</dfn>", "", html), entrada)

    def test_todos_os_corpos_ida_e_volta(self):
        from glossario import carregar_glossario
        g = carregar_glossario()
        for f in sorted((RAIZ / "_geradores").glob("*_body.html")):
            with self.subTest(f=f.name):
                entrada = f.read_text(encoding="utf-8")
                html, _ = marcar_termos(entrada, g)
                self.assertEqual(re.sub(r"<dfn[^>]*>|</dfn>", "", html), entrada)

    def test_tags_maiusculas_e_autofechadas_preservadas(self):
        entrada = sec('<P CLASS="x">HMAC<BR/><img src="a.png"> fim</P><!-- c HMAC --><!DOCTYPE x>')
        html, _ = marcar_termos(entrada, [V])
        self.assertEqual(re.sub(r"<dfn[^>]*>|</dfn>", "", html), entrada)

    def test_ida_e_volta(self):
        entrada = (RAIZ / "_geradores" / "fundamentos_ciber_body.html").read_text(encoding="utf-8")
        html, ids = marcar_termos(entrada, [V])
        self.assertEqual(re.sub(r"<dfn[^>]*>|</dfn>", "", html), entrada)
        self.assertEqual(ids, ["hmac"])

    def test_estudo_01(self):
        entrada = (RAIZ / "_geradores" / "fundamentos_ciber_body.html").read_text(encoding="utf-8")
        html, _ = marcar_termos(entrada, [V])
        self.assertGreaterEqual(html.count("<dfn"), 1)
        for m in re.finditer(r"<(button|script)\b.*?</\1>", html, flags=re.S):
            self.assertNotIn("<dfn", m.group(0))


if __name__ == "__main__":
    unittest.main()
