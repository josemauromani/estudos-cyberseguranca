"""Testes do chassi gerado pelo montar.py (barra, sumário, cabeçalho, seções, fim)."""

import re
import subprocess
import sys
import tempfile
import unittest
from html import escape
from pathlib import Path

TESTES = Path(__file__).resolve().parent
GERADORES = TESTES.parent
sys.path.insert(0, str(GERADORES))
sys.path.insert(0, str(TESTES))

from chassi import aplicar_cabecalhos_de_secao, info_modulo, inserir_fim, numerar_questoes  # noqa: E402
from contrato import extrair_secoes  # noqa: E402
from contrato import ContratoInvalido  # noqa: E402
from index_dados import ESTUDOS_DADOS  # noqa: E402
from montar import montar_treinamento  # noqa: E402
from navegador import CHROME, executar  # noqa: E402

SLUG = "Threat-Hunting"


def corpo_valido(titulo_secao="Fundamentos") -> str:
    return f"""<article class="study-container">
<section class="study-section" id="s1" data-tipo="teoria"><h2>{titulo_secao}</h2><p>Texto.</p></section>
<section class="study-section" id="s2" data-tipo="teoria"><h2>Mais teoria</h2><p>Texto.</p></section>
<section class="study-section" id="s4" data-tipo="checklist"><h2>Checklist final</h2>
<ul class="checklist"><li class="checklist-item"><input type="checkbox" id="c1"><label for="c1">Item 1</label></li>
<li class="checklist-item"><input type="checkbox" id="c2"><label for="c2">Item 2</label></li></ul></section>
<section class="study-section" id="s5" data-tipo="questoes"><h2>Questões</h2>
<div class="quiz-item"><div class="quiz-question">P1?</div><details class="quiz-details"><summary class="quiz-toggle">Ver</summary><div class="quiz-answer">R1</div></details></div>
<div class="quiz-item"><div class="quiz-question">P2?</div><details class="quiz-details"><summary class="quiz-toggle">Ver</summary><div class="quiz-answer">R2</div></details></div>
<div class="quiz-item"><div class="quiz-question">P3?</div><details class="quiz-details"><summary class="quiz-toggle">Ver</summary><div class="quiz-answer">R3</div></details></div>
</section>
<section class="study-section" id="s6" data-tipo="referencias"><h2>Referências</h2><ul><li>Ref</li></ul></section>
</article>"""


CORPO_INVALIDO = corpo_valido().replace('data-tipo="checklist"', 'data-tipo="teoria"')


def montar_fixture(slug, titulo_secao="Fundamentos", corpo=None) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        body = Path(tmp) / "fixture_body.html"
        body.write_text(corpo if corpo is not None else corpo_valido(titulo_secao), encoding="utf-8")
        saida = Path(tmp) / "saida.html"
        montar_treinamento(body, saida, meta={"slug": slug})
        return saida.read_text(encoding="utf-8")


