# Mapa da Cibersegurança, Módulos 61 e 62 e Ampliação de Redes: Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Levar o nome "Mapa da Cibersegurança" ao repositório inteiro sem o nome do autor, ampliar o Estudo 02 (CIDR, roteamento/NAT, HTTP, Wi-Fi) e criar os módulos 61 (Fundamentos de Computação e SO) e 62 (Exploração e Escalada de Privilégio), com catálogo, rotas e certificações em 62 módulos.

**Architecture:** Portal estático e offline. Cada módulo é um corpo `_geradores/<slug_snake>_body.html` compilado por `montar.py` para `<Pasta>/treinamento-<slug-kebab>.html`; metadados vêm de `_geradores/index_dados.py` e `_geradores/estudos.txt` (a ordem das linhas é o número do módulo). Simuladores em JavaScript puro leem um bloco `<script type="application/json">`; os testes `unittest` espelham as regras em Python.

**Tech Stack:** Python 3 (`unittest`), HTML/CSS/JS puro, Mermaid pré-compilado, `_geradores/gerar.sh`.

**Spec:** `docs/superpowers/specs/2026-11-04-fundamentos-computacao-e-exploracao-design.md`

## Global Constraints

- Trabalho num branch `feat/fundamentos-e-exploracao` (ou worktree criado pelo executor); nada direto na `main`.
- Textos em pt-BR, no tom e no contrato do `_geradores/GUIA-DO-AUTOR.md` §2.2 (um `article`; seções com `class`/`id`/`data-tipo` nessa ordem; `h2` no início; callout sempre com modificador). Checklist de 4 a 8 itens; ao menos 6 `quiz-item` e 1 `pre class="mermaid"` por módulo novo.
- Módulos 61 e 62 no **fim** de `estudos.txt`, nessa ordem; módulos 01–60 não mudam de número nem de trilha.
- Cenário fictício: Ipê Store. Hosts só em `*.ipestore.example`; IPs só em RFC 5737 (`192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`) ou RFC 1918.
- Módulo 62: nenhum payload funcional contra alvo real, nenhum exploit de CVE copiável; abertura com callout `law` citando autorização por escrito e a Lei 12.737/2012 (remete ao Estudo 14 e ao 37); cada seção de técnica termina com callout `tip` "Como o defensor vê".
- Remissões por número: 05 Segmentacao-e-Firewall, 06 Hardening-Sistemas, 10 Seguranca-em-Endpoints-EDR, 12 OWASP-Top-10-Web, 14 Pentest-Metodologias, 33 Certificacoes-e-Carreira, 39 Ataques-e-Defesa-no-AD, 48 Monitoramento-de-Rede-NSM. Os demais, conferir a posição em `estudos.txt`.
- Números de RFC, padrão ou recurso de ferramenta só com fonte oficial conferida; na dúvida, "confira na fonte".
- Interface dos simuladores montada com `textContent`/`createElement`; sem `innerHTML =` com dado do usuário ou do JSON, sem `eval`, sem `fetch`.
- Testes: rodar a partir de `_geradores/` com `python3 -m unittest testes.<arquivo>`. Antes da suíte completa, `free -h`; com menos de ~4 GB disponíveis, só os arquivos afetados. Suíte completa só em `systemd-run --user --scope --quiet -p MemoryMax=4G -p MemorySwapMax=1G python3 -m unittest discover -s testes`. Nunca duas suítes em paralelo.
- Para truncar saída longa, `cut -c1-1500`; nunca `sed`/`grep` com intervalo grande no regex.
- Commits terminam com `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Review Focus

1. **A varredura de nome acusando a si mesma:** o teste que procura "José Mauro" e o nome antigo contém esses textos. Deve ignorar o próprio arquivo e `docs/superpowers/`, e varrer só arquivos versionados (`git ls-files`), pulando binários (Task 1, `test_varredura_ignora_a_si_mesma_e_binarios`).
2. **Texto com acento nos simuladores do 61:** a pilha conta **bytes UTF-8**, não caracteres (`"ç" * 9` = 18 bytes, estoura), e o Base64 faz ida e volta com acento sem o erro do `btoa` (Task 3, `test_bytes_utf8`).
3. **Entrada estranha no Repeater do 62:** vazia, só espaços, com HTML (`<img src=x onerror=…>`) ou com mais de 200 caracteres. Deve dar mensagem, não quebrar, e mostrar a entrada como texto, nunca como HTML (Task 4, `test_entradas_invalidas_do_repeater`).
4. **Calculadora CIDR com entrada inválida ou de borda:** `/33`, `256.1.1.1/24` e texto sem barra são recusados com mensagem. `/31` dá 2 hosts úteis (RFC 3021) e `/32` dá 1 (Task 2, `test_cidr_bordas_e_invalidos`).
5. **Progresso salvo do aluno:** os 60 primeiros slugs de `estudos.txt` continuam na mesma ordem, e os novos ficam em 61 e 62 (Task 4, `test_numeracao_preservada`).

---

### Task 1: Nome "Mapa da Cibersegurança" e remoção do nome do autor

**Files:**
- Create: `_geradores/testes/test_marca.py`
- Modify: `_geradores/montar.py` (docstring, `<title>` na linha ~221, `argparse` na ~252), `_geradores/gerar.sh`, `_geradores/index_dados.py`, `_geradores/glossario_dados.py` (cabeçalhos), `README.md`, `_geradores/CURRICULO.md`, `_geradores/GUIA-DO-AUTOR.md`, `_geradores/estudos.txt` (linha 1), `AGENTS.md`, `GEMINI.md` (se for arquivo próprio e não link)
- Modify: corpos `autenticacao_e_iam`, `seguranca_de_redes_defesa`, `arquitetura_zero_trust`, `segmentacao_e_firewall`, `hardening_sistemas`, `gestao_de_vulnerabilidades` (`_body.html`): comentário `Estudos de Cibersegurança - José Mauro da Silva Brandão` → `Mapa da Cibersegurança`
- Modify: `_geradores/testes/test_cli.py:99` ("Mapa da Cibersegurança")
- Recompilados: todos os `treinamento-*.html` e `index.html`

**Interfaces:**
- Produces: `PROIBIDOS = ("José Mauro", "Brandão", "Stelling", "Estudos de Cibersegurança", "Estudos em Cibersegurança")` em `test_marca.py`; as tasks seguintes não podem reintroduzir esses textos.

- [ ] **Step 1: Escrever `test_marca.py` (falhando).** Lista os arquivos com `git ls-files` (raiz do repositório), ignora os prefixos `docs/superpowers/`, `.agents/`, `perfis-linkedin/`, `.superpowers/` e o próprio `_geradores/testes/test_marca.py`, e pula arquivos que não decodificam como UTF-8. Testes:
  - `test_sem_nome_antigo_nem_autor`: nenhum arquivo contém algum item de `PROIBIDOS`; a mensagem de falha lista `arquivo: termo`.
  - `test_nome_novo_presente`: `Mapa da Cibersegurança` aparece em `README.md` (no título `# Mapa da Cibersegurança`), em `index.html` e no `<title>` de `Fundamentos-Ciber/treinamento-fundamentos-ciber.html` (termina com `— Mapa da Cibersegurança</title>`).
  - `test_varredura_ignora_a_si_mesma_e_binarios`: a função de listagem não devolve `_geradores/testes/test_marca.py` e não levanta erro com os `.woff2` de `_geradores/fontes/`.
  Rodar `python3 -m unittest testes.test_marca` → FAIL listando os arquivos atuais.

