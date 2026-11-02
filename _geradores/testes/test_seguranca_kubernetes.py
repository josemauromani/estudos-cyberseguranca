#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_seguranca_kubernetes.py
Testes automatizados para o Estudo 51: Seguranca-em-Kubernetes

O Cluster em Miniatura guarda num bloco JSON o cluster fictício da Ipê Store:
manifestos de pod, contas de serviço, bindings de RBAC, segredos de token,
pods em execução e NetworkPolicies. Este teste espelha em Python as regras das
três fases do motor JavaScript (violações do Pod Security Standards por
manifesto, caminhos de escalação no RBAC e alcançabilidade entre pods dada a
NetworkPolicy) e confere os resultados esperados declarados no JSON.
"""

import copy
import ipaddress
import itertools
import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402

SLUG = "Seguranca-em-Kubernetes"
REDES_PRIVADAS = [ipaddress.ip_network(n) for n in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16")]
NIVEIS = ["privileged", "baseline", "restricted"]
SECCOMP_OK = ("RuntimeDefault", "Localhost")
ADMIN = "cluster-admin"


# ============================================== fase 1: Pod Security Standards
def avaliar_pod(d, spec):
    """Espelho de avaliarPod: achados por regra (na ordem do catálogo), nível de cada achado e nível atendido."""
    pss = d["pss"]
    ev = {}

    def add(rid, texto):
        ev.setdefault(rid, []).append(texto)

    psc = spec.get("securityContext", {})
    cs = spec.get("containers", [])
    for c in cs:
        if c.get("securityContext", {}).get("privileged") is True:
            add("privileged", f"{c['name']}: privileged: true")
    for k in ("hostNetwork", "hostPID", "hostIPC"):
        if spec.get(k) is True:
            add("host_namespaces", f"{k}: true")
    for v in spec.get("volumes", []):
        if "hostPath" in v:
            add("host_path", f"volume {v['name']}: hostPath {v['hostPath']['path']}")
    cap_baseline = False
    for c in cs:
        caps = c.get("securityContext", {}).get("capabilities", {})
        if "ALL" not in [x.upper() for x in caps.get("drop", [])]:
            add("capabilities", f"{c['name']}: não remove ALL")
        for cap in [x.upper() for x in caps.get("add", [])]:
            if cap != "NET_BIND_SERVICE":
                add("capabilities", f"{c['name']}: adiciona {cap}")
                if cap not in pss["caps_baseline"]:
                    cap_baseline = True
    unconfined = False
    pod_t = psc.get("seccompProfile", {}).get("type")
    if pod_t == "Unconfined":
        unconfined = True
        add("seccomp", "pod: seccompProfile Unconfined")
    for c in cs:
        ct = c.get("securityContext", {}).get("seccompProfile", {}).get("type")
        if ct == "Unconfined":
            unconfined = True
            add("seccomp", f"{c['name']}: seccompProfile Unconfined")
        elif ct is None and pod_t is None:
            add("seccomp", f"{c['name']}: sem seccompProfile (nem no pod)")
    if psc.get("runAsUser") == 0:
        add("run_as_non_root", "pod: runAsUser: 0")
    for c in cs:
        sc = c.get("securityContext", {})
        if sc.get("runAsUser") == 0:
            add("run_as_non_root", f"{c['name']}: runAsUser: 0")
        nr = sc["runAsNonRoot"] if "runAsNonRoot" in sc else psc.get("runAsNonRoot")
        if nr is not True:
            add("run_as_non_root", f"{c['name']}: runAsNonRoot " + ("false" if nr is False else "ausente"))
    for c in cs:
        ape = c.get("securityContext", {}).get("allowPrivilegeEscalation")
        if ape is not False:
            add("allow_privilege_escalation", f"{c['name']}: allowPrivilegeEscalation " + ("true" if ape is True else "ausente"))
    achados = []
    for rid in pss["ordem_regras"]:
        if rid not in ev:
            continue
        nivel = pss["regras"][rid]["nivel"]
        if (rid == "capabilities" and cap_baseline) or (rid == "seccomp" and unconfined):
            nivel = "baseline"
        achados.append({"id": rid, "nivel": nivel, "evidencias": ev[rid]})
    if any(a["nivel"] == "baseline" for a in achados):
        atende = "privileged"
    elif achados:
        atende = "baseline"
    else:
        atende = "restricted"
    return {"achados": achados, "ids": [a["id"] for a in achados], "atende": atende}


def admitido(atende, exigido):
    """Espelho de admitidoPsa: o Pod Security Admission aceita o pod se ele atende ao nível do namespace."""
    return NIVEIS.index(atende) >= NIVEIS.index(exigido)


def corrigir_pod(spec, rid):
    """Espelho de corrigirPod: a correção padrão de cada regra, sobre uma cópia do spec."""
    s = copy.deepcopy(spec)
    cs = s.get("containers", [])
    if rid == "privileged":
        for c in cs:
            if c.get("securityContext", {}).get("privileged") is True:
                c["securityContext"]["privileged"] = False
    elif rid == "host_namespaces":
        for k in ("hostNetwork", "hostPID", "hostIPC"):
            if s.get(k) is True:
                del s[k]
    elif rid == "host_path":
        s["volumes"] = [{"name": v["name"], "emptyDir": {}} if "hostPath" in v else v for v in s.get("volumes", [])]
    elif rid == "capabilities":
        for c in cs:
            caps = c.setdefault("securityContext", {}).setdefault("capabilities", {})
            caps["drop"] = ["ALL"]
            add = [x for x in caps.get("add", []) if x.upper() == "NET_BIND_SERVICE"]
            if add:
                caps["add"] = add
            else:
                caps.pop("add", None)
    elif rid == "seccomp":
        s.setdefault("securityContext", {})["seccompProfile"] = {"type": "RuntimeDefault"}
        for c in cs:
            sc = c.get("securityContext", {})
            if "seccompProfile" in sc and sc["seccompProfile"].get("type") not in SECCOMP_OK:
                del sc["seccompProfile"]
    elif rid == "run_as_non_root":
        psc = s.setdefault("securityContext", {})
        psc["runAsNonRoot"] = True
        if psc.get("runAsUser") == 0:
            psc["runAsUser"] = 10001
        for c in cs:
            sc = c.get("securityContext", {})
            if sc.get("runAsNonRoot") is False:
                del sc["runAsNonRoot"]
            if sc.get("runAsUser") == 0:
                sc["runAsUser"] = 10001
    elif rid == "allow_privilege_escalation":
        for c in cs:
            c.setdefault("securityContext", {})["allowPrivilegeEscalation"] = False
    return s


# ======================================================== fase 2: RBAC
def ns_da_conta(conta):
    return conta.split(":", 1)[0]


def permissoes(rb, conta):
    """(escopo, regra, binding): RoleBinding vale no namespace dele; ClusterRoleBinding, no cluster todo ('*')."""
    out = []
    for b in rb["bindings"]:
        if conta in b["sujeitos"]:
            escopo = "*" if b["tipo"] == "ClusterRoleBinding" else b["ns"]
            for r in b["regras"]:
                out.append((escopo, r, b["id"]))
    return out


def concede(perms, verbo, recurso, ns):
    """Bindings que dão o verbo no recurso; ns='*' exige escopo de cluster."""
    out = []
    for escopo, r, bid in perms:
        if (verbo in r["verbos"] or "*" in r["verbos"]) and (recurso in r["recursos"] or "*" in r["recursos"]) \
                and (escopo == "*" or escopo == ns) and bid not in out:
            out.append(bid)
    return out


def unir(*listas):
    out = []
    for lst in listas:
        for x in lst:
            if x not in out:
                out.append(x)
    return out


def arestas(rb, conta):
    """Espelho de arestasRbac: para onde a conta consegue ir, por qual motivo e graças a quais bindings."""
    p = permissoes(rb, conta)
    out = []
    cur = [bid for escopo, r, bid in p if escopo == "*" and "*" in r["verbos"] and "*" in r["recursos"]]
    if cur:
        out.append((ADMIN, "curinga", unir(cur)))
    b1, b2 = concede(p, "create", "clusterrolebindings", "*"), concede(p, "bind", "clusterroles", "*")
    if b1 and b2:
        out.append((ADMIN, "bind", unir(b1, b2)))
    e1 = concede(p, "escalate", "clusterroles", "*")
    e2 = unir(concede(p, "update", "clusterroles", "*"), concede(p, "patch", "clusterroles", "*"))
    if e1 and e2:
        out.append((ADMIN, "escalate", unir(e1, e2)))
    for t in rb["contas"]:
        if t == conta:
            continue
        ns = ns_da_conta(t)
        g = concede(p, "impersonate", "serviceaccounts", ns)
        if g:
            out.append((t, "personificar", g))
        g = unir(*[concede(p, "create", rec, ns) for rec in rb["recursos_de_carga"]])
        if g:
            out.append((t, "criar_pods", g))
        g = []
        for s in rb["segredos"]:
            if s["conta"] == t:
                g = unir(g, concede(p, "get", "secrets", s["ns"]), concede(p, "list", "secrets", s["ns"]))
        if g:
            out.append((t, "ler_segredos", g))
        g = []
        for pod in rb["pods"]:
            if pod["conta"] == t:
                g = unir(g, concede(p, "create", "pods/exec", pod["ns"]))
        if g:
            out.append((t, "exec", g))
    return out


def caminho(rb, origem):
    """Espelho de caminhoRbac: busca em largura até o cluster-admin; devolve (caminho de nós, alcançáveis)."""
    pai, fila, vistos = {origem: None}, [origem], [origem]
    achou = None
    while fila:
        u = fila.pop(0)
        if u == ADMIN:
            continue
        for para, motivo, bids in arestas(rb, u):
            if para in pai:
                continue
            pai[para] = (u, motivo, bids)
            vistos.append(para)
            if para == ADMIN and achou is None:
                achou = para
            fila.append(para)
    nos = None
    if achou:
        nos, x = [], ADMIN
        while x is not None:
            nos.insert(0, x)
            x = pai[x][0] if pai[x] else None
    return nos, [v for v in vistos if v != ADMIN]


def aplicar_mudancas(rb, mudancas):
    """Espelho de aplicarMudancasRbac: 'remover' apaga o binding; 'restringir' aplica a restrição sugerida."""
    out = copy.deepcopy(rb)
    novos = []
    for b in out["bindings"]:
        m = mudancas.get(b["id"], "manter")
        if m == "remover":
            continue
        if m == "restringir" and b.get("restricao"):
            for k in ("tipo", "ns", "regras"):
                if k in b["restricao"]:
                    b[k] = b["restricao"][k]
        novos.append(b)
    out["bindings"] = novos
    return out


def avaliar_rbac(rb, mudancas):
    r = aplicar_mudancas(rb, mudancas)
    nos, alc = caminho(r, rb["comprometida"])
    ess = [b["id"] for b in rb["bindings"] if b["essencial"] and mudancas.get(b["id"]) == "remover"]
    return {"caminho": nos, "admin": nos is not None, "alcancaveis": alc, "essenciais_removidos": ess}


# ================================================== fase 3: NetworkPolicy
def casa_seletor(pol, pod):
    return pod["ns"] == pol["ns"] and all(pod.get(k) == v for k, v in pol["seletor"].items())


def casa_peer(peer, pol_ns, pod):
    if pod.get("externo"):
        return False  # seletor de namespace ou de pod nunca casa com endereço fora do cluster
    ns = peer.get("ns", pol_ns)
    return (ns == "*" or ns == pod["ns"]) and ("app" not in peer or peer["app"] == pod["app"])


def regra_ok(regra, campo, pol_ns, pod, porta):
    peers = regra.get(campo)
    if peers is not None and not any(casa_peer(x, pol_ns, pod) for x in peers):
        return False
    portas = regra.get("portas") or []
    return not portas or porta in portas


def permitido(pols, origem, destino):
    """Espelho de permitidoNp: a saída da origem e a entrada do destino precisam permitir a conexão."""
    porta = destino["porta"]
    saida = [p for p in pols if "Egress" in p["tipos"] and casa_seletor(p, origem)]
    if saida and not any(regra_ok(r, "para", p["ns"], destino, porta) for p in saida for r in p.get("egress", [])):
        return False
    entrada = [p for p in pols if "Ingress" in p["tipos"] and casa_seletor(p, destino)]
    if entrada and not any(regra_ok(r, "de", p["ns"], origem, porta) for p in entrada for r in p.get("ingress", [])):
        return False
    return True


def avaliar_rede(rede, ids, extras=(), origem=None, pods_extra=()):
    """Espelho de avaliarRede: pods alcançáveis a partir do comprometido e fluxos legítimos quebrados."""
    pols = [p for p in rede["politicas"] if p["id"] in ids] + list(extras)
    todos = rede["pods"] + list(pods_extra)
    pods = {p["nome"]: p for p in todos}
    comp = pods[origem or rede["comprometido"]]
    alc = [p["nome"] for p in todos if p is not comp and permitido(pols, comp, p)]
    quebrados = [f"{f['de']}->{f['para']}" for f in rede["fluxos"] if not permitido(pols, pods[f["de"]], pods[f["para"]])]
    return {"alcancaveis": alc, "quebrados": quebrados}


def liberacao(rede, tipo, de, para):
    """Espelho de criarLiberacaoNp: a política que o formulário gera (entrada no destino ou saída na origem)."""
    pods = {p["nome"]: p for p in rede["pods"]}
    o, t = pods[de], pods[para]
    if tipo == "entrada":
        return {"id": f"lib-{de}-{para}-entrada", "ns": t["ns"], "seletor": {"app": t["app"]}, "tipos": ["Ingress"],
                "ingress": [{"de": [{"ns": o["ns"], "app": o["app"]}], "portas": [t["porta"]]}]}
    return {"id": f"lib-{de}-{para}-saida", "ns": o["ns"], "seletor": {"app": o["app"]}, "tipos": ["Egress"],
            "egress": [{"para": [{"ns": t["ns"], "app": t["app"]}], "portas": [t["porta"]]}]}


# ============================================================ esperados
ESPERADO_PSS = {
    "api-pedidos": ["capabilities", "seccomp", "run_as_non_root", "allow_privilege_escalation"],
    "coletor-logs": ["privileged", "host_namespaces", "host_path", "capabilities", "seccomp", "run_as_non_root",
                     "allow_privilege_escalation"],
    "worker-relatorios": ["capabilities", "run_as_non_root", "allow_privilege_escalation"],
    "vitrine-web": ["seccomp"],
}
ATENDE = {"api-pedidos": "baseline", "coletor-logs": "privileged", "worker-relatorios": "privileged",
          "vitrine-web": "baseline"}
API, MIG, DEP, OPL = "pedidos:sa-api-pedidos", "pedidos:sa-migracoes", "ci:sa-deployer", "kube-system:sa-operador-legado"


class TestSegurancaKubernetes(unittest.TestCase):
    """Estrutura, conteúdo, simulador e compilação do estudo 51."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "seguranca_em_kubernetes_body.html"
        self.compiled_path = self.root / SLUG / "treinamento-seguranca-em-kubernetes.html"
        self.portal_path = self.root / "index.html"

    def _body(self):
        return self.body_path.read_text(encoding="utf-8")

    def _dados(self):
        m = re.search(r'<script type="application/json" id="k8s-dados">(.*?)</script>', self._body(), re.S)
        self.assertIsNotNone(m, "Bloco JSON #k8s-dados ausente no body")
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
        self.assertIn('data-slug="seguranca-em-kubernetes"', body)

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
        for ref in ("Estudo 50", "Estudo 04"):
            self.assertIn(ref, intro, ref)
        fim = body[body.index('id="fatos"'):body.index("</article>")]
        for ref in ("Trilha 12", "Estudo 52", "Estudo 53"):
            self.assertIn(ref, fim, ref)

    # ---------------------------------------------------------------- dados
    def test_dados_ficticios_e_bem_formados(self):
        d = self._dados()
        self.assertIn(".example", d["contexto"])
        self.assertEqual(d["niveis"], NIVEIS)
        pss = d["pss"]
        self.assertEqual(pss["ordem_regras"], list(pss["regras"]))
        self.assertEqual(len(pss["regras"]), 7)
        for rid, r in pss["regras"].items():
            with self.subTest(regra=rid):
                self.assertIn(r["nivel"], ("baseline", "restricted"))
                self.assertTrue(r["titulo"] and r["porque"] and r["correcao"])
        self.assertEqual([m["id"] for m in pss["manifestos"]], list(ESPERADO_PSS))
        for m in pss["manifestos"]:
            self.assertIn(pss["namespaces"][m["ns"]], NIVEIS)
        texto = json.dumps(d, ensure_ascii=False)
        for ip in re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", texto):
            self.assertTrue(any(ipaddress.ip_address(ip) in n for n in REDES_PRIVADAS), ip)
        for host in re.findall(r"\b[\w-]+(?:\.[\w-]+)*\.(?:com|net|org|io|br)\b", texto):
            self.assertTrue(host.endswith("kubernetes.io"), f"domínio real nos dados: {host}")
        rb = d["rbac"]
        ids = [b["id"] for b in rb["bindings"]]
        self.assertEqual(len(ids), len(set(ids)))
        for b in rb["bindings"]:
            with self.subTest(binding=b["id"]):
                self.assertIn(b["tipo"], ("RoleBinding", "ClusterRoleBinding"))
                if b["tipo"] == "RoleBinding":
                    self.assertTrue(b["ns"])
                self.assertTrue(b["uso"] and b["role"])
        for x in rb["segredos"] + rb["pods"]:
            self.assertIn(x["conta"], rb["contas"])
            self.assertEqual(ns_da_conta(x["conta"]), x["ns"], "token e pod ficam no namespace da conta")
        self.assertEqual(set(rb["motivos"]), {"curinga", "bind", "escalate", "personificar", "criar_pods",
                                              "ler_segredos", "exec"})
        verbos = {v for b in rb["bindings"] for r in b["regras"] for v in r["verbos"]}
        for perigoso in ("create", "get", "bind", "impersonate", "*"):
            self.assertIn(perigoso, verbos, perigoso)
        rede = d["rede"]
        nomes = [p["nome"] for p in rede["pods"]]
        self.assertIn(rede["comprometido"], nomes)
        for f in rede["fluxos"]:
            self.assertIn(f["de"], nomes)
            self.assertIn(f["para"], nomes)
        self.assertTrue(set(rede["referencia"]) <= {p["id"] for p in rede["politicas"]})
        self.assertTrue(any(p.get("armadilha") for p in rede["politicas"]))

    # --------------------------------------------------------------- fase 1
    def test_violacoes_pss_por_manifesto(self):
        d = self._dados()
        for m in d["pss"]["manifestos"]:
            with self.subTest(manifesto=m["id"]):
                r = avaliar_pod(d, m["spec"])
                self.assertEqual(r["ids"], ESPERADO_PSS[m["id"]])
                self.assertEqual(r["ids"], m["esperado"], "o JSON declara as mesmas violações")
                self.assertEqual(r["atende"], ATENDE[m["id"]])
                self.assertEqual(r["atende"], m["atende"])

    def test_nivel_do_achado_e_admissao(self):
        d = self._dados()
        ms = {m["id"]: m for m in d["pss"]["manifestos"]}
        niv = {k: {a["id"]: a["nivel"] for a in avaliar_pod(d, m["spec"])["achados"]} for k, m in ms.items()}
        self.assertEqual(niv["coletor-logs"]["capabilities"], "baseline", "SYS_ADMIN viola até o baseline")
        self.assertEqual(niv["coletor-logs"]["seccomp"], "baseline", "Unconfined explícito viola o baseline")
        self.assertEqual(niv["worker-relatorios"]["capabilities"], "baseline", "NET_ADMIN fora da lista do baseline")
        self.assertEqual(niv["api-pedidos"]["capabilities"], "restricted")
        self.assertEqual(niv["vitrine-web"]["seccomp"], "restricted")
        adm = {k: admitido(ATENDE[k], d["pss"]["namespaces"][m["ns"]]) for k, m in ms.items()}
        self.assertEqual(adm, {"api-pedidos": True, "coletor-logs": True, "worker-relatorios": False,
                               "vitrine-web": False})
        ev = avaliar_pod(d, ms["worker-relatorios"]["spec"])["achados"]
        rn = next(a for a in ev if a["id"] == "run_as_non_root")
        self.assertEqual(rn["evidencias"], ["worker: runAsNonRoot false"], "o contêiner sobrepõe o pod; o sidecar herda")

    def test_correcoes_pss_convergem(self):
        d = self._dados()
        for m in d["pss"]["manifestos"]:
            original = copy.deepcopy(m["spec"])
            ids = ESPERADO_PSS[m["id"]]
            for ordem in (ids, list(reversed(ids))):
                with self.subTest(manifesto=m["id"], ordem=ordem[0]):
                    s = m["spec"]
                    for rid in ordem:
                        s = corrigir_pod(s, rid)
                    r = avaliar_pod(d, s)
                    self.assertEqual((r["ids"], r["atende"]), ([], "restricted"))
            for rid in ids:
                with self.subTest(manifesto=m["id"], isolada=rid):
                    s = corrigir_pod(m["spec"], rid)
                    self.assertNotIn(rid, avaliar_pod(d, s)["ids"])
                    self.assertEqual(corrigir_pod(s, rid), s, "corrigir de novo não muda nada")
            self.assertEqual(m["spec"], original, "corrigir trabalha sobre cópia")

    def test_casos_pss_de_calibracao(self):
        d = self._dados()
        self.assertGreaterEqual(len(d["pss"]["casos"]), 5)
        for caso in d["pss"]["casos"]:
            with self.subTest(caso=caso["nome"]):
                r = avaliar_pod(d, caso["spec"])
                self.assertEqual(r["ids"], caso["esperado"])
                self.assertEqual(r["atende"], caso["atende"])

    # --------------------------------------------------------------- fase 2
    def test_caminho_de_escalacao_inicial(self):
        rb = self._dados()["rbac"]
        r = avaliar_rbac(rb, {})
        self.assertEqual(r["caminho"], [API, MIG, DEP, ADMIN])
        self.assertEqual(len(r["alcancaveis"]), len(rb["contas"]), "sem correção, a conta comprometida chega a todas")
        ar = {(para, motivo): bids for para, motivo, bids in arestas(rb, API)}
        self.assertEqual(ar, {(MIG, "ler_segredos"): ["api-pedidos-config"], (MIG, "exec"): ["api-pedidos-depuracao"]})
        mot = {motivo for para, motivo, _ in arestas(rb, MIG)}
        self.assertEqual(mot, {"criar_pods"})
        self.assertIn((ADMIN, "bind", ["deployer-rbac"]), arestas(rb, DEP))
        self.assertIn((ADMIN, "curinga", ["operador-legado-admin"]), arestas(rb, OPL))
        rel = {(p, m) for p, m, _ in arestas(rb, "relatorios:sa-relatorios")}
        self.assertIn((OPL, "personificar"), rel)
        col = {(p, m) for p, m, _ in arestas(rb, "observabilidade:sa-coletor")}
        self.assertIn((OPL, "ler_segredos"), col)

    def test_quebrar_o_caminho(self):
        rb = self._dados()["rbac"]
        casos = [
            ({"migracoes-jobs": "restringir"}, None, [API, MIG], []),
            ({"migracoes-jobs": "remover"}, None, [API, MIG], ["migracoes-jobs"]),
            ({"operador-legado-admin": "remover"}, [API, MIG, DEP, ADMIN], None, []),
            ({"deployer-rbac": "remover"}, [API, MIG, OPL, ADMIN], None, ["deployer-rbac"]),
            ({"deployer-rbac": "restringir", "operador-legado-admin": "remover"}, None, None, []),
            ({"api-pedidos-config": "restringir"}, [API, MIG, DEP, ADMIN], None, []),
            ({"api-pedidos-config": "restringir", "api-pedidos-depuracao": "remover"}, None, [API], []),
            ({"api-pedidos-config": "remover", "api-pedidos-depuracao": "remover"}, None, [API], ["api-pedidos-config"]),
        ]
        for mud, cam, alc, ess in casos:
            with self.subTest(mudancas=mud):
                r = avaliar_rbac(rb, mud)
                self.assertEqual(r["caminho"], cam)
                if alc is not None:
                    self.assertEqual(r["alcancaveis"], alc)
                self.assertEqual(r["essenciais_removidos"], ess)

    def test_menor_correcao_sem_derrubar_servico(self):
        """Exatamente uma mudança isolada quebra o caminho sem remover binding essencial: restringir o job de migração."""
        rb = self._dados()["rbac"]
        boas = []
        for b in rb["bindings"]:
            for acao in ("remover", "restringir"):
                if acao == "restringir" and not b.get("restricao"):
                    continue
                r = avaliar_rbac(rb, {b["id"]: acao})
                if not r["admin"] and not r["essenciais_removidos"]:
                    boas.append((b["id"], acao))
        self.assertEqual(boas, [("migracoes-jobs", "restringir")])

    def test_casos_rbac_de_calibracao(self):
        rb = self._dados()["rbac"]
        self.assertGreaterEqual(len(rb["casos"]), 8)
        for caso in rb["casos"]:
            with self.subTest(caso=caso["nome"]):
                c = {"contas": caso["contas"], "bindings": caso["bindings"], "segredos": caso.get("segredos", []),
                     "pods": caso.get("pods", []), "recursos_de_carga": rb["recursos_de_carga"]}
                self.assertEqual(caminho(c, caso["contas"][0])[0], caso["esperado"])

    # --------------------------------------------------------------- fase 3
    def test_alcance_sem_politica_e_com_referencia(self):
        rede = self._dados()["rede"]
        outros = [p["nome"] for p in rede["pods"] if p["nome"] != rede["comprometido"]]
        r0 = avaliar_rede(rede, [])
        self.assertEqual((r0["alcancaveis"], r0["quebrados"]), (outros, []), "sem política, tudo fala com tudo")
        r = avaliar_rede(rede, rede["referencia"])
        self.assertEqual(r["quebrados"], [])
        self.assertEqual(r["alcancaveis"], rede["alcancaveis_esperados"])
        self.assertEqual(r["alcancaveis"], ["banco-pedidos", "gateway-pagamentos", "coredns"])

    def test_negar_por_padrao_e_liberacoes(self):
        rede = self._dados()["rede"]
        r = avaliar_rede(rede, ["negar-tudo-pedidos"])
        self.assertEqual(r["alcancaveis"], [], "negar saída corta tudo, inclusive o DNS")
        self.assertEqual(len(r["quebrados"]), 5)
        so_entrada = [i for i in rede["referencia"] if i not in ("negar-tudo-pedidos", "permitir-saida-api")] + ["negar-entrada-pedidos"]
        r = avaliar_rede(rede, so_entrada)
        self.assertEqual(r["quebrados"], [])
        self.assertIn("controlador-ingress", r["alcancaveis"], "sem regra de saída, o que não tem política continua aberto")
        self.assertIn("internet", r["alcancaveis"], "sem regra de saída, o pod comprometido fala com a internet")
        armadilha = [p["id"] for p in rede["politicas"] if p.get("armadilha")]
        r = avaliar_rede(rede, rede["referencia"] + armadilha)
        self.assertIn("internet", r["alcancaveis"], "a saída liberada geral soma às outras regras e reabre a internet")
        sem_dns = [i for i in rede["referencia"] if i != "permitir-saida-api"]
        r = avaliar_rede(rede, sem_dns)
        self.assertEqual(r["alcancaveis"], [])
        self.assertIn("api-pedidos->coredns", r["quebrados"])

    def test_liberacoes_do_formulario(self):
        rede = self._dados()["rede"]
        base = ["negar-tudo-pedidos", "negar-entrada-vitrine", "negar-entrada-relatorios", "negar-entrada-pagamentos"]
        extras = [liberacao(rede, "entrada", "controlador-ingress", "vitrine-web"),
                  liberacao(rede, "entrada", "vitrine-web", "api-pedidos"),
                  liberacao(rede, "entrada", "api-pedidos", "banco-pedidos"),
                  liberacao(rede, "entrada", "worker-relatorios", "banco-pedidos"),
                  liberacao(rede, "entrada", "api-pedidos", "gateway-pagamentos")]
        for destino in ("banco-pedidos", "gateway-pagamentos", "coredns"):
            extras.append(liberacao(rede, "saida", "api-pedidos", destino))
        r = avaliar_rede(rede, base, extras)
        self.assertEqual(r["quebrados"], [])
        self.assertEqual(r["alcancaveis"], rede["alcancaveis_esperados"])
        r = avaliar_rede(rede, base, extras[:-1])
        self.assertEqual(r["quebrados"], ["api-pedidos->coredns"])

    def test_negar_por_padrao_protege_o_que_nao_tem_politica(self):
        rede = self._dados()["rede"]
        ref = rede["referencia"]
        sem = lambda pid: [i for i in ref if i != pid]  # noqa: E731
        self.assertNotIn("admin-vitrine", avaliar_rede(rede, ref, origem="vitrine-web")["alcancaveis"])
        self.assertIn("admin-vitrine", avaliar_rede(rede, sem("negar-entrada-vitrine"), origem="vitrine-web")["alcancaveis"])
        novo = {"nome": "novo-servico", "ns": "pedidos", "app": "novo-servico", "porta": 8000, "ip": "10.42.3.99"}
        r = avaliar_rede(rede, ref, origem="vitrine-web", pods_extra=[novo])
        self.assertNotIn("novo-servico", r["alcancaveis"], "pod novo nasce protegido pelo negar por padrão")
        r = avaliar_rede(rede, sem("negar-tudo-pedidos"), origem="vitrine-web", pods_extra=[novo])
        self.assertIn("novo-servico", r["alcancaveis"])

    def test_combinacoes_nunca_abrem_mais_que_sem_politica(self):
        rede = self._dados()["rede"]
        todos = set(avaliar_rede(rede, [])["alcancaveis"])
        ids = [p["id"] for p in rede["politicas"]]
        for n in (1, 2):
            for combo in itertools.combinations(ids, n):
                self.assertTrue(set(avaliar_rede(rede, list(combo))["alcancaveis"]) <= todos)

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
        self.assertIn('id="k8s-dados"', content)
        ini = content.index("JSON.parse(document.getElementById(\"k8s-dados\")")
        motor = content[ini:content.index("</script>", ini)]
        for proibido in ("innerHTML", "outerHTML", "eval(", "new Function", "fetch(", "XMLHttpRequest", "WebSocket",
                         "document.write"):
            self.assertNotIn(proibido, motor, proibido)
        for marcador in ("k8s-lab", "k8s-manifesto", "k8s-yaml", "k8s-palpites", "k8s-pss-status", "k8s-pss-achados",
                         "k8s-pss-conferencia", "k8s-rbac-bindings", "k8s-rbac-proximo", "k8s-rbac-trilha",
                         "k8s-rbac-resultado", "k8s-np-politicas", "k8s-np-tipo", "k8s-np-origem", "k8s-np-destino",
                         "k8s-np-resultado", "avaliarPod", "corrigirPod", "admitidoPsa", "arestasRbac", "caminhoRbac",
                         "aplicarMudancasRbac", "permitidoNp", "avaliarRede", "criarLiberacaoNp"):
            self.assertIn(marcador, content, marcador)
        for campo in ("k8s-manifesto", "k8s-rbac-proximo", "k8s-np-tipo", "k8s-np-origem", "k8s-np-destino"):
            self.assertRegex(content, r'<label[^>]*for="%s"' % campo)
        self.assertIn("aria-label", motor)
        self.assertIn("textContent", motor)

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        termos = ["API server", "etcd", "kubelet", "Role", "ClusterRole", "RoleBinding", "ClusterRoleBinding",
                  "create pods", "escalate", "bind", "impersonate", "get secrets", "pods/exec", "curinga",
                  "conta de serviço", "automountServiceAccountToken", "TokenRequest", "token projetado",
                  "Pod Security Admission", "privileged", "baseline", "restricted",
                  "pod-security.kubernetes.io/enforce", "runAsNonRoot", "allowPrivilegeEscalation",
                  "seccompProfile", "RuntimeDefault", "hostPath", "hostNetwork", "hostPID", "NetworkPolicy",
                  "negar por padrão", "CNI", "Calico", "Cilium", "EncryptionConfiguration", "KMS",
                  "controle de admissão", "Kyverno", "Gatekeeper", "ValidatingAdmissionPolicy", "auditoria",
                  "kubectl auth can-i", "CIS Kubernetes Benchmark", "kube-bench", "T1609", "T1613", "T1611",
                  "Ipê Store", "Estudo 50", "Estudo 04", "NSA"]
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
        self.assertIn('initChecklist("seguranca-em-kubernetes")', content)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn(f"{SLUG}/treinamento-seguranca-em-kubernetes.html", content)
        self.assertIn(f'data-slug="{SLUG}"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)


if __name__ == "__main__":
    unittest.main()
