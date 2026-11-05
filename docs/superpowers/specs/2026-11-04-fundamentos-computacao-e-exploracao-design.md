# Design Spec: Mapa da Cibersegurança — Módulos 61 e 62 e Ampliação de Redes

**Data:** 2026-11-04
**Status:** Em revisão pelo usuário (revisada por builder check em 2026-11-04)
**Repositório:** `estudos_cyberseguranca`
**Specs anteriores:** [`2026-11-03-lideranca-e-estrategia-design.md`](2026-11-03-lideranca-e-estrategia-design.md), [`2026-11-03-certificacoes-praticas-pentest-design.md`](2026-11-03-certificacoes-praticas-pentest-design.md)
**Referência Metodológica:** Superpowers Spec-Driven Development (SDD)

---

## 1. Propósito e Entendimento

O usuário comparou o catálogo com uma lista de 10 temas de uma formação em cibersegurança (Fundamentos de Computação e Redes; Linux e SO; Fundamentos de Segurança e Ameaças; Segurança de Redes; Criptografia; Web; Ethical Hacking; SIEM/SOC/IR; Nuvem; Certificações). A análise (2026-11-04) mostrou 7 temas bem cobertos e 3 parciais:

- **Fundamentos de Computação:** nenhum módulo trata memória, processos, kernel, binário/hexadecimal e virtualização; os termos aparecem só de passagem.
- **Ethical Hacking:** o Estudo 14 (Pentest-Metodologias) ensina o projeto (PTES, escopo, RoE, relatório), mas nenhum módulo ensina a execução técnica: exploração, shell, escalada de privilégio. "Burp" não aparece em nenhum arquivo.
- **Redes:** o Estudo 02 (Redes-e-Protocolos) cobre IPv4, TCP, UDP, DNS e ARP, mas não ensina sub-redes/CIDR, roteamento/NAT, HTTP nem segurança de Wi-Fi.

O usuário também pediu que o projeto passe a se chamar **Mapa da Cibersegurança** e que o nome dele saia da curadoria. O portal já foi trocado (commit `0ba3cd6`); falta levar o nome e a remoção para o resto do repositório.

### Estado atual (2026-11-04)

- 60 módulos em 14 trilhas. A numeração vem da ordem das linhas em `_geradores/estudos.txt`; módulos novos entram no fim (o 58 entrou assim na Trilha 6).
- Totais fixos: `test_curriculo.py` (60 linhas no catálogo, "60 módulos" no README) e textos "60 módulos" verificados por `test_auditoria_de_ti.py`, `test_estruturacao_da_area.py` e `test_gestao_riscos_terceiros.py` nos corpos de Auditoria-de-TI, Estruturacao-da-Area-de-Seguranca e Gestao-de-Riscos-de-Terceiros.
- O portal calcula o total a partir de `ESTUDOS_DADOS`, sem número fixo.
- O glossário tem um único verbete (HMAC); acrescentar verbetes não faz parte desta spec.
- O cenário fictício compartilhado entre módulos é a **Ipê Store** (loja `loja.ipestore.example`), usado em 41 corpos.

### Decisões do usuário

| Decisão | Escolha |
|---|---|
| Itens a fazer | Os três recomendados: módulo de Fundamentos de Computação e SO, módulo de Exploração e Escalada de Privilégio, ampliação de Redes e Protocolos |
| Público do módulo 61 | **Revisão para quem já é de TI**: conceitos vistos pelo ângulo da segurança, sem ensinar o que é um processador |
| Foco do módulo 62 | **Os dois**: o percurso de uma máquina do começo ao fim (estilo eJPT/OSCP) **e** exploração web com o Burp, numa história só (a falha web é a porta de entrada, a escalada termina o serviço) |
| Abordagem | **A**: dois módulos novos no fim da numeração (61 na Trilha 1, 62 na Trilha 3), sem renumerar os existentes |
| Nome do projeto | "Mapa da Cibersegurança" em todo o repositório, num commit separado, antes dos módulos |
| Nome do autor | Sai da curadoria e dos demais pontos onde aparece |

### Critérios de sucesso

- O catálogo tem **62 módulos em 14 trilhas**, consistente em `estudos.txt`, `index_dados.py`, `CURRICULO.md` e `README.md`.
- Os módulos 01–60 mantêm número e trilha.
- Os módulos 61 e 62 passam em `contrato.validar_corpo`, compilam com `montar.py` e têm teste próprio que espelha o motor do simulador (padrão dos testes por módulo, como `test_pentest.py`).
- O Estudo 02 tem a seção nova, com ao menos 2 questões de fixação novas e referências oficiais (RFCs, IEEE/Wi-Fi Alliance).
- `git grep` por "José Mauro", "Brandão", "Stelling", "Estudos de Cibersegurança" e "Estudos em Cibersegurança" retorna zero ocorrências fora de `docs/superpowers/` e `.agents/`.
- A suíte `unittest` passa inteira (com o teto de memória do `CLAUDE.md` global); `gerar.sh todos` compila o portal e as 62 páginas sem erro.

