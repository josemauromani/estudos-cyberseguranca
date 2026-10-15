# Matriz Curricular: Estudos de Cibersegurança

## 1. Visão Geral e Filosofia Pedagógica

O currículo de **Estudos de Cibersegurança** foi concebido como uma formação autoinstrucional, prática e modular, dividida em **33 módulos temáticos** organizados em **7 trilhas estruturantes**. 

O projeto segue quatro diretrizes fundamentais:
1. **Teoria Pragmática e Direta ao Ponto:** Eliminação de floreios acadêmicos desnecessários; foco no que engenheiros, analistas e auditores de segurança executam na rotina corporativa e no que bancas de concursos e certificações (CompTIA Security+, CySA+, PenTest+, CEH, CISSP) cobram.
2. **Interatividade 100% Offline e Standalone:** Cada módulo consolida sua teoria com checklists gravados localmente (`localStorage`), quizzes de fixação comentados e **simuladores práticos em JavaScript puro (Vanilla JS)** executáveis diretamente no navegador sem servidores backend nem dependências pesadas.
3. **Duplo Mapeamento Normativo:** Integração orgânica entre a pedagogia por trilhas temáticas e os frameworks internacionais:
   - **NIST Cybersecurity Framework (CSF) 2.0:** Govern, Identify, Protect, Detect, Respond, Recover.
   - **MITRE ATT&CK Matrix:** Táticas e técnicas reais de adversários cibernéticos.
4. **Alinhamento a Perfis de Carreira:** Blue Team / Defesa, Red Team / Pentest, Engenharia de Nuvem & DevSecOps, Resposta a Incidentes / SOC, Governança, Risco e Conformidade (GRC) e Analista de Segurança da Informação (perfil generalista de vaga corporativa).

---

## 2. Mapa das 7 Trilhas Temáticas

| Trilha | Denominação | Cor do Tema | Foco Técnico | Módulos |
|---|---|---|---|---|
| **Trilha 1** | Fundamentos & Redes | `#2563EB` (Azul) | Base sólida: CIA, protocolos, criptografia, IAM e perímetro | 01 ao 05 |
| **Trilha 2** | Segurança Defensiva | `#059669` (Verde) | Bastionamento, defesas de rede, Zero Trust, vulnerabilidades e EDR | 06 ao 10, 29, 30 |
| **Trilha 3** | Segurança Ofensiva | `#DC2626` (Vermelho) | Reconhecimento, falhas web, APIs, testes de intrusão e phishing | 11 ao 15 |
| **Trilha 4** | Operações, SOC & Resposta | `#7C3AED` (Roxo) | Monitoramento, SIEM, CTI, contenção de incidentes e forense | 16 ao 20 |
| **Trilha 5** | Especialidades & Fronteiras | `#0891B2` (Ciano) | Nuvem pública, DevSecOps/CI-CD, IoT/TO (Purdue) e Inteligência Artificial | 21 ao 24 |
| **Trilha 6** | Governança, Riscos & Conformidade | `#D97706` (Âmbar) | Gestão de risco (ALE/SLE), ISO 27001/27002, LGPD e continuidade de negócios | 25 ao 28, 31 |
| **Trilha 7** | Carreira & Formação | `#DB2777` (Rosa) | Inglês técnico, formação acadêmica, certificações e preparação para vagas | 32 e 33 |

---

## 3. Detalhamento dos 33 Módulos de Aprendizagem

### Trilha 1: Fundamentos & Redes (`#2563EB`)

#### 01. Fundamentos-Ciber
- **Título:** Tríade CIA, Ameaças e Modelagem STRIDE
- **Função NIST CSF 2.0:** *Identify (ID)*
- **Tempo Estimado:** 40 minutos | **Carreiras:** Todas (Fundação Universal)
- **Objetivos de Aprendizagem:** Compreender os pilares da segurança (Confidencialidade, Integridade, Disponibilidade, Autenticidade, Não-repúdio); categorizar vetores de ameaça; aplicar a metodologia de modelagem de ameaças da Microsoft (STRIDE).
- **Pré-requisitos:** Nenhum.
- **Conceitos-Chave:** Confidencialidade vs Criptografia, Hashing vs Integridade, SLA vs Disponibilidade, Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege.
- **Simulador Interativo em JS:** *STRIDE Threat Canvas* — Quadro interativo onde o estudante seleciona componentes de um sistema (banco de dados, API, usuário, link de rede) e mapeia ameaças STRIDE correspondentes com controles mitigatórios sugeridos.

#### 02. Redes-e-Protocolos
- **Título:** TCP/IP, DNS, Roteamento e Inspeção de Tráfego
- **Função NIST CSF 2.0:** *Protect (PR) / Detect (DE)*
- **Tempo Estimado:** 50 minutos | **Carreiras:** Blue Team, Red Team, SOC
- **Objetivos de Aprendizagem:** Dominar a pilha TCP/IP (camadas 2 a 7); dissecar cabeçalhos IPv4/IPv6, TCP (flags SYN/ACK/FIN/RST) e UDP; analisar resoluções DNS e envenenamento de cache; compreender a estrutura de pacotes para análise forense e detecção de anomalias.
- **Pré-requisitos:** Fundamentos-Ciber.
- **Conceitos-Chave:** 3-Way Handshake, TCP Flags, TTL, DNS Recursivo vs Autoritativo, ARP Spoofing, MTU e fragmentação.
- **Simulador Interativo em JS:** *Inspetor Visual de Cabeçalhos IP/TCP/UDP* — Permite ao aluno manipular flags TCP, endereços e portas, visualizando os bytes brutos do cabeçalho e a reação simulada do host de destino (ex.: porta aberta SYN-ACK vs fechada RST-ACK).

#### 03. Criptografia-Pratica
- **Título:** Criptografia Simétrica, Assimétrica, Hashes e PKI
- **Função NIST CSF 2.0:** *Protect (PR)*
- **Tempo Estimado:** 45 minutos | **Carreiras:** Blue Team, AppSec, GRC
- **Objetivos de Aprendizagem:** Diferenciar cifras de bloco e de fluxo (AES vs ChaCha20); dominar troca de chaves Diffie-Hellman e RSA; entender funções de resumo criptográfico (SHA-256, HMAC); compreender a cadeia de confiança de Certificados Digitais X.509 e PKI.
- **Pré-requisitos:** Redes-e-Protocolos.
- **Conceitos-Chave:** AES-GCM, RSA-2048/4096, Curvas Elípticas (ECDSA, Ed25519), Salting, Hash Colisões, CA Raiz, CRL e OCSP Stapling.
- **Simulador Interativo em JS:** *Lab de Cifras (Web Crypto API)* — Gera chaves simétricas AES-GCM e resumos SHA-256 diretamente no navegador utilizando a API criptográfica nativa, demonstrando o efeito avalanche de hashes e decifrações com chave errada.