- [ ] **Step 2: Trocar os textos** dos arquivos listados em **Files**. No README, a linha `- **Autor:** José Mauro da Silva Stelling` sai (sem colocar outro nome). `Estudos em/de Cibersegurança` → `Mapa da Cibersegurança` (ajustar a concordância: "o projeto **Mapa da Cibersegurança**", "a plataforma Mapa da Cibersegurança"). `test_cli.py:99` passa a exigir `Mapa da Cibersegurança`.

- [ ] **Step 3: Recompilar tudo:** `./gerar.sh todos` → sem erro.

- [ ] **Step 4: Rodar** `python3 -m unittest testes.test_marca testes.test_cli testes.test_index testes.test_montar testes.test_compilados_atualizados testes.test_documentacao` → PASS.

- [ ] **Step 5: Commit** `chore(marca): projeto passa a se chamar Mapa da Cibersegurança e o nome do autor sai do repositório`.

---

### Task 2: Estudo 02, endereçamento, roteamento, HTTP e Wi-Fi

**Files:**
- Modify: `_geradores/redes_e_protocolos_body.html` (seção nova `id="enderecamento-http-wifi"` entre `dissecacao-protocolos` e `laboratorio-inspetor`; 2+ `quiz-item` novos em `questoes-fixacao`; referências em `fatos-essenciais`)
- Modify: `_geradores/index_dados.py` (`ESTUDOS_DADOS["Redes-e-Protocolos"]`: `subtitulo` e `fatos` com os temas novos)
- Modify: `_geradores/testes/test_redes_protocolos.py`
- Recompilado: `Redes-e-Protocolos/treinamento-redes-e-protocolos.html`