### Não objetivos

- Renumerar ou mudar a trilha de módulos existentes.
- Verbetes novos no glossário.
- Perfil de carreira, vaga ou certificação nova (CompTIA PenTest+ continua fora da matriz).
- Ampliar o Estudo 01 com uma tabela de tipos de malware ou DoS/DDoS (lacuna menor apontada na análise, fora do recomendado).
- Reescrever Linux-para-Seguranca ou PowerShell-e-Windows-Interno.

### Anti-objetivos (seria falha mesmo funcionando)

- O 61 virar curso de informática básica ("o que é RAM"). Todo conceito tem de aparecer ligado a um ataque, uma defesa ou uma evidência.
- O 61 repetir o que Linux-para-Seguranca, PowerShell-e-Windows-Interno, Forense-Digital ou Seguranca-de-Containers já ensinam. Onde o assunto encosta, o 61 dá a base em poucas linhas e remete.
- O 62 ensinar ataque sem o lado defensivo. Cada etapa traz "como o defensor vê e corrige".
- O 62 conter payload funcional contra alvo real, exploit de CVE específica copiável ou instrução para uso fora de laboratório. Comandos ilustram a técnica no laboratório fictício (`*.example`, faixas RFC 5737/RFC 1918), com o aviso de ética do Estudo 14.
- O 62 repetir a teoria do OWASP (Estudo 12) ou os ataques de domínio do Estudo 39 (Ataques-e-Defesa-no-AD). Remete a eles.
- Inventar números (versões de ferramentas, pesos de prova, datas de padrões). Vem da fonte oficial ou o texto diz "confira na fonte".

---

## 2. Abordagens Consideradas

| Abordagem | Troca | Decisão |
|---|---|---|
| **A. Dois módulos novos no fim da numeração** (61 na Trilha 1, 62 na Trilha 3) + seção nova no 02 | Mantém números, links, progresso salvo no navegador e as remissões "Estudo NN". O 61 é fundamento com número alto; as rotas sugeridas resolvem isso pondo o 61 no começo | **Escolhida** |
| B. Computação como 01 e renumeração do resto | Catálogo mais bonito, mas renumera 60 módulos, quebra o progresso salvo (`localStorage`) e dezenas de remissões | Descartada |
| C. Como A, mas o 62 dividido em dois (web e escalada) | Módulos de tamanho habitual, porém um simulador a mais e a história "da porta ao root" cortada ao meio, contra a escolha "os dois" | Descartada |

---

## 3. Parte 0 — Nome "Mapa da Cibersegurança" e remoção do nome do autor

Commit próprio, antes dos módulos.

| Onde | Mudança |
|---|---|
| `_geradores/montar.py` | Sufixo do `<title>` dos módulos: "— Mapa da Cibersegurança"; docstring e descrição do `argparse` |
| `_geradores/gerar.sh`, `index_dados.py`, `glossario_dados.py` | Cabeçalhos "Estudos em Cibersegurança" → "Mapa da Cibersegurança" |
| `README.md` | Título e menções ao nome; a linha "Autor: José Mauro da Silva Stelling" sai |
| `_geradores/CURRICULO.md`, `GUIA-DO-AUTOR.md`, `estudos.txt` | Título e menções ao nome |
| Corpos `autenticacao_e_iam`, `seguranca_de_redes_defesa`, `arquitetura_zero_trust`, `segmentacao_e_firewall`, `hardening_sistemas`, `gestao_de_vulnerabilidades` | O comentário "Estudos de Cibersegurança - José Mauro da Silva Brandão" vira "Mapa da Cibersegurança" |
| `testes/test_cli.py` | Passa a exigir "Mapa da Cibersegurança" no README |
| Teste novo | Varre o repositório (fora de `docs/superpowers/`, `.agents/`, `.git/`, `perfis-linkedin/`) e falha se achar o nome do autor ou o nome antigo do projeto |

Depois: `gerar.sh todos` recompila os 60 módulos e o portal.

`AGENTS.md`/`GEMINI.md` dizem "Estudos em Cibersegurança" na visão geral e também mudam. Specs e planos antigos em `docs/superpowers/` ficam como estão, por serem registro histórico.

