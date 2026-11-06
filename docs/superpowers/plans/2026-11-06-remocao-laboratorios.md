# Remoção dos Laboratórios: Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apagar todos os laboratórios/simuladores JS existentes e alinhar contrato, portal, Design System, testes e docs a um produto só de conteúdo (teoria, checklist, questões, referências), corrigindo a deriva “60 estudos” → 62.

**Architecture:** Cirurgia em lote no pipeline `_geradores/`: o contrato deixa de conhecer `laboratorio`; os 62 `*_body.html` perdem a seção lab e os `<script>`/`<style>` do simulador (incluindo JSON `application/json` só usados pelo lab); metadados/portal/CSS/JS/docs param de mencionar simulador; rebuild regenera os HTML.

**Tech Stack:** Python 3 (`unittest`), HTML/CSS/JS vanilla, `_geradores/gerar.sh`, `_geradores/montar.py`.

**Spec:** `docs/superpowers/specs/2026-11-06-remocao-laboratorios-design.md`

## Global Constraints

- Textos em pt-BR; marca: nunca “Estudos de/em Cibersegurança”, “José Mauro”, “Brandão”, “Stelling” (`test_marca`).
- Catálogo permanece em **62** módulos; não renumerar, não mudar trilhas; o estudo `Laboratorio-Domestico-e-Portfolio` **permanece** (só perde o simulador).
- Sem vestígio: sem `simulador_nome`, sem coluna “Simulador”, sem “em breve”, sem pasta `_legado/` de JS de lab, sem versionar script de migração.
- Commits só se o usuário pedir; se pedir, mensagens focadas no “porquê”, em pt-BR ou no estilo do repo.
- Testes: de `_geradores/`, `python3 -m unittest testes.<modulo>`. Suíte completa no fim: `python3 -m unittest discover -s _geradores/testes` (respeitar teto de memória do projeto se documentado).
- Falhas Mermaid/`chrome-headless-shell` por ambiente: não bloqueiam este plano se não forem regressão da remoção.

## File map

| Área | Arquivos |
|---|---|
| Contrato | `_geradores/contrato.py`, `_geradores/testes/test_contrato.py`, fixtures em `_geradores/testes/test_chassi.py` |
| Corpos | `_geradores/*_body.html` (62) |
| Metadados/portal | `_geradores/index_dados.py`, `_geradores/build_index.py` → `index.html` |
| Design System | apagar `_geradores/laboratorio.css`; `_geradores/montar.py`; `_geradores/base.css`; `_geradores/tokens.css`; `_geradores/base.js` |
| Docs | `README.md`, `_geradores/CURRICULO.md`, `_geradores/GUIA-DO-AUTOR.md` |
| Testes | `test_index`, `test_portal*`, `test_componentes_css`, `test_tokens`, `test_base_js`, `test_piloto`, testes por módulo com asserts/espelhos de lab, `test_certificacoes_carreira` (`#cert-dados`) |
| Saída | 62 `*/treinamento-*.html` + `index.html` via `gerar.sh todos` |

## Review Focus

1. **Scripts que não são “só lab”:** o planejador de certificações (`#cert-dados` + JS) e datasets `*-dados` são o simulador — saem com o lab; testes que pinam `#cert-dados` devem migrar para `CERTIFICACOES` / texto de teoria, não reintroduzir o JSON do lab. Task 2 + Task 5.
2. **Homelab ≠ tipo laboratorio:** slug/pasta/título do módulo 37 permanecem; só a seção simulador some. Task 2.
3. **Portal e cards:** tag `🧪` / `.tag.lab` / `total_simuladores` e lede com “laboratório interativo” têm de sumir juntos. Task 3.
4. **Contrato rejeita lab residual:** corpo com `data-tipo="laboratorio"` deve falhar (§2 tipo inválido), não ser ignorado. Task 1.
5. **Copy interna nos corpos:** frases “veja o laboratório / simulador deste módulo” devem ser removidas ou reescritas no mesmo lote dos corpos. Task 2.