**Interfaces:**
- Produces: função JS `calcularCidr(texto)` no `<script>` do corpo, devolvendo `{rede, broadcast, mascara, prefixo, hosts_uteis, primeiro, ultimo}` ou `{erro: string}`; elementos `#cidr-entrada`, `#cidr-resultado`.

- [ ] **Step 1: Testes novos em `test_redes_protocolos.py` (falhando).**
  - `test_secao_enderecamento`: ids na ordem `modelos-rede`, `dissecacao-protocolos`, `enderecamento-http-wifi`, `laboratorio-inspetor`, `checklist-pratico`, `questoes-fixacao`, `fatos-essenciais`; a seção nova contém `CIDR`, `máscara`, `broadcast`, `RFC 1918`, `RFC 5737`, `gateway`, `NAT`, `PAT`, `não é firewall`, `GET`, `POST`, `HTTP/2`, `HTTP/3`, `Set-Cookie`, `WPA2-PSK`, `802.1X`, `WPA3`, `SAE`, `4-way handshake`, `evil twin`, `Estudo 05`, `Estudo 12`.
  - `test_questoes_e_referencias_novas`: `quiz-item` ≥ 5 (hoje 3); `fatos-essenciais` contém `RFC 4632`, `RFC 1918`, `RFC 9110`, `IEEE 802.11`, `WPA3`.
  - `test_cidr_espelhado`: `cidr(texto) -> dict` em Python (via `ipaddress`): `cidr("192.168.10.77/26")` → rede `192.168.10.64`, broadcast `192.168.10.127`, máscara `255.255.255.192`, `hosts_uteis` 62, primeiro `192.168.10.65`, último `192.168.10.126`; `cidr("10.0.0.0/8")["hosts_uteis"]` = 16777214. O corpo contém `function calcularCidr(`.
  - `test_cidr_bordas_e_invalidos`: `/31` → `hosts_uteis` 2; `/32` → 1; `"10.0.0.1/33"`, `"256.1.1.1/24"`, `"10.0.0.1"` e `""` → `{"erro": ...}`. O JS contém a mensagem `"Use o formato 192.168.1.10/24"` e o caso de `/31` com `RFC 3021` num comentário ou no texto de saída.
  Rodar `python3 -m unittest testes.test_redes_protocolos` → FAIL.

- [ ] **Step 2: Escrever a seção e a calculadora** com o conteúdo da spec §6: tabela HTTP/1.1 × HTTP/2 × HTTP/3, tabela WPA2-PSK × WPA2-Enterprise × WPA3, callout `warning` "NAT não é firewall". A calculadora valida octetos de 0 a 255 e prefixo de 0 a 32, e calcula com inteiros sem sinal (`>>> 0`). A seção nova é `data-tipo="teoria"`. Atualizar `subtitulo` e `fatos` do Estudo 02.

- [ ] **Step 3: Compilar** `./gerar.sh Redes-e-Protocolos` → sem erro.

- [ ] **Step 4: Rodar** `python3 -m unittest testes.test_redes_protocolos testes.test_corpos_migrados testes.test_index testes.test_marca` → PASS.

- [ ] **Step 5: Commit** `feat(redes): Estudo 02 ganha CIDR, roteamento e NAT, HTTP e Wi-Fi`.

---

### Task 3: Módulo 61 Fundamentos de Computação e SO

