#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Construtor do Portal Central — Estudos em Cibersegurança
========================================================
Gera a página raiz index.html a partir de index_dados.py, das fontes embutidas,
de tokens.css, de index.css e do status de compilação de cada estudo do catálogo.

Estrutura: barra superior (menu, marca, busca, tema) + menu lateral com sete visões
(Catálogo, Rotas sugeridas, Por certificação, Pela necessidade, Rota por vaga,
Meu progresso) + conteúdo. Só o Catálogo aparece na carga; as demais visões vêm
com `hidden` e são alternadas pelo JavaScript do portal.

Uso via CLI:
    python3 _geradores/build_index.py [caminho_saida]

Uso como módulo:
    from build_index import gerar_index_html
    gerar_index_html(output_path)
"""

import argparse
import json
import sys
import unicodedata
from functools import lru_cache
from html import escape
from pathlib import Path
from typing import Dict, List, Optional

GERADORES_DIR = Path(__file__).resolve().parent
ROOT_DIR = GERADORES_DIR.parent
sys.path.insert(0, str(GERADORES_DIR))

from contrato import extrair_secoes
from fontes import css_fontes
from glossario import GlossarioInvalido, carregar_glossario, marcar_termos, texto_sem_html
from index_dados import (
    CERTIFICACOES,
    ESTUDOS_DADOS,
    NECESSIDADES,
    NIVEIS,
    ROTA_VAGA,
    ROTAS_PERFIL,
    TRILHAS,
)
from montar import carregar_catalogo_estudos, normalizar_chave

DEFAULT_INDEX_CSS = GERADORES_DIR / "index.css"
TOKENS_CSS = GERADORES_DIR / "tokens.css"
DEFAULT_OUTPUT_HTML = ROOT_DIR / "index.html"

# Visões do menu lateral, na ordem de exibição: (id, ícone, rótulo)
VISOES = [
    ("catalogo", "📚", "Catálogo"),
    ("rotas", "🧭", "Rotas sugeridas"),
    ("certificacoes", "🎓", "Por certificação"),
    ("necessidades", "🛠", "Pela necessidade"),
    ("vaga", "💼", "Rota por vaga"),
    ("progresso", "📈", "Meu progresso"),
    ("glossario", "📖", "Glossário"),
]

# Botões da barra "Agrupar por" do catálogo: (id, rótulo)
GRUPOS_CATALOGO = [
    ("trilha", "Trilha"),
    ("nivel", "Nível"),
    ("perfil", "Perfil"),
    ("nist", "NIST"),
]


def corpo_do_modulo(slug: str, catalogo: Optional[Dict[str, dict]] = None) -> Optional[Path]:
    """Fragmento `_geradores/<snake>_body.html` do módulo, ou None se não houver.

    Casa o nome do arquivo com o slug, a pasta ou o arquivo HTML do catálogo pela
    mesma normalização usada por montar.py e gerar.sh.
    """
    catalogo = carregar_catalogo_estudos() if catalogo is None else catalogo
    info = catalogo.get(slug, {})
    chaves = {
        normalizar_chave(v)
        for v in (slug, info.get("pasta", ""), info.get("arquivo_html", ""))
        if v
    }
    for corpo in sorted(GERADORES_DIR.glob("*_body.html")):
        if normalizar_chave(corpo.name) in chaves:
            return corpo
    return None


@lru_cache(maxsize=None)
def contar_secoes(slug: str) -> int:
    """Total de seções de primeiro nível do corpo do módulo (0 se não houver corpo)."""
    corpo = corpo_do_modulo(slug)
    if corpo is None:
        return 0
    return len(extrair_secoes(corpo.read_text(encoding="utf-8")))


def calcular_estatisticas(catalogo: Dict[str, dict], dados: Dict[str, dict]) -> dict:
    """Calcula estatísticas de progresso, minutos e disponibilidade dos módulos."""
    total_estudos = len(dados)
    total_trilhas = len(TRILHAS)
    total_simuladores = total_estudos
    tempo_total_minutos = sum(d["tempo_minutos"] for d in dados.values())
    horas_totais = round(tempo_total_minutos / 60, 1)

    estudos_disponiveis = 0
    status_map = {}

    for slug, meta in dados.items():
        info_cat = catalogo.get(slug, {})
        pasta = info_cat.get("pasta", slug)
        arquivo_html = info_cat.get("arquivo_html", f"treinamento-{slug.lower()}.html")
        caminho_arquivo = ROOT_DIR / pasta / arquivo_html

        if caminho_arquivo.exists():
            estudos_disponiveis += 1
            status_map[slug] = {
                "disponivel": True,
                "caminho_relativo": f"{pasta}/{arquivo_html}",
            }
        else:
            status_map[slug] = {
                "disponivel": False,
                "caminho_relativo": f"{pasta}/{arquivo_html}",
            }

    return {
        "total_estudos": total_estudos,
        "total_trilhas": total_trilhas,
        "total_simuladores": total_simuladores,
        "tempo_total_minutos": tempo_total_minutos,
        "horas_totais": horas_totais,
        "estudos_disponiveis": estudos_disponiveis,
        "status_map": status_map,
    }


def render_necessidades_grid(necessidades: List[dict], status_map: Optional[Dict[str, dict]] = None) -> str:
    """Gera o HTML da grade de desafios práticos do mundo real.

    Cada cartão leva ao módulo compilado; sem o módulo (ou sem status_map), aponta
    para o cartão do módulo no catálogo (#estudo-<slug>).
    """
    status_map = status_map or {}
    cards_html = []
    for item in necessidades:
        slug = item["slug"]
        desafio = escape(item["desafio"])
        cat = escape(item.get("categoria", "Segurança"))
        icone = item.get("icone", "🎯")
        estudo_info = ESTUDOS_DADOS.get(slug, {})
        titulo_estudo = escape(estudo_info.get("titulo", slug))
        info = status_map.get(slug, {})
        href = escape(info["caminho_relativo"], quote=True) if info.get("disponivel") else f"#estudo-{slug}"

        card = f"""      <a href="{href}" class="need-card" data-slug="{slug}">
        <span class="need-category">{icone} {cat}</span>
        <span class="need-title">{desafio}</span>
        <span class="need-target">→ Ver módulo: {titulo_estudo}</span>
      </a>"""
        cards_html.append(card)

    return "\n".join(cards_html)


def render_cartao(slug: str, d: dict, status_info: dict) -> str:
    """Cartão de módulo do catálogo (a.mc), com os atributos lidos pelo JS do portal.

    Mostra número, tempo, título, subtítulo, nível, NIST, simulador e o status
    (.mc-status, vazio no HTML e preenchido pelo JS).
    """
    numero = list(ESTUDOS_DADOS).index(slug) + 1
    titulo = escape(d["titulo"])
    subtitulo = escape(d["subtitulo"])
    simulador = escape(d["simulador_nome"])
    nist = escape(d["nist"], quote=True)
    nivel = d["nivel"]
    perfis = escape("|".join(d["carreiras"]), quote=True)
    rotas_str = " ".join(r["id"] for r in ROTAS_PERFIL if slug in r["modulos"])
    certs_str = escape("|".join(c["sigla"] for c in CERTIFICACOES if slug in c["modulos"]), quote=True)
    busca = escape(
        " ".join([
            slug, d["titulo"], d["subtitulo"], d["pergunta_chave"], d["simulador_nome"],
            d["nist"], " ".join(d["carreiras"]), " ".join(d["fatos"]),
        ]).lower(),
        quote=True,
    )

    if status_info.get("disponivel"):
        destino = f'href="{escape(status_info["caminho_relativo"], quote=True)}"'
        classe = "mc"
        pendente = ""
    else:
        destino = 'aria-disabled="true"'
        classe = "mc pendente"
        pendente = '<span class="tag tag-pendente">⏳ Em elaboração</span>'

    return f"""          <a class="{classe}" id="estudo-{slug}"
            data-slug="{slug}"
            data-trilha="{d['trilha']}"
            data-nivel="{nivel}"
            data-perfis="{perfis}"
            data-nist="{nist}"
            data-secoes="{contar_secoes(slug)}"
            data-rotas="{rotas_str}"
            data-certs="{certs_str}"
            data-busca="{busca}"
            {destino}>
            <span class="mc-top"><span class="mc-num">Estudo {numero:02d}</span><span class="mc-tempo">⏱ {d['tempo_minutos']} min</span></span>
            <h3 class="mc-titulo">{titulo}</h3>
            <p class="mc-sub">{subtitulo}</p>
            <span class="mc-tags"><span class="tag tag-nivel">{escape(NIVEIS[nivel])}</span><span class="tag">NIST {escape(d['nist'])}</span><span class="tag lab">🧪 {simulador}</span>{pendente}</span>
            <span class="mc-status"></span>
          </a>"""


def render_catalogo(dados: Dict[str, dict], status_map: Dict[str, dict]) -> str:
    """Grupos do catálogo, um por trilha (agrupamento padrão; funciona sem JS)."""
    grupos = []
    for tid, info in TRILHAS.items():
        slugs = [s for s, d in dados.items() if d["trilha"] == tid]
        if not slugs:
            continue
        cartoes = "\n".join(
            render_cartao(s, dados[s], status_map.get(s, {"disponivel": False, "caminho_relativo": ""}))
            for s in slugs
        )
        grupos.append(f"""        <div class="grupo" data-trilha="{tid}">
          <div class="grupo-cab"><span class="k">Trilha {tid}</span><h2>{escape(info['nome'])}</h2><span class="p">0 de {len(slugs)} concluídos</span></div>
          <div class="grid">
{cartoes}
          </div>
        </div>""")
    return "\n".join(grupos)


def render_menu_lateral(contagens: Dict[str, int]) -> str:
    """Links do menu lateral (nav.menu-lateral), um por visão; o Catálogo começa ativo."""
    links = []
    for vid, icone, rotulo in VISOES:
        atual = ' aria-current="page"' if vid == "catalogo" else ""
        n = f' <span class="n">{contagens[vid]}</span>' if vid in contagens else ""
        links.append(f'      <a href="#v-{vid}" data-view="{vid}"{atual}>{icone} {rotulo}{n}</a>')
    return "\n".join(links)


def render_progresso_global(stats: dict) -> str:
    """Bloco "Seu progresso" do menu lateral; o JS preenche os campos data-gp."""
    total = stats["total_estudos"]
    return f"""    <div class="gprog" id="progresso-global">
      <span class="gp-rotulo">Seu progresso</span>
      <p class="gp-total"><b data-gp="concluidos">0</b> de {total} concluídos</p>
      <div class="bar" role="progressbar" aria-label="Módulos concluídos" aria-valuemin="0" aria-valuemax="{total}" aria-valuenow="0"><i data-gp="barra"></i></div>
      <div class="gp-row"><span><span data-gp="andamento">0</span> em andamento</span><span>~{stats["tempo_total_minutos"]} min</span></div>
      <div class="gp-row"><span>Módulos Compilados</span><span>{stats["estudos_disponiveis"]} / {total}</span></div>
    </div>"""


def render_meu_progresso(dados: Dict[str, dict], status_map: Dict[str, dict]) -> str:
    """Lista "Meu progresso": um item por módulo, com a caixa de conclusão (cs_done_<slug>)."""
    total = len(dados)
    itens = []
    for numero, (slug, d) in enumerate(dados.items(), start=1):
        titulo = escape(d["titulo"])
        info = status_map.get(slug, {"disponivel": False, "caminho_relativo": ""})
        if info["disponivel"]:
            href = escape(info["caminho_relativo"], quote=True)
            alvo = f'<a class="progresso-titulo" href="{href}">{titulo}</a>'
            disp = '<span class="progresso-disp">Disponível</span>'
        else:
            alvo = f'<span class="progresso-titulo pendente">{titulo}</span>'
            disp = '<span class="progresso-disp pendente">⏳ Em elaboração</span>'
        itens.append(
            f'        <li class="progresso-item">'
            f'<input type="checkbox" data-slug="{slug}" id="feito-{slug}" '
            f'aria-label="Concluí o Estudo {numero:02d}: {titulo}">'
            f'<span class="progresso-num">{numero:02d}</span>{alvo}{disp}</li>'
        )
    lista = "\n".join(itens)
    return f"""      <div class="progresso-resumo">
        <span class="progresso-texto" id="progresso-texto">0 de {total} concluídos (0%)</span>
        <div class="bar" role="progressbar" aria-label="Módulos concluídos" aria-valuemin="0" aria-valuemax="{total}" aria-valuenow="0"><i></i></div>
        <button type="button" class="btn" id="zerar-progresso">Zerar progresso salvo no navegador</button>
      </div>
      <ol class="progresso-lista" id="progresso-lista">
{lista}
      </ol>"""


def _render_painel(grupos: List[dict], status_map: Dict[str, dict], secao_id: str, comentario: str) -> str:
    """Painel com passos (módulos), progresso e próximo módulo, um bloco por grupo.

    Cada grupo traz: id, titulo (cabeçalho), descricao e modulos (slugs na ordem de exibição).
    Todos os grupos ficam visíveis dentro da visão; o JavaScript do portal calcula o
    progresso e o próximo módulo a partir das chaves cs_done_<slug> salvas no navegador.
    """
    ordem = list(ESTUDOS_DADOS)
    blocos = []
    for g in grupos:
        passos = []
        for slug in g["modulos"]:
            numero = ordem.index(slug) + 1
            titulo = escape(ESTUDOS_DADOS[slug]["titulo"])
            rotulo = f"{numero:02d} · {titulo}"
            info = status_map.get(slug, {"disponivel": False, "caminho_relativo": ""})
            if info["disponivel"]:
                href = escape(info["caminho_relativo"], quote=True)
                alvo = f'<a href="{href}" class="rota-passo-link">{titulo}</a>'
            else:
                alvo = f'<span class="rota-passo-link pendente" title="Em construção">⏳ {titulo}</span>'
            passos.append(
                f'<li class="rota-passo" data-slug="{escape(slug, quote=True)}" data-rotulo="{rotulo}">'
                f'<span class="rota-passo-num">{numero:02d}</span> {alvo}'
                f'<span class="rota-passo-check" aria-label="concluído">✓</span></li>'
            )
        total = len(g["modulos"])
        blocos.append(f"""      <div class="rota-sugerida" data-rota="{escape(g['id'], quote=True)}">
        <div class="rota-cabecalho">
          <h2>{g['titulo']}</h2>
          <p>{escape(g['descricao'])}</p>
        </div>
        <div class="rota-progresso">
          <div class="rota-progresso-barra" role="progressbar" aria-label="Progresso" aria-valuemin="0" aria-valuemax="{total}" aria-valuenow="0"><div class="rota-progresso-preenchido"></div></div>
          <span class="rota-progresso-texto">0 de {total} concluídos (0%)</span>
        </div>
        <p class="rota-proximo"></p>
        <ol class="rota-passos">
          {chr(10).join("          " + p for p in passos).lstrip()}
        </ol>
      </div>""")
    return f"""    <!-- {comentario} -->
    <section class="rota-sugerida-section" id="{secao_id}">
{chr(10).join(blocos)}
    </section>"""


def render_painel_rotas(rotas: List[dict], status_map: Dict[str, dict]) -> str:
    """Painel da visão Rotas sugeridas: passos na ordem de estudo da rota."""
    grupos = [
        {"id": r["id"], "titulo": f"{r['icone']} Rota: {escape(r['nome'])}", "descricao": r["descricao"], "modulos": r["modulos"]}
        for r in rotas
    ]
    return _render_painel(grupos, status_map, "secao-rota-sugerida", "Painel: rotas sugeridas (visão Rotas sugeridas)")


def render_painel_certificacoes(certs: List[dict], status_map: Dict[str, dict]) -> str:
    """Painel da visão Por certificação: módulos que cobrem a prova, em ordem numérica."""
    ordem = list(ESTUDOS_DADOS)
    grupos = [
        {
            "id": c["sigla"],
            "titulo": f"🎓 {escape(c['sigla'])}: {escape(c['nome'])}",
            "descricao": f"{c['orgao']} · {c['foco']} · Experiência: {c['experiencia']}",
            "modulos": sorted(c["modulos"], key=ordem.index),
        }
        for c in certs
    ]
    return _render_painel(grupos, status_map, "secao-cert-painel", "Painel: progresso por certificação (visão Por certificação)")


def render_chip_modulo(slug: str, status_map: Dict[str, dict], apoio: bool = False) -> str:
    """Chip de módulo: link se disponível, senão span desabilitado."""
    numero = list(ESTUDOS_DADOS).index(slug) + 1
    texto = f"{numero:02d} · {escape(ESTUDOS_DADOS[slug]['titulo'])}"
    info = status_map.get(slug, {"disponivel": False, "caminho_relativo": ""})
    if not info["disponivel"]:
        texto = f"⏳ {texto}"
    extra = " apoio" if apoio else ""
    data_slug = f'data-slug="{escape(slug, quote=True)}"'
    if info["disponivel"]:
        href = escape(info["caminho_relativo"], quote=True)
        return f'<a href="{href}" class="vaga-chip{extra}" {data_slug}>{texto}</a>'
    return f'<span class="vaga-chip pendente{extra}" {data_slug} aria-disabled="true" title="Em construção">{texto}</span>'


def _sem_acento(texto: str) -> str:
    """Minúsculas e sem marcas combinantes (ordenação e busca do glossário)."""
    nfd = unicodedata.normalize("NFD", texto)
    return "".join(c for c in nfd if not unicodedata.combining(c)).casefold()


def modulos_por_termo(verbetes: List[dict]) -> Dict[str, List[str]]:
    """id do verbete -> slugs dos módulos cujo corpo o marca, na ordem de ESTUDOS_DADOS."""
    resultado: Dict[str, List[str]] = {v["id"]: [] for v in verbetes}
    catalogo = carregar_catalogo_estudos()
    for slug in ESTUDOS_DADOS:
        corpo = corpo_do_modulo(slug, catalogo)
        if corpo is None:
            continue
        _, ids = marcar_termos(corpo.read_text(encoding="utf-8"), verbetes)
        for i in ids:
            resultado[i].append(slug)
    return resultado


def _render_verbete(v: dict, por_id: Dict[str, dict], slugs: List[str], status_map: Dict[str, dict]) -> str:
    busca = " ".join(
        [v["termo"], v.get("sigla_de", ""), v.get("termo_ingles", ""), *v.get("variacoes", []),
         texto_sem_html(v["significado"])]
    )
    busca = escape(_sem_acento(busca), quote=True)
    campos = []

    def campo(rotulo: str, conteudo: str) -> None:
        campos.append(f"          <dt>{rotulo}</dt><dd>{conteudo}</dd>")

    if v.get("termo_ingles"):
        campo("Termo em inglês", escape(v["termo_ingles"]))
    campo("Significado", v["significado"])
    if v.get("explicacao"):
        campo("Explicação", v["explicacao"])
    if v.get("historico"):
        campo("Histórico", v["historico"])
    if v.get("variacoes"):
        campo("Variações", ", ".join(f"<code>{escape(x)}</code>" for x in v["variacoes"]))
    if v.get("relacionados"):
        links = ", ".join(
            f'<a href="#v-glossario/{escape(r, quote=True)}">{escape(por_id[r]["termo"] if r in por_id else r)}</a>'
            for r in v["relacionados"]
        )
        campo("Relacionados", links)
    if v.get("referencias"):
        itens = "".join(
            f'<li><a href="{escape(url, quote=True)}" target="_blank" rel="noopener">{escape(nome)}</a></li>'
            for nome, url in v["referencias"]
        )
        campo("Referências", f'<ul class="verbete-refs">{itens}</ul>')
    if slugs:
        chips = " ".join(render_chip_modulo(sl, status_map) for sl in slugs)
        campo("Aparece em", f'<span class="verbete-modulos">{chips}</span>')
    sigla = f'\n          <p class="verbete-sigla">{escape(v["sigla_de"])}</p>' if v.get("sigla_de") else ""
    vid = escape(v["id"], quote=True)
    return (
        f'        <article class="verbete" id="g-{vid}" data-busca="{busca}">\n'
        f'          <header><h3>{escape(v["termo"])}</h3> <span class="verbete-cat">{escape(v["categoria"])}</span></header>{sigla}\n'
        f'          <dl>\n' + "\n".join(campos) + "\n          </dl>\n        </article>"
    )


def render_glossario(verbetes: List[dict], aparece_em: Dict[str, List[str]], status_map: Dict[str, dict]) -> str:
    """Conteúdo da visão Glossário: busca, índice A–Z, grupos por letra e verbetes."""
    por_id = {v["id"]: v for v in verbetes}
    ordenados = sorted(verbetes, key=lambda v: (_sem_acento(v["termo"]), v["termo"]))
    grupos: Dict[str, List[dict]] = {}
    for v in ordenados:
        inicial = _sem_acento(v["termo"])[:1].upper()
        letra = inicial if "A" <= inicial <= "Z" else "#"
        grupos.setdefault(letra, []).append(v)
    letras = []
    for l in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        if l in grupos:
            letras.append(f'<a href="#v-glossario/letra-{l.lower()}">{l}</a>')
        else:
            letras.append(f'<span aria-disabled="true">{l}</span>')
    blocos = []
    for letra, vs in grupos.items():
        ident = "num" if letra == "#" else letra.lower()
        cartoes = "\n".join(_render_verbete(v, por_id, aparece_em.get(v["id"], []), status_map) for v in vs)
        blocos.append(
            f'      <section class="glossario-grupo" data-letra="{letra}">\n'
            f'        <h2 id="g-letra-{ident}">{letra}</h2>\n{cartoes}\n      </section>'
        )
    return (
        '      <label class="glossario-busca">\n'
        '        <span class="sr-only">Buscar no glossário</span>\n'
        '        <input type="search" id="busca-glossario" placeholder="Buscar termo, sigla ou significado…" autocomplete="off">\n'
        '      </label>\n'
        f'      <nav class="glossario-letras" aria-label="Índice por letra">{" ".join(letras)}</nav>\n'
        + "\n".join(blocos)
        + '\n      <p class="glossario-vazio" hidden>Nenhum termo encontrado.</p>'
    )


def render_rota_vaga(rota: List[dict], status_map: Dict[str, dict]) -> str:
    """Seção 'Rota por Vaga' com as competências e seus módulos."""
    cobertas = sum(
        1 for c in rota if any(status_map.get(s, {}).get("disponivel") for s in c["principais"])
    )
    artigos = []
    for c in rota:
        por_numero = lambda s: list(ESTUDOS_DADOS).index(s)  # noqa: E731
        chips = [render_chip_modulo(s, status_map) for s in sorted(c["principais"], key=por_numero)]
        chips += [render_chip_modulo(s, status_map, apoio=True) for s in sorted(c["apoio"], key=por_numero)]
        chips_html = "\n          ".join(chips)
        if c["texto_vaga"].strip().lower() == c["competencia"].strip().lower():
            texto_html = ""
        else:
            texto_html = f"\n        <p class=\"vaga-texto\">{escape(c['texto_vaga'])}</p>"
        artigos.append(f"""      <article class="vaga-competencia" id="vaga-{escape(c['id'], quote=True)}">
        <h3>{c['icone']} {escape(c['competencia'])}</h3>{texto_html}
        <div class="vaga-chips">
          {chips_html}
        </div>
      </article>""")
    corpo = "\n".join(artigos)
    return f"""    <section class="vaga-section" id="secao-rota-vaga">
      <div class="needs-header">
        <h2>🎯 Rota por Vaga: Analista de Segurança da Informação</h2>
        <p>{cobertas} de {len(rota)} competências com módulo disponível</p>
        <p class="vaga-legenda">Legenda:
          <span class="vaga-chip">módulo disponível (link)</span>
          <span class="vaga-chip pendente">⏳ em construção</span>
          <span class="vaga-chip apoio">apoio (módulo complementar)</span>
        </p>
      </div>
      <div class="vaga-grid">
{corpo}
      </div>
    </section>"""


def render_certificacoes(certs: List[dict], status_map: Dict[str, dict]) -> str:
    """Seção 'Matriz de Certificações' (tabela responsiva)."""
    linhas = []
    for c in certs:
        chips = " ".join(render_chip_modulo(s, status_map) for s in c["modulos"])
        linhas.append(f"""          <tr class="cert-row">
            <td data-label="Sigla"><strong>{escape(c['sigla'])}</strong><br><span class="cert-nome">{escape(c['nome'])}</span><br><a class="cert-site" href="{escape(c['site_oficial'], quote=True)}" target="_blank" rel="noopener noreferrer">site oficial</a></td>
            <td data-label="Órgão">{escape(c['orgao'])}</td>
            <td data-label="Foco">{escape(c['foco'])}</td>
            <td data-label="Experiência">{escape(c['experiencia'])}</td>
            <td data-label="Módulos"><div class="vaga-chips">{chips}</div></td>
          </tr>""")
    corpo = "\n".join(linhas)
    return f"""    <section class="vaga-section" id="secao-certificacoes">
      <div class="needs-header">
        <h2>🎓 Matriz de Certificações</h2>
        <p>Quais módulos preparam para cada certificação.</p>
      </div>
      <table class="cert-table">
        <thead>
          <tr><th>Sigla</th><th>Órgão</th><th>Foco</th><th>Experiência</th><th>Módulos</th></tr>
        </thead>
        <tbody>
{corpo}
        </tbody>
      </table>
      <p class="cert-nota">Confira os requisitos atuais no site oficial do órgão emissor.</p>
    </section>"""


# JavaScript do portal: armazenamento seguro, tema (chave cs_theme), status dos módulos,
# "Continuar estudando", agrupamento, busca, visões, gaveta do menu e progresso.
# `__DADOS_PORTAL__` é trocado pelo JSON de dados_portal().
PORTAL_JS = """
  // --------------------------------------------------------------------------
  // 0. Utilitários Seguros de Armazenamento Local (localStorage)
  // --------------------------------------------------------------------------
  function safeStorageGet(key) {
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        return window.localStorage.getItem(key);
      }
    } catch (e) {
      console.warn('[CS] Falha ao ler localStorage chave "' + key + '":', e);
    }
    return null;
  }

  function safeStorageSet(key, value) {
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        window.localStorage.setItem(key, String(value));
        return true;
      }
    } catch (e) {
      console.warn('[CS] Falha ao gravar localStorage chave "' + key + '":', e);
    }
    return false;
  }

  function safeStorageRemove(key) {
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        window.localStorage.removeItem(key);
        return true;
      }
    } catch (e) {
      console.warn('[CS] Falha ao remover localStorage chave "' + key + '":', e);
    }
    return false;
  }

  // Todas as chaves do localStorage (lista vazia se o armazenamento estiver bloqueado).
  function safeStorageKeys() {
    try {
      if (typeof window !== 'undefined' && window.localStorage) {
        const keys = [];
        for (let i = 0; i < window.localStorage.length; i++) keys.push(window.localStorage.key(i));
        return keys;
      }
    } catch (e) {
      console.warn('[CS] Falha ao listar localStorage:', e);
    }
    return [];
  }

  // --------------------------------------------------------------------------
  // 1. Normalização de Texto com Remoção de Acentos (Accent Folding)
  // --------------------------------------------------------------------------
  function removerAcentos(str) {
    if (!str) return '';
    return str.normalize('NFD').replace(/[\\u0300-\\u036f]/g, '').toLowerCase();
  }

  // --------------------------------------------------------------------------
  // 2. Tema (Claro / Escuro): mesmo mecanismo dos módulos (cs_theme)
  // --------------------------------------------------------------------------
  function temaDoSistema() {
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function temaAtual() {
    return safeStorageGet('cs_theme') || temaDoSistema();
  }

  function atualizarBotoesTema(tema) {
    document.querySelectorAll('.theme-toggle-btn').forEach(btn => {
      const escuro = tema === 'dark';
      btn.setAttribute('aria-label', escuro ? 'Alternar para tema claro' : 'Alternar para tema escuro');
      btn.innerHTML = escuro
        ? '<span class="theme-icon">☀️</span> <span class="theme-label">Claro</span>'
        : '<span class="theme-icon">🌙</span> <span class="theme-label">Escuro</span>';
    });
  }

  function applyTheme(tema) {
    if (tema === 'dark' || tema === 'light') {
      document.documentElement.setAttribute('data-theme', tema);
      atualizarBotoesTema(tema);
    } else {
      document.documentElement.removeAttribute('data-theme');
      atualizarBotoesTema(temaDoSistema());
    }
  }

  function toggleTheme() {
    const proximo = temaAtual() === 'dark' ? 'light' : 'dark';
    safeStorageSet('cs_theme', proximo);
    applyTheme(proximo);
  }

  function initTheme() {
    const salvo = safeStorageGet('cs_theme');
    if (salvo) applyTheme(salvo);
    else atualizarBotoesTema(temaAtual());
    if (window.matchMedia) {
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
        if (!safeStorageGet('cs_theme')) atualizarBotoesTema(temaDoSistema());
      });
    }
    document.querySelectorAll('.theme-toggle-btn').forEach(btn => btn.addEventListener('click', toggleTheme));
  }

  // --------------------------------------------------------------------------
  // 3. Busca: cartões do catálogo (data-busca) e itens das visões especiais
  // --------------------------------------------------------------------------
  function filtrarCards() {
    const input = document.getElementById('busca');
    const query = removerAcentos((input && input.value || '').trim());
    const soPend = document.getElementById('so-pendentes');
    const apenasPendentes = !!(soPend && soPend.checked);
    const slugsVisiveis = new Set();
    const slugsMostrados = new Set();

    document.querySelectorAll('.mc[data-slug]').forEach(card => {
      const slug = card.getAttribute('data-slug');
      const casaBusca = !query || removerAcentos(card.getAttribute('data-busca')).includes(query);
      if (casaBusca) slugsVisiveis.add(slug);
      const ok = casaBusca && !(apenasPendentes && safeStorageGet('cs_done_' + slug) === 'true');
      card.hidden = !ok;
      if (ok) slugsMostrados.add(slug);
    });
    const visiveis = slugsMostrados.size;
    document.querySelectorAll('#grupos .grupo').forEach(grupo => {
      grupo.hidden = !grupo.querySelector('.mc:not([hidden])');
    });

    const contagem = document.getElementById('contagem');
    if (contagem) contagem.textContent = visiveis + (visiveis === 1 ? ' módulo' : ' módulos');
    const vazio = document.getElementById('sem-resultados');
    if (vazio) vazio.hidden = visiveis > 0;
    const msgVazio = document.getElementById('sem-resultados-msg');
    if (msgVazio) {
      msgVazio.textContent = (!query && apenasPendentes)
        ? 'Todos os módulos deste filtro estão concluídos.'
        : 'Nenhum módulo encontrado com essa busca.';
    }

    filtrarSecoesRelacionadas(slugsVisiveis, query.length > 0);
  }

  // Necessidades, Rota da Vaga e Certificações seguem a busca dos cartões:
  // com busca ativa, só ficam os itens cujo data-slug está entre os módulos visíveis.
  // Grupos (competência, linha de certificação) e seções que ficam vazios somem.
  function filtrarSecoesRelacionadas(slugsVisiveis, filtroAtivo) {
    const mostra = el => !filtroAtivo || slugsVisiveis.has(el.getAttribute('data-slug'));

    const secaoComItens = (secaoId, grupoSel) => {
      const secao = document.getElementById(secaoId);
      if (!secao) return;
      let secaoTemItem = false;
      secao.querySelectorAll(grupoSel).forEach(grupo => {
        let grupoTemItem = false;
        grupo.querySelectorAll('[data-slug]').forEach(item => {
          const ok = mostra(item);
          item.style.display = ok ? '' : 'none';
          grupoTemItem = grupoTemItem || ok;
        });
        if (grupo !== secao) grupo.style.display = grupoTemItem ? '' : 'none';
        secaoTemItem = secaoTemItem || grupoTemItem;
      });
      secao.style.display = secaoTemItem ? '' : 'none';
    };

    secaoComItens('secao-necessidades', '.needs-grid');
    secaoComItens('secao-rota-vaga', '.vaga-competencia');
    secaoComItens('secao-certificacoes', '.cert-row');
  }

  function clearSearch() {
    const input = document.getElementById('busca');
    if (input) {
      input.value = '';
      input.focus();
    }
    const soPend = document.getElementById('so-pendentes');
    if (soPend) soPend.checked = false;
    filtrarCards();
  }

  // --------------------------------------------------------------------------
  // 4. Estado dos módulos (cs_done_, cs_read_, cs_check_, cs_quiz_, cs_last)
  // --------------------------------------------------------------------------
  const DADOS = __DADOS_PORTAL__;
  const ROTULOS_TIPO = {
    teoria: '📘 Teoria',
    laboratorio: '🧪 Laboratório',
    checklist: '☑️ Checklist',
    questoes: '❓ Questões de concurso',
    referencias: '📚 Referências'
  };
  const PREFIXOS_PROGRESSO = ['cs_done_', 'cs_read_', 'cs_check_', 'cs_quiz_'];

  function listaLida(slug) {
    const bruto = safeStorageGet('cs_read_' + slug);
    if (!bruto) return { presente: false, ids: [] };
    let ids = [];
    try {
      const v = JSON.parse(bruto);
      if (Array.isArray(v)) ids = v.filter(x => typeof x === 'string');
    } catch (e) { /* corrompido: conta como nenhuma seção lida */ }
    const conhecidas = DADOS.modulos[slug] && DADOS.modulos[slug].secoes;
    if (conhecidas) ids = ids.filter(id => Object.prototype.hasOwnProperty.call(conhecidas, id));
    return { presente: true, ids: Array.from(new Set(ids)) };
  }

  // Resume o progresso de um módulo a partir do localStorage.
  function estadoDoModulo(slug, totalSecoes, chaves) {
    if (safeStorageGet('cs_done_' + slug) === 'true') return { estado: 'concluido', pct: 100 };
    const lida = listaLida(slug);
    const prefChk = 'cs_check_' + slug + '_';
    const prefQuiz = 'cs_quiz_' + slug + '_';
    let checks = 0;
    let quiz = 0;
    let acertos = 0;
    chaves.forEach(k => {
      if (k.indexOf(prefChk) === 0 && safeStorageGet(k) === 'true') checks++;
      else if (k.indexOf(prefQuiz) === 0) {
        quiz++;
        if (safeStorageGet(k) === 'acertei') acertos++;
      }
    });
    const pct = totalSecoes > 0 ? Math.min(100, Math.round(100 * lida.ids.length / totalSecoes)) : 0;
    const andamento = lida.presente || checks > 0 || quiz > 0;
    return { estado: andamento ? 'andamento' : 'novo', pct: andamento ? pct : 0, checks, quiz, acertos };
  }

  function preencherStatus(card, est) {
    const el = card.querySelector('.mc-status');
    if (!el) return;
    el.textContent = '';
    el.className = 'mc-status';
    if (est.estado === 'concluido') {
      el.classList.add('concluido');
      el.textContent = '✓ Concluído';
    } else if (est.estado === 'andamento') {
      el.classList.add('andamento');
      el.appendChild(document.createTextNode('◐ ' + est.pct + '% lido'));
      const bar = document.createElement('span');
      bar.className = 'bar';
      const i = document.createElement('i');
      i.style.width = est.pct + '%';
      bar.appendChild(i);
      el.appendChild(bar);
    } else if (!card.classList.contains('pendente')) {
      el.classList.add('novo');
      el.textContent = '○ Não iniciado';
    }
  }

  function definirBarra(bar, valor, maximo) {
    if (!bar) return;
    const pct = maximo > 0 ? Math.round(100 * valor / maximo) : 0;
    bar.setAttribute('aria-valuenow', String(valor));
    const i = bar.querySelector('i');
    if (i) i.style.width = pct + '%';
  }

  function atualizarStatusCartoes() {
    const chaves = safeStorageKeys();
    const resumo = { concluidos: 0, andamento: 0, total: 0, estados: {} };
    document.querySelectorAll('.mc[data-slug]').forEach(card => {
      const slug = card.getAttribute('data-slug');
      let est = resumo.estados[slug];
      if (!est) {
        est = estadoDoModulo(slug, parseInt(card.getAttribute('data-secoes'), 10) || 0, chaves);
        resumo.total++;
        resumo.estados[slug] = est;
        if (est.estado === 'concluido') resumo.concluidos++;
        else if (est.estado === 'andamento') resumo.andamento++;
      }
      preencherStatus(card, est);
    });
    return resumo;
  }

  function atualizarProgressoGlobal(resumo) {
    const raiz = document.getElementById('progresso-global');
    if (!raiz) return;
    const c = raiz.querySelector('[data-gp="concluidos"]');
    if (c) c.textContent = String(resumo.concluidos);
    const a = raiz.querySelector('[data-gp="andamento"]');
    if (a) a.textContent = String(resumo.andamento);
    const barra = raiz.querySelector('.bar');
    definirBarra(barra, resumo.concluidos, resumo.total);
  }

  function atualizarGrupos() {
    document.querySelectorAll('#grupos .grupo').forEach(grupo => {
      const cards = Array.from(grupo.querySelectorAll('.mc[data-slug]'));
      const feitos = cards.filter(c => safeStorageGet('cs_done_' + c.getAttribute('data-slug')) === 'true').length;
      const p = grupo.querySelector('.grupo-cab .p');
      if (p) p.textContent = feitos + ' de ' + cards.length + ' concluídos';
    });
  }

  // "Continuar estudando": último módulo/seção aberto (cs_last).
  function atualizarContinuar(resumo) {
    const alvo = document.getElementById('continuar');
    if (!alvo) return;
    let ultimo = null;
    try {
      ultimo = JSON.parse(safeStorageGet('cs_last') || 'null');
    } catch (e) { ultimo = null; }
    const card = ultimo && typeof ultimo.slug === 'string'
      ? cartoesOrdem.find(c => c.getAttribute('data-slug') === ultimo.slug) : null;
    if (!card || !card.getAttribute('href')) {
      alvo.hidden = true;
      alvo.textContent = '';
      return;
    }
    const slug = ultimo.slug;
    const est = resumo.estados[slug] || { pct: 0, checks: 0, quiz: 0, acertos: 0 };
    const modulo = DADOS.modulos[slug] || { secoes: {}, chk: 0, q: 0 };
    const secaoId = typeof ultimo.secao === 'string' ? ultimo.secao : '';
    const tipo = modulo.secoes[secaoId];
    const rotulo = ROTULOS_TIPO[tipo] || secaoId || 'Início';

    const el = (tag, cls, texto) => {
      const n = document.createElement(tag);
      if (cls) n.className = cls;
      if (texto !== undefined) n.textContent = texto;
      return n;
    };
    const meta = el('div', 'meta');
    const item = (rot, valor) => {
      const s = el('span', '', rot + ' ');
      s.appendChild(el('b', '', valor));
      meta.appendChild(s);
    };
    item('Lido', (est.pct || 0) + '%');
    item('Parou em', rotulo);
    if (modulo.chk) item('Checklist', (est.checks || 0) + '/' + modulo.chk);
    if (modulo.q) item('Questões', (est.acertos || 0) + '/' + modulo.q);

    const texto = el('div');
    texto.appendChild(el('div', 'k', 'Continuar estudando'));
    texto.appendChild(el('h2', '', card.querySelector('.mc-titulo').textContent));
    const bar = el('div', 'bar');
    bar.setAttribute('role', 'progressbar');
    bar.setAttribute('aria-label', 'Leitura do módulo');
    bar.setAttribute('aria-valuemin', '0');
    bar.setAttribute('aria-valuemax', '100');
    bar.setAttribute('aria-valuenow', String(est.pct || 0));
    const i = document.createElement('i');
    i.style.width = (est.pct || 0) + '%';
    bar.appendChild(i);
    texto.appendChild(bar);
    texto.appendChild(meta);

    const link = el('a', 'btn btn-primary', 'Continuar');
    link.href = card.getAttribute('href') + (secaoId ? '#' + encodeURIComponent(secaoId) : '');

    alvo.textContent = '';
    alvo.setAttribute('data-trilha', card.getAttribute('data-trilha') || '');
    alvo.appendChild(texto);
    alvo.appendChild(link);
    alvo.hidden = false;
  }

  // Rotas sugeridas e Por certificação: progresso "X de N concluídos", passo feito e próximo.
  function atualizarPaineis() {
    ['secao-rota-sugerida', 'secao-cert-painel'].forEach(secaoId => {
      const secao = document.getElementById(secaoId);
      if (!secao) return;
      secao.querySelectorAll('.rota-sugerida').forEach(div => {
        const passos = Array.from(div.querySelectorAll('.rota-passo'));
        let feitos = 0;
        let proximo = null;
        passos.forEach(li => {
          const feito = safeStorageGet('cs_done_' + li.getAttribute('data-slug')) === 'true';
          li.classList.toggle('feito', feito);
          li.classList.remove('proximo');
          if (feito) feitos++;
          else if (!proximo) proximo = li;
        });
        if (proximo) proximo.classList.add('proximo');
        const pct = passos.length ? Math.round((feitos / passos.length) * 100) : 0;
        const barra = div.querySelector('.rota-progresso-barra');
        if (barra) barra.setAttribute('aria-valuenow', String(feitos));
        const cheio = div.querySelector('.rota-progresso-preenchido');
        if (cheio) cheio.style.width = pct + '%';
        const texto = div.querySelector('.rota-progresso-texto');
        if (texto) texto.textContent = feitos + ' de ' + passos.length + ' concluídos (' + pct + '%)';
        const prox = div.querySelector('.rota-proximo');
        if (prox) {
          prox.textContent = proximo
            ? 'Próximo módulo: ' + proximo.getAttribute('data-rotulo')
            : 'Tudo concluído! Todos os módulos foram marcados como estudados.';
        }
      });
    });
  }

  // Meu progresso: caixas de conclusão, resumo e barra.
  function atualizarMeuProgresso() {
    let feitos = 0;
    let total = 0;
    document.querySelectorAll('#progresso-lista input[data-slug]').forEach(cb => {
      const feito = safeStorageGet('cs_done_' + cb.getAttribute('data-slug')) === 'true';
      cb.checked = feito;
      total++;
      if (feito) feitos++;
    });
    const pct = total ? Math.round((feitos / total) * 100) : 0;
    const texto = document.getElementById('progresso-texto');
    if (texto) texto.textContent = feitos + ' de ' + total + ' concluídos (' + pct + '%)';
    definirBarra(document.querySelector('.progresso-resumo .bar'), feitos, total);
  }

  function atualizarTudo() {
    const resumo = atualizarStatusCartoes();
    atualizarProgressoGlobal(resumo);
    atualizarGrupos();
    atualizarContinuar(resumo);
    atualizarPaineis();
    atualizarMeuProgresso();
    filtrarCards();
  }

  function alternarConclusao(slug, feito) {
    if (feito) safeStorageSet('cs_done_' + slug, 'true');
    else safeStorageRemove('cs_done_' + slug);
    atualizarTudo();
  }

  // Zera só o progresso de estudo; mantém o tema. A confirmação é inline (sem diálogo).
  let zerarTimer = null;
  function restaurarBotaoZerar(btn) {
    if (zerarTimer) clearTimeout(zerarTimer);
    zerarTimer = null;
    btn.removeAttribute('data-confirmar');
    if (btn.dataset.rotuloOriginal) btn.textContent = btn.dataset.rotuloOriginal;
  }

  function zerarProgresso() {
    safeStorageKeys().forEach(k => {
      if (k === 'cs_last' || PREFIXOS_PROGRESSO.some(p => k.indexOf(p) === 0)) safeStorageRemove(k);
    });
    atualizarTudo();
  }

  function aoClicarZerar(e) {
    const btn = e.currentTarget;
    if (btn.getAttribute('data-confirmar') === 'true') {
      restaurarBotaoZerar(btn);
      zerarProgresso();
      return;
    }
    btn.dataset.rotuloOriginal = btn.textContent;
    btn.setAttribute('data-confirmar', 'true');
    btn.textContent = 'Confirmar? Clique de novo para zerar';
    zerarTimer = setTimeout(() => restaurarBotaoZerar(btn), 5000);
  }

  // --------------------------------------------------------------------------
  // 5. Agrupar o catálogo (trilha, nível, perfil, NIST)
  // --------------------------------------------------------------------------
  const ORDEM_NIST = ['Govern', 'Identify', 'Protect', 'Detect', 'Respond', 'Recover'];
  let cartoesOrdem = [];

  // Em trilha e nível cada módulo cai em um grupo; em perfil e NIST, em todos os que carrega.
  function chavesDoGrupo(modo, card) {
    if (modo === 'trilha') {
      const id = card.getAttribute('data-trilha');
      return [{ id, kicker: 'Trilha ' + id, nome: DADOS.trilhas[id] || id, attrs: { 'data-trilha': id } }];
    }
    if (modo === 'nivel') {
      const id = card.getAttribute('data-nivel');
      const par = DADOS.niveis.find(n => n[0] === id);
      return [{ id, kicker: 'Nível', nome: par ? par[1] : id, attrs: { 'data-nivel': id } }];
    }
    if (modo === 'perfil') {
      const nomes = (card.getAttribute('data-perfis') || '').split('|').map(x => x.trim()).filter(Boolean);
      return (nomes.length ? nomes : ['Outros']).map(nome => ({ id: nome, kicker: 'Perfil', nome, attrs: {} }));
    }
    const funcoes = (card.getAttribute('data-nist') || '').split('/').map(x => x.trim()).filter(Boolean);
    return (funcoes.length ? funcoes : ['Outros']).map(nome => ({ id: nome, kicker: 'NIST CSF 2.0', nome, attrs: {} }));
  }

  function ordemDoGrupo(modo, id) {
    if (modo === 'trilha') return parseInt(id, 10) || 0;
    if (modo === 'nivel') return DADOS.niveis.findIndex(n => n[0] === id);
    if (modo === 'perfil') { const k = DADOS.carreiras.indexOf(id); return k < 0 ? DADOS.carreiras.length : k; }
    const k = ORDEM_NIST.indexOf(id);
    return k < 0 ? ORDEM_NIST.length : k;
  }

  function agruparPor(modo) {
    const raiz = document.getElementById('grupos');
    if (!raiz) return;
    document.querySelectorAll('.agrupar button[data-grupo]').forEach(b => {
      b.setAttribute('aria-pressed', b.getAttribute('data-grupo') === modo ? 'true' : 'false');
    });
    const grupos = new Map();
    cartoesOrdem.forEach(card => {
      chavesDoGrupo(modo, card).forEach((info, n) => {
        if (!grupos.has(info.id)) grupos.set(info.id, { info, cards: [] });
        let alvo = card;
        if (n > 0) {
          alvo = card.cloneNode(true);
          alvo.removeAttribute('id');
          alvo.setAttribute('data-copia', 'true');
        }
        grupos.get(info.id).cards.push(alvo);
      });
    });
    const lista = Array.from(grupos.values()).sort((a, b) => {
      const d = ordemDoGrupo(modo, a.info.id) - ordemDoGrupo(modo, b.info.id);
      return d || String(a.info.nome).localeCompare(String(b.info.nome), 'pt-BR');
    });
    const frag = document.createDocumentFragment();
    lista.forEach(g => {
      const div = document.createElement('div');
      div.className = 'grupo';
      Object.keys(g.info.attrs).forEach(k => div.setAttribute(k, g.info.attrs[k]));
      const cab = document.createElement('div');
      cab.className = 'grupo-cab';
      const k = document.createElement('span');
      k.className = 'k';
      k.textContent = g.info.kicker;
      const h2 = document.createElement('h2');
      h2.textContent = g.info.nome;
      const p = document.createElement('span');
      p.className = 'p';
      cab.appendChild(k);
      cab.appendChild(h2);
      cab.appendChild(p);
      const grid = document.createElement('div');
      grid.className = 'grid';
      g.cards.forEach(c => grid.appendChild(c));
      div.appendChild(cab);
      div.appendChild(grid);
      frag.appendChild(div);
    });
    raiz.textContent = '';
    raiz.appendChild(frag);
    atualizarTudo();
  }

  // --------------------------------------------------------------------------
  // 6. Visões, gaveta do menu e atalhos
  // --------------------------------------------------------------------------
  function visaoDoHash() {
    const h = location.hash || '';
    if (h.indexOf('#v-') !== 0) return null;
    const v = h.slice(3).split('/')[0];
    const existe = Array.from(document.querySelectorAll('section.view')).some(s => s.getAttribute('data-view') === v);
    return existe ? v : null;
  }

  // Âncora de "#v-<visao>/<ancora>" (ex.: #v-glossario/hmac), ou ''.
  function ancoraDoHash() {
    const h = location.hash || '';
    const i = h.indexOf('/');
    if (h.indexOf('#v-') !== 0 || i < 0) return '';
    try { return decodeURIComponent(h.slice(i + 1)); } catch (e) { return ''; }
  }

  let destaqueTimer = null;
  function irParaAncora() {
    const ancora = ancoraDoHash();
    if (!ancora) return;
    // Um filtro ativo esconderia o alvo: limpa a busca do glossário antes de resolver a âncora.
    const campo = document.getElementById('busca-glossario');
    if (campo && campo.value) { campo.value = ''; filtrarGlossario(); }
    const alvo = document.getElementById('g-' + ancora);
    document.querySelectorAll('.verbete.destaque').forEach(el => el.classList.remove('destaque'));
    clearTimeout(destaqueTimer);
    if (!alvo || alvo.offsetParent === null) { window.scrollTo(0, 0); return; }
    alvo.scrollIntoView({ block: 'start' });
    if (!alvo.classList.contains('verbete')) return;  // letras do índice: só rola
    alvo.classList.add('destaque');
    destaqueTimer = setTimeout(() => alvo.classList.remove('destaque'), 2000);
  }

  function mostrarVisao(v) {
    document.querySelectorAll('section.view').forEach(s => { s.hidden = s.getAttribute('data-view') !== v; });
    document.querySelectorAll('.menu-lateral a[data-view]').forEach(a => {
      if (a.getAttribute('data-view') === v) a.setAttribute('aria-current', 'page');
      else a.removeAttribute('aria-current');
    });
  }

  function menuAberto() {
    return document.body.classList.contains('menu-aberto');
  }

  function abrirMenu() {
    const btn = document.querySelector('.menu-toggle');
    document.body.classList.add('menu-aberto');
    if (btn) {
      btn.setAttribute('aria-expanded', 'true');
      btn.setAttribute('aria-label', 'Fechar menu');
    }
    const atual = document.querySelector('.menu-lateral a[aria-current="page"]');
    if (atual) atual.focus();
  }

  function fecharMenu(devolverFoco) {
    const btn = document.querySelector('.menu-toggle');
    document.body.classList.remove('menu-aberto');
    if (btn) {
      btn.setAttribute('aria-expanded', 'false');
      btn.setAttribute('aria-label', 'Abrir menu');
      if (devolverFoco) btn.focus();
    }
  }

  function initNavegacao() {
    const btn = document.querySelector('.menu-toggle');
    if (btn) btn.addEventListener('click', () => { if (menuAberto()) fecharMenu(true); else abrirMenu(); });

    document.querySelectorAll('.menu-lateral a[data-view]').forEach(a => {
      a.addEventListener('click', e => {
        e.preventDefault();
        const v = a.getAttribute('data-view');
        mostrarVisao(v);
        if (location.hash !== '#v-' + v) location.hash = '#v-' + v;
        window.scrollTo(0, 0);
        if (menuAberto()) fecharMenu(true);
      });
    });
    window.addEventListener('hashchange', () => {
      mostrarVisao(visaoDoHash() || 'catalogo');
      irParaAncora();
    });
    const inicial = visaoDoHash();
    if (inicial) { mostrarVisao(inicial); irParaAncora(); }

    document.addEventListener('click', e => {
      if (!menuAberto()) return;
      if (e.target.closest && (e.target.closest('.side') || e.target.closest('.menu-toggle'))) return;
      fecharMenu(true);
    });
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape' && menuAberto()) {
        fecharMenu(true);
        return;
      }
      const alvo = e.target;
      const digitando = alvo && (alvo.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(alvo.tagName || ''));
      if (e.key === '/' && !digitando && !e.ctrlKey && !e.metaKey && !e.altKey) {
        const busca = document.getElementById('busca');
        if (busca) {
          e.preventDefault();
          busca.focus();
        }
      }
    });
  }

  // Glossário: filtra os verbetes por data-busca (sem acento) e esconde grupos vazios.
  function filtrarGlossario() {
    const campo = document.getElementById('busca-glossario');
    const query = removerAcentos((campo && campo.value || '').trim());
    let visiveis = 0;
    document.querySelectorAll('.glossario-grupo').forEach(grupo => {
      let n = 0;
      grupo.querySelectorAll('.verbete').forEach(v => {
        const casa = !query || (v.getAttribute('data-busca') || '').includes(query);
        v.hidden = !casa;
        if (casa) n++;
      });
      grupo.hidden = n === 0;
      visiveis += n;
    });
    const vazio = document.querySelector('.glossario-vazio');
    if (vazio) vazio.hidden = visiveis > 0;
  }

  document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    const buscaGlossario = document.getElementById('busca-glossario');
    if (buscaGlossario) buscaGlossario.addEventListener('input', filtrarGlossario);
    const input = document.getElementById('busca');
    if (input) input.addEventListener('input', filtrarCards);
    const limpar = document.getElementById('limpar-busca');
    if (limpar) limpar.addEventListener('click', clearSearch);

    cartoesOrdem = Array.from(document.querySelectorAll('.mc[data-slug]'));
    document.querySelectorAll('.agrupar button[data-grupo]').forEach(b => {
      b.addEventListener('click', () => agruparPor(b.getAttribute('data-grupo')));
    });
    const soPend = document.getElementById('so-pendentes');
    if (soPend) soPend.addEventListener('change', filtrarCards);
    document.querySelectorAll('#progresso-lista input[data-slug]').forEach(cb => {
      cb.addEventListener('change', () => alternarConclusao(cb.getAttribute('data-slug'), cb.checked));
    });
    const zerar = document.getElementById('zerar-progresso');
    if (zerar) zerar.addEventListener('click', aoClicarZerar);
    window.addEventListener('storage', atualizarTudo);
    window.addEventListener('pageshow', e => { if (e.persisted) atualizarTudo(); });

    initNavegacao();
    atualizarTudo();
  });
