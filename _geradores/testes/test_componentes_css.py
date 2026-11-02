"""Testes dos componentes do novo design (base.css) e da preservação dos simuladores (laboratorio.css)."""

import re
import sys
import unittest
from pathlib import Path

TESTES = Path(__file__).resolve().parent
sys.path.insert(0, str(TESTES.parent))
sys.path.insert(0, str(TESTES))

from montar import carregar_css  # noqa: E402
from test_responsivo import bloco_media  # noqa: E402
from test_tokens import GERADORES, TIPOS, git_show  # noqa: E402

CLASSES_T3 = [
    ".topbar", ".topbar-in", ".nav-back", ".crumb", ".tipo-atual", ".theme-toggle-btn", ".toc-toggle",
    ".readbar", ".shell", ".content", ".toc", ".toc-lista", ".toc-item", ".toc-item.on", ".toc-item.lida",
    ".toc-contador", ".toc-progresso", ".btn-concluir", ".btn-concluir.pronto", ".btn-concluir.concluido",
    ".mhead", ".mhead-kicker", ".mhead-sub", ".chips", ".chip", ".roadmap", ".shead", ".stype", ".lead-text",
    ".callout", ".callout.tip", ".callout.warning", ".callout.danger", ".callout.law", ".callout.key",
    ".callout-title", ".callout-icon", ".table-responsive", ".data-table", ".terminal-box", ".terminal-header",
    ".terminal-title", ".terminal-copy-btn", ".diagram-box", ".diagram-header", ".diagram-title",
    ".diagram-svg-wrap", ".lab-box", ".lab-header", ".lab-body", ".checklist", ".checklist-head",
    ".checklist-item", ".checklist-item.completed", ".quiz-score", ".quiz-filtros", ".quiz-item",
    '.quiz-item[data-res="acertei"]', '.quiz-item[data-res="errei"]', '.quiz-item[data-res="revisar"]',
    ".quiz-question", ".quiz-details", ".quiz-toggle", ".quiz-answer", ".quiz-selfeval", ".facts-grid",
    ".facts-card", ".study-done", ".study-pager", "body.toc-aberto",
]


def classes_com_regra(css):
    """Nomes de classe que aparecem em seletores (texto antes de `{`), ignorando comentários e @-regras."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    nomes = set()
    for seletor in re.findall(r"([^{}]+)\{", css):
        if seletor.strip().startswith("@"):
            continue
        nomes |= set(re.findall(r"\.(-?[_a-zA-Z][\w-]*)", seletor))
    return nomes


class TestComponentesCss(unittest.TestCase):
    def test_classes_da_spec(self):
        css = carregar_css()
        for c in CLASSES_T3:  # a lista do bloco Produces acima
            self.assertRegex(css, re.escape(c) + r"[\s,{:.\[>]", c)

    def test_cinco_tipos_mapeados(self):
        css = carregar_css()
        for t in TIPOS:
            self.assertIn(f'[data-tipo="{t}"]', css)
            self.assertIn(f"var(--tipo-{t})", css)

    def test_classes_legadas_continuam_estilizadas(self):
        antigas = classes_com_regra(git_show("a671fbe:_geradores/base.css"))
        usadas = set()
        for corpo in GERADORES.glob("*_body.html"):
            for attr in re.findall(r'class="([^"]+)"', corpo.read_text(encoding="utf-8")):
                usadas |= set(attr.split())
        novas = classes_com_regra(carregar_css())
        removidas_de_proposito = {"hero-header", "hero-subtitle", "section-num", "section-title-wrap",
                                  "section-tag", "section-header", "study-header", "study-title",
                                  "study-lead", "study-track-kicker", "study-meta-bar", "content-section",
                                  "check-item", "callout-tip", "top-nav", "top-nav-inner", "nav-title",
                                  "nav-actions", "study-footer"}
        self.assertEqual((antigas & usadas) - novas - removidas_de_proposito, set())

    def test_gaveta_abaixo_de_1024(self):
        movel = bloco_media(carregar_css(), "max-width: 1023px")
        self.assertIn(".toc", movel)
        self.assertIn("body.toc-aberto .toc", movel)

    def test_movimento_reduzido_e_foco_visivel(self):
        css = carregar_css()
        self.assertIn("prefers-reduced-motion: reduce", css)
        self.assertIn(":focus-visible", css)


if __name__ == "__main__":
    unittest.main()
