# Identidade Federada e Rotas CISO/AppSec: Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Densificar SAML/SSO/SCIM no estudo Autenticação e IAM, acrescentar ponte de federação no estudo Identidade Híbrida, e expor rotas `ciso` e `appsec` no portal.

**Architecture:** Conteúdo em `*_body.html` (contrato atual: teoria/checklist/questões/referências); metadados e `ROTAS_PERFIL` em `index_dados.py`; CURRICULO/README espelham título e §5 das rotas; rebuild via `gerar.sh`.

**Tech Stack:** Python 3 (`unittest`), HTML/CSS/JS vanilla, Mermaid nos corpos, `_geradores/gerar.sh`, `_geradores/montar.py`.

**Spec:** `docs/superpowers/specs/2026-11-06-identidade-federada-rotas-ciso-appsec-design.md`

## Global Constraints

- Textos em pt-BR; marca: nunca “Estudos de/em Cibersegurança”, “José Mauro”, “Brandão”, “Stelling” (`test_marca`).
- Catálogo permanece em **62** módulos; sem módulo 63; sem labs/simuladores.
- Seções SAML e SCIM são **irmãs** de `federacao-oauth-oidc` (não fundir OIDC e SAML).
- Ordem no 04: `… → federacao-oauth-oidc → saml-sso → scim-provisionamento → anatomia-jwt → …`.
- Rotas: ids `ciso` e `appsec`; ícones `👔` e `🧩`; inserção **após `grc`, antes de `pericia`**.
- Rota AppSec **não** promete SSDLC/SAMM como já entregue no DevSecOps.
- Commits só se o usuário pedir; mensagens no estilo do repo.
- Testes: de `_geradores/`, `python3 -m unittest testes.<modulo>`. Mermaid/`chrome-headless-shell` por ambiente não bloqueia se não for regressão deste ciclo.

## File map

| Área | Arquivos |
|---|---|
| Corpo 04 | `_geradores/autenticacao_e_iam_body.html` → `Autenticacao-e-IAM/treinamento-*.html` |
| Corpo 41 | `_geradores/identidade_hibrida_e_nuvem_body.html` → `Identidade-Hibrida-e-Nuvem/treinamento-*.html` |
| Metadados/rotas | `_geradores/index_dados.py` |
| Docs | `_geradores/CURRICULO.md` (§3 módulo 04 + §5 rotas + intro de perfis), `README.md` (linha do módulo 04) |
| Testes | `_geradores/testes/test_autenticacao_iam_conteudo.py` (criar), `_geradores/testes/test_identidade_hibrida_conteudo.py` (criar), `test_rotas_sugeridas.py`, `test_curriculo.py` se necessário |
| Portal | `index.html` via `gerar.sh` |

## Review Focus

1. **Ordem das seções no 04:** `saml-sso` e `scim-provisionamento` entre OIDC e JWT — pinar ids na ordem em `extrair_secoes`. Task 1.
2. **Ponte sem duplicar protocolo:** 41 cita SAML/Entra/AD FS e remete ao 04; não reexplica bindings/NameID. Task 2.
3. **Slugs das rotas existem:** todo módulo em `ciso`/`appsec` ∈ `ESTUDOS_DADOS`. Task 3.
4. **CURRICULO §5 = `ROTAS_PERFIL`:** sequências numéricas (`01 -> …`) batem com `numero(slug)`. Task 3.
5. **Descrição AppSec honesta:** copy da rota não afirma SSDLC/SAMM já cobertos. Task 3.

---

### Task 1: Conteúdo denso SAML/SCIM no estudo 04

**Files:**
- Create: `_geradores/testes/test_autenticacao_iam_conteudo.py`
- Modify: `_geradores/autenticacao_e_iam_body.html`
- Modify: `_geradores/index_dados.py` (`ESTUDOS_DADOS["Autenticacao-e-IAM"]` — `titulo`, `subtitulo`, `fatos`)
- Modify: `_geradores/CURRICULO.md` (bloco `#### 04. Autenticacao-e-IAM`)
- Modify: `README.md` (célula de título do módulo 04 na tabela)