---

## 4. Grade Curricular: 60 → 62 Módulos

### 4.1 Módulos novos

| Nº | Slug | Título curto | Corpo | Trilha | NIST | Nível | Tempo |
|---|---|---|---|---|---|---|---|
| 61 | `Fundamentos-de-Computacao-e-SO` | Fundamentos de Computação e SO para Segurança | `fundamentos_de_computacao_e_so_body.html` | 1 (`#2563EB`) | Identify / Protect | intermediário | 40 min |
| 62 | `Exploracao-e-Escalada-de-Privilegio` | Exploração e Escalada de Privilégio | `exploracao_e_escalada_de_privilegio_body.html` | 3 (`#DC2626`) | Identify | avançado | 55 min |

Pastas e HTML pela convenção: `Fundamentos-de-Computacao-e-SO/treinamento-fundamentos-de-computacao-e-so.html` e `Exploracao-e-Escalada-de-Privilegio/treinamento-exploracao-e-escalada-de-privilegio.html`.

`ESTUDOS_DADOS` no formato atual (`titulo`, `subtitulo`, `trilha`, `nist`, `mitre`, `carreiras`, `tempo_minutos`, `nivel`, `pergunta_chave`, `simulador_nome`, `fatos`):

- **61:** `mitre` "N/A (fundamentos de computação)"; carreiras: Blue Team & Defesa, Red Team & Pentest, `ROTULO_ANALISTA_SI`.
- **62:** `mitre` "TA0001 Initial Access, TA0002 Execution, TA0004 Privilege Escalation"; carreiras: Red Team & Pentest.

### 4.2 Rotas e certificações

- **`ROTAS_PERFIL`:** o 61 entra logo depois de `Fundamentos-Ciber` nas rotas `blue_soc`, `red_team`, `devsecops_cloud`, `pericia` e `analista_si` *(decisão do autor da spec: `pericia` entra porque dumps hex, assinaturas de arquivo e memória são a base da forense)*. Fica fora da rota `grc`. O 62 entra na rota `red_team` logo depois de `Pentest-Metodologias`.
- **`CERTIFICACOES`:** o 62 entra em `modulos` de CEH, eJPT, eCPPT e OSCP; o 61 entra em Security+, GSEC e eCPPT.
- **Estudo 33 (`#cert-dados`):** o JSON mapeia módulos a **domínios** de cada prova, com marcações `parcial`, domínios vazios ("Estude por fora") e notas. `test_coerencia_com_a_matriz_do_portal` exige que todo módulo de `CERTIFICACOES` apareça em algum domínio da certificação, então a mudança é obrigatória:
  - **eJPT**, domínio "Teste de intrusão em hosts e redes": entra o 62; a nota que diz que nenhum módulo cobre exploração e escalada é reescrita.
  - **OSCP**, domínio "Escalada de privilégio no Windows e no Linux": entra o 62; a nota é reescrita.
  - **eCPPT**, "Exploração e pós-exploração": entra o 62 e o domínio deixa de ser `parcial`. "Desenvolvimento de exploits": entra o 61, **marcado `parcial`** (o 61 explica por que o estouro funciona, mas não ensina a escrever exploit); a nota diz isso.
  - **CEH**, "Ataques a redes sem fio": entra o 02, **marcado `parcial`** (uma subseção de teoria, sem laboratório de Wi-Fi). `test_lacuna_e_cobertura_parcial`, que hoje exige esse domínio vazio, é ajustado para a nova realidade.
  - **Security+** e **GSEC**: o 61 entra no domínio de arquitetura/fundamentos de cada um (o implementador escolhe o domínio pelo nome no JSON).
  - Qualquer outra nota do Estudo 33 que fique falsa com os módulos novos é reescrita.
  *(Decisões do autor da spec, com base no que cada conteúdo de fato cobre.)*
- **`AVANCADOS`** em `test_aba_nivel.py` ganha o 62.

### 4.3 Arquivos de catálogo e textos com total

`estudos.txt` (cabeçalho "62 Módulos" e duas linhas novas no fim), `index_dados.py`, `CURRICULO.md` (visão geral, diagrama, tabela de trilhas, detalhamento dos dois módulos, distribuição NIST, rotas), `README.md` (contagens, diagrama, tabela de módulos). A frase "60 módulos" nos corpos de Auditoria-de-TI, Estruturacao-da-Area-de-Seguranca e Gestao-de-Riscos-de-Terceiros vira "62 módulos", junto com os testes que a verificam e `test_curriculo.py`. No README, a legenda da Trilha 1 deixa de dizer "Módulos 01 a 05", passando a listar os números, e a da Trilha 3 faz o mesmo.

