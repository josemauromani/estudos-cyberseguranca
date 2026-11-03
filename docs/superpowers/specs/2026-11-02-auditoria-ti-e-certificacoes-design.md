# Design Spec: Auditoria de TI (Módulo 58), Normas ISO Complementares e Certificações de Mercado

**Data:** 2026-11-02
**Status:** Aprovada (2026-11-02) e implementada
**Repositório:** `estudos_cyberseguranca`
**Specs anteriores:** [`2026-10-15-competencias-vaga-analista-si-design.md`](2026-10-15-competencias-vaga-analista-si-design.md), [`2026-11-02-trilhas-especializacao-design.md`](2026-11-02-trilhas-especializacao-design.md)
**Referência Metodológica:** Superpowers Spec-Driven Development (SDD)

---

## 1. Propósito e Entendimento

O usuário perguntou quais outras vagas caberiam na visão **Rota por vaga**. Para responder com dados reais, trouxe perfis de conexões do LinkedIn (PDF exportado). Os dois primeiros perfis analisados são de **liderança de GRC** (um CISO regional e um Head de Riscos de TI/Cyber). Eles expuseram três grupos de lacunas no catálogo, que o usuário mandou implementar inteiros:

- **A. Certificações:** os dois perfis não têm CISSP, CISM, CEH nem Security+. Têm certificações de entrada da EXIN e da CertiProf, mais ITIL. A matriz do portal só conhece as 6 certificações internacionais caras.
- **B. Conteúdo:** SOX, ITGC e COBIT não aparecem em nenhum módulo. ISO 27701, 27017, 27018 e 42001 também não. ISO 22301, 27005 e NIST AI RMF aparecem de passagem (3 arquivos cada). Privacy by Design não aparece com esse nome.
- **C. Carreira:** os dois perfis seguem a mesma trajetória (suporte ou telecom → analista → gestor → CISO, com MBA em Gestão de SI; um deles nem lista graduação), e o módulo de carreira não mostra trajetórias reais.

### Por que agora

Quem mira vagas de GRC em empresa auditada (listada em bolsa, regulada pelo BACEN, com auditoria Big4) é cobrado em SOX/ITGC e costuma começar pelas certificações Foundation. O catálogo hoje forma bem o analista técnico e o gestor de SGSI, mas não o analista de auditoria de TI nem o de privacidade.

### Decisões do usuário

| Decisão | Escolha |
|---|---|
| Itens | Todos os itens A, B e C da análise dos perfis |
| Abordagem | **2**: módulo novo só para Auditoria de TI; os demais temas viram seções em módulos existentes |
| Certificações | As 4 do item A **mais CISA e ISO/IEC 27001 Lead Auditor** (6 → 12) |
| Revisão de impacto | Pedida pelo usuário; resultado na §5 |
| Item D (vaga de GRC na Rota por vaga) | Fica para quando houver anúncio real |
| Planejador de Certificações | **Manter o modelo atual**; CISA, Lead Auditor e EXIN DPO mostram o requisito em texto, sem cálculo |

### Critérios de sucesso

- O catálogo tem **58 módulos em 13 trilhas**, consistente em `estudos.txt`, `index_dados.py`, `CURRICULO.md` e `README.md`.
- O módulo 58 passa no validador do contrato (`contrato.validar_corpo`) e compila com `montar.py`.
- Os módulos 01–57 mantêm número e trilha.
- A visão **Por certificação** mostra 12 certificações; cada uma tem ao menos 3 módulos.
- O planejador do módulo de Carreira oferece as 12 certificações.
- As 6 seções novas (§4) existem nos módulos indicados, cada uma com ao menos 1 questão de fixação e 1 referência oficial nova.
- Nenhum nome, empresa ou dado pessoal dos perfis do LinkedIn entra no repositório.
- A suíte `unittest` passa inteira; `gerar.sh todos` compila o portal e as 58 páginas sem erro.

