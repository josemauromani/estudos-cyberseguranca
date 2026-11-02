# Design Spec: Trilhas de Especialização (Trilhas 11, 12 e 13)

**Data:** 2026-11-02
**Status:** Aprovada (2026-11-02) e implementada (branch feat/trilhas-especializacao)
**Repositório:** `estudos_cyberseguranca`
**Specs anteriores:** [`2026-10-15-competencias-vaga-analista-si-design.md`](2026-10-15-competencias-vaga-analista-si-design.md), [`2026-11-01-trilhas-empregabilidade-design.md`](2026-11-01-trilhas-empregabilidade-design.md)
**Referência Metodológica:** Superpowers Spec-Driven Development (SDD)

---

## 1. Propósito e Entendimento

Com os 45 módulos prontos, o usuário pediu novas categorias de trilha. Das seis sugeridas, escolheu as três que mais aumentam a empregabilidade a partir do que o catálogo já tem:

1. **Detecção Avançada & Threat Hunting:** o degrau seguinte à rotina de SOC L1/L2 do módulo 16, cobrado em vagas de analista pleno.
2. **Nuvem, Containers & Kubernetes:** a maior lacuna em relação às vagas. Hoje só os módulos 21 e 41 tratam de nuvem, e containers aparecem de passagem no 22.
3. **Setor Regulado no Brasil:** regulação financeira, fraude em Pix, legislação penal e terceiros, conteúdo prático raro em português.

### Estado atual (2026-11-02)

- 45 módulos em 10 trilhas, **todos construídos**, cada um com teste próprio; suíte com 472 testes passando.
- Os totais de módulos e trilhas são derivados dos dados; só `test_tamanho_da_grade` (`test_curriculo.py`) fixa 45 e 10.
- Distribuição NIST de `estudos.txt`: Protect 28, Detect 13, Identify 6, Respond 6, Govern 4, Recover 4.

### Decisões do usuário

| Decisão | Escolha |
|---|---|
| Objetivo das trilhas novas | Empregabilidade (mesmo das Trilhas 8–10) |
| Trilhas | Detecção Avançada & Threat Hunting; Nuvem, Containers & Kubernetes; Setor Regulado no Brasil |
| Escopo desta spec | **Só grade e rotas.** O HTML dos módulos 46–57 entra depois, um módulo por vez |
| Módulos | 4 por trilha (46–57), conforme §2.3 |
| Perfis de carreira | **Só os 7 existentes**: tags de carreira e as 6 rotas por perfil atualizadas; nenhum perfil novo |
| Abordagem técnica | **A**: mesmo padrão das Trilhas 8–10 (dados em `estudos.txt` e `index_dados.py`, cores escritas à mão nos dois CSS) |
| Cores | Fúcsia (T11), verde-azulado (T12), verde-oliva (T13) |

### Critérios de sucesso

- O catálogo tem **57 módulos em 13 trilhas**, consistente em `estudos.txt`, `index_dados.py`, `CURRICULO.md` e `README.md`.
- Os módulos 01–45 mantêm número e trilha; os novos ficam em 46–57.
- A Rota da Vaga mantém os 7 requisitos e os mesmos módulos principais, e ganha os apoios do §3.1.
- Cada trilha nova tem token de cor nos 4 blocos de tema dos dois CSS, selo (`.badge-tN`) e bloco (`.track-tile.tN`).
- A suíte `unittest` passa inteira; `gerar.sh todos` compila o portal e as 45 páginas sem erro.

### Fora de escopo

- O HTML (`*_body.html`) e o teste próprio dos módulos 46–57.
- Perfis novos em `CARREIRAS` e rotas por perfil novas.
- Certificações novas em `CERTIFICACOES` (o teste `test_certificacoes_exatas` fixa as 6 atuais).
- Mudanças nos 7 requisitos ou nos módulos principais da Rota da Vaga.
- Mover módulos existentes de trilha (por exemplo, 21 continua na Trilha 5 e 41 na Trilha 9).

---

## 2. Grade Curricular: 45 → 57 Módulos, 10 → 13 Trilhas

### 2.1 Trilhas novas

| Trilha | Denominação | Cor (claro) | Cor (escuro) | Token CSS | `cor_nome` | Módulos |
|---|---|---|---|---|---|---|
| **Trilha 11** | Detecção Avançada & Threat Hunting | `#A21CAF` | `#E879F9` | `--t11-fuchsia` | `fuchsia` | 46 a 49 |
| **Trilha 12** | Nuvem, Containers & Kubernetes | `#0F766E` | `#2DD4BF` | `--t12-teal` | `teal` | 50 a 53 |
| **Trilha 13** | Setor Regulado no Brasil | `#4D7C0F` | `#A3E635` | `--t13-lime` | `lime` | 54 a 57 |

Contraste das cores claras sobre branco: fúcsia ≈ 6,3:1, verde-azulado ≈ 5,5:1, verde-oliva ≈ 5,0:1. Contraste das cores escuras sobre `#172229` (superfície do tema escuro): 6,6:1, 8,7:1 e 10,7:1. O fúcsia fica próximo do rosa (T7) e do roxo (T4), e o verde-azulado do ciano (T5); todo selo e bloco mostra o número da trilha, então a cor nunca é o único identificador.

Fundo dos selos em `base.css`, a 15% da cor clara, no padrão das trilhas existentes:

```css
.badge-t11 { background-color: rgba(162, 28, 175, 0.15); color: var(--t11-fuchsia); }
.badge-t12 { background-color: rgba(15, 118, 110, 0.15); color: var(--t12-teal); }
.badge-t13 { background-color: rgba(77, 124, 15, 0.15); color: var(--t13-lime); }
```

Descrições para `TRILHAS` (`index_dados.py`):

- **11:** "Detecção além da rotina do SOC: engenharia de detecção, threat hunting, monitoramento de rede e automação de resposta com SOAR."
- **12:** "Segurança de nuvem nativa: containers, Kubernetes, infraestrutura como código e detecção e resposta a incidentes em nuvem."
- **13:** "Segurança no contexto brasileiro: regulação do setor financeiro, fraude em pagamentos e Pix, legislação penal e riscos de terceiros."

### 2.2 Linhas novas em `_geradores/estudos.txt`

Acrescentadas ao fim, nesta ordem. O número do módulo é a posição em `ESTUDOS_DADOS`, então a ordem define a numeração 46–57:

```text
Engenharia-de-Deteccao|Engenharia de Detecção: Detection-as-Code e Cobertura ATT&CK|Engenharia-de-Deteccao|treinamento-engenharia-de-deteccao.html|11|#A21CAF|Detect
Threat-Hunting|Threat Hunting: Caça por Hipótese e Linhas de Base|Threat-Hunting|treinamento-threat-hunting.html|11|#A21CAF|Detect
Monitoramento-de-Rede-NSM|Monitoramento de Rede: Zeek, PCAP e NetFlow|Monitoramento-de-Rede-NSM|treinamento-monitoramento-de-rede-nsm.html|11|#A21CAF|Detect
SOAR-e-Automacao-de-Resposta|SOAR: Playbooks e Automação de Resposta|SOAR-e-Automacao-de-Resposta|treinamento-soar-e-automacao-de-resposta.html|11|#A21CAF|Respond
Seguranca-de-Containers|Segurança de Containers: Imagens, Build e Runtime|Seguranca-de-Containers|treinamento-seguranca-de-containers.html|12|#0F766E|Protect
Seguranca-em-Kubernetes|Segurança em Kubernetes: RBAC, Pod Security e NetworkPolicy|Seguranca-em-Kubernetes|treinamento-seguranca-em-kubernetes.html|12|#0F766E|Protect
Infraestrutura-como-Codigo-Segura|Infraestrutura como Código Segura: Terraform e Policy-as-Code|Infraestrutura-como-Codigo-Segura|treinamento-infraestrutura-como-codigo-segura.html|12|#0F766E|Protect
Deteccao-e-Resposta-em-Nuvem|Detecção e Resposta a Incidentes em Nuvem|Deteccao-e-Resposta-em-Nuvem|treinamento-deteccao-e-resposta-em-nuvem.html|12|#0F766E|Detect / Respond
Regulacao-Setor-Financeiro|Regulação Cibernética do Setor Financeiro|Regulacao-Setor-Financeiro|treinamento-regulacao-setor-financeiro.html|13|#4D7C0F|Govern
Fraude-em-Pagamentos-e-Pix|Fraude em Pagamentos: Pix, Golpes e Antifraude|Fraude-em-Pagamentos-e-Pix|treinamento-fraude-em-pagamentos-e-pix.html|13|#4D7C0F|Detect / Protect
Legislacao-e-Crimes-Ciberneticos|Legislação Brasileira e Crimes Cibernéticos|Legislacao-e-Crimes-Ciberneticos|treinamento-legislacao-e-crimes-ciberneticos.html|13|#4D7C0F|Govern
Gestao-de-Riscos-de-Terceiros|Gestão de Riscos de Terceiros e Fornecedores|Gestao-de-Riscos-de-Terceiros|treinamento-gestao-de-riscos-de-terceiros.html|13|#4D7C0F|Govern
```

O cabeçalho do arquivo passa a dizer "57 Módulos" e ganha as linhas `# 11 = Detecção Avançada & Threat Hunting (#A21CAF)`, `# 12 = Nuvem, Containers & Kubernetes (#0F766E)` e `# 13 = Setor Regulado no Brasil (#4D7C0F)`.

Os módulos 54, 56 e 57 são **Govern** porque o NIST CSF 2.0 põe requisitos legais e regulatórios em **GV.OC** e riscos da cadeia de suprimentos em **GV.SC**.

Efeito na distribuição NIST: Govern passa de 4 para 7 (+54, 56, 57), Detect de 13 para 18 (+46, 47, 48, 53, 55), Respond de 6 para 8 (+49, 53) e Protect de 28 para 32 (+50, 51, 52, 55).

### 2.3 Detalhamento dos módulos

Cada módulo abaixo vira uma entrada em `ESTUDOS_DADOS` e uma seção no §3 do `CURRICULO.md`. Os campos `titulo`, `trilha` e `nist` coincidem com `estudos.txt`. Rótulos de carreira usam exatamente os nomes de `CARREIRAS`; "Analista de SI" abaixo significa `ROTULO_ANALISTA_SI` ("Analista de Segurança da Informação"). Todo cenário de simulador usa empresas, pessoas e dados fictícios.

---

#### 46 · `Engenharia-de-Deteccao`: Engenharia de Detecção: Detection-as-Code e Cobertura ATT&CK

- **Trilha:** 11 · **NIST:** Detect · **Tempo:** 45 min
- **MITRE:** Cobertura da matriz ATT&CK Enterprise (mapeamento de detecções)
- **Carreiras:** Operações SOC & Resposta, Blue Team & Defesa
- **Subtítulo:** "Regras versionadas, testadas e medidas pela cobertura de técnicas"
- **Objetivos:**
  - Tratar detecções como código: versionamento, revisão, testes e implantação.
  - Escrever e ajustar regras Sigma com condições, filtros e níveis.
  - Medir cobertura ATT&CK e distinguir "tenho regra" de "a regra dispara".
  - Calcular precisão e volume de alertas para decidir se uma regra vai para produção.
- **Pré-requisitos:** Operacoes-SOC-e-SIEM, Threat-Intelligence.
- **Conceitos-chave:** ciclo de vida da detecção; Sigma (logsource, detection, condition); falso positivo vs falso negativo; precisão; emulação de adversário para validar regras (Atomic Red Team); matriz de cobertura; débito de detecção.
- **Diferença para o módulo 16:** o 16 ensina a ler e editar regras na rotina do SOC; este trata de como produzir, testar e medir um conjunto de detecções.
- **Pergunta-chave:** "Quantas técnicas ATT&CK suas regras realmente detectam, e como você sabe?"
- **Simulador: *Bancada de Detecções*.** O aluno edita uma regra Sigma e a roda contra um conjunto de eventos rotulados (maliciosos e benignos). O simulador mostra acertos, falsos positivos e falsos negativos, e atualiza a matriz de cobertura conforme as regras passam no teste.
- **Fatos:**
  - "Detecção como código: versionar, revisar, testar"
  - "Regras Sigma com filtros e condições"
  - "Cobertura ATT&CK medida por teste, não por existência da regra"
  - "Precisão e volume de alertas antes da produção"

#### 47 · `Threat-Hunting`: Threat Hunting: Caça por Hipótese e Linhas de Base

