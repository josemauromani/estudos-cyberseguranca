# Design Spec: Redesenho de UI/UX — UI Kit, Página de Módulo e Portal

**Data:** 2026-11-02
**Status:** Em revisão pelo usuário
**Repositório:** `estudos_cyberseguranca`
**Specs anteriores:** [`2026-10-06-estudos-cyberseguranca-design.md`](2026-10-06-estudos-cyberseguranca-design.md), [`2026-10-17-diagramas-mermaid-design.md`](2026-10-17-diagramas-mermaid-design.md), [`2026-11-02-trilhas-especializacao-design.md`](2026-11-02-trilhas-especializacao-design.md)
**Referência visual aprovada:** [`assets/2026-11-02-redesenho-ui-ux/mockup-modulo.html`](assets/2026-11-02-redesenho-ui-ux/mockup-modulo.html) e [`assets/2026-11-02-redesenho-ui-ux/mockup-portal.html`](assets/2026-11-02-redesenho-ui-ux/mockup-portal.html) (abrir no navegador; são funcionais)
**Referência Metodológica:** Superpowers Spec-Driven Development (SDD)

---

## 1. Propósito e Entendimento

O usuário pediu uma remodelação da UI e da UX dos módulos para que quem estuda **entenda em que tipo de seção está** (teoria, laboratório, checklist, questões de concurso, referências) e **onde está no módulo**, estendida a uma refatoração do UI kit de todo o site, incluindo o portal.

### Estado atual (2026-11-02)

- 57 módulos compilados por `_geradores/montar.py` a partir de `_geradores/<slug>_body.html` + `base.css` (1.260 linhas) + `base.js` (420 linhas). O portal `index.html` é gerado por `build_index.py` com `index.css` (1.293 linhas). Os dois CSS duplicam os tokens.
- Suíte `unittest` em `_geradores/testes/` (73 arquivos).

**Problemas de orientação:**

1. A página de módulo é uma coluna única de até ~16.000 px, sem sumário, sem progresso de leitura e sem indicação da seção atual.
2. Todas as 355 seções têm a mesma aparência; nada distingue teoria de laboratório ou de questões.
3. 48 módulos não têm cabeçalho (título, tempo, NIST, trilha aparecem só na barra superior).
4. As questões de concurso são `<details>` "Ver resposta explicada", sem registro de desempenho.
5. Os diagramas Mermaid são SVGs de tema escuro fixo e viram blocos pretos no tema claro.
6. No portal, a aba padrão empilha matriz de necessidades, rota por vaga e matriz de certificações antes do catálogo, que começa por volta de 10.000 px. Não há "continuar de onde parou".

**Defeitos encontrados:**

7. **Checklist quebrado em 56 módulos:** o markup usa `li.checklist-item`, mas `initChecklist()` (`base.js`) busca `.check-item`; nada é salvo e, sem CSS para `.checklist-item`, a lista aparece como bullets com checkbox nativo.
8. Classes usadas em massa sem estilo em `base.css`: `section-tag`, `study-header`, `lead-text`, `quiz-details`, `quiz-toggle`.
9. Conclusão do módulo (`cs_done_<slug>`) só pode ser marcada no portal.
10. Fontes vêm do Google Fonts; offline caem para Arial/Consolas, contrariando o "100% offline" do README.

**Três gerações de markup nos corpos:**

| Geração | Módulos | Marcas |
|---|---|---|
| G1 | `fundamentos_ciber` | `hero-header`, `content-section`, `check-item`, `quiz-btn` (múltipla escolha com `checkQuiz`), `callout-tip` |
| G2 | `arquitetura_zero_trust`, `autenticacao_e_iam`, `criptografia_pratica`, `gestao_de_vulnerabilidades`, `hardening_sistemas`, `redes_e_protocolos`, `segmentacao_e_firewall`, `seguranca_de_redes_defesa` | `header.study-header`, `section-num`/`section-title-wrap`, sem `article.study-container` |
| G3 | os 48 restantes | `article.study-container`, `span.section-tag` "Seção 0X" |

### Decisões do usuário

