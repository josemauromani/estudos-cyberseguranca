# Design Spec: Remoção dos Laboratórios e Limpeza Documental

**Data:** 2026-11-06  
**Status:** Aprovada pelo usuário (2026-11-06)  
**Repositório:** `estudos_cyberseguranca` (Mapa da Cibersegurança)  
**Referência Metodológica:** Superpowers Spec-Driven Development (SDD)  
**Origem:** Análise profunda do projeto + decisão do usuário de apagar labs existentes e focar em conteúdo; recriar labs do zero em ciclo futuro.

---

## 1. Propósito e Entendimento

O Mapa hoje exige e entrega um **simulador JS** em cada um dos 62 módulos (`data-tipo="laboratorio"`, ~1,8 MB de JS inline, `laboratorio.css`, campo `simulador_nome`, portal e docs centrados em “laboratório interativo”). O usuário decidiu **apagar o que existe** — não pausar nem arquivar para reuso — e **refazer todos os labs posteriormente**, de outra forma. Neste ciclo o produto passa a ser só conteúdo de qualidade: teoria, checklist, questões e referências.

### Decisões do usuário (brainstorming)

| Decisão | Escolha |
|---|---|
| Escopo do ciclo | **B** — exclusão completa dos labs + limpeza rápida de deriva documental |
| Design System | **A** — apagar também CSS/JS só de lab (sem vestígio) |
| Comunicação do produto | **A** — remover toda menção a laboratório/simulador (sem “em breve”, sem coluna vazia) |
| Abordagem de execução | **1** — cirurgia em lote (estado final coerente), com commits lógicos internos |

### Critérios de sucesso

- Zero seções `data-tipo="laboratorio"`, zero `.lab-box`, zero `simulador_nome`, zero arquivo `laboratorio.css` no código ativo.
- `contrato.validar_corpo` **não** exige laboratório; se o tipo aparecer, **falha** (tipo inválido).
- Portal, README, CURRICULO e GUIA-DO-AUTOR descrevem o produto sem simuladores; README corrige a deriva “60 estudos” → 62.
- Os 62 módulos compilam (`gerar.sh todos` ou equivalente) e a suíte `unittest` passa nos testes do produto (após ajuste/remoção do que só validava lab).
- O módulo de **conteúdo** `Laboratorio-Domestico-e-Portfolio` (homelab/portfólio) permanece; apenas perde a seção/tipo simulador, como os demais.

### Não objetivos

- Recriar laboratórios ou stubs “para ligar depois”.
- Aprofundar conteúdo teórico (SAML, SSDLC, etc.) — ciclo seguinte.
- CI novo, IDs estáveis de quiz, rotas CISO/AppSec, fonte única do catálogo, remissões por slug.
- Reescrever em massa specs/plans históricos em `docs/superpowers/` (salvo se algum teste de documentação piná-los e quebrar).
- Alterar numeração, trilhas ou quantidade de módulos (continua 62).

### Anti-objetivos (falha mesmo “funcionando”)

- Deixar `simulador_nome: ""` ou coluna “Simulador” com “—” / “em breve”.
- Manter `laboratorio` em `TIPOS` “só por compatibilidade” enquanto corpos ainda pudessem compilá-lo em silêncio.
- Apagar ou renomear o estudo **Laboratório Doméstico e Portfólio** por confusão com o tipo de seção.
- Arquivar JS de lab em pasta `_legado/` no repo para reaproveitar depois.

---

## 2. Abordagens Consideradas

| Abordagem | Troca | Decisão |
|---|---|---|
| **1. Cirurgia em lote** | Um ciclo: contrato → corpos → metadados/portal → DS → testes → docs → rebuild. Diff grande; produto coerente no fim. | **Escolhida** |
| 2. Em camadas (PRs sequenciais) | Revisão mais fácil; estados intermediários quebrados ou com vestígios. | Descartada |
| 3. Edição manual módulo a módulo | Controle fino; lento e inconsistente. | Descartada |

Commits lógicos sugeridos na implementação (não necessariamente um PR por commit): contrato; corpos; metadados/portal; Design System; testes; docs + rebuild.

---

## 3. Design

### 3.1 Contrato e forma do corpo

**`_geradores/contrato.py`**
- Remover `laboratorio` de `TIPOS` e `ROTULOS`.
- §5: tipos obrigatórios além da estrutura existente: pelo menos uma seção `checklist`, `questoes` e `referencias` (teoria continua via `data-tipo="teoria"` como hoje).
- Qualquer `data-tipo="laboratorio"` restante → erro de tipo inválido (força limpeza total).