**Files:**
- Create: `_geradores/fundamentos_de_computacao_e_so_body.html`
- Create: `_geradores/testes/test_fundamentos_computacao.py`
- Create (compilado): `Fundamentos-de-Computacao-e-SO/treinamento-fundamentos-de-computacao-e-so.html`
- Modify: `_geradores/estudos.txt` (cabeçalho "61 Módulos", linha nova no fim), `_geradores/index_dados.py` (`ESTUDOS_DADOS`), `_geradores/testes/test_curriculo.py:29` (60 → 61)

**Interfaces:**
- Produces: slug `Fundamentos-de-Computacao-e-SO` (número 61); JSON `<script type="application/json" id="comp-dados">`; JS `identificarAssinatura(hex)`, `simularPilha(entrada, canario, aslr)`, `textoParaHex(texto)`, `hexParaTexto(hex)`, `textoParaBase64(texto)`, `base64ParaTexto(b64)`.

- [ ] **Step 1: Catálogo e metadados.** Linha no fim de `estudos.txt`:
  `Fundamentos-de-Computacao-e-SO|Fundamentos de Computação e SO para Segurança|Fundamentos-de-Computacao-e-SO|treinamento-fundamentos-de-computacao-e-so.html|1|#2563EB|Identify / Protect`
  `ESTUDOS_DADOS`: `titulo` igual ao título curto; `subtitulo` "Memória e processos, kernel e chamadas de sistema, binário e codificações, permissões e virtualização vistos pela segurança"; `trilha` 1; `nist` "Identify / Protect"; `mitre` "N/A (fundamentos de computação)"; `carreiras` `["Blue Team & Defesa", "Red Team & Pentest", ROTULO_ANALISTA_SI]`; `tempo_minutos` 40; `nivel` "intermediario"; `pergunta_chave` "Por que escrever 300 bytes num campo de 64 pode dar ao atacante o controle do servidor?"; `simulador_nome` "Inspetor de Bytes"; `fatos`: "Pilha, heap e o estouro de buffer", "ASLR, DEP/NX e stack canaries", "Kernel, espaço de usuário e chamadas de sistema", "Magic bytes, hexadecimal e Base64", "Hipervisor, VM e container". `test_curriculo.py`: 61.

