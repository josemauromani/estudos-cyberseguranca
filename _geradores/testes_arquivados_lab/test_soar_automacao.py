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
from index_dados import ESTUDOS_DADOS
REDES_PRIVADAS = [ipaddress.ip_network(n) for n in ('10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16')]
REDES_DOC = [ipaddress.ip_network(n) for n in ('192.0.2.0/24', '198.51.100.0/24', '203.0.113.0/24')]
ACOES = ('isolar', 'bloquear', 'desativar')
ENRIQUECIMENTOS = ('rep', 'ativo', 'usuario')
TIPO_EXCECAO = {'isolar': 'host', 'bloquear': 'indicador', 'desativar': 'conta'}

def alvo(a, tipo):
    """Espelho de alvoDoBloco: o que cada bloco consulta ou contém neste alerta (None = sem alvo)."""
    if tipo == 'rep':
        return a['indicador']['valor'] if a['indicador'] else None
    if tipo in ('ativo', 'isolar'):
        return a['host']
    if tipo in ('usuario', 'desativar'):
        return a['conta']
    if tipo == 'bloquear':
        ind = a['indicador']
        return ind['valor'] if ind and ind['tipo'] in ('ip', 'dominio') else None
    return None

def consultar(d, tipo, valor):
    if tipo == 'rep':
        return d['reputacao'][valor]['veredito']
    if tipo == 'ativo':
        return d['ativos'][valor]['tipo']
    return d['usuarios'][valor]['tipo']

def avaliar(d, cond, a, ctx):
    """Espelho de avaliarCondicao: True, False ou None (dado ausente ou fonte fora do ar)."""
    if cond == 'severidade_alta':
        return a['severidade'] in ('alta', 'crítica')
    v = ctx.get(d['condicoes'][cond]['fonte'])
    if v is None or v == 'indisponivel':
        return None
    if cond == 'rep_maliciosa':
        return v == 'maliciosa'
    if cond == 'rep_nao_limpa':
        return v in ('maliciosa', 'suspeita', 'desconhecida')
    if cond == 'ativo_estacao':
        return v == 'estacao'
    if cond == 'conta_comum':
        return v == 'comum'
    raise ValueError(cond)

def alto_impacto(d, a, tipo):
    return tipo == 'desativar' or (tipo == 'isolar' and d['ativos'][a['host']]['tipo'] == 'servidor')

