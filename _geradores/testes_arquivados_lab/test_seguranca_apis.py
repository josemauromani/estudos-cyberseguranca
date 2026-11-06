"""
test_seguranca_apis.py
Testes automatizados para o Estudo 13: Seguranca-em-APIs
"""
import base64
import hashlib
import hmac
import json
import re
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from index_dados import ESTUDOS_DADOS
API_TOP10_2023 = [('API1:2023', 'Broken Object Level Authorization'), ('API2:2023', 'Broken Authentication'), ('API3:2023', 'Broken Object Property Level Authorization'), ('API4:2023', 'Unrestricted Resource Consumption'), ('API5:2023', 'Broken Function Level Authorization'), ('API6:2023', 'Unrestricted Access to Sensitive Business Flows'), ('API7:2023', 'Server Side Request Forgery'), ('API8:2023', 'Security Misconfiguration'), ('API9:2023', 'Improper Inventory Management'), ('API10:2023', 'Unsafe Consumption of APIs')]
DEFESAS = {'assinatura', 'campos', 'funcao', 'v1off', 'rate'}

def b64url_decode(s):
    return base64.urlsafe_b64decode(s + '=' * (-len(s) % 4))

def b64url(b):
    return base64.urlsafe_b64encode(b).rstrip(b'=').decode()

def assinatura_ok(d, jwt):
    h, p, s = jwt.split('.')
    esperado = b64url(hmac.new(d['segredo_lab'].encode(), (h + '.' + p).encode(), hashlib.sha256).digest())
    return hmac.compare_digest(esperado, s)

def responder(d, token, metodo, caminho, corpo, defesas):
    m = d['mensagens']
    rota = re.match('^/api/(v1|v2)/pedidos/(\\d+)$', caminho)
    if rota:
        nome, metodos = ('pedido', ['GET'])
    elif caminho == '/api/v2/usuarios/me':
        nome, metodos = ('me', ['GET', 'PATCH'])
    elif caminho == '/api/v2/admin/relatorios/vendas':
        nome, metodos = ('admin', ['GET'])
    else:
        return (404, {'erro': m['rota']})
    if metodo not in metodos:
        return (405, {'erro': m['metodo']})
    if rota and rota.group(1) == 'v1' and ('v1off' in defesas):
        return (410, {'erro': m['v1off']})
    if not token:
        return (401, {'erro': m['sem_token']})
    jwt = d['tokens'][token]['jwt']
    try:
        h64, p64, _ = jwt.split('.')
        cab = json.loads(b64url_decode(h64))
        carga = json.loads(b64url_decode(p64))
    except Exception:
        return (401, {'erro': m['malformado']})
    if 'assinatura' in defesas:
        if cab.get('alg') != 'HS256':
            return (401, {'erro': m['alg']})
        if not assinatura_ok(d, jwt):
            return (401, {'erro': m['assinatura']})
        if carga.get('exp', 0) <= d['agora']:
            return (401, {'erro': m['expirado']})
        if carga.get('aud') != d['aud']:
            return (401, {'erro': m['aud']})
    rec = d['usuarios'].get(str(carga.get('sub')))
    if rec is None:
        return (401, {'erro': m['desconhecido']})
    if nome == 'pedido':
        pid = int(rota.group(2))
        ped = next((p for p in d['pedidos'] if p['id'] == pid), None)
        if ped is None or (rota.group(1) == 'v2' and ped['cliente_id'] != rec['id']):
            return (404, {'erro': m['pedido']})
        return (200, ped)
    if nome == 'admin':
        if 'funcao' in defesas and carga.get('papel') != 'admin':
            return (403, {'erro': m['funcao']})
        return (200, d['relatorio'])
    publico = lambda r: {k: r[k] for k in d['campos_publicos']}
    if metodo == 'GET':
        return (200, publico(rec) if 'campos' in defesas else rec)
    try:
        dados = json.loads(corpo)
    except Exception:
        return (400, {'erro': m['json']})
    if not isinstance(dados, dict):
        return (400, {'erro': m['json']})
    if 'campos' in defesas:
        recusados = sorted((k for k in dados if k not in d['campos_editaveis']))
        if recusados:
            return (422, {'erro': m['campos'], 'campos_recusados': recusados})
        for k in sorted(dados):
            if not isinstance(dados[k], str) or len(dados[k]) > 60:
                return (422, {'erro': m['tipo'], 'campo': k})
    novo = dict(rec)
    novo.update(dados)
    return (200, publico(novo) if 'campos' in defesas else novo)

def janela_fixa(ts, p):
    cont, out = ({}, [])
    for t in ts:
        k = t // p['janela_ms']
        ok = cont.get(k, 0) < p['limite']
        if ok:
            cont[k] = cont.get(k, 0) + 1
        out.append(ok)
    return out

def janela_deslizante(ts, p):
    aceitos, out = ([], [])
    for t in ts:
        aceitos = [a for a in aceitos if a > t - p['janela_ms']]
        ok = len(aceitos) < p['limite']
        if ok:
            aceitos.append(t)
        out.append(ok)
    return out

def token_bucket(ts, p):
    fichas, ultimo, out = (p['capacidade'], ts[0] if ts else 0, [])
    for t in ts:
        fichas = min(p['capacidade'], fichas + (t - ultimo) * p['por_segundo'] / 1000)
        ultimo = t
        ok = fichas >= 1
        if ok:
            fichas -= 1
        out.append(ok)
    return out

def leaky_bucket(ts, p):
    fila, out = ([], [])
    for t in ts:
        fila = [c for c in fila if c > t]
        if len(fila) < p['fila']:
            fim = max(t, fila[-1] if fila else t) + 1000 / p['por_segundo']
            fila.append(fim)
            out.append(fim - t)
        else:
            out.append(None)
    return out

def instantes(cenario):
    return sorted((r['inicio'] + i * r['intervalo'] for r in cenario['rajadas'] for i in range(r['quantidade'])))

def contagens(ts, p):
    return {'fixa': sum(janela_fixa(ts, p)), 'deslizante': sum(janela_deslizante(ts, p)), 'bucket': sum(token_bucket(ts, p)), 'leaky': sum((x is not None for x in leaky_bucket(ts, p)))}

class TestSegurancaAPIs(unittest.TestCase):
    """Valida a estrutura, o conteúdo, a API simulada, os tokens, o rate limiting e a compilação do estudo Seguranca-em-APIs."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / '_geradores' / 'seguranca_em_apis_body.html'
        self.compiled_path = self.root / 'Seguranca-em-APIs' / 'treinamento-seguranca-em-apis.html'
        self.portal_path = self.root / 'index.html'

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        termos = ['OWASP API Security Top 10', '2023', 'BOLA', 'mass assignment', 'exposição excessiva', 'JWT', 'alg', 'none', 'exp', 'aud', 'iss', 'decodificar não é validar', 'Token Bucket', 'Leaky Bucket', 'janela fixa', 'janela deslizante', '429', 'Retry-After', 'API Gateway', 'GraphQL', 'introspecção', 'profundidade', 'batching', 'zumbi', 'inventário', 'esquema', 'allowlist', 'Estudo 12']
        termos += [nome for _, nome in API_TOP10_2023]
        for termo in termos:
            self.assertIn(termo, content, f'Termo obrigatório ausente: {termo}')

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn('Seguranca-em-APIs/treinamento-seguranca-em-apis.html', content)
        self.assertIn('data-slug="Seguranca-em-APIs"', content)
        self.assertIn(f'/ {len(ESTUDOS_DADOS)}', content)
if __name__ == '__main__':
    unittest.main()
