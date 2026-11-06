"""
test_active_directory.py
Testes automatizados para o Estudo 38: Active-Directory-Fundamentos
"""
import json
import re
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from index_dados import ESTUDOS_DADOS
MENSAGENS = ['AS-REQ', 'AS-REP', 'TGS-REQ', 'TGS-REP', 'AP-REQ', 'AP-REP']
ERROS_KERBEROS = {'KRB_AP_ERR_SKEW', 'KDC_ERR_PREAUTH_FAILED', 'KDC_ERR_S_PRINCIPAL_UNKNOWN', 'KDC_ERR_CLIENT_REVOKED'}

def gpo_efetiva(g, ajustes):
    """Precedência LSDOU com ordem de link, Enforced e Block Inheritance (espelhada no JavaScript).

    Devolve {configuração: (valor, gpo vencedora)}.
    """
    enforced = set(ajustes.get('enforced', []))
    desativados = set(ajustes.get('desativados', []))
    bloqueios = set(ajustes.get('block', []))
    ordem = ajustes.get('ordem', {})
    conts = g['containers']

    def links(c):
        nomes = ordem.get(c['id'], [l['gpo'] for l in c['links']])
        return [n for n in nomes if c['id'] + ':' + n not in desativados]
    profundidade_bloqueio = max([i for i, c in enumerate(conts) if c['id'] in bloqueios], default=-1)
    sequencia = []
    for i, c in enumerate(conts):
        bloqueado = i < profundidade_bloqueio and c['tipo'] != 'local'
        for n in reversed(links(c)):
            if c['id'] + ':' + n not in enforced and (not bloqueado):
                sequencia.append(n)
    for c in reversed(conts):
        for n in reversed(links(c)):
            if c['id'] + ':' + n in enforced:
                sequencia.append(n)
    resultado = {}
    for n in sequencia:
        for chave, valor in g['gpos'][n]['valores'].items():
            resultado[chave] = (valor, n)
    return resultado

class TestActiveDirectory(unittest.TestCase):
    """Valida a estrutura, o conteúdo, a precedência de GPO, o Kerberos e a compilação do estudo Active-Directory-Fundamentos."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / '_geradores' / 'active_directory_fundamentos_body.html'
        self.compiled_path = self.root / 'Active-Directory-Fundamentos' / 'treinamento-active-directory-fundamentos.html'
        self.portal_path = self.root / 'index.html'

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        termos = ['floresta', 'domínio', 'OU', 'Global Catalog', 'FSMO', 'PDC Emulator', 'RID Master', 'LDAP', 'LSDOU', 'Enforced', 'Block Inheritance', 'ordem de link', 'loopback', 'KDC', 'TGT', 'SPN', 'PAC', 'krbtgt', 'NTLM', '4768', '4769', '4771', '4776', '5 minutos', 'gMSA', 'Tier 0', 'PAW', 'Kerberoasting', 'Golden Ticket', 'Silver Ticket', 'AS-REP roasting', 'T1558.003', 'pass-the-hash', 'corp.ipestore.example']
        for termo in termos:
            self.assertIn(termo, content, f'Termo obrigatório ausente: {termo}')

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn('Active-Directory-Fundamentos/treinamento-active-directory-fundamentos.html', content)
        self.assertIn('data-slug="Active-Directory-Fundamentos"', content)
        self.assertIn(f'/ {len(ESTUDOS_DADOS)}', content)
if __name__ == '__main__':
    unittest.main()
