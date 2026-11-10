"""Conteúdo SSDLC/SLSA/secrets do estudo DevSecOps-e-CI-CD."""

import re
import sys
import unittest
from pathlib import Path

GERADORES = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GERADORES))

from contrato import extrair_secoes, validar_corpo  # noqa: E402

CORPO = GERADORES / "devsecops_e_ci_cd_body.html"


class TestDevsecopsConteudo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = CORPO.read_text(encoding="utf-8")

    def test_validar_corpo(self):
        self.assertEqual(validar_corpo(self.html, CORPO.stem), [])

    def test_ordem_secoes(self):
        ids = [s.id for s in extrair_secoes(self.html)]
        self.assertIn("ssdlc-samm", ids)
        self.assertIn("secrets-no-pipeline", ids)
        self.assertLess(ids.index("introducao"), ids.index("ssdlc-samm"))
        self.assertLess(ids.index("ssdlc-samm"), ids.index("cadeia"))
        self.assertLess(ids.index("cadeia"), ids.index("secrets-no-pipeline"))

    def test_mencoes_chave(self):
        self.assertIn("SSDLC", self.html)
        self.assertIn("SAMM", self.html)
        self.assertIn("SLSA", self.html)
        self.assertIn("VEX", self.html)
        html_cf = self.html.casefold()
        self.assertTrue("secret" in html_cf or "segredo" in html_cf)

    def test_slsa_na_cadeia_nao_so_em_secrets(self):
        secoes = {s.id: s for s in extrair_secoes(self.html)}
        # extrair_secoes may not expose raw HTML; use id markers in full file
        m_cadeia = re.search(
            r'id="cadeia".*?(?=<section class="study-section"|$)', self.html, flags=re.S
        )
        self.assertIsNotNone(m_cadeia)
        self.assertIn("SLSA", m_cadeia.group(0))
        self.assertIn("VEX", m_cadeia.group(0))

    def test_checklist_temas(self):
        labels = re.findall(r"<label[^>]*>(.*?)</label>", self.html, flags=re.S | re.I)
        textos = [re.sub(r"<[^>]+>", "", l).casefold() for l in labels]
        chaves = ("ssdlc", "champion", "slsa", "vex", "secret", "segredo", "revog")
        n = sum(1 for t in textos if any(k in t for k in chaves))
        self.assertGreaterEqual(n, 3, textos)

    def test_questoes_temas(self):
        partes = re.split(r'<div class="quiz-item">', self.html)[1:]
        chaves = ("ssdlc", "samm", "slsa", "vex", "secret", "segredo", "champion")
        n = sum(1 for b in partes if any(k in b.casefold() for k in chaves))
        self.assertGreaterEqual(n, 3)

    def test_sem_laboratorio(self):
        self.assertNotIn('data-tipo="laboratorio"', self.html)
        self.assertNotIn("lab-box", self.html)


if __name__ == "__main__":
    unittest.main()
