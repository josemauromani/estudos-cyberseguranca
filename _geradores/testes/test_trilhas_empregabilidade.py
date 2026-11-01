#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testes das Trilhas 8, 9 e 10 (módulos 34–45) e de suas ligações no portal."""

import re
import sys
import tempfile
import unittest
from pathlib import Path

GERADORES_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GERADORES_DIR))

from index_dados import CARREIRAS, ESTUDOS_DADOS, TRILHAS  # noqa: E402

from build_index import gerar_index_html  # noqa: E402

NOVOS = [
    "Linux-para-Seguranca",
    "Python-para-Seguranca",
    "PowerShell-e-Windows-Interno",
    "Laboratorio-Domestico-e-Portfolio",
    "Active-Directory-Fundamentos",
    "Ataques-e-Defesa-no-AD",
    "PAM-e-Acessos-Privilegiados",
    "Identidade-Hibrida-e-Nuvem",
    "Ransomware-Prevencao-a-Recuperacao",
    "Gestao-de-Crise-e-Comunicacao",
    "Exercicios-Tabletop",
    "Backup-Imutavel-e-Recuperacao",
]

NOMES_CARREIRAS = {c["nome"] for c in CARREIRAS.values()}


class TestCatalogoNovo(unittest.TestCase):
    def test_posicoes_34_a_45(self):
        self.assertEqual(list(ESTUDOS_DADOS)[33:], NOVOS)
        self.assertEqual([ESTUDOS_DADOS[s]["trilha"] for s in NOVOS], [8] * 4 + [9] * 4 + [10] * 4)

    def test_trilhas_novas(self):
        esperado = {
            8: ("Ferramentas & Automação do Analista", "#475569", "slate"),
            9: ("Identidade Corporativa & Active Directory", "#4F46E5", "indigo"),
            10: ("Resiliência, Crise & Ransomware", "#C2410C", "orange"),
        }
        for tid, (nome, cor, cor_nome) in esperado.items():
            with self.subTest(trilha=tid):
                info = TRILHAS[tid]
                self.assertEqual((info["id"], info["nome"], info["cor"], info["cor_nome"]), (tid, nome, cor, cor_nome))

    def test_modulo_37_tem_todas_as_carreiras(self):
        self.assertEqual(set(ESTUDOS_DADOS["Laboratorio-Domestico-e-Portfolio"]["carreiras"]), NOMES_CARREIRAS)

    def test_carreiras_dos_modulos_existem(self):
        for slug, dados in ESTUDOS_DADOS.items():
            with self.subTest(slug=slug):
                self.assertLessEqual(set(dados["carreiras"]), NOMES_CARREIRAS)

    def test_trilha_10_nao_colide_com_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            html = gerar_index_html(output_path=Path(tmp) / "index.html").read_text(encoding="utf-8")
        for slug in NOVOS:
            m = re.search(rf'id="estudo-{re.escape(slug)}"\s+data-slug="[^"]*"\s+data-trilha="(\d+)"', html)
            self.assertIsNotNone(m, slug)
            self.assertNotEqual(m.group(1), "1", slug)
            if slug in NOVOS[8:]:
                self.assertEqual(m.group(1), "10", slug)
        self.assertIn('data-value="10"', html)


if __name__ == "__main__":
    unittest.main()