| Decisão | Escolha |
|---|---|
| Escopo | **UI kit + página de módulo + portal**, num redesenho único |
| Uso principal | Desktop, sessões longas; celular precisa funcionar bem |
| Layout do módulo | **Sumário lateral fixo** + barra fina de progresso no topo |
| Direção visual | **Editorial técnico**: evolução do visual atual (IBM Plex Sans/Mono, Barlow Semi Condensed, fundo cinza-claro); estética "console" só em terminal, laboratório e diagramas |
| Questões de concurso | **Flashcard ativo**: revelar → autoavaliar (Acertei / Errei / Revisar depois) → placar e filtros |
| Layout do portal | **Navegação lateral** espelhando o módulo; catálogo como tela inicial |
| Abordagem técnica | **Chassi gerado pelo `montar.py` + contrato de markup + migração automatizada** dos 57 corpos |
| Fontes | **Embutidas** (WOFF2, subconjunto latino) |
| Visual | Mockups de módulo e portal **aprovados** como referência |

### Critérios de sucesso

1. Em qualquer ponto da página de módulo, o aluno vê em que módulo está, em que seção, de que tipo ela é e quanto já leu.
2. Os cinco tipos de seção têm identidade visual própria (cor, ícone, rótulo) idêntica nos 57 módulos.
3. Checklist, autoavaliação das questões e "Concluir módulo" gravam e restauram estado em todos os módulos.
4. Portal e módulos usam os mesmos tokens e o mesmo esqueleto (barra superior + navegação lateral + conteúdo).
5. Cada HTML gerado funciona via `file://` sem rede, inclusive a tipografia.
6. O texto didático dos 57 módulos não muda (verificado por teste).
7. A compilação falha, com mensagem clara, se um corpo violar o contrato de markup.

### Fora de escopo

- Reescrever conteúdo didático, converter as questões abertas para múltipla escolha ou criar questões novas.
- Alterar a lógica dos simuladores dos laboratórios (só o invólucro visual muda).
- Renderizar os diagramas Mermaid em duas versões de tema (eles passam a ser exibidos numa placa escura nos dois temas).
- Novas visões no portal, novos dados curriculares, mudanças em `estudos.txt`, rotas, certificações ou necessidades.
- Busca dentro do conteúdo dos módulos (a busca do portal continua por metadados, como hoje).
- Estilos de impressão.

---

## 2. UI Kit

### 2.1 `tokens.css` (novo, `_geradores/tokens.css`)

Fonte única de tokens, embutida por `montar.py` e por `build_index.py` antes do CSS específico. `base.css` e `index.css` deixam de declarar tokens.

| Grupo | Tokens (claro → escuro) |
|---|---|
| Superfícies | `--ground` `#F4F6F8`→`#0E151A`; `--surface` `#FFFFFF`→`#152028`; `--sunk` `#EAEFF2`→`#1C2A33`; `--rule` `#D5DCE1`→`#2A3943`; `--rule-strong` `#C4CDD3`→`#364853` |
| Texto | `--ink` `#14212B`→`#E4EAED`; `--muted` `#5B6B77`→`#9BABB6` |
| Ação | `--accent` `#2563EB`→`#60A5FA`; `--accent-soft`; `--ok` `#15803D`→`#4ADE80`; `--bad` `#DC2626`→`#F87171` |
| Tipos de seção (`--x` / `--x-soft`) | `teo` `#2563EB`; `lab` `#0D9488`; `chk` `#B45309`; `qst` `#C026D3`; `ref` `#64748B` (variantes escuras conforme o mockup) |
| Callouts (`--x` / `--x-soft`) | `tip` `#059669`; `warn` `#EA580C`; `danger` `#DC2626`; `law` `#6D28D9`; pergunta-chave usa `--accent` |
| Console | `--console` `#0F1820`→`#0A1015`; `--console-ink` `#D6E2EA` |
| Trilhas | `--t1` … `--t13`, mantendo os valores atuais de `base.css`/`index.css` e acrescentando a variante escura onde faltar |
| Tipografia | `--f-display` Barlow Semi Condensed; `--f-body` IBM Plex Sans; `--f-mono` IBM Plex Mono |
| Forma | `--r-sm` 4px, `--r-md` 8px, `--r-lg` 12px; `--shadow` (nenhuma no escuro) |

O tema escuro é aplicado por `:root[data-theme="dark"]`. O tema inicial segue `cs_theme` ou, na ausência dele, `prefers-color-scheme` (comportamento atual de `initTheme`). Os valores exatos de cada variante escura são os do mockup aprovado. Contraste mínimo AA (4,5:1) para texto sobre `--ground`, `--surface` e cada `--x-soft`.

