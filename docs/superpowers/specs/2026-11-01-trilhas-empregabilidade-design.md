# Design Spec: Trilhas de Empregabilidade (Trilhas 8, 9 e 10)

**Data:** 2026-11-01
**Status:** Aprovada (2026-11-01) e implementada (branch feat/trilhas-empregabilidade)
**Repositório:** `estudos_cyberseguranca`
**Specs anteriores:** [`2026-10-06-estudos-cyberseguranca-design.md`](2026-10-06-estudos-cyberseguranca-design.md), [`2026-10-15-competencias-vaga-analista-si-design.md`](2026-10-15-competencias-vaga-analista-si-design.md)
**Referência Metodológica:** Superpowers Spec-Driven Development (SDD)

---

## 1. Propósito e Entendimento

O usuário pediu sugestões de trilhas novas para o guia de estudos. Das seis sugeridas, escolheu três, com **foco em empregabilidade** (preparação para vagas):

1. **Ferramentas & Automação do Analista**: a base prática (Linux, Python, PowerShell, laboratório e portfólio) que nenhum módulo cobre hoje.
2. **Identidade Corporativa & Active Directory**: a maior lacuna técnica do catálogo, cobrada tanto em vagas de Blue Team quanto de Red Team.
3. **Resiliência, Crise & Ransomware**: reforça as funções NIST mais fracas da grade (Respond tinha 3 módulos; Recover, 1).

### Estado atual (2026-11-01)

- 33 módulos em 7 trilhas; módulos 01–11 construídos, 12–33 pendentes.
- Distribuição NIST de `estudos.txt`: Protect domina, Respond tem 3 módulos (18, 19, 20) e Recover tem 1 (28).
- As contagens "33" e "7" aparecem escritas à mão em `test_curriculo.py`, `test_index.py`, `test_cli.py` e `test_assets.py`.

### Decisões do usuário

| Decisão | Escolha |
|---|---|
| Objetivo das trilhas novas | Empregabilidade (preparação para vagas) |
| Trilhas | Ferramentas & Automação; Identidade Corporativa & AD; Resiliência, Crise & Ransomware |
| Escopo desta spec | **Só grade e rotas.** O HTML dos módulos 34–45 entra na fila normal de construção |
| Ligação com vagas | Tags de carreira + rotas por perfil + **módulos de apoio** na Rota da Vaga (requisitos e módulos principais intactos) |
| Abordagem técnica | **A**: mesmo padrão da spec de 2026-10-15, com os testes derivando os totais dos dados |
| Trilha 8 | 4 módulos (Regex incorporado ao módulo de Python) |
| Cores | Ardósia (T8), índigo (T9), laranja (T10) |

### Critérios de sucesso

- O catálogo tem **45 módulos em 10 trilhas**, consistente em `estudos.txt`, `index_dados.py`, `CURRICULO.md` e `README.md`.
- Os módulos 01–33 mantêm o número; os novos ficam em 34–45.
- A Rota da Vaga continua com 7 competências e os mesmos módulos principais, e ganha os módulos de apoio do §3.1.
- Cada trilha em `TRILHAS` tem token de cor nos 4 blocos de tema, selo (`.badge-tN`) e bloco (`.track-tile.tN`).
- A suíte `unittest` passa inteira; o portal e os módulos 01–11 compilam sem erro.

### Fora de escopo

- O HTML (`*_body.html`) dos módulos 34–45.
- Rotas por perfil novas (só as 6 existentes são atualizadas) e carreiras novas em `CARREIRAS`.
- Mudanças nos 7 requisitos ou nos módulos principais da Rota da Vaga.
- As outras três trilhas sugeridas (Ofensiva Avançada, Engenharia de Detecção, Regulação Brasileira).

---

## 2. Grade Curricular: 33 → 45 Módulos, 7 → 10 Trilhas

### 2.1 Trilhas novas

| Trilha | Denominação | Cor (claro) | Cor (escuro) | Token CSS | `cor_nome` | Módulos |
|---|---|---|---|---|---|---|
| **Trilha 8** | Ferramentas & Automação do Analista | `#475569` | `#94A3B8` | `--t8-slate` | `slate` | 34 a 37 |
| **Trilha 9** | Identidade Corporativa & Active Directory | `#4F46E5` | `#818CF8` | `--t9-indigo` | `indigo` | 38 a 41 |
| **Trilha 10** | Resiliência, Crise & Ransomware | `#C2410C` | `#FB923C` | `--t10-orange` | `orange` | 42 a 45 |

Contraste das cores claras sobre branco: ardósia ≈ 7,6:1, índigo ≈ 6,3:1, laranja ≈ 5,2:1. O laranja usa o tom 700 porque o 600 (`#EA580C`) não chega a 4,5:1. O índigo e o laranja ficam próximos de cores existentes (azul/roxo e vermelho/âmbar). Todo selo e bloco mostra o número da trilha, então a cor nunca é o único identificador.

Descrições para `TRILHAS` (`index_dados.py`):

- **8:** "Base prática do analista: Linux e PowerShell para investigação, automação com Python e regex, laboratório doméstico e portfólio."
- **9:** "Identidade no ambiente corporativo: Active Directory, Kerberos, ataques e detecção no AD, acessos privilegiados (PAM) e Entra ID."
- **10:** "Resiliência operacional: ransomware da prevenção à recuperação, gestão de crise, exercícios tabletop e backup imutável."

### 2.2 Linhas novas em `_geradores/estudos.txt`

Acrescentadas ao fim, nesta ordem. O número do módulo é a posição em `ESTUDOS_DADOS`, então a ordem define a numeração 34–45:

```text
Linux-para-Seguranca|Linux para Segurança: Shell, Permissões e Logs|Linux-para-Seguranca|treinamento-linux-para-seguranca.html|8|#475569|Protect / Detect
Python-para-Seguranca|Python para Segurança: Automação, Regex e Parsing|Python-para-Seguranca|treinamento-python-para-seguranca.html|8|#475569|Detect
PowerShell-e-Windows-Interno|PowerShell, Event Log e Registro do Windows|PowerShell-e-Windows-Interno|treinamento-powershell-e-windows-interno.html|8|#475569|Detect
Laboratorio-Domestico-e-Portfolio|Laboratório Doméstico, CTFs e Portfólio|Laboratorio-Domestico-e-Portfolio|treinamento-laboratorio-domestico-e-portfolio.html|8|#475569|Protect
Active-Directory-Fundamentos|Active Directory: Domínios, GPO e Kerberos|Active-Directory-Fundamentos|treinamento-active-directory-fundamentos.html|9|#4F46E5|Protect
Ataques-e-Defesa-no-AD|Ataques ao AD e Detecção: Kerberoasting, Pass-the-Hash e DCSync|Ataques-e-Defesa-no-AD|treinamento-ataques-e-defesa-no-ad.html|9|#4F46E5|Protect / Detect
PAM-e-Acessos-Privilegiados|Gestão de Acessos Privilegiados (PAM)|PAM-e-Acessos-Privilegiados|treinamento-pam-e-acessos-privilegiados.html|9|#4F46E5|Protect
Identidade-Hibrida-e-Nuvem|Entra ID, Identidade Híbrida e Acesso Condicional|Identidade-Hibrida-e-Nuvem|treinamento-identidade-hibrida-e-nuvem.html|9|#4F46E5|Protect
Ransomware-Prevencao-a-Recuperacao|Ransomware: Prevenção, Contenção e Recuperação|Ransomware-Prevencao-a-Recuperacao|treinamento-ransomware-prevencao-a-recuperacao.html|10|#C2410C|Respond / Recover
Gestao-de-Crise-e-Comunicacao|Gestão de Crise Cibernética e Comunicação de Incidentes|Gestao-de-Crise-e-Comunicacao|treinamento-gestao-de-crise-e-comunicacao.html|10|#C2410C|Respond
Exercicios-Tabletop|Exercícios Tabletop: Planejar, Conduzir e Avaliar|Exercicios-Tabletop|treinamento-exercicios-tabletop.html|10|#C2410C|Respond / Recover
Backup-Imutavel-e-Recuperacao|Backup Imutável e Recuperação de Identidade|Backup-Imutavel-e-Recuperacao|treinamento-backup-imutavel-e-recuperacao.html|10|#C2410C|Recover
```

O cabeçalho do arquivo passa a dizer "45 Módulos" e ganha as linhas `# 8 = Ferramentas & Automação (#475569)`, `# 9 = Identidade & AD (#4F46E5)` e `# 10 = Resiliência & Ransomware (#C2410C)`.

O módulo 37 é **Protect** porque o NIST CSF 2.0 põe capacitação em **PR.AT (Awareness and Training)**, como nos módulos 32 e 33.

Efeito na distribuição NIST: Respond passa de 3 para 6 módulos (+42, 43, 44) e Recover de 1 para 4 (+42, 44, 45).

### 2.3 Detalhamento dos módulos

Cada módulo abaixo vira uma entrada em `ESTUDOS_DADOS` e uma seção no §3 do `CURRICULO.md`. Os campos `titulo`, `trilha` e `nist` coincidem com `estudos.txt`. Rótulos de carreira usam exatamente os nomes de `CARREIRAS`; "Analista de SI" abaixo significa `ROTULO_ANALISTA_SI` ("Analista de Segurança da Informação").

---

#### 34 · `Linux-para-Seguranca`: Linux para Segurança: Shell, Permissões e Logs

- **Trilha:** 8 · **NIST:** Protect / Detect · **Tempo:** 50 min
- **MITRE:** T1548.001 Setuid and Setgid / T1053.003 Cron / T1110 Brute Force
- **Carreiras:** Blue Team & Defesa, Operações SOC & Resposta, Red Team & Pentest, Analista de SI
- **Subtítulo:** "Linha de comando, permissões, usuários, processos e logs para investigar um servidor Linux"
- **Objetivos:**
  - Navegar e filtrar com pipes (`grep`, `awk`, `sort`, `uniq`).
  - Ler e corrigir permissões (rwx, SUID/SGID, umask) e regras do `sudoers`.
  - Investigar `auth.log` e `journalctl`, processos (`ps`) e portas (`ss`).
  - Encontrar persistência em `cron` e em serviços `systemd`.
- **Pré-requisitos:** Fundamentos-Ciber.
- **Conceitos-chave:** FHS; permissões octais; SUID/SGID e *sticky bit*; `/etc/passwd` vs `/etc/shadow`; `sudoers`; `auth.log`, `journalctl`; `ps`, `ss`, `lsof`; `crontab` e *timers* do systemd.
- **Pergunta-chave:** "Que comandos revelam, em poucos minutos, se um servidor Linux foi comprometido?"
- **Simulador: *Terminal de Investigação Linux*.** Terminal simulado sobre um sistema de arquivos fictício, no mesmo padrão do terminal do módulo 11. Missões pontuadas: achar binários SUID fora do padrão, identificar força bruta no `auth.log`, corrigir um diretório com permissão 777 e localizar persistência em `cron`.
- **Fatos (cards do portal):**
  - "Permissões octais, SUID/SGID e sudoers"
  - "Investigação de auth.log e journalctl"
  - "Processos, portas e persistência em cron"
  - "Terminal simulado com missões de investigação"

