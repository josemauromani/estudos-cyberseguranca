"""
test_ataques_ad.py
Testes automatizados para o Estudo 39: Ataques-e-Defesa-no-AD
"""
import itertools
import json
import re
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from index_dados import ESTUDOS_DADOS
GUID_GET_CHANGES = '1131f6aa-9c07-11d1-f79f-00c04fc2dcd2'
GUID_GET_CHANGES_ALL = '1131f6ad-9c07-11d1-f79f-00c04fc2dcd2'
TECNICAS = {'T1558.003', 'T1550.002', 'T1003.006'}
RESPOSTAS = {'kerberoasting', 'pth', 'dcsync', 'normal'}
OFENSIVOS = ['Invoke-Kerberoast', 'sekurlsa::', 'lsadump::', 'Rubeus.exe', 'secretsdump', 'GetUserSPNs', 'Invoke-Mimikatz']

def caminhos(d, removidas=frozenset()):
    """Todos os caminhos simples (listas de ids de arestas) do início até o alvo."""
    saidas = {}
    for a in d['arestas']:
        if a['id'] not in removidas:
            saidas.setdefault(a['de'], []).append(a)
    achados = []

    def dfs(no, visitados, trilha):
        if no == d['alvo']:
            achados.append(list(trilha))
            return
        for a in saidas.get(no, []):
            if a['para'] not in visitados:
                dfs(a['para'], visitados | {a['para']}, trilha + [a['id']])
    dfs(d['inicio'], {d['inicio']}, [])
    return achados

def removidas_por(d, ids):
    mit = {m['id']: m for m in d['mitigacoes']}
    return frozenset((a for i in ids for a in mit[i]['remove']))

def classificar(ev, dcs):
    """Regras de campo que o aluno deve aprender (espelham as explicações)."""
    c = ev['campos']
    if ev['evento'] == 4769:
        servico = c['ServiceName']
        if c['TicketEncryptionType'] == '0x17' and (not servico.endswith('$')) and (servico != 'krbtgt'):
            return 'kerberoasting'
        return 'normal'
    if ev['evento'] == 4624:
        if c['LogonType'] == '9' and c['LogonProcessName'].strip() == 'seclogo':
            return 'pth'
        local = c['TargetDomainName'].upper() != 'CORP'
        if c['LogonType'] == '3' and c['AuthenticationPackageName'] == 'NTLM' and local:
            return 'pth'
        return 'normal'
    if ev['evento'] == 4662:
        replica = GUID_GET_CHANGES_ALL in c['Properties']
        if replica and c['SubjectUserName'] not in dcs:
            return 'dcsync'
        return 'normal'
    raise AssertionError('evento inesperado: %s' % ev['evento'])

class TestAtaquesAD(unittest.TestCase):
    """Valida a estrutura, o conteúdo, o grafo, os eventos e a compilação do estudo Ataques-e-Defesa-no-AD."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / '_geradores' / 'ataques_e_defesa_no_ad_body.html'
        self.compiled_path = self.root / 'Ataques-e-Defesa-no-AD' / 'treinamento-ataques-e-defesa-no-ad.html'
        self.portal_path = self.root / 'index.html'

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        termos = ['BloodHound', 'grafo', 'MemberOf', 'AdminTo', 'HasSession', 'GenericAll', 'Kerberoasting', 'SPN', 'Pass-the-Hash', 'NTLM', 'DCSync', 'krbtgt', 'Golden Ticket', 'duas vezes', '4769', '0x17', '4624', 'tipo 9', '4662', GUID_GET_CHANGES, GUID_GET_CHANGES_ALL, 'gMSA', 'AES', 'LAPS', 'Protected Users', 'tiering', 'Tier 0', 'T1558.003', 'T1550.002', 'T1003.006', 'Estudo 38', 'Estudo 40']
        for termo in termos:
            self.assertIn(termo, content, f'Termo obrigatório ausente: {termo}')

    def test_sem_comandos_ofensivos(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        for termo in OFENSIVOS:
            self.assertNotIn(termo, content, f'O módulo é defensivo: {termo}')

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn('Ataques-e-Defesa-no-AD/treinamento-ataques-e-defesa-no-ad.html', content)
        self.assertIn('data-slug="Ataques-e-Defesa-no-AD"', content)
        self.assertIn(f'/ {len(ESTUDOS_DADOS)}', content)
if __name__ == '__main__':
    unittest.main()