### 2.2 Fontes embutidas

- Arquivos WOFF2 (subconjunto latino + latino estendido) em `_geradores/fontes/`: IBM Plex Sans 400, 400 itálico, 600; IBM Plex Mono 400; Barlow Semi Condensed 700. Licença SIL OFL 1.1, cujo texto vai junto em `_geradores/fontes/OFL.txt`.
- `montar.py` e `build_index.py` geram `@font-face` com `src: url(data:font/woff2;base64,…)` e `font-display: swap`. O `<link>` para o Google Fonts é removido.
- Orçamento: até 200 KB de acréscimo por HTML gerado. Se os subconjuntos excederem, corta-se primeiro o itálico.

### 2.3 Componentes (`base.css`)

Seguem o mockup de módulo aprovado:

| Componente | Classes |
|---|---|
| Barra superior | `.topbar` (caminho Trilha › Estudo, selo do tipo da seção atual, alternância de tema, botão "☰ Sumário" abaixo de 1024 px) + `.readbar` (progresso de rolagem) |
| Esqueleto | `.shell` (grade 272 px + conteúdo de até 860 px) |
| Sumário | `.toc` (fixo; título, % lido, lista de seções com tipo, estado e contadores; "Concluir módulo"; anterior/próximo) |
| Cabeçalho do módulo | `.mhead` (filete na cor da trilha, kicker, `h1`, subtítulo, chips de metadados, `.roadmap` com os tipos presentes) |
| Seção tipada | `.study-section[data-tipo]` + `.shead` (`.stype` "📘 Teoria · Seção X de N" + `h2`, sublinhado na cor do tipo) |
| Callouts | `.callout` + `tip`/`warning`/`danger`/`law`/`key`, com `.callout-title` (ícone + rótulo) |
| Tabela | `.table-responsive` > `.data-table` |
| Terminal | `.terminal-box` (placa console, cabeçalho com título e botão copiar) |
| Diagrama | `.diagram-box` (cabeçalho claro + placa console onde fica o SVG) |
| Laboratório | `.lab-box` (cabeçalho console com rótulo "// laboratório interativo", corpo claro; controles e saída internos ao simulador mantêm suas classes) |
| Checklist | `.checklist` > `.checklist-item` (cabeçalho com "N de M" e barra; checkbox customizado; item marcado esmaecido) |
| Questões | `.quiz-score` (placar + filtros), `.quiz-item[data-res]` (filete por resultado), `.quiz-selfeval` (três botões) |
| Fatos e fim | `.facts-grid` > `.facts-card`, `.study-done` (caixa de conclusão), `.study-pager` (anterior/próximo) |

Ícones e rótulos dos tipos: 📘 Teoria, 🧪 Laboratório, ☑️ Checklist, ❓ Questões de concurso, 📚 Referências.

---

## 3. Página de Módulo

### 3.1 Contrato de markup do corpo (`_body.html`)

```html
<article class="study-container" data-slug="<slug-kebab>">
  <section class="study-section" id="<id>" data-tipo="teoria|laboratorio|checklist|questoes|referencias">
    <h2>Título da seção</h2>
    ...conteúdo...
  </section>
  ...
</article>
```

Regras verificadas pelo validador (§3.4):

1. Exatamente um `article.study-container` na raiz do corpo.
2. Cada filho de `article.study-container` é `section.study-section` com `id` único e `data-tipo` válido, nessa ordem de atributos (`class`, `id`, `data-tipo`), para manter compatíveis os testes que fazem regex sobre `<section class="study-section" id="…"`.
3. Cada seção tem exatamente um `h2` como primeiro elemento de título.
4. Sem cabeçalho de módulo (`study-header`, `hero-header`), sem `section-tag`/`section-num` e sem `footer`; o chassi gera esses elementos.
5. Pelo menos uma seção de cada tipo `laboratorio`, `checklist`, `questoes` e `referencias` (os 57 corpos atuais já têm os quatro).
6. Checklist: `ul.checklist` > `li.checklist-item` > `input[type=checkbox][id]` + `label[for]`.
7. Questão aberta: `div.quiz-item` > `.quiz-question` + `details.quiz-details` > `summary.quiz-toggle` + `.quiz-answer`. Questão de múltipla escolha (hoje só no Fundamentos-Ciber): `div.quiz-item[data-formato="multipla"]` com os `button.quiz-btn` atuais.
8. Callouts: `div.callout` com um dos modificadores `tip`, `warning`, `danger`, `law`, `key`.