### Não objetivos

- Uma vaga nova na Rota por vaga (item D).
- Perfil de carreira novo em `CARREIRAS` ou rota sugerida nova.
- Reescrever laboratórios existentes dos módulos que recebem seções novas.
- FCPA e Módulo Certified Security Officer (fora de segurança ou pouco pedidos hoje).

### Anti-objetivos (seria falha mesmo funcionando)

- O módulo 58 repetir a auditoria do SGSI que o módulo 26 já ensina (cláusula 9.2, fases da certificação).
- Apresentar 2 perfis como estatística de mercado. A seção de trajetórias mostra padrões ilustrativos, não "X% dos CISOs".
- Pesos de prova ou requisitos de experiência inventados. Todo número de certificação vem da página oficial da certificadora, ou o campo diz que não é publicado.

---

## 2. Abordagens consideradas

| # | Abordagem | Prós | Contras |
|---|---|---|---|
| 1 | Tudo como seções em módulos existentes (SOX/ITGC/COBIT dentro de Gestão de Riscos de TI) | Catálogo fica em 57; sem mexer em rotas, contagens e testes de quantidade | Auditoria de TI é uma disciplina inteira; espremida num módulo centrado na ISO 31000, fica rasa e sem laboratório próprio |
| **2 (escolhida)** | **Módulo 58 "Auditoria de TI: SOX, ITGC e COBIT"; demais temas como seções** | O tema mais cobrado em auditoria corporativa ganha profundidade, laboratório e lugar no catálogo, nas rotas e na matriz | Mais trabalho: metadados, contagens 57 → 58, testes |
| 3 | Trilha nova "GRC avançado" com vários módulos | Espaço máximo | Infla o catálogo; os temas do item B cabem bem como seções. Descartada |

---

## 3. Módulo 58: Auditoria de TI: SOX, ITGC e COBIT

### 3.1 Metadados (`estudos.txt` e `ESTUDOS_DADOS`)

| Campo | Valor |
|---|---|
| Slug / pasta | `Auditoria-de-TI` |
| Arquivo | `Auditoria-de-TI/treinamento-auditoria-de-ti.html` |
| Corpo | `_geradores/auditoria_de_ti_body.html` |
| Título | Auditoria de TI: SOX, ITGC e COBIT |
| Subtítulo | Controles gerais de TI, teste de desenho e de efetividade, amostragem e deficiências |
| Trilha | 6 (Governança, Riscos & Conformidade), cor da trilha 6 |
| Posição | **58**, acrescentado no fim de `estudos.txt`, sem renumerar (precedente: módulo 29 na Trilha 2) |
| NIST | Govern |
| MITRE | T1078 Valid Accounts / T1098 Account Manipulation (as falhas de ITGC de acesso que viram incidente) |
| Carreiras | `GRC & Auditoria`, `ROTULO_ANALISTA_SI` |
| Tempo | 45 min |
| Nível | intermediario |
| Pergunta-chave | O controle está no papel. Como você prova que ele funcionou o ano inteiro? |
| Simulador | Testador de ITGC |
| Fatos | SOX 404 e ICFR; 4 domínios de ITGC; TOD vs TOE e amostragem por frequência; deficiência, deficiência significativa e fraqueza material |

### 3.2 Seções do corpo

Segue o contrato do `GUIA-DO-AUTOR.md` §2.2 e o tom dos módulos existentes.