#### 04. Autenticacao-e-IAM
- **Título:** Senhas, MFA, OAuth 2.0, Tokens JWT e RBAC
- **Função NIST CSF 2.0:** *Protect (PR)*
- **Tempo Estimado:** 45 minutos | **Carreiras:** AppSec, Blue Team, Cloud/DevSecOps
- **Objetivos de Aprendizagem:** Projetar controles de identidade e controle de acesso; implementar autenticação multifator (TOTP/FIDO2); decodificar e validar tokens JSON Web Token (JWT); comparar RBAC (Role-Based) com ABAC (Attribute-Based).
- **Pré-requisitos:** Criptografia-Pratica.
- **Conceitos-Chave:** Hashing de senhas (Argon2, bcrypt), TOTP RFC 6238, FIDO2/WebAuthn, JWT Header/Payload/Signature, None Algorithm Attack, Principle of Least Privilege.
- **Simulador Interativo em JS:** *Validador e Decodificador JWT + Matriz RBAC* — Decodifica tokens JWT em tempo real, permite alterar claims e simular ataques de assinatura inválida ou algoritmo 'none', testando permissões de acesso em matriz de perfis RBAC.

#### 05. Segmentacao-e-Firewall
- **Título:** DMZ, VLANs, Regras de Firewall e Filtragem
- **Função NIST CSF 2.0:** *Protect (PR)*
- **Tempo Estimado:** 40 minutos | **Carreiras:** Blue Team, Engenharia de Redes
- **Objetivos de Aprendizagem:** Desenhar arquiteturas de rede seguras com zonas desmilitarizadas (DMZ) e VLANs (802.1Q); formular regras de firewall de filtragem de pacotes e stateful inspection; entender a ordem de precedência das regras (First-Match).
- **Pré-requisitos:** Redes-e-Protocolos.
- **Conceitos-Chave:** Stateful vs Stateless, Tabela de Estados Conntrack, Regra Default Drop, DMZ de dois estágios, Trunking 802.1Q e isolamento inter-VLAN.
- **Simulador Interativo em JS:** *Simulador de Regras de Firewall (Pass / Drop)* — Console interativo onde o aluno cadastra regras de firewall (ordem, IP origem/destino, porta, ação) e dispara pacotes de teste para visualizar qual regra capturou o pacote e a razão da decisão.

---

### Trilha 2: Segurança Defensiva (`#059669`)

#### 06. Hardening-Sistemas
- **Título:** Bastionamento Linux e Windows (CIS Benchmarks)
- **Função NIST CSF 2.0:** *Protect (PR)*
- **Tempo Estimado:** 50 minutos | **Carreiras:** Blue Team, SysAdmin, DevSecOps
- **Objetivos de Aprendizagem:** Aplicar diretrizes CIS Benchmarks em ambientes operacionais; desativar serviços e portas desnecessárias; configurar `/etc/ssh/sshd_config` restritivo, PAM, AppArmor/SELinux e Group Policies (GPO) do Windows.
- **Pré-requisitos:** Fundamentos-Ciber, Redes-e-Protocolos.
- **Conceitos-Chave:** CIS Level 1 e Level 2, Umask, Rootless containers, SSH Key-only + fail2ban, Windows Defender Exploit Guard, PowerShell Constrained Language Mode.
- **Simulador Interativo em JS:** *Auditor Interativo de Configuração de Servidor* — Analisa snippets de configuração de sistemas (`sshd_config`, `sysctl.conf`, `GPO`) e aponta vulnerabilidades em conformidade com as recomendações dos CIS Benchmarks.

#### 07. Seguranca-de-Redes-Defesa
- **Título:** IDS/IPS, WAF, VPNs e Proxies Reversos
- **Função NIST CSF 2.0:** *Protect (PR) / Detect (DE)*
- **Tempo Estimado:** 50 minutos | **Carreiras:** Blue Team, SOC, Engenharia de Redes
- **Objetivos de Aprendizagem:** Compreender a atuação de sistemas de detecção e prevenção de intrusão (Snort, Suricata); configurar Web Application Firewalls (ModSecurity, AWS WAF); estabelecer túneis VPN seguros (IPsec IKEv2, WireGuard, OpenVPN).
- **Pré-requisitos:** Segmentacao-e-Firewall.
- **Conceitos-Chave:** Assinaturas vs Anomalias heurísticas, PCRE em regras IDS, WAF Core Rule Set (CRS), MTLS em proxies reversos, WireGuard Noise Protocol.
- **Simulador Interativo em JS:** *Analisador de Regras Snort/Suricata vs Tráfego* — Mostra payloads de rede de teste sendo avaliados por uma lista de regras de IDS, demonstrando alertas gerados, extração de variáveis (`content`, `nocase`, `sid`) e mitigação.

#### 08. Arquitetura-Zero-Trust
- **Título:** Princípios Zero Trust e Microsegmentação
- **Função NIST CSF 2.0:** *Protect (PR)*
- **Tempo Estimado:** 40 minutos | **Carreiras:** Blue Team, Arquitetura de TI, GRC
- **Objetivos de Aprendizagem:** Dominar os 3 pilares NIST SP 800-207: "Never trust, always verify", "Assume breach" e "Verify explicitly"; implementar Policy Decision Points (PDP) e Policy Enforcement Points (PEP); planejar microsegmentação por workload.
- **Pré-requisitos:** Autenticacao-e-IAM, Segmentacao-e-Firewall.
- **Conceitos-Chave:** NIST SP 800-207, ZTNA (Zero Trust Network Access), Postura de Dispositivo (Device Health/Compliance), Context-aware Access, SDP (Software-Defined Perimeter).
- **Simulador Interativo em JS:** *Motor de Decisão de Acesso Zero Trust (PDP/PEP)* — O aluno define parâmetros de contexto (horário, IP da requisição, conformidade do dispositivo, cargo do usuário) e simula a pontuação de risco e a decisão de acesso (Permitir, Bloquear, Exigir MFA adicional).

