# Redesenho de UI/UX — Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Novo UI kit (tokens, fontes embutidas, componentes), página de módulo com sumário lateral e seções tipadas, migração dos 57 corpos para um contrato de markup e portal com navegação lateral.

**Architecture:** O `montar.py` passa a gerar o chassi da página (barra superior, sumário, cabeçalho, cabeçalhos de seção, fim) a partir de `ESTUDOS_DADOS` e do `data-tipo` de cada seção. Um validador (`contrato.py`) barra corpos fora do padrão, e um script idempotente (`migrar_markup.py`) leva os 57 corpos ao padrão sem alterar o texto. O portal (`build_index.py`) é reconstruído sobre os mesmos tokens. O comportamento no navegador (`base.js` e o JS do portal) é testado por um harness Python que roda o Chrome headless.

**Tech Stack:** Python 3 (biblioteca padrão; `html.parser`), `unittest`, HTML/CSS/JS vanilla, Chrome headless (`google-chrome`), Fontsource 5.1.0 (WOFF2, OFL).

**Spec:** [`docs/superpowers/specs/2026-11-02-redesenho-ui-ux-design.md`](../specs/2026-11-02-redesenho-ui-ux-design.md). Referência visual: `docs/superpowers/specs/assets/2026-11-02-redesenho-ui-ux/mockup-modulo.html` e `mockup-portal.html` (abrir no navegador; valores de cor, espaçamento e comportamento saem deles).

## Global Constraints

- Textos de interface e documentação em **pt-BR**.
- Nenhuma dependência nova: Python só com biblioteca padrão; JS vanilla; nenhum recurso externo no HTML gerado (sem `fonts.googleapis.com`, sem CDN).
- Cada HTML gerado funciona via `file://` sem rede.
- **Todo token CSS declarado hoje em `_geradores/base.css` continua existindo com o mesmo nome** (spec §2.1). Tokens novos: `--rule-strong`, `--accent-soft`, `--ok`, `--bad`, `--console`, `--console-ink`, `--tipo-<t>` e `--tipo-<t>-bg` para `t` em `teoria|laboratorio|checklist|questoes|referencias`.
- Tema escuro: mesmo mecanismo atual (bloco `@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) }` + bloco `:root[data-theme="dark"]` com os mesmos valores).
- Chaves de `localStorage` existentes inalteradas: `cs_theme`, `cs_done_<slug>`, `cs_check_<slug>_<inputId>`. Novas: `cs_read_<slug>` (JSON lista de ids), `cs_quiz_<slug>_<qid>` (`acertei|errei|revisar`), `cs_last` (JSON `{"slug","secao","ts"}`). `<slug>` é a chave de `ESTUDOS_DADOS` (ex.: `Threat-Hunting`).
- Número do estudo = posição (1-based) do slug em `ESTUDOS_DADOS`; total = `len(ESTUDOS_DADOS)`. Nada fixa 57.
- O `index.html` gerado continua contendo `Módulos Compilados`, `"{disponiveis} / {total}"`, o caminho `<Pasta>/<arquivo_html>` e `data-slug="<slug>"` de cada módulo (55 testes de módulo dependem disso).
- Ordem de atributos nas seções: `<section class="study-section" id="…" data-tipo="…">` (testes fazem regex em `<section class="study-section" id="…"`).
- Testes: `unittest`. Rode só os arquivos afetados (`python3 -m unittest _geradores/testes/test_x.py`). Antes de suíte completa ou de recompilar os 57 módulos, confira `free -h`; a suíte completa roda com `systemd-run --user --scope --quiet -p MemoryMax=4G -p MemorySwapMax=1G python3 -m unittest discover -s _geradores/testes`. Nunca duas suítes ou duas instâncias do Chrome em paralelo.
- Para truncar saída, use `cut -c1-1500`; nunca `sed`/`grep` com intervalo grande no regex.
- Trabalhe num branch `feat/redesenho-ui-ux`. Commits terminam com `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Review Focus

1. **Laboratórios dependem de CSS e variáveis legados.** Um simulador que usa `var(--danger-color)` inline ou uma classe estilizada hoje em `base.css` (`.lab-controls`, `.edr-grid-container`, `.form-control`…) precisa continuar com a mesma aparência. Testes: T2 (`test_toda_variavel_usada_nos_corpos_existe`) e T3 (`test_classes_legadas_continuam_estilizadas`); erros de JS cobertos pela fumaça (T8).
2. **Títulos com entidades HTML** (`ATT&amp;CK`, `Pix &amp; MED`) devem aparecer uma vez escapados no sumário, no cabeçalho e no "anterior/próximo", nunca como `&amp;amp;`. Teste: T6 (`test_titulo_com_entidade_nao_e_escapado_duas_vezes`).
3. **`localStorage` antigo ou corrompido.** Quem já tem `cs_done_<slug>=true` (marcado no portal antigo) vê "Concluído"; `cs_read_<slug>` com JSON inválido conta como vazio, sem exceção. Testes: T4 (`test_cs_read_corrompido_nao_quebra`) e T10 (`test_status_concluido_sem_leitura`).
4. **Seção aninhada ou `h2` dentro do laboratório.** O sumário lista só as seções de primeiro nível, cada uma com o título do seu primeiro `h2`; um `h2` dentro de um simulador não vira item. Teste: T5 (`test_extrair_secoes_ignora_aninhadas`).
5. **Tema escuro pelo sistema, sem `cs_theme`.** As cores de tipo de seção e do console precisam existir também no bloco `prefers-color-scheme`, não só em `[data-theme="dark"]`. Teste: T2 (`test_tokens_novos_nos_tres_blocos`).

---

## Fase 1 — UI kit

### Task 1: Fontes embutidas

**Files:**
- Create: `_geradores/fontes/ibm-plex-sans-latin-400-normal.woff2`, `ibm-plex-sans-latin-400-italic.woff2`, `ibm-plex-sans-latin-600-normal.woff2`, `ibm-plex-mono-latin-400-normal.woff2`, `barlow-semi-condensed-latin-700-normal.woff2`, `_geradores/fontes/OFL.txt`
- Create: `_geradores/fontes.py`
- Test: `_geradores/testes/test_fontes.py`

**Interfaces:**
- Produces: `fontes.FONTES_DIR: Path`; `fontes.FACES: list[tuple[str, str, int, str]]` (arquivo, família, peso, estilo); `fontes.css_fontes(dir_fontes: Path = FONTES_DIR) -> str` — levanta `FileNotFoundError` com o nome do arquivo ausente.

- [ ] **Step 1: Baixar fontes e licenças**

Baixe de `https://cdn.jsdelivr.net/npm/@fontsource/<pacote>@5.1.0/files/<arquivo>` os 5 arquivos (pacotes `ibm-plex-sans`, `ibm-plex-mono`, `barlow-semi-condensed`). `OFL.txt` = concatenação de `https://cdn.jsdelivr.net/npm/@fontsource/<pacote>@5.1.0/LICENSE` dos três pacotes, separados por uma linha `====`. Esperado: tamanhos 19156, 20880, 20356, 14812, 23196 bytes.

- [ ] **Step 2: Escrever os testes**

