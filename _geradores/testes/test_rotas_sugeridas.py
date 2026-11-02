#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testes da aba "Rotas Sugeridas" do portal: dados das rotas, coerência com o CURRICULO e HTML gerado."""

import re
import sys
import tempfile
import unittest
from pathlib import Path

GERADORES_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GERADORES_DIR))

from index_dados import ESTUDOS_DADOS, ROTAS_PERFIL  # noqa: E402

from build_index import gerar_index_html, render_filtros_rota, render_painel_rotas  # noqa: E402

IDS_ESPERADOS = ["blue_soc", "red_team", "devsecops_cloud", "grc", "pericia", "analista_si"]


def numero(slug):
    return list(ESTUDOS_DADOS).index(slug) + 1


def sequencias_do_curriculo():
    """As 6 sequências do §5 do CURRICULO.md, na ordem em que aparecem, como listas de números."""
    txt = (GERADORES_DIR / "CURRICULO.md").read_text(encoding="utf-8")
    secao = txt.split("## 5. Rotas de Aprendizagem por Perfil Profissional", 1)[1]
    return [[int(n) for n in seq.split(" -> ")] for seq in re.findall(r"`(\d\d(?: -> \d\d)+)`", secao)]


class TestDadosDasRotas(unittest.TestCase):
    def test_seis_rotas_com_ids_e_campos(self):
        self.assertEqual([r["id"] for r in ROTAS_PERFIL], IDS_ESPERADOS)
        for r in ROTAS_PERFIL:
            with self.subTest(rota=r["id"]):
                for campo in ("nome", "icone", "descricao"):
                    self.assertTrue(r[campo].strip(), campo)
                self.assertGreaterEqual(len(r["modulos"]), 10)
                self.assertEqual(len(r["modulos"]), len(set(r["modulos"])), "módulo repetido na rota")
                for slug in r["modulos"]:
                    self.assertIn(slug, ESTUDOS_DADOS)

    def test_rotas_batem_com_o_curriculo(self):
        """O §5 do CURRICULO.md documenta as mesmas sequências que o portal mostra."""
        self.assertEqual(sequencias_do_curriculo(), [[numero(s) for s in r["modulos"]] for r in ROTAS_PERFIL])

    def test_rota_blue_team_comeca_e_termina_como_documentado(self):
        r = ROTAS_PERFIL[0]
        self.assertEqual(numero(r["modulos"][0]), 1)
        self.assertEqual(numero(r["modulos"][-1]), 42)
        self.assertEqual(len(r["modulos"]), 17)

    def test_rota_blue_team_poe_threat_intel_antes_da_engenharia_de_deteccao(self):
        """O 17 é pré-requisito do 46: a rota não pode pedir a detecção antes da inteligência."""
        m = [numero(s) for s in ROTAS_PERFIL[0]["modulos"]]
        self.assertEqual(m[m.index(16):m.index(47) + 1], [16, 17, 46, 47])


class TestHtmlDasRotas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as tmp:
            cls.html = gerar_index_html(output_path=Path(tmp) / "index.html").read_text(encoding="utf-8")

    def test_aba_e_botoes_das_rotas(self):
        self.assertIn('data-facet="rotas" onclick="switchTab(\'rotas\')">Rotas Sugeridas</button>', self.html)
        self.assertIn('<div class="filter-subpanel" data-panel="rotas"', self.html)
        botoes = render_filtros_rota(ROTAS_PERFIL)
        self.assertIn('data-value="all"', botoes)
        for r in ROTAS_PERFIL:
            self.assertIn(f'data-value="{r["id"]}"', botoes)

    def test_cards_marcam_as_rotas_de_que_fazem_parte(self):
        for slug in ESTUDOS_DADOS:
            esperado = [r["id"] for r in ROTAS_PERFIL if slug in r["modulos"]]
            m = re.search(rf'id="estudo-{re.escape(slug)}"[^>]*?data-rotas="([^"]*)"', self.html, re.S)
            with self.subTest(slug=slug):
                self.assertIsNotNone(m)
                self.assertEqual(m.group(1).split(), esperado)

    def test_painel_lista_os_passos_na_ordem_com_link(self):
        painel = render_painel_rotas(ROTAS_PERFIL, {s: {"disponivel": True, "caminho_relativo": f"{s}/x.html"} for s in ESTUDOS_DADOS})
        self.assertIn('id="secao-rota-sugerida"', painel)
        for r in ROTAS_PERFIL:
            bloco = re.search(rf'<div class="rota-sugerida" data-rota="{r["id"]}".*?</ol>', painel, re.S)
            with self.subTest(rota=r["id"]):
                self.assertIsNotNone(bloco)
                passos = re.findall(r'<li class="rota-passo" data-slug="([^"]+)"', bloco.group(0))
                self.assertEqual(passos, r["modulos"])
                for slug in r["modulos"]:
                    self.assertIn(f'href="{slug}/x.html"', bloco.group(0))
                self.assertIn('class="rota-progresso-texto"', bloco.group(0))
                self.assertIn('class="rota-proximo"', bloco.group(0))

    def test_painel_comeca_oculto_e_esta_no_portal(self):
        self.assertIn('<section class="rota-sugerida-section" id="secao-rota-sugerida" hidden', self.html)
        self.assertLess(self.html.index('id="secao-rota-sugerida"'), self.html.index('id="secao-catalogo"'))

    def test_javascript_filtra_e_atualiza_o_painel(self):
        self.assertIn("currentFacet === 'rotas'", self.html)
        self.assertIn("function atualizarPainelRota()", self.html)
        self.assertIn("data-rotas", self.html)


if __name__ == "__main__":
    unittest.main()
