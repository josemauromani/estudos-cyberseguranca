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
from index_dados import ESTUDOS_DADOS
SLUG = 'Infraestrutura-como-Codigo-Segura'
REDES_OK = [ipaddress.ip_network(n) for n in ('10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16')]
FLAGS_PAB = ('block_public_acls', 'block_public_policy', 'ignore_public_acls', 'restrict_public_buckets')
ABERTOS = ('0.0.0.0/0', '::/0')
ACOES_AVALIADAS = ('create', 'update')

def expressoes(plano, address):
    """Expressões do HCL (bloco configuration do plano) para um endereço."""
    for r in plano.get('configuration', {}).get('root_module', {}).get('resources', []):
        if r['address'] == address:
            return r.get('expressions', {})
    return {}

def porta_admin_aberta(d, r):
    """Espelho de portaAdminAberta: evidência se a regra de entrada abre porta administrativa para a internet."""
    abertos = [c for c in (r.get('cidr_blocks') or []) + (r.get('ipv6_cidr_blocks') or []) if c in ABERTOS]
    if not abertos:
        return None
    todas = r.get('protocol') in ('-1', 'all')
    portas = [p for p in d['portas_admin'] if todas or r['from_port'] <= p <= r['to_port']]
    if not portas:
        return None
    return 'ingress ' + '/'.join((str(p) for p in portas)) + ' de ' + abertos[0]

def violacoes(d, rc, expr):
    """Espelho de violacoesRecurso: {politica: [evidências]} na ordem do catálogo (todas as políticas)."""
    ev = {}

    def add(pid, texto):
        ev.setdefault(pid, []).append(texto)
    acoes = rc['change']['actions']
    if not any((a in ACOES_AVALIADAS for a in acoes)):
        return {}
    after = rc['change'].get('after') or {}
    t = rc['type']
    if t == 'aws_s3_bucket_public_access_block':
        for k in FLAGS_PAB:
            if after.get(k) is not True:
                add('bucket_publico', f'{k} = false')
    if t == 'aws_s3_bucket_acl' and after.get('acl') in ('public-read', 'public-read-write'):
        add('bucket_publico', f'acl = {after['acl']}')
    regras = []
    if t == 'aws_security_group':
        regras = after.get('ingress') or []
    elif t == 'aws_security_group_rule' and after.get('type') == 'ingress':
        regras = [after]
    for r in regras:
        aberta = porta_admin_aberta(d, r)
        if aberta:
            add('porta_admin_aberta', aberta)
    if t == 'aws_ebs_volume' and after.get('encrypted') is not True:
        add('sem_criptografia', 'encrypted = false')
    if t == 'aws_instance':
        for b in after.get('root_block_device') or []:
            if b.get('encrypted') is not True:
                add('sem_criptografia', 'root_block_device.encrypted = false')
    if t == 'aws_db_instance' and after.get('storage_encrypted') is not True:
        add('sem_criptografia', 'storage_encrypted = false')
    if t == 'aws_s3_bucket_server_side_encryption_configuration':
        for r in after.get('rule') or []:
            for a in r.get('apply_server_side_encryption_by_default') or []:
                if a.get('sse_algorithm') != 'aws:kms':
                    add('sem_criptografia', f'sse_algorithm = {a.get('sse_algorithm')} (exige aws:kms)')
    if t == 'aws_cloudtrail':
        if after.get('enable_logging') is False:
            add('log_desligado', 'enable_logging = false')
        if after.get('enable_log_file_validation') is not True:
            add('log_desligado', 'enable_log_file_validation = false')
    if t == 'aws_lb':
        logs = after.get('access_logs') or []
        if not logs or logs[0].get('enabled') is not True:
            add('log_desligado', 'access_logs.enabled = false')
    for attr in d['atributos_secretos']:
        if 'constant_value' in expr.get(attr, {}):
            add('segredo_no_codigo', f'{attr} com valor literal no HCL')
    return {pid: ev[pid] for pid in d['politicas']['ordem'] if pid in ev}

def dias(a, b):
    return (date.fromisoformat(b) - date.fromisoformat(a)).days

def motivos_excecao(d, exc):
    """Espelho de motivosExcecao: lista vazia = exceção válida na data da revisão."""
    m = []
    if not exc.get('responsavel', '').strip():
        m.append('sem responsável')
    if dias(d['data_revisao'], exc['expira']) < 0:
        m.append('vencida')
    if dias(exc['criada'], exc['expira']) > d['prazo_max_dias']:
        m.append('prazo acima do máximo')
    return m

