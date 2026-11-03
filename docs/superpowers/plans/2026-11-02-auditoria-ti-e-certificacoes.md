# Auditoria de TI, Normas ISO Complementares e 12 Certificações: Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar o módulo 58 "Auditoria de TI: SOX, ITGC e COBIT", acrescentar 6 seções normativas e de carreira a módulos existentes e ampliar a matriz de certificações de 6 para 12.

**Architecture:** Portal estático e offline. Cada módulo é um corpo `_geradores/<slug_snake>_body.html` compilado por `montar.py` para `<Pasta>/treinamento-<slug-kebab>.html`; os metadados e as visões do portal vêm de `_geradores/index_dados.py` e de `_geradores/estudos.txt`, renderizados por `build_index.py`. Os simuladores são JavaScript puro com os dados num bloco `<script type="application/json">`, e os testes `unittest` espelham as regras em Python.

**Tech Stack:** Python 3 (`unittest`), HTML/CSS/JS puro, Mermaid pré-compilado, `_geradores/gerar.sh`.

**Spec:** `docs/superpowers/specs/2026-11-02-auditoria-ti-e-certificacoes-design.md`

## Global Constraints

- Textos em pt-BR, no tom e no contrato do `_geradores/GUIA-DO-AUTOR.md` (§2.2: um `article`, seções `class`/`id`/`data-tipo` nessa ordem, `h2` no início, callout sempre com modificador).
- Checklist de cada módulo: 4 a 8 itens. Os módulos 21, 24, 25, 27, 28 e 33 têm 7 hoje e ficam com **8**.
- Seção nova de teoria em módulo existente entra **imediatamente antes** de `<section ... id="simulador" data-tipo="laboratorio">`.
- Módulo 58 no **fim** de `estudos.txt`; os módulos 01–57 não mudam de número nem de trilha.
- **Nenhum** nome, empresa, URL ou dado pessoal dos perfis do LinkedIn no repositório. Trajetórias descritas como exemplos, nunca como estatística.
- Requisitos de experiência e pesos de prova só vêm da página oficial da certificadora; sem peso publicado → `"peso": null` e `nota_dominios` explicando.
- Edições de normas conferidas na página da ISO antes de escritas (27701, 27017, 27018, 22301, 42001, 27005).
- Testes: rodar a partir de `_geradores/` com `python3 -m unittest testes.<arquivo>`. Antes da suíte completa, conferir `free -h`; com menos de ~4 GB livres, só os arquivos afetados. Suíte completa sempre em `systemd-run --user --scope --quiet -p MemoryMax=4G -p MemorySwapMax=1G python3 -m unittest discover -s testes`. Nunca duas suítes em paralelo.
- Commits terminam com `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Review Focus

1. **Portal com o módulo 58 catalogado mas não compilado:** o portal mostra "57 / 58" e `test_gestao_riscos_terceiros::test_integracao_com_portal_index` falha. Por isso a Task 1 só termina com o corpo compilado (teste: `test_portal_mostra_58_compilados` na Task 1).
2. **Ordem das certificações divergente entre portal e planejador:** `test_coerencia_com_a_matriz_do_portal` exige a mesma ordem de siglas; as 6 novas entram no fim das duas listas na mesma ordem (Task 3).
3. **Certificação "conferir" tratada como elegível pelo planejador:** um estudante sem experiência não pode ver "Elegível" para CISA (teste `test_status_conferir` na Task 3).
4. **Seção nova quebrando a numeração "Seção n de N" ou o sumário:** cada task de seção verifica no compilado que a seção aparece antes do laboratório (teste `test_secao_<tema>_antes_do_laboratorio`).
5. **Dados pessoais vazando na seção de trajetórias:** teste `test_trajetorias_sem_dados_pessoais` (Task 4) e a varredura da Task 10 com a lista de termos fora do repositório.

---

### Task 1: Módulo 58 Auditoria de TI (catálogo, corpo, simulador, teste)

**Files:**
- Create: `_geradores/auditoria_de_ti_body.html`
- Create: `_geradores/testes/test_auditoria_de_ti.py`
- Create (compilado): `Auditoria-de-TI/treinamento-auditoria-de-ti.html`
- Modify: `_geradores/estudos.txt` (linha nova no fim)
- Modify: `_geradores/index_dados.py` (`ESTUDOS_DADOS`, `NECESSIDADES`)
- Modify: `_geradores/testes/test_curriculo.py:29` (57 → 58)

**Interfaces:**
- Produces: slug `Auditoria-de-TI` em `ESTUDOS_DADOS` e no `estudos.txt` (número 58); JSON do simulador em `<script type="application/json" id="aud-dados">`; funções JS `amostraMinima(frequencia)`, `classificarControle(controle, excecoes, compensatorio)`.

- [ ] **Step 1: Linha do catálogo e metadados.** Acrescentar ao fim de `estudos.txt`:
  `Auditoria-de-TI|Auditoria de TI: SOX, ITGC e COBIT|Auditoria-de-TI|treinamento-auditoria-de-ti.html|6|#D97706|Govern`
  Em `ESTUDOS_DADOS`, entrada `"Auditoria-de-TI"` com os valores da spec §3.1: `titulo`, `subtitulo` "Controles gerais de TI, teste de desenho e de efetividade, amostragem e deficiências", `trilha` 6, `nist` "Govern", `mitre` "T1078 Valid Accounts / T1098 Account Manipulation", `carreiras` `["GRC & Auditoria", ROTULO_ANALISTA_SI]`, `tempo_minutos` 45, `nivel` "intermediario", `pergunta_chave` "O controle está no papel. Como você prova que ele funcionou o ano inteiro?", `simulador_nome` "Testador de ITGC", `fatos` com 4 itens (SOX 404 e ICFR; 4 domínios de ITGC; TOD vs TOE e amostragem por frequência; deficiência, deficiência significativa e fraqueza material). Em `NECESSIDADES`, ao fim: `{"desafio": "Preciso preparar a TI para uma auditoria SOX ou de ITGC", "slug": "Auditoria-de-TI", "categoria": "Governança", "icone": "🧾"}` (usar a mesma `categoria` dos itens de GRC já existentes, se diferente de "Governança").

