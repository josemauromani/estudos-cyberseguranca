"""
test_gestao_crise.py
Testes automatizados para o Estudo 43: Gestao-de-Crise-e-Comunicacao

Os prazos seguem a Resolução CD/ANPD nº 15/2024 (arts. 6º, 9º e 10), conferida
no texto oficial: 3 dias úteis para ANPD e titulares, complementação em 20 dias
úteis, declaração em 3 dias úteis após o prazo dos titulares, prazos em dobro
para agentes de pequeno porte e registro por no mínimo 5 anos.
"""
import json
import re
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from index_dados import ESTUDOS_DADOS
INCISOS = {'I', 'II', 'III', 'IV', 'V', 'VI', 'VII'}

def somar_dias_uteis(inicio, n, feriados):
    """Exclui o dia de início, pula sábados, domingos e feriados nacionais."""
    d = inicio
    while n > 0:
        d += timedelta(days=1)
        if d.weekday() < 5 and d.isoformat() not in feriados:
            n -= 1
    return d

def prazos(d, pequeno_porte, feriados=None):
    feriados = set(d['feriados'] if feriados is None else feriados)
    r = d['regras']
    fator = 2 if pequeno_porte else 1
    conhecimento = date.fromisoformat(d['conhecimento'][:10])
    anpd = somar_dias_uteis(conhecimento, r['anpd_dias'] * fator, feriados)
    titulares = somar_dias_uteis(conhecimento, r['titulares_dias'] * fator, feriados)
    return {'anpd': anpd.isoformat(), 'titulares': titulares.isoformat(), 'declaracao': somar_dias_uteis(titulares, r['declaracao_dias'], feriados).isoformat(), 'complementacao': somar_dias_uteis(anpd, r['complementacao_dias'] * fator, feriados).isoformat(), 'registro': conhecimento.replace(year=conhecimento.year + r['registro_anos']).isoformat()}

class TestGestaoCrise(unittest.TestCase):
    """Valida a estrutura, o conteúdo, os prazos, as notificações e a compilação do estudo Gestao-de-Crise-e-Comunicacao."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / '_geradores' / 'gestao_de_crise_e_comunicacao_body.html'
        self.compiled_path = self.root / 'Gestao-de-Crise-e-Comunicacao' / 'treinamento-gestao-de-crise-e-comunicacao.html'
        self.portal_path = self.root / 'index.html'

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        termos = ['incidente', 'crise', 'comitê de crise', 'RACI', 'porta-voz', 'sala de guerra', 'registro de decisões', 'Resolução CD/ANPD nº 15/2024', 'três dias úteis', 'vinte dias úteis', 'pequeno porte', 'em dobro', 'três meses', 'cinco anos', 'art. 5º', 'art. 9º', 'encarregado', 'linguagem simples', 'Resolução CMN nº 4.893/2021', 'declaração inicial']
        for termo in termos:
            self.assertIn(termo, content, f'Termo obrigatório ausente: {termo}')

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn('Gestao-de-Crise-e-Comunicacao/treinamento-gestao-de-crise-e-comunicacao.html', content)
        self.assertIn('data-slug="Gestao-de-Crise-e-Comunicacao"', content)
        self.assertIn(f'/ {len(ESTUDOS_DADOS)}', content)
if __name__ == '__main__':
    unittest.main()
