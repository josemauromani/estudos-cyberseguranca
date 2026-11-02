import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from contrato import extrair_secoes, validar_corpo  # noqa: E402
import migrar_markup  # noqa: E402
from migrar_markup import (  # noqa: E402
    EXCECOES, cabecalho_legado, classificar, migrar, texto_visivel,
)

# G1: estrutura de fundamentos_ciber_body.html (main.container, hero-header,
# content-section, div.checklist > label.check-item, quiz-btn, callout-tip).
G1 = """<!-- ==========================================================================
     MÓDULO 01: FUNDAMENTOS-CIBER — CORPO DIDÁTICO E SIMULADOR STRIDE
     ========================================================================== -->

<main class="container">

  <!-- 1. CABEÇALHO HERO & METADADOS -->
  <header class="hero-header" style="--track-color: var(--t1-blue);">
    <div class="badge badge-t1">Trilha 1 &bull; Fundamentos &amp; Redes</div>
    <h1>Tríade CIA, Ameaças e Modelagem STRIDE</h1>
    <p class="hero-subtitle">Pilares da segurança da informação e metodologia STRIDE.</p>
    <div class="meta-bar">
      <span class="meta-item">⏱️ <strong>Tempo Estimado:</strong> 40 minutos</span>
      <span class="meta-item">🛡️ <strong>NIST CSF 2.0:</strong> Identify (ID.AM, ID.RA)</span>
      <span class="meta-item">🔬 <strong>MITRE ATT&amp;CK:</strong> TA0043 (Reconnaissance) &bull; TA0001 (Initial Access)</span>
    </div>
  </header>

  <!-- 2. FUNDAMENTAÇÃO TEÓRICA E ARQUITETURA -->
  <section class="content-section" id="fundamentacao-teorica">
    <h2>1. Introdução e Contexto Prático da Cibersegurança</h2>
    <p>
      Cibersegurança moderna não é um produto de software; é uma disciplina contínua de gerenciamento de risco.
    </p>

    <div class="callout callout-tip">
      <strong>💡 Fundamento Profissional:</strong>
      A segurança não busca eliminar 100% dos riscos.
    </div>
    <div class="callout callout-warning">
      <strong>⚠️ Atenção:</strong> Nem todo incidente é um ataque.
    </div>
    <div class="callout callout-danger">
      <strong>🚨 Risco:</strong> Credenciais vazadas.
    </div>
    <div class="callout callout-law">
      <strong>⚖️ LGPD:</strong> Art. 46.
    </div>
  </section>

  <!-- 4. LABORATÓRIO -->
  <section class="content-section" id="simulador-stride">
    <h2>3. Laboratório Interativo: STRIDE Canvas</h2>
    <div class="lab-box">
      <div class="lab-header">
        <h3>🧪 Simulador STRIDE Canvas</h3>
      </div>
    </div>
  </section>

  <!-- 5. CHECKLIST OPERACIONAL DE BOAS PRÁTICAS -->
  <section class="content-section" id="checklist-pratico">
    <h2>4. Checklist de Auditoria: Modelagem de Ameaças em Projetos Reais</h2>
    <p>
      O progresso é <strong>salvo automaticamente</strong> no seu navegador.
    </p>

    <div class="checklist" data-checklist-id="fundamentos-ciber">
      <h4>
        <span>Auditoria de Modelagem de Ameaças STRIDE</span>
        <span class="checklist-counter" style="font-size: 0.85rem; color: var(--muted); font-weight: normal;">0 de 2 itens auditados</span>
      </h4>
      <div class="checklist-progress-bar">
        <div class="checklist-progress-fill"></div>
      </div>

      <label class="check-item">
        <input type="checkbox" id="chk-fnd-1">
        <span><strong>1. Inventário de Ativos e Dados:</strong> Identificar e catalogar formalmente todos os ativos críticos.</span>
      </label>

      <label class="check-item">
        <input type="checkbox" id="chk-fnd-2">
        <span><strong>2. Fronteiras de Confiança (Trust Boundaries):</strong> Mapear visualmente no diagrama arquitetural.</span>
      </label>
    </div>
  </section>

  <!-- 6. QUIZ DE FIXAÇÃO E VALIDAÇÃO -->
  <section class="content-section" id="quiz-fixacao">
    <h2>5. Questões de Fixação e Concursos Públicos</h2>
    <div class="quiz-section">
      <!-- Questão 1 -->
      <div class="quiz-item" data-quiz-id="q1">
        <p class="quiz-question">
          <strong>Questão 1 (Tríade CIA &amp; DAD):</strong> Qual pilar foi violado?
        </p>
        <div class="quiz-options">
          <button class="quiz-btn" onclick="CS.checkQuiz(this, false, 'Incorreto.')">
            A) Confidencialidade.
          </button>
          <button class="quiz-btn" onclick="CS.checkQuiz(this, true, 'Correto!')">
            B) Disponibilidade.
          </button>
        </div>
        <div class="quiz-feedback" style="display: none;"></div>
      </div>
    </div>
  </section>

  <!-- 7. FATOS ESSENCIAIS, NORMAS E PRÓXIMOS PASSOS -->
  <section class="content-section" id="fatos-essenciais">
    <h2>6. Fatos Essenciais, Normas e Próximos Passos</h2>
    <div class="facts-grid">
      <div class="facts-card">
        <h4>📚 Tríade CIA &amp; Tríade DAD</h4>
        <p>Confidencialidade, Integridade e Disponibilidade.</p>
      </div>
    </div>
  </section>

</main>

<!-- JAVASCRIPT EXCLUSIVO DO SIMULADOR STRIDE CANVAS (VANILLA JS) -->
<script>
(function() {
  'use strict';
  document.querySelectorAll('.quiz-btn');
})();
</script>
"""

