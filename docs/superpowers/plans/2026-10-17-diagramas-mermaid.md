# Padronização e Pré-compilação de Diagramas com Mermaid: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implementar o pipeline de pré-compilação de diagramas Mermaid para SVG com cache determinístico, convertendo diagramas ASCII dos módulos HTML e adicionando diagramas conceituais nas documentações Markdown.

**Architecture:** Módulo Python `_geradores/diagramas.py` integrado a `montar.py` que detecta blocos `<pre class="mermaid">`, consulta cache local `_geradores/cache_diagramas/<hash>.svg` ou invoca `npx @mermaid-js/mermaid-cli` com configuração Puppeteer sem sandbox, injetando `<svg>` transparente e responsivo estilizado via `base.css`. Documentações Markdown (`README.md`, `CURRICULO.md`, `GUIA-DO-AUTOR.md`) recebem blocos ````mermaid nativos.

**Tech Stack:** Python 3 (stdlib: `hashlib`, `re`, `subprocess`, `pathlib`), Node.js / `@mermaid-js/mermaid-cli` (`mmdc`), CSS3 / SVG, Markdown.

**Spec:** `docs/superpowers/specs/2026-10-17-diagramas-mermaid-design.md`

## Global Constraints

- 100% Offline e Standalone: Nenhum script runtime externo (como `mermaid.min.js`) deve ser carregado pelo navegador do usuário em `treinamento-*.html`.
- Formato de entrada nos módulos: `<pre class="mermaid" [data-title="..."]>...</pre>`.
- Formato de saída no HTML compilado: `<div class="diagram-box"><div class="diagram-header">...</div><div class="diagram-svg-wrap" role="img">...<svg ...>...</div></div>`.
- Resiliência: Se Node/CLI estiver ausente e o SVG não estiver no cache, emitir aviso e reter o bloco legível sem travar o build.
- Responsividade: O SVG gerado e seu contêiner devem respeitar `max-width: 100%` e `overflow-x: auto`, sem introduzir rolagem horizontal global na página.

## Review Focus

- Diagrama malformado ou com sintaxe inválida: o utilitário não deve quebrar o script `montar.py`; deve reter o bloco e emitir aviso.
- Execução em ambiente Linux sem sandbox: Puppeteer deve sempre usar os argumentos `--no-sandbox` e `--disable-setuid-sandbox`.
- Estabilidade de hash SHA-256: variações de espaços em branco antes ou depois do código não devem alterar o hash do diagrama.
- Preservação de atributos SVG: o SVG inlined deve possuir classes limpas e permitir escalabilidade em telas pequenas (360px a 480px).
- Compatibilidade com o Design System: o SVG transparente deve manter contraste legível no tema escuro padrão e no tema claro.

---

### Task 1: Scaffolding do Módulo de Diagramas e Configuração Puppeteer

**Files:**
- Create: `_geradores/puppeteer-config.json`
- Create: `_geradores/diagramas.py`
- Create: `_geradores/testes/test_diagramas.py`
- Create: `_geradores/cache_diagramas/.gitkeep`

**Interfaces:**
- Produces:
  - `extrair_blocos_mermaid(html: str) -> list[dict]`
  - `calcular_hash_mermaid(codigo: str) -> str`
  - `gerar_svg_mermaid(codigo: str, caminho_svg: Path, config_puppeteer: Path) -> bool`
  - `obter_ou_gerar_svg(codigo: str, cache_dir: Path, forcar: bool = False) -> tuple[Optional[str], str]`
  - `processar_diagramas_html(html: str, cache_dir: Path, forcar: bool = False) -> str`

- [ ] **Step 1: Criar arquivo de configuração do Puppeteer**
  Criar `_geradores/puppeteer-config.json` com:
  ```json
  {
    "args": ["--no-sandbox", "--disable-setuid-sandbox"]
  }
  ```

- [ ] **Step 2: Escrever testes unitários em `_geradores/testes/test_diagramas.py`**
  Cobrir:
  - `test_extrair_blocos_mermaid`: extração de múltiplos blocos e captura de atributos como `data-title`.
  - `test_calcular_hash_mermaid_determinismo`: garantia de que strings com espaçamentos marginais diferentes geram mesmo hash SHA-256 truncado em 12 caracteres.
  - `test_obter_ou_gerar_svg_cache_existente`: verificar que se o arquivo `.svg` já existe em cache, não chama subprocesso.
  - `test_processar_diagramas_html_substituicao`: testar substituição de `<pre class="mermaid">` por `.diagram-box` contendo o SVG.
  - `test_fallback_quando_cli_falha`: simular falha no subprocesso e validar que o bloco original é preservado.

- [ ] **Step 3: Executar teste para verificar falha (Red)**
  Comando: `python3 -m unittest _geradores/testes/test_diagramas.py`
  Resultado esperado: FAIL / ImportError (`diagramas.py` não existe).

