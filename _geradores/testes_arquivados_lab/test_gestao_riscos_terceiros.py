"""
test_gestao_riscos_terceiros.py
Testes automatizados para o Estudo 57: Gestao-de-Riscos-de-Terceiros

O simulador Avaliador de Fornecedores guarda num bloco JSON os eixos do
questionário (dados, acesso, dependência), o catálogo de cláusulas, os itens
do plano de saída e três fornecedores fictícios avaliados pela Ipê Pay, com
respostas a questionário, evidências (ISO 27001, SOC 2, teste de intrusão,
declaração de subcontratados) e a proposta de plano de saída. Este teste
espelha em Python as regras do motor JavaScript: impacto, probabilidade,
criticidade, risco inerente, validade de cada evidência, redução e risco
residual, cláusulas obrigatórias por criticidade, lacunas do plano de saída,
decisão (contratar, contratar com condições ou recusar) e a correção das
respostas do aluno, inclusive as armadilhas didáticas.
"""
import json
import re
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from index_dados import ESTUDOS_DADOS
SLUG = 'Gestao-de-Riscos-de-Terceiros'
CRITICIDADES = ('baixa', 'media', 'critica')
DECISOES = ('contratar', 'condicoes', 'recusar')
CLAUSULAS = ('notificacao_incidente', 'direito_auditoria', 'subcontratacao', 'localizacao_dados', 'devolucao_eliminacao', 'plano_saida', 'acesso_regulador')
ITENS_SAIDA = ('exportacao_formato_aberto', 'prazo_transicao', 'transferencia_antes_exclusao', 'eliminacao_certificada', 'fornecedor_alternativo', 'gatilhos_saida')
TIPOS_EVIDENCIA = ('iso27001', 'soc2', 'pentest', 'subcontratados')
GABARITO = {'F1': {'impacto': 5, 'prob': 5, 'crit': 'critica', 'inerente': 25, 'faixa': 'Crítico', 'validas': {'F1-iso', 'F1-soc2', 'F1-pentest', 'F1-sub'}, 'reducao': 4, 'residual': 5, 'clausulas': set(CLAUSULAS), 'lacunas': [], 'decisao': 'contratar'}, 'F2': {'impacto': 4, 'prob': 4, 'crit': 'critica', 'inerente': 16, 'faixa': 'Crítico', 'validas': {'F2-soc2', 'F2-pentest', 'F2-sub'}, 'reducao': 2, 'residual': 10, 'clausulas': set(CLAUSULAS) - {'acesso_regulador'}, 'lacunas': ['prazo_transicao', 'transferencia_antes_exclusao', 'fornecedor_alternativo'], 'decisao': 'condicoes'}, 'F3': {'impacto': 3, 'prob': 3, 'crit': 'media', 'inerente': 9, 'faixa': 'Médio', 'validas': set(), 'reducao': -1, 'residual': 11, 'clausulas': {'notificacao_incidente', 'direito_auditoria', 'subcontratacao', 'devolucao_eliminacao'}, 'lacunas': ['transferencia_antes_exclusao', 'eliminacao_certificada'], 'decisao': 'recusar'}}

def impacto(f):
    """Espelho de impactoFornecedor: o maior eixo entre dados e dependência manda; se ambos >= 2, +1."""
    d, p = (f['eixos']['dados'], f['eixos']['dependencia'])
    return min(5, 1 + max(d, p) + (1 if min(d, p) >= 2 else 0))

def probabilidade(f):
    """Espelho de probabilidadeFornecedor: 1 + acesso + 1 se existe quarta parte (declarada ou não)."""
    return min(5, 1 + f['eixos']['acesso'] + (1 if f['quarta_parte'] else 0))

def criticidade(f):
    """Espelho de criticidadeFornecedor: impacto >= 4 crítica; 2 a 3 média; 1 baixa."""
    i = impacto(f)
    return 'critica' if i >= 4 else 'media' if i >= 2 else 'baixa'

def inerente(f):
    return impacto(f) * probabilidade(f)

def faixa(d, pontos):
    """Espelho de faixaRisco."""
    for fx in d['faixas']:
        if fx['min'] <= pontos <= fx['max']:
            return fx['nome']
    return None

