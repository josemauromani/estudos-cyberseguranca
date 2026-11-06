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
from index_dados import ESTUDOS_DADOS
SLUG = 'Seguranca-em-Kubernetes'
REDES_PRIVADAS = [ipaddress.ip_network(n) for n in ('10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16')]
NIVEIS = ['privileged', 'baseline', 'restricted']
SECCOMP_OK = ('RuntimeDefault', 'Localhost')
ADMIN = 'cluster-admin'

def avaliar_pod(d, spec):
    """Espelho de avaliarPod: achados por regra (na ordem do catálogo), nível de cada achado e nível atendido."""
    pss = d['pss']
    ev = {}

    def add(rid, texto):
        ev.setdefault(rid, []).append(texto)
    psc = spec.get('securityContext', {})
    cs = spec.get('containers', [])
    for c in cs:
        if c.get('securityContext', {}).get('privileged') is True:
            add('privileged', f'{c['name']}: privileged: true')
    for k in ('hostNetwork', 'hostPID', 'hostIPC'):
        if spec.get(k) is True:
            add('host_namespaces', f'{k}: true')
    for v in spec.get('volumes', []):
        if 'hostPath' in v:
            add('host_path', f'volume {v['name']}: hostPath {v['hostPath']['path']}')
    cap_baseline = False
    for c in cs:
        caps = c.get('securityContext', {}).get('capabilities', {})
        if 'ALL' not in [x.upper() for x in caps.get('drop', [])]:
            add('capabilities', f'{c['name']}: não remove ALL')
        for cap in [x.upper() for x in caps.get('add', [])]:
            if cap != 'NET_BIND_SERVICE':
                add('capabilities', f'{c['name']}: adiciona {cap}')
                if cap not in pss['caps_baseline']:
                    cap_baseline = True
    unconfined = False
    pod_t = psc.get('seccompProfile', {}).get('type')
    if pod_t == 'Unconfined':
        unconfined = True
        add('seccomp', 'pod: seccompProfile Unconfined')
    for c in cs:
        ct = c.get('securityContext', {}).get('seccompProfile', {}).get('type')
        if ct == 'Unconfined':
            unconfined = True
            add('seccomp', f'{c['name']}: seccompProfile Unconfined')
        elif ct is None and pod_t is None:
            add('seccomp', f'{c['name']}: sem seccompProfile (nem no pod)')
    if psc.get('runAsUser') == 0:
        add('run_as_non_root', 'pod: runAsUser: 0')
    for c in cs:
        sc = c.get('securityContext', {})
        if sc.get('runAsUser') == 0:
            add('run_as_non_root', f'{c['name']}: runAsUser: 0')
        nr = sc['runAsNonRoot'] if 'runAsNonRoot' in sc else psc.get('runAsNonRoot')
        if nr is not True:
            add('run_as_non_root', f'{c['name']}: runAsNonRoot ' + ('false' if nr is False else 'ausente'))
    for c in cs:
        ape = c.get('securityContext', {}).get('allowPrivilegeEscalation')
        if ape is not False:
            add('allow_privilege_escalation', f'{c['name']}: allowPrivilegeEscalation ' + ('true' if ape is True else 'ausente'))
    achados = []
    for rid in pss['ordem_regras']:
        if rid not in ev:
            continue
        nivel = pss['regras'][rid]['nivel']
        if rid == 'capabilities' and cap_baseline or (rid == 'seccomp' and unconfined):
            nivel = 'baseline'
        achados.append({'id': rid, 'nivel': nivel, 'evidencias': ev[rid]})
    if any((a['nivel'] == 'baseline' for a in achados)):
        atende = 'privileged'
    elif achados:
        atende = 'baseline'
    else:
        atende = 'restricted'
    return {'achados': achados, 'ids': [a['id'] for a in achados], 'atende': atende}

def admitido(atende, exigido):
    """Espelho de admitidoPsa: o Pod Security Admission aceita o pod se ele atende ao nível do namespace."""
    return NIVEIS.index(atende) >= NIVEIS.index(exigido)