#### 09. Gestao-de-Vulnerabilidades
- **Título:** CVE, CVSS v3.1/v4.0 e Priorização de Patches
- **Função NIST CSF 2.0:** *Identify (ID) / Protect (PR)*
- **Tempo Estimado:** 45 minutos | **Carreiras:** Blue Team, GRC, SOC
- **Objetivos de Aprendizagem:** Entender o ciclo de vida de vulnerabilidades (descoberta, atribuição de CVE, divulgação responsável); calcular scores CVSS v3.1 e entender novidades do CVSS v4.0; correlacionar CVSS com EPSS (Exploit Prediction Scoring System) e CISA KEV (Known Exploited Vulnerabilities).
- **Pré-requisitos:** Hardening-Sistemas.
- **Conceitos-Chave:** Base Score vs Temporal vs Environmental, Vetores de ataque (AV, AC, PR, UI, S, C, I, A), EPSS score, CISA KEV Catalog, SLA de correção por severidade.
- **Simulador Interativo em JS:** *Calculadora Interativa de Score CVSS v3.1 / v4.0* — Permite ao aluno selecionar métricas de ataque (Vetor de Ataque, Complexidade, Privilégios, Impacto) e calcula dinamicamente o score base de 0.0 a 10.0 com a string de vetor correspondente.

#### 10. Seguranca-em-Endpoints-EDR
- **Título:** Antivírus, EDR/XDR e Proteção de Host
- **Função NIST CSF 2.0:** *Protect (PR) / Detect (DE)*
- **Tempo Estimado:** 45 minutos | **Carreiras:** Blue Team, SOC, Incident Response
- **Objetivos de Aprendizagem:** Comparar antivírus tradicional baseado em assinatura com EDR (Endpoint Detection and Response) comportamental; compreender telemetria de host (Sysmon, Event ID do Windows, auditd no Linux); entender árvore de processos maliciosos (`parent-child`).
- **Pré-requisitos:** Hardening-Sistemas.
- **Conceitos-Chave:** Heurística e ML no host, Sysmon Event ID 1 (Process Create), Event ID 3 (Network Connect), Process Injection, LSASS dumping detecção, Isolamento de host em rede.
- **Simulador Interativo em JS:** *Linha do Tempo de Telemetria e Detecção EDR* — Simula eventos de um endpoint atacado (Office disparando PowerShell, conexão de rede externa, modificação de registro) e permite ao analista identificar anomalias e executar a ação de isolamento de host.

#### 29. Protecao-de-Dados-e-Conteudo
- **Título:** DLP, AntiSpam e Filtro de Conteúdo
- **Função NIST CSF 2.0:** *Protect (PR) / Detect (DE)*
- **Tempo Estimado:** 50 minutos | **Carreiras:** Blue Team, SOC, GRC, Analista de Segurança da Informação
- **Objetivos de Aprendizagem:** Diferenciar DLP de rede, de endpoint e de nuvem (CASB); construir detectores por padrão (regex), por checksum (Luhn) e por dicionário; explicar a autenticação de e-mail (SPF, DKIM, DMARC) e a filtragem antispam por reputação e conteúdo; configurar filtro de conteúdo e URL por categoria em proxy seguro (SWG).
- **Pré-requisitos:** Redes-e-Protocolos, Seguranca-de-Redes-Defesa.
- **Conceitos-Chave:** Dados em uso, em trânsito e em repouso, Classificação da informação, Falso positivo vs falso negativo em DLP, Quarentena, Políticas DMARC (`none`, `quarantine`, `reject`), SWG, Categorização de URL, Inspeção TLS.
- **Simulador Interativo em JS:** *Gateway de Conteúdo* — O aluno escolhe ou edita uma mensagem de e-mail ou um upload web de exemplo, que passa por três estágios em sequência: AntiSpam (SPF, DKIM, DMARC e reputação do remetente), DLP (detectores de CPF com dígito verificador, cartão de pagamento com Luhn e palavras-chave configuráveis) e Filtro de URL (bloqueio por categoria do domínio). O resultado final é Permitir, Quarentena ou Bloquear, com a justificativa de cada estágio, e o aluno pode alterar políticas e limiares e reprocessar.

#### 30. Seguranca-de-Bancos-de-Dados
- **Título:** Bancos de Dados Relacionais: SQL, Privilégios e Auditoria
- **Função NIST CSF 2.0:** *Protect (PR) / Detect (DE)*
- **Tempo Estimado:** 50 minutos | **Carreiras:** Blue Team, AppSec, GRC, Analista de Segurança da Informação
- **Objetivos de Aprendizagem:** Revisar o modelo relacional (tabelas, chaves, JOIN, normalização) e SQL DDL/DML/DCL; aplicar menor privilégio com roles, `GRANT`/`REVOKE`, views e Row-Level Security; configurar auditoria de banco; proteger dados com TDE, criptografia de coluna, mascaramento dinâmico e backups cifrados; prevenir SQLi com prepared statements.
- **Pré-requisitos:** Autenticacao-e-IAM, Criptografia-Pratica.
- **Conceitos-Chave:** ACID, DDL vs DML vs DCL, Roles e esquemas, RLS, TDE, Dynamic Data Masking, Auditoria nativa (pgAudit, SQL Server Audit), Database Activity Monitoring (DAM), Contas de serviço, Hardening de SGBD (CIS Benchmarks para PostgreSQL, MySQL e SQL Server).
- **Simulador Interativo em JS:** *Matriz GRANT/REVOKE* — Um esquema fictício com 3 a 4 tabelas, roles e usuários. O aluno concede e revoga privilégios (`SELECT`, `INSERT`, `UPDATE`, `DELETE`) por role e tabela e então executa uma lista de consultas de usuários fictícios. Cada consulta é marcada como permitida ou negada, gera uma entrada na trilha de auditoria e, quando houver mascaramento ativo, mostra o valor mascarado.

---

### Trilha 3: Segurança Ofensiva (`#DC2626`)