---

### Task 1: Contrato sem `laboratorio`

**Files:**
- Modify: `_geradores/contrato.py` (`TIPOS`, `ROTULOS`, §5)
- Modify: `_geradores/testes/test_contrato.py` (`CORPO_VALIDO`, asserts de `TIPOS`/§5)
- Modify: `_geradores/testes/test_chassi.py` (fixture `corpo_valido` / `CORPO_SEM_LAB` — alinhar ao novo contrato)

**Interfaces:**
- Produces: `TIPOS == ("teoria", "checklist", "questoes", "referencias")`; §5 exige `checklist`, `questoes`, `referencias`; `laboratorio` ∉ `TIPOS` (qualquer uso → erro §2 tipo inválido).

- [x] **Step 1: Testes (RED).** Em `test_contrato.py`: `TIPOS` sem `laboratorio`; `CORPO_VALIDO` sem seção lab (teoria + checklist + questões + referências); trocar `test_regra_5_falta_laboratorio` por (a) `test_regra_5_falta_checklist` (e/ou questoes/referencias) e (b) `test_regra_2_laboratorio_invalido` — corpo com `data-tipo="laboratorio"` → mensagem §2 tipo inválido. Ajustar `test_extrair_secoes_ignora_aninhadas` / contagens que indexavam a seção lab. Rodar `python3 -m unittest testes.test_contrato` → FAIL.

- [x] **Step 2: Implementar** em `contrato.py` conforme Interfaces.

- [x] **Step 3: Alinhar** `test_chassi.py` ao fixture sem lab.

- [x] **Step 4: Rodar** `python3 -m unittest testes.test_contrato testes.test_chassi` → PASS.

- [x] **Step 5: Commit** (se pedido) `fix(contrato): remove tipo laboratorio do contrato do corpo`.

---

### Task 2: Apagar labs dos 62 corpos

**Files:**
- Modify: todos `_geradores/*_body.html`
- Não versionar script de migração (se usar um, descartar após o lote)

**Interfaces:**
- Consumes: contrato da Task 1.
- Produces: cada corpo valida com `validar_corpo`; zero `data-tipo="laboratorio"`; zero `.lab-box`; zero `<script>` / `<style>` de simulador (inclui `type="application/json"` só do lab, ex. `#cert-dados`, `#risco-dados`, `#soc-dados`); módulo 37 mantém título/tema Homelab.

**Heurística de limpeza (obrigatória):**
1. Remover a `<section … data-tipo="laboratorio">…</section>` completa.
2. Remover filhos `<script>` e `<style>` do `article` que restarem após o passo 1 (hoje todos os scripts dos corpos servem ao simulador).
3. Remover/reescrever frases no HTML que mandem o aluno ao “laboratório”/“simulador” deste módulo.
4. Não apagar o arquivo `laboratorio_domestico_e_portfolio_body.html` nem renomear o slug.

- [x] **Step 1: Teste de lote (RED).** Acrescentar (ou estender) um teste em `_geradores/testes/` que, para cada `*_body.html`: `validar_corpo` sem erros; `"laboratorio" not in` tipos extraídos; ausência de `data-tipo="laboratorio"`, `.lab-box`, e (após limpeza) ausência de `<script` nos corpos **ou** lista explícita vazia de exceções. Rodar → FAIL enquanto corpos ainda têm lab.

- [x] **Step 2: Limpar os 62 corpos** pela heurística acima. Conferir amostragem: `fundamentos_ciber`, `certificacoes_e_carreira`, `gestao_de_riscos_ti`, `laboratorio_domestico_e_portfolio`, `operacoes_soc_e_siem`.

- [x] **Step 3: Rodar** o teste de lote + `python3 -m unittest testes.test_contrato` → PASS. Grep: zero `data-tipo="laboratorio"` e zero `.lab-box` em `_geradores/*_body.html`.

