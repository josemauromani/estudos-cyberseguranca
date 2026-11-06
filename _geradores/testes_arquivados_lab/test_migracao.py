import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contrato import extrair_secoes, validar_corpo
import migrar_markup
from migrar_markup import EXCECOES, cabecalho_legado, classificar, migrar, texto_visivel
G1 = '<!-- ==========================================================================\n     MÓDULO 01: FUNDAMENTOS-CIBER — CORPO DIDÁTICO E SIMULADOR STRIDE\n     ========================================================================== -->\n\n<main class="container">\n\n  <!-- 1. CABEÇALHO HERO & METADADOS -->\n  <header class="hero-header" style="--track-color: var(--t1-blue);">\n    <div class="badge badge-t1">Trilha 1 &bull; Fundamentos &amp; Redes</div>\n    <h1>Tríade CIA, Ameaças e Modelagem STRIDE</h1>\n    <p class="hero-subtitle">Pilares da segurança da informação e metodologia STRIDE.</p>\n    <div class="meta-bar">\n      <span class="meta-item">⏱️ <strong>Tempo Estimado:</strong> 40 minutos</span>\n      <span class="meta-item">🛡️ <strong>NIST CSF 2.0:</strong> Identify (ID.AM, ID.RA)</span>\n      <span class="meta-item">🔬 <strong>MITRE ATT&amp;CK:</strong> TA0043 (Reconnaissance) &bull; TA0001 (Initial Access)</span>\n    </div>\n  </header>\n\n  <!-- 2. FUNDAMENTAÇÃO TEÓRICA E ARQUITETURA -->\n  <section class="content-section" id="fundamentacao-teorica">\n    <h2>1. Introdução e Contexto Prático da Cibersegurança</h2>\n    <p>\n      Cibersegurança moderna não é um produto de software; é uma disciplina contínua de gerenciamento de risco.\n    </p>\n\n    <div class="callout callout-tip">\n      <strong>💡 Fundamento Profissional:</strong>\n      A segurança não busca eliminar 100% dos riscos.\n    </div>\n    <div class="callout callout-warning">\n      <strong>⚠️ Atenção:</strong> Nem todo incidente é um ataque.\n    </div>\n    <div class="callout callout-danger">\n      <strong>🚨 Risco:</strong> Credenciais vazadas.\n    </div>\n    <div class="callout callout-law">\n      <strong>⚖️ LGPD:</strong> Art. 46.\n    </div>\n  </section>\n\n  <!-- 4. LABORATÓRIO -->\n  <section class="content-section" id="simulador-stride">\n    <h2>3. Laboratório Interativo: STRIDE Canvas</h2>\n    <div class="lab-box">\n      <div class="lab-header">\n        <h3>🧪 Simulador STRIDE Canvas</h3>\n      </div>\n    </div>\n  </section>\n\n  <!-- 5. CHECKLIST OPERACIONAL DE BOAS PRÁTICAS -->\n  <section class="content-section" id="checklist-pratico">\n    <h2>4. Checklist de Auditoria: Modelagem de Ameaças em Projetos Reais</h2>\n    <p>\n      O progresso é <strong>salvo automaticamente</strong> no seu navegador.\n    </p>\n\n    <div class="checklist" data-checklist-id="fundamentos-ciber">\n      <h4>\n        <span>Auditoria de Modelagem de Ameaças STRIDE</span>\n        <span class="checklist-counter" style="font-size: 0.85rem; color: var(--muted); font-weight: normal;">0 de 2 itens auditados</span>\n      </h4>\n      <div class="checklist-progress-bar">\n        <div class="checklist-progress-fill"></div>\n      </div>\n\n      <label class="check-item">\n        <input type="checkbox" id="chk-fnd-1">\n        <span><strong>1. Inventário de Ativos e Dados:</strong> Identificar e catalogar formalmente todos os ativos críticos.</span>\n      </label>\n\n      <label class="check-item">\n        <input type="checkbox" id="chk-fnd-2">\n        <span><strong>2. Fronteiras de Confiança (Trust Boundaries):</strong> Mapear visualmente no diagrama arquitetural.</span>\n      </label>\n    </div>\n  </section>\n\n  <!-- 6. QUIZ DE FIXAÇÃO E VALIDAÇÃO -->\n  <section class="content-section" id="quiz-fixacao">\n    <h2>5. Questões de Fixação e Concursos Públicos</h2>\n    <div class="quiz-section">\n      <!-- Questão 1 -->\n      <div class="quiz-item" data-quiz-id="q1">\n        <p class="quiz-question">\n          <strong>Questão 1 (Tríade CIA &amp; DAD):</strong> Qual pilar foi violado?\n        </p>\n        <div class="quiz-options">\n          <button class="quiz-btn" onclick="CS.checkQuiz(this, false, \'Incorreto.\')">\n            A) Confidencialidade.\n          </button>\n          <button class="quiz-btn" onclick="CS.checkQuiz(this, true, \'Correto!\')">\n            B) Disponibilidade.\n          </button>\n        </div>\n        <div class="quiz-feedback" style="display: none;"></div>\n      </div>\n    </div>\n  </section>\n\n  <!-- 7. FATOS ESSENCIAIS, NORMAS E PRÓXIMOS PASSOS -->\n  <section class="content-section" id="fatos-essenciais">\n    <h2>6. Fatos Essenciais, Normas e Próximos Passos</h2>\n    <div class="facts-grid">\n      <div class="facts-card">\n        <h4>📚 Tríade CIA &amp; Tríade DAD</h4>\n        <p>Confidencialidade, Integridade e Disponibilidade.</p>\n      </div>\n    </div>\n  </section>\n\n</main>\n\n<!-- JAVASCRIPT EXCLUSIVO DO SIMULADOR STRIDE CANVAS (VANILLA JS) -->\n<script>\n(function() {\n  \'use strict\';\n  document.querySelectorAll(\'.quiz-btn\');\n})();\n</script>\n'
G2 = '<!-- ==========================================================================\n     Estudo 02: Redes e Protocolos\n     ========================================================================== -->\n\n<header class="study-header">\n  <span class="study-track-kicker">Trilha 1: Fundamentos &amp; Redes Seguras &bull; Estudo 02</span>\n  <h1 class="study-title">Redes e Protocolos</h1>\n  <p class="study-lead">\n    A cibersegurança operacional começa na camada de transporte e roteamento.\n  </p>\n  <div class="study-meta-bar">\n    <span class="badge blue">NIST CSF 2.0: Protect (PR) &amp; Detect (DE)</span>\n    <span class="badge slate">MITRE ATT&amp;CK: T1046, T1071, T1557</span>\n    <span class="badge slate">Tempo Estimado: ~50 minutos</span>\n  </div>\n</header>\n\n<!-- SEÇÃO 1: INTRODUÇÃO E MODELOS DE REDE -->\n<section class="study-section" id="modelos-rede">\n  <div class="section-title-wrap">\n    <span class="section-num">01</span>\n    <h2>Modelos de Rede, Camadas e Encapsulamento</h2>\n  </div>\n\n  <p>\n    Para proteger ou investigar uma rede, o profissional de segurança deve visualizar como a informação transita.\n  </p>\n\n  <div class="callout tip">\n    <h4>Dica</h4>\n    <p>Encapsulamento é a chave.</p>\n  </div>\n</section>\n\n<!-- SEÇÃO 3: LABORATÓRIO -->\n<section class="study-section" id="laboratorio-inspetor">\n  <div class="section-title-wrap">\n    <span class="section-num">03</span>\n    <h2>Laboratório Interativo: Inspetor Visual de Pacotes</h2>\n  </div>\n\n  <div class="lab-box" id="packet-inspector">\n    <div class="lab-header">\n      <h3>Inspetor de Pacotes &bull; Probe de Portas</h3>\n    </div>\n  </div>\n</section>\n\n<!-- SEÇÃO 6: CHECKLIST -->\n<section class="study-section" id="checklist-zero-trust">\n  <div class="section-title-wrap">\n    <span class="section-num">06</span>\n    <h2>Checklist de Aplicação Prática</h2>\n  </div>\n\n  <div class="checklist" id="checklist-arquitetura-zero-trust">\n    <label class="checklist-item">\n      <input type="checkbox" onchange="toggleCheckItem(this)">\n      <span class="check-box"></span>\n      <span class="check-text">\n        <strong>Erradicação da Confiança Implícita:</strong>\n        Dispositivos conectados à rede local não possuem privilégios adicionais.\n      </span>\n    </label>\n\n    <label class="checklist-item">\n      <input type="checkbox" onchange="toggleCheckItem(this)">\n      <span class="check-box"></span>\n      <span class="check-text">\n        <strong>Adoção de ZTNA:</strong>\n        O acesso remoto é baseado em ZTNA/SDP.\n      </span>\n    </label>\n  </div>\n</section>\n\n<!-- SEÇÃO 7: QUESTÕES DE FIXAÇÃO E CONCURSOS -->\n<section class="study-section" id="questoes-fixacao">\n  <div class="section-title-wrap">\n    <span class="section-num">07</span>\n    <h2>Questões de Fixação e Concursos Públicos</h2>\n  </div>\n\n  <div class="quiz" id="quiz-arquitetura-zero-trust">\n    <!-- Questão 1 -->\n    <div class="quiz-item">\n      <div class="quiz-question">\n        <span class="quiz-badge">Questão 1 &bull; Componentes Lógicos do NIST SP 800-207</span>\n        <p>\n          Qual é a responsabilidade do Policy Enforcement Point (PEP)?\n        </p>\n      </div>\n      <details class="quiz-answer">\n        <summary>Ver resposta comentada</summary>\n        <div class="quiz-explanation">\n          <p>\n            <strong>Gabarito: O PEP atua no Plano de Dados.</strong>\n          </p>\n        </div>\n      </details>\n    </div>\n  </div>\n</section>\n\n<!-- SEÇÃO 8: FATOS ESSENCIAIS -->\n<section class="study-section" id="fatos-essenciais">\n  <div class="section-title-wrap">\n    <span class="section-num">08</span>\n    <h2>Fatos Essenciais e Conexões da Trilha</h2>\n  </div>\n\n  <div class="facts-grid">\n    <div class="facts-card">\n      <span class="facts-card-num">20 B</span>\n      <span class="facts-card-label">Tamanho Base IPv4</span>\n    </div>\n  </div>\n</section>\n\n<!-- ==========================================================================\n     SCRIPT DO LABORATÓRIO INTERATIVO (Vanilla JS puro & autônomo)\n     ========================================================================== -->\n<script>\n(function() {\n  \'use strict\';\n})();\n</script>\n'
G2B = '<header class="study-header">\n  <span class="study-track-kicker">Trilha 1 &bull; Estudo 03</span>\n  <h1 class="study-title">Criptografia Prática</h1>\n  <p class="study-lead">A criptografia é a espinha dorsal.</p>\n  <div class="study-meta-bar">\n    <span class="badge slate">MITRE ATT&amp;CK: T1003</span>\n  </div>\n</header>\n\n<!-- SEÇÃO 1 -->\n<section class="study-section" id="pilares">\n  <div class="section-title-wrap">\n    <span class="section-num">01</span>\n    <h2>Pilares</h2>\n  </div>\n  <div class="callout info">\n    <h4>RSA vs Curvas Elípticas (ECC)</h4>\n    <p>O RSA baseia sua segurança na fatoração.</p>\n  </div>\n</section>\n\n<section class="study-section" id="lab">\n  <div class="section-title-wrap">\n    <span class="section-num">02</span>\n    <h2>Laboratório</h2>\n  </div>\n  <div class="lab-box"><p>Simulador</p></div>\n</section>\n\n<section class="study-section" id="checklist-cripto">\n  <div class="section-title-wrap">\n    <span class="section-num">03</span>\n    <h2>Checklist</h2>\n  </div>\n\n  <div class="checklist">\n    <div class="checklist-header">\n      <h3>Procedimento de Análise de Tráfego</h3>\n      <div class="checklist-progress-bar"><div class="progress-fill" id="chk-progress"></div></div>\n    </div>\n    <ul class="checklist-items">\n      <li class="checklist-item">\n        <label>\n          <input type="checkbox" id="chk-1">\n          <span class="chk-label">\n            <strong>1. Mapeamento de Camada 2:</strong>\n            Verifique a tabela de vizinhos ARP (<code>arp -a</code>).\n          </span>\n        </label>\n      </li>\n      <li class="checklist-item">\n        <label>\n          <input type="checkbox" id="chk-2">\n          <span class="chk-label">\n            <strong>2. Flags TCP:</strong>\n            Filtre por combinações ilegítimas de flags.\n          </span>\n        </label>\n      </li>\n    </ul>\n  </div>\n</section>\n\n<section class="study-section" id="questoes-fixacao">\n  <div class="section-title-wrap">\n    <span class="section-num">04</span>\n    <h2>Questões</h2>\n  </div>\n\n  <div class="quiz-container">\n    <!-- Questão 1 -->\n    <details class="quiz-item">\n      <summary class="quiz-summary">\n        <span class="quiz-tag">Questão 1 &bull; Pilha TCP/IP</span>\n        <p class="quiz-question">\n          Qual pacote o scanner envia após receber [SYN, ACK]?\n        </p>\n      </summary>\n      <div class="quiz-answer">\n        <div class="answer-badge correct">Resposta Correta: [RST].</div>\n        <p>O scanner aborta a transação.</p>\n      </div>\n    </details>\n  </div>\n</section>\n\n<section class="study-section" id="fatos">\n  <div class="section-title-wrap">\n    <span class="section-num">05</span>\n    <h2>Fatos</h2>\n  </div>\n  <div class="facts-grid"><div class="facts-card">AES-256</div></div>\n</section>\n\n<script>\n(function() {})();\n</script>\n'
G3 = '<!-- Estudo 47: Threat-Hunting Body Fragment -->\n<article class="study-container" data-slug="threat-hunting">\n\n    <!-- SEÇÃO 1: CAÇA POR HIPÓTESE -->\n    <section class="study-section" id="intro">\n        <div class="section-header">\n            <span class="section-tag">Seção 01</span>\n            <h2>Introdução: Nenhum Alerta Não Quer Dizer Nenhum Invasor</h2>\n        </div>\n\n        <p class="lead-text">\n            Na segunda-feira, o SOC da Ipê Store recebeu um relatório de inteligência.\n        </p>\n\n        <div class="callout tip">\n            <div class="callout-title">\n                <span class="callout-icon">🔦</span>\n                <strong>Caça por hipótese</strong>\n            </div>\n            <p>Comece por uma pergunta testável.</p>\n        </div>\n    </section>\n\n    <section class="study-section" id="simulador">\n        <div class="section-header">\n            <span class="section-tag">Seção 03</span>\n            <h2>Laboratório Prático: Caçada Guiada</h2>\n        </div>\n\n        <div class="lab-box th-lab" id="th-lab">\n            <p>Painel</p>\n        </div>\n    </section>\n\n    <section class="study-section" id="checklist">\n        <div class="section-header">\n            <span class="section-tag">Seção 04</span>\n            <h2>Checklist de uma Caçada</h2>\n        </div>\n\n        <ul class="checklist" data-checklist-slug="threat-hunting">\n            <li class="checklist-item">\n                <input type="checkbox" id="chk-th-1">\n                <label for="chk-th-1"><strong>Hipótese:</strong> escrita antes da busca.</label>\n            </li>\n            <li class="checklist-item">\n                <input type="checkbox" id="chk-th-2">\n                <label for="chk-th-2"><strong>Visibilidade:</strong> a fonte enxerga o comportamento.</label>\n            </li>\n        </ul>\n    </section>\n\n    <section class="study-section" id="quiz">\n        <div class="section-header">\n            <span class="section-tag">Seção 05</span>\n            <h2>Questões de Fixação e Entrevista</h2>\n        </div>\n\n        <div class="quiz-item">\n            <div class="quiz-question">\n                <strong>Questão 1 (Indicador):</strong> A varredura deu zero resultados. Dá para encerrar?\n            </div>\n            <details class="quiz-details">\n                <summary class="quiz-toggle">Ver resposta explicada</summary>\n                <div class="quiz-answer">\n                    <p><strong>Resposta:</strong> Não.</p>\n                </div>\n            </details>\n        </div>\n    </section>\n\n    <section class="study-section" id="fatos">\n        <div class="section-header">\n            <span class="section-tag">Seção 06</span>\n            <h2>Fatos Essenciais, Referências e Próximos Passos</h2>\n        </div>\n\n        <h3>Referências</h3>\n        <ul>\n            <li>Splunk SURGe — PEAK Threat Hunting Framework (2023).</li>\n        </ul>\n    </section>\n\n</article>\n\n<!-- DADOS DO SIMULADOR -->\n<script type="application/json" id="th-dados">\n{"etapas": [1, 2, 3]}\n</script>\n'

