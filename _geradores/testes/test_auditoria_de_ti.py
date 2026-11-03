#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_auditoria_de_ti.py
Testes automatizados para o Estudo 58: Auditoria-de-TI

O simulador Testador de ITGC guarda num bloco JSON a tabela de amostragem por
frequência do controle (prática de mercado, com a fonte citada) e os controles
gerais de TI de uma empresa fictícia, cada um com domínio, frequência,
população, a amostra sorteada (itens com evidência e exceção), o risco do que
pode dar errado, o controle compensatório (quando existe) e a classificação
esperada. Este teste espelha em Python as regras do motor JavaScript: a
amostra mínima por frequência, limitada à população, e a classificação da
deficiência (efetivo, deficiência, deficiência significativa, fraqueza
material), inclusive o efeito do controle compensatório e as armadilhas
didáticas.
"""

import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402

SLUG = "Auditoria-de-TI"
SECOES = ["introducao", "sox-404", "itgc", "cobit", "ciclo-do-teste", "simulador", "checklist", "quiz", "fatos"]
DOMINIOS = ("acesso", "mudanca", "desenvolvimento", "operacoes")
FREQUENCIAS = ("anual", "trimestral", "mensal", "semanal", "diaria", "multipla")
CLASSES = ("efetivo", "deficiencia", "significativa", "material")
RISCOS = ("baixo", "moderado", "alto")
BASE_POR_RISCO = {"baixo": "deficiencia", "moderado": "significativa", "alto": "material"}

GABARITO = {
    "C1": {"amostra": 2, "excecoes": 1, "classe": "significativa"},
    "C2": {"amostra": 20, "excecoes": 2, "classe": "deficiencia"},
    "C3": {"amostra": 5, "excecoes": 2, "classe": "material"},
    "C4": {"amostra": 1, "excecoes": 0, "classe": "efetivo"},
    "C5": {"amostra": 2, "excecoes": 0, "classe": "efetivo"},
}


# ============================================================ regras
def amostra_minima(tabela, frequencia, populacao):
    """Espelho de amostraMinima: mínimo da tabela para a frequência, nunca acima da população."""
    return min(tabela[frequencia]["min"], populacao)


def classificar_por(risco, excecoes, compensatorio):
    """Espelho de classificarControle: sem exceção, efetivo; com exceção, a base vem do risco;
    o controle compensatório rebaixa um nível, mas a deficiência continua existindo."""
    if excecoes == 0:
        return "efetivo"
    nivel = CLASSES.index(BASE_POR_RISCO[risco])
    if compensatorio:
        nivel = max(1, nivel - 1)
    return CLASSES[nivel]


def classificar(controle):
    excecoes = sum(1 for i in controle["itens"] if i["excecao"])
    return classificar_por(controle["risco"], excecoes, controle["compensatorio"])


def corrigir(d, c, resp):
    """Espelho de corrigirControle: 3 pontos (amostra, exceções, classificação)."""
    minimo = amostra_minima(d["tabela_amostragem"], c["frequencia"], c["populacao"])
    marcadas = set(resp["marcadas"])
    itens = {}
    for i in c["itens"]:
        m = i["id"] in marcadas
        itens[i["id"]] = "acerto" if m == i["excecao"] else ("falso_positivo" if m else "omitiu")
    out = {
        "amostra_ok": minimo <= resp["amostra"] <= c["populacao"],
        "excecoes_ok": all(s == "acerto" for s in itens.values()),
        "itens": itens,
        "classe_ok": resp["classe"] == classificar(c),
        "classe_com_marcas": classificar_por(c["risco"], len(marcadas & {i["id"] for i in c["itens"]}),
                                             c["compensatorio"]),
    }
    out["pontos"] = int(out["amostra_ok"]) + int(out["excecoes_ok"]) + int(out["classe_ok"])
    return out


class TestAuditoriaDeTI(unittest.TestCase):
    """Estrutura, conteúdo, simulador e compilação do estudo 58."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "auditoria_de_ti_body.html"
        self.compiled_path = self.root / SLUG / "treinamento-auditoria-de-ti.html"
        self.portal_path = self.root / "index.html"

    def _body(self):
        return self.body_path.read_text(encoding="utf-8")

    def _compilado(self):
        return self.compiled_path.read_text(encoding="utf-8")

    def _secao(self, sid):
        body = self._body()
        ini = body.index(f'id="{sid}"')
        fim = body.find('<section class="study-section"', ini)
        return body[ini:fim if fim >= 0 else body.index("</article>")]

    def _dados(self):
        m = re.search(r'<script type="application/json" id="aud-dados">(.*?)</script>', self._body(), re.S)
        self.assertIsNotNone(m, "Bloco JSON #aud-dados ausente no body")
        return json.loads(m.group(1))

    def _controle(self, d, cid):
        return next(c for c in d["controles"] if c["id"] == cid)

    def _resp_gabarito(self, c):
        return {"amostra": GABARITO[c["id"]]["amostra"], "classe": GABARITO[c["id"]]["classe"],
                "marcadas": [i["id"] for i in c["itens"] if i["excecao"]]}

    # ------------------------------------------------------------ estrutura
    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_secoes(self):
        body = self._body()
        ids = re.findall(r'<section class="study-section" id="([\w-]+)"', body)
        self.assertEqual(ids, SECOES)
        compilado = self._compilado()
        for n in range(1, len(SECOES) + 1):
            self.assertIn(f"Seção {n} de {len(SECOES)}", compilado)
        self.assertIn('data-slug="auditoria-de-ti"', body)

    def test_coerencia_com_o_catalogo(self):
        content = self._compilado()
        info = ESTUDOS_DADOS[SLUG]
        self.assertIn(info["simulador_nome"], content)
        self.assertIn(info["pergunta_chave"], content)
        self.assertIn(info["subtitulo"], self.portal_path.read_text(encoding="utf-8"))
        self.assertEqual(len(info["fatos"]), 4)
        for fato in info["fatos"]:
            self.assertIn(fato, content, fato)

    def test_metadados(self):
        info = ESTUDOS_DADOS[SLUG]
        self.assertEqual(info["titulo"], "Auditoria de TI: SOX, ITGC e COBIT")
        self.assertEqual(info["subtitulo"],
                         "Controles gerais de TI, teste de desenho e de efetividade, amostragem e deficiências")
        self.assertEqual(info["trilha"], 6)
        self.assertEqual(info["nist"], "Govern")
        self.assertEqual(info["mitre"], "T1078 Valid Accounts / T1098 Account Manipulation")
        self.assertEqual(info["carreiras"][0], "GRC & Auditoria")
        self.assertEqual(len(info["carreiras"]), 2)
        self.assertEqual(info["tempo_minutos"], 45)
        self.assertEqual(info["nivel"], "intermediario")
        self.assertEqual(info["simulador_nome"], "Testador de ITGC")
        self.assertEqual(info["pergunta_chave"],
                         "O controle está no papel. Como você prova que ele funcionou o ano inteiro?")

    # ------------------------------------------------------------ conteúdo
    def test_termos_chave(self):
        body = self._body()
        for termo in ("SOX", "404", "ICFR", "COSO", "PCAOB AS 2201", "ITGC", "ITAC", "IPE", "SOC 1", "SOC 2",
                      "COBIT 2019", "EDM", "APO", "BAI", "DSS", "MEA", "TOD", "TOE", "walkthrough",
                      "fraqueza material", "deficiência significativa", "controle compensatório"):
            self.assertIn(termo, body, termo)

    def test_pontes(self):
        body = self._body()
        antes = body[:body.index('id="simulador"')]
        for ref in ("Estudo 26", "Estudo 04", "Estudo 40", "Estudo 22", "Estudo 52", "Estudo 30", "Estudo 57"):
            self.assertIn(ref, antes, ref)
        fim = self._secao("fatos")
        for ref in ("Estudo 25", "Estudo 26", "Estudo 57", "58 módulos"):
            self.assertIn(ref, fim, ref)

    def test_nao_repete_auditoria_do_sgsi(self):
        body = self._body()
        self.assertNotIn("Fase 2", body, "as fases da certificação ISO são ensinadas no Estudo 26")
        paragrafos = re.findall(r"<p>(.*?)</p>", body, re.S)
        self.assertTrue(any("auditoria do SGSI" in p and "Estudo 26" in p for p in paragrafos),
                        "ao falar da auditoria do SGSI, remeter ao Estudo 26")

    def test_referencias(self):
        fim = self._secao("fatos")
        for ref in ("Sarbanes-Oxley", "AS 2201", "COSO", "COBIT 2019", "ITAF", "Global Internal Audit Standards",
                    "SOC 1"):
            self.assertIn(ref, fim, ref)

    def test_fonte_da_tabela_de_amostragem_no_texto(self):
        """A tabela por frequência é prática de mercado, não norma: o texto diz isso e cita a fonte."""
        d = self._dados()
        teoria = self._secao("ciclo-do-teste")
        self.assertIn("prática de mercado", teoria)
        self.assertIn("Audit Sampling", teoria)
        self.assertIn("Audit Sampling", d["fonte_amostragem"])
        self.assertIn("prática de mercado", d["fonte_amostragem"])
        for freq in FREQUENCIAS:
            self.assertIn(d["tabela_amostragem"][freq]["faixa"], teoria, freq)

    # ---------------------------------------------------------------- dados
    def test_dados_do_simulador(self):
        d = self._dados()
        self.assertIn("fictíci", d["contexto"])
        texto = json.dumps(d, ensure_ascii=False)
        for host in re.findall(r"\b[\w-]+(?:\.[\w-]+)*\.(?:com|net|org|io|br)\b", texto):
            self.fail(f"domínio real nos dados: {host}")
        self.assertEqual(set(d["tabela_amostragem"]), set(FREQUENCIAS))
        for freq, linha in d["tabela_amostragem"].items():
            with self.subTest(frequencia=freq):
                self.assertIsInstance(linha["min"], int)
                self.assertGreater(linha["min"], 0)
                self.assertTrue(linha["faixa"].strip() and linha["rotulo"].strip())
        minimos = [d["tabela_amostragem"][f]["min"] for f in FREQUENCIAS]
        self.assertEqual(minimos, sorted(minimos), "amostra cresce com a frequência")
        self.assertTrue(d["fonte_amostragem"].strip())
        self.assertGreaterEqual(len(d["sistemas"]), 3)
        self.assertIn(len(d["controles"]), range(4, 7))
        self.assertEqual([c["id"] for c in d["controles"]], list(GABARITO))
        self.assertEqual({c["dominio"] for c in d["controles"]}, set(DOMINIOS))
        for c in d["controles"]:
            with self.subTest(controle=c["id"]):
                self.assertIn(c["dominio"], DOMINIOS)
                self.assertIn(c["frequencia"], FREQUENCIAS)
                self.assertIsInstance(c["populacao"], int)
                self.assertGreater(c["populacao"], 0)
                self.assertIn(c["risco"], RISCOS)
                self.assertIn(c["sistema"], d["sistemas"])
                self.assertIn(c["gabarito"], CLASSES)
                self.assertTrue(c["compensatorio"] is None or (isinstance(c["compensatorio"], str)
                                                               and c["compensatorio"].strip()))
                for campo in ("nome", "descricao", "risco_texto", "explicacao"):
                    self.assertTrue(c[campo].strip(), campo)
                ids = [i["id"] for i in c["itens"]]
                self.assertEqual(len(ids), len(set(ids)))
                for i in c["itens"]:
                    self.assertTrue(i["id"].startswith(c["id"] + "-"))
                    self.assertIsInstance(i["excecao"], bool)
                    self.assertTrue(i["evidencia"].strip() and i["motivo"].strip())

    def test_armadilhas_presentes_nos_dados(self):
        d = self._dados()
        armadilhas = {i.get("armadilha") for c in d["controles"] for i in c["itens"] if i["excecao"]}
        self.assertTrue({"aprovacao_apos_implantacao", "aprovador_igual_executor", "acesso_apos_prazo"}
                        <= armadilhas, armadilhas)
        for c in d["controles"]:
            for i in c["itens"]:
                if i["excecao"]:
                    self.assertIn(i.get("armadilha"), {"aprovacao_apos_implantacao", "aprovador_igual_executor",
                                                       "acesso_apos_prazo"}, i["id"])
        # há itens que parecem exceção e não são (dentro do prazo da política)
        self.assertGreaterEqual(sum(1 for c in d["controles"] for i in c["itens"]
                                    if not i["excecao"] and i.get("parece_excecao")), 2)

    # ------------------------------------------------------------ motor
    def test_regras_espelhadas(self):
        d = self._dados()
        tab = d["tabela_amostragem"]
        for c in d["controles"]:
            g = GABARITO[c["id"]]
            with self.subTest(controle=c["id"]):
                minimo = amostra_minima(tab, c["frequencia"], c["populacao"])
                self.assertEqual(minimo, g["amostra"])
                self.assertEqual(len(c["itens"]), minimo, "a amostra sorteada tem o tamanho mínimo")
                self.assertEqual(sum(1 for i in c["itens"] if i["excecao"]), g["excecoes"])
                self.assertEqual(classificar(c), c["gabarito"])
                self.assertEqual(c["gabarito"], g["classe"])
        self.assertGreaterEqual(len({classificar(c) for c in d["controles"]}), 3)
        rebaixados = [c["id"] for c in d["controles"]
                      if c["compensatorio"] and classificar(dict(c, compensatorio=None)) != classificar(c)]
        self.assertGreaterEqual(len(rebaixados), 1, "ao menos um compensatório rebaixa a classificação")

    def test_amostra_limitada_a_populacao(self):
        tab = self._dados()["tabela_amostragem"]
        self.assertEqual(amostra_minima(tab, "diaria", 250), tab["diaria"]["min"])
        self.assertEqual(amostra_minima(tab, "semanal", 3), 3)
        self.assertEqual(amostra_minima(tab, "anual", 1), 1)

    def test_classificacao(self):
        self.assertEqual(classificar_por("alto", 0, "x"), "efetivo")
        self.assertEqual(classificar_por("baixo", 1, None), "deficiencia")
        self.assertEqual(classificar_por("baixo", 3, "x"), "deficiencia", "compensatório não apaga a deficiência")
        self.assertEqual(classificar_por("moderado", 1, None), "significativa")
        self.assertEqual(classificar_por("moderado", 1, "x"), "deficiencia")
        self.assertEqual(classificar_por("alto", 2, None), "material")
        self.assertEqual(classificar_por("alto", 2, "x"), "significativa")

    def test_gabarito_completo_vale_tres_pontos(self):
        d = self._dados()
        total = 0
        for c in d["controles"]:
            with self.subTest(controle=c["id"]):
                res = corrigir(d, c, self._resp_gabarito(c))
                self.assertEqual(res["pontos"], 3)
                self.assertEqual(res["classe_com_marcas"], c["gabarito"])
                total += res["pontos"]
        self.assertEqual(total, 3 * len(d["controles"]))

    def test_amostra_pequena_e_excecao_omitida(self):
        d = self._dados()
        c2 = self._controle(d, "C2")
        resp = self._resp_gabarito(c2)
        resp["amostra"] = 5
        resp["marcadas"] = resp["marcadas"][:1]
        res = corrigir(d, c2, resp)
        self.assertFalse(res["amostra_ok"], "5 itens para controle diário é amostra pequena demais")
        self.assertEqual(list(res["itens"].values()).count("omitiu"), 1)
        self.assertEqual(res["pontos"], 1)

    def test_falso_positivo_dentro_do_prazo(self):
        d = self._dados()
        for c in d["controles"]:
            for i in c["itens"]:
                if i.get("parece_excecao"):
                    resp = self._resp_gabarito(c)
                    resp["marcadas"] = resp["marcadas"] + [i["id"]]
                    res = corrigir(d, c, resp)
                    self.assertEqual(res["itens"][i["id"]], "falso_positivo")
                    self.assertFalse(res["excecoes_ok"])

    def test_material_sem_compensatorio_na_gestao_de_mudancas(self):
        d = self._dados()
        c3 = self._controle(d, "C3")
        self.assertEqual(c3["dominio"], "mudanca")
        self.assertIsNone(c3["compensatorio"])
        self.assertEqual(classificar(c3), "material")
        c2 = self._controle(d, "C2")
        self.assertIsNotNone(c2["compensatorio"])
        self.assertEqual(classificar(dict(c2, compensatorio=None)), "significativa")

    # ------------------------------------------------------------ simulador
    def test_simulador_sem_apis_inseguras(self):
        content = self._compilado()
        self.assertIn('id="aud-dados"', content)
        ini = content.index("JSON.parse(document.getElementById(\"aud-dados\")")
        motor = content[ini:content.index("</script>", ini)]
        for proibido in ("innerHTML", "outerHTML", "eval(", "new Function", "fetch(", "XMLHttpRequest", "WebSocket",
                         "document.write", "localStorage"):
            self.assertNotIn(proibido, motor, proibido)
        for marcador in ("aud-lab", "aud-controles", "aud-controle", "aud-placar", "amostraMinima",
                         "classificarControle", "corrigirControle", "responderControleAud"):
            self.assertIn(marcador, content, marcador)
        self.assertIn("aria-label", motor)
        self.assertIn("textContent", motor)
        self.assertIn('"radio"', motor)
        self.assertIn('"checkbox"', motor)
        self.assertIn('"number"', motor)

    def test_componentes_pedagogicos(self):
        body = self._body()
        content = self._compilado()
        self.assertIn('<pre class="mermaid"', body)
        self.assertIn('class="diagram-svg-wrap', content)
        self.assertNotIn('<pre class="mermaid"', content)
        self.assertIn('class="callout', content)
        self.assertIn('class="facts-grid', content)
        self.assertIn(content.count('class="checklist-item"'), range(4, 9))
        self.assertGreaterEqual(content.count('class="quiz-item"'), 6)
        self.assertIn('initChecklist("auditoria-de-ti")', content)

    def test_portal_mostra_58_compilados(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn(f"{SLUG}/treinamento-auditoria-de-ti.html", content)
        self.assertIn(f'data-slug="{SLUG}"', content)
        self.assertIn("58 / 58", content)


if __name__ == "__main__":
    unittest.main()
