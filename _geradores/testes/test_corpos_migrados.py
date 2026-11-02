"""Os 57 corpos de módulo seguem o contrato de markup e a migração já foi aplicada."""
import sys
import unittest
from pathlib import Path

GERADORES = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GERADORES))

from contrato import validar_corpo  # noqa: E402
from migrar_markup import migrar  # noqa: E402


class TestCorposMigrados(unittest.TestCase):
    def test_todos_os_corpos_no_contrato(self):
        erros = [e for c in sorted(GERADORES.glob("*_body.html"))
                 for e in validar_corpo(c.read_text(encoding="utf-8"), c.stem)]
        self.assertEqual(erros, [])

    def test_migracao_ja_aplicada_e_idempotente(self):
        for c in GERADORES.glob("*_body.html"):
            html = c.read_text(encoding="utf-8")
            self.assertEqual(migrar(html, c.stem.replace("_body", "")), html, c.name)


if __name__ == "__main__":
    unittest.main()
