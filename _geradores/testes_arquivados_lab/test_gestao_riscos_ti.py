"""
test_gestao_riscos_ti.py
Testes automatizados para o Estudo 25: Gestao-de-Riscos-TI
"""
import json
import re
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from index_dados import ESTUDOS_DADOS
TRATAMENTOS_CONTROLE = {'mitigar', 'transferir', 'evitar'}

def nivel(escala, valor):
    """Nível (1 a 5) cujo limite inferior é o maior que não passa de `valor`."""
    n = 0
    for item in escala:
        if valor >= item['min']:
            n = item['nivel']
    return n

def faixa(faixas, pontuacao):
    for f in faixas:
        if f['min'] <= pontuacao <= f['max']:
            return f['nome']
    return None

class TestGestaoRiscosTI(unittest.TestCase):
    """Valida a estrutura, o conteúdo, os cálculos e a compilação do estudo Gestao-de-Riscos-TI."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / '_geradores' / 'gestao_de_riscos_ti_body.html'
        self.compiled_path = self.root / 'Gestao-de-Riscos-TI' / 'treinamento-gestao-de-riscos-ti.html'
        self.portal_path = self.root / 'index.html'

    def _pontuacao(self, d, sle, aro):
        return nivel(d['escala_probabilidade'], aro) * nivel(d['escala_impacto'], sle)

    @staticmethod
    def _ale(av, ef, aro):
        return av * ef * aro

    def _avaliar_controles(self, d, c):
        """Para cada controle: ALE residual, benefício líquido anual e ROSI."""
        ale_antes = self._ale(c['av'], c['ef'], c['aro'])
        saida = []
        for ctl in c['controles']:
            ale_depois = self._ale(c['av'], ctl['ef'], ctl['aro'])
            beneficio = ale_antes - ale_depois - ctl['custo_anual']
            saida.append({'id': ctl['id'], 'tratamento': ctl['tratamento'], 'custo': ctl['custo_anual'], 'ale_depois': ale_depois, 'beneficio': beneficio, 'rosi': beneficio / ctl['custo_anual'], 'pontuacao': self._pontuacao(d, c['av'] * ctl['ef'], ctl['aro'])})
        return (ale_antes, saida)

    def _recomendado(self, d, c):
        _, avaliados = self._avaliar_controles(d, c)
        melhor = max(avaliados, key=lambda a: a['beneficio'])
        return melhor if melhor['beneficio'] > 0 else None

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        termos = ['ISO 31000:2018', 'ISO/IEC 27005:2022', 'NIST SP 800-30', 'NIST IR 8286', 'GV.RM', 'Valor do Ativo', 'Fator de Exposição', 'SLE', 'ARO', 'ALE', 'ROSI', 'risco inerente', 'risco residual', 'apetite', 'tolerância', 'registro de riscos', 'Mitigar', 'Aceitar', 'Transferir', 'Evitar', 'FAIR', '6.1.3']
        for termo in termos:
            self.assertIn(termo, content, f'Termo obrigatório ausente: {termo}')

    def _secao(self, content, sid):
        m = re.search('<section class="study-section" id="%s" data-tipo="[a-z]+">(.*?)</section>' % sid, content, re.S)
        self.assertIsNotNone(m, f'Seção {sid} ausente')
        return m.group(1)

    def test_secao_excecoes_conteudo(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        sec = self._secao(content, 'excecoes')
        for termo in ('exceção', 'aceitação', 'alçada', 'controle compensatório', 'prazo', 'reavaliação', 'vencida', 'sistêmico', 'Estudo 58', 'Estudo 26'):
            self.assertIn(termo, sec, f'Termo ausente na seção: {termo}')
        self.assertIn('class="callout warning"', sec)
        self.assertIn('class="data-table"', sec)

    def test_secao_iso_27005_conteudo(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        sec = self._secao(content, 'iso-27005')
        for termo in ('ISO/IEC 27005:2022', 'ISO 31000', '6.1.2', 'baseada em eventos', 'baseada em ativos', 'critérios de aceitação', 'matriz 5×5'):
            self.assertIn(termo, sec, f'Termo ausente na seção: {termo}')

    def test_secao_iso_27005_referencia(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        self.assertIn('ISO/IEC 27005:2022', self._secao(content, 'fatos'))

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn('Gestao-de-Riscos-TI/treinamento-gestao-de-riscos-ti.html', content)
        self.assertIn('data-slug="Gestao-de-Riscos-TI"', content)
        self.assertIn(f'/ {len(ESTUDOS_DADOS)}', content)
if __name__ == '__main__':
    unittest.main()
