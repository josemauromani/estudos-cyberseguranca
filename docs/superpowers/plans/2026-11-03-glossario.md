# Glossário com tooltip nos módulos — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Cadastro único de verbetes (primeiro: HMAC), marcação automática dos termos no build dos módulos com tooltip acessível, e uma visão "📖 Glossário" no portal.

**Architecture:** `glossario_dados.py` guarda os verbetes; `glossario.py` valida os dados e marca os termos percorrendo o corpo com `html.parser` (só nós de texto). `montar.py` chama a marcação e embute um JSON com os verbetes usados; `base.js` mostra o popover. `build_index.py` renderiza a visão nova e calcula "Aparece em" com a mesma função de marcação.

**Tech Stack:** Python 3.12 (biblioteca padrão), JavaScript puro, CSS com tokens, `unittest`, Chrome headless via `testes/navegador.py`.

**Spec:** `docs/superpowers/specs/2026-11-03-glossario-design.md`

## Global Constraints

- Zero dependências novas: só a biblioteca padrão do Python; nada de CDN ou requisição externa nas páginas.
- Todo texto de interface, mensagem e documentação em pt-BR.
- Cores só por variáveis de `tokens.css` (`--ink`, `--muted`, `--surface`, `--rule`, `--accent`, `--accent-soft` etc.); `base.css` e `index.css` não declaram tokens.
- Campos de texto dos verbetes aceitam apenas `<strong>`, `<em>` e `<code>` como HTML.
- Testes rodam só os arquivos afetados, a partir da raiz: `python3 -m unittest discover -s _geradores/testes -p "<arquivo>" -v`. Antes de rodar suíte grande, conferir `free -h` (abaixo de ~4 GB disponíveis, só arquivos afetados). Suíte completa só na Task 7, dentro de `systemd-run --user --scope --quiet -p MemoryMax=4G -p MemorySwapMax=1G`.
- `GUIA-DO-AUTOR.md` não pode conter as strings `hero-header`, `section-tag`, `class="check-item"` nem `quiz-btn` (`test_documentacao.py`).
- Commits terminam com `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Build (HTML compilados) em commit separado do código.

## Review Focus

1. **Entidades HTML no texto** (`&amp;`, `&nbsp;`, `&#8212;`, `&lt;`): a marcação deve devolvê-las intactas, sem decodificar. `HTMLParser` decodifica por padrão (`convert_charrefs=True`), o que corromperia o texto. Teste na Task 2.
2. **Termo colado em pontuação** (`(HMAC)`, `HMAC,`, `HMAC.`, `assinaturas/HMAC`, início e fim do nó de texto): deve marcar. Teste na Task 2.
3. **Termo dentro de formatação inline** (`<strong>HMAC</strong>`, `<em>`): deve marcar, com o `dfn` dentro do `strong`. É o caso real da linha 114 do Estudo 01. Teste na Task 2.
4. **Tooltip num termo perto da borda direita, em tela de celular (360 px)**: o popover não pode sair da janela. Teste na Task 4.
5. **Hash para verbete inexistente** (`#v-glossario/nao-existe`): mostra a visão no topo, sem erro no console. Teste na Task 5.

---

### Task 1: Dados do glossário e validação

**Files:**
- Create: `_geradores/glossario_dados.py`
- Create: `_geradores/glossario.py` (só a parte de validação nesta task)
- Test: `_geradores/testes/test_glossario_dados.py`

**Interfaces:**
- Produces:
  - `glossario_dados.GLOSSARIO: list[dict]`, com os campos da tabela da spec (§1). `referencias` é `list[tuple[str, str]]` (rótulo, URL).
  - `glossario.GlossarioInvalido(Exception)` com atributo `erros: list[str]`.
  - `glossario.validar_glossario(verbetes: list[dict]) -> list[str]`: mensagens no formato `"glossario <id>: <campo>: <descrição>"`; lista vazia se tudo certo.
  - `glossario.carregar_glossario() -> list[dict]`: importa `GLOSSARIO`, valida e levanta `GlossarioInvalido` se houver erro.
  - `glossario.texto_sem_html(s: str) -> str`: remove as tags `strong`/`em`/`code`, mantendo o texto.

