"""Testes dos componentes do novo design (base.css) e da preservação dos simuladores (laboratorio.css)."""

import re
import sys
import unittest
from pathlib import Path

TESTES = Path(__file__).resolve().parent
sys.path.insert(0, str(TESTES.parent))
sys.path.insert(0, str(TESTES))

from montar import carregar_css  # noqa: E402
from test_responsivo import bloco_media, regra  # noqa: E402
from test_tokens import GERADORES, TIPOS, bloco, declaracoes, git_show  # noqa: E402

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


# ---------------------------------------------------------------------------
# Contraste WCAG AA dos rótulos pequenos coloridos (spec §2.3)
# ---------------------------------------------------------------------------
TEMAS = {
    "claro": ":root {",
    "escuro": ':root[data-theme="dark"]',
}
CALLOUTS = {"tip": ("--tip-color", "--tip-bg"), "warning": ("--warning-color", "--warning-bg"),
            "danger": ("--danger-color", "--danger-bg"), "law": ("--law-color", "--law-bg"),
            "key": ("--accent", "--accent-soft")}


def declarado(css, seletor, prop):
    """Valor da última declaração `prop` na regra de seletor exato (a que vale na cascata)."""
    corpo = regra(css, seletor)
    valores = re.findall(r"(?<![-\w])" + re.escape(prop) + r"\s*:\s*([^;]+);", corpo)
    if not valores:
        raise AssertionError(f"{seletor} sem {prop}")
    return valores[-1].strip()


def resolver(expr, tokens, base, local):
    """Resolve hex, rgba (composto sobre `base`), var() com fallback e color-mix(in srgb) para (r, g, b)."""
    expr = expr.strip()
    m = re.fullmatch(r"color-mix\(in srgb,\s*(.+?)\s+(\d+(?:\.\d+)?)%,\s*(.+)\)", expr)
    if m:
        p = float(m.group(2)) / 100
        a = resolver(m.group(1), tokens, base, local)
        b = resolver(m.group(3), tokens, base, local)
        return tuple(a[i] * p + b[i] * (1 - p) for i in range(3))
    m = re.fullmatch(r"var\((--[\w-]+)(?:,\s*(.+))?\)", expr)
    if m:
        nome, reserva = m.group(1), m.group(2)
        if nome in local:
            return resolver(local[nome], tokens, base, local)
        if nome in tokens:
            return resolver(tokens[nome], tokens, base, local)
        return resolver(reserva, tokens, base, local)
    if expr.startswith("#"):
        return tuple(int(expr[i:i + 2], 16) for i in (1, 3, 5))
    m = re.fullmatch(r"rgba\((\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)\)", expr)
    if m:
        alfa = float(m.group(4))
        return tuple(int(m.group(i + 1)) * alfa + base[i] * (1 - alfa) for i in range(3))
    raise ValueError(f"cor não suportada: {expr}")


def contraste(a, b):
    def lum(c):
        c = [x / 255 for x in c]
        c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    la, lb = sorted([lum(a), lum(b)], reverse=True)
    return (la + 0.05) / (lb + 0.05)


