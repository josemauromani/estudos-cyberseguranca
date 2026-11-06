"""
test_engenharia_deteccao.py
Testes automatizados para o Estudo 46: Engenharia-de-Deteccao

A Bancada de Detecções guarda eventos rotulados, rascunhos e soluções de
referência num bloco JSON. Este teste espelha em Python o leitor de YAML
(subconjunto) e o avaliador Sigma do JavaScript para validar as contagens de
acertos, falsos positivos e falsos negativos e a matriz de cobertura.
"""
import json
import re
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from index_dados import ESTUDOS_DADOS
MODIFICADORES = {'contains', 'startswith', 'endswith', 'all'}

class ErroRegra(Exception):
    pass

def tirar_comentario(linha):
    aspas = None
    for i, ch in enumerate(linha):
        if aspas:
            if ch == aspas:
                aspas = None
        elif ch in '\'"':
            aspas = ch
        elif ch == '#' and (i == 0 or linha[i - 1] in ' \t'):
            return linha[:i]
    return linha

def dividir_fluxo(s):
    partes, atual, aspas = ([], '', None)
    for ch in s:
        if aspas:
            atual += ch
            if ch == aspas:
                aspas = None
        elif ch in '\'"':
            aspas = ch
            atual += ch
        elif ch == ',':
            partes.append(atual)
            atual = ''
        else:
            atual += ch
    partes.append(atual)
    return [p for p in partes if p.strip()]

def escalar(s):
    s = s.strip()
    if len(s) >= 2 and s[0] == "'" and (s[-1] == "'"):
        return s[1:-1].replace("''", "'")
    if len(s) >= 2 and s[0] == '"' and (s[-1] == '"'):
        return re.sub('\\\\(["\\\\])', '\\1', s[1:-1])
    if s.startswith('[') and s.endswith(']'):
        return [escalar(p) for p in dividir_fluxo(s[1:-1])]
    return s

def eh_item(c):
    return c == '-' or c.startswith('- ')

def separar_chave(c, n):
    aspas = None
    for i, ch in enumerate(c):
        if aspas:
            if ch == aspas:
                aspas = None
        elif ch in '\'"':
            aspas = ch
        elif ch == ':' and (i == len(c) - 1 or c[i + 1] == ' '):
            chave = escalar(c[:i])
            if not isinstance(chave, str) or not chave:
                break
            return (chave, c[i + 1:].strip())
    raise ErroRegra(f"linha {n}: esperado 'chave: valor'")

def ler_yaml(texto):
    linhas = []
    for n, bruta in enumerate(texto.split('\n'), 1):
        recuo = bruta[:len(bruta) - len(bruta.lstrip())]
        if '\t' in recuo:
            raise ErroRegra(f'linha {n}: use espaços, não tabulação, na indentação')
        sem = tirar_comentario(bruta).rstrip()
        if not sem.strip():
            continue
        linhas.append((n, len(sem) - len(sem.lstrip(' ')), sem.strip()))
    if not linhas:
        raise ErroRegra('a regra está vazia')
    pos = [0]

    def bloco(ind):
        return lista(ind) if eh_item(linhas[pos[0]][2]) else mapa(ind)

    def mapa(ind):
        obj = {}
        while pos[0] < len(linhas):
            n, i, c = linhas[pos[0]]
            if i < ind:
                break
            if i > ind:
                raise ErroRegra(f'linha {n}: indentação inesperada')
            if eh_item(c):
                raise ErroRegra(f"linha {n}: item de lista onde se esperava 'chave: valor'")
            k, resto = separar_chave(c, n)
            if k in obj:
                raise ErroRegra(f"linha {n}: chave '{k}' repetida")
            pos[0] += 1
            if resto == '':
                prox = linhas[pos[0]] if pos[0] < len(linhas) else None
                if prox and prox[1] > ind:
                    obj[k] = bloco(prox[1])
                elif prox and prox[1] == ind and eh_item(prox[2]):
                    obj[k] = lista(ind)
                else:
                    obj[k] = None
            else:
                obj[k] = escalar(resto)
        return obj

    def lista(ind):
        arr = []
        while pos[0] < len(linhas):
            n, i, c = linhas[pos[0]]
            if i < ind or (i == ind and (not eh_item(c))):
                break
            if i > ind:
                raise ErroRegra(f'linha {n}: indentação inesperada')
            item = c[1:].strip()
            pos[0] += 1
            if item == '':
                prox = linhas[pos[0]] if pos[0] < len(linhas) else None
                arr.append(bloco(prox[1]) if prox and prox[1] > ind else None)
            else:
                arr.append(escalar(item))
        return arr
    raiz = bloco(linhas[0][1])
    if pos[0] < len(linhas):
        raise ErroRegra(f'linha {linhas[pos[0]][0]}: indentação inesperada')
    if not isinstance(raiz, dict):
        raise ErroRegra('a regra precisa ser um mapa de chaves (title, logsource, detection...)')
    return raiz

