# Design Spec: Trilha 14 — Liderança & Estratégia (Módulos 59 e 60) e Ajustes Vindos de Perfis Executivos

**Data:** 2026-11-03
**Status:** Rascunho para aprovação
**Repositório:** `estudos_cyberseguranca`
**Specs anteriores:** [`2026-11-02-auditoria-ti-e-certificacoes-design.md`](2026-11-02-auditoria-ti-e-certificacoes-design.md), [`2026-11-02-trilhas-especializacao-design.md`](2026-11-02-trilhas-especializacao-design.md), [`2026-11-03-certificacoes-praticas-pentest-design.md`](2026-11-03-certificacoes-praticas-pentest-design.md)
**Referência Metodológica:** Superpowers Spec-Driven Development (SDD)

---

## 1. Propósito e Entendimento

O usuário trouxe mais cinco perfis públicos do LinkedIn (PDF exportado), todos de **liderança executiva**: CISOs, dois deles acumulando a função de CTO. Os três perfis analisados antes eram de GRC intermediário e de pentest. O cruzamento dos cinco perfis com os 58 módulos mostrou que o catálogo forma bem o analista e o gestor de SGSI, mas **não ensina o papel de CISO**: a palavra aparece em só 2 corpos (`gestao_de_crise_e_comunicacao` e `certificacoes_e_carreira`), e KPI, KRI, linha de reporte, modelo das três linhas, sourcing de SOC (MSSP/MDR) e orçamento de segurança não aparecem em nenhum.

Os perfis também mostraram quatro lacunas menores:

- **Criptografia:** ciclo de vida de certificados (CLM), ACME, redução da validade dos certificados TLS, inventário criptográfico e migração pós-quântica. Hoje "pós-quântica" aparece uma vez e não há CLM, CBOM nem FIPS 203/204/205.
- **Regulação financeira:** os perfis citam normas revogadas (Res. CMN 4.658/2018, Circular BCB 3.909), que ainda aparecem em currículos e vagas. O catálogo cita só as vigentes, sem a correspondência.
- **Certificações:** CRISC e CDPSE (ISACA) não aparecem em nenhum arquivo do repositório; a matriz tem CISA e CISM, mas não as duas que completam a família.
- **Carreira:** a seção de trajetórias do Estudo 33 descreve três perfis e nenhum de liderança executiva.

### Estado atual (2026-11-03)

- 58 módulos em 13 trilhas, todos construídos. O módulo 58 (Auditoria de TI) entrou na Trilha 6.
- 15 certificações em `CERTIFICACOES` (`index_dados.py`) e no JSON `#cert-dados` do Estudo 33.
- Totais fixos nos testes: `test_curriculo.py` (58 módulos, 13 trilhas) e `test_certificacoes_carreira.py` (15 certificações).
- Cores das trilhas em `tokens.css` (4 blocos de tema), `index.css` (`[data-trilha="N"]`) e `base.css` (`.badge-tN`).

### Decisões do usuário

| Decisão | Escolha |
|---|---|
| Itens da análise | 1 (módulo de CISO), 2 (CLM e pós-quântica), 4 (histórico normativo BACEN), 5 (CRISC e CDPSE), 6 (trajetórias de 3 para 8 perfis) |
| Público do conteúdo de liderança | **Os dois, em camadas**: base para o analista que quer crescer, avançado para o gestor que vai assumir a área |
| Onde entra | **Trilha 14 nova**, "Liderança & Estratégia" |
| Abordagem | **A**: dois módulos na Trilha 14, um por camada (59 base, 60 avançado) |
| Cor da Trilha 14 | Dourado: `#A16207` (claro) e `#FDE047` (escuro), sujeito ao teste de contraste |
| Perfis de carreira | Nenhum perfil novo em `CARREIRAS`; só as rotas existentes ganham os módulos novos |

### Critérios de sucesso

