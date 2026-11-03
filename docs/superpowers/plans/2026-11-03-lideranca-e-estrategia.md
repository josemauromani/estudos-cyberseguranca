# Trilha 14 Liderança & Estratégia e Ajustes de Perfis Executivos: Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar a Trilha 14 com os módulos 59 (Liderança e Programa de Segurança) e 60 (Estruturação da Área de Segurança), acrescentar CRISC e CDPSE à matriz (15 → 17), uma seção de ciclo de vida de certificados no Estudo 03, a correspondência normativa no Estudo 54 e as trajetórias executivas no Estudo 33.

**Architecture:** Portal estático e offline. Cada módulo é um corpo `_geradores/<slug_snake>_body.html` compilado por `montar.py` para `<Pasta>/treinamento-<slug-kebab>.html`; metadados e visões do portal vêm de `_geradores/index_dados.py` e `_geradores/estudos.txt`, renderizados por `build_index.py`. Simuladores em JavaScript puro leem um bloco `<script type="application/json">`; os testes `unittest` espelham as regras em Python. Cores de trilha: tokens em `tokens.css`, regra em `index.css`, selo em `base.css`.

**Tech Stack:** Python 3 (`unittest`), HTML/CSS/JS puro, Mermaid pré-compilado, `_geradores/gerar.sh`.

**Spec:** `docs/superpowers/specs/2026-11-03-lideranca-e-estrategia-design.md`

## Global Constraints

- Trabalho num branch `feat/lideranca-e-estrategia` (ou worktree criado pelo executor); nada direto na `main`.
- Textos em pt-BR, no tom e no contrato do `_geradores/GUIA-DO-AUTOR.md` §2.2 (um `article`; seções `class`/`id`/`data-tipo` nessa ordem; `h2` no início; callout sempre com modificador). Checklist: 4 a 8 itens.
- Módulos 59 e 60 no **fim** de `estudos.txt`, nessa ordem; módulos 01–58 não mudam de número nem de trilha.
- Trilha 14: nome `Liderança & Estratégia`, `cor` `#A16207`, `cor_nome` `gold`, token `--t14-gold` (`#A16207` nos blocos claros, `#FDE047` nos escuros). Fallback se o contraste falhar: `#854D0E` (claro); registrar `Ruling` no `progress.md`.
- **Nenhum** nome, empresa, instituição, URL ou conquista identificável dos perfis do LinkedIn no repositório (nem "F63", "A93", "primeiro programa do Brasil"). Trajetórias são exemplos, nunca estatística (sem `%`).
- Números de certificação, norma ou padrão só com fonte oficial. Valores já conferidos estão neste plano; os do BCB têm passo de conferência próprio (Task 7).
- Sourcing ensinado por modelo (interno, MSSP, MDR, híbrido), sem marcas de fornecedor.
- Testes: rodar a partir de `_geradores/` com `python3 -m unittest testes.<arquivo>`. Antes da suíte completa, `free -h`; com menos de ~4 GB disponíveis, só os arquivos afetados. Suíte completa só em `systemd-run --user --scope --quiet -p MemoryMax=4G -p MemorySwapMax=1G python3 -m unittest discover -s testes`. Nunca duas suítes em paralelo.
- Para truncar saída longa, `cut -c1-1500`; nunca `sed`/`grep` com intervalo grande no regex.
- Commits terminam com `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Review Focus

1. **Contagem do portal fixa no teste:** ao entrar o 59, `index.html` mostra `59 / 59` e `test_auditoria_de_ti::test_integracao_com_portal_index` (que exige `58 / 58`) quebra. A Task 1 troca a asserção por uma derivada do catálogo (`f"{n} / {n}"`).
2. **Dourado sem contraste no tema claro:** `test_assets::test_numero_do_bloco_de_trilha_legivel_nos_dois_temas`, `test_portal::test_texto_pequeno_colorido_tem_contraste_aa_nos_temas` e `test_componentes_css` decidem; fallback na Task 1.
3. **Mais de 6 KRIs no painel do simulador 59:** o motor deve recusar o sétimo com aviso, não cortar em silêncio (teste `test_limite_de_kris`, Task 1).
4. **Alocação inválida no simulador 60:** soma acima do orçamento, pontos negativos ou não inteiros devem ser recusados com mensagem e sem calcular perfil (teste `test_alocacao_invalida`, Task 2).
5. **Marca de perfil vazando nos módulos novos:** exemplos inspirados nos perfis com números de rating ou "primeiro programa" (teste `test_sem_marcas_de_perfis` nas Tasks 1 e 2; varredura com a lista de termos na Task 8).

---

### Task 1: Trilha 14 e Módulo 59 Liderança e Programa de Segurança

**Files:**
- Create: `_geradores/lideranca_e_programa_de_seguranca_body.html`
- Create: `_geradores/testes/test_lideranca_e_programa.py`
- Create (compilado): `Lideranca-e-Programa-de-Seguranca/treinamento-lideranca-e-programa-de-seguranca.html`
- Modify: `_geradores/estudos.txt` (cabeçalho "59 Módulos" nesta task, legenda `# 14 = Liderança & Estratégia (#A16207)`, linha nova no fim)
- Modify: `_geradores/index_dados.py` (`TRILHAS[14]`, `ESTUDOS_DADOS`)
- Modify: `_geradores/tokens.css` (4 blocos), `_geradores/index.css` (`[data-trilha="14"]`), `_geradores/base.css` (`.badge-t14`)
- Modify: `_geradores/testes/test_curriculo.py:29-30` (58 → 59, 13 → 14), `_geradores/testes/test_componentes_css.py:186` (13 → 14), `_geradores/testes/test_auditoria_de_ti.py:367` (contagem derivada)

