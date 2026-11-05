# Aprimoramentos de GRC (Exceções, Assurance, CIS Controls, CGEIT): Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fechar cinco lacunas de GRC no Mapa da Cibersegurança, todas como seções/edições de módulos existentes (25, 26, 33, 58), mantendo o catálogo em 62 módulos.

**Architecture:** Portal estático e offline. Corpos `_geradores/<slug>_body.html` compilados por `montar.py`/`gerar.sh` para `<Pasta>/treinamento-*.html`; metadados e certificações em `_geradores/index_dados.py`; a matriz de certificações vive em `CERTIFICACOES` (listas planas) e no JSON `#cert-dados` do corpo do módulo 33 (domínios), que devem ficar em sincronia. Testes `unittest` espelham e travam estrutura.

**Tech Stack:** Python 3 (`unittest`), HTML/CSS/JS puro, `_geradores/gerar.sh`.

**Spec:** `docs/superpowers/specs/2026-11-05-grc-assurance-excecoes-design.md`

## Global Constraints

- Branch `feat/grc-aprimoramentos` (ou worktree); nada na `main`.
- Textos em pt-BR, contrato do corpo `_geradores/GUIA-DO-AUTOR.md` §2 (um `article`; seções `class`/`id`/`data-tipo`; `h2` no início; callout sempre com modificador `tip|warning|danger|law|key`; tabelas `class="data-table"`). Seções novas são `data-tipo="teoria"`.
- Os `<h2>` dos módulos 25/26/58 **não** são numerados no texto — **não** renumerar títulos (o chassi gera "Seção 0X de 0Y").
- Catálogo permanece em **62 módulos**; nenhum módulo muda número/trilha.
- CGEIT entra **sem pesos** (como CEH/GSEC): domínios reais da ISACA com `peso: None`, módulos mapeados, `nota` onde um domínio não tiver módulo; `requisitos: {"conferir": true}`. **Não** adicionar CGEIT a `com_pesos`/`esperados`/fontes-com-peso.
- Nenhuma ferramenta de GRC recomendada; ServiceNow GRC/Archer/MetricStream só como exemplos de categoria.
- Dados oficiais (domínios/experiência CGEIT, cláusulas ISO/NIST) confirmados na fonte, ou texto "confira na página oficial".
- Nunca escrever "Estudos de Cibersegurança"/"Estudos em Cibersegurança"/"José Mauro"/"Brandão"/"Stelling" (`test_marca`).
- Testes: de `_geradores/`, `python3 -m unittest testes.<arquivo>`. Suíte completa só uma vez, no fim, após `free -h` (≥~4 GB), em `systemd-run --user --scope --quiet -p MemoryMax=4G -p MemorySwapMax=1G python3 -m unittest discover -s testes`. Truncar saída com `cut -c1-1500`.
- Commits terminam com `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.

## Review Focus

1. **Sincronia `CERTIFICACOES` ↔ `#cert-dados` com a CGEIT:** cada módulo da CGEIT em `CERTIFICACOES` precisa estar em algum domínio da CGEIT no `#cert-dados` (`test_coerencia_com_a_matriz_do_portal`). Coberto na Task 1.
2. **Contagens travadas em "17" e na lista ordenada de siglas:** `test_rota_vaga.py:54` (lista), `test_certificacoes_carreira.py:515` (`len==17`), README (2×). Task 1 atualiza todas.
3. **Adjacência e contagem de seções no 25 e no 58:** `test_gestao_riscos_ti` (iso-27005→lab, "Seção 7 de 7") e `test_auditoria_de_ti` (9 ids, "Seção N de 9") quebram ao inserir seções. Tasks 3 e 4 atualizam.
4. **Item 4 não duplicar o que já existe no 26:** os 18 Controls, IG1-3 e o crosswalk (15 entradas, travado) já estão lá; a Task 2 só acrescenta a distinção Controls×Benchmarks + 1 questão, sem tocar no crosswalk.
5. **Exceção sem dono / vencida e acúmulo sistêmico:** a seção do item 1 deve deixar claro que exceção vencida é risco aceito sem dono e que acúmulo vira risco sistêmico (liga ao item 5) — senão o conteúdo não cumpre o anti-objetivo. Task 3.