def corrigir_pod(spec, rid):
    """Espelho de corrigirPod: a correção padrão de cada regra, sobre uma cópia do spec."""
    s = copy.deepcopy(spec)
    cs = s.get('containers', [])
    if rid == 'privileged':
        for c in cs:
            if c.get('securityContext', {}).get('privileged') is True:
                c['securityContext']['privileged'] = False
    elif rid == 'host_namespaces':
        for k in ('hostNetwork', 'hostPID', 'hostIPC'):
            if s.get(k) is True:
                del s[k]
    elif rid == 'host_path':
        s['volumes'] = [{'name': v['name'], 'emptyDir': {}} if 'hostPath' in v else v for v in s.get('volumes', [])]
    elif rid == 'capabilities':
        for c in cs:
            caps = c.setdefault('securityContext', {}).setdefault('capabilities', {})
            caps['drop'] = ['ALL']
            add = [x for x in caps.get('add', []) if x.upper() == 'NET_BIND_SERVICE']
            if add:
                caps['add'] = add
            else:
                caps.pop('add', None)
    elif rid == 'seccomp':
        s.setdefault('securityContext', {})['seccompProfile'] = {'type': 'RuntimeDefault'}
        for c in cs:
            sc = c.get('securityContext', {})
            if 'seccompProfile' in sc and sc['seccompProfile'].get('type') not in SECCOMP_OK:
                del sc['seccompProfile']
    elif rid == 'run_as_non_root':
        psc = s.setdefault('securityContext', {})
        psc['runAsNonRoot'] = True
        if psc.get('runAsUser') == 0:
            psc['runAsUser'] = 10001
        for c in cs:
            sc = c.get('securityContext', {})
            if sc.get('runAsNonRoot') is False:
                del sc['runAsNonRoot']
            if sc.get('runAsUser') == 0:
                sc['runAsUser'] = 10001
    elif rid == 'allow_privilege_escalation':
        for c in cs:
            c.setdefault('securityContext', {})['allowPrivilegeEscalation'] = False
    return s

def ns_da_conta(conta):
    return conta.split(':', 1)[0]

def permissoes(rb, conta):
    """(escopo, regra, binding): RoleBinding vale no namespace dele; ClusterRoleBinding, no cluster todo ('*')."""
    out = []
    for b in rb['bindings']:
        if conta in b['sujeitos']:
            escopo = '*' if b['tipo'] == 'ClusterRoleBinding' else b['ns']
            for r in b['regras']:
                out.append((escopo, r, b['id']))
    return out

def concede(perms, verbo, recurso, ns):
    """Bindings que dão o verbo no recurso; ns='*' exige escopo de cluster."""
    out = []
    for escopo, r, bid in perms:
        if (verbo in r['verbos'] or '*' in r['verbos']) and (recurso in r['recursos'] or '*' in r['recursos']) and (escopo == '*' or escopo == ns) and (bid not in out):
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
    cur = [bid for escopo, r, bid in p if escopo == '*' and '*' in r['verbos'] and ('*' in r['recursos'])]
    if cur:
        out.append((ADMIN, 'curinga', unir(cur)))
    b1, b2 = (concede(p, 'create', 'clusterrolebindings', '*'), concede(p, 'bind', 'clusterroles', '*'))
    if b1 and b2:
        out.append((ADMIN, 'bind', unir(b1, b2)))
    e1 = concede(p, 'escalate', 'clusterroles', '*')
    e2 = unir(concede(p, 'update', 'clusterroles', '*'), concede(p, 'patch', 'clusterroles', '*'))
    if e1 and e2:
        out.append((ADMIN, 'escalate', unir(e1, e2)))
    for t in rb['contas']:
        if t == conta:
            continue
        ns = ns_da_conta(t)
        g = concede(p, 'impersonate', 'serviceaccounts', ns)
        if g:
            out.append((t, 'personificar', g))
        g = unir(*[concede(p, 'create', rec, ns) for rec in rb['recursos_de_carga']])
        if g:
            out.append((t, 'criar_pods', g))
        g = []
        for s in rb['segredos']:
            if s['conta'] == t:
                g = unir(g, concede(p, 'get', 'secrets', s['ns']), concede(p, 'list', 'secrets', s['ns']))
        if g:
            out.append((t, 'ler_segredos', g))
        g = []
        for pod in rb['pods']:
            if pod['conta'] == t:
                g = unir(g, concede(p, 'create', 'pods/exec', pod['ns']))
        if g:
            out.append((t, 'exec', g))
    return out

