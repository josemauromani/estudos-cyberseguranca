#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_ransomware.py
Testes automatizados para o Estudo 42: Ransomware-Prevencao-a-Recuperacao
"""

import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402


def custo(d, efeitos):
    return sum(d["pesos"][k] * v for k, v in efeitos.items())


def ordem_valida(itens, ordem):
    pos = {i: n for n, i in enumerate(ordem)}
    return all(pos[dep] < pos[it["id"]] for it in itens for dep in it["depende_de"])


class TestRansomware(unittest.TestCase):
    """Valida a estrutura, o conteúdo, a linha do tempo, a ordem de recuperação e a compilação do estudo Ransomware."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "ransomware_prevencao_a_recuperacao_body.html"
        self.compiled_path = (self.root / "Ransomware-Prevencao-a-Recuperacao"
                              / "treinamento-ransomware-prevencao-a-recuperacao.html")
        self.portal_path = self.root / "index.html"

    def _dados(self):
        body = self.body_path.read_text(encoding="utf-8")
        m = re.search(r'<script type="application/json" id="rw-dados">(.*?)</script>', body, re.S)
        self.assertIsNotNone(m, "Bloco JSON #rw-dados ausente no body")
        return json.loads(m.group(1))

    # ----------------------------------------------------------------- arquivos
    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        termos = [
            "RaaS", "afiliados", "dupla extorsão", "tripla extorsão", "shadow copies", "vssadmin", "rclone",
            "T1486", "T1490", "T1567", "T1003.006", "DCSync", "isolar", "desligar", "RAM", "krbtgt",
            "No More Ransom", "ID Ransomware", "3 dias úteis", "ANPD", "OFAC", "3-2-1-1-0", "imutável",
            "#StopRansomware", "NIST IR 8374",
        ]
        for termo in termos:
            self.assertIn(termo, content, f"Termo obrigatório ausente: {termo}")

    # ---------------------------------------------------------- linha do tempo
    def test_decisoes_e_melhor_opcao(self):
        d = self._dados()
        metricas = set(d["pesos"])
        self.assertEqual(metricas, set(d["estado_inicial"]))
        decisoes = d["decisoes"]
        self.assertEqual(len(decisoes), 6)
        horarios = [x["quando"] for x in decisoes]
        self.assertEqual(horarios, sorted(horarios), "decisões em ordem cronológica")
        for dec in decisoes:
            with self.subTest(decisao=dec["id"]):
                self.assertTrue(dec["situacao"].strip() and dec["rotulo_hora"].strip())
                self.assertEqual(len(dec["opcoes"]), 3)
                melhores = [o for o in dec["opcoes"] if o["melhor"]]
                self.assertEqual(len(melhores), 1)
                for o in dec["opcoes"]:
                    self.assertTrue(o["texto"].strip() and o["consequencia"].strip())
                    self.assertTrue(set(o["efeitos"]) <= metricas)
                    self.assertTrue(all(v >= 0 for v in o["efeitos"].values()), "efeitos só pioram ou mantêm")
                c_melhor = custo(d, melhores[0]["efeitos"])
                for o in dec["opcoes"]:
                    if not o["melhor"]:
                        self.assertLess(c_melhor, custo(d, o["efeitos"]), o["texto"])

    def test_melhor_caminho_e_minimo_global(self):
        d = self._dados()
        melhor = sum(custo(d, next(o for o in dec["opcoes"] if o["melhor"])["efeitos"]) for dec in d["decisoes"])
        pior = sum(max(custo(d, o["efeitos"]) for o in dec["opcoes"]) for dec in d["decisoes"])
        self.assertEqual(d["custo_melhor_caminho"], melhor)
        self.assertGreater(pior, 5 * melhor)

    # -------------------------------------------------------- ordem de recuperação
    def test_ordem_de_recuperacao(self):
        r = self._dados()["recuperacao"]
        ids = [i["id"] for i in r["itens"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreaterEqual(len(ids), 8)
        for it in r["itens"]:
            with self.subTest(item=it["id"]):
                self.assertTrue(it["nome"].strip() and it["motivo"].strip())
                self.assertTrue(set(it["depende_de"]) <= set(ids))
                self.assertNotIn(it["id"], it["depende_de"])
        self.assertEqual(sorted(r["sugerida"]), sorted(ids))
        self.assertTrue(ordem_valida(r["itens"], r["sugerida"]))
        self.assertFalse(ordem_valida(r["itens"], list(reversed(r["sugerida"]))), "a ordem inversa deve violar dependências")
        self.assertNotEqual(r["inicial"], r["sugerida"])
        self.assertEqual(sorted(r["inicial"]), sorted(ids))
        self.assertFalse(ordem_valida(r["itens"], r["inicial"]), "o aluno começa de uma ordem inválida")

    # ---------------------------------------------------------------- compilado
    def test_simulador_estrutura(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        for marcador in ("rw-lab", 'id="rw-dados"', "rw-decisao", "rw-metricas", "rw-historico", "rw-recuperacao",
                         "rw-ordem-resultado", "escolherAcaoRansomware", "avancarRansomware",
                         "moverItemRecuperacao", "verificarOrdemRecuperacao", "restaurarRansomware"):
            self.assertIn(marcador, content, marcador)
        ini = content.index("var RW = JSON.parse")
        motor = content[ini:content.index("</script>", ini)]
        self.assertNotIn("innerHTML", motor)

    def test_componentes_pedagogicos(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        self.assertIn('class="callout', content)
        self.assertIn('class="terminal-box', content)
        self.assertIn('class="diagram-svg-wrap', content)
        self.assertNotIn('<pre class="mermaid"', content)
        self.assertEqual(content.count('class="checklist-item"'), 7)
        self.assertGreaterEqual(content.count('class="quiz-item"'), 6)
        self.assertIn('class="facts-grid', content)
        self.assertIn('initChecklist("ransomware")', content)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn("Ransomware-Prevencao-a-Recuperacao/treinamento-ransomware-prevencao-a-recuperacao.html", content)
        self.assertIn('data-slug="Ransomware-Prevencao-a-Recuperacao"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)


if __name__ == "__main__":
    unittest.main()
