"""
test_devsecops.py
Testes automatizados para o Estudo 22: DevSecOps-e-CI-CD
"""
import json
import re
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from index_dados import ESTUDOS_DADOS
SEVERIDADES = ['baixa', 'media', 'alta', 'critica']

def nivel(sev):
    return SEVERIDADES.index(sev) + 1

def resolvido(d, a, estado):
    return any((c['resolve'] and c['id'] in estado['correcoes'] for c in a['correcoes']))

def excecao_valida(d, a, estado):
    if a['severidade'] == 'critica':
        return False
    return any((e['achado'] == a['id'] and e['id'] in estado['excecoes'] and (e['validade'] >= d['hoje']) for e in d['excecoes']))

def bloqueia(d, a, estado):
    lim = estado['limiares'][a['etapa']]
    if resolvido(d, a, estado) or lim == 'nunca':
        return False
    if nivel(a['severidade']) < nivel(lim):
        return False
    if estado['baseline'] and (not a['novo']):
        return False
    return not excecao_valida(d, a, estado)

def avaliar(d, estado):
    """Espelho do avaliador do pipeline em JavaScript."""
    for etapa in d['etapas']:
        bl = [a['id'] for a in d['achados'] if a['etapa'] == etapa['id'] and bloqueia(d, a, estado)]
        if bl:
            return {'resultado': etapa['id'], 'bloqueantes': bl, 'producao': []}
    prod = [a['id'] for a in d['achados'] if not resolvido(d, a, estado)]
    return {'resultado': 'deploy', 'bloqueantes': [], 'producao': prod}

class TestDevSecOps(unittest.TestCase):
    """Valida a estrutura, o conteúdo, o avaliador do pipeline e a compilação do estudo DevSecOps-e-CI-CD."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / '_geradores' / 'devsecops_e_ci_cd_body.html'
        self.compiled_path = self.root / 'DevSecOps-e-CI-CD' / 'treinamento-devsecops-e-ci-cd.html'
        self.portal_path = self.root / 'index.html'

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        termos = ['Shift-Left', 'SSDLC', 'SAST', 'DAST', 'IAST', 'SCA', 'SBOM', 'CycloneDX', 'SPDX', 'EPSS', 'KEV', 'CVE-2021-44228', 'Gitleaks', 'Semgrep', 'pip-audit', 'Trivy', 'OWASP ZAP', 'distroless', 'digest', 'USER', 'runAsNonRoot', 'readOnlyRootFilesystem', 'Sigstore', 'Cosign', 'cosign verify', 'quality gate', 'baseline', 'histórico', 'revogar', 'Estudo 12', 'Estudo 13', 'Estudo 25']
        for termo in termos:
            self.assertIn(termo, content, f'Termo obrigatório ausente: {termo}')

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn('DevSecOps-e-CI-CD/treinamento-devsecops-e-ci-cd.html', content)
        self.assertIn('data-slug="DevSecOps-e-CI-CD"', content)
        self.assertIn(f'/ {len(ESTUDOS_DADOS)}', content)
if __name__ == '__main__':
    unittest.main()