**Interfaces:**
- Produces: `TRILHAS[14] = {"id": 14, "nome": "Liderança & Estratégia", "cor": "#A16207", "cor_nome": "gold", "descricao": "Como o CISO pensa e como se monta uma área de segurança: governança, métricas para o conselho, orçamento, maturidade e sourcing."}`; slug `Lideranca-e-Programa-de-Seguranca` (número 59); JSON `<script type="application/json" id="lid-dados">`; JS `classificar(indicadorId, classe)`, `avaliarPainel()`.

- [ ] **Step 1: Preparação fora do repositório.** Mover `~/Downloads/Profile (4).pdf` … `Profile (8).pdf` para `perfis-linkedin/` (ignorada pelo git; conferir com `git status` que nada aparece). Criar `.superpowers/sdd/<plano>/termos-proibidos.txt` com nomes, sobrenomes, empresas, instituições de ensino, URLs dos 5 perfis e as marcas "F63", "A93". Não commitar.

- [ ] **Step 2: Trilha 14 nos dados e no CSS.** `TRILHAS[14]` como em Interfaces. `--t14-gold: #A16207;` nos 2 blocos claros e `--t14-gold: #FDE047;` nos 2 escuros de `tokens.css`, seguindo a posição de `--t13-lime`; `[data-trilha="14"] { --gc: var(--t14-gold); }` em `index.css` ao lado da linha 650; `.badge-t14 { background-color: rgba(161, 98, 7, 0.15); color: var(--t14-gold); }` em `base.css` após `.badge-t13`.

- [ ] **Step 3: Catálogo e metadados.** Linha no fim de `estudos.txt`:
  `Lideranca-e-Programa-de-Seguranca|Liderança e Programa de Segurança: o Papel do CISO|Lideranca-e-Programa-de-Seguranca|treinamento-lideranca-e-programa-de-seguranca.html|14|#A16207|Govern`
  `ESTUDOS_DADOS["Lideranca-e-Programa-de-Seguranca"]`: `titulo` igual ao título curto; `subtitulo` "Linha de reporte, governança, KPI e KRI, relato ao conselho e orçamento de segurança"; `trilha` 14; `nist` "Govern"; `mitre` "N/A (liderança e governança)"; `carreiras` `["GRC & Auditoria", ROTULO_ANALISTA_SI]`; `tempo_minutos` 45; `nivel` "intermediario"; `pergunta_chave` "O SIEM gerou 40 mil alertas no trimestre. O que disso o conselho precisa saber?"; `simulador_nome` "Do SIEM ao Conselho"; `fatos`: "Modelo das três linhas (IIA, 2020)", "Função Govern do NIST CSF 2.0", "KPI, KRI e métrica de vaidade", "Business case e limites do ROSI".

- [ ] **Step 4: Ajustar testes de total.** `test_curriculo.py`: 59 módulos e 14 trilhas. `test_componentes_css.py:186`: 14. `test_auditoria_de_ti.py:367`: trocar `"58 / 58"` por `f"{n} / {n}"` com `n` = número de linhas do catálogo (`montar.carregar_catalogo_estudos()`).

