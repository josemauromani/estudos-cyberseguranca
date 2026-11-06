import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from contrato import (  # noqa: E402
    ROTULOS, TIPOS, ContratoInvalido, Secao, extrair_secoes, validar_corpo,
)

CORPO_VALIDO = """<!-- Estudo X -->
<article class="study-container" data-slug="x">
  <section class="study-section" id="s1" data-tipo="teoria">
    <h2>Conceitos &amp; Fundamentos</h2>
    <p>Texto.</p>
    <div class="callout tip"><p>Dica</p></div>
    <div class="callout warning"><p>Atenção</p></div>
  </section>
  <section class="study-section" id="s3" data-tipo="checklist">
    <h2>Checklist</h2>
    <ul class="checklist" data-checklist-slug="x">
      <li class="checklist-item"><input type="checkbox" id="c1"> <label for="c1">Um</label></li>
      <li class="checklist-item"><input type="checkbox" id="c2"> <label for="c2">Dois</label></li>
      <li class="checklist-item"><input type="checkbox" id="c3"> <label for="c3">Três</label></li>
    </ul>
  </section>
  <section class="study-section" id="s4" data-tipo="questoes">
    <h2>Questões</h2>
    <div class="quiz-item">
      <div class="quiz-question">P1?</div>
      <details class="quiz-details"><summary class="quiz-toggle">Ver</summary><div class="quiz-answer">R1</div></details>
    </div>
    <div class="quiz-item">
      <div class="quiz-question">P2?</div>
      <details class="quiz-details"><summary class="quiz-toggle">Ver</summary><div class="quiz-answer">R2</div></details>
    </div>
    <div class="quiz-item" data-formato="multipla">
      <div class="quiz-question">P3?</div>
      <button class="quiz-btn">A</button><button class="quiz-btn">B</button>
    </div>
  </section>
  <section class="study-section" id="s5" data-tipo="referencias">
    <h2>Referências</h2>
    <ul><li>Ref</li></ul>
  </section>
</article>
"""


def msgs(html):
    return validar_corpo(html, "X")