def casos_de_contraste(css, trilhas):
    """(descrição, texto, fundo, sob, local): `fundo` é composto sobre o token `sob`."""
    casos = []
    for nome, (cc, cs) in CALLOUTS.items():
        for sob in ("--ground", "--surface"):
            casos.append((f".callout.{nome} .callout-title sobre {sob}", declarado(css, ".callout-title", "color"),
                          "var(--cs)", sob, {"--cc": f"var({cc})", "--cs": f"var({cs})"}))
    for t in TIPOS:
        local = {"--c": f"var(--tipo-{t})", "--soft": f"var(--tipo-{t}-bg)"}
        fundo_stype = declarado(css, ".stype", "background")
        casos.append((f".stype {t}", declarado(css, ".stype", "color"), fundo_stype, "--ground", local))
        casos.append((f".stype small {t}", declarado(css, ".stype small", "color"), fundo_stype, "--ground", local))
        for fundo, sob in (("var(--ground)", "--ground"), ("var(--surface)", "--surface"),
                           ("var(--soft)", "--surface")):  # sumário, item atual, roadmap
            casos.append((f".toc-tipo {t} sobre {fundo}", declarado(css, ".toc-tipo", "color"), fundo, sob, local))
        casos.append((f".tipo-atual {t}", declarado(css, ".tipo-atual", "color"),
                      declarado(css, ".tipo-atual", "background"), "--surface", local))
    for trilha in trilhas:
        casos.append((f".mhead-kicker {trilha}", declarado(css, ".mhead-kicker", "color"), "var(--surface)",
                      "--surface", {"--track-color": f"var({trilha})"}))
    for v in ("acertei", "errei", "revisar"):
        sel = f'.quiz-selfeval button[data-v="{v}"].on'
        casos.append((sel, declarado(css, sel, "color"), declarado(css, sel, "background"), "--surface", {}))
    casos.append((".quiz-selfeval button", declarado(css, ".quiz-selfeval button", "color"),
                  declarado(css, ".quiz-selfeval button", "background"), "--surface", {}))
    casos.append((".btn-concluir", declarado(css, ".btn-concluir", "color"),
                  declarado(css, ".btn-concluir", "background"), "--surface", {}))
    casos.append((".btn-concluir.pronto", declarado(css, ".btn-concluir.pronto", "color"),
                  declarado(css, ".btn-concluir.pronto", "background"), "--surface", {}))
    for sob in ("--ground", "--surface"):  # no sumário e na caixa de conclusão
        casos.append((f".btn-concluir.concluido sobre {sob}", declarado(css, ".btn-concluir.concluido", "color"),
                      f"var({sob})", sob, {}))
        casos.append((f".toc-contador sobre {sob}", declarado(css, ".toc-contador", "color"), f"var({sob})", sob, {}))
    casos.append((".quiz-score > span", "var(--ink)", declarado(css, ".quiz-score > span", "background"),
                  "--surface", {}))
    sel_filtro = '.quiz-filtros button.on, .quiz-filtros button[aria-pressed="true"]'
    casos.append((".quiz-filtros button.on", declarado(css, sel_filtro, "color"),
                  declarado(css, sel_filtro, "background"), "--surface", {}))
    casos.append((".quiz-question > strong:first-child", declarado(css, ".quiz-question > strong:first-child", "color"),
                  "var(--surface)", "--surface", {}))
    casos.append((".diagram-badge", declarado(css, ".diagram-badge", "color"), "var(--surface)", "--surface", {}))
    return casos


class TestContrasteAA(unittest.TestCase):
    def test_rotulos_pequenos_coloridos_tem_4_5_para_1(self):
        base_css = (GERADORES / "base.css").read_text(encoding="utf-8")
        tokens_css = (GERADORES / "tokens.css").read_text(encoding="utf-8")
        claro = declaracoes(bloco(tokens_css, TEMAS["claro"]))
        trilhas = sorted(n for n in claro if re.fullmatch(r"--t\d+-[a-z]+", n))
        self.assertEqual(len(trilhas), 14)
        for tema, inicio in TEMAS.items():
            tokens = dict(claro)
            tokens.update(declaracoes(bloco(tokens_css, inicio)))
            for descricao, texto, fundo, sob, local in casos_de_contraste(base_css, trilhas):
                with self.subTest(tema=tema, caso=descricao):
                    chao = resolver(f"var({sob})", tokens, (255, 255, 255), {})
                    cor_fundo = resolver(fundo, tokens, chao, local)
                    cor_texto = resolver(texto, tokens, cor_fundo, local)
                    self.assertGreaterEqual(contraste(cor_texto, cor_fundo), 4.5)


if __name__ == "__main__":
    unittest.main()
