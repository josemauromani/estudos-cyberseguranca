#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testes da visão "Rotas sugeridas" do portal: dados das rotas, coerência com o CURRICULO e HTML gerado."""

import re
import sys
import tempfile
import unittest
from pathlib import Path

GERADORES_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GERADORES_DIR))

from index_dados import ESTUDOS_DADOS, ROTAS_PERFIL  # noqa: E402

from build_index import gerar_index_html, render_painel_rotas  # noqa: E402

IDS_ESPERADOS = ["blue_soc", "red_team", "devsecops_cloud", "grc", "ciso", "appsec", "pericia", "analista_si"]

CISO_MODULOS = [
    "Fundamentos-Ciber",
    "Arquitetura-Zero-Trust",
    "Autenticacao-e-IAM",
    "PAM-e-Acessos-Privilegiados",
    "Gestao-de-Vulnerabilidades",
    "Gestao-de-Riscos-TI",
    "ISO-27001-e-27002",
    "Auditoria-de-TI",
    "Gestao-de-Riscos-de-Terceiros",
    "Continuidade-e-Disaster-Recovery",
    "Gestao-de-Crise-e-Comunicacao",
    "Exercicios-Tabletop",
    "Lideranca-e-Programa-de-Seguranca",
    "Estruturacao-da-Area-de-Seguranca",
]

APPSEC_MODULOS = [
    "Fundamentos-Ciber",
    "Fundamentos-de-Computacao-e-SO",
    "Criptografia-Pratica",
    "Autenticacao-e-IAM",
    "Python-para-Seguranca",
    "OWASP-Top-10-Web",
    "Seguranca-em-APIs",
    "Seguranca-em-Mobile-e-MDM",
    "Seguranca-em-Nuvem",
    "Identidade-Hibrida-e-Nuvem",
    "DevSecOps-e-CI-CD",
    "Seguranca-de-Containers",
    "Seguranca-em-Kubernetes",
    "Infraestrutura-como-Codigo-Segura",
    "Deteccao-e-Resposta-em-Nuvem",
]


def numero(slug):
    return list(ESTUDOS_DADOS).index(slug) + 1


def visao(html, nome):
    """Trecho do HTML da visão <section class="view" data-view="nome">."""
    ini = html.index(f'<section class="view" data-view="{nome}"')
    fim = html.find('<section class="view" ', ini + 1)
    return html[ini:fim if fim != -1 else html.index("</main>")]


def sequencias_do_curriculo():
    """As sequências do §5 do CURRICULO.md, na ordem em que aparecem, como listas de números."""
    txt = (GERADORES_DIR / "CURRICULO.md").read_text(encoding="utf-8")
    secao = txt.split("## 5. Rotas de Aprendizagem por Perfil Profissional", 1)[1]
    return [[int(n) for n in seq.split(" -> ")] for seq in re.findall(r"`(\d\d(?: -> \d\d)+)`", secao)]


