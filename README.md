# Estudos de Cibersegurança

> Plataforma autoinstrucional, prática e enciclopédica sobre segurança da informação, defesa cibernética e governança corporativa, estruturada em **57 módulos temáticos** organizados em **13 trilhas estruturantes**.

---

## 🎯 Visão Geral do Projeto

O projeto **Estudos de Cibersegurança** foi desenvolvido para oferecer uma trilha de aprendizagem moderna, prática e rigorosa, voltada a estudantes de tecnologia, analistas e engenheiros de segurança (Blue Team, Red Team, AppSec, SOC e GRC), bem como a candidatos a certificações técnicas internacionais (**CompTIA Security+**, **CySA+**, **PenTest+**, **CEH**, **CISSP**) e concursos públicos de TI (**FGV**, **Cebraspe**, **FCC**, etc.).

### Pilares Fundamentais

1. **Zero Dependências Pesadas:**
   - Não requer servidores locais, containers Docker, bancos de dados ou dependências externas como LibreOffice (`soffice`).
2. **100% Offline e Standalone:**
   - Cada módulo compila em um único arquivo HTML5 autocontido, com Design System CSS e utilitários JavaScript totalmente embutidos (*inlined*). Funciona instantaneamente em qualquer navegador, mesmo sem conexão à internet.
3. **Interatividade Prática em Cada Módulo:**
   - Teoria pragmática e direta ao ponto (sem jargões desnecessários).
   - **Simuladores práticos em JavaScript Vanilla:** ferramentas interativas reais (analisadores de regras, decodificadores JWT, laboratórios de criptografia, calculadoras CVSS e terminais simulados).
   - **Checklists operacionais:** salvamento automático de progresso em `localStorage`.
   - **Quizzes de fixação:** perguntas comentadas com fundamentação técnica e normativa.
4. **Duplo Mapeamento Normativo:**
   - **NIST Cybersecurity Framework (CSF) 2.0:** categorização formal por funções (*Govern*, *Identify*, *Protect*, *Detect*, *Respond*, *Recover*).
   - **MITRE ATT&CK Matrix:** táticas e técnicas reais de ameaças contemporâneas.

---

## 🚀 Como Começar

Para acessar o material imediatamente, basta abrir o portal central:

```bash
# Abra diretamente no seu navegador preferido (Linux, macOS ou Windows):
xdg-open index.html          # No Linux
# ou abra 'index.html' pelo seu gerenciador de arquivos / navegador
```

O portal `index.html` conta com:
- **Estatísticas em Tempo Real:** contagem de módulos disponíveis, horas estimadas e progresso individual de conclusão gravado no navegador.
- **Filtros Dinâmicos:** visualização por trilha temática, perfil profissional (Blue Team, Red Team, AppSec, GRC, Cloud/DevSecOps, Analista de Segurança da Informação) e função do NIST CSF 2.0.
- **Matriz "Escolha pela Necessidade":** atalhos para os módulos com base em problemas práticos reais do dia a dia corporativo.
- **Busca Instantânea:** pesquisa rápida por título, termos técnicos ou conceitos-chave.

---

## 📚 Grade Curricular dos 57 Módulos

### Estrutura das Trilhas e Percurso Formativo

