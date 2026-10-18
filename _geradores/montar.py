#!/usr/bin/env python3
"""
Compilador de Treinamentos Standalone — Estudos em Cibersegurança
================================================================
Empacota fragmentos HTML de estudos (_body.html) em páginas HTML5
completas, independentes e 100% offline-ready, embutindo inlined o
Design System (base.css) e a biblioteca JavaScript reativa (base.js).

Uso via CLI:
    python3 _geradores/montar.py <caminho_body_html> [caminho_saida]
    python3 _geradores/montar.py _geradores/fundamentos_ciber_body.html

Uso como módulo:
    from montar import montar_treinamento
    montar_treinamento(body_path, output_path, titulo="...", meta={...})
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, Optional, Union

GERADORES_DIR = Path(__file__).resolve().parent
ROOT_DIR = GERADORES_DIR.parent
DEFAULT_ESTUDOS_TXT = GERADORES_DIR / "estudos.txt"
DEFAULT_BASE_CSS = GERADORES_DIR / "base.css"
DEFAULT_BASE_JS = GERADORES_DIR / "base.js"

if str(GERADORES_DIR) not in sys.path:
    sys.path.insert(0, str(GERADORES_DIR))

try:
    from diagramas import processar_diagramas_html
except ImportError:
    from _geradores.diagramas import processar_diagramas_html


def normalizar_chave(texto: str) -> str:
    """Normaliza identificador para correspondência insensível a formato e separadores."""
    s = texto.strip().lower()
    s = s.replace("_body.html", "").replace(".html", "").replace("_body", "")
    s = s.replace("treinamento-", "").replace("treinamento_", "")
    s = s.replace("-e-", "").replace("_e_", "")
    s = s.replace("-", "").replace("_", "")
    return s


def carregar_catalogo_estudos(caminho_estudos: Optional[Path] = None) -> Dict[str, dict]:
    """Lê e realiza o parse de estudos.txt, retornando dicionário mapeado por slug."""
    arquivo = Path(caminho_estudos) if caminho_estudos else DEFAULT_ESTUDOS_TXT
    if not arquivo.exists():
        return {}

    catalogo: Dict[str, dict] = {}
    with open(arquivo, mode="r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if not linha or linha.startswith("#"):
                continue
            partes = [p.strip() for p in linha.split("|")]
            if len(partes) >= 7:
                slug, titulo, pasta, arquivo_html, trilha_num, cor_tema, nist_fn = partes[:7]
                catalogo[slug] = {
                    "slug": slug,
                    "titulo": titulo,
                    "pasta": pasta,
                    "arquivo_html": arquivo_html,
                    "trilha_num": trilha_num,
                    "cor_tema": cor_tema,
                    "nist_fn": nist_fn,
                }
    return catalogo


def encontrar_estudo_por_slug_ou_arquivo(
    termo: str, catalogo: Optional[Dict[str, dict]] = None
) -> Optional[dict]:
    """Busca estudo no catálogo por correspondência exata ou normalizada."""
    if catalogo is None:
        catalogo = carregar_catalogo_estudos()

    # 1. Correspondência exata de chave
    if termo in catalogo:
        return catalogo[termo]

    # 2. Correspondência normalizada
    termo_norm = normalizar_chave(termo)
    for slug, dados in catalogo.items():
        if normalizar_chave(slug) == termo_norm:
            return dados
        if normalizar_chave(dados.get("pasta", "")) == termo_norm:
            return dados
        if normalizar_chave(dados.get("arquivo_html", "")) == termo_norm:
            return dados

    return None


def montar_treinamento(
    body_html_path: Union[str, Path],
    output_path: Union[str, Path],
    titulo: Optional[str] = None,
    meta: Optional[dict] = None,
    css_path: Optional[Path] = None,
    js_path: Optional[Path] = None,
    recompilar_diagramas: bool = False,
) -> Path:
    """Compila um fragmento HTML em um arquivo de treinamento standalone completo.

    Args:
        body_html_path: Caminho para o arquivo contendo o corpo HTML (_body.html).
        output_path: Caminho de destino para gravação do HTML compilado.
        titulo: Título da página/treinamento (opcional, extraído do catálogo se omitido).
        meta: Metadados contextuais opcionais (slug, trilha, nist, etc.).
        css_path: Caminho customizado para base.css (padrão: _geradores/base.css).
        js_path: Caminho customizado para base.js (padrão: _geradores/base.js).
        recompilar_diagramas: Se True, força a recompilação dos diagramas Mermaid ignorando cache.

    Returns:
        Path para o arquivo gerado.
    """
    body_path = Path(body_html_path).resolve()
    out_path = Path(output_path).resolve()

    if not body_path.exists():
        raise FileNotFoundError(f"Arquivo de corpo HTML não encontrado: {body_path}")

    # Leitura do CSS e JS para inlining
    css_file = Path(css_path) if css_path else DEFAULT_BASE_CSS
    js_file = Path(js_path) if js_path else DEFAULT_BASE_JS

    css_content = css_file.read_text(encoding="utf-8") if css_file.exists() else ""
    js_content = js_file.read_text(encoding="utf-8") if js_file.exists() else ""

    # Resolução de metadados
    meta_dict = dict(meta) if meta else {}
    catalogo = carregar_catalogo_estudos()
    busca_chave = meta_dict.get("slug") or body_path.name
    estudo_info = encontrar_estudo_por_slug_ou_arquivo(busca_chave, catalogo)

    slug = meta_dict.get("slug") or (estudo_info["slug"] if estudo_info else body_path.stem.replace("_body", ""))
    titulo_final = (
        titulo
        or meta_dict.get("titulo")
        or (estudo_info["titulo"] if estudo_info else slug.replace("-", " "))
    )
    trilha = str(
        meta_dict.get("trilha")
        or (estudo_info["trilha_num"] if estudo_info else "1")
    )

    # Leitura do conteúdo do corpo
    body_content = body_path.read_text(encoding="utf-8").strip()

    # Processamento e pré-compilação de diagramas Mermaid embutidos
    body_content = processar_diagramas_html(body_content, forcar=recompilar_diagramas)

    # Montagem do rodapé padronizado
    footer_html = """    <footer class="study-footer">
      <p>&copy; 2026 Estudos em Cibersegurança &bull; Material Autoinstrucional e Prático 100% Offline</p>
      <p><a href="../index.html">← Painel de Estudos</a> &bull; Curadoria e Desenvolvimento por José Mauro da Silva Brandão</p>
    </footer>"""

    # Estruturação do bloco de conteúdo
    if "<main" in body_content:
        if "study-footer" not in body_content and "<footer" not in body_content:
            if "</main>" in body_content:
                main_html = body_content.replace("</main>", f"{footer_html}\n  </main>")
            else:
                main_html = f"{body_content}\n{footer_html}"
        else:
            main_html = body_content
    else:
        conteudo_interno = [f"  <main class=\"container\">", body_content]
        if "study-footer" not in body_content and "<footer" not in body_content:
            conteudo_interno.append(footer_html)
        conteudo_interno.append("  </main>")
        main_html = "\n".join(conteudo_interno)

    # Shell HTML5 semântico completo
    html_template = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="study-slug" content="{slug}">
  <title>{titulo_final} — Estudos de Cibersegurança</title>

  <!-- Google Fonts: Barlow Semi Condensed, IBM Plex Sans, IBM Plex Mono -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Barlow+Semi+Condensed:ital,wght@0,600;0,700;0,800;1,700&family=IBM+Plex+Mono:ital,wght@0,400;0,500;0,600;1,400&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap" rel="stylesheet">

  <style>
{css_content}
  </style>
</head>
<body data-slug="{slug}">

  <!-- Barra de Navegação Superior e Breadcrumbs -->
  <header class="top-nav">
    <div class="top-nav-inner">
      <a href="../index.html" class="nav-back">← Painel de Estudos</a>
      <span class="nav-title">{titulo_final}</span>
      <div class="nav-actions">
        <span class="badge badge-t{trilha}">Trilha {trilha}</span>
        <button class="theme-toggle-btn" aria-label="Alternar tema" onclick="toggleTheme()">
          <span class="theme-icon">🌙</span> <span class="theme-label">Escuro</span>
        </button>
      </div>
    </div>
  </header>

  <!-- Conteúdo Principal do Treinamento -->
{main_html}

  <!-- Scripts Interativos Embutidos -->
  <script>
{js_content}
  </script>
</body>
</html>
"""

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html_template, encoding="utf-8")
    return out_path


