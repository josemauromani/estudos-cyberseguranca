"""
test_operacoes_soc_siem.py
Testes automatizados para o Estudo 16: Operacoes-SOC-e-SIEM

As regras Sigma ficam no JSON do módulo como objetos (o simulador gera o YAML
para edição). Este teste avalia essas regras em Python, com o mesmo subconjunto
do JavaScript, para validar os eventos, os alertas esperados e as missões.
"""
import copy
import fnmatch
import ipaddress
import json
import re
import sys
import unittest
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from index_dados import ESTUDOS_DADOS
MODIFICADORES = {'contains', 'startswith', 'endswith', 'all'}

def campo(evento, nome):
    for k, v in evento['campos'].items():
        if k.lower() == nome.lower():
            return v
    return None

def casa_valor(valor_evento, esperado, mods):
    if valor_evento is None:
        return False
    a = str(valor_evento).lower()
    b = str(esperado).lower()
    if 'contains' in mods:
        return b in a
    if 'startswith' in mods:
        return a.startswith(b)
    if 'endswith' in mods:
        return a.endswith(b)
    return fnmatch.fnmatchcase(a, b) if '*' in b or '?' in b else a == b

def casa_selecao(evento, selecao):
    for chave, esperado in selecao.items():
        nome, *mods = chave.split('|')
        assert set(mods) <= MODIFICADORES, mods
        valores = esperado if isinstance(esperado, list) else [esperado]
        testes = [casa_valor(campo(evento, nome), v, mods) for v in valores]
        if not (all(testes) if 'all' in mods else any(testes)):
            return False
    return True

def avaliar_condicao(cond, resultados):
    tokens = re.findall('\\(|\\)|[^\\s()]+', cond)
    pos = [0]

    def ver():
        return tokens[pos[0]].lower() if pos[0] < len(tokens) else None

    def pegar():
        t = tokens[pos[0]]
        pos[0] += 1
        return t

    def expr_or():
        v = expr_and()
        while ver() == 'or':
            pegar()
            v = expr_and() or v
        return v

    def expr_and():
        v = expr_not()
        while ver() == 'and':
            pegar()
            v = expr_not() and v
        return v

    def expr_not():
        if ver() == 'not':
            pegar()
            return not expr_not()
        return primario()

    def primario():
        t = pegar()
        if t == '(':
            v = expr_or()
            assert pegar() == ')'
            return v
        if t.lower() in ('1', 'all') and ver() == 'of':
            pegar()
            alvo = pegar()
            nomes = list(resultados) if alvo == 'them' else [n for n in resultados if fnmatch.fnmatchcase(n, alvo)]
            assert nomes, alvo
            vals = [resultados[n] for n in nomes]
            return any(vals) if t == '1' else all(vals)
        return resultados[t]
    v = expr_or()
    assert pos[0] == len(tokens), cond
    return v

def regra_casa(regra, evento):
    for k, v in regra['logsource'].items():
        if evento['logsource'].get(k) != v:
            return False
    det = regra['deteccao']
    resultados = {nome: casa_selecao(evento, sel) for nome, sel in det.items() if nome != 'condition'}
    return avaliar_condicao(det['condition'], resultados)

def disparos(d, regra):
    return [e['id'] for e in d['eventos'] if regra_casa(regra, e)]

class TestOperacoesSocSiem(unittest.TestCase):
    """Valida a estrutura, o conteúdo, os eventos, as regras e a compilação do estudo Operacoes-SOC-e-SIEM."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / '_geradores' / 'operacoes_soc_e_siem_body.html'
        self.compiled_path = self.root / 'Operacoes-SOC-e-SIEM' / 'treinamento-operacoes-soc-e-siem.html'
        self.portal_path = self.root / 'index.html'

    def _regra(self, d, rid):
        return next((r for r in d['regras'] if r['id'] == rid))

    def _evento(self, d, eid):
        return next((e for e in d['eventos'] if e['id'] == eid))

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        termos = ['N1', 'N2', 'N3', 'MTTD', 'MTTA', 'MTTR', 'falso positivo', 'falso negativo', 'ECS', 'CEF', 'LEEF', 'OCSF', 'normalização', 'enriquecimento', 'correlação', 'retenção', '4624', '4625', '4688', '4720', '4732', '1102', 'Sysmon', 'LogonType', 'Sigma', 'logsource', 'detection', 'condition', 'falsepositives', 'pySigma', 'sigma-cli', 'Kibana Query Language', 'Kusto Query Language', 'SPL', 'T1110', 'T1078', 'T1059.001', 'T1136.001', 'T1098', 'T1070.001', '10.4.1.1']
        for termo in termos:
            self.assertIn(termo, content, f'Termo obrigatório ausente: {termo}')

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn('Operacoes-SOC-e-SIEM/treinamento-operacoes-soc-e-siem.html', content)
        self.assertIn('data-slug="Operacoes-SOC-e-SIEM"', content)
        self.assertIn(f'/ {len(ESTUDOS_DADOS)}', content)
if __name__ == '__main__':
    unittest.main()
