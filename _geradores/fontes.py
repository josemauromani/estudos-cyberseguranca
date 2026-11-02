#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fontes embutidas nos HTML gerados (IBM Plex e Barlow Semi Condensed, OFL).

Os arquivos WOFF2 ficam em `_geradores/fontes/` e são convertidos em data URI,
para que os estudos funcionem via file:// sem rede.
"""

import base64
from pathlib import Path

FONTES_DIR = Path(__file__).resolve().parent / "fontes"

# (arquivo, família, peso, estilo)
FACES = [
    ("ibm-plex-sans-latin-400-normal.woff2", "IBM Plex Sans", 400, "normal"),
    ("ibm-plex-sans-latin-400-italic.woff2", "IBM Plex Sans", 400, "italic"),
    ("ibm-plex-sans-latin-600-normal.woff2", "IBM Plex Sans", 600, "normal"),
    ("ibm-plex-mono-latin-400-normal.woff2", "IBM Plex Mono", 400, "normal"),
    ("barlow-semi-condensed-latin-700-normal.woff2", "Barlow Semi Condensed", 700, "normal"),
]


def css_fontes(dir_fontes: Path = FONTES_DIR) -> str:
    """Retorna o CSS com um @font-face por fonte, em data URI base64.

    Levanta FileNotFoundError citando o nome do arquivo que falta.
    """
    blocos = []
    for arquivo, familia, peso, estilo in FACES:
        caminho = dir_fontes / arquivo
        if not caminho.is_file():
            raise FileNotFoundError(f"fonte ausente: {arquivo} (em {dir_fontes})")
        dados = base64.b64encode(caminho.read_bytes()).decode("ascii")
        blocos.append(
            "@font-face {\n"
            f'  font-family: "{familia}";\n'
            f"  font-style: {estilo};\n"
            f"  font-weight: {peso};\n"
            "  font-display: swap;\n"
            f"  src: url(data:font/woff2;base64,{dados}) format(\"woff2\");\n"
            "}\n"
        )
    return "\n".join(blocos)
