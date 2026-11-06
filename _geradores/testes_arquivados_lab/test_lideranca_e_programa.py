"""
test_lideranca_e_programa.py
Testes automatizados para o Estudo 59: Lideranca-e-Programa-de-Seguranca

O simulador Do SIEM ao Conselho guarda num bloco JSON 12 indicadores fictícios
de uma empresa, cada um com o gabarito (KRI para o conselho, KPI operacional ou
métrica de vaidade), a marca de KRI essencial e a explicação. O aluno
classifica cada indicador, e o painel do conselho aceita no máximo
`limite_painel` KRIs. Este teste espelha em Python as regras do motor
JavaScript: a contagem de acertos, os KRIs que foram ao painel, os KRIs
essenciais ausentes, a métrica de vaidade marcada como KRI e a recusa do KRI
acima do limite (o motor recusa com aviso; não corta em silêncio).
"""
import json
import re
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from index_dados import ESTUDOS_DADOS
from navegador import CHROME, executar
SLUG = 'Lideranca-e-Programa-de-Seguranca'
SECOES = ['introducao', 'governanca', 'risco-de-negocio', 'metricas-conselho', 'orcamento', 'checklist', 'quiz', 'fatos']
CLASSES = ('kri', 'kpi', 'vaidade')
AVISO_LIMITE = 'O painel aceita no máximo 6 KRIs'

def avaliar_painel(dados, escolhas):
    """Espelho de avaliarPainel: escolhas é {id do indicador: classe}; indicador sem escolha conta como erro.

    O painel do conselho aceita no máximo limite_painel KRIs: acima disso o motor recusa (aqui, ValueError)."""
    for ind_id, classe in escolhas.items():
        if classe not in CLASSES:
            raise ValueError(f'classe inválida para {ind_id}: {classe}')
    indicadores = dados['indicadores']
    kri = [i['id'] for i in indicadores if escolhas.get(i['id']) == 'kri']
    if len(kri) > dados['limite_painel']:
        raise ValueError(f'o painel aceita no máximo {dados['limite_painel']} KRIs')
    return {'acertos': sum((1 for i in indicadores if escolhas.get(i['id']) == i['gabarito'])), 'kri_no_painel': kri, 'essenciais_ausentes': [i['id'] for i in indicadores if i['essencial'] and escolhas.get(i['id']) != 'kri'], 'vaidade_no_painel': [i['id'] for i in indicadores if i['gabarito'] == 'vaidade' and escolhas.get(i['id']) == 'kri']}