- [ ] **Step 2: Teste do tamanho da grade.** Em `test_curriculo.py::test_tamanho_da_grade`, trocar 57 por 58. Rodar `python3 -m unittest testes.test_curriculo` → PASS.

- [ ] **Step 3: Escrever `test_auditoria_de_ti.py` (falhando),** no padrão de `test_gestao_riscos_terceiros.py`. `SLUG = "Auditoria-de-TI"`. Testes:
  - `test_body_and_compiled_files_exist`.
  - `test_secoes`: ids na ordem `["introducao", "sox-404", "itgc", "cobit", "ciclo-do-teste", "simulador", "checklist", "quiz", "fatos"]`; compilado contém `Seção 1 de 9` … `Seção 9 de 9`; `data-slug="auditoria-de-ti"`.
  - `test_coerencia_com_o_catalogo`: `simulador_nome`, `pergunta_chave` e cada `fato` no compilado; `subtitulo` no `index.html`.
  - `test_termos_chave`: `SOX`, `404`, `ICFR`, `COSO`, `PCAOB AS 2201`, `ITGC`, `ITAC`, `IPE`, `SOC 1`, `SOC 2`, `COBIT 2019`, `EDM`, `APO`, `BAI`, `DSS`, `MEA`, `TOD`, `TOE`, `walkthrough`, `fraqueza material`, `deficiência significativa`, `controle compensatório` no corpo.
  - `test_pontes`: antes de `id="simulador"`, `Estudo 26`, `Estudo 04`, `Estudo 40`, `Estudo 22`, `Estudo 52`, `Estudo 30`, `Estudo 57`; em `id="fatos"`, `Estudo 25`, `Estudo 26`, `Estudo 57`, `58 módulos`.
  - `test_nao_repete_auditoria_do_sgsi`: o corpo não contém `Fase 2` (etapa da certificação ISO, ensinada no 26) e cita o `Estudo 26` ao falar de auditoria do SGSI.
  - `test_referencias`: em `id="fatos"`: `Sarbanes-Oxley`, `AS 2201`, `COSO`, `COBIT 2019`, `ITAF`, `Global Internal Audit Standards`, `SOC 1`.
  - `test_dados_do_simulador`: JSON `#aud-dados` com `controles` (4 a 6), cada um com `id`, `dominio` ∈ {`acesso`, `mudanca`, `desenvolvimento`, `operacoes`} (todos os 4 presentes), `frequencia` ∈ {`anual`, `trimestral`, `mensal`, `semanal`, `diaria`, `multipla`}, `populacao` (int > 0), `itens` (lista com `id`, `evidencia`, `excecao` bool), `compensatorio` (str ou null) e `gabarito` ∈ {`efetivo`, `deficiencia`, `significativa`, `material`}; `tabela_amostragem` com as 6 frequências e a fonte em `fonte_amostragem`.
  - `test_regras_espelhadas`: funções Python `amostra_minima(tabela, frequencia, populacao)` (mínimo da tabela, limitado à população) e `classificar(controle)` reproduzem o `gabarito` de cada controle; ao menos 3 classificações diferentes no cenário; ao menos 1 controle com `compensatorio` que rebaixa a classificação.
  - `test_simulador_sem_apis_inseguras`: sem `innerHTML =` com dado do JSON, sem `eval`, sem `fetch` (copiar o critério de `test_gestao_riscos_terceiros.py:482`).
  - `test_componentes_pedagogicos`: `checklist-item` entre 4 e 8; `quiz-item` ≥ 6; ao menos 1 `pre class="mermaid"`.
  - `test_portal_mostra_58_compilados`: `index.html` contém `58 / 58`.
  Rodar `python3 -m unittest testes.test_auditoria_de_ti` → FAIL (arquivos ausentes).