- [ ] **Step 1: Write the failing tests** em `test_glossario_dados.py`:
  - `test_glossario_real_valido`: `validar_glossario(GLOSSARIO) == []`.
  - `test_hmac_cadastrado`: o verbete `hmac` tem `termo == "HMAC"`, `categoria == "Criptografia"`, `sigla_de` começando com `"Hash-based Message Authentication Code"`, `variacoes == ["HMAC-SHA256", "HMAC-SHA1"]`, `relacionados == []`, e os rótulos de `referencias` são `["RFC 2104", "FIPS 198-1"]` com as URLs `https://www.rfc-editor.org/rfc/rfc2104` e `https://csrc.nist.gov/pubs/fips/198-1/final`.
  - `test_campos_obrigatorios`: verbete sem `significado` gera erro contendo `"significado"`.
  - `test_id_invalido_e_duplicado`: `"HMAC"` e `"hmac_x"` geram erro de formato; dois verbetes `"hmac"` geram erro de duplicado.
  - `test_relacionado_inexistente`: `relacionados=["nao-existe"]` gera erro contendo `"nao-existe"`.
  - `test_referencia_sem_https`: URL `http://x` gera erro.
  - `test_html_proibido`: `significado` com `<a href="x">` ou `<script>` gera erro; com `<strong>`, `<em>` e `<code>` não gera.
  - `test_campo_desconhecido`: chave `"pronuncia"` gera erro (evita erro de digitação silencioso).
  - `test_carregar_levanta`: com `GLOSSARIO` substituído por um inválido (`unittest.mock.patch`), `carregar_glossario()` levanta `GlossarioInvalido`.
  - `test_texto_sem_html`: `texto_sem_html("a <strong>b</strong> <code>c</code>") == "a b c"`.

- [ ] **Step 2: Run and confirm failure**
  Run: `python3 -m unittest discover -s _geradores/testes -p "test_glossario_dados.py" -v`
  Expected: ERROR (`ModuleNotFoundError: glossario_dados`).

- [ ] **Step 3: Write `glossario_dados.py`** com o verbete HMAC exatamente como na spec, §1 "Verbete inicial". `sigla_de`: `"Hash-based Message Authentication Code (Código de Autenticação de Mensagem baseado em Hash)"`. Nos textos de `explicacao` e `historico`, use `<code>` para HS256 e `<em>` para o título do artigo.

- [ ] **Step 4: Implement validação em `glossario.py`.** Campos permitidos: `id, termo, significado, sigla_de, termo_ingles, categoria, explicacao, historico, variacoes, relacionados, referencias`. Id: `^[a-z0-9]+(-[a-z0-9]+)*$`. HTML proibido: qualquer tag que não case `</?(strong|em|code)>`.

- [ ] **Step 5: Run and confirm pass** (mesmo comando). Expected: OK.

- [ ] **Step 6: Commit**
  ```bash
  git add _geradores/glossario_dados.py _geradores/glossario.py _geradores/testes/test_glossario_dados.py
  git commit -m "feat(glossario): cadastro de verbetes com validação e o verbete HMAC"
  ```

---

### Task 2: Marcação automática de termos

**Files:**
- Modify: `_geradores/glossario.py`
- Test: `_geradores/testes/test_glossario.py`

**Interfaces:**
- Consumes: `texto_sem_html` (Task 1).
- Produces: `glossario.marcar_termos(html: str, verbetes: list[dict]) -> tuple[str, list[str]]`. Devolve o HTML marcado e os ids usados, ordenados. Saída de cada marca:
  `<dfn class="glossario" data-termo="<id>" tabindex="0" title="<texto_sem_html(significado), escapado com quote=True>"><texto original></dfn>`

