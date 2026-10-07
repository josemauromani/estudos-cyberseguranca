#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Construtor do Portal Central — Estudos em Cibersegurança
========================================================
Gera a página raiz index.html a partir de index_dados.py, index.css e do
status de compilação de cada um dos 28 estudos do catálogo.

Uso via CLI:
    python3 _geradores/build_index.py [caminho_saida]

Uso como módulo:
    from build_index import gerar_index_html
    gerar_index_html(output_path)
"""

import argparse
import os
import sys
from html import escape
from pathlib import Path
from typing import Dict, List, Optional

GERADORES_DIR = Path(__file__).resolve().parent
ROOT_DIR = GERADORES_DIR.parent
sys.path.insert(0, str(GERADORES_DIR))

from index_dados import (
    CARREIRAS,
    ESTUDOS_DADOS,
    FUNCOES_NIST,
    NECESSIDADES,
    TRILHAS,
)
from montar import carregar_catalogo_estudos

DEFAULT_INDEX_CSS = GERADORES_DIR / "index.css"
DEFAULT_OUTPUT_HTML = ROOT_DIR / "index.html"


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


def render_necessidades_grid(necessidades: List[dict]) -> str:
    """Gera o HTML da grade de desafios práticos do mundo real."""
    cards_html = []
    for item in necessidades:
        slug = item["slug"]
        desafio = escape(item["desafio"])
        cat = escape(item.get("categoria", "Segurança"))
        icone = item.get("icone", "🎯")
        estudo_info = ESTUDOS_DADOS.get(slug, {})
        titulo_estudo = escape(estudo_info.get("titulo", slug))

        card = f"""      <a href="#estudo-{slug}" class="need-card" onclick="focarEstudo('{slug}')">
        <span class="need-category">{icone} {cat}</span>
        <span class="need-title">{desafio}</span>
        <span class="need-target">→ Ver módulo: {titulo_estudo}</span>
      </a>"""
        cards_html.append(card)

    return "\n".join(cards_html)


def render_study_cards(
    catalogo: Dict[str, dict],
    dados: Dict[str, dict],
    status_map: Dict[str, dict],
) -> str:
    """Gera o HTML dos 28 cartões de estudos com metadados e simuladores."""
    cards_html = []

    for slug, d in dados.items():
        trilha_id = d["trilha"]
        trilha_info = TRILHAS.get(trilha_id, {})
        status_info = status_map.get(slug, {"disponivel": False, "caminho_relativo": ""})
        disponivel = status_info["disponivel"]
        link_estudo = status_info["caminho_relativo"]

        titulo = escape(d["titulo"])
        subtitulo = escape(d["subtitulo"])
        pergunta = escape(d["pergunta_chave"])
        simulador = escape(d["simulador_nome"])
        nist = escape(d["nist"])
        tempo = d["tempo_minutos"]
        carreiras_str = ",".join(d["carreiras"])

        # Lista de termos para busca em tempo real
        fatos_texto = " ".join(d["fatos"])
        search_terms = escape(
            f"{slug} {titulo} {subtitulo} {pergunta} {simulador} {nist} {carreiras_str} {fatos_texto}".lower()
        )

        fatos_li = "\n".join(
            f'          <li>{escape(fato)}</li>' for fato in d["fatos"]
        )

        if disponivel:
            badge_status = '<span class="status-badge pronto">Disponível</span>'
            btn_action = f'<a href="{link_estudo}" class="btn-open-study">Acessar Estudo →</a>'
        else:
            badge_status = '<span class="status-badge preparo">Em elaboração</span>'
            btn_action = '<span class="btn-disabled">Em elaboração</span>'

        card = f"""    <article class="study-card" id="estudo-{slug}"
      data-slug="{slug}"
      data-trilha="{trilha_id}"
      data-nist="{nist}"
      data-carreiras="{escape(carreiras_str)}"
      data-search="{search_terms}">
      
      <div class="card-header">
        <div class="card-tile-group">
          <div class="track-tile t{trilha_id}" title="Trilha {trilha_id}: {trilha_info.get('nome', '')}">
            {trilha_id}
          </div>
          <div class="card-badges">
            <span class="badge badge-nist">🛡️ NIST: {nist}</span>
            <span class="badge badge-time">⏱️ {tempo} min</span>
            <span class="badge badge-sim">🧪 {simulador}</span>
          </div>
        </div>
        {badge_status}
      </div>

      <h3 class="study-title">{titulo}</h3>
      <p class="study-desc">{subtitulo}</p>

      <div class="study-ask">
        <strong>Responde a:</strong>
        {pergunta}
      </div>

      <ul class="study-facts">
{fatos_li}
      </ul>

      <div class="card-actions">
        {btn_action}
        <label class="done-label">
          <input type="checkbox" data-slug="{slug}" onchange="toggleDone('{slug}', this.checked)">
          <span>Estudo Concluído</span>
        </label>
      </div>
    </article>"""
        cards_html.append(card)

    return "\n\n".join(cards_html)


def gerar_index_html(
    output_path: Optional[Path] = None,
    css_path: Optional[Path] = None,
) -> Path:
    """Gera o arquivo index.html completo e standalone na raiz do projeto."""
    out_file = Path(output_path) if output_path else DEFAULT_OUTPUT_HTML
    css_file = Path(css_path) if css_path else DEFAULT_INDEX_CSS

    css_content = css_file.read_text(encoding="utf-8") if css_file.exists() else ""
    catalogo = carregar_catalogo_estudos()
    stats = calcular_estatisticas(catalogo, ESTUDOS_DADOS)

    necessidades_html = render_necessidades_grid(NECESSIDADES)
    cards_html = render_study_cards(catalogo, ESTUDOS_DADOS, stats["status_map"])

    # JavaScript do Portal Central
    portal_js = """
  // Gerenciador de Tema (Claro / Escuro)
  function initTheme() {
    const savedTheme = localStorage.getItem('cs_theme');
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    const theme = savedTheme || (prefersDark ? 'dark' : 'light');
    applyTheme(theme);
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('cs_theme', theme);
    const icon = document.querySelector('.theme-icon');
    const label = document.querySelector('.theme-label');
    if (icon && label) {
      if (theme === 'dark') {
        icon.textContent = '☀️';
        label.textContent = 'Claro';
      } else {
        icon.textContent = '🌙';
        label.textContent = 'Escuro';
      }
    }
  }

  function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
    applyTheme(nextTheme);
  }

  // Gerenciador de Progresso Global do Estudante
  const TOTAL_ESTUDOS = 28;

  function initProgress() {
    let concluidos = 0;
    const cards = document.querySelectorAll('.study-card');
    
    cards.forEach(card => {
      const slug = card.getAttribute('data-slug');
      const isDone = localStorage.getItem('cs_done_' + slug) === 'true';
      const checkbox = card.querySelector('input[type="checkbox"]');
      if (checkbox) {
        checkbox.checked = isDone;
      }
      if (isDone) {
        card.classList.add('card-done');
        concluidos++;
      } else {
        card.classList.remove('card-done');
      }
    });

    updateProgressUI(concluidos);
  }

  function toggleDone(slug, isDone) {
    if (isDone) {
      localStorage.setItem('cs_done_' + slug, 'true');
    } else {
      localStorage.removeItem('cs_done_' + slug);
    }
    const card = document.getElementById('estudo-' + slug);
    if (card) {
      if (isDone) {
        card.classList.add('card-done');
      } else {
        card.classList.remove('card-done');
      }
    }
    initProgress();
  }

  function resetProgress() {
    if (confirm('Deseja realmente zerar todo o progresso de estudos concluídos registrado neste navegador?')) {
      const cards = document.querySelectorAll('.study-card');
      cards.forEach(card => {
        const slug = card.getAttribute('data-slug');
        localStorage.removeItem('cs_done_' + slug);
      });
      initProgress();
    }
  }

  function updateProgressUI(concluidos) {
    const pct = Math.round((concluidos / TOTAL_ESTUDOS) * 100);
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    if (progressBar) {
      progressBar.style.width = pct + '%';
    }
    if (progressText) {
      progressText.innerHTML = `<strong>${concluidos}</strong> de <strong>${TOTAL_ESTUDOS}</strong> concluídos (${pct}%)`;
    }
  }

  // Filtros Multifacetados e Busca em Tempo Real
  let currentFacet = 'todas';
  let currentFilterValue = 'all';

  function switchTab(facetName) {
    currentFacet = facetName;
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-facet') === facetName);
    });

    document.querySelectorAll('.filter-subpanel').forEach(panel => {
      panel.style.display = panel.getAttribute('data-panel') === facetName ? 'flex' : 'none';
    });

    currentFilterValue = 'all';
    document.querySelectorAll(`.filter-subpanel[data-panel="${facetName}"] .filter-badge`).forEach(b => {
      b.classList.toggle('active', b.getAttribute('data-value') === 'all');
    });

    filtrarCards();
  }

  function setSubFilter(value, element) {
    currentFilterValue = value;
    const parent = element.parentElement;
    parent.querySelectorAll('.filter-badge').forEach(b => b.classList.remove('active'));
    element.classList.add('active');
    filtrarCards();
  }

  function filtrarCards() {
    const query = (document.getElementById('search-input').value || '').trim().toLowerCase();
    const clearBtn = document.querySelector('.clear-search-btn');
    if (clearBtn) {
      clearBtn.style.display = query.length > 0 ? 'block' : 'none';
    }

    const cards = document.querySelectorAll('.study-card');
    let visibleCount = 0;

    cards.forEach(card => {
      const cardSearch = card.getAttribute('data-search') || '';
      const cardTrilha = card.getAttribute('data-trilha');
      const cardNist = card.getAttribute('data-nist');
      const cardCarreiras = card.getAttribute('data-carreiras') || '';

      let matchSearch = !query || cardSearch.includes(query);
      let matchFacet = true;

      if (currentFacet === 'trilhas' && currentFilterValue !== 'all') {
        matchFacet = cardTrilha === currentFilterValue;
      } else if (currentFacet === 'nist' && currentFilterValue !== 'all') {
        matchFacet = cardNist.includes(currentFilterValue);
      } else if (currentFacet === 'carreiras' && currentFilterValue !== 'all') {
        matchFacet = cardCarreiras.includes(currentFilterValue);
      }

      if (matchSearch && matchFacet) {
        card.style.display = 'flex';
        visibleCount++;
      } else {
        card.style.display = 'none';
      }
    });

    const info = document.getElementById('visible-count');
    if (info) {
      info.textContent = `Exibindo ${visibleCount} de ${TOTAL_ESTUDOS} estudos`;
    }

    const noResults = document.getElementById('no-results-msg');
    if (noResults) {
      noResults.style.display = visibleCount === 0 ? 'block' : 'none';
    }
  }

  function clearSearch() {
    const input = document.getElementById('search-input');
    if (input) {
      input.value = '';
      input.focus();
      filtrarCards();
    }
  }

  function focarEstudo(slug) {
    const card = document.getElementById('estudo-' + slug);
    if (card) {
      card.style.display = 'flex';
      card.scrollIntoView({ behavior: 'smooth', block: 'center' });
      card.classList.add('highlight-pulse');
      setTimeout(() => card.classList.remove('highlight-pulse'), 2000);
    }
  }

  // Inicialização no Carregamento do DOM
  document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initProgress();
    
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
      searchInput.addEventListener('input', filtrarCards);
    }

    // Suporte a âncora direta na URL (ex: #estudo-Fundamentos-Ciber)
    if (window.location.hash) {
      const hashId = window.location.hash.substring(1);
      const target = document.getElementById(hashId);
      if (target) {
        setTimeout(() => target.scrollIntoView({ behavior: 'smooth', block: 'center' }), 100);
      }
    }
  });
