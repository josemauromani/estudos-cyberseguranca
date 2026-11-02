# Trilhas de Especialização (11, 12 e 13) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ampliar o catálogo de 45 para 57 módulos em 13 trilhas (Detecção Avançada & Threat Hunting; Nuvem, Containers & Kubernetes; Setor Regulado no Brasil) e ligar os módulos novos às rotas por perfil, à Rota da Vaga (como apoio), às necessidades e às certificações.

**Architecture:** `estudos.txt` e `index_dados.py` são a fonte única; `build_index.py` só renderiza e já deriva filtros, blocos de trilha e contagens de `TRILHAS` e do catálogo. O número de cada módulo é a sua posição em `ESTUDOS_DADOS`, então os 12 módulos entram no fim, na ordem 46 → 57. As cores de trilha são escritas à mão nos dois CSS, como nas Trilhas 8–10 (abordagem A).

**Tech Stack:** Python 3 (stdlib, `unittest`), HTML/CSS estáticos, Bash (`gerar.sh`), Chrome headless só para a verificação final.

**Spec:** `docs/superpowers/specs/2026-11-02-trilhas-especializacao-design.md` (aprovada em 2026-11-02). Conteúdo de módulo, descrições de trilha, tabelas de rota, necessidades e certificações são copiados **literalmente** da spec; o plano indica a seção.

## Global Constraints

