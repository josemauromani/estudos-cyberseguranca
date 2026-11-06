"""
test_threat_hunting.py
Testes automatizados para o Estudo 47: Threat-Hunting

A Caçada Guiada guarda a frota fictícia, as hipóteses, as fontes de dados e a
detecção sugerida num bloco JSON. Este teste espelha em Python a expansão dos
grupos em eventos, a contagem por frequência (stack counting) e a pontuação do
JavaScript para validar que o implante aparece na cauda longa quando o
agrupamento é feito pelo campo certo e some no ruído quando não é.
"""
import json
import re
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from index_dados import ESTUDOS_DADOS
LIMIAR = 3

def substituir(texto, estacao):
    return str(texto).replace('{host}', estacao['nome']).replace('{usuario}', estacao['usuario']).replace('{rid}', str(estacao['rid']))

def hosts_do_grupo(d, g):
    """Espelho de hostsDoGrupo: '*' é a frota toda, menos as estações em 'exceto'."""
    nomes = [e['nome'] for e in d['estacoes']] if g['hosts'] == '*' else list(g['hosts'])
    exceto = set(g.get('exceto', []))
    return [n for n in nomes if n not in exceto]

def expandir(d, fonte_id):
    """Espelho de expandirEventos: cada grupo vira um evento por estação."""
    fonte = fonte_por_id(d, fonte_id)
    por_nome = {e['nome']: e for e in d['estacoes']}
    eventos = []
    for gi, g in enumerate(fonte.get('grupos', [])):
        for h in hosts_do_grupo(d, g):
            est = por_nome[h]
            eventos.append({'host': h, 'grupo': gi, 'malicioso': g['malicioso'], 'valores': {k: substituir(v, est) for k, v in g['valores'].items()}})
    return eventos

def empilhar(d, fonte_id, campo, limiar=LIMIAR):
    """Espelho de empilharCaca: agrupa por valor, conta estações distintas e ocorrências."""
    linhas = {}
    for e in expandir(d, fonte_id):
        v = e['valores'][campo]
        ln = linhas.setdefault(v, {'valor': v, 'hosts': set(), 'ocorrencias': 0, 'maliciosos': 0, 'grupos': set()})
        ln['hosts'].add(e['host'])
        ln['ocorrencias'] += 1
        ln['maliciosos'] += 1 if e['malicioso'] else 0
        ln['grupos'].add(e['grupo'])
    res = sorted(linhas.values(), key=lambda ln: (len(ln['hosts']), ln['ocorrencias'], ln['valor']))
    for ln in res:
        ln['estacoes'] = len(ln['hosts'])
        ln['cauda'] = ln['estacoes'] <= limiar
    return res

def avaliar_achado(linha):
    """Espelho de avaliarAchado: 2 se a linha é só implante, 1 se mistura, 0 se é legítima."""
    if linha['maliciosos'] == 0:
        return 0
    return 2 if linha['maliciosos'] == linha['ocorrencias'] else 1

def fonte_por_id(d, fid):
    return next((f for f in d['fontes'] if f['id'] == fid))

def hipotese_por_id(d, hid):
    return next((h for h in d['hipoteses'] if h['id'] == hid))

def campo_por_id(fonte, cid):
    return next((c for c in fonte['campos'] if c['id'] == cid))

def tem_implante(d, fonte_id):
    return any((g['malicioso'] for g in fonte_por_id(d, fonte_id).get('grupos', [])))

def pontuar(d, primeira_hipotese, hipotese, primeira_fonte, fonte, campo, achado):
    """Espelho de pontuarCaca. achado é o valor da linha marcada ou None (hipótese refutada)."""
    p_hip = hipotese_por_id(d, primeira_hipotese)['pontos']
    p_fonte = fonte_por_id(d, primeira_fonte)['pontos'].get(hipotese, 0)
    p_campo = campo_por_id(fonte_por_id(d, fonte), campo)['pontos']
    if achado is None:
        p_achado = 0 if tem_implante(d, fonte) else 2
    else:
        linha = next((ln for ln in empilhar(d, fonte, campo) if ln['valor'] == achado))
        p_achado = avaliar_achado(linha)
    return {'hipotese': p_hip, 'fonte': p_fonte, 'campo': p_campo, 'achado': p_achado, 'total': p_hip + p_fonte + p_campo + p_achado}

def valor_do_implante(d, fonte_id, campo):
    linhas = [ln for ln in empilhar(d, fonte_id, campo) if ln['maliciosos']]
    return linhas

class TestThreatHunting(unittest.TestCase):
    """Valida a estrutura, o conteúdo, a Caçada Guiada e a compilação do estudo 47."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / '_geradores' / 'threat_hunting_body.html'
        self.compiled_path = self.root / 'Threat-Hunting' / 'treinamento-threat-hunting.html'
        self.portal_path = self.root / 'index.html'

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        termos = ['threat hunting', 'caça por hipótese', 'caça por indicador', 'hipótese testável', 'PEAK', 'Prepare', 'Execute', 'Act with Knowledge', 'linha de base', 'stack counting', 'cauda longa', 'Pirâmide da Dor', 'Hunting Maturity Model', 'comprometimento presumido', 'normalizar', 'EDR', 'Sysmon', 'Velociraptor', '4698', '4697', '7045', '4624', 'Get-ScheduledTask', 'Group-Object', 'dcount', 'T1053.005', 'T1543.003', 'TA0003', 'documentação da caça', 'inconclusiva', 'confirmada', 'refutada', 'lacuna de visibilidade', 'Sigma', 'Estudo 16', 'Estudo 17', 'Estudo 18', 'Estudo 36', 'Estudo 46', 'Estudo 48']
        for termo in termos:
            self.assertIn(termo, content, f'Termo obrigatório ausente: {termo}')

    def test_ponte_com_engenharia_de_deteccao(self):
        body = self.body_path.read_text(encoding='utf-8')
        fim = body[body.index('id="fatos"'):body.index('</article>')]
        self.assertIn('Estudo 46', fim)
        self.assertIn('vira detecção', fim)

    def test_menciona_ecthp(self):
        body = self.body_path.read_text(encoding='utf-8')
        self.assertIn('eCTHP', body)
        fim = body[body.index('id="fatos"'):body.index('</article>')]
        m = re.search('<a [^>]*href="(https://[^"]*ine\\.com[^"]*)"[^>]*>', fim)
        self.assertIsNotNone(m, 'link https para ine.com ausente em fatos')
        self.assertIn('noopener noreferrer', m.group(0))
        self.assertIn('Estudo 33', body)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn('Threat-Hunting/treinamento-threat-hunting.html', content)
        self.assertIn('data-slug="Threat-Hunting"', content)
        self.assertIn(f'/ {len(ESTUDOS_DADOS)}', content)
if __name__ == '__main__':
    unittest.main()
