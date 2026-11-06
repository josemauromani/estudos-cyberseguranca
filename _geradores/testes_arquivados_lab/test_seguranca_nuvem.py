"""
test_seguranca_nuvem.py
Testes automatizados para o Estudo 21: Seguranca-em-Nuvem
"""
import ipaddress
import json
import re
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from index_dados import ESTUDOS_DADOS
CONTA = '111122223333'

def lista(v):
    return v if isinstance(v, list) else [v]

def curinga(padrao, valor, sem_caixa=False):
    rx = '^' + ''.join(('.*' if c == '*' else '.' if c == '?' else re.escape(c) for c in padrao)) + '$'
    return re.match(rx, valor, re.S | (re.I if sem_caixa else 0)) is not None

def condicao_ok(cond, ctx):
    for op, pares in (cond or {}).items():
        for chave, valores in pares.items():
            vals = [str(v) for v in lista(valores)]
            presente = chave in ctx
            negado = op in ('StringNotEquals', 'NotIpAddress')
            if not presente:
                if not negado:
                    return False
                continue
            atual = str(ctx[chave])
            if op == 'StringEquals' or op == 'Bool':
                ok = atual.lower() in [v.lower() for v in vals] if op == 'Bool' else atual in vals
            elif op == 'StringNotEquals':
                ok = atual not in vals
            elif op == 'StringLike':
                ok = any((curinga(v, atual) for v in vals))
            elif op in ('IpAddress', 'NotIpAddress'):
                dentro = any((ipaddress.ip_address(atual) in ipaddress.ip_network(v, strict=False) for v in vals))
                ok = dentro if op == 'IpAddress' else not dentro
            else:
                raise ValueError(op)
            if not ok:
                return False
    return True

def casa_acao(st, acao):
    if 'Action' in st:
        return any((curinga(a, acao, True) for a in lista(st['Action'])))
    return not any((curinga(a, acao, True) for a in lista(st['NotAction'])))

def casa_recurso(st, recurso):
    if 'Resource' in st:
        return any((curinga(r, recurso) for r in lista(st['Resource'])))
    return not any((curinga(r, recurso) for r in lista(st['NotResource'])))

def casa_principal(st, quem):
    p = st.get('Principal')
    if p == '*':
        return True
    alvos = lista(p.get('AWS', [])) if isinstance(p, dict) else []
    for a in alvos:
        if a == '*':
            return True
        if quem != 'anonimo' and (a == quem or (a == f'arn:aws:iam::{CONTA}:root' and quem.startswith(f'arn:aws:iam::{CONTA}:'))):
            return True
    return False

def publico(st):
    p = st.get('Principal')
    return p == '*' or (isinstance(p, dict) and '*' in lista(p.get('AWS', [])))

def bucket_de(recurso):
    return recurso.split(':::', 1)[1].split('/', 1)[0]

def avaliar(d, politicas, bpa, req):
    """Mesma conta: negação explícita > permissão (identidade ou recurso) > negação implícita."""
    ctx = req['contexto']
    quem = req['principal']
    cands = []
    if quem != 'anonimo':
        papel = quem.split('/')[-1]
        for i, st in enumerate(politicas.get('identidade:' + papel, {'Statement': []})['Statement']):
            cands.append(('identidade:' + papel, i, st))
    b = bucket_de(req['recurso'])
    for i, st in enumerate(politicas.get('bucket:' + b, {'Statement': []})['Statement']):
        if not casa_principal(st, quem):
            continue
        if st['Effect'] == 'Allow' and publico(st) and bpa.get(b) and (quem == 'anonimo'):
            continue
        cands.append(('bucket:' + b, i, st))
    aplic = [(o, i, st) for o, i, st in cands if casa_acao(st, req['acao']) and casa_recurso(st, req['recurso']) and condicao_ok(st.get('Condition'), ctx)]
    negs = [(o, i) for o, i, st in aplic if st['Effect'] == 'Deny']
    if negs:
        return {'decisao': 'negado_explicito', 'por': [f'{o}#{i}' for o, i in negs]}
    perms = [(o, i) for o, i, st in aplic if st['Effect'] == 'Allow']
    if perms:
        return {'decisao': 'permitido', 'por': [f'{o}#{i}' for o, i in perms]}
    return {'decisao': 'negado_implicito', 'por': []}

