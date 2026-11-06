"""
test_lgpd.py
Testes automatizados para o Estudo 27: LGPD-e-Privacidade
"""
import json
import re
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from index_dados import ESTUDOS_DADOS
SALV_ALTO_RISCO = ['criptografia', 'controle_acesso', 'registro_acesso', 'minimizacao']

def sensivel(f):
    return any((c.startswith('sensivel_') for c in f['categorias']))

def vulneravel(f):
    return any((c in ('crianca_adolescente', 'idoso') for c in f['categorias']))

def avaliar(d, f):
    """Espelho do avaliador em JavaScript."""
    base, sens = (f['base'], sensivel(f))
    if base == 'politicas_publicas':
        st, mot = ('invalida', 'politicas')
    elif sens and base in ('legitimo_interesse', 'protecao_credito', 'execucao_contrato'):
        st, mot = ('invalida', 'art11_sem_base')
    elif not sens and base == 'prevencao_fraude':
        st, mot = ('invalida', 'so_sensiveis')
    elif sens and base == 'consentimento':
        st, mot = ('alerta', 'consentimento_destacado')
    elif base == 'tutela_saude':
        st, mot = ('alerta', 'saude_restrita')
    elif base == 'pesquisa':
        st, mot = ('alerta', 'orgao_pesquisa')
    elif base == 'legitimo_interesse' and (not f['lia']):
        st, mot = ('alerta', 'lia')
    elif base in ('consentimento', 'consentimento_especifico') and 'funcionarios' in f['titulares']:
        st, mot = ('alerta', 'consentimento_emprego')
    else:
        st, mot = ('ok', 'ok')
    gerais = [c for c in ('larga_escala', 'afeta_direitos') if f[c]]
    especificos = [c for c in ('tecnologia_emergente', 'vigilancia_publica', 'decisao_automatizada') if f[c]]
    if sens or vulneravel(f):
        especificos.append('sensiveis_ou_vulneraveis')
    alto = bool(gerais and especificos)
    exigidas = (list(SALV_ALTO_RISCO) if alto else []) + (['contrato_operador'] if f['operador'] else []) + (['clausulas_padrao'] if f['transferencia'] else []) + ['retencao_definida']
    faltam = [s for s in exigidas if s not in f['salvaguardas']]
    impacto = 3 if sens or vulneravel(f) else 2 if any((c in ('identificacao', 'financeiro', 'localizacao') for c in f['categorias'])) else 1
    prob = min(3, 1 + (1 if f['operador'] or f['terceiros'] or f['transferencia'] else 0) + (1 if faltam else 0))
    nivel = 'alto' if impacto * prob >= 6 else 'medio' if impacto * prob >= 3 else 'baixo'
    direitos = []
    if base in ('consentimento', 'consentimento_especifico'):
        direitos += ['art18_vi', 'art18_ix']
    if f['operador'] or f['terceiros']:
        direitos.append('art18_vii')
    if f['decisao_automatizada']:
        direitos.append('art20')
    return {'base': st, 'motivo': mot, 'alto_risco': alto, 'criterios': gerais + especificos, 'faltam': faltam, 'impacto': impacto, 'probabilidade': prob, 'nivel': nivel, 'ripd': alto or nivel == 'alto', 'direitos': direitos}

class TestLgpd(unittest.TestCase):
    """Valida a estrutura, o conteúdo jurídico, o avaliador de fluxos e a compilação do estudo 27."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / '_geradores' / 'lgpd_e_privacidade_body.html'
        self.compiled_path = self.root / 'LGPD-e-Privacidade' / 'treinamento-lgpd-e-privacidade.html'
        self.portal_path = self.root / 'index.html'

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        termos = ['Lei nº 13.709/2018', 'dado pessoal', 'dado pessoal sensível', 'anonimizado', 'controlador', 'operador', 'encarregado', 'finalidade', 'adequação', 'necessidade', 'art. 7º', 'art. 11', 'legítimo interesse', 'teste de balanceamento', 'art. 18', 'art. 20', 'art. 37', 'art. 38', 'RIPD', 'art. 48', 'art. 52', 'Resolução CD/ANPD nº 2/2022', 'Resolução CD/ANPD nº 15/2024', '3 dias úteis', 'Resolução CD/ANPD nº 19/2024', 'cláusulas-padrão contratuais', '2% do faturamento', 'R$ 50 milhões', 'Estudo 43', 'Estudo 29']
        for termo in termos:
            self.assertIn(termo, content, f'Termo obrigatório ausente: {termo}')

    def _secao_27701(self, texto):
        ini = texto.index('<section class="study-section" id="iso-27701" data-tipo="teoria">')
        return texto[ini:texto.index('</section>', ini)]

    def test_secao_iso_27701_conteudo(self):
        for texto in (self.body_path.read_text(encoding='utf-8'), self.compiled_path.read_text(encoding='utf-8')):
            sec = self._secao_27701(texto)
            for termo in ('ISO/IEC 27701', 'controlador', 'operador', 'art. 46', 'GDPR', 'art. 25', 'Privacy by Design', 'by Default', 'SGPI', '2025', '2019'):
                self.assertIn(termo, sec, termo)

    def test_secao_iso_27701_referencia(self):
        for texto in (self.body_path.read_text(encoding='utf-8'), self.compiled_path.read_text(encoding='utf-8')):
            ini = texto.index('id="fatos"')
            self.assertIn('ISO/IEC 27701', texto[ini:texto.index('</section>', ini)])

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn('LGPD-e-Privacidade/treinamento-lgpd-e-privacidade.html', content)
        self.assertIn('data-slug="LGPD-e-Privacidade"', content)
        self.assertIn(f'/ {len(ESTUDOS_DADOS)}', content)
if __name__ == '__main__':
    unittest.main()
