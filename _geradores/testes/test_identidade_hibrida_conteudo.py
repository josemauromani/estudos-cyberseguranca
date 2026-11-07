"""Ponte SAML/Entra no estudo Identidade-Hibrida-e-Nuvem."""

import re
import sys
import unittest
from pathlib import Path

GERADORES = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GERADORES))

from contrato import extrair_secoes, validar_corpo  # noqa: E402

CORPO = GERADORES / "identidade_hibrida_e_nuvem_body.html"


class TestIdentidadeHibridaConteudo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = CORPO.read_text(encoding="utf-8")

    def test_validar_corpo(self):
        self.assertEqual(validar_corpo(self.html, CORPO.stem), [])

    def test_secao_ponte_saml(self):
        ids = [s.id for s in extrair_secoes(self.html)]
        self.assertIn("federacao-saml-entra", ids)
        self.assertIn("SAML", self.html)

    def test_remissao_ao_iam(self):
        html_cf = self.html.casefold()
        ok = (
            "Autenticacao-e-IAM" in self.html
            or "autenticação e iam" in html_cf
            or ("estudo" in html_cf and "iam" in html_cf and "saml" in html_cf)
        )
        self.assertTrue(ok, "esperava remissão ao estudo Autenticação e IAM")

    def test_checklist_e_questao(self):
        labels = re.findall(r"<label[^>]*>(.*?)</label>", self.html, flags=re.S | re.I)
        textos = [re.sub(r"<[^>]+>", "", l).casefold() for l in labels]
        self.assertGreaterEqual(
            sum(1 for t in textos if "saml" in t or "federa" in t), 1, textos
        )
        partes = re.split(r'<div class="quiz-item">', self.html)[1:]
        self.assertGreaterEqual(
            sum(1 for b in partes if "saml" in b.casefold() or "federa" in b.casefold()), 1
        )


if __name__ == "__main__":
    unittest.main()