- [ ] **Step 4: Implementar `_geradores/diagramas.py`**
  Implementar as funções especificadas em `Interfaces`, garantindo:
  - Regex para capturar `<pre class="mermaid"([^>]*)>(.*?)</pre>`.
  - Hashing SHA-256 com strip de quebras de linha.
  - Subprocesso chamando `npx --yes @mermaid-js/mermaid-cli -p puppeteer-config.json -i temp.mmd -o temp.svg -b transparent -t dark`.
  - Wrapper HTML `.diagram-box`, `.diagram-header`, `.diagram-title` e `.diagram-svg-wrap`.

- [ ] **Step 5: Executar testes para verificar passagem (Green)**
  Comando: `python3 -m unittest _geradores/testes/test_diagramas.py`
  Resultado esperado: PASS (todos os testes de diagramas passam).

- [ ] **Step 6: Criar diretório de cache e comitar**
  ```bash
  mkdir -p _geradores/cache_diagramas
  touch _geradores/cache_diagramas/.gitkeep
  git add _geradores/puppeteer-config.json _geradores/diagramas.py _geradores/cache_diagramas/.gitkeep _geradores/testes/test_diagramas.py
  git commit -m "feat(diagramas): modulo de compilacao mermaid para svg com cache local"
  ```

---

### Task 2: Integração com `montar.py` e Estilos no Design System (`base.css`)

**Files:**
- Modify: `_geradores/base.css`
- Modify: `_geradores/montar.py`
- Modify: `_geradores/testes/test_montar.py`

**Interfaces:**
- Consumes: `processar_diagramas_html` de `_geradores/diagramas.py`
- Produces: `montar_treinamento(..., recompilar_diagramas: bool = False)` e flag CLI `--recompilar-diagramas` em `montar.py`.

- [ ] **Step 1: Escrever teste de integração em `_geradores/testes/test_montar.py`**
  Adicionar teste que monta um fragmento com `<pre class="mermaid">` e verifica a presença da classe `.diagram-box` e da tag `<svg` no HTML compilado resultante.

- [ ] **Step 2: Executar teste para verificar falha (Red)**
  Comando: `python3 -m unittest _geradores/testes/test_montar.py`
  Resultado esperado: FAIL (ainda não há integração com `diagramas.py`).

- [ ] **Step 3: Adicionar regras CSS em `_geradores/base.css`**
  Inserir classes:
  - `.diagram-box`: borda, `border-radius: var(--radius)`, fundo `var(--surface)`, `box-shadow`.
  - `.diagram-header`: flexbox, fundo `var(--ground)`, `color: var(--muted)`.
  - `.diagram-title`: tipografia em destaque.
  - `.diagram-badge`: estilo cápsula com tema visual do projeto.
  - `.diagram-svg-wrap`: `overflow-x: auto`, `text-align: center`, com regras para `svg { max-width: 100%; height: auto; display: inline-block; }`.

- [ ] **Step 4: Integrar processamento de diagramas em `_geradores/montar.py`**
  - Importar `processar_diagramas_html` de `diagramas`.
  - Chamar `processar_diagramas_html` sobre o `body_html` antes da injeção no template mestre.
  - Adicionar argumento `--recompilar-diagramas` ao `argparse` do CLI.

- [ ] **Step 5: Executar testes de integração (Green)**
  Comando: `python3 -m unittest _geradores/testes/test_montar.py`
  Resultado esperado: PASS.

- [ ] **Step 6: Comitar alterações**
  ```bash
  git add _geradores/base.css _geradores/montar.py _geradores/testes/test_montar.py
  git commit -m "feat(compilador): integracao de pre-compilacao de diagramas e estilos css"
  ```

---

### Task 3: Conversão dos Diagramas nos Módulos HTML e Geração de SVGs no Cache

**Files:**
- Modify: `_geradores/arquitetura_zero_trust_body.html`
- Modify: `_geradores/segmentacao_e_firewall_body.html`
- Modify: `_geradores/gestao_de_vulnerabilidades_body.html`
- Modify: `_geradores/seguranca_de_redes_defesa_body.html`
- Output: `_geradores/cache_diagramas/*.svg`
- Output: `Arquitetura-Zero-Trust/treinamento-arquitetura-zero-trust.html`
- Output: `Segmentacao-e-Firewall/treinamento-segmentacao-e-firewall.html`
- Output: `Gestao-de-Vulnerabilidades/treinamento-gestao-de-vulnerabilidades.html`
- Output: `Seguranca-de-Redes-Defesa/treinamento-seguranca-de-redes-defesa.html`

- [ ] **Step 1: Converter `_geradores/arquitetura_zero_trust_body.html`**
  Substituir o ASCII `nist-zta-diagram` pelo bloco `<pre class="mermaid" data-title="Fluxo Lógico de Decisão NIST SP 800-207">` com o `flowchart TD` mapeando Control Plane (PDP: PE e PA) e Data Plane (Subject, PEP, Recurso Protegido).

- [ ] **Step 2: Converter `_geradores/segmentacao_e_firewall_body.html`**
  Substituir o ASCII `vlan-tag-struct` pelo bloco `<pre class="mermaid" data-title="Estrutura da Tag IEEE 802.1Q">` com a decomposição do quadro e detalhamento dos campos TPID e TCI (PCP, DEI, VID).