### 3.2 Chassi gerado por `montar.py`

`montar.py` recebe o corpo validado e gera, a partir de `ESTUDOS_DADOS[slug]` e `TRILHAS` (`index_dados.py`) e da ordem do catálogo (`estudos.txt`):

- **Barra superior:** link para `../index.html`, "Trilha N · <nome> / NN · <título curto>", selo do tipo atual, botão de tema, botão de sumário.
- **Sumário:** "Estudo NN de <total>" (total vindo de `estudos.txt`, não fixo), título, barra de % lido, um item por seção (ícone, rótulo do tipo, título do `h2`, contador para `laboratorio`, `checklist` e `questoes`), botão "Concluir módulo", links para anterior e próximo.
- **Cabeçalho do módulo:** kicker "Trilha N · <nome da trilha> · Estudo NN", `h1` = `titulo`, subtítulo = `subtitulo`, chips (tempo, nível, NIST, MITRE, carreiras), mapa com os tipos presentes e quantidades (seções de teoria, itens de checklist, questões).
- **Em cada seção:** `.shead` com `.stype` "<ícone> <Tipo> · Seção X de N", envolvendo o `h2` original.
- **Fim:** caixa "Concluir módulo" e cartões anterior/próximo, inseridos ao final da última seção.

O contador do laboratório mostra o progresso só quando o simulador o informa (§3.3, `CS.labProgress`). Sem isso, o item do sumário não exibe contador.

### 3.3 Comportamento (`base.js`)

- **Seção atual:** a última seção cujo topo passou de 35% da altura da janela. Atualiza o selo da barra superior e o destaque no sumário (`aria-current="true"`).
- **Leitura:** uma seção conta como lida quando o seu fim passa de 60% da altura da janela, ou quando a página chega ao final. Grava em `cs_read_<slug>`.
- **Checklist:** `initChecklist()` passa a operar sobre `.checklist-item`, mantendo a chave `cs_check_<slug>_<inputId>`. Atualiza o cabeçalho "N de M" e o contador do sumário.
- **Flashcards:** ao abrir `details.quiz-details`, mostra a autoavaliação. O clique grava `cs_quiz_<slug>_<qid>` (`acertei`/`errei`/`revisar`) e atualiza o filete, o placar e o contador do sumário ("acertos/total"). `qid` = atributo `data-q` gerado pelo `montar.py` (`q1…qN` na ordem). Filtros: Todas, Erradas e a revisar, Sem resposta.
- **Múltipla escolha:** `checkQuiz()` registra `acertei` se o primeiro clique foi na alternativa correta, `errei` caso contrário, no mesmo placar.
- **Concluir:** alterna `cs_done_<slug>`. O botão fica verde quando todas as seções estão lidas e, depois de concluído, mostra "Concluído · desfazer".
- **Último acesso:** a cada mudança de seção grava `cs_last = {"slug", "secao", "ts"}`.
- **Laboratório (opcional):** `CS.labProgress(feitos, total)` permite que um simulador informe seu progresso ao sumário. Nenhum simulador é obrigado a chamá-lo.
- **API pública preservada:** `window.CS`, `toggleTheme`, `initTheme`, `initChecklist`, `initQuiz`, `checkQuiz`, `copyCode`, `isStudyDone`, `setStudyDone`, `safeStorageGet`, `safeStorageSet`, `escapeHtml`, `formatBytes`, `formatNumber`, `bytesToHex`, `hexToBytes`, `sha256Hex`.

### 3.4 Validador de contrato

A função `validar_corpo(html, slug) -> list[str]` em `_geradores/contrato.py` (novo) devolve a lista de violações das regras de §3.1, cada uma no formato `"<slug> §<regra>: <seção ou elemento>: <descrição>"`. `montar.py` chama o validador e aborta com código de saída 1 e as mensagens no stderr se a lista não estiver vazia. O parser é `html.parser` da biblioteca padrão; nenhuma dependência nova.

### 3.5 Migração (`_geradores/migrar_markup.py`, novo)

Script idempotente, executado uma vez sobre os 57 corpos; fica no repositório como registro.