- [ ] **Step 2: Escrever `test_fundamentos_computacao.py` (falhando)**, no padrão de `test_lideranca_e_programa.py`. `SLUG = "Fundamentos-de-Computacao-e-SO"`. Testes:
  - `test_body_and_compiled_files_exist`.
  - `test_secoes`: ids na ordem `["introducao", "memoria-e-processos", "kernel-e-syscalls", "binario-e-codificacoes", "arquivos-e-permissoes", "virtualizacao", "simulador", "checklist", "quiz", "fatos"]`; compilado contém `Seção 1 de 10` … `Seção 10 de 10`; `data-slug="fundamentos-de-computacao-e-so"`.
  - `test_coerencia_com_o_catalogo`: `simulador_nome`, `pergunta_chave` e cada `fato` no compilado; `subtitulo` no `index.html`.
  - `test_termos_chave`: `pilha`, `heap`, `endereço de retorno`, `buffer overflow`, `ASLR`, `DEP`, `NX`, `canário`, `kernel`, `espaço de usuário`, `chamada de sistema`, `rootkit`, `hexadecimal`, `little-endian`, `UTF-8`, `Base64`, `codificação não é criptografia`, `magic bytes`, `UID`, `SID`, `ACL`, `SYSTEM`, `setuid`, `hipervisor`, `tipo 1`, `tipo 2`, `namespaces`, `cgroups`.
  - `test_pontes_sem_repetir`: antes de `id="simulador"`, `Estudo 10`, `Estudo 62` e os números de Linux-para-Seguranca, PowerShell-e-Windows-Interno, Forense-Digital, Analise-Basica-de-Malware e Seguranca-de-Containers (obtidos de `estudos.txt` no teste); a seção `arquivos-e-permissoes` tem no máximo 1 `<table` e no máximo 600 palavras de texto.
  - `test_referencias`: em `id="fatos"`, `RFC 4648`, `Intel` ou `AMD` (manual de arquitetura), `ELF`, `PE`.
  - `test_dados_do_simulador`: JSON `#comp-dados` com `assinaturas` (6: `png` `89504E470D0A1A0A`, `pdf` `255044462D`, `zip` `504B0304`, `elf` `7F454C46`, `pe` `4D5A`, `script` `2321`), `arquivos` (6, cada um com `id`, `nome`, `hex`, `tipo_real` ∈ chaves de `assinaturas`; exatamente 1 com extensão de `nome` diferente de `tipo_real`), `pilha` = `{"buffer": 16, "canario": 8, "retorno": 8}`.
  - `test_assinaturas_espelhadas`: `identificar(hex)` devolve o tipo cujo prefixo casa (o mais longo primeiro); cada `arquivo["hex"]` → `tipo_real`; `"FFD8FF"` → `None`.
  - `test_pilha_espelhada`: `simular_pilha(entrada: str, canario: bool, aslr: bool) -> str` com resultados `"normal"`, `"abortado_canario"`, `"crash"`, `"controle_do_fluxo"`. Regra com `n = len(entrada.encode("utf-8"))`: `n <= 16` → normal; senão, com canário → abortado_canario; sem canário e com ASLR → crash; sem canário e sem ASLR: `n >= 24` → controle_do_fluxo, `16 < n < 24` → crash. Casos: `("A"*16, True, True)` normal; `("A"*17, True, False)` abortado_canario; `("A"*30, False, True)` crash; `("A"*20, False, False)` crash; `("A"*24, False, False)` controle_do_fluxo.
  - `test_bytes_utf8`: `simular_pilha("ç"*9, False, False)` = crash (18 bytes); o JS usa `TextEncoder` em `simularPilha` e em `textoParaBase64`/`textoParaHex`, e `TextDecoder` na volta; em Python, `base64` de `"ação"` é `"YcOnw6Nv"` e o corpo mostra esse exemplo.
  - `test_simulador_sem_apis_inseguras`: critério de `test_lideranca_e_programa.py`.
  - `test_componentes_pedagogicos`: `checklist-item` entre 4 e 8 (os 6 da spec §5.1); `quiz-item` ≥ 6; ao menos 1 `pre class="mermaid"`.
  Rodar `python3 -m unittest testes.test_fundamentos_computacao` → FAIL.

- [ ] **Step 3: Escrever o corpo** com o conteúdo da spec §5.1, no tom de revisão para quem já é de TI (sem definir o que é CPU ou RAM). Mermaid do espaço de endereçamento de um processo (texto, dados, heap, pilha, kernel). Laboratório com três abas (Assinatura, Decodificador, Pilha). A pilha é desenhada como 32 células (16 + 8 + 8; sem canário, 24) que se preenchem conforme a entrada, e as chaves "Canário" e "ASLR" mudam o resultado.

- [ ] **Step 4: Compilar** `./gerar.sh Fundamentos-de-Computacao-e-SO` → sem erro.

- [ ] **Step 5: Rodar** `python3 -m unittest testes.test_fundamentos_computacao testes.test_curriculo testes.test_portal testes.test_corpos_migrados testes.test_index testes.test_marca testes.test_auditoria_de_ti` → PASS.

- [ ] **Step 6: Commit** `feat(fundamentos): módulo 61 Fundamentos de Computação e SO`.

---

### Task 4: Módulo 62 Exploração e Escalada de Privilégio

**Files:**
- Create: `_geradores/exploracao_e_escalada_de_privilegio_body.html`
- Create: `_geradores/testes/test_exploracao_escalada.py`
- Create (compilado): `Exploracao-e-Escalada-de-Privilegio/treinamento-exploracao-e-escalada-de-privilegio.html`
- Modify: `_geradores/estudos.txt` (cabeçalho "62 Módulos", linha nova no fim), `_geradores/index_dados.py` (`ESTUDOS_DADOS`), `_geradores/testes/test_curriculo.py` (61 → 62; teste novo), `_geradores/testes/test_aba_nivel.py:19` (`AVANCADOS` ganha 62)

**Interfaces:**
- Consumes: Estudo 61 (remissão "Estudo 61" para pilha e memória).
- Produces: slug `Exploracao-e-Escalada-de-Privilegio` (número 62); JSON `<script type="application/json" id="exp-dados">`; JS `avaliarRepeater(entrada)`, `avancar(acao)`, `escolherVetor(id)`, `linhaDoTempo()`.

