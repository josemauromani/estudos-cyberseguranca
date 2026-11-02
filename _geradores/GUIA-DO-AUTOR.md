# Guia do Autor: Diretrizes Pedagógicas e Padrões de Conteúdo

Este documento estabelece as diretrizes de redação técnica, arquitetura de informação e padrões de código HTML/JS para a elaboração dos 57 módulos da plataforma **Estudos de Cibersegurança**.

---

## 1. Princípios Editoriais e Tom de Voz

1. **Linguagem Oficial:** Todo o conteúdo é redigido em **Português do Brasil (pt-BR)**.
   - Termos técnicos amplamente consagrados na indústria internacional podem ser mantidos no original em inglês, sempre acompanhados de explicação contextual no primeiro uso (ex.: *Least Privilege*, *Zero Trust Network Access (ZTNA)*, *Prompt Injection*, *Handshake*).
   - Siglas normativas (NIST, MITRE ATT&CK, ISO/IEC, RFC, OWASP, LGPD) devem ser explicitadas em sua primeira menção.
2. **Tom de Voz:**
   - **Pragmático e Operacional:** Escreva como um especialista sênior orientando um par ou liderado. Vá direto ao ponto.
   - **Didático e Rigoroso:** Cada afirmação técnica deve ser fundamentada em normas (NIST SP, ISO, RFCs) ou evidências empíricas de mercado.
   - **Livre de Floreios:** Evite introduções longas ou jargões vazios ("No mundo globalizado de hoje..."). Comece o módulo apresentando imediatamente o problema de segurança real e o que o estudante aprenderá a resolver.
3. **Público-Alvo:** Estudantes de tecnologia, analistas e engenheiros de segurança (Blue/Red/AppSec/GRC), operadores de SOC e candidatos a concursos públicos de alto nível e certificações profissionais (CompTIA Security+, CySA+, CEH, Pentest+, CISSP).

---

## 2. Estrutura de um Treinamento: o Contrato do Corpo

Cada módulo é redigido em um arquivo fragmento `_geradores/<slug_snake_case>_body.html` (o **corpo**) e compilado pelo `montar.py` para gerar `<Pasta>/treinamento-<slug_kebab_case>.html`.

### 2.1 O que o autor escreve e o que o gerador cria

| O autor escreve (no `_body.html`) | O gerador cria (não escreva) |
|---|---|
| `<article class="study-container">` com as seções de conteúdo | Cabeçalho do estudo (trilha, título, subtítulo, tempo, nível, NIST, MITRE, carreiras) |
| Cada `<section class="study-section">` com seu `<h2>` | Rodapé, navegação lateral/sumário e botão "Concluir módulo" |
| Componentes do conteúdo (callouts, tabelas, terminais, diagramas, laboratório, checklist, questões) | Rótulo e numeração das seções ("Seção 0X", ícone e tipo) |

**Metadados do módulo** (título, subtítulo, tempo, nível, NIST, MITRE, carreiras) ficam em `ESTUDOS_DADOS`, em `_geradores/index_dados.py`, e são renderizados por `_geradores/chassi.py`. Nunca os escreva no corpo. Ao adicionar, remover ou reordenar módulos, rode `./_geradores/gerar.sh todos` (cada página traz "Estudo NN de <total>" e anterior/próximo). Não escreva cabeçalho, rodapé, "Seção 0X" nem marcações de etiqueta de seção: o validador rejeita esses elementos.

### 2.2 As regras do corpo

1. Há exatamente um `<article class="study-container" data-slug="...">`, na raiz do arquivo.
2. Os filhos diretos do `article` são `<section class="study-section" id="..." data-tipo="...">`, com os atributos nessa ordem (`class`, `id`, `data-tipo`). Os `<script>` e `<style>` do simulador também podem ser filhos diretos do `article`.
3. Cada seção começa com um `<h2>`, e o `id` é único.
4. Não há `<footer>` nem classes de cabeçalho ou etiqueta de seção (o chassi as gera).
5. Existe ao menos uma seção de cada tipo: `laboratorio`, `checklist`, `questoes` e `referencias`.
6. O checklist usa `ul.checklist > li.checklist-item`, cada item com `input[type=checkbox][id]` e `label[for]` correspondente.
7. Cada `.quiz-item` tem `.quiz-question` e a resposta no formato aberto (3.5), ou o formato de múltipla escolha.
8. Todo `div.callout` tem um modificador: `tip`, `warning`, `danger`, `law` ou `key`.

