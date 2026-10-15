# Competências da Vaga "Analista de SI" — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ampliar o catálogo de 28 para 33 módulos em 7 trilhas e acrescentar ao portal a "Rota por Vaga: Analista de Segurança da Informação" e a "Matriz de Certificações".

**Architecture:** Os dados ficam em `estudos.txt` e `index_dados.py`, que são a fonte única. `build_index.py` só lê esses dados e renderiza HTML estático. As partes do portal que hoje estão fixas (botões de trilha e carreira, `TOTAL_ESTUDOS`, meta description) passam a ser derivadas dos dados. Nenhum `*_body.html` é criado e nada é renumerado.

**Tech Stack:** Python 3 (stdlib, `unittest`), HTML e CSS estáticos, Bash (`gerar.sh`).

**Spec:** `docs/superpowers/specs/2026-10-15-competencias-vaga-analista-si-design.md`

## Global Constraints

- Todo texto de interface e documentação em pt-BR.
- Os números 01–28 e os slugs existentes não mudam. Os módulos 29–33 entram no **fim** de `estudos.txt`, na ordem da spec §2.2.
- Trilha 7: nome `Carreira & Formação`, cor `#DB2777` (claro) e `#F472B6` (escuro), token `--t7-rose`, `cor_nome` `"rose"`.
- Rótulo exato da carreira nova: `Analista de Segurança da Informação` (id `analista_si`, ícone `🎯`).
- Não criar `*_body.html` nem pastas de módulo para 29–33. Eles aparecem como **pendentes** no portal.
- Sem dependências novas. O portal continua estático e offline, e as seções novas não usam JS.
- Testes: `python3 -m unittest discover -s _geradores/testes -v` a partir da raiz do repositório. Conferir `free -h` antes e, com menos de 4 GB disponíveis, rodar só os arquivos de teste afetados.
- Toda mensagem de commit termina com `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Review Focus

1. **Filtro por trilha "7":** clicar no botão da Trilha 7 deve mostrar exatamente os cards 32 e 33. A comparação JS é `cardTrilha === valor`, então o botão precisa ter `data-value="7"`. Coberto pelo Task 2 (`test_botoes_trilha_gerados_de_TRILHAS`).
2. **Filtro de carreira por substring (`includes`):** um rótulo contido em outro faria cards errados aparecerem. Coberto pelo Task 3 (`test_carreiras_sem_substring`).
3. **Barra de progresso com 33 módulos:** um `TOTAL_ESTUDOS` fixo em 28 daria porcentagem errada (podendo passar de 100%) para quem já concluiu módulos. Coberto pelo Task 2 (`test_total_estudos_js_dinamico`).
4. **Rota com nenhum módulo principal disponível:** o contador deve mostrar "0 de 7" sem quebrar a renderização. Coberto pelo Task 4 (`test_contador_zero`).
5. **Matriz de certificações em largura de celular:** sem rolagem horizontal abaixo de 640 px. Coberto pelo Task 4 (`test_css_responsivo_certificacoes`) e pela checagem visual do Task 5.

---

### Task 1: Catálogo com 33 módulos e design system da Trilha 7

**Files:**
- Modify: `_geradores/estudos.txt` (cabeçalho; linhas de 18, 25 e 26; 5 linhas novas no fim)
- Modify: `_geradores/index_dados.py` (docstring; `TRILHAS[7]`; `ESTUDOS_DADOS` de 18, 25 e 26; 5 entradas novas no fim)
- Modify: `_geradores/base.css` (4 blocos de tema e `.badge-t7` após a linha 382)
- Modify: `_geradores/index.css` (4 blocos de tema e `.track-tile.t7` após a linha 683)
- Modify: `_geradores/montar.py:240` (texto de ajuda "1 a 7")
- Modify: `README.md` (tabela da grade com 33 linhas, títulos de 18, 25 e 26, "33 módulos / 7 trilhas" no topo e na linha 87)
- Test: `_geradores/testes/test_curriculo.py`, `_geradores/testes/test_index.py`, `_geradores/testes/test_cli.py`, `_geradores/testes/test_assets.py`

**Interfaces:**
- Produces:
  - `TRILHAS[7] = {"id": 7, "nome": "Carreira & Formação", "cor": "#DB2777", "cor_nome": "rose", "descricao": ...}`
  - os slugs `Protecao-de-Dados-e-Conteudo`, `Seguranca-de-Bancos-de-Dados`, `PCI-DSS`, `Ingles-Tecnico-Ciber` e `Certificacoes-e-Carreira` em `ESTUDOS_DADOS` e em `estudos.txt`
  - as classes CSS `.badge-t7` e `.track-tile.t7`

- [ ] **Step 1: Atualizar os testes existentes para a nova grade**

  - `test_curriculo.py`: `28` → `33` em `test_estudos_txt_contains_28_valid_entries`, renomeado para `..._33_...`; faixa de trilha `1 <= int(trilha) <= 7` com a mensagem "deve ser 1 a 7".
  - `test_index.py`:
    - `len(ESTUDOS_DADOS) == 33`, com o teste renomeado para `..._33_entries`;
    - `len(slugs_txt) == 33`;
    - `1 <= dados["trilha"] <= 7`;
    - `len(TRILHAS) == 7`, com o laço de ids em `range(1, 8)`;
    - `assertIn("33", conteudo)` e `assertIn("7", conteudo)` no teste do portal.
  - `test_cli.py`: `len(estudos_linhas) == 33`, com o teste renomeado para `test_readme_contains_all_33_studies`.
  - `test_assets.py`: acrescentar `"--t7-rose"` à lista de cores de trilha e trocar o comentário para "7 trilhas".

  Acrescentar a `test_index.py`:

  ```python
  def test_titulo_trilha_nist_coincidem_com_estudos_txt(self):
      for linha in self.estudos_txt.read_text(encoding="utf-8").splitlines():
          linha = linha.strip()
          if not linha or linha.startswith("#"):
              continue
          slug, titulo, _pasta, _arq, trilha, _cor, nist = [p.strip() for p in linha.split("|")]
          d = ESTUDOS_DADOS[slug]
          self.assertEqual(d["titulo"], titulo, slug)
          self.assertEqual(d["trilha"], int(trilha), slug)
          self.assertEqual(d["nist"], nist, slug)
  ```

  Acrescentar a `test_assets.py` (no `TestCase` que já lê `base.css`; ler `index.css` do mesmo jeito):

  ```python
  def test_trilha7_tokens_em_4_blocos(self):
      for nome in ("base.css", "index.css"):
          css = (GERADORES / nome).read_text(encoding="utf-8")
          self.assertEqual(css.count("--t7-rose:"), 4, nome)
      self.assertIn(".badge-t7", (GERADORES / "base.css").read_text(encoding="utf-8"))
      self.assertIn(".track-tile.t7", (GERADORES / "index.css").read_text(encoding="utf-8"))
  ```
  (Usar o nome de constante de diretório que `test_assets.py` já define; se não houver, `Path(__file__).resolve().parent.parent`.)

- [ ] **Step 2: Rodar os testes e confirmar que falham**

  Run: `for t in curriculo index cli assets; do python3 -m unittest discover -s _geradores/testes -p "test_$t.py" 2>&1 | tail -2; done`
  Expected: FAIL, com contagens 28 ≠ 33, 6 ≠ 7 e `--t7-rose` ausente.

- [ ] **Step 3: Atualizar `estudos.txt`**

  - Cabeçalho: `(33 Módulos)` e a linha `# 7 = Carreira & Formação (#DB2777)`.
  - Campo `titulo_curto`:
    - 18 → `Ciclo NIST SP 800-61 Rev. 2 e Rev. 3 (Contenção e Erradicação)`
    - 25 → `ISO 31000 e Avaliação Qualitativa vs Quantitativa (ALE/SLE)`
    - 26 → `SGSI, Anexo A, CIS Controls e NIST 800-53`
  - Acrescentar no fim as 5 linhas da spec §2.2, copiadas literalmente.