#### 35 · `Python-para-Seguranca`: Python para Segurança: Automação, Regex e Parsing

- **Trilha:** 8 · **NIST:** Detect · **Tempo:** 50 min
- **MITRE:** T1059.006 Python (uso defensivo e reconhecimento do vetor)
- **Carreiras:** Blue Team & Defesa, Operações SOC & Resposta, AppSec & DevSecOps, Analista de SI
- **Subtítulo:** "Scripts para ler logs, extrair indicadores com regex e consultar APIs de reputação"
- **Objetivos:**
  - Ler arquivos de log e extrair campos com o módulo `re`.
  - Agregar eventos com `collections.Counter` e aplicar limiares.
  - Consultar APIs de reputação (VirusTotal, AbuseIPDB) com `requests` e tratar JSON/CSV.
  - Aplicar boas práticas: segredos fora do código, tratamento de erros e limites de taxa.
- **Pré-requisitos:** Linux-para-Seguranca.
- **Conceitos-chave:** expressões regulares (grupos, quantificadores, âncoras); `re.finditer` vs `re.search`; `Counter`; `requests` e códigos HTTP; JSON e CSV; variáveis de ambiente para chaves de API; *rate limiting*.
- **Pergunta-chave:** "Como transformar uma triagem manual de logs em um script repetível?"
- **Simulador: *Montador de Detector*.** O aluno encaixa blocos prontos (ler log → aplicar regex → contar por IP → aplicar limiar → gerar alerta). O JavaScript mostra o código Python equivalente e executa a mesma lógica sobre um log de exemplo. Inclui um testador de regex ao vivo com destaque das correspondências.
- **Fatos:**
  - "Regex aplicada a logs reais"
  - "Agregação com Counter e limiares de alerta"
  - "Consulta a APIs de reputação com requests"
  - "Montador visual de detector com código Python gerado"

#### 36 · `PowerShell-e-Windows-Interno`: PowerShell, Event Log e Registro do Windows

- **Trilha:** 8 · **NIST:** Detect · **Tempo:** 50 min
- **MITRE:** T1059.001 PowerShell / T1547.001 Registry Run Keys / T1136 Create Account
- **Carreiras:** Blue Team & Defesa, Operações SOC & Resposta, Perícia Forense & Malware, Analista de SI
- **Subtítulo:** "Pipeline de objetos, eventos de segurança, Sysmon e chaves de persistência no Registro"
- **Objetivos:**
  - Usar cmdlets e o pipeline de objetos do PowerShell.
  - Consultar eventos com `Get-WinEvent` e reconhecer os Event IDs essenciais.
  - Interpretar eventos do Sysmon (1 e 3) e o log de *ScriptBlock*.
  - Encontrar persistência em chaves Run do Registro e em serviços.
- **Pré-requisitos:** Hardening-Sistemas.
- **Conceitos-chave:** cmdlets Verbo-Substantivo; pipeline de objetos; `Get-WinEvent` com `FilterHashtable`; Event IDs 4624, 4625, 4688, 4720, 7045; tipos de logon; Sysmon 1 e 3; *ScriptBlock Logging* (4104); HKLM/HKCU `...\Run`.
- **Pergunta-chave:** "Que eventos do Windows contam a história de uma intrusão?"
- **Simulador: *Visualizador de Eventos*.** Linha do tempo fictícia de intrusão em um host Windows. O aluno filtra por Event ID e responde perguntas sobre acesso inicial, conta criada e persistência, com correção comentada.
- **Fatos:**
  - "Pipeline de objetos e Get-WinEvent"
  - "Event IDs essenciais e tipos de logon"
  - "Sysmon e ScriptBlock Logging"
  - "Linha do tempo de intrusão para investigar"

#### 37 · `Laboratorio-Domestico-e-Portfolio`: Laboratório Doméstico, CTFs e Portfólio

- **Trilha:** 8 · **NIST:** Protect (categoria PR.AT; o campo `nist` é só "Protect") · **Tempo:** 35 min
- **MITRE:** N/A (módulo de carreira)
- **Carreiras:** todas as 7 de `CARREIRAS` (Blue Team & Defesa, Red Team & Pentest, AppSec & DevSecOps, Operações SOC & Resposta, GRC & Auditoria, Perícia Forense & Malware, Analista de SI)
- **Subtítulo:** "Montar um laboratório isolado, praticar em CTFs e transformar a prática em portfólio"
- **Objetivos:**
  - Planejar um laboratório virtual com redes isoladas (host-only, NAT).
  - Montar uma topologia mínima: firewall, controlador de domínio, SIEM e máquina atacante.
  - Escolher plataformas de CTF e de laboratório guiado conforme a carreira.
  - Documentar a prática em *write-ups* e em um portfólio no GitHub.
  - Respeitar limites éticos e legais (só testar o que é seu ou autorizado; Lei 12.737/2012).
- **Pré-requisitos:** Nenhum.
- **Conceitos-chave:** hipervisores tipo 1 vs tipo 2; *snapshots*; redes host-only, NAT e interna; requisitos de RAM por VM; CTF *jeopardy* vs *attack-defense*; *write-up*; README de portfólio; autorização por escrito.
- **Pergunta-chave:** "Como provar numa entrevista o que você sabe fazer?"
- **Simulador: *Planejador de Homelab*.** O aluno informa RAM e CPU da máquina e escolhe VMs de um catálogo (OPNsense, Windows Server com AD, Wazuh, Kali, Ubuntu). O planejador mostra se tudo cabe, desenha a topologia e gera um checklist de isolamento e um roteiro de portfólio.
- **Fatos:**
  - "Topologia mínima de laboratório isolado"
  - "Orçamento de RAM e CPU por VM"
  - "CTFs, write-ups e portfólio no GitHub"
  - "Planejador de homelab com checklist de isolamento"

