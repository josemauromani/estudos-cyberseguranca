"""
test_laboratorio_portfolio.py
Testes automatizados para o Estudo 37: Laboratorio-Domestico-e-Portfolio
"""
import json
import re
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from index_dados import ESTUDOS_DADOS
VEREDITOS = {'cabe', 'apertado', 'nao_cabe', 'incompativel'}

def veredito(d, host, vms):
    """Regra do planejador (espelhada no JavaScript)."""
    cat = {v['id']: v for v in d['catalogo']}
    if host['arm'] and any((not cat[v]['arm'] for v in vms)):
        return 'incompativel'
    ram = sum((cat[v]['ram'] for v in vms)) + d['reserva_host_gb']
    vcpu = sum((cat[v]['vcpu'] for v in vms))
    disco = sum((cat[v]['disco'] for v in vms))
    if ram > host['ram'] or disco > host['disco']:
        return 'nao_cabe'
    if ram > d['limite_apertado'] * host['ram'] or vcpu > d['vcpu_por_nucleo'] * host['nucleos']:
        return 'apertado'
    return 'cabe'

class TestLaboratorioPortfolio(unittest.TestCase):
    """Valida a estrutura, o conteúdo, o planejador e a compilação do estudo Laboratorio-Domestico-e-Portfolio."""

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        termos = ['tipo 1', 'tipo 2', 'Proxmox', 'VirtualBox', 'Hyper-V', 'snapshot', 'NAT', 'host-only', 'rede interna', 'bridge', 'OPNsense', 'Wazuh', 'Kali', '180 dias', 'jeopardy', 'attack-defense', 'write-up', 'README', 'GitHub', 'Lei 12.737/2012', '154-A', 'Lei 14.155/2021', 'autorização por escrito', 'bug bounty', 'PortSwigger', 'Hack The Box', 'TryHackMe', 'CyberDefenders', 'OverTheWire']
        for termo in termos:
            self.assertIn(termo, content, f'Termo obrigatório ausente: {termo}')
if __name__ == '__main__':
    unittest.main()