- **Trilha:** 11 · **NIST:** Detect · **Tempo:** 45 min
- **MITRE:** TA0003 Persistence / T1053 Scheduled Task/Job / T1543 Create or Modify System Process (alvos de caça)
- **Carreiras:** Operações SOC & Resposta, Blue Team & Defesa, Perícia Forense & Malware
- **Subtítulo:** "Procurar o que nenhum alerta pegou, partindo de uma hipótese"
- **Objetivos:**
  - Formular hipóteses de caça a partir de inteligência, ATT&CK ou anomalias.
  - Escolher a fonte de dados que confirma ou refuta a hipótese.
  - Usar linhas de base e contagem de ocorrências (*stack counting*) para achar o raro.
  - Transformar uma caça bem-sucedida em detecção automatizada.
- **Pré-requisitos:** Operacoes-SOC-e-SIEM, PowerShell-e-Windows-Interno.
- **Conceitos-chave:** caça por hipótese vs por indicador; ciclo de caça (PEAK); linha de base; *stack counting* e cauda longa; fontes (EDR, Sysmon, logs de autenticação); documentação da caça; saída para engenharia de detecção.
- **Pergunta-chave:** "Se um invasor estiver na rede sem disparar alertas, por onde você começa a procurar?"
- **Simulador: *Caçada Guiada*.** O aluno escolhe uma hipótese (por exemplo, persistência por tarefa agendada), seleciona a fonte de dados e agrupa os eventos por frequência. O implante aparece entre as ocorrências raras; o simulador pontua a hipótese, a fonte escolhida e o achado.
- **Fatos:**
  - "Caça por hipótese, não por alerta"
  - "Linha de base e contagem de ocorrências raras"
  - "Ciclo de caça PEAK"
  - "Toda caça bem-sucedida vira detecção"

#### 48 · `Monitoramento-de-Rede-NSM`: Monitoramento de Rede: Zeek, PCAP e NetFlow

- **Trilha:** 11 · **NIST:** Detect · **Tempo:** 45 min
- **MITRE:** T1071 Application Layer Protocol / T1071.004 DNS / T1048 Exfiltration Over Alternative Protocol
- **Carreiras:** Operações SOC & Resposta, Blue Team & Defesa, Perícia Forense & Malware
- **Subtítulo:** "Logs de conexão, beaconing, túnel DNS e fingerprints TLS"
- **Objetivos:**
  - Diferenciar PCAP completo, metadados (Zeek) e fluxos (NetFlow/IPFIX) por custo e valor.
  - Ler `conn.log`, `dns.log` e `ssl.log` do Zeek.
  - Detectar beaconing pela regularidade dos intervalos e pelo tamanho das conexões.
  - Reconhecer túnel DNS e usar fingerprints TLS (JA3/JA4) com cautela.
- **Pré-requisitos:** Redes-e-Protocolos, Seguranca-de-Redes-Defesa.
- **Conceitos-chave:** NSM; Zeek e seus logs; NetFlow/IPFIX; beaconing (intervalo e *jitter*); túnel DNS (subdomínios longos, alta entropia, volume); JA3/JA4; tráfego cifrado e o que ainda se vê.
- **Diferença para o módulo 07:** o 07 trata de IDS/IPS por assinatura; este trata de análise de metadados de rede para achar o que as assinaturas não pegam.
- **Pergunta-chave:** "Como achar um implante que fala com o atacante a cada 60 segundos, mesmo com o tráfego cifrado?"
- **Simulador: *Analisador de Conexões*.** O aluno recebe um `conn.log` e um `dns.log` fictícios, agrupa as conexões por par origem–destino e ajusta limiares de intervalo e *jitter*. O simulador destaca o beaconing e o túnel DNS e conta os falsos positivos do limiar escolhido.
- **Fatos:**
  - "PCAP, Zeek e NetFlow: custo vs valor"
  - "Beaconing pela regularidade dos intervalos"
  - "Túnel DNS por entropia e volume de subdomínios"
  - "JA3/JA4 ajudam, mas não provam sozinhos"

#### 49 · `SOAR-e-Automacao-de-Resposta`: SOAR: Playbooks e Automação de Resposta

- **Trilha:** 11 · **NIST:** Respond · **Tempo:** 40 min
- **MITRE:** N/A (orquestração da resposta)
- **Carreiras:** Operações SOC & Resposta, Blue Team & Defesa, Analista de SI
- **Subtítulo:** "Enriquecer, decidir e conter, com aprovação humana onde o erro custa caro"
- **Objetivos:**
  - Desenhar um playbook com gatilho, enriquecimento, decisão e ação.
  - Separar ações automáticas das que exigem aprovação humana.
  - Medir o efeito da automação em tempo de triagem (MTTA/MTTR).
  - Prever falhas: fonte de enriquecimento fora do ar, falso positivo, bloqueio de ativo crítico.
- **Pré-requisitos:** Operacoes-SOC-e-SIEM, Resposta-a-Incidentes, Python-para-Seguranca.
- **Conceitos-chave:** SOAR; playbook vs runbook; enriquecimento (reputação, ativo, usuário); *human-in-the-loop*; idempotência; listas de exceção para ativos críticos; métricas MTTA e MTTR.
- **Pergunta-chave:** "O que o seu playbook deve fazer sozinho, e o que ele nunca deve fazer sem perguntar?"
- **Simulador: *Montador de Playbook*.** O aluno encadeia blocos (enriquecer, decidir, isolar host, bloquear IP, abrir chamado, pedir aprovação) e roda o playbook contra uma fila de alertas fictícios. O simulador mostra o tempo economizado e o custo dos erros, como o isolamento indevido de um servidor de produção.
- **Fatos:**
  - "Playbook: gatilho, enriquecimento, decisão, ação"
  - "Aprovação humana para ações de alto impacto"
  - "MTTA e MTTR como medida da automação"
  - "Exceções para ativos críticos"

#### 50 · `Seguranca-de-Containers`: Segurança de Containers: Imagens, Build e Runtime

- **Trilha:** 12 · **NIST:** Protect · **Tempo:** 45 min
- **MITRE:** T1610 Deploy Container / T1611 Escape to Host
- **Carreiras:** AppSec & DevSecOps, Blue Team & Defesa
- **Subtítulo:** "Da imagem base ao processo em execução"
- **Objetivos:**
  - Endurecer um Dockerfile: imagem mínima, usuário não root, tag fixa, sem segredos.
  - Interpretar a varredura de vulnerabilidades de uma imagem e priorizar o que corrigir.
  - Assinar imagens e restringir o registro de origem.
  - Reconhecer configurações que permitem escape (privilegiado, socket do Docker, *capabilities*).