- [ ] **Step 1: Write the failing tests** em `test_glossario.py`. Use um verbete de teste `V = {"id": "hmac", "termo": "HMAC", "significado": "Código <strong>com</strong> chave.", "variacoes": ["HMAC-SHA256"]}` e um de palavra `P = {"id": "integridade", "termo": "Integridade", "significado": "Dado não alterado."}`. Auxiliar `sec(corpo, sid="s1")` gera `<section class="study-section" id="{sid}" data-tipo="teoria"><h2>T</h2>{corpo}</section>`.
  - `test_marca_primeira_ocorrencia_por_secao`: `sec("<p>HMAC e HMAC</p>") + sec("<p>HMAC</p>", "s2")` → exatamente 2 `<dfn`, uma por seção; ids `["hmac"]`.
  - `test_saida_exata`: `sec("<p>Use HMAC.</p>")` contém `<dfn class="glossario" data-termo="hmac" tabindex="0" title="Código com chave.">HMAC</dfn>.`
  - `test_contextos_ignorados`: para cada um de `<pre>HMAC</pre>`, `<code>HMAC</code>`, `<kbd>HMAC</kbd>`, `<samp>HMAC</samp>`, `<script>var a="HMAC"</script>`, `<style>/*HMAC*/</style>`, `<svg><text>HMAC</text></svg>`, `<textarea>HMAC</textarea>`, `<h3>HMAC</h3>`, `<a href="#">HMAC</a>`, `<button>HMAC</button>`, `<label>HMAC</label>`, `<div class="terminal-box x"><p>HMAC</p></div>`, `<pre class="mermaid">HMAC</pre>`: nenhuma `<dfn`, ids `[]`.
  - `test_ignorado_nao_consome_a_ocorrencia`: `sec("<code>HMAC</code><p>HMAC</p>")` → 1 `<dfn` (no `<p>`).
  - `test_atributo_nao_marca`: `sec('<p title="HMAC">x</p>')` → sem `<dfn`.
  - `test_fora_de_secao_nao_marca`: `"<p>HMAC</p>"` → sem `<dfn`.
  - `test_sigla_diferencia_caixa`: `sec("<p>hmac</p>")` → sem `<dfn`.
  - `test_palavra_nao_diferencia_caixa`: com `P`, `sec("<p>a integridade</p>")` → `<dfn …>integridade</dfn>` (texto original preservado).
  - `test_fronteira`: `HMACs`, `XHMAC`, `HMAC_x`, `pré-HMAC` não casam como HMAC (com verbete só `{"id":"hmac","termo":"HMAC","significado":"x"}`, sem variações; `HMAC-SHA1` também não casa).
  - `test_variacao_mais_longa_vence`: com `V`, `sec("<p>HMAC-SHA256</p>")` → `<dfn …>HMAC-SHA256</dfn>`.
  - `test_pontuacao` *(Review Focus 2)*: em seções separadas, `(HMAC)`, `HMAC,`, `HMAC.`, `assinaturas/HMAC`, `HMAC` (nó inteiro) → cada uma marcada.
  - `test_dentro_de_formatacao` *(Review Focus 3)*: `sec("<p>use <strong>HMAC</strong></p>")` contém `<strong><dfn class="glossario"`.
  - `test_entidades_preservadas` *(Review Focus 1)*: `sec("<p>A &amp; B&nbsp;HMAC &#8212; &lt;x&gt;</p>")` → resultado sem `dfn` igual à entrada; o termo é marcado.
  - `test_ida_e_volta`: para o corpo real `fundamentos_ciber_body.html`, remover `<dfn[^>]*>` e `</dfn>` do resultado devolve a entrada byte a byte; ids `["hmac"]`.
  - `test_estudo_01`: no corpo real, as marcas não aparecem dentro de `<button` nem de `<script` (conferir que todo `<dfn` está fora desses trechos) e existe ao menos uma.

- [ ] **Step 2: Run and confirm failure**
  Run: `python3 -m unittest discover -s _geradores/testes -p "test_glossario.py" -v`
  Expected: ERROR/FAIL (`marcar_termos` não existe).

