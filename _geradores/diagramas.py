"""
Módulo de extração, compilação e cache de diagramas Mermaid para SVG.
"""
from __future__ import annotations

import hashlib
import html as html_lib
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

CONFIG_PUPPETEER_PADRAO = Path(__file__).parent / "puppeteer-config.json"
CACHE_DIR_PADRAO = Path(__file__).parent / "cache_diagramas"

PADRAO_MERMAID = re.compile(
    r'<pre\b([^>]*\bclass=["\']mermaid["\'][^>]*)>(.*?)</pre>',
    re.DOTALL | re.IGNORECASE
)

PADRAO_ATTR = re.compile(
    r'([\w\-]+)(?:\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|([^\s>]+)))?'
)


def extrair_blocos_mermaid(html: str) -> list[dict]:
    """
    Localiza e extrai blocos <pre class="mermaid" ...>...</pre> do HTML.
    Retorna lista de dicionários com código, atributos, título e tag original.
    """
    blocos = []
    for match in PADRAO_MERMAID.finditer(html):
        tag_attrs_str = match.group(1)
        codigo = match.group(2)
        bloco_completo = match.group(0)

        atributos = {}
        for attr_m in PADRAO_ATTR.finditer(tag_attrs_str):
            nome = attr_m.group(1)
            val = attr_m.group(2) if attr_m.group(2) is not None else (
                attr_m.group(3) if attr_m.group(3) is not None else (
                    attr_m.group(4) if attr_m.group(4) is not None else ""
                )
            )
            atributos[nome] = val

        titulo = atributos.get("data-title", "")

        blocos.append({
            "codigo": codigo,
            "raw": bloco_completo,
            "bloco_completo": bloco_completo,
            "atributos": atributos,
            "titulo": titulo,
            "data_title": titulo,
        })
    return blocos


def calcular_hash_mermaid(codigo: str) -> str:
    """
    Calcula hash SHA-256 de 12 caracteres hexadecimais sobre o código Mermaid normalizado.
    """
    normalizado = codigo.strip().replace("\r\n", "\n").encode("utf-8")
    return hashlib.sha256(normalizado).hexdigest()[:12]


def gerar_svg_mermaid(
    codigo: str,
    caminho_svg: Path,
    config_puppeteer: Optional[Path] = None
) -> bool:
    """
    Invoca o Mermaid CLI (@mermaid-js/mermaid-cli) via npx para compilar o código em SVG.
    """
    if config_puppeteer is None:
        config_puppeteer = CONFIG_PUPPETEER_PADRAO

    caminho_svg = Path(caminho_svg)
    config_puppeteer = Path(config_puppeteer)

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        temp_mmd = tmp_path / "diagrama.mmd"
        temp_svg = tmp_path / "diagrama.svg"

        temp_mmd.write_text(codigo.strip() + "\n", encoding="utf-8")

        cmd = [
            "npx", "--yes", "@mermaid-js/mermaid-cli",
            "-p", str(config_puppeteer.resolve()),
            "-i", str(temp_mmd.resolve()),
            "-o", str(temp_svg.resolve()),
            "-b", "transparent",
            "-t", "dark"
        ]

        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                timeout=120
            )
            if res.returncode != 0:
                print(f"[AVISO] mermaid-cli retornou código {res.returncode}: {res.stderr}", file=sys.stderr)
                return False

            if not temp_svg.exists() or temp_svg.stat().st_size == 0:
                print("[AVISO] mermaid-cli não gerou arquivo SVG válido.", file=sys.stderr)
                return False

            caminho_svg.parent.mkdir(parents=True, exist_ok=True)
            caminho_svg.write_text(temp_svg.read_text(encoding="utf-8"), encoding="utf-8")
            return True
        except (subprocess.SubprocessError, FileNotFoundError, OSError, Exception) as e:
            print(f"[AVISO] Exceção ao executar mermaid-cli: {e}", file=sys.stderr)
            return False


def obter_ou_gerar_svg(
    codigo: str,
    cache_dir: Optional[Path] = None,
    forcar: bool = False
) -> tuple[Optional[str], str]:
    """
    Busca o SVG no cache ou compila sob demanda. Retorna (conteudo_svg, hash_id).
    Em caso de falha no CLI, conteudo_svg será None.
    """
    if cache_dir is None:
        cache_dir = CACHE_DIR_PADRAO

    cache_dir = Path(cache_dir)
    hash_id = calcular_hash_mermaid(codigo)
    caminho_svg = cache_dir / f"{hash_id}.svg"

    if caminho_svg.exists() and not forcar:
        try:
            return caminho_svg.read_text(encoding="utf-8"), hash_id
        except OSError as e:
            print(f"[AVISO] Erro ao ler SVG em cache ({caminho_svg}): {e}", file=sys.stderr)

    sucesso = gerar_svg_mermaid(codigo, caminho_svg, CONFIG_PUPPETEER_PADRAO)
    if sucesso and caminho_svg.exists():
        try:
            return caminho_svg.read_text(encoding="utf-8"), hash_id
        except OSError:
            pass

    return None, hash_id


def processar_diagramas_html(
    html: str,
    cache_dir: Optional[Path] = None,
    forcar: bool = False
) -> str:
    """
    Substitui todos os blocos <pre class="mermaid"> por contêineres .diagram-box com SVG inline.
    Se a compilação falhar e não houver cache, preserva o bloco original como fallback.
    """
    if cache_dir is None:
        cache_dir = CACHE_DIR_PADRAO

    blocos = extrair_blocos_mermaid(html)
    if not blocos:
        return html

    resultado = html
    for bloco in blocos:
        codigo = bloco["codigo"]
        svg_content, hash_id = obter_ou_gerar_svg(codigo, cache_dir, forcar=forcar)

        if not svg_content:
            # Fallback seguro: mantém o bloco original intacto
            continue

        titulo_puro = bloco["titulo"] if bloco["titulo"] else "Diagrama de Arquitetura"
        titulo_escapado = html_lib.escape(titulo_puro, quote=True)
        svg_inline = svg_content.strip()

        markup_substituto = (
            f'<div class="diagram-box">\n'
            f'  <div class="diagram-header">\n'
            f'    <span class="diagram-title">{titulo_escapado}</span>\n'
            f'    <span class="diagram-badge">Mermaid Arquitetura</span>\n'
            f'  </div>\n'
            f'  <div class="diagram-svg-wrap" role="img" aria-label="{titulo_escapado}">\n'
            f'    {svg_inline}\n'
            f'  </div>\n'
            f'</div>'
        )

        resultado = resultado.replace(bloco["bloco_completo"], markup_substituto, 1)

    return resultado
