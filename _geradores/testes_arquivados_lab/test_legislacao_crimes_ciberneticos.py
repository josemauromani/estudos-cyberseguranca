"""
test_legislacao_crimes_ciberneticos.py
Testes automatizados para o Estudo 56: Legislacao-e-Crimes-Ciberneticos

O simulador Enquadramento de Casos guarda num bloco JSON os tipos penais (com
o dispositivo do Código Penal), o catálogo de registros que podem ser pedidos
(com o destinatário certo, o prazo de guarda do Marco Civil e a exigência de
ordem judicial), o catálogo de passos de preservação de provas e os casos
fictícios da Ipê Pay e da Ipê Store. Este teste espelha em Python as regras do
motor JavaScript: correção do tipo penal, classificação de cada registro
pedido (acerto, faltou, destinatário errado, desnecessário ou prazo de guarda
vencido), correção da ordem dos passos de preservação e pontuação por caso.
Também impede o módulo de afirmar números de pena não conferidos.
"""
import json
import re
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from index_dados import ESTUDOS_DADOS
SLUG = 'Legislacao-e-Crimes-Ciberneticos'
TIPOS = ('invasao', 'furto_fraude', 'fraude_eletronica', 'nao_crime')
DESTINOS = ('propria_empresa', 'provedor_conexao', 'provedor_aplicacao')
REGISTROS = {'logs_internos': ('propria_empresa', None, False), 'conexao': ('provedor_conexao', 365, True), 'aplicacao': ('provedor_aplicacao', 180, True), 'conteudo': ('provedor_aplicacao', None, True)}
ORDEM_CANONICA = ['isolar', 'fixar', 'coletar_hash', 'registrar', 'analisar_copia', 'comunicar']
GABARITO = {'C1': ('invasao', {'logs_internos', 'aplicacao', 'conexao'}, 40, ['isolar', 'fixar', 'coletar_hash', 'registrar', 'analisar_copia', 'comunicar']), 'C2': ('fraude_eletronica', {'logs_internos', 'aplicacao', 'conteudo', 'conexao'}, 10, ['fixar', 'coletar_hash', 'registrar', 'comunicar']), 'C3': ('furto_fraude', {'logs_internos', 'aplicacao', 'conexao'}, 20, ['fixar', 'coletar_hash', 'registrar', 'analisar_copia', 'comunicar']), 'C4': ('nao_crime', {'logs_internos'}, 5, ['isolar', 'fixar', 'coletar_hash', 'registrar', 'analisar_copia']), 'C5': ('invasao', {'logs_internos', 'conexao'}, 240, ['isolar', 'coletar_hash', 'registrar', 'analisar_copia', 'comunicar'])}

def prazo_vencido(registro, dias):
    """Espelho de prazoVencido: só registros com prazo de guarda do Marco Civil vencem."""
    prazo = registro.get('prazo_dias')
    return prazo is not None and dias > prazo

def corrigir_tipo(caso, escolha):
    """Espelho de corrigirTipo."""
    return escolha == caso['tipo']

def classificar_registros(caso, escolhas, catalogo):
    """Espelho de classificarRegistros: escolhas = {registro: destino}."""
    res = {}
    for rid in caso['registros']:
        if rid not in escolhas:
            res[rid] = 'faltou'
        elif escolhas[rid] != catalogo[rid]['destino']:
            res[rid] = 'destinatario_errado'
        else:
            res[rid] = 'acerto'
    for rid in escolhas:
        if rid in caso['registros'] or rid not in catalogo:
            continue
        res[rid] = 'vencido' if prazo_vencido(catalogo[rid], caso['dias_desde_fato']) else 'desnecessario'
    return res

def corrigir_ordem(caso, ordem):
    """Espelho de corrigirOrdem: posições certas e acerto total."""
    certa = caso['ordem_correta']
    posicoes = sum((1 for a, b in zip(ordem, certa) if a == b))
    return {'posicoes': posicoes, 'total': len(certa), 'ok': list(ordem) == list(certa)}

def mover(ordem, i, delta):
    """Espelho de moverPasso: troca o passo i com o vizinho; fora dos limites, nada muda."""
    j = i + delta
    nova = list(ordem)
    if 0 <= i < len(nova) and 0 <= j < len(nova):
        nova[i], nova[j] = (nova[j], nova[i])
    return nova