- [ ] **Step 5: Escrever `test_lideranca_e_programa.py` (falhando),** no padrão de `test_auditoria_de_ti.py`. `SLUG = "Lideranca-e-Programa-de-Seguranca"`. Testes:
  - `test_body_and_compiled_files_exist`.
  - `test_secoes`: ids na ordem `["introducao", "governanca", "risco-de-negocio", "metricas-conselho", "orcamento", "simulador", "checklist", "quiz", "fatos"]`; compilado contém `Seção 1 de 9` … `Seção 9 de 9`; `data-slug="lideranca-e-programa-de-seguranca"`.
  - `test_coerencia_com_o_catalogo`: `simulador_nome`, `pergunta_chave` e cada `fato` no compilado; `subtitulo` no `index.html`.
  - `test_termos_chave`: no corpo, `três linhas`, `IIA`, `independência`, `CISO`, `CTO`, `DPO`, `encarregado`, `NIST CSF 2.0`, `GV.OC`, `GV.RM`, `GV.RR`, `GV.PO`, `GV.OV`, `GV.SC`, `RACI`, `apetite`, `tolerância`, `KPI`, `KRI`, `métrica de vaidade`, `Capex`, `Opex`, `business case`, `ROSI`, `Res. CMN 4.893/2021`.
  - `test_pontes`: antes de `id="simulador"`, `Estudo 25`, `Estudo 26`, `Estudo 54`, `Estudo 58`; em `id="fatos"`, `Trilha 14`, `Estudo 60`, `Estudo 33`.
  - `test_nao_repete_calculo_de_risco`: o corpo não contém `ALE =` nem `SLE =` e cita o `Estudo 25` na seção `risco-de-negocio`.
  - `test_referencias`: em `id="fatos"`, `Three Lines Model`, `NIST CSF 2.0`, `CSWP 29`, `Res. CMN 4.893/2021`.
  - `test_dados_do_simulador`: JSON `#lid-dados` com `limite_painel` = 6 e `indicadores` (12), cada um com `id`, `nome`, `valor`, `gabarito` ∈ {`kri`, `kpi`, `vaidade`}, `essencial` (bool) e `explicacao` (str não vazia); ao menos 4 `kri`, 3 `kpi` e 3 `vaidade`; `essencial` só em `kri`, entre 3 e 5 essenciais.
  - `test_regras_espelhadas`: `avaliar_painel(dados, escolhas: dict[str, str]) -> dict` com chaves `acertos` (int), `kri_no_painel` (list), `essenciais_ausentes` (list), `vaidade_no_painel` (list); escolhas = gabarito → `acertos` 12 e as três listas sem problema; trocar um essencial para `kpi` → aparece em `essenciais_ausentes`; marcar uma `vaidade` como `kri` → aparece em `vaidade_no_painel`.
  - `test_limite_de_kris`: o JS contém o texto de aviso do limite (`"O painel aceita no máximo 6 KRIs"`) e `classificar` recusa o sétimo `kri` (verificar no código a comparação com `limite_painel` antes de aceitar); em Python, `avaliar_painel` com 7 `kri` levanta `ValueError`.
  - `test_simulador_sem_apis_inseguras`: critério de `test_auditoria_de_ti.py` (sem `innerHTML =` com dado do JSON, sem `eval`, sem `fetch`).
  - `test_sem_marcas_de_perfis`: o corpo não contém `F63`, `A93`, `primeiro programa`.
  - `test_componentes_pedagogicos`: `checklist-item` entre 4 e 8; `quiz-item` ≥ 6; ao menos 1 `pre class="mermaid"`.
  Rodar `python3 -m unittest testes.test_lideranca_e_programa` → FAIL (arquivos ausentes).

- [ ] **Step 6: Escrever o corpo** com o conteúdo da spec §4.1, nas seções da ordem do teste (o papel do CISO e a linha de reporte ficam em `introducao`). Diagrama Mermaid das três linhas com o CISO e o conselho. Laboratório: 12 indicadores fictícios da spec; três botões por indicador (KRI, KPI, Vaidade); painel lateral com os KRIs escolhidos; "Avaliar painel" mostra acertos, essenciais ausentes, vaidade no painel e a `explicacao` de cada item. Interface montada com `textContent`/`createElement`. Checklist "Antes de levar um tema ao conselho" (5 itens da spec). 6+ questões com resposta explicada.

- [ ] **Step 7: Compilar.** De `_geradores/`: `./gerar.sh Lideranca-e-Programa-de-Seguranca` → sem erro do validador; cria o HTML e regenera `index.html`.

- [ ] **Step 8: Rodar** `python3 -m unittest testes.test_lideranca_e_programa testes.test_curriculo testes.test_assets testes.test_portal testes.test_componentes_css testes.test_auditoria_de_ti testes.test_corpos_migrados testes.test_index` → PASS. Se só os testes de contraste falharem, aplicar o fallback `#854D0E` (tokens claros, `estudos.txt`, `TRILHAS[14]["cor"]`, `rgba` do selo), registrar o `Ruling` e rodar de novo.

