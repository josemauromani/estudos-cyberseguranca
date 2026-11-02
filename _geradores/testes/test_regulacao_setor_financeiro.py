#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_regulacao_setor_financeiro.py
Testes automatizados para o Estudo 54: Regulacao-Setor-Financeiro

O simulador Verificador de Aderência guarda num bloco JSON as entidades da
fase 1 (quem se sujeita à Res. CMN 4.893 e quem se sujeita à Res. BCB 85) e
os requisitos da fase 2, cada um com o trecho da política de segurança
cibernética ou do contrato de nuvem da Ipê Pay (instituição de pagamento
fictícia, parceira da Ipê Store), o gabarito (atendido, parcial ou ausente),
a criticidade e a ação corretiva. Este teste espelha em Python as regras do
motor JavaScript: conferência da sujeição, classificação de cada marcação do
aluno (certa, otimista, pessimista ou sem marcação), índice de aderência e
plano de ação priorizado a partir das marcações.
"""

import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402

SLUG = "Regulacao-Setor-Financeiro"
STATUS = ("atendido", "parcial", "ausente")
NIVEL = {"atendido": 2, "parcial": 1, "ausente": 0}
FATOR = {"ausente": 2, "parcial": 1}
TEMAS = ("politica", "incidentes", "nuvem", "dez2025")
NORMAS = ("cmn4893", "bcb85", "nenhuma")

# id → (tema, gabarito, criticidade), na ordem em que aparecem no simulador
GABARITO = {
    "pol_aprovacao": ("politica", "parcial", 2),
    "pol_controles": ("politica", "parcial", 2),
    "pol_classificacao": ("politica", "atendido", 1),
    "pol_capacitacao": ("politica", "atendido", 1),
    "inc_plano": ("incidentes", "ausente", 3),
    "inc_diretor": ("incidentes", "ausente", 2),
    "inc_comunicacao": ("incidentes", "ausente", 3),
    "rel_anual": ("incidentes", "parcial", 2),
    "nuv_comunicacao": ("nuvem", "ausente", 2),
    "nuv_diligencia": ("nuvem", "atendido", 2),
    "nuv_localizacao": ("nuvem", "ausente", 2),
    "nuv_acesso_saida": ("nuvem", "parcial", 2),
    "nuv_responsabilidade": ("nuvem", "ausente", 3),
    "dez_controles": ("dez2025", "parcial", 2),
    "dez_pentest": ("dez2025", "ausente", 3),
    "dez_pix": ("dez2025", "ausente", 3),
    "dez_darkweb": ("dez2025", "atendido", 1),
}

SUJEICAO = {
    "banco_multiplo": "cmn4893",
    "cooperativa": "cmn4893",
    "financeira": "cmn4893",
    "ipe_pay": "bcb85",
    "corretora_cambio": "bcb85",
    "dtvm": "bcb85",
    "ipe_store": "nenhuma",
}

PLANO_GABARITO = [
    ("inc_plano", "P1"), ("inc_comunicacao", "P1"), ("nuv_responsabilidade", "P1"), ("dez_pentest", "P1"),
    ("dez_pix", "P1"),
    ("inc_diretor", "P2"), ("nuv_comunicacao", "P2"), ("nuv_localizacao", "P2"),
    ("pol_aprovacao", "P3"), ("pol_controles", "P3"), ("rel_anual", "P3"), ("nuv_acesso_saida", "P3"),
    ("dez_controles", "P3"),
]


# ============================================================ regras
def conferir_sujeicao(d, respostas):
    """Espelho de conferirSujeicao: compara a norma escolhida para cada entidade com o gabarito."""
    erros = [e["id"] for e in d["entidades"] if respostas.get(e["id"]) != e["norma"]]
    return {"acertos": len(d["entidades"]) - len(erros), "total": len(d["entidades"]), "erros": erros}


def avaliar_aderencia(d, marcacoes):
    """Espelho de avaliarAderencia: classifica cada marcação do aluno contra o gabarito."""
    itens, cont = [], {"certo": 0, "otimista": 0, "pessimista": 0, "sem_marcacao": 0}
    for r in d["requisitos"]:
        m = marcacoes.get(r["id"])
        if m not in NIVEL:
            res = "sem_marcacao"
        elif NIVEL[m] > NIVEL[r["gabarito"]]:
            res = "otimista"
        elif NIVEL[m] < NIVEL[r["gabarito"]]:
            res = "pessimista"
        else:
            res = "certo"
        cont[res] += 1
        itens.append({"id": r["id"], "marcado": m if m in NIVEL else None, "gabarito": r["gabarito"],
                      "resultado": res})
    return {"itens": itens, **cont}


def indice_aderencia(d, marcacoes):
    """Espelho de indiceAderencia: atendido 2, parcial 1, ausente 0, sobre os requisitos marcados (inteiro)."""
    marcados = [marcacoes[r["id"]] for r in d["requisitos"] if marcacoes.get(r["id"]) in NIVEL]
    if not marcados:
        return None
    soma, den = sum(NIVEL[m] for m in marcados), len(marcados)
    return (100 * soma + den) // (2 * den)


def prioridade(pontos):
    return "P1" if pontos >= 6 else ("P2" if pontos >= 3 else "P3")


def plano_de_acao(d, marcacoes):
    """Espelho de planoDeAcao: lacunas marcadas pelo aluno, pontuadas por criticidade × fator do status."""
    plano = []
    for k, r in enumerate(d["requisitos"]):
        m = marcacoes.get(r["id"])
        if m not in FATOR:
            continue
        pontos = r["criticidade"] * FATOR[m]
        plano.append({"id": r["id"], "status": m, "pontos": pontos, "prioridade": prioridade(pontos),
                      "criticidade": r["criticidade"], "ordem": k})
    plano.sort(key=lambda p: (-p["pontos"], -p["criticidade"], p["ordem"]))
    return plano


class TestRegulacaoSetorFinanceiro(unittest.TestCase):
    """Estrutura, conteúdo, simulador e compilação do estudo 54."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "regulacao_setor_financeiro_body.html"
        self.compiled_path = self.root / SLUG / "treinamento-regulacao-setor-financeiro.html"
        self.portal_path = self.root / "index.html"

    def _body(self):
        return self.body_path.read_text(encoding="utf-8")

    def _dados(self):
        m = re.search(r'<script type="application/json" id="rsf-dados">(.*?)</script>', self._body(), re.S)
        self.assertIsNotNone(m, "Bloco JSON #rsf-dados ausente no body")
        return json.loads(m.group(1))

    def _gabarito(self, d):
        return {r["id"]: r["gabarito"] for r in d["requisitos"]}

    # ------------------------------------------------------------ estrutura
    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_seis_secoes_obrigatorias(self):
        body = self._body()
        ids = re.findall(r'<section class="study-section" id="([\w-]+)"', body)
        self.assertEqual(len(ids), 6, ids)
        self.assertEqual(ids[2:], ["simulador", "checklist", "quiz", "fatos"])
        for n in range(1, 7):
            self.assertIn(f"Seção 0{n}", body)
        self.assertIn('data-slug="regulacao-setor-financeiro"', body)

    def test_coerencia_com_o_catalogo(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        info = ESTUDOS_DADOS[SLUG]
        self.assertIn(info["simulador_nome"], content)
        self.assertIn(info["pergunta_chave"], content)
        for fato in info["fatos"]:
            self.assertIn(fato, content, fato)

    def test_pontes_com_os_estudos_vizinhos(self):
        body = self._body()
        intro = body[:body.index('id="simulador"')]
        for ref in ("Estudo 25", "Estudo 26", "Estudo 31", "Estudo 43", "Estudo 53"):
            self.assertIn(ref, intro, ref)
        fim = body[body.index('id="fatos"'):body.index("</article>")]
        for ref in ("Trilha 13", "Estudo 55", "Estudo 57"):
            self.assertIn(ref, fim, ref)

    # ------------------------------------------------- fatos normativos
    def test_normas_citadas_com_os_numeros_conferidos(self):
        body = self._body()
        for termo in ("Res. CMN 4.893", "Res. CMN 5.274", "Res. BCB 85", "Res. BCB 538", "18/12/2025",
                      "01/03/2026", "normativos.bcb.gov.br"):
            self.assertIn(termo, body, termo)
        self.assertNotIn("448", body, "a BCB 448 foi descartada na conferência")
        self.assertNotIn("552", body, "a alteração de 2026 não foi conferida: não citar")
        self.assertIsNone(re.search(r"\b\d+\s+controles\b", body), "não citar número de controles mínimos")

    def test_requisitos_citam_tema_e_nao_artigo(self):
        d = self._dados()
        for r in d["requisitos"]:
            with self.subTest(requisito=r["id"]):
                self.assertIn("Res. CMN 4.893", r["norma"])
                self.assertIn("Res. BCB 85", r["norma"])
                self.assertIsNone(re.search(r"\bart(?:igo|\.)?\s*\d", r["norma"] + r["explicacao"] + r["acao"], re.I),
                                  "não citar número de artigo não conferido")

    # ---------------------------------------------------------------- dados
    def test_dados_ficticios_e_bem_formados(self):
        d = self._dados()
        self.assertIn("Ipê Pay", d["contexto"])
        self.assertIn("fictícia", d["contexto"])
        texto = json.dumps(d, ensure_ascii=False)
        for host in re.findall(r"\b[\w-]+(?:\.[\w-]+)*\.(?:com|net|org|io|br)\b", texto):
            self.fail(f"domínio real nos dados: {host}")
        self.assertIsNone(re.search(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}", texto), "sem CNPJ nos dados")
        self.assertEqual([r["id"] for r in d["requisitos"]], list(GABARITO))
        for r in d["requisitos"]:
            with self.subTest(requisito=r["id"]):
                tema, gab, crit = GABARITO[r["id"]]
                self.assertEqual(r["tema"], tema)
                self.assertEqual(r["gabarito"], gab)
                self.assertEqual(r["criticidade"], crit)
                for campo in ("titulo", "fonte", "trecho", "explicacao", "acao", "norma"):
                    self.assertTrue(r[campo].strip(), campo)
                self.assertIn(r["tema"], d["temas"])
        self.assertEqual(sorted(d["temas"]), sorted(TEMAS))
        for p in ("P1", "P2", "P3"):
            self.assertTrue(d["prioridades"][p]["rotulo"] and d["prioridades"][p]["prazo"], p)
        cont = {s: sum(1 for v in GABARITO.values() if v[1] == s) for s in STATUS}
        self.assertEqual(cont, {"atendido": 4, "parcial": 5, "ausente": 8})

    def test_temas_das_alteracoes_de_dezembro_de_2025(self):
        d = self._dados()
        dez = {r["id"]: r for r in d["requisitos"] if r["tema"] == "dez2025"}
        self.assertIn("anual", dez["dez_pentest"]["titulo"])
        self.assertIn("independentes", dez["dez_pentest"]["titulo"])
        self.assertIn("Pix", dez["dez_pix"]["titulo"])
        self.assertIn("STR", dez["dez_pix"]["explicacao"])
        self.assertIn("RSFN", dez["dez_pix"]["explicacao"])
        self.assertIn("auditáveis", dez["dez_controles"]["titulo"])
        for r in dez.values():
            self.assertIn("5.274", r["norma"])
            self.assertIn("538", r["norma"])
        nuv = next(r for r in d["requisitos"] if r["id"] == "nuv_responsabilidade")
        self.assertIn("não se transfere", nuv["explicacao"])

    # ------------------------------------------------------------ sujeição
    def test_aviso_da_redacao_de_2021(self):
        """Requisitos descritos no nível da redação original de 2021 da CMN 4.893 trazem o aviso de conferir a redação de dez/2025."""
        body = self._body()
        self.assertIn("redação original de 2021", body)
        self.assertIn("confira a redação vigente", body)

    def test_quem_se_sujeita_a_cada_norma(self):
        d = self._dados()
        self.assertEqual({e["id"]: e["norma"] for e in d["entidades"]}, SUJEICAO)
        self.assertEqual(sorted(d["normas"]), sorted(NORMAS))
        for e in d["entidades"]:
            with self.subTest(entidade=e["id"]):
                self.assertTrue(e["nome"] and e["explicacao"])
        r = conferir_sujeicao(d, SUJEICAO)
        self.assertEqual((r["acertos"], r["total"], r["erros"]), (7, 7, []))
        r = conferir_sujeicao(d, dict(SUJEICAO, ipe_pay="cmn4893", ipe_store="bcb85"))
        self.assertEqual(r["erros"], ["ipe_pay", "ipe_store"])
        self.assertEqual(conferir_sujeicao(d, {})["acertos"], 0)

    # --------------------------------------------------------- aderência
    def test_gabarito_completo(self):
        d = self._dados()
        g = self._gabarito(d)
        r = avaliar_aderencia(d, g)
        self.assertEqual((r["certo"], r["otimista"], r["pessimista"], r["sem_marcacao"]), (17, 0, 0, 0))
        self.assertEqual(indice_aderencia(d, g), 38)
        self.assertEqual([(p["id"], p["prioridade"]) for p in plano_de_acao(d, g)], PLANO_GABARITO)

    def test_tudo_atendido_esconde_as_lacunas(self):
        d = self._dados()
        tudo = {r["id"]: "atendido" for r in d["requisitos"]}
        r = avaliar_aderencia(d, tudo)
        self.assertEqual(r["otimista"], 13)
        self.assertEqual(r["certo"], 4)
        self.assertEqual(plano_de_acao(d, tudo), [])
        self.assertEqual(indice_aderencia(d, tudo), 100)

    def test_tudo_ausente_superestima_o_plano(self):
        d = self._dados()
        nada = {r["id"]: "ausente" for r in d["requisitos"]}
        r = avaliar_aderencia(d, nada)
        self.assertEqual((r["pessimista"], r["certo"]), (9, 8))
        plano = plano_de_acao(d, nada)
        self.assertEqual(len(plano), 17)
        self.assertEqual(indice_aderencia(d, nada), 0)
        self.assertEqual([p["prioridade"] for p in plano].count("P1"), 5)

    def test_lacuna_escondida_some_do_plano(self):
        d = self._dados()
        m = dict(self._gabarito(d), dez_pix="atendido")
        r = avaliar_aderencia(d, m)
        self.assertEqual([i["id"] for i in r["itens"] if i["resultado"] == "otimista"], ["dez_pix"])
        self.assertNotIn("dez_pix", [p["id"] for p in plano_de_acao(d, m)])
        m = dict(self._gabarito(d), dez_pix="parcial")
        item = next(p for p in plano_de_acao(d, m) if p["id"] == "dez_pix")
        self.assertEqual((item["pontos"], item["prioridade"]), (3, "P2"))

    def test_marcacao_parcial_e_valores_invalidos(self):
        d = self._dados()
        m = {"inc_plano": "ausente", "dez_darkweb": "atendido", "pol_aprovacao": "talvez"}
        r = avaliar_aderencia(d, m)
        self.assertEqual((r["certo"], r["sem_marcacao"]), (2, 15))
        self.assertIsNone(next(i for i in r["itens"] if i["id"] == "pol_aprovacao")["marcado"])
        self.assertEqual(indice_aderencia(d, m), 50)
        self.assertIsNone(indice_aderencia(d, {}))
        self.assertEqual([p["id"] for p in plano_de_acao(d, m)], ["inc_plano"])

    def test_faixas_de_prioridade(self):
        self.assertEqual([prioridade(p) for p in (6, 4, 3, 2, 1)], ["P1", "P2", "P2", "P3", "P3"])

    # ------------------------------------------------------------ diagrama
    def test_diagrama_no_formato_do_guia(self):
        body = self._body()
        caixas = re.findall(
            r'<div class="diagram-box">\s*<div class="diagram-header">\s*'
            r'<span class="diagram-title">([^<]+)</span>.*?'
            r'<pre class="mermaid" data-title="([^"]+)">',
            body, re.S)
        self.assertGreaterEqual(len(caixas), 1, "falta um .diagram-box com cabeçalho e Mermaid")
        for titulo, data_title in caixas:
            self.assertEqual(titulo.strip(), data_title.strip())

    # ------------------------------------------------------------ simulador
    def test_simulador_sem_apis_inseguras(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        self.assertIn('id="rsf-dados"', content)
        ini = content.index("JSON.parse(document.getElementById(\"rsf-dados\")")
        motor = content[ini:content.index("</script>", ini)]
        for proibido in ("innerHTML", "outerHTML", "eval(", "new Function", "fetch(", "XMLHttpRequest", "WebSocket",
                         "document.write"):
            self.assertNotIn(proibido, motor, proibido)
        for marcador in ("rsf-lab", "rsf-entidades", "rsf-sujeicao-resultado", "rsf-requisitos", "rsf-resultado",
                         "rsf-indice", "rsf-divergencias", "rsf-plano", "conferirSujeicao", "avaliarAderencia",
                         "indiceAderencia", "planoDeAcao"):
            self.assertIn(marcador, content, marcador)
        self.assertIn("aria-label", motor)
        self.assertIn("textContent", motor)
        self.assertIn('"legend"', motor, "cada requisito é um fieldset com legend")
        self.assertIn('"fieldset"', motor)

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        termos = ["política de segurança cibernética", "plano de ação e de resposta a incidentes", "relatório anual",
                  "31 de dezembro", "diretor", "conselho de administração", "incidentes relevantes",
                  "processamento, armazenamento de dados e computação em nuvem", "países e regiões",
                  "não se transfere", "teste de intrusão", "controles mínimos", "Pix", "STR", "RSFN",
                  "dark web", "instituição de pagamento", "instituições financeiras", "Ipê Pay", "Ipê Store",
                  "PCI DSS", "ISO/IEC 27001", "Banco Central"]
        for termo in termos:
            self.assertIn(termo, content, f"Termo obrigatório ausente: {termo}")

    def test_componentes_pedagogicos(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        self.assertIn('class="callout', content)
        self.assertIn('class="terminal-box', content)
        self.assertIn('class="diagram-svg-wrap', content)
        self.assertNotIn('<pre class="mermaid"', content)
        self.assertEqual(content.count('class="checklist-item"'), 7)
        self.assertGreaterEqual(content.count('class="quiz-item"'), 6)
        self.assertIn('class="facts-grid', content)
        self.assertIn('initChecklist("regulacao-setor-financeiro")', content)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn(f"{SLUG}/treinamento-regulacao-setor-financeiro.html", content)
        self.assertIn(f'data-slug="{SLUG}"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)


if __name__ == "__main__":
    unittest.main()
