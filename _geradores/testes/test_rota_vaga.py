#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testes dos dados da rota da vaga, das certificações e da carreira Analista de SI."""

import re
import sys
import unittest
from html import escape
from pathlib import Path

GERADORES_DIR = Path(__file__).resolve().parent.parent
GERADORES = GERADORES_DIR
ROOT = GERADORES_DIR.parent
sys.path.insert(0, str(GERADORES_DIR))

from index_dados import (  # noqa: E402
    CARREIRAS,
    CERTIFICACOES,
    ESTUDOS_DADOS,
    NECESSIDADES,
    ROTA_VAGA,
    ROTULO_ANALISTA_SI,
)

from build_index import (  # noqa: E402
    gerar_index_html,
    render_certificacoes,
    render_chip_modulo,
    render_rota_vaga,
)

ESTUDOS_TXT = GERADORES_DIR / "estudos.txt"
SLUGS = {l.split("|")[0].strip() for l in ESTUDOS_TXT.read_text(encoding="utf-8").splitlines()
         if l.strip() and not l.startswith("#")}


class TestRotaVagaDados(unittest.TestCase):
    def test_slugs_existem_no_catalogo(self):
        for c in ROTA_VAGA:
            for s in c["principais"] + c["apoio"]:
                self.assertIn(s, SLUGS, c["id"])
        for cert in CERTIFICACOES:
            for s in cert["modulos"]:
                self.assertIn(s, SLUGS, cert["sigla"])

    def test_sete_competencias_com_principal(self):
        self.assertEqual([c["id"] for c in ROTA_VAGA],
            ["solucoes", "banco_dados", "ingles", "normas", "resposta_incidentes", "controles", "formacao"])
        for c in ROTA_VAGA:
            self.assertGreaterEqual(len(c["principais"]), 1, c["id"])

    def test_certificacoes_exatas(self):
        siglas = [c["sigla"] for c in CERTIFICACOES]
        self.assertEqual(siglas, ["CEH", "CISM", "CISSP", "CCSP", "GSEC", "Security+",
                                  "ISFS", "PDPF/PDPP", "ITIL 4 F", "CSFPC", "CISA", "ISO 27001 LA", "eJPT", "eCPPT", "OSCP", "CRISC", "CDPSE", "CGEIT"])
        self.assertEqual(len(siglas), len(set(siglas)))

    def test_modulos_da_rota_tem_carreira_analista(self):
        for c in ROTA_VAGA:
            for s in c["principais"] + c["apoio"]:
                self.assertIn(ROTULO_ANALISTA_SI, ESTUDOS_DADOS[s]["carreiras"], s)

    def test_carreiras_sem_substring(self):
        nomes = [c["nome"] for c in CARREIRAS.values()]
        for a in nomes:
            for b in nomes:
                if a != b:
                    self.assertNotIn(a, b)

    def test_necessidades_novas(self):
        alvo = {"Protecao-de-Dados-e-Conteudo", "Seguranca-de-Bancos-de-Dados", "PCI-DSS",
                "Ingles-Tecnico-Ciber", "Certificacoes-e-Carreira"}
        self.assertTrue(alvo <= {n["slug"] for n in NECESSIDADES})


def _status(disponiveis):
    return {s: {"disponivel": s in disponiveis, "caminho_relativo": f"{s}/treinamento-{s.lower()}.html"}
            for s in SLUGS}


