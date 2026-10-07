#!/usr/bin/env bash
# ==============================================================================
# Script CLI Mestre — Estudos em Cibersegurança
# ==============================================================================
# Automatiza a compilação de treinamentos individuais ou em lote e a
# regeneração do portal principal index.html.
#
# Uso:
#   ./_geradores/gerar.sh portal        # Regenera apenas index.html
#   ./_geradores/gerar.sh todos         # Compila todos os estudos e index.html
#   ./_geradores/gerar.sh <slug>        # Compila um estudo e index.html
#   ./_geradores/gerar.sh help          # Exibe instruções de uso
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

exibir_ajuda() {
    cat << 'EOF'
==============================================================================
Estudos em Cibersegurança — Gerador de Treinamentos e Portal
==============================================================================

Uso:
  ./_geradores/gerar.sh [comando | slug]

Comandos disponíveis:
  portal           Regenera apenas a página raiz index.html
  todos            Compila todos os estudos que possuem arquivo *_body.html
                   em _geradores/ e regera o portal index.html
  <slug>           Compila o estudo especificado (ex: Fundamentos-Ciber,
                   redes_e_protocolos ou caminho para fragmento _body.html)
                   e regera o portal index.html
  help, --help, -h Exibe esta mensagem de ajuda

Exemplos:
  ./_geradores/gerar.sh portal
  ./_geradores/gerar.sh Fundamentos-Ciber
  ./_geradores/gerar.sh todos
==============================================================================
EOF
}

comando_portal() {
    echo "==> Regenerando portal raiz (index.html)..."
    python3 "$SCRIPT_DIR/build_index.py" "$REPO_ROOT/index.html"
    echo "[OK] index.html gerado com sucesso."
}

comando_todos() {
    echo "==> Compilando todos os estudos disponíveis..."
    shopt -s nullglob
    local bodies=("$SCRIPT_DIR"/*_body.html)
    shopt -u nullglob

    if [ ${#bodies[@]} -eq 0 ]; then
        echo "[INFO] Nenhum fragmento *_body.html encontrado em _geradores/."
    else
        for body in "${bodies[@]}"; do
            echo "--- Compilando: $(basename "$body") ---"
            python3 "$SCRIPT_DIR/montar.py" "$body"
        done
        echo "[OK] Todos os fragmentos disponíveis foram compilados com sucesso."
    fi

    comando_portal
}

comando_slug() {
    local alvo="$1"
    local body_encontrado=""

    # 1. Se foi passado caminho direto para arquivo existente
    if [ -f "$alvo" ]; then
        body_encontrado="$alvo"
    elif [ -f "$SCRIPT_DIR/$alvo" ]; then
        body_encontrado="$SCRIPT_DIR/$alvo"
    fi

    # 2. Se não foi achado diretamente, busca usando o resolvedor python
    if [ -z "$body_encontrado" ]; then
        body_encontrado=$(python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, '$SCRIPT_DIR')
try:
    from montar import normalizar_chave
    alvo = sys.argv[1]
    norm = normalizar_chave(alvo)
    ger_dir = Path('$SCRIPT_DIR')
    for f in ger_dir.glob('*_body.html'):
        if normalizar_chave(f.name) == norm or normalizar_chave(f.stem) == norm:
            print(f.resolve())
            sys.exit(0)
        if norm in normalizar_chave(f.stem):
            print(f.resolve())
            sys.exit(0)
    sys.exit(1)
except Exception:
    sys.exit(1)
" "$alvo" 2>/dev/null || true)
    fi

    if [ -n "$body_encontrado" ] && [ -f "$body_encontrado" ]; then
        echo "==> Compilando estudo a partir de: $body_encontrado"
        python3 "$SCRIPT_DIR/montar.py" "$body_encontrado"
        echo "[OK] Estudo compilado com sucesso."
        comando_portal
    else
        echo "[ERRO] Não foi encontrado fragmento de corpo (*_body.html) correspondente a '$alvo' em _geradores/." >&2
        echo "Verifique o slug do estudo no arquivo _geradores/estudos.txt ou passe o caminho do arquivo." >&2
        exit 1
    fi
}

# Tratamento dos argumentos da linha de comando
if [ $# -eq 0 ]; then
    exibir_ajuda
    exit 0
fi

case "$1" in
    portal)
        comando_portal
        ;;
    todos)
        comando_todos
        ;;
    help|--help|-h)
        exibir_ajuda
        exit 0
        ;;
    *)
        comando_slug "$1"
        ;;
esac