- [ ] **Step 3: Implement `marcar_termos`** como subclasse de `HTMLParser(convert_charrefs=False)` que reemite a entrada:
  - Tags: reemitir `self.get_starttag_text()` e o texto bruto da tag de fechamento. Entidades (`handle_entityref`, `handle_charref`), comentários, `decl`, `pi` e `unknown_decl` são reemitidos sem mudança. `handle_startendtag` reemite sem empilhar; elementos vazios (`br, img, input, hr, meta, link, source, wbr, col, area, base, embed, param, track`) não entram na pilha.
  - Pilha de elementos abertos; no fechamento, desempilhar até a tag correspondente. Contexto ignorado = há na pilha uma tag da lista da spec ou um elemento com classe `terminal-box` ou `mermaid`.
  - Ao abrir `section` com classe `study-section`, zerar o conjunto de ids já marcados na seção; fora de seção, não marcar.
  - Casamento em `handle_data`: um único regex com todas as formas (termo + variações) ordenadas da mais longa para a mais curta. Sigla (sem minúscula) entra literal; palavra entra como `(?i:…)`. Envolver com `(?<![\w-])` e `(?![\w-])`. Mapear o trecho casado de volta ao id por dicionário (exato para siglas, `casefold()` para palavras). Uma ocorrência só é marcada se o id ainda não foi usado na seção.
  - Entidades quebram o texto em vários `handle_data`; isso é aceito (um termo nunca contém entidade).

- [ ] **Step 4: Run and confirm pass** (mesmo comando). Expected: OK.

- [ ] **Step 5: Commit**
  ```bash
  git add _geradores/glossario.py _geradores/testes/test_glossario.py
  git commit -m "feat(glossario): marcação automática dos termos no corpo do módulo"
  ```

---

### Task 3: Integração no build do módulo

**Files:**
- Modify: `_geradores/glossario.py` (função do bloco JSON)
- Modify: `_geradores/montar.py:176-185` (após `extrair_secoes`, antes de `processar_diagramas_html`) e o template (antes do `<script>` do `base.js`)
- Test: `_geradores/testes/test_glossario_modulo.py`

**Interfaces:**
- Consumes: `carregar_glossario`, `marcar_termos` (Tasks 1–2).
- Produces: `glossario.bloco_dados_glossario(ids: list[str], verbetes: list[dict]) -> str`. Devolve `""` se `ids` vazio; senão `<script type="application/json" id="glossario-dados">{json}</script>`, onde `json` é um objeto `{id: {"termo", "categoria", "sigla_de", "termo_ingles", "significado"}}` (chaves ausentes omitidas), `ensure_ascii=False`, com `<`, `>`, `&` trocados por `<`, `>`, `&`.
  O módulo compilado passa a ter o JSON imediatamente antes de `<!-- Scripts Interativos Embutidos -->`.

- [ ] **Step 1: Write the failing tests** em `test_glossario_modulo.py` (compilar com `montar_treinamento` num diretório temporário):
  - `test_estudo_01_tem_termo_e_json`: compilar `fundamentos_ciber_body.html`; o HTML contém `<dfn class="glossario" data-termo="hmac"`; o JSON de `#glossario-dados` decodifica para um dict com chaves `["hmac"]` e `significado` igual ao de `GLOSSARIO`.
  - `test_modulo_sem_termo_sem_json`: compilar `corpo_valido()` de `test_chassi` (sem HMAC) → `glossario-dados` ausente.
  - `test_json_escapado`: `bloco_dados_glossario(["x"], [{"id":"x","termo":"X","significado":"a</script>&b"}])` não contém `</script>` antes do fechamento final nem `&b`; `json.loads` do conteúdo devolve `"a</script>&b"`.
  - `test_glossario_invalido_aborta`: com `glossario_dados.GLOSSARIO` substituído por um verbete sem `significado` (`unittest.mock.patch`), `montar.main(["_geradores/fundamentos_ciber_body.html", "<tmp>/x.html"])` levanta `SystemExit` com código 1, e o stderr capturado (`contextlib.redirect_stderr`) contém `glossario `.

- [ ] **Step 2: Run and confirm failure**
  Run: `python3 -m unittest discover -s _geradores/testes -p "test_glossario_modulo.py" -v`
  Expected: FAIL.

