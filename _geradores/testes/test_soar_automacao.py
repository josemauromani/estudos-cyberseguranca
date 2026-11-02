#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_soar_automacao.py
Testes automatizados para o Estudo 49: SOAR-e-Automacao-de-Resposta

O Montador de Playbook guarda num bloco JSON a fila fictícia de alertas da Ipê
Store, as fontes de enriquecimento (reputação, CMDB e IdP), a lista de exceção
e os custos estimados de cada ação indevida. Este teste espelha em Python o
motor do JavaScript (execução passo a passo, aprovação humana, idempotência,
falhas de fonte, MTTA e MTTR) e valida os resultados esperados de alguns
playbooks de referência.
"""

import ipaddress
import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402

REDES_PRIVADAS = [ipaddress.ip_network(n) for n in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16")]
REDES_DOC = [ipaddress.ip_network(n) for n in ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24")]

ACOES = ("isolar", "bloquear", "desativar")
ENRIQUECIMENTOS = ("rep", "ativo", "usuario")
TIPO_EXCECAO = {"isolar": "host", "bloquear": "indicador", "desativar": "conta"}


# ----------------------------------------------------- espelho do motor JS
def alvo(a, tipo):
    """Espelho de alvoDoBloco: o que cada bloco consulta ou contém neste alerta (None = sem alvo)."""
    if tipo == "rep":
        return a["indicador"]["valor"] if a["indicador"] else None
    if tipo in ("ativo", "isolar"):
        return a["host"]
    if tipo in ("usuario", "desativar"):
        return a["conta"]
    if tipo == "bloquear":
        ind = a["indicador"]
        return ind["valor"] if ind and ind["tipo"] in ("ip", "dominio") else None
    return None


def consultar(d, tipo, valor):
    if tipo == "rep":
        return d["reputacao"][valor]["veredito"]
    if tipo == "ativo":
        return d["ativos"][valor]["tipo"]
    return d["usuarios"][valor]["tipo"]


def avaliar(d, cond, a, ctx):
    """Espelho de avaliarCondicao: True, False ou None (dado ausente ou fonte fora do ar)."""
    if cond == "severidade_alta":
        return a["severidade"] in ("alta", "crítica")
    v = ctx.get(d["condicoes"][cond]["fonte"])
    if v is None or v == "indisponivel":
        return None
    if cond == "rep_maliciosa":
        return v == "maliciosa"
    if cond == "rep_nao_limpa":
        return v in ("maliciosa", "suspeita", "desconhecida")
    if cond == "ativo_estacao":
        return v == "estacao"
    if cond == "conta_comum":
        return v == "comum"
    raise ValueError(cond)


def alto_impacto(d, a, tipo):
    return tipo == "desativar" or (tipo == "isolar" and d["ativos"][a["host"]]["tipo"] == "servidor")


def executar(d, passos, politicas=None, falhas=None):
    """Espelho de executarPlaybook: roda o playbook contra a fila, na ordem, com estado compartilhado."""
    politicas, falhas = politicas or {}, falhas or {}
    P, B = d["parametros"], d["blocos"]
    excecoes = {(e["tipo"], e["valor"]) for e in d["excecoes"]}
    estado = {k: set() for k in ACOES}
    chamados = {}
    res = []
    for a in d["fila"]:
        r = {"id": a["id"], "t": 0, "mtta": None, "mttr": None, "status": "andamento", "ctx": {}, "enriquecido": False,
             "gate": False, "aprov": False, "executadas": [], "efeito": set(), "erradas": [], "negadas": [],
             "aprovadas": [], "idempotentes": [], "chamado": None, "custo": 0, "alto_sem_aprov": 0, "fn": False}

        def escalar():
            r["status"] = "escalado"
            ack = P["ack_escalado_min"] * 60 if r["enriquecido"] else a["manual"]["mtta_min"] * 60
            trab = a["analista_min"] * 60 if r["enriquecido"] else (a["manual"]["mttr_min"] - a["manual"]["mtta_min"]) * 60
            if r["mtta"] is None:
                r["mtta"] = r["t"] + ack
            r["mttr"] = r["t"] + ack + trab

        for p in passos:
            if r["status"] != "andamento":
                break
            tipo = p["tipo"]
            if tipo in ENRIQUECIMENTOS:
                v = alvo(a, tipo)
                if v is None:
                    r["ctx"][tipo] = "sem_alvo"
                elif falhas.get(B[tipo]["fonte"]):
                    r["t"] += P["timeout_s"]
                    r["ctx"][tipo] = "indisponivel"
                else:
                    r["t"] += B[tipo]["duracao_s"]
                    r["ctx"][tipo] = consultar(d, tipo, v)
                    r["enriquecido"] = True
            elif tipo == "decidir":
                ok = avaliar(d, p["condicao"], a, r["ctx"])
                if ok is None and politicas.get("escalar_sem_dado"):
                    escalar()
                elif not ok:
                    if p["senao"] == "encerrar":
                        r["status"] = "encerrado"
                        if r["mtta"] is None:
                            r["mtta"] = r["t"]
                        if a["verdade"] == "malicioso":
                            r["fn"] = True
                            r["custo"] += a["custo_fn"]
                        else:
                            r["mttr"] = r["t"]
                    elif p["senao"] == "escalar":
                        escalar()
                    else:
                        r["gate"] = True
            elif tipo == "aprovacao":
                r["gate"] = True
            elif tipo == "chamado":
                if a["caso"] in chamados:
                    r["t"] += P["chamado_atualizar_s"]
                    r["chamado"] = "atualizado"
                else:
                    r["t"] += B["chamado"]["duracao_s"]
                    chamados[a["caso"]] = a["id"]
                    r["chamado"] = "aberto"
            else:
                v = alvo(a, tipo)
                if v is None:
                    continue
                if v in estado[tipo]:
                    r["t"] += P["idempotente_s"]
                    r["idempotentes"].append(tipo)
                    r["efeito"].add(tipo)
                    continue
                precisa = r["gate"] or (politicas.get("excecoes") and (TIPO_EXCECAO[tipo], v) in excecoes)
                correta = tipo in a["corretas"]
                if precisa:
                    if not r["aprov"]:
                        r["t"] += P["aprovacao_min"] * 60
                        r["aprov"] = True
                    if r["mtta"] is None:
                        r["mtta"] = r["t"]
                    if not correta:
                        r["negadas"].append(tipo)
                        continue
                    r["aprovadas"].append(tipo)
                r["t"] += B[tipo]["duracao_s"]
                estado[tipo].add(v)
                r["executadas"].append(tipo)
                r["efeito"].add(tipo)
                if not precisa:
                    if r["mtta"] is None:
                        r["mtta"] = r["t"]
                    if alto_impacto(d, a, tipo):
                        r["alto_sem_aprov"] += 1
                    if not correta:
                        r["erradas"].append(tipo)
                        r["custo"] += a["erros"][tipo]["custo"]
        if r["status"] == "andamento":
            if a["verdade"] == "malicioso" and all(c in r["efeito"] for c in a["corretas"]):
                r["status"] = "contido"
                r["mttr"] = r["t"]
                if r["mtta"] is None:
                    r["mtta"] = r["t"]
            elif a["verdade"] == "benigno" and r["aprov"] and not r["erradas"]:
                r["status"] = "encerrado_humano"
                r["mttr"] = r["t"]
            else:
                escalar()
        r["sem_registro"] = bool(r["executadas"]) and r["chamado"] is None
        res.append(r)
    return res, chamados


def resumir(d, res):
    """Espelho de resumirExecucao: contagens, custo e médias em segundos."""
    resolvidos = [r for r in res if r["mttr"] is not None]
    manual = {a["id"]: a["manual"] for a in d["fila"]}
    st = [r["status"] for r in res]
    return {
        "contidos": st.count("contido"),
        "encerrados": sum(1 for r in res if r["status"] == "encerrado" and not r["fn"]),
        "encerrados_humano": st.count("encerrado_humano"),
        "escalados": st.count("escalado"),
        "fn": sum(1 for r in res if r["fn"]),
        "aprovacoes": sum(1 for r in res if r["aprov"]),
        "negadas": sum(len(r["negadas"]) for r in res),
        "indevidas": sum(len(r["erradas"]) for r in res),
        "custo": sum(r["custo"] for r in res),
        "alto_sem_aprov": sum(r["alto_sem_aprov"] for r in res),
        "sem_registro": sum(1 for r in res if r["sem_registro"]),
        "mtta_s": sum(r["mtta"] for r in res) / len(res),
        "mttr_s": sum(r["mttr"] for r in resolvidos) / len(resolvidos) if resolvidos else 0,
        "manual_mtta_s": 60 * sum(m["mtta_min"] for m in manual.values()) / len(res),
        "manual_mttr_s": 60 * sum(m["mttr_min"] for m in manual.values()) / len(res),
        "economia_s": sum(manual[r["id"]]["mttr_min"] * 60 - r["mttr"] for r in resolvidos),
    }


def P(tipo, **kw):
    return dict(tipo=tipo, **kw)


REFERENCIA = [P("rep"), P("ativo"), P("usuario"), P("decidir", condicao="rep_nao_limpa", senao="encerrar"), P("chamado"),
              P("decidir", condicao="ativo_estacao", senao="aprovacao"), P("isolar"), P("bloquear"), P("desativar")]
SEGURA = {"excecoes": True, "escalar_sem_dado": True}


class TestSoarAutomacao(unittest.TestCase):
    """Valida a estrutura, o conteúdo, o Montador de Playbook e a compilação do estudo 49."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "soar_e_automacao_de_resposta_body.html"
        self.compiled_path = self.root / "SOAR-e-Automacao-de-Resposta" / "treinamento-soar-e-automacao-de-resposta.html"
        self.portal_path = self.root / "index.html"

    def _dados(self):
        body = self.body_path.read_text(encoding="utf-8")
        m = re.search(r'<script type="application/json" id="soar-dados">(.*?)</script>', body, re.S)
        self.assertIsNotNone(m, "Bloco JSON #soar-dados ausente no body")
        return json.loads(m.group(1))

    def _rodar(self, d, passos, politicas=None, falhas=None):
        res, chamados = executar(d, passos, politicas, falhas)
        return {r["id"]: r for r in res}, resumir(d, res), chamados

    # ------------------------------------------------------------ estrutura
    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_seis_secoes_obrigatorias(self):
        body = self.body_path.read_text(encoding="utf-8")
        ids = re.findall(r'<section class="study-section" id="([\w-]+)"', body)
        self.assertEqual(len(ids), 6, ids)
        self.assertEqual(ids[2:], ["simulador", "checklist", "quiz", "fatos"])
        for n in range(1, 7):
            self.assertIn(f"Seção 0{n}", body)
        self.assertIn('data-slug="soar-e-automacao-de-resposta"', body)

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        termos = ["SOAR", "Security Orchestration, Automation and Response", "orquestração", "playbook", "runbook",
                  "gatilho", "enriquecimento", "reputação", "CMDB", "IdP", "decisão", "human-in-the-loop",
                  "aprovação humana", "idempotência", "idempotente", "lista de exceção", "ativos críticos",
                  "MTTA", "MTTR", "Mean Time to Acknowledge", "Mean Time to Respond", "timeout", "Retry-After",
                  "backoff", "desconhecido não é limpo", "fail-safe", "deduplicação", "trilha de auditoria",
                  "falso positivo", "webhook", "API", "Splunk SOAR", "Cortex XSOAR", "Microsoft Sentinel",
                  "Logic Apps", "Shuffle", "TheHive", "Cortex", "CACAO", "NIST SP 800-61", "art. 20", "LGPD",
                  "Estudo 16", "Estudo 18", "Estudo 35", "Estudo 46", "Estudo 47", "Estudo 48", "RFC 5737"]
        for termo in termos:
            self.assertIn(termo, content, f"Termo obrigatório ausente: {termo}")

    def test_coerencia_com_o_catalogo(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        info = ESTUDOS_DADOS["SOAR-e-Automacao-de-Resposta"]
        self.assertIn(info["simulador_nome"], content)
        self.assertIn(info["pergunta_chave"], content)
        for fato in info["fatos"]:
            self.assertIn(fato, content, fato)

    def test_diferenca_para_o_modulo_18_e_fechamento_da_trilha(self):
        body = self.body_path.read_text(encoding="utf-8")
        intro = body[:body.index('id="simulador"')]
        self.assertIn("Estudo 18", intro)
        self.assertIn("runbook", intro)
        fim = body[body.index('id="fatos"'):body.index("</article>")]
        for ref in ("Estudo 46", "Estudo 47", "Estudo 48", "Trilha 11"):
            self.assertIn(ref, fim, ref)

    # ---------------------------------------------------------------- dados
    def test_dados_ficticios_e_bem_formados(self):
        d = self._dados()
        self.assertIn(".example", d["contexto"])
        self.assertIn("RFC 5737", d["contexto"])
        self.assertEqual(d["ordem_paleta"], list(d["blocos"]))
        self.assertEqual(len(d["fila"]), 10)
        self.assertEqual(len({a["id"] for a in d["fila"]}), 10)
        for a in d["fila"]:
            with self.subTest(alerta=a["id"]):
                self.assertIn(a["verdade"], ("malicioso", "benigno"))
                if a["host"]:
                    self.assertIn(a["host"], d["ativos"])
                if a["conta"]:
                    self.assertIn(a["conta"], d["usuarios"])
                if a["indicador"]:
                    self.assertIn(a["indicador"]["tipo"], ("ip", "dominio", "hash"))
                    self.assertIn(a["indicador"]["valor"], d["reputacao"])
                aplicaveis = [t for t in ACOES if alvo(a, t) is not None]
                self.assertTrue(set(a["corretas"]) <= set(aplicaveis))
                for t in aplicaveis:
                    if t not in a["corretas"]:
                        self.assertIn(t, a["erros"], "toda ação indevida possível tem custo estimado")
                        self.assertGreater(a["erros"][t]["custo"], 0)
                if a["verdade"] == "malicioso":
                    self.assertEqual(a["corretas"], [t for t in a["corretas"] if t in aplicaveis])
                    self.assertTrue(a["corretas"])
                    self.assertEqual(set(aplicaveis), set(a["corretas"]), "em alerta malicioso toda ação aplicável é correta")
                else:
                    self.assertEqual(a["corretas"], [])
                    self.assertEqual(a["custo_fn"], 0)
                self.assertGreater(a["manual"]["mttr_min"], a["manual"]["mtta_min"])
                self.assertLess(a["analista_min"], a["manual"]["mttr_min"] - a["manual"]["mtta_min"])
                self.assertTrue(a["nota"] and a["resumo"])
        for e in d["excecoes"]:
            fonte = {"host": d["ativos"], "indicador": d["reputacao"], "conta": d["usuarios"]}[e["tipo"]]
            self.assertIn(e["valor"], fonte)
            self.assertTrue(e["dono"] and e["motivo"] and re.fullmatch(r"\d{4}-\d{2}-\d{2}", e["revisao"]))
        ips = [v["ip"] for v in d["ativos"].values()] + [k for k in d["reputacao"] if re.fullmatch(r"[\d.]+", k)]
        for ip in ips:
            a = ipaddress.ip_address(ip)
            self.assertTrue(any(a in n for n in REDES_PRIVADAS + REDES_DOC), ip)
        for k in d["reputacao"]:
            if not re.fullmatch(r"[\d.]+|[0-9a-f]{64}", k):
                self.assertTrue(k.endswith(".example"), k)
        self.assertEqual([a["id"] for a in d["fila"] if a["verdade"] == "malicioso"], ["A01", "A02", "A04", "A05", "A06", "A09"])

    def test_ligacao_com_os_estudos_47_e_48(self):
        d = self._dados()
        c2 = [a["id"] for a in d["fila"] if a["indicador"] and a["indicador"]["valor"] == "203.0.113.47"]
        self.assertEqual(c2, ["A01", "A02", "A09"])
        self.assertEqual(d["ativos"]["WS-FIN-03"]["ip"], "10.20.3.13")
        self.assertEqual(d["ativos"]["SRV-PDV-01"]["ip"], "10.20.1.20")
        self.assertEqual(d["reputacao"]["f1b07840b0901638efec072af967f4a17918e98cd97cafce07da2e89855ab92f"]["veredito"], "desconhecida")
        self.assertIn(("host", "SRV-PDV-01"), {(e["tipo"], e["valor"]) for e in d["excecoes"]})
        self.assertIn(("indicador", "198.51.100.60"), {(e["tipo"], e["valor"]) for e in d["excecoes"]})

    # ------------------------------------------------------------ playbooks
    def test_playbook_vazio_reproduz_o_processo_manual(self):
        d = self._dados()
        res, s, chamados = self._rodar(d, [])
        self.assertEqual(s["escalados"], 10)
        self.assertEqual((s["custo"], s["fn"], s["economia_s"]), (0, 0, 0))
        self.assertAlmostEqual(s["mtta_s"], s["manual_mtta_s"])
        self.assertAlmostEqual(s["mttr_s"], s["manual_mttr_s"])
        self.assertAlmostEqual(s["manual_mtta_s"] / 60, 24.8)
        self.assertAlmostEqual(s["manual_mttr_s"] / 60, 76.5)
        self.assertEqual(chamados, {})

    def test_ingenuo_custa_caro(self):
        d = self._dados()
        p = d["presets"]["ingenuo"]
        res, s, _ = self._rodar(d, p["passos"], p["politicas"])
        self.assertEqual(s["custo"], 107300)
        self.assertEqual(s["indevidas"], 7)
        self.assertEqual(s["fn"], 0)
        self.assertEqual(s["contidos"], 6, "contém todo o malicioso...")
        self.assertEqual(res["A03"]["erradas"], ["isolar", "bloquear"], "...isolando o PDV e bloqueando o parceiro")
        self.assertEqual(res["A08"]["erradas"], ["isolar", "desativar"])
        self.assertEqual(s["alto_sem_aprov"], 5, "servidores isolados e contas desativadas sem ninguém olhar")
        self.assertEqual(s["sem_registro"], 0)
        self.assertEqual(res["A02"]["idempotentes"], ["bloquear"])
        self.assertEqual(res["A09"]["idempotentes"], ["isolar", "bloquear"])

    def test_lista_de_excecao_troca_o_prejuizo_por_aprovacao(self):
        d = self._dados()
        p = d["presets"]["ingenuo"]
        res, s, _ = self._rodar(d, p["passos"], dict(p["politicas"], excecoes=True))
        self.assertEqual(s["custo"], 2300, "sobram o hotel bloqueado e a estação da TI isolada")
        self.assertEqual(sorted((r, t) for r in res for t in res[r]["erradas"]), [("A07", "bloquear"), ("A10", "isolar")])
        self.assertEqual(s["negadas"], 5)
        self.assertEqual(s["aprovacoes"], 3)
        self.assertEqual(res["A03"]["status"], "encerrado_humano")
        self.assertEqual(res["A03"]["mttr"], 6 * 60 + 3, "o aprovador nega e o caso fecha logo depois do chamado")

    def test_so_enriquecer_e_escalar(self):
        d = self._dados()
        p = d["presets"]["enriquecer"]
        res, s, chamados = self._rodar(d, p["passos"], p["politicas"])
        self.assertEqual((s["escalados"], s["custo"], s["fn"]), (10, 0, 0))
        self.assertEqual(res["A01"]["mtta"], 4 + 2 + 3 + 8 * 60)
        self.assertEqual(res["A01"]["mttr"], 4 + 2 + 3 + 8 * 60 + 25 * 60)
        self.assertLess(s["mtta_s"], s["manual_mtta_s"] / 2)
        self.assertLess(s["mttr_s"], s["manual_mttr_s"] / 2)
        self.assertEqual(len(chamados), 8, "A01, A05 e A09 compartilham o caso WS-FIN-03")

    def test_referencia_sem_erros(self):
        d = self._dados()
        res, s, chamados = self._rodar(d, REFERENCIA, SEGURA)
        self.assertEqual((s["custo"], s["fn"], s["indevidas"], s["alto_sem_aprov"], s["sem_registro"]), (0, 0, 0, 0, 0))
        self.assertEqual((s["contidos"], s["encerrados"], s["escalados"]), (6, 4, 0))
        self.assertEqual([r for r in res if res[r]["aprov"]], ["A06"], "só a conta comprometida pede aprovação")
        self.assertEqual(res["A06"]["aprovadas"], ["bloquear", "desativar"])
        self.assertEqual(res["A01"]["mtta"], 24)
        self.assertEqual(res["A01"]["mttr"], 32)
        self.assertEqual(res["A06"]["mtta"], 4 + 2 + 3 + 360)
        self.assertEqual(res["A06"]["mttr"], 4 + 2 + 3 + 360 + 8 + 6)
        self.assertLess(s["mtta_s"], 60)
        self.assertLess(s["mttr_s"], 60)
        self.assertGreater(s["economia_s"] / 60, 750)
        # sem a lista de exceção a referência continua sem erro: a decisão por reputação já separa
        self.assertEqual(self._rodar(d, REFERENCIA, dict(SEGURA, excecoes=False))[1]["custo"], 0)

    def test_idempotencia_e_deduplicacao(self):
        d = self._dados()
        res, s, chamados = self._rodar(d, REFERENCIA, SEGURA)
        self.assertEqual(res["A02"]["idempotentes"], ["bloquear"])
        self.assertEqual(res["A05"]["idempotentes"], ["isolar"])
        self.assertEqual(res["A05"]["executadas"], ["bloquear"])
        self.assertEqual(res["A09"]["idempotentes"], ["isolar", "bloquear"])
        self.assertEqual(res["A09"]["executadas"], [])
        self.assertEqual(res["A09"]["status"], "contido")
        self.assertEqual(chamados, {"WS-FIN-03": "A01", "WS-VEN-07": "A02", "WS-VEN-02": "A04", "marina.lopes": "A06"})
        self.assertEqual([res[i]["chamado"] for i in ("A05", "A09")], ["atualizado", "atualizado"])

    def test_desconhecido_nao_e_limpo(self):
        d = self._dados()
        passos = [dict(p) for p in REFERENCIA]
        passos[3]["condicao"] = "rep_maliciosa"
        res, s, _ = self._rodar(d, passos, SEGURA)
        self.assertEqual([r for r in res if res[r]["fn"]], ["A04", "A05"])
        self.assertEqual(s["custo"], 140000)

    def test_fonte_de_reputacao_fora_do_ar(self):
        d = self._dados()
        falhas = {"reputacao": True}
        res, s, _ = self._rodar(d, REFERENCIA, dict(SEGURA, escalar_sem_dado=False), falhas)
        self.assertEqual([r for r in res if res[r]["fn"]], ["A01", "A02", "A04", "A05", "A06", "A09"])
        self.assertEqual(s["custo"], 305000, "sem dado tratado como limpo encerra as ameaças")
        res, s, _ = self._rodar(d, REFERENCIA, SEGURA, falhas)
        self.assertEqual((s["custo"], s["fn"], s["escalados"], s["encerrados"]), (0, 0, 9, 1))
        self.assertEqual(res["A08"]["status"], "encerrado", "sem indicador externo, a queda não afeta o A08")
        self.assertEqual(res["A01"]["mtta"], 30 + 2 + 8 * 60, "o timeout entra no tempo")

    def test_cmdb_fora_do_ar(self):
        d = self._dados()
        falhas = {"cmdb": True}
        res, s, _ = self._rodar(d, REFERENCIA, SEGURA, falhas)
        self.assertEqual((s["custo"], s["fn"]), (0, 0))
        self.assertEqual(sorted(r for r in res if res[r]["status"] == "escalado"), ["A01", "A02", "A04", "A05", "A09"])
        self.assertEqual(res["A06"]["status"], "contido", "A06 não tem host: a CMDB não faz falta")
        res2, s2, _ = self._rodar(d, REFERENCIA, dict(SEGURA, escalar_sem_dado=False), falhas)
        self.assertEqual((s2["custo"], s2["contidos"], s2["aprovacoes"]), (0, 6, 5), "o desvio para aprovação é seguro (A09 já estava contido)")

    def test_decisao_sem_o_enriquecimento_antes(self):
        d = self._dados()
        passos = [P("decidir", condicao="ativo_estacao", senao="encerrar"), P("isolar"), P("chamado")]
        _, s, _ = self._rodar(d, passos, {"escalar_sem_dado": False})
        self.assertEqual((s["fn"], s["encerrados"]), (6, 4))
        _, s, _ = self._rodar(d, passos, {"escalar_sem_dado": True})
        self.assertEqual((s["fn"], s["escalados"]), (0, 10))

    def test_severidade_nao_basta_mas_a_excecao_segura_o_pior(self):
        d = self._dados()
        passos = [P("decidir", condicao="severidade_alta", senao="encerrar"), P("chamado"), P("isolar"), P("bloquear"), P("desativar")]
        res, s, _ = self._rodar(d, passos, {"excecoes": False})
        self.assertEqual(s["custo"], 60000)
        self.assertEqual(res["A03"]["erradas"], ["isolar", "bloquear"])
        res, s, _ = self._rodar(d, passos, {"excecoes": True})
        self.assertEqual(s["custo"], 0)
        self.assertEqual(res["A03"]["negadas"], ["isolar", "bloquear"])
        self.assertEqual(s["alto_sem_aprov"], 1, "a conta da Marina foi desativada sem aprovação")

    # ------------------------------------------------------------ simulador
    def test_simulador_estrutura(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        for marcador in ("soar-lab", 'id="soar-dados"', "soar-contexto", "soar-paleta", "soar-passos", "soar-preset",
                         "soar-pol-excecoes", "soar-pol-escalar", "soar-falha-reputacao", "soar-falha-cmdb",
                         "soar-falha-idp", "soar-placar", "soar-resultados", "soar-fila", "soar-excecoes",
                         "soar-codigo", "executarPlaybook", "resumirExecucao", "rodarPlaybookSoar",
                         "carregarPresetSoar", "adicionarBlocoSoar", "avaliarCondicao", "alvoDoBloco"):
            self.assertIn(marcador, content, marcador)
        for campo in ("soar-preset", "soar-pol-excecoes", "soar-pol-escalar", "soar-falha-reputacao",
                      "soar-falha-cmdb", "soar-falha-idp"):
            self.assertRegex(content, r'<label[^>]*for="%s"' % campo)
        ini = content.index("var SOAR = JSON.parse")
        motor = content[ini:content.index("</script>", ini)]
        for proibido in ("innerHTML", "eval(", "new Function", "fetch(", "XMLHttpRequest", "WebSocket"):
            self.assertNotIn(proibido, motor, proibido)
        self.assertIn("aria-label", motor, "selects e botões gerados dinamicamente têm rótulo acessível")

    def test_componentes_pedagogicos(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        self.assertIn('class="callout', content)
        self.assertIn('class="terminal-box', content)
        self.assertIn('class="diagram-svg-wrap', content)
        self.assertNotIn('<pre class="mermaid"', content)
        self.assertEqual(content.count('class="checklist-item"'), 7)
        self.assertGreaterEqual(content.count('class="quiz-item"'), 6)
        self.assertIn('class="facts-grid', content)
        self.assertIn('initChecklist("soar-e-automacao-de-resposta")', content)
        self.assertNotIn("cdn.", content.lower().replace("cdnjs", "").replace("cdn.example", ""))

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn("SOAR-e-Automacao-de-Resposta/treinamento-soar-e-automacao-de-resposta.html", content)
        self.assertIn('data-slug="SOAR-e-Automacao-de-Resposta"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)


if __name__ == "__main__":
    unittest.main()
