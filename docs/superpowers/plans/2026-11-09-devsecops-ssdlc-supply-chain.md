# DevSecOps SSDLC / Supply Chain / Secrets: Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Densificar o estudo DevSecOps-e-CI-CD com SSDLC/SAMM/Champions, SLSA/VEX na cadeia e secrets no pipeline, alinhando metadados, CURRICULO/README e a descrição da rota `appsec`.

**Architecture:** Conteúdo no `*_body.html` (contrato teoria/checklist/questões/referências); ordem pedagógica `introducao` → `ssdlc-samm` → `cadeia` → `secrets-no-pipeline`; metadados e `ROTAS_PERFIL` em `index_dados.py`; rebuild via `gerar.sh`.

**Tech Stack:** Python 3 (`unittest`), HTML/CSS/JS vanilla, Mermaid, `_geradores/gerar.sh`, `_geradores/montar.py`.

**Spec:** `docs/superpowers/specs/2026-11-09-devsecops-ssdlc-supply-chain-design.md`

## Global Constraints

- Textos em pt-BR; marca: nunca “Estudos de/em Cibersegurança”, “José Mauro”, “Brandão”, “Stelling” (`test_marca`).
- Catálogo permanece em **62** módulos; sem módulo 63; sem labs/simuladores.
- Ordem das teorias no 22: `introducao` → `ssdlc-samm` → `cadeia` → `secrets-no-pipeline`.
- Densidade B; SAMM como régua — **não** checklist SAMM íntegro; rota `appsec` **não** promete “SAMM completo”.
- Lista de módulos da rota `appsec` **não muda**.
- Commits só se o usuário pedir; mensagens no estilo do repo.
- Testes: de `_geradores/`, `python3 -m unittest testes.<modulo>`. Mermaid/`chrome-headless-shell` por ambiente não bloqueia se não for regressão deste ciclo.

## File map