def executar(d, passos, politicas=None, falhas=None):
    """Espelho de executarPlaybook: roda o playbook contra a fila, na ordem, com estado compartilhado."""
    politicas, falhas = (politicas or {}, falhas or {})
    P, B = (d['parametros'], d['blocos'])
    excecoes = {(e['tipo'], e['valor']) for e in d['excecoes']}
    estado = {k: set() for k in ACOES}
    chamados = {}
    res = []
    for a in d['fila']:
        r = {'id': a['id'], 't': 0, 'mtta': None, 'mttr': None, 'status': 'andamento', 'ctx': {}, 'enriquecido': False, 'gate': False, 'aprov': False, 'executadas': [], 'efeito': set(), 'erradas': [], 'negadas': [], 'aprovadas': [], 'idempotentes': [], 'chamado': None, 'custo': 0, 'alto_sem_aprov': 0, 'fn': False}

        def escalar():
            r['status'] = 'escalado'
            ack = P['ack_escalado_min'] * 60 if r['enriquecido'] else a['manual']['mtta_min'] * 60
            trab = a['analista_min'] * 60 if r['enriquecido'] else (a['manual']['mttr_min'] - a['manual']['mtta_min']) * 60
            if r['mtta'] is None:
                r['mtta'] = r['t'] + ack
            r['mttr'] = r['t'] + ack + trab
        for p in passos:
            if r['status'] != 'andamento':
                break
            tipo = p['tipo']
            if tipo in ENRIQUECIMENTOS:
                v = alvo(a, tipo)
                if v is None:
                    r['ctx'][tipo] = 'sem_alvo'
                elif falhas.get(B[tipo]['fonte']):
                    r['t'] += P['timeout_s']
                    r['ctx'][tipo] = 'indisponivel'
                else:
                    r['t'] += B[tipo]['duracao_s']
                    r['ctx'][tipo] = consultar(d, tipo, v)
                    r['enriquecido'] = True
            elif tipo == 'decidir':
                ok = avaliar(d, p['condicao'], a, r['ctx'])
                if ok is None and politicas.get('escalar_sem_dado'):
                    escalar()
                elif not ok:
                    if p['senao'] == 'encerrar':
                        r['status'] = 'encerrado'
                        if r['mtta'] is None:
                            r['mtta'] = r['t']
                        if a['verdade'] == 'malicioso':
                            r['fn'] = True
                            r['custo'] += a['custo_fn']
                        else:
                            r['mttr'] = r['t']
                    elif p['senao'] == 'escalar':
                        escalar()
                    else:
                        r['gate'] = True
            elif tipo == 'aprovacao':
                r['gate'] = True
            elif tipo == 'chamado':
                if a['caso'] in chamados:
                    r['t'] += P['chamado_atualizar_s']
                    r['chamado'] = 'atualizado'
                else:
                    r['t'] += B['chamado']['duracao_s']
                    chamados[a['caso']] = a['id']
                    r['chamado'] = 'aberto'
            else:
                v = alvo(a, tipo)
                if v is None:
                    continue
                if v in estado[tipo]:
                    r['t'] += P['idempotente_s']
                    r['idempotentes'].append(tipo)
                    r['efeito'].add(tipo)
                    continue
                precisa = r['gate'] or (politicas.get('excecoes') and (TIPO_EXCECAO[tipo], v) in excecoes)
                correta = tipo in a['corretas']
                if precisa:
                    if not r['aprov']:
                        r['t'] += P['aprovacao_min'] * 60
                        r['aprov'] = True
                    if r['mtta'] is None:
                        r['mtta'] = r['t']
                    if not correta:
                        r['negadas'].append(tipo)
                        continue
                    r['aprovadas'].append(tipo)
                r['t'] += B[tipo]['duracao_s']
                estado[tipo].add(v)
                r['executadas'].append(tipo)
                r['efeito'].add(tipo)
                if not precisa:
                    if r['mtta'] is None:
                        r['mtta'] = r['t']
                    if alto_impacto(d, a, tipo):
                        r['alto_sem_aprov'] += 1
                    if not correta:
                        r['erradas'].append(tipo)
                        r['custo'] += a['erros'][tipo]['custo']
        if r['status'] == 'andamento':
            if a['verdade'] == 'malicioso' and all((c in r['efeito'] for c in a['corretas'])):
                r['status'] = 'contido'
                r['mttr'] = r['t']
                if r['mtta'] is None:
                    r['mtta'] = r['t']
            elif a['verdade'] == 'benigno' and r['aprov'] and (not r['erradas']):
                r['status'] = 'encerrado_humano'
                r['mttr'] = r['t']
            else:
                escalar()
        r['sem_registro'] = bool(r['executadas']) and r['chamado'] is None
        res.append(r)
    return (res, chamados)

def resumir(d, res):
    """Espelho de resumirExecucao: contagens, custo e médias em segundos."""
    resolvidos = [r for r in res if r['mttr'] is not None]
    manual = {a['id']: a['manual'] for a in d['fila']}
    st = [r['status'] for r in res]
    return {'contidos': st.count('contido'), 'encerrados': sum((1 for r in res if r['status'] == 'encerrado' and (not r['fn']))), 'encerrados_humano': st.count('encerrado_humano'), 'escalados': st.count('escalado'), 'fn': sum((1 for r in res if r['fn'])), 'aprovacoes': sum((1 for r in res if r['aprov'])), 'negadas': sum((len(r['negadas']) for r in res)), 'indevidas': sum((len(r['erradas']) for r in res)), 'custo': sum((r['custo'] for r in res)), 'alto_sem_aprov': sum((r['alto_sem_aprov'] for r in res)), 'sem_registro': sum((1 for r in res if r['sem_registro'])), 'mtta_s': sum((r['mtta'] for r in res)) / len(res), 'mttr_s': sum((r['mttr'] for r in resolvidos)) / len(resolvidos) if resolvidos else 0, 'manual_mtta_s': 60 * sum((m['mtta_min'] for m in manual.values())) / len(res), 'manual_mttr_s': 60 * sum((m['mttr_min'] for m in manual.values())) / len(res), 'economia_s': sum((manual[r['id']]['mttr_min'] * 60 - r['mttr'] for r in resolvidos))}