```python
class TestFontes(unittest.TestCase):
    def test_cinco_faces_embutidas(self):
        css = css_fontes()
        self.assertEqual(css.count("@font-face"), 5)
        self.assertEqual(css.count("url(data:font/woff2;base64,"), 5)
        self.assertEqual(css.count("font-display: swap"), 5)
        for fam in ('"IBM Plex Sans"', '"IBM Plex Mono"', '"Barlow Semi Condensed"'):
            self.assertIn(f"font-family: {fam}", css)
        self.assertIn("font-style: italic", css)

    def test_orcamento_de_200kb(self):
        self.assertLess(len(css_fontes().encode("utf-8")), 200 * 1024)

    def test_arquivo_ausente_falha_com_nome(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(FileNotFoundError, "ibm-plex-sans-latin-400-normal.woff2"):
                css_fontes(Path(d))

    def test_licenca_presente(self):
        self.assertIn("SIL Open Font License", (FONTES_DIR / "OFL.txt").read_text(encoding="utf-8"))
```

- [ ] **Step 3: Rodar e ver falhar** — `python3 -m unittest _geradores/testes/test_fontes.py` → `ModuleNotFoundError: fontes`.
- [ ] **Step 4: Implementar `css_fontes`** em `_geradores/fontes.py` (base64 de cada arquivo, um `@font-face` por entrada de `FACES`, `font-display: swap`).
- [ ] **Step 5: Rodar e ver passar.**
- [ ] **Step 6: Commit** — `feat(ui-kit): fontes IBM Plex e Barlow embutidas em WOFF2 (OFL)`.

### Task 2: `tokens.css` e carga de CSS do `montar.py`

**Files:**
- Create: `_geradores/tokens.css`
- Modify: `_geradores/base.css` (remover §0 importação de fontes, §1 e §2 tokens — passam para `tokens.css`)
- Modify: `_geradores/montar.py` (nova `carregar_css`; template usa ela; remover os `<link>` do Google Fonts)
- Test: `_geradores/testes/test_tokens.py`; Modify: `_geradores/testes/test_assets.py` (testes de tokens passam a ler `tokens.css`)

**Interfaces:**
- Consumes: `fontes.css_fontes()` (T1).
- Produces: `montar.carregar_css() -> str` = `css_fontes()` + `tokens.css` + `base.css` + `laboratorio.css` (este último só existe a partir de T3; até lá, ignorado se ausente). `montar.TOKENS_CSS`, `montar.LABORATORIO_CSS: Path`.

- [ ] **Step 1: Escrever os testes**

```python
TIPOS = ["teoria", "laboratorio", "checklist", "questoes", "referencias"]
NOVOS = ["--rule-strong", "--accent-soft", "--ok", "--bad", "--console", "--console-ink"] + \
        [f"--tipo-{t}" for t in TIPOS] + [f"--tipo-{t}-bg" for t in TIPOS]

class TestTokens(unittest.TestCase):
    def test_toda_variavel_usada_nos_corpos_existe(self):
        usadas = set()
        for corpo in GERADORES.glob("*_body.html"):
            usadas |= set(re.findall(r"var\((--[a-z0-9-]+)", corpo.read_text(encoding="utf-8")))
        definidas = set(re.findall(r"(--[a-z0-9-]+)\s*:", TOKENS.read_text(encoding="utf-8")))
        self.assertEqual(usadas - definidas, set())

    def test_nomes_legados_preservados(self):
        antigos = set(re.findall(r"^\s*(--[a-z0-9-]+)\s*:", git_show("a671fbe:_geradores/base.css"), re.M))
        definidas = set(re.findall(r"(--[a-z0-9-]+)\s*:", TOKENS.read_text(encoding="utf-8")))
        self.assertEqual(antigos - definidas, set())

    def test_tokens_novos_nos_tres_blocos(self):
        css = TOKENS.read_text(encoding="utf-8")
        claro = bloco(css, ":root {")
        sistema = bloco(css, ':root:not([data-theme="light"])')
        escuro = bloco(css, ':root[data-theme="dark"]')
        for t in NOVOS:
            for b in (claro, sistema, escuro):
                self.assertIn(t + ":", b)
        self.assertEqual(declaracoes(sistema), declaracoes(escuro))

    def test_valores_da_spec(self):
        claro = bloco(TOKENS.read_text(encoding="utf-8"), ":root {")
        for nome, valor in {"--ground": "#F4F6F8", "--ink": "#14212B", "--tipo-teoria": "#2563EB",
                            "--tipo-laboratorio": "#0D9488", "--tipo-checklist": "#B45309",
                            "--tipo-questoes": "#C026D3", "--tipo-referencias": "#64748B",
                            "--warning-color": "#EA580C", "--law-color": "#6D28D9", "--console": "#0F1820"}.items():
            self.assertRegex(claro, rf"{nome}:\s*{valor}", nome)

    def test_html_gerado_sem_google_fonts(self):
        # montar um corpo mínimo num tempdir com montar_treinamento e checar:
        self.assertNotIn("fonts.googleapis.com", html)
        self.assertIn("@font-face", html)
```

`git_show(ref)` roda `git show <ref>` (o commit `a671fbe` é a base anterior ao redesenho). `bloco(css, inicio)` devolve o texto entre a `{` que segue `inicio` e a `}` correspondente; `declaracoes(b)` devolve o dicionário `nome → valor`. Escreva esses helpers no próprio arquivo de teste.

- [ ] **Step 2: Rodar e ver falhar** (`tokens.css` ausente).
- [ ] **Step 3: Criar `tokens.css`** com os valores da spec §2.1 e as variantes escuras do mockup (`:root[data-theme="dark"]` em `mockup-modulo.html`), mapeando os nomes do mockup para os nomes preservados (`--teo`→`--tipo-teoria`, `--f-body`→`--font-body`, `--r-md`→`--radius-md`…). Remova §0–§2 de `base.css`. Em `montar.py`, `carregar_css()` substitui a leitura direta de `base.css` e os três `<link>` de fontes saem do template.
- [ ] **Step 4: Atualizar `test_assets.py`**: `test_base_css_contains_design_tokens`, `test_tokens_de_cada_trilha`, `test_numero_do_bloco_de_trilha_legivel_nos_dois_temas` e `test_base_css_supports_dark_mode` passam a ler `tokens.css`.
- [ ] **Step 5: Rodar** `test_tokens.py`, `test_assets.py`, `test_montar.py`, `test_fontes.py` → PASS.
- [ ] **Step 6: Commit** — `feat(ui-kit): tokens.css com nomes preservados e tipos de seção`.

### Task 3: Componentes em `base.css` e `laboratorio.css`

**Files:**
- Create: `_geradores/laboratorio.css`
- Modify (reescrever): `_geradores/base.css`
- Test: `_geradores/testes/test_componentes_css.py`; Modify: `_geradores/testes/test_assets.py` (`test_base_css_contains_component_classes`), `_geradores/testes/test_responsivo.py` (`TestTreinamentosResponsivos` lê `montar.carregar_css()`)