- [ ] **Step 3: Implement** `bloco_dados_glossario`, a chamada em `montar_treinamento` e o tratamento de `GlossarioInvalido` em `main()` (imprimir cada erro em stderr, `sys.exit(1)`, como `ContratoInvalido`).

- [ ] **Step 4: Run and confirm pass**, mais as suítes vizinhas:
  Run: `python3 -m unittest discover -s _geradores/testes -p "test_glossario_modulo.py" -v && python3 -m unittest discover -s _geradores/testes -p "test_montar.py" && python3 -m unittest discover -s _geradores/testes -p "test_chassi.py"`
  Expected: OK nas três.

- [ ] **Step 5: Commit**
  ```bash
  git add _geradores/glossario.py _geradores/montar.py _geradores/testes/test_glossario_modulo.py
  git commit -m "feat(glossario): módulo compilado marca os termos e embute os verbetes usados"
  ```

---

### Task 4: Tooltip no módulo (`base.js` + `base.css`)

**Files:**
- Modify: `_geradores/base.js` (nova função `initGlossario`, chamada no fim de `init()`, exposta em `window.CS`)
- Modify: `_geradores/base.css` (seção nova "Glossário" no fim)
- Test: `_geradores/testes/test_glossario_js.py`

**Interfaces:**
- Consumes: `#glossario-dados` e `dfn.glossario[data-termo]` (Task 3).
- Produces: popover `div#glossario-pop.glossario-pop[role=tooltip]`, criado uma vez no `body`, com estes filhos (os testes dependem deles): `.glossario-pop-titulo` ("HMAC · Criptografia", sem " · " se não houver categoria), `.glossario-pop-sub` (sigla_de ou termo_ingles; ausente se nenhum dos dois), `.glossario-pop-texto` (significado, via `innerHTML`, pois o HTML é validado), `a.glossario-pop-link` ("Ver no glossário →", `href="../index.html#v-glossario/<id>"`). Visível = sem atributo `hidden`.

- [ ] **Step 1: Write the failing tests** em `test_glossario_js.py`, `@unittest.skipUnless(CHROME, ...)`. Em `setUpClass`, compilar `fundamentos_ciber_body.html` com `montar_treinamento` num diretório temporário e guardar o HTML. Todos os testes conferem `r["erros"] == []`.
  - `test_title_removido`: após a carga, o primeiro `dfn.glossario` não tem `title`.
  - `test_foco_abre_e_esc_fecha`: `d.focus()` → popover visível, `.glossario-pop-titulo` = `"HMAC · Criptografia"`, `.glossario-pop-texto` contém `"chave secreta"`, `d.getAttribute('aria-describedby') == 'glossario-pop'`, link termina em `index.html#v-glossario/hmac`. Disparar `keydown` `Tab` (sem Shift) no termo com o popover aberto → `document.activeElement` é o `a.glossario-pop-link`. Focar o termo de novo e disparar `keydown` `Escape` → popover oculto, `aria-describedby` ausente, `document.activeElement === d`.
  - `test_mouse_abre_com_atraso`: `mouseenter` no termo → oculto antes de 150 ms, visível após 200 ms (`setTimeout` dentro do script de teste; o harness usa `--virtual-time-budget`).
  - `test_toque_abre_e_fora_fecha`: `click` no termo → visível; `click` em `document.body` → oculto.
  - `test_borda_direita_no_celular` *(Review Focus 4)*: `largura=360`; posicionar o termo no extremo direito (`d.style.position='fixed'; d.style.right='0'; d.style.top='100px'`), focar; `getBoundingClientRect()` do popover tem `left >= 16` e `right <= innerWidth - 16`.
  - `test_vira_para_cima_sem_espaco`: termo com `position:fixed; bottom:0` → `popover.bottom <= termo.top`.
  - `test_sem_dados_nao_cria_popover`: página de `test_base_js.pagina_fixture()` → `#glossario-pop` não existe, sem erros.
  - Em `test_componentes_css.py`, acrescentar `test_glossario_estilizado`: `base.css` tem regras para `dfn.glossario`, `dfn.glossario:focus-visible` e `.glossario-pop`, e nenhuma cor hexadecimal dentro do bloco "Glossário".