**Corpos (`_geradores/*_body.html`, 62 arquivos)**
- Apagar a `<section class="study-section" … data-tipo="laboratorio">` inteira.
- Apagar `<script>` e `<style>` filhos do `article` usados só pelo simulador.
- Preservar teoria, checklist, questões, referências e qualquer markup pedagógico que não seja o lab.
- Homelab (estudo 37): mesmo tratamento — remove o simulador, mantém o tema do módulo.

### 3.2 Metadados e portal

**`_geradores/index_dados.py`**
- Remover o campo `simulador_nome` de todos os `ESTUDOS_DADOS` (não deixar vazio).

**`_geradores/build_index.py` (e saída `index.html`)**
- Remover tag `🧪 {simulador}` dos cards.
- Remover contadores/copy de “simuladores” / “laboratório interativo” (meta description, lede, labels JS do sumário que citem `laboratorio`).
- Narrativa do portal: teoria, checklist, questões (referências nos módulos).

### 3.3 Design System

- Apagar `_geradores/laboratorio.css`.
- Remover inclusão em `montar.py` (`LABORATORIO_CSS`).
- `base.css` / `tokens.css`: remover tokens e regras de `.lab-box`, `.lab-header`, `.lab-body`, `[data-tipo="laboratorio"]` e correlatos.
- `base.js`: remover tipo/rótulo `laboratorio` e `CS.labProgress` (ou equivalente); manter tema, checklist, quiz e utilitários ainda usados por eles.

### 3.4 Documentação (escopo B)

- **README.md:** tirar pilar de simuladores; remover coluna “Simulador Interativo…” da tabela; corrigir “60 estudos” → 62; ajustar descrição do pipeline/CURRICULO sem “especificações de cada simulador”.
- **CURRICULO.md:** remover blocos “Simulador Interativo em JS” por módulo e menções equivalentes.
- **GUIA-DO-AUTOR.md:** contrato sem lab; remover § de `.lab-box`, diretrizes técnicas de simuladores e itens de checklist do autor sobre lab.
- Specs/plans antigos: não reescrever em massa.

### 3.5 Testes

- Atualizar `test_contrato.py` ao novo contrato.
- Em testes de módulo: remover asserts de lab, espelhos Python do motor JS e fixtures só de simulador; manter asserts de conteúdo.
- Ajustar `test_componentes_css`, `test_tokens`, `test_base_js`, `test_portal*`, `test_piloto`, `test_index`, etc.
- Arquivos cujo propósito era só o lab: apagar ou reduzir ao mínimo de conteúdo do módulo.
- Falhas de Mermaid/`chrome-headless-shell` por ambiente: fora do escopo deste ciclo se não forem regressão introduzida pela remoção.

### 3.6 Verificação final

- `./_geradores/gerar.sh todos` (ou fluxo equivalente) regenera 62 treinamentos + portal.
- `python3 -m unittest discover -s _geradores/testes` verde no que for produto.
- Grep residual no código ativo: zero `data-tipo="laboratorio"`, `.lab-box`, `simulador_nome`, `laboratorio.css`, e copy de produto prometendo simulador (README/GUIA/CURRICULO/portal gerado).

### 3.7 Erros e edge cases

- Corpo com lab residual → falha no `montar.py` via contrato (não gerar HTML “meio lab”).
- Referências textuais internas do tipo “veja o laboratório deste módulo” nos corpos: remover ou reescrever para apontar a checklist/teoria no mesmo ciclo, para não mentir ao estudante.
- Não confundir a palavra “laboratório” no sentido de **homelab / lab doméstico** (conteúdo do módulo 37) com o tipo de seção removido — o título e o tema do módulo 37 permanecem.

---

## 4. Ordem de implementação sugerida

1. Contrato + testes do contrato (vermelho→verde).
2. Limpeza dos 62 corpos (edição em lote ou script **descartável** — não versionar ferramenta de migração no repo).
3. Metadados + portal.
4. Design System (`laboratorio.css`, CSS/JS).
5. Demais testes.
6. README / CURRICULO / GUIA.
7. Rebuild + grep residual + suíte.

---

## 5. Ciclos seguintes (fora desta spec)

- Aprofundamento de conteúdo (gaps P0 da análise: SAML, secrets, SSDLC, etc.).
- Hardening arquitetural (check de deriva, CI, IDs de quiz, …).
- **Nova feature de laboratórios**, desenhada do zero — sem restaurar o código apagado aqui.
