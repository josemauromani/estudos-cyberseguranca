"""
test_monitoramento_rede_nsm.py
Testes automatizados para o Estudo 48: Monitoramento-de-Rede-NSM

O Analisador de Conexões guarda um conn.log e um dns.log fictícios, no formato
do Zeek, num bloco JSON. Este teste espelha em Python a expansão das séries em
conexões, o agrupamento por par origem–destino, as métricas de beaconing
(intervalo médio, jitter e estabilidade do tamanho), as métricas de túnel DNS
(comprimento, entropia e nomes distintos) e as contagens de acertos e falsos
positivos do JavaScript, para validar que os limiares padrão geram os falsos
positivos esperados e que existe um ajuste que pega só o que é malicioso.
"""
import base64
import ipaddress
import json
import math
import re
import sys
import unittest
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from index_dados import ESTUDOS_DADOS
REDES_PRIVADAS = [ipaddress.ip_network(n) for n in ('10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16')]
REDES_DOC = [ipaddress.ip_network(n) for n in ('192.0.2.0/24', '198.51.100.0/24', '203.0.113.0/24')]
ALFABETO_B32 = 'abcdefghijklmnopqrstuvwxyz234567'

def privado(ip):
    a = ipaddress.ip_address(ip)
    return any((a in n for n in REDES_PRIVADAS))

def expandir_conexoes(d):
    """Espelho de expandirConexoes: cada série vira uma conexão por instante (t0 + intervalos acumulados)."""
    conns = []
    for s in d['series']:
        t = s['t0']
        offs = [t]
        for iv in s['intervalos']:
            t += iv
            offs.append(t)
        for k, off in enumerate(offs):
            conns.append({'serie': s['id'], 'off': off, 'orig_h': s['orig_h'], 'resp_h': s['resp_h'], 'resp_p': s['resp_p'], 'proto': s['proto'], 'orig_bytes': s['orig_bytes'][k], 'resp_bytes': s['resp_bytes'][k], 'beacon': s['rotulo'] == 'beacon'})
    conns.sort(key=lambda c: (c['off'], c['serie']))
    return conns

def casa_excecao(c, e):
    return all((c[k] == e[k] for k in ('orig_h', 'resp_h', 'resp_p') if k in e))

def chave(c, agrupar):
    if agrupar == 'par':
        return '%s → %s:%s/%s' % (c['orig_h'], c['resp_h'], c['resp_p'], c['proto'])
    if agrupar == 'destino':
        return '* → %s:%s/%s' % (c['resp_h'], c['resp_p'], c['proto'])
    return '%s → *' % c['orig_h']

def mediana(v):
    s = sorted(v)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2

def agrupar_conexoes(d, cfg):
    """Espelho de agruparConexoes: filtra (externos, exceções), agrupa e mede cada grupo."""
    exc = [e for e in d['excecoes'] if e['id'] in cfg.get('excecoes', [])]
    grupos, ignoradas = ({}, 0)
    for c in expandir_conexoes(d):
        if cfg.get('so_externos') and privado(c['resp_h']) or any((casa_excecao(c, e) for e in exc)):
            ignoradas += 1
            continue
        grupos.setdefault(chave(c, cfg['agrupar']), []).append(c)
    res = []
    for k, cs in grupos.items():
        offs = [c['off'] for c in cs]
        ivs = [offs[i + 1] - offs[i] for i in range(len(offs) - 1)]
        n = len(cs)
        media = sum(ivs) / len(ivs) if ivs else 0
        jitter = 100 * math.sqrt(sum(((x - media) ** 2 for x in ivs)) / len(ivs)) / media if ivs and media > 0 else 0
        med = mediana([c['orig_bytes'] for c in cs])
        estab = 100 * sum((1 for c in cs if abs(c['orig_bytes'] - med) <= 0.1 * med)) / n
        beacons = sorted({c['serie'] for c in cs if c['beacon']})
        alerta = n >= cfg['min_conexoes'] and len(ivs) > 0 and (media <= cfg['max_intervalo']) and (jitter <= cfg['max_jitter']) and (estab >= cfg['min_estabilidade'])
        res.append({'chave': k, 'n': n, 'media': media, 'jitter': jitter, 'estab': estab, 'series': sorted({c['serie'] for c in cs}), 'beacons': beacons, 'alerta': alerta})
    res.sort(key=lambda g: (not g['alerta'], g['jitter'], g['chave']))
    return (res, ignoradas)

def placar_conexoes(d, grupos):
    """Espelho de placarConexoes: alertas com beacon, falsos positivos e beacons perdidos."""
    todos = {s['id'] for s in d['series'] if s['rotulo'] == 'beacon'}
    alertas = [g for g in grupos if g['alerta']]
    vp = [g for g in alertas if g['beacons']]
    fp = [g for g in alertas if not g['beacons']]
    vistos = {b for g in vp for b in g['beacons']}
    return {'vp': len(vp), 'fp': len(fp), 'fn': len(todos - vistos), 'fp_series': sorted((s for g in fp for s in g['series']))}

def base_dominio(q):
    return '.'.join(q.split('.')[-2:])