# G2: estrutura de arquitetura_zero_trust_body.html / redes_e_protocolos_body.html
# (header.study-header, section-title-wrap > section-num + h2, sem article,
# div.checklist > label.checklist-item sem id, quiz-item > details.quiz-answer).
G2 = """<!-- ==========================================================================
     Estudo 02: Redes e Protocolos
     ========================================================================== -->

<header class="study-header">
  <span class="study-track-kicker">Trilha 1: Fundamentos &amp; Redes Seguras &bull; Estudo 02</span>
  <h1 class="study-title">Redes e Protocolos</h1>
  <p class="study-lead">
    A cibersegurança operacional começa na camada de transporte e roteamento.
  </p>
  <div class="study-meta-bar">
    <span class="badge blue">NIST CSF 2.0: Protect (PR) &amp; Detect (DE)</span>
    <span class="badge slate">MITRE ATT&amp;CK: T1046, T1071, T1557</span>
    <span class="badge slate">Tempo Estimado: ~50 minutos</span>
  </div>
</header>

<!-- SEÇÃO 1: INTRODUÇÃO E MODELOS DE REDE -->
<section class="study-section" id="modelos-rede">
  <div class="section-title-wrap">
    <span class="section-num">01</span>
    <h2>Modelos de Rede, Camadas e Encapsulamento</h2>
  </div>

  <p>
    Para proteger ou investigar uma rede, o profissional de segurança deve visualizar como a informação transita.
  </p>

  <div class="callout tip">
    <h4>Dica</h4>
    <p>Encapsulamento é a chave.</p>
  </div>
</section>

<!-- SEÇÃO 3: LABORATÓRIO -->
<section class="study-section" id="laboratorio-inspetor">
  <div class="section-title-wrap">
    <span class="section-num">03</span>
    <h2>Laboratório Interativo: Inspetor Visual de Pacotes</h2>
  </div>

  <div class="lab-box" id="packet-inspector">
    <div class="lab-header">
      <h3>Inspetor de Pacotes &bull; Probe de Portas</h3>
    </div>
  </div>
</section>

<!-- SEÇÃO 6: CHECKLIST -->
<section class="study-section" id="checklist-zero-trust">
  <div class="section-title-wrap">
    <span class="section-num">06</span>
    <h2>Checklist de Aplicação Prática</h2>
  </div>

  <div class="checklist" id="checklist-arquitetura-zero-trust">
    <label class="checklist-item">
      <input type="checkbox" onchange="toggleCheckItem(this)">
      <span class="check-box"></span>
      <span class="check-text">
        <strong>Erradicação da Confiança Implícita:</strong>
        Dispositivos conectados à rede local não possuem privilégios adicionais.
      </span>
    </label>

    <label class="checklist-item">
      <input type="checkbox" onchange="toggleCheckItem(this)">
      <span class="check-box"></span>
      <span class="check-text">
        <strong>Adoção de ZTNA:</strong>
        O acesso remoto é baseado em ZTNA/SDP.
      </span>
    </label>
  </div>
</section>

<!-- SEÇÃO 7: QUESTÕES DE FIXAÇÃO E CONCURSOS -->
<section class="study-section" id="questoes-fixacao">
  <div class="section-title-wrap">
    <span class="section-num">07</span>
    <h2>Questões de Fixação e Concursos Públicos</h2>
  </div>

  <div class="quiz" id="quiz-arquitetura-zero-trust">
    <!-- Questão 1 -->
    <div class="quiz-item">
      <div class="quiz-question">
        <span class="quiz-badge">Questão 1 &bull; Componentes Lógicos do NIST SP 800-207</span>
        <p>
          Qual é a responsabilidade do Policy Enforcement Point (PEP)?
        </p>
      </div>
      <details class="quiz-answer">
        <summary>Ver resposta comentada</summary>
        <div class="quiz-explanation">
          <p>
            <strong>Gabarito: O PEP atua no Plano de Dados.</strong>
          </p>
        </div>
      </details>
    </div>
  </div>
</section>

<!-- SEÇÃO 8: FATOS ESSENCIAIS -->
<section class="study-section" id="fatos-essenciais">
  <div class="section-title-wrap">
    <span class="section-num">08</span>
    <h2>Fatos Essenciais e Conexões da Trilha</h2>
  </div>

  <div class="facts-grid">
    <div class="facts-card">
      <span class="facts-card-num">20 B</span>
      <span class="facts-card-label">Tamanho Base IPv4</span>
    </div>
  </div>
</section>

<!-- ==========================================================================
     SCRIPT DO LABORATÓRIO INTERATIVO (Vanilla JS puro & autônomo)
     ========================================================================== -->
<script>
(function() {
  'use strict';
})();
</script>
"""

