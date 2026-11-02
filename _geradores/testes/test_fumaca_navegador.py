"""Fumaça no navegador: cada módulo compilado e o portal abrem sem erro de JS.

Roda sequencialmente (uma instância do Chrome por vez).
"""
import sys
import unittest
from pathlib import Path

TESTES = Path(__file__).resolve().parent
GERADORES = TESTES.parent
RAIZ = GERADORES.parent
sys.path.insert(0, str(GERADORES))
sys.path.insert(0, str(TESTES))

from index_dados import ESTUDOS_DADOS  # noqa: E402
from montar import carregar_catalogo_estudos  # noqa: E402
from navegador import CHROME, executar  # noqa: E402

SCRIPT_MODULO = (
    "__fim({toc: document.querySelectorAll('.toc-item').length, "
    "secoes: document.querySelectorAll('section.study-section[data-tipo]').length, "
    "total: document.querySelectorAll('section.study-section').length})"
)


def _compilados():
    catalogo = carregar_catalogo_estudos()
    for slug in ESTUDOS_DADOS:
        c = catalogo.get(slug, {})
        caminho = RAIZ / c.get("pasta", slug) / c.get("arquivo_html", f"treinamento-{slug.lower()}.html")
        if caminho.exists():
            yield slug, caminho


@unittest.skipUnless(CHROME, "Chrome não encontrado")
class TestFumacaNavegador(unittest.TestCase):
    def test_modulos_compilados_abrem_sem_erro(self):
        compilados = list(_compilados())
        self.assertTrue(compilados)
        for slug, caminho in compilados:
            with self.subTest(slug=slug):
                r = executar(caminho.read_text(encoding="utf-8"), SCRIPT_MODULO)
                self.assertEqual(r["erros"], [], slug)
                s = r["saida"]
                self.assertIsNotNone(s, slug)
                self.assertGreater(s["total"], 0, slug)
                self.assertEqual(s["toc"], s["secoes"], slug)
                self.assertEqual(s["secoes"], s["total"], slug)

    def test_portal_abre_sem_erro(self):
        r = executar((RAIZ / "index.html").read_text(encoding="utf-8"), "__fim(1)")
        self.assertEqual(r["erros"], [])
        self.assertEqual(r["saida"], 1)


if __name__ == "__main__":
    unittest.main()