def validar_evidencia(ev, f, data_ref):
    """Espelho de validarEvidencia: valida, pontos nominais (o que o fornecedor alega) e pontos reais."""
    t = ev['tipo']
    if t == 'iso27001':
        valida = ev['cobre_servico'] and ev['validade'] >= data_ref
        nominal = 1
    elif t == 'soc2':
        valida = ev['tipo_relatorio'] == 'II' and ev['periodo_meses'] >= 6 and (ev['emitido_ha_meses'] <= 12)
        nominal = 2 - (1 if any((x['relevante'] for x in ev['excecoes'])) else 0)
    elif t == 'pentest':
        valida = ev['meses_desde'] <= 12 and ev['criticos_abertos'] == 0 and ev['independente']
        nominal = 1
    elif t == 'subcontratados':
        valida = all((q['declarado'] for q in f['quarta_parte'] if q['critico']))
        nominal = 0
    else:
        raise ValueError(t)
    return {'valida': bool(valida), 'nominal': nominal}

def contribuicao(ev, aceita):
    """Aceita: soma os pontos nominais. Recusada: zero; declaração de subcontratados recusada pesa -1."""
    v_nominal = {'iso27001': 1, 'pentest': 1, 'subcontratados': 0}.get(ev['tipo'])
    if ev['tipo'] == 'soc2':
        v_nominal = 2 - (1 if any((x['relevante'] for x in ev['excecoes'])) else 0)
    if aceita:
        return v_nominal
    return -1 if ev['tipo'] == 'subcontratados' else 0

def reducao(f, data_ref, aceitas=None):
    """Espelho de reducaoRisco: com aceitas=None usa a validade real; senão, as escolhas do aluno."""
    total = 0
    for ev in f['evidencias']:
        ok = validar_evidencia(ev, f, data_ref)['valida'] if aceitas is None else ev['id'] in aceitas
        total += contribuicao(ev, ok)
    return max(-1, min(4, total))