# G2, variante de redes_e_protocolos/criptografia_pratica: div.checklist >
# div.checklist-header + ul.checklist-items, details.quiz-item > summary.quiz-summary,
# callout info.
G2B = """<header class="study-header">
  <span class="study-track-kicker">Trilha 1 &bull; Estudo 03</span>
  <h1 class="study-title">Criptografia Prática</h1>
  <p class="study-lead">A criptografia é a espinha dorsal.</p>
  <div class="study-meta-bar">
    <span class="badge slate">MITRE ATT&amp;CK: T1003</span>
  </div>
</header>

<!-- SEÇÃO 1 -->
<section class="study-section" id="pilares">
  <div class="section-title-wrap">
    <span class="section-num">01</span>
    <h2>Pilares</h2>
  </div>
  <div class="callout info">
    <h4>RSA vs Curvas Elípticas (ECC)</h4>
    <p>O RSA baseia sua segurança na fatoração.</p>
  </div>
</section>

<section class="study-section" id="lab">
  <div class="section-title-wrap">
    <span class="section-num">02</span>
    <h2>Laboratório</h2>
  </div>
  <div class="lab-box"><p>Simulador</p></div>
</section>

<section class="study-section" id="checklist-cripto">
  <div class="section-title-wrap">
    <span class="section-num">03</span>
    <h2>Checklist</h2>
  </div>

  <div class="checklist">
    <div class="checklist-header">
      <h3>Procedimento de Análise de Tráfego</h3>
      <div class="checklist-progress-bar"><div class="progress-fill" id="chk-progress"></div></div>
    </div>
    <ul class="checklist-items">
      <li class="checklist-item">
        <label>
          <input type="checkbox" id="chk-1">
          <span class="chk-label">
            <strong>1. Mapeamento de Camada 2:</strong>
            Verifique a tabela de vizinhos ARP (<code>arp -a</code>).
          </span>
        </label>
      </li>
      <li class="checklist-item">
        <label>
          <input type="checkbox" id="chk-2">
          <span class="chk-label">
            <strong>2. Flags TCP:</strong>
            Filtre por combinações ilegítimas de flags.
          </span>
        </label>
      </li>
    </ul>
  </div>
</section>

<section class="study-section" id="questoes-fixacao">
  <div class="section-title-wrap">
    <span class="section-num">04</span>
    <h2>Questões</h2>
  </div>

  <div class="quiz-container">
    <!-- Questão 1 -->
    <details class="quiz-item">
      <summary class="quiz-summary">
        <span class="quiz-tag">Questão 1 &bull; Pilha TCP/IP</span>
        <p class="quiz-question">
          Qual pacote o scanner envia após receber [SYN, ACK]?
        </p>
      </summary>
      <div class="quiz-answer">
        <div class="answer-badge correct">Resposta Correta: [RST].</div>
        <p>O scanner aborta a transação.</p>
      </div>
    </details>
  </div>
</section>

<section class="study-section" id="fatos">
  <div class="section-title-wrap">
    <span class="section-num">05</span>
    <h2>Fatos</h2>
  </div>
  <div class="facts-grid"><div class="facts-card">AES-256</div></div>
</section>

<script>
(function() {})();
</script>
"""

