#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testes dos dados da rota da vaga, das certificações e da carreira Analista de SI."""

import sys
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
        self.assertEqual(sorted(siglas), sorted(["CEH", "CISM", "CISSP", "CCSP", "GSEC", "Security+"]))
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


if __name__ == "__main__":
    unittest.main()