class TestRotaVagaRender(unittest.TestCase):
    def test_chip_disponivel_e_pendente(self):
        st = _status({"Segmentacao-e-Firewall"})
        self.assertIn('<a href="Segmentacao-e-Firewall/treinamento-segmentacao-e-firewall.html"',
                      render_chip_modulo("Segmentacao-e-Firewall", st))
        pend = render_chip_modulo("PCI-DSS", st)
        self.assertIn('aria-disabled="true"', pend)
        self.assertNotIn("<a ", pend)
        self.assertIn("31 · ", pend)  # número do módulo = posição em estudos.txt
        self.assertIn("⏳ 31 · ", pend)
        disp = render_chip_modulo("Segmentacao-e-Firewall", st)
        self.assertNotIn("⏳", disp)

    def test_css_pendente_sem_opacity(self):
        css = (GERADORES / "index.css").read_text(encoding="utf-8")
        ini = css.index(".vaga-chip.pendente {")
        regra = css[ini:css.index("}", ini)]
        self.assertNotIn("opacity", regra)
        self.assertIn("dashed", regra)

    def test_legenda_dos_estados(self):
        html = render_rota_vaga(ROTA_VAGA, _status(set()))
        self.assertIn("em construção", html)
        self.assertIn("apoio", html)
        self.assertIn('class="vaga-legenda"', html)

    def test_texto_vaga_igual_a_competencia_omitido(self):
        item = {"id": "x", "competencia": "Inglês", "texto_vaga": " inglês ", "icone": "🌍",
                "principais": ["Ingles-Tecnico-Ciber"], "apoio": []}
        html = render_rota_vaga([item], _status(set()))
        self.assertNotIn('<p class="vaga-texto">', html)
        item["texto_vaga"] = "Leitura de manuais em Inglês"
        self.assertIn('<p class="vaga-texto">', render_rota_vaga([item], _status(set())))

    def test_chips_ordenados_por_numero(self):
        import re
        item = next(c for c in ROTA_VAGA if c["id"] == "solucoes")
        html = render_rota_vaga([item], _status(set()))
        nums = re.findall(r"(\d\d) · ", html.split('class="vaga-chips"')[1])
        principais = [f"{list(ESTUDOS_DADOS).index(s) + 1:02d}" for s in item["principais"]]
        self.assertEqual(nums[:len(principais)], sorted(principais))
        self.assertEqual(nums[:4], ["05", "07", "10", "29"])
        apoio = nums[len(principais):]
        self.assertEqual(apoio, sorted(apoio))

    def test_contador_so_principais(self):
        # 15 é só apoio em "solucoes"; não pode contar
        html = render_rota_vaga(ROTA_VAGA, _status({"Engenharia-Social-e-Phishing"}))
        self.assertIn("0 de 7 competências com módulo disponível", html)
        html = render_rota_vaga(ROTA_VAGA, _status({"Segmentacao-e-Firewall", "Seguranca-de-Bancos-de-Dados"}))
        self.assertIn("2 de 7 competências com módulo disponível", html)

    def test_contador_zero(self):
        self.assertIn("0 de 7", render_rota_vaga(ROTA_VAGA, _status(set())))

    def test_certificacoes_render(self):
        html = render_certificacoes(CERTIFICACOES, _status(set()))
        for c in CERTIFICACOES:
            self.assertIn(escape(c["sigla"]), html)
        self.assertEqual(html.count('<tr class="cert-row"'), len(CERTIFICACOES))
        self.assertIn("Confira os requisitos atuais no site oficial do órgão emissor", html)

    def test_matriz_link_site_oficial(self):
        html = render_certificacoes(CERTIFICACOES, _status(set()))
        linhas = html.split('<tr class="cert-row"')[1:]
        self.assertEqual(len(linhas), len(CERTIFICACOES))
        for c, linha in zip(CERTIFICACOES, linhas):
            with self.subTest(cert=c["sigla"]):
                self.assertIn(
                    f'<a class="cert-site" href="{escape(c["site_oficial"], quote=True)}" target="_blank" rel="noopener noreferrer"',
                    linha)
        conteudo = (ROOT / "index.html").read_text(encoding="utf-8")
        for c in CERTIFICACOES:
            self.assertIn(f'href="{escape(c["site_oficial"], quote=True)}"', conteudo)
        self.assertEqual(conteudo.count('<tr class="cert-row"'), len(CERTIFICACOES))

    def test_portal_contem_secoes_cada_uma_na_sua_visao(self):
        conteudo = Path(gerar_index_html(output_path=ROOT / "index.html")).read_text(encoding="utf-8")
        visoes = [m.start() for m in re.finditer(r'<section class="view" data-view="', conteudo)] + [conteudo.index("</main>")]

        def visao_de(marcador):
            i = conteudo.index(marcador)
            j = max(k for k, v in enumerate(visoes) if v < i)
            return re.match(r'<section class="view" data-view="(\w+)"', conteudo[visoes[j]:]).group(1)

        self.assertEqual(visao_de('id="secao-necessidades"'), "necessidades")
        self.assertEqual(visao_de('id="secao-rota-vaga"'), "vaga")
        self.assertEqual(visao_de('id="secao-certificacoes"'), "certificacoes")
        self.assertEqual(visao_de('id="secao-catalogo"'), "catalogo")
        self.assertIn("Rota por Vaga: Analista de Segurança da Informação", conteudo)
        self.assertIn("Matriz de Certificações", conteudo)

    def test_css_responsivo_certificacoes(self):
        css = (GERADORES / "index.css").read_text(encoding="utf-8")
        bloco = css[css.index("@media (max-width: 640px)"):]
        self.assertIn(".cert-table", bloco)


class TestContadorDoPortalReal(unittest.TestCase):
    def test_contador_da_rota_bate_com_modulos_compilados(self):
        """O "X de 7" do index.html versionado reflete os módulos principais já compilados."""
        compilados = set()
        for linha in ESTUDOS_TXT.read_text(encoding="utf-8").splitlines():
            if linha.strip() and not linha.startswith("#"):
                slug, _t, pasta, arquivo = [p.strip() for p in linha.split("|")[:4]]
                if (ROOT / pasta / arquivo).exists():
                    compilados.add(slug)
        cobertas = sum(1 for c in ROTA_VAGA if set(c["principais"]) & compilados)
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn(f"{cobertas} de {len(ROTA_VAGA)} competências com módulo disponível", html)


if __name__ == "__main__":
    unittest.main()