- [ ] **Step 9: Commit** `feat(lideranca): trilha 14 e módulo 59 Liderança e Programa de Segurança`.

---

### Task 2: Módulo 60 Estruturação da Área de Segurança

**Files:**
- Create: `_geradores/estruturacao_da_area_de_seguranca_body.html`
- Create: `_geradores/testes/test_estruturacao_da_area.py`
- Create (compilado): `Estruturacao-da-Area-de-Seguranca/treinamento-estruturacao-da-area-de-seguranca.html`
- Modify: `_geradores/estudos.txt` (cabeçalho "60 Módulos", linha nova no fim), `_geradores/index_dados.py` (`ESTUDOS_DADOS`), `_geradores/testes/test_curriculo.py:29` (59 → 60)

**Interfaces:**
- Consumes: `TRILHAS[14]` (Task 1).
- Produces: slug `Estruturacao-da-Area-de-Seguranca` (número 60); JSON `<script type="application/json" id="est-dados">`; JS `aplicarPlano(cenarioId, sourcing, alocacao)`.

- [ ] **Step 1: Catálogo e metadados.** Linha no fim de `estudos.txt`:
  `Estruturacao-da-Area-de-Seguranca|Estruturação da Área de Segurança: Maturidade, Time e Sourcing|Estruturacao-da-Area-de-Seguranca|treinamento-estruturacao-da-area-de-seguranca.html|14|#A16207|Govern` (usar a cor final da Task 1).
  `ESTUDOS_DADOS`: `subtitulo` "Plano de 90 dias, perfis do NIST CSF 2.0, desenho do time, SOC interno, MSSP e MDR, conscientização e aquisições"; `trilha` 14; `nist` "Govern"; `mitre` "N/A (estruturação e sourcing)"; `carreiras` `["GRC & Auditoria"]`; `tempo_minutos` 50; `nivel` "avancado"; `pergunta_chave` "Você chegou como primeiro CISO da empresa. O que acontece nos primeiros 90 dias?"; `simulador_nome` "Alocador de Programa"; `fatos`: "Perfil atual e perfil alvo (NIST CSF 2.0)", "Níveis (tiers) 1 a 4", "SOC interno, MSSP, MDR e híbrido", "Plano de 90 dias". `test_curriculo.py`: 60.

- [ ] **Step 2: Escrever `test_estruturacao_da_area.py` (falhando).** `SLUG = "Estruturacao-da-Area-de-Seguranca"`. Testes:
  - `test_body_and_compiled_files_exist`; `test_secoes`: ids `["introducao", "maturidade", "time-e-sourcing", "conscientizacao", "fusoes-e-aquisicoes", "simulador", "checklist", "quiz", "fatos"]`, `Seção 1 de 9` … `Seção 9 de 9`; `test_coerencia_com_o_catalogo` (como na Task 1).
  - `test_termos_chave`: `90 dias`, `perfil atual`, `perfil alvo`, `Tier 1`, `Tier 4`, `CMMI`, `C2M2`, `SOC interno`, `MSSP`, `MDR`, `híbrido`, `SLA`, `plano de saída`, `taxa de reporte`, `due diligence`, `federação`, `risco herdado`.
  - `test_pontes`: antes de `id="simulador"`, `Estudo 15`, `Estudo 16`, `Estudo 41`, `Estudo 57`, `Estudo 59`; em `id="fatos"`, `Trilha 14`, `60 módulos`.
  - `test_referencias`: em `id="fatos"`, `NIST CSF 2.0`, `CSWP 29`, `Quick-Start Guide`.
  - `test_sem_marcas_de_fornecedor_e_de_perfis`: a seção `time-e-sourcing` não contém nomes de produto (lista no teste: `CrowdStrike`, `SentinelOne`, `Splunk`, `QRadar`, `Microsoft Sentinel`, `Arctic Wolf`); o corpo não contém `F63`, `A93`, `primeiro programa`.
  - `test_dados_do_simulador`: JSON `#est-dados` com `funcoes` = `["GV", "ID", "PR", "DE", "RS", "RC"]`; `frentes` (6: `identidade`, `vulnerabilidades`, `deteccao`, `resiliencia`, `conscientizacao`, `grc`), cada uma com `efeitos` `{funcao: pontos_por_nivel}` (inteiro > 0); `sourcing` com 4 opções (`interno`, `mssp`, `mdr`, `hibrido`), cada uma com `custo` (int), `efeitos` `{funcao: niveis}` e `riscos` (lista de str); `cenarios` (3: `varejo`, `fintech`, `industria`), cada um com `orcamento` (int), `perfil_atual` e `perfil_alvo` (`{funcao: 1..4}`), `exigencias` (lista de `{funcao, nivel_minimo, motivo}`), `solucao_exemplo` (`{sourcing, alocacao}`) e `armadilha` (`{sourcing, alocacao, falha_esperada}`).
  - `test_regras_espelhadas`: `aplicar_plano(dados, cenario_id, sourcing, alocacao) -> dict` com `perfil_alcancado` (`{funcao: nivel}`), `exigencias_nao_atendidas` (lista de `motivo`) e `riscos_residuais` (funções com alcançado < alvo, mais os `riscos` do sourcing). Regra: `nivel = min(4, perfil_atual[f] + efeitos_do_sourcing[f] + soma(alocacao[frente] // pontos_por_nivel[f] para cada frente que afeta f))`; orçamento disponível para frentes = `orcamento - custo do sourcing`. Para cada cenário: `solucao_exemplo` → `exigencias_nao_atendidas == []`; `armadilha` → `falha_esperada` ∈ `exigencias_nao_atendidas`.
  - `test_alocacao_invalida`: soma acima do disponível, valor negativo ou não inteiro → `aplicar_plano` levanta `ValueError`; o JS mostra mensagem (`"A alocação passa do orçamento"`) e não calcula o perfil.
  - `test_exigencia_regulatoria_fundamentada`: no cenário `fintech`, toda exigência cujo `motivo` cite norma cita `Res. CMN 4.893/2021`, e o corpo explica a exigência no texto do cenário.
  - `test_simulador_sem_apis_inseguras`; `test_componentes_pedagogicos` (checklist 4–8 com o "Plano de 90 dias" da spec; `quiz-item` ≥ 6; ao menos 1 Mermaid).
  Rodar → FAIL.

