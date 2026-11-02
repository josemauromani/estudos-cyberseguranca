#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_continuidade.py
Testes automatizados para o Estudo 28: Continuidade-e-Disaster-Recovery
"""

import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402

CENARIOS = ["storage", "incendio", "ransomware", "exclusao"]


def custo(d, e):
    c = d["custos"]
    return (c["frequencia"][str(e["frequencia_h"])] + c["replicacao"][e["replicacao"]] + c["site"][e["site"]]
            + sum(c["copias"][x] for x in e["copias"]) + c["retencao"][str(e["retencao_dias"])] + (c["teste"] if e["teste"] else 0))


def regra_32110(d, e):
    copias = [d["tipos_copia"][x] for x in e["copias"]]
    return {"tres_copias": 1 + len(copias) >= 3,
            "duas_midias": len({"disco"} | {c["midia"] for c in copias}) >= 2,
            "uma_fora": any(c["local"] != "mesmo_datacenter" for c in copias),
            "uma_imutavel_offline": any(c["imutavel"] or c["offline"] for c in copias),
            "zero_erros": bool(e["teste"])}


def recuperar(d, s, e, cenario):
    """Melhor forma de recuperar o sistema s com a estratégia e no cenário. Espelho do JavaScript."""
    opcoes = []
    site = d["sites"][e["site"]]
    if e["replicacao"] != "nenhuma" and e["site"] != "nenhum" and cenario in ("storage", "incendio"):
        opcoes.append({"metodo": "failover", "parada": site["ativacao_h"], "perda": d["perda_replicacao"][e["replicacao"]], "copia": None})
    if cenario == "exclusao" and e["retencao_dias"] < d["exclusao_descoberta_dias"]:
        sobreviventes = []
    else:
        sobreviventes = []
        for x in e["copias"]:
            t = d["tipos_copia"][x]
            if cenario == "incendio" and t["local"] == "mesmo_datacenter":
                continue
            if cenario == "ransomware" and not (t["imutavel"] or t["offline"]):
                continue
            sobreviventes.append(x)
    if sobreviventes:
        infra = (site["ativacao_h"] if e["site"] != "nenhum" else d["nova_infra_h"]) if cenario == "incendio" else 0
        melhor = min(sobreviventes, key=lambda x: (s["tamanho_gb"] / d["tipos_copia"][x]["taxa_gb_h"], x))
        tempo = infra + s["tamanho_gb"] / d["tipos_copia"][melhor]["taxa_gb_h"]
        if not e["teste"]:
            tempo *= 1.5
        opcoes.append({"metodo": "restauracao", "parada": round(tempo, 2), "perda": e["frequencia_h"], "copia": melhor})
    if not opcoes:
        return {"metodo": "irrecuperavel", "parada": None, "perda": None, "copia": None}
    return min(opcoes, key=lambda o: (o["parada"], o["perda"], o["metodo"]))


def avaliar(d, alvos, estrategias):
    res = {}
    for s in d["sistemas"]:
        a, e = alvos[s["id"]], estrategias[s["id"]]
        linhas = {}
        for c in CENARIOS:
            r = recuperar(d, s, e, c)
            ok = r["metodo"] != "irrecuperavel" and r["parada"] <= a["rto"] and r["perda"] <= a["rpo"]
            linhas[c] = dict(r, ok=ok)
        res[s["id"]] = {"cenarios": linhas, "custo": custo(d, e), "regra": regra_32110(d, e),
                        "bia_ok": a["rto"] <= s["mtpd_h"] and a["rpo"] <= s["perda_tolerada_h"]}
    return res


class TestContinuidade(unittest.TestCase):
    """Valida a estrutura, o conteúdo, a BIA, as estratégias, os cenários e a compilação do estudo 28."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "continuidade_e_disaster_recovery_body.html"
        self.compiled_path = self.root / "Continuidade-e-Disaster-Recovery" / "treinamento-continuidade-e-disaster-recovery.html"
        self.portal_path = self.root / "index.html"

    def _dados(self):
        body = self.body_path.read_text(encoding="utf-8")
        m = re.search(r'<script type="application/json" id="dr-dados">(.*?)</script>', body, re.S)
        self.assertIsNotNone(m, "Bloco JSON #dr-dados ausente no body")
        return json.loads(m.group(1))

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        termos = ["BCP", "DRP", "BIA", "MTPD", "RTO", "RPO", "MBCO", "ISO 22301", "site quente", "site morno", "site frio",
                  "replicação síncrona", "replicação assíncrona", "3-2-1", "3-2-1-1-0", "imutável", "retenção",
                  "teste de restauração", "Estudo 44", "Estudo 45", "Estudo 25"]
        for termo in termos:
            self.assertIn(termo, content, f"Termo obrigatório ausente: {termo}")

    def test_referencia_viavel_e_dentro_do_orcamento(self):
        d = self._dados()
        res = avaliar(d, d["alvos_referencia"], d["estrategia_referencia"])
        total = 0
        for sid, r in res.items():
            with self.subTest(sistema=sid):
                self.assertTrue(r["bia_ok"])
                self.assertTrue(all(x["ok"] for x in r["cenarios"].values()), r["cenarios"])
                self.assertTrue(all(r["regra"].values()), r["regra"])
            total += r["custo"]
        self.assertLessEqual(total, d["orcamento_mensal"])
        self.assertEqual(total, d["custo_referencia"])

    def test_orcamento_tem_folga_controlada(self):
        d = self._dados()
        self.assertGreater(d["orcamento_mensal"], d["custo_referencia"])
        self.assertLessEqual(d["orcamento_mensal"], round(d["custo_referencia"] * 1.25))

    def test_estado_inicial_falha_como_esperado(self):
        d = self._dados()
        res = avaliar(d, d["alvos_referencia"], d["estrategia_inicial"])
        for s in d["sistemas"]:
            r = res[s["id"]]["cenarios"]
            self.assertEqual(r["incendio"]["metodo"], "irrecuperavel", "cópia só no mesmo datacenter")
            self.assertEqual(r["ransomware"]["metodo"], "irrecuperavel", "nenhuma cópia imutável ou offline")
            self.assertEqual(r["exclusao"]["metodo"], "irrecuperavel", "retenção menor que o tempo de descoberta")

    def test_licoes(self):
        d = self._dados()
        s = d["sistemas"][0]
        e = dict(d["estrategia_referencia"][s["id"]])
        self.assertEqual(recuperar(d, s, dict(e, copias=[c for c in e["copias"] if not (d["tipos_copia"][c]["imutavel"] or d["tipos_copia"][c]["offline"])]),
                                   "ransomware")["metodo"], "irrecuperavel", "réplica não salva do ransomware")
        sem_teste = recuperar(d, s, dict(e, teste=False), "ransomware")["parada"]
        com_teste = recuperar(d, s, e, "ransomware")["parada"]
        self.assertAlmostEqual(sem_teste, round(com_teste * 1.5, 2), places=1)
        for x in d["sistemas"]:
            self.assertLess(d["alvos_referencia"][x["id"]]["rto"], x["mtpd_h"] + 0.001)

    def test_simulador_estrutura(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        for marcador in ("dr-lab", 'id="dr-dados"', "dr-missoes", "dr-bia", "dr-estrategias", "dr-resultado",
                         "dr-orcamento", "avaliarContinuidade", "simularDesastresDr", "restaurarDr"):
            self.assertIn(marcador, content, marcador)
        ini = content.index("var DR = JSON.parse")
        motor = content[ini:content.index("</script>", ini)]
        self.assertNotIn("innerHTML", motor)
        self.assertNotIn("eval(", motor)

    def test_componentes_pedagogicos(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        self.assertIn('class="callout', content)
        self.assertIn('class="terminal-box', content)
        self.assertIn('class="diagram-svg-wrap', content)
        self.assertNotIn('<pre class="mermaid"', content)
        self.assertEqual(content.count('class="checklist-item"'), 7)
        self.assertGreaterEqual(content.count('class="quiz-item"'), 6)
        self.assertIn('class="facts-grid', content)
        self.assertIn('initChecklist("continuidade")', content)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn("Continuidade-e-Disaster-Recovery/treinamento-continuidade-e-disaster-recovery.html", content)
        self.assertIn('data-slug="Continuidade-e-Disaster-Recovery"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)


if __name__ == "__main__":
    unittest.main()