| Área | Arquivos |
|---|---|
| Corpo 22 | `_geradores/devsecops_e_ci_cd_body.html` → `DevSecOps-e-CI-CD/treinamento-*.html` |
| Metadados/rota | `_geradores/index_dados.py` (`ESTUDOS_DADOS["DevSecOps-e-CI-CD"]`, `ROTAS_PERFIL` entry `appsec`) |
| Docs | `_geradores/CURRICULO.md` (#### 22), `README.md` (linha módulo 22) |
| Testes | `_geradores/testes/test_devsecops_conteudo.py` (criar); `test_rotas_sugeridas.py` (assert descrição appsec) |
| Portal | `index.html` via `gerar.sh` se rota/metadados mudarem |

## Review Focus

1. **Ordem das seções:** `ssdlc-samm` entre intro e cadeia; `secrets-no-pipeline` depois de cadeia — pinar em `extrair_secoes`. Task 1.
2. **SLSA/VEX na cadeia, não em secrets:** `cadeia` contém SLSA e VEX; `secrets-no-pipeline` não é o único lugar de SLSA. Task 1.
3. **Rota appsec honesta:** descrição menciona SSDLC (ou “ciclo de desenvolvimento seguro”) e não contém “SAMM completo”. Task 2.
4. **Callout de segredo:** conteúdo de revogação/histórico vive em `secrets-no-pipeline` (não só callout órfão na cadeia). Task 1.
5. **Sem lab:** zero `data-tipo="laboratorio"` / `.lab-box` no corpo 22. Task 3.

---

### Task 1: Conteúdo denso no estudo 22

**Files:**
- Create: `_geradores/testes/test_devsecops_conteudo.py`
- Modify: `_geradores/devsecops_e_ci_cd_body.html`

**Interfaces:**
- Produces: seções `id="ssdlc-samm"` e `id="secrets-no-pipeline"` (`data-tipo="teoria"`); `cadeia` expandida com SLSA e VEX; ordem  
  `introducao < ssdlc-samm < cadeia < secrets-no-pipeline`;  
  HTML contém `SSDLC`, `SAMM`, `SLSA`, `VEX` e (casefold) `secret`/`segredo`;  
  checklist ≥3 itens novos cobrindo SSDLC/Champion **ou** SLSA/VEX **ou** secrets/revogação;  
  ≥3 `quiz-item` cujo texto casefold menciona um de `ssdlc`, `samm`, `slsa`, `vex`, `secret`, `segredo`, `champion`;  
  `validar_corpo(html, stem)` sem erros; sem lab.

- [ ] **Step 1: Teste (RED).** Criar `test_devsecops_conteudo.py` com asserts das Interfaces (ordem via `extrair_secoes`; menções; checklist/questões; `validar_corpo`).  
  Rodar: `python3 -m unittest testes.test_devsecops_conteudo` → FAIL.

- [ ] **Step 2: Implementar** corpo conforme spec §3.1 (densidade B; ponte na intro; Mermaid em `ssdlc-samm`; SLSA 0–4 + VEX + provenance em `cadeia`; secrets densos na seção própria; checklist/quiz/refs; remover comentário residual de simulador se ainda existir).

- [ ] **Step 3: Rodar** `python3 -m unittest testes.test_devsecops_conteudo testes.test_marca` → PASS.

- [ ] **Step 4: Compilar** `./_geradores/gerar.sh DevSecOps-e-CI-CD` → OK (falha Mermaid de ambiente não bloqueia se o HTML foi gerado).

- [ ] **Step 5: Commit** (se pedido) `feat(devsecops): densifica SSDLC, SLSA/VEX e secrets no estudo 22`.

---

### Task 2: Metadados, docs e descrição da rota `appsec`

**Files:**
- Modify: `_geradores/index_dados.py` (`ESTUDOS_DADOS["DevSecOps-e-CI-CD"]`, `ROTAS_PERFIL` id `appsec` → `descricao` apenas)
- Modify: `_geradores/CURRICULO.md` (bloco `#### 22. DevSecOps-e-CI-CD`)
- Modify: `README.md` (célula de título do módulo 22)
- Modify: `_geradores/testes/test_rotas_sugeridas.py` (asserts da descrição `appsec`)

**Interfaces:**
- Produces:
  - `titulo` exemplo: `"SSDLC, SAST/DAST/SCA, SLSA e Secrets no Pipeline"` (ou equivalente que cite SSDLC + SLSA/secrets).
  - `subtitulo` e `fatos` incluem SSDLC, SLSA (ou supply chain) e secrets.
  - `tempo_minutos` ≥ 55 (corpo cresceu).
  - CURRICULO e README alinhados ao novo título/objetivos/conceitos (SAMM, SLSA, VEX, secrets).
  - `descricao` da rota `appsec`: casefold contém `ssdlc` **ou** `ciclo de desenvolvimento seguro`; **não** contém `samm completo`; preferível mencionar SBOM/SLSA ou secrets.
  - `modulos` da rota `appsec` inalterados.

- [ ] **Step 1: Teste (RED).** Em `test_rotas_sugeridas.py` acrescentar `test_descricao_appsec_reflete_ssdlc_sem_prometer_samm_completo` com os asserts de Interfaces. Rodar o módulo → FAIL na descrição atual.

- [ ] **Step 2: Implementar** metadados + CURRICULO + README + `descricao` da rota conforme Interfaces.

- [ ] **Step 3: Rodar** `python3 -m unittest testes.test_rotas_sugeridas testes.test_curriculo testes.test_devsecops_conteudo` → PASS.

- [ ] **Step 4: Compilar portal** `./_geradores/gerar.sh portal` → OK; confirmar no `index.html` que a rota `appsec` mostra a nova descrição (ou título do painel coerente).

- [ ] **Step 5: Commit** (se pedido) `docs(devsecops): alinha metadados e rota AppSec ao SSDLC/SLSA`.

---

### Task 3: Rebuild final e verificação residual

**Files:**
- Regenerados: `DevSecOps-e-CI-CD/treinamento-*.html`, `index.html` se stale

- [ ] **Step 1: Compilar** `./_geradores/gerar.sh DevSecOps-e-CI-CD` (e portal se necessário).

- [ ] **Step 2: Grep residual**
  - Corpo: `id="ssdlc-samm"`, `id="secrets-no-pipeline"`, `SLSA`, `VEX`, `SSDLC`, `SAMM`.
  - `data-tipo="laboratorio"` / `lab-box` ausentes no corpo 22.
  - `index_dados` / portal: descrição appsec sem `SAMM completo`.

- [ ] **Step 3: Suíte amostral**  
  `python3 -m unittest testes.test_devsecops_conteudo testes.test_rotas_sugeridas testes.test_curriculo testes.test_corpos_sem_laboratorio testes.test_marca` → PASS.

- [ ] **Step 4: Commit** (se pedido) `build: regenera DevSecOps e portal com SSDLC/supply chain`.

---

## Spec coverage (self-review)

| Spec | Task |
|---|---|
| §3.1 corpo (ordem, seções, densidade) | 1 |
| §3.2 metadados/CURRICULO/README | 2 |
| §3.3 rota appsec | 2 |
| §3.4 testes + rebuild | 1–3 |
| Não objetivos / anti-objetivos | Review Focus + Global Constraints |