class TestMigracao(unittest.TestCase):

    def test_g2_envolve_em_article_e_simplifica_h2(self):
        out = migrar(G2, 'x')
        self.assertIn('<article class="study-container"', out)
        self.assertNotIn('study-header', out)
        self.assertNotIn('section-num', out)

    def test_g1_normaliza_variantes(self):
        out = migrar(G1, 'x')
        for velho in ('hero-header', 'content-section', 'class="check-item"', 'callout-tip'):
            self.assertNotIn(velho, out)
        self.assertIn('class="callout tip"', out)
        self.assertIn('data-formato="multipla"', out)

    def test_idempotente(self):
        for g in (G1, G2, G3):
            uma = migrar(g, 'x')
            self.assertEqual(migrar(uma, 'x'), uma)

    def test_texto_preservado(self):
        for g in (G1, G2, G3):
            self.assertEqual(texto_visivel(g), texto_visivel(migrar(g, 'x')))

    def test_resultado_passa_no_contrato(self):
        for g in (G1, G2, G3):
            self.assertEqual(validar_corpo(migrar(g, 'x'), 'x'), [])

class TestMigracaoDetalhes(unittest.TestCase):

    def test_g2_variante_redes(self):
        out = migrar(G2B, 'x')
        self.assertEqual(validar_corpo(out, 'x'), [])
        self.assertEqual(texto_visivel(G2B), texto_visivel(out))
        self.assertEqual(migrar(out, 'x'), out)
        self.assertIn('class="callout key"', out)
        self.assertNotIn('callout info', out)
        self.assertNotIn('checklist-items', out)
        self.assertIn('<div class="quiz-summary">', out)
        self.assertNotIn('<summary class="quiz-summary"', out)
        self.assertIn('<summary class="quiz-toggle">Ver resposta explicada</summary>', out)
        self.assertNotIn('<details class="quiz-item"', out)
        self.assertIn('<label for="chk-1">', out)
        self.assertNotIn('progress-fill', out)

    def test_ordem_dos_atributos_da_secao(self):
        for g in (G1, G2, G2B, G3):
            for linha in migrar(g, 'x').splitlines():
                if '<section' in linha:
                    self.assertRegex(linha.strip(), '^<section class="study-section" id="[^"]+" data-tipo="[a-z]+">$')

    def test_g1_um_unico_article_sem_main(self):
        out = migrar(G1, 'x')
        self.assertNotIn('<main', out)
        self.assertNotIn('</main>', out)
        self.assertNotIn('CABEÇALHO HERO', out)
        self.assertEqual(out.count('<article class="study-container" data-slug="x">'), 1)
        self.assertNotIn('checklist-counter', out)
        self.assertNotIn('checklist-progress-bar"', out.split('<script>')[0])

    def test_g1_checklist_vira_ul_li_com_label_for(self):
        out = migrar(G1, 'x')
        self.assertIn('<ul class="checklist" data-checklist-id="fundamentos-ciber">', out)
        self.assertIn('<input type="checkbox" id="chk-fnd-1">', out)
        self.assertIn('<label for="chk-fnd-1"><strong>1. Inventário de Ativos e Dados:</strong>', out)

    def test_checklist_sem_id_preserva_chave_do_localstorage(self):
        out = migrar(G2, 'x')
        self.assertIn('id="list_0_0"', out)
        self.assertIn('<label for="list_0_1">', out)
        self.assertIn('<ul class="checklist" id="checklist-arquitetura-zero-trust">', out)

    def test_g2_quiz_details_quiz_answer(self):
        out = migrar(G2, 'x')
        self.assertIn('<details class="quiz-details">', out)
        self.assertIn('<summary class="quiz-toggle">Ver resposta comentada</summary>', out)
        self.assertIn('<div class="quiz-answer">', out)

    def test_conteudo_de_script_intacto(self):
        js = '<script>\nconst t = \'<section class="content-section" id="falso"><span class="section-tag">x</span></section>\';\n</script>\n'
        out = migrar(G3 + js, 'x')
        self.assertTrue(out.endswith(js))
        self.assertEqual(validar_corpo(out, 'x'), [])

    def test_texto_visivel_detecta_mudanca(self):
        alterado = G3.replace('escrita antes da busca', 'escrita depois da busca')
        self.assertNotEqual(texto_visivel(G3), texto_visivel(alterado))

    def test_texto_visivel_ignora_marcadores_removidos(self):
        textos = texto_visivel(G3)
        self.assertEqual(len(textos), 5)
        self.assertNotIn('Seção 01', textos[0])
        self.assertTrue(textos[0].startswith('Introdução: Nenhum Alerta'))

    def test_cabecalho_legado(self):
        g2 = cabecalho_legado(G2)
        self.assertEqual(g2['titulo'], 'Redes e Protocolos')
        self.assertIn('T1046', g2['badges'])
        self.assertEqual(g2['kicker'], 'Trilha 1: Fundamentos & Redes Seguras • Estudo 02')
        self.assertEqual(g2['subtitulo'], 'A cibersegurança operacional começa na camada de transporte e roteamento.')
        g1 = cabecalho_legado(G1)
        self.assertEqual(g1['titulo'], 'Tríade CIA, Ameaças e Modelagem STRIDE')
        self.assertIn('TA0043', g1['badges'])
        self.assertEqual(cabecalho_legado(G3), {})

