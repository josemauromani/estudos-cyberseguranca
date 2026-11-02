#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testes das Trilhas 11, 12 e 13 (módulos 46–57) e de suas ligações no portal."""

import re
import sys
import tempfile
import unittest
from pathlib import Path

GERADORES_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GERADORES_DIR))

from index_dados import (  # noqa: E402
    CARREIRAS,
    CERTIFICACOES,
    ESTUDOS_DADOS,
    NECESSIDADES,
    ROTA_VAGA,
    ROTULO_ANALISTA_SI,
    TRILHAS,
)

from build_index import gerar_index_html, render_rota_vaga  # noqa: E402

NOVOS = [
    "Engenharia-de-Deteccao",
    "Threat-Hunting",
    "Monitoramento-de-Rede-NSM",
    "SOAR-e-Automacao-de-Resposta",
    "Seguranca-de-Containers",
    "Seguranca-em-Kubernetes",
    "Infraestrutura-como-Codigo-Segura",
    "Deteccao-e-Resposta-em-Nuvem",
    "Regulacao-Setor-Financeiro",
    "Fraude-em-Pagamentos-e-Pix",
    "Legislacao-e-Crimes-Ciberneticos",
    "Gestao-de-Riscos-de-Terceiros",
]

NIST_NOVOS = [
    "Detect",
    "Detect",
    "Detect",
    "Respond",
    "Protect",
    "Protect",
    "Protect",
    "Detect / Respond",
    "Govern",
    "Detect / Protect",
    "Govern",
    "Govern",
]

NOMES_CARREIRAS = {c["nome"] for c in CARREIRAS.values()}

# Perfis aceitos em cada rota da spec §3.2 -> módulos novos daquela rota
ROTAS_NOVAS = {
    ("Blue Team & Defesa", "Operações SOC & Resposta"): [
        "Monitoramento-de-Rede-NSM", "Engenharia-de-Deteccao", "Threat-Hunting", "SOAR-e-Automacao-de-Resposta",
    ],
    ("Red Team & Pentest",): ["Seguranca-em-Kubernetes"],
    ("AppSec & DevSecOps",): [
        "Seguranca-de-Containers", "Seguranca-em-Kubernetes", "Infraestrutura-como-Codigo-Segura", "Deteccao-e-Resposta-em-Nuvem",
    ],
    ("GRC & Auditoria",): [
        "Gestao-de-Riscos-de-Terceiros", "Legislacao-e-Crimes-Ciberneticos", "Regulacao-Setor-Financeiro", "Fraude-em-Pagamentos-e-Pix",
    ],
    ("Perícia Forense & Malware",): [
        "Monitoramento-de-Rede-NSM", "Threat-Hunting", "Deteccao-e-Resposta-em-Nuvem", "Legislacao-e-Crimes-Ciberneticos",
    ],
    (ROTULO_ANALISTA_SI,): ["Regulacao-Setor-Financeiro", "Gestao-de-Riscos-de-Terceiros", "SOAR-e-Automacao-de-Resposta"],
}


class TestCatalogoEspecializacao(unittest.TestCase):
    def test_posicoes_46_a_57(self):
        self.assertEqual(list(ESTUDOS_DADOS)[45:], NOVOS)
        self.assertEqual([ESTUDOS_DADOS[s]["trilha"] for s in NOVOS], [11] * 4 + [12] * 4 + [13] * 4)
        self.assertEqual([ESTUDOS_DADOS[s]["nist"] for s in NOVOS], NIST_NOVOS)

    def test_trilhas_novas(self):
        esperado = {
            11: ("Detecção Avançada & Threat Hunting", "#A21CAF", "fuchsia"),
            12: ("Nuvem, Containers & Kubernetes", "#0F766E", "teal"),
            13: ("Setor Regulado no Brasil", "#4D7C0F", "lime"),
        }
        for tid, (nome, cor, cor_nome) in esperado.items():
            with self.subTest(trilha=tid):
                t = TRILHAS[tid]
                self.assertEqual((t["id"], t["nome"], t["cor"], t["cor_nome"]), (tid, nome, cor, cor_nome))

    def test_carreiras_dos_modulos_novos_existem(self):
        for slug in NOVOS:
            for rotulo in ESTUDOS_DADOS[slug]["carreiras"]:
                with self.subTest(slug=slug, rotulo=rotulo):
                    self.assertIn(rotulo, NOMES_CARREIRAS)

    def test_modulos_novos_tem_carreira_das_rotas(self):
        for perfis, slugs in ROTAS_NOVAS.items():
            for slug in slugs:
                with self.subTest(perfis=perfis, slug=slug):
                    self.assertTrue(set(perfis) & set(ESTUDOS_DADOS[slug]["carreiras"]))

    def test_trilhas_11_a_13_nao_colidem_com_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            html = gerar_index_html(output_path=Path(tmp) / "index.html").read_text(encoding="utf-8")
        for slug in NOVOS:
            with self.subTest(slug=slug):
                m = re.search(rf'id="estudo-{re.escape(slug)}"\s+data-slug="[^"]*"\s+data-trilha="(\d+)"', html)
                self.assertIsNotNone(m)
                self.assertEqual(m.group(1), str(ESTUDOS_DADOS[slug]["trilha"]))
                self.assertNotEqual(m.group(1), "1")
        for valor in ("11", "12", "13"):
            self.assertIn(f'data-value="{valor}"', html)


if __name__ == "__main__":
    unittest.main()