- [ ] **Step 1: Catálogo e metadados.** Linha no fim de `estudos.txt`:
  `Exploracao-e-Escalada-de-Privilegio|Exploração e Escalada de Privilégio|Exploracao-e-Escalada-de-Privilegio|treinamento-exploracao-e-escalada-de-privilegio.html|3|#DC2626|Identify`
  `ESTUDOS_DADOS`: `subtitulo` "Do scan ao root num laboratório autorizado: nmap, Burp Suite, shell, escalada no Linux e no Windows, e o que o defensor vê em cada passo"; `trilha` 3; `nist` "Identify"; `mitre` "TA0001 Initial Access, TA0002 Execution, TA0004 Privilege Escalation"; `carreiras` `["Red Team & Pentest"]`; `tempo_minutos` 55; `nivel` "avancado"; `pergunta_chave` "Do primeiro scan ao root: o que aconteceu, e onde o defensor poderia ter parado o ataque?"; `simulador_nome` "Da Porta ao Root"; `fatos`: "Varredura e enumeração com nmap", "Burp Suite: Proxy, Repeater e Intruder", "Reverse shell e Metasploit", "Escalada no Linux: sudo, SUID, cron e capabilities", "Escalada no Windows: serviços, tokens e credenciais", "A linha do tempo do defensor". `test_curriculo.py`: 62; `AVANCADOS` com 62.

- [ ] **Step 2: Escrever `test_exploracao_escalada.py` (falhando).** `SLUG = "Exploracao-e-Escalada-de-Privilegio"`. Testes:
  - `test_body_and_compiled_files_exist`; `test_secoes`: ids `["introducao", "varredura", "burp", "shell", "escalada-linux", "escalada-windows", "simulador", "checklist", "quiz", "fatos"]`, `Seção 1 de 10` … `Seção 10 de 10`; `test_coerencia_com_o_catalogo` (como na Task 3).
  - `test_termos_chave`: `nmap`, `-sV`, `NSE`, `Proxy`, `Repeater`, `Intruder`, `injeção de comando`, `reverse shell`, `bind shell`, `Metasploit`, `meterpreter`, `sudo -l`, `SUID`, `cron`, `capabilities`, `caminho sem aspas`, `SeImpersonatePrivilege`, `egress`, `auditd`.
  - `test_etica_e_defesa`: `introducao` tem `class="callout law"` com `autorização por escrito`, `Lei 12.737/2012`, `Estudo 14`; cada seção entre `varredura` e `escalada-windows` tem `class="callout tip"` com `Como o defensor vê`.
  - `test_pontes`: antes de `id="simulador"`, `Estudo 06`, `Estudo 12`, `Estudo 14`, `Estudo 39`, `Estudo 48`, `Estudo 61` e o número de PowerShell-e-Windows-Interno.
  - `test_cenario_ficticio`: todo hostname no corpo termina em `.ipestore.example` ou é `lab-web01`/`lab-win01`; todo IPv4 está em RFC 5737 ou RFC 1918 (checado com `ipaddress`).
  - `test_dados_do_simulador`: JSON `#exp-dados` com `estados` = `["scan", "burp", "shell", "escalada", "root"]`; `scan.opcoes` (lista de `{id, rotulo, valida: bool, saida: str}`, ao menos 1 válida e 1 inválida); `repeater` = `{"filtro_bloqueia": [";"], "separadores": [";", "&&", "|", "$(", "`"], "limite": 200}`; `vetores` (ao menos 4, cada um `{id, pista, valido: bool, explicacao}`, ao menos 2 válidos e 1 inválido); `eventos` (`{estado: [{fonte, mensagem}]}` com fontes em `{"IDS", "log web", "auditd"}`).
  - `test_repeater_espelhado`: `avaliar_repeater(dados, entrada) -> str`: `"normal"` sem separador; `"bloqueado"` se contém algum de `filtro_bloqueia`; `"injecao"` se contém outro separador. Casos: `"192.0.2.10"` normal; `"192.0.2.10; id"` bloqueado; `"192.0.2.10 && id"` injecao; `"192.0.2.10 | id"` injecao.
  - `test_entradas_invalidas_do_repeater`: `""`, `"   "` e uma entrada com 201 caracteres → `"invalida"`; `"<img src=x onerror=alert(1)>"` → normal (o filtro não trata HTML). O JS mostra a entrada com `textContent` (o teste procura `textContent` dentro de `avaliarRepeater` ou da função de saída dele e nenhum `innerHTML` no script) e tem a mensagem `"Digite um host para o diagnóstico"`.
  - `test_maquina_de_estados`: `percorrer(dados, acoes) -> (estado_final, linha_do_tempo)`. A opção de scan válida leva a `burp`; a inválida deixa em `scan`. Repeater `injecao` leva a `shell`, `bloqueado`/`normal` deixam em `burp`. Um vetor válido leva de `escalada` a `root`; um inválido deixa em `escalada`. O percurso completo válido termina em `root`, com `linha_do_tempo` contendo eventos de `IDS`, `log web` e `auditd`, nessa ordem de primeira aparição.
  - `test_windows_na_teoria`: `escalada-windows` contém um `<pre>` com saída fictícia de enumeração (ex.: `sc qc`, `whoami /priv`) e há ao menos 1 `quiz-item` que cita `SeImpersonatePrivilege` ou `caminho sem aspas`.
  - `test_simulador_sem_apis_inseguras`; `test_componentes_pedagogicos` (checklist 4–8 com os 6 itens "Antes de declarar root" da spec §5.2; `quiz-item` ≥ 6; ao menos 1 Mermaid).
  Em `test_curriculo.py`, `test_numeracao_preservada`: a linha 60 é `Estruturacao-da-Area-de-Seguranca`, a 61 é `Fundamentos-de-Computacao-e-SO`, a 62 é `Exploracao-e-Escalada-de-Privilegio`, e as 60 primeiras batem com os slugs da `main` antes desta branch (lista fixa gerada com `git show main:_geradores/estudos.txt` e colada no teste).
  Rodar `python3 -m unittest testes.test_exploracao_escalada testes.test_curriculo` → FAIL.

