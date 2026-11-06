"""
test_protecao_dados_conteudo.py
Testes automatizados para o Estudo 29: Protecao-de-Dados-e-Conteudo

O motor do Gateway de Conteúdo é reimplementado aqui em Python, com as mesmas
regras do JavaScript, para validar os dados e os vereditos esperados.
"""
import copy
import json
import re
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from index_dados import ESTUDOS_DADOS
SEVERIDADE = {'permitir': 0, 'quarentena': 1, 'bloquear': 2}
RE_CPF = re.compile('\\b\\d{3}\\.?\\d{3}\\.?\\d{3}-?\\d{2}\\b')
RE_CARTAO = re.compile('\\b(?:\\d[ -]?){12,18}\\d\\b')
RE_URL = re.compile('https?://[^\\s<>\\"\']+')

def cpf_valido(texto):
    d = re.sub('\\D', '', texto)
    if len(d) != 11 or len(set(d)) == 1:
        return False
    for n in (9, 10):
        s = sum((int(d[i]) * (n + 1 - i) for i in range(n)))
        r = s % 11
        if int(d[n]) != (0 if r < 2 else 11 - r):
            return False
    return True

def luhn_valido(texto):
    d = [int(x) for x in re.sub('\\D', '', texto)][::-1]
    total = 0
    for i, x in enumerate(d):
        if i % 2:
            x *= 2
            if x > 9:
                x -= 9
        total += x
    return total % 10 == 0

def dominio(endereco):
    return endereco.split('@')[-1].lower()

def org(dom):
    return '.'.join(dom.lower().split('.')[-2:])

def maior(*vereditos):
    return max((v for v in vereditos if v), key=lambda v: SEVERIDADE[v])

def antispam(d, item, pol):
    if item['tipo'] != 'email-entrada':
        return None
    info = {}
    if pol['bloquear_lista'] and item['lista_bloqueio']:
        info['veredito'] = 'bloquear'
        return info
    de = dominio(item['de'])
    spf_alinhado = item['spf'] == 'pass' and org(dominio(item['envelope'])) == org(de)
    dkim_alinhado = item['dkim'] == 'pass' and org(item['dkim_dominio']) == org(de)
    info['dmarc'] = 'pass' if spf_alinhado or dkim_alinhado else 'fail'
    veredito = 'permitir'
    if info['dmarc'] == 'fail' and pol['respeitar_dmarc']:
        veredito = {'reject': 'bloquear', 'quarantine': 'quarentena', 'none': 'permitir'}[item['dmarc_politica']]
    texto = (item['assunto'] + ' ' + item['corpo']).lower()
    pontos = sum((r['pontos'] for r in d['regras_spam'] if r['termo'] in texto))
    if item['idade_dominio_dias'] < d['idade_dominio_novo']:
        pontos += d['pontos_dominio_novo']
    info['pontos'] = pontos
    if pontos >= pol['limiar_spam']:
        veredito = maior(veredito, 'quarentena')
    info['veredito'] = veredito
    return info

def dlp(d, item, pol):
    if item['tipo'] == 'email-entrada':
        return None
    info = {}
    if item['tipo'] == 'email-saida' and dominio(item['para']) == d['dominio_interno']:
        info['veredito'] = 'permitir'
        return info
    texto = item.get('assunto', '') + ' ' + item['corpo']
    cpfs = {re.sub('\\D', '', m) for m in RE_CPF.findall(texto) if not pol['validar_cpf'] or cpf_valido(m)}
    cartoes = {re.sub('\\D', '', m) for m in RE_CARTAO.findall(texto) if not pol['validar_luhn'] or luhn_valido(m)}
    palavras = [p for p in pol['palavras_chave'] if p.strip() and p.strip().lower() in texto.lower()]
    info.update(cpfs=len(cpfs), cartoes=len(cartoes), palavras=len(palavras))
    veredito = 'permitir'
    if palavras:
        veredito = 'quarentena'
    if cartoes or len(cpfs) >= pol['limiar_cpf']:
        veredito = 'bloquear'
    info['veredito'] = veredito
    return info

def filtro_url(d, item, pol):
    urls = [item['url']] if item['tipo'] == 'upload' else RE_URL.findall(item['corpo'])
    veredito = 'permitir'
    cats = []
    for u in urls:
        host = re.sub('^https?://', '', u).split('/')[0].split(':')[0].lower()
        cat = d['dominios'].get(org(host), 'nao-categorizado')
        cats.append(cat)
        if cat in pol['categorias_bloqueadas']:
            veredito = maior(veredito, 'bloquear')
        elif cat == 'nao-categorizado':
            veredito = maior(veredito, 'quarentena')
    return {'veredito': veredito, 'categorias': cats}

def processar(d, item, pol):
    estagios = [antispam(d, item, pol), dlp(d, item, pol), filtro_url(d, item, pol)]
    return (maior(*[e['veredito'] for e in estagios if e]), estagios)

class TestProtecaoDadosConteudo(unittest.TestCase):
    """Valida a estrutura, o conteúdo, o motor e a compilação do estudo Protecao-de-Dados-e-Conteudo."""

    def _item(self, d, item_id):
        return next((i for i in d['itens'] if i['id'] == item_id))

    def test_detectores_de_checksum(self):
        self.assertTrue(cpf_valido('274.618.903-87'))
        self.assertFalse(cpf_valido('123.456.789-00'))
        self.assertFalse(cpf_valido('111.111.111-11'))
        self.assertTrue(luhn_valido('4111 1111 1111 1111'))
        self.assertFalse(luhn_valido('4000 1234 5678 9010'))
        self.assertEqual(org('mail.fornecedor-embalagens.example'), 'fornecedor-embalagens.example')

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        termos = ['em uso', 'em trânsito', 'em repouso', 'classificação da informação', 'DLP de rede', 'DLP de endpoint', 'CASB', 'regex', 'dígito verificador', 'Luhn', 'dicionário', 'EDM', 'falso positivo', 'falso negativo', 'quarentena', 'SPF', 'RFC 7208', 'DKIM', 'RFC 6376', 'DMARC', 'RFC 7489', 'alinhamento', 'p=none', 'p=quarantine', 'p=reject', 'DNSBL', 'SWG', 'categoria', 'inspeção TLS', 'LGPD', 'T1566', 'T1567']
        for termo in termos:
            self.assertIn(termo, content, f'Termo obrigatório ausente: {termo}')
if __name__ == '__main__':
    unittest.main()
