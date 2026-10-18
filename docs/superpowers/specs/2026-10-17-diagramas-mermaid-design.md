# Design Spec: Padronização e Pré-compilação de Diagramas com Mermaid

**Data:** 2026-10-17  
**Status:** Em Revisão (Aguardando Aprovação do Usuário)  
**Autor:** Antigravity & Equipe  
**Repositório:** `estudos_cyberseguranca`  
**Referência Metodológica:** Superpowers Spec-Driven Development (SDD)

---

## 1. Visão Geral e Motivação

O projeto **Estudos de Cibersegurança** consolida 33 módulos de aprendizagem técnica, priorizando conteúdo pragmático, rigor normativo (NIST CSF 2.0 e MITRE ATT&CK) e uma arquitetura estritamente **100% offline e standalone**.

Atualmente, alguns módulos utilizam esquemas visuais em **ASCII art** (por exemplo, o fluxo de decisão NIST SP 800-207 em `Arquitetura-Zero-Trust`, a estrutura da tag IEEE 802.1Q em `Segmentacao-e-Firewall` e o vetor CVSS v3.1 em `Gestao-de-Vulnerabilidades`), enquanto a documentação Markdown (`README.md`, `CURRICULO.md`, `GUIA-DO-AUTOR.md`) carece de diagramas conceituais padronizados para representar a arquitetura do compilador e as trilhas de formação.

Embora o formato ASCII seja simples, ele apresenta limitações:
- Dificuldade de manutenção e edição rápida.
- Falta de escalabilidade visual em dispositivos móveis.
- Ausência de semântica vetorial e estilização integrada ao Design System.

Esta especificação define a transição completa desses diagramas para a sintaxe canônica **Mermaid**, estabelecendo um pipeline de compilação em `_geradores/montar.py` que pré-renderiza o código Mermaid em vetores **SVG inline transparentes**, com cache local determinístico (`_geradores/cache_diagramas/`), garantindo que o produto final entregue aos alunos continue sendo um arquivo HTML único, levíssimo e sem dependências em tempo de execução.

---

## 2. Objetivos e Não-Objetivos

### Objetivos
1. **Padronização Visual:** Declarar diagramas de arquitetura, fluxos lógicos e estruturas de dados em sintaxe **Mermaid** canônica.
2. **Pré-compilação em Tempo de Build:** Converter blocos `<pre class="mermaid">` presentes nos fragmentos `_body.html` em elementos `<svg>` puros embutidos no HTML final durante a execução de `montar.py`.
3. **Preservação do Pilar 100% Offline:** Não incluir bibliotecas JS de terceiros (como `mermaid.min.js`) em tempo de execução no navegador do aluno, mantendo o carregamento instantâneo via `file://`.
4. **Cache Determinístico de SVGs:** Armazenar os SVGs gerados em `_geradores/cache_diagramas/<hash>.svg` indexados por hash SHA-256 do código Mermaid, tornando compilações subsequentes instantâneas (< 1s) e permitindo o build mesmo sem Node.js instalado na máquina local.
5. **Diagramas na Documentação:** Enriquecer `README.md`, `CURRICULO.md` e `GUIA-DO-AUTOR.md` com diagramas Mermaid nativos renderizados pelo GitHub/GitLab.
6. **Harmonia com Design System e Responsividade:** Integrar a renderização dos diagramas às variáveis de tema escuro e claro (`--ground`, `--surface`, `--accent`) e garantir compatibilidade estrita contra rolagem horizontal indesejada no celular.

### Não-Objetivos
- Não carregar o runtime do Mermaid via CDN em tempo de execução no navegador (para evitar falhas quando o usuário estiver sem conexão à internet).
- Não embutir o bundle completo `mermaid.min.js` (~2.8MB) dentro de cada arquivo HTML compilado.
- Não alterar a lógica dos simuladores interativos em JavaScript Vanilla existentes nos módulos.

---

## 3. Arquitetura do Pipeline de Compilação

### 3.1. Declaração nos Fragmentos de Conteúdo (`_geradores/*_body.html`)

O autor de conteúdo escreve diagramas em blocos semânticos e identificados:

