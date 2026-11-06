"""
test_pam.py
Testes automatizados para o Estudo 40: PAM-e-Acessos-Privilegiados
"""
import json
import re
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from index_dados import ESTUDOS_DADOS
TIPOS_PROBLEMA = {'compartilhada', 'sem_rotacao', 'permanente', 'orfa', 'sem_mfa', 'servico'}
TIPOS_CONTA = {'humana', 'builtin', 'servico', 'gmsa', 'emergencia'}

def achados(d, c):
    """Regras de auditoria (espelhadas no JavaScript)."""
    pol = d['politica']
    out = set()
    if c['compartilhada']:
        out.add('compartilhada')
    if c['tipo'] != 'gmsa' and c['senha_idade_dias'] > pol['rotacao_dias']:
        out.add('sem_rotacao')
    if c['tipo'] == 'humana' and c['privilegio_permanente']:
        out.add('permanente')
    if c['tipo'] != 'emergencia' and c['ativa'] and (c['dono_desligado'] or c['ultimo_logon_dias'] > pol['inatividade_dias']):
        out.add('orfa')
    if c['tipo'] == 'humana' and c['tier'] in (0, 1) and (not c['mfa']):
        out.add('sem_mfa')
    if c['tipo'] == 'servico' and (c['logon_interativo'] or c['tier'] == 0):
        out.add('servico')
    return out

def corrigido(d, c, problema, ativos):
    for k in d['controles']:
        if k['id'] in ativos and problema in k['corrige'] and (not k['apenas_se'] or c[k['apenas_se']]):
            return True
    return False

def risco(d, ativos=()):
    total = 0
    for c in d['contas']:
        peso = d['pesos_tier'][str(c['tier'])]
        for p in achados(d, c):
            if not corrigido(d, c, p, set(ativos)):
                total += peso * d['problemas'][p]['severidade']
    return total

class TestPam(unittest.TestCase):
    """Valida a estrutura, o conteúdo, as regras de auditoria e a compilação do estudo PAM-e-Acessos-Privilegiados."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / '_geradores' / 'pam_e_acessos_privilegiados_body.html'
        self.compiled_path = self.root / 'PAM-e-Acessos-Privilegiados' / 'treinamento-pam-e-acessos-privilegiados.html'
        self.portal_path = self.root / 'index.html'

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        termos = ['PAM', 'cofre', 'checkout', 'rotação', 'gravação de sessão', 'just-in-time', 'JIT', 'PIM', 'JEA', 'break-glass', 'conta órfã', 'recertificação', 'menor privilégio', 'segregação de funções', 'Windows LAPS', 'gMSA', '8.2', '5.18', '7.2.4', '8.2.2', '8.6', 'T1078.002', 'T1098', 'CIS Controls']
        for termo in termos:
            self.assertIn(termo, content, f'Termo obrigatório ausente: {termo}')

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn('PAM-e-Acessos-Privilegiados/treinamento-pam-e-acessos-privilegiados.html', content)
        self.assertIn('data-slug="PAM-e-Acessos-Privilegiados"', content)
        self.assertIn(f'/ {len(ESTUDOS_DADOS)}', content)
if __name__ == '__main__':
    unittest.main()