#### 11. Reconhecimento-e-OSINT
- **Título:** Superfície de Ataque, DNS, WHOIS e Shodan
- **Função NIST CSF 2.0:** *Identify (ID)*
- **Tempo Estimado:** 45 minutos | **Carreiras:** Red Team, Threat Intelligence
- **Objetivos de Aprendizagem:** Mapear a superfície de ataque externa de uma organização usando inteligência de fontes abertas (OSINT); consultar registros DNS, WHOIS, certificados SSL (Certificate Transparency Logs); pesquisar ativos expostos em Shodan e Censys de forma ética.
- **Pré-requisitos:** Redes-e-Protocolos.
- **Conceitos-Chave:** Reconhecimento passivo vs ativo, Dorks do Google, Subdomain Takeover, Shodan dorks (`org:`, `port:`, `vuln:`), Metadados em documentos (ExifTool).
- **Simulador Interativo em JS:** *Terminal Simulado de OSINT e Enumeração* — Terminal interativo com comandos simulados (`whois`, `dig`, `crtsh`, `shodan_search`) para mapear alvos corporativos fictícios e descobrir subdomínios e portas desprotegidas.

#### 12. OWASP-Top-10-Web
- **Título:** Falhas Web (SQLi, XSS, CSRF, Broken Auth)
- **Função NIST CSF 2.0:** *Protect (PR)*
- **Tempo Estimado:** 55 minutos | **Carreiras:** AppSec, Red Team, Desenvolvedores
- **Objetivos de Aprendizagem:** Identificar e mitigar as principais vulnerabilidades em aplicações web de acordo com a lista oficial da OWASP; entender injeções SQL (clássica, cega, baseada em tempo); dominar cross-site scripting (Reflected, Stored, DOM); prevenir broken object level authorization (BOLA) e CSRF.
- **Pré-requisitos:** Autenticacao-e-IAM.
- **Conceitos-Chave:** OWASP Top 10 A01-A10, Prepared Statements / Parametrização, Content Security Policy (CSP), SameSite Cookies, Sanitização vs Encoding de saída.
- **Simulador Interativo em JS:** *Playground de Injeção e Sanitização Web* — Interface com campos vulneráveis (busca vulnerável a SQLi, comentários com XSS) onde o aluno digita payloads de teste, observa o impacto no DOM ou na query simulada, e ativa filtros sanitizadores para validar a correção.

#### 13. Seguranca-em-APIs
- **Título:** OWASP API Security, Rate Limiting e Tokens
- **Função NIST CSF 2.0:** *Protect (PR)*
- **Tempo Estimado:** 40 minutos | **Carreiras:** AppSec, DevSecOps, Backend Devs
- **Objetivos de Aprendizagem:** Analisar os 10 riscos críticos em APIs (OWASP API Security Top 10); proteger endpoints contra Broken Object Level Authorization (BOLA/IDOR); implementar algoritmos de rate limiting (Token Bucket, Leaky Bucket); validar esquemas e payloads JSON.
- **Pré-requisitos:** Autenticacao-e-IAM, OWASP-Top-10-Web.
- **Conceitos-Chave:** API1:2023 Broken Object Level Authorization, API2 Broken Authentication, Token Bucket Algorithm, API Gateways, Mass Assignment, GraphQL vs REST Security.
- **Simulador Interativo em JS:** *Simulador de Chamadas de API com Rate Limiter* — Permite disparar requisições para endpoints REST simulados, configurando headers de autorização e observando o bloqueio por HTTP 429 (Too Many Requests) e HTTP 403 por quebra de BOLA.

#### 14. Pentest-Metodologias
- **Título:** Fases do Pentest (PTES), Escopo e Relatório
- **Função NIST CSF 2.0:** *Identify (ID)*
- **Tempo Estimado:** 45 minutos | **Carreiras:** Red Team, Auditores, Consultores
- **Objetivos de Aprendizagem:** Compreender as fases formais do teste de invasão segundo o PTES (Pre-engagement, Intelligence Gathering, Threat Modeling, Vulnerability Analysis, Exploitation, Post-Exploitation, Reporting); definir regras de engajamento (RoE); redigir relatórios executivos e técnicos com recomendações acionáveis.
- **Pré-requisitos:** Reconhecimento-e-OSINT, OWASP-Top-10-Web.
- **Conceitos-Chave:** White-box vs Gray-box vs Black-box, Scope Creep, Rules of Engagement (RoE), Matriz de Risco do Achado, Sumário Executivo vs Detalhes de Reprodução Técnica.
- **Simulador Interativo em JS:** *Construtor de Matriz de Achados e Relatórios de Pentest* — Ferramenta onde o estudante cadastra vulnerabilidades encontradas durante um teste hipotético, atribui severidade e gera automaticamente a matriz de risco e a minuta de relatório executivo formatado.

#### 15. Engenharia-Social-e-Phishing
- **Título:** Pretexting, Spear Phishing e Defesas Humanas
- **Função NIST CSF 2.0:** *Protect (PR)*
- **Tempo Estimado:** 40 minutos | **Carreiras:** Red Team, Blue Team, Conscientização
- **Objetivos de Aprendizagem:** Reconhecer táticas psicológicas de engenharia social (urgência, autoridade, escassez, prova social); diferenciar phishing em massa de spear phishing e whaling; validar autenticação de e-mail (SPF, DKIM, DMARC); estruturar programas corporativos de conscientização e simulação controlada.
- **Pré-requisitos:** Fundamentos-Ciber.
- **Conceitos-Chave:** Pretexting, Vishing, Smishing, Typosquatting em domínios, SPF (`v=spf1`), DKIM selector e assinatura criptográfica, DMARC política (`p=reject`), Chaves de segurança física anti-phishing (FIDO2).
- **Simulador Interativo em JS:** *Analisador de E-mails Suspeitos (Spot the Indicators)* — Apresenta e-mails simulados na interface com cabeçalhos brutos e corpo visual; o estudante deve inspecionar e clicar nos indicadores de comprometimento (erros no cabeçalho `Return-Path`, links divergentes, spoofing de remetente, urgência forçada).

---

### Trilha 4: Operações, SOC & Resposta (`#7C3AED`)

#### 16. Operacoes-SOC-e-SIEM
- **Título:** Rotina de SOC L1/L2, Logs e Regras Sigma
- **Função NIST CSF 2.0:** *Detect (DE)*
- **Tempo Estimado:** 50 minutos | **Carreiras:** SOC Analyst, Blue Team
- **Objetivos de Aprendizagem:** Entender a operação de um Centro de Operações de Segurança (SOC); diferenciar níveis de suporte (N1 triagem, N2 investigação, N3 caça a ameaças); configurar ingestão e parsing de logs em SIEM (Elastic, Splunk); escrever e interpretar regras de detecção padronizadas no formato Sigma.
- **Pré-requisitos:** Hardening-Sistemas, Seguranca-em-Endpoints-EDR.
- **Conceitos-Chave:** MTTD (Mean Time to Detect), MTTR (Mean Time to Respond), Falsos Positivos vs Falsos Negativos, Normalização CEF/LEEF/ECS, Estrutura de regra Sigma (title, logsource, detection, condition).
- **Simulador Interativo em JS:** *Console SIEM com Busca de Logs e Alertas* — Painel com fluxo de eventos em tempo real onde o analista executa queries simuladas estilo KQL/Splunk e testa regras Sigma contra a base de logs para disparar alertas de segurança.

