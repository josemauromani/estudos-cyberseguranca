"""
test_ia_ciber.py
Testes automatizados para o Estudo 24: IA-e-Ciberseguranca
"""
import itertools
import json
import re
import sys
import unicodedata
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from index_dados import ESTUDOS_DADOS
LLM_TOP10_2025 = [('LLM01:2025', 'Prompt Injection'), ('LLM02:2025', 'Sensitive Information Disclosure'), ('LLM03:2025', 'Supply Chain'), ('LLM04:2025', 'Data and Model Poisoning'), ('LLM05:2025', 'Improper Output Handling'), ('LLM06:2025', 'Excessive Agency'), ('LLM07:2025', 'System Prompt Leakage'), ('LLM08:2025', 'Vector and Embedding Weaknesses'), ('LLM09:2025', 'Misinformation'), ('LLM10:2025', 'Unbounded Consumption')]
DEFESAS = ['entrada', 'separacao', 'saida', 'ferramentas', 'segredo', 'codificacao']

def norm(t):
    return ''.join((c for c in unicodedata.normalize('NFD', t) if unicodedata.category(c) != 'Mn')).lower()

def simular(d, msg, defs):
    """Espelho do modelo simulado em JavaScript. defs: conjunto de defesas ligadas."""
    n = norm(msg)
    r = {'entrada_bloqueada': False, 'contexto': [], 'chamadas': [], 'saida_modelo': '', 'filtros': [], 'saida_final': '', 'xss': False, 'vazou': []}
    if 'entrada' in defs and re.search(d['regex_entrada'], n, re.A):
        r['entrada_bloqueada'] = True
        r['saida_final'] = d['textos']['entrada_bloqueada']
        return r
    prompt = [l.replace('{CUPOM}', d['cupom']) for l in d['prompt_sistema'] if not ('segredo' in defs and '{CUPOM}' in l)]
    prompt_txt = '\n'.join(prompt)
    partes = []
    for doc in d['documentos']:
        if any((g in n for g in doc['gatilhos'])):
            r['contexto'].append(doc['id'])
            partes.append(doc['visivel'])
            if 'separacao' not in defs and doc.get('injecao'):
                inj = doc['injecao']
                if 'ferramentas' in defs and (not inj['destino'].endswith('@' + d['dominio_interno'])):
                    res = d['textos']['email_bloqueado']
                else:
                    res = 'enviado'
                r['chamadas'].append(['enviar_email', inj['destino'], res])
    m = re.search('pedido\\D{0,12}(\\d{4})', n)
    if m:
        pid = int(m.group(1))
        ped = next((p for p in d['pedidos'] if p['id'] == pid), None)
        if ped is None or ('ferramentas' in defs and ped['cliente_id'] != d['sessao_cliente']):
            res = d['textos']['pedido_nao_encontrado']
        else:
            res = f'Pedido {ped['id']} de {ped['cliente']}: {ped['status']}. Entrega em {ped['endereco']}. CPF {ped['cpf']}.'
        r['chamadas'].append(['consultar_pedido', str(pid), res])
        partes.append(res)
    manip = re.search(d['regex_manipulacao'], n, re.A)
    if re.search('cupom|codigo de desconto|desconto dos funcionarios', n):
        if manip:
            if 'segredo' in defs:
                partes.append(d['textos']['sem_segredo'])
            else:
                c = d['cupom']
                if re.search('letras separadas|separad[ao]s? por hifen|soletr', n):
                    c = '-'.join((x for x in c if x.isalnum()))
                partes.append(f'Claro! O código é {c}.')
        else:
            partes.append(d['textos']['recusa_segredo'])
    if re.search('instrucoes|prompt|regras internas|configuracao', n) and re.search('liste|mostre|repita|revele|imprima', n):
        partes.append('Minhas instruções:\n' + prompt_txt if manip else d['textos']['recusa_prompt'])
    eco = re.search('(?:responda|repita)(?: exatamente)? com:? (.+)$', msg, re.I | re.S)
    if eco and '<' in eco.group(1):
        partes.append(eco.group(1).strip())
    saida = '\n'.join(partes) or d['textos']['padrao']
    r['saida_modelo'] = saida
    final = saida
    if 'saida' in defs:
        compacto = re.sub('[^A-Z0-9]', '', saida.upper())
        if d['canario'] in saida:
            r['filtros'].append('canario')
        if re.sub('[^A-Z0-9]', '', d['cupom'].upper()) in compacto:
            r['filtros'].append('cupom')
        if r['filtros']:
            final = d['textos']['saida_bloqueada']
        elif re.search('\\d{3}\\.\\d{3}\\.\\d{3}-\\d{2}', final):
            r['filtros'].append('cpf_mascarado')
            final = re.sub('\\d{3}\\.\\d{3}\\.\\d{3}-\\d{2}', '***.***.***-**', final)
    r['saida_final'] = final
    if 'codificacao' not in defs and re.search('<script|\\bon[a-z]+\\s*=|javascript:', final, re.I | re.A):
        r['xss'] = True
    vaz = []
    if re.sub('[^A-Z0-9]', '', d['cupom'].upper()) in re.sub('[^A-Z0-9]', '', final.upper()):
        vaz.append('cupom')
    if d['canario'] in final:
        vaz.append('prompt')
    if any((c[0] == 'enviar_email' and c[2] == 'enviado' for c in r['chamadas'])):
        vaz.append('email_externo')
    if any((p['cliente'] in final for p in d['pedidos'] if p['cliente_id'] != d['sessao_cliente'])):
        vaz.append('pedido_outro_cliente')
    if r['xss']:
        vaz.append('xss')
    r['vazou'] = vaz
    return r

