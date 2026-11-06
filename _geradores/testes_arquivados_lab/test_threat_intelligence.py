"""
test_threat_intelligence.py
Testes automatizados para o Estudo 17: Threat-Intelligence
"""
import ipaddress
import json
import re
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from index_dados import ESTUDOS_DADOS
TATICAS_2025 = ['TA0043', 'TA0042', 'TA0001', 'TA0002', 'TA0003', 'TA0004', 'TA0005', 'TA0006', 'TA0007', 'TA0008', 'TA0009', 'TA0011', 'TA0010', 'TA0040']
CRIADO = '2026-11-02T00:00:00.000Z'

def refang(t):
    t = re.sub('hxxp', 'http', t, flags=re.I)
    for a, b in (('[.]', '.'), ('(.)', '.'), ('[:]', ':'), ('[@]', '@')):
        t = t.replace(a, b)
    return t

def defang(v):
    return v.replace('http', 'hxxp').replace('.', '[.]').replace('@', '[@]')

def extrair(d, texto):
    """Espelho do extrator em JavaScript: lista de [tipo, valor] na ordem da primeira aparição."""
    t = refang(texto)
    achados = []
    vistos = set()

    def add(tipo, v, pos):
        if (tipo, v) not in vistos:
            vistos.add((tipo, v))
            achados.append((pos, tipo, v))
    urls = []
    for m in re.finditer('https?://[^\\s<>\\"\']+', t, re.A):
        v = m.group(0).rstrip('.,;:)')
        urls.append((m.start(), m.start() + len(v)))
        add('url', v, m.start())
    emails = []
    for m in re.finditer('\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}\\b', t, re.A):
        emails.append((m.start(), m.end()))
        add('email', m.group(0).lower(), m.start())
    dentro = lambda a, b: any((x <= a and b <= y for x, y in urls + emails))
    for m in re.finditer('\\b(?:\\d{1,3}\\.){3}\\d{1,3}\\b', t, re.A):
        if all((int(o) <= 255 and (o == '0' or not o.startswith('0')) for o in m.group(0).split('.'))):
            ip = ipaddress.ip_address(m.group(0))
            interno = any((ip in ipaddress.ip_network(r) for r in ('10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16', '127.0.0.0/8')))
            add('ip_interno' if interno else 'ip', m.group(0), m.start())
    for tam, tipo in ((64, 'sha256'), (40, 'sha1'), (32, 'md5')):
        for m in re.finditer('\\b[a-fA-F0-9]{%d}\\b' % tam, t, re.A):
            add(tipo, m.group(0).lower(), m.start())
    for m in re.finditer('\\b(?:[A-Za-z0-9-]+\\.)+([A-Za-z]{2,})\\b', t, re.A):
        if m.group(1).lower() in d['tlds'] and (not dentro(m.start(), m.end())):
            add('dominio', m.group(0).lower(), m.start())
    for m in re.finditer('\\bCVE-\\d{4}-\\d{4,7}\\b', t, re.A):
        add('cve', m.group(0), m.start())
    for m in re.finditer('\\bT\\d{4}(?:\\.\\d{3})?\\b', t, re.A):
        add('tecnica', m.group(0), m.start())
    baixo = t.lower()
    for f in d['ferramentas']:
        i = baixo.find(f.lower())
        if i >= 0:
            add('ferramenta', f, i)
    return [[tipo, v] for _, tipo, v in sorted(achados, key=lambda x: (x[0], x[1]))]

def tecnicas(d, texto, extras=()):
    ids = [v for tipo, v in extrair(d, texto) if tipo == 'tecnica' and v in d['catalogo']]
    baixo = refang(texto).lower()
    for chave, tid in d['palavras']:
        if chave.lower() in baixo and tid not in ids:
            ids.append(tid)
    for tid in extras:
        if tid in d['catalogo'] and tid not in ids:
            ids.append(tid)
    return ids