"""

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="Plataforma de estudos autoinstrucional e prática em cibersegurança com 28 módulos temáticos, 6 trilhas e simuladores interativos em JavaScript.">
  <title>Estudos de Cibersegurança — Catálogo e Portal Central</title>

  <!-- Google Fonts: Barlow Semi Condensed, IBM Plex Sans, IBM Plex Mono -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Barlow+Semi+Condensed:ital,wght@0,600;0,700;0,800;1,700&family=IBM+Plex+Mono:ital,wght@0,400;0,500;0,600;1,400&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap" rel="stylesheet">

  <style>
{css_content}
  </style>
</head>
<body>

  <div class="portal-container">

    <!-- Masthead e Identidade da Plataforma -->
    <header class="masthead">
      <div class="masthead-top">
        <div>
          <p class="kicker">Plataforma Autoinstrucional &bull; 100% Offline &bull; Prática em JavaScript</p>
          <h1>Estudos de Cibersegurança</h1>
        </div>
        <button class="theme-toggle-btn" aria-label="Alternar tema" onclick="toggleTheme()">
          <span class="theme-icon">🌙</span> <span class="theme-label">Escuro</span>
        </button>
      </div>

      <p class="lead">
        Formação técnica de alto nível em segurança defensiva, ofensiva, arquitetura, operações de SOC, governança e riscos cibernéticos, com fundamentação normativa (NIST CSF 2.0 / MITRE ATT&amp;CK) e simuladores práticos interativos em Vanilla JS.
      </p>

      <div class="byline">
        Curadoria e Desenvolvimento Técnico por <strong>José Mauro da Silva Brandão</strong> &bull; Edição 2026
      </div>

      <!-- Barra de Estatísticas do Portal -->
      <div class="stats-bar">
        <div class="stat-item">
          <span class="stat-number">{stats["total_estudos"]}</span>
          <span class="stat-label">Estudos Mapeados</span>
        </div>
        <div class="stat-item">
          <span class="stat-number">{stats["total_trilhas"]}</span>
          <span class="stat-label">Trilhas Temáticas</span>
        </div>
        <div class="stat-item">
          <span class="stat-number">{stats["total_simuladores"]}</span>
          <span class="stat-label">Simuladores Interativos</span>
        </div>
        <div class="stat-item">
          <span class="stat-number">~{stats["tempo_total_minutos"]} min</span>
          <span class="stat-label">Tempo Total ({stats["horas_totais"]}h)</span>
        </div>
        <div class="stat-item">
          <span class="stat-number">{stats["estudos_disponiveis"]} / {stats["total_estudos"]}</span>
          <span class="stat-label">Módulos Compilados</span>
        </div>
      </div>
    </header>

    <!-- Rastreador de Progresso Global do Estudante -->
    <section class="progress-section" aria-label="Progresso global">
      <div class="progress-header">
        <h2 class="progress-title">🎯 Progresso de Conclusão Global</h2>
        <span class="progress-metrics" id="progress-text">0 de 28 concluídos (0%)</span>
      </div>
      <div class="progress-bar-track">
        <div class="progress-bar-fill" id="progress-bar"></div>
      </div>
      <div class="progress-actions">
        <button class="btn-reset-progress" onclick="resetProgress()">Zerar progresso salvo no navegador</button>
      </div>
    </section>

    <!-- Controles de Busca e Filtros Multifacetados -->
    <section class="controls-section" aria-label="Filtros e busca">
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input type="text" id="search-input" placeholder="Buscar por palavra-chave, protocolo, comando, CVE, simulador ou norma..." aria-label="Buscar estudos">
        <button class="clear-search-btn" aria-label="Limpar busca" onclick="clearSearch()">&times;</button>
      </div>

      <!-- Abas de Navegação -->
      <nav class="filter-tabs" aria-label="Abas de filtragem">
        <button class="tab-btn active" data-facet="todas" onclick="switchTab('todas')">Todas as Trilhas</button>
        <button class="tab-btn" data-facet="trilhas" onclick="switchTab('trilhas')">Por Trilha Temática</button>
        <button class="tab-btn" data-facet="carreiras" onclick="switchTab('carreiras')">Por Perfil Profissional</button>
        <button class="tab-btn" data-facet="nist" onclick="switchTab('nist')">Por Função NIST CSF 2.0</button>
      </nav>

      <!-- Painel: Por Trilha -->
      <div class="filter-subpanel" data-panel="trilhas" style="display: none;">
        <button class="filter-badge active" data-value="all" onclick="setSubFilter('all', this)">Todas as Trilhas</button>
        <button class="filter-badge" data-value="1" onclick="setSubFilter('1', this)">Trilha 1: Fundamentos &amp; Redes</button>
        <button class="filter-badge" data-value="2" onclick="setSubFilter('2', this)">Trilha 2: Segurança Defensiva</button>
        <button class="filter-badge" data-value="3" onclick="setSubFilter('3', this)">Trilha 3: Segurança Ofensiva</button>
        <button class="filter-badge" data-value="4" onclick="setSubFilter('4', this)">Trilha 4: Operações &amp; SOC</button>
        <button class="filter-badge" data-value="5" onclick="setSubFilter('5', this)">Trilha 5: Especialidades</button>
        <button class="filter-badge" data-value="6" onclick="setSubFilter('6', this)">Trilha 6: Governança &amp; Riscos</button>
      </div>

      <!-- Painel: Por Perfil Profissional -->
      <div class="filter-subpanel" data-panel="carreiras" style="display: none;">
        <button class="filter-badge active" data-value="all" onclick="setSubFilter('all', this)">Todos os Perfis</button>
        <button class="filter-badge" data-value="Blue Team &amp; Defesa" onclick="setSubFilter('Blue Team &amp; Defesa', this)">🛡️ Blue Team</button>
        <button class="filter-badge" data-value="Red Team &amp; Pentest" onclick="setSubFilter('Red Team &amp; Pentest', this)">⚔️ Red Team</button>
        <button class="filter-badge" data-value="AppSec &amp; DevSecOps" onclick="setSubFilter('AppSec &amp; DevSecOps', this)">💻 AppSec / DevSecOps</button>
        <button class="filter-badge" data-value="Operações SOC &amp; Resposta" onclick="setSubFilter('Operações SOC &amp; Resposta', this)">👁️ SOC &amp; Resposta</button>
        <button class="filter-badge" data-value="GRC &amp; Auditoria" onclick="setSubFilter('GRC &amp; Auditoria', this)">📋 GRC &amp; Auditoria</button>
        <button class="filter-badge" data-value="Perícia Forense &amp; Malware" onclick="setSubFilter('Perícia Forense &amp; Malware', this)">🔍 Forense Digital</button>
      </div>

      <!-- Painel: Por Função NIST CSF 2.0 -->
      <div class="filter-subpanel" data-panel="nist" style="display: none;">
        <button class="filter-badge active" data-value="all" onclick="setSubFilter('all', this)">Todas as Funções</button>
        <button class="filter-badge" data-value="Govern" onclick="setSubFilter('Govern', this)">🏛️ Govern (GV)</button>
        <button class="filter-badge" data-value="Identify" onclick="setSubFilter('Identify', this)">🔎 Identify (ID)</button>
        <button class="filter-badge" data-value="Protect" onclick="setSubFilter('Protect', this)">🛡️ Protect (PR)</button>
        <button class="filter-badge" data-value="Detect" onclick="setSubFilter('Detect', this)">👁️ Detect (DE)</button>
        <button class="filter-badge" data-value="Respond" onclick="setSubFilter('Respond', this)">🚨 Respond (RS)</button>
        <button class="filter-badge" data-value="Recover" onclick="setSubFilter('Recover', this)">🔄 Recover (RC)</button>
      </div>

      <div class="results-info">
        <span id="visible-count">Exibindo {stats["total_estudos"]} de {stats["total_estudos"]} estudos</span>
        <span>Atalhos: clique nas tags ou use o campo de busca</span>
      </div>
    </section>

    <!-- Seção: Escolha pela Necessidade Prática -->
    <section class="needs-section" id="secao-necessidades">
      <div class="needs-header">
        <h2>🧭 Escolha pela Necessidade Prática</h2>
        <p>Enfrentando um desafio operacional ou projeto corporativo? Encontre a solução direta no catálogo:</p>
      </div>
      <div class="needs-grid">
{necessidades_html}
      </div>
    </section>

    <!-- Seção Principal: Catálogo dos 28 Estudos -->
    <main class="studies-section" id="secao-catalogo">
      <div class="section-title-wrap">
        <h2 class="section-title">📚 Módulos e Treinamentos Práticos</h2>
      </div>

      <div class="cards-grid" id="cards-grid">
{cards_html}

        <div class="no-results" id="no-results-msg" style="display: none;">
          <p>Nenhum estudo encontrado com os critérios de busca aplicados.</p>
          <button class="btn-open-study" onclick="clearSearch(); switchTab('todas');">Limpar Filtros e Busca</button>
        </div>
      </div>
    </main>

    <!-- Rodapé Geral do Portal -->
    <footer class="portal-footer">
      <p>&copy; 2026 Estudos de Cibersegurança &bull; Material Autoinstrucional e Prático 100% Offline</p>
      <p>Desenvolvido e mantido por <strong>José Mauro da Silva Brandão</strong> &bull; Alinhado a NIST CSF 2.0, MITRE ATT&amp;CK Enterprise, ISO/IEC 27001:2022 e LGPD (Lei nº 13.709/2018).</p>
    </footer>

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

    caminho_gerado = gerar_index_html(output_path=output_path, css_path=css_path)
    print(f"[OK] Portal central gerado com sucesso em: {caminho_gerado}")


if __name__ == "__main__":
    main()