- [ ] **Step 3: Escrever o corpo** com o conteúdo da spec §5.2. Mermaid do percurso (scan → burp → shell → escalada → root) com o ponto de detecção de cada etapa. Laboratório com terminal e painel "Burp" (abas Proxy e Repeater) sobre `lab-web01.ipestore.example`. O campo do Repeater é o parâmetro `host` de um diagnóstico de ping. A etapa de escalada mostra uma saída fictícia de enumeração com as pistas dos `vetores`. No fim, o simulador exibe a linha do tempo do defensor. O laboratório percorre só o caminho Linux; o Windows fica na teoria, com o exercício da spec.

- [ ] **Step 4: Compilar** `./gerar.sh Exploracao-e-Escalada-de-Privilegio` → sem erro.

- [ ] **Step 5: Rodar** `python3 -m unittest testes.test_exploracao_escalada testes.test_curriculo testes.test_aba_nivel testes.test_portal testes.test_corpos_migrados testes.test_index testes.test_marca` → PASS.

- [ ] **Step 6: Commit** `feat(ofensiva): módulo 62 Exploração e Escalada de Privilégio`.

---

### Task 5: Rotas, certificações, documentação e totais (62 módulos)

**Files:**
- Modify: `_geradores/index_dados.py` (`ROTAS_PERFIL`, `CERTIFICACOES`)
- Modify: `_geradores/certificacoes_e_carreira_body.html` (JSON `#cert-dados`)
- Modify: `_geradores/auditoria_de_ti_body.html`, `_geradores/estruturacao_da_area_de_seguranca_body.html`, `_geradores/gestao_de_riscos_de_terceiros_body.html` ("60 módulos" → "62 módulos")
- Modify: `README.md`, `_geradores/CURRICULO.md`
- Modify: `_geradores/testes/test_certificacoes_carreira.py`, `test_curriculo.py`, `test_auditoria_de_ti.py`, `test_estruturacao_da_area.py`, `test_gestao_riscos_terceiros.py` ("60 módulos" → "62 módulos"), `test_rotas_sugeridas.py` (se fixar listas de rota)