---

### Task 1: CGEIT na matriz (item 3) — módulo 33

**Files:**
- Modify: `_geradores/index_dados.py` (`CERTIFICACOES`: entrada CGEIT após CDPSE)
- Modify: `_geradores/certificacoes_e_carreira_body.html` (JSON `#cert-dados`: entrada CGEIT + bloco de lookup, texto do planejador/legenda que lista certs "conferir")
- Modify: `README.md` (2× "17 certificações" → 18 e incluir CGEIT nas listas enumeradas: linhas ~41 e ~206), `_geradores/CURRICULO.md` (lista de certs "conferir", se o teste exigir), subtítulo do módulo 33 se citar 17
- Modify tests: `_geradores/testes/test_rota_vaga.py` (lista ordenada de siglas + dict `DOMINIO_OFICIAL`), `_geradores/testes/test_certificacoes_carreira.py` (`len==17`→18; `test_requisitos_de_experiencia` com CGEIT em `{"conferir": True}`; `test_textos_listam_todas_as_certificacoes_conferir`)
- Recompilado: `Certificacoes-e-Carreira/treinamento-certificacoes-e-carreira.html`, `index.html`

**Interfaces:**
- Produces: `CERTIFICACOES[-1]` com `sigla: "CGEIT"`, `modulos: ["Lideranca-e-Programa-de-Seguranca", "Estruturacao-da-Area-de-Seguranca", "Auditoria-de-TI", "Gestao-de-Riscos-TI", "ISO-27001-e-27002"]`; entrada CGEIT no `#cert-dados` com domínios `peso: None`.

- [ ] **Step 1: Testes (RED).** Em `test_rota_vaga.py`, acrescentar `"CGEIT"` ao fim da lista de siglas (linha ~54) e a entrada CGEIT no `DOMINIO_OFICIAL` (→ `https://www.isaca.org/credentialing/cgeit`). Em `test_certificacoes_carreira.py`: `len(CERTIFICACOES)` 17→18 (linha ~515); em `test_requisitos_de_experiencia`, CGEIT no grupo `{"conferir": True}`. Rodar `python3 -m unittest testes.test_rota_vaga testes.test_certificacoes_carreira` → FAIL.
- [ ] **Step 2: `CERTIFICACOES`.** Entrada CGEIT modelada na de **CISA** (ISACA, conferir): `site_oficial` `https://www.isaca.org/credentialing/cgeit`, `nome` "Certified in the Governance of Enterprise IT", `orgao` "ISACA", `foco` "Governança de TI corporativa", `experiencia` confirmada na ISACA ou "confira na certificadora", `modulos` como em Interfaces.
- [ ] **Step 3: `#cert-dados`.** Entrada CGEIT no mesmo formato de CISA: `fontes` (página oficial + exam content da ISACA), `nome`, `orgao`, `foco`, `experiencia`, `manutencao`, `nota_dominios`, `dominios` (os domínios oficiais da CGEIT, `peso: None`, cada um com `modulos` dos 5 do currículo onde couber e `nota` + `parcial` onde não houver módulo), `requisitos: {"conferir": true}`. Acrescentar a CGEIT ao bloco de lookup `slug→…`/legenda e à lista de certificações "conferir" no texto do corpo/CURRICULO que o `test_textos_listam_todas_as_certificacoes_conferir` cobra. Garantir coerência: cada módulo de `CERTIFICACOES["CGEIT"]` aparece em algum domínio.
- [ ] **Step 4: Textos de contagem.** README linhas ~41 e ~206: "17 certificações" → "18" e incluir "CGEIT" nas enumerações; subtítulo do 33 se citar 17.
- [ ] **Step 5: Compilar** `./_geradores/gerar.sh Certificacoes-e-Carreira`.
- [ ] **Step 6: Rodar** `python3 -m unittest testes.test_rota_vaga testes.test_certificacoes_carreira testes.test_curriculo testes.test_marca` → PASS.
- [ ] **Step 7: Commit** `feat(grc): CGEIT entra na matriz de certificações (17 → 18)`.

---

### Task 2: CIS Controls vs Benchmarks (item 4) — módulo 26

