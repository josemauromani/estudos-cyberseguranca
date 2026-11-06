"""
test_regulacao_setor_financeiro.py
Testes automatizados para o Estudo 54: Regulacao-Setor-Financeiro

O simulador Verificador de Aderência guarda num bloco JSON as entidades da
fase 1 (quem se sujeita à Res. CMN 4.893 e quem se sujeita à Res. BCB 85) e
os requisitos da fase 2, cada um com o trecho da política de segurança
cibernética ou do contrato de nuvem da Ipê Pay (instituição de pagamento
fictícia, parceira da Ipê Store), o gabarito (atendido, parcial ou ausente),
a criticidade e a ação corretiva. Este teste espelha em Python as regras do
motor JavaScript: conferência da sujeição, classificação de cada marcação do
aluno (certa, otimista, pessimista ou sem marcação), índice de aderência e
plano de ação priorizado a partir das marcações.
"""
import json
import re
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from index_dados import ESTUDOS_DADOS
SLUG = 'Regulacao-Setor-Financeiro'
STATUS = ('atendido', 'parcial', 'ausente')
NIVEL = {'atendido': 2, 'parcial': 1, 'ausente': 0}
FATOR = {'ausente': 2, 'parcial': 1}
TEMAS = ('politica', 'incidentes', 'nuvem', 'dez2025')
NORMAS = ('cmn4893', 'bcb85', 'nenhuma')
GABARITO = {'pol_aprovacao': ('politica', 'parcial', 2), 'pol_controles': ('politica', 'parcial', 2), 'pol_classificacao': ('politica', 'atendido', 1), 'pol_capacitacao': ('politica', 'atendido', 1), 'inc_plano': ('incidentes', 'ausente', 3), 'inc_diretor': ('incidentes', 'ausente', 2), 'inc_comunicacao': ('incidentes', 'ausente', 3), 'rel_anual': ('incidentes', 'parcial', 2), 'nuv_comunicacao': ('nuvem', 'ausente', 2), 'nuv_diligencia': ('nuvem', 'atendido', 2), 'nuv_localizacao': ('nuvem', 'ausente', 2), 'nuv_acesso_saida': ('nuvem', 'parcial', 2), 'nuv_responsabilidade': ('nuvem', 'ausente', 3), 'dez_controles': ('dez2025', 'parcial', 2), 'dez_pentest': ('dez2025', 'ausente', 3), 'dez_pix': ('dez2025', 'ausente', 3), 'dez_darkweb': ('dez2025', 'atendido', 1)}
SUJEICAO = {'banco_multiplo': 'cmn4893', 'cooperativa': 'cmn4893', 'financeira': 'cmn4893', 'ipe_pay': 'bcb85', 'corretora_cambio': 'bcb85', 'dtvm': 'bcb85', 'ipe_store': 'nenhuma'}
PLANO_GABARITO = [('inc_plano', 'P1'), ('inc_comunicacao', 'P1'), ('nuv_responsabilidade', 'P1'), ('dez_pentest', 'P1'), ('dez_pix', 'P1'), ('inc_diretor', 'P2'), ('nuv_comunicacao', 'P2'), ('nuv_localizacao', 'P2'), ('pol_aprovacao', 'P3'), ('pol_controles', 'P3'), ('rel_anual', 'P3'), ('nuv_acesso_saida', 'P3'), ('dez_controles', 'P3')]

def conferir_sujeicao(d, respostas):
    """Espelho de conferirSujeicao: compara a norma escolhida para cada entidade com o gabarito."""
    erros = [e['id'] for e in d['entidades'] if respostas.get(e['id']) != e['norma']]
    return {'acertos': len(d['entidades']) - len(erros), 'total': len(d['entidades']), 'erros': erros}

def avaliar_aderencia(d, marcacoes):
    """Espelho de avaliarAderencia: classifica cada marcação do aluno contra o gabarito."""
    itens, cont = ([], {'certo': 0, 'otimista': 0, 'pessimista': 0, 'sem_marcacao': 0})
    for r in d['requisitos']:
        m = marcacoes.get(r['id'])
        if m not in NIVEL:
            res = 'sem_marcacao'
        elif NIVEL[m] > NIVEL[r['gabarito']]:
            res = 'otimista'
        elif NIVEL[m] < NIVEL[r['gabarito']]:
            res = 'pessimista'
        else:
            res = 'certo'
        cont[res] += 1
        itens.append({'id': r['id'], 'marcado': m if m in NIVEL else None, 'gabarito': r['gabarito'], 'resultado': res})
    return {'itens': itens, **cont}