- [ ] **Step 2: Run and confirm failure**
  Run: `python3 -m unittest discover -s _geradores/testes -p "test_glossario_js.py" -v`
  Expected: FAIL.

- [ ] **Step 3: Implement `initGlossario()`** conforme a spec §3. Tab no termo com o popover aberto leva o foco ao link (o popover fica no fim do `body`, então isso é feito por código); Shift+Tab no link devolve o foco ao termo; o popover fecha quando o foco sai do termo e do popover. Demais regras: atrasos de 150 ms (abrir) e 200 ms (fechar); popover continua aberto com o cursor sobre ele; posição abaixo do termo, ou acima se não couber, com margem lateral de 16 px. CSS: `dfn.glossario` com `font-style: normal`, `text-decoration: underline dotted`, `cursor: help`; `.glossario-pop` com `max-width: 22rem`, `position: fixed`, `z-index` acima da topbar, cores de token.

- [ ] **Step 4: Run and confirm pass**, mais as suítes vizinhas:
  Run: `python3 -m unittest discover -s _geradores/testes -p "test_glossario_js.py" -v && python3 -m unittest discover -s _geradores/testes -p "test_base_js.py" && python3 -m unittest discover -s _geradores/testes -p "test_componentes_css.py"`
  Expected: OK nas três.

- [ ] **Step 5: Commit**
  ```bash
  git add _geradores/base.js _geradores/base.css _geradores/testes/test_glossario_js.py _geradores/testes/test_componentes_css.py
  git commit -m "feat(glossario): tooltip acessível dos termos nos módulos"
  ```

---

### Task 5: Visão "Glossário" no portal

**Files:**
- Modify: `_geradores/build_index.py` (`VISOES`, nova `modulos_por_termo`, nova `render_glossario`, contagem no menu, seção da visão depois de "Meu progresso", `PORTAL_JS`)
- Modify: `_geradores/index.css` (estilos da visão)
- Modify: `_geradores/testes/test_portal.py` (docstring e listas de visões: sete, com `glossario` no fim)
- Test: `_geradores/testes/test_glossario_portal.py`

**Interfaces:**
- Consumes: `carregar_glossario`, `marcar_termos`, `texto_sem_html` (Tasks 1–2); `render_chip_modulo(slug, status_map)` e `corpo_do_modulo(slug)` já existentes.
- Produces:
  - `modulos_por_termo(verbetes: list[dict]) -> dict[str, list[str]]`: id → slugs, na ordem de `ESTUDOS_DADOS`, só módulos com corpo.
  - `render_glossario(verbetes: list[dict], aparece_em: dict[str, list[str]], status_map: dict) -> str`: conteúdo da visão. Marcação usada pelos testes e pelo JS: `input#busca-glossario[type=search]`; `nav.glossario-letras` com um `<a>` por letra A–Z (`href="#g-letra-<l>"` se houver verbete, senão `<span aria-disabled="true">`); `section.glossario-grupo[data-letra]` com `<h2 id="g-letra-<l>">`; `article.verbete#g-<id>[data-busca]`, em que `data-busca` = termo, sigla_de, termo_ingles, variações e `texto_sem_html(significado)` juntos, em minúsculas e sem acento; `p.glossario-vazio[hidden]` com "Nenhum termo encontrado". Rótulos dos campos em `<dt>`: Significado, Explicação, Histórico, Variações, Relacionados, Referências, Aparece em.