# G3: estrutura de threat_hunting_body.html (article.study-container,
# div.section-header > span.section-tag + h2).
G3 = """<!-- Estudo 47: Threat-Hunting Body Fragment -->
<article class="study-container" data-slug="threat-hunting">

    <!-- SEÇÃO 1: CAÇA POR HIPÓTESE -->
    <section class="study-section" id="intro">
        <div class="section-header">
            <span class="section-tag">Seção 01</span>
            <h2>Introdução: Nenhum Alerta Não Quer Dizer Nenhum Invasor</h2>
        </div>

        <p class="lead-text">
            Na segunda-feira, o SOC da Ipê Store recebeu um relatório de inteligência.
        </p>

        <div class="callout tip">
            <div class="callout-title">
                <span class="callout-icon">🔦</span>
                <strong>Caça por hipótese</strong>
            </div>
            <p>Comece por uma pergunta testável.</p>
        </div>
    </section>

    <section class="study-section" id="simulador">
        <div class="section-header">
            <span class="section-tag">Seção 03</span>
            <h2>Laboratório Prático: Caçada Guiada</h2>
        </div>

        <div class="lab-box th-lab" id="th-lab">
            <p>Painel</p>
        </div>
    </section>

    <section class="study-section" id="checklist">
        <div class="section-header">
            <span class="section-tag">Seção 04</span>
            <h2>Checklist de uma Caçada</h2>
        </div>

        <ul class="checklist" data-checklist-slug="threat-hunting">
            <li class="checklist-item">
                <input type="checkbox" id="chk-th-1">
                <label for="chk-th-1"><strong>Hipótese:</strong> escrita antes da busca.</label>
            </li>
            <li class="checklist-item">
                <input type="checkbox" id="chk-th-2">
                <label for="chk-th-2"><strong>Visibilidade:</strong> a fonte enxerga o comportamento.</label>
            </li>
        </ul>
    </section>

    <section class="study-section" id="quiz">
        <div class="section-header">
            <span class="section-tag">Seção 05</span>
            <h2>Questões de Fixação e Entrevista</h2>
        </div>

        <div class="quiz-item">
            <div class="quiz-question">
                <strong>Questão 1 (Indicador):</strong> A varredura deu zero resultados. Dá para encerrar?
            </div>
            <details class="quiz-details">
                <summary class="quiz-toggle">Ver resposta explicada</summary>
                <div class="quiz-answer">
                    <p><strong>Resposta:</strong> Não.</p>
                </div>
            </details>
        </div>
    </section>

    <section class="study-section" id="fatos">
        <div class="section-header">
            <span class="section-tag">Seção 06</span>
            <h2>Fatos Essenciais, Referências e Próximos Passos</h2>
        </div>

        <h3>Referências</h3>
        <ul>
            <li>Splunk SURGe — PEAK Threat Hunting Framework (2023).</li>
        </ul>
    </section>

</article>

<!-- DADOS DO SIMULADOR -->
<script type="application/json" id="th-dados">
{"etapas": [1, 2, 3]}
</script>
"""