- Todo texto de interface e documentação em pt-BR.
- Os módulos 01–45 e seus slugs, números e trilhas não mudam. Os módulos novos entram no **fim** de `estudos.txt` e de `ESTUDOS_DADOS`, na ordem da spec §2.2 (46 → 57).
- Trilhas: 11 `Detecção Avançada & Threat Hunting` (`#A21CAF` / escuro `#E879F9`, token `--t11-fuchsia`, `cor_nome` `"fuchsia"`); 12 `Nuvem, Containers & Kubernetes` (`#0F766E` / `#2DD4BF`, `--t12-teal`, `"teal"`); 13 `Setor Regulado no Brasil` (`#4D7C0F` / `#A3E635`, `--t13-lime`, `"lime"`).
- Rótulos de carreira só com os nomes exatos de `CARREIRAS`; "Analista de SI" na spec = `ROTULO_ANALISTA_SI`.
- Nenhum `*_body.html`, pasta de módulo, carreira, certificação, rota por perfil ou requisito de vaga novo. Módulos principais da `ROTA_VAGA` intactos.
- Sem dependências novas; portal estático e offline.
- Testes a partir da raiz: `python3 -m unittest discover -s _geradores/testes`. Antes, `free -h`; suíte inteira dentro de `systemd-run --user --scope --quiet -p MemoryMax=4G -p MemorySwapMax=1G`. Com menos de 4 GB disponíveis, rodar só os arquivos afetados.
- Branch de trabalho: `feat/trilhas-especializacao` (já existe, com o commit da spec).
- Toda mensagem de commit termina com `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Review Focus

1. **Filtro "Trilha 1" vs 11, 12 e 13:** o JS compara `cardTrilha === valor`; o botão 1 não pode mostrar nenhum card de 46–57, e cada botão 11–13 mostra só os 4 módulos da sua trilha. Coberto no Task 1 (`test_trilhas_11_a_13_nao_colidem_com_1`) e na verificação headless do Task 3.
2. **Recorte por posição nos testes das Trilhas 8–10:** `list(ESTUDOS_DADOS)[33:]` passa a ter 24 itens; o teste antigo tem de recortar `[33:45]`. Coberto no Task 1 (Step 1).
3. **Competência "Normas" com chips de apoio pendentes:** os chips 54 e 57 precisam existir com `data-slug` dentro de `id="vaga-normas"`, para o filtro da Trilha 13 achar a competência mesmo com os módulos pendentes. Coberto no Task 2 (`test_chips_de_apoio_normas_tem_data_slug`).
4. **Módulo novo numa rota sem a carreira do perfil:** o filtro de perfil esconderia o módulo da própria rota. Coberto no Task 1 (`test_modulos_novos_tem_carreira_das_rotas`).
5. **Blocos de trilha "11", "12" e "13" e cores próximas:** o `.track-tile` tem 32 px e o fúcsia fica perto do rosa (T7). Coberto pelas capturas de tela do Task 3.

---

### Task 1: Catálogo com 57 módulos, Trilhas 11–13 e cores

**Files:**
- Modify: `_geradores/estudos.txt` (cabeçalho + 12 linhas no fim)
- Modify: `_geradores/index_dados.py` (comentário do bloco de trilhas; `TRILHAS[11..13]`; 12 entradas no fim de `ESTUDOS_DADOS`)
- Modify: `_geradores/base.css` (3 tokens × 4 blocos; `.badge-t11`…`.badge-t13` logo após `.badge-t10`)
- Modify: `_geradores/index.css` (3 tokens × 4 blocos; `.track-tile.t11`…`.t13` logo após `.track-tile.t10`)
- Modify: `README.md` (contagens e tabela da grade)
- Modify: `_geradores/CURRICULO.md` (§3: seções das Trilhas 11–13 com os módulos 46–57)
- Create: `_geradores/testes/test_trilhas_especializacao.py`
- Modify: `_geradores/testes/test_curriculo.py`, `_geradores/testes/test_trilhas_empregabilidade.py`

**Interfaces:**
- Consumes: `test_tamanho_da_grade` (`test_curriculo.py`) e `test_tokens_de_cada_trilha` (`test_assets.py`), que já percorre `TRILHAS`.
- Produces: `TRILHAS[11]`, `TRILHAS[12]`, `TRILHAS[13]` com `id`, `nome`, `cor`, `cor_nome`, `descricao`; os 12 slugs da spec §2.2 em `estudos.txt` e `ESTUDOS_DADOS`; constante de teste `NOVOS` (os 12 slugs em ordem) em `test_trilhas_especializacao.py`, usada pelos Tasks 2 e 3.

- [ ] **Step 1: Escrever os testes que falham**

  - `test_curriculo.py`: `test_tamanho_da_grade` passa a exigir **57** e **13**. Em `test_curriculo_cobre_modulos_e_rota`, exigir também `"Trilha 11: Detecção Avançada & Threat Hunting"`, `"Trilha 12: Nuvem, Containers & Kubernetes"` e `"Trilha 13: Setor Regulado no Brasil"`.
  - `test_trilhas_empregabilidade.py`, `test_posicoes_34_a_45`: `list(ESTUDOS_DADOS)[33:45]` em vez de `[33:]` (Review Focus 2).
  - Criar `test_trilhas_especializacao.py` com o mesmo cabeçalho de `sys.path` e imports de `test_trilhas_empregabilidade.py`, `NOVOS` com os 12 slugs da spec §2.2 em ordem e a classe `TestCatalogoEspecializacao`:
    - `test_posicoes_46_a_57`: `list(ESTUDOS_DADOS)[45:] == NOVOS`; trilhas `[11]*4 + [12]*4 + [13]*4`; `nist` igual ao campo 7 das linhas da spec §2.2 (`Detect`, `Detect`, `Detect`, `Respond`, `Protect`, `Protect`, `Protect`, `Detect / Respond`, `Govern`, `Detect / Protect`, `Govern`, `Govern`).
    - `test_trilhas_novas`: para 11, 12 e 13, `nome`, `cor` e `cor_nome` iguais à spec §2.1.
    - `test_carreiras_dos_modulos_novos_existem`: todo rótulo em `carreiras` dos 12 módulos está em `{c["nome"] for c in CARREIRAS.values()}`.
    - `test_modulos_novos_tem_carreira_das_rotas` (Review Focus 4):
      ```python
      ROTAS_NOVAS = {
          ("Blue Team & Defesa", "Operações SOC & Resposta"): ["Monitoramento-de-Rede-NSM", "Engenharia-de-Deteccao", "Threat-Hunting", "SOAR-e-Automacao-de-Resposta"],
          ("Red Team & Pentest",): ["Seguranca-em-Kubernetes"],
          ("AppSec & DevSecOps",): ["Seguranca-de-Containers", "Seguranca-em-Kubernetes", "Infraestrutura-como-Codigo-Segura", "Deteccao-e-Resposta-em-Nuvem"],
          ("GRC & Auditoria",): ["Gestao-de-Riscos-de-Terceiros", "Legislacao-e-Crimes-Ciberneticos", "Regulacao-Setor-Financeiro", "Fraude-em-Pagamentos-e-Pix"],
          ("Perícia Forense & Malware",): ["Monitoramento-de-Rede-NSM", "Threat-Hunting", "Deteccao-e-Resposta-em-Nuvem", "Legislacao-e-Crimes-Ciberneticos"],
          (ROTULO_ANALISTA_SI,): ["Regulacao-Setor-Financeiro", "Gestao-de-Riscos-de-Terceiros", "SOAR-e-Automacao-de-Resposta"],
      }
      # para cada (perfis, slugs): set(perfis) & set(ESTUDOS_DADOS[slug]["carreiras"]) não vazio
      ```
    - `test_trilhas_11_a_13_nao_colidem_com_1` (Review Focus 1): gerar o portal com `gerar_index_html(output_path=Path(tmp) / "index.html")`; para cada slug de `NOVOS`, o card `id="estudo-<slug>"` tem `data-trilha` igual à trilha do módulo (`"11"`, `"12"` ou `"13"`), nunca `"1"`; o HTML contém `data-value="11"`, `data-value="12"` e `data-value="13"`. Usar o mesmo regex de `test_trilha_10_nao_colide_com_1`.

- [ ] **Step 2: Rodar e confirmar que falham**

  Run (em `_geradores/`): `python3 -m unittest testes.test_trilhas_especializacao testes.test_curriculo testes.test_trilhas_empregabilidade 2>&1 | tail -3`
  Expected: FAIL (45 ≠ 57, `KeyError: 11`, slugs ausentes). `test_posicoes_34_a_45` ainda passa.

- [ ] **Step 3: `estudos.txt`**

  Cabeçalho "(57 Módulos)" e as 3 linhas de legenda da spec §2.2; acrescentar no fim as 12 linhas da spec §2.2, literalmente.

- [ ] **Step 4: `index_dados.py`**

  - Comentário `# 1. TRILHAS ESTRUTURANTES (10 Trilhas)` sem número fixo: `# 1. TRILHAS ESTRUTURANTES`.
  - `TRILHAS[11..13]`: valores da spec §2.1, `descricao` literal.
  - 12 entradas no fim de `ESTUDOS_DADOS`, na ordem 46 → 57. Campos a partir da spec §2.3: `titulo` = texto após o segundo `: ` do cabeçalho do módulo (igual ao `estudos.txt`); `subtitulo`, `mitre`, `pergunta_chave` = linhas homônimas, sem aspas; `trilha`, `nist`, `tempo_minutos` = linha "Trilha · NIST · Tempo"; `carreiras` = linha "Carreiras", com "Analista de SI" → `ROTULO_ANALISTA_SI`; `simulador_nome` = nome em itálico após "Simulador:"; `fatos` = os 4 itens de "Fatos".