**Interfaces:**
- Consumes: `montar.carregar_css()` (T2).
- Produces: as classes da spec §2.3, com estes nomes exatos, usados por T4 (JS) e T6 (chassi): `.topbar`, `.topbar-in`, `.nav-back`, `.crumb`, `.tipo-atual`, `.theme-toggle-btn`, `.toc-toggle`, `.readbar`, `.shell`, `.content`, `.toc`, `.toc-lista`, `.toc-item` (`.on`, `.lida`), `.toc-contador`, `.toc-progresso`, `.btn-concluir` (`.pronto`, `.concluido`), `.mhead`, `.mhead-kicker`, `.mhead-sub`, `.chips`, `.chip`, `.roadmap`, `.shead`, `.stype`, `.lead-text`, `.callout` + `tip|warning|danger|law|key`, `.callout-title`, `.callout-icon`, `.table-responsive`, `.data-table`, `.terminal-box`, `.terminal-header`, `.terminal-title`, `.terminal-copy-btn`, `.diagram-box`, `.diagram-header`, `.diagram-title`, `.diagram-svg-wrap`, `.lab-box`, `.lab-header`, `.lab-body`, `.checklist`, `.checklist-head`, `.checklist-item` (`.completed`), `.quiz-score`, `.quiz-filtros`, `.quiz-item` (`[data-res]`), `.quiz-question`, `.quiz-details`, `.quiz-toggle`, `.quiz-answer`, `.quiz-selfeval`, `.facts-grid`, `.facts-card`, `.study-done`, `.study-pager`, `body.toc-aberto` (gaveta). Seletores de tipo: `[data-tipo="<t>"] { --c: var(--tipo-<t>); --soft: var(--tipo-<t>-bg) }`.

- [ ] **Step 1: Escrever os testes**

```python
class TestComponentesCss(unittest.TestCase):
    def test_classes_da_spec(self):
        css = carregar_css()
        for c in CLASSES_T3:  # a lista do bloco Produces acima
            self.assertRegex(css, re.escape(c) + r"[\s,{:.\[>]", c)

    def test_cinco_tipos_mapeados(self):
        css = carregar_css()
        for t in TIPOS:
            self.assertIn(f'[data-tipo="{t}"]', css)
            self.assertIn(f"var(--tipo-{t})", css)

    def test_classes_legadas_continuam_estilizadas(self):
        antigas = classes_com_regra(git_show("a671fbe:_geradores/base.css"))
        usadas = set()
        for corpo in GERADORES.glob("*_body.html"):
            for attr in re.findall(r'class="([^"]+)"', corpo.read_text(encoding="utf-8")):
                usadas |= set(attr.split())
        novas = classes_com_regra(carregar_css())
        removidas_de_proposito = {"hero-header", "hero-subtitle", "section-num", "section-title-wrap",
                                  "section-tag", "section-header", "study-header", "study-title",
                                  "study-lead", "study-track-kicker", "study-meta-bar", "content-section",
                                  "check-item", "callout-tip", "top-nav", "top-nav-inner", "nav-title",
                                  "nav-actions", "study-footer"}
        self.assertEqual((antigas & usadas) - novas - removidas_de_proposito, set())

    def test_gaveta_abaixo_de_1024(self):
        movel = bloco_media(carregar_css(), "max-width: 1023px")
        self.assertIn(".toc", movel)
        self.assertIn("body.toc-aberto .toc", movel)

    def test_movimento_reduzido_e_foco_visivel(self):
        css = carregar_css()
        self.assertIn("prefers-reduced-motion: reduce", css)
        self.assertIn(":focus-visible", css)
```

`classes_com_regra(css)` extrai os nomes de classe que aparecem em seletores (texto antes de `{`). `bloco_media` vem de `test_responsivo.py`.

- [ ] **Step 2: Rodar e ver falhar.**
- [ ] **Step 3: Mover para `laboratorio.css`, sem mudar as regras:** a §8 inteira do `base.css` atual (`.lab-box` e internos), a §9 (botões e controles: `.btn`, `.btn-primary`, `.btn-secondary`, `.form-control`, `.lab-btn`…) e as regras específicas de simuladores (`.edr-grid-container` e afins). Só os valores literais de cor passam a usar tokens quando houver token equivalente.
- [ ] **Step 4: Reescrever `base.css`** com as classes do bloco Produces, reproduzindo o mockup de módulo (estrutura e valores do `<style>` de `mockup-modulo.html`, com os nomes de classe e de token deste plano). O cabeçalho de `.lab-box` passa a ser placa console (`--console`), e `.diagram-box` ganha a placa console ao redor do `.diagram-svg-wrap`. As regras de `TestTreinamentosResponsivos` que continuam válidas (`.lab-controls > *`, `img, select, input, textarea`, `.btn` no celular, `:not(pre) > code`) permanecem.
- [ ] **Step 5: Atualizar testes existentes:** em `test_responsivo.py`, `test_barra_superior_mostra_so_voltar_e_tema` passa a exigir, em `max-width: 640px`, `display: none` para `.crumb`; os demais testes da classe leem `carregar_css()`. Em `test_assets.py`, a lista de componentes passa a ser a de `CLASSES_T3`.
- [ ] **Step 6: Rodar** `test_componentes_css.py test_assets.py test_responsivo.py test_tokens.py` → PASS.
- [ ] **Step 7: Commit** — `feat(ui-kit): componentes do novo design e laboratorio.css preservando simuladores`.

### Task 4: `base.js` e harness de navegador

**Files:**
- Create: `_geradores/testes/navegador.py`
- Modify (reescrever): `_geradores/base.js`
- Test: `_geradores/testes/test_base_js.py`; Modify: `_geradores/testes/test_assets.py` (`test_base_js_contains_core_functions`, `test_base_js_handles_localstorage_persistence`)

**Interfaces:**
- Consumes: classes de T3.
- Produces:
  - `navegador.CHROME: str | None` (de `shutil.which("google-chrome") or shutil.which("chromium")`).
  - `navegador.executar(html: str, script_teste: str = "", perfil: Path | None = None, largura: int = 1440, altura: int = 900, budget_ms: int = 4000, script_antes: str = "") -> dict`: grava `html` num diretório temporário, injeta logo após `<head>` um coletor e o `script_antes` (antes de qualquer outro script da página) (`window.onerror` + `console.error` → `window.__erros`) e antes de `</body>` o `script_teste`, que termina chamando `__fim(valor)`; `__fim` grava `JSON.stringify({saida: valor, erros: window.__erros})` num `<pre id="__saida">`. Roda `CHROME --headless=new --disable-gpu --no-sandbox --user-data-dir=<perfil ou tmp> --window-size=L,A --virtual-time-budget=B --dump-dom file://…` e devolve o JSON lido do DOM. O `perfil` persistente permite testar a restauração do `localStorage` entre duas execuções.
  - `base.js` expõe a API pública da spec §3.3 (`window.CS`, `toggleTheme`, `initTheme`, `initChecklist`, `initQuiz`, `checkQuiz`, `copyCode`, `isStudyDone`, `setStudyDone`, `safeStorageGet`, `safeStorageSet`, `escapeHtml`, `formatBytes`, `formatNumber`, `bytesToHex`, `hexToBytes`, `sha256Hex`) mais `CS.labProgress(feitos: number, total: number)`. Na carga, `CS.init()` lê o slug de `<body data-slug>` e liga tema, sumário, leitura, checklist, questões, concluir e gaveta.