def main(argv=None):
    """Ponto de entrada para execução via linha de comando."""
    parser = argparse.ArgumentParser(
        description="Compilador de Treinamentos Standalone (Estudos em Cibersegurança)."
    )
    parser.add_argument(
        "body_html",
        help="Caminho para o fragmento HTML do corpo (_body.html ou slug).",
    )
    parser.add_argument(
        "saida",
        nargs="?",
        default=None,
        help="Caminho de saída para o arquivo HTML compilado (opcional).",
    )
    parser.add_argument(
        "--titulo",
        default=None,
        help="Título opcional para sobrescrever o valor do catálogo.",
    )
    parser.add_argument(
        "--trilha",
        default=None,
        help="Número da trilha (1 a 7) para sobrescrever o valor do catálogo.",
    )
    parser.add_argument(
        "--recompilar-diagramas",
        action="store_true",
        default=False,
        help="Força a recompilação de diagramas Mermaid mesmo se estiverem em cache.",
    )

    args = parser.parse_args(argv)

    body_path = Path(args.body_html)
    # Se o caminho passado não existir diretamente, tenta buscar dentro de _geradores/
    if not body_path.exists():
        tentativa_geradores = GERADORES_DIR / body_path.name
        if tentativa_geradores.exists():
            body_path = tentativa_geradores

    catalogo = carregar_catalogo_estudos()
    estudo_info = encontrar_estudo_por_slug_ou_arquivo(body_path.name, catalogo)

    # Determinação do caminho de saída se não fornecido
    if args.saida:
        output_path = Path(args.saida)
    elif estudo_info:
        output_path = ROOT_DIR / estudo_info["pasta"] / estudo_info["arquivo_html"]
    else:
        nome_base = body_path.stem.replace("_body", "")
        output_path = Path(f"treinamento-{nome_base}.html")

    meta = {}
    if args.trilha:
        meta["trilha"] = args.trilha

    caminho_final = montar_treinamento(
        body_html_path=body_path,
        output_path=output_path,
        titulo=args.titulo,
        meta=meta,
        recompilar_diagramas=args.recompilar_diagramas,
    )

    print(f"[OK] Treinamento compilado com sucesso em: {caminho_final}")


if __name__ == "__main__":
    main()