```html
<div class="diagram-box">
  <div class="diagram-header">
    <span class="diagram-title">Fluxo Lógico de Decisão NIST SP 800-207</span>
    <span class="diagram-badge">Mermaid Arquitetura</span>
  </div>
  <pre class="mermaid" data-title="Fluxo Lógico de Decisão NIST SP 800-207">
flowchart TD
    subgraph PDP["PLANO DE CONTROLE (PDP)"]
        PE["Policy Engine (PE)<br><small>Avaliação e Cálculo de Risco</small>"]
        PA["Policy Administrator (PA)<br><small>Comando de Abertura/Revogação</small>"]
        PE <--> PA
    end
    subgraph DP["PLANO DE DADOS (DATA PLANE)"]
        Subject["Subject<br><small>Usuário / Dispositivo</small>"]
        PEP["PEP Gateway<br><small>Ponto de Execução de Políticas</small>"]
        Recurso["Recurso Protegido<br><small>Workload / Banco / App</small>"]
        Subject ==>|"1. Requisição de Acesso"| PEP
        PEP ==>|"3. Acesso Autorizado"| Recurso
    end
    Subject -.->|"Telemetria & Contexto"| PE
    PA -->|"2. Comando de Acesso"| PEP
  </pre>
</div>
```

### 3.2. Módulo de Renderização e Cache (`_geradores/diagramas.py`)

Um módulo dedicado `_geradores/diagramas.py` fornecerá a lógica de processamento que será invocada por `montar.py`:

```
_geradores/
  ├── diagramas.py             # Parser de blocos, hashing, invocação do mmdc e cache
  ├── cache_diagramas/         # Diretório com SVGs pré-compilados versionados
  │     ├── 4f8b91c2e0a1.svg
  │     └── ...
  ├── puppeteer-config.json    # Configuração de segurança Chromium ({ "args": ["--no-sandbox", ...] })
  └── montar.py                # Pipeline principal integrado
```

#### Fluxo de Execução:
1. **Parsing:** Regex varre o conteúdo HTML procurando por `<pre class="mermaid"[^>]*>(.*?)</pre>`.
2. **Hash e Assinatura:** Extrai o código Mermaid e calcula o hash SHA-256 normalizado (removendo espaços vazios iniciais e finais):
   ```python
   hash_id = hashlib.sha256(codigo_mermaid.strip().encode("utf-8")).hexdigest()[:12]
   svg_cache_file = CACHE_DIR / f"{hash_id}.svg"
   ```
3. **Reaproveitamento de Cache:** Se `svg_cache_file.exists()` for verdadeiro e a flag `--recompilar-diagramas` não estiver ativa, lê o SVG diretamente do disco sem invocar subprocesso.
4. **Geração via Mermaid CLI:**
   - Se o SVG não existir em cache:
     - Grava o código Mermaid em arquivo temporário `.mmd`.
     - Executa o utilitário `npx --yes @mermaid-js/mermaid-cli`:
       ```bash
       npx --yes @mermaid-js/mermaid-cli \
         -p _geradores/puppeteer-config.json \
         -i <temp_in>.mmd \
         -o <temp_out>.svg \
         -b transparent \
         -t dark
       ```
     - Valida o código de saída (0) e armazena em `_geradores/cache_diagramas/<hash_id>.svg`.
5. **Fallback Seguro:** Caso o utilitário `npx`/Node.js não esteja disponível e o cache não possua o SVG, o compilador mantém o bloco original `<pre class="mermaid">` e registra aviso no console, garantindo que o build nunca falhe catastroficamente.
6. **Substituição Vetorial:** Substitui o bloco `<pre class="mermaid">` no HTML compilado por:
   ```html
   <div class="diagram-svg-wrap" role="img" aria-label="Diagrama de Arquitetura">
     <!-- <svg ...> inlined diretamente -->
   </div>
   ```

---

## 4. Mapeamento e Modelagem dos Diagramas

### 4.1. Módulos de Treinamento HTML

| Módulo | Arquivo Fonte | Conteúdo Atual | Nova Modelagem Mermaid |
|---|---|---|---|
| **08. Arquitetura Zero Trust** | `_geradores/arquitetura_zero_trust_body.html` | Bloco ASCII `nist-zta-diagram` (linhas 127–142) | `flowchart TD` detalhando Plano de Controle (PE, PA) e Plano de Dados (Subject, PEP, Recurso) com conexões bidirecionais e fluxo numerado. |
| **05. Segmentação e Firewall** | `_geradores/segmentacao_e_firewall_body.html` | Bloco ASCII `vlan-tag-struct` (linhas 131–139) | `flowchart TD` estruturando o Quadro Ethernet com expansão da Tag IEEE 802.1Q (TPID `0x8100`, TCI: PCP, DEI, VID de 12 bits). |
| **09. Gestão de Vulnerabilidades** | `_geradores/gestao_de_vulnerabilidades_body.html` | Bloco ASCII `cvss-vector-example` (linhas 141–150) | `flowchart LR` mapeando métricas de *Explorabilidade* (AV, AC, PR, UI), *Escopo* (S) e *Impacto* (C, I, A) com scores qualitativos. |
| **07. Segurança de Redes & Defesa** | `_geradores/seguranca_de_redes_defesa_body.html` | Descrição textual de IDS vs IPS e Proxies | `flowchart LR` comparando topologia passiva (TAP/SPAN) de IDS com topologia em linha (Drop) de IPS e inspeção reversa mTLS. |