**Interfaces:**
- Produces: seções `id="saml-sso"` e `id="scim-provisionamento"` com `data-tipo="teoria"`; checklist ≥3 itens novos sobre SAML/SCIM; ≥3 questões novas; referências SAML/SCIM; `validar_corpo` ok; título metadados inclui SAML (ex.: `"Senhas, MFA, OAuth 2.0, SAML, JWT e RBAC"`).

- [x] **Step 1: Teste (RED).** Criar `test_autenticacao_iam_conteudo.py` que:
  - carrega o corpo; `validar_corpo` sem erros;
  - `ids = [s.id for s in extrair_secoes(html)]` contém `saml-sso` e `scim-provisionamento`;
  - índice: `ids.index("federacao-oauth-oidc") < ids.index("saml-sso") < ids.index("scim-provisionamento") < ids.index("anatomia-jwt")`;
  - `"SAML" in html` e `"SCIM" in html`;
  - checklist: pelo menos 3 labels contendo (casefold) um de `saml`, `scim`, `acs`, `asserção`/`assert`;
  - questões: pelo menos 3 `quiz-item` cujo texto casefold menciona `saml` ou `scim`.
  Rodar: `python3 -m unittest testes.test_autenticacao_iam_conteudo` → FAIL.

- [x] **Step 2: Implementar** corpo + metadados + CURRICULO §3.04 + README conforme Interfaces e spec §3.1 (densidade B: bindings, NameID, metadados, SAML×OIDC, pitfalls, Mermaid SP-initiated; SCIM/JML). Sem `<script>` de lab.

- [x] **Step 3: Rodar** `python3 -m unittest testes.test_autenticacao_iam_conteudo testes.test_contrato testes.test_marca` → PASS.

- [x] **Step 4: Compilar** `./_geradores/gerar.sh Autenticacao-e-IAM` → OK.

- [x] **Step 5: Commit** (se pedido) `feat(iam): adiciona SAML/SSO e SCIM ao estudo Autenticacao-e-IAM`.

---

### Task 2: Ponte de federação no estudo 41

**Files:**
- Create: `_geradores/testes/test_identidade_hibrida_conteudo.py`
- Modify: `_geradores/identidade_hibrida_e_nuvem_body.html`

**Interfaces:**
- Consumes: existência do estudo 04 como destino da remissão (slug/título “Autenticação e IAM” / `Autenticacao-e-IAM`).
- Produces: seção `id="federacao-saml-entra"` `data-tipo="teoria"`; texto com SAML + (Entra ou AD FS); remissão ao 04; +1–2 checklist; +1 questão; **não** contém tutorial de bindings SAML (ausência de subtítulo/heading “Binding” / “NameID” como tópico próprio — pode citar de passagem).

- [x] **Step 1: Teste (RED).** Arquivo novo: `validar_corpo` ok; `federacao-saml-entra` em ids; `"SAML" in html`; remissão: `"Autenticacao-e-IAM" in html` **ou** frase casefold com `autenticação e iam` / `estudo`+`iam`; checklist ≥1 item com `saml` ou `federa`; ≥1 `quiz-item` com `saml` ou `federa`. Rodar → FAIL.

- [x] **Step 2: Implementar** seção curta + checklist/questão conforme Interfaces e spec §3.2.

- [x] **Step 3: Rodar** `python3 -m unittest testes.test_identidade_hibrida_conteudo` → PASS.

- [x] **Step 4: Compilar** `./_geradores/gerar.sh Identidade-Hibrida-e-Nuvem` → OK.

- [x] **Step 5: Commit** (se pedido) `feat(identidade): ponte SAML/Entra remetendo ao IAM`.

---

### Task 3: Rotas `ciso` e `appsec` no portal + CURRICULO §5

**Files:**
- Modify: `_geradores/index_dados.py` (`ROTAS_PERFIL`)
- Modify: `_geradores/CURRICULO.md` (§5 + linha de perfis na intro se listar só as 6 antigas)
- Modify: `_geradores/testes/test_rotas_sugeridas.py` (`IDS_ESPERADOS`, rename/ajuste de `test_seis_rotas_com_ids_e_campos`)

**Interfaces:**
- Produces: `ROTAS_PERFIL` com ids na ordem  
  `["blue_soc", "red_team", "devsecops_cloud", "grc", "ciso", "appsec", "pericia", "analista_si"]`.