class TestChassi(unittest.TestCase):
    def test_cabecalho_a_partir_dos_dados(self):
        html = montar_fixture(SLUG)
        d = ESTUDOS_DADOS[SLUG]
        self.assertIn(f"Estudo {list(ESTUDOS_DADOS).index(SLUG) + 1:02d}", html)
        self.assertIn(f"<h1>{escape(d['titulo'])}</h1>", html)
        self.assertIn(f"⏱ {d['tempo_minutos']} min", html)
        self.assertIn(f'<body data-slug="{SLUG}"', html)
        self.assertIn(f"de {len(ESTUDOS_DADOS)}", html)

    def test_sumario_um_item_por_secao(self):
        html = montar_fixture(SLUG)
        self.assertEqual(html.count('class="toc-item'), 5)
        for i in range(1, 6):
            self.assertIn(f"Seção {i} de 5", html)

    def test_roadmap_com_quantidades(self):
        html = montar_fixture(SLUG)
        self.assertIn("2 seções", html)
        self.assertIn("2 itens", html)
        self.assertIn("3 questões", html)

    def test_chassi_sem_legado(self):
        html = montar_fixture(SLUG)
        self.assertNotIn("study-footer", html)
        self.assertNotIn("top-nav", html)
        self.assertIn("✓ Concluir módulo", html)
        self.assertEqual(html.count('class="study-done"'), 1)
        self.assertEqual(html.count('class="study-pager"'), 1)

    def test_anterior_e_proximo_nas_pontas(self):
        primeiro, ultimo = list(ESTUDOS_DADOS)[0], list(ESTUDOS_DADOS)[-1]
        self.assertIsNone(info_modulo(primeiro).anterior)
        self.assertIsNone(info_modulo(ultimo).proximo)
        self.assertTrue(info_modulo(primeiro).proximo[2].startswith("../"))

    def test_titulo_com_entidade_nao_e_escapado_duas_vezes(self):
        html = montar_fixture(SLUG, titulo_secao="Caça &amp; ATT&amp;CK")
        self.assertIn("Caça &amp; ATT&amp;CK", html)
        self.assertNotIn("&amp;amp;", html)

    def test_questoes_numeradas(self):
        html = montar_fixture(SLUG)
        self.assertEqual(re.findall(r'data-q="(q\d+)"', html), ["q1", "q2", "q3"])

    def test_numerar_questoes_preserva_outros_atributos(self):
        saida = numerar_questoes('<div class="quiz-item" data-formato="multipla">x</div><div class="quiz-item">y</div>')
        self.assertIn('<div class="quiz-item" data-q="q1" data-formato="multipla">', saida)
        self.assertIn('<div class="quiz-item" data-q="q2">', saida)

    def test_corpo_invalido_aborta(self):
        with self.assertRaises(ContratoInvalido) as cm:
            montar_fixture(SLUG, corpo=CORPO_INVALIDO)
        self.assertTrue(any("§5" in e for e in cm.exception.erros))

    def test_cli_corpo_invalido_sai_com_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            body = Path(tmp) / "threat_hunting_body.html"
            body.write_text(CORPO_INVALIDO, encoding="utf-8")
            r = subprocess.run([sys.executable, str(GERADORES / "montar.py"), str(body), str(Path(tmp) / "o.html")],
                               capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        self.assertIn("§5", r.stderr)

    def test_numerar_ignora_script_classes_extras_e_data_q_anterior(self):
        corpo = (
            '<script>var t = \'<div class="quiz-item">falso</div>\';</script>'
            '<div class="quiz-item-foo">nao</div>'
            '<div data-q="velho" class="quiz-item extra">a</div>'
            '<div id="x" class="outra quiz-item" data-q="q9">b</div>'
        )
        saida = numerar_questoes(corpo)
        self.assertIn('<div class="quiz-item">falso</div>', saida)
        self.assertIn('<div class="quiz-item-foo">nao</div>', saida)
        self.assertIn('<div class="quiz-item extra" data-q="q1">a</div>', saida)
        self.assertIn('<div id="x" class="outra quiz-item" data-q="q2">b</div>', saida)
        self.assertEqual(saida.count("data-q="), 2)

    def test_cabecalho_h2_com_atributos_e_multilinha(self):
        corpo = corpo_valido().replace("<h2>Fundamentos</h2>", '<h2 class="x"\n id="h">Fundamentos\n e mais</h2>')
        saida = aplicar_cabecalhos_de_secao(corpo, extrair_secoes(corpo))
        self.assertIn('<span class="stype">📘 Teoria <small>· Seção 1 de 5</small></span><h2 class="x"\n id="h">Fundamentos\n e mais</h2></div>', saida)
        self.assertEqual(saida.count('class="shead"'), 5)

    def test_cabecalho_ignora_secao_em_script(self):
        corpo = corpo_valido().replace(
            "</article>", '<script>var h = \'<section class="study-section" id="x"><h2>fake</h2></section>\';</script></article>')
        saida = aplicar_cabecalhos_de_secao(corpo, extrair_secoes(corpo))
        self.assertEqual(saida.count('class="shead"'), 5)
        self.assertIn("Seção 5 de 5", saida)
        self.assertIn("<section class=\"study-section\" id=\"x\"><h2>fake</h2>", saida)

    def test_cabecalho_levanta_com_contagem_divergente(self):
        corpo = corpo_valido()
        with self.assertRaises(ValueError):
            aplicar_cabecalhos_de_secao(corpo, extrair_secoes(corpo)[:-1])

    def test_cabecalho_levanta_secao_sem_h2(self):
        corpo = corpo_valido().replace("<h2>Referências</h2>", "")
        with self.assertRaises(ValueError):
            aplicar_cabecalhos_de_secao(corpo, extrair_secoes(corpo))

    def test_keyerror_alheio_nao_vira_slug_sem_dados(self):
        with tempfile.TemporaryDirectory() as tmp:
            body = Path(tmp) / "threat_hunting_body.html"
            body.write_text(corpo_valido(), encoding="utf-8")
            r = subprocess.run(
                [sys.executable, "-c",
                 "import sys; sys.path.insert(0, %r); import montar; "
                 "montar.gerar_fim = lambda i: {}['x']; montar.main([%r, %r])"
                 % (str(GERADORES), str(body), str(Path(tmp) / "o.html"))],
                capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertNotIn("Slug sem dados", r.stderr)
        self.assertIn("KeyError", r.stderr)

    def test_cli_nao_aceita_trilha(self):
        r = subprocess.run([sys.executable, str(GERADORES / "montar.py"), "x", "--trilha", "1"],
                           capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("unrecognized", r.stderr)

    def test_slug_sem_dados(self):
        with self.assertRaisesRegex(KeyError, "Nao-Existe"):
            info_modulo("Nao-Existe")

    @unittest.skipUnless(CHROME, "Chrome ausente")
    def test_pagina_montada_funciona_com_base_js(self):
        html = montar_fixture(SLUG)
        r = executar(html, """
          setTimeout(() => __fim({itens: document.querySelectorAll('.toc-item').length,
            secoes: document.querySelectorAll('section.study-section').length}), 300);
        """)
        self.assertEqual(r["erros"], [])
        self.assertEqual(r["saida"]["itens"], 5)
        self.assertEqual(r["saida"]["itens"], r["saida"]["secoes"])


if __name__ == "__main__":
    unittest.main()


class TestInserirFim(unittest.TestCase):
    def test_script_com_fecha_section_nao_recebe_o_fim(self):
        corpo = (
            '<article class="study-container">\n'
            '<section class="study-section" id="s1" data-tipo="teoria"><h2>A</h2></section>\n'
            '<section class="study-section" id="s2" data-tipo="referencias"><h2>B</h2><p>x</p></section>\n'
            "</article>\n<script>var t = '</section>';</script>"
        )
        r = inserir_fim(corpo, "<!--FIM-->")
        self.assertLess(r.index("<!--FIM-->"), r.index("<script>"))
        ultima = r.index('id="s2"')
        self.assertGreater(r.index("<!--FIM-->"), ultima)
        self.assertLess(r.index("<!--FIM-->"), r.index("</section>", ultima))
