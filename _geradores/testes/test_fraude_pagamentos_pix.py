#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_fraude_pagamentos_pix.py
Testes automatizados para o Estudo 55: Fraude-em-Pagamentos-e-Pix

O simulador Mesa Antifraude guarda num bloco JSON os sinais de risco (com
peso padrão e faixa do controle deslizante), os limiares padrão de "segurar"
e "bloquear" e a fila de transações Pix fictícias da Ipê Pay (instituição de
pagamento fictícia do Estudo 54): golpes típicos (falsa central, falso
parente, conta laranja, sequestro de conta) e casos legítimos que parecem
suspeitos. Este teste espelha em Python as regras do motor JavaScript:
pontuação de risco (soma dos pesos dos sinais presentes), decisão por limiar
(aprovar, segurar ou bloquear), desfecho de cada transação, contagens de
fraudes evitadas e clientes legítimos bloqueados e a recuperação pelo MED 2.0
para as fraudes que passaram (devolução limitada ao saldo, com rastreio para
outras contas e prazo de 80 dias corridos para a vítima contestar).
"""

import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402

SLUG = "Fraude-em-Pagamentos-e-Pix"
DECISOES = ("aprovar", "segurar", "bloquear")
GOLPES = ("falsa_central", "falso_parente", "conta_laranja", "sequestro_conta")
PRAZO_CONTESTACAO = 80

PESOS_PADRAO = {
    "valor_atipico": 25, "madrugada": 10, "conta_nova": 25, "chave_nova": 10, "primeiro_pix": 10,
    "dispositivo_novo": 20, "limite_alterado": 20, "em_ligacao": 15, "muitos_pagadores": 20,
    "denuncias": 35, "recebedor_recorrente": -15,
}
LIMIARES_PADRAO = {"segurar": 40, "bloquear": 70}

# id → (fraude, golpe, pontuação com os pesos padrão), na ordem da fila
FILA = {
    "T01": (False, None, 35),
    "T02": (True, "falso_parente", 45),
    "T03": (True, "falsa_central", 95),
    "T04": (False, None, 20),
    "T05": (True, "conta_laranja", 65),
    "T06": (False, None, 5),
    "T07": (True, "falso_parente", 35),
    "T08": (False, None, 50),
    "T09": (True, "falsa_central", 50),
    "T10": (False, None, 55),
    "T11": (True, "conta_laranja", 20),
    "T12": (False, None, 45),
    "T13": (True, "sequestro_conta", 85),
    "T14": (False, None, 25),
}


# ============================================================ regras
def pontuar_risco(t, pesos):
    """Espelho de pontuarRisco: soma dos pesos dos sinais presentes na transação."""
    return sum(pesos.get(s, 0) for s in t["sinais"])


def decidir(pontos, limiares):
    """Espelho de decidirTransacao: bloquear tem precedência sobre segurar."""
    if pontos >= limiares["bloquear"]:
        return "bloquear"
    if pontos >= limiares["segurar"]:
        return "segurar"
    return "aprovar"


def recuperacao_med(t):
    """Espelho de simularMed: devolução limitada ao saldo encontrado, dentro do prazo de contestação."""
    med = t["med"]
    if med["dias_para_contestar"] > PRAZO_CONTESTACAO:
        return {"no_prazo": False, "so_original": 0, "med2": 0}
    rastreado = sum(c["saldo"] for c in med["rastreio"])
    return {
        "no_prazo": True,
        "so_original": min(t["valor"], med["saldo_recebedora"]),
        "med2": min(t["valor"], med["saldo_recebedora"] + rastreado),
    }


def desfecho(t, decisao):
    if t["fraude"]:
        if decisao == "bloquear" or (decisao == "segurar" and t["analise_evita"]):
            return "fraude_evitada"
        return "fraude_passou"
    return {"aprovar": "legitima_aprovada", "segurar": "legitima_segurada", "bloquear": "legitima_bloqueada"}[decisao]


def avaliar_mesa(d, pesos, limiares, manuais=None):
    """Espelho de avaliarMesa: decide cada transação (manual vence a automática) e consolida os números."""
    manuais = manuais or {}
    r = {"itens": [], "fraudes": 0, "fraudes_evitadas": 0, "prejuizo_evitado": 0, "fraudes_passaram": 0,
         "prejuizo_passou": 0, "legitimas": 0, "legitimas_bloqueadas": 0, "legitimas_seguradas": 0,
         "seguradas": 0, "recuperado_med2": 0, "recuperado_so_original": 0}
    for t in d["transacoes"]:
        pontos = pontuar_risco(t, pesos)
        auto = decidir(pontos, limiares)
        dec = manuais.get(t["id"]) if manuais.get(t["id"]) in DECISOES else auto
        res = desfecho(t, dec)
        item = {"id": t["id"], "pontos": pontos, "automatica": auto, "decisao": dec, "desfecho": res}
        if dec == "segurar":
            r["seguradas"] += 1
        if t["fraude"]:
            r["fraudes"] += 1
            if res == "fraude_evitada":
                r["fraudes_evitadas"] += 1
                r["prejuizo_evitado"] += t["valor"]
            else:
                r["fraudes_passaram"] += 1
                r["prejuizo_passou"] += t["valor"]
                med = recuperacao_med(t)
                item["med"] = med
                r["recuperado_med2"] += med["med2"]
                r["recuperado_so_original"] += med["so_original"]
        else:
            r["legitimas"] += 1
            if res == "legitima_bloqueada":
                r["legitimas_bloqueadas"] += 1
            elif res == "legitima_segurada":
                r["legitimas_seguradas"] += 1
        r["itens"].append(item)
    return r


class TestFraudePagamentosPix(unittest.TestCase):
    """Estrutura, conteúdo, simulador e compilação do estudo 55."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "fraude_em_pagamentos_e_pix_body.html"
        self.compiled_path = self.root / SLUG / "treinamento-fraude-em-pagamentos-e-pix.html"
        self.portal_path = self.root / "index.html"

    def _body(self):
        return self.body_path.read_text(encoding="utf-8")

    def _dados(self):
        m = re.search(r'<script type="application/json" id="fpx-dados">(.*?)</script>', self._body(), re.S)
        self.assertIsNotNone(m, "Bloco JSON #fpx-dados ausente no body")
        return json.loads(m.group(1))

    def _pesos(self, d, **alt):
        p = {s["id"]: s["peso"] for s in d["sinais"]}
        p.update(alt)
        return p

    def _resumo(self, r):
        return (r["fraudes_evitadas"], r["legitimas_bloqueadas"], r["legitimas_seguradas"], r["prejuizo_evitado"],
                r["prejuizo_passou"], r["recuperado_med2"], r["recuperado_so_original"])

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
        self.assertIn('data-slug="fraude-em-pagamentos-e-pix"', body)

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
        for ref in ("Estudo 15", "Estudo 46", "Estudo 49", "Estudo 54"):
            self.assertIn(ref, intro, ref)
        fim = body[body.index('id="fatos"'):body.index("</article>")]
        for ref in ("Trilha 13", "Estudo 56", "Estudo 57"):
            self.assertIn(ref, fim, ref)

    # ------------------------------------------------- fatos normativos
    def test_med_com_os_fatos_conferidos(self):
        body = self._body()
        for termo in ("Res. BCB 493", "28/08/2025", "01/10/2025", "80 dias corridos", "IN BCB 766", "01/09/2026",
                      "7 dias", "até 11 dias", "contas diferentes", "parcial", "autoatendimento", "bloqueio cautelar",
                      "fevereiro de 2026"):
            self.assertIn(termo, body, termo)
        self.assertIsNone(re.search(r"11 dias (?:úteis|corridos)", body), "não qualificar os 11 dias")
        self.assertIsNone(re.search(r"bloqueio cautelar[^.]{0,80}\d+\s*(?:horas|dias|h\b)", body),
                          "bloqueio cautelar sem prazo")
        self.assertIsNone(re.search(r"\bart(?:igo|\.)?\s*\d", body, re.I), "não citar número de artigo não conferido")

    def test_fontes_dos_prazos_do_med_sao_as_conferidas(self):
        """Os prazos vieram de comunicados do BCB e da IN BCB 766, não do texto da Res. BCB 493."""
        body = self._body()
        self.assertNotIn("foram conferidos na Res. BCB 493", body)
        self.assertIn("comunicados do Banco Central", body)
        self.assertIn("IN BCB 766", body)

    def test_diagrama_poe_o_bloqueio_cautelar_fora_do_med(self):
        """O texto diz 'Além do MED…': o bloqueio cautelar é medida à parte, não etapa da contestação."""
        body = self._body()
        m = re.search(r'<pre class="mermaid" data-title="Fluxo do MED 2.0[^"]*">(.*?)</pre>', body, re.S)
        self.assertIsNotNone(m, "diagrama do MED ausente")
        codigo = m.group(1)
        sub = re.search(r'subgraph MED\b[^\n]*\n(.*?)\n\s*end\b', codigo, re.S)
        self.assertIsNotNone(sub, "as etapas do MED ficam num subgraph MED")
        self.assertIn("Vítima contesta", sub.group(1))
        self.assertIn("Devolução", sub.group(1))
        self.assertNotIn("Bloqueio cautelar", sub.group(1), "o bloqueio cautelar fica fora do MED")
        no = re.search(r'(\w+)\["Bloqueio cautelar[^\]]*\]', codigo)
        self.assertIsNotNone(no)
        self.assertRegex(no.group(0), r"à parte do MED")
        self.assertIn("sem prazo", no.group(0))
        bc = no.group(1)
        self.assertIsNone(re.search(r"\b%s\s*-->" % bc, codigo), "o bloqueio cautelar não leva à análise do MED")
        self.assertIsNone(re.search(r"-->\s*%s\b" % bc, codigo), "a contestação não leva ao bloqueio cautelar")

    def test_med_nao_cobre_pix_por_engano(self):
        body = self._body()
        self.assertIn("por engano", body)
        self.assertIn("falha operacional", body)

    # ---------------------------------------------------------------- dados
    def test_dados_ficticios_e_bem_formados(self):
        d = self._dados()
        self.assertIn("Ipê Pay", d["contexto"])
        self.assertIn("fictícia", d["contexto"])
        texto = json.dumps(d, ensure_ascii=False)
        for host in re.findall(r"\b[\w-]+(?:\.[\w-]+)*\.(?:com|net|org|io|br)\b", texto):
            self.fail(f"domínio real nos dados: {host}")
        self.assertIsNone(re.search(r"\d{3}\.\d{3}\.\d{3}-\d{2}", texto), "sem CPF nos dados")
        self.assertIsNone(re.search(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}", texto), "sem CNPJ nos dados")
        self.assertEqual({s["id"]: s["peso"] for s in d["sinais"]}, PESOS_PADRAO)
        self.assertEqual(d["limiares"], LIMIARES_PADRAO)
        for s in d["sinais"]:
            with self.subTest(sinal=s["id"]):
                self.assertTrue(s["nome"].strip() and s["descricao"].strip())
                self.assertIn(s["grupo"], d["grupos"])
                self.assertLessEqual(s["min"], s["peso"])
                self.assertLessEqual(s["peso"], s["max"])
        self.assertEqual(sorted(d["grupos"]), ["conta", "dispositivo", "transacao"])
        self.assertEqual([t["id"] for t in d["transacoes"]], list(FILA))
        sinais = set(PESOS_PADRAO)
        for t in d["transacoes"]:
            with self.subTest(transacao=t["id"]):
                fraude, golpe, pontos = FILA[t["id"]]
                self.assertEqual(t["fraude"], fraude)
                self.assertEqual(t.get("golpe"), golpe)
                self.assertEqual(pontuar_risco(t, PESOS_PADRAO), pontos)
                self.assertTrue(set(t["sinais"]) <= sinais, t["sinais"])
                self.assertEqual(len(t["sinais"]), len(set(t["sinais"])))
                self.assertFalse({"primeiro_pix", "recebedor_recorrente"} <= set(t["sinais"]))
                self.assertIsInstance(t["valor"], int)
                self.assertGreater(t["valor"], 0)
                self.assertRegex(t["hora"], r"^\d{2}:\d{2}$")
                for campo in ("pagador", "recebedor", "descricao", "explicacao"):
                    self.assertTrue(t[campo].strip(), campo)
                if fraude:
                    self.assertIn(golpe, d["golpes"])
                    self.assertIsInstance(t["analise_evita"], bool)
                    self.assertIn("med", t)
                    self.assertIsInstance(t["med"]["dias_para_contestar"], int)
                    for c in t["med"]["rastreio"]:
                        self.assertTrue(c["conta"].strip())
                        self.assertGreaterEqual(c["saldo"], 0)
                else:
                    self.assertTrue(t["atrito"].strip(), "legítima precisa explicar o custo do atrito")
                    self.assertNotIn("med", t)
        self.assertEqual(sorted(d["golpes"]), sorted(GOLPES))
        golpes = {v[1] for v in FILA.values() if v[0]}
        self.assertEqual(golpes, set(GOLPES), "a fila cobre os quatro golpes típicos")
        self.assertEqual(sum(1 for v in FILA.values() if v[0]), 7)
        self.assertEqual(sum(t["valor"] for t in d["transacoes"] if t["fraude"]), 33130)

    def test_legitimos_que_parecem_suspeitos(self):
        d = self._dados()
        por_id = {t["id"]: t for t in d["transacoes"]}
        self.assertIn("valor_atipico", por_id["T01"]["sinais"], "compra grande de cliente antigo")
        self.assertIn("primeiro_pix", por_id["T04"]["sinais"], "primeiro Pix para um parente de verdade")
        self.assertIn("parente", por_id["T04"]["descricao"])
        # o golpe da falsa central coagido e a compra legítima ao telefone têm os mesmos sinais
        self.assertEqual(sorted(por_id["T08"]["sinais"]), sorted(por_id["T09"]["sinais"]))
        self.assertFalse(por_id["T09"]["analise_evita"], "vítima orientada pelo golpista confirma na análise")
        self.assertFalse(por_id["T03"]["analise_evita"])

    # ------------------------------------------------------------ motor
    def test_pontuacao_e_decisao(self):
        self.assertEqual([decidir(p, LIMIARES_PADRAO) for p in (0, 39, 40, 69, 70, 120)],
                         ["aprovar", "aprovar", "segurar", "segurar", "bloquear", "bloquear"])
        # limiares invertidos: a faixa de segurar some, bloquear tem precedência
        self.assertEqual(decidir(50, {"segurar": 60, "bloquear": 50}), "bloquear")
        self.assertEqual(decidir(55, {"segurar": 60, "bloquear": 50}), "bloquear")
        self.assertEqual(pontuar_risco({"sinais": ["dispositivo_novo", "recebedor_recorrente"]}, PESOS_PADRAO), 5)
        self.assertEqual(pontuar_risco({"sinais": []}, PESOS_PADRAO), 0)

    def test_configuracao_padrao(self):
        d = self._dados()
        r = avaliar_mesa(d, self._pesos(d), d["limiares"])
        self.assertEqual(self._resumo(r), (4, 0, 3, 16800, 16330, 9480, 1580))
        self.assertEqual((r["fraudes"], r["fraudes_passaram"], r["legitimas"], r["seguradas"]), (7, 3, 7, 6))
        dec = {i["id"]: i["decisao"] for i in r["itens"]}
        self.assertEqual(dec, {"T01": "aprovar", "T02": "segurar", "T03": "bloquear", "T04": "aprovar",
                               "T05": "segurar", "T06": "aprovar", "T07": "aprovar", "T08": "segurar",
                               "T09": "segurar", "T10": "segurar", "T11": "aprovar", "T12": "segurar",
                               "T13": "bloquear", "T14": "aprovar"})
        passaram = [i["id"] for i in r["itens"] if i["desfecho"] == "fraude_passou"]
        self.assertEqual(passaram, ["T07", "T09", "T11"])

    def test_mesa_rigida_bloqueia_clientes(self):
        d = self._dados()
        r = avaliar_mesa(d, self._pesos(d), {"segurar": 20, "bloquear": 40})
        self.assertEqual(self._resumo(r), (7, 3, 3, 33130, 0, 0, 0))
        bloqueadas = [i["id"] for i in r["itens"] if i["desfecho"] == "legitima_bloqueada"]
        self.assertEqual(bloqueadas, ["T08", "T10", "T12"])

    def test_mesa_frouxa_deixa_passar(self):
        d = self._dados()
        r = avaliar_mesa(d, self._pesos(d), {"segurar": 80, "bloquear": 100})
        self.assertEqual(self._resumo(r), (1, 0, 0, 4800, 28330, 18780, 6880))
        self.assertEqual([i["id"] for i in r["itens"] if i["desfecho"] == "fraude_evitada"], ["T13"])
        t05 = next(i for i in r["itens"] if i["id"] == "T05")
        self.assertEqual(t05["med"], {"no_prazo": False, "so_original": 0, "med2": 0})

    def test_peso_da_ligacao_troca_fraude_por_atrito(self):
        d = self._dados()
        r = avaliar_mesa(d, self._pesos(d, em_ligacao=40), d["limiares"])
        self.assertEqual(self._resumo(r), (5, 1, 2, 31800, 1330, 980, 380))
        self.assertEqual([i["id"] for i in r["itens"] if i["desfecho"] == "legitima_bloqueada"], ["T08"])

    def test_decisao_manual_vence_a_automatica(self):
        d = self._dados()
        r = avaliar_mesa(d, self._pesos(d), d["limiares"], {"T09": "bloquear", "T08": "aprovar", "T11": "talvez"})
        self.assertEqual(self._resumo(r), (5, 0, 2, 31800, 1330, 980, 380))
        it = {i["id"]: i for i in r["itens"]}
        self.assertEqual((it["T09"]["automatica"], it["T09"]["decisao"]), ("segurar", "bloquear"))
        self.assertEqual(it["T11"]["decisao"], "aprovar", "valor inválido cai na decisão automática")

    def test_med_devolucao_limitada_ao_saldo(self):
        d = self._dados()
        por_id = {t["id"]: t for t in d["transacoes"]}
        self.assertEqual(recuperacao_med(por_id["T11"]), {"no_prazo": True, "so_original": 380, "med2": 380})
        self.assertEqual(recuperacao_med(por_id["T07"]), {"no_prazo": True, "so_original": 0, "med2": 600})
        self.assertEqual(recuperacao_med(por_id["T09"]), {"no_prazo": True, "so_original": 1200, "med2": 8500})
        self.assertEqual(recuperacao_med(por_id["T05"])["no_prazo"], False)
        self.assertGreater(por_id["T05"]["med"]["dias_para_contestar"], PRAZO_CONTESTACAO)
        for t in d["transacoes"]:
            if t["fraude"]:
                with self.subTest(transacao=t["id"]):
                    m = recuperacao_med(t)
                    self.assertLessEqual(m["med2"], t["valor"])
                    self.assertGreaterEqual(m["med2"], m["so_original"])

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
        self.assertIn('id="fpx-dados"', content)
        ini = content.index("JSON.parse(document.getElementById(\"fpx-dados\")")
        motor = content[ini:content.index("</script>", ini)]
        for proibido in ("innerHTML", "outerHTML", "eval(", "new Function", "fetch(", "XMLHttpRequest", "WebSocket",
                         "document.write"):
            self.assertNotIn(proibido, motor, proibido)
        for marcador in ("fpx-lab", "fpx-sinais", "fpx-limiares", "fpx-fila", "fpx-resultado", "fpx-placar",
                         "fpx-med", "pontuarRisco", "decidirTransacao", "avaliarMesa", "simularMed"):
            self.assertIn(marcador, content, marcador)
        self.assertIn("aria-label", motor)
        self.assertIn("textContent", motor)
        self.assertIn('"range"', motor, "pesos e limiares em controles deslizantes")

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        termos = ["falsa central", "falso parente", "conta laranja", "sequestro de conta", "engenharia social",
                  "Mecanismo Especial de Devolução", "MED 2.0", "falso positivo", "atrito", "regras",
                  "pontuação", "dispositivo", "Ipê Pay", "DICT", "rastreio", "saldo", "Banco Central"]
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
        self.assertIn('initChecklist("fraude-em-pagamentos-e-pix")', content)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn(f"{SLUG}/treinamento-fraude-em-pagamentos-e-pix.html", content)
        self.assertIn(f'data-slug="{SLUG}"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)


if __name__ == "__main__":
    unittest.main()
