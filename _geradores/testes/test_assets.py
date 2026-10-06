"""Testes unitários para o Design System (base.css) e biblioteca JavaScript (base.js)."""

import unittest
from pathlib import Path


class TestAssets(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.css_file = self.root / "_geradores" / "base.css"
        self.js_file = self.root / "_geradores" / "base.js"

    def test_base_css_exists_and_valid(self):
        """Verifica se base.css existe e possui tamanho mínimo substancial."""
        self.assertTrue(self.css_file.exists(), "base.css deve existir em _geradores/")
        content = self.css_file.read_text(encoding="utf-8")
        self.assertGreater(len(content), 500, "base.css deve conter definições de estilo substanciais")

    def test_base_css_contains_design_tokens(self):
        """Verifica a presença de tokens de cores, temas e fontes obrigatórios."""
        self.assertTrue(self.css_file.exists(), "base.css deve existir")
        content = self.css_file.read_text(encoding="utf-8")

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

        # Cores das 6 trilhas
        trilhas = [
            "--t1-blue",
            "--t2-green",
            "--t3-red",
            "--t4-purple",
            "--t5-cyan",
            "--t6-amber",
        ]
        for t in trilhas:
            self.assertIn(t, content, f"Cor de trilha ausente no CSS: {t}")

        # Tipografia
        fontes = [
            "IBM Plex Sans",
            "IBM Plex Mono",
            "Barlow Semi Condensed",
        ]
        for f in fontes:
            self.assertIn(f, content, f"Família de fonte ausente no CSS: {f}")

    def test_base_css_contains_component_classes(self):
        """Verifica as classes de componentes do Design System."""
        self.assertTrue(self.css_file.exists(), "base.css deve existir")
        content = self.css_file.read_text(encoding="utf-8")

        classes_obrigatorias = [
            ".callout",
            ".callout-tip",
            ".callout-warning",
            ".callout-danger",
            ".callout-law",
            ".terminal-box",
            ".btn-copy",
            ".lab-box",
            ".lab-header",
            ".lab-controls",
            ".lab-output",
            ".checklist",
            ".check-item",
            ".quiz-item",
            ".quiz-options",
            ".quiz-feedback",
            ".facts-grid",
            ".facts-card",
        ]
        for cls in classes_obrigatorias:
            self.assertIn(cls, content, f"Classe de componente ausente no CSS: {cls}")

    def test_base_css_supports_dark_mode(self):
        """Verifica se há suporte a tema escuro via media query e atributo de dados."""
        self.assertTrue(self.css_file.exists(), "base.css deve existir")
        content = self.css_file.read_text(encoding="utf-8")

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
            "initTheme",
            "initChecklist",
            "initQuiz",
            "checkQuiz",
            "copyCode",
            "escapeHtml",
            "formatBytes",
            "formatNumber",
        ]
        for fn in funcoes:
            self.assertIn(fn, content, f"Função JS obrigatória ausente em base.js: {fn}")

    def test_base_js_handles_localstorage_persistence(self):
        """Verifica convenções de chaves localStorage padronizadas no guia do autor."""
        self.assertTrue(self.js_file.exists(), "base.js deve existir")
        content = self.js_file.read_text(encoding="utf-8")

        self.assertIn("cs_theme", content, "Chave de tema no localStorage deve ser cs_theme")
        self.assertIn("cs_check_", content, "Chave de checklist no localStorage deve conter cs_check_")


if __name__ == "__main__":
    unittest.main()
