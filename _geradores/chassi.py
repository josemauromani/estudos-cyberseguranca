"""Chassi das páginas de módulo: barra superior, sumário, cabeçalho, cabeçalhos de seção e fim.

Gerado a partir de ESTUDOS_DADOS/TRILHAS (index_dados.py) e da ordem do catálogo.
Textos vindos de ESTUDOS_DADOS passam por html.escape uma única vez; os títulos de seção
(Secao.titulo_html) já são HTML do corpo e entram sem reescapar.
"""
import re
from dataclasses import dataclass, field
from html import escape
from typing import List, Optional, Tuple

from contrato import ROTULOS, TIPOS, Secao, posicoes_corpo
from index_dados import ESTUDOS_DADOS, NIVEIS, TRILHAS

Vizinho = Tuple[str, str, str]  # (slug, titulo, caminho_rel)

TIPOS_COM_CONTADOR = ("laboratorio", "checklist", "questoes")


@dataclass
class InfoModulo:
    slug: str
    numero: int
    total: int
    titulo: str
    subtitulo: str
    trilha_num: int
    trilha_nome: str
    tempo_minutos: int
    nivel_rotulo: str
    nist: str
    mitre: str
    carreiras: List[str]
    caminho_rel: str
    anterior: Optional[Vizinho]
    proximo: Optional[Vizinho]
    titulo_curto: str = ""
    trilha_cor: str = ""


def _caminho_rel(catalogo: dict, slug: str) -> str:
    c = catalogo.get(slug)
    if not c:
        return f"../{slug}/"
    return f"../{c['pasta']}/{c['arquivo_html']}"


def info_modulo(slug: str) -> InfoModulo:
    if slug not in ESTUDOS_DADOS:
        raise SlugSemDados(slug)
    from montar import carregar_catalogo_estudos

    catalogo = carregar_catalogo_estudos()
    slugs = list(ESTUDOS_DADOS)
    i = slugs.index(slug)
    d = ESTUDOS_DADOS[slug]

    def vizinho(j: int) -> Optional[Vizinho]:
        if j < 0 or j >= len(slugs):
            return None
        s = slugs[j]
        return (s, ESTUDOS_DADOS[s]["titulo"], _caminho_rel(catalogo, s))

    trilha = TRILHAS.get(d.get("trilha"), {})
    nivel = NIVEIS.get(d.get("nivel", ""), d.get("nivel", ""))
    if " " in nivel and not nivel[0].isalnum():
        nivel = nivel.split(" ", 1)[1]
    return InfoModulo(
        slug=slug,
        numero=i + 1,
        total=len(slugs),
        titulo=d["titulo"],
        subtitulo=d.get("subtitulo", ""),
        trilha_num=d.get("trilha", 0),
        trilha_nome=trilha.get("nome", ""),
        tempo_minutos=d.get("tempo_minutos", 0),
        nivel_rotulo=nivel,
        nist=d.get("nist", ""),
        mitre=d.get("mitre", ""),
        carreiras=list(d.get("carreiras", [])),
        caminho_rel=_caminho_rel(catalogo, slug),
        anterior=vizinho(i - 1),
        proximo=vizinho(i + 1),
        titulo_curto=catalogo.get(slug, {}).get("titulo", d["titulo"]),
        trilha_cor=trilha.get("cor", ""),
    )


def _nn(n: int) -> str:
    return f"{n:02d}"


def gerar_topbar(info: InfoModulo) -> str:
    return f"""<header class="topbar">
  <div class="topbar-in">
    <a class="nav-back" href="../index.html">← Painel</a>
    <span class="crumb">Trilha {info.trilha_num} · {escape(info.trilha_nome)} / {_nn(info.numero)} · <b>{escape(info.titulo_curto)}</b></span>
    <span class="tipo-atual"></span>
    <button class="theme-toggle-btn" type="button" aria-label="Alternar tema"><span class="theme-icon">🌙</span> <span class="theme-label">Escuro</span></button>
    <button class="toc-toggle" type="button" aria-expanded="false" aria-controls="toc">☰ Sumário</button>
  </div>
  <div class="readbar"></div>
</header>"""


def _link_nav(v: Optional[Vizinho], texto: str) -> str:
    if v is None:
        return ""
    return f'<a href="{escape(v[2], quote=True)}" title="{escape(v[1], quote=True)}">{texto}</a>'


def gerar_sumario(info: InfoModulo, secoes: List[Secao]) -> str:
    itens = []
    for s in secoes:
        icone, rotulo = ROTULOS[s.tipo]
        itens.append(
            f'    <li><a class="toc-item" href="#{escape(s.id, quote=True)}" data-tipo="{s.tipo}">'
            f'<span class="toc-icone">{icone}</span>'
            f'<span><span class="toc-tipo">{rotulo}</span><span class="toc-titulo">{s.titulo_html}</span></span>'
            f'<span class="toc-contador"></span></a></li>'
        )
    nav = _link_nav(info.anterior, "← Anterior") + _link_nav(info.proximo, "Próximo →")
    return f"""<aside class="toc" id="toc" aria-label="Sumário do módulo">
  <div class="toc-rotulo">Estudo {_nn(info.numero)} de {info.total}</div>
  <div class="toc-modulo">{escape(info.titulo)}</div>
  <div class="toc-progresso">0%</div>
  <ol class="toc-lista">
{chr(10).join(itens)}
  </ol>
  <div class="toc-pe">
    <button class="btn-concluir" type="button">✓ Concluir módulo</button>
    <div class="toc-nav">{nav}</div>
  </div>
</aside>"""


