#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_tabletop.py
Testes automatizados para o Estudo 44: Exercicios-Tabletop
"""

import datetime
import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402

PRIORIDADES = ["alta", "media", "baixa"]


def mmss(s):
    return f"{s // 60:02d}:{s % 60:02d}"


def br(iso):
    a, m, d = iso.split("-")
    return f"{d}/{m}/{a}"


def status(pct):
    return "Atingido" if pct >= 80 else "Parcial" if pct >= 50 else "Não atingido"


def gerar_relatorio(d, estado):
    """Espelho do gerador de relatório pós-ação em JavaScript."""
    c = next(x for x in d["cenarios"] if x["id"] == estado["cenario"])
    injects = c["injects"] + estado.get("extras", [])
    resp = estado["respostas"]
    total = sum(resp.get(i["id"], {}).get("segundos", 0) for i in injects)
    L = [f"# Relatório pós-ação — {c['nome']}", "",
         f"Data do exercício: {br(estado['data'])} · Tipo: tabletop (discussão, NIST SP 800-84) · Duração registrada: {mmss(total)}", "",
         "## Objetivos e resultado", ""]
    for o in c["objetivos"]:
        pts = [p for i in injects for p in i["pontos"] if p["objetivo"] == o["id"]]
        cob = [p for i in injects for p in i["pontos"] if p["objetivo"] == o["id"] and p["id"] in resp.get(i["id"], {}).get("pontos", [])]
        pct = len(cob) * 100 // len(pts) if pts else 0
        L.append(f"- {o['id']} {o['texto']}: {len(cob)} de {len(pts)} pontos ({pct}%) — {status(pct)}")
    L += ["", "## Linha do tempo", ""]
    lacunas = []
    for ordem, i in enumerate(injects):
        r = resp.get(i["id"], {})
        cob = [p for p in i["pontos"] if p["id"] in r.get("pontos", [])]
        fal = [p for p in i["pontos"] if p["id"] not in r.get("pontos", [])]
        L += [f"### {i['momento']} — {i['titulo']}",
              f"Situação: {i['texto']}",
              f"Resposta da equipe: {r.get('texto', '').strip() or '(sem registro)'}",
              f"Tempo de discussão: {mmss(r.get('segundos', 0))}",
              "Pontos cobertos: " + ("; ".join(p["texto"] for p in cob) or "nenhum"),
              "Lacunas: " + ("; ".join(p["texto"] for p in fal) or "nenhuma"), ""]
        lacunas += [(PRIORIDADES.index(p["prioridade"]), ordem, p) for p in fal]
    L += ["## Plano de melhorias", ""]
    if not lacunas:
        L.append("Nenhuma lacuna registrada.")
    else:
        L += ["| Nº | Melhoria | Objetivo | Prioridade | Responsável | Prazo |", "|---|---|---|---|---|---|"]
        base = datetime.date.fromisoformat(estado["data"])
        for n, (_, _, p) in enumerate(sorted(lacunas, key=lambda x: (x[0], x[1])), 1):
            prazo = base + datetime.timedelta(days=d["prazos"][p["prioridade"]])
            L.append(f"| {n} | {p['melhoria']} | {p['objetivo']} | {d['rotulos'][p['prioridade']]} | {p['responsavel']} | {br(prazo.isoformat())} |")
    L += ["", "## Hot wash", "", estado.get("hotwash", "").strip() or "(sem registro)"]
    return "\n".join(L) + "\n"


class TestTabletop(unittest.TestCase):
    """Valida a estrutura, o conteúdo, os cenários, o relatório pós-ação e a compilação do estudo 44."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "exercicios_tabletop_body.html"
        self.compiled_path = self.root / "Exercicios-Tabletop" / "treinamento-exercicios-tabletop.html"
        self.portal_path = self.root / "index.html"

    def _dados(self):
        body = self.body_path.read_text(encoding="utf-8")
        m = re.search(r'<script type="application/json" id="tt-dados">(.*?)</script>', body, re.S)
        self.assertIsNotNone(m, "Bloco JSON #tt-dados ausente no body")
        return json.loads(m.group(1))

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        termos = [
            "NIST SP 800-84", "tabletop", "funcional", "completo", "objetivos", "cenário", "inject", "MSEL",
            "facilitador", "participantes", "observadores", "escriba", "sem culpa", "hot wash", "relatório pós-ação",
            "plano de melhorias", "responsável", "prazo", "Estudo 18", "Estudo 43",
        ]
        for termo in termos:
            self.assertIn(termo, content, f"Termo obrigatório ausente: {termo}")

    def test_cenarios(self):
        d = self._dados()
        self.assertEqual([c["id"] for c in d["cenarios"]], ["ransomware", "vazamento", "fornecedor"])
        ids = []
        for c in d["cenarios"]:
            with self.subTest(cenario=c["id"]):
                objs = {o["id"] for o in c["objetivos"]}
                self.assertEqual(len(objs), 3)
                self.assertEqual(len(c["injects"]), 4)
                por_obj = {o: 0 for o in objs}
                for i in c["injects"]:
                    self.assertEqual(len(i["pontos"]), 3)
                    self.assertTrue(i["texto"].strip() and i["pergunta"].strip() and i["momento"].strip())
                    for p in i["pontos"]:
                        ids.append(p["id"])
                        self.assertIn(p["objetivo"], objs)
                        self.assertIn(p["prioridade"], PRIORIDADES)
                        self.assertTrue(p["texto"].strip() and p["melhoria"].strip() and p["responsavel"].strip())
                        por_obj[p["objetivo"]] += 1
                self.assertTrue(all(v >= 3 for v in por_obj.values()), por_obj)
                for m in re.findall(r"Estudo (\d+)", json.dumps(c, ensure_ascii=False)):
                    self.assertRegex(self._curriculo(), rf"(?m)^#### 0?{int(m)}\. ", f"Estudo {m} não existe")
        self.assertEqual(len(ids), len(set(ids)), "ids de pontos únicos em todos os cenários")
        self.assertEqual(d["prazos"], {"alta": 30, "media": 60, "baixa": 90})

    def _curriculo(self):
        return (self.root / "_geradores" / "CURRICULO.md").read_text(encoding="utf-8")

    def test_prazo_anpd_coerente_com_estudo_43(self):
        d = self._dados()
        texto = json.dumps(d, ensure_ascii=False)
        self.assertIn("3 dias úteis", texto)
        self.assertNotIn("72 horas", texto, "o prazo da Resolução CD/ANPD 15/2024 é em dias úteis")

    def test_exemplo_de_relatorio(self):
        d = self._dados()
        ex = d["exemplo"]
        self.assertEqual(gerar_relatorio(d, ex["estado"]), ex["relatorio"])
        self.assertIn("| 1 |", ex["relatorio"])
        rel = gerar_relatorio(d, {"cenario": "ransomware", "data": "2026-11-10", "respostas": {}, "hotwash": ""})
        self.assertIn("0 de", rel)
        self.assertIn("Não atingido", rel)
        self.assertIn("10/12/2026", rel, "prioridade alta: 30 dias")
        cheio = {i["id"]: {"texto": "ok", "segundos": 60, "pontos": [p["id"] for p in i["pontos"]]} for i in d["cenarios"][0]["injects"]}
        rel = gerar_relatorio(d, {"cenario": "ransomware", "data": "2026-11-10", "respostas": cheio, "hotwash": "bom"})
        self.assertIn("Nenhuma lacuna registrada.", rel)
        self.assertIn("Duração registrada: 04:00", rel)

    def test_simulador_estrutura(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        for marcador in ("tt-lab", 'id="tt-dados"', "tt-missoes", "tt-cenario", "tt-inject", "tt-cronometro",
                         "tt-extra", "tt-relatorio", "iniciarTabletop", "proximoInjectTabletop",
                         "adicionarInjectTabletop", "gerarRelatorioTabletop", "restaurarTabletop"):
            self.assertIn(marcador, content, marcador)
        ini = content.index("var TT = JSON.parse")
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
        self.assertIn('initChecklist("tabletop")', content)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn("Exercicios-Tabletop/treinamento-exercicios-tabletop.html", content)
        self.assertIn('data-slug="Exercicios-Tabletop"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)


if __name__ == "__main__":
    unittest.main()
