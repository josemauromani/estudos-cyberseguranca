# Design Spec: Segurança em Mobile e MDM (módulo 63)

**Data:** 2026-11-09  
**Status:** Aprovada pelo usuário (2026-11-09)  
**Repositório:** `estudos_cyberseguranca` (Mapa da Cibersegurança)  
**Referência Metodológica:** Superpowers Spec-Driven Development (SDD)  
**Origem:** Gaps P0 da análise profunda (Mobile + MDM/UEM); ciclo seguinte a DevSecOps SSDLC/SLSA/secrets (`2026-11-09-devsecops-ssdlc-supply-chain`).

---

## 1. Propósito e Entendimento

O catálogo cobre web/API, endpoint (EDR) e identidade, mas **MASVS/MASTG, riscos Android/iOS e MDM/UEM/BYOD estão quase ausentes** — gap P0 para AppSec, Pix e frota corporativa. A análise marcou o tema como candidato a **módulo novo (63)**.

Este ciclo cria o **módulo 63** completo (densidade C), na Trilha 5, e encaixa o slug nas rotas `appsec` e `analista_si` — sem labs JS e sem abrir KMS/HSM ou CI neste pacote.

### Decisões do usuário (brainstorming)

| Decisão | Escolha |
|---|---|
| Fatia | **A** — AppSec mobile (MASVS/MASTG + Android/iOS) **+** MDM/UEM/BYOD no mesmo módulo |
| Profundidade | **C** — quase-curso: A+B + lab mental de revisão/pentest + matriz de controles por perfil |
| Trilha | **A** — Trilha 5 (Especialidades & Fronteiras) |
| Rotas | **B** — incluir em `appsec` e `analista_si` (não em `blue_soc` neste ciclo) |
| Ordem pedagógica | **A** — AppSec mobile → MDM/UEM/BYOD → matriz de controles |
| Abordagem | **1** — um módulo 63 denso + atualização de catálogo 62→63 + duas rotas |

### Critérios de sucesso

- Existe slug `Seguranca-em-Mobile-e-MDM` com corpo `_geradores/seguranca_em_mobile_e_mdm_body.html` e HTML compilado em `Seguranca-em-Mobile-e-MDM/`.
- Seções de teoria na ordem: `introducao` → `masvs-riscos` → `android-ios` → `lab-mental-mobile` → `mdm-uem-byod` → `matriz-controles` → checklist → quiz → fatos; `validar_corpo` sem erros.
- Densidade C: MASVS/MASTG, riscos Android/iOS concretos, percurso guiado (lab mental **sem** `data-tipo="laboratorio"`), MDM vs UEM, COPE/BYOD/CYOD, matriz perfil × risco × controle.
- Catálogo passa a **63** módulos (`ESTUDOS_DADOS`, CURRICULO, README, testes que pinam 62).
- `ROTAS_PERFIL`: `appsec` inclui o slug após `Seguranca-em-APIs`; `analista_si` após `Seguranca-em-Endpoints-EDR`; descrições citam mobile/MDM sem prometer “pentest mobile completo” nem fornecedor MDM.
- Testes de conteúdo + rotas/currículo + rebuild do módulo e portal passam.
- Zero `laboratorio` / `lab-box` no corpo 63.

### Não objetivos

- Laboratórios/simuladores JS; reativar contrato `laboratorio`.
- KMS/HSM como tema próprio; CI byte-a-byte; IDs estáveis de quiz em massa.
- Incluir o 63 em `blue_soc` (pode ser ciclo futuro).
- Módulo 64 separado (AppSec mobile vs MDM).
- Mermaid/`chrome-headless-shell` como bloqueio de ambiente.

### Anti-objetivos

- Usar `data-tipo="laboratorio"` no “lab mental”.
- Prometer pentest mobile completo, certificação MASVS ou produto MDM específico.
- Diluir o módulo em seções genéricas sem matriz e sem percurso guiado (viola densidade C).
- Manter textos “62 módulos” após o registro do 63.

---

## 2. Abordagens Consideradas

1. **Módulo 63 único na T5 + rotas appsec/analista_si** *(escolhida)* — fecha o P0 mobile num pacote; catálogo 63.
2. MDM antes do AppSec no corpo — conflita com a ordem pedagógica A.
3. Dois módulos (63 + 64) — fora da fatia A; estoura o ciclo.

---

## 3. Design

### 3.1 Corpo do estudo 63