```mermaid
flowchart TD
    subgraph Fundacao["1. Fundação Universal"]
        T1["Trilha 1: Fundamentos & Redes<br><small>Módulos 01 a 05 | CIA, TCP/IP, Criptografia, IAM e Perímetro</small>"]
    end

    subgraph Tecnicas["2. Trilhas Técnicas e Especialidades"]
        T2["Trilha 2: Segurança Defensiva<br><small>Módulos 06 a 10, 29, 30 | Hardening, Firewalls, Zero Trust, EDR e DB</small>"]
        T3["Trilha 3: Segurança Ofensiva<br><small>Módulos 11 a 15 | Reconhecimento, OWASP Top 10, APIs e Pentest</small>"]
        T4["Trilha 4: Operações, SOC & Resposta<br><small>Módulos 16 a 20 | SIEM, Sigma, CTI, Resposta e Forense</small>"]
        T5["Trilha 5: Especialidades & Fronteiras<br><small>Módulos 21 a 24 | Nuvem, DevSecOps, IoT/TO e IA</small>"]
    end

    subgraph Governanca["3. Governança e Estratégia"]
        T6["Trilha 6: Governança, Riscos & Conformidade<br><small>Módulos 25 a 28, 31 | ISO 27001, NIST CSF, LGPD e PCI-DSS</small>"]
        T7["Trilha 7: Carreira & Formação<br><small>Módulos 32 e 33 | Inglês Técnico e Planejamento Profissional</small>"]
    end

    subgraph Empregabilidade["4. Empregabilidade"]
        T8["Trilha 8: Ferramentas & Automação<br><small>Módulos 34 a 37 | Linux, Python, PowerShell e Homelab</small>"]
        T9["Trilha 9: Identidade & AD<br><small>Módulos 38 a 41 | Active Directory, Ataques ao AD, PAM e Entra ID</small>"]
        T10["Trilha 10: Resiliência & Ransomware<br><small>Módulos 42 a 45 | Ransomware, Crise, Tabletop e Backup Imutável</small>"]
    end

    subgraph Conexoes["5. Rota Profissional e Certificações"]
        ROTA["🎯 Rota Analista de Segurança da Informação<br><small>Firewall, EDR, DLP, SQL, Normas, Incidentes e Controles</small>"]
        CERTS["🏆 Certificações Internacionais & Concursos<br><small>CompTIA Security+, CySA+, CEH, CISSP, CISM e Provas de TI</small>"]
    end

    T1 --> T2
    T1 --> T3
    T1 --> T6

    T2 --> T4
    T3 --> T4
    T2 --> T5

    T1 --> T8
    T1 --> T9
    T4 --> T10

    T2 --> ROTA
    T8 --> ROTA
    T9 --> ROTA
    T10 --> ROTA
    T4 --> ROTA
    T6 --> ROTA
    T7 --> ROTA

    T2 --> CERTS
    T4 --> CERTS
    T6 --> CERTS
    T7 --> CERTS
```