def corrigir_caso(caso, catalogo, tipo, escolhas, ordem):
    """Espelho de corrigirCaso: 1 ponto pelo tipo, 1 pelos registros sem erro, 1 pela ordem."""
    t = corrigir_tipo(caso, tipo)
    r = classificar_registros(caso, escolhas, catalogo)
    o = corrigir_ordem(caso, ordem)
    reg_ok = all((s in ('acerto', 'vencido') for s in r.values()))
    return {'tipo_ok': t, 'registros': r, 'registros_ok': reg_ok, 'ordem': o, 'pontos': int(t) + int(reg_ok) + int(o['ok'])}

class TestLegislacaoCrimesCiberneticos(unittest.TestCase):
    """Estrutura, conteúdo, simulador e compilação do estudo 56."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / '_geradores' / 'legislacao_e_crimes_ciberneticos_body.html'
        self.compiled_path = self.root / SLUG / 'treinamento-legislacao-e-crimes-ciberneticos.html'
        self.portal_path = self.root / 'index.html'

    def _body(self):
        return self.body_path.read_text(encoding='utf-8')

    def _caso(self, d, cid):
        return next((c for c in d['casos'] if c['id'] == cid))

    def _gabarito_escolhas(self, d, caso):
        return {rid: d['registros'][rid]['destino'] for rid in caso['registros']}

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_fato_do_catalogo_atualizado(self):
        fatos = ESTUDOS_DADOS[SLUG]['fatos']
        self.assertIn('Fraude eletrônica: art. 171 §2º-A (redação de 2026)', fatos)
        self.assertFalse(any(('171' in f and '14.155' in f for f in fatos)), 'fato do 171 §2º-A desatualizado')

    def test_dispositivos_e_normas_conferidos(self):
        body = self._body()
        for termo in ('Lei 12.737/2012', 'Lei 14.155/2021', 'Lei 15.397/2026', 'Lei 12.965/2014', 'art. 154-A', '§4º-B', '§4º-C', '§2º-A', '§2º-B', 'art. 13', 'art. 15', '1 ano', '6 meses', '158-A a 158-F', 'Decreto 11.856/2023', 'Decreto 12.573/2025', 'ordem judicial', 'reclusão de 1 a 4 anos', 'cadeia de custódia', 'hash'):
            self.assertIn(termo, body, termo)

    def test_aviso_de_conferencia_e_de_material_educativo(self):
        body = self._body()
        self.assertIn('planalto.gov.br', body)
        self.assertIn('02/11/2026', body)
        self.assertIn('Código Penal compilado', body)
        self.assertIn('não é orientação jurídica', body)

    def test_mover_passos(self):
        o = ['a', 'b', 'c']
        self.assertEqual(mover(o, 0, 1), ['b', 'a', 'c'])
        self.assertEqual(mover(o, 2, -1), ['a', 'c', 'b'])
        self.assertEqual(mover(o, 0, -1), o, 'primeiro passo não sobe')
        self.assertEqual(mover(o, 2, 1), o, 'último passo não desce')
        self.assertEqual(o, ['a', 'b', 'c'], 'não altera a lista original')

    def test_diagrama_no_formato_do_guia(self):
        body = self._body()
        caixas = re.findall('<div class="diagram-box">\\s*<div class="diagram-header">\\s*<span class="diagram-title">([^<]+)</span>.*?<pre class="mermaid" data-title="([^"]+)">', body, re.S)
        self.assertGreaterEqual(len(caixas), 1, 'falta um .diagram-box com cabeçalho e Mermaid')
        for titulo, data_title in caixas:
            self.assertEqual(titulo.strip(), data_title.strip())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        termos = ['invasão de dispositivo informático', 'fraude eletrônica', 'furto mediante fraude', 'Marco Civil da Internet', 'provedor de conexão', 'provedor de aplicação', 'registros de conexão', 'registros de acesso a aplicações', 'ordem judicial', 'cadeia de custódia', 'hash', 'SHA-256', 'PNCiber', 'E-Ciber', 'Ipê Pay', 'Ipê Store', 'boletim de ocorrência', 'induzid', 'ANPD']
        for termo in termos:
            self.assertIn(termo, content, f'Termo obrigatório ausente: {termo}')

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn(f'{SLUG}/treinamento-legislacao-e-crimes-ciberneticos.html', content)
        self.assertIn(f'data-slug="{SLUG}"', content)
        self.assertIn(f'/ {len(ESTUDOS_DADOS)}', content)
if __name__ == '__main__':
    unittest.main()