---

#### 38 · `Active-Directory-Fundamentos`: Active Directory: Domínios, GPO e Kerberos

- **Trilha:** 9 · **NIST:** Protect · **Tempo:** 50 min
- **MITRE:** TA0006 Credential Access / TA0008 Lateral Movement (contexto)
- **Carreiras:** Blue Team & Defesa, Red Team & Pentest, Operações SOC & Resposta, Analista de SI
- **Subtítulo:** "Estrutura do AD, precedência de GPO, Kerberos e NTLM e o modelo de camadas de administração"
- **Objetivos:**
  - Descrever floresta, domínio, OU, controladores de domínio e relações de confiança.
  - Calcular a configuração efetiva de GPOs pela ordem LSDOU.
  - Explicar a troca Kerberos (AS, TGS, AP) e quando o NTLM entra em cena.
  - Aplicar o modelo de camadas (*tiering*) às contas administrativas.
- **Pré-requisitos:** Autenticacao-e-IAM.
- **Conceitos-chave:** floresta, árvore, domínio, OU; DC e FSMO; LDAP; GPO e LSDOU (*Enforced*, *Block Inheritance*); Kerberos (KDC, TGT, TGS, SPN); NTLM; contas de serviço e gMSA; *tiering* 0/1/2.
- **Pergunta-chave:** "Como o AD decide quem é você e o que você pode fazer em cada máquina?"
- **Simulador: *Kerberos Passo a Passo*.** Percorre a troca AS → TGS → AP; cada mensagem é clicável e mostra seus campos e o que pode dar errado. Inclui uma calculadora de precedência de GPO: o aluno empilha políticas e vê a configuração efetiva.
- **Fatos:**
  - "Floresta, domínio, OU e controladores de domínio"
  - "Precedência de GPO (LSDOU)"
  - "Kerberos (AS, TGS, AP) e NTLM"
  - "Simulador da troca Kerberos e calculadora de GPO"

#### 39 · `Ataques-e-Defesa-no-AD`: Ataques ao AD e Detecção: Kerberoasting, Pass-the-Hash e DCSync

- **Trilha:** 9 · **NIST:** Protect / Detect · **Tempo:** 55 min
- **MITRE:** T1558.003 Kerberoasting / T1550.002 Pass the Hash / T1003.006 DCSync
- **Carreiras:** Blue Team & Defesa, Red Team & Pentest, Operações SOC & Resposta
- **Subtítulo:** "Caminhos de ataque no AD, sinais de detecção e mitigações que quebram cada caminho"
- **Objetivos:**
  - Ler caminhos de ataque como grafo (a ideia por trás do BloodHound).
  - Explicar Kerberoasting, Pass-the-Hash e DCSync no nível conceitual.
  - Associar cada técnica aos sinais de detecção nos logs.
  - Escolher mitigações: gMSA, AES obrigatório, LAPS, grupo Protected Users, *tiering*.
- **Pré-requisitos:** Active-Directory-Fundamentos, PowerShell-e-Windows-Interno.
- **Conceitos-chave:** grafo de permissões (MemberOf, AdminTo, HasSession); evento 4769 com cifra RC4; logons anômalos (4624 tipo 3 e 9); evento 4662 para replicação de diretório; senhas de contas de serviço; LAPS; Protected Users.
- **Escopo do conteúdo:** conceitual e defensivo. O módulo não traz comandos de ataque prontos para uso.
- **Pergunta-chave:** "Qual é o caminho mais curto de um usuário comum até Domain Admin, e como fechá-lo?"
- **Simulador: *Mapa de Caminhos de Ataque*.** Domínio fictício em grafo. Fase 1: o aluno encontra o caminho de um usuário comum até Domain Admin e aplica mitigações até quebrar todos os caminhos. Fase 2: o aluno associa eventos de log à técnica correspondente.
- **Fatos:**
  - "Caminhos de ataque em grafo"
  - "Kerberoasting, Pass-the-Hash e DCSync"
  - "Sinais de detecção nos eventos do Windows"
  - "Mapa interativo para quebrar caminhos de ataque"

#### 40 · `PAM-e-Acessos-Privilegiados`: Gestão de Acessos Privilegiados (PAM)

- **Trilha:** 9 · **NIST:** Protect · **Tempo:** 40 min
- **MITRE:** T1078.002 Domain Accounts / T1098 Account Manipulation
- **Carreiras:** Blue Team & Defesa, GRC & Auditoria, Analista de SI
- **Subtítulo:** "Inventário, cofre, rotação, gravação de sessão e acesso just-in-time a contas privilegiadas"
- **Objetivos:**
  - Inventariar contas privilegiadas (humanas, de serviço e de emergência).
  - Aplicar cofre de senhas, rotação automática e gravação de sessão.
  - Reduzir privilégio permanente com JIT e JEA.
  - Ligar os controles à ISO/IEC 27002 (controle 8.2) e ao PCI DSS (requisitos 7 e 8).
- **Pré-requisitos:** Active-Directory-Fundamentos.
- **Conceitos-chave:** privilégio permanente vs *just-in-time*; cofre de credenciais; rotação; *session recording*; JEA; contas *break-glass*; contas órfãs; recertificação de acessos.
- **Pergunta-chave:** "Quem tem poder de administrador hoje, e por quanto tempo deveria ter?"
- **Simulador: *Auditor de Contas Privilegiadas*.** Inventário fictício com problemas (conta compartilhada, senha sem rotação, administrador permanente, conta órfã). O aluno sinaliza cada problema, aplica controles e vê o risco residual cair.
- **Fatos:**
  - "Inventário de contas privilegiadas"
  - "Cofre, rotação e gravação de sessão"
  - "Just-in-time, JEA e break-glass"
  - "Auditor interativo de contas privilegiadas"