class TestMigracao(unittest.TestCase):
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


class TestMigracaoDetalhes(unittest.TestCase):
    def test_g2_variante_redes(self):
        out = migrar(G2B, "x")
        self.assertEqual(validar_corpo(out, "x"), [])
        self.assertEqual(texto_visivel(G2B), texto_visivel(out))
        self.assertEqual(migrar(out, "x"), out)
        self.assertIn('class="callout key"', out)
        self.assertNotIn("callout info", out)
        self.assertNotIn("checklist-items", out)
        self.assertIn('<div class="quiz-summary">', out)
        self.assertNotIn('<summary class="quiz-summary"', out)
        self.assertIn('<summary class="quiz-toggle">Ver resposta explicada</summary>', out)
        self.assertNotIn("<details class=\"quiz-item\"", out)
        self.assertIn('<label for="chk-1">', out)
        self.assertNotIn("progress-fill", out)

    def test_ordem_dos_atributos_da_secao(self):
        for g in (G1, G2, G2B, G3):
            for linha in migrar(g, "x").splitlines():
                if "<section" in linha:
                    self.assertRegex(linha.strip(),
                                     r'^<section class="study-section" id="[^"]+" data-tipo="[a-z]+">$')

    def test_tipos_das_secoes(self):
        tipos = {s.id: s.tipo for s in extrair_secoes(migrar(G3, "x"))}
        self.assertEqual(tipos, {"intro": "teoria", "simulador": "laboratorio", "checklist": "checklist",
                                 "quiz": "questoes", "fatos": "referencias"})

    def test_g1_um_unico_article_sem_main(self):
        out = migrar(G1, "x")
        self.assertNotIn("<main", out); self.assertNotIn("</main>", out)
        self.assertNotIn("CABEÇALHO HERO", out)
        self.assertEqual(out.count('<article class="study-container" data-slug="x">'), 1)
        self.assertNotIn("checklist-counter", out)
        self.assertNotIn("checklist-progress-bar\"", out.split("<script>")[0])

    def test_g1_checklist_vira_ul_li_com_label_for(self):
        out = migrar(G1, "x")
        self.assertIn('<ul class="checklist" data-checklist-id="fundamentos-ciber">', out)
        self.assertIn('<input type="checkbox" id="chk-fnd-1">', out)
        self.assertIn('<label for="chk-fnd-1"><strong>1. Inventário de Ativos e Dados:</strong>', out)

    def test_checklist_sem_id_preserva_chave_do_localstorage(self):
        # base.js usa `${listId}_${itemIdx}` com listId = list_<índice do .checklist> quando
        # o input não tem id; o id gerado reproduz essa chave.
        out = migrar(G2, "x")
        self.assertIn('id="list_0_0"', out); self.assertIn('<label for="list_0_1">', out)
        self.assertIn('<ul class="checklist" id="checklist-arquitetura-zero-trust">', out)

    def test_g2_quiz_details_quiz_answer(self):
        out = migrar(G2, "x")
        self.assertIn('<details class="quiz-details">', out)
        self.assertIn('<summary class="quiz-toggle">Ver resposta comentada</summary>', out)
        self.assertIn('<div class="quiz-answer">', out)

    def test_conteudo_de_script_intacto(self):
        js = ('<script>\nconst t = \'<section class="content-section" id="falso">'
              '<span class="section-tag">x</span></section>\';\n</script>\n')
        out = migrar(G3 + js, "x")
        self.assertTrue(out.endswith(js))
        self.assertEqual(validar_corpo(out, "x"), [])

    def test_g3_preserva_resto_byte_a_byte(self):
        out = migrar(G3, "x")
        fim = '<section class="study-section" id="simulador"'
        self.assertEqual(out[out.index('<p class="lead-text">'):out.index(fim)],
                         G3[G3.index('<p class="lead-text">'):G3.index(fim)])
        self.assertIn('    <section class="study-section" id="intro" data-tipo="teoria">\n'
                      '        <h2>Introdução: Nenhum Alerta Não Quer Dizer Nenhum Invasor</h2>\n\n'
                      '        <p class="lead-text">', out)
        self.assertTrue(out.endswith(G3[G3.index("</article>"):]))
        self.assertTrue(out.startswith("<!-- Estudo 47: Threat-Hunting Body Fragment -->\n"
                                       '<article class="study-container" data-slug="threat-hunting">\n'))

    def test_texto_visivel_detecta_mudanca(self):
        alterado = G3.replace("escrita antes da busca", "escrita depois da busca")
        self.assertNotEqual(texto_visivel(G3), texto_visivel(alterado))

    def test_texto_visivel_ignora_marcadores_removidos(self):
        textos = texto_visivel(G3)
        self.assertEqual(len(textos), 5)
        self.assertNotIn("Seção 01", textos[0])
        self.assertTrue(textos[0].startswith("Introdução: Nenhum Alerta"))

    def test_cabecalho_legado(self):
        g2 = cabecalho_legado(G2)
        self.assertEqual(g2["titulo"], "Redes e Protocolos")
        self.assertIn("T1046", g2["badges"])
        self.assertEqual(g2["kicker"], "Trilha 1: Fundamentos & Redes Seguras • Estudo 02")
        self.assertEqual(g2["subtitulo"], "A cibersegurança operacional começa na camada de transporte e roteamento.")
        g1 = cabecalho_legado(G1)
        self.assertEqual(g1["titulo"], "Tríade CIA, Ameaças e Modelagem STRIDE")
        self.assertIn("TA0043", g1["badges"])
        self.assertEqual(cabecalho_legado(G3), {})