- [ ] **Step 3: Escrever o corpo** com o conteúdo da spec §4.2. Diagrama Mermaid perfil atual → gap → roadmap. Laboratório: seletor de cenário, rádio de sourcing, 6 campos inteiros de alocação com "disponível" ao vivo; "Aplicar plano" mostra tabela por função (atual, alcançado, alvo), exigências não atendidas e riscos residuais; o feedback diz que o exemplo é didático, não receita única. Exigências do cenário `fintech` só citam a Res. CMN 4.893/2021 onde ela de fato exige (conferir o texto no módulo 54 e na norma).

- [ ] **Step 4: Compilar** `./gerar.sh Estruturacao-da-Area-de-Seguranca` → sem erro.

- [ ] **Step 5: Rodar** `python3 -m unittest testes.test_estruturacao_da_area testes.test_lideranca_e_programa testes.test_curriculo testes.test_portal testes.test_corpos_migrados testes.test_index testes.test_auditoria_de_ti` → PASS.

- [ ] **Step 6: Commit** `feat(lideranca): módulo 60 Estruturação da Área de Segurança`.

---

### Task 3: Rotas, matriz e documentação para 60 módulos

**Files:**
- Modify: `_geradores/index_dados.py` (`ROTAS_PERFIL` `grc` e `analista_si`; `CERTIFICACOES` CISM e CISSP)
- Modify: `_geradores/CURRICULO.md`, `README.md`, `_geradores/GUIA-DO-AUTOR.md`
- Modify: `_geradores/gestao_de_riscos_de_terceiros_body.html`, `_geradores/auditoria_de_ti_body.html` ("58 módulos" → "60 módulos")
- Modify: `_geradores/testes/test_auditoria_de_ti.py` (175, 379, 382–383), `_geradores/testes/test_gestao_riscos_terceiros.py:252`, `_geradores/testes/test_curriculo.py`

**Interfaces:**
- Consumes: slugs dos módulos 59 e 60.

- [ ] **Step 1: Teste (falhando)** `test_curriculo.py::test_trilha_14_documentada`: `"Trilha 14: Liderança & Estratégia"` em `CURRICULO.md` e `README.md`; `"#### 59. Lideranca-e-Programa-de-Seguranca"` e `"#### 60. Estruturacao-da-Area-de-Seguranca"` em `CURRICULO.md`; `"60 módulos"` no `README.md`; nenhum `"58 módulos"` em `README.md`, `CURRICULO.md`, `GUIA-DO-AUTOR.md` e nos `*_body.html`. E `test_rotas_incluem_lideranca`: em `ROTAS_PERFIL`, `grc` termina com `[..., "Lideranca-e-Programa-de-Seguranca", "Estruturacao-da-Area-de-Seguranca"]` e `analista_si` termina com `"Lideranca-e-Programa-de-Seguranca"`; CISM contém os dois slugs e CISSP contém o 59. Trocar nos testes de 57 e 58 as asserções de "58 módulos" por "60 módulos". Rodar → FAIL.

