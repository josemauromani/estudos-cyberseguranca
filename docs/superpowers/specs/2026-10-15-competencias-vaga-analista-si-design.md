# Design Spec: Competências da Vaga "Analista de Segurança da Informação"

**Data:** 2026-10-15
**Status:** Em Revisão (Aguardando Aprovação do Usuário)
**Repositório:** `estudos_cyberseguranca`
**Spec de origem:** [`2026-10-06-estudos-cyberseguranca-design.md`](2026-10-06-estudos-cyberseguranca-design.md)
**Referência Metodológica:** Superpowers Spec-Driven Development (SDD)

---

## 1. Propósito e Entendimento

O usuário trouxe a lista de requisitos de uma vaga de **Analista de Segurança da Informação** e quer que o currículo cubra essas competências. O objetivo é **duplo**:

1. **Ampliar a grade permanentemente**: as lacunas viram módulos ou escopos definitivos do currículo.
2. **Criar uma rota da vaga**: um caminho no portal que liga cada requisito aos módulos que o cobrem.

### Requisitos da vaga (texto original)

1. Soluções de Cyber Security (Firewalls, Antivírus, DLP, AntiSpam, WAF, Filtro de conteúdo)
2. Banco de dados relacionais
3. Inglês
4. Requisitos PCI-DSS, ISO 27.001 e 27.002, 31.000 e NIST
5. Resposta a incidentes de segurança da informação
6. Controles de segurança da Informação
7. Ensino Superior completo (preferencialmente Ciências da Computação ou Sistemas de Informação); Pós-graduação em Segurança da Informação e/ou certificação (CEH, CISM, CCSP, CISSP, GSEC)

### Análise de lacunas (estado em 2026-10-15, módulos 01–11 construídos)

| Requisito | Cobertura antes desta spec | Lacuna |
|---|---|---|
| Firewalls, Antivírus, WAF | 05, 10, 07 (construídos) | — |
| DLP, AntiSpam, Filtro de conteúdo | Tangencial (15, pendente) | Sem módulo |
| Banco de dados relacionais | Só SQLi (12, pendente) | Sem módulo |
| Inglês | Nenhuma | Sem módulo |
| ISO 27001/27002 | 26 (pendente) | — |
| ISO 31000 | Nenhuma | Fora do escopo do 25 |
| NIST | CSF 2.0 transversal; 800-61 no 18 | 800-53 e 800-61r3 ausentes |
| PCI-DSS | Nenhuma | Sem módulo |
| Resposta a incidentes | 18 (pendente) | — |
| Controles de segurança | 26 Anexo A (pendente) | CIS Controls ausentes |
| Formação e certificações | Citadas no README | Sem módulo e sem mapeamento |

### Decisões do usuário

| Decisão | Escolha |
|---|---|
| Objetivo | Ampliar a grade **e** criar uma rota da vaga |
| Integração | **Híbrido**: módulos novos só para lacunas reais; os módulos pendentes 18, 25 e 26 têm escopo ampliado |
| Posição nas trilhas | **Por tema + Trilha 7 nova**: numeração 29–33 acrescentada no fim, sem renumerar 01–28 |
| Escopo desta spec | **Grade + rota**: o HTML dos módulos 29–33 fica para a fila normal de construção |

### Critérios de sucesso

- O catálogo tem 33 módulos em 7 trilhas, consistente em `estudos.txt`, `index_dados.py`, `CURRICULO.md` e `README.md`.
- Cada um dos 7 requisitos da vaga aparece no portal com pelo menos um módulo principal associado.
- O portal mostra a matriz de certificações (CEH, CISM, CISSP, CCSP, GSEC, Security+) com os módulos que cobrem cada uma.
- Os módulos 01–11 já construídos continuam compilando e com o mesmo número.
- A suíte `unittest` passa inteira.

### Fora de escopo

- Construir o HTML (`*_body.html`) dos módulos 29–33 e dos módulos 18, 25 e 26. Eles entram na fila normal de construção.
- Rastrear progresso por competência além do status disponível/pendente de cada módulo.
- Qualquer backend: o portal continua estático e offline.
- O requisito "Ensino Superior" não vira conteúdo de estudo; ele é tratado como orientação de carreira no módulo 33.

---

## 2. Grade Curricular: 28 → 33 Módulos, 6 → 7 Trilhas

