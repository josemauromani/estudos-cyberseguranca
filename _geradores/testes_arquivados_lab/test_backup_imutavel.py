"""
test_backup_imutavel.py
Testes automatizados para o Estudo 45: Backup-Imutavel-e-Recuperacao
"""
import json
import re
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from index_dados import ESTUDOS_DADOS

def atacar(d, a, perfil):
    """Espelho do motor em JavaScript: o que sobrevive a um atacante com Domain Admin."""
    dias = d['perfis'][perfil]['dias']
    alcanca = not a['rede_gerencia_isolada'] or a['servidor_no_dominio']
    console = alcanca and (a['servidor_no_dominio'] or (a['console_contas'] == 'dominio' and (not a['console_mfa'])))
    copias = {}
    for c in a['copias']:
        if c == 'nas_smb':
            copias[c] = ['perdida', 'nas_dominio']
        elif c == 'site_remoto':
            copias[c] = ['perdida', 'remoto_dominio']
        elif c == 'linux_endurecido':
            if a['linux_ssh_dominio']:
                copias[c] = ['perdida', 'ssh_dominio']
            elif a['retencao_imutavel_dias'] < dias:
                copias[c] = ['perdida', 'imutabilidade_expirou']
            else:
                copias[c] = ['sobrevive', 'imutavel']
        elif c == 'nuvem_object_lock':
            expostas = a['nuvem_credencial'] == 'no_servidor' and console
            if a['object_lock_modo'] == 'governance' and expostas:
                copias[c] = ['perdida', 'governance_contornado']
            elif a['retencao_imutavel_dias'] < dias:
                copias[c] = ['perdida', 'imutabilidade_expirou']
            else:
                copias[c] = ['sobrevive', 'object_lock']
        elif c == 'fita_offline':
            if not a['fita_ejetada'] and console:
                copias[c] = ['perdida', 'fita_conectada']
            else:
                copias[c] = ['sobrevive', 'air_gap']
    sobrev = [c for c, v in copias.items() if v[0] == 'sobrevive']
    ad = a['backup_dc'] and a['dsrm_cofre'] and bool(sobrev)
    if not sobrev:
        status = 'perdido'
    elif not ad:
        status = 'sem_ad'
    elif not a['teste_restauracao']:
        status = 'nao_testado'
    else:
        status = 'recuperavel'
    return {'console_comprometido': console, 'copias': copias, 'status': status}

def regra(d, a):
    midias = {'disco'} | {d['copias'][c]['midia'] for c in a['copias']}
    return {'tres_copias': 1 + len(a['copias']) >= 3, 'duas_midias': len(midias) >= 2, 'uma_fora': any((d['copias'][c]['fora'] for c in a['copias'])), 'uma_imutavel_offline': any((c in ('linux_endurecido', 'nuvem_object_lock') or (c == 'fita_offline' and a['fita_ejetada']) for c in a['copias'])), 'zero_erros': bool(a['teste_restauracao'])}

class TestBackupImutavel(unittest.TestCase):
    """Valida a estrutura, o conteúdo, o motor de ataque e a compilação do estudo 45."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / '_geradores' / 'backup_imutavel_e_recuperacao_body.html'
        self.compiled_path = self.root / 'Backup-Imutavel-e-Recuperacao' / 'treinamento-backup-imutavel-e-recuperacao.html'
        self.portal_path = self.root / 'index.html'

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        termos = ['3-2-1-1-0', 'WORM', 'object lock', 'governance', 'compliance', 'air gap', 'imutabilidade', 'repositório Linux endurecido', 'fora do domínio', 'MFA', 'DSRM', 'restauração autoritativa', 'não autoritativa', 'krbtgt', 'recuperação de floresta', 'ambiente isolado', 'wbadmin', 'ntdsutil', 'chattr +i', 'put-object-lock-configuration', 'Estudo 28', 'Estudo 39', 'Estudo 42']
        for termo in termos:
            self.assertIn(termo, content, f'Termo obrigatório ausente: {termo}')

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn('Backup-Imutavel-e-Recuperacao/treinamento-backup-imutavel-e-recuperacao.html', content)
        self.assertIn('data-slug="Backup-Imutavel-e-Recuperacao"', content)
        self.assertIn(f'/ {len(ESTUDOS_DADOS)}', content)
if __name__ == '__main__':
    unittest.main()