#### 17. Threat-Intelligence
- **Título:** IoCs, TTPs, MITRE ATT&CK e STIX/TAXII
- **Função NIST CSF 2.0:** *Identify (ID) / Detect (DE)*
- **Tempo Estimado:** 45 minutos | **Carreiras:** Threat Intel Analyst, SOC, Blue Team
- **Objetivos de Aprendizagem:** Aplicar a Pirâmide da Dor de David Bianco; diferenciar Indicadores de Comprometimento (IoCs) voláteis de Táticas, Técnicas e Procedimentos (TTPs) persistentes; navegar pela matriz MITRE ATT&CK para Enterprise; compreender os padrões de troca de inteligência STIX 2.1 e TAXII.
- **Pré-requisitos:** Operacoes-SOC-e-SIEM.
- **Conceitos-Chave:** Pyramid of Pain (Hash, IP, Domínio, Artefato, Ferramenta, TTP), ATT&CK Táticas (TA0001 a TA0040), Técnicas e Subtécnicas (T1059.001), STIX Objetos (Indicator, Threat Actor, Malware, Relationship), TAXII Collections.
- **Simulador Interativo em JS:** *Mapeador de IoCs e TTPs na Matriz ATT&CK* — Permite ao analista colar relatórios de inteligência, extrair IoCs e relacionar técnicas descritas às colunas da matriz MITRE ATT&CK, gerando mapa visual de calor de táticas do adversário.

#### 18. Resposta-a-Incidentes
- **Título:** Ciclo NIST SP 800-61 Rev. 2 e Rev. 3 (Contenção e Erradicação)
- **Função NIST CSF 2.0:** *Respond (RS)*
- **Tempo Estimado:** 50 minutos | **Carreiras:** Incident Responder, SOC N2/N3, Gestores
- **Objetivos de Aprendizagem:** Executar as 4 etapas do ciclo de incidentes do NIST SP 800-61 Rev 2: 1. Preparação, 2. Detecção & Análise, 3. Contenção, Erradicação & Recuperação, 4. Atividades Pós-Incidente (Lições Aprendidas); elaborar playbooks de resposta; gerenciar comunicação com stakeholders e órgãos reguladores; conhecer a NIST SP 800-61 Rev. 3 (2025), que reorganiza a resposta a incidentes segundo as funções do CSF 2.0, ao lado do ciclo clássico da Rev. 2.
- **Pré-requisitos:** Operacoes-SOC-e-SIEM.
- **Conceitos-Chave:** Contenção de curto vs longo prazo, Preservação de evidências voláteis antes do reboot, Erradicação de persistência de malware, Post-Mortem / Retrospectiva sem culpados (Blameless), NIST SP 800-61 Rev. 3 e funções do CSF 2.0.
- **Simulador Interativo em JS:** *Runbook Interativo em Árvore de Decisão* — Simula um incidente crítico de segurança (ex.: Ransomware em progressão ou vazamento de banco de dados). O usuário toma decisões passo a passo com ramificações em árvore e cronômetro de impacto no negócio.

#### 19. Forense-Digital
- **Título:** Cadeia de Custódia, Coleta de RAM e Artefatos
- **Função NIST CSF 2.0:** *Respond (RS)*
- **Tempo Estimado:** 45 minutos | **Carreiras:** Perito Forense, Incident Response, Jurídico
- **Objetivos de Aprendizagem:** Preservar a cadeia de custódia segundo a ISO/IEC 27037; respeitar a ordem de volatilidade de evidências digitais (RFC 3227); coletar cópias bit-a-bit com bloqueadores de escrita e conferência de hashes; extrair e analisar artefatos do Windows (Prefetch, Amcache, Shimcache, LNK, $MFT, Registro).
- **Pré-requisitos:** Hardening-Sistemas, Resposta-a-Incidentes.
- **Conceitos-Chave:** ISO/IEC 27037, RFC 3227 Ordem de Volatilidade (RAM, Swap, Disco, Logs remotos), Hashes de integridade (SHA-256), Write Blocker de hardware/software, Timeline Analysis (Super-timeline com Plaso).
- **Simulador Interativo em JS:** *Analisador de Timeline de Evidências e Logs Forenses* — Permite carregar e inspecionar linhas do tempo simuladas de eventos de múltiplos artefatos (criação de arquivos, execuções de Prefetch, conexões de rede), ordenando cronologicamente as ações de um invasor.

#### 20. Analise-Basica-de-Malware
- **Título:** Análise Estática vs Dinâmica e Sandboxes
- **Função NIST CSF 2.0:** *Detect (DE) / Respond (RS)*
- **Tempo Estimado:** 45 minutos | **Carreiras:** Malware Analyst, SOC N3, Incident Response
- **Objetivos de Aprendizagem:** Diferenciar análise de malware estática (sem execução) de dinâmica (em ambiente isolado); inspecionar cabeçalhos de arquivos executáveis (PE no Windows, ELF no Linux); extrair strings e funções importadas (IAT); interpretar relatórios de sandboxes automatizadas (Cuckoo, CAPEv2).
- **Pré-requisitos:** Criptografia-Pratica, Hardening-Sistemas.
- **Conceitos-Chave:** Hashes de arquivo (MD5, SHA-256, SSDEEP para fuzzy hashing), Seções do PE (.text, .data, .rsrc), Entropia de Shannon (detecção de packers/crypters), Imports maliciosos comuns (`VirtualAllocEx`, `WriteProcessMemory`, `CreateRemoteThread`).
- **Simulador Interativo em JS:** *Inspetor de Metadados PE/ELF e Hashes* — Analisador interativo que desmonta um arquivo binário simulado, exibindo seções, cálculo de entropia com indicação de empacotamento (UPX) e lista de chamadas da API do Windows para classificar a intenção do arquivo.

---

### Trilha 5: Especialidades & Fronteiras (`#0891B2`)

