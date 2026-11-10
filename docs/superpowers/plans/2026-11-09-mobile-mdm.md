# Mobile + MDM (módulo 63): Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar o módulo 63 `Seguranca-em-Mobile-e-MDM` (MASVS/MASTG, Android/iOS, lab mental, MDM/UEM/BYOD, matriz de controles) na Trilha 5 e incluí-lo nas rotas `appsec` e `analista_si`, elevando o catálogo de 62 para 63.

**Architecture:** Novo `*_body.html` no contrato teoria/checklist/questões/referências; registro em `estudos.txt` + `ESTUDOS_DADOS` (número = índice+1 → 63); rotas e docs; rebuild via `gerar.sh`.

**Tech Stack:** Python 3 (`unittest`), HTML/CSS/JS vanilla, Mermaid, `_geradores/gerar.sh`, `_geradores/montar.py`.

**Spec:** `docs/superpowers/specs/2026-11-09-mobile-mdm-design.md`

## Global Constraints

- Textos em pt-BR; marca: nunca “Estudos de/em Cibersegurança”, “José Mauro”, “Brandão”, “Stelling” (`test_marca`).
- Catálogo passa a **63** módulos; slug `Seguranca-em-Mobile-e-MDM`; Trilha **5**; NIST **Protect**.
- Ordem das teorias: `introducao` → `masvs-riscos` → `android-ios` → `lab-mental-mobile` → `mdm-uem-byod` → `matriz-controles`.
- Densidade C; `lab-mental-mobile` é **`data-tipo="teoria"`** — proibido `laboratorio` / `lab-box`.
- Rotas: só `appsec` (após `Seguranca-em-APIs`) e `analista_si` (após `Seguranca-em-Endpoints-EDR`); sem `blue_soc`.
- Descrições de rota: citar mobile/MDM; **não** “pentest mobile completo”; sem vendor MDM.
- Commits só se o usuário pedir; mensagens no estilo do repo.
- Testes: de `_geradores/`, `python3 -m unittest testes.<modulo>`. Mermaid/`chrome-headless-shell` de ambiente não bloqueia se o HTML foi gerado.

## File map

| Área | Arquivos |
|---|---|
| Corpo 63 | Create: `_geradores/seguranca_em_mobile_e_mdm_body.html` → `Seguranca-em-Mobile-e-MDM/treinamento-*.html` |
| Catálogo | `_geradores/estudos.txt` (linha + header 63), `_geradores/index_dados.py` (`ESTUDOS_DADOS`, `NECESSIDADES`, `ROTAS_PERFIL`) |
| Docs | `_geradores/CURRICULO.md`, `README.md`, `_geradores/GUIA-DO-AUTOR.md` (contagem 63) |
| Testes | Create: `_geradores/testes/test_mobile_mdm_conteudo.py`; Modify: `test_rotas_sugeridas.py`, `test_curriculo.py` |
| Portal | `index.html` via `gerar.sh` |

## Review Focus

1. **Lab mental ≠ lab:** `lab-mental-mobile` com `data-tipo="teoria"`; zero `laboratorio`/`lab-box`. Task 1.
2. **Ordem das seções:** ids na ordem da spec; pinar com `extrair_secoes`. Task 1.
3. **Número 63:** append em `ESTUDOS_DADOS`/`estudos.txt` (não inserir no meio e renumerar 61/62). Task 2.
4. **Rotas:** `appsec` após APIs; `analista_si` após EDR; CURRICULO §5 com `63` nas sequências. Task 3.
5. **Contagem:** nenhum “62 módulos” restante em README/CURRICULO/GUIA (e header de `estudos.txt`). Tasks 2–4.

---

### Task 1: Corpo do estudo 63

**Files:**
- Create: `_geradores/testes/test_mobile_mdm_conteudo.py`
- Create: `_geradores/seguranca_em_mobile_e_mdm_body.html`