- Entrada `ciso`: `nome="CISO / Liderança de Segurança"`, `icone="👔"`, `descricao` focada em liderança/governança (sem SOC ofensivo), `modulos` exatamente a lista da spec §3.3.
- Entrada `appsec`: `nome="AppSec / Segurança de Aplicações"`, `icone="🧩"`, `descricao` que **não** contenha `SSDLC` nem `SAMM` como promessa cumprida; `modulos` exatamente a lista da spec §3.3.
- CURRICULO §5: itens numerados 1–8 com sequências:
  - ciso: `` `01 -> 08 -> 04 -> 40 -> 09 -> 25 -> 26 -> 58 -> 57 -> 28 -> 43 -> 44 -> 59 -> 60` ``
  - appsec: `` `01 -> 61 -> 03 -> 04 -> 35 -> 12 -> 13 -> 21 -> 41 -> 22 -> 50 -> 51 -> 52 -> 53` ``  
  (inserir como rotas 5 e 6; renumerar Perícia→7 e Analista SI→8).

- [x] **Step 1: Teste (RED).** Em `test_rotas_sugeridas.py`: atualizar `IDS_ESPERADOS` para as 8 ids; renomear teste de “seis” para “oito” rotas. Acrescentar:
  - `test_rota_ciso_modulos` — `ROTAS_PERFIL` entry `ciso` tem os 14 slugs da spec na ordem;
  - `test_rota_appsec_modulos` — idem para `appsec`;
  - `test_descricao_appsec_nao_promete_ssdlc` — `"SSDLC" not in` descrição e `"SAMM" not in` descrição (casefold ok).
  Rodar `python3 -m unittest testes.test_rotas_sugeridas` → FAIL (ids/CURRICULO).

- [x] **Step 2: Implementar** `ROTAS_PERFIL` + CURRICULO §5 (+ intro de perfis se necessário) conforme Interfaces.

- [x] **Step 3: Rodar** `python3 -m unittest testes.test_rotas_sugeridas testes.test_curriculo testes.test_portal` → PASS.

- [x] **Step 4: Compilar portal** `./_geradores/gerar.sh portal` → OK; grep no `index.html`: `data-rota="ciso"` e `data-rota="appsec"`.

- [x] **Step 5: Commit** (se pedido) `feat(portal): adiciona rotas CISO e AppSec`.

---

### Task 4: Rebuild final e verificação residual

**Files:**
- Regenerados: treinamentos 04/41 (se ainda stale), `index.html`

- [x] **Step 1: Compilar** `./_geradores/gerar.sh Autenticacao-e-IAM` e `./_geradores/gerar.sh Identidade-Hibrida-e-Nuvem` (ou `todos` se preferir uma passada).

- [x] **Step 2: Grep residual**
  - Em `_geradores/autenticacao_e_iam_body.html`: `SAML` e `SCIM` presentes; `id="saml-sso"` e `id="scim-provisionamento"`.
  - Em `_geradores/identidade_hibrida_e_nuvem_body.html`: `id="federacao-saml-entra"` e `SAML`.
  - Em `index.html`: `ciso` e `appsec` nas rotas.
  - Zero `data-tipo="laboratorio"` / `.lab-box` reintroduzidos nestes corpos.

- [x] **Step 3: Suíte amostral**  
  `python3 -m unittest testes.test_autenticacao_iam_conteudo testes.test_identidade_hibrida_conteudo testes.test_rotas_sugeridas testes.test_curriculo testes.test_corpos_sem_laboratorio testes.test_marca` → PASS.

- [x] **Step 4: Commit** (se pedido) `build: regenera IAM, Identidade Híbrida e portal com rotas CISO/AppSec`.

---

## Spec coverage (self-review)

| Spec | Task |
|---|---|
| §3.1 saml-sso / scim + checklist/questões/refs + metadados 04 | 1 |
| §3.2 ponte 41 | 2 |
| §3.3 rotas ciso/appsec + ordem após grc | 3 |
| §3.4 testes + rebuild | 1–4 |
| Não objetivos (63, SSDLC profundo, labs) | fora |
| Review Focus 1–5 | pinados nas Tasks 1–3 |
