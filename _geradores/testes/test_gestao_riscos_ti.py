#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_gestao_riscos_ti.py
Testes automatizados para o Estudo 25: Gestao-de-Riscos-TI
"""

import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402

TRATAMENTOS_CONTROLE = {"mitigar", "transferir", "evitar"}


def nivel(escala, valor):
    """Nível (1 a 5) cujo limite inferior é o maior que não passa de `valor`."""
    n = 0
    for item in escala:
        if valor >= item["min"]:
            n = item["nivel"]
    return n


def faixa(faixas, pontuacao):
    for f in faixas:
        if f["min"] <= pontuacao <= f["max"]:
            return f["nome"]
    return None


class TestGestaoRiscosTI(unittest.TestCase):
    """Valida a estrutura, o conteúdo, os cálculos e a compilação do estudo Gestao-de-Riscos-TI."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "gestao_de_riscos_ti_body.html"
        self.compiled_path = self.root / "Gestao-de-Riscos-TI" / "treinamento-gestao-de-riscos-ti.html"
        self.portal_path = self.root / "index.html"

    # ------------------------------------------------------------------ apoio
    def _dados(self):
        body = self.body_path.read_text(encoding="utf-8")
        m = re.search(r'<script type="application/json" id="risco-dados">(.*?)</script>', body, re.S)
        self.assertIsNotNone(m, "Bloco JSON #risco-dados ausente no body")
        return json.loads(m.group(1))

    def _pontuacao(self, d, sle, aro):
        return nivel(d["escala_probabilidade"], aro) * nivel(d["escala_impacto"], sle)

    @staticmethod
    def _ale(av, ef, aro):
        return av * ef * aro

    def _avaliar_controles(self, d, c):
        """Para cada controle: ALE residual, benefício líquido anual e ROSI."""
        ale_antes = self._ale(c["av"], c["ef"], c["aro"])
        saida = []
        for ctl in c["controles"]:
            ale_depois = self._ale(c["av"], ctl["ef"], ctl["aro"])
            beneficio = ale_antes - ale_depois - ctl["custo_anual"]
            saida.append({
                "id": ctl["id"],
                "tratamento": ctl["tratamento"],
                "custo": ctl["custo_anual"],
                "ale_depois": ale_depois,
                "beneficio": beneficio,
                "rosi": beneficio / ctl["custo_anual"],
                "pontuacao": self._pontuacao(d, c["av"] * ctl["ef"], ctl["aro"]),
            })
        return ale_antes, saida

    def _recomendado(self, d, c):
        _, avaliados = self._avaliar_controles(d, c)
        melhor = max(avaliados, key=lambda a: a["beneficio"])
        return melhor if melhor["beneficio"] > 0 else None

    # ----------------------------------------------------------------- arquivos
    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        termos = [
            "ISO 31000:2018", "ISO/IEC 27005:2022", "NIST SP 800-30", "NIST IR 8286", "GV.RM",
            "Valor do Ativo", "Fator de Exposição", "SLE", "ARO", "ALE", "ROSI",
            "risco inerente", "risco residual", "apetite", "tolerância", "registro de riscos",
            "Mitigar", "Aceitar", "Transferir", "Evitar", "FAIR", "6.1.3",
        ]
        for termo in termos:
            self.assertIn(termo, content, f"Termo obrigatório ausente: {termo}")

    # -------------------------------------------------------------------- dados
    def test_escalas_e_faixas(self):
        d = self._dados()
        for nome in ("escala_probabilidade", "escala_impacto"):
            with self.subTest(escala=nome):
                escala = d[nome]
                self.assertEqual([e["nivel"] for e in escala], [1, 2, 3, 4, 5])
                self.assertEqual(escala[0]["min"], 0)
                mins = [e["min"] for e in escala]
                self.assertEqual(mins, sorted(set(mins)), "limites devem ser crescentes")
                for e in escala:
                    self.assertTrue(e["rotulo"].strip())
        cobertos = []
        for f in d["faixas"]:
            cobertos.extend(range(f["min"], f["max"] + 1))
        self.assertEqual(cobertos, list(range(1, 26)), "faixas devem cobrir 1..25 sem lacunas")
        self.assertEqual([f["nome"] for f in d["faixas"]], ["Baixo", "Médio", "Alto", "Crítico"])
        self.assertIsNotNone(faixa(d["faixas"], d["apetite"]))

    def test_cenarios_e_controles_validos(self):
        d = self._dados()
        self.assertTrue(d["empresa"].strip())
        self.assertEqual(len(d["cenarios"]), 6)
        ids_cenario = [c["id"] for c in d["cenarios"]]
        self.assertEqual(len(ids_cenario), len(set(ids_cenario)))
        ids_controle = []
        for c in d["cenarios"]:
            with self.subTest(cenario=c["id"]):
                for campo in ("titulo", "ativo", "ameaca", "vulnerabilidade", "composicao_av"):
                    self.assertTrue(c[campo].strip(), campo)
                self.assertGreater(c["av"], 0)
                self.assertGreater(c["ef"], 0)
                self.assertLessEqual(c["ef"], 1)
                self.assertGreater(c["aro"], 0)
                self.assertGreaterEqual(len(c["controles"]), 2)
                for ctl in c["controles"]:
                    ids_controle.append(ctl["id"])
                    self.assertIn(ctl["tratamento"], TRATAMENTOS_CONTROLE)
                    self.assertTrue(ctl["nome"].strip())
                    self.assertGreater(ctl["custo_anual"], 0)
                    self.assertGreaterEqual(ctl["ef"], 0)
                    self.assertLessEqual(ctl["ef"], 1)
                    self.assertGreaterEqual(ctl["aro"], 0)
        self.assertEqual(len(ids_controle), len(set(ids_controle)), "ids de controle repetidos")

    def test_controles_reduzem_risco(self):
        d = self._dados()
        for c in d["cenarios"]:
            inerente = self._pontuacao(d, c["av"] * c["ef"], c["aro"])
            ale_antes, avaliados = self._avaliar_controles(d, c)
            for a in avaliados:
                with self.subTest(controle=a["id"]):
                    self.assertLess(a["ale_depois"], ale_antes)
                    self.assertLessEqual(a["pontuacao"], inerente)

    def test_recomendacao_e_maior_beneficio_liquido(self):
        d = self._dados()
        for c in d["cenarios"]:
            with self.subTest(cenario=c["id"]):
                melhor = self._recomendado(d, c)
                self.assertEqual(c["recomendado"], melhor["id"] if melhor else "aceitar")

    def test_casos_pedagogicos(self):
        d = self._dados()
        tratamentos = set()
        rosi_negativo = False
        rosi_maior_nao_recomendado = False
        criticos = 0
        for c in d["cenarios"]:
            _, avaliados = self._avaliar_controles(d, c)
            melhor = self._recomendado(d, c)
            tratamentos.add(melhor["tratamento"] if melhor else "aceitar")
            rosi_negativo = rosi_negativo or any(a["rosi"] < 0 for a in avaliados)
            maior_rosi = max(avaliados, key=lambda a: a["rosi"])
            if melhor and maior_rosi["id"] != melhor["id"]:
                rosi_maior_nao_recomendado = True
            if faixa(d["faixas"], self._pontuacao(d, c["av"] * c["ef"], c["aro"])) == "Crítico":
                criticos += 1
        self.assertEqual(tratamentos, {"mitigar", "transferir", "evitar", "aceitar"})
        self.assertTrue(rosi_negativo, "deve haver controle com ROSI negativo")
        self.assertTrue(rosi_maior_nao_recomendado, "deve haver caso em que o maior ROSI não é a melhor escolha")
        self.assertGreaterEqual(criticos, 1)

    def test_selecao_recomendada_cabe_no_orcamento_e_no_apetite(self):
        d = self._dados()
        custo_total = 0
        for c in d["cenarios"]:
            melhor = self._recomendado(d, c)
            if melhor:
                custo_total += melhor["custo"]
                residual = melhor["pontuacao"]
            else:
                residual = self._pontuacao(d, c["av"] * c["ef"], c["aro"])
            with self.subTest(cenario=c["id"]):
                self.assertLessEqual(residual, d["apetite"], "residual recomendado acima do apetite")
        self.assertLessEqual(custo_total, d["orcamento_anual"])
        caro = sum(max(ctl["custo_anual"] for ctl in c["controles"]) for c in d["cenarios"])
        self.assertGreater(caro, d["orcamento_anual"], "o orçamento deve obrigar a escolher")

    # ---------------------------------------------------------------- compilado
    def test_simulador_estrutura(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        for marcador in ("risco-lab", 'id="risco-dados"', "risco-matriz", "risco-quantitativo",
                         "risco-registro", "selecionarCenarioRisco", "escolherControleRisco",
                         "restaurarRisco"):
            self.assertIn(marcador, content, marcador)
        ini = content.index("var RISCO = JSON.parse")
        motor = content[ini:content.index("</script>", ini)]
        self.assertNotIn("innerHTML", motor)

    def test_componentes_pedagogicos(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        self.assertIn('class="callout', content)
        self.assertIn('class="terminal-box', content)
        self.assertIn('class="diagram-svg-wrap', content)
        self.assertNotIn('<pre class="mermaid"', content)
        self.assertEqual(content.count('class="checklist-item"'), 7)
        self.assertGreaterEqual(content.count('class="quiz-item"'), 5)
        self.assertIn('class="facts-grid', content)
        self.assertIn('initChecklist("gestao-riscos-ti")', content)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn("Gestao-de-Riscos-TI/treinamento-gestao-de-riscos-ti.html", content)
        self.assertIn('data-slug="Gestao-de-Riscos-TI"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)


if __name__ == "__main__":
    unittest.main()
