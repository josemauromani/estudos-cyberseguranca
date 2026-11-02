#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_gestao_crise.py
Testes automatizados para o Estudo 43: Gestao-de-Crise-e-Comunicacao

Os prazos seguem a Resolução CD/ANPD nº 15/2024 (arts. 6º, 9º e 10), conferida
no texto oficial: 3 dias úteis para ANPD e titulares, complementação em 20 dias
úteis, declaração em 3 dias úteis após o prazo dos titulares, prazos em dobro
para agentes de pequeno porte e registro por no mínimo 5 anos.
"""

import json
import re
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402

INCISOS = {"I", "II", "III", "IV", "V", "VI", "VII"}


def somar_dias_uteis(inicio, n, feriados):
    """Exclui o dia de início, pula sábados, domingos e feriados nacionais."""
    d = inicio
    while n > 0:
        d += timedelta(days=1)
        if d.weekday() < 5 and d.isoformat() not in feriados:
            n -= 1
    return d


def prazos(d, pequeno_porte, feriados=None):
    feriados = set(d["feriados"] if feriados is None else feriados)
    r = d["regras"]
    fator = 2 if pequeno_porte else 1
    conhecimento = date.fromisoformat(d["conhecimento"][:10])
    anpd = somar_dias_uteis(conhecimento, r["anpd_dias"] * fator, feriados)
    titulares = somar_dias_uteis(conhecimento, r["titulares_dias"] * fator, feriados)
    return {
        "anpd": anpd.isoformat(),
        "titulares": titulares.isoformat(),
        "declaracao": somar_dias_uteis(titulares, r["declaracao_dias"], feriados).isoformat(),
        "complementacao": somar_dias_uteis(anpd, r["complementacao_dias"] * fator, feriados).isoformat(),
        "registro": conhecimento.replace(year=conhecimento.year + r["registro_anos"]).isoformat(),
    }


class TestGestaoCrise(unittest.TestCase):
    """Valida a estrutura, o conteúdo, os prazos, as notificações e a compilação do estudo Gestao-de-Crise-e-Comunicacao."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "gestao_de_crise_e_comunicacao_body.html"
        self.compiled_path = self.root / "Gestao-de-Crise-e-Comunicacao" / "treinamento-gestao-de-crise-e-comunicacao.html"
        self.portal_path = self.root / "index.html"

    def _dados(self):
        body = self.body_path.read_text(encoding="utf-8")
        m = re.search(r'<script type="application/json" id="crise-dados">(.*?)</script>', body, re.S)
        self.assertIsNotNone(m, "Bloco JSON #crise-dados ausente no body")
        return json.loads(m.group(1))

    # ----------------------------------------------------------------- arquivos
    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        termos = [
            "incidente", "crise", "comitê de crise", "RACI", "porta-voz", "sala de guerra", "registro de decisões",
            "Resolução CD/ANPD nº 15/2024", "três dias úteis", "vinte dias úteis", "pequeno porte", "em dobro",
            "três meses", "cinco anos", "art. 5º", "art. 9º", "encarregado", "linguagem simples",
            "Resolução CMN nº 4.893/2021", "declaração inicial",
        ]
        for termo in termos:
            self.assertIn(termo, content, f"Termo obrigatório ausente: {termo}")

    # ------------------------------------------------------------------ prazos
    def test_regras_conferem_com_a_resolucao(self):
        r = self._dados()["regras"]
        self.assertEqual((r["anpd_dias"], r["titulares_dias"], r["complementacao_dias"], r["declaracao_dias"], r["registro_anos"]),
                         (3, 3, 20, 3, 5))

    def test_prazos_esperados_batem_com_a_contagem(self):
        d = self._dados()
        self.assertEqual(d["conhecimento"], "2025-11-08T02:00")
        self.assertEqual(prazos(d, False), d["prazos_esperados"]["normal"])
        self.assertEqual(prazos(d, True), d["prazos_esperados"]["pequeno_porte"])

    def test_feriados_mudam_o_resultado(self):
        d = self._dados()
        self.assertIn("2025-11-20", d["feriados"], "20/11 é feriado nacional desde a Lei 14.759/2023")
        sem_20 = [f for f in d["feriados"] if f != "2025-11-20"]
        self.assertNotEqual(prazos(d, False, sem_20)["complementacao"], d["prazos_esperados"]["normal"]["complementacao"])
        for f in d["feriados"]:
            date.fromisoformat(f)

    # ------------------------------------------------------------ notificações
    def test_destinatarios(self):
        d = self._dados()
        opcoes = set(d["opcoes_prazo"])
        self.assertEqual(len(d["destinatarios"]), 9)
        ids = {x["id"] for x in d["destinatarios"]}
        self.assertTrue({"anpd", "titulares", "adquirente", "banco_central"} <= ids)
        for x in d["destinatarios"]:
            with self.subTest(destinatario=x["id"]):
                self.assertIn(x["correto"], ("notificar", "nao_se_aplica"))
                self.assertTrue(x["nome"].strip() and x["explicacao"].strip())
                if x["correto"] == "notificar":
                    self.assertIn(x["prazo_correto"], opcoes)
                else:
                    self.assertIsNone(x["prazo_correto"])
        por_id = {x["id"]: x for x in d["destinatarios"]}
        self.assertEqual(por_id["anpd"]["prazo_correto"], "3du")
        self.assertEqual(por_id["titulares"]["prazo_correto"], "3du")
        self.assertEqual(por_id["adquirente"]["correto"], "nao_se_aplica", "nenhum dado de cartão foi afetado")
        self.assertEqual(por_id["banco_central"]["correto"], "nao_se_aplica", "empresa não financeira")

    def test_itens_da_mensagem_cobrem_o_art_9(self):
        d = self._dados()
        itens = d["itens_mensagem"]
        obrig = {i["inciso"] for i in itens if i["tipo"] == "obrigatorio"}
        cond = {i["inciso"] for i in itens if i["tipo"] == "condicional"}
        self.assertEqual(obrig | cond, INCISOS)
        self.assertEqual(cond, {"IV"}, "motivos da demora só se a comunicação atrasar")
        self.assertTrue(any(i["tipo"] == "boa_pratica" for i in itens))
        self.assertGreaterEqual(sum(1 for i in itens if i["tipo"] == "distrator"), 4)
        for i in itens:
            with self.subTest(item=i["id"]):
                self.assertTrue(i["texto"].strip() and i["explicacao"].strip())

    # ---------------------------------------------------------------- compilado
    def test_simulador_estrutura(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        for marcador in ("crise-lab", 'id="crise-dados"', "crise-prazos", "crise-destinatarios", "crise-mensagem",
                         "crise-previa", "crise-resultado-notif", "crise-resultado-msg", "calcularPrazosCrise",
                         "conferirNotificacoesCrise", "conferirMensagemCrise", "restaurarCrise"):
            self.assertIn(marcador, content, marcador)
        ini = content.index("var CRISE = JSON.parse")
        motor = content[ini:content.index("</script>", ini)]
        self.assertNotIn("innerHTML", motor)

    def test_componentes_pedagogicos(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        self.assertIn('class="callout', content)
        self.assertIn('class="diagram-svg-wrap', content)
        self.assertNotIn('<pre class="mermaid"', content)
        self.assertEqual(content.count('class="checklist-item"'), 7)
        self.assertGreaterEqual(content.count('class="quiz-item"'), 6)
        self.assertIn('class="facts-grid', content)
        self.assertIn('initChecklist("gestao-crise")', content)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn("Gestao-de-Crise-e-Comunicacao/treinamento-gestao-de-crise-e-comunicacao.html", content)
        self.assertIn('data-slug="Gestao-de-Crise-e-Comunicacao"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)


if __name__ == "__main__":
    unittest.main()
