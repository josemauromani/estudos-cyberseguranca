"""Migração dos corpos (_body.html) para o contrato de markup (spec §3.1 e §3.5).

Leva as três gerações de markup (G1 `fundamentos_ciber`, G2 com `header.study-header`
e `section-title-wrap`, G3 com `article.study-container` e `span.section-tag`) a um
markup único, sem alterar o texto didático. Cada transformação é uma edição pontual
sobre o texto do fonte, ancorada em tags localizadas pelo `html.parser` (via
`contrato._Arvore`); o restante do arquivo (indentação, comentários, scripts) fica
byte a byte igual. O script é idempotente: rodar de novo não muda nada.

Uso:
    python3 _geradores/migrar_markup.py --revisar [chave ...]   # só imprime
    python3 _geradores/migrar_markup.py --aplicar [chave ...]   # grava

`chave` é o nome do corpo sem o sufixo `_body.html` (ex.: `threat_hunting`).
"""
import argparse
import re
import sys
from collections import Counter
from html import escape
from html.parser import HTMLParser
from pathlib import Path

from contrato import TIPOS, VOID, _Arvore, extrair_secoes, validar_corpo

DIR = Path(__file__).resolve().parent
SUFIXO = "_body.html"

# (chave do corpo, id da seção) -> tipo. Correções manuais da classificação automática,
# registradas depois da conferência da tabela do --revisar.
EXCECOES: dict = {
    # Seções de teoria que usam .facts-grid para os conceitos (não são referências).
    ("fundamentos_ciber", "fundamentacao-teorica"): "teoria",
    ("seguranca_em_endpoints_edr", "telemetria"): "teoria",
}

CLASSES_SECAO = ("study-section", "content-section")
CLASSES_WRAPPER_TITULO = ("section-header", "section-title-wrap")
CLASSES_MARCADOR = ("section-tag", "section-num")
CLASSES_CABECALHO = ("study-header", "hero-header")
# Parágrafo introdutório do cabeçalho legado (texto didático): vai para a 1ª seção (R11).
CLASSES_LEAD_LEGADO = ("study-lead", "hero-subtitle")
# Widgets do checklist legado substituídos pelo cabeçalho "N de M" do base.js.
CLASSES_WIDGET_CHECKLIST = ("checklist-counter", "checklist-progress-bar")
CALLOUT_LEGADO = {
    "callout-tip": "tip",
    "callout-warning": "warning",
    "callout-danger": "danger",
    "callout-law": "law",
    "info": "key",
}
ROTULO_RESPOSTA = "Ver resposta explicada"
# Texto que a migração remove (ou acrescenta) de propósito e que não entra na conferência.
CLASSES_FORA_DO_TEXTO = CLASSES_MARCADOR + ("checklist-counter", "quiz-toggle")

_RE_CLASSE = re.compile(r"""(?<![\w-])class\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>]+)""")
_RE_MITRE = re.compile(r"\bTA?\d{4}(?:\.\d{3})?\b")
FUNCOES_NIST = ("Govern", "Identify", "Protect", "Detect", "Respond", "Recover")


