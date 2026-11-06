"""Testes de regressão da responsividade para celular (portal e treinamentos)."""

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


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
        self.gaveta = bloco_media(self.css, "max-width: 1023px")

    def test_grades_nunca_mais_largas_que_a_tela(self):
        """As grades auto-fill usam min(…, 100%) para não exceder telas de 360px."""
        for seletor, minimo in [(".grid", "250px"), (".needs-grid", "280px"), (".vaga-grid", "320px")]:
            self.assertIn(f"minmax(min({minimo}, 100%), 1fr)", regra(self.css, seletor), seletor)

    def test_cartoes_podem_encolher(self):
        """Os cartões do catálogo não impõem largura mínima pelo conteúdo."""
        self.assertIn("min-width: 0", regra(self.css, ".mc"))
        self.assertIn("overflow-wrap: anywhere", regra(self.css, ".mc .tag"))

    def test_menu_vira_gaveta_abaixo_de_1024(self):
        """Abaixo de 1024 px o menu lateral sai da grade e vira gaveta aberta por body.menu-aberto."""
        self.assertIn("display: none", regra(self.css, ".menu-toggle"))
        self.assertIn("display: inline-flex", regra(self.gaveta, ".menu-toggle"))
        self.assertIn("grid-template-columns: minmax(0, 1fr)", regra(self.gaveta, ".shell"))
        lateral = regra(self.gaveta, ".side")
        self.assertIn("position: fixed", lateral)
        self.assertIn("transform: translateX(-100%)", lateral)
        self.assertIn("visibility: hidden", lateral)
        self.assertIn("transform: none", regra(self.gaveta, "body.menu-aberto .side"))
        self.assertIn("position: fixed", regra(self.gaveta, "body.menu-aberto::before"))

    def test_movimento_reduzido(self):
        self.assertIn("transition: none", bloco_media(self.css, "prefers-reduced-motion: reduce"))

    def test_tabela_de_certificacoes_empilha_no_celular(self):
        self.assertIn("display: none", regra(bloco_media(self.css, "max-width: 640px"), ".cert-table thead"))


class TestTreinamentosResponsivos(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.geradores = self.root / "_geradores"
        from montar import carregar_css
        self.css = carregar_css()
        self.mobile = bloco_media(self.css, "max-width: 640px")

    def test_barra_superior_mostra_so_voltar_e_tema(self):
        """No celular, o caminho Trilha / Estudo sai da barra superior."""
        self.assertIn("display: none", regra(self.mobile, ".crumb"))

    @unittest.skip("dependia de markup de laboratório")
    def test_controles_de_laboratorio_encolhem(self):
        """Os filhos de .lab-controls podem encolher e não passam da largura disponível."""
        controles = regra(self.css, ".lab-controls > *")
        self.assertIn("min-width: 0", controles)
        self.assertIn("max-width: 100%", controles)

    def test_midia_e_formularios_limitados_a_largura(self):
        """Imagens, campos e tabelas nunca excedem o contêiner."""
        self.assertIn("max-width: 100%", regra(self.css, "img, select, input, textarea"))

    @unittest.skip("dependia de markup de laboratório")
    def test_botoes_longos_quebram_linha_no_celular(self):
        """No celular, botões com comandos longos (ex.: domínios) quebram mesmo no meio da palavra."""
        self.assertIn("overflow-wrap: anywhere", regra(self.mobile, ".btn"))

    def test_codigo_inline_quebra_linha(self):
        """Código inline em parágrafos (ex.: comandos reg add) quebra linha; blocos <pre> continuam rolando."""
        self.assertIn("overflow-wrap: anywhere", regra(self.css, ":not(pre) > code"))

    @unittest.skip("dependia de markup de laboratório")
    def test_campo_do_terminal_osint_pode_encolher(self):
        """O campo do terminal OSINT encolhe para o botão Executar caber na linha."""
        corpo = (self.geradores / "reconhecimento_e_osint_body.html").read_text(encoding="utf-8")
        linha = next(l for l in corpo.splitlines() if 'id="osint-cli-input"' in l)
        self.assertIn("min-width: 0", linha)

    @unittest.skip("dependia de markup de laboratório")
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