- [ ] **Step 5: CSS**

  - Em `base.css` e `index.css`, logo abaixo de cada `--t10-orange:`, declarar `--t11-fuchsia`, `--t12-teal`, `--t13-lime`: cores claras nos blocos `:root` e `[data-theme="light"]`, escuras nos blocos `@media (prefers-color-scheme: dark)` e `[data-theme="dark"]`.
  - `base.css`, após `.badge-t10`: as 3 regras `.badge-t11`…`.badge-t13` da spec §2.1, literalmente.
  - `index.css`, após `.track-tile.t10`: `.track-tile.t11 { background: var(--t11-fuchsia); }` e equivalentes para 12 (`--t12-teal`) e 13 (`--t13-lime`).

- [ ] **Step 6: Documentação que lista os módulos**

  - `README.md`: "45" → "57" módulos e "10" → "13" trilhas no topo, no título "Grade Curricular dos 57 Módulos", no diagrama do pipeline e na descrição de `estudos.txt`; acrescentar à tabela da grade as linhas 46–57 no formato das existentes (número, slug, título, `Trilha N: <nome curto>`, NIST, nome do simulador). Nomes curtos: "Trilha 11: Detecção Avançada", "Trilha 12: Nuvem & Kubernetes", "Trilha 13: Setor Regulado BR".
  - `CURRICULO.md` §3: após a Trilha 10, as seções `### Trilha 11: Detecção Avançada & Threat Hunting (\`#A21CAF\`)`, `### Trilha 12: Nuvem, Containers & Kubernetes (\`#0F766E\`)` e `### Trilha 13: Setor Regulado no Brasil (\`#4D7C0F\`)`, cada uma com os 4 módulos no formato de `#### 45. Backup-Imutavel-e-Recuperacao` (campos Objetivos, Conceitos-Chave, Simulador Interativo em JS etc., copiados da spec §2.3, incluindo as linhas "Conferência na construção" dos módulos 54–56).

