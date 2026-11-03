# -*- coding: utf-8 -*-
"""
Glossário — validação do cadastro e utilitários
===============================================
Valida os verbetes de glossario_dados.py. Biblioteca padrão apenas.
"""

import re
from typing import Any, Dict, List

CAMPOS_PERMITIDOS = {
    "id", "termo", "significado", "sigla_de", "termo_ingles", "categoria",
    "explicacao", "historico", "variacoes", "relacionados", "referencias",
}
CAMPOS_OBRIGATORIOS = ("id", "termo", "significado")
CAMPOS_TEXTO = ("termo", "significado", "sigla_de", "termo_ingles", "categoria", "explicacao", "historico")

RE_ID = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
RE_TAG = re.compile(r"<[^>]*>")
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
    return any(not RE_TAG_PERMITIDA.fullmatch(t) for t in RE_TAG.findall(s))


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