- [ ] **Step 2: Dados.** Rotas e certificações como no teste. Se o JSON `#cert-dados` do Estudo 33 lista módulos por domínio do CISM, acrescentar o 59 ao domínio de governança e o 60 ao de programa de segurança (`test_modulos_batem_com_o_catalogo` decide).

- [ ] **Step 3: Documentação.** `CURRICULO.md`: visão geral (60 módulos, 14 trilhas), diagrama Mermaid das trilhas (`T14["Trilha 14: Liderança & Estratégia"]` ligado a Govern), tabela de trilhas (`#A16207` Dourado), seção `### Trilha 14: Liderança & Estratégia` com `#### 59.` e `#### 60.` no formato das demais, distribuição NIST (GOVERN passa a 10 módulos: 25, 26, 27, 31, 54, 56, 57, 58, 59, 60), rota GRC com `-> 59 -> 60` no fim. `README.md`: contagens, diagrama, linhas 59 e 60 da tabela de módulos, perfis. `GUIA-DO-AUTOR.md` e os corpos de 57 e 58: "60 módulos". Recompilar 57 e 58 (`./gerar.sh Gestao-de-Riscos-de-Terceiros`, `./gerar.sh Auditoria-de-TI`).

- [ ] **Step 4: Rodar** `python3 -m unittest testes.test_curriculo testes.test_auditoria_de_ti testes.test_gestao_riscos_terceiros testes.test_certificacoes_carreira testes.test_index testes.test_portal` → PASS.

- [ ] **Step 5: Commit** `docs(lideranca): rotas, matriz e documentação para 60 módulos`.

---

### Task 4: Certificações CRISC e CDPSE (15 → 17)

**Files:**
- Modify: `_geradores/index_dados.py` (`CERTIFICACOES`, fim da lista)
- Modify: `_geradores/certificacoes_e_carreira_body.html` (JSON `#cert-dados`, subtítulo e textos com "15 certificações")
- Modify: `_geradores/testes/test_certificacoes_carreira.py`

**Interfaces:**
- Consumes: slug `Lideranca-e-Programa-de-Seguranca` (Task 1).
- Produces: siglas `CRISC` e `CDPSE` na 16ª e 17ª posições das duas listas.

Valores conferidos em 2026-11-03 nas páginas da ISACA (`/credentialing/crisc`, `/crisc-exam-content-outline`, `/get-crisc-certified`, `/maintain-crisc-certification` e os equivalentes da CDPSE):

| | CRISC | CDPSE |
|---|---|---|
| Domínios e pesos | Governance 26; Risk Assessment 22; Risk Response and Reporting 32; Technology and Security 20 | Privacy Governance 20; Privacy Risk Management and Compliance 18; Data Life Cycle Management 23; Privacy Engineering 39 |
| Experiência | 3 anos em ao menos 2 dos 4 domínios, nos 10 anos anteriores ao pedido | 3 anos nos domínios da CDPSE, nos 10 anos anteriores ao pedido |
| Pedido após a prova | até 5 anos | até 5 anos |
| Manutenção | 20 CPE/ano, 120 por ciclo de 3 anos, taxa anual | idem |
| Dispensas | a página não publica; texto diz "confira dispensas na página oficial" | idem |

- [ ] **Step 1: Testes (falhando).** `test_tabela_certificacoes_da_secao` (linha 450): 17. `test_dominios_e_pesos`: `pesos("CRISC") == [26, 22, 32, 20]`, `pesos("CDPSE") == [20, 18, 23, 39]`. `test_crisc_e_cdpse`: no JSON, as duas com `orgao` "ISACA", `nivel` 3, `requisitos == {"conferir": True}`, `fontes` com a página oficial e a do conteúdo do exame, `manutencao` contendo `120` e `3 anos`, `experiencia` contendo `3 anos` e `10 anos`; na matriz, `site_oficial` `https://www.isaca.org/credentialing/crisc` e `https://www.isaca.org/credentialing/cdpse`; CRISC com ≥ 5 módulos incluindo `Lideranca-e-Programa-de-Seguranca`; CDPSE com ≥ 5 incluindo `LGPD-e-Privacidade`. `test_sem_texto_de_quinze`: nenhum `"15 certificações"` nos arquivos verificados por `test_sem_texto_de_doze`. Rodar → FAIL.

