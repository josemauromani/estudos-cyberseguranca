# Trilhas de Empregabilidade (8, 9 e 10) — Implementation Plan

**Status:** Concluído em 2026-11-01 (commits `b757453`..`83eacd1`, mais `770ace4`).

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ampliar o catálogo de 33 para 45 módulos em 10 trilhas (Ferramentas & Automação, Identidade & AD, Resiliência & Ransomware), ligar os módulos novos às rotas, à Rota da Vaga (como apoio), às necessidades e às certificações, e fazer os testes derivarem os totais dos dados.

**Architecture:** `estudos.txt` e `index_dados.py` continuam sendo a fonte única; `build_index.py` só renderiza, e já deriva filtros, blocos de trilha e contagens de `TRILHAS` e do catálogo. O número de cada módulo é a sua posição em `ESTUDOS_DADOS`, por isso os módulos novos entram no fim. Nenhum `*_body.html` novo é criado: os módulos 34–45 aparecem como pendentes.

**Tech Stack:** Python 3 (stdlib, `unittest`), HTML/CSS estáticos, Bash (`gerar.sh`), Chrome headless só para a verificação final.

**Spec:** `docs/superpowers/specs/2026-11-01-trilhas-empregabilidade-design.md` (aprovada em 2026-11-01). Os conteúdos de módulo, tabelas de rota, necessidades e certificações são copiados **literalmente** da spec; o plano indica a seção.

## Global Constraints