def auditar(d, nome, politica):
    meta = d['buckets'].get(nome.split(':', 1)[1], {}) if nome.startswith('bucket:') else {}
    achados = []
    tem_tls = False
    for i, st in enumerate(politica['Statement']):
        acoes = [a.lower() for a in lista(st.get('Action', []))]
        if st['Effect'] == 'Deny' and st.get('Condition', {}).get('Bool', {}).get('aws:SecureTransport') in ('false', False):
            tem_tls = True
        if st['Effect'] != 'Allow':
            continue
        if nome.startswith('bucket:') and publico(st) and (not st.get('Condition')):
            achados.append([i, 'publico', 'info' if meta.get('publico_intencional') and all((a == 's3:getobject' for a in acoes)) else 'alta'])
        if '*' in acoes or any((a.endswith(':*') for a in acoes)):
            achados.append([i, 'acao_curinga', 'alta'])
        if 'Resource' in st and '*' in lista(st['Resource']):
            achados.append([i, 'recurso_curinga', 'media'])
        if 'NotAction' in st or 'NotResource' in st:
            achados.append([i, 'negacao_invertida', 'media'])
        if 'iam:passrole' in acoes and '*' in lista(st.get('Resource', [])):
            achados.append([i, 'passrole_curinga', 'alta'])
    if nome.startswith('bucket:') and (not tem_tls):
        achados.append([None, 'sem_tls', 'media'])
    return achados

class TestSegurancaNuvem(unittest.TestCase):
    """Valida a estrutura, o conteúdo, o avaliador de políticas e a compilação do estudo Seguranca-em-Nuvem."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / '_geradores' / 'seguranca_em_nuvem_body.html'
        self.compiled_path = self.root / 'Seguranca-em-Nuvem' / 'treinamento-seguranca-em-nuvem.html'
        self.portal_path = self.root / 'index.html'

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        termos = ['responsabilidade compartilhada', 'IaaS', 'PaaS', 'SaaS', 'AWS', 'Azure', 'GCP', 'Effect', 'Principal', 'Action', 'Resource', 'Condition', 'negação explícita', 'negação implícita', 'Block Public Access', 'aws:SecureTransport', 'IMDSv2', 'SSRF', '169.254.169.254', 'http-tokens required', 'Capital One', 'CSPM', 'CWPP', 'CNAPP', 'CIS', 'Access Analyzer', 'mínimo privilégio', 'Estudo 12']
        for termo in termos:
            self.assertIn(termo, content, f'Termo obrigatório ausente: {termo}')

    def test_motor_basico(self):
        self.assertTrue(curinga('s3:Get*', 's3:getobject', True))
        self.assertFalse(curinga('s3:Get*', 's3:getobject'))
        self.assertTrue(curinga('arn:aws:s3:::b/*', 'arn:aws:s3:::b/2026/nf.pdf'))
        self.assertFalse(curinga('arn:aws:s3:::b/*', 'arn:aws:s3:::b'))
        self.assertTrue(condicao_ok({'StringNotEquals': {'aws:SourceVpce': 'vpce-1'}}, {}), 'negada com chave ausente é verdadeira')
        self.assertFalse(condicao_ok({'Bool': {'aws:MultiFactorAuthPresent': 'true'}}, {}))
        self.assertTrue(condicao_ok({'IpAddress': {'aws:SourceIp': '203.0.113.0/24'}}, {'aws:SourceIp': '203.0.113.9'}))

    def _secao_isos(self, texto):
        ini = texto.index('<section class="study-section" id="iso-27017-27018" data-tipo="teoria">')
        return texto[ini:texto.index('</section>', ini)]

    def test_secao_iso_27017_27018_conteudo(self):
        for texto in (self.body_path.read_text(encoding='utf-8'), self.compiled_path.read_text(encoding='utf-8')):
            sec = self._secao_isos(texto)
            for termo in ('ISO/IEC 27017', 'ISO/IEC 27018', 'Declaração de Aplicabilidade', 'responsabilidade compartilhada', 'dados pessoais', '2015', '2026', '2019', '2025'):
                self.assertIn(termo, sec, termo)

    def test_secao_iso_27017_27018_referencia(self):
        for texto in (self.body_path.read_text(encoding='utf-8'), self.compiled_path.read_text(encoding='utf-8')):
            ini = texto.index('id="fatos"')
            fatos = texto[ini:texto.index('</section>', ini)]
            self.assertIn('ISO/IEC 27017', fatos)
            self.assertIn('ISO/IEC 27018', fatos)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn('Seguranca-em-Nuvem/treinamento-seguranca-em-nuvem.html', content)
        self.assertIn('data-slug="Seguranca-em-Nuvem"', content)
        self.assertIn(f'/ {len(ESTUDOS_DADOS)}', content)
if __name__ == '__main__':
    unittest.main()