- [ ] **Step 2: Dados.** `CERTIFICACOES` (matriz): CRISC foco "Risco de TI e controles", módulos `Gestao-de-Riscos-TI`, `Lideranca-e-Programa-de-Seguranca`, `ISO-27001-e-27002`, `Gestao-de-Riscos-de-Terceiros`, `Auditoria-de-TI`, `Continuidade-e-Disaster-Recovery`, `Autenticacao-e-IAM`, `Gestao-de-Vulnerabilidades`; CDPSE foco "Privacidade na arquitetura e no ciclo de vida dos dados", módulos `LGPD-e-Privacidade`, `Gestao-de-Riscos-de-Terceiros`, `Protecao-de-Dados-e-Conteudo`, `Seguranca-de-Bancos-de-Dados`, `Criptografia-Pratica`, `DevSecOps-e-CI-CD`, `Seguranca-em-Nuvem`, `Seguranca-em-APIs`. JSON do planejador: domínios em pt-BR (Governança; Avaliação de riscos; Resposta a riscos e relato; Tecnologia e segurança / Governança da privacidade; Gestão de riscos de privacidade e conformidade; Gestão do ciclo de vida dos dados; Engenharia de privacidade), cada um com os módulos da matriz que o cobrem; `nota_dominios` citando o conteúdo do exame publicado pela ISACA; `sem_experiencia` no modelo da CISA (prova antes, pedido em até 5 anos). Textos: subtítulo do Estudo 33 e "15 certificações" → "17 certificações"; textos que listam as certificações "conferir" incluem CRISC e CDPSE (`test_textos_listam_todas_as_certificacoes_conferir` decide).

- [ ] **Step 3: Compilar** `./gerar.sh Certificacoes-e-Carreira` e rodar `python3 -m unittest testes.test_certificacoes_carreira testes.test_abas_certificacao_progresso testes.test_index testes.test_portal` → PASS.

- [ ] **Step 4: Commit** `feat(certificacoes): CRISC e CDPSE na matriz e no planejador`.

---

### Task 5: Trajetórias executivas no Estudo 33 (3 → 8 perfis)

**Files:**
- Modify: `_geradores/certificacoes_e_carreira_body.html` (seção `trajetorias`, `quiz`)
- Modify: `_geradores/testes/test_certificacoes_carreira.py`

**Interfaces:**
- Consumes: siglas CRISC (Task 4); slugs 59 e 60.

- [ ] **Step 1: Testes (falhando).** Em `test_trajetorias_conteudo`, trocar `"três perfis"` por `"oito perfis"`. Novo `test_trajetorias_lideranca_executiva`: a seção contém `Liderança executiva`, `auditor`, `DPO`, `arquiteto`, `CTO`, `IAM`, `mesma empresa`, `comunidade`, `CISSP`, `setor financeiro`, `Estudo 59`, `Estudo 60`, a frase `só 1 dos 5` e `ilustra`; a tabela "Por onde começar" tem a linha `Liderança / CISO` com `CISM`, `CRISC`, `CISSP` e `Estudo 25`, `Estudo 26`, `Estudo 58`, `Estudo 59`, `Estudo 60`. `test_trajetorias_sem_dados_pessoais` continua (sem `%`) e ganha `F63`, `A93`, `primeiro programa`. `test_checklist_e_quiz_33`: +1 no mínimo de `quiz-item`; checklist continua 8. Rodar → FAIL.

- [ ] **Step 2: Texto** conforme a spec §5.4: abertura com "oito perfis", bloco `<h3>Liderança executiva</h3>` com os 4 padrões, fecho, linha nova da tabela e 1 questão sobre o que pesa no topo da carreira.

- [ ] **Step 3: Compilar e rodar** `./gerar.sh Certificacoes-e-Carreira`; `python3 -m unittest testes.test_certificacoes_carreira` → PASS.

- [ ] **Step 4: Commit** `feat(carreira): trajetórias de liderança executiva no Estudo 33`.

---

### Task 6: Estudo 03, ciclo de vida de certificados e cripto-agilidade

**Files:**
- Modify: `_geradores/criptografia_pratica_body.html` (seção nova antes de `id="laboratorio-cripto"`; `questoes-fixacao`; `fatos-essenciais`)
- Modify: `_geradores/testes/test_criptografia_pratica.py`

Valores conferidos em 2026-11-03 no texto da votação SC-081v3 (CA/Browser Forum, votação encerrada em 11/04/2025) e em csrc.nist.gov:

| Emitido a partir de | Validade máxima | Reuso da validação de domínio |
|---|---|---|
| antes de 15/03/2026 | 398 dias | 398 dias |
| 15/03/2026 | 200 dias | 200 dias |
| 15/03/2027 | 100 dias | 100 dias |
| 15/03/2029 | 47 dias | 10 dias |