Comportamento (spec §3.3): seção atual = última `section.study-section` cujo topo está acima de 35% da janela; `a.toc-item[href="#id"]` recebe `.on` e `aria-current="true"`; `.tipo-atual` mostra ícone + rótulo do tipo. Seção lida quando o fim passa de 60% da janela, ou ao chegar no fim da página; `.toc-item.lida`; `cs_read_<slug>`; `.toc-progresso` com `N%`. Checklist: insere `div.checklist-head` ("N de M" + barra) antes de cada `ul.checklist`; chave `cs_check_<slug>_<inputId>`; `.checklist-item.completed`; contador `.toc-contador` do item de checklist = `marcados/total`. Questões: insere `div.quiz-score` (contagens + filtros `todas|pendentes|sem`) no início da seção `questoes` e `div.quiz-selfeval` (botões `data-v="acertei|errei|revisar"`) dentro de cada `details.quiz-details` aberta; `quiz-item[data-res]`; contador = `acertos/total`. Múltipla escolha (`quiz-item[data-formato="multipla"]`): o primeiro clique em `.quiz-btn` grava `acertei` ou `errei`. Concluir: `.btn-concluir` alterna `cs_done_<slug>` e ganha `.pronto` quando 100% lido e `.concluido` quando feito. `cs_last` grava `{slug, secao, ts}` a cada troca de seção atual. Gaveta: `.toc-toggle` alterna `body.toc-aberto` e `aria-expanded`; Esc e clique num item fecham e devolvem o foco ao botão.

Os testes usam uma página de fixture montada pelo próprio teste com o markup que T6 vai gerar: `body[data-slug="Teste"]`, `.topbar` com `.tipo-atual` e `.toc-toggle`, `aside.toc` com `a.toc-item[href="#s1"] … [href="#s5"]` (cada um com `data-tipo` e um `.toc-contador`), `.btn-concluir`, e cinco seções (`teoria`, `laboratorio`, `checklist` com 3 itens, `questoes` com 2 abertas e 1 de múltipla escolha, `referencias`) altas o bastante (`min-height: 1200px`) para rolar. Escreva essa fixture como função `pagina_fixture() -> str` em `test_base_js.py`, incluindo o CSS de `carregar_css()` e o `base.js`.

- [ ] **Step 1: Escrever os testes** (`@unittest.skipUnless(CHROME, "Chrome ausente")`):

```python
def test_sem_erros_na_carga(self):
    r = executar(pagina_fixture(), "__fim(1)")
    self.assertEqual(r["erros"], [])

def test_secao_atual_e_leitura(self):
    r = executar(pagina_fixture(), """
      document.getElementById('s3').scrollIntoView(); window.dispatchEvent(new Event('scroll'));
      setTimeout(() => __fim({on: document.querySelector('.toc-item.on').getAttribute('href'),
        tipo: document.querySelector('.tipo-atual').textContent,
        lidas: JSON.parse(localStorage.getItem('cs_read_Teste'))}), 300);""")
    self.assertEqual(r["saida"]["on"], "#s3")
    self.assertIn("Checklist", r["saida"]["tipo"])
    self.assertEqual(r["saida"]["lidas"][:2], ["s1", "s2"])

def test_checklist_salva_e_restaura(self):
    with tempfile.TemporaryDirectory() as perfil:
        executar(pagina_fixture(), "document.querySelector('#c2').click(); __fim(1)", perfil=Path(perfil))
        r = executar(pagina_fixture(), """__fim({marcado: document.querySelector('#c2').checked,
            cab: document.querySelector('.checklist-head').textContent,
            cnt: document.querySelector('a[href="#s3"] .toc-contador').textContent})""", perfil=Path(perfil))
    self.assertTrue(r["saida"]["marcado"]); self.assertIn("1 de 3", r["saida"]["cab"]); self.assertEqual(r["saida"]["cnt"], "1/3")

def test_autoavaliacao_placar_e_filtro(self):
    r = executar(pagina_fixture(), """
      const d = document.querySelector('[data-q="q1"] details'); d.open = true; d.dispatchEvent(new Event('toggle'));
      document.querySelector('[data-q="q1"] .quiz-selfeval [data-v="errei"]').click();
      document.querySelector('.quiz-filtros [data-f="pendentes"]').click();
      __fim({res: document.querySelector('[data-q="q1"]').dataset.res,
             chave: localStorage.getItem('cs_quiz_Teste_q1'),
             visiveis: [...document.querySelectorAll('.quiz-item')].filter(q => q.offsetParent).length})""")
    self.assertEqual(r["saida"], {"res": "errei", "chave": "errei", "visiveis": 1})

def test_multipla_escolha_conta_primeiro_clique(self): ...
    # clicar primeiro na alternativa errada e depois na certa → cs_quiz_Teste_q3 == "errei"

def test_concluir_alterna_cs_done(self): ...
    # clique → localStorage cs_done_Teste == "true" e .btn-concluir.concluido; segundo clique → "false"

def test_cs_last_registra_secao(self): ...
    # rolar até s2 → JSON.parse(cs_last).slug == "Teste" e .secao == "s2"

def test_cs_read_corrompido_nao_quebra(self):
    r = executar(pagina_fixture(), "__fim(1)", script_antes="localStorage.setItem('cs_read_Teste','{x')")
    self.assertEqual(r["erros"], [])

def test_gaveta_no_celular(self): ...
    # largura=400: clicar .toc-toggle → body.toc-aberto e aria-expanded="true"; Escape → fechada e foco no botão

def test_lab_progress_no_sumario(self):
    r = executar(pagina_fixture(), "CS.labProgress(2, 4); __fim(document.querySelector('a[href=\"#s2\"] .toc-contador').textContent)")
    self.assertEqual(r["saida"], "2/4")

def test_lab_sem_progresso_sem_contador(self):
    r = executar(pagina_fixture(), "__fim(document.querySelector('a[href=\"#s2\"] .toc-contador').textContent)")
    self.assertEqual(r["saida"], "")

def test_api_publica_preservada(self):
    nomes = ["CS","toggleTheme","initTheme","initChecklist","initQuiz","checkQuiz","copyCode","isStudyDone",
             "setStudyDone","safeStorageGet","safeStorageSet","escapeHtml","formatBytes","formatNumber",
             "bytesToHex","hexToBytes","sha256Hex"]
    r = executar(pagina_fixture(), f"__fim({json.dumps(nomes)}.filter(n => typeof window[n] === 'undefined'))")
    self.assertEqual(r["saida"], [])
```

- [ ] **Step 2: Rodar e ver falhar.**
- [ ] **Step 3: Implementar `navegador.py`.**
- [ ] **Step 4: Reescrever `base.js`** com o comportamento acima, mantendo os utilitários atuais (crypto, bytes, formatação, cópia, tema) sem alteração de assinatura.
- [ ] **Step 5: Rodar** `test_base_js.py test_assets.py` → PASS.
- [ ] **Step 6: Commit** — `feat(ui-kit): base.js com sumário, leitura, flashcards, concluir e harness de navegador`.

---

## Fase 2 — Chassi

### Task 5: Validador de contrato

**Files:**
- Create: `_geradores/contrato.py`
- Test: `_geradores/testes/test_contrato.py`