- [ ] **Step 4: Atualizar `index_dados.py`**

  - Docstring e comentários: "33 módulos", "7 Trilhas".
  - Acrescentar `TRILHAS[7]` (Interfaces), com `descricao` igual a "Inglês técnico, formação acadêmica, certificações e preparação para vagas de segurança."
  - Atualizar 18, 25 e 26:
    - `titulo` igual ao de `estudos.txt`;
    - `subtitulo`, `pergunta_chave` e `fatos` passam a citar o acréscimo da spec §2.3 (NIST SP 800-61 Rev. 3; processo ISO 31000:2018; CIS Controls v8.1 IG1/IG2/IG3 e NIST SP 800-53 Rev. 5).
  - Acrescentar as 5 entradas em `ESTUDOS_DADOS`. A tabela abaixo fixa os valores; os campos `subtitulo`, `pergunta_chave` e os 4 `fatos` (o último sempre nomeia o simulador) vêm dos Objetivos e Conceitos-chave da spec §2.2.

  | slug | trilha | nist | mitre | carreiras | tempo_minutos | simulador_nome |
  |---|---|---|---|---|---|---|
  | Protecao-de-Dados-e-Conteudo | 2 | `Protect / Detect` | `TA0010 Exfiltration (T1048, T1567) / T1566 Phishing` | Blue Team & Defesa, Operações SOC & Resposta, GRC & Auditoria | 50 | `Gateway de Conteúdo` |
  | Seguranca-de-Bancos-de-Dados | 2 | `Protect / Detect` | `T1190 Exploit Public-Facing Application / T1078 Valid Accounts / T1213 Data from Information Repositories` | Blue Team & Defesa, AppSec & DevSecOps, GRC & Auditoria | 50 | `Matriz GRANT/REVOKE` |
  | PCI-DSS | 6 | `Govern / Protect` | `TA0009 Collection / TA0010 Exfiltration` | GRC & Auditoria, Blue Team & Defesa | 45 | `Delimitador de Escopo CDE` |
  | Ingles-Tecnico-Ciber | 7 | `Protect` | `N/A (módulo de carreira)` | as 6 carreiras de `CARREIRAS` | 40 | `Leitor de Advisory` |
  | Certificacoes-e-Carreira | 7 | `Protect` | `N/A (módulo de carreira)` | as 6 carreiras de `CARREIRAS` | 35 | `Planejador de Certificações` |

  O `titulo` de cada entrada é o `titulo_curto` de `estudos.txt`. O rótulo "Analista de Segurança da Informação" **não** entra aqui; ele é acrescentado no Task 3.