#### 41 · `Identidade-Hibrida-e-Nuvem`: Entra ID, Identidade Híbrida e Acesso Condicional

- **Trilha:** 9 · **NIST:** Protect · **Tempo:** 45 min
- **MITRE:** T1110.003 Password Spraying / T1528 Steal Application Access Token / T1566 Phishing
- **Carreiras:** Blue Team & Defesa, AppSec & DevSecOps, Analista de SI
- **Subtítulo:** "Sincronização híbrida, acesso condicional, MFA resistente a phishing e PIM"
- **Objetivos:**
  - Comparar os modos de sincronização híbrida (PHS, PTA, federação).
  - Escrever políticas de acesso condicional por usuário, local, dispositivo e risco.
  - Escolher MFA resistente a phishing (FIDO2, passkeys).
  - Reconhecer *password spraying*, *consent phishing* e roubo de token, e as defesas de cada um.
- **Pré-requisitos:** Active-Directory-Fundamentos, Arquitetura-Zero-Trust.
- **Conceitos-chave:** Entra Connect; PHS, PTA, federação; acesso condicional (atribuições, condições, controles); dispositivo em conformidade; risco de entrada; FIDO2; PIM; consentimento de aplicativos OAuth.
- **Diferença para o módulo 08:** o motor PDP/PEP do 08 trata Zero Trust de forma genérica; aqui as políticas são concretas, no estilo de produto.
- **Pergunta-chave:** "Que política de acesso bloqueia o atacante sem travar o usuário legítimo?"
- **Simulador: *Avaliador de Acesso Condicional*.** O aluno escreve políticas e dispara tentativas de login fictícias (local, dispositivo, risco). O avaliador mostra, para cada tentativa, se o acesso foi concedido, bloqueado ou condicionado a MFA, e qual política decidiu.
- **Fatos:**
  - "PHS, PTA e federação"
  - "Acesso condicional por risco e dispositivo"
  - "MFA resistente a phishing e PIM"
  - "Avaliador de políticas com logins simulados"

---

#### 42 · `Ransomware-Prevencao-a-Recuperacao`: Ransomware: Prevenção, Contenção e Recuperação

- **Trilha:** 10 · **NIST:** Respond / Recover · **Tempo:** 50 min
- **MITRE:** T1486 Data Encrypted for Impact / T1490 Inhibit System Recovery / T1567 Exfiltration Over Web Service
- **Carreiras:** Blue Team & Defesa, Operações SOC & Resposta, Perícia Forense & Malware, Analista de SI
- **Subtítulo:** "Anatomia do ataque, dupla extorsão, decisões de contenção e retomada da operação"
- **Objetivos:**
  - Descrever a anatomia de um ataque: acesso inicial → movimentação → exfiltração → criptografia.
  - Explicar dupla extorsão e o modelo RaaS.
  - Tomar decisões de contenção (isolar ou desligar o host, reset de credenciais em massa) e entender o custo de cada uma.
  - Conhecer os descriptografadores públicos (No More Ransom) e a ordem de recuperação.
  - Discutir o dilema do pagamento só do ponto de vista jurídico e de risco.
- **Pré-requisitos:** Resposta-a-Incidentes, Continuidade-e-Disaster-Recovery.
- **Conceitos-chave:** vetores de acesso inicial (phishing, RDP exposto, VPN sem MFA); RaaS e afiliados; dupla e tripla extorsão; exclusão de *shadow copies*; isolamento de rede vs desligamento (perda de evidência em RAM); reset de krbtgt; *No More Ransom*; prioridade de restauração.
- **Pergunta-chave:** "Nas primeiras horas de um ransomware, que decisões reduzem o estrago e quais o pioram?"
- **Simulador: *Linha do Tempo do Ransomware*.** Um incidente fictício avança hora a hora. Em cada ponto de decisão o aluno escolhe uma ação e vê a consequência: evidência perdida, propagação contida, tempo de parada.
- **Fatos:**
  - "Anatomia do ataque e dupla extorsão"
  - "Decisões de contenção e seus custos"
  - "Ordem de recuperação e descriptografadores públicos"
  - "Linha do tempo interativa com pontos de decisão"

#### 43 · `Gestao-de-Crise-e-Comunicacao`: Gestão de Crise Cibernética e Comunicação de Incidentes

- **Trilha:** 10 · **NIST:** Respond · **Tempo:** 40 min
- **MITRE:** N/A (gestão e comunicação)
- **Carreiras:** GRC & Auditoria, Operações SOC & Resposta, Analista de SI
- **Subtítulo:** "Comitê de crise, registro de decisões e comunicação a público interno, clientes, imprensa e ANPD"
- **Objetivos:**
  - Montar um comitê de crise com papéis definidos (matriz RACI).
  - Manter sala de guerra e registro de decisões.
  - Planejar a comunicação interna, com clientes e com a imprensa.
  - Cumprir a comunicação obrigatória à ANPD e aos titulares.
