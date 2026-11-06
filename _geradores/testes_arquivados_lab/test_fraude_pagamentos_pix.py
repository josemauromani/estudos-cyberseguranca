"""
test_fraude_pagamentos_pix.py
Testes automatizados para o Estudo 55: Fraude-em-Pagamentos-e-Pix

O simulador Mesa Antifraude guarda num bloco JSON os sinais de risco (com
peso padrão e faixa do controle deslizante), os limiares padrão de "segurar"
e "bloquear" e a fila de transações Pix fictícias da Ipê Pay (instituição de
pagamento fictícia do Estudo 54): golpes típicos (falsa central, falso
parente, conta laranja, sequestro de conta) e casos legítimos que parecem
suspeitos. Este teste espelha em Python as regras do motor JavaScript:
pontuação de risco (soma dos pesos dos sinais presentes), decisão por limiar
(aprovar, segurar ou bloquear), desfecho de cada transação, contagens de
fraudes evitadas e clientes legítimos bloqueados e a recuperação pelo MED 2.0
para as fraudes que passaram (devolução limitada ao saldo, com rastreio para
outras contas e prazo de 80 dias corridos para a vítima contestar).
"""
import json
import re
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from index_dados import ESTUDOS_DADOS
SLUG = 'Fraude-em-Pagamentos-e-Pix'
DECISOES = ('aprovar', 'segurar', 'bloquear')
GOLPES = ('falsa_central', 'falso_parente', 'conta_laranja', 'sequestro_conta')
PRAZO_CONTESTACAO = 80
PESOS_PADRAO = {'valor_atipico': 25, 'madrugada': 10, 'conta_nova': 25, 'chave_nova': 10, 'primeiro_pix': 10, 'dispositivo_novo': 20, 'limite_alterado': 20, 'em_ligacao': 15, 'muitos_pagadores': 20, 'denuncias': 35, 'recebedor_recorrente': -15}
LIMIARES_PADRAO = {'segurar': 40, 'bloquear': 70}
FILA = {'T01': (False, None, 35), 'T02': (True, 'falso_parente', 45), 'T03': (True, 'falsa_central', 95), 'T04': (False, None, 20), 'T05': (True, 'conta_laranja', 65), 'T06': (False, None, 5), 'T07': (True, 'falso_parente', 35), 'T08': (False, None, 50), 'T09': (True, 'falsa_central', 50), 'T10': (False, None, 55), 'T11': (True, 'conta_laranja', 20), 'T12': (False, None, 45), 'T13': (True, 'sequestro_conta', 85), 'T14': (False, None, 25)}

def pontuar_risco(t, pesos):
    """Espelho de pontuarRisco: soma dos pesos dos sinais presentes na transação."""
    return sum((pesos.get(s, 0) for s in t['sinais']))

def decidir(pontos, limiares):
    """Espelho de decidirTransacao: bloquear tem precedência sobre segurar."""
    if pontos >= limiares['bloquear']:
        return 'bloquear'
    if pontos >= limiares['segurar']:
        return 'segurar'
    return 'aprovar'

def recuperacao_med(t):
    """Espelho de simularMed: devolução limitada ao saldo encontrado, dentro do prazo de contestação."""
    med = t['med']
    if med['dias_para_contestar'] > PRAZO_CONTESTACAO:
        return {'no_prazo': False, 'so_original': 0, 'med2': 0}
    rastreado = sum((c['saldo'] for c in med['rastreio']))
    return {'no_prazo': True, 'so_original': min(t['valor'], med['saldo_recebedora']), 'med2': min(t['valor'], med['saldo_recebedora'] + rastreado)}

def desfecho(t, decisao):
    if t['fraude']:
        if decisao == 'bloquear' or (decisao == 'segurar' and t['analise_evita']):
            return 'fraude_evitada'
        return 'fraude_passou'
    return {'aprovar': 'legitima_aprovada', 'segurar': 'legitima_segurada', 'bloquear': 'legitima_bloqueada'}[decisao]

def avaliar_mesa(d, pesos, limiares, manuais=None):
    """Espelho de avaliarMesa: decide cada transação (manual vence a automática) e consolida os números."""
    manuais = manuais or {}
    r = {'itens': [], 'fraudes': 0, 'fraudes_evitadas': 0, 'prejuizo_evitado': 0, 'fraudes_passaram': 0, 'prejuizo_passou': 0, 'legitimas': 0, 'legitimas_bloqueadas': 0, 'legitimas_seguradas': 0, 'seguradas': 0, 'recuperado_med2': 0, 'recuperado_so_original': 0}
    for t in d['transacoes']:
        pontos = pontuar_risco(t, pesos)
        auto = decidir(pontos, limiares)
        dec = manuais.get(t['id']) if manuais.get(t['id']) in DECISOES else auto
        res = desfecho(t, dec)
        item = {'id': t['id'], 'pontos': pontos, 'automatica': auto, 'decisao': dec, 'desfecho': res}
        if dec == 'segurar':
            r['seguradas'] += 1
        if t['fraude']:
            r['fraudes'] += 1
            if res == 'fraude_evitada':
                r['fraudes_evitadas'] += 1
                r['prejuizo_evitado'] += t['valor']
            else:
                r['fraudes_passaram'] += 1
                r['prejuizo_passou'] += t['valor']
                med = recuperacao_med(t)
                item['med'] = med
                r['recuperado_med2'] += med['med2']
                r['recuperado_so_original'] += med['so_original']
        else:
            r['legitimas'] += 1
            if res == 'legitima_bloqueada':
                r['legitimas_bloqueadas'] += 1
            elif res == 'legitima_segurada':
                r['legitimas_seguradas'] += 1
        r['itens'].append(item)
    return r