### 2.1 Trilha 7 (nova)

| Trilha | Denominação | Cor (claro) | Cor (escuro) | Token CSS | Foco |
|---|---|---|---|---|---|
| **Trilha 7** | Carreira & Formação | `#DB2777` | `#F472B6` | `--t7-rose` | Inglês técnico, formação acadêmica, certificações e preparação para vagas |

O rosa é o único matiz livre: as seis trilhas existentes já ocupam azul, verde, vermelho, roxo, ciano e âmbar.

### 2.2 Módulos novos

Linhas a acrescentar ao fim de `_geradores/estudos.txt`, no formato `slug|titulo_curto|pasta|arquivo_html|trilha_num|cor_tema|nist_fn`:

```text
Protecao-de-Dados-e-Conteudo|DLP, AntiSpam e Filtro de Conteúdo|Protecao-de-Dados-e-Conteudo|treinamento-protecao-de-dados-e-conteudo.html|2|#059669|Protect / Detect
Seguranca-de-Bancos-de-Dados|Bancos de Dados Relacionais: SQL, Privilégios e Auditoria|Seguranca-de-Bancos-de-Dados|treinamento-seguranca-de-bancos-de-dados.html|2|#059669|Protect / Detect
PCI-DSS|PCI DSS v4.0.1: Escopo CDE e os 12 Requisitos|PCI-DSS|treinamento-pci-dss.html|6|#D97706|Govern / Protect
Ingles-Tecnico-Ciber|Inglês Técnico para Segurança da Informação|Ingles-Tecnico-Ciber|treinamento-ingles-tecnico-ciber.html|7|#DB2777|Protect
Certificacoes-e-Carreira|Formação, Certificações e Carreira|Certificacoes-e-Carreira|treinamento-certificacoes-e-carreira.html|7|#DB2777|Protect
```

Os módulos 32 e 33 são classificados como **Protect** porque o NIST CSF 2.0 põe capacitação na categoria **PR.AT (Awareness and Training)**.

#### 29 · `Protecao-de-Dados-e-Conteudo`: DLP, AntiSpam e Filtro de Conteúdo

- **Trilha:** 2 (Segurança Defensiva) · **NIST:** Protect / Detect · **Tempo:** 50 min
- **MITRE ATT&CK:** TA0010 Exfiltration (T1048, T1567) / T1566 Phishing
- **Carreiras:** Blue Team & Defesa, Operações SOC & Resposta, GRC & Auditoria, Analista de Segurança da Informação
- **Objetivos:**
  - Diferenciar DLP de rede, de endpoint e de nuvem (CASB).
  - Construir detectores por padrão (regex), por checksum (Luhn) e por dicionário.
  - Explicar autenticação de e-mail (SPF, DKIM, DMARC) e filtragem antispam por reputação e conteúdo.
  - Configurar filtro de conteúdo e URL por categoria em proxy seguro (SWG).
- **Pré-requisitos:** Redes-e-Protocolos, Seguranca-de-Redes-Defesa.
- **Conceitos-chave:** dados em uso, em trânsito e em repouso; classificação da informação; falso positivo vs falso negativo em DLP; quarentena; políticas DMARC (`none`, `quarantine`, `reject`); SWG; categorização de URL; inspeção TLS.
- **Simulador: *Gateway de Conteúdo*.** O aluno escolhe ou edita uma mensagem de e-mail ou um upload web de exemplo, que passa por três estágios em sequência:
  1. **AntiSpam:** avalia SPF, DKIM, DMARC e a reputação do remetente.
  2. **DLP:** aplica detectores de CPF (com dígito verificador), cartão de pagamento (com Luhn) e palavras-chave configuráveis.
  3. **Filtro de URL:** bloqueia conforme a categoria do domínio.

  O resultado final é **Permitir**, **Quarentena** ou **Bloquear**, com a justificativa de cada estágio. O aluno pode alterar políticas e limiares e reprocessar.

#### 30 · `Seguranca-de-Bancos-de-Dados`: Bancos de Dados Relacionais: SQL, Privilégios e Auditoria

