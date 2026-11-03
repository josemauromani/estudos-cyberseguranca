"""Integração do glossário no build do módulo (montar.py)."""

import contextlib
import io
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

TESTES = Path(__file__).resolve().parent
GERADORES = TESTES.parent
RAIZ = GERADORES.parent
sys.path.insert(0, str(GERADORES))
sys.path.insert(0, str(TESTES))

import glossario_dados  # noqa: E402
import montar  # noqa: E402
from glossario import bloco_dados_glossario  # noqa: E402
from test_chassi import corpo_valido  # noqa: E402

RE_JSON = re.compile(r'<script type="application/json" id="glossario-dados">(.*?)</script>', re.S)


def compilar(body: Path, slug=None) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        saida = Path(tmp) / "saida.html"
        meta = {"slug": slug} if slug else {}
        montar.montar_treinamento(body, saida, meta=meta)
        return saida.read_text(encoding="utf-8")


class TestGlossarioModulo(unittest.TestCase):
    def test_estudo_01_tem_termo_e_json(self):
        html = compilar(GERADORES / "fundamentos_ciber_body.html")
        self.assertIn('<dfn class="glossario" data-termo="hmac"', html)
        m = RE_JSON.search(html)
        self.assertIsNotNone(m)
        dados = json.loads(m.group(1))
        self.assertEqual(list(dados), ["hmac"])
        esperado = next(v for v in glossario_dados.GLOSSARIO if v["id"] == "hmac")
        self.assertEqual(dados["hmac"]["significado"], esperado["significado"])
        self.assertLess(m.start(), html.index("<!-- Scripts Interativos Embutidos -->"))
        self.assertEqual(html[m.end():].lstrip().split("\n")[0].strip(),
                         "<!-- Scripts Interativos Embutidos -->")

    def test_modulo_sem_termo_sem_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            body = Path(tmp) / "fixture_body.html"
            body.write_text(corpo_valido(), encoding="utf-8")
            html = compilar(body, "Threat-Hunting")
        self.assertNotIn("glossario-dados", html)

    def test_json_escapado(self):
        bloco = bloco_dados_glossario(
            ["x"], [{"id": "x", "termo": "X", "significado": "a</script>&b"}])
        interno = bloco[bloco.index(">") + 1:bloco.rindex("</script>")]
        self.assertNotIn("</script>", interno)
        self.assertNotIn("&b", interno)
        self.assertEqual(json.loads(interno)["x"]["significado"], "a</script>&b")

    def test_sem_ids_devolve_vazio(self):
        self.assertEqual(bloco_dados_glossario([], []), "")

    def test_glossario_invalido_aborta(self):
        ruim = [{"id": "hmac", "termo": "HMAC"}]
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch("glossario_dados.GLOSSARIO", ruim):
            err = io.StringIO()
            with contextlib.redirect_stderr(err), self.assertRaises(SystemExit) as cm:
                montar.main([str(GERADORES / "fundamentos_ciber_body.html"),
                             str(Path(tmp) / "x.html")])
        self.assertEqual(cm.exception.code, 1)
        self.assertIn("glossario ", err.getvalue())


if __name__ == "__main__":
    unittest.main()
