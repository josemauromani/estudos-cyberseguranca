#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_certificacoes_carreira.py
Testes automatizados para o Estudo 33: Certificacoes-e-Carreira
"""

import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import CERTIFICACOES, ESTUDOS_DADOS  # noqa: E402

GERADORES = Path(__file__).resolve().parent.parent
CAMPOS_PERFIL = ("anos_ti", "anos_si", "anos_gestao_si", "anos_nuvem")


def catalogo():
    """slug -> número do módulo, na ordem de _geradores/estudos.txt."""
    numeros = {}
    for linha in (GERADORES / "estudos.txt").read_text(encoding="utf-8").splitlines():
        if linha.strip() and not linha.startswith("#"):
            numeros[linha.split("|")[0]] = len(numeros) + 1
    return numeros


def efetivo(perfil):
    """Gestão de segurança conta como segurança; segurança e nuvem contam como TI."""
    p = dict(perfil)
    p["anos_si"] = max(p.get("anos_si", 0), p.get("anos_gestao_si", 0))
    p["anos_ti"] = max(p.get("anos_ti", 0), p["anos_si"], p.get("anos_nuvem", 0))
    return p


def elegibilidade(cert, perfil):
    """Regra espelhada no JavaScript: 'sem-exigencia', 'elegivel' ou 'pendente'."""
    perfil = efetivo(perfil)
    req = cert["requisitos"]
    if not req:
        return "sem-exigencia"
    if req.get("alternativa") and perfil.get("treinamento_oficial"):
        return "elegivel"
    for campo in CAMPOS_PERFIL:
        if campo in req:
            minimo = req[campo]
            if campo == "anos_si" and perfil.get("graduacao"):
                minimo -= req.get("desconto_graduacao", 0)
            if perfil.get(campo, 0) < minimo:
                return "pendente"
    return "elegivel"


class TestCertificacoesCarreira(unittest.TestCase):
    """Valida a estrutura, o conteúdo, a coerência com o portal e a compilação do estudo Certificacoes-e-Carreira."""

    def setUp(self):
        self.root = GERADORES.parent
        self.body_path = GERADORES / "certificacoes_e_carreira_body.html"
        self.compiled_path = self.root / "Certificacoes-e-Carreira" / "treinamento-certificacoes-e-carreira.html"
        self.portal_path = self.root / "index.html"

    def _dados(self):
        body = self.body_path.read_text(encoding="utf-8")
        m = re.search(r'<script type="application/json" id="cert-dados">(.*?)</script>', body, re.S)
        self.assertIsNotNone(m, "Bloco JSON #cert-dados ausente no body")
        return json.loads(m.group(1))

    def _cert(self, d, sigla):
        return next(c for c in d["certificacoes"] if c["sigla"] == sigla)

    # ----------------------------------------------------------------- arquivos
    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        termos = [
            "Ciência da Computação", "Sistemas de Informação", "tecnólogo", "lato sensu", "stricto sensu",
            "360 horas", "CEH", "EC-Council", "CISM", "ISACA", "CISSP", "ISC2", "CCSP", "GSEC", "GIAC",
            "Security+", "CompTIA", "SY0-701", "Associate of ISC2", "CPE", "ISO/IEC 17024",
            "NICE Framework", "NIST SP 800-181", "Work Role", "TKS",
        ]
        for termo in termos:
            self.assertIn(termo, content, f"Termo obrigatório ausente: {termo}")

    # -------------------------------------------------------------------- dados
    def test_coerencia_com_a_matriz_do_portal(self):
        d = self._dados()
        self.assertEqual([c["sigla"] for c in d["certificacoes"]], [c["sigla"] for c in CERTIFICACOES])
        for portal in CERTIFICACOES:
            with self.subTest(cert=portal["sigla"]):
                cert = self._cert(d, portal["sigla"])
                self.assertEqual(cert["nome"], portal["nome"])
                self.assertEqual(cert["orgao"], portal["orgao"])
                cobertos = {m for dom in cert["dominios"] for m in dom["modulos"]}
                faltando = set(portal["modulos"]) - cobertos
                self.assertFalse(faltando, f"módulos do portal sem domínio: {faltando}")

    def test_modulos_batem_com_o_catalogo(self):
        d = self._dados()
        numeros = catalogo()
        usados = {m for c in d["certificacoes"] for dom in c["dominios"] for m in dom["modulos"]}
        self.assertEqual(set(d["modulos"]), usados, "o dicionário de módulos deve ter exatamente os usados")
        for slug, info in d["modulos"].items():
            with self.subTest(modulo=slug):
                self.assertIn(slug, ESTUDOS_DADOS)
                self.assertEqual(info["numero"], numeros[slug])
                self.assertEqual(info["titulo"], ESTUDOS_DADOS[slug]["titulo"])

    def test_dominios_e_pesos(self):
        d = self._dados()
        esperados = {"Security+": 5, "CISSP": 8, "CCSP": 6, "CISM": 4, "CEH": 9}
        for c in d["certificacoes"]:
            with self.subTest(cert=c["sigla"]):
                self.assertIn(c["nivel"], (1, 2, 3))
                for campo in ("foco", "experiencia", "manutencao", "nota_dominios"):
                    self.assertTrue(c[campo].strip(), campo)
                if c["sigla"] in esperados:
                    self.assertEqual(len(c["dominios"]), esperados[c["sigla"]])
                pesos = [dom["peso"] for dom in c["dominios"]]
                if c["sigla"] in ("Security+", "CISSP", "CCSP", "CISM"):
                    self.assertEqual(sum(pesos), 100)
                else:
                    self.assertTrue(all(p is None for p in pesos), "sem pesos inventados para CEH e GSEC")
                for dom in c["dominios"]:
                    self.assertTrue(dom["nome"].strip())
                    if dom.get("parcial") or not dom["modulos"]:
                        self.assertTrue(dom.get("nota", "").strip(), f"{dom['nome']} precisa de nota")

    def test_lacuna_e_cobertura_parcial(self):
        d = self._dados()
        ceh = self._cert(d, "CEH")
        lacunas = [dom["nome"] for dom in ceh["dominios"] if not dom["modulos"]]
        parciais = [dom["nome"] for dom in ceh["dominios"] if dom.get("parcial")]
        self.assertEqual(len(lacunas), 1)
        self.assertIn("sem fio", lacunas[0])
        self.assertEqual(len(parciais), 1)

    def test_requisitos_de_experiencia(self):
        d = self._dados()
        req = {c["sigla"]: c["requisitos"] for c in d["certificacoes"]}
        self.assertEqual(req["Security+"], {})
        self.assertEqual(req["GSEC"], {})
        self.assertEqual(req["CEH"]["anos_si"], 2)
        self.assertTrue(req["CEH"]["alternativa"].strip())
        self.assertEqual((req["CISSP"]["anos_si"], req["CISSP"]["desconto_graduacao"]), (5, 1))
        self.assertEqual((req["CCSP"]["anos_ti"], req["CCSP"]["anos_si"], req["CCSP"]["anos_nuvem"]), (5, 3, 1))
        self.assertEqual((req["CISM"]["anos_si"], req["CISM"]["anos_gestao_si"]), (5, 3))
        for c in d["certificacoes"]:
            if c["requisitos"]:
                self.assertTrue(c["sem_experiencia"].strip(), c["sigla"])

    def test_regra_de_elegibilidade(self):
        d = self._dados()
        iniciante = {"anos_ti": 0, "anos_si": 0, "anos_gestao_si": 0, "anos_nuvem": 0}
        self.assertEqual(elegibilidade(self._cert(d, "Security+"), iniciante), "sem-exigencia")
        self.assertEqual(elegibilidade(self._cert(d, "CISSP"), iniciante), "pendente")
        self.assertEqual(elegibilidade(self._cert(d, "CEH"), dict(iniciante, treinamento_oficial=True)), "elegivel")
        graduado = {"anos_ti": 6, "anos_si": 4, "anos_gestao_si": 0, "anos_nuvem": 0, "graduacao": True}
        self.assertEqual(elegibilidade(self._cert(d, "CISSP"), graduado), "elegivel")
        self.assertEqual(elegibilidade(self._cert(d, "CISSP"), dict(graduado, graduacao=False)), "pendente")
        self.assertEqual(elegibilidade(self._cert(d, "CCSP"), graduado), "pendente")
        self.assertEqual(elegibilidade(self._cert(d, "CCSP"), dict(graduado, anos_si=3, anos_nuvem=1)), "elegivel")
        self.assertEqual(elegibilidade(self._cert(d, "CISM"), dict(graduado, anos_si=5, anos_gestao_si=3)), "elegivel")
        # Anos em segurança contam como anos em TI, e anos em gestão de segurança contam como anos em segurança.
        so_seguranca = {"anos_ti": 0, "anos_si": 5, "anos_gestao_si": 0, "anos_nuvem": 1}
        self.assertEqual(elegibilidade(self._cert(d, "CCSP"), so_seguranca), "elegivel")
        so_gestao = {"anos_ti": 0, "anos_si": 0, "anos_gestao_si": 5, "anos_nuvem": 0}
        self.assertEqual(elegibilidade(self._cert(d, "CISM"), so_gestao), "elegivel")

    # ---------------------------------------------------------------- compilado
    def test_simulador_estrutura(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        for marcador in ("cert-lab", 'id="cert-dados"', "cert-selecao", "cert-perfil", "cert-resultado",
                         "cert-plano", "alternarCertificacao", "atualizarPerfilCert", "restaurarCert"):
            self.assertIn(marcador, content, marcador)
        ini = content.index("var CERT = JSON.parse")
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
        self.assertIn('initChecklist("certificacoes-carreira")', content)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn("Certificacoes-e-Carreira/treinamento-certificacoes-e-carreira.html", content)
        self.assertIn('data-slug="Certificacoes-e-Carreira"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)


if __name__ == "__main__":
    unittest.main()