class TestLeadLegado(unittest.TestCase):
    """R11: o parágrafo introdutório do cabeçalho legado vai para a 1ª seção."""

    def test_g2_lead_logo_apos_o_primeiro_h2(self):
        out = migrar(G2, 'x')
        self.assertIn('<section class="study-section" id="modelos-rede" data-tipo="teoria">\n  <h2>Modelos de Rede, Camadas e Encapsulamento</h2>\n\n  <p class="lead-text">\n    A cibersegurança operacional começa na camada de transporte e roteamento.\n  </p>\n\n  <p>\n', out)
        self.assertNotIn('study-header', out)
        self.assertNotIn('study-lead', out)
        self.assertEqual(out.count('A cibersegurança operacional começa'), 1)

    def test_g1_lead_logo_apos_o_primeiro_h2(self):
        out = migrar(G1, 'x')
        self.assertIn('    <h2>1. Introdução e Contexto Prático da Cibersegurança</h2>\n\n    <p class="lead-text">Pilares da segurança da informação e metodologia STRIDE.</p>\n    <p>\n', out)
        self.assertNotIn('hero-header', out)
        self.assertNotIn('hero-subtitle', out)

    def test_lead_idempotente_e_valido(self):
        for g in (G1, G2, G2B):
            uma = migrar(g, 'x')
            self.assertEqual(migrar(uma, 'x'), uma)
            self.assertEqual(uma.count('class="lead-text"'), 1)
            self.assertEqual(validar_corpo(uma, 'x'), [])

    def test_texto_visivel_conta_o_lead_na_primeira_secao(self):
        primeira = texto_visivel(G2)[0]
        self.assertTrue(primeira.startswith('Modelos de Rede, Camadas e Encapsulamento A cibersegurança operacional começa'))
        self.assertEqual(texto_visivel(G2), texto_visivel(migrar(G2, 'x')))
        self.assertEqual(texto_visivel(G1), texto_visivel(migrar(G1, 'x')))

    def test_texto_visivel_acusa_lead_perdido(self):
        sem_lead = migrar(G2, 'x').replace('    A cibersegurança operacional começa na camada de transporte e roteamento.\n', '')
        self.assertNotEqual(texto_visivel(G2), texto_visivel(sem_lead))