class TestCli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        patcher = mock.patch.object(migrar_markup, "DIR", self.dir)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _rodar(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = migrar_markup.main(list(args))
        return rc, out.getvalue(), err.getvalue()

    def test_revisar_imprime_tabela_sem_gravar(self):
        (self.dir / "x_body.html").write_text(G3, encoding="utf-8")
        rc, out, _ = self._rodar("--revisar")
        self.assertEqual(rc, 0)
        self.assertIn("x | simulador | laboratorio | Laboratório Prático: Caçada Guiada", out)
        self.assertEqual((self.dir / "x_body.html").read_text(encoding="utf-8"), G3)

    def test_aplicar_grava_e_e_idempotente(self):
        corpo = self.dir / "x_body.html"
        corpo.write_text(G3, encoding="utf-8")
        self.assertEqual(self._rodar("--aplicar")[0], 0)
        self.assertEqual(corpo.read_text(encoding="utf-8"), migrar(G3, "x"))
        rc, out, _ = self._rodar("--aplicar")
        self.assertEqual(rc, 0); self.assertNotIn("migrado", out)

    def test_aplicar_aborta_corpo_que_viola_o_contrato(self):
        inicio = G3.index('    <section class="study-section" id="checklist">')
        fim = G3.index('    <section class="study-section" id="quiz">')
        sem_checklist = G3[:inicio] + G3[fim:]
        corpo = self.dir / "x_body.html"
        corpo.write_text(sem_checklist, encoding="utf-8")
        rc, _, err = self._rodar("--aplicar")
        self.assertEqual(rc, 1)
        self.assertIn('x §5: corpo: falta seção do tipo "checklist"', err)
        self.assertEqual(corpo.read_text(encoding="utf-8"), sem_checklist)

    def test_aplicar_aborta_corpo_cujo_texto_mudaria(self):
        corpo = self.dir / "x_body.html"
        corpo.write_text(G3, encoding="utf-8")
        estragado = migrar(G3, "x").replace("escrita antes da busca", "escrita depois")
        with mock.patch.object(migrar_markup, "migrar", return_value=estragado):
            rc, _, err = self._rodar("--aplicar")
        self.assertEqual(rc, 1)
        self.assertIn("x: texto visível das seções mudaria", err)
        self.assertEqual(corpo.read_text(encoding="utf-8"), G3)


if __name__ == "__main__":
    unittest.main()
