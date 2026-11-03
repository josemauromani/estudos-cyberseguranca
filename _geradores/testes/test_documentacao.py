"""A documentação do autor descreve o contrato vigente e o .gitignore cobre as pastas de rascunho."""
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "_geradores"))

from contrato import TIPOS  # noqa: E402

ROOT = RAIZ
GUIA = RAIZ / "_geradores" / "GUIA-DO-AUTOR.md"
README = RAIZ / "README.md"


class TestDocumentacao(unittest.TestCase):
    def test_guia_documenta_contrato(self):
        guia = GUIA.read_text(encoding="utf-8")
        for t in TIPOS:
            self.assertIn(f'data-tipo="{t}"', guia)
        for velho in ("hero-header", "section-tag", 'class="check-item"', "quiz-btn"):
            self.assertNotIn(velho, guia)

    def test_guia_cita_validador(self):
        guia = GUIA.read_text(encoding="utf-8")
        self.assertIn("contrato.validar_corpo", guia)

    def test_readme_atualizado(self):
        readme = README.read_text(encoding="utf-8")
        self.assertIn("unittest discover -s _geradores/testes", readme)
        self.assertIn("fontes", readme.lower())
        self.assertNotIn("a aba **Por Nível**", readme)

    def test_guia_documenta_glossario(self):
        guia = GUIA.read_text(encoding="utf-8")
        for trecho in ("glossario_dados.py", "marcar_termos", "1ª ocorrência", "por seção"):
            self.assertIn(trecho, guia)

    def test_readme_cita_glossario(self):
        readme = README.read_text(encoding="utf-8")
        self.assertIn("sete visões", readme)
        self.assertIn("**Glossário:**", readme)
        self.assertNotIn("seis visões", readme)

    def test_gitignore(self):
        texto = (ROOT / ".gitignore").read_text(encoding="utf-8")
        for pasta in (".superpowers/brainstorm/", ".superpowers/capturas/",
                      ".superpowers/sdd/", ".superpowers/cache/"):
            self.assertIn(pasta, texto)


if __name__ == "__main__":
    unittest.main()