- **Trilha:** 2 (Segurança Defensiva) · **NIST:** Protect / Detect · **Tempo:** 50 min
- **MITRE ATT&CK:** T1190 Exploit Public-Facing Application / T1078 Valid Accounts / T1213 Data from Information Repositories
- **Carreiras:** Blue Team & Defesa, AppSec & DevSecOps, GRC & Auditoria, Analista de Segurança da Informação
- **Objetivos:**
  - Revisar o modelo relacional (tabelas, chaves, JOIN, normalização) e SQL DDL/DML/DCL.
  - Aplicar menor privilégio com roles, `GRANT`/`REVOKE`, views e Row-Level Security.
  - Configurar auditoria de banco.
  - Proteger dados com TDE, criptografia de coluna, mascaramento dinâmico e backups cifrados.
  - Prevenir SQLi com prepared statements.
- **Pré-requisitos:** Autenticacao-e-IAM, Criptografia-Pratica.
- **Conceitos-chave:** ACID; DDL vs DML vs DCL; roles e esquemas; RLS; TDE; Dynamic Data Masking; auditoria nativa (pgAudit, SQL Server Audit); Database Activity Monitoring (DAM); contas de serviço; hardening de SGBD (CIS Benchmarks para PostgreSQL, MySQL e SQL Server).
- **Simulador: *Matriz GRANT/REVOKE*.** Um esquema fictício com 3–4 tabelas, roles e usuários. O aluno concede e revoga privilégios (`SELECT`, `INSERT`, `UPDATE`, `DELETE`) por role e tabela, e então executa uma lista de consultas de usuários fictícios. Cada consulta é marcada como **permitida** ou **negada**, gera uma entrada na trilha de auditoria e, quando houver mascaramento ativo, mostra o valor mascarado.

#### 31 · `PCI-DSS`: PCI DSS v4.0.1: Escopo CDE e os 12 Requisitos

- **Trilha:** 6 (Governança & Riscos) · **NIST:** Govern / Protect · **Tempo:** 45 min
- **MITRE ATT&CK:** TA0009 Collection / TA0010 Exfiltration
- **Carreiras:** GRC & Auditoria, Blue Team & Defesa, Analista de Segurança da Informação
- **Objetivos:**
  - Conhecer os 6 objetivos e os 12 requisitos do PCI DSS v4.0.1.
  - Delimitar o ambiente de dados do portador do cartão (CDE) e usar segmentação para reduzir o escopo.
  - Diferenciar dados do portador (PAN) de dados sensíveis de autenticação (SAD).
  - Escolher entre os tipos de SAQ e entender ROC/QSA.
  - Distinguir a abordagem definida da customizada (v4.x).
- **Pré-requisitos:** Segmentacao-e-Firewall, ISO-27001-e-27002.
- **Conceitos-chave:** PAN, SAD, CVV, tokenização vs truncamento vs criptografia; CDE e sistemas "connected-to"; segmentação validada por teste; SAQ A, A-EP, B, C, D; QSA, ISA, ROC, AOC; níveis de comerciante; requisitos que passaram a ser obrigatórios em 31/03/2025.
- **Simulador: *Delimitador de Escopo CDE*.** Um inventário de cerca de 10 sistemas fictícios (POS, servidor de aplicação, banco de dados, AD, estação de RH, gateway de pagamento terceirizado etc.). Para cada sistema, o aluno indica se ele armazena, processa ou transmite PAN, se está conectado ao CDE e se está segmentado. O simulador classifica cada um como **dentro**, **conectado** ou **fora** do escopo, explica o motivo e sugere o tipo de SAQ do cenário.

#### 32 · `Ingles-Tecnico-Ciber`: Inglês Técnico para Segurança da Informação

- **Trilha:** 7 (Carreira & Formação) · **NIST:** Protect (PR.AT) · **Tempo:** 40 min
- **MITRE ATT&CK:** N/A (módulo de carreira)
- **Carreiras:** todas as 6 existentes e Analista de Segurança da Informação
- **Objetivos:**
  - Ler advisories, registros CVE/NVD, RFCs e documentação de fabricantes em inglês.
  - Dominar o vocabulário técnico essencial e os falsos cognatos da área.
  - Redigir em inglês um resumo de incidente e um e-mail técnico curto.
