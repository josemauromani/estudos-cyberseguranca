"""Conteúdo SAML/SCIM do estudo Autenticacao-e-IAM (spec identidade federada)."""

import re
import sys
import unittest
from pathlib import Path

GERADORES = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GERADORES))

from contrato import extrair_secoes, validar_corpo  # noqa: E402

CORPO = GERADORES / "autenticacao_e_iam_body.html"


class TestAutenticacaoIamConteudo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = CORPO.read_text(encoding="utf-8")

    def test_validar_corpo(self):
        self.assertEqual(validar_corpo(self.html, CORPO.stem), [])

    def test_secoes_saml_scim_entre_oidc_e_jwt(self):
        ids = [s.id for s in extrair_secoes(self.html)]
        self.assertIn("saml-sso", ids)
        self.assertIn("scim-provisionamento", ids)
        self.assertLess(ids.index("federacao-oauth-oidc"), ids.index("saml-sso"))
        self.assertLess(ids.index("saml-sso"), ids.index("scim-provisionamento"))
        self.assertLess(ids.index("scim-provisionamento"), ids.index("anatomia-jwt"))

    def test_menciona_saml_e_scim(self):
        self.assertIn("SAML", self.html)
        self.assertIn("SCIM", self.html)

    def test_checklist_com_itens_federacao(self):
        labels = re.findall(r"<label[^>]*>(.*?)</label>", self.html, flags=re.S | re.I)
        textos = [re.sub(r"<[^>]+>", "", l).casefold() for l in labels]
        chaves = ("saml", "scim", "acs", "asserção", "assert")
        n = sum(1 for t in textos if any(k in t for k in chaves))
        self.assertGreaterEqual(n, 3, textos)

    def test_questoes_saml_ou_scim(self):
        partes = re.split(r'<div class="quiz-item">', self.html)[1:]
        n = sum(1 for bloco in partes if "saml" in bloco.casefold() or "scim" in bloco.casefold())
        self.assertGreaterEqual(n, 3)


if __name__ == "__main__":
    unittest.main()