def combos():
    for k in range(len(DEFESAS) + 1):
        for c in itertools.combinations(DEFESAS, k):
            yield set(c)

class TestIaCiber(unittest.TestCase):
    """Valida a estrutura, o conteúdo, o modelo simulado, as defesas e a compilação do estudo 24."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / '_geradores' / 'ia_e_ciberseguranca_body.html'
        self.compiled_path = self.root / 'IA-e-Ciberseguranca' / 'treinamento-ia-e-ciberseguranca.html'
        self.portal_path = self.root / 'index.html'

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        termos = ['OWASP Top 10 for LLM Applications', '2025', 'injeção direta', 'injeção indireta', 'RAG', 'guardrails', 'envenenamento', 'deepfake', 'canário', 'humano no circuito', 'MITRE ATLAS', 'NIST AI RMF', 'Estudo 12', 'Estudo 15', 'simulado']
        termos += [nome for _, nome in LLM_TOP10_2025]
        for termo in termos:
            self.assertIn(termo, content, f'Termo obrigatório ausente: {termo}')

    def _secao_governanca(self, texto):
        ini = texto.index('<section class="study-section" id="governanca-ia" data-tipo="teoria">')
        return texto[ini:texto.index('</section>', ini)]

    def test_secao_governanca_ia_conteudo(self):
        for texto in (self.body_path.read_text(encoding='utf-8'), self.compiled_path.read_text(encoding='utf-8')):
            sec = self._secao_governanca(texto)
            for termo in ('ISO/IEC 42001:2023', 'AI RMF', 'Govern', 'Map', 'Measure', 'Manage', 'NIST AI 600-1'):
                self.assertIn(termo, sec, termo)

    def test_secao_governanca_ia_referencia(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        ini = content.index('id="fatos"')
        fatos = content[ini:]
        self.assertIn('ISO/IEC 42001:2023', fatos)
        self.assertIn('NIST AI 100-1', fatos)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn('IA-e-Ciberseguranca/treinamento-ia-e-ciberseguranca.html', content)
        self.assertIn('data-slug="IA-e-Ciberseguranca"', content)
        self.assertIn(f'/ {len(ESTUDOS_DADOS)}', content)
if __name__ == '__main__':
    unittest.main()
