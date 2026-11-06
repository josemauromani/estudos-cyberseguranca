# Design Spec: Identidade Federada (SAML/SCIM) e Rotas CISO / AppSec

**Data:** 2026-11-06  
**Status:** Aguardando revisão do usuário  
**Repositório:** `estudos_cyberseguranca` (Mapa da Cibersegurança)  
**Referência Metodológica:** Superpowers Spec-Driven Development (SDD)  
**Origem:** Gaps P0 da análise profunda do Mapa; ciclo seguinte à remoção dos laboratórios (`2026-11-06-remocao-laboratorios`).

---

## 1. Propósito e Entendimento

O catálogo tem IAM forte em senhas/MFA/OAuth/OIDC/JWT/RBAC, mas **zero menções a SAML** e quase nada de SCIM — base de SSO corporativo. O portal tem seis rotas de perfil e **não** monta trajetória CISO nem AppSec, apesar dos módulos 59/60 e da trilha DevSecOps existirem.

Este ciclo fecha esse subprojeto de conteúdo P0: densificar federação clássica no estudo 04, ponte no 41, e duas rotas novas no portal — sem labs e sem módulo 63.

### Decisões do usuário (brainstorming)

| Decisão | Escolha |
|---|---|
| Fatia do P0 de conteúdo | **A** — identidade federada (04 + 41) + rotas no portal |
| Profundidade SAML/SCIM | **B** — denso (quase mini-módulo no 04): bindings, NameID, metadados, SAML×OIDC, troubleshooting + SCIM/JML |
| Rotas | **B** — `ciso` e `appsec` como entradas **separadas** em `ROTAS_PERFIL` |
| Abordagem | **1** — seção(ões) densas no 04 + ponte no 41 + duas rotas; catálogo permanece em 62 |

### Critérios de sucesso

- Corpo `autenticacao_e_iam_body.html` contém seções de teoria `saml-sso` e `scim-provisionamento` (irmãs de `federacao-oauth-oidc`, sem fundir OIDC e SAML); checklist, questões e referências do 04 cobrem o tema; `validar_corpo` sem erros.
- Corpo `identidade_hibrida_e_nuvem_body.html` contém seção curta de ponte federação Entra/AD FS → estudo 04; checklist/questão mínimos; sem duplicar o protocolo SAML.
- `ESTUDOS_DADOS` (e espelhos CURRICULO/README se pinarem título/conceitos) refletem SAML/SCIM no estudo IAM.
- `ROTAS_PERFIL` inclui `ciso` e `appsec` (8 rotas no total), só com slugs existentes; ordem: após `grc`, antes de `pericia`.
- Rebuild dos dois treinamentos + `index.html`; testes de rotas/currículo e asserts de conteúdo dos corpos passam.
- Grep: SAML presente no 04 e na ponte do 41.

### Não objetivos

- Módulo 63 (Mobile, Secrets, Federação como estudo separado).
- Aprofundar SSDLC/SAMM/SBOM/SLSA (ciclo AppSec/DevSecOps seguinte).
- Recriar laboratórios/simuladores.
- Renumerar trilhas ou alterar a contagem de 62 módulos.
- Push remoto; CI novo; IDs estáveis de quiz em massa.

### Anti-objetivos

- Misturar SAML dentro de `federacao-oauth-oidc` de forma que OIDC e SAML fiquem indistingíveis.
- Duplicar o tratado SAML no módulo 41.
- Incluir na rota `appsec` a expectativa de conteúdo SSDLC que ainda não existe no 22.
- Criar slugs de módulo inexistentes nas rotas.

---

## 2. Abordagens Consideradas

1. **Seção densa no 04 + ponte no 41 + duas rotas** *(escolhida)* — fecha SAML=0 com densidade B; portal ganha CISO/AppSec; 62 módulos.
2. Várias seções “quase-módulo” só de SAML no 04 com remanejamento pesado de OAuth — mais profundidade, maior risco de desbalancear o estudo.
3. Módulo 63 “Federação e Provisionamento” — isolamento limpo, mas fora da preferência por seções em módulos existentes e escopo maior.

---

## 3. Design

### 3.1 Estudo 04 — Autenticação e IAM

**Arquivo:** `_geradores/autenticacao_e_iam_body.html`

**Ordem das seções de teoria (relevante):**  
`pilares-iam` → `senhas-e-mfa` → `federacao-oauth-oidc` → **`saml-sso`** → **`scim-provisionamento`** → `anatomia-jwt` → `modelos-controle-acesso` → checklist → questões → referências.

**`saml-sso` (teoria):** SP/IdP; asserção (Subject, Conditions, AttributeStatement); bindings (Redirect, POST, Artifact em visão prática); metadados XML; NameID; assinatura/criptografia da asserção; comparação SAML × OIDC (quando usar cada um); pitfalls (clock skew, ACS, Audience, certificado expirado, asserção sem assinatura); diagrama Mermaid do fluxo SP-initiated.