**Files:**
- Modify: `_geradores/iso_27001_e_27002_body.html` (acréscimo na seção `sgsi`: um callout ou parágrafo distinguindo Controls×Benchmarks; +1 `quiz-item` na seção de questões; referência CIS Controls v8.1 nas referências)
- Modify (se preciso): `_geradores/testes/test_iso_27001_27002.py` (asserção de termo novo, sem tocar no `test_crosswalk_tem_15_entradas_completas`)
- Recompilado: `ISO-27001-e-27002/treinamento-iso-27001-e-27002.html`, `index.html`

**Interfaces:**
- Consumes: nada das outras tasks.

- [ ] **Step 1: Teste (RED).** Em `test_iso_27001_27002.py`, acrescentar asserção de que a seção `sgsi` contém a distinção (ex.: termos `CIS Benchmarks` e `CIS Controls` na mesma seção, e `Estudo 06`). Rodar → FAIL.
- [ ] **Step 2: Conteúdo mínimo.** Na seção `sgsi`, acrescentar um callout (ou parágrafo) curto: **CIS Controls** = os 18 (já listados ali) "o que fazer"; **CIS Benchmarks** = endurecimento por dispositivo, "como configurar" (módulo 06). **Não** re-listar os 18 nem alterar o crosswalk. +1 `quiz-item` sobre a distinção na seção de questões; referência a CIS Controls v8.1 nas referências.
- [ ] **Step 3: Compilar** `./_geradores/gerar.sh ISO-27001-e-27002`.
- [ ] **Step 4: Rodar** `python3 -m unittest testes.test_iso_27001_27002 testes.test_marca testes.test_corpos_migrados` → PASS (incl. crosswalk intacto).
- [ ] **Step 5: Commit** `feat(grc): distinção CIS Controls × Benchmarks no Estudo 26`.

---

### Task 3: Gestão de exceções de segurança (item 1) — módulo 25

**Files:**
- Modify: `_geradores/gestao_de_riscos_ti_body.html` (seção nova `id="excecoes" data-tipo="teoria"` **entre** `iso-27005` e `simulador`; +1–2 `quiz-item`; referência)
- Modify: `_geradores/testes/test_gestao_riscos_ti.py` (`test_secao_iso_27005_antes_do_laboratorio`: agora `iso-27005` → `excecoes` → `simulador`; "Seção 7 de 7" → "Seção 8 de 8")
- Recompilado: `Gestao-de-Riscos-TI/treinamento-gestao-de-riscos-ti.html`, `index.html`

**Interfaces:**
- Produces: nova ordem de seções do 25: `introducao, processo, iso-27005, excecoes, simulador, checklist, quiz, fatos` (8).

- [ ] **Step 1: Teste (RED/ajuste).** Em `test_gestao_riscos_ti.py`, trocar a asserção de adjacência para: a `iso-27005` é seguida por `id="excecoes" data-tipo="teoria"`, e a `excecoes` é seguida por `id="simulador" data-tipo="laboratorio"`; "Seção 7 de 7" → "Seção 8 de 8". Acrescentar asserção de termos-chave na `excecoes`: `exceção`, `aceitação`, `alçada`, `controle compensatório`, `prazo`, `reavaliação`, `vencida`, `sistêmico`, `Estudo 58`. Rodar → FAIL.
- [ ] **Step 2: Seção.** Escrever `excecoes` com o conteúdo da spec §3.1: exceção como aceitação formal e temporária de risco; ciclo (solicitação → análise → aprovação por alçada → controle compensatório → prazo/remediação → reavaliação/expiração); como a função de GRC desafia uma exceção; tabela de estados (solicitada, aprovada, vigente, vencida, encerrada) e papéis; callout `warning` (exceção vencida = risco aceito sem dono; acúmulo = risco sistêmico, liga ao 58). Remissões 26 e 58. +1–2 `quiz-item` + referência (ISO/IEC 27001 tratamento de risco; NIST SP 800-37 risk acceptance).
- [ ] **Step 3: Compilar** `./_geradores/gerar.sh Gestao-de-Riscos-TI`.
- [ ] **Step 4: Rodar** `python3 -m unittest testes.test_gestao_riscos_ti testes.test_marca testes.test_corpos_migrados` → PASS.
- [ ] **Step 5: Commit** `feat(grc): seção de gestão de exceções de segurança no Estudo 25`.