class TestLiderancaEPrograma(unittest.TestCase):
    """Estrutura, conteúdo, conteúdo e compilação do estudo 59."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / '_geradores' / 'lideranca_e_programa_de_seguranca_body.html'
        self.compiled_path = self.root / SLUG / 'treinamento-lideranca-e-programa-de-seguranca.html'
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

    def _gabarito(self, d):
        return {i['id']: i['gabarito'] for i in d['indicadores']}

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
        self.assertIn('data-slug="lideranca-e-programa-de-seguranca"', body)

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
        self.assertEqual(info['titulo'], 'Liderança e Programa de Segurança: o Papel do CISO')
        self.assertEqual(info['subtitulo'], 'Linha de reporte, governança, KPI e KRI, relato ao conselho e orçamento de segurança')
        self.assertEqual(info['trilha'], 14)
        self.assertEqual(info['nist'], 'Govern')
        self.assertEqual(info['mitre'], 'N/A (liderança e governança)')
        self.assertEqual(info['carreiras'], ['GRC & Auditoria', 'Analista de Segurança da Informação'])
        self.assertEqual(info['tempo_minutos'], 45)
        self.assertEqual(info['nivel'], 'intermediario')
        self.assertEqual(info['pergunta_chave'], 'O SIEM gerou 40 mil alertas no trimestre. O que disso o conselho precisa saber?')
        self.assertEqual(info['fatos'], ['Modelo das três linhas (IIA, 2020)', 'Função Govern do NIST CSF 2.0', 'KPI, KRI e métrica de vaidade', 'Business case e limites do ROSI'])

    def test_termos_chave(self):
        body = self._body()
        for termo in ('três linhas', 'IIA', 'independência', 'CISO', 'CTO', 'DPO', 'encarregado', 'NIST CSF 2.0', 'GV.OC', 'GV.RM', 'GV.RR', 'GV.PO', 'GV.OV', 'GV.SC', 'RACI', 'apetite', 'tolerância', 'KPI', 'KRI', 'métrica de vaidade', 'Capex', 'Opex', 'business case', 'ROSI', 'Res. CMN 4.893/2021'):
            self.assertIn(termo, body, termo)

    def test_pontes(self):
        body = self._body()
        antes = body[:body.index('id=')]
        for ref in ('Estudo 25', 'Estudo 26', 'Estudo 54', 'Estudo 58'):
            self.assertIn(ref, antes, ref)
        fim = self._secao('fatos')
        for ref in ('Trilha 14', 'Estudo 60', 'Estudo 33'):
            self.assertIn(ref, fim, ref)

    def test_nao_repete_calculo_de_risco(self):
        body = self._body()
        for proibido in ('ALE =', 'SLE ='):
            self.assertNotIn(proibido, body, 'o cálculo de ALE e SLE é ensinado no Estudo 25')
        self.assertIn('Estudo 25', self._secao('risco-de-negocio'))

    def test_referencias(self):
        fim = self._secao('fatos')
        for ref in ('Three Lines Model', 'NIST CSF 2.0', 'CSWP 29', 'Res. CMN 4.893/2021'):
            self.assertIn(ref, fim, ref)

    def test_sem_marcas_de_perfis(self):
        body = self._body()
        for proibido in ('F63', 'A93'):
            self.assertNotIn(proibido, body, proibido)
        self.assertNotIn('primeiro programa', body.lower())

    def test_foco_restaurado_no_codigo(self):
        """Cada clique recria os cartões e o painel: o motor guarda a chave do botão e devolve o foco a ele."""
        motor = self._motor()
        self.assertIn('estado.foco = i.id + ":" + c', motor)
        self.assertIn('registrarAlvo(i.id + ":" + c, b)', motor)
        ini = motor.index('function renderTudo()')
        render = motor[ini:motor.index('\n    }', ini)]
        self.assertLess(render.index('renderIndicadores()'), render.index('restaurarFoco()'))
        self.assertLess(render.index('renderPainel()'), render.index('restaurarFoco()'))
        ini = motor.index('function restaurarFoco()')
        self.assertIn('.focus()', motor[ini:motor.index('\n    }', ini)])

    @unittest.skipUnless(CHROME, 'Chrome ausente')
    def test_foco_do_teclado_sobrevive_a_classificacao(self):
        """No navegador: classificar e tirar do painel não jogam o foco para o <body>."""
        r = executar(self._compilado(), "\n          const card = (n) => document.querySelectorAll('#lid-indicadores [role=group]')[n];\n          const ativo = () => document.activeElement;\n          const out = {};\n          let b = card(2).querySelectorAll('button')[0];        // I03 como KRI\n          const rotulo = b.getAttribute('aria-label');\n          b.focus(); b.click();\n          out.kri = {label: ativo().getAttribute('aria-label'), novo: ativo() !== b,\n                     pressed: ativo().getAttribute('aria-pressed')};\n          b = card(4).querySelectorAll('button')[0]; b.focus(); b.click();   // I05 como KRI\n          b = card(4).querySelectorAll('button')[1]; b.focus(); b.click();   // I05 vira KPI\n          out.kpi = ativo().getAttribute('aria-label');\n          b = card(4).querySelectorAll('button')[0]; b.focus(); b.click();   // I05 volta a KRI\n          let tirar = document.querySelectorAll('#lid-painel button');\n          tirar[0].focus(); tirar[0].click();\n          out.tirar1 = {noPainel: document.getElementById('lid-painel').contains(ativo()),\n                        tag: ativo().tagName, restantes: document.querySelectorAll('#lid-painel button').length};\n          tirar = document.querySelectorAll('#lid-painel button');\n          tirar[0].focus(); tirar[0].click();\n          out.tirar2 = {noPainel: document.getElementById('lid-painel').contains(ativo()), tag: ativo().tagName};\n          out.rotulo = rotulo;\n          __fim(out);\n        ")
        self.assertEqual(r['erros'], [])
        s = r['saida']
        self.assertEqual(s['kri']['label'], s['rotulo'], 'o foco volta ao botão clicado, recriado')
        self.assertTrue(s['kri']['novo'])
        self.assertEqual(s['kri']['pressed'], 'true')
        self.assertIn('como KPI operacional', s['kpi'])
        self.assertEqual(s['tirar1'], {'noPainel': True, 'tag': 'BUTTON', 'restantes': 1})
        self.assertTrue(s['tirar2']['noPainel'], 'painel vazio: o foco fica no título do painel')
        self.assertEqual(s['tirar2']['tag'], 'H4')

    def test_portal_mostra_o_59(self):
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn(f'{SLUG}/treinamento-lideranca-e-programa-de-seguranca.html', content)
        self.assertIn(f'data-slug="{SLUG}"', content)
if __name__ == '__main__':
    unittest.main()
