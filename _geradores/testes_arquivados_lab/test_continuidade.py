"""
test_continuidade.py
Testes automatizados para o Estudo 28: Continuidade-e-Disaster-Recovery
"""
import json
import re
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from index_dados import ESTUDOS_DADOS
CENARIOS = ['storage', 'incendio', 'ransomware', 'exclusao']

def custo(d, e):
    c = d['custos']
    return c['frequencia'][str(e['frequencia_h'])] + c['replicacao'][e['replicacao']] + c['site'][e['site']] + sum((c['copias'][x] for x in e['copias'])) + c['retencao'][str(e['retencao_dias'])] + (c['teste'] if e['teste'] else 0)

def regra_32110(d, e):
    copias = [d['tipos_copia'][x] for x in e['copias']]
    return {'tres_copias': 1 + len(copias) >= 3, 'duas_midias': len({'disco'} | {c['midia'] for c in copias}) >= 2, 'uma_fora': any((c['local'] != 'mesmo_datacenter' for c in copias)), 'uma_imutavel_offline': any((c['imutavel'] or c['offline'] for c in copias)), 'zero_erros': bool(e['teste'])}

def recuperar(d, s, e, cenario):
    """Melhor forma de recuperar o sistema s com a estratégia e no cenário. Espelho do JavaScript."""
    opcoes = []
    site = d['sites'][e['site']]
    if e['replicacao'] != 'nenhuma' and e['site'] != 'nenhum' and (cenario in ('storage', 'incendio')):
        opcoes.append({'metodo': 'failover', 'parada': site['ativacao_h'], 'perda': d['perda_replicacao'][e['replicacao']], 'copia': None})
    if cenario == 'exclusao' and e['retencao_dias'] < d['exclusao_descoberta_dias']:
        sobreviventes = []
    else:
        sobreviventes = []
        for x in e['copias']:
            t = d['tipos_copia'][x]
            if cenario == 'incendio' and t['local'] == 'mesmo_datacenter':
                continue
            if cenario == 'ransomware' and (not (t['imutavel'] or t['offline'])):
                continue
            sobreviventes.append(x)
    if sobreviventes:
        infra = (site['ativacao_h'] if e['site'] != 'nenhum' else d['nova_infra_h']) if cenario == 'incendio' else 0
        melhor = min(sobreviventes, key=lambda x: (s['tamanho_gb'] / d['tipos_copia'][x]['taxa_gb_h'], x))
        tempo = infra + s['tamanho_gb'] / d['tipos_copia'][melhor]['taxa_gb_h']
        if not e['teste']:
            tempo *= 1.5
        opcoes.append({'metodo': 'restauracao', 'parada': round(tempo, 2), 'perda': e['frequencia_h'], 'copia': melhor})
    if not opcoes:
        return {'metodo': 'irrecuperavel', 'parada': None, 'perda': None, 'copia': None}
    return min(opcoes, key=lambda o: (o['parada'], o['perda'], o['metodo']))

def avaliar(d, alvos, estrategias):
    res = {}
    for s in d['sistemas']:
        a, e = (alvos[s['id']], estrategias[s['id']])
        linhas = {}
        for c in CENARIOS:
            r = recuperar(d, s, e, c)
            ok = r['metodo'] != 'irrecuperavel' and r['parada'] <= a['rto'] and (r['perda'] <= a['rpo'])
            linhas[c] = dict(r, ok=ok)
        res[s['id']] = {'cenarios': linhas, 'custo': custo(d, e), 'regra': regra_32110(d, e), 'bia_ok': a['rto'] <= s['mtpd_h'] and a['rpo'] <= s['perda_tolerada_h']}
    return res

class TestContinuidade(unittest.TestCase):
    """Valida a estrutura, o conteúdo, a BIA, as estratégias, os cenários e a compilação do estudo 28."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / '_geradores' / 'continuidade_e_disaster_recovery_body.html'
        self.compiled_path = self.root / 'Continuidade-e-Disaster-Recovery' / 'treinamento-continuidade-e-disaster-recovery.html'
        self.portal_path = self.root / 'index.html'

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        termos = ['BCP', 'DRP', 'BIA', 'MTPD', 'RTO', 'RPO', 'MBCO', 'ISO 22301', 'site quente', 'site morno', 'site frio', 'replicação síncrona', 'replicação assíncrona', '3-2-1', '3-2-1-1-0', 'imutável', 'retenção', 'teste de restauração', 'Estudo 44', 'Estudo 45', 'Estudo 25']
        for termo in termos:
            self.assertIn(termo, content, f'Termo obrigatório ausente: {termo}')

    def _secao_iso22301(self, texto):
        ini = texto.index('<section class="study-section" id="iso-22301" data-tipo="teoria">')
        return texto[ini:texto.index('</section>', ini)]

    def test_secao_iso_22301_conteudo(self):
        for texto in (self.body_path.read_text(encoding='utf-8'), self.compiled_path.read_text(encoding='utf-8')):
            sec = self._secao_iso22301(texto)
            for termo in ('ISO 22301:2019', 'SGCN', 'BIA', 'exercícios', 'certificação', '2024', 'MTPD', 'ISO 22313'):
                self.assertIn(termo, sec, termo)

    def test_secao_iso_22301_referencia(self):
        for texto in (self.body_path.read_text(encoding='utf-8'), self.compiled_path.read_text(encoding='utf-8')):
            ini = texto.index('id="fatos"')
            self.assertIn('ISO 22301:2019', texto[ini:texto.index('</section>', ini)])

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn('Continuidade-e-Disaster-Recovery/treinamento-continuidade-e-disaster-recovery.html', content)
        self.assertIn('data-slug="Continuidade-e-Disaster-Recovery"', content)
        self.assertIn(f'/ {len(ESTUDOS_DADOS)}', content)
if __name__ == '__main__':
    unittest.main()