### 2.3 Tipos de seção e rótulos

O `data-tipo` define o ícone e o rótulo que o chassi mostra na navegação. O módulo costuma ter várias seções de teoria; os demais tipos aparecem ao menos uma vez.

| `data-tipo` | Rótulo gerado | Conteúdo |
|---|---|---|
| `data-tipo="teoria"` | 📘 Teoria | Fundamentação, arquitetura, tabelas, diagramas, terminais e callouts |
| `data-tipo="laboratorio"` | 🧪 Laboratório | Simulador interativo em JavaScript puro (`.lab-box`) |
| `data-tipo="checklist"` | ☑️ Checklist | Lista de 4 a 8 itens práticos de verificação ou auditoria |
| `data-tipo="questoes"` | ❓ Questões de concurso | Questões de fixação com resposta comentada |
| `data-tipo="referencias"` | 📚 Referências | Padrões oficiais (RFCs, NIST SPs, CIS Benchmarks, OWASP, fabricantes) e leituras |

Esqueleto mínimo (copiado do padrão de `_geradores/threat_hunting_body.html`):

```html
<article class="study-container" data-slug="threat-hunting">

    <section class="study-section" id="introducao" data-tipo="teoria">
        <h2>Introdução: Nenhum Alerta Não Quer Dizer Nenhum Invasor</h2>
        <p class="lead-text">Parágrafo de abertura: o problema real e o que o estudante vai resolver.</p>
        ...
    </section>

    <section class="study-section" id="simulador" data-tipo="laboratorio">
        <h2>Laboratório Prático: Caçada Guiada</h2>
        ...
    </section>

    <section class="study-section" id="checklist" data-tipo="checklist">
        <h2>Checklist de uma Caçada</h2>
        ...
    </section>

    <section class="study-section" id="quiz" data-tipo="questoes">
        <h2>Questões de Fixação e Entrevista</h2>
        ...
    </section>

    <section class="study-section" id="fatos" data-tipo="referencias">
        <h2>Fatos Essenciais, Referências e Próximos Passos</h2>
        ...
    </section>

    <script>/* JavaScript do simulador, filho direto do article */</script>
</article>
```

### 2.4 Validação

O `montar.py` valida o corpo antes de compilar (`contrato.validar_corpo(html, slug)`). Se alguma regra falhar, a compilação **aborta com código de saída 1** e imprime mensagens no formato `"<slug> §<n>: <onde>: <descrição>"`, em que `<n>` é o número da regra da seção 2.2:

```bash
python3 _geradores/montar.py _geradores/threat_hunting_body.html
```

Corrija o corpo e compile de novo; não há opção para ignorar o validador.

### 2.5 Orientações editoriais por tipo de seção

- **Teoria:** explique princípios, protocolos e metodologias com clareza. Use tabelas comparativas, diagramas, callouts para boas práticas e armadilhas, e `.terminal-box` para comandos e configurações reais. Abra com o problema de segurança real.
- **Laboratório:** cada módulo **deve conter um simulador interativo em JavaScript puro (Vanilla JS)**. Ele deve permitir manipulação ativa (alterar parâmetros, acionar filtros, inspecionar pacotes, validar hashes) e operar 100% offline.
- **Checklist:** 4 a 8 itens que o estudante possa reutilizar como modelo de trabalho em auditorias reais. O estado das caixas é gravado no `localStorage` pelo `base.js`.
- **Questões:** no mínimo 3 a 4 questões com foco analítico (estilo certificação ou concurso). Toda resposta traz explicação pedagógica que justifica o porquê de estar correta ou incorreta.
- **Referências:** lista concisa de fontes oficiais.

---

## 3. Componentes HTML e Padrões CSS do Design System

### 3.0 Estilo: tokens, fontes e arquivos CSS

- `tokens.css`: variáveis de design. Os nomes antigos foram preservados; os novos incluem a escala tipográfica `--tipo-*` e as cores de console `--console*`. Use sempre as variáveis, nunca cores fixas.
- `base.css`: os componentes descritos abaixo.
- `laboratorio.css`: regras específicas dos simuladores.
- `index.css`: o portal.
- Fontes: ficam embutidas no HTML a partir de `_geradores/fontes/` (licença OFL, texto em `OFL.txt`). Não há CDN nem requisição externa.

