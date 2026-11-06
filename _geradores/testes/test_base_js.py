"""Testes de comportamento do base.js no Chrome headless, sobre uma página de fixture com o markup do chassi."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

TESTES = Path(__file__).resolve().parent
GERADORES = TESTES.parent
sys.path.insert(0, str(GERADORES))
sys.path.insert(0, str(TESTES))

from montar import carregar_css  # noqa: E402
from navegador import CHROME, executar  # noqa: E402

BASE_JS = GERADORES / "base.js"

ITENS_TOC = [
    ("s1", "teoria", "📘", "Teoria", "Fundamentos"),
    ("s2", "checklist", "☑️", "Checklist", "Checklist final"),
    ("s3", "questoes", "❓", "Questões de concurso", "Questões"),
    ("s4", "referencias", "📚", "Referências", "Referências"),
]


def _toc_itens() -> str:
    linhas = []
    for sid, tipo, icone, rotulo, titulo in ITENS_TOC:
        linhas.append(
            f'<li><a class="toc-item" href="#{sid}" data-tipo="{tipo}">'
            f'<span class="toc-icone">{icone}</span>'
            f'<span><span class="toc-tipo">{rotulo}</span><span class="toc-titulo">{titulo}</span></span>'
            f'<span class="toc-contador"></span></a></li>'
        )
    return "\n".join(linhas)


def _secao(sid: str, tipo: str, icone: str, rotulo: str, n: int, corpo: str) -> str:
    return (
        f'<section class="study-section" id="{sid}" data-tipo="{tipo}" style="min-height:1200px">\n'
        f'<div class="shead"><span class="stype">{icone} {rotulo} · Seção {n} de 4</span><h2>{rotulo}</h2></div>\n'
        f"{corpo}\n</section>"
    )


def _flashcard(qid: str, n: int) -> str:
    return (
        f'<div class="quiz-item" data-q="{qid}">'
        f'<div class="quiz-question"><strong>{n}.</strong> Pergunta {n}?</div>'
        '<details class="quiz-details"><summary class="quiz-toggle">Ver resposta explicada</summary>'
        f'<div class="quiz-answer"><p>Resposta {n}.</p></div></details></div>'
    )


def pagina_fixture() -> str:
    """Página completa (CSS + base.js) com o markup que o chassi (Task 6) vai gerar."""
    checklist = (
        '<ul class="checklist">'
        + "".join(
            f'<li class="checklist-item"><input type="checkbox" id="c{i}"><label for="c{i}">Item {i}</label></li>'
            for i in (1, 2, 3)
        )
        + "</ul>"
    )
    multipla = (
        '<div class="quiz-item" data-q="q3" data-formato="multipla">'
        '<div class="quiz-question"><strong>3.</strong> Qual alternativa?</div>'
        '<button class="quiz-btn" id="alt-errada" onclick="CS.checkQuiz(this, false, \'Errada.\')">A) errada</button>'
        '<button class="quiz-btn" id="alt-certa" onclick="CS.checkQuiz(this, true, \'Certa.\')">B) certa</button></div>'
    )
    secoes = [
        _secao("s1", "teoria", "📘", "Teoria", 1, "<p>Texto de teoria.</p>"),
        _secao("s2", "checklist", "☑️", "Checklist", 2, checklist),
        _secao("s3", "questoes", "❓", "Questões de concurso", 3, _flashcard("q1", 1) + _flashcard("q2", 2) + multipla),
        _secao("s4", "referencias", "📚", "Referências", 4, "<ul><li>Referência</li></ul>"),
    ]
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Fixture</title>
<style>
{carregar_css()}
html {{ scroll-behavior: auto; }}
</style>
</head>
<body data-slug="Teste">
<header class="topbar">
  <div class="topbar-in">
    <a class="nav-back" href="../index.html">← Painel</a>
    <span class="crumb">Trilha 1 · <b>Teste</b></span>
    <span class="tipo-atual"></span>
    <button class="theme-toggle-btn" type="button">Escuro</button>
    <button class="toc-toggle" type="button" aria-expanded="false" aria-controls="toc">☰ Sumário</button>
  </div>
  <div class="readbar"></div>
</header>
<div class="shell">
<aside class="toc" id="toc" aria-label="Sumário do módulo">
  <div class="toc-rotulo">Estudo 01 de 57</div>
  <div class="toc-modulo">Módulo de teste</div>
  <div class="toc-progresso">0%</div>
  <ol class="toc-lista">
{_toc_itens()}
  </ol>
  <div class="toc-pe">
    <button class="btn-concluir" type="button">✓ Concluir módulo</button>
    <div class="toc-nav"><a href="#">← Anterior</a><a href="#">Próximo →</a></div>
  </div>
</aside>
<main class="content">
{chr(10).join(secoes)}
</main>
</div>
<script>
{BASE_JS.read_text(encoding="utf-8")}
</script>
</body>
</html>
"""