| # | Slug / Pasta | Título do Estudo | Trilha Temática | Função NIST CSF 2.0 | Simulador Interativo em JavaScript |
|:---:|---|---|---|:---:|---|
| **01** | `Fundamentos-Ciber` | Tríade CIA, Ameaças e Modelagem STRIDE | Trilha 1: Fundamentos & Redes | Identify | STRIDE Threat Canvas interativo |
| **02** | `Redes-e-Protocolos` | TCP/IP, DNS, Roteamento e Inspeção de Tráfego | Trilha 1: Fundamentos & Redes | Protect / Detect | Inspetor visual de cabeçalhos IP/TCP/UDP |
| **03** | `Criptografia-Pratica` | Criptografia Simétrica, Assimétrica, Hashes e PKI | Trilha 1: Fundamentos & Redes | Protect | Lab de Cifras (Web Crypto API SHA-256 + AES) |
| **04** | `Autenticacao-e-IAM` | Senhas, MFA, OAuth 2.0, Tokens JWT e RBAC | Trilha 1: Fundamentos & Redes | Protect | Validador/Decodificador JWT + Teste de RBAC |
| **05** | `Segmentacao-e-Firewall` | DMZ, VLANs, Regras de Firewall e Filtragem | Trilha 1: Fundamentos & Redes | Protect | Simulador de Regras de Firewall (Pass/Drop) |
| **06** | `Hardening-Sistemas` | Bastionamento Linux e Windows (CIS Benchmarks) | Trilha 2: Segurança Defensiva | Protect | Auditor interativo de configurações (`/etc/ssh`, etc.) |
| **07** | `Seguranca-de-Redes-Defesa` | IDS/IPS, WAF, VPNs e Proxies Reversos | Trilha 2: Segurança Defensiva | Protect / Detect | Analisador de regras Snort/Suricata vs Tráfego |
| **08** | `Arquitetura-Zero-Trust` | Princípios Zero Trust e Microsegmentação | Trilha 2: Segurança Defensiva | Protect | Motor de Decisão de Acesso Zero Trust |
| **09** | `Gestao-de-Vulnerabilidades` | CVE, CVSS v3.1/v4.0 e Priorização de Patches | Trilha 2: Segurança Defensiva | Identify / Protect | Calculadora interativa de Score CVSS v3.1/v4.0 |
| **10** | `Seguranca-em-Endpoints-EDR` | Antivírus, EDR/XDR e Proteção de Host | Trilha 2: Segurança Defensiva | Protect / Detect | Linha do tempo de telemetria e detecção EDR |
| **11** | `Reconhecimento-e-OSINT` | Superfície de Ataque, DNS, WHOIS e Shodan | Trilha 3: Segurança Ofensiva | Identify | Terminal simulado de OSINT e enumeração |
| **12** | `OWASP-Top-10-Web` | Falhas Web (SQLi, XSS, CSRF, Broken Auth) | Trilha 3: Segurança Ofensiva | Protect | Playground de injeção e sanitização web |
| **13** | `Seguranca-em-APIs` | OWASP API Security, Rate Limiting e Tokens | Trilha 3: Segurança Ofensiva | Protect | Simulador de chamadas de API com Rate Limiter |
| **14** | `Pentest-Metodologias` | Fases do Pentest (PTES), Escopo e Relatório | Trilha 3: Segurança Ofensiva | Identify | Construtor de matriz de achados e relatórios |
| **15** | `Engenharia-Social-e-Phishing` | Pretexting, Spear Phishing e Defesas Humanas | Trilha 3: Segurança Ofensiva | Protect | Analisador de e-mails suspeitos (Spot the Indicators) |
| **16** | `Operacoes-SOC-e-SIEM` | Rotina de SOC L1/L2, Logs e Regras Sigma | Trilha 4: Operações & SOC | Detect | Console SIEM com busca de logs e alertas |
| **17** | `Threat-Intelligence` | IoCs, TTPs, MITRE ATT&CK e STIX/TAXII | Trilha 4: Operações & SOC | Identify / Detect | Mapeador de IoCs e TTPs na matriz ATT&CK |
| **18** | `Resposta-a-Incidentes` | Ciclo NIST SP 800-61 Rev. 2 e Rev. 3 (Contenção e Erradicação) | Trilha 4: Operações & SOC | Respond | Runbook interativo em árvore de decisão |
| **19** | `Forense-Digital` | Cadeia de Custódia, Coleta de RAM e Artefatos | Trilha 4: Operações & SOC | Respond | Analisador de timeline de evidências e logs |
| **20** | `Analise-Basica-de-Malware` | Análise Estática vs Dinâmica e Sandboxes | Trilha 4: Operações & SOC | Detect / Respond | Inspetor de metadados PE/ELF e hashes |
| **21** | `Seguranca-em-Nuvem` | Responsabilidade Compartilhada e CSPM | Trilha 5: Especialidades | Protect | Auditor de permissões S3 e políticas IAM Cloud |
| **22** | `DevSecOps-e-CI-CD` | Shift-Left, SAST, DAST, SCA e Containers | Trilha 5: Especialidades | Protect | Simulador de pipeline CI/CD com security gates |
| **23** | `Seguranca-em-IoT-e-OT` | Redes Industriais (SCADA/Modbus) e IoT | Trilha 5: Especialidades | Protect | Mapeador do Modelo Purdue (TI vs TO) |
| **24** | `IA-e-Ciberseguranca` | Ameaças a LLMs (OWASP LLM), Deepfakes e Defesa | Trilha 5: Especialidades | Protect / Detect | Lab de Prompt Injection e defesas |
| **25** | `Gestao-de-Riscos-TI` | ISO 31000 e Avaliação Qualitativa vs Quantitativa (ALE/SLE) | Trilha 6: Governança & Riscos | Govern / Identify | Calculadora de matriz 5x5 e risco financeiro |
| **26** | `ISO-27001-e-27002` | SGSI, Anexo A, CIS Controls e NIST 800-53 | Trilha 6: Governança & Riscos | Govern | Matriz de Controles e Declaração de Aplicabilidade |
| **27** | `LGPD-e-Privacidade` | Bases Legais, Direitos do Titular e RIPD/DPIA | Trilha 6: Governança & Riscos | Govern / Protect | Construtor de Avaliação de Impacto (RIPD) |
| **28** | `Continuidade-e-Disaster-Recovery` | BCP, DRP, Cálculo de RTO/RPO e Regra 3-2-1 | Trilha 6: Governança & Riscos | Recover | Calculadora de RTO/RPO e estratégia 3-2-1 |
| **29** | `Protecao-de-Dados-e-Conteudo` | DLP, AntiSpam e Filtro de Conteúdo | Trilha 2: Segurança Defensiva | Protect / Detect | Gateway de Conteúdo |
| **30** | `Seguranca-de-Bancos-de-Dados` | Bancos de Dados Relacionais: SQL, Privilégios e Auditoria | Trilha 2: Segurança Defensiva | Protect / Detect | Matriz GRANT/REVOKE |
| **31** | `PCI-DSS` | PCI DSS v4.0.1: Escopo CDE e os 12 Requisitos | Trilha 6: Governança & Riscos | Govern / Protect | Delimitador de Escopo CDE |
| **32** | `Ingles-Tecnico-Ciber` | Inglês Técnico para Segurança da Informação | Trilha 7: Carreira & Formação | Protect | Leitor de Advisory |
| **33** | `Certificacoes-e-Carreira` | Formação, Certificações e Carreira | Trilha 7: Carreira & Formação | Protect | Planejador de Certificações |
| **34** | `Linux-para-Seguranca` | Linux para Segurança: Shell, Permissões e Logs | Trilha 8: Ferramentas & Automação | Protect / Detect | Terminal de Investigação Linux |
| **35** | `Python-para-Seguranca` | Python para Segurança: Automação, Regex e Parsing | Trilha 8: Ferramentas & Automação | Detect | Montador de Detector |
| **36** | `PowerShell-e-Windows-Interno` | PowerShell, Event Log e Registro do Windows | Trilha 8: Ferramentas & Automação | Detect | Visualizador de Eventos |
| **37** | `Laboratorio-Domestico-e-Portfolio` | Laboratório Doméstico, CTFs e Portfólio | Trilha 8: Ferramentas & Automação | Protect | Planejador de Homelab |
| **38** | `Active-Directory-Fundamentos` | Active Directory: Domínios, GPO e Kerberos | Trilha 9: Identidade & AD | Protect | Kerberos Passo a Passo |
| **39** | `Ataques-e-Defesa-no-AD` | Ataques ao AD e Detecção: Kerberoasting, Pass-the-Hash e DCSync | Trilha 9: Identidade & AD | Protect / Detect | Mapa de Caminhos de Ataque |
| **40** | `PAM-e-Acessos-Privilegiados` | Gestão de Acessos Privilegiados (PAM) | Trilha 9: Identidade & AD | Protect | Auditor de Contas Privilegiadas |
| **41** | `Identidade-Hibrida-e-Nuvem` | Entra ID, Identidade Híbrida e Acesso Condicional | Trilha 9: Identidade & AD | Protect | Avaliador de Acesso Condicional |
| **42** | `Ransomware-Prevencao-a-Recuperacao` | Ransomware: Prevenção, Contenção e Recuperação | Trilha 10: Resiliência & Ransomware | Respond / Recover | Linha do Tempo do Ransomware |
| **43** | `Gestao-de-Crise-e-Comunicacao` | Gestão de Crise Cibernética e Comunicação de Incidentes | Trilha 10: Resiliência & Ransomware | Respond | Relógio da Crise |
| **44** | `Exercicios-Tabletop` | Exercícios Tabletop: Planejar, Conduzir e Avaliar | Trilha 10: Resiliência & Ransomware | Respond / Recover | Gerador de Tabletop |
| **45** | `Backup-Imutavel-e-Recuperacao` | Backup Imutável e Recuperação de Identidade | Trilha 10: Resiliência & Ransomware | Recover | Teste de Sobrevivência do Backup |
| **46** | `Engenharia-de-Deteccao` | Engenharia de Detecção: Detection-as-Code e Cobertura ATT&CK | Trilha 11: Detecção Avançada | Detect | Bancada de Detecções |
| **47** | `Threat-Hunting` | Threat Hunting: Caça por Hipótese e Linhas de Base | Trilha 11: Detecção Avançada | Detect | Caçada Guiada |
| **48** | `Monitoramento-de-Rede-NSM` | Monitoramento de Rede: Zeek, PCAP e NetFlow | Trilha 11: Detecção Avançada | Detect | Analisador de Conexões |
| **49** | `SOAR-e-Automacao-de-Resposta` | SOAR: Playbooks e Automação de Resposta | Trilha 11: Detecção Avançada | Respond | Montador de Playbook |
| **50** | `Seguranca-de-Containers` | Segurança de Containers: Imagens, Build e Runtime | Trilha 12: Nuvem & Kubernetes | Protect | Auditor de Dockerfile |
| **51** | `Seguranca-em-Kubernetes` | Segurança em Kubernetes: RBAC, Pod Security e NetworkPolicy | Trilha 12: Nuvem & Kubernetes | Protect | Cluster em Miniatura |
| **52** | `Infraestrutura-como-Codigo-Segura` | Infraestrutura como Código Segura: Terraform e Policy-as-Code | Trilha 12: Nuvem & Kubernetes | Protect | Revisor de Plano Terraform |
| **53** | `Deteccao-e-Resposta-em-Nuvem` | Detecção e Resposta a Incidentes em Nuvem | Trilha 12: Nuvem & Kubernetes | Detect / Respond | Conta Comprometida |
| **54** | `Regulacao-Setor-Financeiro` | Regulação Cibernética do Setor Financeiro | Trilha 13: Setor Regulado BR | Govern | Verificador de Aderência |
| **55** | `Fraude-em-Pagamentos-e-Pix` | Fraude em Pagamentos: Pix, Golpes e Antifraude | Trilha 13: Setor Regulado BR | Detect / Protect | Mesa Antifraude |
| **56** | `Legislacao-e-Crimes-Ciberneticos` | Legislação Brasileira e Crimes Cibernéticos | Trilha 13: Setor Regulado BR | Govern | Enquadramento de Casos |
| **57** | `Gestao-de-Riscos-de-Terceiros` | Gestão de Riscos de Terceiros e Fornecedores | Trilha 13: Setor Regulado BR | Govern | Avaliador de Fornecedores |