1. **Introdução (teoria):** o problema real. A empresa tem política de acesso, mas o auditor pede a evidência das revisões de janeiro a dezembro e metade não existe.
2. **SOX 404, ICFR e por que a TI entra (teoria):** a lei, a seção 404, controles internos sobre relatórios financeiros, COSO 2013 como estrutura, abordagem top-down baseada em risco (PCAOB AS 2201). Quem está sujeito no Brasil: empresas com valores mobiliários registrados na SEC (ADR). Relação com auditoria interna e externa.
3. **ITGC na prática (teoria):** os 4 domínios (acesso a programas e dados, gestão de mudanças, desenvolvimento e aquisição, operações de computador). Exemplos de controle e de evidência por domínio, ITGC vs ITAC, IPE (relatório gerado pelo sistema usado como evidência), SOC 1 vs SOC 2 de fornecedores (remete ao 57). O domínio de acesso remete a 04 e 40 (SoD e recertificação); o de mudança, a 22 DevSecOps e 52 IaC; operações, a Continuidade e Backup.
4. **COBIT 2019 (teoria):** governança vs gestão, os 5 domínios (EDM, APO, BAI, DSS, MEA) e os 40 objetivos, fatores de desenho, níveis de capacidade. Tabela que liga os domínios de ITGC aos objetivos COBIT mais usados.
5. **O ciclo do teste (teoria):** planejamento, walkthrough, teste de desenho (TOD) e de efetividade operacional (TOE), amostragem por frequência do controle, exceções, controles compensatórios, classificação (deficiência, deficiência significativa, fraqueza material), carta de recomendação e remediação. Um diagrama Mermaid do ciclo.
6. **Laboratório: Testador de ITGC.** Ver §3.3.
7. **Checklist (4 a 8 itens):** preparação para uma auditoria de ITGC (inventário de sistemas no escopo, matriz de riscos e controles, evidências PBC, população completa e íntegra, revisões de acesso datadas e assinadas, mudanças com aprovação prévia, segregação entre desenvolvimento e produção, plano de remediação com dono e prazo).
8. **Questões de fixação e entrevista:** 6 questões no estilo CISA e de entrevista de Big4.
9. **Referências:** Sarbanes-Oxley Act seção 404; PCAOB AS 2201; COSO Internal Control – Integrated Framework (2013); ISACA COBIT 2019; ISACA ITAF; IIA Global Internal Audit Standards (2024); AICPA SOC 1 e SOC 2. "Próximos passos" aponta 26, 25, 57, 04 e 40.

### 3.3 Laboratório: Testador de ITGC

JavaScript puro, sem dependências, como os demais simuladores (`GUIA-DO-AUTOR.md` §4).

- **Cenário:** uma empresa fictícia com 3 sistemas no escopo e 4 a 6 controles, um ou mais por domínio. Cada controle tem frequência (anual, trimestral, mensal, semanal, diária ou várias vezes ao dia) e população (por exemplo, 12 revisões mensais, 80 mudanças no ano, 250 desligamentos).
- **Passo 1, amostra:** o estudante escolhe o tamanho da amostra de cada controle. O simulador compara com a tabela de referência de amostragem por frequência (prática de mercado usada pelas grandes auditorias) e explica quando a amostra é pequena demais.
- **Passo 2, teste:** o simulador sorteia os itens e mostra a evidência de cada um (aprovação, data, aprovador). O estudante marca o que é exceção (aprovação depois da implantação, aprovador igual ao executor, desligado com acesso ativo depois do prazo).
- **Passo 3, conclusão:** o estudante classifica cada controle (efetivo, deficiência, deficiência significativa, fraqueza material), levando em conta um controle compensatório quando existir. O simulador mostra a classificação esperada e o porquê.
- O cenário é fixo (sem aleatoriedade na correção) para que o teste automatizado verifique o resultado.

### 3.4 Teste próprio

`_geradores/testes/test_auditoria_de_ti.py`, no padrão de `test_gestao_riscos_terceiros.py`: estrutura e contrato, termos-chave presentes (SOX 404, ITGC, COBIT 2019, TOD, TOE, fraqueza material), referências, metadados, compilação e lógica do simulador.

---

## 4. Seções novas em módulos existentes

Cada módulo abaixo tem hoje 7 itens de checklist e 6 questões. Cada um ganha **1 seção de teoria**, inserida antes do laboratório, **1 item de checklist** (chega a 8, o máximo do guia), **1 ou 2 questões** e as referências oficiais.