- [ ] **Step 5: Tokens e classes da Trilha 7**

  - Em `base.css` e `index.css`, logo abaixo de cada declaração `--t6-amber:`, declarar `--t7-rose:`: `#DB2777` nos blocos claros (`:root` e `[data-theme="light"]`) e `#F472B6` nos escuros (`@media (prefers-color-scheme: dark)` e `[data-theme="dark"]`).
  - Trocar os comentários "6 Trilhas" por "7 Trilhas".
  - `base.css`: `.badge-t7 { background-color: rgba(219, 39, 119, 0.15); color: var(--t7-rose); }`
  - `index.css`: `.track-tile.t7 { background: var(--t7-rose); }`
  - `montar.py:240`: `"Número da trilha (1 a 7) ..."`.

- [ ] **Step 6: Atualizar o `README.md`**

  - "28 módulos" → "33 módulos" e "6 trilhas" → "7 trilhas" na linha 3, no título "Grade Curricular dos 33 Módulos" e na linha 87.
  - Títulos de 18, 25 e 26 iguais aos de `estudos.txt`.
  - Acrescentar à tabela as linhas 29–33 (colunas: #, slug, título, trilha, NIST, simulador), com a Trilha 7 escrita "Trilha 7: Carreira & Formação".

- [ ] **Step 7: Rodar os testes e confirmar que passam**

  Run: `free -h | head -2 && python3 -m unittest discover -s _geradores/testes -v 2>&1 | tail -5`
  Expected: `OK`. Se algum teste de portal falhar por "0 de 28" ou `TOTAL_ESTUDOS`, isso é escopo do Task 2; registre no ledger e siga, porque `assertIn("33")` já passa pela contagem do masthead.

- [ ] **Step 8: Commit**

  ```bash
  git add _geradores/estudos.txt _geradores/index_dados.py _geradores/base.css _geradores/index.css _geradores/montar.py README.md _geradores/testes/
  git commit -m "feat(curriculo): grade com 33 módulos e Trilha 7 Carreira & Formação

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

---

### Task 2: Portal derivado dos dados (filtros, totais e meta)

**Files:**
- Modify: `_geradores/build_index.py` (docstrings nas linhas 7 e 107; `TOTAL_ESTUDOS` na linha 286; meta na linha 475; texto de progresso na linha 540; painéis de filtro nas linhas 567–585; comentário na linha 616)
- Test: `_geradores/testes/test_index.py`

**Interfaces:**
- Consumes: `TRILHAS` com 7 chaves e `CARREIRAS` (Task 1).
- Produces:
  - `render_filtros_trilha(trilhas: Dict[int, dict]) -> str`
  - `render_filtros_carreira(carreiras: Dict[str, dict]) -> str`

  As duas retornam os `<button class="filter-badge" ...>` **incluindo** o botão inicial "Todas as Trilhas" / "Todos os Perfis" com `data-value="all"` e a classe `active`.

- [ ] **Step 1: Escrever os testes que falham**

  Em `test_index.py`, numa classe nova `TestPortalDerivado`:

  ```python
  def test_botoes_trilha_gerados_de_TRILHAS(self):
      html = render_filtros_trilha(TRILHAS)
      for tid, info in TRILHAS.items():
          self.assertIn(f'data-value="{tid}"', html)
          self.assertIn(f"Trilha {tid}: {escape(info['nome'])}", html)
      self.assertIn('data-value="all"', html)

  def test_botoes_carreira_gerados_de_CARREIRAS(self):
      html = render_filtros_carreira(CARREIRAS)
      for c in CARREIRAS.values():
          self.assertIn(f'data-value="{escape(c["nome"])}"', html)
          self.assertIn(c["icone"], html)

  def test_total_estudos_js_dinamico(self):
      conteudo = Path(gerar_index_html(output_path=OUT)).read_text(encoding="utf-8")
      self.assertIn(f"const TOTAL_ESTUDOS = {len(ESTUDOS_DADOS)};", conteudo)
      self.assertIn(f"0 de {len(ESTUDOS_DADOS)} concluídos", conteudo)
      self.assertNotIn("TOTAL_ESTUDOS = 28", conteudo)

  def test_meta_description_usa_contagens(self):
      conteudo = Path(gerar_index_html(output_path=OUT)).read_text(encoding="utf-8")
      self.assertIn(f"com {len(ESTUDOS_DADOS)} módulos temáticos, {len(TRILHAS)} trilhas", conteudo)
  ```
  `OUT` é a raiz `index.html`, igual ao padrão de `TestIndexGeracao`. `escape` é `html.escape`.

- [ ] **Step 2: Rodar e confirmar a falha**

  Run: `python3 -m unittest discover -s _geradores/testes -p "test_index.py" 2>&1 | tail -5`
  Expected: FAIL com `ImportError` de `render_filtros_trilha`.

- [ ] **Step 3: Implementar em `build_index.py`**

  - Criar `render_filtros_trilha` e `render_filtros_carreira`, que geram o mesmo markup dos botões fixos atuais. O rótulo de carreira é `f"{icone} {nome}"` com `nome` escapado.
  - Substituir os botões fixos dos painéis `trilhas` e `carreiras` por `{filtros_trilha_html}` e `{filtros_carreira_html}`, calculados em `gerar_index_html`. O painel NIST não muda.
  - `portal_js` não é f-string: trocar `28` por `__TOTAL_ESTUDOS__` e fazer `portal_js = portal_js.replace("__TOTAL_ESTUDOS__", str(stats["total_estudos"]))`.
  - Linha 540: `0 de {stats["total_estudos"]} concluídos (0%)`.
  - Meta: `... com {stats["total_estudos"]} módulos temáticos, {stats["total_trilhas"]} trilhas e simuladores ...`.
  - Docstrings e comentários sem "28".

- [ ] **Step 4: Rodar e confirmar que passa**

  Run: `python3 -m unittest discover -s _geradores/testes -p "test_index.py" 2>&1 | tail -3`
  Expected: `OK`.

- [ ] **Step 5: Commit**

  ```bash
  git add _geradores/build_index.py _geradores/testes/test_index.py
  git commit -m "refactor(portal): filtros de trilha/carreira e totais derivados dos dados

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

---

### Task 3: Dados da rota da vaga, das certificações e da carreira nova

**Files:**
- Modify: `_geradores/index_dados.py` (`CARREIRAS`, `NECESSIDADES`, campos `carreiras` de `ESTUDOS_DADOS`; novas `ROTA_VAGA` e `CERTIFICACOES` entre `NECESSIDADES` e `ESTUDOS_DADOS`)
- Create: `_geradores/testes/test_rota_vaga.py`

**Interfaces:**
- Consumes: os slugs de 29–33 (Task 1).
- Produces:
  - `ROTA_VAGA: List[Dict[str, Any]]` com chaves `id`, `competencia`, `texto_vaga`, `icone`, `principais: List[str]`, `apoio: List[str]`
  - `CERTIFICACOES: List[Dict[str, Any]]` com chaves `sigla`, `nome`, `orgao`, `foco`, `experiencia`, `modulos: List[str]`
  - `CARREIRAS["analista_si"]`
  - a constante `ROTULO_ANALISTA_SI = "Analista de Segurança da Informação"`

- [ ] **Step 1: Escrever `test_rota_vaga.py` com os testes que falham**

  ```python
  SLUGS = {l.split("|")[0].strip() for l in ESTUDOS_TXT.read_text(encoding="utf-8").splitlines()
           if l.strip() and not l.startswith("#")}

  class TestRotaVagaDados(unittest.TestCase):
      def test_slugs_existem_no_catalogo(self):
          for c in ROTA_VAGA:
              for s in c["principais"] + c["apoio"]:
                  self.assertIn(s, SLUGS, c["id"])
          for cert in CERTIFICACOES:
              for s in cert["modulos"]:
                  self.assertIn(s, SLUGS, cert["sigla"])

      def test_sete_competencias_com_principal(self):
          self.assertEqual([c["id"] for c in ROTA_VAGA],
              ["solucoes", "banco_dados", "ingles", "normas", "resposta_incidentes", "controles", "formacao"])
          for c in ROTA_VAGA:
              self.assertGreaterEqual(len(c["principais"]), 1, c["id"])

      def test_certificacoes_exatas(self):
          siglas = [c["sigla"] for c in CERTIFICACOES]
          self.assertEqual(sorted(siglas), sorted(["CEH", "CISM", "CISSP", "CCSP", "GSEC", "Security+"]))
          self.assertEqual(len(siglas), len(set(siglas)))

      def test_modulos_da_rota_tem_carreira_analista(self):
          for c in ROTA_VAGA:
              for s in c["principais"] + c["apoio"]:
                  self.assertIn(ROTULO_ANALISTA_SI, ESTUDOS_DADOS[s]["carreiras"], s)

      def test_carreiras_sem_substring(self):
          nomes = [c["nome"] for c in CARREIRAS.values()]
          for a in nomes:
              for b in nomes:
                  if a != b:
                      self.assertNotIn(a, b)

      def test_necessidades_novas(self):
          alvo = {"Protecao-de-Dados-e-Conteudo", "Seguranca-de-Bancos-de-Dados", "PCI-DSS",
                  "Ingles-Tecnico-Ciber", "Certificacoes-e-Carreira"}
          self.assertTrue(alvo <= {n["slug"] for n in NECESSIDADES})
  ```

- [ ] **Step 2: Rodar e confirmar a falha**

  Run: `python3 -m unittest discover -s _geradores/testes -p "test_rota_vaga.py" 2>&1 | tail -5`
  Expected: FAIL com `ImportError` de `ROTA_VAGA`.

- [ ] **Step 3: Implementar os dados em `index_dados.py`**

  - `ROTA_VAGA`: os 7 itens da tabela da spec §3.1, nessa ordem, com os slugs completos (05 = Segmentacao-e-Firewall, 06 = Hardening-Sistemas, 07 = Seguranca-de-Redes-Defesa, 08 = Arquitetura-Zero-Trust, 10 = Seguranca-em-Endpoints-EDR, 12 = OWASP-Top-10-Web, 15 = Engenharia-Social-e-Phishing, 16 = Operacoes-SOC-e-SIEM, 18 = Resposta-a-Incidentes, 19 = Forense-Digital, 25 = Gestao-de-Riscos-TI, 26 = ISO-27001-e-27002). O campo `texto_vaga` reproduz o texto original da spec §1. Ícones: 🧱, 🗄️, 🌍, 📜, 🚨, 🔐, 🎓.
  - `CERTIFICACOES`: as 6 linhas da spec §3.2, na ordem e com os textos dela. As colunas Módulos viram slugs.
  - `CARREIRAS["analista_si"]`: o bloco da spec §3.3. `ROTULO_ANALISTA_SI` é usado tanto aqui quanto nos `carreiras`.
  - Acrescentar `ROTULO_ANALISTA_SI` ao campo `carreiras` de 05, 06, 07, 08, 10, 12, 15, 16, 18, 19, 25, 26, 29, 30, 31, 32 e 33. É o conjunto exato de módulos citados na rota.
  - `NECESSIDADES`: acrescentar os 5 itens da spec §3.4, com texto, categoria e ícone literais.

- [ ] **Step 4: Rodar e confirmar que passa**

  Run: `python3 -m unittest discover -s _geradores/testes -p "test_*.py" 2>&1 | tail -3`
  Expected: `OK`. O botão da carreira nova já aparece pelo Task 2.

- [ ] **Step 5: Commit**

  ```bash
  git add _geradores/index_dados.py _geradores/testes/test_rota_vaga.py
  git commit -m "feat(portal): dados da rota da vaga Analista de SI, certificações e carreira

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

---

### Task 4: Seções "Rota por Vaga" e "Matriz de Certificações" no portal

**Files:**
- Modify: `_geradores/build_index.py` (importar `ROTA_VAGA` e `CERTIFICACOES`; duas funções novas; inserção depois de `#secao-necessidades`)
- Modify: `_geradores/index.css` (estilos das seções; regra em `@media (max-width: 640px)`)
- Test: `_geradores/testes/test_rota_vaga.py`

**Interfaces:**
- Consumes: `ROTA_VAGA`, `CERTIFICACOES` (Task 3); `status_map` de `calcular_estatisticas`, no formato `{slug: {"disponivel": bool, "caminho_relativo": str}}`; `catalogo` de `carregar_catalogo_estudos()`.
- Produces:
  - `render_chip_modulo(slug: str, status_map: Dict[str, dict], apoio: bool = False) -> str`
  - `render_rota_vaga(rota: List[dict], status_map: Dict[str, dict]) -> str`, que retorna a `<section id="secao-rota-vaga">` completa
  - `render_certificacoes(certs: List[dict], status_map: Dict[str, dict]) -> str`, que retorna a `<section id="secao-certificacoes">` completa

- [ ] **Step 1: Escrever os testes que falham** (classe `TestRotaVagaRender` em `test_rota_vaga.py`)

  ```python
  def _status(disponiveis):
      return {s: {"disponivel": s in disponiveis, "caminho_relativo": f"{s}/treinamento-{s.lower()}.html"}
              for s in SLUGS}

  def test_chip_disponivel_e_pendente(self):
      st = _status({"Segmentacao-e-Firewall"})
      self.assertIn('<a href="Segmentacao-e-Firewall/treinamento-segmentacao-e-firewall.html"',
                    render_chip_modulo("Segmentacao-e-Firewall", st))
      pend = render_chip_modulo("PCI-DSS", st)
      self.assertIn('aria-disabled="true"', pend)
      self.assertNotIn("<a ", pend)
      self.assertIn("31 · ", pend)  # número do módulo = posição em estudos.txt

  def test_contador_so_principais(self):
      # 15 é só apoio em "solucoes"; não pode contar
      html = render_rota_vaga(ROTA_VAGA, _status({"Engenharia-Social-e-Phishing"}))
      self.assertIn("0 de 7 competências com módulo disponível", html)
      html = render_rota_vaga(ROTA_VAGA, _status({"Segmentacao-e-Firewall", "Seguranca-de-Bancos-de-Dados"}))
      self.assertIn("2 de 7 competências com módulo disponível", html)

  def test_contador_zero(self):
      self.assertIn("0 de 7", render_rota_vaga(ROTA_VAGA, _status(set())))

  def test_certificacoes_render(self):
      html = render_certificacoes(CERTIFICACOES, _status(set()))
      for c in CERTIFICACOES:
          self.assertIn(escape(c["sigla"]), html)
      self.assertEqual(html.count('<tr class="cert-row"'), 6)
      self.assertIn("Confira os requisitos atuais no site oficial do órgão emissor", html)

  def test_portal_contem_secoes_na_ordem(self):
      conteudo = Path(gerar_index_html(output_path=ROOT / "index.html")).read_text(encoding="utf-8")
      i_nec = conteudo.index('id="secao-necessidades"')
      i_rota = conteudo.index('id="secao-rota-vaga"')
      i_cert = conteudo.index('id="secao-certificacoes"')
      i_cat = conteudo.index('id="secao-catalogo"')
      self.assertTrue(i_nec < i_rota < i_cert < i_cat)
      self.assertIn("Rota por Vaga: Analista de Segurança da Informação", conteudo)
      self.assertIn("Matriz de Certificações", conteudo)

  def test_css_responsivo_certificacoes(self):
      css = (GERADORES / "index.css").read_text(encoding="utf-8")
      bloco = css[css.index("@media (max-width: 640px)"):]
      self.assertIn(".cert-table", bloco)
  ```

- [ ] **Step 2: Rodar e confirmar a falha**

  Run: `python3 -m unittest discover -s _geradores/testes -p "test_rota_vaga.py" 2>&1 | tail -5`
  Expected: FAIL com `ImportError` de `render_chip_modulo`.

- [ ] **Step 3: Implementar em `build_index.py`**

  - **Chip:** texto `f"{NN:02d} · {titulo}"`, em que NN é a posição 1-based do slug na ordem do catálogo (`list(ESTUDOS_DADOS)` coincide com `estudos.txt`) e `titulo` é `ESTUDOS_DADOS[slug]["titulo"]` escapado.
    - Disponível: `<a href="{caminho_relativo}" class="vaga-chip{ ' apoio' se apoio}">`.
    - Pendente: `<span class="vaga-chip pendente{ apoio}" aria-disabled="true" title="Em construção">`.
  - **`render_rota_vaga`:**
    - `<h2>🎯 Rota por Vaga: Analista de Segurança da Informação</h2>`;
    - parágrafo `"{x} de 7 competências com módulo disponível"`, em que x conta as competências com algum principal `disponivel` (o 7 vem de `len(rota)`);
    - um `<article class="vaga-competencia">` por item, com ícone, `competencia`, `texto_vaga` em `<p class="vaga-texto">`, chips principais e depois chips de apoio.
  - **`render_certificacoes`:**
    - `<h2>🎓 Matriz de Certificações</h2>`;
    - `<table class="cert-table">` com cabeçalho Sigla, Órgão, Foco, Experiência e Módulos, e uma `<tr class="cert-row">` por certificação, com os chips em Módulos;
    - depois a nota `<p class="cert-nota">Confira os requisitos atuais no site oficial do órgão emissor.</p>`.
  - Em `gerar_index_html`, calcular os dois HTMLs com `stats["status_map"]` e inseri-los entre `</section>` de `#secao-necessidades` e o comentário do catálogo.

- [ ] **Step 4: CSS em `index.css`**

  Classes `.vaga-section`, `.vaga-competencia`, `.vaga-texto`, `.vaga-chip`, `.vaga-chip.apoio`, `.vaga-chip.pendente`, `.cert-table`, `.cert-nota`, todas com os tokens já existentes (`--surface`, `--rule`, `--ink`, `--muted`, `--t7-rose` para o acento). `.pendente` usa `opacity: .55; cursor: default`.

  Dentro do `@media (max-width: 640px)`: `.cert-table thead { display: none; }`, e `.cert-table tr` e `.cert-table td` com `display: block`, para empilhar como cards sem rolagem horizontal. Se `index.css` ainda não tiver um bloco 640 px, criar um no fim do arquivo.

- [ ] **Step 5: Rodar e confirmar que passa**

  Run: `free -h | head -2 && python3 -m unittest discover -s _geradores/testes -v 2>&1 | tail -3`
  Expected: `OK`.

- [ ] **Step 6: Commit**

  ```bash
  git add _geradores/build_index.py _geradores/index.css _geradores/testes/test_rota_vaga.py
  git commit -m "feat(portal): seções Rota por Vaga e Matriz de Certificações

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```

---

### Task 5: Documentação curricular, portal regenerado e verificação final

**Files:**
- Modify: `_geradores/CURRICULO.md`
- Modify: `README.md` (seção "Rota por Vaga" e perfil novo)
- Modify: `docs/superpowers/specs/2026-10-06-estudos-cyberseguranca-design.md` (nota no topo)
- Regenerate: `index.html`
- Test: `_geradores/testes/test_curriculo.py`

**Interfaces:**
- Consumes: tudo o que foi produzido nos Tasks 1 a 4.

- [ ] **Step 1: Escrever o teste que falha** (em `test_curriculo.py`)

  ```python
  def test_curriculo_cobre_33_modulos_e_rota(self):
      txt = self.curriculo_file.read_text(encoding="utf-8")
      for linha in self.estudos_file.read_text(encoding="utf-8").splitlines():
          if linha.strip() and not linha.startswith("#"):
              self.assertIn(linha.split("|")[0].strip(), txt)
      self.assertIn("Trilha 7: Carreira & Formação", txt)
      self.assertIn("Rota 6: Analista de Segurança da Informação", txt)
      self.assertIn("ISO 31000", txt)
      self.assertIn("CIS Controls v8.1", txt)
      self.assertIn("800-61 Rev. 3", txt)
  ```

- [ ] **Step 2: Rodar e confirmar a falha**

  Run: `python3 -m unittest discover -s _geradores/testes -p "test_curriculo.py" 2>&1 | tail -5`
  Expected: FAIL com `Protecao-de-Dados-e-Conteudo` ausente.

- [ ] **Step 3: Atualizar o `CURRICULO.md`**

  - §1: "33 módulos" e "7 trilhas"; acrescentar "Analista de Segurança da Informação" aos perfis.
  - §2: na tabela de trilhas, acrescentar a Trilha 7 (`#DB2777` (Rosa), foco da spec §2.1, módulos 32–33) e ajustar as colunas de módulos da T2 ("06 ao 10, 29, 30") e da T6 ("25 ao 28, 31").
  - §3:
    - Acrescentar `#### 29.` e `#### 30.` ao fim da seção da Trilha 2 e `#### 31.` ao fim da Trilha 6.
    - Criar `### Trilha 7: Carreira & Formação (`#DB2777`)` com `#### 32.` e `#### 33.`. Os campos seguem o formato dos módulos existentes (Título, Função NIST, Tempo/Carreiras, Objetivos, Pré-requisitos, Conceitos-Chave, Simulador), com o conteúdo da spec §2.2.
    - Reescrever os blocos 18, 25 e 26 com os títulos novos e os acréscimos da spec §2.3.
  - §4: substituir a tabela NIST pelos valores abaixo, recalculados de `estudos.txt`. Confira com o comando do Step 4.

    | Função | Qtde | Módulos |
    |---|---|---|
    | GOVERN | 4 | 25, 26, 27, 31 |
    | IDENTIFY | 6 | 01, 09, 11, 14, 17, 25 |
    | PROTECT | 22 | 02–10, 12, 13, 15, 21–24, 27, 29–33 |
    | DETECT | 9 | 02, 07, 10, 16, 17, 20, 24, 29, 30 |
    | RESPOND | 3 | 18, 19, 20 |
    | RECOVER | 1 | 28 |

  - §5: `6. **Rota 6: Analista de Segurança da Informação (vaga):**` com a sequência `01 -> 05 -> 07 -> 10 -> 29 -> 30 -> 06 -> 26 -> 25 -> 31 -> 18 -> 32 -> 33`, seguida de uma frase que remete à seção do portal.

- [ ] **Step 4: Conferir a tabela NIST**

  Run:
  ```bash
  python3 -I -c "
  import collections
  c=collections.defaultdict(list)
  for i,l in enumerate([x for x in open('_geradores/estudos.txt',encoding='utf-8') if x.strip() and not x.startswith('#')],1):
      for f in l.strip().split('|')[6].split(' / '): c[f].append(i)
  print({k:(len(v),v) for k,v in c.items()})"
  ```
  Expected: Govern 4, Identify 6, Protect 22, Detect 9, Respond 3, Recover 1, com os números da tabela.

- [ ] **Step 5: README e nota na spec original**

  - `README.md`:
    - nova seção `## 🎯 Rota por Vaga: Analista de Segurança da Informação` antes de "Como o Material é Gerado", com a tabela competência → módulos da spec §3.1 e uma linha sobre a Matriz de Certificações no portal;
    - em "Perfis de Carreira", o item "Analista de Segurança da Informação".
  - Spec de 2026-10-06, logo abaixo do cabeçalho: `> **Atualização 2026-10-15:** grade ampliada para 33 módulos / 7 trilhas — ver [2026-10-15-competencias-vaga-analista-si-design.md](2026-10-15-competencias-vaga-analista-si-design.md).`

- [ ] **Step 6: Regenerar e rodar a suíte inteira**

  Run: `free -h | head -2 && ./_geradores/gerar.sh todos && python3 -m unittest discover -s _geradores/testes -v 2>&1 | tail -3`
  Expected: os 11 módulos existentes compilam, o portal é gerado com mensagem de sucesso, e a suíte termina com `OK`.

- [ ] **Step 7: Checagem visual do `index.html`**

  Abrir `index.html` no navegador (`xdg-open index.html`, ou pela ferramenta de browser disponível) e confirmar:
  - o filtro "Trilha 7" mostra só os cards 32 e 33 (pendentes);
  - o filtro "🎯 Analista de Segurança da Informação" mostra 17 cards;
  - a rota da vaga mostra "1 de 7 competências com módulo disponível";
  - os chips de 05, 07 e 10 abrem os treinamentos;
  - a matriz de certificações empilha sem rolagem horizontal a 375 px;
  - os temas claro e escuro estão legíveis;
  - o console JS não tem erros.

  Se não houver ferramenta de browser, registrar no ledger que a checagem visual ficou para o usuário.

- [ ] **Step 8: Commit**

  ```bash
  git add _geradores/CURRICULO.md README.md docs/superpowers/specs/2026-10-06-estudos-cyberseguranca-design.md index.html _geradores/testes/test_curriculo.py
  git commit -m "docs(curriculo): módulos 29–33, Trilha 7, rota da vaga e portal regenerado

  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
  ```
