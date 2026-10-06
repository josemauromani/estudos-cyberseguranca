# Estudos de Cibersegurança: Infraestrutura e Módulo Piloto Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir a infraestrutura completa do pipeline `_geradores/`, o portal central responsivo `index.html` para os 28 módulos com duplo mapeamento NIST/MITRE, e implementar o estudo piloto completo `Fundamentos-Ciber` com o simulador interativo STRIDE.

**Architecture:** Pipeline em Python (biblioteca padrão) que compila corpos HTML individuais com `base.css` e `base.js` inlined para máxima portabilidade offline (zero dependências pesadas como LibreOffice). O construtor `build_index.py` consome metadados ricos em `index_dados.py` para gerar o portal `index.html` com filtros multifacetados e persistência de progresso em `localStorage`.

**Tech Stack:** Python 3 (standard library: `pathlib`, `re`, `json`, `sys`, `os`), HTML5 semântico, CSS3 moderno (Custom Properties, Flexbox, CSS Grid), JavaScript Vanilla (Web Crypto API, `localStorage`), Bash, `pytest`.

**Spec:** [`docs/superpowers/specs/2026-10-06-estudos-cyberseguranca-design.md`](file:///home/josemauro/projects/josemauro/estudos_cyberseguranca/docs/superpowers/specs/2026-10-06-estudos-cyberseguranca-design.md)

## Global Constraints

- Todos os textos, títulos, comentários e documentação em Português do Brasil (`pt-BR`).
- Treinamentos compilados devem ser arquivos HTML únicos e autocontidos (standalone), executáveis offline via protocolo `file:///` sem dependência de servidor HTTP local.
- Zero dependência externa de LibreOffice (`soffice`) ou bibliotecas pesadas de compilação.
- Todos os simuladores devem utilizar JavaScript puro (Vanilla JS), sem bibliotecas ou frameworks externos (React, Vue, jQuery).
- Todas as classes CSS e tokens visuais devem seguir o Design System baseado em `IBM Plex Sans`, `IBM Plex Mono` e `Barlow Semi Condensed`, com suporte total a modo claro e modo escuro.

## Review Focus

- **Navegação Offline / `file:///`**: Links relativos e caminhos de arquivos entre `index.html` raiz e `<Pasta>/treinamento-<slug>.html` devem funcionar tanto sob servidor web quanto via sistema de arquivos local.
- **Persistência de `localStorage`**: Namespaces de chaves de storage (`cs_check_*`, `cs_theme`, `cs_done_*`) devem ser prefixados para evitar colisões entre estudos e com outros sites.
- **Responsividade Mobile**: Tabelas de cabeçalhos, formulários de simuladores e grids de cards devem quebrar layout adequadamente em telas menores que 640px.
- **Metadados dos 28 Estudos**: Todos os 28 módulos definidos na especificação devem constar tanto em `estudos.txt` quanto em `index_dados.py` sem inconsistência de slugs ou nomes de pastas.
- **Simulador STRIDE do Piloto**: O canvas de modelagem deve permitir alternar entre componentes e categorias STRIDE com feedback imediato sem erros no console.

---

### Task 1: Catálogo, Matriz Curricular e Diretrizes Pedagógicas

**Files:**
- Create: `_geradores/estudos.txt`
- Create: `_geradores/CURRICULO.md`
- Create: `_geradores/GUIA-DO-AUTOR.md`
- Create: `_geradores/testes/test_curriculo.py`

**Interfaces:**
- Produces: `_geradores/estudos.txt` com exatamente 28 linhas no formato `slug|titulo_curto|pasta|arquivo_html|trilha_num|cor_tema|nist_fn`.

- [ ] **Step 1: Escrever teste de validação do currículo e catálogo**

```python
# _geradores/testes/test_curriculo.py
from pathlib import Path

def test_estudos_txt_contains_28_valid_entries():
    root = Path(__file__).resolve().parent.parent.parent
    estudos_file = root / "_geradores" / "estudos.txt"
    assert estudos_file.exists(), "estudos.txt deve existir"
    
    lines = [line.strip() for line in estudos_file.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")]
    assert len(lines) == 28, f"Esperava 28 estudos, encontrou {len(lines)}"
    
    slugs = set()
    for line in lines:
        parts = [p.strip() for p in line.split("|")]
        assert len(parts) == 7, f"Linha inválida: {line}"
        slug, titulo, pasta, arq, trilha, cor, nist = parts
        assert slug not in slugs, f"Slug duplicado: {slug}"
        slugs.add(slug)
        assert 1 <= int(trilha) <= 6, f"Trilha inválida em {slug}: {trilha}"
```

- [ ] **Step 2: Executar teste para verificar falha**

Run: `pytest _geradores/testes/test_curriculo.py -v`
Expected: FAIL (arquivo não existe)

- [ ] **Step 3: Criar `_geradores/estudos.txt`, `CURRICULO.md` e `GUIA-DO-AUTOR.md`**

Criar os 3 arquivos documentando a grade curricular completa de 28 módulos, objetivos e regras de autoria.

- [ ] **Step 4: Executar teste para verificar aprovação**

Run: `pytest _geradores/testes/test_curriculo.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add _geradores/estudos.txt _geradores/CURRICULO.md _geradores/GUIA-DO-AUTOR.md _geradores/testes/test_curriculo.py
git commit -m "feat(curriculo): catálogo dos 28 estudos, matriz pedagógica e guia do autor"
```

---

### Task 2: Design System e Scripts Base Compartilhados (`base.css` e `base.js`)

**Files:**
- Create: `_geradores/base.css`
- Create: `_geradores/base.js`
- Create: `_geradores/testes/test_assets.py`

**Interfaces:**
- Produces: `_geradores/base.css` (tokens de cores das 6 trilhas, tipografia, callouts, lab-box, terminal, quizzes, checklists).
- Produces: `_geradores/base.js` (funções `initChecklist()`, `initQuiz()`, `initTheme()`, `copyCode()`).

- [ ] **Step 1: Escrever teste de validação de `base.css` e `base.js`**

```python
# _geradores/testes/test_assets.py
from pathlib import Path

def test_base_css_contains_design_tokens():
    root = Path(__file__).resolve().parent.parent.parent
    css_file = root / "_geradores" / "base.css"
    assert css_file.exists()
    content = css_file.read_text(encoding="utf-8")
    assert "--ground" in content
    assert "--surface" in content
    assert "--ink" in content
    assert "--t1-blue" in content
    assert ".callout" in content
    assert ".lab-box" in content
    assert ".checklist" in content

def test_base_js_contains_core_functions():
    root = Path(__file__).resolve().parent.parent.parent
    js_file = root / "_geradores" / "base.js"
    assert js_file.exists()
    content = js_file.read_text(encoding="utf-8")
    assert "initChecklist" in content
    assert "initQuiz" in content
    assert "initTheme" in content
```

- [ ] **Step 2: Executar teste para verificar falha**

Run: `pytest _geradores/testes/test_assets.py -v`
Expected: FAIL

- [ ] **Step 3: Implementar `_geradores/base.css` e `_geradores/base.js`**

Implementar estilo visual refinado (Barlow / IBM Plex) com dark/light mode e scripts reativos Vanilla JS.

- [ ] **Step 4: Executar teste para verificar aprovação**

Run: `pytest _geradores/testes/test_assets.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add _geradores/base.css _geradores/base.js _geradores/testes/test_assets.py
git commit -m "feat(design-system): base.css com tokens de temas e base.js com utilitários interativos"
```

---

### Task 3: Compilador de Treinamentos Standalone (`montar.py`)

**Files:**
- Create: `_geradores/montar.py`
- Create: `_geradores/testes/test_montar.py`

**Interfaces:**
- Consumes: `_geradores/base.css`, `_geradores/base.js`
- Produces: `montar_treinamento(body_html_path: Path, output_path: Path, titulo: str, meta: dict) -> Path`

- [ ] **Step 1: Escrever teste para o compilador `montar.py`**

```python
# _geradores/testes/test_montar.py
from pathlib import Path
import tempfile
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from montar import montar_treinamento

def test_montar_treinamento_creates_standalone_html():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        body = tmp_path / "teste_body.html"
        body.write_text("<section><h1>Conteúdo de Teste</h1><p>Parágrafo de teste.</p></section>", encoding="utf-8")
        
        output = tmp_path / "treinamento-teste.html"
        res = montar_treinamento(body, output, titulo="Treinamento Teste", meta={"slug": "teste", "trilha": "1"})
        
        assert res.exists()
        content = res.read_text(encoding="utf-8")
        assert "<!DOCTYPE html>" in content
        assert "Treinamento Teste" in content
        assert "Conteúdo de Teste" in content
        assert "<style>" in content
        assert "<script>" in content
```

- [ ] **Step 2: Executar teste para verificar falha**

Run: `pytest _geradores/testes/test_montar.py -v`
Expected: FAIL

- [ ] **Step 3: Implementar `_geradores/montar.py`**

Construir o gerador que embute o shell HTML semântico com meta viewport, links para fontes do Google Fonts, inlining de `base.css` e `base.js`, breadcrumbs de navegação de volta para o `../index.html` e cabeçalho formal.

- [ ] **Step 4: Executar teste para verificar aprovação**

Run: `pytest _geradores/testes/test_montar.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add _geradores/montar.py _geradores/testes/test_montar.py
git commit -m "feat(compiler): script montar.py para compilação de treinamentos standalone"
```

---

### Task 4: Metadados Ricos e Construtor do Portal Central (`index_dados.py`, `index.css`, `build_index.py`)

**Files:**
- Create: `_geradores/index_dados.py`
- Create: `_geradores/index.css`
- Create: `_geradores/build_index.py`
- Create: `_geradores/testes/test_index.py`

**Interfaces:**
- Produces: `index.html` na raiz do projeto com catálogo dos 28 estudos, estatísticas, barra de progresso e filtros interativos.

- [ ] **Step 1: Escrever teste para `build_index.py`**

```python
# _geradores/testes/test_index.py
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from build_index import gerar_index_html
from index_dados import ESTUDOS_DADOS, TRILHAS

def test_dados_completeness():
    assert len(ESTUDOS_DADOS) == 28
    assert len(TRILHAS) == 6
    for slug, d in ESTUDOS_DADOS.items():
        assert "titulo" in d
        assert "nist" in d
        assert "pergunta_chave" in d
        assert "carreiras" in d
        assert "tempo_minutos" in d

def test_gerar_index_creates_valid_portal():
    root = Path(__file__).resolve().parent.parent.parent
    output_index = root / "index.html"
    gerar_index_html(output_path=output_index)
    assert output_index.exists()
    content = output_index.read_text(encoding="utf-8")
    assert "Estudos de Cibersegurança" in content
    assert "28" in content
    assert "STRIDE" in content
    assert "Escolha pela necessidade" in content
```

- [ ] **Step 2: Executar teste para verificar falha**

Run: `pytest _geradores/testes/test_index.py -v`
Expected: FAIL

- [ ] **Step 3: Implementar `index_dados.py`, `index.css` e `build_index.py`**

Escrever o catálogo completo de dados enriquecidos para os 28 estudos, estilizar o portal mestre e implementar a geração dinâmica do `index.html`.

- [ ] **Step 4: Executar teste para verificar aprovação**

Run: `pytest _geradores/testes/test_index.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add _geradores/index_dados.py _geradores/index.css _geradores/build_index.py _geradores/testes/test_index.py index.html
git commit -m "feat(portal): index_dados.py, index.css e build_index.py gerando index.html raiz"
```

---

### Task 5: Script CLI Mestre (`gerar.sh`) e Documentação Principal (`README.md`)

**Files:**
- Create: `_geradores/gerar.sh`
- Modify: `README.md`
- Create: `_geradores/testes/test_cli.py`

**Interfaces:**
- Produces: Executável `./_geradores/gerar.sh [todos | portal | <slug>]`.
- Produces: `README.md` com tabela dos 28 estudos, instruções de navegação e guia de uso dos geradores.

- [ ] **Step 1: Escrever teste para execução do CLI `gerar.sh`**

```python
# _geradores/testes/test_cli.py
from pathlib import Path
import subprocess

def test_gerar_sh_portal():
    root = Path(__file__).resolve().parent.parent.parent
    script = root / "_geradores" / "gerar.sh"
    assert script.exists()
    assert (script.stat().st_mode & 0o111) != 0, "gerar.sh deve ser executável"
    
    result = subprocess.run([str(script), "portal"], cwd=str(root), capture_output=True, text=True)
    assert result.returncode == 0
    assert "index.html gerado com sucesso" in result.stdout or "sucesso" in result.stdout.lower()
```

- [ ] **Step 2: Executar teste para verificar falha**

Run: `pytest _geradores/testes/test_cli.py -v`
Expected: FAIL

- [ ] **Step 3: Implementar `_geradores/gerar.sh` e `README.md`**

Criar o script bash mestre com permissão `chmod +x` e atualizar o `README.md` com a visão geral do projeto.

- [ ] **Step 4: Executar teste para verificar aprovação**

Run: `pytest _geradores/testes/test_cli.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add _geradores/gerar.sh README.md _geradores/testes/test_cli.py
git commit -m "feat(cli): gerar.sh mestre e README.md principal do repositório"
```

---

### Task 6: Módulo Piloto: `Fundamentos-Ciber` com Simulador STRIDE Interativo

**Files:**
- Create: `_geradores/fundamentos_ciber_body.html`
- Create: `Fundamentos-Ciber/treinamento-fundamentos-ciber.html` (via compilação)
- Create: `_geradores/testes/test_piloto.py`

**Interfaces:**
- Consumes: `_geradores/montar.py`, `_geradores/gerar.sh`
- Produces: `Fundamentos-Ciber/treinamento-fundamentos-ciber.html` completo, com teoria da Tríade CIA/STRIDE, simulador interativo STRIDE Canvas, checklist e quiz de fixação.

- [ ] **Step 1: Escrever teste de validação do módulo piloto**

```python
# _geradores/testes/test_piloto.py
from pathlib import Path

def test_fundamentos_ciber_treinamento_exists_and_complete():
    root = Path(__file__).resolve().parent.parent.parent
    piloto = root / "Fundamentos-Ciber" / "treinamento-fundamentos-ciber.html"
    assert piloto.exists(), "Treinamento do piloto deve existir"
    content = piloto.read_text(encoding="utf-8")
    
    # Teoria
    assert "Tríade CIA" in content
    assert "Confidencialidade" in content
    assert "Integridade" in content
    assert "Disponibilidade" in content
    
    # Simulador STRIDE
    assert "STRIDE Canvas" in content
    assert "Spoofing" in content
    assert "Tampering" in content
    assert "Repudiation" in content
    assert "Information Disclosure" in content
    assert "Denial of Service" in content
    assert "Elevation of Privilege" in content
    
    # Componentes pedagógicos
    assert "checklist" in content
    assert "quiz" in content
    assert "callout" in content
```

- [ ] **Step 2: Executar teste para verificar falha**

Run: `pytest _geradores/testes/test_piloto.py -v`
Expected: FAIL

- [ ] **Step 3: Escrever `_geradores/fundamentos_ciber_body.html` e compilar via `gerar.sh fundamentos-ciber`**

Elaborar o conteúdo didático aprofundado, o simulador STRIDE interativo em JS Vanilla, o checklist prático e as questões de fixação, gerando o arquivo final em `Fundamentos-Ciber/treinamento-fundamentos-ciber.html`.

- [ ] **Step 4: Executar teste para verificar aprovação**

Run: `pytest _geradores/testes/test_piloto.py -v`
Expected: PASS

- [ ] **Step 5: Atualizar portal e verificar integração ponta a ponta**

Run: `./_geradores/gerar.sh portal && pytest _geradores/testes/ -v`
Expected: Todos os testes passando e `index.html` apontando status "Disponível" para o estudo piloto.

- [ ] **Step 6: Commit**

```bash
git add _geradores/fundamentos_ciber_body.html Fundamentos-Ciber/treinamento-fundamentos-ciber.html _geradores/testes/test_piloto.py index.html
git commit -m "feat(estudo-01): módulo piloto Fundamentos-Ciber com simulador STRIDE interativo"
```
