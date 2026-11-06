"""
test_auditoria_de_ti.py
Testes automatizados para o Estudo 58: Auditoria-de-TI

O simulador Testador de ITGC guarda num bloco JSON a tabela de amostragem por
frequência do controle (prática de mercado, com a fonte citada) e os controles
gerais de TI de uma empresa fictícia, cada um com domínio, frequência,
população, a amostra sorteada (itens com evidência e exceção), o risco do que
pode dar errado, o controle compensatório (quando existe) e a classificação
esperada. Este teste espelha em Python as regras do motor JavaScript: a
amostra mínima por frequência, limitada à população, e a classificação da
deficiência (efetivo, deficiência, deficiência significativa, fraqueza
material), inclusive o efeito do controle compensatório e as armadilhas
didáticas.
"""
import json
import re
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from index_dados import ESTUDOS_DADOS
SLUG = 'Auditoria-de-TI'
SECOES = ['introducao', 'sox-404', 'itgc', 'cobit', 'ciclo-do-teste', 'assurance', 'correlacao-grc', 'checklist', 'quiz', 'fatos']
DOMINIOS = ('acesso', 'mudanca', 'desenvolvimento', 'operacoes')
FREQUENCIAS = ('anual', 'trimestral', 'mensal', 'semanal', 'diaria', 'multipla')
CLASSES = ('efetivo', 'deficiencia', 'significativa', 'material')
RISCOS = ('baixo', 'moderado', 'alto')
BASE_POR_RISCO = {'baixo': 'deficiencia', 'moderado': 'significativa', 'alto': 'material'}
GABARITO = {'C1': {'amostra': 2, 'excecoes': 1, 'classe': 'significativa'}, 'C2': {'amostra': 20, 'excecoes': 2, 'classe': 'deficiencia'}, 'C3': {'amostra': 5, 'excecoes': 2, 'classe': 'material'}, 'C4': {'amostra': 1, 'excecoes': 0, 'classe': 'efetivo'}, 'C5': {'amostra': 2, 'excecoes': 0, 'classe': 'efetivo'}}

def amostra_minima(tabela, frequencia, populacao):
    """Espelho de amostraMinima: mínimo da tabela para a frequência, nunca acima da população."""
    return min(tabela[frequencia]['min'], populacao)

def classificar_por(risco, excecoes, compensatorio):
    """Espelho de classificarControle: sem exceção, efetivo; com exceção, a base vem do risco;
    o controle compensatório rebaixa um nível, mas a deficiência continua existindo."""
    if excecoes == 0:
        return 'efetivo'
    nivel = CLASSES.index(BASE_POR_RISCO[risco])
    if compensatorio:
        nivel = max(1, nivel - 1)
    return CLASSES[nivel]

def classificar(controle):
    excecoes = sum((1 for i in controle['itens'] if i['excecao']))
    return classificar_por(controle['risco'], excecoes, controle['compensatorio'])

def corrigir(d, c, resp):
    """Espelho de corrigirControle: 3 pontos (amostra, exceções, classificação)."""
    minimo = amostra_minima(d['tabela_amostragem'], c['frequencia'], c['populacao'])
    marcadas = set(resp['marcadas'])
    itens = {}
    for i in c['itens']:
        m = i['id'] in marcadas
        itens[i['id']] = 'acerto' if m == i['excecao'] else 'falso_positivo' if m else 'omitiu'
    out = {'amostra_ok': minimo <= resp['amostra'] <= c['populacao'], 'excecoes_ok': all((s == 'acerto' for s in itens.values())), 'itens': itens, 'classe_ok': resp['classe'] == classificar(c), 'classe_com_marcas': classificar_por(c['risco'], len(marcadas & {i['id'] for i in c['itens']}), c['compensatorio'])}
    out['pontos'] = int(out['amostra_ok']) + int(out['excecoes_ok']) + int(out['classe_ok'])
    return out