- [ ] **Step 7: Rodar e confirmar que passam**

  Run (na raiz): `free -h | head -2 && systemd-run --user --scope --quiet -p MemoryMax=4G -p MemorySwapMax=1G python3 -m unittest discover -s _geradores/testes 2>&1 | tail -3`
  Expected: `OK`. (`test_tokens_de_cada_trilha` agora cobre 13 trilhas; `test_cli` confirma os 57 slugs no README.)

- [ ] **Step 8: Commit**

  ```bash
  git add _geradores/estudos.txt _geradores/index_dados.py _geradores/base.css _geradores/index.css README.md _geradores/CURRICULO.md _geradores/testes/
  git commit -m "feat(curriculo): grade com 57 módulos e Trilhas 11, 12 e 13

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

---

### Task 2: Rota da Vaga, necessidades e certificações

**Files:**
- Modify: `_geradores/index_dados.py` (`ROTA_VAGA`, `NECESSIDADES`, `CERTIFICACOES`)
- Test: `_geradores/testes/test_trilhas_especializacao.py`

**Interfaces:**
- Consumes: `NOVOS` e os 12 slugs (Task 1); `render_rota_vaga(rota, status_map) -> str` de `build_index.py` (cada chip tem `data-slug`).
- Produces: só dados.

- [ ] **Step 1: Escrever os testes que falham** (classe `TestLigacoesEspecializacao`)

  - `test_principais_da_rota_intactos`: `{c["id"]: c["principais"] for c in ROTA_VAGA}` igual ao dicionário de `test_principais_da_rota_intactos` em `test_trilhas_empregabilidade.py` (copiar a constante).
  - `test_apoios_novos`: `apoio` de `normas` termina com `["Regulacao-Setor-Financeiro", "Gestao-de-Riscos-de-Terceiros"]`; `apoio` de `resposta_incidentes` termina com `["SOAR-e-Automacao-de-Resposta"]`; as demais competências têm o mesmo `apoio` de antes.
  - `test_necessidades_novas`: os 12 últimos itens de `NECESSIDADES` são, em ordem, os da spec §3.3 (`desafio`, `slug`, `categoria`, `icone`).
  - `test_certificacoes_novas`: para cada sigla da spec §3.4, `modulos` termina com a lista da spec, na ordem da spec.
  - `test_chips_de_apoio_normas_tem_data_slug` (Review Focus 3): `render_rota_vaga(ROTA_VAGA, {})` contém `data-slug="Regulacao-Setor-Financeiro"` e `data-slug="Gestao-de-Riscos-de-Terceiros"` dentro do `<article ... id="vaga-normas">`, e `data-slug="SOAR-e-Automacao-de-Resposta"` dentro de `id="vaga-resposta_incidentes"`.

- [ ] **Step 2: Rodar e confirmar que falham**

  Run (em `_geradores/`): `python3 -m unittest testes.test_trilhas_especializacao 2>&1 | tail -3`
  Expected: FAIL nos testes de dados (o de principais intactos já passa).

- [ ] **Step 3: Atualizar os dados**

  `ROTA_VAGA` (spec §3.1), `NECESSIDADES` (12 itens no fim, spec §3.3) e `CERTIFICACOES` (spec §3.4), sempre acrescentando no fim das listas.

- [ ] **Step 4: Rodar os testes de rota e filtro**

  Run (em `_geradores/`): `python3 -m unittest testes.test_trilhas_especializacao testes.test_trilhas_empregabilidade testes.test_rota_vaga testes.test_filtro_secoes 2>&1 | tail -3`
  Expected: `OK`. `test_modulos_da_rota_tem_carreira_analista` confirma que os 3 apoios novos levam `ROTULO_ANALISTA_SI`; `test_certificacoes_exatas` confirma que nenhuma sigla nova entrou.

- [ ] **Step 5: Commit**

  ```bash
  git add _geradores/index_dados.py _geradores/testes/test_trilhas_especializacao.py
  git commit -m "feat(portal): módulos 46–57 na rota da vaga (apoio), necessidades e certificações

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

