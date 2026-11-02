#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_gestao_riscos_terceiros.py
Testes automatizados para o Estudo 57: Gestao-de-Riscos-de-Terceiros

O simulador Avaliador de Fornecedores guarda num bloco JSON os eixos do
questionário (dados, acesso, dependência), o catálogo de cláusulas, os itens
do plano de saída e três fornecedores fictícios avaliados pela Ipê Pay, com
respostas a questionário, evidências (ISO 27001, SOC 2, teste de intrusão,
declaração de subcontratados) e a proposta de plano de saída. Este teste
espelha em Python as regras do motor JavaScript: impacto, probabilidade,
criticidade, risco inerente, validade de cada evidência, redução e risco
residual, cláusulas obrigatórias por criticidade, lacunas do plano de saída,
decisão (contratar, contratar com condições ou recusar) e a correção das
respostas do aluno, inclusive as armadilhas didáticas.
"""

import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402

SLUG = "Gestao-de-Riscos-de-Terceiros"
CRITICIDADES = ("baixa", "media", "critica")
DECISOES = ("contratar", "condicoes", "recusar")
CLAUSULAS = ("notificacao_incidente", "direito_auditoria", "subcontratacao", "localizacao_dados",
             "devolucao_eliminacao", "plano_saida", "acesso_regulador")
ITENS_SAIDA = ("exportacao_formato_aberto", "prazo_transicao", "transferencia_antes_exclusao",
               "eliminacao_certificada", "fornecedor_alternativo", "gatilhos_saida")
TIPOS_EVIDENCIA = ("iso27001", "soc2", "pentest", "subcontratados")

GABARITO = {
    "F1": {"impacto": 5, "prob": 5, "crit": "critica", "inerente": 25, "faixa": "Crítico",
           "validas": {"F1-iso", "F1-soc2", "F1-pentest", "F1-sub"}, "reducao": 4, "residual": 5,
           "clausulas": set(CLAUSULAS), "lacunas": [], "decisao": "contratar"},
    "F2": {"impacto": 4, "prob": 4, "crit": "critica", "inerente": 16, "faixa": "Crítico",
           "validas": {"F2-soc2", "F2-pentest", "F2-sub"}, "reducao": 2, "residual": 10,
           "clausulas": set(CLAUSULAS) - {"acesso_regulador"},
           "lacunas": ["prazo_transicao", "transferencia_antes_exclusao", "fornecedor_alternativo"],
           "decisao": "condicoes"},
    "F3": {"impacto": 3, "prob": 3, "crit": "media", "inerente": 9, "faixa": "Médio",
           "validas": set(), "reducao": -1, "residual": 11,
           "clausulas": {"notificacao_incidente", "direito_auditoria", "subcontratacao", "devolucao_eliminacao"},
           "lacunas": ["transferencia_antes_exclusao", "eliminacao_certificada"], "decisao": "recusar"},
}


# ============================================================ regras
def impacto(f):
    """Espelho de impactoFornecedor: o maior eixo entre dados e dependência manda; se ambos >= 2, +1."""
    d, p = f["eixos"]["dados"], f["eixos"]["dependencia"]
    return min(5, 1 + max(d, p) + (1 if min(d, p) >= 2 else 0))


def probabilidade(f):
    """Espelho de probabilidadeFornecedor: 1 + acesso + 1 se existe quarta parte (declarada ou não)."""
    return min(5, 1 + f["eixos"]["acesso"] + (1 if f["quarta_parte"] else 0))


def criticidade(f):
    """Espelho de criticidadeFornecedor: impacto >= 4 crítica; 2 a 3 média; 1 baixa."""
    i = impacto(f)
    return "critica" if i >= 4 else ("media" if i >= 2 else "baixa")


def inerente(f):
    return impacto(f) * probabilidade(f)


def faixa(d, pontos):
    """Espelho de faixaRisco."""
    for fx in d["faixas"]:
        if fx["min"] <= pontos <= fx["max"]:
            return fx["nome"]
    return None


def validar_evidencia(ev, f, data_ref):
    """Espelho de validarEvidencia: valida, pontos nominais (o que o fornecedor alega) e pontos reais."""
    t = ev["tipo"]
    if t == "iso27001":
        valida = ev["cobre_servico"] and ev["validade"] >= data_ref
        nominal = 1
    elif t == "soc2":
        valida = ev["tipo_relatorio"] == "II" and ev["periodo_meses"] >= 6 and ev["emitido_ha_meses"] <= 12
        nominal = 2 - (1 if any(x["relevante"] for x in ev["excecoes"]) else 0)
    elif t == "pentest":
        valida = ev["meses_desde"] <= 12 and ev["criticos_abertos"] == 0 and ev["independente"]
        nominal = 1
    elif t == "subcontratados":
        valida = all(q["declarado"] for q in f["quarta_parte"] if q["critico"])
        nominal = 0
    else:
        raise ValueError(t)
    return {"valida": bool(valida), "nominal": nominal}


def contribuicao(ev, aceita):
    """Aceita: soma os pontos nominais. Recusada: zero; declaração de subcontratados recusada pesa -1."""
    v_nominal = {"iso27001": 1, "pentest": 1, "subcontratados": 0}.get(ev["tipo"])
    if ev["tipo"] == "soc2":
        v_nominal = 2 - (1 if any(x["relevante"] for x in ev["excecoes"]) else 0)
    if aceita:
        return v_nominal
    return -1 if ev["tipo"] == "subcontratados" else 0


def reducao(f, data_ref, aceitas=None):
    """Espelho de reducaoRisco: com aceitas=None usa a validade real; senão, as escolhas do aluno."""
    total = 0
    for ev in f["evidencias"]:
        ok = validar_evidencia(ev, f, data_ref)["valida"] if aceitas is None else ev["id"] in aceitas
        total += contribuicao(ev, ok)
    return max(-1, min(4, total))


def residual(inerente_pts, r):
    """Espelho de riscoResidual: inerente × (100 − 20·R)%, arredondado meio para cima, mínimo 1."""
    return max(1, (inerente_pts * (100 - 20 * r) + 50) // 100)


def clausulas_obrigatorias(d, f):
    """Espelho de clausulasObrigatorias."""
    base = list(d["clausulas_por_criticidade"][criticidade(f)])
    if f["nuvem_relevante"]:
        for c in d["clausulas_nuvem_relevante"]:
            if c not in base:
                base.append(c)
    return [c for c in d["clausulas"] if c in base]


def lacunas_saida(d, f):
    """Espelho de lacunasSaida: itens exigidos pela criticidade que a proposta não prevê."""
    return [i for i in d["saida_por_criticidade"][criticidade(f)] if i not in f["plano_saida"]]


def decidir(d, f, aceitas=None):
    """Espelho de decidirFornecedor."""
    r = reducao(f, d["data_ref"], aceitas)
    res = residual(inerente(f), r)
    obrig = clausulas_obrigatorias(d, f)
    bloqueios = [c for c in f["recusa_clausulas"] if c in obrig]
    invalidas = [ev["id"] for ev in f["evidencias"]
                 if not (validar_evidencia(ev, f, d["data_ref"])["valida"] if aceitas is None else ev["id"] in aceitas)]
    lac = lacunas_saida(d, f)
    pendencias = invalidas + lac
    if bloqueios or res >= d["limite_recusa"]:
        dec = "recusar"
    elif res <= d["apetite"] and not pendencias:
        dec = "contratar"
    else:
        dec = "condicoes"
    return {"decisao": dec, "residual": res, "reducao": r, "bloqueios": bloqueios,
            "invalidas": invalidas, "lacunas": lac, "pendencias": pendencias}


def corrigir(d, f, resp):
    """Espelho de corrigirFornecedor: 5 pontos (criticidade, faixa, evidências, cláusulas, decisão)."""
    validas = {ev["id"] for ev in f["evidencias"] if validar_evidencia(ev, f, d["data_ref"])["valida"]}
    aceitas = set(resp["aceitas"])
    ev_status = {}
    for ev in f["evidencias"]:
        a, v = ev["id"] in aceitas, ev["id"] in validas
        ev_status[ev["id"]] = "acerto" if a == v else ("aceitou_invalida" if a else "rejeitou_valida")
    obrig = set(clausulas_obrigatorias(d, f))
    esc = set(resp["clausulas"])
    cl_status = {}
    for c in d["clausulas"]:
        if c in obrig:
            cl_status[c] = "acerto" if c in esc else "faltou"
        elif c in esc:
            cl_status[c] = "excesso"
    gab = decidir(d, f)
    out = {
        "criticidade_ok": resp["criticidade"] == criticidade(f),
        "faixa_ok": resp["faixa"] == faixa(d, inerente(f)),
        "evidencias": ev_status,
        "evidencias_ok": all(s == "acerto" for s in ev_status.values()),
        "clausulas": cl_status,
        "clausulas_ok": all(s == "acerto" for s in cl_status.values()),
        "decisao_ok": resp["decisao"] == gab["decisao"],
        "residual_aluno": residual(inerente(f), reducao(f, d["data_ref"], aceitas)),
        "residual_real": gab["residual"],
    }
    out["pontos"] = sum(int(out[k]) for k in ("criticidade_ok", "faixa_ok", "evidencias_ok", "clausulas_ok",
                                               "decisao_ok"))
    return out


class TestGestaoRiscosTerceiros(unittest.TestCase):
    """Estrutura, conteúdo, simulador e compilação do estudo 57."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "gestao_de_riscos_de_terceiros_body.html"
        self.compiled_path = self.root / SLUG / "treinamento-gestao-de-riscos-de-terceiros.html"
        self.portal_path = self.root / "index.html"

    def _body(self):
        return self.body_path.read_text(encoding="utf-8")

    def _dados(self):
        m = re.search(r'<script type="application/json" id="grt-dados">(.*?)</script>', self._body(), re.S)
        self.assertIsNotNone(m, "Bloco JSON #grt-dados ausente no body")
        return json.loads(m.group(1))

    def _forn(self, d, fid):
        return next(f for f in d["fornecedores"] if f["id"] == fid)

    def _resp_gabarito(self, d, f):
        g = GABARITO[f["id"]]
        return {"criticidade": g["crit"], "faixa": g["faixa"], "aceitas": sorted(g["validas"]),
                "clausulas": sorted(g["clausulas"]), "decisao": g["decisao"]}

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
        self.assertIn('data-slug="gestao-de-riscos-de-terceiros"', body)

    def test_coerencia_com_o_catalogo(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        info = ESTUDOS_DADOS[SLUG]
        self.assertIn(info["simulador_nome"], content)
        self.assertIn(info["pergunta_chave"], content)
        self.assertIn(info["subtitulo"], self.portal_path.read_text(encoding="utf-8"))
        for fato in info["fatos"]:
            self.assertIn(fato, content, fato)

    def test_pontes_com_os_estudos_vizinhos(self):
        body = self._body()
        intro = body[:body.index('id="simulador"')]
        for ref in ("Estudo 25", "Estudo 26", "Estudo 54"):
            self.assertIn(ref, intro, ref)
        fim = body[body.index('id="fatos"'):body.index("</article>")]
        for ref in ("Trilha 13", "Estudo 54", "Estudo 55", "Estudo 56", "Estudo 33", "Estudo 37",
                    "Rota por Vaga", "57 módulos"):
            self.assertIn(ref, fim, ref)

    # ------------------------------------------------- fatos normativos
    def test_referencias_normativas(self):
        body = self._body()
        for termo in ("GV.SC", "NIST CSF 2.0", "ISO/IEC 27002:2022", "5.19", "5.20", "5.21", "5.22", "5.23",
                      "Res. CMN 4.893", "CMN 5.274/2025", "SOC 2 Tipo I", "SOC 2 Tipo II", "quarta parte",
                      "T1195", "T1199", "direito de auditoria", "plano de saída", "países e regiões",
                      "responsabilidade não se transfere"):
            self.assertIn(termo, body, termo)

    def test_sem_numero_de_artigo_da_cmn(self):
        body = self._body()
        self.assertIsNone(re.search(r"art(?:igo|\.)\s*\d+[^<]{0,80}(?:4\.893|5\.274)", body, re.I),
                          "não citar número de artigo da Res. CMN 4.893")
        self.assertIsNone(re.search(r"(?:4\.893|5\.274)[^<]{0,80}art(?:igo|\.)\s*\d+", body, re.I),
                          "não citar número de artigo da Res. CMN 4.893")

    # ---------------------------------------------------------------- dados
    def test_dados_ficticios_e_bem_formados(self):
        d = self._dados()
        self.assertIn("fictíci", d["contexto"])
        texto = json.dumps(d, ensure_ascii=False)
        for host in re.findall(r"\b[\w-]+(?:\.[\w-]+)*\.(?:com|net|org|io|br)\b", texto):
            self.fail(f"domínio real nos dados: {host}")
        self.assertIsNone(re.search(r"\d{3}\.\d{3}\.\d{3}-\d{2}", texto), "sem CPF nos dados")
        self.assertIsNone(re.search(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}", texto), "sem CNPJ nos dados")
        self.assertEqual(d["data_ref"], "2026-11-02")
        self.assertEqual(d["apetite"], 9)
        self.assertEqual(d["limite_recusa"], 16)
        self.assertEqual([(fx["nome"], fx["min"], fx["max"]) for fx in d["faixas"]],
                         [("Baixo", 1, 4), ("Médio", 5, 9), ("Alto", 10, 15), ("Crítico", 16, 25)])
        self.assertEqual(sorted(d["eixos"]), ["acesso", "dados", "dependencia"])
        for eid, e in d["eixos"].items():
            with self.subTest(eixo=eid):
                self.assertEqual(len(e["niveis"]), 4)
                self.assertTrue(e["titulo"].strip())
        self.assertEqual(tuple(d["clausulas"]), CLAUSULAS)
        for cid, c in d["clausulas"].items():
            with self.subTest(clausula=cid):
                self.assertTrue(c["nome"].strip() and c["explicacao"].strip())
        self.assertEqual(d["clausulas_por_criticidade"], {
            "baixa": ["notificacao_incidente", "devolucao_eliminacao"],
            "media": ["notificacao_incidente", "direito_auditoria", "subcontratacao", "devolucao_eliminacao"],
            "critica": ["notificacao_incidente", "direito_auditoria", "subcontratacao", "localizacao_dados",
                        "devolucao_eliminacao", "plano_saida"],
        })
        self.assertEqual(d["clausulas_nuvem_relevante"], ["acesso_regulador", "localizacao_dados"])
        self.assertIn("4.893", d["clausulas"]["acesso_regulador"]["explicacao"])
        self.assertEqual(tuple(d["itens_saida"]), ITENS_SAIDA)
        self.assertEqual(d["saida_por_criticidade"], {
            "baixa": ["eliminacao_certificada"],
            "media": ["exportacao_formato_aberto", "transferencia_antes_exclusao", "eliminacao_certificada"],
            "critica": list(ITENS_SAIDA),
        })
        self.assertEqual([f["id"] for f in d["fornecedores"]], list(GABARITO))
        for f in d["fornecedores"]:
            with self.subTest(fornecedor=f["id"]):
                for campo in ("nome", "servico", "explicacao"):
                    self.assertTrue(f[campo].strip(), campo)
                self.assertGreaterEqual(len(f["questionario"]), 5)
                for q in f["questionario"]:
                    self.assertTrue(q["pergunta"].strip() and q["resposta"].strip())
                for k in ("dados", "acesso", "dependencia"):
                    self.assertIn(f["eixos"][k], range(4))
                self.assertTrue(set(f["plano_saida"]) <= set(ITENS_SAIDA))
                self.assertTrue(set(f["recusa_clausulas"]) <= set(CLAUSULAS))
                for ev in f["evidencias"]:
                    self.assertIn(ev["tipo"], TIPOS_EVIDENCIA)
                    self.assertTrue(ev["id"].startswith(f["id"] + "-"))
                    self.assertTrue(ev["titulo"].strip() and ev["detalhe"].strip())
                for q in f["quarta_parte"]:
                    self.assertTrue(q["nome"].strip() and q["servico"].strip())

    def test_armadilhas_presentes_nos_dados(self):
        d = self._dados()
        f2, f3 = self._forn(d, "F2"), self._forn(d, "F3")
        iso = next(e for e in f2["evidencias"] if e["tipo"] == "iso27001")
        self.assertFalse(iso["cobre_servico"], "certificado ISO com escopo que não cobre o serviço")
        self.assertGreaterEqual(iso["validade"], d["data_ref"], "o certificado está válido: a armadilha é o escopo")
        self.assertIn("escopo", iso["detalhe"].lower())
        soc = next(e for e in f3["evidencias"] if e["tipo"] == "soc2")
        self.assertEqual(soc["tipo_relatorio"], "I", "SOC 2 Tipo I apresentado como se fosse Tipo II")
        self.assertIn("Tipo I", soc["detalhe"])
        ocultos = [q for q in f3["quarta_parte"] if q["critico"] and not q["declarado"]]
        self.assertGreaterEqual(len(ocultos), 1, "subcontratado crítico não declarado")
        for q in ocultos:
            self.assertIn(q["nome"], soc["detalhe"], "o subcontratado oculto aparece no relatório SOC 2")
        self.assertEqual(f3["recusa_clausulas"], ["direito_auditoria"])
        soc2 = next(e for e in f2["evidencias"] if e["tipo"] == "soc2")
        self.assertTrue(any(x["relevante"] for x in soc2["excecoes"]), "SOC 2 Tipo II com exceção relevante")
        self.assertTrue(self._forn(d, "F1")["nuvem_relevante"])
        self.assertFalse(f2["nuvem_relevante"])
        self.assertFalse(f3["nuvem_relevante"])

    # ------------------------------------------------------------ motor
    def test_gabarito_por_fornecedor(self):
        d = self._dados()
        for f in d["fornecedores"]:
            g = GABARITO[f["id"]]
            with self.subTest(fornecedor=f["id"]):
                self.assertEqual(impacto(f), g["impacto"])
                self.assertEqual(probabilidade(f), g["prob"])
                self.assertEqual(criticidade(f), g["crit"])
                self.assertEqual(inerente(f), g["inerente"])
                self.assertEqual(faixa(d, inerente(f)), g["faixa"])
                validas = {ev["id"] for ev in f["evidencias"] if validar_evidencia(ev, f, d["data_ref"])["valida"]}
                self.assertEqual(validas, g["validas"])
                self.assertEqual(reducao(f, d["data_ref"]), g["reducao"])
                self.assertEqual(set(clausulas_obrigatorias(d, f)), g["clausulas"])
                self.assertEqual(lacunas_saida(d, f), g["lacunas"])
                dec = decidir(d, f)
                self.assertEqual(dec["residual"], g["residual"])
                self.assertEqual(dec["decisao"], g["decisao"])

    def test_tres_decisoes_diferentes(self):
        d = self._dados()
        self.assertEqual({decidir(d, f)["decisao"] for f in d["fornecedores"]}, set(DECISOES))

    def test_residual_e_faixas(self):
        self.assertEqual(residual(25, 4), 5)
        self.assertEqual(residual(16, 2), 10)
        self.assertEqual(residual(9, -1), 11)
        self.assertEqual(residual(16, 3), 6)
        self.assertEqual(residual(1, 4), 1, "residual nunca abaixo de 1")
        self.assertEqual(residual(10, 0), 10)
        d = self._dados()
        self.assertEqual([faixa(d, p) for p in (1, 4, 5, 9, 10, 15, 16, 25)],
                         ["Baixo", "Baixo", "Médio", "Médio", "Alto", "Alto", "Crítico", "Crítico"])

    def test_gabarito_completo_vale_cinco_pontos(self):
        d = self._dados()
        total = 0
        for f in d["fornecedores"]:
            with self.subTest(fornecedor=f["id"]):
                res = corrigir(d, f, self._resp_gabarito(d, f))
                self.assertEqual(res["pontos"], 5)
                self.assertEqual(res["residual_aluno"], res["residual_real"])
                total += res["pontos"]
        self.assertEqual(total, 15)

    def test_armadilha_iso_fora_do_escopo(self):
        d = self._dados()
        f2 = self._forn(d, "F2")
        resp = self._resp_gabarito(d, f2)
        resp["aceitas"] = resp["aceitas"] + ["F2-iso"]
        res = corrigir(d, f2, resp)
        self.assertEqual(res["evidencias"]["F2-iso"], "aceitou_invalida")
        self.assertFalse(res["evidencias_ok"])
        self.assertEqual(res["residual_aluno"], 6, "com o certificado aceito, o residual cairia para 6")
        self.assertEqual(res["residual_real"], 10)
        self.assertEqual(res["pontos"], 4)
        self.assertEqual(decidir(d, f2, set(resp["aceitas"]))["decisao"], "condicoes",
                         "as lacunas do plano de saída ainda impõem condições")

    def test_armadilhas_soc2_tipo_i_e_quarta_parte_oculta(self):
        d = self._dados()
        f3 = self._forn(d, "F3")
        todas = [ev["id"] for ev in f3["evidencias"]]
        res = corrigir(d, f3, {"criticidade": "critica", "faixa": "Alto", "aceitas": todas,
                               "clausulas": ["notificacao_incidente", "devolucao_eliminacao", "plano_saida"],
                               "decisao": "contratar"})
        self.assertEqual(res["evidencias"], {"F3-soc2": "aceitou_invalida", "F3-pentest": "aceitou_invalida",
                                             "F3-sub": "aceitou_invalida"})
        self.assertEqual(res["residual_aluno"], 4, "aceitando tudo, o risco parece Baixo")
        self.assertEqual(res["residual_real"], 11)
        self.assertEqual(res["clausulas"], {"notificacao_incidente": "acerto", "direito_auditoria": "faltou",
                                            "subcontratacao": "faltou", "devolucao_eliminacao": "acerto",
                                            "plano_saida": "excesso"})
        self.assertEqual(res["pontos"], 0)

    def test_recusa_de_clausula_obrigatoria_bloqueia(self):
        d = self._dados()
        f3 = dict(self._forn(d, "F3"))
        dec = decidir(d, f3)
        self.assertEqual(dec["bloqueios"], ["direito_auditoria"])
        self.assertEqual(dec["decisao"], "recusar")
        # sem a recusa, o residual Alto levaria a contratar com condições
        f3["recusa_clausulas"] = []
        self.assertEqual(decidir(d, f3)["decisao"], "condicoes")

    def test_lacuna_no_plano_de_saida_impoe_condicoes(self):
        d = self._dados()
        f1 = dict(self._forn(d, "F1"))
        self.assertEqual(decidir(d, f1)["pendencias"], [])
        f1["plano_saida"] = [i for i in f1["plano_saida"] if i != "fornecedor_alternativo"]
        dec = decidir(d, f1)
        self.assertEqual(dec["lacunas"], ["fornecedor_alternativo"])
        self.assertEqual(dec["decisao"], "condicoes")

    def test_pendencias_do_fornecedor_2(self):
        d = self._dados()
        dec = decidir(d, self._forn(d, "F2"))
        self.assertEqual(dec["invalidas"], ["F2-iso"])
        self.assertEqual(len(dec["pendencias"]), 4)
        self.assertEqual(dec["bloqueios"], [])

    def test_criticidade_nao_e_risco_residual(self):
        """O fornecedor de maior criticidade é o de menor risco residual: criticidade não muda com controles."""
        d = self._dados()
        f1 = self._forn(d, "F1")
        self.assertEqual(criticidade(f1), "critica")
        self.assertEqual(decidir(d, f1)["residual"], min(decidir(d, f)["residual"] for f in d["fornecedores"]))

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
        self.assertIn('id="grt-dados"', content)
        ini = content.index("JSON.parse(document.getElementById(\"grt-dados\")")
        motor = content[ini:content.index("</script>", ini)]
        for proibido in ("innerHTML", "outerHTML", "eval(", "new Function", "fetch(", "XMLHttpRequest", "WebSocket",
                         "document.write", "localStorage"):
            self.assertNotIn(proibido, motor, proibido)
        for marcador in ("grt-lab", "grt-fornecedores", "grt-fornecedor", "grt-placar", "impactoFornecedor",
                         "probabilidadeFornecedor", "criticidadeFornecedor", "faixaRisco", "validarEvidencia",
                         "reducaoRisco", "riscoResidual", "clausulasObrigatorias", "lacunasSaida",
                         "decidirFornecedor", "corrigirFornecedor", "responderFornecedorGrt"):
            self.assertIn(marcador, content, marcador)
        self.assertIn("aria-label", motor)
        self.assertIn("textContent", motor)
        self.assertIn('"radio"', motor)
        self.assertIn('"checkbox"', motor)

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        termos = ["ciclo de vida do terceiro", "due diligence", "criticidade", "risco inerente", "risco residual",
                  "questionário", "autodeclaração", "escopo", "Declaração de Aplicabilidade", "exceções",
                  "organizações subcontratadas", "quarta parte", "notificação de incidente", "direito de auditoria",
                  "subcontratação", "devolução", "eliminação", "plano de saída", "monitoramento contínuo",
                  "Ipê Pay", "fornecedor crítico", "concentração"]
        for termo in termos:
            self.assertIn(termo, content, f"Termo obrigatório ausente: {termo}")

    def test_componentes_pedagogicos(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        self.assertIn('class="callout', content)
        self.assertIn('class="diagram-svg-wrap', content)
        self.assertNotIn('<pre class="mermaid"', content)
        self.assertIn('class="terminal-box"', content)
        self.assertEqual(content.count('class="checklist-item"'), 7)
        self.assertGreaterEqual(content.count('class="quiz-item"'), 6)
        self.assertIn('class="facts-grid', content)
        self.assertIn('initChecklist("gestao-de-riscos-de-terceiros")', content)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn(f"{SLUG}/treinamento-gestao-de-riscos-de-terceiros.html", content)
        self.assertIn(f'data-slug="{SLUG}"', content)
        self.assertIn(f"{len(ESTUDOS_DADOS)} / {len(ESTUDOS_DADOS)}", content, "portal com todos os módulos compilados")


if __name__ == "__main__":
    unittest.main()