---

## 5. Conteúdo dos Módulos

Os dois seguem o contrato do corpo (`GUIA-DO-AUTOR.md` §2): abertura com o problema real, seções de teoria, 1 laboratório, 1 checklist (4 a 8 itens), questões (ao menos 6, com resposta comentada) e referências oficiais. Cada um com ao menos 1 diagrama Mermaid. O cenário é a Ipê Store.

### 5.1 Módulo 61 — Fundamentos de Computação e SO para Segurança

**Público:** profissional de TI (suporte, infraestrutura, desenvolvimento) revendo a base pelo ângulo da segurança.

**Pergunta-chave:** "Por que escrever 300 bytes num campo de 64 pode dar ao atacante o controle do servidor?"

| Seção | Conteúdo |
|---|---|
| Memória e processos | Espaço de endereçamento de um processo; pilha × heap; quadro de pilha e endereço de retorno; por que o estouro de buffer funciona; ASLR, DEP/NX e stack canaries como resposta. Base para o 62 |
| Kernel, espaço de usuário e chamadas de sistema | Anéis de privilégio; system calls; drivers; por que rootkit de kernel é pior; o que o EDR observa (remete ao Estudo 10, EDR) |
| Binário, hexadecimal e codificações | Bits, bytes, hexadecimal; endianness; ASCII/UTF-8; Base64 (codificação não é cifra); *magic bytes* e assinaturas de arquivo. Remete a Malware e Forense |
| Arquivos, usuários e permissões: Linux × Windows | Tabela comparativa (UID/SID, rwx/ACL, root/SYSTEM, setuid/tokens), em poucas linhas, remetendo a Linux-para-Seguranca e PowerShell-e-Windows-Interno |
| Virtualização e containers | Hipervisor tipo 1 × tipo 2; isolamento de VM × container (namespaces, cgroups); fuga de VM e de container como classe de risco. Remete a Seguranca-de-Containers |

**Laboratório "Inspetor de Bytes".** Três abas em JavaScript puro:

1. **Assinatura de arquivo:** o aluno recebe os primeiros bytes (hex) de 6 arquivos fictícios, um deles com extensão falsa, e identifica o tipo (PNG, PDF, ZIP, ELF, PE, script) pelos *magic bytes*.
2. **Decodificador:** converte entre texto, hexadecimal e Base64, e mostra por que Base64 não protege um segredo.
3. **Pilha simulada:** um buffer de 16 bytes, o canário e o endereço de retorno desenhados como células. O aluno digita uma entrada e vê os bytes ocuparem a pilha; com entrada longa, o endereço de retorno é sobrescrito. Chaves "ASLR" e "canário" mostram como cada defesa muda o resultado.

O teste em Python espelha as três funções: identificação por assinatura, conversões hex/Base64 (ida e volta) e o resultado da pilha para entradas de tamanhos diferentes, com e sem canário.

**Checklist "Revisão de fundamentos para o analista":** ler um dump hex; reconhecer arquivo por assinatura; explicar pilha × heap; saber que proteções de memória o SO ativa; distinguir codificação de cifra; comparar permissões Linux × Windows.

### 5.2 Módulo 62 — Exploração e Escalada de Privilégio

**Pergunta-chave:** "Do primeiro scan ao root: o que aconteceu, e onde o defensor poderia ter parado o ataque?"

**Cenário:** `lab-web01.ipestore.example`, servidor de laboratório da Ipê Store com uma aplicação web interna e serviços expostos, dentro de um engajamento autorizado (remete ao escopo e às RoE do Estudo 14). Um segundo alvo, `lab-win01`, serve à parte de Windows.

| Seção | Conteúdo (atacante · defensor) |
|---|---|
| Varredura e enumeração | nmap (tipos de varredura, detecção de versão, scripts NSE), enumeração de diretórios web · o que aparece no IDS e no log do servidor; reduzir a superfície |
| Exploração web com o Burp Suite | Proxy, histórico, Repeater e Intruder; da manipulação da requisição à execução de comando (injeção de comando num campo de diagnóstico da aplicação) · WAF, validação no servidor, logs de aplicação. Remete ao Estudo 12 para a teoria |
| Acesso inicial e shell | Bind × reverse shell; estabilizar o shell; Metasploit e meterpreter como alternativa (quando ajuda, quando atrapalha e por que certas provas limitam o uso) · egress filtering, detecção de conexão de saída (remete ao Estudo 48, NSM) |
| Escalada de privilégio no Linux | Enumeração local; `sudo` mal configurado; binários SUID; cron gravável; capabilities; kernel desatualizado como último recurso · hardening e auditoria (remete ao Estudo 06, Hardening-Sistemas) |
| Escalada de privilégio no Windows | Serviços com caminho sem aspas ou permissão fraca; privilégios de token (SeImpersonate); credenciais em arquivos e no registro · eventos que denunciam cada técnica (remete a PowerShell-e-Windows-Interno e, para domínio, ao Estudo 39) |