**Interfaces:**
- Produces: `article[data-slug="seguranca-em-mobile-e-mdm"]` (ou slug canônico alinhado ao contrato do montador — usar o mesmo padrão dos outros corpos, tipicamente kebab do nome).
- Seções teoria com ids: `introducao`, `masvs-riscos`, `android-ios`, `lab-mental-mobile`, `mdm-uem-byod`, `matriz-controles` — nesta ordem relativa.
- `lab-mental-mobile` tem `data-tipo="teoria"`.
- HTML contém (casefold onde indicado): `MASVS`, `MASTG` ou `mastg`, `MDM`, `BYOD`, `Android`, `iOS` (ou `ios`).
- Checklist ≥4 itens cobrindo MASVS/MDM/BYOD/matriz; quiz ≥4 itens com temas mobile/MDM/MASVS; seção `fatos` + referências OWASP MASVS/MASTG.
- `validar_corpo(html, stem)` sem erros; sem lab.

- [ ] **Step 1: Teste (RED).** Criar `test_mobile_mdm_conteudo.py` espelhando o estilo de `test_devsecops_conteudo.py` (ordem, menções, checklist/quiz, `validar_corpo`, sem lab).  
  Rodar: `python3 -m unittest testes.test_mobile_mdm_conteudo` → FAIL (arquivo ausente ou asserts).

- [ ] **Step 2: Implementar** o corpo completo conforme spec §3.1 (densidade C; Mermaid opcional na intro ou MDM; matriz em tabela; lab mental com passos numerados).

- [ ] **Step 3: Rodar** `python3 -m unittest testes.test_mobile_mdm_conteudo testes.test_marca` → PASS.

- [ ] **Step 4: Commit** (se pedido) `feat(mobile): adiciona corpo do estudo 63 Mobile/MDM`.

---

### Task 2: Catálogo (estudos.txt + ESTUDOS_DADOS + necessidade)

**Files:**
- Modify: `_geradores/estudos.txt` (header “63 Módulos”; append linha do slug)
- Modify: `_geradores/index_dados.py` (`ESTUDOS_DADOS` append; `NECESSIDADES` +1 desafio)

**Interfaces:**
- Linha `estudos.txt` (7 campos):  
  `Seguranca-em-Mobile-e-MDM|<titulo_curto>|Seguranca-em-Mobile-e-MDM|treinamento-seguranca-em-mobile-e-mdm.html|5|#0891B2|Protect`  
  com `titulo_curto` alinhado ao `titulo` de `ESTUDOS_DADOS` (ex.: `MASVS, Android/iOS, MDM e BYOD`).
- `ESTUDOS_DADOS["Seguranca-em-Mobile-e-MDM"]` **último** no dict (número 63): `trilha=5`, `nist="Protect"`, `tempo_minutos` ≥ 70, `titulo`/`subtitulo`/`fatos` citam MASVS, MDM/BYOD e Android/iOS.
- `NECESSIDADES`: um item com `slug` = `Seguranca-em-Mobile-e-MDM` (ex.: app mobile / frota BYOD).
- `len(ESTUDOS_DADOS) == 63` e bate com linhas de `estudos.txt` (`test_index` / `test_curriculo`).

- [ ] **Step 1: Teste (RED).** Em `test_curriculo.py`, alterar `test_tamanho_da_grade` para esperar **63** (e `test_trilha_14_documentada` / asserts de “62 módulos” → “63 módulos” nos docs — pode falhar até Task 3 se docs ainda dizem 62; neste step pelo menos o assert de `estudos.txt` length). Preferência: neste step só mudar o assert de `len(_linhas_catalogo())` para 63 e rodar → FAIL até append.

- [ ] **Step 2: Implementar** append em `estudos.txt` + `ESTUDOS_DADOS` + `NECESSIDADES`.

- [ ] **Step 3: Rodar** `python3 -m unittest testes.test_index testes.test_curriculo.TestCurriculo.test_tamanho_da_grade testes.test_curriculo.TestCurriculo.test_estudos_txt_formato_valido` → PASS no catálogo (demais asserts de README “63” podem ainda falhar — ok se isolados).