- [x] **Step 4: Commit** (se pedido) `chore(conteudo): remove secoes e scripts de laboratorio dos 62 corpos`.

---

### Task 3: Metadados e portal sem simulador

**Files:**
- Modify: `_geradores/index_dados.py` (remover chave `simulador_nome` de todos os `ESTUDOS_DADOS`)
- Modify: `_geradores/build_index.py` (cards, stats, meta, lede, labels JS do sumário)
- Modify: `_geradores/testes/test_index.py`, `test_portal.py`, `test_portal_js.py` (e correlatos que assertam `simulador_nome` / tag lab)
- Recompilado: `index.html`

**Interfaces:**
- Consumes: corpos sem lab (Task 2) não são obrigatórios para compilar o portal, mas o rebuild final espera ambos.
- Produces: nenhum `simulador_nome` em `ESTUDOS_DADOS`; portal sem `🧪`, sem `.tag.lab`, sem `total_simuladores`, sem copy “simulador(es)” / “laboratório interativo” na UI gerada.

- [x] **Step 1: Testes (RED).** Em `test_index.py`, tirar `simulador_nome` do schema esperado. Em `test_portal.py`, remover assert da tag `🧪 {simulador}` e regras CSS `.tag.lab` / `--tipo-laboratorio` no portal. Ajustar textos esperados do lede/meta. Rodar → FAIL.

- [x] **Step 2: Implementar** remoção em `index_dados.py` e `build_index.py`.

- [x] **Step 3: Compilar portal** `./_geradores/gerar.sh portal`.

- [x] **Step 4: Rodar** `python3 -m unittest testes.test_index testes.test_portal testes.test_portal_js` → PASS.

- [x] **Step 5: Commit** (se pedido) `feat(portal): remove simuladores dos metadados e do index`.

---

### Task 4: Design System sem vestígio de lab

**Files:**
- Delete: `_geradores/laboratorio.css`
- Modify: `_geradores/montar.py` (parar de embutir `LABORATORIO_CSS`)
- Modify: `_geradores/base.css`, `_geradores/tokens.css`, `_geradores/base.js`
- Modify: `_geradores/testes/test_componentes_css.py`, `test_tokens.py`, `test_base_js.py`, `test_piloto.py`

**Interfaces:**
- Produces: `carregar_css()` sem `laboratorio.css`; `base.js` sem rótulo/tipo `laboratorio` e sem `CS.labProgress`; tokens sem `--tipo-laboratorio*`; CSS sem `.lab-box` / `.lab-header` / `.lab-body` / `[data-tipo="laboratorio"]`.

- [x] **Step 1: Testes (RED).** Remover `.lab-box` etc. das listas canônicas; `TIPOS` de tokens sem `laboratorio`; apagar/ajustar testes de `CS.labProgress` e sumário com seção lab; `test_carregar_css_ordem_e_laboratorio_opcional` → CSS sem arquivo de lab. Rodar os quatro módulos → FAIL.

- [x] **Step 2: Implementar** delete + edições listadas.

- [x] **Step 3: Rodar** `python3 -m unittest testes.test_componentes_css testes.test_tokens testes.test_base_js testes.test_piloto testes.test_montar` → PASS (ignorar só falhas Mermaid de ambiente).

- [x] **Step 4: Commit** (se pedido) `refactor(ds): remove laboratorio.css e APIs de lab`.

---

### Task 5: Testes de módulo e certificações

**Files:**
- Modify: testes em `_geradores/testes/test_*.py` que assertam lab, `.lab-box`, espelhos Python do motor JS, datasets de simulador, ou `#cert-dados`
- Em especial: `test_certificacoes_carreira.py` — migrar o que for requisito de produto para `CERTIFICACOES` / texto teórico; remover dependência do JSON `#cert-dados` removido na Task 2
- Apagar ou enxugar arquivos cujo único propósito era o motor do lab