#### 21. Seguranca-em-Nuvem
- **Título:** Responsabilidade Compartilhada e CSPM
- **Função NIST CSF 2.0:** *Protect (PR)*
- **Tempo Estimado:** 45 minutos | **Carreiras:** Cloud Security Engineer, DevSecOps, Arquitetura
- **Objetivos de Aprendizagem:** Dominar o Modelo de Responsabilidade Compartilhada em IaaS, PaaS e SaaS nos provedores AWS, Azure e GCP; auditar e endurecer políticas de IAM e permissões em nuvem (Least Privilege); proteger buckets de armazenamento contra vazamentos públicos; entender ferramentas de CSPM (Cloud Security Posture Management) e CWPP.
- **Pré-requisitos:** Autenticacao-e-IAM, Hardening-Sistemas.
- **Conceitos-Chave:** Shared Responsibility Model, AWS IAM Policies (Effect, Principal, Action, Resource, Condition), Políticas de Bucket S3 (Block Public Access), Metadados de Instância (IMDSv2 vs SSRF), CIS Cloud Benchmarks.
- **Simulador Interativo em JS:** *Auditor de Permissões S3 e Políticas IAM Cloud* — Editor interativo de políticas JSON de nuvem onde o aluno avalia políticas de acesso e testa se a política permite ações perigosas (`s3:*`, `Principal: *`) ou atende aos princípios de mínimo privilégio.

#### 22. DevSecOps-e-CI-CD
- **Título:** Shift-Left, SAST, DAST, SCA e Containers
- **Função NIST CSF 2.0:** *Protect (PR)*
- **Tempo Estimado:** 45 minutos | **Carreiras:** DevSecOps, Engenharia de Software, AppSec
- **Objetivos de Aprendizagem:** Integrar segurança ao ciclo de vida de desenvolvimento (SSDLC / Shift-Left); posicionar ferramentas SAST (Static Analysis), DAST (Dynamic Analysis) e SCA (Software Composition Analysis) em pipelines CI/CD; aplicar boas práticas de segurança em Docker e Kubernetes (imagens enxutas, containers sem privilégios de root, assinatura com Sigstore/Cosign).
- **Pré-requisitos:** OWASP-Top-10-Web, Seguranca-em-APIs.
- **Conceitos-Chave:** Shift-Left Security, SAST vs DAST vs IAST, Vulnerabilidades em dependências (SCA, SBOM - CycloneDX/SPDX), Dockerfile seguro (`USER nonroot`, imagens distroless), Quality Gates de build.
- **Simulador Interativo em JS:** *Simulador de Pipeline CI/CD com Security Gates* — Interface que simula as etapas de uma esteira CI/CD (Lint, SAST, SCA, Testes, Deploy) com parametrização de thresholds de quebra de build baseados na gravidade de vulnerabilidades detectadas.

#### 23. Seguranca-em-IoT-e-OT
- **Título:** Redes Industriais (SCADA/Modbus) e IoT
- **Função NIST CSF 2.0:** *Protect (PR)*
- **Tempo Estimado:** 40 minutos | **Carreiras:** Segurança Industrial, Blue Team, Red Team
- **Objetivos de Aprendizagem:** Compreender a separação entre Tecnologia da Informação (TI) e Tecnologia da Operação (TO); navegar pelas camadas do Modelo Purdue para sistemas de controle industrial (ICS/SCADA); reconhecer a falta de autenticação e criptografia nativas em protocolos legados (Modbus, DNP3, BACnet); proteger dispositivos IoT com firmware seguro e isolamento de rede.
- **Pré-requisitos:** Redes-e-Protocolos, Segmentacao-e-Firewall.
- **Conceitos-Chave:** Modelo Purdue (Níveis 0 ao 5), SCADA vs CLP (PLC) vs IHM (HMI), Protocolo Modbus TCP (Porta 502), Ataques Stuxnet e Industroyer, Norma IEC 62443.
- **Simulador Interativo em JS:** *Mapeador do Modelo Purdue (TI vs TO)* — Diagrama arquitetural interativo onde o estudante posiciona sensores, PLCs, servidores SCADA, firewalls industriais e estações de trabalho nos níveis corretos do Modelo Purdue e visualiza regras de tráfego permitidas entre zonas.

#### 24. IA-e-Ciberseguranca
- **Título:** Ameaças a LLMs (OWASP LLM), Deepfakes e Defesa
- **Função NIST CSF 2.0:** *Protect (PR) / Detect (DE)*
- **Tempo Estimado:** 45 minutos | **Carreiras:** Engenheiros de IA, AppSec, Blue Team
- **Objetivos de Aprendizagem:** Identificar os 10 riscos críticos em aplicações de Inteligência Artificial Generativa segundo o OWASP Top 10 for LLM Applications; entender ataques de Prompt Injection (direto e indireto) e Data Poisoning; analisar o impacto de Deepfakes de áudio e vídeo na engenharia social; utilizar IA defensiva para triagem de alertas e análise preditiva.
- **Pré-requisitos:** Fundamentos-Ciber, OWASP-Top-10-Web.
- **Conceitos-Chave:** OWASP LLM01: Prompt Injection, LLM02: Sensitive Information Disclosure, LLM06: Excessive Agency, Guardrails de entrada e saída, Detecção de Deepfake, IA em operações defensivas.
- **Simulador Interativo em JS:** *Lab de Prompt Injection e Defesas* — Simula um chatbot de atendimento corporativo integrado a ferramentas internas. O aluno testa técnicas de injeção de prompt para tentar extrair segredos do sistema e depois ativa guardrails com regex e sanitização para bloquear o bypass.

---

### Trilha 6: Governança, Riscos & Conformidade (`#D97706`)