**`scim-provisionamento` (teoria):** SCIM 2.0 em alto nível; JML (joiner-mover-leaver); mapeamento de atributos; desprovisionamento vs apenas desligar SSO; relação IdP/HRIS — sem virar RFC linha a linha.

**Checklist:** acrescentar 3–5 itens (assinatura/Audience/ACS, rotação de certificado SAML, SCIM no offboarding, escolha SAML×OIDC na integração).

**Questões:** acrescentar 3–4 itens no padrão banca/certificação já usado no módulo.

**Referências:** OASIS SAML, materiais OpenID (contraste), RFC 7643/7644 (SCIM), documentação conceitual Entra/Okta — no estilo atual do módulo.

**Metadados:** atualizar `titulo` / `subtitulo` / conceitos do slug `Autenticacao-e-IAM` em `index_dados.py` (e CURRICULO se espelhar) para incluir SAML/SCIM sem abandonar OAuth/JWT/RBAC.

### 3.2 Estudo 41 — Identidade híbrida e nuvem

**Arquivo:** `_geradores/identidade_hibrida_e_nuvem_body.html`

**Nova seção** `federacao-saml-entra` (teoria, curta): papel do AD FS / Entra como IdP SAML; claim mapping; risco da chave de assinatura; remissão explícita ao protocolo detalhado no estudo Autenticação e IAM.  
+1–2 itens de checklist; +1 questão; sem copiar bindings/NameID do 04.

### 3.3 Portal — `ROTAS_PERFIL`

**Arquivo:** `_geradores/index_dados.py`  
Inserir após `grc` e antes de `pericia`.

**`ciso`** — nome: “CISO / Liderança de Segurança”; ícone: `👔`.  
Módulos (ordem pedagógica):

1. Fundamentos-Ciber  
2. Arquitetura-Zero-Trust  
3. Autenticacao-e-IAM  
4. PAM-e-Acessos-Privilegiados  
5. Gestao-de-Vulnerabilidades  
6. Gestao-de-Riscos-TI  
7. ISO-27001-e-27002  
8. Auditoria-de-TI  
9. Gestao-de-Riscos-de-Terceiros  
10. Continuidade-e-Disaster-Recovery  
11. Gestao-de-Crise-e-Comunicacao  
12. Exercicios-Tabletop  
13. Lideranca-e-Programa-de-Seguranca  
14. Estruturacao-da-Area-de-Seguranca  

**`appsec`** — nome: “AppSec / Segurança de Aplicações”; ícone: `🧩`.  
Módulos:

1. Fundamentos-Ciber  
2. Fundamentos-de-Computacao-e-SO  
3. Criptografia-Pratica  
4. Autenticacao-e-IAM  
5. Python-para-Seguranca  
6. OWASP-Top-10-Web  
7. Seguranca-em-APIs  
8. Seguranca-em-Nuvem  
9. Identidade-Hibrida-e-Nuvem  
10. DevSecOps-e-CI-CD  
11. Seguranca-de-Containers  
12. Seguranca-em-Kubernetes  
13. Infraestrutura-como-Codigo-Segura  
14. Deteccao-e-Resposta-em-Nuvem  

**Nota explícita:** a rota AppSec usa o catálogo atual; o aprofundamento SSDLC/SAMM no módulo DevSecOps fica para ciclo seguinte — a descrição da rota não deve prometer esse conteúdo como já entregue.

### 3.4 Testes e verificação

- Atualizar `IDS_ESPERADOS` e asserts em `_geradores/testes/test_rotas_sugeridas.py` e `_geradores/testes/test_curriculo.py`.
- Testes de conteúdo enxutos para 04/41: presença dos ids de seção; menção a SAML; `validar_corpo` ok — sem reativar `_geradores/testes_arquivados_lab/`.
- `./_geradores/gerar.sh` dos dois módulos + portal (ou `todos` se mais simples na execução).
- Falhas Mermaid/`chrome-headless-shell` por ambiente: não bloqueiam se não forem regressão deste ciclo.

### 3.5 Tom e marca

- Textos em pt-BR.
- Marca: nunca “Estudos de/em Cibersegurança”, “José Mauro”, “Brandão”, “Stelling” (`test_marca`).
- Sem simuladores / “em breve” / coluna vazia de lab.

---

## 4. Ordem de implementação (orientação ao plano)

1. Conteúdo e metadados do estudo 04.  
2. Ponte e ajustes do estudo 41.  
3. Rotas `ciso` e `appsec` + testes de portal/currículo.  
4. Testes de conteúdo dos corpos + rebuild + grep residual SAML.

---

## 5. Ciclos seguintes (fora desta spec)

- SSDLC / SAMM / Security Champions + SBOM/SLSA/secrets em DevSecOps.  
- Mobile + MDM/UEM (candidato a módulo 63).  
- Secrets/KMS/HSM como consolidação ou módulo.  
- Labs redesenhados do zero.