**Interfaces:**
- Produces:
  - `contrato.TIPOS: tuple[str, ...] = ("teoria", "laboratorio", "checklist", "questoes", "referencias")`
  - `contrato.ROTULOS: dict[str, tuple[str, str]] = {"teoria": ("📘", "Teoria"), "laboratorio": ("🧪", "Laboratório"), "checklist": ("☑️", "Checklist"), "questoes": ("❓", "Questões de concurso"), "referencias": ("📚", "Referências")}`
  - `@dataclass(frozen=True) class Secao: id: str; tipo: str; titulo_html: str; n_checklist: int; n_questoes: int` (`titulo_html` = conteúdo interno do primeiro `h2`, como está no fonte, sem reescapar).
  - `contrato.extrair_secoes(html: str) -> list[Secao]` — só `section.study-section` filhas diretas de `article.study-container`.
  - `class ContratoInvalido(Exception)` com o atributo `erros: list[str]` (a mensagem da exceção é `"\n".join(erros)`).
  - `contrato.validar_corpo(html: str, slug: str) -> list[str]` — mensagens `"<slug> §<n>: <onde>: <descrição>"` para as regras 1–8 da spec §3.1.

- [ ] **Step 1: Escrever os testes.** Um `CORPO_VALIDO` mínimo com as cinco seções. Para cada regra, um corpo inválido e a mensagem esperada, por exemplo:

```python
def test_regra_2_tipo_invalido(self):
    erros = validar_corpo(CORPO_VALIDO.replace('data-tipo="teoria"', 'data-tipo="teorico"', 1), "X")
    self.assertIn('X §2: section#s1: data-tipo "teorico" inválido', erros)

def test_regra_2_ordem_dos_atributos(self):
    html = CORPO_VALIDO.replace('<section class="study-section" id="s1" data-tipo="teoria">',
                                '<section data-tipo="teoria" class="study-section" id="s1">')
    self.assertTrue(any(e.startswith("X §2: section#s1: ordem") for e in validar_corpo(html, "X")))

def test_regra_4_section_tag_proibido(self):
    html = CORPO_VALIDO.replace("<h2>", '<span class="section-tag">Seção 01</span><h2>', 1)
    self.assertTrue(any(e.startswith("X §4:") for e in validar_corpo(html, "X")))

def test_regra_5_falta_laboratorio(self): ...
def test_regra_6_checklist_sem_label_for(self): ...
def test_regra_7_quiz_sem_details(self): ...
def test_regra_8_callout_sem_modificador(self): ...
def test_regra_1_dois_articles(self): ...
def test_regra_3_secao_sem_h2(self): ...
def test_ids_duplicados(self): ...

def test_corpo_valido_sem_erros(self):
    self.assertEqual(validar_corpo(CORPO_VALIDO, "X"), [])

def test_extrair_secoes_ignora_aninhadas(self):
    html = CORPO_VALIDO.replace("<!--lab-->", '<section class="study-section" id="interna" data-tipo="teoria"><h2>Interna</h2></section><h2>Passo</h2>')
    secoes = extrair_secoes(html)
    self.assertEqual([s.id for s in secoes], ["s1", "s2", "s3", "s4", "s5"])
    self.assertEqual(secoes[1].titulo_html, "Laboratório X")

def test_contagens(self):
    s = {x.tipo: x for x in extrair_secoes(CORPO_VALIDO)}
    self.assertEqual((s["checklist"].n_checklist, s["questoes"].n_questoes), (3, 3))
```

- [ ] **Step 2: Rodar e ver falhar.**
- [ ] **Step 3: Implementar** com `html.parser.HTMLParser` (pilha de tags para saber profundidade; registra posição de início e fim de cada seção de primeiro nível).
- [ ] **Step 4: Rodar e ver passar.**
- [ ] **Step 5: Commit** — `feat(chassi): validador do contrato de markup dos corpos`.

### Task 6: Chassi gerado pelo `montar.py`

**Files:**
- Create: `_geradores/chassi.py`
- Modify: `_geradores/montar.py` (`montar_treinamento` valida e monta o chassi; o rodapé antigo `study-footer` e o `header.top-nav` saem)
- Test: `_geradores/testes/test_chassi.py`; Modify: `_geradores/testes/test_montar.py`

**Interfaces:**
- Consumes: `contrato.extrair_secoes`, `contrato.validar_corpo`, `contrato.ROTULOS` (T5); `montar.carregar_css` (T2); `index_dados.ESTUDOS_DADOS`, `TRILHAS`, `NIVEIS`; `montar.carregar_catalogo_estudos()`.
- Produces:
  - `@dataclass class InfoModulo: slug, numero: int, total: int, titulo, subtitulo, trilha_num: int, trilha_nome, tempo_minutos: int, nivel_rotulo, nist, mitre, carreiras: list[str], caminho_rel: str, anterior: tuple[str, str, str] | None, proximo: tuple[str, str, str] | None` (tuplas = `(slug, titulo, caminho_rel)`; `caminho_rel` = `"../<pasta>/<arquivo_html>"`).
  - `chassi.info_modulo(slug: str) -> InfoModulo` — `KeyError` com o slug se não houver `ESTUDOS_DADOS`.
  - `chassi.gerar_topbar(info) -> str`, `chassi.gerar_sumario(info, secoes) -> str`, `chassi.gerar_cabecalho(info, secoes) -> str`, `chassi.gerar_fim(info) -> str`.
  - `chassi.aplicar_cabecalhos_de_secao(body: str, secoes: list[Secao]) -> str` — troca o primeiro `<h2>…</h2>` de cada seção por `<div class="shead"><span class="stype">ÍCONE RÓTULO <small>· Seção X de N</small></span><h2>…</h2></div>`.
  - `chassi.numerar_questoes(body: str) -> str` — adiciona `data-q="q1"…"qN"` aos `div.quiz-item`, na ordem.
  - `montar.montar_treinamento(...)` — mesma assinatura; levanta `contrato.ContratoInvalido` (T5) se `validar_corpo` acusar erros. O `main()` captura, imprime as mensagens no stderr e sai com código 1.

Layout da página (ordem): `.topbar` > `.readbar`; `.shell` com `aside.toc` + `main.content` (> `.mhead` + corpo com `.shead` + `.study-done` + `.study-pager` dentro da última seção). Textos fixos: kicker `Trilha {n} · {nome} · Estudo {NN}`; sumário `Estudo {NN} de {total}`; botões `✓ Concluir módulo`; pager `← Anterior · Estudo {NN}` / `Próximo · Estudo {NN} →`. Chips do cabeçalho: `⏱ {tempo} min`, `📈 {nivel}`, `🛡 NIST {nist}`, `🎯 ATT&CK {mitre}`, `👤 {carreiras unidas por " · "}`. Roadmap: um link por tipo presente, na ordem de `TIPOS`, com quantidade (`2 seções`, `7 itens`, `7 questões`; laboratório e referências sem número). O título do `h1` e dos itens vem de `ESTUDOS_DADOS` e de `Secao.titulo_html` sem reescapar; textos vindos de `ESTUDOS_DADOS` passam por `html.escape` uma única vez.

- [ ] **Step 1: Escrever os testes** com um corpo válido temporário e o slug `Threat-Hunting` (dados reais):