def indice_aderencia(d, marcacoes):
    """Espelho de indiceAderencia: atendido 2, parcial 1, ausente 0, sobre os requisitos marcados (inteiro)."""
    marcados = [marcacoes[r['id']] for r in d['requisitos'] if marcacoes.get(r['id']) in NIVEL]
    if not marcados:
        return None
    soma, den = (sum((NIVEL[m] for m in marcados)), len(marcados))
    return (100 * soma + den) // (2 * den)

def prioridade(pontos):
    return 'P1' if pontos >= 6 else 'P2' if pontos >= 3 else 'P3'

def plano_de_acao(d, marcacoes):
    """Espelho de planoDeAcao: lacunas marcadas pelo aluno, pontuadas por criticidade × fator do status."""
    plano = []
    for k, r in enumerate(d['requisitos']):
        m = marcacoes.get(r['id'])
        if m not in FATOR:
            continue
        pontos = r['criticidade'] * FATOR[m]
        plano.append({'id': r['id'], 'status': m, 'pontos': pontos, 'prioridade': prioridade(pontos), 'criticidade': r['criticidade'], 'ordem': k})
    plano.sort(key=lambda p: (-p['pontos'], -p['criticidade'], p['ordem']))
    return plano

class TestRegulacaoSetorFinanceiro(unittest.TestCase):
    """Estrutura, conteúdo, simulador e compilação do estudo 54."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / '_geradores' / 'regulacao_setor_financeiro_body.html'
        self.compiled_path = self.root / SLUG / 'treinamento-regulacao-setor-financeiro.html'
        self.portal_path = self.root / 'index.html'

    def _body(self):
        return self.body_path.read_text(encoding='utf-8')

    def _gabarito(self, d):
        return {r['id']: r['gabarito'] for r in d['requisitos']}

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_normas_citadas_com_os_numeros_conferidos(self):
        body = self._body()
        for termo in ('Res. CMN 4.893', 'Res. CMN 5.274', 'Res. BCB 85', 'Res. BCB 538', '18/12/2025', '01/03/2026', 'normativos.bcb.gov.br'):
            self.assertIn(termo, body, termo)
        self.assertNotIn('448', body, 'a BCB 448 foi descartada na conferência')
        self.assertNotIn('552', body, 'a alteração de 2026 não foi conferida: não citar')
        self.assertIsNone(re.search('\\b\\d+\\s+controles\\b', body), 'não citar número de controles mínimos')

    def test_aviso_da_redacao_de_2021(self):
        """Requisitos descritos no nível da redação original de 2021 da CMN 4.893 trazem o aviso de conferir a redação de dez/2025."""
        body = self._body()
        self.assertIn('redação original de 2021', body)
        self.assertIn('confira a redação vigente', body)

    def test_faixas_de_prioridade(self):
        self.assertEqual([prioridade(p) for p in (6, 4, 3, 2, 1)], ['P1', 'P2', 'P2', 'P3', 'P3'])

    def test_diagrama_no_formato_do_guia(self):
        body = self._body()
        caixas = re.findall('<div class="diagram-box">\\s*<div class="diagram-header">\\s*<span class="diagram-title">([^<]+)</span>.*?<pre class="mermaid" data-title="([^"]+)">', body, re.S)
        self.assertGreaterEqual(len(caixas), 1, 'falta um .diagram-box com cabeçalho e Mermaid')
        for titulo, data_title in caixas:
            self.assertEqual(titulo.strip(), data_title.strip())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        termos = ['política de segurança cibernética', 'plano de ação e de resposta a incidentes', 'relatório anual', '31 de dezembro', 'diretor', 'conselho de administração', 'incidentes relevantes', 'processamento, armazenamento de dados e computação em nuvem', 'países e regiões', 'não se transfere', 'teste de intrusão', 'controles mínimos', 'Pix', 'STR', 'RSFN', 'dark web', 'instituição de pagamento', 'instituições financeiras', 'Ipê Pay', 'Ipê Store', 'PCI DSS', 'ISO/IEC 27001', 'Banco Central']
        for termo in termos:
            self.assertIn(termo, content, f'Termo obrigatório ausente: {termo}')

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn(f'{SLUG}/treinamento-regulacao-setor-financeiro.html', content)
        self.assertIn(f'data-slug="{SLUG}"', content)
        self.assertIn(f'/ {len(ESTUDOS_DADOS)}', content)
if __name__ == '__main__':
    unittest.main()
