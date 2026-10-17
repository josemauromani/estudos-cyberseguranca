"""Testes de regressão da responsividade para celular (portal e treinamentos)."""

import re
import unittest
from pathlib import Path


def bloco_media(css, consulta):
    """Concatena o conteúdo de todos os blocos @media com a consulta informada."""
    blocos = []
    for m in re.finditer(r"@media\s*\(" + re.escape(consulta) + r"\)\s*\{", css):
        nivel, i = 1, m.end()
        while nivel:
            nivel += {"{": 1, "}": -1}.get(css[i], 0)
            i += 1
        blocos.append(css[m.end():i - 1])
    return "\n".join(blocos)


def regra(css, seletor):
    """Retorna as declarações da primeira regra cujo seletor é exatamente o informado."""
    m = re.search(r"(?:^|\}|\*/)\s*" + re.escape(seletor) + r"\s*\{([^}]*)\}", css)
    return m.group(1) if m else ""


class TestPortalResponsivo(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.css = (self.root / "_geradores" / "index.css").read_text(encoding="utf-8")

    def test_grades_nunca_mais_largas_que_a_tela(self):
        """As grades auto-fill usam min(…, 100%) para não exceder telas de 360px."""
        for seletor, minimo in [(".needs-grid", "280px"), (".cards-grid", "340px"), (".vaga-grid", "320px")]:
            self.assertIn(f"minmax(min({minimo}, 100%), 1fr)", regra(self.css, seletor), seletor)

    def test_cards_podem_encolher(self):
        """Os cards do catálogo não impõem largura mínima pelo conteúdo."""
        self.assertIn("min-width: 0", regra(self.css, ".study-card"))

    def test_selos_quebram_linha_no_celular(self):
        """No celular, os selos (NIST, MITRE, carreiras) podem quebrar linha."""
        mobile = bloco_media(self.css, "max-width: 768px")
        self.assertIn("white-space: normal", regra(mobile, ".badge"))

    def test_abas_de_filtro_rolam_em_linha_unica(self):
        """No celular, as abas de filtro ficam numa linha com rolagem horizontal própria."""
        abas = regra(bloco_media(self.css, "max-width: 768px"), ".filter-tabs")
        self.assertIn("flex-wrap: nowrap", abas)
        self.assertIn("overflow-x: auto", abas)


class TestTreinamentosResponsivos(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.geradores = self.root / "_geradores"
        self.css = (self.geradores / "base.css").read_text(encoding="utf-8")
        self.mobile = bloco_media(self.css, "max-width: 640px")

    def test_barra_superior_mostra_so_voltar_e_tema(self):
        """No celular, o título e o selo de trilha saem da barra superior."""
        self.assertIn("display: none", regra(self.mobile, ".nav-title"))
        self.assertIn("display: none", regra(self.mobile, ".nav-actions .badge"))

    def test_controles_de_laboratorio_encolhem(self):
        """Os filhos de .lab-controls podem encolher e não passam da largura disponível."""
        controles = regra(self.css, ".lab-controls > *")
        self.assertIn("min-width: 0", controles)
        self.assertIn("max-width: 100%", controles)

    def test_midia_e_formularios_limitados_a_largura(self):
        """Imagens, campos e tabelas nunca excedem o contêiner."""
        self.assertIn("max-width: 100%", regra(self.css, "img, select, input, textarea"))

    def test_botoes_longos_quebram_linha_no_celular(self):
        """No celular, botões com comandos longos (ex.: domínios) quebram mesmo no meio da palavra."""
        self.assertIn("overflow-wrap: anywhere", regra(self.mobile, ".btn"))

    def test_codigo_inline_quebra_linha(self):
        """Código inline em parágrafos (ex.: comandos reg add) quebra linha; blocos <pre> continuam rolando."""
        self.assertIn("overflow-wrap: anywhere", regra(self.css, ":not(pre) > code"))

    def test_campo_do_terminal_osint_pode_encolher(self):
        """O campo do terminal OSINT encolhe para o botão Executar caber na linha."""
        corpo = (self.geradores / "reconhecimento_e_osint_body.html").read_text(encoding="utf-8")
        linha = next(l for l in corpo.splitlines() if 'id="osint-cli-input"' in l)
        self.assertIn("min-width: 0", linha)

    def test_grade_edr_vira_uma_coluna_no_celular(self):
        """A grade do inspetor EDR é definida no CSS e vira uma coluna no celular."""
        corpo = (self.geradores / "seguranca_em_endpoints_edr_body.html").read_text(encoding="utf-8")
        linha = next(l for l in corpo.splitlines() if 'class="edr-grid-container"' in l)
        self.assertNotIn("grid-template-columns", linha)
        self.assertIn("grid-template-columns: 1fr 1fr", regra(self.css, ".edr-grid-container"))
        self.assertIn("grid-template-columns: minmax(0, 1fr)", regra(self.mobile, ".edr-grid-container"))

    def test_tabelas_de_gestao_vulnerabilidades_rolam_na_propria_caixa(self):
        """Toda tabela de Gestão de Vulnerabilidades fica dentro de .table-responsive."""
        corpo = (self.geradores / "gestao_de_vulnerabilidades_body.html").read_text(encoding="utf-8")
        tabelas = corpo.count("<table")
        self.assertGreater(tabelas, 0)
        envolvidas = len(re.findall(r'<div class="table-responsive">\s*<table', corpo))
        self.assertEqual(envolvidas, tabelas)


if __name__ == "__main__":
    unittest.main()