---

## 🎯 Rota por Vaga: Analista de Segurança da Informação

O portal (`index.html`) traz a seção **Rota por Vaga**, que liga cada requisito de uma vaga de Analista de Segurança da Informação aos módulos que o cobrem (principais e de apoio):

| Competência da vaga | Módulos principais | Módulos de apoio |
|---|---|---|
| Soluções de Cyber Security (Firewalls, Antivírus, DLP, AntiSpam, WAF, Filtro de conteúdo) | 05, 07, 10, 29 | 15, 34, 36 |
| Banco de dados relacionais | 30 | 12 |
| Inglês | 32 | — |
| PCI-DSS, ISO 27001/27002, ISO 31000 e NIST | 25, 26, 31 | 18 |
| Resposta a incidentes | 18 | 16, 19, 42, 43 |
| Controles de segurança da informação | 26 | 06, 08, 38, 40 |
| Formação e certificações | 33 | 37 |

O portal também exibe a **Matriz de Certificações** (CEH, CISM, CISSP, CCSP, GSEC e Security+), com os módulos que cobrem cada uma.

---

## 🛠️ Como o Material é Gerado

A plataforma utiliza um pipeline de compilação em Python puro e Shell Script, localizado na pasta `_geradores/`.

### Fluxo do Pipeline de Compilação

