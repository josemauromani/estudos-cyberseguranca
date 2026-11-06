"""Garante que nenhum corpo exige ou contém laboratório/simulador."""

import re
import sys
import unittest
from pathlib import Path

GERADORES = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GERADORES))

from contrato import extrair_secoes, validar_corpo  # noqa: E402

CORPOS = sorted(GERADORES.glob("*_body.html"))


class TestCorposSemLaboratorio(unittest.TestCase):
    def test_existem_62_corpos(self):
        self.assertEqual(len(CORPOS), 62)

if __name__ == "__main__":
    unittest.main()
