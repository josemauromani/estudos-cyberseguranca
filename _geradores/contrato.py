"""Validador do contrato de markup dos corpos (_body.html) e extrator de seções.

Regras (spec §3.1): as mensagens têm o formato "<slug> §<n>: <onde>: <descrição>".
"""
from dataclasses import dataclass
from html.parser import HTMLParser

TIPOS = ("teoria", "laboratorio", "checklist", "questoes", "referencias")

ROTULOS = {
    "teoria": ("📘", "Teoria"),
    "laboratorio": ("🧪", "Laboratório"),
    "checklist": ("☑️", "Checklist"),
    "questoes": ("❓", "Questões de concurso"),
    "referencias": ("📚", "Referências"),
}

MODIFICADORES_CALLOUT = ("tip", "warning", "danger", "law", "key")
CLASSES_PROIBIDAS = ("study-header", "hero-header", "section-tag", "section-num")
ORDEM_ATRIBUTOS_SECAO = ["class", "id", "data-tipo"]
TITULOS = ("h1", "h2", "h3", "h4", "h5", "h6")
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}


@dataclass(frozen=True)
class Secao:
    id: str
    tipo: str
    titulo_html: str
    n_checklist: int
    n_questoes: int


class ContratoInvalido(Exception):
    def __init__(self, erros):
        self.erros = list(erros)
        super().__init__("\n".join(self.erros))


class _No:
    def __init__(self, tag, attrs, pai, ini=0, fim_abertura=0):
        self.tag = tag
        self.attrs = attrs  # lista ordenada de (nome, valor)
        self.pai = pai
        self.filhos = []
        self.ini = ini
        self.fim_abertura = fim_abertura  # offset logo após o '>' da abertura
        self.ini_fechamento = None  # offset do '<' da tag de fechamento

    def get(self, nome, padrao=None):
        for k, v in self.attrs:
            if k == nome:
                return v if v is not None else ""
        return padrao

    @property
    def classes(self):
        return (self.get("class") or "").split()

    def tem_classe(self, c):
        return c in self.classes

    def descendentes(self):
        for f in self.filhos:
            yield f
            yield from f.descendentes()


