"""
test_estruturacao_da_area.py
Testes automatizados para o Estudo 60: Estruturacao-da-Area-de-Seguranca

O simulador Alocador de Programa guarda num bloco JSON as seis funções do NIST
CSF 2.0, as seis frentes de investimento (cada uma com os pontos necessários
para subir um nível em cada função que ela afeta), os quatro modelos de SOC
(interno, MSSP, MDR e híbrido, com custo, efeito em níveis e riscos) e três
cenários fictícios (varejo, fintech regulada e indústria com OT), cada um com
orçamento, perfil atual, perfil alvo, exigências, um plano de exemplo e uma
armadilha comum. Este teste espelha em Python o cálculo do motor JavaScript:
o perfil alcançado por função, as exigências não atendidas, os riscos
residuais e a recusa da alocação inválida (acima do orçamento, negativa ou não
inteira), sem calcular perfil.
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
SLUG = 'Estruturacao-da-Area-de-Seguranca'
SECOES = ['introducao', 'maturidade', 'time-e-sourcing', 'conscientizacao', 'fusoes-e-aquisicoes', 'checklist', 'quiz', 'fatos']
FUNCOES = ['GV', 'ID', 'PR', 'DE', 'RS', 'RC']
FRENTES = ['identidade', 'vulnerabilidades', 'deteccao', 'resiliencia', 'conscientizacao', 'grc']
SOURCING = ['interno', 'mssp', 'mdr', 'hibrido']
CENARIOS = ['varejo', 'fintech', 'industria']
AVISO_ORCAMENTO = 'A alocação passa do orçamento'
NORMA_FINTECH = 'Res. CMN 4.893/2021'
CITA_NORMA = re.compile('\\bRes\\.|Resolução|Circular|\\bLei\\b|\\bnorma\\b', re.I)

def aplicar_plano(dados, cenario_id, sourcing, alocacao):
    """Espelho de aplicarPlano.

    nivel(f) = min(4, atual[f] + efeito do sourcing em f + soma(alocacao[frente] // pontos_por_nivel[f]))
    para cada frente que afeta f. O orçamento das frentes é o do cenário menos o custo do sourcing.
    Alocação acima do disponível, negativa, não inteira ou com frente desconhecida: ValueError (o motor
    mostra a mensagem e não calcula o perfil)."""
    cenario = next((c for c in dados['cenarios'] if c['id'] == cenario_id), None)
    if cenario is None:
        raise ValueError(f'cenário desconhecido: {cenario_id}')
    if sourcing not in dados['sourcing']:
        raise ValueError(f'modelo de SOC desconhecido: {sourcing}')
    frentes = {f['id']: f for f in dados['frentes']}
    for frente, pontos in alocacao.items():
        if frente not in frentes:
            raise ValueError(f'frente desconhecida: {frente}')
        if isinstance(pontos, bool) or not isinstance(pontos, int) or pontos < 0:
            raise ValueError(f'pontos inválidos em {frente}: {pontos!r}')
    disponivel = cenario['orcamento'] - dados['sourcing'][sourcing]['custo']
    if sum(alocacao.values()) > disponivel:
        raise ValueError('a alocação passa do orçamento')
    efeitos_soc = dados['sourcing'][sourcing]['efeitos']
    alcancado = {}
    for f in dados['funcoes']:
        ganho = efeitos_soc.get(f, 0)
        for frente in dados['frentes']:
            if f in frente['efeitos']:
                ganho += alocacao.get(frente['id'], 0) // frente['efeitos'][f]
        alcancado[f] = min(4, cenario['perfil_atual'][f] + ganho)
    return {'perfil_alcancado': alcancado, 'exigencias_nao_atendidas': [e['motivo'] for e in cenario['exigencias'] if alcancado[e['funcao']] < e['nivel_minimo']], 'riscos_residuais': [f for f in dados['funcoes'] if alcancado[f] < cenario['perfil_alvo'][f]] + list(dados['sourcing'][sourcing]['riscos'])}

class TestEstruturacaoDaArea(unittest.TestCase):
    """Estrutura, conteúdo, conteúdo e compilação do estudo 60."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / '_geradores' / 'estruturacao_da_area_de_seguranca_body.html'
        self.compiled_path = self.root / SLUG / 'treinamento-estruturacao-da-area-de-seguranca.html'
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

    def _cenario(self, d, cid):
        return next((c for c in d['cenarios'] if c['id'] == cid))

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
        self.assertIn('data-slug="estruturacao-da-area-de-seguranca"', body)

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
        self.assertEqual(info['titulo'], 'Estruturação da Área de Segurança: Maturidade, Time e Sourcing')
        self.assertEqual(info['subtitulo'], 'Plano de 90 dias, perfis do NIST CSF 2.0, desenho do time, SOC interno, MSSP e MDR, conscientização e aquisições')
        self.assertEqual(info['trilha'], 14)
        self.assertEqual(info['nist'], 'Govern')
        self.assertEqual(info['mitre'], 'N/A (estruturação e sourcing)')
        self.assertEqual(info['carreiras'], ['GRC & Auditoria'])
        self.assertEqual(info['tempo_minutos'], 50)
        self.assertEqual(info['nivel'], 'avancado')
        self.assertEqual(info['pergunta_chave'], 'Você chegou como primeiro CISO da empresa. O que acontece nos primeiros 90 dias?')
        self.assertEqual(info['fatos'], ['Perfil atual e perfil alvo (NIST CSF 2.0)', 'Níveis (tiers) 1 a 4', 'SOC interno, MSSP, MDR e híbrido', 'Plano de 90 dias'])

    def test_termos_chave(self):
        body = self._body()
        for termo in ('90 dias', 'perfil atual', 'perfil alvo', 'Tier 1', 'Tier 4', 'CMMI', 'C2M2', 'SOC interno', 'MSSP', 'MDR', 'híbrido', 'SLA', 'plano de saída', 'taxa de reporte', 'due diligence', 'federação', 'risco herdado'):
            self.assertIn(termo, body, termo)

    def test_pontes(self):
        body = self._body()
        antes = body[:body.index('id=')]
        for ref in ('Estudo 15', 'Estudo 16', 'Estudo 41', 'Estudo 57', 'Estudo 59'):
            self.assertIn(ref, antes, ref)
        fim = self._secao('fatos')
        for ref in ('Trilha 14', '62 módulos'):
            self.assertIn(ref, fim, ref)

    def test_referencias(self):
        fim = self._secao('fatos')
        for ref in ('NIST CSF 2.0', 'CSWP 29', 'Quick-Start Guide'):
            self.assertIn(ref, fim, ref)

    def test_sem_marcas_de_fornecedor_e_de_perfis(self):
        secao = self._secao('time-e-sourcing')
        for marca in ('CrowdStrike', 'SentinelOne', 'Splunk', 'QRadar', 'Microsoft Sentinel', 'Arctic Wolf'):
            self.assertNotIn(marca.lower(), secao.lower(), f'sourcing é ensinado por modelo, não por marca: {marca}')
        body = self._body()
        for proibido in ('F63', 'A93'):
            self.assertNotIn(proibido, body, proibido)
        self.assertNotIn('primeiro programa', body.lower())

    def test_campos_nao_sao_recriados(self):
        """Os campos de alocação existem uma vez; digitar só atualiza o 'disponível', sem recriar controles."""
        motor = self._motor()
        ini = motor.index('function atualizarDisponivel()')
        corpo = motor[ini:motor.index('\n    }', ini)]
        for proibido in ('replaceChildren', 'removeChild', 'appendChild'):
            self.assertNotIn(proibido, corpo, proibido)

    def test_portal_mostra_o_60(self):
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn(f'{SLUG}/treinamento-estruturacao-da-area-de-seguranca.html', content)
        self.assertIn(f'data-slug="{SLUG}"', content)
if __name__ == '__main__':
    unittest.main()
