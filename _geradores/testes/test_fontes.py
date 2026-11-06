"""Testes das fontes embutidas (IBM Plex e Barlow Semi Condensed em WOFF2)."""
import sys
import tempfile
import unittest
from pathlib import Path
GERADORES_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GERADORES_DIR))
from fontes import FONTES_DIR, css_fontes

class TestFontes(unittest.TestCase):

    def test_cinco_faces_embutidas(self):
        css = css_fontes()
        self.assertEqual(css.count('@font-face'), 5)
        self.assertEqual(css.count('url(data:font/woff2;base64,'), 5)
        self.assertEqual(css.count('font-display: swap'), 5)
        for fam in ('"IBM Plex Sans"', '"IBM Plex Mono"', '"Barlow Semi Condensed"'):
            self.assertIn(f'font-family: {fam}', css)
        self.assertIn('font-style: italic', css)

    def test_orcamento_de_200kb(self):
        self.assertLess(len(css_fontes().encode('utf-8')), 200 * 1024)

    def test_arquivo_ausente_falha_com_nome(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(FileNotFoundError, 'ibm-plex-sans-latin-400-normal.woff2'):
                css_fontes(Path(d))

    def test_licenca_presente(self):
        self.assertIn('SIL Open Font License', (FONTES_DIR / 'OFL.txt').read_text(encoding='utf-8'))
if __name__ == '__main__':
    unittest.main()