class TestDadosDasRotas(unittest.TestCase):
    def test_oito_rotas_com_ids_e_campos(self):
        self.assertEqual([r["id"] for r in ROTAS_PERFIL], IDS_ESPERADOS)
        for r in ROTAS_PERFIL:
            with self.subTest(rota=r["id"]):
                for campo in ("nome", "icone", "descricao"):
                    self.assertTrue(r[campo].strip(), campo)
                self.assertGreaterEqual(len(r["modulos"]), 10)
                self.assertEqual(len(r["modulos"]), len(set(r["modulos"])), "módulo repetido na rota")
                for slug in r["modulos"]:
                    self.assertIn(slug, ESTUDOS_DADOS)

    def test_rota_ciso_modulos(self):
        rotas = {r["id"]: r for r in ROTAS_PERFIL}
        self.assertEqual(rotas["ciso"]["modulos"], CISO_MODULOS)
        self.assertEqual(rotas["ciso"]["nome"], "CISO / Liderança de Segurança")
        self.assertEqual(rotas["ciso"]["icone"], "👔")

    def test_rota_appsec_modulos(self):
        rotas = {r["id"]: r for r in ROTAS_PERFIL}
        self.assertEqual(rotas["appsec"]["modulos"], APPSEC_MODULOS)
        self.assertEqual(rotas["appsec"]["nome"], "AppSec / Segurança de Aplicações")
        self.assertEqual(rotas["appsec"]["icone"], "🧩")

    def test_descricao_appsec_reflete_ssdlc_sem_prometer_samm_completo(self):
        rotas = {r["id"]: r for r in ROTAS_PERFIL}
        desc = rotas["appsec"]["descricao"].casefold()
        self.assertTrue(
            "ssdlc" in desc or "ciclo de desenvolvimento seguro" in desc,
            "descrição appsec deve citar SSDLC ou ciclo de desenvolvimento seguro",
        )
        self.assertNotIn("samm completo", desc)
        self.assertTrue(
            "sbom" in desc or "slsa" in desc or "secret" in desc,
            "descrição appsec deve citar SBOM/SLSA ou secrets",
        )
        self.assertTrue(
            "mobile" in desc or "masvs" in desc or "mdm" in desc,
            "descrição appsec deve citar mobile/MASVS/MDM",
        )
        self.assertNotIn("pentest mobile completo", desc)

    def test_rota_analista_inclui_mobile_apos_edr(self):
        rotas = {r["id"]: r for r in ROTAS_PERFIL}
        m = rotas["analista_si"]["modulos"]
        self.assertIn("Seguranca-em-Mobile-e-MDM", m)
        self.assertEqual(
            m.index("Seguranca-em-Mobile-e-MDM"),
            m.index("Seguranca-em-Endpoints-EDR") + 1,
        )
        desc = rotas["analista_si"]["descricao"].casefold()
        self.assertTrue("mdm" in desc or "byod" in desc or "mobile" in desc)

    def test_rotas_do_modulo_61(self):
        slug = "Fundamentos-de-Computacao-e-SO"
        rotas = {r["id"]: r["modulos"] for r in ROTAS_PERFIL}
        for rid in ("blue_soc", "red_team", "devsecops_cloud", "pericia", "analista_si"):
            with self.subTest(rota=rid):
                m = rotas[rid]
                self.assertEqual(m.index(slug), m.index("Fundamentos-Ciber") + 1)
        self.assertNotIn(slug, rotas["grc"])

    def test_rotas_batem_com_o_curriculo(self):
        """O §5 do CURRICULO.md documenta as mesmas sequências que o portal mostra."""
        self.assertEqual(sequencias_do_curriculo(), [[numero(s) for s in r["modulos"]] for r in ROTAS_PERFIL])

    def test_rota_blue_team_comeca_e_termina_como_documentado(self):
        r = ROTAS_PERFIL[0]
        self.assertEqual(numero(r["modulos"][0]), 1)
        self.assertEqual(numero(r["modulos"][-1]), 42)
        self.assertEqual(len(r["modulos"]), 18)

    def test_rota_blue_team_poe_threat_intel_antes_da_engenharia_de_deteccao(self):
        """O 17 é pré-requisito do 46: a rota não pode pedir a detecção antes da inteligência."""
        m = [numero(s) for s in ROTAS_PERFIL[0]["modulos"]]
        self.assertEqual(m[m.index(16):m.index(47) + 1], [16, 17, 46, 47])


class TestHtmlDasRotas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as tmp:
            cls.html = gerar_index_html(output_path=Path(tmp) / "index.html").read_text(encoding="utf-8")

    def test_visao_no_menu_com_uma_rota_por_perfil(self):
        self.assertRegex(self.html, r'<a href="#v-rotas" data-view="rotas">[^<]*Rotas sugeridas')
        rotas = visao(self.html, "rotas")
        self.assertEqual(re.findall(r'<div class="rota-sugerida" data-rota="([^"]+)"', rotas), IDS_ESPERADOS)

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

    def test_painel_esta_na_visao_rotas(self):
        self.assertIn('<section class="rota-sugerida-section" id="secao-rota-sugerida"', visao(self.html, "rotas"))
        self.assertIn('<section class="view" data-view="rotas" hidden>', self.html)


if __name__ == "__main__":
    unittest.main()