- **Pré-requisitos:** Linux-para-Seguranca, DevSecOps-e-CI-CD.
- **Conceitos-chave:** imagem base mínima e *distroless*; build multiestágio; `USER` não root; tag vs *digest*; segredos em camadas; varredura de imagem; assinatura de imagens; namespaces, cgroups e *capabilities*; `--privileged` e `docker.sock`; detecção em runtime.
- **Diferença para o módulo 22:** o 22 cobre o pipeline (SAST, DAST, SCA) e cita containers; este aprofunda imagem, registro e runtime.
- **Pergunta-chave:** "O que separa um container comprometido do servidor que o hospeda?"
- **Simulador: *Auditor de Dockerfile*.** O aluno recebe um Dockerfile e um comando `docker run` fictícios, identifica os achados (root, `latest`, segredo em `ENV`, `ADD` remoto, `--privileged`, socket montado) e aplica correções. O simulador recalcula o risco e explica o caminho de escape que cada achado abria.
- **Fatos:**
  - "Imagem mínima, usuário não root e tag fixa"
  - "Segredos nunca em camadas da imagem"
  - "--privileged e docker.sock abrem caminho ao host"
  - "Assinatura e registro confiável"

#### 51 · `Seguranca-em-Kubernetes`: Segurança em Kubernetes: RBAC, Pod Security e NetworkPolicy

- **Trilha:** 12 · **NIST:** Protect · **Tempo:** 50 min
- **MITRE:** T1609 Container Administration Command / T1613 Container and Resource Discovery / T1611 Escape to Host
- **Carreiras:** AppSec & DevSecOps, Blue Team & Defesa, Red Team & Pentest
- **Subtítulo:** "Quem pode fazer o quê no cluster, e o que cada pod alcança"
- **Objetivos:**
  - Ler Roles, ClusterRoles e bindings e achar caminhos de escalação.
  - Aplicar os níveis de Pod Security Standards (privileged, baseline, restricted).
  - Restringir tráfego entre pods com NetworkPolicy (negar por padrão).
  - Proteger segredos, a API do cluster e as contas de serviço.
- **Pré-requisitos:** Seguranca-de-Containers, Autenticacao-e-IAM.
- **Conceitos-chave:** arquitetura (API server, etcd, kubelet); RBAC e verbos perigosos (`create pods`, `escalate`, `bind`, `impersonate`); token de conta de serviço; Pod Security Admission; NetworkPolicy; Secrets e criptografia no etcd; controle de admissão; logs de auditoria; CIS Kubernetes Benchmark.
- **Pergunta-chave:** "Uma conta de serviço comprometida consegue chegar a administrador do cluster?"
- **Simulador: *Cluster em Miniatura*.** Um cluster fictício com namespaces, pods e bindings. Fase 1: o aluno avalia manifestos contra o nível *restricted* e corrige as violações. Fase 2: encontra o caminho de escalação no RBAC a partir de uma conta de serviço e o quebra. Fase 3: escreve NetworkPolicies e vê quais pods continuam alcançáveis.
- **Fatos:**
  - "RBAC: create pods, bind e escalate são privilégio"
  - "Pod Security Standards: privileged, baseline, restricted"
  - "NetworkPolicy com negação por padrão"
  - "Token de conta de serviço é credencial"

#### 52 · `Infraestrutura-como-Codigo-Segura`: Infraestrutura como Código Segura: Terraform e Policy-as-Code

- **Trilha:** 12 · **NIST:** Protect · **Tempo:** 40 min
- **MITRE:** T1578 Modify Cloud Compute Infrastructure / T1530 Data from Cloud Storage (prevenção)
- **Carreiras:** AppSec & DevSecOps, GRC & Auditoria
- **Subtítulo:** "Barrar a configuração insegura antes do apply"
- **Objetivos:**
  - Ler um plano Terraform e identificar mudanças de risco.
  - Escrever políticas como código que bloqueiam configurações proibidas.
  - Proteger o *state* (segredos, acesso, bloqueio).
  - Detectar *drift* entre o código e o ambiente real.
- **Pré-requisitos:** Seguranca-em-Nuvem, DevSecOps-e-CI-CD.
- **Conceitos-chave:** IaC declarativa; `plan` vs `apply`; *state* e seus segredos; módulos aprovados; varredura de IaC (Checkov, tfsec/Trivy); policy-as-code (OPA/Rego); exceções com prazo; *drift*.
- **Diferença para o módulo 21:** o 21 audita políticas e recursos já criados (CSPM); este impede que a configuração insegura chegue a ser criada.
- **Pergunta-chave:** "Como impedir que um bucket público chegue à produção, em vez de achá-lo depois?"
- **Simulador: *Revisor de Plano Terraform*.** O aluno recebe trechos de HCL e o plano resultante, ativa políticas (bucket público, `0.0.0.0/0` em porta administrativa, disco sem criptografia, log desligado) e vê quais mudanças são bloqueadas. Uma etapa final compara o código com o ambiente e aponta o *drift*.
- **Fatos:**
  - "Plano antes do apply, política antes do plano"
  - "State do Terraform contém segredos"
  - "Policy-as-code com exceções com prazo"
  - "Drift: o ambiente diverge do código"

#### 53 · `Deteccao-e-Resposta-em-Nuvem`: Detecção e Resposta a Incidentes em Nuvem

- **Trilha:** 12 · **NIST:** Detect / Respond · **Tempo:** 50 min
- **MITRE:** T1078.004 Valid Accounts: Cloud Accounts / T1098 Account Manipulation / T1530 Data from Cloud Storage
- **Carreiras:** Operações SOC & Resposta, Blue Team & Defesa, Perícia Forense & Malware, AppSec & DevSecOps
- **Subtítulo:** "Trilhas de auditoria, detecção nativa e contenção de credencial vazada"
- **Objetivos:**
  - Saber quais logs existem por padrão e quais precisam ser ligados (trilha de auditoria, logs de dados, logs de fluxo).
  - Ler eventos de auditoria de nuvem: quem, o quê, de onde e com qual credencial.
  - Reconstruir a linha do tempo de uma credencial vazada.
  - Conter na nuvem: revogar sessões e chaves, isolar recursos, preservar evidências.