```mermaid
flowchart LR
    subgraph Fontes["Arquivos Fonte (_geradores/)"]
        direction TB
        B["_body.html<br>(Fragmentos e Labs)"]
        E["estudos.txt<br>(Catálogo e Metadados)"]
        A["base.css & base.js<br>(Design System e Engine)"]
    end

    subgraph Compilacao["Pipeline de Compilação"]
        direction TB
        M["montar.py<br>(Injeção de Assets e Validação)"]
        D["diagramas.py<br>(Renderização SVG Mermaid + Cache)"]
        M <--> D
    end

    subgraph Saida["Entrega Offline Standalone"]
        direction TB
        H["treinamento-*.html<br>(57 Módulos 100% Offline)"]
        I["index.html<br>(Portal Central Dinâmico)"]
    end

    B --> M
    E --> M
    A --> M
    M --> H
    E --> I
```

### Estrutura do Pipeline

- `_geradores/estudos.txt`: Catálogo canônico dos 57 estudos com metadados estruturais (slug, título, pasta, arquivo HTML, número da trilha, cor do tema e função NIST CSF 2.0).
- `_geradores/CURRICULO.md`: Matriz pedagógica detalhada com competências, pré-requisitos e especificações de cada simulador interativo.
- `_geradores/GUIA-DO-AUTOR.md`: Manual editorial e técnico para criação de novos módulos ou expansão de conteúdo.
- `_geradores/base.css` e `_geradores/base.js`: Design System responsivo com suporte a temas claro e escuro, além de controladores de quizzes, checklists e utilitários de simulação.
- `_geradores/montar.py`: Compilador que processa fragmentos HTML (`*_body.html`) e injeta os assets necessários, gerando treinamentos autossuficientes.
- `_geradores/index_dados.py` & `_geradores/build_index.py`: Motor de compilação do portal mestre `index.html`.
- `_geradores/gerar.sh`: Script CLI mestre para execução ágil das rotinas de compilação.

