#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_resposta_incidentes.py
Testes automatizados para o Estudo 18: Resposta-a-Incidentes
"""

import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402

FASES_REV2 = {
    "Preparação",
    "Detecção e Análise",
    "Contenção, Erradicação e Recuperação",
    "Atividades Pós-Incidente",
}
FUNCOES_REV3 = {"Govern", "Identify", "Protect", "Detect", "Respond", "Recover"}
CAMPOS_OPCAO = {"texto", "fase_rev2", "funcao_rev3", "horas", "evidencia", "propagacao", "pontos", "comentario", "proximo"}


class TestRespostaIncidentes(unittest.TestCase):
    """Valida a estrutura, o conteúdo e a compilação do estudo Resposta-a-Incidentes."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "resposta_a_incidentes_body.html"
        self.compiled_path = self.root / "Resposta-a-Incidentes" / "treinamento-resposta-a-incidentes.html"
        self.portal_path = self.root / "index.html"

    def _body(self):
        return self.body_path.read_text(encoding="utf-8")

    def _cenarios(self):
        m = re.search(
            r'<script type="application/json" id="ir-cenarios">(.*?)</script>', self._body(), re.S
        )
        self.assertIsNotNone(m, "Bloco JSON #ir-cenarios ausente no body")
        return json.loads(m.group(1))

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists(), "_geradores/resposta_a_incidentes_body.html deve existir.")
        self.assertTrue(self.compiled_path.exists(), "Resposta-a-Incidentes/treinamento-resposta-a-incidentes.html deve existir.")

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        termos = [
            "NIST SP 800-61 Rev. 2",
            "NIST SP 800-61 Rev. 3",
            "CSF 2.0",
            "Preparação",
            "Detecção e Análise",
            "Contenção, Erradicação e Recuperação",
            "Atividades Pós-Incidente",
            "Contenção de curto prazo",
            "Contenção de longo prazo",
            "RFC 3227",
            "Ordem de volatilidade",
            "Playbook",
            "Blameless",
            "Resolução CD/ANPD nº 15/2024",
            "MTTD",
            "MTTR",
            "ISO/IEC 27035",
        ]
        for termo in termos:
            self.assertIn(termo, content, f"Termo obrigatório ausente: {termo}")

    def test_diagrama_do_ciclo_compilado_em_svg(self):
        self.assertIn('<pre class="mermaid"', self._body())
        compilado = self.compiled_path.read_text(encoding="utf-8")
        self.assertIn('class="diagram-svg-wrap"', compilado)
        self.assertNotIn('<pre class="mermaid"', compilado)

    def test_simulador_estrutura(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        for marcador in ("ir-lab", 'id="ir-cenarios"', "iniciarCenarioIR", "escolherOpcaoIR", "reiniciarIR", "ir-cronometro"):
            self.assertIn(marcador, content, marcador)
        # O motor renderiza texto dos cenários só com textContent
        ini = content.index("var CENARIOS = JSON.parse")
        motor = content[ini:content.index("</script>", ini)]
        self.assertIn("window.iniciarCenarioIR", motor)
        self.assertNotIn("innerHTML", motor)

    def test_cenarios_existem(self):
        cen = self._cenarios()
        self.assertEqual(set(cen), {"ransomware", "vazamento-bd"})
        for chave, c in cen.items():
            for campo in ("titulo", "descricao", "inicio", "nos"):
                self.assertIn(campo, c, f"{chave}: campo {campo}")

    def test_arvore_valida_em_cada_cenario(self):
        for chave, c in self._cenarios().items():
            with self.subTest(cenario=chave):
                nos = c["nos"]
                self.assertIn(c["inicio"], nos)
                decisoes = [n for n in nos.values() if not n.get("final")]
                self.assertTrue(6 <= len(decisoes) <= 8, f"{len(decisoes)} decisões")
                fases_vistas = set()
                for nid, no in nos.items():
                    self.assertTrue(no.get("situacao"), f"{nid} sem situação")
                    if no.get("final"):
                        self.assertNotIn("opcoes", no, f"{nid} final com opções")
                        continue
                    self.assertTrue(2 <= len(no["opcoes"]) <= 3, f"{nid}: {len(no['opcoes'])} opções")
                    for op in no["opcoes"]:
                        self.assertEqual(set(op), CAMPOS_OPCAO, f"{nid}: campos da opção")
                        self.assertIn(op["fase_rev2"], FASES_REV2, nid)
                        self.assertIn(op["funcao_rev3"], FUNCOES_REV3, nid)
                        self.assertIn(op["proximo"], nos, f"{nid} -> {op['proximo']} inexistente")
                        self.assertIsInstance(op["horas"], (int, float))
                        self.assertGreaterEqual(op["horas"], 0)
                        self.assertIsInstance(op["evidencia"], bool)
                        self.assertIsInstance(op["propagacao"], bool)
                        self.assertIsInstance(op["pontos"], int)
                        self.assertTrue(op["comentario"])
                        fases_vistas.add(op["fase_rev2"])
                self.assertEqual(fases_vistas, FASES_REV2, "as 4 fases da Rev. 2 devem aparecer")

    def test_todo_caminho_termina_sem_ciclos(self):
        for chave, c in self._cenarios().items():
            with self.subTest(cenario=chave):
                nos = c["nos"]
                visitados = set()

                def percorre(nid, pilha):
                    self.assertNotIn(nid, pilha, f"ciclo em {nid}")
                    visitados.add(nid)
                    no = nos[nid]
                    if no.get("final"):
                        return
                    for op in no["opcoes"]:
                        percorre(op["proximo"], pilha | {nid})

                percorre(c["inicio"], frozenset())
                self.assertEqual(visitados, set(nos), f"nós inalcançáveis: {set(nos) - visitados}")

    def test_pior_caminho_custa_mais_horas_que_o_melhor(self):
        """O cronômetro mede impacto no negócio: decisões ruins não podem parecer mais baratas."""
        for chave, c in self._cenarios().items():
            with self.subTest(cenario=chave):
                nos = c["nos"]

                def extremo(nid, melhor):
                    no = nos[nid]
                    if no.get("final"):
                        return 0
                    escolha = (max if melhor else min)(no["opcoes"], key=lambda o: o["pontos"])
                    return escolha["horas"] + extremo(escolha["proximo"], melhor)

                self.assertGreater(extremo(c["inicio"], False), extremo(c["inicio"], True))

    def test_componentes_pedagogicos(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        self.assertIn('class="callout', content)
        self.assertIn('class="terminal-box', content)
        self.assertEqual(content.count('class="checklist-item"'), 7)
        self.assertGreaterEqual(content.count('class="quiz-item"'), 4)
        self.assertIn('class="facts-grid', content)
        self.assertIn('initChecklist("resposta-incidentes")', content)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn("Resposta-a-Incidentes/treinamento-resposta-a-incidentes.html", content)
        self.assertIn('data-slug="Resposta-a-Incidentes"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)


if __name__ == "__main__":
    unittest.main()