- [ ] **Step 3: Converter `_geradores/gestao_de_vulnerabilidades_body.html`**
  Substituir o ASCII `cvss-vector-example` pelo bloco `<pre class="mermaid" data-title="Métricas Base do Vetor CVSS v3.1">` com diagrama conectando métricas de Explorabilidade, Escopo e Impacto.

- [ ] **Step 4: Adicionar diagrama em `_geradores/seguranca_de_redes_defesa_body.html`**
  Inserir bloco `<pre class="mermaid" data-title="Topologia Comparativa: IDS vs IPS e Proxies Reversos">` comparando tráfego fora de banda (TAP/SPAN) com tráfego in-line e terminação de TLS/WAF.

- [ ] **Step 5: Compilar os 4 módulos com `montar.py` para gerar SVGs e atualizar HTMLs**
  Executar:
  ```bash
  python3 _geradores/montar.py _geradores/arquitetura_zero_trust_body.html
  python3 _geradores/montar.py _geradores/segmentacao_e_firewall_body.html
  python3 _geradores/montar.py _geradores/gestao_de_vulnerabilidades_body.html
  python3 _geradores/montar.py _geradores/seguranca_de_redes_defesa_body.html
  ```
  Verificar que os arquivos `.svg` foram gerados em `_geradores/cache_diagramas/` e que os arquivos `treinamento-*.html` contêm as tags `<svg`.

- [ ] **Step 6: Executar testes de validação dos módulos**
  Comando: `python3 -m unittest _geradores/testes/test_arquitetura_zero_trust.py _geradores/testes/test_segmentacao_firewall.py _geradores/testes/test_gestao_vulnerabilidades.py _geradores/testes/test_seguranca_redes_defesa.py`
  Resultado esperado: PASS.

- [ ] **Step 7: Comitar alterações**
  ```bash
  git add _geradores/*_body.html _geradores/cache_diagramas/*.svg Arquitetura-Zero-Trust/ Segmentacao-e-Firewall/ Gestao-de-Vulnerabilidades/ Seguranca-de-Redes-Defesa/
  git commit -m "feat(modulos): converter diagramas ascii para mermaid pre-compilado em svg"
  ```

---

### Task 4: Adição de Diagramas Mermaid na Documentação Markdown

**Files:**
- Modify: `README.md`
- Modify: `_geradores/CURRICULO.md`
- Modify: `_geradores/GUIA-DO-AUTOR.md`
- Modify: `_geradores/testes/test_curriculo.py`

- [ ] **Step 1: Atualizar `README.md` com diagramas Mermaid**
  - Inserir diagrama do pipeline: `flowchart LR` ilustrando fontes (`_body.html`, `estudos.txt`, `base.css/js`), compilação (`montar.py` + renderização SVG) e geração do treinamento offline.
  - Inserir diagrama das 7 trilhas e progressão formativa (`flowchart TD`).

- [ ] **Step 2: Atualizar `_geradores/CURRICULO.md`**
  - Inserir diagrama de correlação entre as 7 Trilhas Temáticas e as funções do **NIST CSF 2.0** (*Govern*, *Identify*, *Protect*, *Detect*, *Respond*, *Recover*).

- [ ] **Step 3: Atualizar `_geradores/GUIA-DO-AUTOR.md`**
  - Adicionar seção detalhando o padrão de autoria de diagramas com `<pre class="mermaid">`.
  - Exemplificar boas práticas de sintaxe e documentar o funcionamento do cache de compilação.

- [ ] **Step 4: Executar testes de consistência da documentação**
  Comando: `python3 -m unittest _geradores/testes/test_curriculo.py`
  Resultado esperado: PASS.

- [ ] **Step 5: Comitar alterações**
  ```bash
  git add README.md _geradores/CURRICULO.md _geradores/GUIA-DO-AUTOR.md
  git commit -m "docs(diagramas): adicionar diagramas conceituais mermaid na documentacao"
  ```

---

### Task 5: Validação da Suíte Completa de Testes Unitários e Responsivos

**Files:**
- Output / Verification: Todas as suítes em `_geradores/testes/`

- [ ] **Step 1: Recompilar todos os treinamentos existentes para garantir consistência global**
  Executar:
  ```bash
  for f in _geradores/*_body.html; do python3 _geradores/montar.py "$f"; done
  python3 _geradores/build_index.py
  ```

- [ ] **Step 2: Executar toda a suíte de testes unitários**
  Comando: `python3 -m unittest discover -s _geradores/testes`
  Resultado esperado: PASS em todos os testes (120+ testes).

- [ ] **Step 3: Executar a suíte de testes de responsividade móvel**
  Comando: `python3 -m unittest _geradores/testes/test_responsivo.py`
  Resultado esperado: PASS (nenhum elemento ou SVG causa rolagem lateral indesejada).

- [ ] **Step 4: Comitar qualquer artefato de compilação restante e registrar conformidade**
  ```bash
  git status
  git commit -am "chore(build): recompilacao geral dos modulos com diagramas svg" || true
  ```
