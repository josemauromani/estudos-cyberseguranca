"""Testes dos design tokens (tokens.css) e da carga de CSS do montar.py."""

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

GERADORES = Path(__file__).resolve().parent.parent
RAIZ = GERADORES.parent
TOKENS = GERADORES / "tokens.css"

TIPOS = ["teoria", "laboratorio", "checklist", "questoes", "referencias"]
NOVOS = ["--rule-strong", "--accent-soft", "--ok", "--bad", "--console", "--console-ink"] + \
        [f"--tipo-{t}" for t in TIPOS] + [f"--tipo-{t}-bg" for t in TIPOS]


def git_show(ref):
    return subprocess.run(["git", "show", ref], cwd=RAIZ, capture_output=True, text=True,
                          encoding="utf-8", check=True).stdout


def bloco(css, inicio):
    """Texto entre a `{` que segue `inicio` e a `}` correspondente."""
    i = css.index(inicio)
    abre = css.index("{", i)
    nivel = 0
    for pos in range(abre, len(css)):
        if css[pos] == "{":
            nivel += 1
        elif css[pos] == "}":
            nivel -= 1
            if nivel == 0:
                return css[abre + 1:pos]
    raise ValueError(f"bloco sem fechamento: {inicio}")


def declaracoes(b):
    return {m.group(1): m.group(2).strip() for m in re.finditer(r"(--[a-z0-9-]+)\s*:\s*([^;]+);", b)}


class TestTokens(unittest.TestCase):
    def setUp(self):
        self.css = TOKENS.read_text(encoding="utf-8")

    def test_toda_variavel_usada_nos_corpos_existe(self):
        usadas = set()
        for corpo in GERADORES.glob("*_body.html"):
            usadas |= set(re.findall(r"var\((--[a-z0-9-]+)", corpo.read_text(encoding="utf-8")))
        definidas = set(re.findall(r"(--[a-z0-9-]+)\s*:", self.css))
        self.assertEqual(usadas - definidas, set())

    def test_nomes_legados_preservados(self):
        antigos = set(re.findall(r"^\s*(--[a-z0-9-]+)\s*:", git_show("a671fbe:_geradores/base.css"), re.M))
        definidas = set(re.findall(r"(--[a-z0-9-]+)\s*:", self.css))
        self.assertEqual(antigos - definidas, set())

    def test_tokens_novos_nos_tres_blocos(self):
        claro = bloco(self.css, ":root {")
        sistema = bloco(self.css, ':root:not([data-theme="light"])')
        escuro = bloco(self.css, ':root[data-theme="dark"]')
        for t in NOVOS:
            for b in (claro, sistema, escuro):
                self.assertIn(t + ":", b)
        self.assertEqual(declaracoes(sistema), declaracoes(escuro))

    def test_claro_forcado_igual_ao_claro(self):
        claro = declaracoes(bloco(self.css, ":root {"))
        forcado = declaracoes(bloco(self.css, ':root[data-theme="light"]'))
        for nome, valor in forcado.items():
            self.assertEqual(claro[nome], valor, nome)
        for t in NOVOS:
            self.assertIn(t, forcado)

    def test_valores_da_spec(self):
        claro = bloco(self.css, ":root {")
        for nome, valor in {"--ground": "#F4F6F8", "--ink": "#14212B", "--tipo-teoria": "#2563EB",
                            "--tipo-laboratorio": "#0D9488", "--tipo-checklist": "#B45309",
                            "--tipo-questoes": "#C026D3", "--tipo-referencias": "#64748B",
                            "--warning-color": "#EA580C", "--law-color": "#6D28D9",
                            "--console": "#0F1820"}.items():
            self.assertRegex(claro, rf"{nome}:\s*{valor}", nome)

    def test_valores_escuros_do_mockup(self):
        escuro = declaracoes(bloco(self.css, ':root[data-theme="dark"]'))
        self.assertEqual(escuro["--ground"], "#0E151A")
        self.assertEqual(escuro["--tipo-teoria"], "#60A5FA")
        self.assertEqual(escuro["--console"], "#0A1015")
        self.assertEqual(escuro["--ok"], "#4ADE80")

    def test_base_css_nao_declara_tokens_nem_importa_fontes(self):
        base = (GERADORES / "base.css").read_text(encoding="utf-8")
        self.assertNotIn("@import", base)
        self.assertNotIn("fonts.googleapis.com", base)
        self.assertIsNone(re.search(r"^:root", base, re.M))

    def test_html_gerado_sem_google_fonts(self):
        from montar import montar_treinamento
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from test_chassi import corpo_valido
        with tempfile.TemporaryDirectory() as tmp:
            corpo = Path(tmp) / "teste_body.html"
            corpo.write_text(corpo_valido(), encoding="utf-8")
            saida = Path(tmp) / "saida.html"
            montar_treinamento(corpo, saida, titulo="Teste", meta={"slug": "Fundamentos-Ciber", "trilha": "1"})
            html = saida.read_text(encoding="utf-8")
        self.assertNotIn("fonts.googleapis.com", html)
        self.assertNotIn("fonts.gstatic.com", html)
        self.assertIn("@font-face", html)
        self.assertIn("--tipo-teoria:", html)

    def test_carregar_css_ordem_e_laboratorio_opcional(self):
        import montar
        css = montar.carregar_css()
        self.assertLess(css.index("@font-face"), css.index("--tipo-teoria:"))
        self.assertLess(css.index("--tipo-teoria:"), css.index(".callout"))
        with tempfile.TemporaryDirectory() as tmp:
            original = montar.LABORATORIO_CSS
            montar.LABORATORIO_CSS = Path(tmp) / "nao_existe.css"
            try:
                self.assertIn("--tipo-teoria:", montar.carregar_css())
            finally:
                montar.LABORATORIO_CSS = original


if __name__ == "__main__":
    unittest.main()
