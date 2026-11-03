# -*- coding: utf-8 -*-
"""
Glossário — validação do cadastro e utilitários
===============================================
Valida os verbetes de glossario_dados.py. Biblioteca padrão apenas.
"""

import json
import re
from typing import Any, Dict, List

CAMPOS_PERMITIDOS = {
    "id", "termo", "significado", "sigla_de", "termo_ingles", "categoria",
    "explicacao", "historico", "variacoes", "relacionados", "referencias",
}
CAMPOS_OBRIGATORIOS = ("id", "termo", "significado")
CAMPOS_TEXTO = ("termo", "significado", "sigla_de", "termo_ingles", "categoria", "explicacao", "historico")

RE_ID = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
RE_TAG_PERMITIDA = re.compile(r"</?(strong|em|code)>")


class GlossarioInvalido(Exception):
    """Cadastro do glossário com erros; `erros` lista as mensagens."""

    def __init__(self, erros: List[str]):
        self.erros = erros
        super().__init__("Glossário inválido:\n" + "\n".join(erros))


def texto_sem_html(s: str) -> str:
    """Remove as tags strong/em/code, mantendo o texto."""
    return RE_TAG_PERMITIDA.sub("", s)


def _html_proibido(s: str) -> bool:
    return "<" in RE_TAG_PERMITIDA.sub("", s)


def validar_glossario(verbetes: List[Dict[str, Any]]) -> List[str]:
    """Devolve mensagens 'glossario <id>: <campo>: <descrição>'; vazia se tudo certo."""
    erros: List[str] = []
    ids = [v.get("id") for v in verbetes if isinstance(v.get("id"), str)]
    vistos = set()
    for v in verbetes:
        vid = v.get("id", "?")

        def erro(campo: str, msg: str) -> None:
            erros.append(f"glossario {vid}: {campo}: {msg}")

        for campo in v:
            if campo not in CAMPOS_PERMITIDOS:
                erro(campo, "campo desconhecido")
        for campo in CAMPOS_OBRIGATORIOS:
            if not isinstance(v.get(campo), str) or not v[campo].strip():
                erro(campo, "obrigatório e deve ser texto não vazio")
        if isinstance(v.get("id"), str):
            if not RE_ID.match(v["id"]):
                erro("id", "formato inválido (use minúsculas, dígitos e hífens)")
            if v["id"] in vistos:
                erro("id", "duplicado")
            vistos.add(v["id"])
        for campo in CAMPOS_TEXTO:
            val = v.get(campo)
            if val is None:
                continue
            if not isinstance(val, str):
                erro(campo, "deve ser texto")
            elif _html_proibido(val):
                erro(campo, "HTML proibido (só <strong>, <em> e <code>)")
        if "variacoes" in v:
            var = v["variacoes"]
            if not isinstance(var, list) or not all(isinstance(x, str) and x.strip() for x in var):
                erro("variacoes", "deve ser lista de textos não vazios")
        if "relacionados" in v:
            rel = v["relacionados"]
            if not isinstance(rel, list) or not all(isinstance(x, str) for x in rel):
                erro("relacionados", "deve ser lista de ids")
            else:
                for r in rel:
                    if r not in ids:
                        erro("relacionados", f"id inexistente: {r}")
        if "referencias" in v:
            refs = v["referencias"]
            if not isinstance(refs, list):
                erro("referencias", "deve ser lista de (rótulo, URL)")
            else:
                for ref in refs:
                    if (not isinstance(ref, (tuple, list)) or len(ref) != 2
                            or not all(isinstance(x, str) and x.strip() for x in ref)):
                        erro("referencias", "cada item deve ser (rótulo, URL)")
                    elif not ref[1].startswith("https://"):
                        erro("referencias", f"URL deve começar com https://: {ref[1]}")
    return erros


def carregar_glossario() -> List[Dict[str, Any]]:
    """Lê glossario_dados.GLOSSARIO (em tempo de chamada), valida e devolve."""
    import glossario_dados

    verbetes = glossario_dados.GLOSSARIO
    erros = validar_glossario(verbetes)
    if erros:
        raise GlossarioInvalido(erros)
    return verbetes


# ---------------------------------------------------------------------------
# Marcação automática de termos no corpo do módulo
# ---------------------------------------------------------------------------

from html import escape
from html.parser import HTMLParser

TAGS_IGNORADAS = {
    "pre", "code", "kbd", "samp", "script", "style", "svg", "textarea",
    "h1", "h2", "h3", "h4", "h5", "h6", "a", "button", "label", "dfn",
}
CLASSES_IGNORADAS = {"terminal-box", "mermaid"}
TAGS_VAZIAS = {
    "br", "img", "input", "hr", "meta", "link", "source", "wbr", "col",
    "area", "base", "embed", "param", "track",
}


RE_FIM_TAG = re.compile(r"</[^>]*>")


def _e_sigla(forma: str) -> bool:
    """Sigla = nenhuma letra minúscula; casa diferenciando caixa."""
    return not any(c.islower() for c in forma)