- Todo texto de interface e documentação em pt-BR.
- Os módulos 01–33 e seus slugs não mudam. Os módulos novos entram no **fim** de `estudos.txt` e de `ESTUDOS_DADOS`, na ordem da spec §2.2 (34 → 45).
- Trilhas: 8 `Ferramentas & Automação do Analista` (`#475569` / escuro `#94A3B8`, token `--t8-slate`, `cor_nome` `"slate"`); 9 `Identidade Corporativa & Active Directory` (`#4F46E5` / `#818CF8`, `--t9-indigo`, `"indigo"`); 10 `Resiliência, Crise & Ransomware` (`#C2410C` / `#FB923C`, `--t10-orange`, `"orange"`).
- Rótulos de carreira só com os nomes exatos de `CARREIRAS`; "Analista de SI" na spec = `ROTULO_ANALISTA_SI`.
- Nenhum `*_body.html`, pasta de módulo, carreira, rota por perfil ou requisito de vaga novo. Módulos principais da `ROTA_VAGA` intactos.
- Sem dependências novas; portal estático e offline.
- Testes a partir da raiz: `python3 -m unittest discover -s _geradores/testes -v`. Antes, `free -h`; suíte inteira dentro de `systemd-run --user --scope --quiet -p MemoryMax=4G -p MemorySwapMax=1G`. Com menos de 4 GB disponíveis, rodar só os arquivos afetados.
- Branch de trabalho: `feat/trilhas-empregabilidade`, criada a partir da `main`.
- Toda mensagem de commit termina com `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Review Focus

1. **Filtro "Trilha 10" vs "Trilha 1":** o JS compara `cardTrilha === valor`; o botão 10 deve mostrar só 42–45 e o botão 1 não pode mostrar nenhum deles. Coberto no Task 2 (`test_trilha_10_nao_colide_com_1`).
2. **Seletores e tokens `t1` vs `t10`:** `--t1-blue:` e `.track-tile.t1` não podem ser confundidos com `--t10-orange:` e `.track-tile.t10`. Coberto no Task 1 (`test_tokens_de_cada_trilha`, contagem exata por nome completo do token).
3. **Rótulo de carreira digitado errado:** o filtro de perfil usa `includes`; um rótulo fora de `CARREIRAS` faria o módulo sumir de todo filtro. Coberto no Task 2 (`test_carreiras_dos_modulos_existem`).
4. **Filtro de seções com a Trilha 9:** a competência "Controles" precisa aparecer com os chips 38 e 40 mesmo com os módulos principais pendentes. Coberto no Task 3 (`test_chips_de_apoio_novos_tem_data_slug`) e na verificação headless do Task 4.
5. **Bloco de trilha com dois dígitos:** o `.track-tile` tem 32 px; "10" tem de caber sem cortar. Coberto pela captura de tela do Task 4.

---

### Task 1: Testes derivam os totais dos dados

Refatoração sem mudança de comportamento: a suíte continua verde com 33 módulos / 7 trilhas.

**Files:**
- Modify: `_geradores/testes/test_curriculo.py`
- Modify: `_geradores/testes/test_index.py`
- Modify: `_geradores/testes/test_cli.py`
- Modify: `_geradores/testes/test_assets.py`

**Interfaces:**
- Produces: `TestCurriculo.test_tamanho_da_grade`, único teste com os totais fixos (aqui 33 / 7; o Task 2 muda para 45 / 10). `TestAssets.test_tokens_de_cada_trilha`, que percorre `TRILHAS`.

- [ ] **Step 1: Criar a branch**

  Run: `git checkout -b feat/trilhas-empregabilidade`

- [ ] **Step 2: Reescrever os testes de contagem**

  - `test_curriculo.py`:
    - `test_estudos_txt_contains_33_valid_entries` → `test_estudos_txt_formato_valido`: mantém todas as checagens de formato, remove a contagem; trilha válida passa a ser `int(trilha) in TRILHAS` (importar `TRILHAS` de `index_dados`, com `sys.path` apontando para `_geradores`).
    - `test_curriculo_cobre_33_modulos_e_rota` → `test_curriculo_cobre_modulos_e_rota` (mesmo corpo).
    - Novo:
      ```python
      def test_tamanho_da_grade(self):
          """Único ponto com os totais fixos: crescer a grade é decisão explícita."""
          self.assertEqual(len(self._linhas_catalogo()), 33)
          self.assertEqual(len(TRILHAS), 7)
      ```
      com `_linhas_catalogo()` devolvendo as linhas não vazias e não comentadas de `estudos.txt`, reaproveitada pelo teste de formato.
  - `test_index.py`:
    - `test_estudos_dados_has_33_entries` → `test_estudos_dados_tem_uma_entrada_por_linha_do_catalogo`: `len(ESTUDOS_DADOS) == len(slugs de estudos.txt)`.
    - Em `test_estudos_slugs_match_estudos_txt_exactly`, remover `assertEqual(len(slugs_txt), 33)` (a igualdade de conjuntos fica).
    - Em `test_estudos_dados_schema_fields`: `self.assertIn(dados["trilha"], TRILHAS, ...)`.
    - `test_trilhas_definition`: `set(TRILHAS) == set(range(1, len(TRILHAS) + 1))`; o laço passa a percorrer `TRILHAS`; cada trilha tem `cor_nome` não vazio e ao menos um módulo em `ESTUDOS_DADOS`.
    - No teste do portal, trocar `assertIn("33", ...)`/`assertIn("7", ...)` por `assertIn(f'<span class="stat-number">{len(ESTUDOS_DADOS)}</span>', conteudo)` e `assertIn(f'<span class="stat-number">{len(TRILHAS)}</span>', conteudo)`.
  - `test_cli.py`: `test_readme_contains_all_33_studies` → `test_readme_contains_all_studies`; remover a contagem fixa.
  - `test_assets.py`: tirar `--t1-blue` … `--t7-rose` da lista fixa de `test_base_css_contains_design_tokens`; trocar `test_trilha7_tokens_em_4_blocos` por:
    ```python
    def test_tokens_de_cada_trilha(self):
        base = self.css_file.read_text(encoding="utf-8")
        index = (self.root / "_geradores" / "index.css").read_text(encoding="utf-8")
        for tid, info in TRILHAS.items():
            token = f"--t{tid}-{info['cor_nome']}:"
            with self.subTest(trilha=tid):
                self.assertEqual(base.count(token), 4)
                self.assertEqual(index.count(token), 4)
                self.assertIn(f".badge-t{tid} ", base)
                self.assertIn(f".track-tile.t{tid} ", index)
    ```

- [ ] **Step 3: Rodar os 4 arquivos e confirmar que passam**

  Run: `for t in curriculo index cli assets; do python3 -m unittest discover -s _geradores/testes -p "test_$t.py" 2>&1 | tail -1; done`
  Expected: `OK` nas 4 linhas (refatoração: nada muda de comportamento). Se `test_tokens_de_cada_trilha` falhar para alguma trilha 1–7, o nome do token difere de `--t{id}-{cor_nome}`: corrigir o `cor_nome` em `TRILHAS`, nunca o CSS.

- [ ] **Step 4: Confirmar que não sobrou contagem fixa**

  Run: `grep -nE '\b33\b|range\(1, ?8\)|<= ?7\b' _geradores/testes/*.py`
  Expected: só a linha `33` de `test_tamanho_da_grade` (e, se houver, `>= 28` em `test_montar.py`, que é limite inferior e fica).

- [ ] **Step 5: Commit**

  ```bash
  git add _geradores/testes/
  git commit -m "test(curriculo): totais de módulos e trilhas derivados dos dados

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

---

### Task 2: Catálogo com 45 módulos, Trilhas 8–10 e cores

**Files:**
- Modify: `_geradores/estudos.txt` (cabeçalho + 12 linhas no fim)
- Modify: `_geradores/index_dados.py` (docstring; `TRILHAS[8..10]`; 12 entradas no fim de `ESTUDOS_DADOS`)
- Modify: `_geradores/base.css` (3 tokens × 4 blocos; `.badge-t8`…`.badge-t10` logo após `.badge-t7`)
- Modify: `_geradores/index.css` (3 tokens × 4 blocos; `.track-tile.t8`…`.t10` logo após `.track-tile.t7`)
- Modify: `_geradores/montar.py:253` (ajuda do `--trilha`)
- Modify: `README.md` (contagens e tabela da grade)
- Modify: `_geradores/CURRICULO.md` (§3: seções das Trilhas 8–10 com os módulos 34–45)
- Create: `_geradores/testes/test_trilhas_empregabilidade.py`
- Test: `_geradores/testes/test_curriculo.py`

**Interfaces:**
- Consumes: `test_tamanho_da_grade` e `test_tokens_de_cada_trilha` (Task 1).
- Produces: `TRILHAS[8]`, `TRILHAS[9]`, `TRILHAS[10]` com `id`, `nome`, `cor`, `cor_nome`, `descricao`; os 12 slugs da spec §2.2 em `estudos.txt` e `ESTUDOS_DADOS`; constante de teste `NOVOS = [...]` (os 12 slugs, em ordem) em `test_trilhas_empregabilidade.py`, reaproveitada pelo Task 3.

- [ ] **Step 1: Escrever os testes que falham**

  - `test_curriculo.py`: `test_tamanho_da_grade` passa a exigir **45** e **10**. Em `test_curriculo_cobre_modulos_e_rota`, exigir também `"Trilha 8: Ferramentas & Automação do Analista"`, `"Trilha 9: Identidade Corporativa & Active Directory"` e `"Trilha 10: Resiliência, Crise & Ransomware"`.
  - Criar `test_trilhas_empregabilidade.py` (mesmo cabeçalho de `sys.path` de `test_rota_vaga.py`), classe `TestCatalogoNovo`:
    - `test_posicoes_34_a_45`: `list(ESTUDOS_DADOS)[33:] == NOVOS`, e as trilhas são `[8]*4 + [9]*4 + [10]*4`.
    - `test_trilhas_novas`: para 8, 9, 10, `nome`, `cor` e `cor_nome` iguais à tabela da spec §2.1.
    - `test_modulo_37_tem_todas_as_carreiras`: `set(ESTUDOS_DADOS["Laboratorio-Domestico-e-Portfolio"]["carreiras"]) == {c["nome"] for c in CARREIRAS.values()}`.
    - `test_carreiras_dos_modulos_existem` (Review Focus 3): todo rótulo em `carreiras` de **todos** os módulos pertence a `{c["nome"] for c in CARREIRAS.values()}`.
    - `test_trilha_10_nao_colide_com_1` (Review Focus 1): gerar o portal com `gerar_index_html(output_path=Path(tmp) / "index.html")` (como em `test_filtro_secoes.py`) e, no HTML, conferir que cada card `id="estudo-<slug>"` de 42–45 traz `data-trilha="10"`, que nenhum card de `NOVOS` traz `data-trilha="1"` e que existe o botão `data-value="10"`.

- [ ] **Step 2: Rodar e confirmar que falham**

  Run (em `_geradores/`): `python3 -m unittest testes.test_trilhas_empregabilidade testes.test_curriculo 2>&1 | tail -3`
  Expected: FAIL (33 ≠ 45, `KeyError: 8`, slugs ausentes).

- [ ] **Step 3: `estudos.txt`**

  Cabeçalho "(45 Módulos)" e as 3 linhas de legenda de trilha da spec §2.2; acrescentar no fim as 12 linhas da spec §2.2, literalmente.

- [ ] **Step 4: `index_dados.py`**

  - Docstring/comentários: "45 módulos", "10 Trilhas".
  - `TRILHAS[8..10]`: valores da spec §2.1 (`descricao` literal).
  - 12 entradas em `ESTUDOS_DADOS`, na ordem 34 → 45. Mapeamento de cada campo a partir da spec §2.3: `titulo` = título após os dois-pontos do cabeçalho do módulo (igual ao `estudos.txt`); `subtitulo`, `mitre`, `pergunta_chave` = linhas homônimas; `trilha`, `nist`, `tempo_minutos` = linha "Trilha · NIST · Tempo" (para o 37, `nist` é `"Protect"`); `carreiras` = linha "Carreiras" com "Analista de SI" → `ROTULO_ANALISTA_SI` e, no 37, as 7 de `CARREIRAS`; `simulador_nome` = nome em itálico do simulador; `fatos` = os 4 itens da spec, na ordem.

- [ ] **Step 5: CSS e `montar.py`**

  - Em `base.css` e `index.css`, logo abaixo de cada `--t7-rose:`, declarar `--t8-slate`, `--t9-indigo`, `--t10-orange`: cores claras nos blocos `:root` e `[data-theme="light"]`, escuras nos blocos `@media (prefers-color-scheme: dark)` e `[data-theme="dark"]` (valores em Global Constraints). Comentário "7 Trilhas" → "10 Trilhas".
  - `base.css`, após `.badge-t7`:
    ```css
    .badge-t8 { background-color: rgba(71, 85, 105, 0.15); color: var(--t8-slate); }
    .badge-t9 { background-color: rgba(79, 70, 229, 0.15); color: var(--t9-indigo); }
    .badge-t10 { background-color: rgba(194, 65, 12, 0.15); color: var(--t10-orange); }
    ```
  - `index.css`, após `.track-tile.t7`: `.track-tile.t8 { background: var(--t8-slate); }` e equivalentes para 9 e 10.
  - `montar.py:253`: ajuda `"Número da trilha, conforme o catálogo (estudos.txt), para sobrescrever o valor do catálogo."`

- [ ] **Step 6: Documentação que lista os módulos**

  - `README.md`: "33" → "45" módulos e "7" → "10" trilhas no topo, no título "Grade Curricular dos 45 Módulos", no diagrama do pipeline ("45 Módulos 100% Offline") e na descrição de `estudos.txt`; acrescentar à tabela da grade as linhas 34–45 (colunas existentes: #, slug, título, trilha, NIST, simulador), com a trilha escrita "Trilha 8: Ferramentas & Automação", "Trilha 9: Identidade & AD" ou "Trilha 10: Resiliência & Ransomware".
  - `CURRICULO.md` §3: após a Trilha 7, as seções `### Trilha 8: Ferramentas & Automação do Analista (\`#475569\`)`, `### Trilha 9: Identidade Corporativa & Active Directory (\`#4F46E5\`)` e `### Trilha 10: Resiliência, Crise & Ransomware (\`#C2410C\`)`, com os módulos 34–45 no formato das seções existentes (`#### 34. Linux-para-Seguranca`, Título, Função NIST, Tempo e Carreiras, Objetivos, Pré-requisitos, Conceitos-Chave, Simulador), conteúdo da spec §2.3. No 43, incluir as pendências de verificação.

- [ ] **Step 7: Rodar e confirmar que passam**

  Run: `free -h | head -2 && systemd-run --user --scope --quiet -p MemoryMax=4G -p MemorySwapMax=1G python3 -m unittest discover -s _geradores/testes 2>&1 | tail -3`
  Expected: `OK`. (`test_tokens_de_cada_trilha` agora cobre 10 trilhas.)

- [ ] **Step 8: Commit**

  ```bash
  git add _geradores/estudos.txt _geradores/index_dados.py _geradores/base.css _geradores/index.css _geradores/montar.py README.md _geradores/CURRICULO.md _geradores/testes/
  git commit -m "feat(curriculo): grade com 45 módulos e Trilhas 8, 9 e 10

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

---

### Task 3: Rota da Vaga, necessidades e certificações

**Files:**
- Modify: `_geradores/index_dados.py` (`ROTA_VAGA`, `NECESSIDADES`, `CERTIFICACOES`)
- Test: `_geradores/testes/test_trilhas_empregabilidade.py`

**Interfaces:**
- Consumes: `NOVOS` e os 12 slugs (Task 2); `render_rota_vaga(rota, status_map) -> str` de `build_index.py` (cada chip tem `data-slug`).
- Produces: nada consumido por outro task além dos dados.

- [ ] **Step 1: Escrever os testes que falham** (classe `TestLigacoesNovas`)

  - `test_principais_da_rota_intactos`: `{c["id"]: c["principais"] for c in ROTA_VAGA}` igual a:
    ```python
    {
        "solucoes": ["Segmentacao-e-Firewall", "Seguranca-em-Endpoints-EDR", "Protecao-de-Dados-e-Conteudo", "Seguranca-de-Redes-Defesa"],
        "banco_dados": ["Seguranca-de-Bancos-de-Dados"],
        "ingles": ["Ingles-Tecnico-Ciber"],
        "normas": ["PCI-DSS", "ISO-27001-e-27002", "Gestao-de-Riscos-TI"],
        "resposta_incidentes": ["Resposta-a-Incidentes"],
        "controles": ["ISO-27001-e-27002"],
        "formacao": ["Certificacoes-e-Carreira"],
    }
    ```
  - `test_apoios_novos`: os apoios da spec §3.1 estão, nessa ordem, no fim da lista `apoio` de cada competência.
  - `test_necessidades_novas`: cada slug de `NOVOS` aparece em exatamente um item novo de `NECESSIDADES`, com `desafio`, `categoria` e `icone` da spec §3.3.
  - `test_certificacoes_novas`: as associações da spec §3.4 estão no fim de `modulos` de cada sigla; CCSP inalterada.
  - `test_chips_de_apoio_novos_tem_data_slug` (Review Focus 4): `render_rota_vaga(ROTA_VAGA, {})` contém `data-slug="Active-Directory-Fundamentos"` e `data-slug="PAM-e-Acessos-Privilegiados"` dentro do `<article ... id="vaga-controles">`.

- [ ] **Step 2: Rodar e confirmar que falham**

  Run (em `_geradores/`): `python3 -m unittest testes.test_trilhas_empregabilidade 2>&1 | tail -3`
  Expected: FAIL nos 4 testes de dados (o de principais intactos já passa).

- [ ] **Step 3: Atualizar os dados**

  `ROTA_VAGA` (spec §3.1), `NECESSIDADES` (12 itens no fim, spec §3.3) e `CERTIFICACOES` (spec §3.4), sempre acrescentando no fim das listas.

- [ ] **Step 4: Rodar a suíte da rota e a nova**

  Run (em `_geradores/`): `python3 -m unittest testes.test_trilhas_empregabilidade testes.test_rota_vaga testes.test_filtro_secoes 2>&1 | tail -3`
  Expected: `OK`. `test_modulos_da_rota_tem_carreira_analista` confirma que os 7 apoios novos levam `ROTULO_ANALISTA_SI` (definido no Task 2).

- [ ] **Step 5: Commit**

  ```bash
  git add _geradores/index_dados.py _geradores/testes/test_trilhas_empregabilidade.py
  git commit -m "feat(portal): módulos 34–45 na rota da vaga (apoio), necessidades e certificações

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

---

### Task 4: Documentação curricular, portal regenerado e verificação final

**Files:**
- Modify: `_geradores/CURRICULO.md` (§1, §2, §4, §5)
- Modify: `README.md` (diagrama das trilhas, "Rota por Vaga", "Perfis de Carreira")
- Modify: `docs/superpowers/specs/2026-10-15-competencias-vaga-analista-si-design.md` (nota no topo)
- Modify: `docs/superpowers/specs/2026-11-01-trilhas-empregabilidade-design.md` (Status)
- Regenerate: `index.html`, `*/treinamento-*.html` dos módulos 01–11
- Test: `_geradores/testes/test_trilhas_empregabilidade.py`

**Interfaces:**
- Consumes: dados dos Tasks 2 e 3.

- [ ] **Step 1: Escrever o teste que falha**

  `test_rotas_por_perfil_no_curriculo`: `CURRICULO.md` contém as 6 sequências da spec §3.2, cada uma escrita como no §5 atual (números de dois dígitos separados por ` -> `, sem negrito), por exemplo `01 -> 02 -> 34 -> 36 -> 05 -> 06 -> 07 -> 10 -> 39 -> 16 -> 17 -> 18 -> 42`.

- [ ] **Step 2: Rodar e confirmar que falha**

  Run (em `_geradores/`): `python3 -m unittest testes.test_trilhas_empregabilidade 2>&1 | tail -2`
  Expected: FAIL em `test_rotas_por_perfil_no_curriculo`.

- [ ] **Step 3: `CURRICULO.md`**

  - §1: "45 módulos temáticos" e "10 trilhas estruturantes".
  - §2: no Mermaid, `T8["Trilha 8: Ferramentas & Automação do Analista"]`, `T9[...]`, `T10[...]` e as arestas `T8 --> PR`, `T8 --> DE`, `T9 --> PR`, `T9 --> DE`, `T10 --> RS`, `T10 --> RC`; na tabela, as 3 linhas novas (cor, foco = descrição da spec §2.1, módulos 34–37 / 38–41 / 42–45); título "Mapa das 10 Trilhas Temáticas".
  - §4: recalcular a tabela NIST a partir de `estudos.txt` (uma função conta para cada módulo cujo campo `nist` a contém). Conferir com: `python3 -c "import collections; c=collections.Counter(); [c.update(f.strip() for f in l.split('|')[6].split('/')) for l in open('_geradores/estudos.txt', encoding='utf-8') if l.strip() and not l.startswith('#')]; print(c)"`. Respond deve dar 6 e Recover 4.
  - §5: as 6 rotas da spec §3.2.

- [ ] **Step 4: `README.md` e notas de spec**

  - Diagrama das trilhas: nós T8–T10 no formato dos existentes (ex.: `T8["Trilha 8: Ferramentas & Automação<br><small>Módulos 34 a 37 | Linux, Python, PowerShell e Homelab</small>"]`).
  - "Rota por Vaga": acrescentar os apoios novos na tabela da seção.
  - "Perfis de Carreira": citar as Trilhas 8–10 onde a rota do perfil mudou.
  - Spec de 2026-10-15: nota no topo `> **Atualização 2026-11-01:** grade ampliada para 45 módulos / 10 trilhas — ver [2026-11-01-trilhas-empregabilidade-design.md](2026-11-01-trilhas-empregabilidade-design.md).`
  - Spec de 2026-11-01: `**Status:** Aprovada (2026-11-01) e implementada (branch feat/trilhas-empregabilidade)`.

- [ ] **Step 5: Regenerar portal e módulos; suíte inteira**

  Run: `free -h | head -2 && ./_geradores/gerar.sh todos && ./_geradores/gerar.sh portal && systemd-run --user --scope --quiet -p MemoryMax=4G -p MemorySwapMax=1G python3 -m unittest discover -s _geradores/testes 2>&1 | tail -3`
  Expected: compilação dos 11 módulos sem erro, `index.html gerado com sucesso` e `OK`.

- [ ] **Step 6: Verificação headless do filtro (Review Focus 1 e 4)**

  Copiar `index.html` para o diretório de rascunho da sessão, injetar antes de `</body>` um `<script>` que, no `load`, aplica cada filtro com `switchTab('trilhas')` + `setSubFilter(v, botão)` e grava em `<pre id="resultado">` um JSON com as contagens visíveis (`el.checkVisibility()`) de `.study-card`, `.need-card`, `.vaga-competencia`, chips `#secao-rota-vaga .vaga-chips [data-slug]` e `.cert-row`. Rodar `google-chrome --headless=new --no-sandbox --disable-gpu --virtual-time-budget=3000 --dump-dom file://<cópia>` e ler o `<pre>`.
  Expected:

  | Filtro | cards | necessidades | competências | chips da rota | linhas de certificação |
  |---|---|---|---|---|---|
  | Trilha 8 | 4 | 4 | 2 | 3 | 1 |
  | Trilha 9 | 4 | 4 | 1 | 2 | 4 |
  | Trilha 10 | 4 | 4 | 1 | 2 | 3 |
  | Trilha 1 | 5 | igual ao `main` atual | — | — | — |

  Nenhum card de 42–45 visível com a Trilha 1.

- [ ] **Step 7: Verificação visual (Review Focus 5)**

  `google-chrome --headless=new ... --window-size=1280,1800 --screenshot=...` com a Trilha 10 selecionada, nos temas claro e escuro (`data-theme`), e uma captura a 390 px de largura. Conferir: bloco "10" sem corte, selos e blocos das Trilhas 8–10 com as cores da spec, sem rolagem horizontal da página.

- [ ] **Step 8: Commit**

  ```bash
  git add _geradores/CURRICULO.md README.md docs/superpowers/specs/ index.html */treinamento-*.html _geradores/testes/test_trilhas_empregabilidade.py
  git commit -m "docs(curriculo): Trilhas 8–10, distribuição NIST e rotas por perfil; recompila portal e módulos

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```
