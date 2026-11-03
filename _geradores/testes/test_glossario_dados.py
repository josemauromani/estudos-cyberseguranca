"""Testes do cadastro do glossário (glossario_dados.py) e da validação (glossario.py)."""

import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from glossario import GlossarioInvalido, carregar_glossario, texto_sem_html, validar_glossario
from glossario_dados import GLOSSARIO


def _verbete(**extra):
    base = {"id": "hmac", "termo": "HMAC", "significado": "Código de autenticação."}
    base.update(extra)
    return base


class TestGlossarioDados(unittest.TestCase):
    def test_glossario_real_valido(self):
        self.assertEqual(validar_glossario(GLOSSARIO), [])

    def test_hmac_cadastrado(self):
        v = next(x for x in GLOSSARIO if x["id"] == "hmac")
        self.assertEqual(v["termo"], "HMAC")
        self.assertEqual(v["categoria"], "Criptografia")
        self.assertTrue(v["sigla_de"].startswith("Hash-based Message Authentication Code"))
        self.assertEqual(v["variacoes"], ["HMAC-SHA256", "HMAC-SHA1"])
        self.assertEqual(v["relacionados"], [])
        self.assertEqual([r[0] for r in v["referencias"]], ["RFC 2104", "FIPS 198-1"])
        self.assertEqual(
            [r[1] for r in v["referencias"]],
            ["https://www.rfc-editor.org/rfc/rfc2104", "https://csrc.nist.gov/pubs/fips/198-1/final"],
        )

    def test_campos_obrigatorios(self):
        erros = validar_glossario([{"id": "hmac", "termo": "HMAC"}])
        self.assertTrue(any("significado" in e for e in erros))

    def test_id_invalido_e_duplicado(self):
        for ruim in ("HMAC", "hmac_x"):
            erros = validar_glossario([_verbete(id=ruim)])
            self.assertTrue(any("id" in e and "formato" in e for e in erros), ruim)
        erros = validar_glossario([_verbete(), _verbete()])
        self.assertTrue(any("duplicado" in e for e in erros))

    def test_relacionado_inexistente(self):
        erros = validar_glossario([_verbete(relacionados=["nao-existe"])])
        self.assertTrue(any("nao-existe" in e for e in erros))

    def test_referencia_sem_https(self):
        erros = validar_glossario([_verbete(referencias=[("X", "http://x")])])
        self.assertTrue(any("referencias" in e for e in erros))

    def test_html_proibido(self):
        for ruim in ('<a href="x">l</a>', "<script>x</script>"):
            erros = validar_glossario([_verbete(significado=ruim)])
            self.assertTrue(any("significado" in e for e in erros), ruim)
        ok = "<strong>a</strong> <em>b</em> <code>c</code>"
        self.assertEqual(validar_glossario([_verbete(significado=ok)]), [])

    def test_menor_que_solto_proibido(self):
        for texto in ("valor <limite", "a < b"):
            self.assertTrue(validar_glossario([_verbete(significado=texto)]), texto)
        self.assertEqual(validar_glossario([_verbete(significado="<strong>x</strong>")]), [])

    def test_campo_desconhecido(self):
        erros = validar_glossario([_verbete(pronuncia="rá-qui")])
        self.assertTrue(any("pronuncia" in e for e in erros))

    def test_carregar_levanta(self):
        with mock.patch("glossario_dados.GLOSSARIO", [{"id": "X"}]):
            with self.assertRaises(GlossarioInvalido) as ctx:
                carregar_glossario()
        self.assertTrue(ctx.exception.erros)

    def test_carregar_real(self):
        self.assertEqual(carregar_glossario(), GLOSSARIO)

    def test_texto_sem_html(self):
        self.assertEqual(texto_sem_html("a <strong>b</strong> <code>c</code>"), "a b c")


if __name__ == "__main__":
    unittest.main()