- O catálogo tem **60 módulos em 14 trilhas**, consistente em `estudos.txt`, `index_dados.py`, `CURRICULO.md` e `README.md`.
- Os módulos 01–58 mantêm número e trilha; os novos ficam em 59 e 60, os dois na Trilha 14.
- Os módulos 59 e 60 passam em `contrato.validar_corpo`, compilam com `montar.py` e têm teste próprio que espelha o motor do simulador.
- A Trilha 14 tem token de cor nos 4 blocos de tema de `tokens.css`, regra `[data-trilha="14"]` em `index.css` e `.badge-t14` em `base.css`, e passa nos testes de contraste existentes.
- A matriz e o planejador mostram **17 certificações**; CRISC e CDPSE têm ao menos 3 módulos cada.
- O Estudo 03 tem a seção nova de CLM e cripto-agilidade, o Estudo 54 tem a tabela de correspondência normativa e o Estudo 33 descreve 8 perfis; cada acréscimo com ao menos 1 questão de fixação e 1 referência oficial nova.
- Nenhum nome, empresa, instituição, URL ou detalhe identificador dos perfis entra no repositório.
- A suíte `unittest` passa inteira; `gerar.sh todos` compila o portal e as 60 páginas sem erro.

### Não objetivos

- Perfil de carreira novo em `CARREIRAS` (por exemplo, "CISO" ou "Privacidade e DPO").
- Vaga nova na Rota por vaga.
- Os itens 3 (fraude corporativa e em fidelidade), 7 (perfil DPO) e 8–10 (bug bounty/VDP, ratings de segurança, conscientização fora do módulo 60) da análise.
- Mover módulos existentes de trilha.
- Mudar a lógica do planejador de certificações: CRISC e CDPSE usam `requisitos: {"conferir": true}`, como a CISA.

### Anti-objetivos (seria falha mesmo funcionando)

- O módulo 59 repetir a gestão de riscos do módulo 25 (ALE/SLE, matriz de risco) ou a governança de SGSI do módulo 26. O 59 parte desses conceitos e trata de **como levá-los à alta direção**.
- O módulo 60 virar lista de produtos ou fornecedores. Sourcing é ensinado por modelo (interno, MSSP, MDR, híbrido), não por marca.
- Apresentar 8 perfis como estatística de mercado. A seção de trajetórias mostra padrões ilustrativos.
- Inventar números: pesos de prova, requisitos de experiência, datas da redução de validade de certificados e números de normas vêm da fonte oficial, ou o texto diz "confira na página oficial".
- Reproduzir conquistas que identifiquem uma pessoa (nota de rating antes e depois, "primeiro programa do país", contrato específico).

---

## 2. Abordagens Consideradas

| Abordagem | Troca | Decisão |
|---|---|---|
| **A. Dois módulos na Trilha 14** (59 base, 60 avançado) | A trilha nasce com dois módulos; cada camada tem tamanho normal; a ordem de estudo é a própria camada. Custa dois módulos completos | **Escolhida** |
| B. Um módulo só com seções marcadas "Base" e "Avançado" | Mais barato, mas o módulo fica muito maior que os outros, a trilha nasce com um módulo e o contrato de markup precisaria de rótulo novo | Descartada |
| C. Só o 59 agora, o 60 numa spec futura | Trilha rala e camada avançada sem data | Descartada |

---

## 3. Grade Curricular: 58 → 60 Módulos, 13 → 14 Trilhas

### 3.1 Trilha nova

| Trilha | Denominação | Cor (claro) | Cor (escuro) | Token CSS | `cor_nome` | Módulos |
|---|---|---|---|---|---|---|
| 14 | Liderança & Estratégia | `#A16207` | `#FDE047` | `--t14-gold` | `gold` | 59, 60 |

Descrição em `TRILHAS[14]`: "Como o CISO pensa e como se monta uma área de segurança: governança, métricas para o conselho, orçamento, maturidade e sourcing."

Se `#A16207` não passar no contraste AA dos testes existentes (`test_componentes_css.py`, `test_portal.py`, `test_assets.py`), escurece-se o tom dentro da mesma família (por exemplo `#854D0E`) e registra-se a troca no progresso do plano. A cor do tema escuro segue a mesma regra.

### 3.2 Módulos novos

| Nº | Slug | Título curto | Arquivo de corpo | NIST | Nível | Tempo |
|---|---|---|---|---|---|---|
| 59 | `Lideranca-e-Programa-de-Seguranca` | Liderança e Programa de Segurança: o Papel do CISO | `lideranca_e_programa_de_seguranca_body.html` | Govern | intermediário | 45 min |
| 60 | `Estruturacao-da-Area-de-Seguranca` | Estruturação da Área de Segurança: Maturidade, Time e Sourcing | `estruturacao_da_area_de_seguranca_body.html` | Govern | avançado | 50 min |

Pasta e HTML seguem a convenção: `Lideranca-e-Programa-de-Seguranca/treinamento-lideranca-e-programa-de-seguranca.html` e `Estruturacao-da-Area-de-Seguranca/treinamento-estruturacao-da-area-de-seguranca.html`.