1. **Classificação de `data-tipo`** por conteúdo, em ordem: contém `.lab-box` → `laboratorio`; contém `.checklist` → `checklist`; contém `.quiz-item` → `questoes`; contém `.facts-grid` ou é a última seção e tem lista de referências → `referencias`; senão → `teoria`. Um dicionário `EXCECOES = {(slug, id): tipo}` no script registra as correções manuais.
2. **Modo revisão** (`--revisar`): imprime a tabela "slug | id | tipo | título" sem gravar nada. A tabela é conferida antes da gravação, e as correções entram em `EXCECOES`.
3. **Normalização:**
   - G1: `hero-header` removido; `content-section` → `study-section`; `check-item` → `checklist-item` (estrutura de §3.1 regra 6); `callout-tip` → `callout tip`; questões `quiz-btn` recebem `data-formato="multipla"`.
   - G2: `header.study-header` removido; `section-title-wrap`/`section-num` → `h2` simples; corpo envolvido em `article.study-container`.
   - G3: `span.section-tag` e o `div.section-header` que o contém removidos, mantendo o `h2`.
   - Todas: `data-tipo` inserido após o `id`.
4. **Preservação de conteúdo:** antes de gravar, o script compara o texto visível de cada seção (sem os elementos removidos em 3) antes e depois. Qualquer diferença aborta a gravação daquele corpo.
5. Uma segunda execução não produz alterações.

Antes da remoção, os dados únicos que só existam nos cabeçalhos G1/G2 (como os códigos MITRE do `study-header`) são conferidos contra `ESTUDOS_DADOS`. Divergências são relatadas pelo modo revisão e corrigidas em `index_dados.py`, não no corpo.

---

## 4. Portal (`build_index.py` + `index.css`)

Segue o mockup de portal aprovado.

- **Esqueleto:** barra superior (marca, busca com atalho `/`, tema) + menu lateral + conteúdo, sobre `tokens.css`.
- **Menu lateral:** Catálogo (padrão), Rotas sugeridas, Por certificação, Pela necessidade, Rota por vaga, Meu progresso; abaixo, o progresso global (concluídos, em andamento, tempo total). Cada item mostra uma visão; nenhuma visão é empilhada com outra.
- **Catálogo:**
  - Cartão "Continuar estudando" (de `cs_last`): título, % lido, seção onde parou, checklist e questões. Não aparece se `cs_last` não existir.
  - Barra "Agrupar por" Trilha (padrão) / Nível / Perfil / NIST e o filtro "Só não concluídos". Substituem as abas atuais Por Trilha, Por Nível, Por Perfil e Por Função NIST.
  - Cabeçalho de grupo com nome, cor e "X de Y concluídos".
  - Cartão de módulo: número, tempo, título, subtítulo, nível, NIST, nome do simulador, status.
- **Status do módulo:** "✓ Concluído" se `cs_done_<slug>`; "◐ X% lido" se houver `cs_read`, `cs_check` ou `cs_quiz` do módulo, com X = seções lidas ÷ total de seções; "○ Não iniciado" nos demais casos. O total de seções por módulo é contado por `build_index.py` a partir dos corpos e embutido no portal.
- **Visões especiais:** o conteúdo e a lógica atuais de Rotas sugeridas, Por certificação, Necessidades, Rota por vaga e Meu progresso são mantidos e restilizados com os tokens e componentes novos. Em "Meu progresso" continua possível marcar e desmarcar a conclusão.
- O cartão perde o checkbox "Estudo concluído", a pergunta "Responde a" e a lista de tópicos (a pergunta-chave aparece no cabeçalho do módulo).
- Os `data-slug` existentes nos chips e cartões das visões especiais são preservados (testes de `test_filtro_secoes.py`).

---

## 5. Celular, Acessibilidade e Falhas

- **Abaixo de 1024 px:** sumário (módulo) e menu (portal) viram gaveta sobreposta, aberta pelo botão "☰" da barra superior e fechada por Esc, clique fora ou escolha de item. A barra superior, com o selo do tipo e o progresso, continua fixa. O conteúdo vai para uma coluna, sem rolagem horizontal da página de 360 px a 1920 px (tabelas e terminais rolam dentro do próprio contêiner).
- **Acessibilidade:** `nav` com `aria-label`; `aria-current` no sumário; foco visível (`:focus-visible`) em todo controle; checklist, `details` e botões de autoavaliação operáveis por teclado; `prefers-reduced-motion` desliga rolagem suave e transições; gaveta com `aria-expanded` e foco retornando ao botão ao fechar.
- **Sem `localStorage`:** os wrappers `safeStorageGet/Set` engolem a exceção, e tudo funciona na sessão sem persistir.
- **Corpo fora do contrato ou slug sem `ESTUDOS_DADOS`:** a compilação aborta (§3.4).
- **Fonte ausente em `_geradores/fontes/`:** a compilação aborta, informando o arquivo.