class _Arvore(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.raiz = _No("#raiz", [], None)
        self.pilha = [self.raiz]
        self._linhas = [0]
        for i, ch in enumerate(html):
            if ch == "\n":
                self._linhas.append(i + 1)
        self.feed(html)
        self.close()

    def _offset(self):
        linha, col = self.getpos()
        return self._linhas[linha - 1] + col

    def _abrir(self, tag, attrs):
        ini = self._offset()
        no = _No(tag, attrs, self.pilha[-1], ini, ini + len(self.get_starttag_text()))
        self.pilha[-1].filhos.append(no)
        return no

    def handle_starttag(self, tag, attrs):
        no = self._abrir(tag, attrs)
        if tag not in VOID:
            self.pilha.append(no)

    def handle_startendtag(self, tag, attrs):
        self._abrir(tag, attrs)

    def handle_endtag(self, tag):
        for i in range(len(self.pilha) - 1, 0, -1):
            if self.pilha[i].tag == tag:
                self.pilha[i].ini_fechamento = self._offset()
                del self.pilha[i:]
                return


def _secoes_de_primeiro_nivel(raiz):
    """Pares (article, [section.study-section filhas diretas])."""
    resultado = []
    for no in raiz.descendentes():
        if no.tag == "article" and no.tem_classe("study-container"):
            resultado.append(no)
    return resultado


def _e_secao(no):
    return no.tag == "section" and no.tem_classe("study-section")


def _primeiro_h2(secao):
    for d in secao.descendentes():
        if d.tag == "h2":
            return d
    return None


def _contar(secao, pred):
    return sum(1 for d in secao.descendentes() if pred(d))


def _e_item_checklist(n):
    return n.tag == "li" and n.tem_classe("checklist-item")


def _e_quiz_item(n):
    return n.tem_classe("quiz-item")


def extrair_secoes(html):
    arvore = _Arvore(html)
    secoes = []
    for article in _secoes_de_primeiro_nivel(arvore.raiz):
        for filho in article.filhos:
            if not _e_secao(filho):
                continue
            h2 = _primeiro_h2(filho)
            if h2 is not None and h2.ini_fechamento is not None:
                titulo = html[h2.fim_abertura:h2.ini_fechamento]
            else:
                titulo = ""
            secoes.append(Secao(
                id=filho.get("id", ""),
                tipo=filho.get("data-tipo", ""),
                titulo_html=titulo,
                n_checklist=_contar(filho, _e_item_checklist),
                n_questoes=_contar(filho, _e_quiz_item),
            ))
    return secoes


def _onde(no):
    """Seção que contém o nó, no formato 'section#id', ou 'corpo'."""
    p = no
    while p is not None:
        if _e_secao(p):
            sid = p.get("id")
            return f"section#{sid}" if sid else "section (sem id)"
        p = p.pai
    return "corpo"


def _nome(no):
    cls = ".".join(no.classes)
    return f"{no.tag}.{cls}" if cls else no.tag


def validar_corpo(html, slug):
    arvore = _Arvore(html)
    raiz = arvore.raiz
    erros = []

    def erro(regra, onde, descricao):
        erros.append(f"{slug} §{regra}: {onde}: {descricao}")

    # §1
    articles = _secoes_de_primeiro_nivel(raiz)
    if len(articles) != 1:
        erro(1, "corpo", f"esperado exatamente um article.study-container, encontrado {len(articles)}")
    for a in articles:
        if a.pai is not raiz:
            erro(1, "corpo", "article.study-container deve estar na raiz do corpo")

    # §2, §3
    secoes = []
    ids_vistos = set()
    for article in articles:
        for filho in article.filhos:
            if filho.tag in ("script", "style"):
                continue
            if not _e_secao(filho):
                erro(2, "article.study-container",
                     f"filho {_nome(filho)} não é section.study-section")
                continue
            secoes.append(filho)
    for s in secoes:
        sid = s.get("id")
        onde = _onde(s)
        if not sid:
            erro(2, onde, "id ausente")
        elif sid in ids_vistos:
            erro(2, onde, "id duplicado")
        else:
            ids_vistos.add(sid)
        tipo = s.get("data-tipo")
        if tipo is None:
            erro(2, onde, "data-tipo ausente")
        elif tipo not in TIPOS:
            erro(2, onde, f'data-tipo "{tipo}" inválido')
        nomes = [k for k, _ in s.attrs if k in ORDEM_ATRIBUTOS_SECAO]
        if nomes != ORDEM_ATRIBUTOS_SECAO and set(nomes) == set(ORDEM_ATRIBUTOS_SECAO):
            erro(2, onde, "ordem dos atributos deve ser class, id, data-tipo")
        titulos = [d for d in s.descendentes() if d.tag in TITULOS]
        if _primeiro_h2(s) is None:
            erro(3, onde, "sem h2")
        elif titulos[0].tag != "h2":
            erro(3, onde, f"primeiro título é {titulos[0].tag}, deveria ser h2")

    # §4
    for d in raiz.descendentes():
        if d.tag == "footer":
            erro(4, _onde(d), "elemento proibido footer (o chassi gera)")
            continue
        for c in CLASSES_PROIBIDAS:
            if d.tem_classe(c):
                erro(4, _onde(d), f"elemento proibido {_nome(d)} (o chassi gera)")
                break

    # §5
    presentes = {s.get("data-tipo") for s in secoes}
    for t in ("laboratorio", "checklist", "questoes", "referencias"):
        if t not in presentes:
            erro(5, "corpo", f'falta seção do tipo "{t}"')

    # §6
    for d in raiz.descendentes():
        if d.tag == "ul" and d.tem_classe("checklist"):
            for f in d.filhos:
                if f.tag != "li" or not f.tem_classe("checklist-item"):
                    erro(6, _onde(d), f"filho {_nome(f)} de ul.checklist não é li.checklist-item")
        elif _e_item_checklist(d):
            if d.pai is None or d.pai.tag != "ul" or not d.pai.tem_classe("checklist"):
                erro(6, _onde(d), "li.checklist-item fora de ul.checklist")
            inputs = [x for x in d.descendentes()
                      if x.tag == "input" and (x.get("type") or "").lower() == "checkbox"]
            if not inputs:
                erro(6, _onde(d), "li.checklist-item sem input[type=checkbox]")
                continue
            for i in inputs:
                iid = i.get("id")
                if not iid:
                    erro(6, _onde(d), "input[type=checkbox] sem id")
                elif not any(x.tag == "label" and x.get("for") == iid for x in d.descendentes()):
                    erro(6, _onde(d), f'li.checklist-item sem label[for="{iid}"]')

    # §7
    n_quiz = 0
    for d in raiz.descendentes():
        if not _e_quiz_item(d):
            continue
        n_quiz += 1
        desc = list(d.descendentes())
        if not any(x.tem_classe("quiz-question") for x in desc):
            erro(7, _onde(d), f"quiz-item {n_quiz} sem .quiz-question")
        if d.get("data-formato") == "multipla":
            if not any(x.tag == "button" and x.tem_classe("quiz-btn") for x in desc):
                erro(7, _onde(d), f"quiz-item {n_quiz} (múltipla escolha) sem button.quiz-btn")
            continue
        detalhes = [x for x in desc if x.tag == "details" and x.tem_classe("quiz-details")]
        if not detalhes:
            erro(7, _onde(d), f"quiz-item {n_quiz} sem details.quiz-details")
            continue
        sub = list(detalhes[0].descendentes())
        if not any(x.tag == "summary" and x.tem_classe("quiz-toggle") for x in sub):
            erro(7, _onde(d), f"quiz-item {n_quiz} sem summary.quiz-toggle")
        if not any(x.tem_classe("quiz-answer") for x in sub):
            erro(7, _onde(d), f"quiz-item {n_quiz} sem .quiz-answer")

    # §8
    for d in raiz.descendentes():
        if d.tag == "div" and d.tem_classe("callout"):
            if not set(d.classes) & set(MODIFICADORES_CALLOUT):
                erro(8, _onde(d), "div.callout sem modificador (" + ", ".join(MODIFICADORES_CALLOUT) + ")")

    return erros


def posicoes_corpo(html):
    """Posições (offsets em `html`) obtidas na mesma varredura do parser que extrair_secoes.

    Devolve (h2s, quizzes): h2s é uma lista com (inicio, fim) do primeiro h2 de cada
    section.study-section filha do article (None se a seção não tem h2 fechado); quizzes é a
    lista, em ordem de documento, de (inicio, fim) da tag de abertura de cada .quiz-item.
    Conteúdo de <script>/<style> e texto escapado nunca vira tag, então não entra aqui.
    """
    arvore = _Arvore(html)
    h2s = []
    for article in _secoes_de_primeiro_nivel(arvore.raiz):
        for filho in article.filhos:
            if not _e_secao(filho):
                continue
            h2 = _primeiro_h2(filho)
            if h2 is None or h2.ini_fechamento is None:
                h2s.append(None)
            else:
                fim = html.index(">", h2.ini_fechamento) + 1
                h2s.append((h2.ini, fim))
    quizzes = [(d.ini, d.fim_abertura) for d in arvore.raiz.descendentes() if _e_quiz_item(d)]
    return h2s, quizzes
