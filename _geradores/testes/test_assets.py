"""Testes unitários para o Design System (base.css) e biblioteca JavaScript (base.js)."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from index_dados import TRILHAS  # noqa: E402


class TestAssets(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.css_file = self.root / "_geradores" / "base.css"
        self.tokens_file = self.root / "_geradores" / "tokens.css"
        self.js_file = self.root / "_geradores" / "base.js"

    def test_base_css_exists_and_valid(self):
        """Verifica se base.css existe e possui tamanho mínimo substancial."""
        self.assertTrue(self.css_file.exists(), "base.css deve existir em _geradores/")
        content = self.css_file.read_text(encoding="utf-8")
        self.assertGreater(len(content), 500, "base.css deve conter definições de estilo substanciais")

    def test_base_css_contains_design_tokens(self):
        """Verifica a presença de tokens de cores, temas e fontes obrigatórios."""
        self.assertTrue(self.tokens_file.exists(), "tokens.css deve existir")
        content = self.tokens_file.read_text(encoding="utf-8")

        # Tokens fundamentais
        tokens_fundamentais = [
            "--ground",
            "--surface",
            "--sunk",
            "--ink",
            "--muted",
            "--rule",
        ]
        for token in tokens_fundamentais:
            self.assertIn(token, content, f"Token ausente no CSS: {token}")

        # Cores das trilhas: ver test_tokens_de_cada_trilha (derivado de TRILHAS)

        # Tipografia
        fontes = [
            "IBM Plex Sans",
            "IBM Plex Mono",
            "Barlow Semi Condensed",
        ]
        for f in fontes:
            self.assertIn(f, content, f"Família de fonte ausente no CSS: {f}")

    def test_tokens_de_cada_trilha(self):
        """Cada trilha de TRILHAS tem token nos 4 blocos de tema, selo e bloco."""
        base = self.tokens_file.read_text(encoding="utf-8")
        base_css = self.css_file.read_text(encoding="utf-8")
        index = (self.root / "_geradores" / "index.css").read_text(encoding="utf-8")
        for tid, info in TRILHAS.items():
            token = f"--t{tid}-{info['cor_nome']}:"
            with self.subTest(trilha=tid):
                self.assertEqual(base.count(token), 4)
                self.assertEqual(index.count(token), 0, "index.css usa os tokens de tokens.css, não os declara")
                self.assertIn(f".badge-t{tid} ", base_css)
                self.assertIn(f'[data-trilha="{tid}"]', index)
                self.assertIn(f"var(--t{tid}-{info['cor_nome']})", index)

    def test_numero_do_bloco_de_trilha_legivel_nos_dois_temas(self):
        """O número do estudo e o rótulo "Trilha N" do portal, escritos na cor da trilha,
        são legíveis sobre o cartão em cada tema: a cor é misturada a 70% com --ink e
        precisa de contraste >= 4.5:1 com --surface e --ground (texto pequeno, WCAG AA)."""
        import re

        def rgb(hexa):
            return [int(hexa[i:i + 2], 16) for i in (1, 3, 5)]

        def luminancia(canais):
            canais = [c / 255 for c in canais]
            canais = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in canais]
            return 0.2126 * canais[0] + 0.7152 * canais[1] + 0.0722 * canais[2]

        def contraste(a, b):
            la, lb = sorted([luminancia(a), luminancia(b)], reverse=True)
            return (la + 0.05) / (lb + 0.05)

        def mistura(a, b, peso_a):
            return [round(x * peso_a + y * (1 - peso_a)) for x, y in zip(rgb(a), rgb(b))]

        index = (self.root / "_geradores" / "index.css").read_text(encoding="utf-8")
        mistura_css = "color: color-mix(in srgb, var(--gc) 70%, var(--ink));"
        for seletor in (r"\.mc-num", r"\.grupo-cab \.k"):
            regra = re.search(seletor + r" \{([^}]*)\}", index)
            self.assertIsNotNone(regra, seletor)
            self.assertIn(mistura_css, regra.group(1), seletor)
        tokens = self.tokens_file.read_text(encoding="utf-8")
        blocos = {
            "claro": r"^:root \{(.*?)^\}",
            "escuro (preferência)": r"^  :root:not\(\[data-theme=\"light\"\]\) \{(.*?)^  \}",
            "escuro": r"^:root\[data-theme=\"dark\"\] \{(.*?)^\}",
            "claro (forçado)": r"^:root\[data-theme=\"light\"\] \{(.*?)^\}",
        }
        for nome, padrao in blocos.items():
            bloco = re.search(padrao, tokens, re.S | re.M)
            self.assertIsNotNone(bloco, nome)
            fundos = [re.search(rf"--{f}:\s*(#[0-9A-Fa-f]{{6}});", bloco.group(1)).group(1) for f in ("surface", "ground")]
            tinta = re.search(r"--ink:\s*(#[0-9A-Fa-f]{6});", bloco.group(1)).group(1)
            for tid, info in TRILHAS.items():
                cor = re.search(rf"--t{tid}-{info['cor_nome']}:\s*(#[0-9A-Fa-f]{{6}});", bloco.group(1))
                with self.subTest(bloco=nome, trilha=tid):
                    self.assertIsNotNone(cor)
                    for fundo in fundos:
                        self.assertGreaterEqual(contraste(mistura(cor.group(1), tinta, 0.70), rgb(fundo)), 4.5, fundo)

    def test_base_css_contains_component_classes(self):
        """Verifica as classes de componentes do Design System."""
        self.assertTrue(self.css_file.exists(), "base.css deve existir")
        content = self.css_file.read_text(encoding="utf-8")

        from test_componentes_css import CLASSES_T3

        for cls in CLASSES_T3:
            self.assertIn(cls, content, f"Classe de componente ausente no CSS: {cls}")

    def test_base_css_supports_dark_mode(self):
        """Verifica se há suporte a tema escuro via media query e atributo de dados."""
        self.assertTrue(self.tokens_file.exists(), "tokens.css deve existir")
        content = self.tokens_file.read_text(encoding="utf-8")

        self.assertIn("prefers-color-scheme: dark", content, "Deve suportar prefers-color-scheme: dark")
        self.assertIn('data-theme="dark"', content, "Deve suportar alternância explícita data-theme='dark'")

    def test_base_js_exists_and_valid(self):
        """Verifica se base.js existe e possui tamanho mínimo substancial."""
        self.assertTrue(self.js_file.exists(), "base.js deve existir em _geradores/")
        content = self.js_file.read_text(encoding="utf-8")
        self.assertGreater(len(content), 500, "base.js deve conter scripts substanciais")

    def test_base_js_contains_core_functions(self):
        """Verifica a presença das funções principais do design system."""
        self.assertTrue(self.js_file.exists(), "base.js deve existir")
        content = self.js_file.read_text(encoding="utf-8")

        funcoes = [
            "safeStorageGet",
            "safeStorageSet",
            "initTheme",
            "initChecklist",
            "isStudyDone",
            "setStudyDone",
            "initQuiz",
            "checkQuiz",
            "copyCode",
            "escapeHtml",
            "formatBytes",
            "formatNumber",
            "bytesToHex",
            "hexToBytes",
            "sha256Hex",
            "toggleTheme",
            "labProgress",
        ]
        for fn in funcoes:
            self.assertIn(fn, content, f"Função JS obrigatória ausente em base.js: {fn}")

    def test_base_js_handles_localstorage_persistence(self):
        """Verifica convenções de chaves localStorage padronizadas no guia do autor."""
        self.assertTrue(self.js_file.exists(), "base.js deve existir")
        content = self.js_file.read_text(encoding="utf-8")

        self.assertIn("cs_theme", content, "Chave de tema no localStorage deve ser cs_theme")
        self.assertIn("cs_check_", content, "Chave de checklist no localStorage deve conter cs_check_")
        self.assertIn("cs_done_", content, "Chave de conclusão no localStorage deve conter cs_done_")
        self.assertIn("cs_read_", content, "Chave de leitura no localStorage deve conter cs_read_")
        self.assertIn("cs_quiz_", content, "Chave de questões no localStorage deve conter cs_quiz_")
        self.assertIn("cs_last", content, "Chave de último acesso no localStorage deve ser cs_last")


if __name__ == "__main__":
    unittest.main()