- **Pré-requisitos:** Seguranca-em-Nuvem, Resposta-a-Incidentes, Identidade-Hibrida-e-Nuvem.
- **Conceitos-chave:** CloudTrail e Azure Activity Log; eventos de gerenciamento vs de dados; detecção nativa (GuardDuty, Defender for Cloud); chave de acesso de longa duração; criação de usuário e de chave como persistência; *snapshot* forense; contenção sem destruir evidência.
- **Pergunta-chave:** "Uma chave de acesso vazou no GitHub há três dias: o que o atacante fez, e como você o tira de lá?"
- **Simulador: *Conta Comprometida*.** O aluno recebe eventos de auditoria fictícios no estilo CloudTrail, filtra pela chave vazada e ordena a linha do tempo (descoberta, criação de usuário, nova chave, leitura de bucket). Depois escolhe a ordem da contenção; o simulador mostra o que cada escolha preserva ou destrói.
- **Fatos:**
  - "Eventos de dados não vêm ligados por padrão"
  - "Credencial vazada: revogar, girar, investigar"
  - "Criação de usuário e de chave como persistência"
  - "Snapshot antes de desligar"

#### 54 · `Regulacao-Setor-Financeiro`: Regulação Cibernética do Setor Financeiro

- **Trilha:** 13 · **NIST:** Govern · **Tempo:** 45 min
- **MITRE:** Conformidade Regulatória
- **Carreiras:** GRC & Auditoria, Analista de SI
- **Subtítulo:** "Resolução CMN 4.893 e Resolução BCB 85, com as alterações de dezembro de 2025"
- **Objetivos:**
  - Identificar quem está sujeito a cada norma (instituições financeiras e de pagamento).
  - Listar o que a política de segurança cibernética e o plano de resposta a incidentes devem conter.
  - Aplicar os requisitos para contratação de processamento, armazenamento e computação em nuvem.
  - Conhecer os controles mínimos e o teste de intrusão anual incluídos em dezembro de 2025.
- **Pré-requisitos:** ISO-27001-e-27002, Gestao-de-Riscos-TI, PCI-DSS.
- **Conceitos-chave:** Res. CMN 4.893/2021 alterada pela Res. CMN 5.274/2025; Res. BCB 85/2021 e sua alteração de dezembro de 2025; política de segurança cibernética; plano de ação e de resposta a incidentes; relatório anual; contratação de nuvem e responsabilidade que não se transfere ao fornecedor; controles mínimos; teste de intrusão anual; segregação de ambientes do Pix e do STR.
- **Pergunta-chave:** "O que o Banco Central exige da sua política de segurança, e o que muda quando o sistema vai para a nuvem?"
- **Simulador: *Verificador de Aderência*.** O aluno recebe a política e o contrato de nuvem de uma instituição fictícia e marca, requisito por requisito, se está atendido, parcial ou ausente. O simulador aponta as lacunas, cita o dispositivo correspondente e gera um plano de ação priorizado.
- **Fatos:**
  - "CMN 4.893/2021, alterada pela CMN 5.274/2025"
  - "BCB 85/2021 para instituições de pagamento"
  - "Responsabilidade não se transfere ao fornecedor de nuvem"
  - "Teste de intrusão anual e controles mínimos"
- **Conferência na construção:** as fontes divergem sobre o número da resolução BCB de dezembro de 2025 que alterou a BCB 85 (538 ou 448), e há menção a uma alteração posterior (BCB 552/2026). O módulo cita o número só depois de conferir no site normativos.bcb.gov.br.

#### 55 · `Fraude-em-Pagamentos-e-Pix`: Fraude em Pagamentos: Pix, Golpes e Antifraude

- **Trilha:** 13 · **NIST:** Detect / Protect · **Tempo:** 45 min
- **MITRE:** T1656 Impersonation / T1566 Phishing (vetores de golpe)
- **Carreiras:** Operações SOC & Resposta, GRC & Auditoria, Analista de SI
- **Subtítulo:** "Golpes com Pix, sinais de risco, regras antifraude e o MED 2.0"
- **Objetivos:**
  - Reconhecer os golpes mais comuns (falsa central, falso parente, conta laranja, sequestro de conta).
  - Combinar sinais de risco (conta recém-aberta, valor atípico, horário, dispositivo novo) em uma pontuação.
  - Equilibrar fraude evitada e cliente legítimo bloqueado.
  - Entender o Mecanismo Especial de Devolução (MED 2.0) e o bloqueio cautelar.
- **Pré-requisitos:** Engenharia-Social-e-Phishing, Regulacao-Setor-Financeiro.
- **Conceitos-chave:** engenharia social financeira; contas laranja; sinais de transação, de conta e de dispositivo; regras vs pontuação; falso positivo e atrito com o cliente; bloqueio cautelar; MED 2.0 (Res. BCB 493/2025), com devolução a partir de contas diferentes da usada na fraude e contestação pelo autoatendimento.
- **Diferença para o módulo 15:** o 15 trata da defesa humana contra phishing; este trata da detecção da transação fraudulenta do lado da instituição.
- **Pergunta-chave:** "Quais sinais separam um Pix legítimo de um golpe, e quanto atrito o cliente honesto aceita?"
- **Simulador: *Mesa Antifraude*.** O aluno recebe uma fila de transações Pix fictícias, ajusta pesos e limiares dos sinais de risco e decide aprovar, segurar ou bloquear. O simulador mostra fraudes evitadas, clientes bloqueados sem motivo e, para as fraudes que passaram, o fluxo do MED.
- **Fatos:**
  - "Golpe de falsa central e conta laranja"
  - "Pontuação de risco com sinais combinados"
  - "Fraude evitada vs cliente bloqueado"
  - "MED 2.0 e bloqueio cautelar"
- **Conferência na construção:** prazos do MED 2.0 (por exemplo, "até 11 dias") vêm de fontes secundárias; o módulo usa só prazos confirmados na Resolução BCB 493/2025 ou no guia do MED do Banco Central.

#### 56 · `Legislacao-e-Crimes-Ciberneticos`: Legislação Brasileira e Crimes Cibernéticos

- **Trilha:** 13 · **NIST:** Govern · **Tempo:** 40 min
- **MITRE:** N/A (legislação)
- **Carreiras:** GRC & Auditoria, Perícia Forense & Malware, Analista de SI
- **Subtítulo:** "Tipos penais, guarda de registros e preservação de provas"
- **Objetivos:**
  - Enquadrar condutas nos tipos penais de invasão de dispositivo, fraude eletrônica e furto mediante fraude eletrônica.
  - Aplicar os prazos de guarda de registros do Marco Civil da Internet.
  - Preservar provas digitais de forma que sejam aceitas.
  - Situar a Política Nacional de Cibersegurança e a E-Ciber.