- [ ] **Step 4: Commit** (se pedido) `feat(catalogo): registra módulo 63 Seguranca-em-Mobile-e-MDM`.

---

### Task 3: Docs, rotas e testes de rota/currículo

**Files:**
- Modify: `_geradores/index_dados.py` (`ROTAS_PERFIL` `appsec` e `analista_si` + `descricao`)
- Modify: `_geradores/CURRICULO.md` (contagem 63; Trilha 5; `#### 63. ...`; §5 sequências AppSec e Analista SI com `63`)
- Modify: `README.md` (62→63; linha da tabela do módulo 63)
- Modify: `_geradores/GUIA-DO-AUTOR.md` (62→63 na intro)
- Modify: `_geradores/testes/test_rotas_sugeridas.py` (`APPSEC_MODULOS` + slug após APIs; asserts descrição)
- Modify: `_geradores/testes/test_curriculo.py` (asserts “63 módulos”)

**Interfaces:**
- `appsec["modulos"]`: `... Seguranca-em-APIs, Seguranca-em-Mobile-e-MDM, Seguranca-em-Nuvem ...`
- `analista_si["modulos"]`: `... Seguranca-em-Endpoints-EDR, Seguranca-em-Mobile-e-MDM, Protecao-de-Dados-e-Conteudo ...` (ou o que vier logo após EDR hoje — inserir imediatamente após EDR)
- CURRICULO AppSec: inserir `63` após `13` na sequência; Analista SI: inserir `63` após `10`.
- `descricao` appsec: casefold com `mobile` ou `masvs` ou `mdm`; **não** contém `pentest mobile completo`.
- `descricao` analista_si: casefold com `mdm` ou `byod` ou `mobile`.
- `APPSEC_MODULOS` no teste = lista atualizada.
- README/CURRICULO/GUIA: “63 módulos”; README tabela com linha **63**.

- [ ] **Step 1: Teste (RED).** Atualizar `APPSEC_MODULOS` e asserts de descrição; asserts curriculo 63. Rodar `test_rotas_sugeridas` / `test_curriculo` → FAIL onde dados/docs ainda velhos.

- [ ] **Step 2: Implementar** rotas + docs + descrições.

- [ ] **Step 3: Rodar** `python3 -m unittest testes.test_rotas_sugeridas testes.test_curriculo testes.test_mobile_mdm_conteudo` → PASS.

- [ ] **Step 4: Commit** (se pedido) `docs(mobile): CURRICULO/README e rotas appsec/analista_si com módulo 63`.

---

### Task 4: Rebuild e verificação residual

**Files:**
- Regenerados: `Seguranca-em-Mobile-e-MDM/treinamento-*.html`, `index.html`

- [ ] **Step 1: Compilar** `./_geradores/gerar.sh Seguranca-em-Mobile-e-MDM` → OK (Mermaid env ok se HTML gerado); portal atualizado.

- [ ] **Step 2: Grep residual**
  - Corpo: ids das 6 teorias; `MASVS`; `MDM`; `BYOD`; ausentes `data-tipo="laboratorio"` e `lab-box`.
  - Docs/portal: “63 módulos”; sem “62 módulos” em README/CURRICULO/GUIA/`estudos.txt` header.
  - Descrições de rota sem `pentest mobile completo`.

- [ ] **Step 3: Suíte amostral**  
  `python3 -m unittest testes.test_mobile_mdm_conteudo testes.test_rotas_sugeridas testes.test_curriculo testes.test_index testes.test_corpos_sem_laboratorio testes.test_marca` → PASS.

- [ ] **Step 4: Commit** (se pedido) `build: regenera estudo 63 Mobile/MDM e portal`.

---

## Spec coverage (self-review)

| Spec | Task |
|---|---|
| §3.1 corpo (ordem, densidade C, lab mental teoria) | 1 |
| §3.2 catálogo/docs | 2–3 |
| §3.3 rotas appsec/analista_si | 3 |
| §3.4 testes + rebuild | 1–4 |
| Não objetivos / anti-objetivos | Review Focus + Global Constraints |