- [ ] **Step 1: Write the failing tests.** Em `test_glossario_portal.py`, gerar o portal com `gerar_index_html(output_path=<tmp>)`:
  - `test_menu_e_visao`: link `<a href="#v-glossario" data-view="glossario">📖 Glossário <span class="n">1</span></a>`; `<section class="view" data-view="glossario" hidden>`.
  - `test_verbete_hmac_completo`: `#g-hmac` contém, nesta ordem, `HMAC`, `Criptografia`, `Hash-based Message Authentication Code`, os `<dt>` Significado, Explicação, Histórico, Variações, Referências, Aparece em; não contém `<dt>Relacionados` nem `<dt>Termo em inglês` (vazios); links de referência com `target="_blank" rel="noopener"`.
  - `test_aparece_em_cinco_modulos`: `modulos_por_termo(GLOSSARIO)["hmac"]` é o conjunto `{"Fundamentos-Ciber", "Criptografia-Pratica", "Autenticacao-e-IAM", "Seguranca-em-APIs", "SOAR-e-Automacao-de-Resposta"}` (Active-Directory-Fundamentos só cita `RC4-HMAC`, que a regra de fronteira não casa) na ordem de `ESTUDOS_DADOS`; o cartão tem 5 chips `data-slug`.
  - `test_letras`: `H` é link para `#g-letra-h`; `A` é `span aria-disabled="true"`.
  - `test_ordem_ignora_acento`: `render_glossario` com termos "Ética", "Escopo" e "Exploit" ordena Escopo, Ética, Exploit, todos no grupo `E`.
  - `test_relacionado_vira_link`: dois verbetes fictícios com `relacionados` cruzados geram `href="#v-glossario/<outro>"`.
  - Browser (`@skipUnless(CHROME)`), todos com `erros == []`:
    - `test_hash_abre_verbete`: `script_antes="history.replaceState(null,'','#v-glossario/hmac')"` → visão `glossario` visível, `#g-hmac` com classe `destaque`, `#g-hmac` visível na janela.
    - `test_hash_inexistente` *(Review Focus 5)*: `#v-glossario/nao-existe` → visão visível, `scrollY == 0`.
    - `test_hash_antigo_continua`: `#v-rotas` ainda mostra a visão de rotas.
    - `test_busca`: digitar `autenticação` (com acento) em `#busca-glossario` e disparar `input` → `#g-hmac` visível e `.glossario-vazio` oculto; digitar `xyz` → `#g-hmac` e o grupo `H` ocultos, `.glossario-vazio` visível.
  - Em `test_portal.py`: `test_menu_com_seis_visoes` vira `test_menu_com_sete_visoes` (lista termina em `"progresso", "glossario"`), e `test_visoes_ocultas_com_hidden` passa a incluir `"glossario"` no fim.

- [ ] **Step 2: Run and confirm failure**
  Run: `python3 -m unittest discover -s _geradores/testes -p "test_glossario_portal.py" -v`
  Expected: FAIL.

- [ ] **Step 3: Implement.**
  - `gerar_index_html` obtém os verbetes com `carregar_glossario()`; `GlossarioInvalido` em `main()` imprime os erros no stderr e sai com código 1 (relacionado inexistente faz o build do portal falhar).
  - `VISOES` ganha `("glossario", "📖", "Glossário")` no fim; a contagem é `len(verbetes)`.
  - Ordenação e letra inicial: `unicodedata.normalize("NFD", termo)` sem marcas combinantes, `casefold()`.
  - `PORTAL_JS`: `visaoDoHash()` passa a separar `#v-<visao>/<ancora>`; após `mostrarVisao`, se a âncora existir como `#g-<ancora>`, rolar até ela (`scrollIntoView`) e aplicar `destaque` por 2 s; senão `scrollTo(0,0)`. Busca usa o `removerAcentos` existente sobre `data-busca`, esconde grupos sem verbete visível e alterna `.glossario-vazio`.
  - `index.css`: cartão `.verbete`, `.glossario-letras`, `.verbete.destaque` (fundo `--accent-soft`), só tokens.

- [ ] **Step 4: Run and confirm pass**, mais as suítes do portal:
  Run: `python3 -m unittest discover -s _geradores/testes -p "test_glossario_portal.py" -v && python3 -m unittest discover -s _geradores/testes -p "test_portal*.py" && python3 -m unittest discover -s _geradores/testes -p "test_index.py" && python3 -m unittest discover -s _geradores/testes -p "test_abas_certificacao_progresso.py"`
  Expected: OK em todas.

