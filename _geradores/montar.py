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
from html import escape
from pathlib import Path
from typing import Dict, Optional, Union

GERADORES_DIR = Path(__file__).resolve().parent
ROOT_DIR = GERADORES_DIR.parent
DEFAULT_ESTUDOS_TXT = GERADORES_DIR / "estudos.txt"
DEFAULT_BASE_CSS = GERADORES_DIR / "base.css"
TOKENS_CSS = GERADORES_DIR / "tokens.css"
LABORATORIO_CSS = GERADORES_DIR / "laboratorio.css"
DEFAULT_BASE_JS = GERADORES_DIR / "base.js"

if str(GERADORES_DIR) not in sys.path:
    sys.path.insert(0, str(GERADORES_DIR))

try:
    from diagramas import processar_diagramas_html
except ImportError:
    from _geradores.diagramas import processar_diagramas_html

from chassi import (
    aplicar_cabecalhos_de_secao,
    gerar_cabecalho,
    gerar_fim,
    gerar_sumario,
    gerar_topbar,
    SlugSemDados,
    info_modulo,
    inserir_fim,
    numerar_questoes,
)
from contrato import ContratoInvalido, extrair_secoes, validar_corpo
from glossario import (
    GlossarioInvalido,
    bloco_dados_glossario,
    carregar_glossario,
    marcar_termos,
)


def carregar_css(base_css: Optional[Path] = None) -> str:
    """Monta o CSS inline: fontes embutidas + tokens + base + laboratório (se existir)."""
    from fontes import css_fontes

    base = Path(base_css) if base_css else DEFAULT_BASE_CSS
    partes = [css_fontes()]
    for arquivo in (TOKENS_CSS, base, LABORATORIO_CSS):
        if arquivo.exists():
            partes.append(arquivo.read_text(encoding="utf-8"))
    return "\n".join(partes)


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
    cache_diagramas: Optional[Path] = None,
) -> Path:
    """Compila um fragmento HTML em um arquivo de treinamento standalone completo.

    Args:
        body_html_path: Caminho para o arquivo contendo o corpo HTML (_body.html).
        output_path: Caminho de destino para gravação do HTML compilado.
        titulo: Título da página/treinamento (opcional, extraído do catálogo se omitido).
        meta: Metadados contextuais opcionais (slug, titulo).
        css_path: Caminho customizado para base.css (padrão: _geradores/base.css; tokens e fontes são sempre incluídos).
        js_path: Caminho customizado para base.js (padrão: _geradores/base.js).
        recompilar_diagramas: Se True, força a recompilação dos diagramas Mermaid ignorando cache.
        cache_diagramas: Diretório do cache de SVGs (padrão: _geradores/cache_diagramas).

    Returns:
        Path para o arquivo gerado.
    """
    body_path = Path(body_html_path).resolve()
    out_path = Path(output_path).resolve()

    if not body_path.exists():
        raise FileNotFoundError(f"Arquivo de corpo HTML não encontrado: {body_path}")

    # Leitura do CSS e JS para inlining
    js_file = Path(js_path) if js_path else DEFAULT_BASE_JS

    css_content = carregar_css(Path(css_path) if css_path else DEFAULT_BASE_CSS)
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

    # Leitura e validação do corpo contra o contrato de markup
    body_content = body_path.read_text(encoding="utf-8").strip()
    erros = validar_corpo(body_content, slug)
    if erros:
        raise ContratoInvalido(erros)
    secoes = extrair_secoes(body_content)

    # Glossário: marca a 1ª ocorrência de cada termo por seção e embute os verbetes usados
    verbetes = carregar_glossario()
    body_content, ids_glossario = marcar_termos(body_content, verbetes)
    bloco_glossario = bloco_dados_glossario(ids_glossario, verbetes)

    # Processamento e pré-compilação de diagramas Mermaid embutidos
    body_content = processar_diagramas_html(
        body_content, cache_dir=cache_diagramas, forcar=recompilar_diagramas
    )

    # Chassi: dados do módulo, cabeçalhos de seção, questões numeradas e fim do módulo
    info = info_modulo(slug)
    body_content = aplicar_cabecalhos_de_secao(body_content, secoes)
    body_content = numerar_questoes(body_content)
    body_content = inserir_fim(body_content, gerar_fim(info))
    main_html = (
        '<div class="shell">\n'
        f"{gerar_sumario(info, secoes)}\n"
        '<main class="content">\n'
        f"{gerar_cabecalho(info, secoes)}\n"
        f"{body_content}\n"
        "</main>\n</div>"
    )

    # Shell HTML5 semântico completo
    html_template = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="study-slug" content="{slug}">
  <title>{escape(titulo_final)} — Estudos de Cibersegurança</title>
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Cpath fill='%233b82f6' d='M32 4 8 14v16c0 15 10 26 24 30 14-4 24-15 24-30V14z'/%3E%3Cpath fill='%23ffffff' d='M28 40 19 31l4-4 5 5 13-13 4 4z'/%3E%3C/svg%3E">


  <style>
{css_content}
  </style>
</head>
<body data-slug="{slug}">

  {gerar_topbar(info)}

{main_html}

  {bloco_glossario}
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
        "--recompilar-diagramas",
        action="store_true",
        default=False,
        help="Força a recompilação de diagramas Mermaid mesmo se estiverem em cache.",
    )
    parser.add_argument(
        "--cache-diagramas",
        default=None,
        help="Diretório do cache de SVGs dos diagramas (padrão: _geradores/cache_diagramas).",
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

    try:
        caminho_final = montar_treinamento(
            body_html_path=body_path,
            output_path=output_path,
            titulo=args.titulo,
            meta=meta,
            recompilar_diagramas=args.recompilar_diagramas,
            cache_diagramas=Path(args.cache_diagramas) if args.cache_diagramas else None,
        )
    except ContratoInvalido as e:
        for msg in e.erros:
            print(msg, file=sys.stderr)
        sys.exit(1)
    except GlossarioInvalido as e:
        for msg in e.erros:
            print(msg, file=sys.stderr)
        sys.exit(1)
    except SlugSemDados as e:
        print(f"Slug sem dados em ESTUDOS_DADOS: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"[OK] Treinamento compilado com sucesso em: {caminho_final}")


if __name__ == "__main__":
    main()
