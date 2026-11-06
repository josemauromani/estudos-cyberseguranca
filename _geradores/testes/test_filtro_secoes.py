"""Testes do filtro do portal aplicado às seções Necessidades, Rota da Vaga e Certificações."""
import re
import sys
import tempfile
import unittest
from pathlib import Path
GERADORES_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GERADORES_DIR))
from index_dados import CERTIFICACOES, NECESSIDADES, ROTA_VAGA
from build_index import gerar_index_html, render_certificacoes, render_chip_modulo, render_necessidades_grid, render_rota_vaga

def _status(disponiveis):
    return {s: {'disponivel': s in disponiveis, 'caminho_relativo': f'{s}/x.html'} for s in ['Segmentacao-e-Firewall', 'PCI-DSS']}

class TestMarcacaoDataSlug(unittest.TestCase):

    def test_chip_disponivel_e_pendente_tem_data_slug(self):
        st = _status({'Segmentacao-e-Firewall'})
        self.assertIn('data-slug="Segmentacao-e-Firewall"', render_chip_modulo('Segmentacao-e-Firewall', st))
        self.assertIn('data-slug="PCI-DSS"', render_chip_modulo('PCI-DSS', st))

    def test_cada_necessidade_tem_data_slug(self):
        html = render_necessidades_grid(NECESSIDADES)
        self.assertEqual(html.count('class="need-card"'), len(NECESSIDADES))
        for item in NECESSIDADES:
            self.assertIn(f'data-slug="{item['slug']}"', html)

    def test_chips_da_rota_tem_data_slug_e_legenda_nao(self):
        html = render_rota_vaga(ROTA_VAGA, {})
        total = sum((len(c['principais']) + len(c['apoio']) for c in ROTA_VAGA))
        self.assertEqual(html.count('data-slug='), total)
        legenda = html[html.index('class="vaga-legenda"'):html.index('</p>', html.index('class="vaga-legenda"'))]
        self.assertNotIn('data-slug', legenda)

    def test_chips_das_certificacoes_tem_data_slug(self):
        html = render_certificacoes(CERTIFICACOES, {})
        total = sum((len(c['modulos']) for c in CERTIFICACOES))
        self.assertEqual(html.count('data-slug='), total)

class TestJsFiltroSecoes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as tmp:
            saida = gerar_index_html(output_path=Path(tmp) / 'index.html')
            cls.html = saida.read_text(encoding='utf-8')

    def test_funcao_definida(self):
        self.assertIn('function filtrarSecoesRelacionadas(', self.html)

    def test_filtrar_cards_chama_filtro_das_secoes(self):
        ini = self.html.index('function filtrarCards(')
        fim = self.html.index('function clearSearch(')
        self.assertRegex(self.html[ini:fim], 'filtrarSecoesRelacionadas\\(')

    def test_secoes_alvo_tem_ids(self):
        for sid in ('secao-necessidades', 'secao-rota-vaga', 'secao-certificacoes'):
            self.assertIn(f'id="{sid}"', self.html)

    def test_filtro_usa_apenas_elementos_com_data_slug(self):
        ini = self.html.index('function filtrarSecoesRelacionadas(')
        corpo = self.html[ini:self.html.index('\n  }\n', ini)]
        self.assertTrue(re.search('\\[data-slug\\]', corpo), 'seletores devem exigir data-slug')
if __name__ == '__main__':
    unittest.main()