`ESTUDOS_DADOS` de cada um segue o formato do 58 (`titulo`, `subtitulo`, `trilha`, `nist`, `mitre`, `carreiras`, `tempo_minutos`, `nivel`, `pergunta_chave`, `simulador_nome`, `fatos`). `mitre` segue o formato já usado por módulos de gestão: "N/A (liderança e governança)" no 59 e "N/A (estruturação e sourcing)" no 60.

### 3.3 Rotas e carreiras

- **Tags de carreira:** 59 e 60 recebem "GRC & Auditoria"; o 59 também recebe `ROTULO_ANALISTA_SI`.
- **Rotas por perfil (`ROTAS_PERFIL`):** a rota `grc` ganha 59 e 60 no fim; a rota `analista_si` ganha o 59 no fim.
- **CISM** passa a listar 59 e 60 em `modulos`; **CISSP** passa a listar o 59.

### 3.4 Arquivos de catálogo atualizados

`estudos.txt` (cabeçalho "60 Módulos", legenda da Trilha 14, duas linhas novas), `index_dados.py`, `CURRICULO.md` (visão geral, diagrama Mermaid das trilhas, tabela de trilhas, detalhamento dos dois módulos, distribuição NIST, rotas), `README.md` (diagrama, tabela de módulos, perfis) e os testes de total fixo.

---

## 4. Conteúdo dos Módulos

Os dois seguem o contrato do corpo do `GUIA-DO-AUTOR.md` §2 e a forma do módulo 58: texto de abertura, 5 seções de teoria, 1 laboratório, 1 checklist, questões e referências. Cada um com ao menos 1 diagrama Mermaid e 6 questões de concurso ou de fixação com resposta explicada.

### 4.1 Módulo 59 — Liderança e Programa de Segurança (camada base)

**Pergunta-chave:** "O SIEM gerou 40 mil alertas no trimestre. O que disso o conselho precisa saber?"

| Seção | Conteúdo |
|---|---|
| O papel do CISO e a linha de reporte | Responsabilidades; modelo das três linhas do IIA (2020); independência; o conflito quando CTO ou CIO acumulam a função de CISO e as salvaguardas (comitê, reporte funcional a risco ou ao conselho); CISO, DPO e encarregado |
| Governança de segurança | Função Govern do NIST CSF 2.0 (categorias GV.OC, GV.RM, GV.RR, GV.PO, GV.OV, GV.SC); política de topo; comitê de segurança; papéis com RACI. Remete ao 26 para o SGSI |
| Risco em linguagem de negócio | Apetite e tolerância; registro de risco executivo; KPI × KRI × métrica de vaidade; como um achado técnico vira decisão. Remete ao 25 para o cálculo |
| Métricas e relato ao conselho | O que entra num painel (poucos KRIs com limite, tendência e dono), o que não entra, armadilhas (contagem de alertas, "100% conforme"); frequência e formato; exigências de reporte da Res. CMN 4.893/2021 como exemplo setorial, remetendo ao 54 |
| Orçamento e business case | Capex × Opex; como montar um business case (problema, opções, custo, risco reduzido, decisão pedida); ROSI e as limitações dele; priorização por risco |

**Laboratório "Do SIEM ao Conselho".** Um bloco JSON lista 12 indicadores fictícios de uma empresa (por exemplo: alertas gerados, MTTD, MTTR, % de vulnerabilidades críticas corrigidas no SLA, cobertura de MFA em contas privilegiadas, bloqueios no firewall, % de fornecedores críticos avaliados, taxa de clique em simulação de phishing, testes de restauração bem-sucedidos). O aluno classifica cada um como **KRI para o conselho**, **KPI operacional** ou **métrica de vaidade**, e o painel do conselho aceita no máximo 6 KRIs. O motor compara com o gabarito do JSON, dá a explicação de cada item e avalia o painel (KRIs essenciais ausentes, excesso, métrica de vaidade incluída). O teste do módulo espelha em Python as regras do motor: classificação, limite de 6 e os itens essenciais.

**Checklist:** "Antes de levar um tema ao conselho" (decisão pedida explícita, impacto em linguagem de negócio, tendência, dono, opções com custo).

### 4.2 Módulo 60 — Estruturação da Área de Segurança (camada avançada)

**Pergunta-chave:** "Você chegou como primeiro CISO da empresa. O que acontece nos primeiros 90 dias?"