- [ ] **Step 4: Escrever `auditoria_de_ti_body.html`** com as seções da spec §3.2, na ordem dos ids do teste, e o simulador da §3.3. Os números da `tabela_amostragem` (por frequência) com a fonte citada no texto e em `fonte_amostragem`. Cenário fixo: empresa fictícia, 3 sistemas, 4 a 6 controles cobrindo os 4 domínios, armadilhas didáticas (aprovação depois da implantação, aprovador = executor, desligado com acesso ativo além do prazo). Motor JS lê `#aud-dados`, monta a interface com `textContent`/`createElement`.

- [ ] **Step 5: Compilar.** `./gerar.sh Auditoria-de-TI` (de `_geradores/`) → sem erro do validador; cria `Auditoria-de-TI/treinamento-auditoria-de-ti.html` e regenera `index.html`.

- [ ] **Step 6: Rodar** `python3 -m unittest testes.test_auditoria_de_ti testes.test_curriculo testes.test_contrato testes.test_filtro_secoes testes.test_index` → PASS.

- [ ] **Step 7: Commit** `feat(auditoria-ti): módulo 58 Auditoria de TI com Testador de ITGC`.

---

### Task 2: Ligações do módulo 58 no portal e na documentação

**Files:**
- Modify: `_geradores/index_dados.py` (`ROTAS_PERFIL` `grc`, `ROTA_VAGA` `controles`, `CERTIFICACOES` CISM e CISSP)
- Modify: `_geradores/gestao_de_riscos_de_terceiros_body.html`, `gestao_de_riscos_ti_body.html`, `iso_27001_e_27002_body.html` (seção `fatos`)
- Modify: `README.md`, `_geradores/CURRICULO.md`, `_geradores/GUIA-DO-AUTOR.md` (só se citar o total)
- Modify tests: `test_trilhas_empregabilidade.py:144`, `test_trilhas_especializacao.py:141`, `test_gestao_riscos_terceiros.py:252`, `test_corpos_migrados.py:1`

**Interfaces:**
- Consumes: slug `Auditoria-de-TI` (Task 1).

- [ ] **Step 1: Atualizar os testes (falhando).**
  - `test_trilhas_empregabilidade.py`: rota GRC passa a `"01 -> 08 -> 40 -> 09 -> 25 -> 26 -> 58 -> 57 -> 27 -> 56 -> 54 -> 55 -> 28 -> 43 -> 44"`.
  - `test_trilhas_especializacao.py::test_apoios_novos`: `"controles"` termina com `"Auditoria-de-TI"`.
  - `test_gestao_riscos_terceiros.py:252`: `"57 módulos"` → `"58 módulos"`.
  - Novo `test_pontes_para_o_58` em `test_auditoria_de_ti.py`: a seção `fatos` dos corpos 25, 26 e 57 contém `Estudo 58`; `Auditoria-de-TI` está em `CERTIFICACOES` de CISM e de CISSP; `README.md` contém `58 módulos` e não contém `57 módulos`; `CURRICULO.md` contém `#### 58. Auditoria-de-TI` e `25 ao 28, 31, 58`.
  Rodar os 4 arquivos → FAIL.