```python
def test_cabecalho_a_partir_dos_dados(self):
    html = montar_fixture("Threat-Hunting")
    d = ESTUDOS_DADOS["Threat-Hunting"]
    self.assertIn(f"Estudo {list(ESTUDOS_DADOS).index('Threat-Hunting') + 1:02d}", html)
    self.assertIn(f"<h1>{escape(d['titulo'])}</h1>", html)
    self.assertIn(f"⏱ {d['tempo_minutos']} min", html)

def test_sumario_um_item_por_secao(self):
    html = montar_fixture("Threat-Hunting")
    self.assertEqual(html.count('class="toc-item'), 5)
    for i in range(1, 6):
        self.assertIn(f"Seção {i} de 5", html)

def test_anterior_e_proximo_nas_pontas(self):
    primeiro, ultimo = list(ESTUDOS_DADOS)[0], list(ESTUDOS_DADOS)[-1]
    self.assertIsNone(info_modulo(primeiro).anterior)
    self.assertIsNone(info_modulo(ultimo).proximo)
    self.assertTrue(info_modulo(primeiro).proximo[2].startswith("../"))

def test_titulo_com_entidade_nao_e_escapado_duas_vezes(self):
    html = montar_fixture("Threat-Hunting", titulo_secao="Caça &amp; ATT&amp;CK")
    self.assertIn("Caça &amp; ATT&amp;CK", html)
    self.assertNotIn("&amp;amp;", html)

def test_questoes_numeradas(self):
    html = montar_fixture("Threat-Hunting")
    self.assertEqual(re.findall(r'data-q="(q\d+)"', html), ["q1", "q2", "q3"])

def test_corpo_invalido_aborta(self):
    with self.assertRaises(ContratoInvalido) as cm:
        montar_fixture("Threat-Hunting", corpo=CORPO_SEM_LAB)
    self.assertTrue(any("§5" in e for e in cm.exception.erros))

def test_cli_corpo_invalido_sai_com_1(self): ...
    # subprocess montar.py com corpo inválido → returncode 1 e "§5" no stderr

def test_slug_sem_dados(self):
    with self.assertRaisesRegex(KeyError, "Nao-Existe"):
        info_modulo("Nao-Existe")
```

- [ ] **Step 2: Atualizar `test_montar.py`:** os testes que montam corpos de exemplo passam a usar corpos válidos pelo contrato e um slug existente; `study-footer` sai das asserções; `test_montar_treinamento_com_diagrama_mermaid` continua verificando o `diagram-svg-wrap`.
- [ ] **Step 3: Rodar e ver falhar.**
- [ ] **Step 4: Implementar `chassi.py` e integrar no `montar.py`.** O `<body>` recebe `data-slug="<slug de ESTUDOS_DADOS>"`. Nesta task, nenhum módulo real é recompilado: os corpos ainda não estão migrados.
- [ ] **Step 5: Rodar** `test_chassi.py test_montar.py test_contrato.py` → PASS.
- [ ] **Step 6: Commit** — `feat(chassi): montar.py gera barra, sumário, cabeçalho, seções e fim do módulo`.

---

## Fase 3 — Migração

### Task 7: `migrar_markup.py`

**Files:**
- Create: `_geradores/migrar_markup.py`
- Test: `_geradores/testes/test_migracao.py`

**Interfaces:**
- Consumes: `contrato.validar_corpo`, `contrato.extrair_secoes` (T5).
- Produces:
  - `migrar_markup.EXCECOES: dict[tuple[str, str], str]` — `(arquivo_body_sem_sufixo, id_secao) → tipo`.
  - `migrar_markup.classificar(secao_html: str, eh_ultima: bool) -> str` — regras da spec §3.5.1, nesta ordem.
  - `migrar_markup.migrar(html: str, chave: str) -> str` — normalização G1/G2/G3 da spec §3.5.3 + `data-tipo` após o `id`; idempotente.
  - `migrar_markup.texto_visivel(html: str) -> list[str]` — texto de cada seção, sem os elementos removidos de propósito, com espaços normalizados.
  - `migrar_markup.cabecalho_legado(html: str) -> dict[str, str]` — dados do `study-header`/`hero-header` (kicker, título, subtítulo, badges) para a conferência.
  - CLI: `python3 _geradores/migrar_markup.py --revisar` imprime `chave | id | tipo | título` e as divergências de cabeçalho; `--aplicar` grava, abortando (código 1) num corpo cujo `texto_visivel` mudou ou que continua violando o contrato.

- [ ] **Step 1: Escrever os testes** com trechos sintéticos de cada geração (copie a estrutura real de `fundamentos_ciber_body.html`, `redes_e_protocolos_body.html` e `threat_hunting_body.html`):

```python
def test_g3_remove_section_tag_e_tipa(self):
    out = migrar(G3, "x")
    self.assertNotIn("section-tag", out); self.assertNotIn("section-header", out)
    self.assertIn('<section class="study-section" id="simulador" data-tipo="laboratorio">', out)

def test_g2_envolve_em_article_e_simplifica_h2(self):
    out = migrar(G2, "x")
    self.assertIn('<article class="study-container"', out)
    self.assertNotIn("study-header", out); self.assertNotIn("section-num", out)

def test_g1_normaliza_variantes(self):
    out = migrar(G1, "x")
    for velho in ("hero-header", "content-section", 'class="check-item"', "callout-tip"):
        self.assertNotIn(velho, out)
    self.assertIn('class="callout tip"', out)
    self.assertIn('data-formato="multipla"', out)

def test_idempotente(self):
    for g in (G1, G2, G3):
        uma = migrar(g, "x"); self.assertEqual(migrar(uma, "x"), uma)

def test_texto_preservado(self):
    for g in (G1, G2, G3):
        self.assertEqual(texto_visivel(g), texto_visivel(migrar(g, "x")))

def test_resultado_passa_no_contrato(self):
    for g in (G1, G2, G3):
        self.assertEqual(validar_corpo(migrar(g, "x"), "x"), [])

def test_excecao_prevalece(self):
    with mock.patch.dict(EXCECOES, {("x", "intro"): "laboratorio"}):
        self.assertIn('id="intro" data-tipo="laboratorio"', migrar(G3, "x"))

def test_classificacao(self):
    self.assertEqual(classificar('<div class="lab-box"></div><ul class="checklist"></ul>', False), "laboratorio")
    self.assertEqual(classificar('<ul class="checklist"></ul>', False), "checklist")
    self.assertEqual(classificar('<div class="quiz-item"></div>', False), "questoes")
    self.assertEqual(classificar('<div class="facts-grid"></div>', False), "referencias")
    self.assertEqual(classificar("<p>texto</p><ul><li>RFC 1</li></ul>", True), "referencias")
    self.assertEqual(classificar("<p>texto</p>", False), "teoria")
```

- [ ] **Step 2: Rodar e ver falhar.**
- [ ] **Step 3: Implementar** com transformações sobre o texto do fonte (regex ancoradas nas tags conhecidas) para preservar formatação e indentação do restante do arquivo; use `html.parser` só para localizar as seções.
- [ ] **Step 4: Rodar e ver passar.**
- [ ] **Step 5: Commit** — `feat(migracao): migrar_markup.py idempotente com preservação de texto`.

### Task 8: Migrar os 57 corpos e recompilar

**Files:**
- Modify: `_geradores/*_body.html` (57), `_geradores/migrar_markup.py` (só `EXCECOES`), `_geradores/index_dados.py` (só divergências da conferência), `*/treinamento-*.html` (57), `index.html`
- Modify: os 11 testes com `Seção 0{n}` em `_geradores/testes/`: `test_seguranca_containers`, `test_gestao_riscos_terceiros`, `test_deteccao_resposta_nuvem`, `test_infraestrutura_como_codigo`, `test_monitoramento_rede_nsm`, `test_legislacao_crimes_ciberneticos`, `test_threat_hunting`, `test_soar_automacao`, `test_fraude_pagamentos_pix`, `test_regulacao_setor_financeiro`, `test_seguranca_kubernetes`; e `test_piloto.py`
- Create: `_geradores/testes/test_corpos_migrados.py`, `_geradores/testes/test_fumaca_navegador.py`