Os temas claro e escuro são automáticos; teste o simulador nos dois.

### 3.1 Texto de abertura (`p.lead-text`)

Opcional. Um parágrafo de abertura logo após o `<h2>` da seção:

```html
<p class="lead-text">
    Conduza a caçada do relatório na frota fictícia da Ipê Store. Escolha a hipótese, a fonte de dados e aponte o achado.
</p>
```

### 3.2 Caixas de Destaque (`div.callout`)

A classe `callout` recebe **um** modificador (`tip`, `warning`, `danger`, `law` ou `key`) e traz um `.callout-title`:

```html
<div class="callout tip">
    <div class="callout-title">
        <span class="callout-icon">🔦</span>
        <strong>Pergunta-chave do módulo</strong>
    </div>
    <p>
        Se um invasor estiver na rede sem disparar alertas, por onde você começa a procurar?
    </p>
</div>
```

| Modificador | Uso |
|---|---|
| `tip` | Dica operacional ou recomendação |
| `warning` | Aviso importante de segurança |
| `danger` | Perigo ou vulnerabilidade crítica |
| `law` | Requisito regulatório ou jurídico (LGPD, ISO) |
| `key` | Ideia central a memorizar |

### 3.3 Terminal de Comandos (`.terminal-box`)

```html
<div class="terminal-box">
    <div class="terminal-header">
        <span class="terminal-title">PowerShell — inventário de tarefas da frota</span>
        <button class="terminal-copy-btn" onclick="copyCode(this, 'code-th-stack')">Copiar</button>
    </div>
    <pre><code id="code-th-stack">$estacoes = Get-Content .\estacoes.txt</code></pre>
</div>
```

O segundo argumento de `copyCode` é o `id` do `<code>` a copiar.

### 3.4 Painel do Simulador (`.lab-box`) e checklist

O simulador mora na seção `data-tipo="laboratorio"`:

```html
<div class="lab-box" id="th-lab">
    <div class="lab-header">
        <div>
            <span class="lab-badge">Caça por hipótese</span>
            <h3>Caçada Guiada na frota da Ipê Store</h3>
        </div>
    </div>
    <div class="lab-body">
        <!-- controles e saída do simulador -->
    </div>
</div>
```

Opcional: o simulador pode informar o progresso ao sumário lateral com `CS.labProgress(feitos, total)` (por exemplo `CS.labProgress(3, 5)` mostra "3/5" ao lado do laboratório). Valores inválidos limpam o contador.

O checklist é uma lista não ordenada; cada item tem checkbox com `id` e `label` ligado por `for`. Não é preciso chamar `initChecklist` nem informar `data-checklist-slug` (opcional e ignorado nas páginas geradas): o `base.js` usa o slug do módulo (`ESTUDOS_DADOS`) como chave `cs_check_<slug>_<id>`.

```html
<ul class="checklist">
    <li class="checklist-item">
        <input type="checkbox" id="chk-th-1">
        <label for="chk-th-1"><strong>Hipótese:</strong> escrita antes da busca, testável e com técnica mapeada.</label>
    </li>
    <li class="checklist-item">
        <input type="checkbox" id="chk-th-2">
        <label for="chk-th-2"><strong>Visibilidade:</strong> a fonte escolhida enxerga o comportamento em toda a população.</label>
    </li>
</ul>
```

### 3.5 Questões com resposta revelável (`.quiz-item`)

Formato padrão (resposta aberta): `div.quiz-item > .quiz-question + details.quiz-details > summary.quiz-toggle + .quiz-answer`.

```html
<div class="quiz-item">
    <div class="quiz-question">
        <strong>Questão 1 (Indicador):</strong> O relatório traz o hash do implante. A varredura no EDR deu zero resultados. Dá para encerrar dizendo que a empresa não foi atingida?
    </div>
    <details class="quiz-details">
        <summary class="quiz-toggle">Ver resposta explicada</summary>
        <div class="quiz-answer">
            <p><strong>Resposta:</strong> Não. O hash fica na base da Pirâmide da Dor: o grupo recompila o implante para cada vítima.</p>
        </div>
    </details>
</div>
```