- **Pré-requisitos:** nenhum.
- **Conceitos-chave:** estrutura de um advisory (Summary, Affected Versions, Impact, Mitigation, Workaround); verbos modais em requisitos normativos (MUST, SHOULD, MAY, conforme RFC 2119); falsos cognatos (*exploit*, *eventually*, *actually*); siglas comuns; registro formal vs informal.
- **Simulador: *Leitor de Advisory*.** Um boletim de segurança em inglês, no formato realista de CVE/fabricante e totalmente fictício. Cada termo técnico é clicável e mostra tradução e definição em pt-BR. Ao final há perguntas de compreensão (versão afetada, impacto, mitigação recomendada) com correção comentada. Um glossário com flashcards guarda o progresso em `localStorage`.

#### 33 · `Certificacoes-e-Carreira`: Formação, Certificações e Carreira

- **Trilha:** 7 (Carreira & Formação) · **NIST:** Protect (PR.AT) · **Tempo:** 35 min
- **MITRE ATT&CK:** N/A (módulo de carreira)
- **Carreiras:** todas as 6 existentes e Analista de Segurança da Informação
- **Objetivos:**
  - Comparar graduações (Ciência da Computação, Sistemas de Informação) e pós-graduações em SI.
  - Conhecer CEH, CISM, CISSP, CCSP, GSEC e Security+: órgão emissor, foco, domínios, experiência exigida e manutenção (CPE).
  - Montar um plano de certificação coerente com o perfil de carreira.
  - Usar o NICE Framework (NIST SP 800-181) para descrever papéis.
- **Pré-requisitos:** nenhum.
- **Conceitos-chave:** certificações de entrada vs gestão vs especialidade; pré-requisitos de experiência e status *Associate of ISC2*; CPE e renovação; NICE Framework.
- **Simulador: *Planejador de Certificações*.** O aluno escolhe uma ou mais certificações-alvo. O simulador mostra os domínios de cada uma, os módulos do currículo que cobrem cada domínio e os domínios ainda sem módulo (lacunas), além de uma sugestão de ordem de estudo. Os dados vêm de uma estrutura JS embutida no próprio módulo, coerente com `CERTIFICACOES` (§3.2).

### 2.3 Escopos ampliados (módulos pendentes)

Os módulos 18, 25 e 26 ainda não foram construídos, então muda apenas a definição em `estudos.txt`, `index_dados.py`, `CURRICULO.md` e `README.md`. Os slugs não mudam.

| # | Slug | Título novo (`titulo_curto`) | Acréscimo de escopo |
|---|---|---|---|
| 18 | `Resposta-a-Incidentes` | Ciclo NIST SP 800-61 Rev. 2 e Rev. 3 (Contenção e Erradicação) | NIST SP 800-61 **Rev. 3** (2025), que reorganiza a resposta segundo as funções do CSF 2.0, ao lado do ciclo clássico da Rev. 2 |
| 25 | `Gestao-de-Riscos-TI` | ISO 31000 e Avaliação Qualitativa vs Quantitativa (ALE/SLE) | Princípios, estrutura e processo da **ISO 31000:2018**: contexto, identificação, análise, avaliação, tratamento, monitoramento e comunicação |
| 26 | `ISO-27001-e-27002` | SGSI, Anexo A, CIS Controls e NIST 800-53 | Crosswalk dos controles do Anexo A com **CIS Controls v8.1** (IG1/IG2/IG3) e **NIST SP 800-53 Rev. 5** |

Os campos `fatos`, `subtitulo` e `pergunta_chave` desses três módulos em `ESTUDOS_DADOS` são atualizados para refletir o novo escopo.

### 2.4 Ordenação

A numeração de 01 a 28 não muda. Os módulos 29 e 30 pertencem à Trilha 2 e o 31 à Trilha 6, mesmo fora da faixa contígua. O portal continua ordenando os cards pela ordem do catálogo, que coincide com o número.

---

## 3. Rota da Vaga e Matriz de Certificações

### 3.1 `ROTA_VAGA` (nova, em `index_dados.py`)

Lista ordenada de 7 competências. Cada item tem a forma:

```python
{
    "id": "solucoes",                       # identificador estável
    "competencia": "Soluções de Cyber Security",
    "texto_vaga": "Soluções de Cyber Security (Firewalls, Antivírus, DLP, AntiSpam, WAF, Filtro de conteúdo)",
    "icone": "🧱",
    "principais": ["Segmentacao-e-Firewall", ...],  # slugs, ≥ 1
    "apoio": ["Engenharia-Social-e-Phishing"],      # slugs, pode ser vazio
}
```