def _montar_regex(verbetes: List[Dict[str, Any]]):
    """Devolve (regex único, mapa sigla->id, mapa palavra(casefold)->id)."""
    siglas: Dict[str, str] = {}
    palavras: Dict[str, str] = {}
    for v in verbetes:
        for forma in [v["termo"]] + list(v.get("variacoes", [])):
            if _e_sigla(forma):
                siglas.setdefault(forma, v["id"])
            else:
                palavras.setdefault(forma.casefold(), v["id"])
    formas = [(f, False) for f in siglas] + [(f, True) for f in palavras]
    if not formas:
        return None, siglas, palavras
    formas.sort(key=lambda x: len(x[0]), reverse=True)
    alternativas = [f"(?i:{re.escape(f)})" if ci else re.escape(f) for f, ci in formas]
    regex = re.compile(r"(?<![\w-])(?:" + "|".join(alternativas) + r")(?![\w-])")
    return regex, siglas, palavras


class _Marcador(HTMLParser):
    def __init__(self, verbetes: List[Dict[str, Any]]):
        super().__init__(convert_charrefs=False)
        self.saida: List[str] = []
        self.pilha: List[tuple] = []  # (tag, ignorado, e_secao)
        self.usados: set = set()
        self.regex, self.siglas, self.palavras = _montar_regex(verbetes)
        self.titulos = {v["id"]: texto_sem_html(v["significado"]) for v in verbetes}
        self._ini_fim = 0
        self._inicio_linhas: List[int] = [0]

    # -- tags ---------------------------------------------------------------
    def handle_starttag(self, tag, attrs):
        self.saida.append(self.get_starttag_text())
        if tag in TAGS_VAZIAS:
            return
        classes = set()
        for nome, valor in attrs:
            if nome == "class" and valor:
                classes = set(valor.split())
        ignorado = tag in TAGS_IGNORADAS or bool(classes & CLASSES_IGNORADAS)
        e_secao = tag == "section" and "study-section" in classes
        self.pilha.append((tag, ignorado, e_secao))

    def handle_startendtag(self, tag, attrs):
        self.saida.append(self.get_starttag_text())

    def parse_endtag(self, i):
        # O handler roda dentro de super().parse_endtag; guardamos o início
        # para recuperar o texto bruto (caixa e espaços originais).
        self._ini_fim = i
        return super().parse_endtag(i)

    def handle_endtag(self, tag):
        m = RE_FIM_TAG.match(self.rawdata, self._ini_fim)
        self.saida.append(m.group(0) if m else f"</{tag}>")
        for idx in range(len(self.pilha) - 1, -1, -1):
            if self.pilha[idx][0] == tag:
                del self.pilha[idx:]
                break

    # -- passagem direta ------------------------------------------------------
    def _ref_bruta(self, tamanho: int) -> str:
        """Texto original da referência (com ou sem ';' final) na posição atual."""
        linha, col = self.getpos()
        ini = self._inicio_linhas[linha - 1] + col
        fim = ini + tamanho
        if self.rawdata[fim:fim + 1] == ";":
            fim += 1
        return self.rawdata[ini:fim]

    def handle_entityref(self, name):
        self.saida.append(self._ref_bruta(1 + len(name)))

    def handle_charref(self, name):
        self.saida.append(self._ref_bruta(2 + len(name)))

    def handle_comment(self, data):
        self.saida.append(f"<!--{data}-->")

    def handle_decl(self, decl):
        self.saida.append(f"<!{decl}>")

    def handle_pi(self, data):
        self.saida.append(f"<?{data}>")

    def unknown_decl(self, data):
        self.saida.append(f"<![{data}]>")

    # -- texto ----------------------------------------------------------------
    def _pode_marcar(self) -> bool:
        if self.regex is None:
            return False
        em_secao = any(e[2] for e in self.pilha)
        return em_secao and not any(e[1] for e in self.pilha)

    def handle_data(self, data):
        if not self._pode_marcar():
            self.saida.append(data)
            return
        pos = 0
        for m in self.regex.finditer(data):
            trecho = m.group(0)
            vid = self.siglas.get(trecho) or self.palavras.get(trecho.casefold())
            if vid is None:
                continue
            self.usados.add(vid)
            self.saida.append(data[pos:m.start()])
            self.saida.append(
                f'<dfn class="glossario" data-termo="{vid}" tabindex="0" '
                f'title="{escape(self.titulos[vid], quote=True)}">{trecho}</dfn>'
            )
            pos = m.end()
        self.saida.append(data[pos:])


def marcar_termos(html: str, verbetes: List[Dict[str, Any]]):
    """Marca todas as ocorrências dos verbetes no texto das seções; devolve (html, ids ordenados)."""
    marcador = _Marcador(verbetes)
    # Offsets de início de linha (para recuperar referências sem ';', como "&CK ").
    marcador._inicio_linhas = [0] + [m.end() for m in re.finditer(r"\n", html)]
    marcador.feed(html)
    marcador.close()
    return "".join(marcador.saida), sorted(marcador.usados)


# ---------------------------------------------------------------------------
# Bloco de dados embutido no módulo compilado
# ---------------------------------------------------------------------------

CAMPOS_BLOCO = ("termo", "categoria", "sigla_de", "termo_ingles", "significado")


def bloco_dados_glossario(ids: List[str], verbetes: List[Dict[str, Any]]) -> str:
    """JSON (<script type="application/json">) com os verbetes usados; "" se ids vazio."""
    if not ids:
        return ""
    por_id = {v["id"]: v for v in verbetes}
    dados = {
        i: {c: por_id[i][c] for c in CAMPOS_BLOCO if c in por_id[i]}
        for i in ids
    }
    texto = json.dumps(dados, ensure_ascii=False)
    texto = texto.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return f'<script type="application/json" id="glossario-dados">{texto}</script>'