- **Pré-requisitos:** LGPD-e-Privacidade, Forense-Digital.
- **Conceitos-chave:** Lei 12.737/2012 (art. 154-A do Código Penal); Lei 14.155/2021 (penas maiores, fraude eletrônica no art. 171 §2º-A, furto mediante fraude eletrônica no art. 155 §4º-B), com nova redação do art. 171 §2º-A e do art. 155 §4º-B dada pela Lei 15.397/2026; Marco Civil da Internet (Lei 12.965/2014): registros de conexão por 1 ano (art. 13) e de acesso a aplicações por 6 meses (art. 15); requisição judicial de registros; cadeia de custódia (arts. 158-A a 158-F do CPP); PNCiber (Decreto 11.856/2023) e E-Ciber (Decreto 12.573/2025).
- **Diferença para o módulo 27:** o 27 trata de dados pessoais e da ANPD; este trata da esfera penal e da prova.
- **Pergunta-chave:** "O que guardar, por quanto tempo e como, para que o caso chegue ao processo penal?"
- **Simulador: *Enquadramento de Casos*.** O aluno lê casos fictícios, escolhe o tipo penal, indica quais registros pedir e a quem, e ordena os passos de preservação de provas. O simulador corrige cada escolha com o dispositivo legal correspondente.
- **Fatos:**
  - "Art. 154-A: invasão de dispositivo informático"
  - "Fraude eletrônica: art. 171 §2º-A (redação de 2026)"
  - "Marco Civil: conexão 1 ano, aplicações 6 meses"
  - "PNCiber (2023) e E-Ciber (2025)"
- **Conferência na construção:** penas e redação dos artigos são conferidas no texto consolidado do Código Penal (planalto.gov.br) antes de entrar no módulo.

#### 57 · `Gestao-de-Riscos-de-Terceiros`: Gestão de Riscos de Terceiros e Fornecedores

- **Trilha:** 13 · **NIST:** Govern · **Tempo:** 40 min
- **MITRE:** T1195 Supply Chain Compromise / T1199 Trusted Relationship
- **Carreiras:** GRC & Auditoria, Analista de SI
- **Subtítulo:** "Due diligence, cláusulas mínimas, monitoramento e plano de saída"
- **Objetivos:**
  - Classificar fornecedores por criticidade e acesso a dados e sistemas.
  - Conduzir due diligence proporcional à criticidade.
  - Definir cláusulas mínimas: notificação de incidente, auditoria, subcontratação, devolução de dados.
  - Monitorar o fornecedor durante o contrato e planejar a saída.
- **Pré-requisitos:** Gestao-de-Riscos-TI, ISO-27001-e-27002.
- **Conceitos-chave:** ciclo de vida do terceiro; criticidade vs risco inerente e residual; questionários e evidências (ISO 27001, SOC 2); quarta parte (subcontratados); cláusulas de segurança; direito de auditoria; plano de saída; NIST CSF 2.0 GV.SC; controle 5.19–5.23 da ISO 27002:2022; exigências de contratação da Res. CMN 4.893.
- **Pergunta-chave:** "Seu fornecedor crítico tem acesso aos seus dados: como você sabe que ele protege, e como sai do contrato se precisar?"
- **Simulador: *Avaliador de Fornecedores*.** O aluno avalia três fornecedores fictícios (respostas a questionário e evidências), calcula criticidade e risco, escolhe as cláusulas obrigatórias e decide contratar, contratar com condições ou recusar. O simulador mostra o risco residual e o que falta no plano de saída.
- **Fatos:**
  - "Due diligence proporcional à criticidade"
  - "Cláusulas: incidente, auditoria, subcontratação, saída"
  - "Quarta parte: o fornecedor do fornecedor"
  - "NIST CSF 2.0 GV.SC e ISO 27002 5.19–5.23"

### 2.4 Ordenação

Os 12 módulos entram ao fim de `estudos.txt` e de `ESTUDOS_DADOS` na ordem 46 → 57 acima. Nenhum módulo existente muda de posição.

---

## 3. Rotas, Necessidades e Certificações

### 3.1 `ROTA_VAGA`: módulos de apoio

Os 7 requisitos, os textos e os módulos **principais** não mudam. Entram só módulos de **apoio**, acrescentados ao fim de cada lista. A vaga exige PCI-DSS, o que indica empresa de pagamentos ou financeira, por isso a regulação financeira se encaixa em `normas`:

| `id` | Apoio novo |
|---|---|
| `normas` | + Regulacao-Setor-Financeiro, Gestao-de-Riscos-de-Terceiros |
| `resposta_incidentes` | + SOAR-e-Automacao-de-Resposta |

Os 3 módulos levam "Analista de Segurança da Informação" em `carreiras` (teste existente `test_modulos_da_rota_tem_carreira_analista`). O contador de competências cobertas continua considerando só os principais.

### 3.2 Rotas por perfil (§5 do `CURRICULO.md`)

Nenhuma rota nova. As 6 existentes passam a ser (módulos novos em **negrito**):

| Rota | Sequência nova |
|---|---|
| 1. Blue Team / Analista SOC | 01 → 02 → 34 → 36 → 05 → 06 → 07 → **48** → 10 → 39 → 16 → **46** → 17 → **47** → 18 → **49** → 42 |
| 2. Red Team / Pentest | 01 → 02 → 34 → 04 → 11 → 12 → 13 → 38 → 39 → **51** → 14 → 15 |
| 3. DevSecOps & Cloud Security | 01 → 03 → 04 → 35 → 06 → 12 → 13 → 21 → 41 → 22 → **50** → **51** → **52** → **53** → 24 |
| 4. GRC, Auditoria & Privacidade | 01 → 08 → 40 → 09 → 25 → 26 → **57** → 27 → **56** → **54** → **55** → 28 → 43 → 44 |
| 5. Perícia & Resposta a Incidentes | 01 → 02 → 06 → 36 → 10 → **48** → 16 → **47** → 18 → **53** → 42 → 45 → 19 → **56** → 20 |
| 6. Analista de Segurança da Informação (vaga) | 01 → 34 → 36 → 05 → 06 → 07 → 10 → 29 → 30 → 38 → 40 → 25 → 26 → 31 → **54** → **57** → 18 → **49** → 42 → 43 → 32 → 37 → 33 |