def mapa(d, ids):
    cont = {t['id']: 0 for t in d['taticas']}
    for i in ids:
        cont[d['catalogo'][i]['tatica']] += 1
    return cont

def uid(tipo, n):
    return f'{tipo}--00000000-0000-4000-8000-{n:012d}'

def padrao(tipo, v):
    if tipo == 'ip':
        return f"[ipv4-addr:value = '{v}']"
    if tipo == 'dominio':
        return f"[domain-name:value = '{v}']"
    if tipo == 'url':
        return f"[url:value = '{v}']"
    if tipo == 'email':
        return f"[email-addr:value = '{v}']"
    nome = {'md5': 'MD5', 'sha1': 'SHA-1', 'sha256': 'SHA-256'}[tipo]
    return f"[file:hashes.'{nome}' = '{v}']"

def bundle(d, texto, extras=()):
    n = 0

    def novo(tipo):
        nonlocal n
        n += 1
        return uid(tipo, n)
    ator = {'type': 'threat-actor', 'spec_version': '2.1', 'id': novo('threat-actor'), 'created': CRIADO, 'modified': CRIADO, 'name': d['ator'], 'threat_actor_types': ['crime-syndicate']}
    objs = [ator]
    for tipo, v in extrair(d, texto):
        if tipo in ('ip', 'dominio', 'url', 'email', 'md5', 'sha1', 'sha256'):
            ind = {'type': 'indicator', 'spec_version': '2.1', 'id': novo('indicator'), 'created': CRIADO, 'modified': CRIADO, 'name': f'{tipo}: {v}', 'pattern': padrao(tipo, v), 'pattern_type': 'stix', 'valid_from': CRIADO}
            objs.append(ind)
            objs.append({'type': 'relationship', 'spec_version': '2.1', 'id': novo('relationship'), 'created': CRIADO, 'modified': CRIADO, 'relationship_type': 'indicates', 'source_ref': ind['id'], 'target_ref': ator['id']})
    for tid in tecnicas(d, texto, extras):
        ap = {'type': 'attack-pattern', 'spec_version': '2.1', 'id': novo('attack-pattern'), 'created': CRIADO, 'modified': CRIADO, 'name': d['catalogo'][tid]['nome'], 'external_references': [{'source_name': 'mitre-attack', 'external_id': tid}]}
        objs.append(ap)
        objs.append({'type': 'relationship', 'spec_version': '2.1', 'id': novo('relationship'), 'created': CRIADO, 'modified': CRIADO, 'relationship_type': 'uses', 'source_ref': ator['id'], 'target_ref': ap['id']})
    return {'type': 'bundle', 'id': uid('bundle', 0), 'objects': objs}

class TestThreatIntelligence(unittest.TestCase):
    """Valida a estrutura, o conteúdo, o extrator, o mapa ATT&CK, o STIX e a compilação do estudo 17."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / '_geradores' / 'threat_intelligence_body.html'
        self.compiled_path = self.root / 'Threat-Intelligence' / 'treinamento-threat-intelligence.html'
        self.portal_path = self.root / 'index.html'

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        termos = ['Pirâmide da Dor', 'David Bianco', 'IoC', 'TTP', 'MITRE ATT&amp;CK', 'tática', 'técnica', 'subtécnica', 'T1059.001', 'estratégica', 'operacional', 'tática', 'ciclo de inteligência', 'TLP', 'TLP:AMBER', 'defang', 'STIX 2.1', 'TAXII', 'Indicator', 'Threat Actor', 'Relationship', 'MISP', 'OpenCTI']
        for termo in termos:
            self.assertIn(termo, content, f'Termo obrigatório ausente: {termo}')

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn('Threat-Intelligence/treinamento-threat-intelligence.html', content)
        self.assertIn('data-slug="Threat-Intelligence"', content)
        self.assertIn(f'/ {len(ESTUDOS_DADOS)}', content)
if __name__ == '__main__':
    unittest.main()