### 4.2. Documentação Markdown

| Arquivo | Seção / Propósito | Diagrama Mermaid |
|---|---|---|
| **`README.md`** | Visão do Pipeline Técnico | `flowchart LR` ilustrando o fluxo: `_body.html` + `estudos.txt` + `base.css/js` -> `montar.py` (com pré-renderização Mermaid) -> `treinamento-*.html` standalone. |
| **`README.md`** | Grade e Trilhas | `flowchart TD` agrupando as 7 trilhas e demonstrando o percurso formativo desde Fundamentos até a Rota por Vaga de Analista de Segurança. |
| **`_geradores/CURRICULO.md`** | Matriz Curricular | `flowchart LR` correlacionando as 7 Trilhas Temáticas aos 6 domínios do **NIST CSF 2.0** (*Govern, Identify, Protect, Detect, Respond, Recover*). |
| **`_geradores/GUIA-DO-AUTOR.md`** | Diretrizes de Diagramação | Atualização do guia com padrões de sintaxe `<pre class="mermaid">`, boas práticas de rotulagem e documentação do cache de compilação. |

---

## 5. Design System, Estilização e Acessibilidade (`base.css`)

Para integrar os diagramas com harmonia visual aos temas escuro e claro da plataforma, as seguintes regras CSS serão adicionadas em `_geradores/base.css`:

```css
/* ==========================================================================
   DIAGRAMAS MERMAID PRÉ-COMPILADOS EM SVG
   ========================================================================== */
.diagram-box {
  background: var(--surface);
  border: 1px solid var(--rule);
  border-radius: var(--radius);
  margin: 1.5rem 0;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.diagram-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.65rem 1rem;
  background: var(--ground);
  border-bottom: 1px solid var(--rule);
  font-size: 0.825rem;
  font-weight: 600;
  color: var(--muted);
}

.diagram-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  background: rgba(37, 99, 235, 0.15);
  color: var(--accent);
  border: 1px solid rgba(37, 99, 235, 0.3);
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
  font-size: 0.725rem;
  font-family: var(--font-mono);
}

.diagram-svg-wrap {
  padding: 1.5rem;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  text-align: center;
  background: var(--surface);
}

.diagram-svg-wrap svg {
  max-width: 100%;
  height: auto;
  display: inline-block;
  margin: 0 auto;
}
```

---

## 6. Plano de Verificação e Testes

A implementação será acompanhada por testes automatizados e validações de integridade:

1. **Testes Unitários de Diagramas (`_geradores/testes/test_diagramas.py`):**
   - Extração correta de blocos `<pre class="mermaid">`.
   - Determinismo do hash SHA-256 e consistência de nomenclatura dos arquivos de cache.
   - Geração e salvamento do SVG em cache.
   - Reutilização de SVG em cache sem acionar o comando de CLI.
   - Comportamento resiliente e fallback sem interrupção de build caso o CLI falhe.
2. **Testes de Integração do Compilador (`_geradores/testes/test_montar.py`):**
   - Verificação de que `montar_treinamento` substitui corretamente o bloco Mermaid pelo SVG embutido.
   - Inspeção de atributos do SVG (`role="img"`, `max-width`, etc.).
3. **Suíte Completa e Responsividade:**
   - Execução de `python3 -m unittest discover -s _geradores/testes` (garantindo que os 120 testes existentes e os novos passem com 100% de sucesso).
   - Validação com `test_responsivo.py` para garantir ausência total de transbordamento horizontal em viewports móveis (360px a 480px).
4. **Verificação nos Navegadores:**
   - Abertura dos arquivos compilados via navegador para inspeção visual da nitidez dos diagramas nos modos escuro e claro.

---

## 7. Rastreabilidade e Transição

Após a aprovação desta especificação:
- A especificação será formalmente comitada no Git.
- Será acionada a habilidade `writing-plans` para decompor a execução em tarefas modulares guiadas por TDD (Red-Green-Refactor) e executadas através do fluxo SDD.