# --------------------------------------------------------------------------
# Classificação (spec §3.5.1)
# --------------------------------------------------------------------------
class _Marcas(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.tags = set()
        self.classes = set()
        self.feed(html)
        self.close()

    def handle_starttag(self, tag, attrs):
        self.tags.add(tag)
        for k, v in attrs:
            if k == "class" and v:
                self.classes.update(v.split())


def classificar(secao_html: str, eh_ultima: bool) -> str:
    m = _Marcas(secao_html)
    if "checklist" in m.classes:
        return "checklist"
    if "quiz-item" in m.classes:
        return "questoes"
    if "facts-grid" in m.classes or (eh_ultima and m.tags & {"ul", "ol"}):
        return "referencias"
    return "teoria"


# --------------------------------------------------------------------------
# Edição do fonte
# --------------------------------------------------------------------------
def _aplicar(html, edicoes):
    """Aplica (inicio, fim, texto) sem sobreposição; inserções têm inicio == fim."""
    saida, pos = [], 0
    for ini, fim, texto in sorted(edicoes, key=lambda e: (e[0], e[1])):
        if ini < pos:
            raise ValueError(f"edições sobrepostas na posição {ini}")
        saida.append(html[pos:ini])
        saida.append(texto)
        pos = fim
    saida.append(html[pos:])
    return "".join(saida)


def _fim(html, no):
    """Offset logo após o fim do elemento (tag de fechamento incluída)."""
    if no.ini_fechamento is None:
        if no.tag in VOID:
            return no.fim_abertura
        raise ValueError(f"<{no.tag}> sem tag de fechamento")
    return html.index(">", no.ini_fechamento) + 1


def _abertura(html, no):
    return html[no.ini:no.fim_abertura]


def _inicio_linha(html, pos):
    return html.rfind("\n", 0, pos) + 1


def _indentacao(html, pos):
    a = _inicio_linha(html, pos)
    trecho = html[a:pos]
    return trecho if not trecho.strip() else ""


def _linhas(html, ini, fim):
    """Expande [ini, fim) para linhas inteiras quando só há espaço em volta."""
    a = _inicio_linha(html, ini)
    if html[a:ini].strip():
        a = ini
    b = html.find("\n", fim)
    b = len(html) if b < 0 else b + 1
    if html[fim:b].strip():
        b = fim
    return a, b


def _remocao(html, ini, fim):
    """Remove o trecho em linhas inteiras e uma linha em branco que sobraria dobrada."""
    a, b = _linhas(html, ini, fim)
    if a == _inicio_linha(html, a) and b > 0 and html[b - 1] == "\n":
        anterior_em_branco = a == 0 or not html[_inicio_linha(html, a - 1):a].strip()
        prox = html.find("\n", b)
        if anterior_em_branco and prox >= 0 and not html[b:prox].strip():
            b = prox + 1
    return (a, b, "")


def _substituicao_em_linhas(html, ini, fim, novo):
    """Troca o elemento [ini, fim) por `novo`, ocupando as mesmas linhas inteiras."""
    a, b = _linhas(html, ini, fim)
    prefixo = html[a:ini] if a < ini else ""
    sufixo = "\n" if b > fim and html[b - 1] == "\n" else ""
    return (a, b, prefixo + novo + sufixo)


def _comentarios_acima(html, a):
    """Recua o início de linha `a` sobre os comentários de uma linha logo acima."""
    while a > 0:
        p = _inicio_linha(html, a - 1)
        linha = html[p:a].strip()
        if not (linha.startswith("<!--") and linha.endswith("-->")):
            break
        a = p
    return a


def _com_classes(tag, classes):
    valor = f'class="{" ".join(classes)}"'
    m = _RE_CLASSE.search(tag)
    if m:
        return tag[:m.start()] + valor + tag[m.end():]
    m = re.match(r"<[\w-]+", tag)
    return tag[:m.end()] + " " + valor + tag[m.end():]


def _apos_classe(tag, atributo):
    m = _RE_CLASSE.search(tag)
    pos = m.end() if m else re.match(r"<[\w-]+", tag).end()
    return tag[:pos] + " " + atributo + tag[pos:]


def _retag(tag, de, para):
    if not tag.lower().startswith("<" + de):
        raise ValueError(f"esperado <{de}>, encontrado {tag[:30]!r}")
    return "<" + para + tag[len(de) + 1:]


def _atributos(attrs):
    return "".join(f" {k}" if v is None else f' {k}="{escape(v, quote=True)}"' for k, v in attrs)


def _nome(no):
    return no.tag + "".join("." + c for c in no.classes)


def _e_secao(no):
    return no.tag == "section" and any(no.tem_classe(c) for c in CLASSES_SECAO)


def _secoes_raiz(raiz):
    """Seções (study-section ou content-section) que não estão dentro de outra seção."""
    saida = []

    def visitar(no):
        for f in no.filhos:
            if _e_secao(f):
                saida.append(f)
            else:
                visitar(f)

    visitar(raiz)
    return saida


# --------------------------------------------------------------------------
# Passos da normalização (spec §3.5.3)
# --------------------------------------------------------------------------
def _insercao_lead(html, raiz, lead):
    """p.lead-text com o miolo do lead legado, logo após o h2 da 1ª seção."""
    secoes = _secoes_raiz(raiz)
    if not secoes:
        raise ValueError("lead do cabeçalho legado sem seção para recebê-lo")
    h2 = next((d for d in secoes[0].descendentes() if d.tag == "h2"), None)
    if h2 is None:
        raise ValueError(f"section#{secoes[0].get('id')} sem h2 para receber o lead")
    # Com invólucro de título (G2), o lead entra depois dele, que o passo seguinte reduz ao h2.
    ancora = h2.pai if any(h2.pai.tem_classe(c) for c in CLASSES_WRAPPER_TITULO) else h2
    pos = _fim(html, ancora)
    miolo = html[lead.fim_abertura:lead.ini_fechamento]
    return (pos, pos, f'\n\n{_indentacao(html, ancora.ini)}<p class="lead-text">{miolo}</p>')


def _passo_estrutura(html, chave):
    """Remove cabeçalhos legados (o lead vai para a 1ª seção) e garante o article na raiz."""
    raiz = _Arvore(html).raiz
    ed = []
    lead_movido = False
    for no in raiz.descendentes():
        if no.tag == "header" and any(no.tem_classe(c) for c in CLASSES_CABECALHO):
            a, b, _ = _remocao(html, no.ini, _fim(html, no))
            # O comentário que anuncia o cabeçalho sai junto com ele.
            ed.append((_comentarios_acima(html, a) if a == _inicio_linha(html, a) else a, b, ""))
            lead = next((d for d in no.descendentes() if d.tag == "p"
                         and any(d.tem_classe(c) for c in CLASSES_LEAD_LEGADO)), None)
            if lead is not None and not lead_movido:
                ed.append(_insercao_lead(html, raiz, lead))
                lead_movido = True
    tem_article = any(n.tag == "article" and n.tem_classe("study-container") for n in raiz.descendentes())
    if not tem_article:
        abertura = f'<article class="study-container" data-slug="{escape(chave.replace("_", "-"))}">'
        mains = [n for n in raiz.filhos if n.tag == "main" and n.tem_classe("container")]
        secoes = [n for n in raiz.filhos if _e_secao(n)]
        if mains:  # G1: main.container vira o article
            m = mains[0]
            ed.append((m.ini, m.fim_abertura, abertura))
            ed.append((m.ini_fechamento, _fim(html, m), "</article>"))
        elif secoes:  # G2: seções soltas na raiz são envolvidas
            # O article abre antes dos comentários de uma linha que anunciam a 1ª seção.
            a = _comentarios_acima(html, _inicio_linha(html, secoes[0].ini))
            ed.append((a, a, abertura + "\n"))
            fim = _fim(html, secoes[-1])
            ed.append((fim, fim, "\n</article>"))
    return _aplicar(html, ed)


def _tag_secao(no, tipo):
    sid = no.get("id")
    if not sid:
        raise ValueError(f"{_nome(no)} sem id")
    extras = [c for c in no.classes if c not in CLASSES_SECAO]
    if extras:
        raise ValueError(f"section#{sid} com classes extras: {' '.join(extras)}")
    outros = [(k, v) for k, v in no.attrs if k not in ("class", "id", "data-tipo")]
    return (f'<section class="study-section" id="{escape(sid, quote=True)}" '
            f'data-tipo="{tipo}"{_atributos(outros)}>')


def _passo_secoes(html, chave):
    """Tipa as seções (data-tipo após o id) e reduz o invólucro do título ao h2."""
    raiz = _Arvore(html).raiz
    secoes = _secoes_raiz(raiz)
    ed = []
    for i, s in enumerate(secoes):
        sid = s.get("id")
        atual = s.get("data-tipo")
        tipo = (EXCECOES.get((chave, sid))
                or (atual if atual in TIPOS else None)
                or classificar(html[s.ini:_fim(html, s)], i == len(secoes) - 1))
        nova = _tag_secao(s, tipo)
        if _abertura(html, s) != nova:
            ed.append((s.ini, s.fim_abertura, nova))
        for w in s.descendentes():
            if not any(w.tem_classe(c) for c in CLASSES_WRAPPER_TITULO):
                continue
            h2s = [f for f in w.filhos if f.tag == "h2"]
            outros = [f for f in w.filhos
                      if f.tag != "h2" and not any(f.tem_classe(c) for c in CLASSES_MARCADOR)]
            if len(h2s) != 1 or outros:
                raise ValueError(f"section#{sid}: {_nome(w)} com estrutura inesperada")
            h2 = h2s[0]
            ed.append(_substituicao_em_linhas(html, w.ini, _fim(html, w), html[h2.ini:_fim(html, h2)]))
    return _aplicar(html, ed)


def _e_item(no):
    return no.tem_classe("checklist-item") or no.tem_classe("check-item")


def _checkboxes(no):
    return [d for d in no.descendentes()
            if d.tag == "input" and (d.get("type") or "").lower() == "checkbox"]


def _item_conforme(it):
    if it.tag != "li" or not it.tem_classe("checklist-item"):
        return False
    caixas = _checkboxes(it)
    return (len(caixas) == 1 and caixas[0].get("id")
            and any(d.tag == "label" and d.get("for") == caixas[0].get("id") for d in it.descendentes()))


def _novo_item(html, it, id_padrao):
    """li.checklist-item > input[id] + label[for], com o texto do item intacto."""
    caixas = _checkboxes(it)
    if len(caixas) != 1:
        raise ValueError(f"{_nome(it)} com {len(caixas)} checkboxes")
    caixa = caixas[0]
    rotulo = it if it.tag == "label" else next((f for f in it.filhos if f.tag == "label"), None)
    if rotulo is None or caixa.pai is not rotulo:
        raise ValueError(f"{_nome(it)} com estrutura inesperada")
    enfeites = [f for f in rotulo.filhos if f.tag == "span" and f.tem_classe("check-box")]
    textos = [f for f in rotulo.filhos if f is not caixa and f not in enfeites]
    if len(textos) != 1 or textos[0].tag != "span":
        raise ValueError(f"{_nome(it)}: esperado um span de texto")
    texto = textos[0]
    sobra = html[rotulo.fim_abertura:rotulo.ini_fechamento]
    for f in sorted(rotulo.filhos, key=lambda n: -n.ini):
        sobra = sobra[:f.ini - rotulo.fim_abertura] + sobra[_fim(html, f) - rotulo.fim_abertura:]
    if sobra.strip() or any(html[e.fim_abertura:e.ini_fechamento].strip() for e in enfeites):
        raise ValueError(f"{_nome(it)}: texto fora do span")

    iid = caixa.get("id") or id_padrao
    tag_caixa = _abertura(html, caixa)
    if not caixa.get("id"):
        fecho = 2 if tag_caixa.endswith("/>") else 1
        tag_caixa = tag_caixa[:-fecho].rstrip() + f' id="{escape(iid, quote=True)}"' + tag_caixa[-fecho:]
    ind = _indentacao(html, it.ini)
    profundidade = 1 if rotulo is it else 2
    dif = len(_indentacao(html, caixa.ini)) - len(ind)
    passo = " " * (dif // profundidade if dif >= 2 * profundidade else 2)
    conteudo = html[texto.fim_abertura:texto.ini_fechamento]
    return (f'<li class="checklist-item">\n{ind}{passo}{tag_caixa}\n'
            f'{ind}{passo}<label for="{escape(iid, quote=True)}">{conteudo}</label>\n{ind}</li>')


def _passo_checklists(html):
    """Leva cada .checklist à forma ul.checklist > li.checklist-item > input[id] + label[for]."""
    raiz = _Arvore(html).raiz
    # Mesma ordem de document.querySelectorAll('.checklist') no base.js.
    listas = [n for n in raiz.descendentes() if n.tem_classe("checklist")]
    ed = []
    for idx, e in enumerate(listas):
        itens = [d for d in e.descendentes() if _e_item(d)]
        if not itens or (e.tag == "ul" and all(_item_conforme(i) for i in itens)):
            continue
        pais = {id(i.pai) for i in itens}
        if len(pais) != 1:
            raise ValueError(f"{_nome(e)}: itens em mais de um contêiner")
        pai = itens[0].pai
        # Ids gerados reproduzem a chave cs_check_<slug>_<listId>_<itemIdx> do base.js.
        list_id = e.get("data-checklist-id") or f"list_{idx}"
        for d in e.descendentes():
            if any(d.tem_classe(c) for c in CLASSES_WIDGET_CHECKLIST):
                ed.append(_remocao(html, d.ini, _fim(html, d)))
        for j, it in enumerate(itens):
            if not _item_conforme(it):
                ed.append((it.ini, _fim(html, it), _novo_item(html, it, f"{list_id}_{j}")))
        if e.tag == "ul":
            continue
        if e.tag != "div":
            raise ValueError(f"{_nome(e)} inesperado")
        atributos_e = [(k, v) for k, v in e.attrs if k != "class"]
        filhos = [f for f in e.filhos if not any(f.tem_classe(c) for c in CLASSES_WIDGET_CHECKLIST)]
        if pai is e and all(_e_item(f) for f in filhos):
            # div.checklist só com itens: vira ul.checklist com os mesmos atributos.
            ed.append((e.ini, e.fim_abertura, _retag(_abertura(html, e), "div", "ul")))
            ed.append((e.ini_fechamento, _fim(html, e), "</ul>"))
            continue
        # Invólucro com título/barra: sai o div, a lista vira (ou ganha) o ul.checklist.
        a, b = _linhas(html, e.ini, e.fim_abertura)
        ed.append((a, b, ""))
        a, b = _linhas(html, e.ini_fechamento, _fim(html, e))
        ed.append((a, b, ""))
        if pai is e:
            posicoes = [e.filhos.index(i) for i in itens]
            if posicoes != list(range(posicoes[0], posicoes[0] + len(itens))):
                raise ValueError(f"{_nome(e)}: itens não contíguos")
            ind = _indentacao(html, itens[0].ini)
            ini_linha = _inicio_linha(html, itens[0].ini) if ind else itens[0].ini
            ed.append((ini_linha, ini_linha, f'{ind}<ul class="checklist"{_atributos(atributos_e)}>\n'))
            fim = _fim(html, itens[-1])
            ed.append((fim, fim, f"\n{ind}</ul>"))
        elif pai.tag == "ul":
            outros = [(k, v) for k, v in pai.attrs if k != "class"]
            ed.append((pai.ini, pai.fim_abertura,
                       f'<ul class="checklist"{_atributos(outros + atributos_e)}>'))
        else:
            raise ValueError(f"{_nome(e)}: itens dentro de {_nome(pai)}")
    return _aplicar(html, ed)


def _passo_questoes(html):
    """Múltipla escolha ganha data-formato; respostas viram details.quiz-details."""
    raiz = _Arvore(html).raiz
    ed = []
    for q in raiz.descendentes():
        if not q.tem_classe("quiz-item"):
            continue
        desc = list(q.descendentes())
        if any(d.tag == "button" and d.tem_classe("quiz-btn") for d in desc):
            if q.get("data-formato") is None:
                ed.append((q.ini, q.fim_abertura, _apos_classe(_abertura(html, q), 'data-formato="multipla"')))
            continue
        if q.tag == "details":
            # details.quiz-item > summary.quiz-summary (enunciado) + .quiz-answer
            resumos = [f for f in q.filhos if f.tag == "summary"]
            respostas = [f for f in q.filhos if f.tem_classe("quiz-answer")]
            if len(resumos) != 1 or len(respostas) != 1:
                raise ValueError(f"{_nome(q)} com estrutura inesperada")
            ed.append((q.ini, q.fim_abertura, _retag(_abertura(html, q), "details", "div")))
            ed.append((q.ini_fechamento, _fim(html, q), "</div>"))
            s = resumos[0]
            ed.append((s.ini, s.fim_abertura, _retag(_abertura(html, s), "summary", "div")))
            ed.append((s.ini_fechamento, _fim(html, s), "</div>"))
            r = respostas[0]
            ind = _indentacao(html, r.ini)
            pos = _inicio_linha(html, r.ini) if ind else r.ini
            ed.append((pos, pos, f'{ind}<details class="quiz-details">\n'
                                 f'{ind}  <summary class="quiz-toggle">{ROTULO_RESPOSTA}</summary>\n'))
            fim = _fim(html, r)
            ed.append((fim, fim, f"\n{ind}</details>"))
            continue
        detalhes = [d for d in desc if d.tag == "details"]
        if any(d.tem_classe("quiz-details") for d in detalhes):
            continue
        alvo = [d for d in detalhes if d.tem_classe("quiz-answer")]
        if len(alvo) != 1:
            continue  # o validador relata
        d = alvo[0]
        # quiz-item > .quiz-question + details.quiz-answer > summary + .quiz-explanation
        ed.append((d.ini, d.fim_abertura,
                   _com_classes(_abertura(html, d), ["quiz-details" if c == "quiz-answer" else c
                                                     for c in d.classes])))
        resumo = next((f for f in d.filhos if f.tag == "summary"), None)
        if resumo is not None and not resumo.tem_classe("quiz-toggle"):
            ed.append((resumo.ini, resumo.fim_abertura,
                       _com_classes(_abertura(html, resumo), resumo.classes + ["quiz-toggle"])))
        if not any(f.tem_classe("quiz-answer") for f in d.filhos):
            expl = [f for f in d.filhos if f.tem_classe("quiz-explanation")]
            if len(expl) == 1:
                x = expl[0]
                ed.append((x.ini, x.fim_abertura,
                           _com_classes(_abertura(html, x), ["quiz-answer" if c == "quiz-explanation" else c
                                                             for c in x.classes])))
    return _aplicar(html, ed)


def _passo_callouts_e_marcadores(html):
    raiz = _Arvore(html).raiz
    ed = []
    for no in raiz.descendentes():
        if no.tem_classe("callout"):
            novas = [CALLOUT_LEGADO.get(c, c) for c in no.classes]
            if novas != no.classes:
                ed.append((no.ini, no.fim_abertura, _com_classes(_abertura(html, no), novas)))
        elif any(no.tem_classe(c) for c in CLASSES_MARCADOR):
            ed.append(_remocao(html, no.ini, _fim(html, no)))
    return _aplicar(html, ed)


def migrar(html: str, chave: str) -> str:
    html = _passo_estrutura(html, chave)
    html = _passo_secoes(html, chave)
    html = _passo_checklists(html)
    html = _passo_questoes(html)
    return _passo_callouts_e_marcadores(html)


# --------------------------------------------------------------------------
# Conferência do texto e dos cabeçalhos
# --------------------------------------------------------------------------
class _NoT:
    def __init__(self, tag, attrs, pai):
        self.tag = tag
        self.classes = set()
        for k, v in attrs:
            if k == "class" and v:
                self.classes = set(v.split())
        self.pai = pai
        self.filhos = []


class _ArvoreTexto(HTMLParser):
    """Árvore com nós de texto (entidades já convertidas)."""

    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.raiz = _NoT("#raiz", [], None)
        self.pilha = [self.raiz]
        self.feed(html)
        self.close()

    def handle_starttag(self, tag, attrs):
        no = _NoT(tag, attrs, self.pilha[-1])
        self.pilha[-1].filhos.append(no)
        if tag not in VOID:
            self.pilha.append(no)

    def handle_startendtag(self, tag, attrs):
        self.pilha[-1].filhos.append(_NoT(tag, attrs, self.pilha[-1]))

    def handle_endtag(self, tag):
        for i in range(len(self.pilha) - 1, 0, -1):
            if self.pilha[i].tag == tag:
                del self.pilha[i:]
                return

    def handle_data(self, data):
        self.pilha[-1].filhos.append(data)


def _fora_do_texto(no):
    if no.tag in ("script", "style") or no.classes & set(CLASSES_FORA_DO_TEXTO):
        return True
    # Rótulo do botão da resposta no G2 (details.quiz-answer > summary).
    return no.tag == "summary" and no.pai.tag == "details" and "quiz-answer" in no.pai.classes


def _texto(no, pular=_fora_do_texto):
    partes = []

    def coletar(n):
        for f in n.filhos:
            if isinstance(f, str):
                partes.append(f)
            elif not pular(f):
                coletar(f)

    coletar(no)
    return " ".join(" ".join(partes).split())


def _lead_legado(raiz):
    """Texto normalizado do lead do cabeçalho legado, ou ""."""
    for cab in _descendentes(raiz):
        if cab.tag == "header" and cab.classes & set(CLASSES_CABECALHO):
            for d in _descendentes(cab):
                if d.tag == "p" and d.classes & set(CLASSES_LEAD_LEGADO):
                    return _texto(d)
    return ""


def texto_visivel(html: str) -> list:
    """Texto de cada seção. Num corpo legado, o lead do cabeçalho conta como o texto logo
    após o h2 da 1ª seção, que é onde a migração o põe (R11)."""
    raiz = _ArvoreTexto(html).raiz
    lead = _lead_legado(raiz)
    saida = []

    def achar(no):
        for f in no.filhos:
            if isinstance(f, str):
                continue
            if f.tag == "section" and f.classes & set(CLASSES_SECAO):
                if lead and not saida:
                    h2 = next((d for d in _descendentes(f) if d.tag == "h2"), None)
                    titulo = _texto(h2) if h2 is not None else ""
                    resto = _texto(f, pular=lambda n: n is h2 or _fora_do_texto(n))
                    saida.append(" ".join(t for t in (titulo, lead, resto) if t))
                else:
                    saida.append(_texto(f))
            else:
                achar(f)

    achar(raiz)
    return saida


def _descendentes(no):
    for f in no.filhos:
        if not isinstance(f, str):
            yield f
            yield from _descendentes(f)


def cabecalho_legado(html: str) -> dict:
    raiz = _ArvoreTexto(html).raiz
    cab = next((n for n in _descendentes(raiz)
                if n.tag == "header" and n.classes & set(CLASSES_CABECALHO)), None)
    if cab is None:
        return {}

    def primeiro(pred):
        return next((n for n in _descendentes(cab) if pred(n)), None)

    def txt(no):
        return _texto(no, pular=lambda n: n.tag in ("script", "style")) if no is not None else ""

    kicker = primeiro(lambda n: "study-track-kicker" in n.classes
                      or (n.tag == "div" and "badge" in n.classes))
    badges = [n for n in _descendentes(cab)
              if n is not kicker and n.classes & {"badge", "meta-item"}]
    return {
        "kicker": txt(kicker),
        "titulo": txt(primeiro(lambda n: n.tag == "h1")),
        "subtitulo": txt(primeiro(lambda n: n.classes & {"study-lead", "hero-subtitle"})),
        "badges": " | ".join(txt(b) for b in badges),
    }


def divergencias_cabecalho(cab: dict, dados: dict) -> list:
    """Dados do cabeçalho legado que não batem com ESTUDOS_DADOS[slug]."""
    saida = []
    for campo in ("titulo", "subtitulo"):
        if cab.get(campo) and cab[campo] != dados.get(campo, ""):
            saida.append(f"{campo}: cabeçalho «{cab[campo]}» ≠ ESTUDOS_DADOS «{dados.get(campo, '')}»")
    badges = cab.get("badges", "")
    mitre = str(dados.get("mitre", ""))
    faltam = [c for c in dict.fromkeys(_RE_MITRE.findall(badges)) if c not in mitre]
    if faltam:
        saida.append(f"mitre: só no cabeçalho: {', '.join(faltam)} (ESTUDOS_DADOS «{mitre}»)")
    m = re.search(r"Tempo[^|]*?(\d+)\s*min", badges)
    if m and int(m.group(1)) != dados.get("tempo_minutos"):
        saida.append(f"tempo: cabeçalho {m.group(1)} min ≠ ESTUDOS_DADOS {dados.get('tempo_minutos')} min")
    nist_cab = next((p for p in badges.split(" | ") if "NIST" in p), "")
    nist = str(dados.get("nist", ""))
    faltam = [f for f in FUNCOES_NIST if f in nist_cab and f not in nist]
    if faltam:
        saida.append(f"nist: só no cabeçalho: {', '.join(faltam)} (ESTUDOS_DADOS «{nist}»)")
    return saida


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def _corpos(chaves):
    corpos = sorted(DIR.glob("*" + SUFIXO))
    if chaves:
        corpos = [p for p in corpos if p.name[:-len(SUFIXO)] in chaves]
    return corpos


def _dados_do_corpo(chave):
    from index_dados import ESTUDOS_DADOS
    from montar import encontrar_estudo_por_slug_ou_arquivo
    estudo = encontrar_estudo_por_slug_ou_arquivo(chave + SUFIXO)
    return ESTUDOS_DADOS.get(estudo["slug"]) if estudo else None


def _problemas(antes, depois, chave):
    problemas = []
    if texto_visivel(antes) != texto_visivel(depois):
        problemas.append(f"{chave}: texto visível das seções mudaria")
    lead = cabecalho_legado(antes).get("subtitulo")
    if lead:
        secoes = extrair_secoes(depois)
        textos = texto_visivel(depois)
        titulo = _texto(_ArvoreTexto(secoes[0].titulo_html).raiz) if secoes else ""
        if not textos or not textos[0].startswith(f"{titulo} {lead}"):
            problemas.append(f"{chave}: lead do cabeçalho legado ausente logo após o h2 da 1ª seção")
    problemas.extend(validar_corpo(depois, chave))
    return problemas


def revisar(chaves=()):
    totais = Counter()
    divergencias, pendencias = [], []
    for p in _corpos(chaves):
        chave = p.name[:-len(SUFIXO)]
        html = p.read_text(encoding="utf-8")
        try:
            novo = migrar(html, chave)
        except ValueError as e:
            pendencias.append(f"{chave}: migração impossível: {e}")
            continue
        for s in extrair_secoes(novo):
            totais[s.tipo] += 1
            titulo = _texto(_ArvoreTexto(s.titulo_html).raiz)
            print(f"{chave} | {s.id} | {s.tipo} | {titulo}")
        cab = cabecalho_legado(html)
        if cab:
            dados = _dados_do_corpo(chave)
            if dados is None:
                divergencias.append(f"{chave}: sem entrada em ESTUDOS_DADOS")
            else:
                divergencias.extend(f"{chave}: {d}" for d in divergencias_cabecalho(cab, dados))
        pendencias.extend(_problemas(html, novo, chave))
    print("\n== Seções por tipo ==")
    for t in TIPOS:
        print(f"{t}: {totais[t]}")
    print("\n== Divergências de cabeçalho (corrigir em index_dados.py) ==")
    print("\n".join(divergencias) or "nenhuma")
    print("\n== Pendências (impedem --aplicar) ==")
    print("\n".join(pendencias) or "nenhuma")
    return 0


def aplicar(chaves=()):
    falhou = False
    for p in _corpos(chaves):
        chave = p.name[:-len(SUFIXO)]
        html = p.read_text(encoding="utf-8")
        try:
            novo = migrar(html, chave)
        except ValueError as e:
            print(f"{chave}: migração impossível: {e}", file=sys.stderr)
            falhou = True
            continue
        if novo == html:
            continue
        problemas = _problemas(html, novo, chave)
        if problemas:
            print("\n".join(problemas), file=sys.stderr)
            print(f"{chave}: não gravado", file=sys.stderr)
            falhou = True
            continue
        p.write_text(novo, encoding="utf-8")
        print(f"{chave}: migrado")
    return 1 if falhou else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Migra os corpos _body.html para o contrato de markup.")
    modo = ap.add_mutually_exclusive_group(required=True)
    modo.add_argument("--revisar", action="store_true", help="imprime a tabela e as pendências, sem gravar")
    modo.add_argument("--aplicar", action="store_true", help="grava os corpos migrados")
    ap.add_argument("chaves", nargs="*", help="corpos a processar (nome sem _body.html); padrão: todos")
    args = ap.parse_args(argv)
    return revisar(args.chaves) if args.revisar else aplicar(args.chaves)


if __name__ == "__main__":
    sys.exit(main())