class TestCli(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        patcher = mock.patch.object(migrar_markup, 'DIR', self.dir)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _rodar(self, *args):
        out, err = (io.StringIO(), io.StringIO())
        with redirect_stdout(out), redirect_stderr(err):
            rc = migrar_markup.main(list(args))
        return (rc, out.getvalue(), err.getvalue())

    def test_aplicar_grava_e_e_idempotente(self):
        corpo = self.dir / 'x_body.html'
        corpo.write_text(G3, encoding='utf-8')
        self.assertEqual(self._rodar('--aplicar')[0], 0)
        self.assertEqual(corpo.read_text(encoding='utf-8'), migrar(G3, 'x'))
        rc, out, _ = self._rodar('--aplicar')
        self.assertEqual(rc, 0)
        self.assertNotIn('migrado', out)

    def test_aplicar_aborta_corpo_que_viola_o_contrato(self):
        inicio = G3.index('    <section class="study-section" id="checklist">')
        fim = G3.index('    <section class="study-section" id="quiz">')
        sem_checklist = G3[:inicio] + G3[fim:]
        corpo = self.dir / 'x_body.html'
        corpo.write_text(sem_checklist, encoding='utf-8')
        rc, _, err = self._rodar('--aplicar')
        self.assertEqual(rc, 1)
        self.assertIn('x §5: corpo: falta seção do tipo "checklist"', err)
        self.assertEqual(corpo.read_text(encoding='utf-8'), sem_checklist)

    def test_aplicar_aborta_corpo_cujo_texto_mudaria(self):
        corpo = self.dir / 'x_body.html'
        corpo.write_text(G3, encoding='utf-8')
        estragado = migrar(G3, 'x').replace('escrita antes da busca', 'escrita depois')
        with mock.patch.object(migrar_markup, 'migrar', return_value=estragado):
            rc, _, err = self._rodar('--aplicar')
        self.assertEqual(rc, 1)
        self.assertIn('x: texto visível das seções mudaria', err)
        self.assertEqual(corpo.read_text(encoding='utf-8'), G3)

    def test_aplicar_aborta_se_o_lead_sumir(self):
        corpo = self.dir / 'x_body.html'
        corpo.write_text(G2, encoding='utf-8')
        estragado = migrar(G2, 'x').replace('    A cibersegurança operacional começa na camada de transporte e roteamento.\n', '')
        with mock.patch.object(migrar_markup, 'migrar', return_value=estragado):
            rc, _, err = self._rodar('--aplicar')
        self.assertEqual(rc, 1)
        self.assertIn('x: lead do cabeçalho legado ausente logo após o h2 da 1ª seção', err)
        self.assertEqual(corpo.read_text(encoding='utf-8'), G2)
if __name__ == '__main__':
    unittest.main()