**Interfaces:**
- Consumes: `migrar_markup` (T7), `contrato` (T5), `montar` (T6), `navegador.executar` (T4).

- [ ] **Step 1: Revisar a classificação** — `python3 _geradores/migrar_markup.py --revisar | cut -c1-1500`. Esperado: 355 linhas de seção; em cada módulo, um `laboratorio`, um `checklist`, um `questoes` e um `referencias`. Corrija os desvios em `EXCECOES` e as divergências de cabeçalho (G1/G2) em `index_dados.py`. Registre no ledger da execução: `Ruling: <seção> → <tipo> — <motivo>`.
- [ ] **Step 2: Escrever `test_corpos_migrados.py`:**

```python
def test_todos_os_corpos_no_contrato(self):
    erros = [e for c in sorted(GERADORES.glob("*_body.html"))
             for e in validar_corpo(c.read_text(encoding="utf-8"), c.stem)]
    self.assertEqual(erros, [])

def test_migracao_ja_aplicada_e_idempotente(self):
    for c in GERADORES.glob("*_body.html"):
        html = c.read_text(encoding="utf-8")
        self.assertEqual(migrar(html, c.stem.replace("_body", "")), html, c.name)
```

- [ ] **Step 3: Rodar e ver falhar.**
- [ ] **Step 4: Aplicar** — `python3 _geradores/migrar_markup.py --aplicar`. Esperado: código 0, 57 arquivos alterados (`git status --short _geradores/*_body.html | wc -l` → 57).
- [ ] **Step 5: Atualizar os testes de módulo:** nos 11 testes, `self.assertIn(f"Seção 0{n}", body)` passa a ser `self.assertIn(f"Seção {n} de {len(ids)}", compilado)`, lendo o HTML compilado. Em `test_piloto.py`, `"hero-header"` vira `"mhead"`.
- [ ] **Step 6: Recompilar** — `free -h`; depois `./_geradores/gerar.sh todos`. Esperado: 57 `[OK]` + portal, sem invocar o mermaid-cli (cache intacto: `git status --short _geradores/cache_diagramas | wc -l` → 0).
- [ ] **Step 7: Escrever `test_fumaca_navegador.py`** (`skipUnless(CHROME)`): para cada `ESTUDOS_DADOS` com HTML compilado, `executar(html, "__fim({toc: document.querySelectorAll('.toc-item').length, secoes: document.querySelectorAll('section.study-section[data-tipo]').length, total: document.querySelectorAll('section.study-section').length})")` → `erros == []`, `toc == secoes == total > 0`. Também `index.html` com `__fim(1)` → `erros == []`. Sequencial.
- [ ] **Step 8: Rodar** `test_corpos_migrados.py`, `test_fumaca_navegador.py` e, com o teto de memória das restrições globais, a suíte completa → tudo PASS, exceto os testes de abas do portal que T9/T10 reescrevem (anote quais falham; nenhuma outra falha é aceitável).
- [ ] **Step 9: Conferência visual intermediária** — capturas headless (1440×4000, tema claro e escuro) de Fundamentos-Ciber, Redes-e-Protocolos, Threat-Hunting, LGPD-e-Privacidade e Pentest-Metodologias em `.superpowers/capturas/`, comparadas com `mockup-modulo.html`. Desvio visual relevante volta para T3.
- [ ] **Step 10: Commit** — `refactor(modulos): 57 corpos no contrato de markup, recompilados com o novo chassi`.

---

## Fase 4 — Portal

### Task 9: Estrutura e CSS do portal

**Files:**
- Modify: `_geradores/build_index.py` (template, cartões, menu, visões), `_geradores/index.css` (reescrito sobre `tokens.css`, sem declarar tokens)
- Test: `_geradores/testes/test_portal.py`; Modify: `test_index.py`, `test_aba_nivel.py`, `test_abas_certificacao_progresso.py`, `test_rotas_sugeridas.py`, `test_responsivo.py` (`TestPortalResponsivo`), `test_trilhas_*.py` (só o que referir abas)

**Interfaces:**
- Consumes: `fontes.css_fontes`, `tokens.css`, `contrato.extrair_secoes`; as funções atuais `render_necessidades_grid`, `render_rota_vaga`, `render_certificacoes`, `render_painel_rotas`, `render_painel_certificacoes`, `render_chip_modulo` (mantidas, só a marcação de invólucro muda).
- Produces:
  - `build_index.contar_secoes(slug: str) -> int` (do corpo `_body.html` via `extrair_secoes`; 0 se não houver corpo).
  - Marcação lida por T10: `button.menu-toggle[aria-expanded="false"]` na barra superior; `nav.menu-lateral a[data-view="catalogo|rotas|certificacoes|necessidades|vaga|progresso"]`; `section.view[data-view="…"]` (só `catalogo` sem `hidden`); `#continuar` (vazio no HTML; preenchido por JS); `.agrupar button[data-grupo="trilha|nivel|perfil|nist"]`; `#so-pendentes`; `#busca`; `#grupos`; cada cartão `a.mc[data-slug][data-trilha][data-nivel][data-perfis="a|b"][data-nist][data-secoes="N"][data-busca="texto minúsculo"]` com `.mc-status` vazio; `#progresso-global` com o texto `Módulos Compilados` e `"{disponiveis} / {total}"`.

O cartão mostra: `Estudo NN`, `⏱ N min`, título, subtítulo, nível, `NIST …`, `🧪 {simulador_nome}`, `.mc-status`. Saem do cartão: checkbox "Estudo concluído", "Responde a" e lista de fatos. A visão `certificacoes` contém o painel de filtro por certificação **e** a matriz (`render_certificacoes`); `vaga` contém `render_rota_vaga`; `necessidades` contém `render_necessidades_grid`; `progresso` contém a lista "Meu progresso" atual (com marcar/desmarcar).

- [ ] **Step 1: Escrever `test_portal.py`:**

```python
def test_menu_com_seis_visoes(self):
    self.assertEqual(re.findall(r'<a [^>]*data-view="(\w+)"', self.html),
                     ["catalogo", "rotas", "certificacoes", "necessidades", "vaga", "progresso"])

def test_so_catalogo_visivel_na_carga(self):
    visiveis = re.findall(r'<section class="view" data-view="(\w+)">', self.html)
    self.assertEqual(visiveis, ["catalogo"])

def test_um_cartao_por_modulo_com_total_de_secoes(self):
    for slug in ESTUDOS_DADOS:
        self.assertRegex(self.html, rf'data-slug="{slug}"[^>]*data-secoes="{contar_secoes(slug)}"')

def test_textos_que_os_testes_de_modulo_exigem(self):
    self.assertIn("Módulos Compilados", self.html)
    self.assertIn(f"/ {len(ESTUDOS_DADOS)}", self.html)

def test_abas_antigas_removidas(self):
    for velho in ("switchTab(", 'data-facet="', "Estudo Concluído"):
        self.assertNotIn(velho, self.html)

def test_sem_google_fonts_e_com_tokens(self):
    self.assertNotIn("fonts.googleapis.com", self.html)
    self.assertIn("--tipo-teoria", self.html)

def test_index_css_nao_declara_tokens(self):
    self.assertNotRegex(INDEX_CSS.read_text(encoding="utf-8"), r"^\s*--ground\s*:", re.M)
```