---

## 6. Testes

Executar só os arquivos afetados por fase, conforme a regra de memória da máquina (`python3 -m unittest _geradores/testes/test_<x>.py`). A suíte completa roda no fim, com teto de memória.

| Arquivo | Cobre |
|---|---|
| `test_contrato.py` (novo) | Os 57 corpos passam no validador; um corpo inválido por regra de §3.1 produz a mensagem esperada. |
| `test_migracao.py` (novo) | Cada variante G1/G2/G3 → padrão; idempotência; texto visível preservado; `EXCECOES` aplicadas. |
| `test_montar.py` (atualizado) | Cabeçalho a partir de `ESTUDOS_DADOS`; sumário com N itens para N seções; "Seção X de N"; anterior/próximo nas pontas (01 sem anterior, 57 sem próximo); `data-q` sequencial; fontes embutidas e ausência de `fonts.googleapis.com`. |
| `test_assets.py` (atualizado) | Tokens em `tokens.css`; componentes presentes em `base.css`; API pública de §3.3 exportada por `base.js`. |
| `test_responsivo.py` (atualizado) | Media query de 1024 px, gaveta e `prefers-reduced-motion`. |
| `test_index.py` e testes de abas (atualizados) | Menu lateral com as seis visões; "Agrupar por"; total de seções por módulo embutido; ausência das abas substituídas; `data-slug` preservados. |
| `test_fumaca_navegador.py` (novo) | Chrome headless, sequencial, nos 57 módulos e no portal: nenhum erro de JavaScript no console (`--enable-logging=stderr`); no DOM final (`--dump-dom`), sumário com um item por seção e todas as seções com `data-tipo`. O teste é pulado se o Chrome não estiver instalado. |
| Testes por módulo (46 arquivos) | Continuam passando sem alteração (contagem de `class="checklist-item"` e regex de `<section class="study-section" id=…>`). |

**Conferência visual:** capturas antes e depois, nos dois temas, de Redes-e-Protocolos (G2), Fundamentos-Ciber (G1), Threat-Hunting (laboratório pesado), LGPD-e-Privacidade (GRC), Pentest-Metodologias (Red Team) e do portal. Ficam em `.superpowers/` e não são versionadas.

---

## 7. Arquivos e Fases

| Arquivo | Ação |
|---|---|
| `_geradores/tokens.css` | novo |
| `_geradores/fontes/*.woff2`, `_geradores/fontes/OFL.txt` | novos |
| `_geradores/base.css`, `_geradores/base.js` | reescritos |
| `_geradores/contrato.py`, `_geradores/migrar_markup.py` | novos |
| `_geradores/montar.py` | chassi, fontes, validação |
| `_geradores/build_index.py`, `_geradores/index.css` | novo layout do portal |
| `_geradores/*_body.html` (57) | migrados |
| `_geradores/index_dados.py` | só correções vindas da conferência de §3.5 |
| `*/treinamento-*.html` (57), `index.html` | recompilados |
| `_geradores/GUIA-DO-AUTOR.md` | contrato de §3.1 e componentes de §2.3 substituem as seções 2 e 3 atuais |
| `README.md` | descrição do portal e da navegação |
| `.gitignore` | acrescenta `.superpowers/brainstorm/` |

**Fases** (cada uma com commits próprios e verificável isoladamente):

1. **UI kit:** `tokens.css`, fontes embutidas, `base.css` e `base.js` novos.
2. **Chassi:** `contrato.py` e geração de barra, sumário, cabeçalho, seções e fim no `montar.py`.
3. **Migração:** `migrar_markup.py`, revisão da tabela de classificação, migração dos 57 corpos, recompilação e teste de fumaça.
4. **Portal:** `build_index.py` e `index.css`.
5. **Documentação:** `GUIA-DO-AUTOR.md`, `README.md`, `.gitignore` e conferência visual final.