def residual(inerente_pts, r):
    """Espelho de riscoResidual: inerente × (100 − 20·R)%, arredondado meio para cima, mínimo 1."""
    return max(1, (inerente_pts * (100 - 20 * r) + 50) // 100)

def clausulas_obrigatorias(d, f):
    """Espelho de clausulasObrigatorias."""
    base = list(d['clausulas_por_criticidade'][criticidade(f)])
    if f['nuvem_relevante']:
        for c in d['clausulas_nuvem_relevante']:
            if c not in base:
                base.append(c)
    return [c for c in d['clausulas'] if c in base]

def lacunas_saida(d, f):
    """Espelho de lacunasSaida: itens exigidos pela criticidade que a proposta não prevê."""
    return [i for i in d['saida_por_criticidade'][criticidade(f)] if i not in f['plano_saida']]

def decidir(d, f, aceitas=None):
    """Espelho de decidirFornecedor."""
    r = reducao(f, d['data_ref'], aceitas)
    res = residual(inerente(f), r)
    obrig = clausulas_obrigatorias(d, f)
    bloqueios = [c for c in f['recusa_clausulas'] if c in obrig]
    invalidas = [ev['id'] for ev in f['evidencias'] if not (validar_evidencia(ev, f, d['data_ref'])['valida'] if aceitas is None else ev['id'] in aceitas)]
    lac = lacunas_saida(d, f)
    pendencias = invalidas + lac
    if bloqueios or res >= d['limite_recusa']:
        dec = 'recusar'
    elif res <= d['apetite'] and (not pendencias):
        dec = 'contratar'
    else:
        dec = 'condicoes'
    return {'decisao': dec, 'residual': res, 'reducao': r, 'bloqueios': bloqueios, 'invalidas': invalidas, 'lacunas': lac, 'pendencias': pendencias}

def corrigir(d, f, resp):
    """Espelho de corrigirFornecedor: 5 pontos (criticidade, faixa, evidências, cláusulas, decisão)."""
    validas = {ev['id'] for ev in f['evidencias'] if validar_evidencia(ev, f, d['data_ref'])['valida']}
    aceitas = set(resp['aceitas'])
    ev_status = {}
    for ev in f['evidencias']:
        a, v = (ev['id'] in aceitas, ev['id'] in validas)
        ev_status[ev['id']] = 'acerto' if a == v else 'aceitou_invalida' if a else 'rejeitou_valida'
    obrig = set(clausulas_obrigatorias(d, f))
    esc = set(resp['clausulas'])
    cl_status = {}
    for c in d['clausulas']:
        if c in obrig:
            cl_status[c] = 'acerto' if c in esc else 'faltou'
        elif c in esc:
            cl_status[c] = 'excesso'
    gab = decidir(d, f)
    out = {'criticidade_ok': resp['criticidade'] == criticidade(f), 'faixa_ok': resp['faixa'] == faixa(d, inerente(f)), 'evidencias': ev_status, 'evidencias_ok': all((s == 'acerto' for s in ev_status.values())), 'clausulas': cl_status, 'clausulas_ok': all((s == 'acerto' for s in cl_status.values())), 'decisao_ok': resp['decisao'] == gab['decisao'], 'residual_aluno': residual(inerente(f), reducao(f, d['data_ref'], aceitas)), 'residual_real': gab['residual']}
    out['pontos'] = sum((int(out[k]) for k in ('criticidade_ok', 'faixa_ok', 'evidencias_ok', 'clausulas_ok', 'decisao_ok')))
    return out

class TestGestaoRiscosTerceiros(unittest.TestCase):
    """Estrutura, conteúdo, simulador e compilação do estudo 57."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / '_geradores' / 'gestao_de_riscos_de_terceiros_body.html'
        self.compiled_path = self.root / SLUG / 'treinamento-gestao-de-riscos-de-terceiros.html'
        self.portal_path = self.root / 'index.html'

    def _body(self):
        return self.body_path.read_text(encoding='utf-8')

    def _forn(self, d, fid):
        return next((f for f in d['fornecedores'] if f['id'] == fid))

    def _resp_gabarito(self, d, f):
        g = GABARITO[f['id']]
        return {'criticidade': g['crit'], 'faixa': g['faixa'], 'aceitas': sorted(g['validas']), 'clausulas': sorted(g['clausulas']), 'decisao': g['decisao']}

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_aviso_da_redacao_de_2021(self):
        """Requisitos descritos no nível da redação original de 2021 da CMN 4.893 trazem o aviso de conferir a redação de dez/2025."""
        body = self._body()
        self.assertIn('redação original de 2021', body)
        self.assertIn('confira a redação vigente', body)

    def test_referencias_normativas(self):
        body = self._body()
        for termo in ('GV.SC', 'NIST CSF 2.0', 'ISO/IEC 27002:2022', '5.19', '5.20', '5.21', '5.22', '5.23', 'Res. CMN 4.893', 'CMN 5.274/2025', 'SOC 2 Tipo I', 'SOC 2 Tipo II', 'quarta parte', 'T1195', 'T1199', 'direito de auditoria', 'plano de saída', 'países e regiões', 'responsabilidade não se transfere'):
            self.assertIn(termo, body, termo)

    def test_sem_numero_de_artigo_da_cmn(self):
        body = self._body()
        self.assertIsNone(re.search('art(?:igo|\\.)\\s*\\d+[^<]{0,80}(?:4\\.893|5\\.274)', body, re.I), 'não citar número de artigo da Res. CMN 4.893')
        self.assertIsNone(re.search('(?:4\\.893|5\\.274)[^<]{0,80}art(?:igo|\\.)\\s*\\d+', body, re.I), 'não citar número de artigo da Res. CMN 4.893')

    def test_diagrama_no_formato_do_guia(self):
        body = self._body()
        caixas = re.findall('<div class="diagram-box">\\s*<div class="diagram-header">\\s*<span class="diagram-title">([^<]+)</span>.*?<pre class="mermaid" data-title="([^"]+)">', body, re.S)
        self.assertGreaterEqual(len(caixas), 1, 'falta um .diagram-box com cabeçalho e Mermaid')
        for titulo, data_title in caixas:
            self.assertEqual(titulo.strip(), data_title.strip())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        termos = ['ciclo de vida do terceiro', 'due diligence', 'criticidade', 'risco inerente', 'risco residual', 'questionário', 'autodeclaração', 'escopo', 'Declaração de Aplicabilidade', 'exceções', 'organizações subcontratadas', 'quarta parte', 'notificação de incidente', 'direito de auditoria', 'subcontratação', 'devolução', 'eliminação', 'plano de saída', 'monitoramento contínuo', 'Ipê Pay', 'fornecedor crítico', 'concentração']
        for termo in termos:
            self.assertIn(termo, content, f'Termo obrigatório ausente: {termo}')

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn(f'{SLUG}/treinamento-gestao-de-riscos-de-terceiros.html', content)
        self.assertIn(f'data-slug="{SLUG}"', content)
        self.assertIn(f'{len(ESTUDOS_DADOS)} / {len(ESTUDOS_DADOS)}', content, 'portal com todos os módulos compilados')
if __name__ == '__main__':
    unittest.main()