---

### Task 3: Documentação curricular, portal regenerado e verificação final

**Files:**
- Modify: `_geradores/CURRICULO.md` (§1, §2, §4, §5)
- Modify: `README.md` (diagrama das trilhas, "Rota por Vaga", "Perfis de Carreira")
- Modify: `docs/superpowers/specs/2026-11-01-trilhas-empregabilidade-design.md` (nota no topo)
- Modify: `docs/superpowers/specs/2026-11-02-trilhas-especializacao-design.md` (Status)
- Modify: `_geradores/testes/test_trilhas_empregabilidade.py` (`test_rotas_por_perfil_no_curriculo`)
- Regenerate: `index.html` e as 45 páginas `*/treinamento-*.html`

**Interfaces:**
- Consumes: dados dos Tasks 1 e 2.

- [ ] **Step 1: Escrever o teste que falha**

  Em `test_trilhas_empregabilidade.py`, `test_rotas_por_perfil_no_curriculo` passa a exigir as 6 sequências da spec §3.2, escritas como no §5 atual (dois dígitos separados por ` -> `, entre crases, sem negrito). Exemplo da rota 1: `` `01 -> 02 -> 34 -> 36 -> 05 -> 06 -> 07 -> 48 -> 10 -> 39 -> 16 -> 46 -> 17 -> 47 -> 18 -> 49 -> 42` ``.

- [ ] **Step 2: Rodar e confirmar que falha**

  Run (em `_geradores/`): `python3 -m unittest testes.test_trilhas_empregabilidade 2>&1 | tail -2`
  Expected: FAIL em `test_rotas_por_perfil_no_curriculo`.

- [ ] **Step 3: `CURRICULO.md`**

  - §1: "57 módulos temáticos" e "13 trilhas estruturantes".
  - §2: no Mermaid, os nós `T11["Trilha 11: Detecção Avançada & Threat Hunting"]`, `T12[...]`, `T13[...]` e as arestas da spec §4.1 (T11 → DE, RS; T12 → PR, DE, RS; T13 → GV, DE, PR); na tabela, as 3 linhas novas (cor, foco = descrição da spec §2.1, módulos 46–49, 50–53, 54–57).
  - §4: recalcular a tabela NIST a partir de `estudos.txt` (uma função conta para cada módulo cujo campo `nist` a contém). Conferir com: `python3 -c "import collections; c=collections.Counter(); [c.update(f.strip() for f in l.strip().split('|')[6].split('/')) for l in open('_geradores/estudos.txt', encoding='utf-8') if l.strip() and not l.startswith('#')]; print(c)"`. Expected: `Protect 32, Detect 18, Respond 8, Govern 7, Identify 6, Recover 4`.
  - §5: as 6 rotas da spec §3.2.

