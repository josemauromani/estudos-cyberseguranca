# Design Spec: DevSecOps — SSDLC, Supply Chain e Secrets

**Data:** 2026-11-09  
**Status:** Aprovada pelo usuário (2026-11-09)  
**Repositório:** `estudos_cyberseguranca` (Mapa da Cibersegurança)  
**Referência Metodológica:** Superpowers Spec-Driven Development (SDD)  
**Origem:** Gaps P0 da análise profunda (SSDLC/SAMM, SBOM/SLSA, secrets); ciclo seguinte a identidade federada / rotas CISO–AppSec.

---

## 1. Propósito e Entendimento

O estudo 22 (DevSecOps-e-CI-CD) já cobre Shift-Left, SAST/DAST/SCA, SBOM básico, containers/Cosign e quality gates, mas é curto (~17 KB, duas seções de teoria). SSDLC aparece de passagem; SAMM/Champions, SLSA/VEX e tratamento denso de secrets no pipeline estão ausentes ou só em callout. A rota `appsec` no portal já existe, porém a descrição evita prometer SSDLC.

Este ciclo densifica o **mesmo** estudo 22 (pacote completo, densidade B, estrutura híbrida) e alinha metadados/docs/rota AppSec — sem labs e sem módulo 63.

### Decisões do usuário (brainstorming)

| Decisão | Escolha |
|---|---|
| Fatia do ciclo | **A** — SSDLC + SAMM/Champions + SBOM/SLSA/VEX + secrets no pipeline |
| Profundidade | **B** — denso (diagramas, SLSA 0–4, políticas de gate, anti-padrões de secrets) |
| Estrutura no corpo | **C** — expandir `cadeia`; criar `ssdlc-samm` e `secrets-no-pipeline` |
| Abordagem | **1** — ordem `introducao` → `ssdlc-samm` → `cadeia` → `secrets-no-pipeline` + checklist/quiz/refs; atualizar rota `appsec` |

### Critérios de sucesso

- Corpo `devsecops_e_ci_cd_body.html` com seções na ordem: `introducao` → `ssdlc-samm` → `cadeia` → `secrets-no-pipeline` → checklist → quiz → fatos; `validar_corpo` sem erros.
- Conteúdo denso: SSDLC/Champion/SAMM (régua, não checklist íntegro); SLSA 0–4, VEX, provenance/in-toto com assinatura; secrets (histórico, revogação, cofre/OIDC no CI, anti-padrões).
- Metadados + CURRICULO (+ README se título mudar) refletem o pacote.
- Descrição da rota `appsec` cita SSDLC/supply chain/secrets do 22 **sem** “SAMM completo”.
- Testes de conteúdo + rebuild do módulo (e portal se rota/metadados mudarem) passam.
- Sem `data-tipo="laboratorio"` / labs reintroduzidos.

### Não objetivos

- Módulo 63 (AppSec, Mobile, Secrets/KMS como estudo separado).
- KMS/HSM como tema próprio (só cofre/OIDC operacional no CI).
- Labs/simuladores; renumerar o catálogo (continua 62).
- Reescrever OWASP/web avançado ou threat modeling além do leve no SSDLC.

### Anti-objetivos

- Prometer “SAMM completo” ou certificação SAMM na rota/docs.
- Fundir secrets e SLSA numa única seção genérica (viola a estrutura C/abordagem 1).
- Duplicar tratado de containers do estudo 50/51 no 22 além do já presente.

---

## 2. Abordagens Consideradas

1. **Ordem pedagógica SSDLC → cadeia → secrets** *(escolhida)* — narrativa clara; secrets com seção própria.
2. Só uma seção nova SSDLC; secrets/SLSA só dentro de `cadeia` — menos seções, conflita com C.
3. Módulo 63 AppSec + 22 só pipeline — fora do “tudo no 22”.

---

## 3. Design

### 3.1 Corpo do estudo 22

**Arquivo:** `_geradores/devsecops_e_ci_cd_body.html`

**Ordem das seções de teoria:**

1. **`introducao`** — manter Shift-Left, tabela de ferramentas e workflow; ponte explícita às seções seguintes (sem duplicar SAMM/SLSA).
2. **`ssdlc-samm`** (nova) — fases SSDLC; Security Champion; OWASP SAMM como régua de maturidade; Mermaid do ciclo ligado à esteira.
3. **`cadeia`** (expandir) — manter SBOM/EPSS/KEV/containers/Cosign/gates; acrescentar SLSA 0–4, VEX, in-toto/provenance; políticas baseline vs break-the-build.
4. **`secrets-no-pipeline`** (nova) — scan MR + histórico; revogar ≠ apagar; cofre/OIDC no CI; anti-padrões (`ENV`/`ARG`, logs, tokens longos); absorver/expandir o callout atual de segredo vazado.

**Checklist / questões / referências:** itens e questões novos para SSDLC/Champion, SLSA/VEX e secrets; refs OWASP SAMM, SLSA, CycloneDX/SPDX, práticas de secrets em CI.

**Tom:** pt-BR; densidade B; zero simulador.

### 3.2 Metadados e documentação

- `ESTUDOS_DADOS["DevSecOps-e-CI-CD"]`: título/subtitulo/`fatos` incluindo SSDLC, SLSA e secrets.
- `_geradores/CURRICULO.md` — bloco do módulo 22.
- `README.md` — célula de título do módulo 22 se o título mudar.

### 3.3 Rota `appsec`

Em `ROTAS_PERFIL`, manter a lista de módulos; reescrever `descricao` para refletir SSDLC, SBOM/SLSA e higiene de secrets **no estudo DevSecOps**, sem “SAMM completo”.

### 3.4 Testes e verificação

- Criar `_geradores/testes/test_devsecops_conteudo.py` (ordem dos ids; menções SSDLC/SAMM/SLSA/VEX/secrets; checklist/questões mínimos; `validar_corpo`).
- Assert da descrição `appsec` (SSDLC ou equivalente; ausência de promessa “SAMM completo”).
- `./_geradores/gerar.sh DevSecOps-e-CI-CD` e portal se necessário.
- Mermaid/`chrome-headless-shell` por ambiente: não bloqueia se não for regressão deste ciclo.

### 3.5 Marca

- Marca: nunca “Estudos de/em Cibersegurança”, “José Mauro”, “Brandão”, “Stelling” (`test_marca`).

---

## 4. Ordem de implementação (orientação ao plano)

1. Testes RED de conteúdo + implementação do corpo 22.  
2. Metadados, CURRICULO/README e descrição da rota `appsec` + testes de rota.  
3. Rebuild + grep residual + suíte amostral.

---

## 5. Ciclos seguintes (fora desta spec)

- Mobile + MDM/UEM (candidato a módulo 63).  
- Secrets/KMS/HSM como consolidação ou módulo.  
- Threat modeling além de STRIDE; web avançado / purple / ADCS.  
- Labs redesenhados do zero.