### Comandos do CLI (`_geradores/gerar.sh`)

O script `_geradores/gerar.sh` é o ponto de entrada para desenvolvimento e manutenção:

```bash
# 1. Regenerar apenas o portal raiz (index.html):
./_geradores/gerar.sh portal

# 2. Compilar todos os módulos disponíveis e atualizar o portal index.html:
./_geradores/gerar.sh todos

# 3. Compilar um módulo específico e atualizar o portal index.html:
./_geradores/gerar.sh Fundamentos-Ciber
# ou
./_geradores/gerar.sh redes_e_protocolos

# 4. Exibir o menu de ajuda com todos os comandos:
./_geradores/gerar.sh help
```

### Execução dos Testes Automatizados

O repositório inclui uma suíte abrangente de testes automatizados com `unittest`:

```bash
# Executa todos os testes do pipeline:
python3 -m unittest discover -s _geradores/testes -v
```

---

## 🧭 Perfis de Carreira Atendidos

O currículo é estruturado de forma a atender diferentes objetivos e momentos de carreira:

- **Blue Team & Defesa Ativa:** Módulos de redes, bastionamento Linux/Windows, firewalls, Zero Trust, EDR e detecção de ameaças; Linux e PowerShell para investigação (Trilha 8), Active Directory e detecção de ataques ao AD (Trilha 9) e ransomware (Trilha 10).
- **Red Team & Testes de Invasão:** Técnicas de reconhecimento OSINT, OWASP Top 10 Web, segurança de APIs e metodologias de pentest; Linux e caminhos de ataque no Active Directory (Trilhas 8 e 9).
- **Operações, SOC & Forense:** Análise de logs SIEM, regras Sigma, inteligência de ameaças (CTI), resposta a incidentes e análise básica de malware.
- **Engenharia de Nuvem & DevSecOps:** Segurança em provedores cloud (AWS/Azure/GCP), pipelines CI/CD seguros, conteinerização e IoT/TO.
- **Governança, Riscos e Conformidade (GRC):** Metodologias de avaliação de risco (ALE/SLE), ISO/IEC 27001/27002:2022, LGPD e planos de continuidade/DRP; acessos privilegiados (PAM), gestão de crise e exercícios tabletop (Trilhas 9 e 10).
- **Analista de Segurança da Informação:** Perfil generalista de vaga corporativa: soluções de segurança (firewall, EDR, DLP), bancos de dados, normas (PCI-DSS, ISO 27001/27002/31000, NIST), controles, resposta a incidentes, inglês técnico e certificações.

---

## 👤 Autor e Créditos

- **Autor:** José Mauro da Silva Stelling
- **Metodologia de Engenharia:** Superpowers Spec-Driven Development (SDD)
- **Idioma:** Português do Brasil (pt-BR)
- **Licença:** Material de uso pessoal, educacional e profissional.