**Interfaces:**
- Consumes: corpos (Task 2), portal (Task 3), DS (Task 4).
- Produces: suíte sem asserts de laboratório; cobertura de conteúdo (teoria/checklist/questões/referências) preservada onde já existia.

- [x] **Step 1: Inventário.** `rg -n "laboratorio|lab-box|labProgress|simulador_nome|#cert-dados|lab-box" _geradores/testes` e listar arquivos a editar/apagar.

- [x] **Step 2: Ajustar/apagar** conforme inventário (TDD: corrigir o teste, depois confirmar PASS no módulo).

- [x] **Step 3: Rodar** amostragem dos módulos mais acoplados (`test_certificacoes_carreira`, `test_gestao_riscos_ti`, `test_operacoes_soc` se existir, `test_soar_automacao`, `test_piloto`) → PASS.

- [x] **Step 4: Commit** (se pedido) `test: alinha suite a produto sem laboratorios`.

---

### Task 6: Docs (README, CURRICULO, GUIA) + deriva 60→62

**Files:**
- Modify: `README.md`, `_geradores/CURRICULO.md`, `_geradores/GUIA-DO-AUTOR.md`
- Modify: `_geradores/testes/test_documentacao.py` (e correlatos) se pinarem copy antiga

**Interfaces:**
- Produces: zero promessa de simulador/lab no README/CURRICULO/GUIA; contrato do autor = teoria + checklist + questões + referências; README com **62** módulos (não “60 estudos”); pipeline descrito sem `laboratorio.css` / simuladores.

- [x] **Step 1: Testes (RED)** se `test_documentacao` (ou similar) exigir frases/contagens — atualizar expectativas primeiro.

- [x] **Step 2: Editar** os três docs conforme Interfaces (remover coluna Simulador da tabela do README; seções de simulador no CURRICULO; §§ de `.lab-box` / JS de lab no GUIA).

- [x] **Step 3: Rodar** `python3 -m unittest testes.test_documentacao testes.test_curriculo testes.test_marca` → PASS.

- [x] **Step 4: Commit** (se pedido) `docs: produto sem laboratorios; corrige contagem 62`.

---

### Task 7: Rebuild completo e verificação residual

**Files:**
- Regenerate: 62 `*/treinamento-*.html`, `index.html`

- [x] **Step 1: Compilar** `./_geradores/gerar.sh todos`.

- [x] **Step 2: Grep residual (deve ser vazio no código ativo do produto):**
  - `data-tipo="laboratorio"`
  - `.lab-box` / `labProgress` / `simulador_nome`
  - `laboratorio.css`
  - Copy de produto: “simuladores interativos”, “laboratório interativo” em `README.md`, `index.html`, `_geradores/GUIA-DO-AUTOR.md`, `_geradores/CURRICULO.md`, `_geradores/build_index.py`
  - Exceção permitida: título/slug do módulo Homelab; histórico em `docs/superpowers/specs|plans` antigos.

- [x] **Step 3: Suíte** `python3 -m unittest discover -s _geradores/testes` → PASS (exceto Mermaid ambiente, se aplicável e documentado na execução).

- [x] **Step 4: Commit** (se pedido) `build: regenera HTML sem laboratorios`.

---

## Spec coverage (self-review)

| Spec | Task |
|---|---|
| Contrato sem lab / rejeita residual | 1 |
| 62 corpos + scripts + copy interna | 2 |
| Homelab permanece | 2 |
| `simulador_nome` / portal | 3 |
| DS sem vestígio | 4 |
| Testes / `#cert-dados` | 5 |
| README/CURRICULO/GUIA + 60→62 | 6 |
| Rebuild + grep + suíte | 7 |
| Não objetivos (CI, quiz IDs, conteúdo novo, recriar labs) | fora do plano |