| Seção | Conteúdo |
|---|---|
| Diagnóstico e plano de 90 dias | Ouvir (stakeholders, incidentes passados, auditorias), medir (inventário, maturidade), decidir (quick wins e roadmap); entregáveis de 30/60/90 dias |
| Maturidade com o NIST CSF 2.0 | Perfil atual × perfil alvo; níveis (tiers) 1–4 e o que eles medem; como o gap vira roadmap; outros modelos citados como alternativa (CMMI, C2M2), sem aprofundar |
| Desenho do time e sourcing | Funções mínimas por porte; SOC interno, MSSP, MDR e híbrido (o que cada um entrega, custo relativo, riscos); contrato, SLA, métricas de fornecedor e plano de saída. Remete ao 16 (SOC) e ao 57 (terceiros) |
| Programa de conscientização medido | Do treinamento anual ao programa por comportamento; métricas (taxa de reporte, não só de clique); público prioritário. Remete ao 15 |
| Fusões, aquisições e integração | Due diligence de segurança antes da compra; integração de identidades e federação depois; o risco herdado. Remete ao 41 (identidade híbrida) |

**Laboratório "Alocador de Programa".** O JSON traz 3 cenários fictícios (varejo de porte médio, fintech regulada, indústria com OT), cada um com orçamento em pontos, perfil atual por função do NIST CSF 2.0 e exigências do setor. O aluno escolhe o modelo de SOC (interno, MSSP, MDR, híbrido) e distribui os pontos entre frentes (identidade e privilégio, gestão de vulnerabilidades, detecção e resposta, resiliência e backup, conscientização, GRC). O motor calcula o perfil alvo alcançado por função, verifica as exigências do cenário e lista os riscos residuais. Regras, custos e efeitos ficam no JSON; o teste espelha o cálculo e as exigências em Python. As exigências do cenário de fintech citam a norma vigente só quando ela de fato exige (conferido no texto da Res. CMN 4.893/2021).

**Checklist:** "Plano de 90 dias" (stakeholders ouvidos, perfil atual medido, top 5 riscos, quick wins, roadmap aprovado, reporte combinado).

---

## 5. Itens Menores

### 5.1 Estudo 03 (Criptografia-Pratica): ciclo de vida de certificados e cripto-agilidade

Seção de teoria nova, posta depois da seção de PKI existente:

- **CLM:** inventário de certificados, dono, renovação automática, revogação; quedas causadas por certificado vencido.
- **ACME** (RFC 8555) como forma de automatizar a renovação.
- **Redução da validade dos certificados TLS públicos** aprovada pelo CA/Browser Forum (votação SC-081). As etapas (datas e número de dias) entram só depois de conferidas no texto da votação ou nos Baseline Requirements.
- **Cripto-agilidade e pós-quântica:** inventário criptográfico (CBOM), os padrões FIPS 203 (ML-KEM), 204 (ML-DSA) e 205 (SLH-DSA) publicados pelo NIST, "colher agora, decifrar depois" e um plano de migração em etapas.
- Ao menos 1 questão de fixação e referências oficiais (RFC 8555, CA/B Forum, NIST FIPS 203/204/205).

### 5.2 Estudo 54 (Regulacao-Setor-Financeiro): correspondência normativa

Tabela "Número antigo → norma vigente" na seção da política de segurança cibernética, com pelo menos a Res. CMN 4.658/2018 e a Circular BCB 3.909 (ano e numeração conferidos no site do BCB) e as normas que as substituíram. Cada linha cita a fonte no site do BCB. Um callout explica por que isso importa: vagas e currículos ainda citam os números antigos. Ao menos 1 questão de fixação.

### 5.3 Certificações: CRISC e CDPSE (15 → 17)

Duas entradas novas no fim de `CERTIFICACOES` e no JSON `#cert-dados` do Estudo 33, com os campos atuais:

| Sigla | Nome | Órgão | Foco | Módulos (mínimo) |
|---|---|---|---|---|
| CRISC | Certified in Risk and Information Systems Control | ISACA | Risco de TI e controles | Gestao-de-Riscos-TI, Auditoria-de-TI, Gestao-de-Riscos-de-Terceiros, Continuidade-e-Disaster-Recovery, Lideranca-e-Programa-de-Seguranca |
| CDPSE | Certified Data Privacy Solutions Engineer | ISACA | Privacidade na arquitetura e no ciclo de vida dos dados | LGPD-e-Privacidade, Protecao-de-Dados-e-Conteudo, Criptografia-Pratica, Seguranca-de-Bancos-de-Dados, DevSecOps-e-CI-CD |