- [ ] **Step 4: `README.md` e notas de spec**

  - Diagrama das trilhas: nós T11–T13 no formato dos existentes (ex.: `T11["Trilha 11: Detecção Avançada<br><small>Módulos 46 a 49 | Detecção como Código, Threat Hunting, NSM e SOAR</small>"]`).
  - "Rota por Vaga": acrescentar os apoios novos (§3.1) na tabela da seção.
  - "Perfis de Carreira": citar as Trilhas 11–13 nos perfis cuja rota mudou.
  - Spec de 2026-11-01: nota no topo `> **Atualização 2026-11-02:** grade ampliada para 57 módulos / 13 trilhas — ver [2026-11-02-trilhas-especializacao-design.md](2026-11-02-trilhas-especializacao-design.md).`
  - Spec de 2026-11-02: `**Status:** Aprovada (2026-11-02) e implementada (branch feat/trilhas-especializacao)`.

- [ ] **Step 5: Regenerar portal e módulos; suíte inteira**

  Run (na raiz): `free -h | head -2 && systemd-run --user --scope --quiet -p MemoryMax=4G -p MemorySwapMax=1G ./_geradores/gerar.sh todos && systemd-run --user --scope --quiet -p MemoryMax=4G -p MemorySwapMax=1G python3 -m unittest discover -s _geradores/testes 2>&1 | tail -3`
  Expected: 45 módulos compilados sem erro, portal gerado, nenhum SVG novo em `_geradores/cache_diagramas/` (`git status --short _geradores/cache_diagramas` vazio) e `OK`.

- [ ] **Step 6: Verificação headless do filtro (Review Focus 1 e 3)**

  Copiar `index.html` para o diretório de rascunho da sessão, injetar antes de `</body>` um `<script>` que, no `load`, aplica cada filtro com `switchTab('trilhas')` + `setSubFilter(v, botão)` e grava em `<pre id="resultado">` um JSON com as contagens visíveis (`el.checkVisibility()`) de `.study-card`, `.need-card`, `.vaga-competencia`, chips `#secao-rota-vaga .vaga-chips [data-slug]` e `.cert-row`. Rodar `google-chrome --headless=new --no-sandbox --disable-gpu --virtual-time-budget=3000 --dump-dom file://<cópia>` e ler o `<pre>`.
  Expected:

  | Filtro | cards | necessidades | competências | chips da rota | linhas de certificação |
  |---|---|---|---|---|---|
  | Trilha 11 | 4 | 4 | 1 | 1 | 3 |
  | Trilha 12 | 4 | 4 | 0 | 0 | 4 |
  | Trilha 13 | 4 | 4 | 1 | 2 | 3 |
  | Trilha 1 | 5 | igual à `main` atual | igual à `main` atual | igual à `main` atual | igual à `main` atual |

  Nenhum card de 46–57 visível com a Trilha 1.

- [ ] **Step 7: Verificação visual (Review Focus 5)**

  `google-chrome --headless=new --no-sandbox --disable-gpu --hide-scrollbars --window-size=1280,1800 --screenshot=<rascunho>/portal-<tema>.png` com a Trilha 13 selecionada, nos temas claro e escuro (`data-theme` no `<html>` da cópia), e uma captura a 390 px de largura. Conferir: blocos "11", "12" e "13" sem corte; selos e blocos das Trilhas 11–13 com as cores da spec e distinguíveis do rosa (T7) e do ciano (T5); 12 cards novos como pendentes; sem rolagem horizontal da página.

- [ ] **Step 8: Commit**

  ```bash
  git add _geradores/CURRICULO.md README.md docs/superpowers/specs/ _geradores/testes/test_trilhas_empregabilidade.py index.html */treinamento-*.html
  git commit -m "docs(curriculo): Trilhas 11–13, distribuição NIST e rotas por perfil; recompila portal e módulos

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```