#### 25. Gestao-de-Riscos-TI
- **Título:** ISO 31000 e Avaliação Qualitativa vs Quantitativa (ALE/SLE)
- **Função NIST CSF 2.0:** *Govern (GV) / Identify (ID)*
- **Tempo Estimado:** 45 minutos | **Carreiras:** GRC, Auditores, CISO, Gestores
- **Objetivos de Aprendizagem:** Conduzir análises de risco qualitativas utilizando matrizes de probabilidade e impacto (5x5); dominar cálculos quantitativos de risco financeiro: Valor do Ativo (AV), Fator de Exposição (EF), Expectativa de Perda Única (SLE = AV * EF), Taxa Anualizada de Ocorrência (ARO) e Expectativa de Perda Anualizada (ALE = SLE * ARO); justificar o Retorno sobre Investimento em Segurança (ROSI); aplicar os princípios, a estrutura e o processo da ISO 31000:2018 (contexto, identificação, análise, avaliação, tratamento, monitoramento e comunicação).
- **Pré-requisitos:** Fundamentos-Ciber.
- **Conceitos-Chave:** ISO 31000:2018 (princípios, estrutura e processo), NIST SP 800-30, Matriz Qualitativa 5x5, Fórmulas de cálculo de SLE e ALE, Estratégias de tratamento de risco: Mitigar, Aceitar, Transferir, Evitar.
- **Simulador Interativo em JS:** *Calculadora de Matriz 5x5 e Risco Financeiro (ALE/SLE)* — Permite ao aluno posicionar cenários de risco na matriz qualitativa e calcular automaticamente valores financeiros de impacto anualizado com simulação de viabilidade econômica de contramedidas (Custo do controle vs Redução da ALE).

#### 26. ISO-27001-e-27002
- **Título:** SGSI, Anexo A, CIS Controls e NIST 800-53
- **Função NIST CSF 2.0:** *Govern (GV)*
- **Tempo Estimado:** 50 minutos | **Carreiras:** Auditores ISO, GRC, Compliance
- **Objetivos de Aprendizagem:** Compreender a estrutura de alto nível (HLS) do Sistema de Gestão de Segurança da Informação (SGSI) da ABNT NBR ISO/IEC 27001:2022 (cláusulas 4 a 10); dominar a nova estrutura consolidada dos 93 controles do Anexo A divididos nos 4 temas: Organizacionais (37), Pessoas (8), Físicos (14) e Tecnológicos (34); elaborar a Declaração de Aplicabilidade (SoA); fazer o crosswalk dos controles do Anexo A com os CIS Controls v8.1 (IG1/IG2/IG3) e com o NIST SP 800-53 Rev. 5.
- **Pré-requisitos:** Gestao-de-Riscos-TI.
- **Conceitos-Chave:** Ciclo PDCA no SGSI, Cláusula 6.1.2/6.1.3 Avaliação e tratamento de riscos, Anexo A ed. 2022 (93 controles e novos atributos como Threat Intelligence e Masking), Declaração de Aplicabilidade (SoA), Auditorias Internas e Externas (Fase 1 e Fase 2), CIS Controls v8.1 (Grupos de Implementação IG1/IG2/IG3), NIST SP 800-53 Rev. 5.
- **Simulador Interativo em JS:** *Matriz de Controles e Declaração de Aplicabilidade (SoA)* — Tabela interativa com os 4 temas do Anexo A onde o estudante seleciona controles, define justificativa de inclusão/exclusão e gera o sumário percentual da Declaração de Aplicabilidade da organização.

#### 27. LGPD-e-Privacidade
- **Título:** Bases Legais, Direitos do Titular e RIPD/DPIA
- **Função NIST CSF 2.0:** *Govern (GV) / Protect (PR)*
- **Tempo Estimado:** 45 minutos | **Carreiras:** DPO/Encarregado, GRC, Jurídico de TI
- **Objetivos de Aprendizagem:** Dominar os fundamentos da Lei Geral de Proteção de Dados (Lei nº 13.709/2018 - LGPD); identificar as 10 bases legais para tratamento de dados pessoais (art. 7º) e dados sensíveis (art. 11); assegurar os direitos dos titulares (art. 18); conduzir um Relatório de Impacto à Proteção de Dados Pessoais (RIPD / DPIA); gerenciar comunicação de incidentes com a ANPD e titulares (art. 48).
- **Pré-requisitos:** Fundamentos-Ciber, Gestao-de-Riscos-TI.
- **Conceitos-Chave:** Dados Pessoais vs Sensíveis vs Anonimizados, Papéis: Controlador, Operador e Encarregado (DPO), Bases Legais (Consentimento, Legítimo Interesse, Cumprimento de Obrigação Legal, etc.), Princípios (Finalidade, Necessidade, Adequação), Prazos de notificação à ANPD.
- **Simulador Interativo em JS:** *Construtor de Avaliação de Impacto à Privacidade (RIPD)* — Formulário interativo para cadastro de fluxos de tratamento de dados que avalia a legitimidade da base legal escolhida, aponta carências de salvaguardas técnicas e gera a matriz de risco à privacidade do titular.

#### 28. Continuidade-e-Disaster-Recovery
- **Título:** BCP, DRP, Cálculo de RTO/RPO e Regra 3-2-1
- **Função NIST CSF 2.0:** *Recover (RC)*
- **Tempo Estimado:** 40 minutos | **Carreiras:** SysAdmin, CISO, Gestores, Infraestrutura
- **Objetivos de Aprendizagem:** Diferenciar Plano de Continuidade de Negócios (BCP) de Plano de Recuperação de Desastres (DRP); conduzir Análise de Impacto no Negócio (BIA); calcular e negociar métricas essenciais de recuperação: Recovery Time Objective (RTO) e Recovery Point Objective (RPO); implementar arquiteturas de backup resilientes seguindo a Regra 3-2-1 e 3-2-1-1-0 (cópia imutável/air-gapped).
- **Pré-requisitos:** Gestao-de-Riscos-TI.
- **Conceitos-Chave:** BIA (Business Impact Analysis), MTPD (Maximum Tolerable Period of Disruption), RTO vs RPO, Hot Site vs Warm Site vs Cold Site, Regra de Backup 3-2-1, Backups Imutáveis contra Ransomware, Testes de restauração periódicos (Tabletop, Simulação real).
- **Simulador Interativo em JS:** *Calculadora de RTO/RPO e Validador da Estratégia 3-2-1* — Permite ao aluno configurar diferentes estratégias de backup (frequência de snapshots, replicação geográfica, mídia offline) e simular cenários de desastre para verificar se a perda de dados e o tempo de indisponibilidade respeitam os SLAs de RTO e RPO definidos pelo negócio.