| Módulo | Seção nova | Conteúdo mínimo |
|---|---|---|
| 25 Gestão de Riscos de TI | ISO/IEC 27005:2022: risco de segurança da informação | Relação com a ISO 31000 e com a ISO 27001 6.1.2; abordagens baseada em eventos e baseada em ativos; critérios de aceitação; ligação com a matriz 5×5 do laboratório existente |
| 27 LGPD e Privacidade | ISO/IEC 27701 e Privacy by Design | SGPI e papéis de controlador e operador; edição vigente da 27701 (verificar se é a de 2025, autônoma); LGPD art. 46 §2º; GDPR art. 25; os 7 princípios de Privacy by Design e by Default |
| 21 Segurança em Nuvem | ISO/IEC 27017 e 27018 | Controles adicionais para nuvem (27017) e proteção de dados pessoais em nuvem pública (27018); como entram na Declaração de Aplicabilidade do provedor e do cliente; ligação com a responsabilidade compartilhada |
| 28 Continuidade e DR | ISO 22301:2019: o SGCN | Estrutura de cláusulas, BIA e avaliação de riscos de continuidade, estratégias, exercícios e certificação; emenda de 2024 |
| 24 IA e Cibersegurança | Governança de IA: ISO/IEC 42001 e NIST AI RMF | Sistema de gestão de IA (42001:2023); as 4 funções do AI RMF 1.0 (Govern, Map, Measure, Manage) e o perfil de IA generativa (NIST AI 600-1) |
| 33 Certificações e Carreira | Trajetórias reais e certificações de entrada | Ver §4.1 |

### 4.1 Módulo de Carreira

- **Seção nova "Trajetórias reais e certificações de entrada":** os padrões dos perfis analisados, **anônimos** e descritos como exemplos, não estatística. Inclui a trajetória suporte/telecom → analista → gestor → CISO, o MBA em Gestão de SI como formação comum, e as certificações Foundation como primeiro passo barato antes de CISSP e CISM. Um quadro "por onde começar" por perfil: GRC, privacidade, auditoria e técnico.
- **Tabela da seção "As Certificações da Vaga"** ganha as 6 certificações novas.
- **Laboratório (Planejador de Certificações):** os dados embutidos no JavaScript (hoje 6 objetos, com domínios, pesos e experiência) ganham as 6 certificações novas. Onde a certificadora não publica peso por domínio, o campo `nota_dominios` diz isso.
- **Modelo de elegibilidade mantido (decisão do usuário).** O planejador continua com as 4 experiências atuais (TI, segurança, gestão, nuvem), o desconto por graduação e a caixa do treinamento oficial. ISFS, ITIL 4 Foundation e CSFPC não exigem experiência e entram no cálculo normal. **CISA, PECB Lead Auditor e o caminho EXIN de privacidade (PDPF/PDPP/DPO)** não são calculados: o planejador mostra o requisito oficial em texto (por exemplo, "5 anos em auditoria, controle, garantia ou segurança; até 3 dispensáveis") e indica que a elegibilidade deve ser conferida na certificadora. A função `elegibilidade` em `test_certificacoes_carreira.py` segue o mesmo comportamento. Nenhum campo novo de entrada.

---

## 5. Revisão de impacto nos módulos e no portal

Feita a pedido do usuário. Nenhum módulo precisa ser reescrito. Os ajustes:

### 5.1 Sobreposição de conteúdo