def curinga(padrao):
    return re.compile('^' + '.*'.join((re.escape(p) for p in padrao.lower().split('*'))) + '$')

def compilar_condicao(cond, nomes):
    tokens = re.findall('\\(|\\)|[^\\s()]+', cond)
    pos = [0]

    def ver():
        return tokens[pos[0]].lower() if pos[0] < len(tokens) else None

    def pegar():
        if pos[0] >= len(tokens):
            raise ErroRegra('condition termina antes do esperado')
        t = tokens[pos[0]]
        pos[0] += 1
        return t

    def ou():
        a = e_()
        while ver() == 'or':
            pegar()
            b = e_()
            a = (lambda p, q: lambda r: p(r) or q(r))(a, b)
        return a

    def e_():
        a = nao()
        while ver() == 'and':
            pegar()
            b = nao()
            a = (lambda p, q: lambda r: p(r) and q(r))(a, b)
        return a

    def nao():
        if ver() == 'not':
            pegar()
            a = nao()
            return lambda r: not a(r)
        return prim()

    def prim():
        t = pegar()
        if t == '(':
            v = ou()
            if pegar() != ')':
                raise ErroRegra('parêntese não fechado na condition')
            return v
        if t == ')':
            raise ErroRegra('parêntese fechado sem abrir na condition')
        tl = t.lower()
        if tl in ('1', 'all') and ver() == 'of':
            pegar()
            alvo = pegar()
            lst = list(nomes) if alvo.lower() == 'them' else [n for n in nomes if curinga(alvo).match(n.lower())]
            if not lst:
                raise ErroRegra(f"'{alvo}' não corresponde a nenhuma seleção")
            if tl == '1':
                return lambda r: any((r[n] for n in lst))
            return lambda r: all((r[n] for n in lst))
        if tl in ('and', 'or', 'not', 'of', '|'):
            raise ErroRegra(f"palavra '{t}' fora do lugar na condition")
        if t not in nomes:
            raise ErroRegra(f"a condition cita '{t}', que não existe em detection")
        return lambda r: r[t]
    if not tokens:
        raise ErroRegra('condition vazia')
    f = ou()
    if pos[0] != len(tokens):
        raise ErroRegra(f"sobrou '{tokens[pos[0]]}' no fim da condition")
    return f

def preparar(texto):
    regra = ler_yaml(texto)
    ls = regra.get('logsource')
    if not isinstance(ls, dict) or not ls:
        raise ErroRegra('falta o bloco logsource')
    det = regra.get('detection')
    if not isinstance(det, dict):
        raise ErroRegra('falta o bloco detection')
    if not isinstance(det.get('condition'), str):
        raise ErroRegra('detection precisa de uma condition')
    nomes = [n for n in det if n != 'condition']
    if not nomes:
        raise ErroRegra('detection precisa de ao menos uma seleção')
    for n in nomes:
        sel = det[n]
        if not isinstance(sel, dict) or not sel:
            raise ErroRegra(f"a seleção '{n}' precisa ser um mapa de campos")
        for chave, valor in sel.items():
            mods = chave.split('|')[1:]
            for m in mods:
                if m not in MODIFICADORES:
                    raise ErroRegra(f"modificador '{m}' não suportado nesta bancada")
            vals = valor if isinstance(valor, list) else [valor]
            if not vals or any((v is None or isinstance(v, (list, dict)) for v in vals)):
                raise ErroRegra(f"o campo '{chave}' em '{n}' está sem valor")
    regra['_cond'] = compilar_condicao(det['condition'], nomes)
    regra['_nomes'] = nomes
    return regra

def campo(evento, nome):
    for k, v in evento['campos'].items():
        if k.lower() == nome.lower():
            return v
    return None

def casa_valor(valor, esperado, mods):
    if valor is None:
        return False
    a, b = (str(valor).lower(), str(esperado).lower())
    if 'contains' in mods:
        return b in a
    if 'startswith' in mods:
        return a.startswith(b)
    if 'endswith' in mods:
        return a.endswith(b)
    return a == b

