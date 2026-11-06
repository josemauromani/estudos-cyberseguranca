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
from index_dados import ESTUDOS_DADOS
SLUG = 'Deteccao-e-Resposta-em-Nuvem'
VAZADA = 'AKIAIOSFODNN7EXAMPLE'
DO_ATACANTE = 'AKIAI44QH8DHBEXAMPLE'
SESSAO = 'ASIAEXAMPLESESSAO001'
REDES_DOC = [ipaddress.ip_network(n) for n in ('192.0.2.0/24', '198.51.100.0/24', '203.0.113.0/24')]
ACOES = ['registrar', 'preservar_logs', 'desativar_vazada', 'desativar_atacante', 'revogar_sessoes', 'snapshot', 'isolar_instancia', 'encerrar_instancia', 'apagar_usuario', 'girar']
CREDENCIAIS = ('vazada', 'atacante', 'sessoes')

def eventos_visiveis(d, dados_ligados):
    """Espelho de eventosVisiveis: eventos de dados só existem se a trilha os registra."""
    return [e for e in d['eventos'] if e['eventCategory'] != 'Data' or dados_ligados]

def eventos_por_chaves(d, chaves, dados_ligados):
    """Espelho de eventosPorChaves: filtro por userIdentity.accessKeyId, na ordem de entrega."""
    return [e for e in eventos_visiveis(d, dados_ligados) if e['userIdentity'].get('accessKeyId') in chaves]

def chaves_derivadas(eventos):
    """Espelho de chavesDerivadas: credenciais emitidas por CreateAccessKey e GetSessionToken bem-sucedidos."""
    novas = []
    for e in eventos:
        if e.get('errorCode'):
            continue
        r = e.get('responseElements') or {}
        if e['eventName'] == 'CreateAccessKey':
            novas.append(r['accessKey']['accessKeyId'])
        elif e['eventName'] == 'GetSessionToken':
            novas.append(r['credentials']['accessKeyId'])
    return novas

def linha_do_tempo(d, chaves, dados_ligados):
    """Espelho de linhaDoTempo: eventos das chaves fora dos IPs conhecidos, ordenados por eventTime."""
    ataque = [e for e in eventos_por_chaves(d, chaves, dados_ligados) if e['sourceIPAddress'] not in d['ips_conhecidos']]
    ataque.sort(key=lambda e: (e['eventTime'], e['eventID']))
    return [e['eventID'] for e in ataque]

def conferir_linha(esperado, ordem):
    """Espelho de conferirLinha."""
    return {'correta': list(ordem) == list(esperado), 'na_posicao': sum((1 for k, i in enumerate(ordem) if k < len(esperado) and esperado[k] == i)), 'intrusos': [i for i in ordem if i not in esperado], 'faltando': [i for i in esperado if i not in ordem]}