- [ ] **Step 2: Dados.** `ROTAS_PERFIL` `grc`: inserir `"Auditoria-de-TI"` logo depois de `"ISO-27001-e-27002"`. `ROTA_VAGA` `controles`: `"Auditoria-de-TI"` no fim de `apoio`. `CERTIFICACOES`: `"Auditoria-de-TI"` no fim de `modulos` de CISM e de CISSP.

- [ ] **Step 3: Corpos.** Em `fatos` dos módulos 25, 26 e 57, um item de "Próximos passos" apontando o `Estudo 58` (auditoria baseada em risco; auditoria de TI além do SGSI; SOC 1 vs SOC 2). No módulo 57, `57 módulos` → `58 módulos`.

- [ ] **Step 4: Documentação.** `README.md`: os 5 lugares com 57 (§5.3 da spec), diagrama da Trilha 6 "Módulos 25 a 28, 31, 58", linha `| **58** | \`Auditoria-de-TI\` | … | Trilha 6 … | Govern | Testador de ITGC |`. `CURRICULO.md`: linha da Trilha 6 "25 ao 28, 31, 58", bloco `#### 58. Auditoria-de-TI` no formato do bloco 57, a rota GRC com o 58 na §5 (mesma string do Step 1). `GUIA-DO-AUTOR.md` só se citar 57.

- [ ] **Step 5: Compilar** `./gerar.sh todos` → sem erro.

- [ ] **Step 6: Rodar** `python3 -m unittest testes.test_auditoria_de_ti testes.test_trilhas_empregabilidade testes.test_trilhas_especializacao testes.test_gestao_riscos_terceiros testes.test_rota_vaga testes.test_rotas_sugeridas testes.test_curriculo testes.test_corpos_migrados` → PASS.

- [ ] **Step 7: Commit** `feat(portal): liga o módulo 58 às rotas, à vaga, às certificações e à documentação`.

---

### Task 3: Matriz de certificações e planejador: 6 → 12

**Files:**
- Modify: `_geradores/index_dados.py` (`CERTIFICACOES`)
- Modify: `_geradores/certificacoes_e_carreira_body.html` (JSON `#cert-dados`, rótulos de status e `function elegibilidade`)
- Modify tests: `test_rota_vaga.py:52-55` e `:139`, `test_trilhas_empregabilidade.py:116-127`, `test_certificacoes_carreira.py` (`elegibilidade`, `test_dominios_e_pesos`, `test_requisitos_de_experiencia`, `test_regra_de_elegibilidade`)

**Interfaces:**
- Consumes: slug `Auditoria-de-TI` (Task 1).
- Produces: siglas `ISFS`, `PDPF/PDPP`, `ITIL 4 F`, `CSFPC`, `CISA`, `ISO 27001 LA`, nesta ordem, no fim de `CERTIFICACOES` e de `cert-dados.certificacoes`; status de elegibilidade `"conferir"`, ativado por `"requisitos": {"conferir": true}`.

- [ ] **Step 1: Testes (falhando).**
  - `test_certificacoes_exatas`: as 12 siglas.
  - `test_certificacoes_render`: `html.count('<tr class="cert-row"') == 12`.
  - `test_certificacoes_novas`: acrescentar as 6 siglas novas ao dicionário `esperado`, com `[]` (nenhuma lista módulos de `NOVOS`) salvo se a proposta final listar algum módulo de `NOVOS`; nesse caso, a lista exata.
  - `test_certificacoes_carreira.py`:
    - `elegibilidade`: primeira regra `if req.get("conferir"): return "conferir"`.
    - `test_dominios_e_pesos`: siglas com pesos que somam 100 passam a incluir `CISA`; `ISFS`, `PDPF/PDPP`, `ITIL 4 F`, `CSFPC` e `ISO 27001 LA` entram na regra "pesos todos `None` ou soma 100" conforme a página oficial (o implementador fixa a regra exata por sigla depois de conferir).
    - `test_requisitos_de_experiencia`: `ISFS`, `ITIL 4 F`, `CSFPC` com `{}`; `CISA`, `ISO 27001 LA`, `PDPF/PDPP` com `{"conferir": True}` e `experiencia` não vazia.
    - Novo `test_status_conferir`: com perfil de 20 anos em tudo e graduação, `elegibilidade` de CISA, ISO 27001 LA e PDPF/PDPP é `"conferir"`; o corpo contém o rótulo do status `"conferir"` no mapa de rótulos JS (texto: "Requisito em texto: confira na certificadora") e a função JS `elegibilidade` retorna `status: "conferir"` quando `req.conferir`.
    - `test_dominios_e_pesos`: todos os `nivel` em (1, 2, 3); as 4 de entrada com `nivel` 1.
  Rodar `python3 -m unittest testes.test_rota_vaga testes.test_trilhas_empregabilidade testes.test_certificacoes_carreira` → FAIL.