Cada seção termina com um callout `tip` "Como o defensor vê". A abertura traz o callout `law` com o aviso de ética e a Lei 12.737/2012, como no Estudo 14.

**Laboratório "Da Porta ao Root".** Um terminal e um painel "Burp" simulados, guiados por um JSON de estados:

1. **Scan:** o aluno escolhe opções de varredura; o terminal devolve portas e versões fictícias.
2. **Burp:** o painel mostra a requisição do campo de diagnóstico; o aluno edita o parâmetro no Repeater e o simulador responde conforme a entrada (texto normal, injeção bloqueada por filtro ingênuo, injeção que passa).
3. **Shell:** a injeção certa abre um shell de usuário `www-data`.
4. **Escalada:** a saída fictícia de enumeração local traz pistas (um `sudo -l` permissivo, um SUID incomum, um cron gravável). O aluno escolhe o vetor; só os vetores válidos levam a root.
5. **Linha do tempo do defensor:** no fim, o simulador mostra os eventos que cada passo gerou (IDS, log web, auditd) e em que ponto cada controle teria parado o ataque.

O laboratório percorre só o caminho Linux. A escalada no Windows (`lab-win01`) fica na seção de teoria, com um exercício curto de identificação do vetor numa saída fictícia de enumeração (sem máquina de estados própria) e ao menos 1 questão *(decisão do autor da spec, para manter o módulo perto de 55 min)*.

Os comandos e as saídas são texto fictício montado pelo simulador; nada é executado. O teste em Python espelha a máquina de estados: transições válidas e inválidas, a resposta do Repeater para cada tipo de entrada, os vetores de escalada aceitos e a linha do tempo gerada.

**Checklist "Antes de declarar root":** escopo e autorização conferidos; evidência de cada passo (comando, saída, horário); nada destrutivo; credenciais encontradas tratadas como sigilosas; achados com correção e detecção sugeridas; ambiente devolvido ao estado original.

---

## 6. Ampliação do Estudo 02 — Redes-e-Protocolos

Seção de teoria nova, **"Endereçamento, Roteamento, HTTP e Wi-Fi"**, posta depois da seção de dissecação de protocolos e antes do laboratório:

- **Sub-redes e CIDR:** máscara, prefixo, rede, broadcast, hosts úteis; faixas privadas (RFC 1918) e de documentação (RFC 5737); por que a segmentação depende disso (remete ao Estudo 05). Inclui uma calculadora CIDR pequena (`<script>` do próprio corpo) com teste em Python espelhando o cálculo.
- **Roteamento e NAT:** tabela de rotas, gateway padrão, NAT/PAT; o NAT não é firewall.
- **HTTP:** métodos, cabeçalhos relevantes para segurança, códigos de resposta, cookies e HTTP/1.1 × HTTP/2 × HTTP/3 em uma tabela; remete ao Estudo 12.
- **Wi-Fi:** WPA2-PSK × WPA2-Enterprise (802.1X) × WPA3 (SAE); captura do *4-way handshake* e ataque de dicionário offline; *evil twin*; recomendações.
- Ao menos 2 questões novas na seção de questões existente e referências: RFC 4632 (CIDR), RFC 1918, RFC 9110 (semântica HTTP), IEEE 802.11 e a especificação WPA3 da Wi-Fi Alliance.

O `subtitulo` e os `fatos` do Estudo 02 em `ESTUDOS_DADOS` ganham os temas novos.

---

## 7. Ordem de Entrega

1. Parte 0 (nome e autor), commit próprio, recompilação completa.
2. Ampliação do Estudo 02.
3. Módulo 61.
4. Módulo 62.
5. Catálogo, rotas, certificações, documentação e totais (62), recompilação completa e suíte inteira.

## 8. O que fica com o implementador

- Redação final, textos das questões e escolha exata dos exemplos fictícios, dentro do que as seções acima definem.
- Detalhes visuais dos simuladores, reaproveitando os componentes CSS existentes (`.lab-box`, terminal e abas já usados em outros módulos).
- Confirmar nas fontes oficiais qualquer número ou nome citado (versões de RFC, especificações, nomes de recursos do Burp).