**Interfaces:**
- Consumes: slugs `Fundamentos-de-Computacao-e-SO` (Task 3) e `Exploracao-e-Escalada-de-Privilegio` (Task 4); seção `enderecamento-http-wifi` do Estudo 02 (Task 2).

- [ ] **Step 1: Testes (falhando).**
  - `test_curriculo.py`: `test_modulos_novos_documentados`: `CURRICULO.md` contém `#### 61. Fundamentos-de-Computacao-e-SO` e `#### 62. Exploracao-e-Escalada-de-Privilegio`; o README contém `62 módulos` e os dois slugs; nem o README nem o CURRICULO contêm `60 módulos` ou `Módulos 01 a 05`.
  - `test_rotas_sugeridas.py` (ou `test_curriculo.py`): `test_rotas_dos_modulos_novos`: em `blue_soc`, `red_team`, `devsecops_cloud`, `pericia` e `analista_si`, `Fundamentos-de-Computacao-e-SO` vem logo depois de `Fundamentos-Ciber`; não está em `grc`; em `red_team`, `Exploracao-e-Escalada-de-Privilegio` vem logo depois de `Pentest-Metodologias`.
  - `test_certificacoes_carreira.py`:
    - `test_modulos_novos_na_matriz`: `CERTIFICACOES` tem o 62 em CEH, eJPT, eCPPT e OSCP e o 61 em Security+, GSEC e eCPPT.
    - Ajustar `test_lacuna_e_cobertura_parcial`: no CEH, nenhum domínio vazio; os parciais são exatamente "Ataques a redes sem fio" (com `Redes-e-Protocolos` e nota citando `Estudo 02`) e "Plataformas móveis, IoT e OT".
    - `test_notas_sem_lacuna_falsa`: eJPT "Teste de intrusão em hosts e redes" contém o 62 e não tem `parcial`; eCPPT "Exploração e pós-exploração" contém o 62 e não tem `parcial`; eCPPT "Desenvolvimento de exploits" contém o 61, tem `parcial` e uma nota que diz que o 61 explica o estouro mas não ensina a escrever exploit; OSCP "Escalada de privilégio no Windows e no Linux" contém o 62 e não tem `parcial`; nenhuma nota de eJPT, eCPPT ou OSCP diz `nenhum módulo` com `escalada` ou `exploração de serviços`.
  Rodar os três arquivos → FAIL.

- [ ] **Step 2: Rotas e matriz** em `index_dados.py`, como nos testes. 61 em Security+ no domínio "Arquitetura de segurança" e em GSEC em "Defesa em profundidade e controles críticos" (o `#cert-dados` recebe o mesmo).

- [ ] **Step 3: `#cert-dados`** no corpo do Estudo 33: os domínios e as notas dos testes. Reescrever qualquer outra nota que fique falsa com os módulos novos (ex.: a nota do eCPPT "Exploração e pós-exploração" sobre escalada; a do eJPT sobre exploração de serviços). Manter `conferido_em` e os pesos.

- [ ] **Step 4: Textos com total.** "60 módulos" → "62 módulos" nos três corpos e nos testes que os conferem. README: contagens, diagrama das trilhas (legendas da Trilha 1 e da 3 listam os números dos módulos, sem "01 a 05"), tabela de módulos, rotas dos perfis. CURRICULO: visão geral, diagrama, tabela de trilhas, `#### 61.` e `#### 62.` no detalhamento, distribuição NIST, rotas.

- [ ] **Step 5: Recompilar tudo:** `./gerar.sh todos` → sem erro.

- [ ] **Step 6: Suíte completa.** `free -h` (≥ ~4 GB disponíveis; senão, esperar ou rodar só os arquivos afetados e registrar). `systemd-run --user --scope --quiet -p MemoryMax=4G -p MemorySwapMax=1G python3 -m unittest discover -s testes` → `OK`.

- [ ] **Step 7: Varredura final:** `git grep -n -e "José Mauro" -e "Brandão" -e "Stelling" -e "Estudos de Cibersegurança" -e "Estudos em Cibersegurança" -- ':!docs/superpowers' ':!.agents' ':!_geradores/testes/test_marca.py'` → nenhuma saída.

- [ ] **Step 8: Commit** `feat(catalogo): rotas, certificações e documentação para 62 módulos`.
