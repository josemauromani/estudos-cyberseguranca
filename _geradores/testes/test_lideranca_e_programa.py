#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_lideranca_e_programa.py
Testes automatizados para o Estudo 59: Lideranca-e-Programa-de-Seguranca

O simulador Do SIEM ao Conselho guarda num bloco JSON 12 indicadores fictícios
de uma empresa, cada um com o gabarito (KRI para o conselho, KPI operacional ou
métrica de vaidade), a marca de KRI essencial e a explicação. O aluno
classifica cada indicador, e o painel do conselho aceita no máximo
`limite_painel` KRIs. Este teste espelha em Python as regras do motor
JavaScript: a contagem de acertos, os KRIs que foram ao painel, os KRIs
essenciais ausentes, a métrica de vaidade marcada como KRI e a recusa do KRI
acima do limite (o motor recusa com aviso; não corta em silêncio).
"""

import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402
from navegador import CHROME, executar  # noqa: E402

SLUG = "Lideranca-e-Programa-de-Seguranca"
SECOES = ["introducao", "governanca", "risco-de-negocio", "metricas-conselho", "orcamento", "simulador",
          "checklist", "quiz", "fatos"]
CLASSES = ("kri", "kpi", "vaidade")
AVISO_LIMITE = "O painel aceita no máximo 6 KRIs"


# ============================================================ regras
def avaliar_painel(dados, escolhas):
    """Espelho de avaliarPainel: escolhas é {id do indicador: classe}; indicador sem escolha conta como erro.

    O painel do conselho aceita no máximo limite_painel KRIs: acima disso o motor recusa (aqui, ValueError)."""
    for ind_id, classe in escolhas.items():
        if classe not in CLASSES:
            raise ValueError(f"classe inválida para {ind_id}: {classe}")
    indicadores = dados["indicadores"]
    kri = [i["id"] for i in indicadores if escolhas.get(i["id"]) == "kri"]
    if len(kri) > dados["limite_painel"]:
        raise ValueError(f"o painel aceita no máximo {dados['limite_painel']} KRIs")
    return {
        "acertos": sum(1 for i in indicadores if escolhas.get(i["id"]) == i["gabarito"]),
        "kri_no_painel": kri,
        "essenciais_ausentes": [i["id"] for i in indicadores if i["essencial"] and escolhas.get(i["id"]) != "kri"],
        "vaidade_no_painel": [i["id"] for i in indicadores if i["gabarito"] == "vaidade"
                              and escolhas.get(i["id"]) == "kri"],
    }


class TestLiderancaEPrograma(unittest.TestCase):
    """Estrutura, conteúdo, simulador e compilação do estudo 59."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "lideranca_e_programa_de_seguranca_body.html"
        self.compiled_path = self.root / SLUG / "treinamento-lideranca-e-programa-de-seguranca.html"
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
        m = re.search(r'<script type="application/json" id="lid-dados">(.*?)</script>', self._body(), re.S)
        self.assertIsNotNone(m, "Bloco JSON #lid-dados ausente no body")
        return json.loads(m.group(1))

    def _motor(self):
        content = self._compilado()
        ini = content.index('JSON.parse(document.getElementById("lid-dados")')
        return content[ini:content.index("</script>", ini)]

    def _gabarito(self, d):
        return {i["id"]: i["gabarito"] for i in d["indicadores"]}

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
        self.assertIn('data-slug="lideranca-e-programa-de-seguranca"', body)

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
        self.assertEqual(info["titulo"], "Liderança e Programa de Segurança: o Papel do CISO")
        self.assertEqual(info["subtitulo"],
                         "Linha de reporte, governança, KPI e KRI, relato ao conselho e orçamento de segurança")
        self.assertEqual(info["trilha"], 14)
        self.assertEqual(info["nist"], "Govern")
        self.assertEqual(info["mitre"], "N/A (liderança e governança)")
        self.assertEqual(info["carreiras"], ["GRC & Auditoria", "Analista de Segurança da Informação"])
        self.assertEqual(info["tempo_minutos"], 45)
        self.assertEqual(info["nivel"], "intermediario")
        self.assertEqual(info["simulador_nome"], "Do SIEM ao Conselho")
        self.assertEqual(info["pergunta_chave"],
                         "O SIEM gerou 40 mil alertas no trimestre. O que disso o conselho precisa saber?")
        self.assertEqual(info["fatos"], ["Modelo das três linhas (IIA, 2020)", "Função Govern do NIST CSF 2.0",
                                         "KPI, KRI e métrica de vaidade", "Business case e limites do ROSI"])

    # ------------------------------------------------------------ conteúdo
    def test_termos_chave(self):
        body = self._body()
        for termo in ("três linhas", "IIA", "independência", "CISO", "CTO", "DPO", "encarregado", "NIST CSF 2.0",
                      "GV.OC", "GV.RM", "GV.RR", "GV.PO", "GV.OV", "GV.SC", "RACI", "apetite", "tolerância", "KPI",
                      "KRI", "métrica de vaidade", "Capex", "Opex", "business case", "ROSI", "Res. CMN 4.893/2021"):
            self.assertIn(termo, body, termo)

    def test_pontes(self):
        body = self._body()
        antes = body[:body.index('id="simulador"')]
        for ref in ("Estudo 25", "Estudo 26", "Estudo 54", "Estudo 58"):
            self.assertIn(ref, antes, ref)
        fim = self._secao("fatos")
        for ref in ("Trilha 14", "Estudo 60", "Estudo 33"):
            self.assertIn(ref, fim, ref)

    def test_nao_repete_calculo_de_risco(self):
        body = self._body()
        for proibido in ("ALE =", "SLE ="):
            self.assertNotIn(proibido, body, "o cálculo de ALE e SLE é ensinado no Estudo 25")
        self.assertIn("Estudo 25", self._secao("risco-de-negocio"))

    def test_referencias(self):
        fim = self._secao("fatos")
        for ref in ("Three Lines Model", "NIST CSF 2.0", "CSWP 29", "Res. CMN 4.893/2021"):
            self.assertIn(ref, fim, ref)

    def test_sem_marcas_de_perfis(self):
        body = self._body()
        # marcas escritas em partes para que a varredura de termos proibidos no repositório não as encontre
        for proibido in ("F" "63", "A" "93"):
            self.assertNotIn(proibido, body, proibido)
        self.assertNotIn("primeiro programa", body.lower())

    # ---------------------------------------------------------------- dados
    def test_dados_do_simulador(self):
        d = self._dados()
        self.assertIn("fictíci", d["contexto"])
        texto = json.dumps(d, ensure_ascii=False)
        for host in re.findall(r"\b[\w-]+(?:\.[\w-]+)*\.(?:com|net|org|io|br)\b", texto):
            self.fail(f"domínio real nos dados: {host}")
        self.assertEqual(d["limite_painel"], 6)
        inds = d["indicadores"]
        self.assertEqual(len(inds), 12)
        ids = [i["id"] for i in inds]
        self.assertEqual(len(ids), len(set(ids)))
        for i in inds:
            with self.subTest(indicador=i.get("id")):
                for campo in ("id", "nome", "valor", "explicacao"):
                    self.assertIsInstance(i[campo], str)
                    self.assertTrue(i[campo].strip(), campo)
                self.assertIn(i["gabarito"], CLASSES)
                self.assertIsInstance(i["essencial"], bool)
                if i["essencial"]:
                    self.assertEqual(i["gabarito"], "kri", "só KRI pode ser essencial")
        por_classe = {c: sum(1 for i in inds if i["gabarito"] == c) for c in CLASSES}
        self.assertGreaterEqual(por_classe["kri"], 4)
        self.assertLessEqual(por_classe["kri"], d["limite_painel"], "o gabarito cabe no painel")
        self.assertGreaterEqual(por_classe["kpi"], 3)
        self.assertGreaterEqual(por_classe["vaidade"], 3)
        self.assertIn(sum(1 for i in inds if i["essencial"]), range(3, 6))
        nomes = " ".join(i["nome"] for i in inds)
        for indicador in ("alertas", "MTTD", "MTTR", "MFA", "fornecedores críticos", "phishing", "restauração"):
            self.assertIn(indicador, nomes, indicador)

    # ------------------------------------------------------------ motor
    def test_regras_espelhadas(self):
        d = self._dados()
        gab = self._gabarito(d)
        res = avaliar_painel(d, gab)
        self.assertEqual(set(res), {"acertos", "kri_no_painel", "essenciais_ausentes", "vaidade_no_painel"})
        self.assertIsInstance(res["acertos"], int)
        self.assertEqual(res["acertos"], 12)
        self.assertEqual(res["kri_no_painel"], [k for k, v in gab.items() if v == "kri"])
        self.assertEqual(res["essenciais_ausentes"], [])
        self.assertEqual(res["vaidade_no_painel"], [])

        essencial = next(i["id"] for i in d["indicadores"] if i["essencial"])
        res = avaliar_painel(d, dict(gab, **{essencial: "kpi"}))
        self.assertEqual(res["essenciais_ausentes"], [essencial])
        self.assertNotIn(essencial, res["kri_no_painel"])
        self.assertEqual(res["acertos"], 11)

        vaidade = next(i["id"] for i in d["indicadores"] if i["gabarito"] == "vaidade")
        escolhas = dict(gab, **{vaidade: "kri"})
        erros = 1
        if sum(1 for v in gab.values() if v == "kri") == d["limite_painel"]:  # abre vaga para não estourar o limite
            nao_essencial = next(i["id"] for i in d["indicadores"] if i["gabarito"] == "kri" and not i["essencial"])
            escolhas[nao_essencial] = "kpi"
            erros = 2
        res = avaliar_painel(d, escolhas)
        self.assertEqual(res["vaidade_no_painel"], [vaidade])
        self.assertIn(vaidade, res["kri_no_painel"])
        self.assertEqual(res["acertos"], 12 - erros)

        self.assertEqual(avaliar_painel(d, {})["acertos"], 0, "indicador sem classificação conta como erro")

    def test_limite_de_kris(self):
        d = self._dados()
        motor = self._motor()
        self.assertIn(AVISO_LIMITE, motor)
        self.assertIn(str(d["limite_painel"]), AVISO_LIMITE)
        ini = motor.index("window.classificar = function(indicadorId, classe)")
        corpo = motor[ini:motor.index("\n    };", ini)]
        checagem = re.search(r"contarKris\(\)\s*>=\s*D\.limite_painel", corpo)
        self.assertIsNotNone(checagem, "classificar compara com limite_painel")
        aceite = corpo.index("estado.escolhas[indicadorId] = classe")
        self.assertLess(checagem.start(), aceite, "a comparação vem antes de aceitar a escolha")
        self.assertIn("return false", corpo[checagem.start():aceite], "o sétimo KRI é recusado")
        self.assertIn("window.avaliarPainel = function()", motor)

        gab = self._gabarito(d)
        sete = dict(gab)
        for i in d["indicadores"]:
            if sum(1 for v in sete.values() if v == "kri") >= d["limite_painel"] + 1:
                break
            sete[i["id"]] = "kri"
        self.assertEqual(sum(1 for v in sete.values() if v == "kri"), d["limite_painel"] + 1)
        with self.assertRaises(ValueError):
            avaliar_painel(d, sete)
        with self.assertRaises(ValueError):
            avaliar_painel(d, dict(gab, **{d["indicadores"][0]["id"]: "conselho"}))

    # ------------------------------------------------------------ simulador
    def test_simulador_sem_apis_inseguras(self):
        content = self._compilado()
        self.assertIn('id="lid-dados"', content)
        motor = self._motor()
        for proibido in ("innerHTML", "outerHTML", "eval(", "new Function", "fetch(", "XMLHttpRequest", "WebSocket",
                         "document.write", "localStorage"):
            self.assertNotIn(proibido, motor, proibido)
        for marcador in ("lid-lab", "lid-indicadores", "lid-painel", "lid-aviso", "lid-resultado"):
            self.assertIn(marcador, content, marcador)
        self.assertIn("aria-label", motor)
        self.assertIn("aria-pressed", motor)
        self.assertIn("textContent", motor)
        self.assertIn("createElement", motor)

    def test_foco_restaurado_no_codigo(self):
        """Cada clique recria os cartões e o painel: o motor guarda a chave do botão e devolve o foco a ele."""
        motor = self._motor()
        self.assertIn('estado.foco = i.id + ":" + c', motor)
        self.assertIn('registrarAlvo(i.id + ":" + c, b)', motor)
        ini = motor.index("function renderTudo()")
        render = motor[ini:motor.index("\n    }", ini)]
        self.assertLess(render.index("renderIndicadores()"), render.index("restaurarFoco()"))
        self.assertLess(render.index("renderPainel()"), render.index("restaurarFoco()"))
        ini = motor.index("function restaurarFoco()")
        self.assertIn(".focus()", motor[ini:motor.index("\n    }", ini)])

    @unittest.skipUnless(CHROME, "Chrome ausente")
    def test_foco_do_teclado_sobrevive_a_classificacao(self):
        """No navegador: classificar e tirar do painel não jogam o foco para o <body>."""
        r = executar(self._compilado(), r"""
          const card = (n) => document.querySelectorAll('#lid-indicadores [role=group]')[n];
          const ativo = () => document.activeElement;
          const out = {};
          let b = card(2).querySelectorAll('button')[0];        // I03 como KRI
          const rotulo = b.getAttribute('aria-label');
          b.focus(); b.click();
          out.kri = {label: ativo().getAttribute('aria-label'), novo: ativo() !== b,
                     pressed: ativo().getAttribute('aria-pressed')};
          b = card(4).querySelectorAll('button')[0]; b.focus(); b.click();   // I05 como KRI
          b = card(4).querySelectorAll('button')[1]; b.focus(); b.click();   // I05 vira KPI
          out.kpi = ativo().getAttribute('aria-label');
          b = card(4).querySelectorAll('button')[0]; b.focus(); b.click();   // I05 volta a KRI
          let tirar = document.querySelectorAll('#lid-painel button');
          tirar[0].focus(); tirar[0].click();
          out.tirar1 = {noPainel: document.getElementById('lid-painel').contains(ativo()),
                        tag: ativo().tagName, restantes: document.querySelectorAll('#lid-painel button').length};
          tirar = document.querySelectorAll('#lid-painel button');
          tirar[0].focus(); tirar[0].click();
          out.tirar2 = {noPainel: document.getElementById('lid-painel').contains(ativo()), tag: ativo().tagName};
          out.rotulo = rotulo;
          __fim(out);
        """)
        self.assertEqual(r["erros"], [])
        s = r["saida"]
        self.assertEqual(s["kri"]["label"], s["rotulo"], "o foco volta ao botão clicado, recriado")
        self.assertTrue(s["kri"]["novo"])
        self.assertEqual(s["kri"]["pressed"], "true")
        self.assertIn("como KPI operacional", s["kpi"])
        self.assertEqual(s["tirar1"], {"noPainel": True, "tag": "BUTTON", "restantes": 1})
        self.assertTrue(s["tirar2"]["noPainel"], "painel vazio: o foco fica no título do painel")
        self.assertEqual(s["tirar2"]["tag"], "H4")

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
        self.assertIn('initChecklist("lideranca-e-programa-de-seguranca")', content)

    def test_portal_mostra_o_59(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn(f"{SLUG}/treinamento-lideranca-e-programa-de-seguranca.html", content)
        self.assertIn(f'data-slug="{SLUG}"', content)


if __name__ == "__main__":
    unittest.main()