---

### Task 4: Security Assurance (item 2) e correlação sistêmica/automação de GRC (item 5) — módulo 58

**Files:**
- Modify: `_geradores/auditoria_de_ti_body.html` (duas seções novas `id="assurance"` e `id="correlacao-grc"` (`data-tipo="teoria"`) **após** `ciclo-do-teste` e **antes** de `simulador`; +quiz; referências)
- Modify: `_geradores/testes/test_auditoria_de_ti.py` (`SECOES` → 11 ids; "Seção N de 9" → "de 11")
- Recompilado: `Auditoria-de-TI/treinamento-auditoria-de-ti.html`, `index.html`

**Interfaces:**
- Consumes: liga à seção de exceções da Task 3 (remissão) e à CGEIT da Task 1 não é necessária.
- Produces: `SECOES = ["introducao", "sox-404", "itgc", "cobit", "ciclo-do-teste", "assurance", "correlacao-grc", "simulador", "checklist", "quiz", "fatos"]` (11).

- [ ] **Step 1: Teste (RED).** Em `test_auditoria_de_ti.py`, atualizar `SECOES` para os 11 ids acima (inserindo `assurance` e `correlacao-grc` após `ciclo-do-teste`); as asserções de "Seção N de len(SECOES)" passam a usar 11 automaticamente. Acrescentar termos-chave: em `assurance` — `desenho`, `efetividade operacional`, `reexecução`, `indagação`, `racionalização`, `modelo de assurance`, `Três Linhas`, `Estudo 59`; em `correlacao-grc` — `causa sistêmica`, `plataforma de GRC`, `sinais`, `Estudo 25`, `Estudo 09`. Rodar → FAIL.
- [ ] **Step 2: Seção `assurance`.** Conteúdo da spec §3.2: desenho × efetividade operacional; tipos de teste (indagação < observação < inspeção < reexecução) remetendo ao `ciclo-do-teste` existente sem repeti-lo; o modelo de assurance (escopo, critérios, ritos, indicadores, evidências, governança de planos); racionalização de controles (mapear controle→risco); onde encaixa nas Três Linhas (remete ao 59). Tabelas: desenho vs efetividade; tipos de teste e força da evidência. +1 `quiz-item` + referências (IIA/COSO, ISACA ITAF).
- [ ] **Step 3: Seção `correlacao-grc`.** Conteúdo da spec §3.3: causas sistêmicas (exemplo do controle de acesso falho em 3 auditorias/2 incidentes/5 exceções = problema de IAM); o que uma plataforma de GRC automatiza, por conceito (sem recomendar fornecedor; ServiceNow/Archer/MetricStream só como exemplos); callout `tip`. Remissões 25, 09, 46/47, 18. +1 `quiz-item` + referência.
- [ ] **Step 4: Compilar** `./_geradores/gerar.sh Auditoria-de-TI`.
- [ ] **Step 5: Rodar** `python3 -m unittest testes.test_auditoria_de_ti testes.test_marca testes.test_corpos_migrados` → PASS.
- [ ] **Step 6: Commit** `feat(grc): seções de Security Assurance e de correlação sistêmica no Estudo 58`.

---

### Task 5: Compilação total, suíte completa e varredura

**Files:** nenhum fonte novo; recompila e valida.

- [ ] **Step 1: Recompilar tudo:** `./_geradores/gerar.sh todos` → sem erro.
- [ ] **Step 2: Suíte completa.** `free -h` (≥~4 GB; senão rodar afetados e registrar). `systemd-run --user --scope --quiet -p MemoryMax=4G -p MemorySwapMax=1G python3 -m unittest discover -s testes` (de `_geradores/`) → `OK`.
- [ ] **Step 3: Varredura de nome:** `git grep -n -e "José Mauro" -e "Brandão" -e "Stelling" -e "Estudos de Cibersegurança" -e "Estudos em Cibersegurança" -- ':(exclude)docs/superpowers' ':(exclude).agents' ':(exclude)_geradores/testes/test_marca.py'` → vazio.
- [ ] **Step 4: Commit** (se a recompilação gerou mudança) `build(grc): recompila portal e módulos com os aprimoramentos de GRC`.
