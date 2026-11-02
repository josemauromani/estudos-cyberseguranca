#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Construtor do Portal Central — Estudos em Cibersegurança
========================================================
Gera a página raiz index.html a partir de index_dados.py, das fontes embutidas,
de tokens.css, de index.css e do status de compilação de cada estudo do catálogo.

Estrutura: barra superior (menu, marca, busca, tema) + menu lateral com seis visões
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
import sys
from functools import lru_cache
from html import escape
from pathlib import Path
from typing import Dict, List, Optional

GERADORES_DIR = Path(__file__).resolve().parent
ROOT_DIR = GERADORES_DIR.parent
sys.path.insert(0, str(GERADORES_DIR))

from contrato import extrair_secoes
from fontes import css_fontes
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
    certs_str = escape(" ".join(c["sigla"] for c in CERTIFICACOES if slug in c["modulos"]), quote=True)
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
            <td data-label="Sigla"><strong>{escape(c['sigla'])}</strong><br><span class="cert-nome">{escape(c['nome'])}</span></td>
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


# JavaScript do portal. Nesta etapa: armazenamento seguro, tema (mesmo mecanismo dos
# módulos: chave cs_theme, sem data-theme enquanto o leitor não escolher) e a busca,
# que filtra os cartões do catálogo e os itens com data-slug das visões especiais.
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
    const slugsVisiveis = new Set();
    let visiveis = 0;

    document.querySelectorAll('.mc[data-slug]').forEach(card => {
      const ok = !query || removerAcentos(card.getAttribute('data-busca')).includes(query);
      card.hidden = !ok;
      if (ok) {
        visiveis++;
        slugsVisiveis.add(card.getAttribute('data-slug'));
      }
    });
    document.querySelectorAll('#grupos .grupo').forEach(grupo => {
      grupo.hidden = !grupo.querySelector('.mc:not([hidden])');
    });

    const contagem = document.getElementById('contagem');
    if (contagem) contagem.textContent = visiveis + (visiveis === 1 ? ' módulo' : ' módulos');
    const vazio = document.getElementById('sem-resultados');
    if (vazio) vazio.hidden = visiveis > 0;

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
      filtrarCards();
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    const input = document.getElementById('busca');
    if (input) input.addEventListener('input', filtrarCards);
    const limpar = document.getElementById('limpar-busca');
    if (limpar) limpar.addEventListener('click', clearSearch);
  });
"""


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
          <p>Nenhum módulo encontrado com essa busca.</p>
          <button type="button" class="btn" id="limpar-busca">Limpar busca</button>
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

    <footer class="portal-footer">
      <p>&copy; 2026 Estudos de Cibersegurança &bull; Material Autoinstrucional e Prático 100% Offline</p>
      <p>Curadoria e desenvolvimento técnico por <strong>José Mauro da Silva Brandão</strong> &bull; Alinhado a NIST CSF 2.0, MITRE ATT&amp;CK Enterprise, ISO/IEC 27001:2022 e LGPD (Lei nº 13.709/2018).</p>
    </footer>
  </main>
</div>

<script>
{PORTAL_JS}
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

    caminho_gerado = gerar_index_html(output_path=output_path, css_path=css_path)
    print(f"[OK] Portal central gerado com sucesso em: {caminho_gerado}")


if __name__ == "__main__":
    main()
