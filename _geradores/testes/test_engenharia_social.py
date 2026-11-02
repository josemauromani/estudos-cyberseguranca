#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_engenharia_social.py
Testes automatizados para o Estudo 15: Engenharia-Social-e-Phishing
"""

import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402

RE_URL = re.compile(r"https?://([^/\s\"]+)")


def dominio(endereco):
    return endereco.split("@")[-1].lower()


def org(dom):
    return ".".join(dom.lower().split(".")[-2:])


class TestEngenhariaSocial(unittest.TestCase):
    """Valida a estrutura, o conteúdo, os e-mails do simulador e a compilação do estudo Engenharia-Social-e-Phishing."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "engenharia_social_e_phishing_body.html"
        self.compiled_path = self.root / "Engenharia-Social-e-Phishing" / "treinamento-engenharia-social-e-phishing.html"
        self.portal_path = self.root / "index.html"

    def _dados(self):
        body = self.body_path.read_text(encoding="utf-8")
        m = re.search(r'<script type="application/json" id="ph-dados">(.*?)</script>', body, re.S)
        self.assertIsNotNone(m, "Bloco JSON #ph-dados ausente no body")
        return json.loads(m.group(1))

    @staticmethod
    def _indicadores(email):
        return [t for t in email["trechos"] if t.get("indicador")]

    # ----------------------------------------------------------------- arquivos
    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        termos = [
            "autoridade", "urgência", "escassez", "prova social", "reciprocidade", "pretexting", "spear phishing",
            "whaling", "BEC", "vishing", "smishing", "quishing", "baiting", "tailgating", "typosquatting",
            "homóglifo", "Return-Path", "Reply-To", "AiTM", "FIDO2", "passkey", "number matching",
            "taxa de reporte", "T1566.001", "T1566.002", "T1598", "T1621", "T1557", "Estudo 29",
        ]
        for termo in termos:
            self.assertIn(termo, content, f"Termo obrigatório ausente: {termo}")

    # -------------------------------------------------------------------- dados
    def test_emails_validos(self):
        d = self._dados()
        self.assertEqual(len(d["emails"]), 4)
        vereditos = [e["veredito"] for e in d["emails"]]
        self.assertEqual(vereditos.count("legitimo"), 1)
        self.assertEqual(vereditos.count("phishing"), 3)
        for e in d["emails"]:
            with self.subTest(email=e["id"]):
                ids = [t["id"] for t in e["trechos"]]
                self.assertEqual(len(ids), len(set(ids)))
                for campo in ("from", "return_path", "remetente_exibido", "assunto", "explicacao_veredito"):
                    self.assertTrue(e[campo].strip(), campo)
                for end in [e["from"], e["return_path"], e.get("reply_to", "x@y.example")]:
                    self.assertTrue(dominio(end).endswith(".example"), end)
                for t in e["trechos"]:
                    self.assertIn(t["parte"], ("cabecalho", "corpo", "link", "anexo"))
                    self.assertTrue(t["texto"].strip())
                    if t["parte"] == "link":
                        self.assertTrue(RE_URL.match(t["href"]).group(1).endswith(".example"), t["href"])
                    ind = t.get("indicador")
                    if ind:
                        self.assertTrue(ind["explicacao"].strip())
                        if ind.get("gatilho"):
                            self.assertIn(ind["gatilho"], d["gatilhos"])
                n = len(self._indicadores(e))
                if e["veredito"] == "phishing":
                    self.assertGreaterEqual(n, 3)
                else:
                    self.assertEqual(n, 0)
        partes = {t["parte"] for e in d["emails"] for t in e["trechos"]}
        self.assertEqual(partes, {"cabecalho", "corpo", "link", "anexo"})

    def test_indicadores_coerentes_com_enderecos_e_links(self):
        d = self._dados()
        for e in d["emails"]:
            with self.subTest(email=e["id"]):
                tipos = {t["indicador"]["tipo"] for t in self._indicadores(e)}
                if "return_path" in tipos:
                    self.assertNotEqual(org(dominio(e["return_path"])), org(dominio(e["from"])))
                if "reply_to" in tipos:
                    self.assertNotEqual(org(dominio(e["reply_to"])), org(dominio(e["from"])))
                for t in e["trechos"]:
                    if t["parte"] != "link":
                        continue
                    exibido = RE_URL.search(t["texto"]).group(1).lower()
                    real = RE_URL.match(t["href"]).group(1).lower()
                    divergente = org(exibido) != org(real)
                    eh_indicador = bool(t.get("indicador")) and t["indicador"]["tipo"] == "link_divergente"
                    self.assertEqual(divergente, eh_indicador, t["id"])
                if e["veredito"] == "legitimo":
                    self.assertEqual(org(dominio(e["return_path"])), org(dominio(e["from"])))
                    self.assertTrue(dominio(e["from"]).endswith(d["dominio_interno"]))

    def test_gatilhos_variados(self):
        d = self._dados()
        usados = {t["indicador"].get("gatilho") for e in d["emails"] for t in self._indicadores(e)} - {None}
        self.assertGreaterEqual(len(usados), 4)

    # ---------------------------------------------------------------- compilado
    def test_simulador_estrutura(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        for marcador in ("ph-lab", 'id="ph-dados"', "ph-caixa", "ph-email", "ph-status", "ph-resultado", "ph-placar",
                         "selecionarEmailPhishing", "marcarTrechoPhishing", "conferirEmailPhishing", "restaurarPhishing"):
            self.assertIn(marcador, content, marcador)
        ini = content.index("var PH = JSON.parse")
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
        self.assertIn('initChecklist("engenharia-social")', content)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn("Engenharia-Social-e-Phishing/treinamento-engenharia-social-e-phishing.html", content)
        self.assertIn('data-slug="Engenharia-Social-e-Phishing"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)


if __name__ == "__main__":
    unittest.main()