| id | Competência | Principais | Apoio |
|---|---|---|---|
| `solucoes` | Soluções de Cyber Security | 05 Segmentacao-e-Firewall, 10 Seguranca-em-Endpoints-EDR, 29 Protecao-de-Dados-e-Conteudo, 07 Seguranca-de-Redes-Defesa | 15 Engenharia-Social-e-Phishing |
| `banco_dados` | Banco de dados relacionais | 30 Seguranca-de-Bancos-de-Dados | 12 OWASP-Top-10-Web |
| `ingles` | Inglês | 32 Ingles-Tecnico-Ciber | — |
| `normas` | PCI-DSS, ISO 27001/27002, ISO 31000 e NIST | 31 PCI-DSS, 26 ISO-27001-e-27002, 25 Gestao-de-Riscos-TI | 18 Resposta-a-Incidentes |
| `resposta_incidentes` | Resposta a incidentes | 18 Resposta-a-Incidentes | 16 Operacoes-SOC-e-SIEM, 19 Forense-Digital |
| `controles` | Controles de segurança da informação | 26 ISO-27001-e-27002 | 06 Hardening-Sistemas, 08 Arquitetura-Zero-Trust |
| `formacao` | Formação e certificações | 33 Certificacoes-e-Carreira | — |

### 3.2 `CERTIFICACOES` (nova, em `index_dados.py`)

Lista de 6 certificações sem duplicatas (o CCSP aparece duas vezes na vaga, mas entra uma vez). Cada item tem `sigla`, `nome`, `orgao`, `foco`, `experiencia` e `modulos` (slugs).

| Sigla | Nome | Órgão | Foco | Experiência exigida | Módulos |
|---|---|---|---|---|---|
| CEH | Certified Ethical Hacker | EC-Council | Técnica / ofensiva | 2 anos em SI **ou** treinamento oficial | 02, 11, 12, 13, 14, 15, 20 |
| CISM | Certified Information Security Manager | ISACA | Gestão de programa de SI | 5 anos em SI, sendo 3 em gestão | 18, 25, 26, 28, 31 |
| CISSP | Certified Information Systems Security Professional | ISC2 | Generalista sênior (8 domínios) | 5 anos em 2+ domínios (1 ano dispensável por graduação ou certificação aprovada) | 01, 03, 04, 05, 18, 22, 25, 26, 28, 30 |
| CCSP | Certified Cloud Security Professional | ISC2 | Segurança em nuvem (6 domínios) | 5 anos em TI, sendo 3 em SI e 1 em nuvem (CISSP substitui) | 03, 04, 21, 22, 27, 30 |
| GSEC | GIAC Security Essentials | GIAC (SANS) | Técnica generalista | Sem exigência formal | 02, 03, 05, 06, 07, 10, 16 |
| Security+ | CompTIA Security+ (SY0-701) | CompTIA | Entrada / fundamentos | Recomendada, sem exigência formal | 01, 02, 03, 04, 05, 09, 10, 18 |

Os requisitos de experiência são os vigentes na data desta spec. A seção do portal exibe a nota "Confira os requisitos atuais no site oficial do órgão emissor".

### 3.3 Carreira nova em `CARREIRAS`

```python
"analista_si": {
    "id": "analista_si",
    "nome": "Analista de Segurança da Informação",
    "icone": "🎯",
    "descricao": "Perfil generalista de vaga corporativa: soluções de segurança, normas (PCI-DSS, ISO, NIST), controles e resposta a incidentes.",
}
```

O rótulo `"Analista de Segurança da Informação"` é acrescentado ao campo `carreiras` de **todo módulo citado em `ROTA_VAGA`**, seja como principal ou como apoio: 05, 06, 07, 08, 10, 12, 15, 16, 18, 19, 25, 26, 29, 30, 31, 32, 33. Com isso, o filtro "Por Perfil Profissional" que já existe passa a cobrir a vaga sem JS novo.

O filtro de carreira em `build_index.py` usa `cardCarreiras.includes(valor)`. Nenhum nome de carreira existente é substring de "Analista de Segurança da Informação", e vice-versa, então não há falso positivo. Um teste garante isso (§5.3).