class TestContrato(unittest.TestCase):
    def test_constantes(self):
        self.assertEqual(TIPOS, ("teoria", "checklist", "questoes", "referencias"))
        self.assertEqual(ROTULOS["questoes"], ("❓", "Questões de concurso"))
        self.assertEqual(set(ROTULOS), set(TIPOS))

    def test_corpo_valido_sem_erros(self):
        self.assertEqual(validar_corpo(CORPO_VALIDO, "X"), [])

    def test_regra_1_dois_articles(self):
        html = CORPO_VALIDO + '<article class="study-container"></article>'
        self.assertTrue(any(e.startswith("X §1:") for e in msgs(html)))

    def test_regra_1_sem_article(self):
        self.assertTrue(any(e.startswith("X §1:") for e in msgs("<p>oi</p>")))

    def test_regra_1_article_nao_na_raiz(self):
        html = "<div>" + CORPO_VALIDO + "</div>"
        self.assertTrue(any(e.startswith("X §1:") for e in msgs(html)))

    def test_regra_2_tipo_invalido(self):
        erros = msgs(CORPO_VALIDO.replace('data-tipo="teoria"', 'data-tipo="teorico"', 1))
        self.assertIn('X §2: section#s1: data-tipo "teorico" inválido', erros)

    def test_regra_2_ordem_dos_atributos(self):
        html = CORPO_VALIDO.replace('<section class="study-section" id="s1" data-tipo="teoria">',
                                    '<section data-tipo="teoria" class="study-section" id="s1">')
        self.assertTrue(any(e.startswith("X §2: section#s1: ordem") for e in msgs(html)))

    def test_regra_2_filho_que_nao_e_secao(self):
        html = CORPO_VALIDO.replace("</article>", "<div>solto</div></article>")
        self.assertTrue(any(e.startswith("X §2:") and "div" in e for e in msgs(html)))

    def test_regra_2_sem_id(self):
        html = CORPO_VALIDO.replace(' id="s5"', "")
        self.assertIn("X §2: section (sem id): id ausente", msgs(html))

    def test_regra_2_laboratorio_invalido(self):
        lab = (
            '<section class="study-section" id="s2" data-tipo="laboratorio">'
            "<h2>Lab</h2><p>x</p></section>"
        )
        html = CORPO_VALIDO.replace("</article>", lab + "</article>")
        self.assertIn('X §2: section#s2: data-tipo "laboratorio" inválido', msgs(html))

    def test_regra_2_script_e_style_permitidos(self):
        script = ('<script>var h = \'<section class="study-section" id="x">\'; '
                  "var t = '<h2>';</script>")
        html = CORPO_VALIDO.replace("</article>", script + "<style>.a{color:red}</style></article>")
        self.assertEqual(msgs(html), [])
        self.assertEqual([s.id for s in extrair_secoes(html)], ["s1", "s3", "s4", "s5"])

    def test_regra_2_style_sozinho(self):
        html = CORPO_VALIDO.replace("</article>", "<style>.a{}</style></article>")
        self.assertEqual(msgs(html), [])

    def test_regra_2_div_continua_erro(self):
        html = CORPO_VALIDO.replace("</article>", "<div>x</div></article>")
        self.assertIn("X §2: article.study-container: filho div não é section.study-section", msgs(html))

    def test_regra_2_atributo_extra_nao_afeta_ordem(self):
        for novo in ('<section style="x" class="study-section" id="s1" data-tipo="teoria">',
                     '<section class="study-section" data-x="1" id="s1" data-tipo="teoria">',
                     '<section class="study-section" id="s1" data-tipo="teoria" style="x">'):
            html = CORPO_VALIDO.replace('<section class="study-section" id="s1" data-tipo="teoria">', novo)
            self.assertEqual(msgs(html), [], novo)

    def test_ids_duplicados(self):
        html = CORPO_VALIDO.replace('id="s5"', 'id="s1"')
        self.assertIn('X §2: section#s1: id duplicado', msgs(html))

    def test_regra_3_secao_sem_h2(self):
        html = CORPO_VALIDO.replace("<h2>Referências</h2>", "")
        self.assertIn("X §3: section#s5: sem h2", msgs(html))

    def test_regra_3_primeiro_titulo_nao_e_h2(self):
        html = CORPO_VALIDO.replace("<h2>Referências</h2>", "<h3>Ref</h3><h2>Referências</h2>")
        self.assertTrue(any(e.startswith("X §3: section#s5:") for e in msgs(html)))

    def test_regra_4_section_tag_proibido(self):
        html = CORPO_VALIDO.replace("<h2>", '<span class="section-tag">Seção 01</span><h2>', 1)
        self.assertTrue(any(e.startswith("X §4:") for e in msgs(html)))

    def test_regra_4_footer_e_hero_header(self):
        html = CORPO_VALIDO.replace("<p>Texto.</p>", "<footer>f</footer>")
        self.assertTrue(any(e.startswith("X §4:") and "footer" in e for e in msgs(html)))
        html = CORPO_VALIDO.replace("<p>Texto.</p>", '<div class="hero-header"></div>')
        self.assertTrue(any(e.startswith("X §4:") and "hero-header" in e for e in msgs(html)))

    def test_regra_5_falta_checklist(self):
        html = CORPO_VALIDO.replace('data-tipo="checklist"', 'data-tipo="teoria"')
        self.assertIn('X §5: corpo: falta seção do tipo "checklist"', msgs(html))

    def test_regra_5_falta_questoes(self):
        html = CORPO_VALIDO.replace('data-tipo="questoes"', 'data-tipo="teoria"')
        self.assertIn('X §5: corpo: falta seção do tipo "questoes"', msgs(html))

    def test_regra_5_falta_referencias(self):
        html = CORPO_VALIDO.replace('data-tipo="referencias"', 'data-tipo="teoria"')
        self.assertIn('X §5: corpo: falta seção do tipo "referencias"', msgs(html))

    def test_regra_6_checklist_sem_label_for(self):
        html = CORPO_VALIDO.replace('<label for="c2">', "<label>")
        erros = msgs(html)
        self.assertTrue(any(e.startswith("X §6: section#s3:") and "c2" in e for e in erros), erros)

    def test_regra_6_item_sem_input(self):
        html = CORPO_VALIDO.replace('<input type="checkbox" id="c3">', "")
        self.assertTrue(any(e.startswith("X §6: section#s3:") for e in msgs(html)))

    def test_regra_6_li_sem_classe(self):
        html = CORPO_VALIDO.replace('<li class="checklist-item"><input type="checkbox" id="c1">',
                                    '<li><input type="checkbox" id="c1">')
        self.assertTrue(any(e.startswith("X §6:") for e in msgs(html)))

    def test_regra_7_quiz_sem_details(self):
        html = CORPO_VALIDO.replace('<details class="quiz-details"><summary class="quiz-toggle">Ver</summary>'
                                    '<div class="quiz-answer">R1</div></details>', "", 1)
        self.assertTrue(any(e.startswith("X §7: section#s4:") for e in msgs(html)))

    def test_regra_7_sem_quiz_answer(self):
        html = CORPO_VALIDO.replace('<div class="quiz-answer">R1</div>', "", 1)
        self.assertTrue(any(e.startswith("X §7: section#s4:") for e in msgs(html)))

    def test_regra_7_multipla_sem_botoes(self):
        html = CORPO_VALIDO.replace('<button class="quiz-btn">A</button><button class="quiz-btn">B</button>', "")
        self.assertTrue(any(e.startswith("X §7: section#s4:") for e in msgs(html)))

    def test_regra_8_callout_sem_modificador(self):
        html = CORPO_VALIDO.replace('class="callout tip"', 'class="callout"')
        self.assertTrue(any(e.startswith("X §8: section#s1:") for e in msgs(html)))

    def test_extrair_secoes_ignora_aninhadas(self):
        html = CORPO_VALIDO.replace(
            "<p>Texto.</p>",
            '<p>Texto.</p><section class="study-section" id="interna" data-tipo="teoria"><h2>Interna</h2></section>',
            1,
        )
        secoes = extrair_secoes(html)
        self.assertEqual([s.id for s in secoes], ["s1", "s3", "s4", "s5"])
        self.assertEqual(secoes[0].titulo_html, "Conceitos &amp; Fundamentos")

    def test_titulo_html_cru(self):
        secoes = extrair_secoes(CORPO_VALIDO)
        self.assertEqual(secoes[0].titulo_html, "Conceitos &amp; Fundamentos")
        self.assertIsInstance(secoes[0], Secao)
        self.assertEqual(secoes[0].tipo, "teoria")

    def test_contagens(self):
        s = {x.tipo: x for x in extrair_secoes(CORPO_VALIDO)}
        self.assertEqual((s["checklist"].n_checklist, s["questoes"].n_questoes), (3, 3))
        self.assertEqual((s["teoria"].n_checklist, s["teoria"].n_questoes), (0, 0))

    def test_contrato_invalido(self):
        e = ContratoInvalido(["a", "b"])
        self.assertEqual(e.erros, ["a", "b"])
        self.assertEqual(str(e), "a\nb")


if __name__ == "__main__":
    unittest.main()