@unittest.skipUnless(CHROME, "Chrome ausente")
class TestBaseJs(unittest.TestCase):
    def test_sem_erros_na_carga(self):
        r = executar(pagina_fixture(), "__fim(1)")
        self.assertEqual(r["erros"], [])

    SCRIPT_PASSO = """
          const ir = (id) => { document.getElementById(id).scrollIntoView(); window.dispatchEvent(new Event('scroll')); };
          const lidas = () => JSON.parse(localStorage.getItem('cs_read_Teste'));
    """

    def test_secao_atual_e_leitura(self):
        r = executar(pagina_fixture(), self.SCRIPT_PASSO + """
          ['s1', 's2', 's3'].forEach(ir);
          setTimeout(() => __fim({on: document.querySelector('.toc-item.on').getAttribute('href'),
            atual: document.querySelector('.toc-item.on').getAttribute('aria-current'),
            tipo: document.querySelector('.tipo-atual').textContent,
            lidas: lidas(),
            pct: document.querySelector('.toc-progresso').textContent,
            lida: document.querySelector('a[href="#s1"]').classList.contains('lida'),
            barra: document.querySelector('.toc-progresso').style.getPropertyValue('--progresso')}), 300);""")
        self.assertEqual(r["saida"]["on"], "#s3")
        self.assertEqual(r["saida"]["atual"], "true")
        self.assertIn("Questões", r["saida"]["tipo"])
        self.assertEqual(r["saida"]["lidas"][:2], ["s1", "s2"])
        self.assertTrue(r["saida"]["lida"])
        self.assertEqual(r["saida"]["pct"], "50%")
        self.assertEqual(r["saida"]["barra"], "50%")

    def test_rolagem_sequencial_ate_o_fim_marca_tudo(self):
        r = executar(pagina_fixture(), self.SCRIPT_PASSO + """
          ['s1', 's2', 's3', 's4'].forEach(ir);
          window.scrollTo(0, document.documentElement.scrollHeight); window.dispatchEvent(new Event('scroll'));
          setTimeout(() => __fim({lidas: lidas(),
            pronto: document.querySelector('.btn-concluir').classList.contains('pronto')}), 300);""")
        self.assertEqual(r["saida"]["lidas"], ["s1", "s2", "s3", "s4"])
        self.assertTrue(r["saida"]["pronto"])

    def test_salto_do_sumario_nao_marca_secoes_puladas(self):
        r = executar(pagina_fixture(), self.SCRIPT_PASSO + """
          ir('s1'); ir('s4');
          window.scrollTo(0, document.documentElement.scrollHeight); window.dispatchEvent(new Event('scroll'));
          setTimeout(() => __fim({lidas: lidas(),
            pronto: document.querySelector('.btn-concluir').classList.contains('pronto')}), 300);""")
        self.assertEqual(r["saida"]["lidas"], ["s1", "s4"])
        self.assertFalse(r["saida"]["pronto"])

    def test_salto_so_conta_secoes_que_foram_atuais(self):
        r = executar(pagina_fixture(), self.SCRIPT_PASSO + """
          ir('s1'); ir('s3'); ir('s4');
          setTimeout(() => __fim({lidas: lidas()}), 300);""")
        self.assertNotIn("s2", r["saida"]["lidas"])
        self.assertIn("s3", r["saida"]["lidas"])
        # Seção atual ainda não entra em cs_read até sair dela.
        self.assertEqual(r["saida"]["lidas"], ["s1", "s3"])

    def test_initchecklist_ignora_argumento_com_data_slug(self):
        r = executar(pagina_fixture(), """
          initChecklist('outro-slug');
          const cb = document.getElementById('c1'); cb.checked = true; cb.dispatchEvent(new Event('change', {bubbles: true}));
          __fim({certo: localStorage.getItem('cs_check_Teste_c1'), errado: localStorage.getItem('cs_check_outro-slug_c1')});""")
        self.assertEqual(r["erros"], [])
        self.assertEqual(r["saida"], {"certo": "true", "errado": None})

    def test_checklist_salva_e_restaura(self):
        with tempfile.TemporaryDirectory() as perfil:
            executar(pagina_fixture(), "document.querySelector('#c2').click(); __fim(1)", perfil=Path(perfil))
            r = executar(pagina_fixture(), """__fim({marcado: document.querySelector('#c2').checked,
                cab: document.querySelector('.checklist-head').textContent,
                cnt: document.querySelector('a[href="#s2"] .toc-contador').textContent})""", perfil=Path(perfil))
        self.assertTrue(r["saida"]["marcado"])
        self.assertIn("1 de 3", r["saida"]["cab"])
        self.assertEqual(r["saida"]["cnt"], "1/3")

    def test_autoavaliacao_placar_e_filtro(self):
        r = executar(pagina_fixture(), """
          const d = document.querySelector('[data-q="q1"] details'); d.open = true; d.dispatchEvent(new Event('toggle'));
          document.querySelector('[data-q="q1"] .quiz-selfeval [data-v="errei"]').click();
          document.querySelector('.quiz-filtros [data-f="pendentes"]').click();
          __fim({res: document.querySelector('[data-q="q1"]').dataset.res,
                 chave: localStorage.getItem('cs_quiz_Teste_q1'),
                 visiveis: [...document.querySelectorAll('.quiz-item')].filter(q => q.offsetParent).length})""")
        self.assertEqual(r["saida"], {"res": "errei", "chave": "errei", "visiveis": 1})

    def test_contador_de_questoes_conta_acertos(self):
        r = executar(pagina_fixture(), """
          const d = document.querySelector('[data-q="q2"] details'); d.open = true; d.dispatchEvent(new Event('toggle'));
          document.querySelector('[data-q="q2"] .quiz-selfeval [data-v="acertei"]').click();
          __fim({cnt: document.querySelector('a[href="#s3"] .toc-contador').textContent,
                 placar: document.querySelector('.quiz-score').textContent})""")
        self.assertEqual(r["saida"]["cnt"], "1/3")
        self.assertIn("1", r["saida"]["placar"])

    def test_multipla_escolha_conta_primeiro_clique(self):
        r = executar(pagina_fixture(), """
          document.querySelector('#alt-errada').click(); document.querySelector('#alt-certa').click();
          __fim({res: document.querySelector('[data-q="q3"]').dataset.res,
                 chave: localStorage.getItem('cs_quiz_Teste_q3'),
                 cnt: document.querySelector('a[href="#s3"] .toc-contador').textContent})""")
        self.assertEqual(r["saida"], {"res": "errei", "chave": "errei", "cnt": "0/3"})

    def test_multipla_escolha_acerto(self):
        r = executar(pagina_fixture(), """
          document.querySelector('#alt-certa').click();
          __fim(localStorage.getItem('cs_quiz_Teste_q3'))""")
        self.assertEqual(r["saida"], "acertei")

    def test_concluir_alterna_cs_done(self):
        r = executar(pagina_fixture(), """
          const b = document.querySelector('.btn-concluir');
          b.click();
          const a = {v: localStorage.getItem('cs_done_Teste'), c: b.classList.contains('concluido')};
          b.click();
          __fim({a, v: localStorage.getItem('cs_done_Teste'), c: b.classList.contains('concluido')})""")
        self.assertEqual(r["saida"], {"a": {"v": "true", "c": True}, "v": "false", "c": False})

    def test_cs_last_registra_secao(self):
        r = executar(pagina_fixture(), """
          document.getElementById('s2').scrollIntoView(); window.dispatchEvent(new Event('scroll'));
          setTimeout(() => __fim(JSON.parse(localStorage.getItem('cs_last'))), 300);""")
        self.assertEqual(r["saida"]["slug"], "Teste")
        self.assertEqual(r["saida"]["secao"], "s2")
        self.assertIsInstance(r["saida"]["ts"], int)

    def test_cs_read_corrompido_nao_quebra(self):
        r = executar(pagina_fixture(), "__fim(1)", script_antes="localStorage.setItem('cs_read_Teste','{x')")
        self.assertEqual(r["erros"], [])

    def test_gaveta_no_celular(self):
        r = executar(pagina_fixture(), """
          const t = document.querySelector('.toc-toggle');
          t.click();
          const aberta = {c: document.body.classList.contains('toc-aberto'), e: t.getAttribute('aria-expanded')};
          document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape', bubbles: true}));
          __fim({aberta, c: document.body.classList.contains('toc-aberto'), e: t.getAttribute('aria-expanded'),
                 foco: document.activeElement === t})""", largura=400)
        self.assertEqual(r["saida"], {"aberta": {"c": True, "e": "true"}, "c": False, "e": "false", "foco": True})

    def test_gaveta_fecha_no_overlay_e_no_item(self):
        r = executar(pagina_fixture(), """
          const t = document.querySelector('.toc-toggle');
          t.click(); document.body.click();
          const porOverlay = !document.body.classList.contains('toc-aberto');
          t.click(); document.querySelector('.toc-item').click();
          const porItem = !document.body.classList.contains('toc-aberto');
          setTimeout(() => __fim({porOverlay, porItem, foco: document.activeElement === t}), 100)""", largura=400)
        self.assertEqual(r["saida"], {"porOverlay": True, "porItem": True, "foco": True})

    def test_teoria_sem_contador_de_progresso(self):
        r = executar(pagina_fixture(), "__fim(document.querySelector('a[href=\"#s1\"] .toc-contador').textContent)")
        self.assertEqual(r["saida"], "")

    def test_api_publica_preservada(self):
        nomes = ["CS", "toggleTheme", "initTheme", "initChecklist", "initQuiz", "checkQuiz", "copyCode", "isStudyDone",
                 "setStudyDone", "safeStorageGet", "safeStorageSet", "escapeHtml", "formatBytes", "formatNumber",
                 "bytesToHex", "hexToBytes", "sha256Hex"]
        r = executar(pagina_fixture(), f"__fim({json.dumps(nomes)}.filter(n => typeof window[n] === 'undefined'))")
        self.assertEqual(r["saida"], [])


if __name__ == "__main__":
    unittest.main()