### 3.4 `NECESSIDADES`: 5 itens novos

| Desafio | Slug | Categoria | Ícone |
|---|---|---|---|
| Preciso impedir vazamento de CPF e cartões por e-mail e upload | Protecao-de-Dados-e-Conteudo | DLP | 🚫 |
| Preciso aplicar menor privilégio e auditoria em um banco de dados | Seguranca-de-Bancos-de-Dados | Banco de Dados | 🗄️ |
| Preciso delimitar o escopo PCI-DSS de um ambiente de pagamento | PCI-DSS | Conformidade | 💳 |
| Preciso ler um advisory de segurança em inglês com segurança | Ingles-Tecnico-Ciber | Inglês | 🌍 |
| Preciso escolher qual certificação de segurança tirar primeiro | Certificacoes-e-Carreira | Carreira | 🎓 |

### 3.5 Seções novas no portal (`index.html`)

As duas seções entram **logo depois** da matriz "Escolha pela Necessidade" e antes do catálogo.

**(a) "Rota por Vaga: Analista de Segurança da Informação"**, gerada por `render_rota_vaga(rota, status_map, catalogo)`:
- Uma linha (card) por competência: ícone, nome da competência, `texto_vaga` em texto secundário, chips dos módulos principais e, depois, chips de apoio com estilo mais discreto.
- Cada chip mostra `NN · título curto`:
  - **Disponível** (o HTML existe, segundo `status_map`): elemento `<a>` com link relativo para o treinamento.
  - **Pendente:** elemento `<span>` esmaecido com `aria-disabled="true"` e a dica "Em construção".
- No cabeçalho, o contador **"X de 7 competências com módulo disponível"**. X conta as competências que têm pelo menos **um módulo principal** disponível.

**(b) "Matriz de Certificações"**, gerada por `render_certificacoes(certs, status_map, catalogo)`:
- Tabela responsiva com as colunas Sigla, Órgão, Foco, Experiência e Módulos (chips com a mesma regra de disponível/pendente).
- Abaixo da tabela, a nota de conferência no site oficial.
- Em telas estreitas (< 640 px), a tabela vira uma lista de cards empilhados, sem rolagem horizontal.

O estilo dessas seções fica em `index.css` e reaproveita os tokens já existentes. Como as seções são estáticas, não há JS novo.

---

## 4. Pipeline, Design System e Documentação

### 4.1 Arquivos alterados

| Arquivo | Alteração |
|---|---|
| `_geradores/estudos.txt` | Cabeçalho "33 Módulos" e linha `# 7 = Carreira & Formação (#DB2777)`; 5 linhas novas (§2.2); títulos de 18, 25 e 26 (§2.3) |
| `_geradores/index_dados.py` | `TRILHAS[7]`; carreira `analista_si`; `ROTA_VAGA`; `CERTIFICACOES`; 5 `NECESSIDADES`; 5 entradas em `ESTUDOS_DADOS`; atualização de 18, 25 e 26; rótulo da carreira nova nos módulos da rota; docstring e comentários sem "28" e "6" fixos |
| `_geradores/build_index.py` | Botões de filtro por trilha **gerados a partir de `TRILHAS`** (substituem as linhas fixas 569–574); meta description e comentários usando as contagens reais (`len(catalogo)`, `len(TRILHAS)`); `render_rota_vaga` e `render_certificacoes` inseridos após a seção de necessidades |
| `_geradores/montar.py` | Ajuda do `--trilha`: "1 a 7" |
| `_geradores/base.css` | `--t7-rose` nos 4 blocos de tema (`:root` claro, `@media (prefers-color-scheme: dark)`, `[data-theme="dark"]`, `[data-theme="light"]`); `.badge-t7`; comentário "7 Trilhas" |
| `_geradores/index.css` | `--t7-rose` nos 4 blocos; `.track-tile.t7`; estilos da rota da vaga e da matriz de certificações |
| `_geradores/CURRICULO.md` | §1 com "33 módulos / 7 trilhas"; §2 com a Trilha 7; §3 com o detalhamento completo de 29–33 e os escopos de 18, 25 e 26; §4 com a tabela NIST **recalculada a partir de `estudos.txt`** (a tabela atual tem contagens divergentes das listas); §5 com a "Rota 6: Analista de Segurança da Informação (vaga)" |
| `README.md` | "33 módulos / 7 trilhas"; tabela com 33 linhas e títulos atualizados; seção curta "Rota por Vaga"; perfil novo em "Perfis de Carreira" |
| `index.html` | Regenerado por `./_geradores/gerar.sh portal` |
| `docs/superpowers/specs/2026-10-06-estudos-cyberseguranca-design.md` | Nota no topo: "Grade ampliada para 33 módulos / 7 trilhas, ver `2026-10-15-competencias-vaga-analista-si-design.md`" |