def _plural(n: int, singular: str, plural: str) -> str:
    return f"{n} {singular if n == 1 else plural}"


def _roadmap(secoes: List[Secao]) -> str:
    links = []
    for tipo in TIPOS:
        do_tipo = [s for s in secoes if s.tipo == tipo]
        if not do_tipo:
            continue
        if tipo == "teoria":
            qtd = _plural(len(do_tipo), "seção", "seções")
        elif tipo == "checklist":
            qtd = _plural(sum(s.n_checklist for s in do_tipo), "item", "itens")
        elif tipo == "questoes":
            qtd = _plural(sum(s.n_questoes for s in do_tipo), "questão", "questões")
        else:
            qtd = ""
        _, rotulo = ROTULOS[tipo]
        links.append(
            f'<a href="#{escape(do_tipo[0].id, quote=True)}" data-tipo="{tipo}">'
            f'<span class="toc-tipo">{rotulo}</span>{qtd}</a>'
        )
    return '<nav class="roadmap" aria-label="Mapa do módulo">' + "".join(links) + "</nav>"


def gerar_cabecalho(info: InfoModulo, secoes: List[Secao]) -> str:
    chips = [
        f"⏱ {info.tempo_minutos} min",
        f"📈 {escape(info.nivel_rotulo)}",
        f"🛡 NIST {escape(info.nist)}",
        f"🎯 ATT&amp;CK {escape(info.mitre)}",
        f"👤 {escape(' · '.join(info.carreiras))}",
    ]
    estilo = f' style="--track-color:{escape(info.trilha_cor, quote=True)}"' if info.trilha_cor else ""
    sub = f'\n  <p class="mhead-sub">{escape(info.subtitulo)}</p>' if info.subtitulo else ""
    return f"""<header class="mhead"{estilo}>
  <div class="mhead-kicker">Trilha {info.trilha_num} · {escape(info.trilha_nome)} · Estudo {_nn(info.numero)}</div>
  <h1>{escape(info.titulo)}</h1>{sub}
  <div class="chips">{''.join(f'<span class="chip">{c}</span>' for c in chips)}</div>
  {_roadmap(secoes)}
</header>"""


def gerar_fim(info: InfoModulo) -> str:
    def cartao(v: Optional[Vizinho], rotulo: str) -> str:
        return (f'<a href="{escape(v[2], quote=True)}"><small>{rotulo}</small>'
                f'<b>{escape(v[1])}</b></a>')

    anterior = (cartao(info.anterior, f"← Anterior · Estudo {_nn(info.numero - 1)}")
                if info.anterior else "<span></span>")
    proximo = cartao(info.proximo, f"Próximo · Estudo {_nn(info.numero + 1)} →") if info.proximo else ""
    return f"""<div class="study-done">
  <span>Terminou este módulo? Marque como concluído para registrar o seu progresso.</span>
  <button class="btn-concluir" type="button">✓ Concluir módulo</button>
</div>
<div class="study-pager">{anterior}{proximo}</div>"""


class SlugSemDados(KeyError):
    """O slug não existe em ESTUDOS_DADOS."""


def aplicar_cabecalhos_de_secao(body: str, secoes: List[Secao]) -> str:
    h2s, _ = posicoes_corpo(body)
    if len(h2s) != len(secoes):
        raise ValueError(f"{len(h2s)} seções no corpo, {len(secoes)} esperadas")
    for sec, pos in zip(secoes, h2s):
        if pos is None:
            raise ValueError(f"seção {sec.id!r} sem h2")
    for idx in range(len(secoes) - 1, -1, -1):
        ini, fim = h2s[idx]
        icone, rotulo = ROTULOS[secoes[idx].tipo]
        shead = (f'<div class="shead"><span class="stype">{icone} {rotulo} '
                 f'<small>· Seção {idx + 1} de {len(secoes)}</small></span>{body[ini:fim]}</div>')
        body = body[:ini] + shead + body[fim:]
    return body


_RE_DATA_Q = re.compile(r"\s+data-q\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s>]+)")
_RE_CLASS = re.compile(r"(?<![\w-])class\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s>]+)")


def numerar_questoes(body: str) -> str:
    _, quizzes = posicoes_corpo(body)
    for n in range(len(quizzes), 0, -1):
        ini, fim = quizzes[n - 1]
        tag = _RE_DATA_Q.sub("", body[ini:fim])
        m = _RE_CLASS.search(tag)
        if not m:
            raise ValueError(f"quiz-item {n} sem atributo class")
        tag = tag[:m.end()] + f' data-q="q{n}"' + tag[m.end():]
        body = body[:ini] + tag + body[fim:]
    return body


def inserir_fim(body: str, fim: str) -> str:
    """Insere o bloco de fim ao final da última seção (antes do último </section>)."""
    i = body.rfind("</section>")
    if i < 0:
        return body + fim
    return body[:i] + fim + "\n" + body[i:]