def avaliar_contencao(ordem):
    """Espelho de avaliarContencao: aplica as ações em ordem e diz o que cada uma preserva ou destrói."""
    st = {'registrado': False, 'logs': False, 'vazada': True, 'atacante': True, 'sessoes': True, 'snapshot': False, 'instancia': 'rodando', 'usuario': True}
    passos, com_atacante = ([], 0)
    for a in ordem:
        if any((st[k] for k in CREDENCIAIS)):
            com_atacante += 1
        ef = 'nada'
        if a == 'registrar':
            if not st['registrado']:
                st['registrado'], ef = (True, 'preserva')
        elif a == 'preservar_logs':
            if not st['logs']:
                st['logs'], ef = (True, 'preserva')
        elif a == 'desativar_vazada':
            if st['vazada']:
                st['vazada'] = False
                ef = 'alerta' if st['atacante'] else 'ok'
        elif a == 'desativar_atacante':
            if st['atacante']:
                st['atacante'], ef = (False, 'ok')
        elif a == 'revogar_sessoes':
            if st['sessoes']:
                st['sessoes'], ef = (False, 'ok')
        elif a == 'snapshot':
            if st['instancia'] == 'encerrada' and (not st['snapshot']):
                ef = 'perdido'
            elif not st['snapshot']:
                st['snapshot'], ef = (True, 'preserva')
        elif a == 'isolar_instancia':
            if st['instancia'] == 'rodando':
                st['instancia'], ef = ('isolada', 'ok')
        elif a == 'encerrar_instancia':
            if st['instancia'] != 'encerrada':
                ef = 'ok' if st['snapshot'] else 'destroi'
                st['instancia'] = 'encerrada'
        elif a == 'apagar_usuario':
            if st['usuario']:
                st['usuario'], st['atacante'] = (False, False)
                ef = 'ok' if st['registrado'] else 'destroi'
        elif a == 'girar':
            st['vazada'] = False
            ef = 'ok' if st['registrado'] else 'destroi'
        passos.append((a, ef))
    ativos = [k for k in CREDENCIAIS if st[k]]
    destruicoes = [a for a, ef in passos if ef in ('destroi', 'perdido')]
    pendencias = []
    if not st['registrado']:
        pendencias.append('registrar')
    if not st['logs']:
        pendencias.append('preservar_logs')
    if not st['snapshot'] and st['instancia'] != 'encerrada':
        pendencias.append('snapshot')
    if ativos or st['instancia'] == 'rodando':
        veredito = 'incompleto'
    elif destruicoes:
        veredito = 'com_perdas'
    elif pendencias:
        veredito = 'sem_preservacao'
    elif com_atacante > 3:
        veredito = 'lento'
    else:
        veredito = 'ideal'
    return {'passos': passos, 'ativos': ativos, 'destruicoes': destruicoes, 'pendencias': pendencias, 'instancia': st['instancia'], 'com_atacante': com_atacante, 'veredito': veredito}
TL_VAZADA = ['e02', 'e03', 'e04', 'e05', 'e06', 'e07', 'e15']
TL_TODAS_SEM_DADOS = ['e02', 'e03', 'e04', 'e05', 'e06', 'e07', 'e09', 'e12', 'e15', 'e16']
TL_TODAS_COM_DADOS = ['e02', 'e03', 'e04', 'e05', 'e06', 'e07', 'e09', 'e10', 'e11', 'e12', 'e15', 'e16']
ESPERADO_CASOS = {'ideal': {'veredito': 'ideal', 'efeitos': ['ok', 'ok', 'ok', 'preserva', 'preserva', 'preserva', 'ok', 'ok', 'ok']}, 'so_vazada': {'veredito': 'incompleto', 'efeitos': ['alerta'], 'ativos': ['atacante', 'sessoes']}, 'pressa': {'veredito': 'com_perdas', 'efeitos': ['destroi', 'ok', 'destroi', 'ok', 'perdido', 'preserva', 'preserva', 'ok'], 'destruicoes': ['apagar_usuario', 'encerrar_instancia', 'snapshot']}, 'sem_registro': {'veredito': 'sem_preservacao', 'efeitos': ['ok', 'ok', 'ok', 'ok', 'preserva', 'ok'], 'pendencias': ['registrar', 'preservar_logs']}, 'lento': {'veredito': 'lento', 'efeitos': ['preserva', 'preserva', 'preserva', 'ok', 'ok', 'ok', 'ok', 'ok', 'ok']}}