### 4.2 Arquivos que não mudam

- Os `*_body.html` e os treinamentos já construídos (01–11). Nada é renumerado.
- `base.js` e `gerar.sh`, porque o CLI já resolve slugs a partir do catálogo.

---

## 5. Testes e Verificação

### 5.1 Princípio

TDD (Red → Green → Refactor) com `unittest`, como no resto do pipeline. A suíte é leve (Python puro), mas o `free -h` é conferido antes da execução, conforme as instruções da máquina.

### 5.2 Testes existentes ajustados

| Arquivo | Ajuste |
|---|---|
| `test_curriculo.py` | 28 → 33 entradas; trilha válida `1 <= t <= 7` |
| `test_index.py` | `ESTUDOS_DADOS` com 33 entradas; slugs coincidindo com `estudos.txt` (33); `TRILHAS` com 7; trilha válida até 7; o portal gerado contém "33" e "7" |
| `test_cli.py` | README com 33 estudos |
| `test_montar.py` | Mantém `>= 28` (continua válido); nenhuma alteração obrigatória |
| `test_assets.py` | Cores das 7 trilhas, incluindo `--t7-rose` |

### 5.3 Testes novos: `_geradores/testes/test_rota_vaga.py`

1. Todo slug em `ROTA_VAGA[*].principais`, `ROTA_VAGA[*].apoio` e `CERTIFICACOES[*].modulos` existe em `estudos.txt`.
2. `ROTA_VAGA` tem exatamente 7 competências com `id` único, cada uma com pelo menos 1 módulo principal.
3. `CERTIFICACOES` contém exatamente as siglas {CEH, CISM, CISSP, CCSP, GSEC, Security+}, sem duplicata.
4. Todo módulo citado em `ROTA_VAGA` tem "Analista de Segurança da Informação" em `carreiras`.
5. Nenhum nome de `CARREIRAS` é substring de outro (protege o filtro `includes`).
6. `render_rota_vaga`, com um `status_map` sintético em que um módulo está disponível e outro pendente, gera `<a href=...>` para o disponível e `<span ... aria-disabled="true">` para o pendente. O contador reflete apenas os módulos principais.
7. `render_certificacoes` gera uma linha por certificação e a nota de conferência no site oficial.
8. O `index.html` gerado contém os títulos das duas seções novas e um botão de filtro `data-value` para cada chave de `TRILHAS` (1 a 7).
9. `base.css` e `index.css` contêm exatamente 4 declarações `--t7-rose:` cada (uma por bloco de tema, sem contar usos `var(--t7-rose)`); `base.css` define `.badge-t7` e `index.css` define `.track-tile.t7`.
10. Os 5 novos itens de `NECESSIDADES` apontam para os slugs 29–33.

### 5.4 Critérios de aceite

- `python3 -m unittest discover -s _geradores/testes -v` passa inteira.
- `./_geradores/gerar.sh portal` executa sem erro, e `./_geradores/gerar.sh todos` continua compilando os 11 módulos existentes.
- O `index.html` aberto no navegador, nos temas claro e escuro e em largura de celular, mostra:
  - a Trilha 7 no filtro;
  - os 5 cards novos como pendentes;
  - a rota da vaga com "1 de 7 competências com módulo disponível" (só `solucoes` tem módulo principal construído hoje);
  - a matriz de certificações sem rolagem horizontal;
  - console do JS sem erros.

---

## 6. Próximos Passos (fora desta spec)

Depois de implementada esta spec, os módulos 12–33 seguem a fila normal de construção, um por commit, com o padrão já estabelecido (`*_body.html` + teste próprio + compilação). Cada módulo novo ou ampliado usa o detalhamento do `CURRICULO.md` produzido aqui como especificação de conteúdo.
