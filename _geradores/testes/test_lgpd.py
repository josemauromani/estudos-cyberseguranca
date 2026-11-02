#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_lgpd.py
Testes automatizados para o Estudo 27: LGPD-e-Privacidade
"""

import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402

SALV_ALTO_RISCO = ["criptografia", "controle_acesso", "registro_acesso", "minimizacao"]


def sensivel(f):
    return any(c.startswith("sensivel_") for c in f["categorias"])


def vulneravel(f):
    return any(c in ("crianca_adolescente", "idoso") for c in f["categorias"])


def avaliar(d, f):
    """Espelho do avaliador em JavaScript."""
    base, sens = f["base"], sensivel(f)
    if base == "politicas_publicas":
        st, mot = "invalida", "politicas"
    elif sens and base in ("legitimo_interesse", "protecao_credito", "execucao_contrato"):
        st, mot = "invalida", "art11_sem_base"
    elif not sens and base == "prevencao_fraude":
        st, mot = "invalida", "so_sensiveis"
    elif sens and base == "consentimento":
        st, mot = "alerta", "consentimento_destacado"
    elif base == "tutela_saude":
        st, mot = "alerta", "saude_restrita"
    elif base == "pesquisa":
        st, mot = "alerta", "orgao_pesquisa"
    elif base == "legitimo_interesse" and not f["lia"]:
        st, mot = "alerta", "lia"
    elif base in ("consentimento", "consentimento_especifico") and "funcionarios" in f["titulares"]:
        st, mot = "alerta", "consentimento_emprego"
    else:
        st, mot = "ok", "ok"
    gerais = [c for c in ("larga_escala", "afeta_direitos") if f[c]]
    especificos = [c for c in ("tecnologia_emergente", "vigilancia_publica", "decisao_automatizada") if f[c]]
    if sens or vulneravel(f):
        especificos.append("sensiveis_ou_vulneraveis")
    alto = bool(gerais and especificos)
    exigidas = (list(SALV_ALTO_RISCO) if alto else []) + (["contrato_operador"] if f["operador"] else []) \
        + (["clausulas_padrao"] if f["transferencia"] else []) + ["retencao_definida"]
    faltam = [s for s in exigidas if s not in f["salvaguardas"]]
    impacto = 3 if sens or vulneravel(f) else 2 if any(c in ("identificacao", "financeiro", "localizacao") for c in f["categorias"]) else 1
    prob = min(3, 1 + (1 if f["operador"] or f["terceiros"] or f["transferencia"] else 0) + (1 if faltam else 0))
    nivel = "alto" if impacto * prob >= 6 else "medio" if impacto * prob >= 3 else "baixo"
    direitos = []
    if base in ("consentimento", "consentimento_especifico"):
        direitos += ["art18_vi", "art18_ix"]
    if f["operador"] or f["terceiros"]:
        direitos.append("art18_vii")
    if f["decisao_automatizada"]:
        direitos.append("art20")
    return {"base": st, "motivo": mot, "alto_risco": alto, "criterios": gerais + especificos, "faltam": faltam,
            "impacto": impacto, "probabilidade": prob, "nivel": nivel, "ripd": alto or nivel == "alto", "direitos": direitos}


class TestLgpd(unittest.TestCase):
    """Valida a estrutura, o conteúdo jurídico, o avaliador de fluxos e a compilação do estudo 27."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "lgpd_e_privacidade_body.html"
        self.compiled_path = self.root / "LGPD-e-Privacidade" / "treinamento-lgpd-e-privacidade.html"
        self.portal_path = self.root / "index.html"

    def _dados(self):
        body = self.body_path.read_text(encoding="utf-8")
        m = re.search(r'<script type="application/json" id="lg-dados">(.*?)</script>', body, re.S)
        self.assertIsNotNone(m, "Bloco JSON #lg-dados ausente no body")
        return json.loads(m.group(1))

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        termos = [
            "Lei nº 13.709/2018", "dado pessoal", "dado pessoal sensível", "anonimizado", "controlador", "operador",
            "encarregado", "finalidade", "adequação", "necessidade", "art. 7º", "art. 11", "legítimo interesse",
            "teste de balanceamento", "art. 18", "art. 20", "art. 37", "art. 38", "RIPD", "art. 48", "art. 52",
            "Resolução CD/ANPD nº 2/2022", "Resolução CD/ANPD nº 15/2024", "3 dias úteis", "Resolução CD/ANPD nº 19/2024",
            "cláusulas-padrão contratuais", "2% do faturamento", "R$ 50 milhões", "Estudo 43", "Estudo 29",
        ]
        for termo in termos:
            self.assertIn(termo, content, f"Termo obrigatório ausente: {termo}")

    def test_bases_legais(self):
        d = self._dados()
        self.assertEqual(len(d["bases_art7"]), 10)
        self.assertEqual(len(d["bases_art11"]), 8)
        a11 = {b["id"] for b in d["bases_art11"]}
        for proibida in ("legitimo_interesse", "protecao_credito", "execucao_contrato"):
            self.assertNotIn(proibida, a11)
        self.assertIn("prevencao_fraude", a11)
        self.assertIn("consentimento_especifico", a11)
        for b in d["bases_art7"] + d["bases_art11"]:
            self.assertRegex(b["artigo"], r"^art\. (7º|11), ")

    def test_estado_inicial_e_corrigido(self):
        d = self._dados()
        inval = 0
        for f in d["fluxos"]:
            with self.subTest(fluxo=f["id"]):
                r = avaliar(d, f)
                self.assertEqual({k: r[k] for k in f["esperado"]}, f["esperado"])
                inval += r["base"] == "invalida"
                g = dict(f, **f["correcao"])
                rc = avaliar(d, g)
                self.assertNotEqual(rc["base"], "invalida")
                self.assertEqual(rc["faltam"], [], f["id"])
                self.assertNotEqual(rc["motivo"], "lia")
        self.assertGreaterEqual(inval, 1)
        self.assertTrue(any(avaliar(d, f)["alto_risco"] for f in d["fluxos"]))
        self.assertTrue(any(not avaliar(d, f)["alto_risco"] for f in d["fluxos"]))

    def test_regras_juridicas(self):
        d = self._dados()
        base = {"categorias": ["identificacao"], "titulares": ["clientes"], "base": "legitimo_interesse", "lia": True,
                "larga_escala": False, "afeta_direitos": False, "tecnologia_emergente": False, "vigilancia_publica": False,
                "decisao_automatizada": False, "operador": False, "terceiros": False, "transferencia": False, "salvaguardas": ["retencao_definida"]}
        f = lambda **kw: dict(base, **kw)  # noqa: E731
        self.assertEqual(avaliar(d, f())["base"], "ok")
        self.assertEqual(avaliar(d, f(categorias=["sensivel_saude"]))["base"], "invalida")
        self.assertEqual(avaliar(d, f(categorias=["sensivel_saude"], base="obrigacao_legal"))["base"], "ok")
        self.assertEqual(avaliar(d, f(base="prevencao_fraude"))["base"], "invalida")
        self.assertEqual(avaliar(d, f(lia=False))["motivo"], "lia")
        self.assertFalse(avaliar(d, f(larga_escala=True))["alto_risco"], "só critério geral não basta")
        self.assertFalse(avaliar(d, f(decisao_automatizada=True))["alto_risco"], "só critério específico não basta")
        self.assertTrue(avaliar(d, f(larga_escala=True, decisao_automatizada=True))["alto_risco"])
        self.assertTrue(avaliar(d, f(afeta_direitos=True, categorias=["idoso"]))["alto_risco"])
        self.assertIn("art20", avaliar(d, f(decisao_automatizada=True))["direitos"])

    def test_simulador_estrutura(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        for marcador in ("lg-lab", 'id="lg-dados"', "lg-missoes", "lg-fluxos", "lg-editor", "lg-matriz", "lg-ripd",
                         "editarFluxoLgpd", "salvarFluxoLgpd", "novoFluxoLgpd", "gerarRipdLgpd", "restaurarLgpd"):
            self.assertIn(marcador, content, marcador)
        ini = content.index("var LG = JSON.parse")
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
        self.assertIn('initChecklist("lgpd")', content)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn("LGPD-e-Privacidade/treinamento-lgpd-e-privacidade.html", content)
        self.assertIn('data-slug="LGPD-e-Privacidade"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)


if __name__ == "__main__":
    unittest.main()