class TestFraudePagamentosPix(unittest.TestCase):
    """Estrutura, conteúdo, simulador e compilação do estudo 55."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / '_geradores' / 'fraude_em_pagamentos_e_pix_body.html'
        self.compiled_path = self.root / SLUG / 'treinamento-fraude-em-pagamentos-e-pix.html'
        self.portal_path = self.root / 'index.html'

    def _body(self):
        return self.body_path.read_text(encoding='utf-8')

    def _pesos(self, d, **alt):
        p = {s['id']: s['peso'] for s in d['sinais']}
        p.update(alt)
        return p

    def _resumo(self, r):
        return (r['fraudes_evitadas'], r['legitimas_bloqueadas'], r['legitimas_seguradas'], r['prejuizo_evitado'], r['prejuizo_passou'], r['recuperado_med2'], r['recuperado_so_original'])

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_med_com_os_fatos_conferidos(self):
        body = self._body()
        for termo in ('Res. BCB 493', '28/08/2025', '01/10/2025', '80 dias corridos', 'IN BCB 766', '01/09/2026', '7 dias', 'até 11 dias', 'contas diferentes', 'parcial', 'autoatendimento', 'bloqueio cautelar', 'fevereiro de 2026'):
            self.assertIn(termo, body, termo)
        self.assertIsNone(re.search('11 dias (?:úteis|corridos)', body), 'não qualificar os 11 dias')
        self.assertIsNone(re.search('bloqueio cautelar[^.]{0,80}\\d+\\s*(?:horas|dias|h\\b)', body), 'bloqueio cautelar sem prazo')
        self.assertIsNone(re.search('\\bart(?:igo|\\.)?\\s*\\d', body, re.I), 'não citar número de artigo não conferido')

    def test_fontes_dos_prazos_do_med_sao_as_conferidas(self):
        """Os prazos vieram de comunicados do BCB e da IN BCB 766, não do texto da Res. BCB 493."""
        body = self._body()
        self.assertNotIn('foram conferidos na Res. BCB 493', body)
        self.assertIn('comunicados do Banco Central', body)
        self.assertIn('IN BCB 766', body)

    def test_diagrama_poe_o_bloqueio_cautelar_fora_do_med(self):
        """O texto diz 'Além do MED…': o bloqueio cautelar é medida à parte, não etapa da contestação."""
        body = self._body()
        m = re.search('<pre class="mermaid" data-title="Fluxo do MED 2.0[^"]*">(.*?)</pre>', body, re.S)
        self.assertIsNotNone(m, 'diagrama do MED ausente')
        codigo = m.group(1)
        sub = re.search('subgraph MED\\b[^\\n]*\\n(.*?)\\n\\s*end\\b', codigo, re.S)
        self.assertIsNotNone(sub, 'as etapas do MED ficam num subgraph MED')
        self.assertIn('Vítima contesta', sub.group(1))
        self.assertIn('Devolução', sub.group(1))
        self.assertNotIn('Bloqueio cautelar', sub.group(1), 'o bloqueio cautelar fica fora do MED')
        no = re.search('(\\w+)\\["Bloqueio cautelar[^\\]]*\\]', codigo)
        self.assertIsNotNone(no)
        self.assertRegex(no.group(0), 'à parte do MED')
        self.assertIn('sem prazo', no.group(0))
        bc = no.group(1)
        self.assertIsNone(re.search('\\b%s\\s*-->' % bc, codigo), 'o bloqueio cautelar não leva à análise do MED')
        self.assertIsNone(re.search('-->\\s*%s\\b' % bc, codigo), 'a contestação não leva ao bloqueio cautelar')

    def test_med_nao_cobre_pix_por_engano(self):
        body = self._body()
        self.assertIn('por engano', body)
        self.assertIn('falha operacional', body)

    def test_pontuacao_e_decisao(self):
        self.assertEqual([decidir(p, LIMIARES_PADRAO) for p in (0, 39, 40, 69, 70, 120)], ['aprovar', 'aprovar', 'segurar', 'segurar', 'bloquear', 'bloquear'])
        self.assertEqual(decidir(50, {'segurar': 60, 'bloquear': 50}), 'bloquear')
        self.assertEqual(decidir(55, {'segurar': 60, 'bloquear': 50}), 'bloquear')
        self.assertEqual(pontuar_risco({'sinais': ['dispositivo_novo', 'recebedor_recorrente']}, PESOS_PADRAO), 5)
        self.assertEqual(pontuar_risco({'sinais': []}, PESOS_PADRAO), 0)

    def test_diagrama_no_formato_do_guia(self):
        body = self._body()
        caixas = re.findall('<div class="diagram-box">\\s*<div class="diagram-header">\\s*<span class="diagram-title">([^<]+)</span>.*?<pre class="mermaid" data-title="([^"]+)">', body, re.S)
        self.assertGreaterEqual(len(caixas), 1, 'falta um .diagram-box com cabeçalho e Mermaid')
        for titulo, data_title in caixas:
            self.assertEqual(titulo.strip(), data_title.strip())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        termos = ['falsa central', 'falso parente', 'conta laranja', 'sequestro de conta', 'engenharia social', 'Mecanismo Especial de Devolução', 'MED 2.0', 'falso positivo', 'atrito', 'regras', 'pontuação', 'dispositivo', 'Ipê Pay', 'DICT', 'rastreio', 'saldo', 'Banco Central']
        for termo in termos:
            self.assertIn(termo, content, f'Termo obrigatório ausente: {termo}')

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn(f'{SLUG}/treinamento-fraude-em-pagamentos-e-pix.html', content)
        self.assertIn(f'data-slug="{SLUG}"', content)
        self.assertIn(f'/ {len(ESTUDOS_DADOS)}', content)
if __name__ == '__main__':
    unittest.main()