#### 31. PCI-DSS
- **Título:** PCI DSS v4.0.1: Escopo CDE e os 12 Requisitos
- **Função NIST CSF 2.0:** *Govern (GV) / Protect (PR)*
- **Tempo Estimado:** 45 minutos | **Carreiras:** GRC, Auditores, Blue Team, Analista de Segurança da Informação
- **Objetivos de Aprendizagem:** Conhecer os 6 objetivos e os 12 requisitos do PCI DSS v4.0.1; delimitar o ambiente de dados do portador do cartão (CDE) e usar segmentação para reduzir o escopo; diferenciar dados do portador (PAN) de dados sensíveis de autenticação (SAD); escolher entre os tipos de SAQ e entender ROC/QSA; distinguir a abordagem definida da customizada (v4.x).
- **Pré-requisitos:** Segmentacao-e-Firewall, ISO-27001-e-27002.
- **Conceitos-Chave:** PAN, SAD, CVV, Tokenização vs truncamento vs criptografia, CDE e sistemas "connected-to", Segmentação validada por teste, SAQ A, A-EP, B, C, D, QSA, ISA, ROC, AOC, Níveis de comerciante, Requisitos que passaram a ser obrigatórios em 31/03/2025.
- **Simulador Interativo em JS:** *Delimitador de Escopo CDE* — Um inventário de cerca de 10 sistemas fictícios (POS, servidor de aplicação, banco de dados, AD, estação de RH, gateway de pagamento terceirizado etc.). Para cada sistema, o aluno indica se ele armazena, processa ou transmite PAN, se está conectado ao CDE e se está segmentado; o simulador classifica cada um como dentro, conectado ou fora do escopo, explica o motivo e sugere o tipo de SAQ do cenário.

### Trilha 7: Carreira & Formação (`#DB2777`)

#### 32. Ingles-Tecnico-Ciber
- **Título:** Inglês Técnico para Segurança da Informação
- **Função NIST CSF 2.0:** *Protect (PR)* (categoria PR.AT, Awareness and Training)
- **Tempo Estimado:** 40 minutos | **Carreiras:** Todas (Fundação Universal), Analista de Segurança da Informação
- **Objetivos de Aprendizagem:** Ler advisories, registros CVE/NVD, RFCs e documentação de fabricantes em inglês; dominar o vocabulário técnico essencial e os falsos cognatos da área; redigir em inglês um resumo de incidente e um e-mail técnico curto.
- **Pré-requisitos:** Nenhum.
- **Conceitos-Chave:** Estrutura de um advisory (Summary, Affected Versions, Impact, Mitigation, Workaround), Verbos modais em requisitos normativos (MUST, SHOULD, MAY, conforme a RFC 2119), Falsos cognatos (*exploit*, *eventually*, *actually*), Siglas comuns, Registro formal vs informal.
- **Simulador Interativo em JS:** *Leitor de Advisory* — Um boletim de segurança em inglês, no formato realista de CVE/fabricante e totalmente fictício. Cada termo técnico é clicável e mostra tradução e definição em pt-BR. Ao final há perguntas de compreensão (versão afetada, impacto, mitigação recomendada) com correção comentada, e um glossário com flashcards guarda o progresso em `localStorage`.

#### 33. Certificacoes-e-Carreira
- **Título:** Formação, Certificações e Carreira
- **Função NIST CSF 2.0:** *Protect (PR)* (categoria PR.AT, Awareness and Training)
- **Tempo Estimado:** 35 minutos | **Carreiras:** Todas (Fundação Universal), Analista de Segurança da Informação
- **Objetivos de Aprendizagem:** Comparar graduações (Ciência da Computação, Sistemas de Informação) e pós-graduações em SI; conhecer CEH, CISM, CISSP, CCSP, GSEC e Security+ (órgão emissor, foco, domínios, experiência exigida e manutenção por CPE); montar um plano de certificação coerente com o perfil de carreira; usar o NICE Framework (NIST SP 800-181) para descrever papéis.
- **Pré-requisitos:** Nenhum.
- **Conceitos-Chave:** Certificações de entrada vs gestão vs especialidade, Pré-requisitos de experiência e status *Associate of ISC2*, CPE e renovação, NICE Framework.
- **Simulador Interativo em JS:** *Planejador de Certificações* — O aluno escolhe uma ou mais certificações-alvo; o simulador mostra os domínios de cada uma, os módulos do currículo que cobrem cada domínio e os domínios ainda sem módulo (lacunas), além de uma sugestão de ordem de estudo. Os dados vêm de uma estrutura JS embutida no próprio módulo, coerente com a Matriz de Certificações do portal.

---

## 4. Matriz de Mapeamento com Frameworks Globais

### Distribuição por Função do NIST CSF 2.0

| Função NIST CSF 2.0 | Quantidade de Módulos | Módulos Vinculados |
|---|---|---|
| **GOVERN (GV)** | 4 módulos | 25, 26, 27, 31 |
| **IDENTIFY (ID)** | 6 módulos | 01, 09, 11, 14, 17, 25 |
| **PROTECT (PR)** | 22 módulos | 02, 03, 04, 05, 06, 07, 08, 09, 10, 12, 13, 15, 21, 22, 23, 24, 27, 29, 30, 31, 32, 33 |
| **DETECT (DE)** | 9 módulos | 02, 07, 10, 16, 17, 20, 24, 29, 30 |
| **RESPOND (RS)** | 3 módulos | 18, 19, 20 |
| **RECOVER (RC)** | 1 módulo | 28 |

*(Nota: Alguns módulos cobrem mais de uma função normativa, como Detecção e Proteção conjugadas).*

---

## 5. Rotas de Aprendizagem por Perfil Profissional

Para orientar estudantes e profissionais com focos específicos, a matriz curricular recomenda as seguintes trilhas rápidas:

1. **Rota Blue Team / Analista SOC:**  
   `01 -> 02 -> 05 -> 06 -> 07 -> 10 -> 16 -> 17 -> 18`
2. **Rota Red Team / Pentest:**  
   `01 -> 02 -> 04 -> 11 -> 12 -> 13 -> 14 -> 15`
3. **Rota DevSecOps & Cloud Security:**  
   `01 -> 03 -> 04 -> 06 -> 12 -> 13 -> 21 -> 22 -> 24`
4. **Rota GRC, Auditoria & Privacidade:**  
   `01 -> 08 -> 09 -> 25 -> 26 -> 27 -> 28`
5. **Rota Perícia & Resposta a Incidentes:**  
   `01 -> 02 -> 06 -> 10 -> 16 -> 18 -> 19 -> 20`
6. **Rota 6: Analista de Segurança da Informação (vaga):**  
   `01 -> 05 -> 06 -> 07 -> 10 -> 29 -> 30 -> 25 -> 26 -> 31 -> 18 -> 32 -> 33`  
   Cada competência da vaga também aparece, com os módulos principais e de apoio, na seção "Rota por Vaga" do portal (`index.html`).