- **Pré-requisitos:** Resposta-a-Incidentes, LGPD-e-Privacidade.
- **Conceitos-chave:** incidente vs crise; RACI; porta-voz único; registro de decisões; comunicação à ANPD (Resolução CD/ANPD nº 15/2024: prazo de **3 dias úteis** contados do conhecimento de que o incidente afetou dados pessoais; complementação em até 20 dias úteis; prazos em dobro para agentes de pequeno porte); comunicação aos titulares.
- **Pendências de verificação para a construção do módulo** (não bloqueiam esta spec):
  - O prazo de comunicação aos **titulares**: fontes secundárias divergem entre "3 dias úteis" e "sem demora injustificada". Conferir no texto oficial da Resolução CD/ANPD nº 15/2024 no DOU.
  - Obrigações do **setor financeiro**: a Resolução CMN nº 4.893/2021 exige comunicar incidentes relevantes ao Banco Central e foi alterada pela Resolução CMN nº 5.274/2025. O prazo não foi confirmado. Por isso, o cenário do simulador é uma empresa **não financeira**, e o módulo só cita a existência dessas regras.
- **Pergunta-chave:** "Quem precisa saber do incidente, quando e com que mensagem?"
- **Simulador: *Relógio da Crise*.** Dado um cenário fictício (empresa não financeira), o aluno decide quem notificar, quando e com que conteúdo. O simulador confere prazos e elementos obrigatórios e comenta cada escolha.
- **Fatos:**
  - "Comitê de crise e matriz RACI"
  - "Registro de decisões e porta-voz único"
  - "Comunicação à ANPD em 3 dias úteis"
  - "Relógio da crise com notificações e prazos"

#### 44 · `Exercicios-Tabletop`: Exercícios Tabletop: Planejar, Conduzir e Avaliar

- **Trilha:** 10 · **NIST:** Respond / Recover · **Tempo:** 35 min
- **MITRE:** N/A (preparação e exercício)
- **Carreiras:** GRC & Auditoria, Operações SOC & Resposta, Analista de SI
- **Subtítulo:** "Tipos de exercício, injects, facilitação e relatório pós-ação com plano de melhorias"
- **Objetivos:**
  - Diferenciar exercícios tabletop, funcionais e completos (NIST SP 800-84).
  - Escrever *injects* e conduzir a sessão como facilitador.
  - Produzir um relatório pós-ação (*after-action report*) com plano de melhorias.
- **Pré-requisitos:** Resposta-a-Incidentes.
- **Conceitos-chave:** objetivos do exercício; cenário e *injects*; papéis (facilitador, participantes, observadores); *hot wash*; relatório pós-ação; plano de melhorias com responsável e prazo.
- **Pergunta-chave:** "Como descobrir as falhas do plano de resposta antes de um incidente real?"
- **Simulador: *Gerador de Tabletop*.** O aluno escolhe um cenário (ransomware, vazamento de dados ou queda de fornecedor) e recebe os *injects* em sequência, com cronômetro. Registra as respostas e, ao fim, recebe um relatório pós-ação pronto para copiar, que serve também como peça de portfólio.
- **Fatos:**
  - "Tipos de exercício (NIST SP 800-84)"
  - "Injects e papel do facilitador"
  - "Relatório pós-ação e plano de melhorias"
  - "Gerador de tabletop com cronômetro e relatório"

#### 45 · `Backup-Imutavel-e-Recuperacao`: Backup Imutável e Recuperação de Identidade

- **Trilha:** 10 · **NIST:** Recover · **Tempo:** 45 min
- **MITRE:** T1490 Inhibit System Recovery / T1485 Data Destruction (mitigação)
- **Carreiras:** Blue Team & Defesa, GRC & Auditoria, Analista de SI
- **Subtítulo:** "Regra 3-2-1-1-0, imutabilidade, air gap e recuperação do Active Directory"
- **Objetivos:**
  - Aplicar a regra 3-2-1-1-0 (cópia imutável ou offline e zero erros nos testes de restauração).
  - Diferenciar imutabilidade (WORM, *object lock*) de *air gap*.
  - Separar as credenciais do backup do domínio de produção.
  - Planejar a recuperação do AD (ordem de restauração, DSRM).
- **Pré-requisitos:** Continuidade-e-Disaster-Recovery, Active-Directory-Fundamentos.
- **Conceitos-chave:** 3-2-1 vs 3-2-1-1-0; WORM e *object lock*; *air gap* lógico vs físico; console de backup fora do domínio; MFA no console; testes de restauração; recuperação de floresta; DSRM.
- **Diferença para o módulo 28:** o 28 ensina RTO/RPO e a regra 3-2-1 básica; este trata de como o backup sobrevive a um atacante com privilégio de administrador do domínio.
- **Pergunta-chave:** "Seu backup sobrevive a um atacante que já é administrador do domínio?"
- **Simulador: *Teste de Sobrevivência do Backup*.** O aluno monta a arquitetura de backup de uma empresa fictícia e roda um ataque com credencial de administrador do domínio. O simulador mostra quais cópias sobrevivem e por quê.
- **Fatos:**
  - "Regra 3-2-1-1-0"
  - "Imutabilidade, object lock e air gap"
  - "Recuperação do Active Directory"
  - "Teste de sobrevivência do backup a um admin de domínio"

### 2.4 Ordenação

Os 12 módulos entram ao fim de `estudos.txt` e de `ESTUDOS_DADOS` na ordem 34 → 45 acima. Nenhum módulo existente muda de posição.

---

## 3. Rotas, Necessidades e Certificações

### 3.1 `ROTA_VAGA`: módulos de apoio

Os 7 requisitos, os textos e os módulos **principais** não mudam. Entram só módulos de **apoio**, acrescentados ao fim de cada lista:

| `id` | Apoio atual | Apoio novo |
|---|---|---|
| `solucoes` | Engenharia-Social-e-Phishing | + Linux-para-Seguranca, PowerShell-e-Windows-Interno |
| `controles` | Hardening-Sistemas, Arquitetura-Zero-Trust | + Active-Directory-Fundamentos, PAM-e-Acessos-Privilegiados |
| `resposta_incidentes` | Operacoes-SOC-e-SIEM, Forense-Digital | + Ransomware-Prevencao-a-Recuperacao, Gestao-de-Crise-e-Comunicacao |
| `formacao` | — | + Laboratorio-Domestico-e-Portfolio |

Os 7 módulos acima levam "Analista de Segurança da Informação" em `carreiras` (teste existente `test_modulos_da_rota_tem_carreira_analista`). O contador de competências cobertas continua considerando só os principais.

### 3.2 Rotas por perfil (§5 do `CURRICULO.md`)

Nenhuma rota nova. As 6 existentes passam a ser:

| Rota | Sequência nova (módulos novos em **negrito**) |
|---|---|
| 1. Blue Team / Analista SOC | 01 → 02 → **34** → **36** → 05 → 06 → 07 → 10 → **39** → 16 → 17 → 18 → **42** |
| 2. Red Team / Pentest | 01 → 02 → **34** → 04 → 11 → 12 → 13 → **38** → **39** → 14 → 15 |
| 3. DevSecOps & Cloud Security | 01 → 03 → 04 → **35** → 06 → 12 → 13 → 21 → **41** → 22 → 24 |
| 4. GRC, Auditoria & Privacidade | 01 → 08 → **40** → 09 → 25 → 26 → 27 → 28 → **43** → **44** |
| 5. Perícia & Resposta a Incidentes | 01 → 02 → 06 → **36** → 10 → 16 → 18 → **42** → **45** → 19 → 20 |
| 6. Analista de Segurança da Informação (vaga) | 01 → **34** → **36** → 05 → 06 → 07 → 10 → 29 → 30 → **38** → **40** → 25 → 26 → 31 → 18 → **42** → **43** → 32 → **37** → 33 |

### 3.3 `NECESSIDADES`: 12 itens novos

Acrescentados ao fim da lista, um por módulo:

| Desafio | Slug | Categoria | Ícone |
|---|---|---|---|
| Preciso investigar um servidor Linux suspeito pela linha de comando | Linux-para-Seguranca | Ferramentas | 🐧 |
| Preciso automatizar a triagem de logs e consultar a reputação de IPs | Python-para-Seguranca | Automação | 🐍 |
| Preciso reconstruir uma intrusão a partir dos eventos do Windows | PowerShell-e-Windows-Interno | Ferramentas | 🪟 |
| Preciso montar um laboratório e um portfólio para entrevistas | Laboratorio-Domestico-e-Portfolio | Carreira | 🧪 |
| Preciso entender Kerberos e a herança de GPOs no Active Directory | Active-Directory-Fundamentos | Identidade | 🏛️ |
| Preciso detectar Kerberoasting e fechar caminhos até Domain Admin | Ataques-e-Defesa-no-AD | Identidade | 🕸️ |
| Preciso controlar e auditar contas de administrador | PAM-e-Acessos-Privilegiados | Identidade | 🗝️ |
| Preciso escrever políticas de acesso condicional no Entra ID | Identidade-Hibrida-e-Nuvem | Identidade | ☁️ |
| Preciso conter um ataque de ransomware e retomar a operação | Ransomware-Prevencao-a-Recuperacao | Resiliência | 🔒 |
| Preciso coordenar a crise e comunicar o incidente à ANPD | Gestao-de-Crise-e-Comunicacao | Resiliência | 📣 |
| Preciso conduzir um exercício tabletop com a diretoria | Exercicios-Tabletop | Resiliência | 🎲 |
| Preciso garantir que o backup sobreviva a um admin de domínio comprometido | Backup-Imutavel-e-Recuperacao | Resiliência | 💾 |

### 3.4 `CERTIFICACOES`: módulos acrescentados

Só onde o domínio da certificação cobre o tema com clareza. Os módulos são acrescentados ao fim de cada lista:

| Sigla | Módulos novos |
|---|---|
| GSEC | Linux-para-Seguranca, PowerShell-e-Windows-Interno, Active-Directory-Fundamentos |
| Security+ | PAM-e-Acessos-Privilegiados, Ransomware-Prevencao-a-Recuperacao, Backup-Imutavel-e-Recuperacao |
| CISSP | Active-Directory-Fundamentos, PAM-e-Acessos-Privilegiados, Backup-Imutavel-e-Recuperacao |
| CISM | Gestao-de-Crise-e-Comunicacao, Exercicios-Tabletop |
| CEH | Ataques-e-Defesa-no-AD |
| CCSP | — |

---

## 4. Pipeline, Design System e Documentação

### 4.1 Arquivos alterados