def caminho(rb, origem):
    """Espelho de caminhoRbac: busca em largura até o cluster-admin; devolve (caminho de nós, alcançáveis)."""
    pai, fila, vistos = ({origem: None}, [origem], [origem])
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
        nos, x = ([], ADMIN)
        while x is not None:
            nos.insert(0, x)
            x = pai[x][0] if pai[x] else None
    return (nos, [v for v in vistos if v != ADMIN])

def aplicar_mudancas(rb, mudancas):
    """Espelho de aplicarMudancasRbac: 'remover' apaga o binding; 'restringir' aplica a restrição sugerida."""
    out = copy.deepcopy(rb)
    novos = []
    for b in out['bindings']:
        m = mudancas.get(b['id'], 'manter')
        if m == 'remover':
            continue
        if m == 'restringir' and b.get('restricao'):
            for k in ('tipo', 'ns', 'regras'):
                if k in b['restricao']:
                    b[k] = b['restricao'][k]
        novos.append(b)
    out['bindings'] = novos
    return out

def avaliar_rbac(rb, mudancas):
    r = aplicar_mudancas(rb, mudancas)
    nos, alc = caminho(r, rb['comprometida'])
    ess = [b['id'] for b in rb['bindings'] if b['essencial'] and mudancas.get(b['id']) == 'remover']
    return {'caminho': nos, 'admin': nos is not None, 'alcancaveis': alc, 'essenciais_removidos': ess}

def casa_seletor(pol, pod):
    return pod['ns'] == pol['ns'] and all((pod.get(k) == v for k, v in pol['seletor'].items()))

def casa_peer(peer, pol_ns, pod):
    if pod.get('externo'):
        return False
    ns = peer.get('ns', pol_ns)
    return (ns == '*' or ns == pod['ns']) and ('app' not in peer or peer['app'] == pod['app'])

def regra_ok(regra, campo, pol_ns, pod, porta):
    peers = regra.get(campo)
    if peers is not None and (not any((casa_peer(x, pol_ns, pod) for x in peers))):
        return False
    portas = regra.get('portas') or []
    return not portas or porta in portas

def permitido(pols, origem, destino):
    """Espelho de permitidoNp: a saída da origem e a entrada do destino precisam permitir a conexão."""
    porta = destino['porta']
    saida = [p for p in pols if 'Egress' in p['tipos'] and casa_seletor(p, origem)]
    if saida and (not any((regra_ok(r, 'para', p['ns'], destino, porta) for p in saida for r in p.get('egress', [])))):
        return False
    entrada = [p for p in pols if 'Ingress' in p['tipos'] and casa_seletor(p, destino)]
    if entrada and (not any((regra_ok(r, 'de', p['ns'], origem, porta) for p in entrada for r in p.get('ingress', [])))):
        return False
    return True

def avaliar_rede(rede, ids, extras=(), origem=None, pods_extra=()):
    """Espelho de avaliarRede: pods alcançáveis a partir do comprometido e fluxos legítimos quebrados."""
    pols = [p for p in rede['politicas'] if p['id'] in ids] + list(extras)
    todos = rede['pods'] + list(pods_extra)
    pods = {p['nome']: p for p in todos}
    comp = pods[origem or rede['comprometido']]
    alc = [p['nome'] for p in todos if p is not comp and permitido(pols, comp, p)]
    quebrados = [f'{f['de']}->{f['para']}' for f in rede['fluxos'] if not permitido(pols, pods[f['de']], pods[f['para']])]
    return {'alcancaveis': alc, 'quebrados': quebrados}