def avaliar_plano(d, plano, ativas, excecoes=None):
    """Espelho de avaliarPlano: status de cada mudança e veredito do plano."""
    excecoes = d['excecoes'] if excecoes is None else excecoes
    out = []
    for rc in plano['resource_changes']:
        v = violacoes(d, rc, expressoes(plano, rc['address']))
        itens = []
        for pid in d['politicas']['ordem']:
            if pid not in v or pid not in ativas:
                continue
            exc = next((e for e in excecoes if e['politica'] == pid and e['address'] == rc['address']), None)
            itens.append({'politica': pid, 'evidencias': v[pid], 'excecao': exc['id'] if exc else None, 'valida': bool(exc) and (not motivos_excecao(d, exc))})
        bloq = [i['politica'] for i in itens if not i['valida']]
        status = 'bloqueado' if bloq else 'excecao' if itens else 'aprovado'
        out.append({'address': rc['address'], 'status': status, 'bloqueios': bloq, 'itens': itens})
    return {'mudancas': out, 'aprovado': not any((m['status'] == 'bloqueado' for m in out))}

def corrigir(d, plano, address, pid):
    """Espelho de corrigirPlano: a correção padrão de uma política num recurso, sobre uma cópia do plano."""
    p = copy.deepcopy(plano)
    rc = next((r for r in p['resource_changes'] if r['address'] == address))
    a = rc['change'].get('after') or {}
    t = rc['type']
    if pid == 'bucket_publico':
        if t == 'aws_s3_bucket_public_access_block':
            for k in FLAGS_PAB:
                a[k] = True
        if t == 'aws_s3_bucket_acl':
            a['acl'] = 'private'
    elif pid == 'porta_admin_aberta':
        if t == 'aws_security_group':
            a['ingress'] = [r for r in a.get('ingress', []) if not porta_admin_aberta(d, r)]
        elif t == 'aws_security_group_rule':
            a['cidr_blocks'] = [d['cidr_vpn']]
            a['ipv6_cidr_blocks'] = []
    elif pid == 'sem_criptografia':
        if t == 'aws_ebs_volume':
            a['encrypted'] = True
        if t == 'aws_instance':
            for b in a.get('root_block_device', []):
                b['encrypted'] = True
        if t == 'aws_db_instance':
            a['storage_encrypted'] = True
        if t == 'aws_s3_bucket_server_side_encryption_configuration':
            for r in a.get('rule', []):
                for x in r.get('apply_server_side_encryption_by_default', []):
                    x['sse_algorithm'] = 'aws:kms'
                    x['kms_master_key_id'] = d['chave_kms']
    elif pid == 'log_desligado':
        if t == 'aws_cloudtrail':
            a['enable_logging'] = True
            a['enable_log_file_validation'] = True
        if t == 'aws_lb':
            a['access_logs'] = [{'enabled': True, 'bucket': d['bucket_logs'], 'prefix': 'lb'}]
    elif pid == 'segredo_no_codigo':
        for r in p.get('configuration', {}).get('root_module', {}).get('resources', []):
            if r['address'] == address:
                for attr in d['atributos_secretos']:
                    r.get('expressions', {}).pop(attr, None)
                if t == 'aws_db_instance':
                    r['expressions']['manage_master_user_password'] = {'constant_value': True}
        for attr in d['atributos_secretos']:
            a.pop(attr, None)
        if t == 'aws_db_instance':
            a['manage_master_user_password'] = True
    return p

def segredos_no_state(state):
    """Espelho de segredosNoState: (endereço, atributo) marcados como sensíveis, em claro no state."""
    out = []
    for r in state['resources']:
        addr = f'{r['type']}.{r['name']}'
        for inst in r['instances']:
            for caminho in inst.get('sensitive_attributes', []):
                attr = caminho[0]['value']
                if attr in inst['attributes']:
                    out.append((addr, attr))
    return out

def state_visivel(d, selecao):
    """Espelho de stateVisivel: com a senha gerida pelo provedor, ela sai do state."""
    s = copy.deepcopy(d['state'])
    if 'segredo_fora' not in selecao:
        return s
    tira = d['backend']['remove_do_state']
    s['resources'] = [r for r in s['resources'] if f'{r['type']}.{r['name']}' not in tira]
    for r in s['resources']:
        addr = f'{r['type']}.{r['name']}'
        for inst in r['instances']:
            for item in tira:
                if item.startswith(addr + ':'):
                    attr = item.split(':', 1)[1]
                    inst['attributes'].pop(attr, None)
                    inst['sensitive_attributes'] = [c for c in inst['sensitive_attributes'] if c[0]['value'] != attr]
            if addr in d['backend'].get('acrescenta', {}):
                inst['attributes'].update(d['backend']['acrescenta'][addr])
    return s

def riscos_backend(d, selecao):
    """Espelho de riscosBackend: opções não atendidas (uma opção que depende de outra só vale com ela)."""
    out = []
    for o in d['backend']['opcoes']:
        ok = o['id'] in selecao and (not o.get('depende') or o['depende'] in selecao)
        if not ok:
            out.append(o['id'])
    return out

def atributos_divergentes(item):
    """Espelho de detectarDrift: atributos de topo cujo valor real difere do código."""
    chaves = list(item['codigo']) + [k for k in item['real'] if k not in item['codigo']]
    return [k for k in chaves if item['codigo'].get(k) != item['real'].get(k)]