- [ ] **Step 2: `CERTIFICACOES`.** As 6 entradas da spec §6, com `sigla`, `nome`, `orgao` ("EXIN", "EXIN", "PeopleCert (Axelos)", "CertiProf", "ISACA", "PECB"), `foco`, `experiencia` (texto conferido na fonte oficial) e `modulos` (proposta da §6, mínimo 3).

- [ ] **Step 3: Planejador.** Em `#cert-dados.certificacoes`, 6 objetos na mesma ordem, com `nome` e `orgao` idênticos ao portal, `nivel`, `foco`, `experiencia`, `manutencao`, `nota_dominios`, `requisitos`, `sem_experiencia` (obrigatório quando `requisitos` não é vazio; para `conferir`, orientar a conferir no site do emissor) e `dominios` cujos `modulos` cobrem todos os `modulos` do portal. Acrescentar `Auditoria-de-TI` e quaisquer módulos novos ao dicionário `modulos` do JSON (com `numero` e `titulo` do catálogo). Em JS: rótulo `"conferir": ["Requisito em texto: confira na certificadora", <cor no padrão dos outros>]` e, em `elegibilidade(c)`, `if (req.conferir) return { status: "conferir", faltas: [] };` antes da regra de "sem-exigencia".

- [ ] **Step 4: Compilar** `./gerar.sh Certificacoes-e-Carreira` → sem erro.

- [ ] **Step 5: Rodar** `python3 -m unittest testes.test_rota_vaga testes.test_trilhas_empregabilidade testes.test_certificacoes_carreira testes.test_abas_certificacao_progresso testes.test_filtro_secoes` → PASS.

- [ ] **Step 6: Commit** `feat(certificacoes): matriz e planejador com 12 certificações, status "conferir"`.

---

### Task 4: Carreira: trajetórias reais e certificações de entrada

**Files:**
- Modify: `_geradores/certificacoes_e_carreira_body.html`
- Modify: `_geradores/testes/test_certificacoes_carreira.py`

- [ ] **Step 1: Testes (falhando).**
  - `test_secao_trajetorias_antes_do_laboratorio`: existe `<section class="study-section" id="trajetorias" data-tipo="teoria">` imediatamente antes de `id="simulador"`; o compilado tem `Seção 7 de 7`.
  - `test_trajetorias_conteudo`: a seção contém `suporte`, `CISO`, `MBA`, `Foundation`, `EXIN`, `CertiProf`, `CQI/IRCA`, a palavra `exemplo` e um quadro "por onde começar" com as linhas `GRC`, `Privacidade`, `Auditoria`, `Técnico`.
  - `test_trajetorias_sem_dados_pessoais`: o corpo não contém `linkedin.com/in/` nem `lattes.cnpq.br`, e a seção `trajetorias` não contém `%` (nada de estatística). Os nomes de pessoas, empresas e instituições dos perfis **não** entram no teste, para não ficarem no repositório: a checagem deles é a da Task 10, Step 4.
  - `test_tabela_certificacoes_da_secao`: a tabela da seção `id="certificacoes"` lista as 12 siglas.
  - `test_componentes_pedagogicos`: checklist `== 8`; quiz `>= 7`.
  Rodar `python3 -m unittest testes.test_certificacoes_carreira` → FAIL.

- [ ] **Step 2: Escrever** a seção `trajetorias` (spec §4.1), acrescentar as 6 linhas à tabela de `id="certificacoes"`, 1 item de checklist (por exemplo, escolher a primeira certificação pelo perfil-alvo) e 1 questão de fixação.

- [ ] **Step 3: Compilar e rodar** `./gerar.sh Certificacoes-e-Carreira && python3 -m unittest testes.test_certificacoes_carreira` → PASS.

- [ ] **Step 4: Commit** `feat(carreira): trajetórias reais e certificações de entrada`.

---

### Tasks 5–9: Seções normativas em módulos existentes