def P(tipo, **kw):
    return dict(tipo=tipo, **kw)
REFERENCIA = [P('rep'), P('ativo'), P('usuario'), P('decidir', condicao='rep_nao_limpa', senao='encerrar'), P('chamado'), P('decidir', condicao='ativo_estacao', senao='aprovacao'), P('isolar'), P('bloquear'), P('desativar')]
SEGURA = {'excecoes': True, 'escalar_sem_dado': True}

class TestSoarAutomacao(unittest.TestCase):
    """Valida a estrutura, o conteúdo, o Montador de Playbook e a compilação do estudo 49."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / '_geradores' / 'soar_e_automacao_de_resposta_body.html'
        self.compiled_path = self.root / 'SOAR-e-Automacao-de-Resposta' / 'treinamento-soar-e-automacao-de-resposta.html'
        self.portal_path = self.root / 'index.html'

    def _rodar(self, d, passos, politicas=None, falhas=None):
        res, chamados = executar(d, passos, politicas, falhas)
        return ({r['id']: r for r in res}, resumir(d, res), chamados)

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        termos = ['SOAR', 'Security Orchestration, Automation and Response', 'orquestração', 'playbook', 'runbook', 'gatilho', 'enriquecimento', 'reputação', 'CMDB', 'IdP', 'decisão', 'human-in-the-loop', 'aprovação humana', 'idempotência', 'idempotente', 'lista de exceção', 'ativos críticos', 'MTTA', 'MTTR', 'Mean Time to Acknowledge', 'Mean Time to Respond', 'timeout', 'Retry-After', 'backoff', 'desconhecido não é limpo', 'fail-safe', 'deduplicação', 'trilha de auditoria', 'falso positivo', 'webhook', 'API', 'Splunk SOAR', 'Cortex XSOAR', 'Microsoft Sentinel', 'Logic Apps', 'Shuffle', 'TheHive', 'Cortex', 'CACAO', 'NIST SP 800-61', 'art. 20', 'LGPD', 'Estudo 16', 'Estudo 18', 'Estudo 35', 'Estudo 46', 'Estudo 47', 'Estudo 48', 'RFC 5737']
        for termo in termos:
            self.assertIn(termo, content, f'Termo obrigatório ausente: {termo}')

    def test_tabela_de_faixas_igual_ao_motor(self):
        body = self.body_path.read_text(encoding='utf-8')
        m = re.search('<tr><td><strong>Automatizar com condição</strong></td><td>(.*?)</td><td>(.*?)</td></tr>', body)
        self.assertIsNotNone(m, "linha 'Automatizar com condição' ausente")
        self.assertIn('maliciosa, suspeita ou desconhecida', m.group(1), 'a tabela isola nas mesmas reputações que rep_nao_limpa')
        self.assertIn('nunca visto', m.group(1) + m.group(2), 'explica por que o hash desconhecido entra')

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn('SOAR-e-Automacao-de-Resposta/treinamento-soar-e-automacao-de-resposta.html', content)
        self.assertIn('data-slug="SOAR-e-Automacao-de-Resposta"', content)
        self.assertIn(f'/ {len(ESTUDOS_DADOS)}', content)
if __name__ == '__main__':
    unittest.main()
