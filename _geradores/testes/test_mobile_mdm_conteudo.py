"""Conteúdo MASVS/MDM do estudo Seguranca-em-Mobile-e-MDM."""

import re
import sys
import unittest
from pathlib import Path

GERADORES = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GERADORES))

from contrato import extrair_secoes, validar_corpo  # noqa: E402

CORPO = GERADORES / "seguranca_em_mobile_e_mdm_body.html"

ORDEM = [
    "introducao",
    "masvs-riscos",
    "android-ios",
    "lab-mental-mobile",
    "mdm-uem-byod",
    "matriz-controles",
]


class TestMobileMdmConteudo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = CORPO.read_text(encoding="utf-8")

    def test_validar_corpo(self):
        self.assertEqual(validar_corpo(self.html, CORPO.stem), [])

    def test_ordem_secoes(self):
        ids = [s.id for s in extrair_secoes(self.html)]
        for sid in ORDEM:
            self.assertIn(sid, ids)
        for a, b in zip(ORDEM, ORDEM[1:]):
            self.assertLess(ids.index(a), ids.index(b))

    def test_lab_mental_e_teoria(self):
        for s in extrair_secoes(self.html):
            if s.id == "lab-mental-mobile":
                self.assertEqual(s.tipo, "teoria")
                break
        else:
            self.fail("lab-mental-mobile ausente")

    def test_mencoes_chave(self):
        self.assertIn("MASVS", self.html)
        html_cf = self.html.casefold()
        self.assertTrue("mastg" in html_cf)
        self.assertIn("MDM", self.html)
        self.assertIn("BYOD", self.html)
        self.assertIn("Android", self.html)
        self.assertTrue("ios" in html_cf)

    def test_checklist_temas(self):
        labels = re.findall(r"<label[^>]*>(.*?)</label>", self.html, flags=re.S | re.I)
        textos = [re.sub(r"<[^>]+>", "", l).casefold() for l in labels]
        chaves = ("masvs", "mdm", "byod", "matriz", "android", "ios", "keystore", "wipe")
        n = sum(1 for t in textos if any(k in t for k in chaves))
        self.assertGreaterEqual(n, 4, textos)

    def test_questoes_temas(self):
        partes = re.split(r'<div class="quiz-item">', self.html)[1:]
        chaves = ("masvs", "mdm", "byod", "android", "ios", "keystore", "deeplink", "matriz")
        n = sum(1 for b in partes if any(k in b.casefold() for k in chaves))
        self.assertGreaterEqual(n, 4)

    def test_sem_laboratorio(self):
        self.assertNotIn('data-tipo="laboratorio"', self.html)
        self.assertNotIn("lab-box", self.html)


if __name__ == "__main__":
    unittest.main()