| Módulo existente | O que já cobre | Tratamento |
|---|---|---|
| 26 ISO 27001 | Auditoria do SGSI: 9.2, não conformidade, fases 1 e 2 da certificação | O 58 não repete; cita o 26. O 26 ganha o 58 em "Próximos passos" |
| 04 IAM e 40 PAM | SoD, recertificação de acessos | O 58 remete a eles no domínio de acesso |
| 22 DevSecOps e 52 IaC | Gestão de mudanças no pipeline | O 58 remete a eles no domínio de mudança |
| 30 Bancos de Dados | Trilha de auditoria de banco | Leitura de apoio do 58 |
| 57 Terceiros | Relatórios SOC 2 de fornecedores | O 58 explica SOC 1 vs SOC 2 e remete ao 57; o 57 ganha o 58 em "Próximos passos" |
| 25 Gestão de Riscos | Risco corporativo | O 25 ganha o 58 em "Próximos passos" (auditoria baseada em risco) |

### 5.2 Dados do portal (`_geradores/index_dados.py`)

- `ROTAS_PERFIL`, rota `grc`: inserir `Auditoria-de-TI` logo depois de `ISO-27001-e-27002`.
- `ROTA_VAGA`, competência `controles`: acrescentar `Auditoria-de-TI` em `apoio` (por isso o módulo leva `ROTULO_ANALISTA_SI` nas carreiras; `test_modulos_da_rota_tem_carreira_analista` exige).
- `CERTIFICACOES`: acrescentar `Auditoria-de-TI` em CISM e CISSP; acrescentar as 6 certificações da §6.

### 5.3 Documentação e contagens 57 → 58

- `README.md`: os 5 lugares com "57", o diagrama das trilhas (faixa da Trilha 6 passa a "Módulos 25 a 28, 31, 58"), a tabela de módulos (linha 58) e a tabela da Rota por vaga, se mudar.
- `CURRICULO.md`: linha 58, faixa da Trilha 6 ("25 ao 28, 31, 58"), seção da Trilha 6, §5 das rotas sugeridas.
- `GUIA-DO-AUTOR.md`: só se citar o total de módulos.

### 5.4 Testes que fixam valores

| Teste | Mudança |
|---|---|
| `test_curriculo.py` | 57 → 58 |
| `test_rota_vaga.py::test_certificacoes_exatas` | 6 → 12 siglas |
| `test_trilhas_empregabilidade.py` | Sequência numérica da rota GRC com o 58 |
| `test_gestao_riscos_terceiros.py` | Texto "57 módulos" → "58 módulos" |
| `test_corpos_migrados.py` | Docstring; conferir se algum valor fixa 57 |
| `test_certificacoes_render` | Número de linhas da matriz: 6 → 12 |
| `test_trilhas_empregabilidade.py::test_certificacoes_novas` | Incluir as 6 siglas novas (hoje daria `KeyError`) |
| `test_certificacoes_carreira.py` | Pesos de domínio e a função `elegibilidade` espelhada em Python, conforme a §4.1 |

Restrição da máquina (`~/.claude/CLAUDE.md`): rodar só os testes afetados durante o trabalho; a suíte completa só no fim, com `--maxWorkers=2` quando aplicável e dentro de `systemd-run --user --scope -p MemoryMax=4G -p MemorySwapMax=1G`, depois de conferir `free -h`.

---

## 6. Matriz de certificações: 6 → 12

Campos iguais aos atuais: `sigla`, `nome`, `orgao`, `foco`, `experiencia`, `modulos`. As 6 novas entram depois das atuais. Requisitos de experiência e pesos de prova devem ser **conferidos na página oficial** antes de escritos.