Variante de múltipla escolha: `div.quiz-item` com `data-formato="multipla"`, em que as alternativas são botões de opção de classe própria do `base.css`, como validado em `_geradores/contrato.py` (regra 7). Prefira o formato aberto acima, que é o usado pelos módulos migrados; consulte `contrato.py` antes de usar a variante.

### 3.6 Tabelas e fatos

Tabelas largas ficam em `div.table-responsive > table.data-table`, para rolar dentro do componente em telas estreitas. Resumos de fim de módulo usam `div.facts-grid > div.facts-card`.

### 3.7 Responsividade

O layout deve funcionar de 360 px a 1920 px **sem rolagem horizontal da página**. Conteúdo largo (tabelas, terminais, diagramas) rola dentro do próprio componente.

### 3.8 Diagramas Arquiteturais e Lógicos (`.diagram-box` e `<pre class="mermaid">`)

Para esquemas arquiteturais, fluxos de decisão e dissecção de protocolos, utilize a sintaxe canônica **Mermaid** encapsulada no container `.diagram-box`:

```html
<div class="diagram-box">
  <div class="diagram-header">
    <span class="diagram-title">Estrutura do Quadro Ethernet e Tag IEEE 802.1Q</span>
    <span class="diagram-badge">Mermaid</span>
  </div>
  <pre class="mermaid" data-title="Estrutura do Quadro Ethernet e Tag IEEE 802.1Q">
flowchart TD
    subgraph Quadro["Quadro Ethernet 802.3"]
        DMAC["MAC Destino<br><small>6 bytes</small>"]
        SMAC["MAC Origem<br><small>6 bytes</small>"]
        TAG["Tag 802.1Q<br><small>4 bytes (Opcional)</small>"]
        TP["EtherType<br><small>2 bytes</small>"]
        PAY["Payload de Dados<br><small>46 a 1500 bytes</small>"]
        FCS["FCS / CRC<br><small>4 bytes</small>"]
    end
    DMAC --> SMAC --> TAG --> TP --> PAY --> FCS
  </pre>
</div>
```

#### Boas Práticas de Diagramação:
1. **Orientação:** Prefira `flowchart TD` (vertical de cima para baixo) para hierarquias conceituais, árvores de decisão ou planos de controle e dados. Utilize `flowchart LR` (horizontal da esquerda para a direita) para pipelines e trajetórias lineares de pacotes.
2. **Nós Explicativos e Quebras de Linha:** Utilize `<br>` e `<small>` para adicionar legendas técnicas e tamanhos de campos sem alargar os nós desnecessariamente (ex.: `id["Policy Engine (PE)<br><small>Avaliação e Cálculo de Risco</small>"]`).
3. **Escapamento e Aspas Duplas:** Sempre envolva o texto dos nós entre aspas duplas: `node["Texto com (Parênteses)"]` para evitar erros de sintaxe no parser Mermaid.
4. **Agrupamento por Subgrafos:** Use `subgraph Nome["Título Visível"]` para isolar zonas de segurança (ex.: DMZ vs LAN), planos arquiteturais (Controle vs Dados) ou camadas da pilha OSI/TCP-IP.
5. **Responsividade Móvel:** Evite cadeias horizontais longas sem quebras; prefira fluxos em colunas ou em cascata que caibam confortavelmente em telas de 360px a 480px.

#### Pré-compilação Automática e Cache de SVGs:
- **Zero Runtime Externo:** A plataforma preserva o compromisso de **100% offline**. Nenhum arquivo JavaScript do Mermaid (`mermaid.min.js`) ou requisição CDN é executada no navegador do aluno.
- **Pipeline no `montar.py`:** Durante a compilação, o compilador detecta blocos `<pre class="mermaid">`, calcula o hash SHA-256 do código e busca o vetor SVG pré-renderizado em `_geradores/cache_diagramas/<hash>.svg`.
- **Injeção SVG Direta:** O bloco `<pre>` é substituído por `<div class="diagram-svg-wrap" role="img" aria-label="..."><svg>...</svg></div>`, com renderização vetorial cristalina em qualquer densidade de pixels.
- **Geração Automática via CLI:** Se um diagrama novo for criado ou um existente for editado, o compilador invoca `npx @mermaid-js/mermaid-cli` em Chromium headless com fundo transparente e tema escuro, persistindo o novo SVG no cache. Compilações subsequentes utilizam o cache instantaneamente sem necessidade de invocar o Node.js.

---

## 4. Diretrizes Técnicas para Simuladores em JavaScript

