# Design Spec: Estudos de Cibersegurança

**Data:** 2026-10-06  
**Status:** Em Revisão (Aguardando Aprovação do Usuário)  
**Autor:** Antigravity & Equipe  
**Repositório:** `estudos_cyberseguranca`  
**Referência Metodológica:** Superpowers Spec-Driven Development (SDD)

> **Atualização 2026-10-15:** grade ampliada para 33 módulos / 7 trilhas — ver [2026-10-15-competencias-vaga-analista-si-design.md](2026-10-15-competencias-vaga-analista-si-design.md).

---

## 1. Visão Geral e Propósito

O projeto **Estudos de Cibersegurança** é uma plataforma autoinstrucional, prática e enciclopédica sobre segurança da informação e defesa cibernética, estruturada em **28 módulos temáticos** e orientada a estudantes, analistas de segurança, candidatos a certificações técnicas (Security+, CEH, Pentest+) e concurseiros de TI.

Inspirado no modelo consolidado dos projetos irmãos [`Estudos ISO - Auditoria`](file:///home/josemauro/projects/josemauro/Estudos%20ISO%20-%20Auditoria) e [`estudos_tecnico_audio_video`](file:///home/josemauro/projects/josemauro/estudos_tecnico_audio_video), este projeto difere na estratégia de entrega prática:
- **Zero Dependências Pesadas:** Não requer LibreOffice (`soffice`) ou geradores de planilhas externas.
- **Interatividade Nativa e 100% Offline:** Cada estudo é um arquivo HTML rico, autocontido, com teoria direta, checklists interativos com persistência em `localStorage`, quizzes de fixação e **simuladores interativos práticos em JavaScript Vanilla**.
- **Duplo Mapeamento:** Grade pedagógica intuitiva de 6 trilhas associada formalmente aos frameworks **NIST CSF 2.0** e **MITRE ATT&CK**.

---

## 2. Grade Curricular dos 28 Módulos

Os 28 módulos cobrem desde a base teórica e de redes até especialidades emergentes (DevSecOps, Nuvem, IoT e IA) e governança/conformidade.

### Tabela Mestra de Módulos

| # | Slug / Pasta | Título do Estudo | Trilha Temática | Função NIST CSF 2.0 | Simulador Interativo em JavaScript |
|---|---|---|---|---|---|
| 01 | `Fundamentos-Ciber` | Tríade CIA, Ameaças e Modelagem STRIDE | 1. Fundamentos & Redes | Identify | STRIDE Threat Canvas interativo |
| 02 | `Redes-e-Protocolos` | TCP/IP, DNS, Roteamento e Inspeção de Tráfego | 1. Fundamentos & Redes | Protect / Detect | Inspetor visual de cabeçalhos IP/TCP/UDP |
| 03 | `Criptografia-Pratica` | Criptografia Simétrica, Assimétrica, Hashes e PKI | 1. Fundamentos & Redes | Protect | Lab de Cifras (Web Crypto API SHA-256 + AES) |
| 04 | `Autenticacao-e-IAM` | Senhas, MFA, OAuth 2.0, Tokens JWT e RBAC | 1. Fundamentos & Redes | Protect | Validador/Decodificador JWT + Teste de RBAC |
| 05 | `Segmentacao-e-Firewall` | DMZ, VLANs, Regras de Firewall e Filtragem | 1. Fundamentos & Redes | Protect | Simulador de Regras de Firewall (Pass/Drop) |
| 06 | `Hardening-Sistemas` | Bastionamento Linux e Windows (CIS Benchmarks) | 2. Segurança Defensiva | Protect | Auditor interativo de configurações (`/etc/ssh`, etc.) |
| 07 | `Seguranca-de-Redes-Defesa` | IDS/IPS, WAF, VPNs e Proxies Reversos | 2. Segurança Defensiva | Protect / Detect | Analisador de regras Snort/Suricata vs Tráfego |
| 08 | `Arquitetura-Zero-Trust` | Princípios Zero Trust e Microsegmentação | 2. Segurança Defensiva | Protect | Motor de Decisão de Acesso Zero Trust |
| 09 | `Gestao-de-Vulnerabilidades` | CVE, CVSS v3.1/v4.0 e Priorização de Patches | 2. Segurança Defensiva | Identify / Protect | Calculadora interativa de Score CVSS v3.1/v4.0 |
| 10 | `Seguranca-em-Endpoints-EDR` | Antivírus, EDR/XDR e Proteção de Host | 2. Segurança Defensiva | Protect / Detect | Linha do tempo de telemetria e detecção EDR |
| 11 | `Reconhecimento-e-OSINT` | Superfície de Ataque, DNS, WHOIS e Shodan | 3. Segurança Ofensiva | Identify | Terminal simulado de OSINT e enumeração |
| 12 | `OWASP-Top-10-Web` | Falhas Web (SQLi, XSS, CSRF, Broken Auth) | 3. Segurança Ofensiva | Protect | Playground de injeção e sanitização web |
| 13 | `Seguranca-em-APIs` | OWASP API Security, Rate Limiting e Tokens | 3. Segurança Ofensiva | Protect | Simulador de chamadas de API com Rate Limiter |
| 14 | `Pentest-Metodologias` | Fases do Pentest (PTES), Escopo e Relatório | 3. Segurança Ofensiva | Identify | Construtor de matriz de achados e relatórios |
| 15 | `Engenharia-Social-e-Phishing` | Pretexting, Spear Phishing e Defesas Humanas | 3. Segurança Ofensiva | Protect | Analisador de e-mails suspeitos (Spot the Indicators) |
| 16 | `Operacoes-SOC-e-SIEM` | Rotina de SOC L1/L2, Logs e Regras Sigma | 4. Operações & SOC | Detect | Console SIEM com busca de logs e alertas |
| 17 | `Threat-Intelligence` | IoCs, TTPs, MITRE ATT&CK e STIX/TAXII | 4. Operações & SOC | Identify / Detect | Mapeador de IoCs e TTPs na matriz ATT&CK |
| 18 | `Resposta-a-Incidentes` | Ciclo NIST SP 800-61 (Contenção e Erradicação) | 4. Operações & SOC | Respond | Runbook interativo em árvore de decisão |
| 19 | `Forense-Digital` | Cadeia de Custódia, Coleta de RAM e Artefatos | 4. Operações & SOC | Respond | Analisador de timeline de evidências e logs |
| 20 | `Analise-Basica-de-Malware` | Análise Estática vs Dinâmica e Sandboxes | 4. Operações & SOC | Detect / Respond | Inspetor de metadados PE/ELF e hashes |
| 21 | `Seguranca-em-Nuvem` | Responsabilidade Compartilhada e CSPM | 5. Especialidades | Protect | Auditor de permissões S3 e políticas IAM Cloud |
| 22 | `DevSecOps-e-CI-CD` | Shift-Left, SAST, DAST, SCA e Containers | 5. Especialidades | Protect | Simulador de pipeline CI/CD com security gates |
| 23 | `Seguranca-em-IoT-e-OT` | Redes Industriais (SCADA/Modbus) e IoT | 5. Especialidades | Protect | Mapeador do Modelo Purdue (TI vs TO) |
| 24 | `IA-e-Ciberseguranca` | Ameaças a LLMs (OWASP LLM), Deepfakes e Defesa | 5. Especialidades | Protect / Detect | Lab de Prompt Injection e defesas |
| 25 | `Gestao-de-Riscos-TI` | Avaliação Qualitativa vs Quantitativa (ALE/SLE) | 6. Governança & Riscos | Govern / Identify | Calculadora de matriz 5x5 e risco financeiro |
| 26 | `ISO-27001-e-27002` | SGSI e Controles do Anexo A (Edição 2022) | 6. Governança & Riscos | Govern | Matriz de Controles e Declaração de Aplicabilidade |
| 27 | `LGPD-e-Privacidade` | Bases Legais, Direitos do Titular e RIPD/DPIA | 6. Governança & Riscos | Govern / Protect | Construtor de Avaliação de Impacto (RIPD) |
| 28 | `Continuidade-e-Disaster-Recovery` | BCP, DRP, Cálculo de RTO/RPO e Regra 3-2-1 | 6. Governança & Riscos | Recover | Calculadora de RTO/RPO e estratégia 3-2-1 |

---

## 3. Arquitetura do Pipeline `_geradores/`

O pipeline é 100% baseado em Python (biblioteca padrão) e shell script Bash:

### Componentes

1. `_geradores/estudos.txt`:
   - Lista tabular com os metadados canônicos dos 28 estudos:
     `slug | titulo_curto | pasta | arquivo_html | trilha_num | cor_tema | nist_fn`
2. `_geradores/CURRICULO.md`:
   - Detalhamento pedagógico de cada estudo: competências desenvolvidas, pré-requisitos, conceitos fundamentais e proposta do simulador.
3. `_geradores/GUIA-DO-AUTOR.md`:
   - Guia de estilo, tom de voz, regras gramaticais em pt-BR, estrutura de seções obrigatórias e especificação dos componentes HTML/JS.
4. `_geradores/base.css`:
   - Design system unificado dos treinamentos: tipografia, tokens de cor para temas claro e escuro, estilos de caixas, terminais, quizzes e simuladores.
5. `_geradores/base.js`:
   - Camada de script compartilhada:
     - Gerenciador de tema (persistência `cs_theme`).
     - Gerenciador de checklists (gravação de checkboxes em `localStorage` com chave `cs_check_<slug>_<id>`).
     - Comportamento de quizzes expansíveis com cálculo de acertos.
     - Utilitários comuns de simulação (cópia de código, formatação de números, sanitização de texto).
6. `_geradores/montar.py`:
   - Script de compilação de treinamentos:
     - Lê `_geradores/<slug>_body.html`.
     - Injeta inlined o `base.css` e o `base.js`.
     - Salva em `<pasta>/treinamento-<slug>.html`.
7. `_geradores/index_dados.py`:
   - Dicionário com metadados ricos dos 28 estudos:
     - `slug`, `titulo`, `subtitulo`, `trilha`, `nist`, `carreiras`, `tempo_minutos`, `pergunta_chave`, `fatos`, `necessidades`.
8. `_geradores/index.css`:
   - Estilização do portal mestre `index.html`.
9. `_geradores/build_index.py`:
   - Gera o portal raiz `index.html`:
     - Lê `index_dados.py`.
     - Checa a existência real de cada `treinamento-<slug>.html` para sinalizar status (disponível vs em elaboração).
     - Insere contadores dinâmicos, barra de progresso, abas de filtro e busca em tempo real.
10. `_geradores/gerar.sh`:
    - Interface de linha de comando:
      - `./_geradores/gerar.sh <slug>`: compila um estudo específico.
      - `./_geradores/gerar.sh todos`: compila todos os estudos que possuem corpo e regera o portal.
      - `./_geradores/gerar.sh portal`: regera apenas o `index.html`.
11. `_geradores/testes/`:
    - Suíte de testes automatizados com `pytest`:
      - Validação de links relativos.
      - Verificação de metadados completos em `index_dados.py`.
      - Validação de compilação sem tags órfãs.

---

## 4. Design System e Identidade Visual

### 4.1 Tipografia
- **Títulos / Display:** `"Barlow Semi Condensed", "Arial Narrow", Arial, sans-serif`
- **Corpo / Leitura:** `"IBM Plex Sans", system-ui, -apple-system, sans-serif`
- **Monospaçado / Terminais / Código:** `"IBM Plex Mono", Menlo, Consolas, monospace`

### 4.2 Paleta de Cores e Tokens CSS

```css
:root {
  --ground: #F3F6F7;
  --surface: #FFFFFF;
  --sunk: #E9EEF0;
  --ink: #16242E;
  --muted: #566672;
  --rule: #D3DBE0;
  
  /* Cores das Trilhas */
  --t1-blue: #2563EB;
  --t2-green: #059669;
  --t3-red: #DC2626;
  --t4-purple: #7C3AED;
  --t5-cyan: #0891B2;
  --t6-amber: #D97706;
}

@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --ground: #0F171C;
    --surface: #172229;
    --sunk: #1E2B33;
    --ink: #E4EAED;
    --muted: #9BABB6;
    --rule: #2B3A44;
    
    --t1-blue: #60A5FA;
    --t2-green: #34D399;
    --t3-red: #F87171;
    --t4-purple: #A78BFA;
    --t5-cyan: #22D3EE;
    --t6-amber: #FBBF24;
  }
}
```

### 4.3 Componentes Padronizados
- `.callout`: Caixas com borda lateral colorida e ícone para avisos (`tip`, `warning`, `danger`, `law`).
- `.terminal-box`: Bloco com botões de janela, botão copiar e comando destacado.
- `.lab-box`: Painel interativo com cabeçalho de laboratório, inputs de controle e área de visualização em tempo real.
- `.checklist`: Lista interativa com caixas de seleção que gravam o progresso do usuário no navegador.
- `.quiz`: Desafios de fixação com revelação explicada e fundamentação técnica.

---

## 5. Portal Central (`index.html`)

O portal raiz reúne:
1. **Masthead com Estatísticas:** 28 estudos, 6 trilhas, 28 simuladores, contagem de minutos totais de capacitação.
2. **Barra de Progresso Global:** Contabiliza os estudos marcados como "Concluído" pelo usuário (armazenado em `localStorage`).
3. **Filtro Multifacetado:**
   - *Por Trilha Temática* (Fundamentos, Defesa, Ofensiva, Operações, Especialidades, Governança).
   - *Por Perfil de Carreira* (Blue Team, Red Team, AppSec, GRC, Cloud/DevSecOps).
   - *Por Função NIST CSF 2.0* (Govern, Identify, Protect, Detect, Respond, Recover).
4. **Matriz "Escolha pela Necessidade":** Grade de problemas comuns do mundo real com atalhos diretos para os estudos que resolvem cada problema.
5. **Busca em Tempo Real:** Filtra instantaneamente os cartões com destaque de termos correspondentes.

---

## 6. Estratégia de Implementação e Verificação

A implementação seguirá o fluxo padrão SDD do Superpowers:
1. **Aprovação desta Especificação:** Validação pelo usuário humano.
2. **Plano de Implementação (`writing-plans`):**
   - Tarefa 1: Scaffolding e infraestrutura do pipeline `_geradores/` (`estudos.txt`, `CURRICULO.md`, `GUIA-DO-AUTOR.md`).
   - Tarefa 2: Motor de templates e estilos (`base.css`, `base.js`, `montar.py`).
   - Tarefa 3: Dados do portal e construtor raiz (`index_dados.py`, `index.css`, `build_index.py`, `gerar.sh`).
   - Tarefa 4: Testes automatizados do pipeline com verificação de integridade.
   - Tarefa 5: Criação do primeiro estudo piloto completo (`Fundamentos-Ciber/treinamento-fundamentos-ciber.html`) demonstrando o padrão do simulador STRIDE, checklist e quiz.
   - Tarefas subsequentes: Entrega progressiva das trilhas.
3. **Critérios de Aceite:**
   - `./_geradores/gerar.sh todos` e `./_geradores/gerar.sh portal` executam sem erros.
   - O arquivo `index.html` gerado abre perfeitamente no navegador, responsivo e sem erros no console JS.
   - O estudo piloto compila como arquivo único standalone, funcionando 100% offline.
   - Todos os testes automatizados passam.