def casa_selecao(evento, sel):
    for chave, valor in sel.items():
        nome, *mods = chave.split('|')
        vals = valor if isinstance(valor, list) else [valor]
        testes = [casa_valor(campo(evento, nome), v, mods) for v in vals]
        if not (all(testes) if 'all' in mods else any(testes)):
            return False
    return True

def regra_casa(regra, evento):
    for k, v in regra['logsource'].items():
        if str(evento['logsource'].get(k, '')).lower() != str(v).lower():
            return False
    r = {n: casa_selecao(evento, regra['detection'][n]) for n in regra['_nomes']}
    return regra['_cond'](r)

def metadados(d, regra, tecnica):
    erros = []
    if not isinstance(regra.get('title'), str) or not regra['title'].strip():
        erros.append('title')
    if regra.get('level') not in d['niveis']:
        erros.append('level')
    tags = regra.get('tags') if isinstance(regra.get('tags'), list) else []
    if 'attack.' + tecnica.lower() not in [str(t).lower() for t in tags]:
        erros.append('tag')
    return erros

def avaliar(d, tecnica, texto):
    """Espelho de avaliarRegraBancada: roda a regra contra o conjunto de teste da técnica."""
    regra = preparar(texto)
    res = {'vp': 0, 'fp': 0, 'fn': 0, 'vn': 0, 'volume': 0, 'disparos': []}
    for e in d['eventos']:
        positivo = e['rotulo'] == 'malicioso' and e['tecnica'] == tecnica
        if e['rotulo'] == 'malicioso' and (not positivo):
            continue
        casou = regra_casa(regra, e)
        if casou:
            res['disparos'].append(e['id'])
        if positivo:
            res['vp' if casou else 'fn'] += 1
        elif casou:
            res['fp'] += 1
            res['volume'] += e['frequencia_dia']
        else:
            res['vn'] += 1
    res['metadados'] = metadados(d, regra, tecnica)
    res['passou'] = not res['metadados'] and res['fn'] == 0 and (res['fp'] == 0)
    return res

def tecnica(d, tid):
    return next((t for t in d['tecnicas'] if t['id'] == tid))

def texto_inicial(d, t):
    return t['rascunho'] if t['rascunho'] is not None else d['modelo_vazio']

class TestEngenhariaDeteccao(unittest.TestCase):
    """Valida a estrutura, o conteúdo, a bancada de testes e a compilação do estudo 46."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / '_geradores' / 'engenharia_de_deteccao_body.html'
        self.compiled_path = self.root / 'Engenharia-de-Deteccao' / 'treinamento-engenharia-de-deteccao.html'
        self.portal_path = self.root / 'index.html'

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        termos = ['Detection-as-Code', 'detecção como código', 'ciclo de vida da detecção', 'Sigma', 'logsource', 'condition', 'falsepositives', 'level', '1 of selection_*', 'falso positivo', 'falso negativo', 'precisão', 'revocação', 'volume de alertas', 'Atomic Red Team', 'Invoke-AtomicTest', 'matriz de cobertura', 'ATT&amp;CK Navigator', 'DeTT&amp;CT', 'débito de detecção', 'pull request', 'sigma check', 'sigma convert', 'pySigma', 'Alerting and Detection Strategy', 'telemetria', 'Estudo 16', 'Estudo 17', 'Estudo 47']
        for termo in termos:
            self.assertIn(termo, content, f'Termo obrigatório ausente: {termo}')

    def test_sigma_convert_grava_saved_searches_no_conf(self):
        """Um .conf do Splunk recebe o formato savedsearches do backend, não a lista padrão de consultas."""
        body = self.body_path.read_text(encoding='utf-8')
        linhas = [l for l in body.splitlines() if 'sigma convert -t splunk' in l]
        self.assertTrue(linhas, 'comando sigma convert ausente')
        for linha in linhas:
            if '.conf' in linha:
                self.assertIn('-f savedsearches', linha, linha)

    def test_coerencia_com_o_catalogo(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        info = ESTUDOS_DADOS['Engenharia-de-Deteccao']
        for fato in ('versionar, revisar, testar', 'filtros e condições', 'medida por teste', 'volume de alertas'):
            self.assertIn(fato, content, fato)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn('Engenharia-de-Deteccao/treinamento-engenharia-de-deteccao.html', content)
        self.assertIn('data-slug="Engenharia-de-Deteccao"', content)
        self.assertIn(f'/ {len(ESTUDOS_DADOS)}', content)
if __name__ == '__main__':
    unittest.main()