Mesmo ciclo nas 5 tasks: teste falhando → seção → compilar → teste passando → commit. Em cada uma, no arquivo de teste do módulo:
- `test_secao_<id>_antes_do_laboratorio`: a seção `<section class="study-section" id="<id>" data-tipo="teoria">` existe e vem imediatamente antes de `id="simulador"`; o compilado tem `Seção N de N` com o novo total.
- `test_secao_<id>_conteudo`: os termos da tabela abaixo dentro da seção.
- `test_secao_<id>_referencia`: a referência oficial dentro de `id="fatos"`.
- Atualizar `test_componentes_pedagogicos`: checklist `7 → 8`; quiz `>=` valor atual `+ 1`.
- Escrever a seção + 1 item de checklist + 1 ou 2 questões + a referência; `./gerar.sh <Slug>`; `python3 -m unittest testes.<arquivo>` → PASS; commit `feat(<slug>): seção <tema>`.

| Task | Módulo / corpo / teste | `id` | Termos obrigatórios na seção | Referência em `fatos` |
|---|---|---|---|---|
| 5 | 25 `gestao_de_riscos_ti_body.html` / `test_gestao_riscos_ti.py` | `iso-27005` | `ISO/IEC 27005:2022`, `ISO 31000`, `6.1.2`, `baseada em eventos`, `baseada em ativos`, `critérios de aceitação`, `matriz 5×5` | `ISO/IEC 27005:2022` |
| 6 | 27 `lgpd_e_privacidade_body.html` / `test_lgpd.py` | `iso-27701` | `ISO/IEC 27701`, `controlador`, `operador`, `art. 46`, `GDPR`, `art. 25`, `Privacy by Design`, `by Default` | `ISO/IEC 27701` |
| 7 | 21 `seguranca_em_nuvem_body.html` / `test_seguranca_nuvem.py` | `iso-27017-27018` | `ISO/IEC 27017`, `ISO/IEC 27018`, `Declaração de Aplicabilidade`, `responsabilidade compartilhada`, `dados pessoais` | `ISO/IEC 27017` e `ISO/IEC 27018` |
| 8 | 28 `continuidade_e_disaster_recovery_body.html` / `test_continuidade.py` | `iso-22301` | `ISO 22301:2019`, `SGCN`, `BIA`, `exercícios`, `certificação`, `2024` | `ISO 22301:2019` |
| 9 | 24 `ia_e_ciberseguranca_body.html` / `test_ia_ciber.py` | `governanca-ia` | `ISO/IEC 42001:2023`, `AI RMF`, `Govern`, `Map`, `Measure`, `Manage`, `NIST AI 600-1` | `ISO/IEC 42001:2023` e `NIST AI 100-1` |

Na Task 6, as edições exatas (27701 de 2019 ou de 2025) entram depois de conferidas; o teste exige só `ISO/IEC 27701`.

---

### Task 10: Compilação total, suíte completa e fechamento

**Files:**
- Modify: `docs/superpowers/specs/2026-11-02-auditoria-ti-e-certificacoes-design.md` (Status)

- [ ] **Step 1:** `./gerar.sh todos` (de `_geradores/`) → 58 páginas e `index.html` sem erro.
- [ ] **Step 2:** `free -h`; com ≥ 4 GB disponíveis, `systemd-run --user --scope --quiet -p MemoryMax=4G -p MemorySwapMax=1G python3 -m unittest discover -s testes 2>&1 | tail -5` → `OK`. Com menos memória, rodar só os arquivos tocados nas Tasks 1–9 e registrar isso.
- [ ] **Step 3:** `git grep -n "57 módulos\|de 57\b" -- ':!docs'` → nenhuma ocorrência fora de histórico.
- [ ] **Step 4:** `git grep -n -i -w -F -f /tmp/claude-1000/-home-josemauro-projects-josemauro-estudos-cyberseguranca/726b8898-e2e0-4ae3-993e-1cc4c25a7484/scratchpad/termos-proibidos.txt -- ':!docs' ':!_geradores/testes'` → vazio (os testes e os docs citam só o termo genérico `linkedin.com/in/`). A lista fica fora do repositório (pasta temporária desta sessão); se não existir mais, pedir ao usuário os termos antes de concluir.
- [ ] **Step 5:** Status da spec: "Aprovada (2026-11-02) e implementada". Commit `docs: fecha a spec da auditoria de TI e certificações`.
