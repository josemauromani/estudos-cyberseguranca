#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_deteccao_resposta_nuvem.py
Testes automatizados para o Estudo 53: Deteccao-e-Resposta-em-Nuvem

O simulador Conta Comprometida guarda num bloco JSON os eventos de auditoria
fictícios (formato do CloudTrail) da conta da Ipê Store depois que a chave de
acesso de longa duração do usuário ci-deploy-legado vazou num repositório
público, o gabarito das etapas do ataque e o catálogo de ações de contenção.
Este teste espelha em Python as regras do motor JavaScript: eventos visíveis
conforme a configuração da trilha (eventos de dados ligados ou não), filtro
pelas chaves sob investigação, pivô para as credenciais derivadas
(CreateAccessKey e GetSessionToken), linha do tempo do ataque, conferência da
ordem montada pelo aluno e o resultado de cada ordem de contenção (o que
preserva e o que destrói).
"""

import ipaddress
import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402

SLUG = "Deteccao-e-Resposta-em-Nuvem"
VAZADA = "AKIAIOSFODNN7EXAMPLE"
DO_ATACANTE = "AKIAI44QH8DHBEXAMPLE"
SESSAO = "ASIAEXAMPLESESSAO001"
REDES_DOC = [ipaddress.ip_network(n) for n in ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24")]
ACOES = ["registrar", "preservar_logs", "desativar_vazada", "desativar_atacante", "revogar_sessoes",
         "snapshot", "isolar_instancia", "encerrar_instancia", "apagar_usuario", "girar"]
CREDENCIAIS = ("vazada", "atacante", "sessoes")


# ============================================================ eventos
def eventos_visiveis(d, dados_ligados):
    """Espelho de eventosVisiveis: eventos de dados só existem se a trilha os registra."""
    return [e for e in d["eventos"] if e["eventCategory"] != "Data" or dados_ligados]


def eventos_por_chaves(d, chaves, dados_ligados):
    """Espelho de eventosPorChaves: filtro por userIdentity.accessKeyId, na ordem de entrega."""
    return [e for e in eventos_visiveis(d, dados_ligados) if e["userIdentity"].get("accessKeyId") in chaves]


def chaves_derivadas(eventos):
    """Espelho de chavesDerivadas: credenciais emitidas por CreateAccessKey e GetSessionToken bem-sucedidos."""
    novas = []
    for e in eventos:
        if e.get("errorCode"):
            continue
        r = e.get("responseElements") or {}
        if e["eventName"] == "CreateAccessKey":
            novas.append(r["accessKey"]["accessKeyId"])
        elif e["eventName"] == "GetSessionToken":
            novas.append(r["credentials"]["accessKeyId"])
    return novas


def linha_do_tempo(d, chaves, dados_ligados):
    """Espelho de linhaDoTempo: eventos das chaves fora dos IPs conhecidos, ordenados por eventTime."""
    ataque = [e for e in eventos_por_chaves(d, chaves, dados_ligados) if e["sourceIPAddress"] not in d["ips_conhecidos"]]
    ataque.sort(key=lambda e: (e["eventTime"], e["eventID"]))
    return [e["eventID"] for e in ataque]


def conferir_linha(esperado, ordem):
    """Espelho de conferirLinha."""
    return {
        "correta": list(ordem) == list(esperado),
        "na_posicao": sum(1 for k, i in enumerate(ordem) if k < len(esperado) and esperado[k] == i),
        "intrusos": [i for i in ordem if i not in esperado],
        "faltando": [i for i in esperado if i not in ordem],
    }


# ============================================================ contenção
def avaliar_contencao(ordem):
    """Espelho de avaliarContencao: aplica as ações em ordem e diz o que cada uma preserva ou destrói."""
    st = {"registrado": False, "logs": False, "vazada": True, "atacante": True, "sessoes": True,
          "snapshot": False, "instancia": "rodando", "usuario": True}
    passos, com_atacante = [], 0
    for a in ordem:
        if any(st[k] for k in CREDENCIAIS):
            com_atacante += 1
        ef = "nada"
        if a == "registrar":
            if not st["registrado"]:
                st["registrado"], ef = True, "preserva"
        elif a == "preservar_logs":
            if not st["logs"]:
                st["logs"], ef = True, "preserva"
        elif a == "desativar_vazada":
            if st["vazada"]:
                st["vazada"] = False
                ef = "alerta" if st["atacante"] else "ok"
        elif a == "desativar_atacante":
            if st["atacante"]:
                st["atacante"], ef = False, "ok"
        elif a == "revogar_sessoes":
            if st["sessoes"]:
                st["sessoes"], ef = False, "ok"
        elif a == "snapshot":
            if st["instancia"] == "encerrada" and not st["snapshot"]:
                ef = "perdido"
            elif not st["snapshot"]:
                st["snapshot"], ef = True, "preserva"
        elif a == "isolar_instancia":
            if st["instancia"] == "rodando":
                st["instancia"], ef = "isolada", "ok"
        elif a == "encerrar_instancia":
            if st["instancia"] != "encerrada":
                ef = "ok" if st["snapshot"] else "destroi"
                st["instancia"] = "encerrada"
        elif a == "apagar_usuario":
            if st["usuario"]:
                st["usuario"], st["atacante"] = False, False
                ef = "ok" if st["registrado"] else "destroi"
        elif a == "girar":
            st["vazada"] = False
            ef = "ok" if st["registrado"] else "destroi"
        passos.append((a, ef))
    ativos = [k for k in CREDENCIAIS if st[k]]
    destruicoes = [a for a, ef in passos if ef in ("destroi", "perdido")]
    pendencias = []
    if not st["registrado"]:
        pendencias.append("registrar")
    if not st["logs"]:
        pendencias.append("preservar_logs")
    if not st["snapshot"] and st["instancia"] != "encerrada":
        pendencias.append("snapshot")
    if ativos or st["instancia"] == "rodando":
        veredito = "incompleto"
    elif destruicoes:
        veredito = "com_perdas"
    elif pendencias:
        veredito = "sem_preservacao"
    elif com_atacante > 3:
        veredito = "lento"
    else:
        veredito = "ideal"
    return {"passos": passos, "ativos": ativos, "destruicoes": destruicoes, "pendencias": pendencias,
            "instancia": st["instancia"], "com_atacante": com_atacante, "veredito": veredito}


# ============================================================ gabarito do teste
TL_VAZADA = ["e02", "e03", "e04", "e05", "e06", "e07", "e15"]
TL_TODAS_SEM_DADOS = ["e02", "e03", "e04", "e05", "e06", "e07", "e09", "e12", "e15", "e16"]
TL_TODAS_COM_DADOS = ["e02", "e03", "e04", "e05", "e06", "e07", "e09", "e10", "e11", "e12", "e15", "e16"]

ESPERADO_CASOS = {
    "ideal": {"veredito": "ideal", "efeitos": ["ok", "ok", "ok", "preserva", "preserva", "preserva", "ok", "ok", "ok"]},
    "so_vazada": {"veredito": "incompleto", "efeitos": ["alerta"], "ativos": ["atacante", "sessoes"]},
    "pressa": {"veredito": "com_perdas",
               "efeitos": ["destroi", "ok", "destroi", "ok", "perdido", "preserva", "preserva", "ok"],
               "destruicoes": ["apagar_usuario", "encerrar_instancia", "snapshot"]},
    "sem_registro": {"veredito": "sem_preservacao", "efeitos": ["ok", "ok", "ok", "ok", "preserva", "ok"],
                     "pendencias": ["registrar", "preservar_logs"]},
    "lento": {"veredito": "lento",
              "efeitos": ["preserva", "preserva", "preserva", "ok", "ok", "ok", "ok", "ok", "ok"]},
}


class TestDeteccaoRespostaNuvem(unittest.TestCase):
    """Estrutura, conteúdo, simulador e compilação do estudo 53."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "deteccao_e_resposta_em_nuvem_body.html"
        self.compiled_path = self.root / SLUG / "treinamento-deteccao-e-resposta-em-nuvem.html"
        self.portal_path = self.root / "index.html"

    def _body(self):
        return self.body_path.read_text(encoding="utf-8")

    def _dados(self):
        m = re.search(r'<script type="application/json" id="drn-dados">(.*?)</script>', self._body(), re.S)
        self.assertIsNotNone(m, "Bloco JSON #drn-dados ausente no body")
        return json.loads(m.group(1))

    # ------------------------------------------------------------ estrutura
    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_seis_secoes_obrigatorias(self):
        body = self._body()
        ids = re.findall(r'<section class="study-section" id="([\w-]+)"', body)
        self.assertEqual(len(ids), 6, ids)
        self.assertEqual(ids[2:], ["simulador", "checklist", "quiz", "fatos"])
        compilado = self.compiled_path.read_text(encoding="utf-8")
        for n in range(1, 7):
            self.assertIn(f"Seção {n} de {len(ids)}", compilado)
        self.assertIn('data-slug="deteccao-e-resposta-em-nuvem"', body)

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
        for ref in ("Estudo 18", "Estudo 21", "Estudo 41", "Estudo 52"):
            self.assertIn(ref, intro, ref)
        fim = body[body.index('id="fatos"'):body.index("</article>")]
        for ref in ("Trilha 12", "Trilha 13", "Estudo 54"):
            self.assertIn(ref, fim, ref)

    # ---------------------------------------------------------------- dados
    def test_dados_ficticios_e_bem_formados(self):
        d = self._dados()
        self.assertIn(".example", d["contexto"])
        self.assertEqual(d["chave_vazada"], VAZADA)
        ids = [e["eventID"] for e in d["eventos"]]
        self.assertEqual(sorted(ids), [f"e{n:02d}" for n in range(1, 17)])
        self.assertNotEqual(ids, sorted(ids), "a ordem de entrega deve vir misturada")
        for e in d["eventos"]:
            with self.subTest(evento=e["eventID"]):
                for campo in ("eventTime", "eventSource", "eventName", "awsRegion", "sourceIPAddress", "userAgent",
                              "userIdentity", "requestParameters", "eventCategory", "readOnly", "recipientAccountId"):
                    self.assertIn(campo, e)
                self.assertRegex(e["eventTime"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
                self.assertTrue(e["eventSource"].endswith(".amazonaws.com"))
                self.assertIn(e["eventCategory"], ("Management", "Data"))
                ui = e["userIdentity"]
                self.assertIn(ui["type"], ("IAMUser", "AssumedRole"))
                self.assertTrue(ui["arn"].startswith("arn:aws:"))
                self.assertIn("accessKeyId", ui)
                self.assertEqual(e["recipientAccountId"], "111122223333")
                self.assertTrue(any(ipaddress.ip_address(e["sourceIPAddress"]) in r for r in REDES_DOC),
                                e["sourceIPAddress"])
        dados = [e["eventID"] for e in d["eventos"] if e["eventCategory"] == "Data"]
        self.assertEqual(sorted(dados), ["e10", "e11"])
        self.assertTrue(all(e["eventName"] == "GetObject" for e in d["eventos"] if e["eventCategory"] == "Data"))
        texto = json.dumps(d, ensure_ascii=False)
        for chave in re.findall(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b", texto):
            self.assertIn("EXAMPLE", chave, f"chave sem cara de exemplo: {chave}")
        for conta in re.findall(r"\b\d{12}\b", texto):
            self.assertEqual(conta, "111122223333")
        for ip in re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", texto):
            self.assertTrue(any(ipaddress.ip_address(ip) in r for r in REDES_DOC), f"IP fora da RFC 5737: {ip}")
        for host in re.findall(r"\b[\w-]+(?:\.[\w-]+)*\.(?:com|net|org|io|br)\b", texto):
            self.assertTrue(host.endswith("amazonaws.com"), f"domínio real nos dados: {host}")
        self.assertEqual(list(d["acoes"]["ordem"]), ACOES)
        self.assertEqual(sorted(d["acoes"]["itens"]), sorted(ACOES))
        for a, item in d["acoes"]["itens"].items():
            with self.subTest(acao=a):
                self.assertTrue(item["rotulo"] and item["comando"] and item["efeitos"])
        self.assertEqual(sorted(d["gabarito"]), sorted(TL_TODAS_COM_DADOS))

    # -------------------------------------------------------- filtro e pivô
    def test_dados_ligados_mostram_get_object(self):
        d = self._dados()
        sem = {e["eventName"] for e in eventos_visiveis(d, False)}
        com = {e["eventName"] for e in eventos_visiveis(d, True)}
        self.assertNotIn("GetObject", sem)
        self.assertIn("GetObject", com)
        self.assertEqual(len(eventos_visiveis(d, False)), 14)
        self.assertEqual(len(eventos_visiveis(d, True)), 16)
        self.assertFalse(d["trilha_padrao_com_dados"], "a trilha da Ipê Store começa só com gerenciamento")

    def test_filtro_pela_chave_vazada(self):
        d = self._dados()
        evs = eventos_por_chaves(d, [VAZADA], True)
        self.assertEqual(sorted(e["eventID"] for e in evs),
                         ["e01", "e02", "e03", "e04", "e05", "e06", "e07", "e14", "e15"])
        legitimos = [e["eventID"] for e in evs if e["sourceIPAddress"] in d["ips_conhecidos"]]
        self.assertEqual(sorted(legitimos), ["e01", "e14"], "o CI ainda usa a chave: nem todo evento é do atacante")
        self.assertEqual(sorted(chaves_derivadas(evs)), sorted([DO_ATACANTE, SESSAO]))
        self.assertEqual(chaves_derivadas(eventos_por_chaves(d, [DO_ATACANTE, SESSAO], True)), [],
                         "as credenciais derivadas não emitem outras")

    def test_pivo_revela_persistencia(self):
        d = self._dados()
        so_vazada = {e["eventID"] for e in eventos_por_chaves(d, [VAZADA], True)}
        todas = {e["eventID"] for e in eventos_por_chaves(d, [VAZADA, DO_ATACANTE, SESSAO], True)}
        self.assertEqual(sorted(todas - so_vazada), ["e09", "e10", "e11", "e12", "e16"])
        e09 = next(e for e in d["eventos"] if e["eventID"] == "e09")
        self.assertEqual(e09["eventName"], "StopLogging")
        self.assertEqual(e09["errorCode"], "AccessDenied")
        e12 = next(e for e in d["eventos"] if e["eventID"] == "e12")
        self.assertEqual(e12["eventName"], "RunInstances")
        self.assertEqual(e12["responseElements"]["instancesSet"]["items"][0]["instanceId"], d["instancia_atacante"])

    def test_linhas_do_tempo(self):
        d = self._dados()
        self.assertEqual(linha_do_tempo(d, [VAZADA], True), TL_VAZADA)
        self.assertEqual(linha_do_tempo(d, [VAZADA], False), TL_VAZADA)
        self.assertEqual(linha_do_tempo(d, [VAZADA, DO_ATACANTE, SESSAO], False), TL_TODAS_SEM_DADOS)
        self.assertEqual(linha_do_tempo(d, [VAZADA, DO_ATACANTE, SESSAO], True), TL_TODAS_COM_DADOS)
        nomes = [next(e["eventName"] for e in d["eventos"] if e["eventID"] == i) for i in TL_TODAS_COM_DADOS]
        self.assertEqual(nomes[:6], ["GetCallerIdentity", "ListBuckets", "ListAttachedUserPolicies",
                                     "CreateUser", "CreateAccessKey", "AttachUserPolicy"])
        self.assertEqual(d["linha_ideal"], TL_TODAS_COM_DADOS)

    def test_conferir_linha(self):
        r = conferir_linha(TL_VAZADA, TL_VAZADA)
        self.assertTrue(r["correta"])
        r = conferir_linha(TL_VAZADA, ["e01", "e02", "e03", "e05", "e04", "e06", "e07"])
        self.assertFalse(r["correta"])
        self.assertEqual(r["intrusos"], ["e01"])
        self.assertEqual(r["faltando"], ["e15"])
        self.assertEqual(r["na_posicao"], 1, "o intruso desloca tudo; só e05 cai na posição certa")
        r = conferir_linha(TL_VAZADA, ["e02", "e03", "e05", "e04"])
        self.assertEqual(r["na_posicao"], 2)
        self.assertEqual(r["faltando"], ["e06", "e07", "e15"])

    def test_gabarito_das_etapas(self):
        d = self._dados()
        g = d["gabarito"]
        self.assertIn("T1078.004", g["e02"]["tecnica"] + g["e15"]["tecnica"])
        self.assertIn("T1098", g["e06"]["tecnica"])
        self.assertIn("T1098", g["e07"]["tecnica"])
        self.assertIn("T1530", g["e10"]["tecnica"])
        self.assertIn("T1136", g["e05"]["tecnica"])
        self.assertIn("T1562", g["e09"]["tecnica"])
        for i, item in g.items():
            with self.subTest(evento=i):
                self.assertTrue(item["etapa"] and item["nota"])

    # ------------------------------------------------------------ contenção
    def test_casos_de_contencao(self):
        d = self._dados()
        self.assertEqual(sorted(d["casos"]), sorted(ESPERADO_CASOS))
        for nome, caso in d["casos"].items():
            with self.subTest(caso=nome):
                self.assertTrue(set(caso["ordem"]) <= set(ACOES))
                r = avaliar_contencao(caso["ordem"])
                esp = ESPERADO_CASOS[nome]
                self.assertEqual(r["veredito"], esp["veredito"])
                self.assertEqual(caso["veredito"], esp["veredito"])
                self.assertEqual([ef for _, ef in r["passos"]], esp["efeitos"])
                for campo in ("ativos", "destruicoes", "pendencias"):
                    if campo in esp:
                        self.assertEqual(r[campo], esp[campo])

    def test_desativar_so_a_vazada_deixa_persistencia(self):
        r = avaliar_contencao(["desativar_vazada", "registrar", "preservar_logs"])
        self.assertEqual(r["ativos"], ["atacante", "sessoes"])
        self.assertEqual(r["passos"][0][1], "alerta")
        self.assertEqual(r["veredito"], "incompleto")

    def test_apagar_antes_de_registrar_destroi(self):
        self.assertEqual(avaliar_contencao(["apagar_usuario"])["passos"][0][1], "destroi")
        self.assertEqual(avaliar_contencao(["registrar", "apagar_usuario"])["passos"][1][1], "ok")
        self.assertEqual(avaliar_contencao(["girar"])["passos"][0][1], "destroi")
        self.assertEqual(avaliar_contencao(["encerrar_instancia", "snapshot"])["passos"][1][1], "perdido")
        self.assertEqual(avaliar_contencao(["snapshot", "encerrar_instancia"])["passos"][1][1], "ok")
        self.assertEqual(avaliar_contencao(["revogar_sessoes", "revogar_sessoes"])["passos"][1][1], "nada")

    def test_todo_efeito_tem_texto(self):
        d = self._dados()
        itens = d["acoes"]["itens"]
        possiveis = {
            "registrar": {"preserva"}, "preservar_logs": {"preserva"}, "desativar_vazada": {"alerta", "ok"},
            "desativar_atacante": {"ok"}, "revogar_sessoes": {"ok"}, "snapshot": {"preserva", "perdido"},
            "isolar_instancia": {"ok"}, "encerrar_instancia": {"ok", "destroi"}, "apagar_usuario": {"ok", "destroi"},
            "girar": {"ok", "destroi"},
        }
        for a, efs in possiveis.items():
            for ef in efs | {"nada"}:
                with self.subTest(acao=a, efeito=ef):
                    self.assertTrue(itens[a]["efeitos"].get(ef), f"{a}: falta texto para {ef}")
        for v in ("ideal", "lento", "sem_preservacao", "com_perdas", "incompleto"):
            self.assertTrue(d["vereditos"].get(v), v)

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
        self.assertIn('id="drn-dados"', content)
        ini = content.index("JSON.parse(document.getElementById(\"drn-dados\")")
        motor = content[ini:content.index("</script>", ini)]
        for proibido in ("innerHTML", "outerHTML", "eval(", "new Function", "fetch(", "XMLHttpRequest", "WebSocket",
                         "document.write"):
            self.assertNotIn(proibido, motor, proibido)
        for marcador in ("drn-lab", "drn-trilha", "drn-chaves", "drn-pivo", "drn-eventos", "drn-json", "drn-linha",
                         "drn-linha-resultado", "drn-acoes", "drn-sequencia", "drn-contencao", "drn-veredito",
                         "eventosVisiveis", "eventosPorChaves", "chavesDerivadas", "linhaDoTempo", "conferirLinha",
                         "avaliarContencao"):
            self.assertIn(marcador, content, marcador)
        self.assertRegex(content, r'<label[^>]*for="drn-trilha"')
        self.assertIn("aria-label", motor)
        self.assertIn("textContent", motor)

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        termos = ["CloudTrail", "Event history", "90 dias", "trilha", "eventos de gerenciamento", "eventos de dados",
                  "VPC Flow Logs", "Azure Activity Log", "Defender for Cloud", "GuardDuty", "Cloud Audit Logs",
                  "eventTime", "eventSource", "eventName", "userIdentity", "accessKeyId", "sourceIPAddress",
                  "userAgent", "requestParameters", "errorCode", "AccessDenied", "GetCallerIdentity", "ListBuckets",
                  "CreateUser", "CreateAccessKey", "AttachUserPolicy", "GetObject", "GetSessionToken",
                  "aws:TokenIssueTime", "update-access-key", "Inactive", "lookup-events", "snapshot", "Object Lock",
                  "OIDC", "SCP", "persistência", "linha do tempo", "chave de acesso de longa duração",
                  "T1078.004", "T1098", "T1530", "Ipê Store", "AKIAIOSFODNN7EXAMPLE", "111122223333",
                  "Estudo 18", "Estudo 21", "Estudo 41", "Estudo 52", "NIST SP 800-61"]
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
        self.assertIn('initChecklist("deteccao-e-resposta-em-nuvem")', content)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn(f"{SLUG}/treinamento-deteccao-e-resposta-em-nuvem.html", content)
        self.assertIn(f'data-slug="{SLUG}"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)


if __name__ == "__main__":
    unittest.main()