- [ ] **Step 2: Atualizar os testes de abas** (`test_aba_nivel`, `test_abas_certificacao_progresso`, `test_rotas_sugeridas`, `test_index`): asserções sobre `data-facet`/`switchTab`/`filter-subpanel` passam a verificar o equivalente novo (`data-grupo="nivel"`, `data-view="rotas"`, `data-view="certificacoes"`, cartão com `data-nivel`). Asserções sobre conteúdo (rotas, certificações, `data-slug` de chips) ficam como estão. `TestPortalResponsivo` passa a verificar: menu vira gaveta em `max-width: 1023px`; `.grid` com `minmax(min(250px, 100%), 1fr)`.
- [ ] **Step 3: Rodar e ver falhar.**
- [ ] **Step 4: Implementar** a estrutura e o `index.css`, reproduzindo `mockup-portal.html`. O JavaScript do portal antigo (abas, filtros) sai neste passo; o novo entra em T10. Nesta task o catálogo renderiza agrupado por trilha no próprio HTML gerado, para funcionar mesmo sem JS.
- [ ] **Step 5: Rodar** `test_portal.py`, os testes de portal alterados e `test_filtro_secoes.py` (inalterado: os `data-slug` de chips e cartões das visões especiais continuam) → PASS.
- [ ] **Step 6: Commit** — `feat(portal): navegação lateral, catálogo como tela inicial e cartões novos`.

### Task 10: Comportamento do portal

**Files:**
- Modify: `_geradores/build_index.py` (bloco `portal_js`)
- Test: `_geradores/testes/test_portal_js.py`

**Interfaces:**
- Consumes: marcação de T9; `navegador.executar` (T4); chaves de `localStorage` das restrições globais.
- Produces (no `index.html`): gaveta do menu abaixo de 1024 px (botão `.menu-toggle` na barra superior alterna `body.menu-aberto` e `aria-expanded`; Esc e escolha de visão fecham e devolvem o foco); visões alternadas pelo menu (`hidden` nas demais; `aria-current` no item ativo; a visão vai para `location.hash` `#v-<view>` e é restaurada na carga); agrupar por trilha/nível/perfil/NIST (cabeçalho de grupo com `X de Y concluídos`); filtro "Só não concluídos"; busca em `data-busca` com atalho `/`; `.mc-status` = `✓ Concluído` | `◐ N% lido` | `○ Não iniciado`; `#continuar` a partir de `cs_last`; progresso global; marcar/desmarcar em "Meu progresso" grava `cs_done_<slug>`.

Status: concluído se `cs_done_<slug> === "true"`; senão em andamento se houver `cs_read_<slug>` não vazio, alguma `cs_check_<slug>_*` igual a `"true"` ou alguma `cs_quiz_<slug>_*`; `N = round(100 × lidas ÷ data-secoes)` (0 se `cs_read` ausente ou corrompido); senão não iniciado.

- [ ] **Step 1: Escrever os testes** (`skipUnless(CHROME)`, `executar(index_html, script, script_antes=…)`):

```python
def test_status_concluido_sem_leitura(self):
    r = executar(PORTAL, "__fim(document.querySelector('[data-slug=\"Threat-Hunting\"] .mc-status').textContent)",
                 script_antes="localStorage.setItem('cs_done_Threat-Hunting','true')")
    self.assertIn("Concluído", r["saida"])

def test_status_em_andamento_com_porcentagem(self):
    # cs_read_Threat-Hunting = ids das 3 primeiras seções de extrair_secoes(corpo de Threat-Hunting), data-secoes=6 → "50% lido"

def test_status_por_checklist_sem_leitura(self):
    # só cs_check_Threat-Hunting_chk-th-1 = "true" → "0% lido"

def test_cs_read_corrompido_conta_zero(self):
    # cs_read_Threat-Hunting = "{x" → erros == [] e "0% lido"

def test_continuar_estudando(self):
    # cs_last = {"slug":"Threat-Hunting","secao":"simulador","ts":1} → #continuar contém o título e "🧪 Laboratório"; sem cs_last → #continuar vazio/oculto

def test_agrupar_por_nivel(self):
    # clicar data-grupo="nivel" → cabeçalhos de grupo == rótulos de NIVEIS presentes, na ordem de NIVEIS

def test_so_pendentes_e_busca(self):
    # com cs_done de 1 módulo, marcar #so-pendentes → esse cartão some; busca "kubernetes" → só cartões cujo data-busca contém o termo

def test_trocar_visao_e_hash(self):
    # clicar data-view="rotas" → só section[data-view="rotas"] visível e location.hash == "#v-rotas"

def test_gaveta_do_menu_no_celular(self):
    # largura=400: clicar .menu-toggle → body.menu-aberto e aria-expanded="true"; Escape → fechada e foco no botão

def test_marcar_em_meu_progresso(self):
    # na visão progresso, marcar o checkbox de Threat-Hunting → cs_done_Threat-Hunting == "true" e status do cartão atualizado
```

- [ ] **Step 2: Rodar e ver falhar.**
- [ ] **Step 3: Implementar o JS do portal.**
- [ ] **Step 4: Rodar** `test_portal_js.py test_portal.py` → PASS. Regerar o portal (`./_geradores/gerar.sh portal`) e rodar `test_fumaca_navegador.py`.
- [ ] **Step 5: Commit** — `feat(portal): status por módulo, continuar estudando, agrupar, filtros e visões`.

---

## Fase 5 — Documentação e fechamento

### Task 11: Guia, README, `.gitignore` e verificação final

**Files:**
- Modify: `_geradores/GUIA-DO-AUTOR.md` (seções 2 e 3 → contrato da spec §3.1, componentes da §2.3, tipos e rótulos; seção 6, checklist de qualidade, inclui "passa no `contrato.validar_corpo`"), `README.md` (portal e navegação; "100% offline" agora inclui fontes; comando de testes), `.gitignore` (`.superpowers/brainstorm/` e `.superpowers/capturas/`)
- Test: `_geradores/testes/test_documentacao.py`

- [ ] **Step 1: Escrever o teste:**

```python
def test_guia_documenta_contrato(self):
    guia = GUIA.read_text(encoding="utf-8")
    for t in TIPOS:
        self.assertIn(f'data-tipo="{t}"', guia)
    for velho in ("hero-header", "section-tag", 'class="check-item"', "quiz-btn"):
        self.assertNotIn(velho, guia)

def test_gitignore(self):
    self.assertIn(".superpowers/brainstorm/", (ROOT / ".gitignore").read_text(encoding="utf-8"))
```

- [ ] **Step 2: Rodar e ver falhar. Step 3: Atualizar os documentos. Step 4: Rodar e ver passar.**
- [ ] **Step 5: Suíte completa** com teto de memória (restrições globais) → 0 falhas, 0 erros. Registre a contagem.
- [ ] **Step 6: Conferência visual final** — capturas dos 5 módulos da T8 e do portal, nos dois temas e a 400 px de largura, comparadas com os mockups. Sem rolagem horizontal da página a 400 px (`document.documentElement.scrollWidth <= 400` via `executar`).
- [ ] **Step 7: Commit** — `docs: guia do autor e README com o novo contrato e a navegação`.