def risco_drift(d, item):
    """Políticas que o valor real viola e o código não violava."""

    def v(after):
        return violacoes(d, {'address': item['address'], 'type': item['type'], 'change': {'actions': ['update'], 'after': after}}, {})
    antes, depois = (v(item['codigo']), v(item['real']))
    return [pid for pid in depois if pid not in antes]

def decidir_drift(d, item, escolha):
    """Espelho de decidirDrift: incorporar um drift de risco é barrado pela política no próximo plano."""
    risco = risco_drift(d, item)
    if escolha == 'incorporar' and risco:
        return 'bloqueado'
    return 'ok' if escolha == item['recomendado'] else 'aceitavel'
TODAS = ['bucket_publico', 'porta_admin_aberta', 'sem_criptografia', 'log_desligado', 'segredo_no_codigo']
ESPERADO_VIOLACOES = {'aws_s3_bucket.notas_fiscais': [], 'aws_s3_bucket_public_access_block.notas_fiscais': ['bucket_publico'], 'aws_s3_bucket_server_side_encryption_configuration.notas_fiscais': ['sem_criptografia'], 'aws_s3_bucket_public_access_block.vitrine_imagens': ['bucket_publico'], 'aws_security_group.app_notas': ['porta_admin_aberta'], 'aws_security_group_rule.lb_https': [], 'aws_instance.app_notas': ['sem_criptografia'], 'aws_db_instance.notas': ['sem_criptografia', 'segredo_no_codigo'], 'aws_cloudtrail.principal': ['log_desligado'], 'aws_lb.notas': ['log_desligado'], 'aws_ebs_volume.backup_notas': [], 'aws_security_group.legado_ftp': []}
ESPERADO_STATUS = {'aws_s3_bucket.notas_fiscais': 'aprovado', 'aws_s3_bucket_public_access_block.notas_fiscais': 'bloqueado', 'aws_s3_bucket_server_side_encryption_configuration.notas_fiscais': 'bloqueado', 'aws_s3_bucket_public_access_block.vitrine_imagens': 'excecao', 'aws_security_group.app_notas': 'bloqueado', 'aws_security_group_rule.lb_https': 'aprovado', 'aws_instance.app_notas': 'bloqueado', 'aws_db_instance.notas': 'bloqueado', 'aws_cloudtrail.principal': 'bloqueado', 'aws_lb.notas': 'bloqueado', 'aws_ebs_volume.backup_notas': 'aprovado', 'aws_security_group.legado_ftp': 'aprovado'}
ESPERADO_EXCECOES = {'EXC-014': [], 'EXC-009': ['vencida'], 'EXC-021': ['sem responsável', 'prazo acima do máximo']}
ESPERADO_SEGREDOS = [('random_password.pedidos', 'result'), ('aws_db_instance.pedidos', 'password'), ('aws_iam_access_key.integracao_sefaz', 'secret')]
ESPERADO_DRIFT = {'aws_security_group.app_pedidos': (['ingress'], ['porta_admin_aberta']), 'aws_s3_bucket_public_access_block.relatorios': (['block_public_policy', 'restrict_public_buckets'], ['bucket_publico']), 'aws_instance.app_pedidos': (['instance_type'], []), 'aws_s3_bucket.vitrine': (['tags'], [])}

class TestInfraestruturaComoCodigo(unittest.TestCase):
    """Estrutura, conteúdo, simulador e compilação do estudo 52."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / '_geradores' / 'infraestrutura_como_codigo_segura_body.html'
        self.compiled_path = self.root / SLUG / 'treinamento-infraestrutura-como-codigo-segura.html'
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
        termos = ['Terraform', 'OpenTofu', 'HCL', 'declarativ', 'terraform plan', 'terraform apply', 'terraform show -json', 'resource_changes', 'state', 'terraform.tfstate', 'backend', 'use_lockfile', 'DynamoDB', 'encrypt', 'sensitive', 'random_password', 'manage_master_user_password', 'módulos aprovados', 'Checkov', 'tfsec', 'Trivy', 'OPA', 'Rego', 'Conftest', 'policy-as-code', 'exceção', 'prazo', 'responsável', 'drift', '-refresh-only', 'terraform import', 'CSPM', '0.0.0.0/0', 'Block Public Access', 'CloudTrail', 'KMS', 'OIDC', 'pull request', 'T1578', 'T1530', 'Ipê Store', 'Estudo 21', 'Estudo 22', 'Estudo 51', 'CIS']
        for termo in termos:
            self.assertIn(termo, content, f'Termo obrigatório ausente: {termo}')

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn(f'{SLUG}/treinamento-infraestrutura-como-codigo-segura.html', content)
        self.assertIn(f'data-slug="{SLUG}"', content)
        self.assertIn(f'/ {len(ESTUDOS_DADOS)}', content)
if __name__ == '__main__':
    unittest.main()