1. **Vanilla JavaScript Apenas:** Proibido o uso de frameworks externos (React, Vue, jQuery) ou bibliotecas de terceiros via CDN. Todo código deve ser executável nativamente em navegadores modernos.
2. **Web APIs Nativas Recomendadas:**
   - Criptografia: `window.crypto.subtle` (SHA-256, AES-GCM, HMAC).
   - Armazenamento: `window.localStorage` (com chaves prefixadas por `cs_`).
   - Manipulação de Texto e Bytes: `TextEncoder`, `TextDecoder`, `Uint8Array`.
3. **Prevenção de XSS nos Simuladores:**
   - Ao renderizar dados digitados pelo usuário, utilize sempre `element.textContent = valor` ou escape devidamente strings antes de concatená-las.
   - Em simuladores didáticos de injeção (ex.: lab de XSS), use elementos `iframe` com atributo `sandbox` ou sanitizadores visuais para evitar efeitos colaterais na própria página.
4. **Isolamento de Estado:**
   - Encapsule funções do simulador em escopos dedicados para evitar conflito de nomes de variáveis globais.
5. **Acessibilidade e Responsividade:**
   - Todos os inputs de formulário devem conter `<label>` associado ou atributo `aria-label`.
   - Layouts devem se adaptar sem quebras em larguras de tela de 360px a 1920px.

---

## 5. Convenções de Arquivos e Identificadores

1. **Nomes dos Slugs:** Utilizar formato Kebab-Case com iniciais maiúsculas nas palavras para o nome de pasta e slug canônico (ex.: `Fundamentos-Ciber`, `Redes-e-Protocolos`, `OWASP-Top-10-Web`).
2. **Nomes dos Arquivos de Entrada:** Salvos em `_geradores/` no formato `<slug_em_snake_case>_body.html` (ex.: `_geradores/fundamentos_ciber_body.html`).
3. **Nomes dos Arquivos de Saída:** Salvos na pasta do estudo no formato `<Pasta>/treinamento-<slug_em_kebab_case_minusculo>.html` (ex.: `Fundamentos-Ciber/treinamento-fundamentos-ciber.html`).
4. **Chaves de `localStorage`** (todas com prefixo `cs_`):
   - Tema global: `cs_theme` (`light` | `dark`).
   - Estudo concluído: `cs_done_<slug>`.
   - Itens de checklist: `cs_check_<slug>_<inputId>`, em que `inputId` é o `id` do checkbox.
   - Seções lidas: `cs_read_<slug>`.
   - Respostas das questões: `cs_quiz_<slug>_<qid>`.
   - Último estudo aberto (usado em "Continuar estudando" no portal): `cs_last`.

---

## 6. Checklist de Qualidade Antes de Submeter um Novo Estudo

Antes de publicar ou compilar um novo estudo, confirme se todos os critérios abaixo foram atendidos:

- [ ] O slug e título constam exatamente como registrados em `_geradores/estudos.txt` e os metadados em `ESTUDOS_DADOS` (`_geradores/index_dados.py`). Ao adicionar, remover ou reordenar módulos, rode `./_geradores/gerar.sh todos`: cada página traz "Estudo NN de <total>" e os links anterior/próximo.
- [ ] O arquivo `_geradores/<slug>_body.html` foi criado e passa no `contrato.validar_corpo` (o `montar.py` não aborta), com ao menos uma seção de cada tipo obrigatório.
- [ ] O corpo não traz cabeçalho, rodapé, "Seção 0X" nem etiquetas de seção escritas à mão.
- [ ] O simulador prático em JS funciona sem disparar erros no console do navegador (`F12`).
- [ ] Os checklists gravam o estado no `localStorage` e o restauram ao recarregar a página.
- [ ] Todas as questões possuem resposta comentada com justificativa pedagógica.
- [ ] Todo `div.callout` tem modificador (`tip`, `warning`, `danger`, `law` ou `key`).
- [ ] Diagramas arquiteturais utilizam `<pre class="mermaid">` e compilam para SVG sem quebra visual.
- [ ] A página não tem rolagem horizontal a 400 px de largura, nos temas claro e escuro.
- [ ] A compilação via `./_geradores/gerar.sh <slug>` executa com sucesso (`exit code 0`).
- [ ] O arquivo gerado funciona 100% offline via protocolo `file:///`.
