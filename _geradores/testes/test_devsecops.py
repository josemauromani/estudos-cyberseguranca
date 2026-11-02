#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_devsecops.py
Testes automatizados para o Estudo 22: DevSecOps-e-CI-CD
"""

import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402

SEVERIDADES = ["baixa", "media", "alta", "critica"]


def nivel(sev):
    return SEVERIDADES.index(sev) + 1


def resolvido(d, a, estado):
    return any(c["resolve"] and c["id"] in estado["correcoes"] for c in a["correcoes"])


def excecao_valida(d, a, estado):
    if a["severidade"] == "critica":
        return False
    return any(e["achado"] == a["id"] and e["id"] in estado["excecoes"] and e["validade"] >= d["hoje"]
               for e in d["excecoes"])


def bloqueia(d, a, estado):
    lim = estado["limiares"][a["etapa"]]
    if resolvido(d, a, estado) or lim == "nunca":
        return False
    if nivel(a["severidade"]) < nivel(lim):
        return False
    if estado["baseline"] and not a["novo"]:
        return False
    return not excecao_valida(d, a, estado)


def avaliar(d, estado):
    """Espelho do avaliador do pipeline em JavaScript."""
    for etapa in d["etapas"]:
        bl = [a["id"] for a in d["achados"] if a["etapa"] == etapa["id"] and bloqueia(d, a, estado)]
        if bl:
            return {"resultado": etapa["id"], "bloqueantes": bl, "producao": []}
    prod = [a["id"] for a in d["achados"] if not resolvido(d, a, estado)]
    return {"resultado": "deploy", "bloqueantes": [], "producao": prod}


class TestDevSecOps(unittest.TestCase):
    """Valida a estrutura, o conteúdo, o avaliador do pipeline e a compilação do estudo DevSecOps-e-CI-CD."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "devsecops_e_ci_cd_body.html"
        self.compiled_path = self.root / "DevSecOps-e-CI-CD" / "treinamento-devsecops-e-ci-cd.html"
        self.portal_path = self.root / "index.html"

    def _dados(self):
        body = self.body_path.read_text(encoding="utf-8")
        m = re.search(r'<script type="application/json" id="ds-dados">(.*?)</script>', body, re.S)
        self.assertIsNotNone(m, "Bloco JSON #ds-dados ausente no body")
        return json.loads(m.group(1))

    # ----------------------------------------------------------------- arquivos
    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        termos = [
            "Shift-Left", "SSDLC", "SAST", "DAST", "IAST", "SCA", "SBOM", "CycloneDX", "SPDX", "EPSS", "KEV",
            "CVE-2021-44228", "Gitleaks", "Semgrep", "pip-audit", "Trivy", "OWASP ZAP", "distroless", "digest",
            "USER", "runAsNonRoot", "readOnlyRootFilesystem", "Sigstore", "Cosign", "cosign verify", "quality gate",
            "baseline", "histórico", "revogar", "Estudo 12", "Estudo 13", "Estudo 25",
        ]
        for termo in termos:
            self.assertIn(termo, content, f"Termo obrigatório ausente: {termo}")

    # -------------------------------------------------------------------- dados
    def test_achados_consistentes(self):
        d = self._dados()
        etapas = [e["id"] for e in d["etapas"]]
        self.assertEqual(etapas, ["segredos", "sast", "sca", "imagem", "testes", "dast"])
        ids = [a["id"] for a in d["achados"]]
        self.assertEqual(len(ids), len(set(ids)))
        for a in d["achados"]:
            with self.subTest(achado=a["id"]):
                self.assertIn(a["etapa"], etapas)
                self.assertIn(a["severidade"], SEVERIDADES)
                self.assertTrue(a["titulo"].strip() and a["ferramenta"].strip())
                if a["novo"]:
                    self.assertTrue(any(c["resolve"] for c in a["correcoes"]), "achado novo precisa de correção")
                else:
                    self.assertEqual(a["correcoes"], [], "o legado não é corrigido neste merge request")
                for c in a["correcoes"]:
                    self.assertTrue(c["rotulo"].strip() and c["diff"])
                    self.assertTrue(all(l[:1] in "+- " for l in c["diff"]))
        novos = [a for a in d["achados"] if a["novo"]]
        self.assertEqual({a["severidade"] for a in novos} >= {"critica", "alta", "media"}, True)
        self.assertGreaterEqual(len([a for a in d["achados"] if not a["novo"]]), 5)
        seg = [a for a in d["achados"] if a["etapa"] == "segredos"]
        self.assertEqual(len(seg), 1)
        self.assertEqual(sorted(c["resolve"] for c in seg[0]["correcoes"]), [False, True],
                         "apagar do código não resolve; revogar resolve")
        ids_corr = [c["id"] for a in d["achados"] for c in a["correcoes"]]
        self.assertEqual(len(ids_corr), len(set(ids_corr)))
        self.assertEqual({e["etapa"] for e in d["achados"]} | {"testes"}, set(etapas))

    def test_excecoes(self):
        d = self._dados()
        achados = {a["id"]: a for a in d["achados"]}
        tipos = set()
        for e in d["excecoes"]:
            with self.subTest(excecao=e["id"]):
                self.assertIn(e["achado"], achados)
                self.assertRegex(e["validade"], r"^\d{4}-\d{2}-\d{2}$")
                self.assertTrue(e["justificativa"].strip() and e["aprovador"].strip())
                if achados[e["achado"]]["severidade"] == "critica":
                    tipos.add("critica")
                elif e["validade"] < d["hoje"]:
                    tipos.add("vencida")
                else:
                    tipos.add("valida")
        self.assertEqual(tipos, {"critica", "vencida", "valida"})

    def test_exemplos_do_pipeline(self):
        d = self._dados()
        corr = {c["id"] for a in d["achados"] for c in a["correcoes"]}
        exc = {e["id"] for e in d["excecoes"]}
        resultados = set()
        for ex in d["exemplos"]:
            with self.subTest(exemplo=ex["nome"]):
                est = ex["estado"]
                self.assertEqual(set(est["limiares"]), {"segredos", "sast", "sca", "imagem", "testes", "dast"})
                self.assertTrue(set(est["correcoes"]) <= corr and set(est["excecoes"]) <= exc)
                self.assertEqual(avaliar(d, est), ex["esperado"])
                resultados.add(ex["esperado"]["resultado"])
        self.assertTrue({"deploy", "segredos", "sast", "sca"} <= resultados)

    def test_licoes_do_pipeline(self):
        d = self._dados()
        todas = [c["id"] for a in d["achados"] for c in a["correcoes"] if c["resolve"]]
        apagar = next(c["id"] for a in d["achados"] for c in a["correcoes"] if not c["resolve"])
        base = lambda lim, **kw: dict({"limiares": {e["id"]: lim for e in d["etapas"]}, "baseline": False,  # noqa: E731
                                       "correcoes": [], "excecoes": []}, **kw)
        sem = avaliar(d, base("nunca"))
        self.assertEqual(sem["resultado"], "deploy")
        self.assertTrue(any(a["severidade"] == "critica" for a in d["achados"] if a["id"] in sem["producao"]))
        tudo = avaliar(d, base("baixa", correcoes=todas))
        self.assertNotEqual(tudo["resultado"], "deploy", "o legado trava o limiar baixa")
        self.assertTrue(all(not a["novo"] for a in d["achados"] if a["id"] in tudo["bloqueantes"]))
        self.assertEqual(avaliar(d, base("baixa", correcoes=todas, baseline=True))["resultado"], "deploy")
        so_apagar = [c for c in todas if c not in {c["id"] for a in d["achados"] if a["etapa"] == "segredos" for c in a["correcoes"]}]
        self.assertEqual(avaliar(d, base("alta", correcoes=so_apagar + [apagar]))["resultado"], "segredos")
        critica = next(e for e in d["excecoes"] if next(a for a in d["achados"] if a["id"] == e["achado"])["severidade"] == "critica")
        sem_critica = [c for c in todas if not any(c == x["id"] for a in d["achados"] if a["id"] == critica["achado"] for x in a["correcoes"])]
        r = avaliar(d, base("critica", correcoes=sem_critica, excecoes=[critica["id"]]))
        self.assertIn(critica["achado"], r["bloqueantes"], "exceção não vale para crítica")

    # ---------------------------------------------------------------- compilado
    def test_simulador_estrutura(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        for marcador in ("ds-lab", 'id="ds-dados"', "ds-missoes", "ds-correcoes", "ds-politica", "ds-excecoes",
                         "ds-execucao", "ds-producao", "executarPipelineDevsecops", "aplicarPresetDevsecops",
                         "restaurarDevsecops"):
            self.assertIn(marcador, content, marcador)
        ini = content.index("var DS = JSON.parse")
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
        self.assertIn('initChecklist("devsecops")', content)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn("DevSecOps-e-CI-CD/treinamento-devsecops-e-ci-cd.html", content)
        self.assertIn('data-slug="DevSecOps-e-CI-CD"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)


if __name__ == "__main__":
    unittest.main()