No planejador: `requisitos: {"conferir": true}`, `nivel` 3 (como CISA), `experiencia`, `manutencao`, `dominios` e pesos tirados da página oficial da ISACA, com as fontes no campo `fontes`. Lacunas de cobertura do currículo ficam explícitas em `nota`. O subtítulo do Estudo 33 e o texto que cita "15 certificações" passam a 17.

### 5.4 Estudo 33 (Certificacoes-e-Carreira): trajetórias de 3 para 8 perfis

Na seção `trajetorias`:

- O parágrafo de abertura passa de três para oito perfis e mantém o aviso de que são exemplos, não medida de mercado.
- Bloco novo **"Liderança executiva"** com 4 padrões, descritos sem nome, empresa ou conquista identificável:
  1. **Auditor → CISO e DPO:** auditoria externa, auditoria interna, auditoria de TI em instituição financeira, depois CISO acumulando DPO; certificações ISACA e de fraude; docência.
  2. **Arquiteto → CTO e CISO:** engenharia de software, gestão de projetos, arquitetura, depois C-level acumulando tecnologia e segurança; certificações de nuvem, não de segurança.
  3. **Infraestrutura e IAM → CISO na mesma empresa:** suporte, redes, identidade e acesso, coordenação, depois CISO; MBA em segurança; nenhuma certificação cara.
  4. **Generalista → CISO em várias empresas:** técnico e infraestrutura, depois CISO em sequência em setores diferentes; CISSP; atuação em comunidade.
- Fecho do bloco: no topo, trajetória, setor (o financeiro domina os oito perfis) e comunicação com a alta direção pesam mais que a sigla; só 1 dos 5 executivos lista CISSP. Remete aos módulos 59 e 60.
- A tabela "Por onde começar" ganha a linha "Liderança / CISO" apontando para 25, 26, 58, 59 e 60, com CISM, CRISC e CISSP como certificações a considerar.

---

## 6. Anonimização e Fontes

- Os 5 PDFs saem de `~/Downloads` para `perfis-linkedin/` (ignorada pelo git), como os 3 anteriores.
- Uma lista de termos proibidos (nomes, empresas, instituições de ensino, URLs, cargos específicos com empresa) fica no workspace do SDD (`.superpowers/sdd/<plano>/`), fora do repositório. A revisão final faz `git grep` de cada termo e espera zero ocorrências.
- Todo número de certificação, norma ou padrão tem fonte oficial conferida durante a implementação. Onde a fonte não publica o dado, o texto diz "confira na página oficial".

---

## 7. Testes e Verificação

- **Testes novos:** `test_lideranca_e_programa.py` e `test_estruturacao_da_area.py`, no padrão de `test_auditoria_de_ti.py`: seções esperadas, metadados em `ESTUDOS_DADOS`, JSON do simulador válido e motor espelhado em Python.
- **Testes atualizados:** totais em `test_curriculo.py` (60, 14 e a string "Trilha 14: Liderança & Estratégia") e `test_certificacoes_carreira.py` (17); testes que enumeram certificações, trilhas ou cores.
- **Acréscimos nos Estudos 03, 33 e 54:** os testes próprios desses módulos ganham asserções da seção, da tabela ou do bloco novos.
- **Execução:** só os arquivos afetados durante as tarefas; a suíte completa no fim, com `systemd-run --user --scope --quiet -p MemoryMax=4G -p MemorySwapMax=1G`, conferindo `free -h` antes (regra do CLAUDE.md global).
- **Compilação:** `gerar.sh todos` compila o portal e as 60 páginas sem erro.

---

## 8. Riscos e Pontos a Conferir na Implementação

| Ponto | Tratamento |
|---|---|
| Contraste do dourado | Testes de contraste existentes decidem; tom alternativo previsto em §3.1 |
| Etapas da redução de validade dos certificados TLS | Conferir no texto da votação SC-081 ou nos Baseline Requirements antes de escrever |
| Ano e numeração da Circular 3.909 e das normas substitutas | Conferir no site do BCB |
| Domínios, pesos e requisitos de CRISC e CDPSE | Conferir nas páginas oficiais da ISACA; sem peso publicado, `peso: null` |
| Simuladores parecerem receita única | Feedback explica a troca de cada escolha; o gabarito é didático e diz isso no texto |
