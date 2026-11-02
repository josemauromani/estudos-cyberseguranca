#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_pam.py
Testes automatizados para o Estudo 40: PAM-e-Acessos-Privilegiados
"""

import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402

TIPOS_PROBLEMA = {"compartilhada", "sem_rotacao", "permanente", "orfa", "sem_mfa", "servico"}
TIPOS_CONTA = {"humana", "builtin", "servico", "gmsa", "emergencia"}


def achados(d, c):
    """Regras de auditoria (espelhadas no JavaScript)."""
    pol = d["politica"]
    out = set()
    if c["compartilhada"]:
        out.add("compartilhada")
    if c["tipo"] != "gmsa" and c["senha_idade_dias"] > pol["rotacao_dias"]:
        out.add("sem_rotacao")
    if c["tipo"] == "humana" and c["privilegio_permanente"]:
        out.add("permanente")
    if c["tipo"] != "emergencia" and c["ativa"] and (c["dono_desligado"] or c["ultimo_logon_dias"] > pol["inatividade_dias"]):
        out.add("orfa")
    if c["tipo"] == "humana" and c["tier"] in (0, 1) and not c["mfa"]:
        out.add("sem_mfa")
    if c["tipo"] == "servico" and (c["logon_interativo"] or c["tier"] == 0):
        out.add("servico")
    return out


def corrigido(d, c, problema, ativos):
    for k in d["controles"]:
        if k["id"] in ativos and problema in k["corrige"] and (not k["apenas_se"] or c[k["apenas_se"]]):
            return True
    return False


def risco(d, ativos=()):
    total = 0
    for c in d["contas"]:
        peso = d["pesos_tier"][str(c["tier"])]
        for p in achados(d, c):
            if not corrigido(d, c, p, set(ativos)):
                total += peso * d["problemas"][p]["severidade"]
    return total


class TestPam(unittest.TestCase):
    """Valida a estrutura, o conteúdo, as regras de auditoria e a compilação do estudo PAM-e-Acessos-Privilegiados."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "pam_e_acessos_privilegiados_body.html"
        self.compiled_path = self.root / "PAM-e-Acessos-Privilegiados" / "treinamento-pam-e-acessos-privilegiados.html"
        self.portal_path = self.root / "index.html"

    def _dados(self):
        body = self.body_path.read_text(encoding="utf-8")
        m = re.search(r'<script type="application/json" id="pam-dados">(.*?)</script>', body, re.S)
        self.assertIsNotNone(m, "Bloco JSON #pam-dados ausente no body")
        return json.loads(m.group(1))

    # ----------------------------------------------------------------- arquivos
    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        termos = [
            "PAM", "cofre", "checkout", "rotação", "gravação de sessão", "just-in-time", "JIT", "PIM", "JEA",
            "break-glass", "conta órfã", "recertificação", "menor privilégio", "segregação de funções",
            "Windows LAPS", "gMSA", "8.2", "5.18", "7.2.4", "8.2.2", "8.6", "T1078.002", "T1098",
            "CIS Controls",
        ]
        for termo in termos:
            self.assertIn(termo, content, f"Termo obrigatório ausente: {termo}")

    # -------------------------------------------------------------------- dados
    def test_contas_validas_e_gabarito_bate_com_as_regras(self):
        d = self._dados()
        self.assertEqual(set(d["problemas"]), TIPOS_PROBLEMA)
        self.assertGreaterEqual(len(d["contas"]), 10)
        ids = [c["id"] for c in d["contas"]]
        self.assertEqual(len(ids), len(set(ids)))
        vistos = set()
        for c in d["contas"]:
            with self.subTest(conta=c["id"]):
                self.assertIn(c["tipo"], TIPOS_CONTA)
                self.assertIn(c["tier"], (0, 1, 2))
                self.assertTrue(c["nome"].strip() and c["dono"].strip() and c["nota"].strip())
                self.assertEqual(set(c["problemas"]), achados(d, c))
                vistos |= set(c["problemas"])
        self.assertEqual(vistos, TIPOS_PROBLEMA, "todo tipo de problema deve aparecer")

    def test_pegadinhas(self):
        d = self._dados()
        limpas = [c for c in d["contas"] if not c["problemas"]]
        self.assertGreaterEqual(len(limpas), 3)
        tipos_limpos = {c["tipo"] for c in limpas}
        self.assertIn("emergencia", tipos_limpos)
        self.assertIn("gmsa", tipos_limpos)
        emerg = next(c for c in d["contas"] if c["tipo"] == "emergencia")
        self.assertTrue(emerg["privilegio_permanente"] and not emerg["mfa"])
        self.assertGreater(emerg["ultimo_logon_dias"], d["politica"]["inatividade_dias"])

    def test_controles_e_risco(self):
        d = self._dados()
        for k in d["controles"]:
            with self.subTest(controle=k["id"]):
                self.assertTrue(set(k["corrige"]) <= TIPOS_PROBLEMA)
                self.assertIn(k["tipo"], ("preventivo", "detectivo", "corretivo"))
                if k["apenas_se"]:
                    self.assertTrue(all(k["apenas_se"] in c for c in d["contas"]))
        inicial = risco(d)
        self.assertGreater(inicial, 0)
        gravacao = next(k for k in d["controles"] if k["id"] == "gravacao")
        self.assertEqual(gravacao["corrige"], [])
        self.assertEqual(gravacao["tipo"], "detectivo")
        self.assertEqual(risco(d, ["gravacao"]), inicial, "controle detectivo não reduz a pontuação")
        jea = next(k for k in d["controles"] if k["id"] == "jea")
        ganho_jea = sum(d["pesos_tier"][str(c["tier"])] * d["problemas"]["permanente"]["severidade"]
                        for c in d["contas"] if c[jea["apenas_se"]] and "permanente" in c["problemas"])
        self.assertGreater(ganho_jea, 0)
        self.assertEqual(risco(d, ["jea"]), inicial - ganho_jea)
        corretivos = [k["id"] for k in d["controles"] if k["corrige"]]
        self.assertEqual(risco(d, corretivos), 0)
        self.assertEqual(d["risco_inicial"], inicial)

    # ---------------------------------------------------------------- compilado
    def test_simulador_estrutura(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        for marcador in ("pam-lab", 'id="pam-dados"', "pam-inventario", "pam-conferencia", "pam-controles", "pam-risco",
                         "alternarAchadoPam", "conferirAchadosPam", "alternarControlePam", "restaurarPam"):
            self.assertIn(marcador, content, marcador)
        ini = content.index("var PAM = JSON.parse")
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
        self.assertIn('initChecklist("pam-acessos-privilegiados")', content)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn("PAM-e-Acessos-Privilegiados/treinamento-pam-e-acessos-privilegiados.html", content)
        self.assertIn('data-slug="PAM-e-Acessos-Privilegiados"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)


if __name__ == "__main__":
    unittest.main()