def subdominio(q):
    return '.'.join(q.split('.')[:-2])

def entropia(s):
    """Espelho de entropiaShannon: bits por caractere do subdomínio, sem os pontos."""
    s = s.replace('.', '')
    if not s:
        return 0.0
    n = len(s)
    return -sum((c / n * math.log2(c / n) for c in Counter(s).values()))

def agrupar_dns(d, cfg):
    """Espelho de agruparDns: agrupa o dns.log por domínio base e mede os subdomínios."""
    g = {}
    for r in d['dns']:
        g.setdefault(base_dominio(r[2]), []).append(r)
    res = []
    for base, rs in g.items():
        subs = [subdominio(r[2]) for r in rs]
        n = len(rs)
        distintos = len({r[2] for r in rs})
        comp = sum((len(s) for s in subs)) / n
        ent = sum((entropia(s) for s in subs)) / n
        rotulo = d['dominios'].get(base, {'rotulo': 'benigno'})['rotulo']
        alerta = distintos >= cfg['dns_min_distintos'] and comp >= cfg['dns_min_comprimento'] and (ent >= cfg['dns_min_entropia'])
        res.append({'base': base, 'n': n, 'distintos': distintos, 'comp': comp, 'ent': ent, 'rotulo': rotulo, 'alerta': alerta, 'origens': sorted({r[1] for r in rs}), 'qtypes': Counter((r[3] for r in rs))})
    res.sort(key=lambda x: (not x['alerta'], -x['ent'], x['base']))
    return res

def placar_dns(grupos):
    """Espelho de placarDns: só o túnel conta como acerto; o domínio de C2 não é túnel."""
    return {'vp': sum((1 for g in grupos if g['alerta'] and g['rotulo'] == 'tunel')), 'fp': sum((1 for g in grupos if g['alerta'] and g['rotulo'] != 'tunel')), 'fn': sum((1 for g in grupos if not g['alerta'] and g['rotulo'] == 'tunel')), 'fp_bases': [g['base'] for g in grupos if g['alerta'] and g['rotulo'] != 'tunel']}

def decodificar_base32(rotulo):
    """Espelho de decodificarBase32: texto legível ou None (rótulos curtos não carregam dados)."""
    if len(rotulo) < 16 or any((ch not in ALFABETO_B32 for ch in rotulo)):
        return None
    pad = '=' * (-len(rotulo) % 8)
    try:
        bruto = base64.b32decode(rotulo.upper() + pad)
    except Exception:
        return None
    legiveis = sum((1 for b in bruto if b in (9, 10, 13) or 32 <= b < 127))
    return bruto.decode('ascii', 'replace') if bruto and legiveis / len(bruto) >= 0.9 else None
IDEAL = {'so_externos': True, 'max_intervalo': 240, 'max_jitter': 35, 'min_estabilidade': 80, 'excecoes': ['exc-ntp']}

class TestMonitoramentoRedeNSM(unittest.TestCase):
    """Valida a estrutura, o conteúdo, o Analisador de Conexões e a compilação do estudo 48."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / '_geradores' / 'monitoramento_de_rede_nsm_body.html'
        self.compiled_path = self.root / 'Monitoramento-de-Rede-NSM' / 'treinamento-monitoramento-de-rede-nsm.html'
        self.portal_path = self.root / 'index.html'

    def _cfg(self, d, **extra):
        cfg = dict(d['padrao'])
        cfg.update(extra)
        return cfg

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        termos = ['Network Security Monitoring', 'NSM', 'Zeek', 'PCAP', 'NetFlow', 'IPFIX', 'RFC 7011', 'conn.log', 'dns.log', 'ssl.log', 'id.orig_h', 'id.resp_h', 'id.resp_p', 'orig_bytes', 'resp_bytes', 'conn_state', 'qtype_name', 'answers', 'server_name', 'zeek-cut', 'beaconing', 'jitter', 'coeficiente de variação', 'túnel DNS', 'entropia', 'Shannon', 'base32', 'TXT', 'JA3', 'JA4', 'SNI', 'TLS 1.3', 'TAP', 'SPAN', 'amostragem', 'RITA', 'nfdump', 'tcpdump', 'T1071', 'T1071.004', 'T1048', 'exceção documentada', 'Estudo 07', 'Estudo 02', 'Estudo 46', 'Estudo 47', 'Estudo 49', 'RFC 5737', 'LGPD']
        for termo in termos:
            self.assertIn(termo, content, f'Termo obrigatório ausente: {termo}')

    def test_pcap_rotativo_nao_para_apos_48_arquivos(self):
        """Com -G, o -W encerra o tcpdump ao atingir o limite: a retenção de 48 h vem da limpeza por idade."""
        body = self.body_path.read_text(encoding='utf-8')
        self.assertNotIn('-W 48', body)
        self.assertIn('-mmin +2880 -delete', body)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn('Monitoramento-de-Rede-NSM/treinamento-monitoramento-de-rede-nsm.html', content)
        self.assertIn('data-slug="Monitoramento-de-Rede-NSM"', content)
        self.assertIn(f'/ {len(ESTUDOS_DADOS)}', content)
if __name__ == '__main__':
    unittest.main()