"""


def dados_portal() -> dict:
    """Dados estáticos lidos pelo JS do portal: nomes de grupos e seções/itens de cada módulo."""
    from index_dados import CARREIRAS

    modulos = {}
    for slug in ESTUDOS_DADOS:
        corpo = corpo_do_modulo(slug)
        if corpo is None:
            continue
        secoes = extrair_secoes(corpo.read_text(encoding="utf-8"))
        modulos[slug] = {
            "secoes": {s.id: s.tipo for s in secoes},
            "chk": sum(s.n_checklist for s in secoes),
            "q": sum(s.n_questoes for s in secoes),
        }
    return {
        "trilhas": {str(tid): info["nome"] for tid, info in TRILHAS.items()},
        "niveis": [[k, v] for k, v in NIVEIS.items()],
        "carreiras": [v["nome"] for v in CARREIRAS.values()],
        "modulos": modulos,
    }


def gerar_index_html(
    output_path: Optional[Path] = None,
    css_path: Optional[Path] = None,
) -> Path:
    """Gera o arquivo index.html completo e standalone na raiz do projeto."""
    out_file = Path(output_path) if output_path else DEFAULT_OUTPUT_HTML
    css_file = Path(css_path) if css_path else DEFAULT_INDEX_CSS

    # Fontes embutidas + tokens + CSS do portal, nessa ordem.
    css_partes = [css_fontes(), TOKENS_CSS.read_text(encoding="utf-8")]
    if css_file.exists():
        css_partes.append(css_file.read_text(encoding="utf-8"))
    css_content = "\n".join(css_partes)

    verbetes = carregar_glossario()
    catalogo = carregar_catalogo_estudos()
    stats = calcular_estatisticas(catalogo, ESTUDOS_DADOS)
    status_map = stats["status_map"]
    total = stats["total_estudos"]

    menu_html = render_menu_lateral({
        "catalogo": total,
        "rotas": len(ROTAS_PERFIL),
        "certificacoes": len(CERTIFICACOES),
        "necessidades": len(NECESSIDADES),
        "vaga": len(ROTA_VAGA),
        "glossario": len(verbetes),
    })
    progresso_global_html = render_progresso_global(stats)
    grupos_html = render_catalogo(ESTUDOS_DADOS, status_map)
    agrupar_html = "".join(
        f'<button type="button" data-grupo="{gid}" aria-pressed="{"true" if gid == "trilha" else "false"}">{rotulo}</button>'
        for gid, rotulo in GRUPOS_CATALOGO
    )
    painel_rotas_html = render_painel_rotas(ROTAS_PERFIL, status_map)
    painel_cert_html = render_painel_certificacoes(CERTIFICACOES, status_map)
    certificacoes_html = render_certificacoes(CERTIFICACOES, status_map)
    necessidades_html = render_necessidades_grid(NECESSIDADES, status_map)
    rota_vaga_html = render_rota_vaga(ROTA_VAGA, status_map)
    meu_progresso_html = render_meu_progresso(ESTUDOS_DADOS, status_map)
    glossario_html = render_glossario(verbetes, modulos_por_termo(verbetes), status_map)

    dados_json = json.dumps(dados_portal(), ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    portal_js = PORTAL_JS.replace("__DADOS_PORTAL__", dados_json)

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="Plataforma de estudos autoinstrucional e prática em cibersegurança com {total} módulos temáticos, {stats["total_trilhas"]} trilhas e simuladores interativos em JavaScript.">
  <title>Estudos de Cibersegurança — Catálogo e Portal Central</title>
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Cpath fill='%233b82f6' d='M32 4 8 14v16c0 15 10 26 24 30 14-4 24-15 24-30V14z'/%3E%3Cpath fill='%23ffffff' d='M28 40 19 31l4-4 5 5 13-13 4 4z'/%3E%3C/svg%3E">
  <style>
{css_content}
  </style>
</head>
<body>

<header class="topbar">
  <div class="topbar-in">
    <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="menu-lateral" aria-label="Abrir menu">☰</button>
    <a class="brand" href="index.html" aria-label="Estudos de Cibersegurança — início">
      <svg width="22" height="22" viewBox="0 0 64 64" aria-hidden="true"><path class="brand-escudo" d="M32 4 8 14v16c0 15 10 26 24 30 14-4 24-15 24-30V14z"/><path class="brand-check" d="M28 40 19 31l4-4 5 5 13-13 4 4z"/></svg>
      <span class="brand-nome">Estudos de Cibersegurança</span>
    </a>
    <label class="busca">
      <span class="busca-icone" aria-hidden="true">🔍</span>
      <input type="search" id="busca" placeholder="Buscar módulo, protocolo, CVE, norma…" aria-label="Buscar módulos" autocomplete="off">
      <kbd aria-hidden="true">/</kbd>
    </label>
    <button class="theme-toggle-btn" type="button" aria-label="Alternar tema"><span class="theme-icon">🌙</span> <span class="theme-label">Escuro</span></button>
  </div>
</header>

<div class="shell">
  <aside class="side" id="menu-lateral">
    <span class="lbl" id="menu-rotulo">Explorar</span>
    <nav class="menu-lateral" aria-label="Visões do portal">
{menu_html}
    </nav>
{progresso_global_html}
  </aside>

  <main class="main" id="conteudo">

    <!-- Visão: Catálogo (tela inicial) -->
    <section class="view" data-view="catalogo">
      <div class="catalogo" id="secao-catalogo">
        <h1>Catálogo de módulos</h1>
        <p class="lede">{total} módulos em {stats["total_trilhas"]} trilhas, com teoria, laboratório interativo, checklist e questões de concurso. Os simuladores são em JavaScript e tudo roda offline no seu navegador.</p>

        <div id="continuar" class="continuar" hidden></div>

        <div class="toolbar">
          <span class="l" id="agrupar-rotulo">Agrupar por</span>
          <div class="seg agrupar" role="group" aria-labelledby="agrupar-rotulo">{agrupar_html}</div>
          <label class="toggle"><input type="checkbox" id="so-pendentes"> Só não concluídos</label>
          <span class="count" id="contagem" aria-live="polite">{total} módulos</span>
        </div>

        <div id="grupos">
{grupos_html}
        </div>
        <div class="sem-resultados" id="sem-resultados" hidden>
          <p id="sem-resultados-msg">Nenhum módulo encontrado com essa busca.</p>
          <button type="button" class="btn" id="limpar-busca">Limpar busca e filtros</button>
        </div>
      </div>
    </section>

    <!-- Visão: Rotas sugeridas -->
    <section class="view" data-view="rotas" hidden>
      <h1>Rotas sugeridas</h1>
      <p class="lede">Sequências de estudo por perfil profissional. O próximo módulo de cada rota fica em destaque.</p>
{painel_rotas_html}
    </section>

    <!-- Visão: Por certificação -->
    <section class="view" data-view="certificacoes" hidden>
      <h1>Por certificação</h1>
      <p class="lede">Os módulos que preparam para cada prova, em ordem de estudo, e a matriz completa de certificações.</p>
{painel_cert_html}

{certificacoes_html}
    </section>

    <!-- Visão: Pela necessidade -->
    <section class="view" data-view="necessidades" hidden>
      <h1>Escolha pela necessidade prática</h1>
      <p class="lede">Enfrentando um desafio operacional ou projeto corporativo? Encontre o módulo que resolve.</p>
      <section class="needs-section" id="secao-necessidades">
        <div class="needs-grid">
{necessidades_html}
        </div>
      </section>
    </section>

    <!-- Visão: Rota por vaga -->
    <section class="view" data-view="vaga" hidden>
      <h1>Rota por vaga</h1>
      <p class="lede">As competências pedidas numa vaga real e os módulos que as cobrem.</p>
{rota_vaga_html}
    </section>

    <!-- Visão: Meu progresso -->
    <section class="view" data-view="progresso" hidden>
      <h1>Meu progresso</h1>
      <p class="lede">Marque os módulos que você concluiu. O progresso fica salvo só neste navegador.</p>
{meu_progresso_html}
    </section>

    <!-- Visão: Glossário -->
    <section class="view" data-view="glossario" hidden>
      <h1>Glossário</h1>
      <p class="lede">Siglas e termos técnicos usados nos módulos, com significado, histórico e onde aparecem.</p>
{glossario_html}
    </section>

    <footer class="portal-footer">
      <p>&copy; 2026 Estudos de Cibersegurança &bull; Material Autoinstrucional e Prático 100% Offline</p>
      <p>Curadoria e desenvolvimento técnico por <strong>José Mauro da Silva Brandão</strong> &bull; Alinhado a NIST CSF 2.0, MITRE ATT&amp;CK Enterprise, ISO/IEC 27001:2022 e LGPD (Lei nº 13.709/2018).</p>
    </footer>
  </main>
</div>

<script>
{portal_js}
</script>
</body>
</html>
"""

    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(html_content, encoding="utf-8")
    return out_file


def main(argv=None):
    """Ponto de entrada para execução via CLI."""
    parser = argparse.ArgumentParser(
        description="Construtor do Portal Central (index.html) para Estudos em Cibersegurança."
    )
    parser.add_argument(
        "saida",
        nargs="?",
        default=str(DEFAULT_OUTPUT_HTML),
        help="Caminho de saída para index.html (padrão: raiz do projeto).",
    )
    parser.add_argument(
        "--css",
        default=str(DEFAULT_INDEX_CSS),
        help="Caminho para index.css (padrão: _geradores/index.css).",
    )

    args = parser.parse_args(argv)
    output_path = Path(args.saida)
    css_path = Path(args.css)

    try:
        caminho_gerado = gerar_index_html(output_path=output_path, css_path=css_path)
    except GlossarioInvalido as e:
        print("\n".join(e.erros), file=sys.stderr)
        return 1
    print(f"[OK] Portal central gerado com sucesso em: {caminho_gerado}")


if __name__ == "__main__":
    sys.exit(main())