class TestAuditoriaDeTI(unittest.TestCase):
    """Estrutura, conteúdo, conteúdo e compilação do estudo 58."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / '_geradores' / 'auditoria_de_ti_body.html'
        self.compiled_path = self.root / SLUG / 'treinamento-auditoria-de-ti.html'
        self.portal_path = self.root / 'index.html'

    def _body(self):
        return self.body_path.read_text(encoding='utf-8')

    def _compilado(self):
        return self.compiled_path.read_text(encoding='utf-8')

    def _secao(self, sid):
        body = self._body()
        ini = body.index(f'id="{sid}"')
        fim = body.find('<section class="study-section"', ini)
        return body[ini:fim if fim >= 0 else body.index('</article>')]

    def _controle(self, d, cid):
        return next((c for c in d['controles'] if c['id'] == cid))

    def _resp_gabarito(self, c):
        return {'amostra': GABARITO[c['id']]['amostra'], 'classe': GABARITO[c['id']]['classe'], 'marcadas': [i['id'] for i in c['itens'] if i['excecao']]}

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_secoes(self):
        body = self._body()
        ids = re.findall('<section class="study-section" id="([\\w-]+)"', body)
        self.assertEqual(ids, SECOES)
        compilado = self._compilado()
        for n in range(1, len(SECOES) + 1):
            self.assertIn(f'Seção {n} de {len(SECOES)}', compilado)
        self.assertIn('data-slug="auditoria-de-ti"', body)

    def test_secoes_assurance_e_correlacao(self):
        a = self._secao('assurance')
        for t in ('desenho', 'efetividade operacional', 'reexecução', 'indagação', 'racionalização', 'modelo de assurance', 'Três Linhas', 'Estudo 59'):
            self.assertIn(t, a, t)
        self.assertEqual(a.count('class="data-table"'), 2)
        c = self._secao('correlacao-grc')
        for t in ('causa sistêmica', 'sistêmic', 'plataforma de GRC', 'Estudo 25', 'Estudo 09', 'Estudo 18', 'Estudos 46', 'ServiceNow', 'Archer', 'MetricStream', 'callout tip'):
            self.assertIn(t, c, t)
        self.assertNotIn('recomendamos', c)

    def test_coerencia_com_o_catalogo(self):
        content = self._compilado()
        info = ESTUDOS_DADOS[SLUG]
        self.assertIn(info['pergunta_chave'], content)
        self.assertIn(info['subtitulo'], self.portal_path.read_text(encoding='utf-8'))
        self.assertEqual(len(info['fatos']), 4)
        for fato in info['fatos']:
            self.assertIn(fato, content, fato)

    def test_metadados(self):
        info = ESTUDOS_DADOS[SLUG]
        self.assertEqual(info['titulo'], 'Auditoria de TI: SOX, ITGC e COBIT')
        self.assertEqual(info['subtitulo'], 'Controles gerais de TI, teste de desenho e de efetividade, amostragem e deficiências')
        self.assertEqual(info['trilha'], 6)
        self.assertEqual(info['nist'], 'Govern')
        self.assertEqual(info['mitre'], 'T1078 Valid Accounts / T1098 Account Manipulation')
        self.assertEqual(info['carreiras'][0], 'GRC & Auditoria')
        self.assertEqual(len(info['carreiras']), 2)
        self.assertEqual(info['tempo_minutos'], 45)
        self.assertEqual(info['nivel'], 'intermediario')
        self.assertEqual(info['pergunta_chave'], 'O controle está no papel. Como você prova que ele funcionou o ano inteiro?')

    def test_termos_chave(self):
        body = self._body()
        for termo in ('SOX', '404', 'ICFR', 'COSO', 'PCAOB AS 2201', 'ITGC', 'ITAC', 'IPE', 'SOC 1', 'SOC 2', 'COBIT 2019', 'EDM', 'APO', 'BAI', 'DSS', 'MEA', 'TOD', 'TOE', 'walkthrough', 'fraqueza material', 'deficiência significativa', 'controle compensatório'):
            self.assertIn(termo, body, termo)

    def test_pontes(self):
        body = self._body()
        antes = body[:body.index('id=')]
        for ref in ('Estudo 26', 'Estudo 04', 'Estudo 40', 'Estudo 22', 'Estudo 52', 'Estudo 30', 'Estudo 57'):
            self.assertIn(ref, antes, ref)
        fim = self._secao('fatos')
        for ref in ('Estudo 25', 'Estudo 26', 'Estudo 57', '62 módulos'):
            self.assertIn(ref, fim, ref)

    def test_nao_repete_auditoria_do_sgsi(self):
        body = self._body()
        for proibido in ('fase 2', 'etapa 2', 'estágio 2', 'stage 2'):
            self.assertNotIn(proibido, body.lower(), 'as fases da certificação ISO são ensinadas no Estudo 26')
        paragrafos = re.findall('<p>(.*?)</p>', body, re.S)
        self.assertTrue(any(('auditoria do SGSI' in p and 'Estudo 26' in p for p in paragrafos)), 'ao falar da auditoria do SGSI, remeter ao Estudo 26')

    def test_referencias(self):
        fim = self._secao('fatos')
        for ref in ('Sarbanes-Oxley', 'AS 2201', 'COSO', 'COBIT 2019', 'ITAF', 'Global Internal Audit Standards', 'SOC 1'):
            self.assertIn(ref, fim, ref)

    def test_classificacao(self):
        self.assertEqual(classificar_por('alto', 0, 'x'), 'efetivo')
        self.assertEqual(classificar_por('baixo', 1, None), 'deficiencia')
        self.assertEqual(classificar_por('baixo', 3, 'x'), 'deficiencia', 'compensatório não apaga a deficiência')
        self.assertEqual(classificar_por('moderado', 1, None), 'significativa')
        self.assertEqual(classificar_por('moderado', 1, 'x'), 'deficiencia')
        self.assertEqual(classificar_por('alto', 2, None), 'material')
        self.assertEqual(classificar_por('alto', 2, 'x'), 'significativa')

    def test_portal_mostra_58_compilados(self):
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn(f'{SLUG}/treinamento-auditoria-de-ti.html', content)
        self.assertIn(f'data-slug="{SLUG}"', content)
        import montar
        n = len(montar.carregar_catalogo_estudos())
        self.assertIn(f'{n} / {n}', content)

    def test_pontes_para_o_58(self):
        for corpo in ('gestao_de_riscos_ti', 'iso_27001_e_27002', 'gestao_de_riscos_de_terceiros'):
            txt = (self.root / '_geradores' / f'{corpo}_body.html').read_text(encoding='utf-8')
            fatos = txt[txt.index('id="fatos"'):]
            self.assertIn('Estudo 58', fatos, corpo)
        import index_dados
        for sigla in ('CISM', 'CISSP'):
            cert = next((c for c in index_dados.CERTIFICACOES if c['sigla'] == sigla))
            self.assertIn(SLUG, cert['modulos'], sigla)
        readme = (self.root / 'README.md').read_text(encoding='utf-8')
        self.assertIn('62 módulos', readme)
        self.assertNotIn('57 módulos', readme)
        curriculo = (self.root / '_geradores' / 'CURRICULO.md').read_text(encoding='utf-8')
        self.assertIn('#### 58. Auditoria-de-TI', curriculo)
        self.assertIn('25 ao 28, 31, 58', curriculo)
if __name__ == '__main__':
    unittest.main()