No `CURRICULO.md`, as rotas continuam no formato atual, entre crases e com `->` (por exemplo, `` `01 -> 02 -> 34 -> ...` ``). Cada módulo novo de uma rota tem a carreira correspondente em `carreiras` (§2.3).

### 3.3 `NECESSIDADES`: 12 itens novos

Acrescentados ao fim da lista, um por módulo:

| Desafio | Slug | Categoria | Ícone |
|---|---|---|---|
| Preciso medir quais técnicas ATT&CK minhas regras realmente detectam | Engenharia-de-Deteccao | Detecção | 🎯 |
| Preciso procurar um invasor que nenhum alerta pegou | Threat-Hunting | Detecção | 🔦 |
| Preciso achar beaconing e túnel DNS no tráfego de rede | Monitoramento-de-Rede-NSM | Detecção | 📡 |
| Preciso automatizar a triagem sem bloquear o que não devia | SOAR-e-Automacao-de-Resposta | Detecção | 🤖 |
| Preciso revisar a segurança de uma imagem de container antes do deploy | Seguranca-de-Containers | Nuvem | 📦 |
| Preciso fechar o RBAC e isolar os pods de um cluster Kubernetes | Seguranca-em-Kubernetes | Nuvem | ☸️ |
| Preciso barrar recurso público ou sem criptografia antes do terraform apply | Infraestrutura-como-Codigo-Segura | Nuvem | 🏗️ |
| Preciso investigar uma chave de acesso vazada na nuvem | Deteccao-e-Resposta-em-Nuvem | Nuvem | 🔑 |
| Preciso adequar a política de segurança às exigências do Banco Central | Regulacao-Setor-Financeiro | Regulação | 🏦 |
| Preciso montar regras antifraude para transações Pix | Fraude-em-Pagamentos-e-Pix | Regulação | 💸 |
| Preciso saber o que guardar e como preservar provas de um crime cibernético | Legislacao-e-Crimes-Ciberneticos | Regulação | ⚖️ |
| Preciso avaliar o risco de um fornecedor crítico antes de contratar | Gestao-de-Riscos-de-Terceiros | Regulação | 🤝 |

### 3.4 `CERTIFICACOES`: módulos acrescentados

Só onde o domínio da certificação cobre o tema com clareza. Os módulos são acrescentados ao fim de cada lista; nenhuma certificação nova:

| Sigla | Módulos novos |
|---|---|
| CCSP | Seguranca-de-Containers, Seguranca-em-Kubernetes, Infraestrutura-como-Codigo-Segura, Deteccao-e-Resposta-em-Nuvem |
| GSEC | Monitoramento-de-Rede-NSM, Seguranca-de-Containers |
| CISSP | Monitoramento-de-Rede-NSM, Deteccao-e-Resposta-em-Nuvem, Gestao-de-Riscos-de-Terceiros |
| CISM | Regulacao-Setor-Financeiro, Gestao-de-Riscos-de-Terceiros |
| Security+ | Engenharia-de-Deteccao, Fraude-em-Pagamentos-e-Pix |
| CEH | Seguranca-em-Kubernetes |

---

## 4. Pipeline, Design System e Documentação

### 4.1 Arquivos alterados

| Arquivo | Alteração |
|---|---|
| `_geradores/estudos.txt` | Cabeçalho "57 Módulos" e legenda das trilhas 11–13; 12 linhas novas (§2.2) |
| `_geradores/index_dados.py` | `TRILHAS[11..13]` (§2.1); 12 entradas em `ESTUDOS_DADOS` (§2.3); apoio em `ROTA_VAGA` (§3.1); 12 `NECESSIDADES` (§3.3); `CERTIFICACOES` (§3.4); comentário do bloco de trilhas sem "10 Trilhas" fixo |
| `_geradores/base.css` | `--t11-fuchsia`, `--t12-teal`, `--t13-lime` nos 4 blocos de tema (`:root` claro, `@media (prefers-color-scheme: dark)`, `[data-theme="dark"]`, `[data-theme="light"]`); `.badge-t11` a `.badge-t13` (§2.1) |
| `_geradores/index.css` | Os mesmos 3 tokens nos 4 blocos; `.track-tile.t11`, `.t12`, `.t13` |
| `_geradores/CURRICULO.md` | §1 com "57 módulos / 13 trilhas"; §2 com T11–T13 no diagrama Mermaid (T11 → DE, RS; T12 → PR, DE, RS; T13 → GV, DE, PR) e na tabela; §3 com o detalhamento dos módulos 46–57; §4 com a distribuição NIST **recalculada a partir de `estudos.txt`**; §5 com as rotas do §3.2 |
| `README.md` | "57 módulos / 13 trilhas"; T11–T13 no diagrama; tabela com 57 linhas; apoio novo na seção "Rota por Vaga" |
| `index.html` | Regenerado por `./_geradores/gerar.sh todos` |
| 45 treinamentos | Recompilados por `./_geradores/gerar.sh todos`, porque `base.css` é embutido nas páginas |
| `docs/superpowers/specs/2026-11-01-trilhas-empregabilidade-design.md` | Nota no topo: "Grade ampliada para 57 módulos / 13 trilhas, ver `2026-11-02-trilhas-especializacao-design.md`" |

### 4.2 Arquivos que não mudam

- `build_index.py`: filtros, blocos de trilha (`track-tile t{id}`) e contagens do cabeçalho já saem de `TRILHAS` e do catálogo. Se a implementação encontrar algum valor fixo, ele é corrigido como parte desta spec.
- `montar.py`, `diagramas.py`, `base.js`, `gerar.sh` e os `*_body.html` existentes.

---

## 5. Testes e Verificação

### 5.1 Princípio

TDD (Red → Green → Refactor) com `unittest`. Antes de rodar a suíte, conferir `free -h`; a suíte inteira roda dentro de `systemd-run --user --scope --quiet -p MemoryMax=4G -p MemorySwapMax=1G`, conforme as instruções da máquina.

### 5.2 Testes existentes que mudam