| Sigla | Nome | Órgão | Foco | Módulos (proposta inicial; o construtor pode refinar, mínimo 3) |
|---|---|---|---|---|
| ISFS | Information Security Foundation based on ISO/IEC 27001 | EXIN | Entrada / fundamentos de SI | Fundamentos-Ciber, ISO-27001-e-27002, Gestao-de-Riscos-TI, LGPD-e-Privacidade, Engenharia-Social-e-Phishing, Legislacao-e-Crimes-Ciberneticos |
| PDPF/PDPP | Privacy & Data Protection Foundation e Practitioner (com ISFS formam o EXIN Certified DPO) | EXIN | Privacidade e proteção de dados | LGPD-e-Privacidade, Protecao-de-Dados-e-Conteudo, Gestao-de-Riscos-de-Terceiros, Resposta-a-Incidentes, Legislacao-e-Crimes-Ciberneticos |
| ITIL 4 F | ITIL 4 Foundation | PeopleCert (Axelos) | Gestão de serviços de TI | Resposta-a-Incidentes, Continuidade-e-Disaster-Recovery, Gestao-de-Crise-e-Comunicacao, Gestao-de-Vulnerabilidades, Auditoria-de-TI |
| CSFPC | Cyber Security Foundation Professional Certificate | CertiProf | Entrada / cibersegurança | Fundamentos-Ciber, Redes-e-Protocolos, Criptografia-Pratica, Autenticacao-e-IAM, Engenharia-Social-e-Phishing, Seguranca-em-Endpoints-EDR, Ransomware-Prevencao-a-Recuperacao |
| CISA | Certified Information Systems Auditor | ISACA | Auditoria de sistemas | Auditoria-de-TI, ISO-27001-e-27002, Gestao-de-Riscos-TI, Continuidade-e-Disaster-Recovery, Autenticacao-e-IAM, PAM-e-Acessos-Privilegiados, DevSecOps-e-CI-CD, Seguranca-de-Bancos-de-Dados, Gestao-de-Riscos-de-Terceiros, Backup-Imutavel-e-Recuperacao |
| ISO 27001 LA | PECB Certified ISO/IEC 27001 Lead Auditor | PECB | Auditoria de SGSI (ISO 19011) | ISO-27001-e-27002, Auditoria-de-TI, Gestao-de-Riscos-TI, Continuidade-e-Disaster-Recovery, LGPD-e-Privacidade |

As Foundations da CertiProf (Ransomware, CSIRT etc.) são representadas pela CSFPC. As demais aparecem só no texto da seção de Carreira.

---

## 7. O que fica para o construtor

- Texto didático de todas as seções, no tom do guia, e o cenário concreto do Testador de ITGC (empresa, sistemas, controles, populações e respostas esperadas).
- Os números exatos da tabela de amostragem, com a fonte citada no módulo.
- Edições vigentes das normas (27701, 27017, 27018, 22301), conferidas nas páginas da ISO.
- Pesos de domínio e requisitos de experiência das 6 certificações, conferidos nas páginas oficiais.

**Decisões tomadas pelo autor do design (o usuário pode revisar):**
- **Lead Auditor = credencial PECB.** É uma credencial pessoal com níveis (Provisional Auditor, Auditor, Lead Auditor) e requisitos publicados, como as demais da matriz. O curso certificado pelo CQI/IRCA aparece só no texto da seção de Carreira, como caminho alternativo (o curso certifica a aprovação, não o auditor).
- Ajuste fino da lista de módulos de cada certificação (mínimo 3 por certificação).
- Ícone e cor do módulo 58 seguem a Trilha 6, como os demais.
- Ordem das tarefas e divisão em commits.

## 8. Arquivos afetados

| Arquivo | Mudança |
|---|---|
| `_geradores/auditoria_de_ti_body.html` | novo |
| `Auditoria-de-TI/treinamento-auditoria-de-ti.html` | novo (compilado) |
| `_geradores/testes/test_auditoria_de_ti.py` | novo |
| `_geradores/estudos.txt` | linha 58 |
| `_geradores/index_dados.py` | `ESTUDOS_DADOS`, `ROTAS_PERFIL`, `ROTA_VAGA`, `CERTIFICACOES` |
| Corpos 21, 24, 25, 26, 27, 28, 33, 57 | seções novas ou "Próximos passos" |
| `_geradores/CURRICULO.md`, `README.md` | contagens, Trilha 6, módulo 58, rotas |
| Testes da §5.4 | valores fixos |
| `index.html` e páginas compiladas | recompilados por `gerar.sh todos` |
