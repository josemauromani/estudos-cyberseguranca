"""
test_powershell_windows.py
Testes automatizados para o Estudo 36: PowerShell-e-Windows-Interno
"""
import base64
import ipaddress
import json
import re
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from index_dados import ESTUDOS_DADOS
SYSMON = 'Microsoft-Windows-Sysmon/Operational'
PSLOG = 'Microsoft-Windows-PowerShell/Operational'

def basename(caminho):
    return caminho.replace('/', '\\').split('\\')[-1]

class TestPowerShellWindows(unittest.TestCase):
    """Valida a estrutura, o conteúdo, os eventos e a compilação do estudo PowerShell-e-Windows-Interno."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / '_geradores' / 'powershell_e_windows_interno_body.html'
        self.compiled_path = self.root / 'PowerShell-e-Windows-Interno' / 'treinamento-powershell-e-windows-interno.html'
        self.portal_path = self.root / 'index.html'

    def _eventos(self, d, log, eid):
        return [e for e in d['eventos'] if e['LogName'] == log and e['Id'] == eid]

    def _ps_malicioso(self, d):
        return next((e for e in self._eventos(d, SYSMON, 1) if basename(e['Image']).lower() == 'powershell.exe' and ' -enc ' in e['CommandLine'].lower()))

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        termos = ['Verbo-Substantivo', 'Get-Command', 'Get-Help', 'Get-Member', 'pipeline de objetos', 'Where-Object', 'Select-Object', 'Group-Object', 'Get-WinEvent', 'FilterHashtable', '4624', '4625', '4648', '4672', '4688', '4720', '4732', '4698', '7045', '1102', 'LogonType', 'Sysmon', '4104', 'ScriptBlock', 'HKLM', 'HKCU', 'execution policy', 'AMSI', 'Constrained Language Mode', 'PowerShell v2', 'T1059.001', 'T1547.001', 'T1136.001', 'T1543.003', 'T1566.001', 'ToXml']
        for termo in termos:
            self.assertIn(termo, content, f'Termo obrigatório ausente: {termo}')

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn('PowerShell-e-Windows-Interno/treinamento-powershell-e-windows-interno.html', content)
        self.assertIn('data-slug="PowerShell-e-Windows-Interno"', content)
        self.assertIn(f'/ {len(ESTUDOS_DADOS)}', content)
if __name__ == '__main__':
    unittest.main()