| Arquivo | Alteração |
|---|---|
| `_geradores/estudos.txt` | Cabeçalho "45 Módulos" e legenda das trilhas 8–10; 12 linhas novas (§2.2) |
| `_geradores/index_dados.py` | `TRILHAS[8..10]` (§2.1); 12 entradas em `ESTUDOS_DADOS` (§2.3); apoio em `ROTA_VAGA` (§3.1); 12 `NECESSIDADES` (§3.3); `CERTIFICACOES` (§3.4); docstring e comentários sem "33" e "7" fixos |
| `_geradores/montar.py` | Ajuda do `--trilha` sem faixa fixa ("número da trilha, conforme o catálogo") |
| `_geradores/base.css` | `--t8-slate`, `--t9-indigo`, `--t10-orange` nos 4 blocos de tema (`:root` claro, `@media (prefers-color-scheme: dark)`, `[data-theme="dark"]`, `[data-theme="light"]`); `.badge-t8`, `.badge-t9`, `.badge-t10` com fundo a 15% da cor clara (`rgba(71, 85, 105, 0.15)`, `rgba(79, 70, 229, 0.15)`, `rgba(194, 65, 12, 0.15)`); comentário "10 Trilhas" |
| `_geradores/index.css` | Os mesmos 3 tokens nos 4 blocos; `.track-tile.t8`, `.t9`, `.t10` |
| `_geradores/CURRICULO.md` | §1 com "45 módulos / 10 trilhas"; §2 com T8–T10 no diagrama Mermaid (T8 → PR, DE; T9 → PR, DE; T10 → RS, RC) e na tabela; §3 com o detalhamento dos módulos 34–45; §4 com a distribuição NIST **recalculada a partir de `estudos.txt`**; §5 com as rotas do §3.2 |
| `README.md` | "45 módulos / 10 trilhas"; T8–T10 no diagrama; tabela com 45 linhas; apoio novo na seção "Rota por Vaga" |
| `index.html` | Regenerado por `./_geradores/gerar.sh portal` |
| Treinamentos 01–11 | Recompilados por `./_geradores/gerar.sh todos`, porque `base.css` é embutido nas páginas |
| `docs/superpowers/specs/2026-10-15-competencias-vaga-analista-si-design.md` | Nota no topo: "Grade ampliada para 45 módulos / 10 trilhas, ver `2026-11-01-trilhas-empregabilidade-design.md`" |

### 4.2 Arquivos que não mudam

- `build_index.py`: os botões de filtro, os blocos de trilha (`track-tile t{id}`) e as contagens do cabeçalho já são gerados a partir de `TRILHAS` e do catálogo. Se a implementação encontrar algum valor fixo, ele é corrigido como parte desta spec.
- `base.js`, `gerar.sh`, `diagramas.py` e os `*_body.html` existentes.

---

## 5. Testes e Verificação

### 5.1 Princípio

TDD (Red → Green → Refactor) com `unittest`. Antes de rodar a suíte, conferir `free -h`; a suíte inteira roda dentro de `systemd-run --user --scope --quiet -p MemoryMax=4G -p MemorySwapMax=1G`, conforme as instruções da máquina.

### 5.2 Testes existentes: contagens derivadas dos dados (abordagem A)

| Arquivo | Ajuste |
|---|---|
| `test_curriculo.py` | `test_estudos_txt_contains_33_valid_entries` vira validação de formato sem contagem fixa; trilha válida = `int(trilha) in TRILHAS`. `test_curriculo_cobre_33_modulos_e_rota` passa a exigir também os nomes "Trilha 8: Ferramentas & Automação do Analista", "Trilha 9: Identidade Corporativa & Active Directory" e "Trilha 10: Resiliência, Crise & Ransomware" |
| `test_index.py` | `len(ESTUDOS_DADOS) == len(linhas de estudos.txt)`; trilha válida = `dados["trilha"] in TRILHAS`; `TRILHAS` com chaves contíguas `1..len(TRILHAS)` e cada trilha com módulo em `estudos.txt`; o portal contém `str(len(catálogo))` e `str(len(TRILHAS))` |
| `test_cli.py` | README cita todos os slugs de `estudos.txt`, sem contagem fixa |
| `test_assets.py` | A lista fixa de 7 tokens e `test_trilha7_tokens_em_4_blocos` viram um teste por trilha de `TRILHAS`: `--t{id}-{cor_nome}:` aparece exatamente 4 vezes em `base.css` e em `index.css`; `base.css` define `.badge-t{id}`; `index.css` define `.track-tile.t{id}` |

### 5.3 Teste único de tamanho da grade

Em `test_curriculo.py`, `test_tamanho_da_grade`: `estudos.txt` tem **45** módulos e `TRILHAS` tem **10** trilhas. É o único lugar onde esses números aparecem; crescer a grade exige mudá-lo de propósito.

### 5.4 Testes novos: `_geradores/testes/test_trilhas_empregabilidade.py`

1. Os slugs do §2.2 ocupam as posições 34–45 de `ESTUDOS_DADOS`, nessa ordem, com as trilhas 8, 9 e 10 do §2.2.
2. `TRILHAS[8..10]` têm os nomes, cores e `cor_nome` do §2.1.
3. Em `ROTA_VAGA`, os módulos principais de todas as 7 competências são exatamente os de antes (lista fixa no teste), e os apoios do §3.1 estão presentes.
4. Cada um dos 12 módulos novos aparece em pelo menos um item de `NECESSIDADES`.
5. As associações do §3.4 estão em `CERTIFICACOES`.
6. O módulo 37 tem todas as carreiras de `CARREIRAS`.
7. `CURRICULO.md` contém as 6 sequências de rota do §3.2.

### 5.5 Critérios de aceite

- `python3 -m unittest discover -s _geradores/testes -v` passa inteira.
- `./_geradores/gerar.sh portal` e `./_geradores/gerar.sh todos` executam sem erro.
- O `index.html`, nos temas claro e escuro e em largura de celular, mostra:
  - as Trilhas 8–10 no filtro e no mapa de trilhas, com as cores do §2.1;
  - os 12 cards novos como pendentes;
  - os chips de apoio novos na Rota da Vaga, também como pendentes;
  - nenhuma rolagem horizontal e nenhum erro no console.

---

## 6. Próximos Passos (fora desta spec)

Os módulos 12–45 seguem a fila normal de construção, um por commit, com o padrão estabelecido (`*_body.html` + teste próprio + compilação). O detalhamento do §2.3, copiado para o `CURRICULO.md`, é a especificação de conteúdo de cada módulo novo. Antes de construir o módulo 43, resolver as pendências de verificação listadas nele.
