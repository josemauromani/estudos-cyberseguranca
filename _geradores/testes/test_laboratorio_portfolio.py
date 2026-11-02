#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_laboratorio_portfolio.py
Testes automatizados para o Estudo 37: Laboratorio-Domestico-e-Portfolio
"""

import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402

VEREDITOS = {"cabe", "apertado", "nao_cabe", "incompativel"}


def veredito(d, host, vms):
    """Regra do planejador (espelhada no JavaScript)."""
    cat = {v["id"]: v for v in d["catalogo"]}
    if host["arm"] and any(not cat[v]["arm"] for v in vms):
        return "incompativel"
    ram = sum(cat[v]["ram"] for v in vms) + d["reserva_host_gb"]
    vcpu = sum(cat[v]["vcpu"] for v in vms)
    disco = sum(cat[v]["disco"] for v in vms)
    if ram > host["ram"] or disco > host["disco"]:
        return "nao_cabe"
    if ram > d["limite_apertado"] * host["ram"] or vcpu > d["vcpu_por_nucleo"] * host["nucleos"]:
        return "apertado"
    return "cabe"


class TestLaboratorioPortfolio(unittest.TestCase):
    """Valida a estrutura, o conteúdo, o planejador e a compilação do estudo Laboratorio-Domestico-e-Portfolio."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "laboratorio_domestico_e_portfolio_body.html"
        self.compiled_path = (self.root / "Laboratorio-Domestico-e-Portfolio"
                              / "treinamento-laboratorio-domestico-e-portfolio.html")
        self.portal_path = self.root / "index.html"

    def _dados(self):
        body = self.body_path.read_text(encoding="utf-8")
        m = re.search(r'<script type="application/json" id="hl-dados">(.*?)</script>', body, re.S)
        self.assertIsNotNone(m, "Bloco JSON #hl-dados ausente no body")
        return json.loads(m.group(1))

    # ----------------------------------------------------------------- arquivos
    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        termos = [
            "tipo 1", "tipo 2", "Proxmox", "VirtualBox", "Hyper-V", "snapshot", "NAT", "host-only",
            "rede interna", "bridge", "OPNsense", "Wazuh", "Kali", "180 dias", "jeopardy", "attack-defense",
            "write-up", "README", "GitHub", "Lei 12.737/2012", "154-A", "Lei 14.155/2021", "autorização por escrito",
            "bug bounty", "PortSwigger", "Hack The Box", "TryHackMe", "CyberDefenders", "OverTheWire",
        ]
        for termo in termos:
            self.assertIn(termo, content, f"Termo obrigatório ausente: {termo}")

    # -------------------------------------------------------------------- dados
    def test_catalogo(self):
        d = self._dados()
        ids = [v["id"] for v in d["catalogo"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreaterEqual(len(ids), 7)
        funcoes = {v["funcao"] for v in d["catalogo"]}
        self.assertTrue({"firewall", "dc", "siem", "atacante", "alvo"} <= funcoes, "topologia mínima")
        for v in d["catalogo"]:
            with self.subTest(vm=v["id"]):
                self.assertIn(v["funcao"], d["funcoes"])
                for campo in ("ram", "vcpu", "disco"):
                    self.assertIsInstance(v[campo], int)
                    self.assertGreater(v[campo], 0)
                self.assertIsInstance(v["arm"], bool)
                self.assertTrue(v["nome"].strip() and v["nota"].strip())
        self.assertTrue(any(not v["arm"] for v in d["catalogo"]) and any(v["arm"] for v in d["catalogo"]))

    def test_perfis_e_exemplos_seguem_a_regra(self):
        d = self._dados()
        ids = {v["id"] for v in d["catalogo"]}
        for p in d["perfis"]:
            self.assertTrue(set(p["vms"]) <= ids, p["id"])
        perfis = {p["id"]: p["vms"] for p in d["perfis"]}
        vistos = set()
        for ex in d["exemplos"]:
            with self.subTest(exemplo=ex["nome"]):
                vms = ex["vms"] if "vms" in ex else perfis[ex["perfil"]]
                self.assertTrue(set(vms) <= ids)
                self.assertEqual(veredito(d, ex["host"], vms), ex["esperado"])
                vistos.add(ex["esperado"])
        self.assertEqual(vistos, VEREDITOS, "os exemplos cobrem os quatro vereditos")

    def test_portfolio_e_isolamento(self):
        d = self._dados()
        ids = {v["id"] for v in d["catalogo"]}
        for p in d["portfolio"]:
            with self.subTest(projeto=p["projeto"][:30]):
                self.assertTrue(set(p["requer"]) <= ids)
                self.assertTrue(p["modulos"])
                for m in p["modulos"]:
                    self.assertIn(m, ESTUDOS_DADOS)
        self.assertTrue(any(not p["requer"] for p in d["portfolio"]), "precisa de projeto que não depende de VM")
        for i in d["isolamento"]:
            self.assertTrue(set(i["com"]) <= ids and set(i["sem"]) <= ids, i["texto"][:30])
        self.assertTrue(any(i["sem"] == ["opnsense"] for i in d["isolamento"]), "aviso para laboratório sem firewall")

    def test_numeros_dos_estudos_no_roteiro(self):
        """O mapa slug -> número usado no roteiro precisa bater com o CURRICULO.md."""
        d = self._dados()
        body = self.body_path.read_text(encoding="utf-8")
        m = re.search(r"var MODULOS = (\{.*?\});", body, re.S)
        self.assertIsNotNone(m, "mapa MODULOS ausente no motor")
        mapa = json.loads(m.group(1))
        curriculo = (self.root / "_geradores" / "CURRICULO.md").read_text(encoding="utf-8")
        numeros = {slug: int(n) for n, slug in re.findall(r"^#### (\d+)\. (\S+)$", curriculo, re.M)}
        usados = {mod for p in d["portfolio"] for mod in p["modulos"]}
        self.assertTrue(usados <= set(mapa), usados - set(mapa))
        for slug, n in mapa.items():
            self.assertEqual(n, numeros[slug], slug)

    # ---------------------------------------------------------------- compilado
    def test_simulador_estrutura(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        for marcador in ("hl-lab", 'id="hl-dados"', "hl-host", "hl-catalogo", "hl-recursos", "hl-topologia",
                         "hl-checklist", "hl-portfolio", "alternarVmHomelab", "aplicarPerfilHomelab",
                         "calcularHomelab", "restaurarHomelab"):
            self.assertIn(marcador, content, marcador)
        ini = content.index("var HL = JSON.parse")
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
        self.assertIn('initChecklist("laboratorio-portfolio")', content)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn("Laboratorio-Domestico-e-Portfolio/treinamento-laboratorio-domestico-e-portfolio.html", content)
        self.assertIn('data-slug="Laboratorio-Domestico-e-Portfolio"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)


if __name__ == "__main__":
    unittest.main()