class TestDeteccaoRespostaNuvem(unittest.TestCase):
    """Estrutura, conteúdo, simulador e compilação do estudo 53."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / '_geradores' / 'deteccao_e_resposta_em_nuvem_body.html'
        self.compiled_path = self.root / SLUG / 'treinamento-deteccao-e-resposta-em-nuvem.html'
        self.portal_path = self.root / 'index.html'

    def _body(self):
        return self.body_path.read_text(encoding='utf-8')

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_conferir_linha(self):
        r = conferir_linha(TL_VAZADA, TL_VAZADA)
        self.assertTrue(r['correta'])
        r = conferir_linha(TL_VAZADA, ['e01', 'e02', 'e03', 'e05', 'e04', 'e06', 'e07'])
        self.assertFalse(r['correta'])
        self.assertEqual(r['intrusos'], ['e01'])
        self.assertEqual(r['faltando'], ['e15'])
        self.assertEqual(r['na_posicao'], 1, 'o intruso desloca tudo; só e05 cai na posição certa')
        r = conferir_linha(TL_VAZADA, ['e02', 'e03', 'e05', 'e04'])
        self.assertEqual(r['na_posicao'], 2)
        self.assertEqual(r['faltando'], ['e06', 'e07', 'e15'])

    def test_desativar_so_a_vazada_deixa_persistencia(self):
        r = avaliar_contencao(['desativar_vazada', 'registrar', 'preservar_logs'])
        self.assertEqual(r['ativos'], ['atacante', 'sessoes'])
        self.assertEqual(r['passos'][0][1], 'alerta')
        self.assertEqual(r['veredito'], 'incompleto')

    def test_apagar_antes_de_registrar_destroi(self):
        self.assertEqual(avaliar_contencao(['apagar_usuario'])['passos'][0][1], 'destroi')
        self.assertEqual(avaliar_contencao(['registrar', 'apagar_usuario'])['passos'][1][1], 'ok')
        self.assertEqual(avaliar_contencao(['girar'])['passos'][0][1], 'destroi')
        self.assertEqual(avaliar_contencao(['encerrar_instancia', 'snapshot'])['passos'][1][1], 'perdido')
        self.assertEqual(avaliar_contencao(['snapshot', 'encerrar_instancia'])['passos'][1][1], 'ok')
        self.assertEqual(avaliar_contencao(['revogar_sessoes', 'revogar_sessoes'])['passos'][1][1], 'nada')

    def test_diagrama_no_formato_do_guia(self):
        body = self._body()
        caixas = re.findall('<div class="diagram-box">\\s*<div class="diagram-header">\\s*<span class="diagram-title">([^<]+)</span>.*?<pre class="mermaid" data-title="([^"]+)">', body, re.S)
        self.assertGreaterEqual(len(caixas), 1, 'falta um .diagram-box com cabeçalho e Mermaid')
        for titulo, data_title in caixas:
            self.assertEqual(titulo.strip(), data_title.strip())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        termos = ['CloudTrail', 'Event history', '90 dias', 'trilha', 'eventos de gerenciamento', 'eventos de dados', 'VPC Flow Logs', 'Azure Activity Log', 'Defender for Cloud', 'GuardDuty', 'Cloud Audit Logs', 'eventTime', 'eventSource', 'eventName', 'userIdentity', 'accessKeyId', 'sourceIPAddress', 'userAgent', 'requestParameters', 'errorCode', 'AccessDenied', 'GetCallerIdentity', 'ListBuckets', 'CreateUser', 'CreateAccessKey', 'AttachUserPolicy', 'GetObject', 'GetSessionToken', 'aws:TokenIssueTime', 'update-access-key', 'Inactive', 'lookup-events', 'snapshot', 'Object Lock', 'OIDC', 'SCP', 'persistência', 'linha do tempo', 'chave de acesso de longa duração', 'T1078.004', 'T1098', 'T1530', 'Ipê Store', 'AKIAIOSFODNN7EXAMPLE', '111122223333', 'Estudo 18', 'Estudo 21', 'Estudo 41', 'Estudo 52', 'NIST SP 800-61']
        for termo in termos:
            self.assertIn(termo, content, f'Termo obrigatório ausente: {termo}')

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn(f'{SLUG}/treinamento-deteccao-e-resposta-em-nuvem.html', content)
        self.assertIn(f'data-slug="{SLUG}"', content)
        self.assertIn(f'/ {len(ESTUDOS_DADOS)}', content)
if __name__ == '__main__':
    unittest.main()
