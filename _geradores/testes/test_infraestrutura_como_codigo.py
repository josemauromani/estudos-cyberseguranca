#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_infraestrutura_como_codigo.py
Testes automatizados para o Estudo 52: Infraestrutura-como-Codigo-Segura

O Revisor de Plano Terraform guarda num bloco JSON o pull request fictício da
Ipê Store: trechos de HCL, o plano no formato de `terraform show -json`
(resource_changes e configuration), o catálogo de políticas, as exceções
registradas, o state de produção, as opções de backend e o drift encontrado
por `terraform plan -refresh-only`. Este teste espelha em Python as regras do
motor JavaScript (políticas aplicadas a cada mudança do plano, validade das
exceções, correções padrão, segredos no state, riscos do backend e
classificação do drift) e confere os resultados esperados declarados no JSON.
"""

import copy
import ipaddress
import itertools
import json
import re
import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402

SLUG = "Infraestrutura-como-Codigo-Segura"
REDES_OK = [ipaddress.ip_network(n) for n in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16")]
FLAGS_PAB = ("block_public_acls", "block_public_policy", "ignore_public_acls", "restrict_public_buckets")
ABERTOS = ("0.0.0.0/0", "::/0")
ACOES_AVALIADAS = ("create", "update")


# ============================================================ políticas
def expressoes(plano, address):
    """Expressões do HCL (bloco configuration do plano) para um endereço."""
    for r in plano.get("configuration", {}).get("root_module", {}).get("resources", []):
        if r["address"] == address:
            return r.get("expressions", {})
    return {}


def porta_admin_aberta(d, r):
    """Espelho de portaAdminAberta: evidência se a regra de entrada abre porta administrativa para a internet."""
    abertos = [c for c in (r.get("cidr_blocks") or []) + (r.get("ipv6_cidr_blocks") or []) if c in ABERTOS]
    if not abertos:
        return None
    todas = r.get("protocol") in ("-1", "all")
    portas = [p for p in d["portas_admin"] if todas or r["from_port"] <= p <= r["to_port"]]
    if not portas:
        return None
    return "ingress " + "/".join(str(p) for p in portas) + " de " + abertos[0]


def violacoes(d, rc, expr):
    """Espelho de violacoesRecurso: {politica: [evidências]} na ordem do catálogo (todas as políticas)."""
    ev = {}

    def add(pid, texto):
        ev.setdefault(pid, []).append(texto)

    acoes = rc["change"]["actions"]
    if not any(a in ACOES_AVALIADAS for a in acoes):
        return {}
    after = rc["change"].get("after") or {}
    t = rc["type"]
    # bucket público
    if t == "aws_s3_bucket_public_access_block":
        for k in FLAGS_PAB:
            if after.get(k) is not True:
                add("bucket_publico", f"{k} = false")
    if t == "aws_s3_bucket_acl" and after.get("acl") in ("public-read", "public-read-write"):
        add("bucket_publico", f"acl = {after['acl']}")
    # porta administrativa aberta para a internet
    regras = []
    if t == "aws_security_group":
        regras = after.get("ingress") or []
    elif t == "aws_security_group_rule" and after.get("type") == "ingress":
        regras = [after]
    for r in regras:
        aberta = porta_admin_aberta(d, r)
        if aberta:
            add("porta_admin_aberta", aberta)
    # sem criptografia
    if t == "aws_ebs_volume" and after.get("encrypted") is not True:
        add("sem_criptografia", "encrypted = false")
    if t == "aws_instance":
        for b in after.get("root_block_device") or []:
            if b.get("encrypted") is not True:
                add("sem_criptografia", "root_block_device.encrypted = false")
    if t == "aws_db_instance" and after.get("storage_encrypted") is not True:
        add("sem_criptografia", "storage_encrypted = false")
    if t == "aws_s3_bucket_server_side_encryption_configuration":
        for r in after.get("rule") or []:
            for a in r.get("apply_server_side_encryption_by_default") or []:
                if a.get("sse_algorithm") != "aws:kms":
                    add("sem_criptografia", f"sse_algorithm = {a.get('sse_algorithm')} (exige aws:kms)")
    # log ou trilha de auditoria desligado
    if t == "aws_cloudtrail":
        if after.get("enable_logging") is False:
            add("log_desligado", "enable_logging = false")
        if after.get("enable_log_file_validation") is not True:
            add("log_desligado", "enable_log_file_validation = false")
    if t == "aws_lb":
        logs = after.get("access_logs") or []
        if not logs or logs[0].get("enabled") is not True:
            add("log_desligado", "access_logs.enabled = false")
    # segredo escrito no código
    for attr in d["atributos_secretos"]:
        if "constant_value" in expr.get(attr, {}):
            add("segredo_no_codigo", f"{attr} com valor literal no HCL")
    return {pid: ev[pid] for pid in d["politicas"]["ordem"] if pid in ev}


def dias(a, b):
    return (date.fromisoformat(b) - date.fromisoformat(a)).days


def motivos_excecao(d, exc):
    """Espelho de motivosExcecao: lista vazia = exceção válida na data da revisão."""
    m = []
    if not exc.get("responsavel", "").strip():
        m.append("sem responsável")
    if dias(d["data_revisao"], exc["expira"]) < 0:
        m.append("vencida")
    if dias(exc["criada"], exc["expira"]) > d["prazo_max_dias"]:
        m.append("prazo acima do máximo")
    return m


def avaliar_plano(d, plano, ativas, excecoes=None):
    """Espelho de avaliarPlano: status de cada mudança e veredito do plano."""
    excecoes = d["excecoes"] if excecoes is None else excecoes
    out = []
    for rc in plano["resource_changes"]:
        v = violacoes(d, rc, expressoes(plano, rc["address"]))
        itens = []
        for pid in d["politicas"]["ordem"]:
            if pid not in v or pid not in ativas:
                continue
            exc = next((e for e in excecoes if e["politica"] == pid and e["address"] == rc["address"]), None)
            itens.append({"politica": pid, "evidencias": v[pid], "excecao": exc["id"] if exc else None,
                          "valida": bool(exc) and not motivos_excecao(d, exc)})
        bloq = [i["politica"] for i in itens if not i["valida"]]
        status = "bloqueado" if bloq else ("excecao" if itens else "aprovado")
        out.append({"address": rc["address"], "status": status, "bloqueios": bloq, "itens": itens})
    return {"mudancas": out, "aprovado": not any(m["status"] == "bloqueado" for m in out)}


def corrigir(d, plano, address, pid):
    """Espelho de corrigirPlano: a correção padrão de uma política num recurso, sobre uma cópia do plano."""
    p = copy.deepcopy(plano)
    rc = next(r for r in p["resource_changes"] if r["address"] == address)
    a = rc["change"].get("after") or {}
    t = rc["type"]
    if pid == "bucket_publico":
        if t == "aws_s3_bucket_public_access_block":
            for k in FLAGS_PAB:
                a[k] = True
        if t == "aws_s3_bucket_acl":
            a["acl"] = "private"
    elif pid == "porta_admin_aberta":
        if t == "aws_security_group":
            a["ingress"] = [r for r in a.get("ingress", []) if not porta_admin_aberta(d, r)]
        elif t == "aws_security_group_rule":
            a["cidr_blocks"] = [d["cidr_vpn"]]
            a["ipv6_cidr_blocks"] = []
    elif pid == "sem_criptografia":
        if t == "aws_ebs_volume":
            a["encrypted"] = True
        if t == "aws_instance":
            for b in a.get("root_block_device", []):
                b["encrypted"] = True
        if t == "aws_db_instance":
            a["storage_encrypted"] = True
        if t == "aws_s3_bucket_server_side_encryption_configuration":
            for r in a.get("rule", []):
                for x in r.get("apply_server_side_encryption_by_default", []):
                    x["sse_algorithm"] = "aws:kms"
                    x["kms_master_key_id"] = d["chave_kms"]
    elif pid == "log_desligado":
        if t == "aws_cloudtrail":
            a["enable_logging"] = True
            a["enable_log_file_validation"] = True
        if t == "aws_lb":
            a["access_logs"] = [{"enabled": True, "bucket": d["bucket_logs"], "prefix": "lb"}]
    elif pid == "segredo_no_codigo":
        for r in p.get("configuration", {}).get("root_module", {}).get("resources", []):
            if r["address"] == address:
                for attr in d["atributos_secretos"]:
                    r.get("expressions", {}).pop(attr, None)
                if t == "aws_db_instance":
                    r["expressions"]["manage_master_user_password"] = {"constant_value": True}
        for attr in d["atributos_secretos"]:
            a.pop(attr, None)
        if t == "aws_db_instance":
            a["manage_master_user_password"] = True
    return p


# ================================================================ state
def segredos_no_state(state):
    """Espelho de segredosNoState: (endereço, atributo) marcados como sensíveis, em claro no state."""
    out = []
    for r in state["resources"]:
        addr = f"{r['type']}.{r['name']}"
        for inst in r["instances"]:
            for caminho in inst.get("sensitive_attributes", []):
                attr = caminho[0]["value"]
                if attr in inst["attributes"]:
                    out.append((addr, attr))
    return out


def state_visivel(d, selecao):
    """Espelho de stateVisivel: com a senha gerida pelo provedor, ela sai do state."""
    s = copy.deepcopy(d["state"])
    if "segredo_fora" not in selecao:
        return s
    tira = d["backend"]["remove_do_state"]
    s["resources"] = [r for r in s["resources"] if f"{r['type']}.{r['name']}" not in tira]
    for r in s["resources"]:
        addr = f"{r['type']}.{r['name']}"
        for inst in r["instances"]:
            for item in tira:
                if item.startswith(addr + ":"):
                    attr = item.split(":", 1)[1]
                    inst["attributes"].pop(attr, None)
                    inst["sensitive_attributes"] = [c for c in inst["sensitive_attributes"] if c[0]["value"] != attr]
            if addr in d["backend"].get("acrescenta", {}):
                inst["attributes"].update(d["backend"]["acrescenta"][addr])
    return s


def riscos_backend(d, selecao):
    """Espelho de riscosBackend: opções não atendidas (uma opção que depende de outra só vale com ela)."""
    out = []
    for o in d["backend"]["opcoes"]:
        ok = o["id"] in selecao and (not o.get("depende") or o["depende"] in selecao)
        if not ok:
            out.append(o["id"])
    return out


# ================================================================ drift
def atributos_divergentes(item):
    """Espelho de detectarDrift: atributos de topo cujo valor real difere do código."""
    chaves = list(item["codigo"]) + [k for k in item["real"] if k not in item["codigo"]]
    return [k for k in chaves if item["codigo"].get(k) != item["real"].get(k)]


def risco_drift(d, item):
    """Políticas que o valor real viola e o código não violava."""
    def v(after):
        return violacoes(d, {"address": item["address"], "type": item["type"],
                             "change": {"actions": ["update"], "after": after}}, {})
    antes, depois = v(item["codigo"]), v(item["real"])
    return [pid for pid in depois if pid not in antes]


def decidir_drift(d, item, escolha):
    """Espelho de decidirDrift: incorporar um drift de risco é barrado pela política no próximo plano."""
    risco = risco_drift(d, item)
    if escolha == "incorporar" and risco:
        return "bloqueado"
    return "ok" if escolha == item["recomendado"] else "aceitavel"


# ============================================================ esperados
TODAS = ["bucket_publico", "porta_admin_aberta", "sem_criptografia", "log_desligado", "segredo_no_codigo"]
ESPERADO_VIOLACOES = {
    "aws_s3_bucket.notas_fiscais": [],
    "aws_s3_bucket_public_access_block.notas_fiscais": ["bucket_publico"],
    "aws_s3_bucket_server_side_encryption_configuration.notas_fiscais": ["sem_criptografia"],
    "aws_s3_bucket_public_access_block.vitrine_imagens": ["bucket_publico"],
    "aws_security_group.app_notas": ["porta_admin_aberta"],
    "aws_security_group_rule.lb_https": [],
    "aws_instance.app_notas": ["sem_criptografia"],
    "aws_db_instance.notas": ["sem_criptografia", "segredo_no_codigo"],
    "aws_cloudtrail.principal": ["log_desligado"],
    "aws_lb.notas": ["log_desligado"],
    "aws_ebs_volume.backup_notas": [],
    "aws_security_group.legado_ftp": [],
}
ESPERADO_STATUS = {
    "aws_s3_bucket.notas_fiscais": "aprovado",
    "aws_s3_bucket_public_access_block.notas_fiscais": "bloqueado",
    "aws_s3_bucket_server_side_encryption_configuration.notas_fiscais": "bloqueado",
    "aws_s3_bucket_public_access_block.vitrine_imagens": "excecao",
    "aws_security_group.app_notas": "bloqueado",
    "aws_security_group_rule.lb_https": "aprovado",
    "aws_instance.app_notas": "bloqueado",
    "aws_db_instance.notas": "bloqueado",
    "aws_cloudtrail.principal": "bloqueado",
    "aws_lb.notas": "bloqueado",
    "aws_ebs_volume.backup_notas": "aprovado",
    "aws_security_group.legado_ftp": "aprovado",
}
ESPERADO_EXCECOES = {"EXC-014": [], "EXC-009": ["vencida"], "EXC-021": ["sem responsável", "prazo acima do máximo"]}
ESPERADO_SEGREDOS = [("random_password.pedidos", "result"), ("aws_db_instance.pedidos", "password"),
                     ("aws_iam_access_key.integracao_sefaz", "secret")]
ESPERADO_DRIFT = {
    "aws_security_group.app_pedidos": (["ingress"], ["porta_admin_aberta"]),
    "aws_s3_bucket_public_access_block.relatorios": (["block_public_policy", "restrict_public_buckets"], ["bucket_publico"]),
    "aws_instance.app_pedidos": (["instance_type"], []),
    "aws_s3_bucket.vitrine": (["tags"], []),
}


class TestInfraestruturaComoCodigo(unittest.TestCase):
    """Estrutura, conteúdo, simulador e compilação do estudo 52."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "infraestrutura_como_codigo_segura_body.html"
        self.compiled_path = self.root / SLUG / "treinamento-infraestrutura-como-codigo-segura.html"
        self.portal_path = self.root / "index.html"

    def _body(self):
        return self.body_path.read_text(encoding="utf-8")

    def _dados(self):
        m = re.search(r'<script type="application/json" id="iac-dados">(.*?)</script>', self._body(), re.S)
        self.assertIsNotNone(m, "Bloco JSON #iac-dados ausente no body")
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
        for n in range(1, 7):
            self.assertIn(f"Seção 0{n}", body)
        self.assertIn('data-slug="infraestrutura-como-codigo-segura"', body)

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
        for ref in ("Estudo 21", "Estudo 22", "Estudo 51"):
            self.assertIn(ref, intro, ref)
        fim = body[body.index('id="fatos"'):body.index("</article>")]
        for ref in ("Trilha 12", "Estudo 53"):
            self.assertIn(ref, fim, ref)

    # ---------------------------------------------------------------- dados
    def test_dados_ficticios_e_bem_formados(self):
        d = self._dados()
        self.assertIn(".example", d["contexto"])
        self.assertEqual(d["politicas"]["ordem"], TODAS)
        self.assertEqual(list(d["politicas"]["regras"]), TODAS)
        for pid, r in d["politicas"]["regras"].items():
            with self.subTest(politica=pid):
                self.assertTrue(r["titulo"] and r["porque"] and r["correcao"] and r["rego"] and r["checkov"])
        self.assertEqual(d["portas_admin"], [22, 3389])
        plano = d["plano"]
        self.assertIn("format_version", plano)
        enderecos = [rc["address"] for rc in plano["resource_changes"]]
        self.assertEqual(enderecos, list(ESPERADO_VIOLACOES))
        for rc in plano["resource_changes"]:
            with self.subTest(recurso=rc["address"]):
                self.assertEqual(rc["address"], f"{rc['type']}.{rc['name']}")
                self.assertTrue(set(rc["change"]["actions"]) <= {"create", "update", "delete", "no-op"})
                self.assertIn(rc["address"], d["hcl"], "todo recurso do plano tem o trecho de HCL")
        self.assertIn("delete", [a for rc in plano["resource_changes"] for a in rc["change"]["actions"]])
        texto = json.dumps(d, ensure_ascii=False)
        for ip in re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?:/\d+)?", texto):
            rede = ipaddress.ip_network(ip, strict=False)
            self.assertTrue(rede == ipaddress.ip_network("0.0.0.0/0") or any(rede.subnet_of(n) for n in REDES_OK), ip)
        for host in re.findall(r"\b[\w-]+(?:\.[\w-]+)*\.(?:com|net|org|io|br)\b", texto):
            self.assertTrue(host.endswith("terraform.io"), f"domínio real nos dados: {host}")
        self.assertNotRegex(texto, r"AKIA[0-9A-Z]{16}", "nada com cara de chave AWS real")
        for e in d["excecoes"]:
            self.assertIn(e["politica"], TODAS)
            self.assertIn(e["address"], enderecos)

    # ------------------------------------------------------------- políticas
    def test_violacoes_por_recurso(self):
        d = self._dados()
        plano = d["plano"]
        for rc in plano["resource_changes"]:
            with self.subTest(recurso=rc["address"]):
                v = list(violacoes(d, rc, expressoes(plano, rc["address"])))
                self.assertEqual(v, ESPERADO_VIOLACOES[rc["address"]])
                self.assertEqual(v, rc["esperado"], "o JSON declara as mesmas violações")

    def test_evidencias_principais(self):
        d = self._dados()
        plano = d["plano"]
        rcs = {rc["address"]: rc for rc in plano["resource_changes"]}
        ev = lambda a: violacoes(d, rcs[a], expressoes(plano, a))  # noqa: E731
        self.assertEqual(ev("aws_security_group.app_notas")["porta_admin_aberta"], ["ingress 22 de 0.0.0.0/0"])
        self.assertEqual(ev("aws_s3_bucket_public_access_block.notas_fiscais")["bucket_publico"],
                         ["block_public_policy = false", "restrict_public_buckets = false"])
        self.assertEqual(ev("aws_db_instance.notas")["segredo_no_codigo"], ["password com valor literal no HCL"])
        self.assertEqual(ev("aws_cloudtrail.principal")["log_desligado"], ["enable_logging = false"])
        antes = rcs["aws_security_group.legado_ftp"]["change"]["before"]
        self.assertTrue(any("0.0.0.0/0" in r["cidr_blocks"] for r in antes["ingress"]),
                        "o recurso apagado era inseguro, mas apagar não é bloqueado")
        self.assertEqual(rcs["aws_cloudtrail.principal"]["change"]["before"]["enable_logging"], True,
                         "a trilha está sendo desligada por um update")

    def test_status_com_todas_as_politicas_e_excecoes(self):
        d = self._dados()
        r = avaliar_plano(d, d["plano"], TODAS)
        self.assertEqual({m["address"]: m["status"] for m in r["mudancas"]}, ESPERADO_STATUS)
        self.assertFalse(r["aprovado"])
        self.assertEqual({m["address"]: m["status"] for m in r["mudancas"]},
                         {rc["address"]: rc["status_esperado"] for rc in d["plano"]["resource_changes"]})
        lb = next(m for m in r["mudancas"] if m["address"] == "aws_lb.notas")
        self.assertEqual(lb["itens"][0]["excecao"], "EXC-009", "a exceção vencida existe, mas não vale")

    def test_politicas_desligadas_nao_bloqueiam(self):
        d = self._dados()
        r = avaliar_plano(d, d["plano"], [])
        self.assertTrue(r["aprovado"], "sem política, o plano passa inteiro: é o problema")
        for pid in TODAS:
            with self.subTest(so=pid):
                r = avaliar_plano(d, d["plano"], [pid])
                bloq = sorted(m["address"] for m in r["mudancas"] if m["status"] == "bloqueado")
                esperado = sorted(a for a, v in ESPERADO_VIOLACOES.items() if pid in v and ESPERADO_STATUS[a] == "bloqueado")
                self.assertEqual(bloq, esperado)
        for n in (1, 2, 3):
            for combo in itertools.combinations(TODAS, n):
                bloq_menor = {m["address"] for m in avaliar_plano(d, d["plano"], combo)["mudancas"] if m["status"] == "bloqueado"}
                bloq_todas = {m["address"] for m in avaliar_plano(d, d["plano"], TODAS)["mudancas"] if m["status"] == "bloqueado"}
                self.assertTrue(bloq_menor <= bloq_todas, "ligar mais políticas nunca libera mudança")

    def test_excecoes_com_prazo_e_responsavel(self):
        d = self._dados()
        self.assertEqual({e["id"]: motivos_excecao(d, e) for e in d["excecoes"]}, ESPERADO_EXCECOES)
        self.assertEqual({e["id"]: e["motivos_esperados"] for e in d["excecoes"]}, ESPERADO_EXCECOES)
        sem = avaliar_plano(d, d["plano"], TODAS, excecoes=[])
        st = {m["address"]: m["status"] for m in sem["mudancas"]}
        self.assertEqual(st["aws_s3_bucket_public_access_block.vitrine_imagens"], "bloqueado")
        renovada = [dict(e, criada="2026-10-20", expira="2026-12-31") if e["id"] == "EXC-009" else e for e in d["excecoes"]]
        st = {m["address"]: m["status"] for m in avaliar_plano(d, d["plano"], TODAS, renovada)["mudancas"]}
        self.assertEqual(st["aws_lb.notas"], "excecao", "renovada dentro do prazo e com dono, vale")
        self.assertEqual(d["data_revisao"], "2026-11-02")
        self.assertEqual(d["prazo_max_dias"], 90)
        nova = {"id": "EXC-NOVA", "politica": "porta_admin_aberta", "address": "aws_security_group.app_notas",
                "responsavel": "Ana", "criada": d["data_revisao"], "expira": "2027-01-31"}
        self.assertEqual(motivos_excecao(d, nova), [], "90 dias exatos ainda valem")
        self.assertEqual(motivos_excecao(d, dict(nova, expira="2027-02-01")), ["prazo acima do máximo"])
        self.assertEqual(motivos_excecao(d, dict(nova, responsavel="   ")), ["sem responsável"])
        venc_hoje = dict(nova, expira=d["data_revisao"])
        self.assertEqual(motivos_excecao(d, venc_hoje), [], "vale até o último dia do prazo")

    def test_correcoes_convergem(self):
        d = self._dados()
        original = copy.deepcopy(d["plano"])
        p = d["plano"]
        for rc in original["resource_changes"]:
            for pid in ESPERADO_VIOLACOES[rc["address"]]:
                p = corrigir(d, p, rc["address"], pid)
        r = avaliar_plano(d, p, TODAS, excecoes=[])
        self.assertTrue(r["aprovado"])
        self.assertEqual([m["status"] for m in r["mudancas"]], ["aprovado"] * len(original["resource_changes"]))
        self.assertEqual(d["plano"], original, "corrigir trabalha sobre cópia")
        for rc in original["resource_changes"]:
            for pid in ESPERADO_VIOLACOES[rc["address"]]:
                with self.subTest(recurso=rc["address"], politica=pid):
                    p1 = corrigir(d, original, rc["address"], pid)
                    rc1 = next(x for x in p1["resource_changes"] if x["address"] == rc["address"])
                    self.assertNotIn(pid, violacoes(d, rc1, expressoes(p1, rc["address"])))
                    self.assertEqual(corrigir(d, p1, rc["address"], pid), p1, "corrigir de novo não muda nada")
        sg = corrigir(d, original, "aws_security_group.app_notas", "porta_admin_aberta")
        rc = next(x for x in sg["resource_changes"] if x["address"] == "aws_security_group.app_notas")
        self.assertEqual([r["from_port"] for r in rc["change"]["after"]["ingress"]], [443], "o HTTPS interno fica")

    def test_casos_de_calibracao(self):
        d = self._dados()
        self.assertGreaterEqual(len(d["casos"]), 8)
        for caso in d["casos"]:
            with self.subTest(caso=caso["nome"]):
                rc = {"address": f"{caso['type']}.caso", "type": caso["type"],
                      "change": {"actions": caso.get("actions", ["create"]), "after": caso["after"]}}
                self.assertEqual(list(violacoes(d, rc, caso.get("expressions", {}))), caso["esperado"])

    # ---------------------------------------------------------------- state
    def test_state_contem_segredos(self):
        d = self._dados()
        self.assertEqual(segredos_no_state(d["state"]), ESPERADO_SEGREDOS)
        db = next(r for r in d["state"]["resources"] if r["type"] == "aws_db_instance")
        rnd = next(r for r in d["state"]["resources"] if r["type"] == "random_password")
        self.assertEqual(db["instances"][0]["attributes"]["password"], rnd["instances"][0]["attributes"]["result"],
                         "a senha gerada por random_password também fica em claro no state")
        sel = [o["id"] for o in d["backend"]["opcoes"]]
        self.assertEqual(segredos_no_state(state_visivel(d, sel)), [("aws_iam_access_key.integracao_sefaz", "secret")],
                         "senha gerida pelo provedor sai do state; a chave de acesso continua lá")
        self.assertEqual(state_visivel(d, []), d["state"])

    def test_riscos_do_backend(self):
        d = self._dados()
        ids = [o["id"] for o in d["backend"]["opcoes"]]
        self.assertEqual(ids, ["remoto", "criptografia", "bloqueio", "versionamento", "acesso", "gitignore", "segredo_fora"])
        self.assertEqual(riscos_backend(d, ids), [])
        self.assertEqual(riscos_backend(d, []), ids)
        sem_remoto = [i for i in ids if i != "remoto"]
        self.assertEqual(riscos_backend(d, sem_remoto), ["remoto", "criptografia", "bloqueio", "versionamento", "acesso"],
                         "criptografia, bloqueio, versão e acesso do bucket só existem com backend remoto")
        self.assertEqual(riscos_backend(d, d["backend"]["inicial"]), [i for i in ids if i not in d["backend"]["inicial"]])
        for o in d["backend"]["opcoes"]:
            self.assertTrue(o["rotulo"] and o["risco"])

    # ---------------------------------------------------------------- drift
    def test_drift_detectado_e_classificado(self):
        d = self._dados()
        itens = d["drift"]["recursos"]
        self.assertEqual([i["address"] for i in itens], list(ESPERADO_DRIFT))
        for item in itens:
            with self.subTest(recurso=item["address"]):
                self.assertEqual((atributos_divergentes(item), risco_drift(d, item)), ESPERADO_DRIFT[item["address"]])
                self.assertEqual(atributos_divergentes(item), item["esperado"]["atributos"])
                self.assertEqual(risco_drift(d, item), item["esperado"]["risco"])
                self.assertEqual(item["recomendado"], "reverter" if risco_drift(d, item) else "incorporar")
        self.assertTrue(d["drift"]["nao_gerenciados"], "há recurso criado fora do Terraform, que o plan não vê")
        for x in d["drift"]["nao_gerenciados"]:
            self.assertNotIn(x["nome"], [i["address"] for i in itens])

    def test_decisoes_de_drift(self):
        d = self._dados()
        it = {i["address"]: i for i in d["drift"]["recursos"]}
        self.assertEqual(decidir_drift(d, it["aws_security_group.app_pedidos"], "reverter"), "ok")
        self.assertEqual(decidir_drift(d, it["aws_security_group.app_pedidos"], "incorporar"), "bloqueado")
        self.assertEqual(decidir_drift(d, it["aws_s3_bucket_public_access_block.relatorios"], "incorporar"), "bloqueado")
        self.assertEqual(decidir_drift(d, it["aws_instance.app_pedidos"], "incorporar"), "ok")
        self.assertEqual(decidir_drift(d, it["aws_instance.app_pedidos"], "reverter"), "aceitavel")
        self.assertEqual(decidir_drift(d, it["aws_s3_bucket.vitrine"], "incorporar"), "ok")

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
        self.assertIn('id="iac-dados"', content)
        ini = content.index("JSON.parse(document.getElementById(\"iac-dados\")")
        motor = content[ini:content.index("</script>", ini)]
        for proibido in ("innerHTML", "outerHTML", "eval(", "new Function", "fetch(", "XMLHttpRequest", "WebSocket",
                         "document.write"):
            self.assertNotIn(proibido, motor, proibido)
        for marcador in ("iac-lab", "iac-recursos", "iac-hcl", "iac-json", "iac-politicas", "iac-resultado",
                         "iac-veredito", "iac-palpites-resultado", "iac-exc-recurso", "iac-exc-responsavel",
                         "iac-exc-prazo", "iac-exc-resultado", "iac-state", "iac-backend", "iac-backend-hcl",
                         "iac-backend-riscos", "iac-drift", "iac-drift-resultado",
                         "violacoesRecurso", "motivosExcecao", "avaliarPlano", "corrigirPlano", "segredosNoState",
                         "stateVisivel", "riscosBackend", "detectarDrift", "riscoDrift", "decidirDrift"):
            self.assertIn(marcador, content, marcador)
        for campo in ("iac-exc-recurso", "iac-exc-responsavel", "iac-exc-prazo"):
            self.assertRegex(content, r'<label[^>]*for="%s"' % campo)
        self.assertIn("aria-label", motor)
        self.assertIn("textContent", motor)

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        termos = ["Terraform", "OpenTofu", "HCL", "declarativ", "terraform plan", "terraform apply",
                  "terraform show -json", "resource_changes", "state", "terraform.tfstate", "backend",
                  "use_lockfile", "DynamoDB", "encrypt", "sensitive", "random_password", "manage_master_user_password",
                  "módulos aprovados", "Checkov", "tfsec", "Trivy", "OPA", "Rego", "Conftest", "policy-as-code",
                  "exceção", "prazo", "responsável", "drift", "-refresh-only", "terraform import", "CSPM",
                  "0.0.0.0/0", "Block Public Access", "CloudTrail", "KMS", "OIDC", "pull request",
                  "T1578", "T1530", "Ipê Store", "Estudo 21", "Estudo 22", "Estudo 51", "CIS"]
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
        self.assertIn('initChecklist("infraestrutura-como-codigo-segura")', content)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn(f"{SLUG}/treinamento-infraestrutura-como-codigo-segura.html", content)
        self.assertIn(f'data-slug="{SLUG}"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)


if __name__ == "__main__":
    unittest.main()