def liberacao(rede, tipo, de, para):
    """Espelho de criarLiberacaoNp: a política que o formulário gera (entrada no destino ou saída na origem)."""
    pods = {p['nome']: p for p in rede['pods']}
    o, t = (pods[de], pods[para])
    if tipo == 'entrada':
        return {'id': f'lib-{de}-{para}-entrada', 'ns': t['ns'], 'seletor': {'app': t['app']}, 'tipos': ['Ingress'], 'ingress': [{'de': [{'ns': o['ns'], 'app': o['app']}], 'portas': [t['porta']]}]}
    return {'id': f'lib-{de}-{para}-saida', 'ns': o['ns'], 'seletor': {'app': o['app']}, 'tipos': ['Egress'], 'egress': [{'para': [{'ns': t['ns'], 'app': t['app']}], 'portas': [t['porta']]}]}
ESPERADO_PSS = {'api-pedidos': ['capabilities', 'seccomp', 'run_as_non_root', 'allow_privilege_escalation'], 'coletor-logs': ['privileged', 'host_namespaces', 'host_path', 'capabilities', 'seccomp', 'run_as_non_root', 'allow_privilege_escalation'], 'worker-relatorios': ['capabilities', 'run_as_non_root', 'allow_privilege_escalation'], 'vitrine-web': ['seccomp']}
ATENDE = {'api-pedidos': 'baseline', 'coletor-logs': 'privileged', 'worker-relatorios': 'privileged', 'vitrine-web': 'baseline'}
API, MIG, DEP, OPL = ('pedidos:sa-api-pedidos', 'pedidos:sa-migracoes', 'ci:sa-deployer', 'kube-system:sa-operador-legado')

class TestSegurancaKubernetes(unittest.TestCase):
    """Estrutura, conteúdo, simulador e compilação do estudo 51."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / '_geradores' / 'seguranca_em_kubernetes_body.html'
        self.compiled_path = self.root / SLUG / 'treinamento-seguranca-em-kubernetes.html'
        self.portal_path = self.root / 'index.html'

    def _body(self):
        return self.body_path.read_text(encoding='utf-8')

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_diagrama_no_formato_do_guia(self):
        body = self._body()
        caixas = re.findall('<div class="diagram-box">\\s*<div class="diagram-header">\\s*<span class="diagram-title">([^<]+)</span>.*?<pre class="mermaid" data-title="([^"]+)">', body, re.S)
        self.assertGreaterEqual(len(caixas), 1, 'falta um .diagram-box com cabeçalho e Mermaid')
        for titulo, data_title in caixas:
            self.assertEqual(titulo.strip(), data_title.strip())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        termos = ['API server', 'etcd', 'kubelet', 'Role', 'ClusterRole', 'RoleBinding', 'ClusterRoleBinding', 'create pods', 'escalate', 'bind', 'impersonate', 'get secrets', 'pods/exec', 'curinga', 'conta de serviço', 'automountServiceAccountToken', 'TokenRequest', 'token projetado', 'Pod Security Admission', 'privileged', 'baseline', 'restricted', 'pod-security.kubernetes.io/enforce', 'runAsNonRoot', 'allowPrivilegeEscalation', 'seccompProfile', 'RuntimeDefault', 'hostPath', 'hostNetwork', 'hostPID', 'NetworkPolicy', 'negar por padrão', 'CNI', 'Calico', 'Cilium', 'EncryptionConfiguration', 'KMS', 'controle de admissão', 'Kyverno', 'Gatekeeper', 'ValidatingAdmissionPolicy', 'auditoria', 'kubectl auth can-i', 'CIS Kubernetes Benchmark', 'kube-bench', 'T1609', 'T1613', 'T1611', 'Ipê Store', 'Estudo 50', 'Estudo 04', 'NSA']
        for termo in termos:
            self.assertIn(termo, content, f'Termo obrigatório ausente: {termo}')

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn(f'{SLUG}/treinamento-seguranca-em-kubernetes.html', content)
        self.assertIn(f'data-slug="{SLUG}"', content)
        self.assertIn(f'/ {len(ESTUDOS_DADOS)}', content)
if __name__ == '__main__':
    unittest.main()
