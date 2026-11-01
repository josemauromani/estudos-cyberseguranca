#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_ingles_tecnico.py
Testes automatizados para o Estudo 32: Ingles-Tecnico-Ciber
"""

import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402

RE_TERMO = re.compile(r"\[\[([^|\]]+)\|([^\]]+)\]\]")
TIPOS = {"tecnico", "falso-cognato", "modal", "sigla"}


class TestInglesTecnico(unittest.TestCase):
    """Valida a estrutura, o conteúdo, os dados do simulador e a compilação do estudo Ingles-Tecnico-Ciber."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "ingles_tecnico_ciber_body.html"
        self.compiled_path = self.root / "Ingles-Tecnico-Ciber" / "treinamento-ingles-tecnico-ciber.html"
        self.portal_path = self.root / "index.html"

    def _dados(self):
        body = self.body_path.read_text(encoding="utf-8")
        m = re.search(r'<script type="application/json" id="ing-dados">(.*?)</script>', body, re.S)
        self.assertIsNotNone(m, "Bloco JSON #ing-dados ausente no body")
        return json.loads(m.group(1))

    def _texto_advisory(self, d):
        return "\n".join(s["titulo"] + "\n" + s["texto"] for s in d["advisory"]["secoes"])

    # ----------------------------------------------------------------- arquivos
    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        termos = [
            "advisory", "Summary", "Affected Versions", "Impact", "Mitigation", "Workaround",
            "CVE", "NVD", "CWE", "CVSS", "AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H", "KEV",
            "RFC 2119", "RFC 8174", "MUST NOT", "SHOULD", "MAY", "REQUIRED", "OPTIONAL",
            "falsos cognatos", "exploit", "eventually", "actually", "registro formal", "registro informal",
        ]
        for termo in termos:
            self.assertIn(termo, content, f"Termo obrigatório ausente: {termo}")

    # -------------------------------------------------------------------- dados
    def test_advisory_ficticio_e_estruturado(self):
        d = self._dados()
        adv = d["advisory"]
        self.assertRegex(adv["cve"], r"^CVE-2099-\d{4,}$", "o ano 2099 deixa claro que o CVE é fictício")
        titulos = [s["titulo"] for s in adv["secoes"]]
        for secao in ("Summary", "Affected Versions", "Impact", "Mitigation", "Workaround"):
            self.assertIn(secao, titulos)
        texto = self._texto_advisory(d)
        self.assertIn("AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H", texto)
        for dominio in re.findall(r"\b[a-z0-9-]+(?:\.[a-z0-9-]+)+\b", RE_TERMO.sub(r"\1", texto)):
            if re.search(r"[a-z]", dominio.split(".")[-1]) and not re.match(r"^\d", dominio):
                self.assertTrue(dominio.endswith(".example"), f"domínio real no advisory: {dominio}")

    def test_termos_marcados_existem_no_glossario(self):
        d = self._dados()
        usados = {chave for _, chave in RE_TERMO.findall(self._texto_advisory(d))}
        faltando = usados - set(d["glossario"])
        self.assertFalse(faltando, f"termos sem glossário: {faltando}")
        self.assertGreaterEqual(len(usados), 20)

    def test_glossario(self):
        d = self._dados()
        g = d["glossario"]
        self.assertGreaterEqual(len(g), 25)
        self.assertEqual({e["tipo"] for e in g.values()}, TIPOS)
        for chave, e in g.items():
            with self.subTest(termo=chave):
                for campo in ("termo", "traducao", "definicao"):
                    self.assertTrue(e[campo].strip(), campo)
        for chave in ("exploit", "eventually", "actually"):
            self.assertEqual(g[chave]["tipo"], "falso-cognato", chave)
        for chave in ("must", "must-not", "should", "may"):
            self.assertEqual(g[chave]["tipo"], "modal", chave)
        self.assertTrue(d["chave_storage"].startswith("cs_"))

    def test_perguntas_de_compreensao(self):
        d = self._dados()
        self.assertEqual(len(d["perguntas"]), 5)
        for i, p in enumerate(d["perguntas"]):
            with self.subTest(pergunta=i + 1):
                self.assertTrue(p["enunciado"].strip())
                self.assertGreaterEqual(len(p["opcoes"]), 3)
                self.assertEqual(sum(1 for o in p["opcoes"] if o["correta"]), 1)
                for o in p["opcoes"]:
                    self.assertTrue(o["texto"].strip())
                    self.assertTrue(o["comentario"].strip())

    # ---------------------------------------------------------------- compilado
    def test_simulador_estrutura(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        for marcador in ("ing-lab", 'id="ing-dados"', "ing-advisory", "ing-definicao", "ing-perguntas",
                         "ing-flashcards", "mostrarTermoIngles", "responderPerguntaIngles",
                         "virarFlashcard", "marcarFlashcard", "reiniciarFlashcards"):
            self.assertIn(marcador, content, marcador)
        ini = content.index("var ING = JSON.parse")
        motor = content[ini:content.index("</script>", ini)]
        self.assertNotIn("innerHTML", motor)
        self.assertIn("try", motor, "acesso ao localStorage deve ser protegido")

    def test_componentes_pedagogicos(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        self.assertIn('class="callout', content)
        self.assertIn('class="terminal-box', content)
        self.assertIn('class="diagram-svg-wrap', content)
        self.assertNotIn('<pre class="mermaid"', content)
        self.assertEqual(content.count('class="checklist-item"'), 7)
        self.assertGreaterEqual(content.count('class="quiz-item"'), 6)
        self.assertIn('class="facts-grid', content)
        self.assertIn('initChecklist("ingles-tecnico")', content)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn("Ingles-Tecnico-Ciber/treinamento-ingles-tecnico-ciber.html", content)
        self.assertIn('data-slug="Ingles-Tecnico-Ciber"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)


if __name__ == "__main__":
    unittest.main()