| Arquivo | Ajuste |
|---|---|
| `test_curriculo.py` | `test_tamanho_da_grade`: `estudos.txt` com **57** módulos e `TRILHAS` com **13** trilhas. Continua sendo o único lugar com esses números |
| `test_trilhas_empregabilidade.py` | `test_rotas_por_perfil_no_curriculo` passa a exigir as 6 sequências do §3.2, porque as rotas mudam de propósito. `test_posicoes_34_a_45` recorta `list(ESTUDOS_DADOS)[33:45]` em vez de `[33:]`, que passaria a incluir 46–57. Os demais testes do arquivo (apoios, necessidades e certificações das Trilhas 8–10) continuam válidos, porque só se acrescenta ao fim das listas |

Já cobertos pelos testes atuais, sem mudança: tokens `--t{id}-{cor_nome}` 4 vezes em cada CSS, `.badge-t{id}` e `.track-tile.t{id}` para toda trilha de `TRILHAS` (`test_assets.py`); total de módulos e trilhas no portal (`test_index.py`); README cita todos os slugs (`test_cli.py`); módulos da Rota da Vaga com a carreira de Analista de SI e as 6 certificações exatas (`test_rota_vaga.py`). O `test_favicon.py` conta páginas compiladas (portal + 45) e não muda, porque nenhuma página nova é criada.

### 5.3 Testes novos: `_geradores/testes/test_trilhas_especializacao.py`

1. Os slugs do §2.2 ocupam as posições 46–57 de `ESTUDOS_DADOS`, nessa ordem, com as trilhas 11, 12 e 13 e o NIST do §2.2.
2. `TRILHAS[11..13]` têm os nomes, cores e `cor_nome` do §2.1.
3. Em `ROTA_VAGA`, os módulos principais das 7 competências são exatamente os de antes (lista fixa no teste), e os apoios do §3.1 estão presentes.
4. Cada um dos 12 módulos novos aparece em pelo menos um item de `NECESSIDADES`.
5. As associações do §3.4 estão em `CERTIFICACOES`.
6. As carreiras dos módulos novos existem em `CARREIRAS` (ou são `ROTULO_ANALISTA_SI`).
7. Cada módulo novo que aparece numa rota do §3.2 tem em `carreiras` o perfil daquela rota: rota 1 → "Blue Team & Defesa" ou "Operações SOC & Resposta"; rota 2 → "Red Team & Pentest"; rota 3 → "AppSec & DevSecOps"; rota 4 → "GRC & Auditoria"; rota 5 → "Perícia Forense & Malware"; rota 6 → `ROTULO_ANALISTA_SI`.

### 5.4 Critérios de aceite

- `python3 -m unittest discover -s _geradores/testes` passa inteira.
- `./_geradores/gerar.sh todos` executa sem erro.
- O `index.html`, nos temas claro e escuro e em largura de celular, mostra:
  - as Trilhas 11–13 no filtro e no mapa de trilhas, com as cores do §2.1;
  - os 12 cards novos como pendentes;
  - os chips de apoio novos na Rota da Vaga, também como pendentes;
  - nenhuma rolagem horizontal e nenhum erro no console.

---

## 6. Referências Normativas Verificadas (2026-11-02)

Conferidas por busca antes desta spec. As marcadas "conferir" precisam de checagem no texto oficial antes de entrar no HTML do módulo.

| Referência | Situação | Módulo |
|---|---|---|
| Res. CMN 4.893/2021 | Em vigor, **alterada pela Res. CMN 5.274/2025** (18/12/2025): controles mínimos detalhados, teste de intrusão anual, segregação Pix/STR; adequação até 01/03/2026 | 54, 57 |
| Res. BCB 85/2021 | Em vigor, alterada em 18/12/2025. **Conferir** o número da norma de alteração (fontes citam BCB 538 e BCB 448) e a alteração posterior citada (BCB 552/2026) | 54 |
| Res. BCB 493/2025 (MED 2.0) | Publicada em 28/08/2025; devolução a partir de contas diferentes da usada na fraude; contestação pelo autoatendimento. **Conferir** prazos no texto oficial ou no guia do MED | 55 |
| Lei 12.737/2012 e Lei 14.155/2021 | Art. 154-A com pena de reclusão; fraude eletrônica (art. 171 §2º-A) e furto mediante fraude eletrônica (art. 155 §4º-B). A Lei 15.397/2026 deu nova redação ao art. 155 §4º-B (reclusão de 4 a 10 anos e multa) e ao art. 171 §2º-A; **conferir** penas no Código Penal consolidado | 56 |
| Lei 12.965/2014 (Marco Civil) | Guarda de registros de conexão por 1 ano (art. 13) e de acesso a aplicações por 6 meses (art. 15) | 56 |
| Decreto 11.856/2023 (PNCiber) | Em vigor; institui a Política e o Comitê Nacional de Cibersegurança | 56 |
| Decreto 12.573/2025 (E-Ciber) | Publicado em 05/08/2025; nova Estratégia Nacional de Cibersegurança, revoga o Decreto 10.222/2020 | 56 |

Fontes da verificação: [LegisWeb: Res. CMN 5.274/2025](https://www.legisweb.com.br/legislacao/?id=488277), [Voto CMN 88/2025](https://normativos.bcb.gov.br/Votos/CMN/202588/Voto_do_CMN_88_2025.pdf), [GlobalSuite: Res. BCB 538](https://www.globalsuitesolutions.com/pt/?p=117773), [LegisWeb: Res. BCB 448/2025](https://www.legisweb.com.br/legislacao/?id=488304), [BCB: MED 2.0](https://www.bcb.gov.br/content/estabilidadefinanceira/pix/MED/MED_2-0_Circuito_Pix-Dia_1.pdf), [Agência Brasil: novas regras do Pix](https://agenciabrasil.ebc.com.br/economia/noticia/2026-02/novas-regras-de-seguranca-do-pix-entram-em-vigor-veja-mudancas), [Planalto: Lei 14.155/2021](https://planalto.gov.br/ccivil_03/_ato2019-2022/2021/Lei/L14155.htm), [Planalto: Decreto 11.856/2023](https://planalto.gov.br/ccivil_03/_ato2023-2026/2023/decreto/d11856.htm), [Planalto: Decreto 12.573/2025](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/decreto/d12573.htm).

---

## 7. Próximos Passos (fora desta spec)

Os módulos 46–57 seguem a fila normal de construção, um por commit, com o padrão estabelecido (`*_body.html` com diagrama Mermaid dentro de `.diagram-box` + teste próprio + compilação). O detalhamento do §2.3, copiado para o `CURRICULO.md`, é a especificação de conteúdo de cada módulo. Antes de construir os módulos 54, 55 e 56, resolver os itens "conferir" do §6.