**Arquivo:** `_geradores/seguranca_em_mobile_e_mdm_body.html`  
**Slug / pasta:** `Seguranca-em-Mobile-e-MDM`  
**Trilha:** 5 · **NIST:** Protect · **Tempo alvo:** 70–90 min · **Nível:** intermediário

**Ordem das seções de teoria:**

1. **`introducao`** — por que mobile + frota; superfície Pix/BYOD; mapa do módulo; remissões 04/08/10/12/13/41.
2. **`masvs-riscos`** — MASVS como régua; MASTG como orientação de teste; OWASP Mobile Top 10 em visão prática (não checklist íntegro de todas as L-levels).
3. **`android-ios`** — armazenamento sensível, IPC/deeplinks, permissões, Network Security Config / ATS, Keystore/Keychain; contrastes úteis sem tutorial de IDE.
4. **`lab-mental-mobile`** — percurso guiado de revisão/pentest (teoria + callouts + passos numerados); **`data-tipo="teoria"`**.
5. **`mdm-uem-byod`** — MDM vs UEM; COPE / BYOD / CYOD; enrollment, compliance, remote wipe; ponte Zero Trust / Conditional Access / EDR.
6. **`matriz-controles`** — tabela perfil de dispositivo × risco × controle (app + dispositivo/política).

**Checklist / questões / referências:** cobrir MASVS, riscos Android/iOS, lab mental (o que verificar), MDM/BYOD e uso da matriz; refs OWASP MASVS/MASTG, Mobile Top 10, NIST/orientações de MDM em alto nível (sem vendor lock).

**Tom:** pt-BR; densidade C; zero simulador.

### 3.2 Catálogo e documentação

- Entrada em `ESTUDOS_DADOS["Seguranca-em-Mobile-e-MDM"]` (titulo, subtitulo, fatos, tempo ≥ 70, carreiras AppSec & DevSecOps / Blue Team conforme couber).
- Entrada em `NECESSIDADES` (desafio prático: app mobile / BYOD).
- `_geradores/CURRICULO.md`: contagem 63; bloco `#### 63. Seguranca-em-Mobile-e-MDM`; Trilha 5 atualizada (módulos 21–24 **e 63** ou redação equivalente clara).
- `README.md`: tabela + “63 módulos”.
- Pasta do estudo + HTML gerado via `gerar.sh`.

### 3.3 Rotas

- **`appsec`:** inserir `Seguranca-em-Mobile-e-MDM` imediatamente após `Seguranca-em-APIs`; ajustar `descricao` (mobile/MASVS/MDM) sem “pentest mobile completo”.
- **`analista_si`:** inserir após `Seguranca-em-Endpoints-EDR`; descrição menciona MDM/BYOD se ainda não cobrir.
- Demais rotas: **inalteradas** neste ciclo.
- `test_rotas_sugeridas.py` / `test_curriculo.py`: asserts de sequência e contagem 63.

### 3.4 Testes e rebuild

- Criar `_geradores/testes/test_mobile_mdm_conteudo.py` (ordem via `extrair_secoes`; menções MASVS, MDM, BYOD, Android, iOS; `validar_corpo`; sem lab).
- Atualizar asserts hardcoded de 62 → 63 onde forem contagem de catálogo (não “número do estudo 62”).
- `./_geradores/gerar.sh Seguranca-em-Mobile-e-MDM` e portal; aviso Mermaid de ambiente não bloqueia se o HTML foi gerado.

---

## 4. Plano de implementação (alto nível)

1. RED: `test_mobile_mdm_conteudo` + ajustes de contagem/rotas que falham.  
2. Corpo HTML do 63 (seções na ordem).  
3. `ESTUDOS_DADOS` + necessidade + CURRICULO/README.  
4. Rotas `appsec` / `analista_si` + testes.  
5. Rebuild + suíte amostral + grep residual.

Commits só se o usuário pedir.

---

## 5. Self-review da spec

- [x] Sem placeholders TBD/TODO no desenho normativo.  
- [x] Decisões do brainstorming refletidas (fatia A, profundidade C, T5, rotas B, ordem A, abordagem 1).  
- [x] Anti-objetivo lab mental ≠ `laboratorio` explícito.  
- [x] Escopo não inclui KMS/HSM, blue_soc, labs JS.  
- [x] Contagem 62→63 tratada como mudança de produto, não detalhe esquecido.