FIPS 203 (ML-KEM), 204 (ML-DSA) e 205 (SLH-DSA), publicados como finais em 13/08/2024.

- [ ] **Step 1: Testes (falhando).** `test_secao_ciclo_de_certificados`: existe `<section class="study-section" id="ciclo-de-certificados" data-tipo="teoria">` imediatamente antes de `id="laboratorio-cripto"`; contém `CLM`, `ACME`, `RFC 8555`, `SC-081`, `15 de março de 2026`, `200 dias`, `15 de março de 2027`, `100 dias`, `15 de março de 2029`, `47 dias`, `398 dias`, `10 dias`, `CBOM`, `FIPS 203`, `ML-KEM`, `FIPS 204`, `ML-DSA`, `FIPS 205`, `SLH-DSA`, `agosto de 2024`, `colher agora, decifrar depois`, `cripto-agilidade`. `test_referencias_clm`: `fatos-essenciais` contém `cabforum.org`, `RFC 8555`, `csrc.nist.gov`. `test_componentes_pedagogicos`: +1 no mínimo de questões. Rodar → FAIL.

- [ ] **Step 2: Escrever a seção** conforme a spec §5.1, com a tabela acima, um callout-warning sobre queda por certificado vencido e um callout-tip com as etapas do plano de migração pós-quântica. 1 questão nova em `questoes-fixacao`; referências novas em `fatos-essenciais`.

- [ ] **Step 3: Compilar e rodar** `./gerar.sh Criptografia-Pratica`; `python3 -m unittest testes.test_criptografia_pratica testes.test_corpos_migrados` → PASS.

- [ ] **Step 4: Commit** `feat(criptografia): ciclo de vida de certificados e cripto-agilidade`.

---

### Task 7: Estudo 54, correspondência normativa

**Files:**
- Modify: `_geradores/regulacao_setor_financeiro_body.html` (fim da seção `exigencias`; `quiz`; `fatos`)
- Modify: `_geradores/testes/test_regulacao_setor_financeiro.py`

- [ ] **Step 1: Conferir no site do BCB pelo navegador** (o fetch automático não renderiza `bcb.gov.br`; usar Claude in Chrome ou a busca de normas do BCB): (a) Res. CMN 4.893/2021 revogou a Res. CMN 4.658/2018; (b) Res. BCB 85/2021 revogou a Circular 3.909 e o ano da circular (esperado: 2018); (c) datas das quatro normas. Anotar a URL de cada conferência no `progress.md`. Se algum valor divergir do esperado, usar o conferido no teste e no texto e registrar `Ruling`. Se o site não abrir de forma alguma, parar e perguntar ao usuário.

- [ ] **Step 2: Teste (falhando)** `test_correspondencia_normativa`: a seção `exigencias` contém uma tabela com `Res. CMN 4.658/2018` → `Res. CMN 4.893/2021` e `Circular 3.909/2018` → `Res. BCB 85/2021` (valores conferidos no Step 1), um `callout` explicando que vagas e currículos ainda citam os números antigos, e `bcb.gov.br` em `fatos`. `test_seis_secoes_obrigatorias` continua passando (nenhuma seção nova). `test_componentes_pedagogicos`: +1 questão. Rodar → FAIL.

- [ ] **Step 3: Escrever a tabela, o callout e a questão.** Compilar `./gerar.sh Regulacao-Setor-Financeiro`; rodar `python3 -m unittest testes.test_regulacao_setor_financeiro` → PASS.

- [ ] **Step 4: Commit** `feat(regulacao): correspondência entre normas revogadas e vigentes`.

---

### Task 8: Compilação total, suíte completa e varredura de anonimização

**Files:**
- Modify (compilados): todos os `treinamento-*.html` e `index.html`

- [ ] **Step 1: Compilar tudo.** `./gerar.sh todos` → sem erro; o portal mostra `60 / 60`.
- [ ] **Step 2: Suíte completa.** `free -h`; com ≥ 4 GB disponíveis, `systemd-run --user --scope --quiet -p MemoryMax=4G -p MemorySwapMax=1G python3 -m unittest discover -s testes` → `OK`.
- [ ] **Step 3: Varredura.** Para cada linha de `.superpowers/sdd/<plano>/termos-proibidos.txt`, `git grep -n -i -F -- "<termo>"` → zero ocorrências. `git status` não mostra `perfis-linkedin/`.
- [ ] **Step 4: Commit** (se a compilação mudou arquivos) `build: recompila portal e módulos para 60 módulos`.