- [ ] **Step 5: Commit**
  ```bash
  git add _geradores/build_index.py _geradores/index.css _geradores/testes/test_glossario_portal.py _geradores/testes/test_portal.py
  git commit -m "feat(portal): visão Glossário com busca, índice por letra e módulos onde o termo aparece"
  ```

---

### Task 6: Documentação

**Files:**
- Modify: `_geradores/GUIA-DO-AUTOR.md` (seção nova "Glossário", depois da seção 3)
- Modify: `README.md:38-46` ("seis visões" → "sete visões" e um item **Glossário**)
- Modify: `_geradores/testes/test_documentacao.py`

- [ ] **Step 1: Write the failing tests** em `test_documentacao.py`:
  - `test_guia_documenta_glossario`: o guia contém `glossario_dados.py`, `marcar_termos`, `1ª ocorrência` e `por seção`.
  - `test_readme_cita_glossario`: o README contém `sete visões` e `**Glossário:**`, e não contém `seis visões`.

- [ ] **Step 2: Run and confirm failure**
  Run: `python3 -m unittest discover -s _geradores/testes -p "test_documentacao.py" -v`
  Expected: FAIL nos dois testes novos.

- [ ] **Step 3: Write the docs.** No guia: como cadastrar um verbete (campos obrigatórios e opcionais, HTML permitido), as regras de marcação (contextos ignorados, sigla × palavra, fronteira, 1ª ocorrência por seção), que o build falha com verbete inválido, e quando um termo merece entrar (sigla ou jargão que aparece em mais de um módulo ou que o texto não explica). Lembrar de rodar `./_geradores/gerar.sh todos` depois de cadastrar. No README: o item **Glossário:** descreve busca, índice por letra, histórico e os módulos onde o termo aparece, com o tooltip nos módulos.

- [ ] **Step 4: Run and confirm pass** (mesmo comando). Expected: OK.

- [ ] **Step 5: Commit**
  ```bash
  git add _geradores/GUIA-DO-AUTOR.md README.md _geradores/testes/test_documentacao.py
  git commit -m "docs(glossario): guia do autor e README com a visão Glossário"
  ```

---

### Task 7: Recompilação e verificação final

**Files:**
- Modify (gerados): os 60 `*/treinamento-*.html` e `index.html`

- [ ] **Step 1: Recompilar.**
  Run: `./_geradores/gerar.sh todos` (da raiz)
  Expected: `[OK]` para os 60 módulos e `[OK] index.html gerado com sucesso.`

- [ ] **Step 2: Conferir o alcance.**
  Run: `grep -l 'data-termo="hmac"' */treinamento-*.html | sort`
  Expected: exatamente os 5 arquivos de Fundamentos-Ciber, Criptografia-Pratica, Autenticacao-e-IAM, Seguranca-em-APIs e SOAR-e-Automacao-de-Resposta (Active-Directory-Fundamentos só cita `RC4-HMAC`).

- [ ] **Step 3: Suíte completa** (conferir `free -h` antes; com menos de ~4 GB disponíveis, rodar só os `test_glossario*.py`, `test_portal*.py`, `test_compilados_atualizados.py` e `test_documentacao.py`).
  Run: `systemd-run --user --scope --quiet -p MemoryMax=4G -p MemorySwapMax=1G python3 -m unittest discover -s _geradores/testes`
  Expected: `OK` (skips só por Chrome ausente são aceitáveis).

- [ ] **Step 4: Conferência visual no Estudo 01**, no navegador, nos temas claro e escuro: tooltip ao passar o mouse e ao focar com Tab sobre o HMAC; o link abre o portal no verbete. Registrar o resultado no `progress.md` do SDD.

- [ ] **Step 5: Commit do build**
  ```bash
  git add index.html */treinamento-*.html
  git commit -m "build: recompila portal e módulos com o glossário"
  ```

- [ ] **Step 6: Marcar a spec como aprovada e implementada** (`**Status:** Aprovada e implementada`) e fazer o commit `docs(spec): marca a spec do glossário como aprovada e implementada`.
