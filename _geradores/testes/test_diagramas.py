"""
Testes unitários para o módulo de compilação de diagramas Mermaid (_geradores/diagramas.py).
"""
import hashlib
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
sys.path.insert(0, str(Path(__file__).parent.parent))
GERADORES = Path(__file__).parent.parent
from diagramas import extrair_blocos_mermaid, calcular_hash_mermaid, gerar_svg_mermaid, obter_ou_gerar_svg, processar_diagramas_html

class TestDiagramasMermaid(unittest.TestCase):

    def test_extrair_blocos_mermaid(self):
        html = '\n        <div>\n          <h2>Módulo 1</h2>\n          <pre class="mermaid" data-title="Fluxo PDP e PEP">\nflowchart TD\n    A --> B\n          </pre>\n          <p>Texto intermediário</p>\n          <pre class="mermaid">\nflowchart LR\n    C --> D\n          </pre>\n        </div>\n        '
        blocos = extrair_blocos_mermaid(html)
        self.assertEqual(len(blocos), 2)
        b1 = blocos[0]
        self.assertIn('A --> B', b1['codigo'])
        self.assertEqual(b1['titulo'], 'Fluxo PDP e PEP')
        self.assertEqual(b1['atributos'].get('data-title'), 'Fluxo PDP e PEP')
        self.assertIn('<pre class="mermaid" data-title="Fluxo PDP e PEP">', b1['bloco_completo'])
        b2 = blocos[1]
        self.assertIn('C --> D', b2['codigo'])
        self.assertEqual(b2['titulo'], '')
        self.assertIn('<pre class="mermaid">', b2['bloco_completo'])

    def test_calcular_hash_mermaid_determinismo(self):
        c1 = 'flowchart TD\n    A --> B'
        c2 = '  \n\n  flowchart TD\n    A --> B \n\t '
        h1 = calcular_hash_mermaid(c1)
        h2 = calcular_hash_mermaid(c2)
        self.assertEqual(h1, h2)
        self.assertEqual(len(h1), 12)
        esperado = hashlib.sha256(c1.strip().encode('utf-8')).hexdigest()[:12]
        self.assertEqual(h1, esperado)

    def test_obter_ou_gerar_svg_cache_existente(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            cache_dir = Path(tmp_dir)
            codigo = 'flowchart TD\n    X --> Y'
            hash_id = calcular_hash_mermaid(codigo)
            svg_file = cache_dir / f'{hash_id}.svg'
            svg_content_mock = '<svg id="teste">SVG CACHEADO</svg>'
            svg_file.write_text(svg_content_mock, encoding='utf-8')
            with patch('diagramas.gerar_svg_mermaid') as mock_gerar:
                svg_retorno, retorno_hash = obter_ou_gerar_svg(codigo, cache_dir)
                mock_gerar.assert_not_called()
                self.assertEqual(retorno_hash, hash_id)
                self.assertEqual(svg_retorno, svg_content_mock)

    def test_obter_ou_gerar_svg_gera_quando_inexistente(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            cache_dir = Path(tmp_dir)
            codigo = 'flowchart TD\n    A --> B'
            hash_id = calcular_hash_mermaid(codigo)
            svg_file = cache_dir / f'{hash_id}.svg'

            def mock_gerar_impl(cod, caminho, cfg):
                caminho.write_text('<svg id="gerado">OK</svg>', encoding='utf-8')
                return True
            with patch('diagramas.gerar_svg_mermaid', side_effect=mock_gerar_impl) as mock_gerar:
                svg_retorno, retorno_hash = obter_ou_gerar_svg(codigo, cache_dir)
                self.assertTrue(mock_gerar.called)
                self.assertEqual(retorno_hash, hash_id)
                self.assertEqual(svg_retorno, '<svg id="gerado">OK</svg>')
                self.assertTrue(svg_file.exists())

    def test_processar_diagramas_html_substituicao(self):
        html = '\n        <section>\n          <h3>Diagrama de Decisão</h3>\n          <pre class="mermaid" data-title="Fluxo de Decisão">\nflowchart TD\n    A --> B\n          </pre>\n        </section>\n        '
        with tempfile.TemporaryDirectory() as tmp_dir:
            cache_dir = Path(tmp_dir)
            codigo = 'flowchart TD\n    A --> B'
            hash_id = calcular_hash_mermaid(codigo)
            svg_file = cache_dir / f'{hash_id}.svg'
            svg_file.write_text('<svg class="diagram-test"><g>nodes</g></svg>', encoding='utf-8')
            html_processado = processar_diagramas_html(html, cache_dir)
            self.assertNotIn('<pre class="mermaid"', html_processado)
            self.assertNotIn('diagram-box', html_processado)
            self.assertNotIn('diagram-header', html_processado)
            self.assertIn('<div class="diagram-svg-wrap" role="img" aria-label="Fluxo de Decisão">', html_processado)
            self.assertIn('<svg class="diagram-test"><g>nodes</g></svg>', html_processado)

    def test_processar_diagramas_html_preserva_um_unico_cabecalho(self):
        html = '\n        <div class="diagram-box">\n          <div class="diagram-header">\n            <span class="diagram-title">Fluxo de Decisão</span>\n            <span class="diagram-badge">Mermaid</span>\n          </div>\n          <pre class="mermaid" data-title="Fluxo de Decisão">\nflowchart TD\n    A --> B\n          </pre>\n        </div>\n        '
        with tempfile.TemporaryDirectory() as tmp_dir:
            cache_dir = Path(tmp_dir)
            hash_id = calcular_hash_mermaid('flowchart TD\n    A --> B')
            (cache_dir / f'{hash_id}.svg').write_text('<svg></svg>', encoding='utf-8')
            html_processado = processar_diagramas_html(html, cache_dir)
            self.assertEqual(html_processado.count('class="diagram-box"'), 1)
            self.assertEqual(html_processado.count('class="diagram-header"'), 1)
            self.assertEqual(html_processado.count('class="diagram-svg-wrap"'), 1)

    def test_fallback_quando_cli_falha(self):
        html = '\n        <div>\n          <pre class="mermaid" data-title="Diagrama com Erro">\nflowchart TD\n    INVALIDO $$$\n          </pre>\n        </div>\n        '
        with tempfile.TemporaryDirectory() as tmp_dir:
            cache_dir = Path(tmp_dir)
            with patch('diagramas.gerar_svg_mermaid', return_value=False):
                html_processado = processar_diagramas_html(html, cache_dir)
                self.assertIn('<pre class="mermaid" data-title="Diagrama com Erro">', html_processado)
                self.assertIn('INVALIDO $$$', html_processado)
                self.assertNotIn('<div class="diagram-box">', html_processado)

    def test_gerar_svg_mermaid_chamada_cli(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            caminho_svg = tmp_path / 'diagrama.svg'
            config_puppeteer = tmp_path / 'puppeteer-config.json'
            config_puppeteer.write_text('{"args": ["--no-sandbox"]}', encoding='utf-8')
            with patch('diagramas.subprocess.run') as mock_run:

                def fake_run(cmd, *args, **kwargs):
                    idx = cmd.index('-o')
                    out_path = Path(cmd[idx + 1])
                    out_path.write_text('<svg>MOCK</svg>', encoding='utf-8')
                    mock_res = MagicMock()
                    mock_res.returncode = 0
                    return mock_res
                mock_run.side_effect = fake_run
                sucesso = gerar_svg_mermaid('flowchart TD\n A --> B', caminho_svg, config_puppeteer)
                self.assertTrue(sucesso)
                self.assertTrue(caminho_svg.exists())
                self.assertEqual(caminho_svg.read_text(encoding='utf-8'), '<svg>MOCK</svg>')
                args, kwargs = mock_run.call_args
                cmd = args[0]
                self.assertIn('npx', cmd)
                self.assertIn('@mermaid-js/mermaid-cli', cmd)
                self.assertIn('-p', cmd)
                self.assertIn('-b', cmd)
                self.assertIn('transparent', cmd)
                self.assertIn('-t', cmd)
                self.assertIn('dark', cmd)

class TestCoberturaDiagramasModulos(unittest.TestCase):
    """Todo módulo traz ao menos um diagrama Mermaid com título."""

    def test_todo_modulo_tem_diagrama_com_titulo(self):
        corpos = sorted(Path(__file__).parent.parent.glob('*_body.html'))
        self.assertGreater(len(corpos), 0)
        sem_diagrama = []
        for corpo in corpos:
            blocos = extrair_blocos_mermaid(corpo.read_text(encoding='utf-8'))
            if not any((b['titulo'].strip() for b in blocos)):
                sem_diagrama.append(corpo.name)
        self.assertEqual(sem_diagrama, [], f'Módulos sem diagrama Mermaid: {sem_diagrama}')

    def test_todo_bloco_mermaid_esta_dentro_de_diagram_box_com_cabecalho(self):
        """GUIA-DO-AUTOR §3.6: o <pre> vem dentro de .diagram-box, após o cabeçalho com o mesmo título."""
        padrao = re.compile('<div class="diagram-box">\\s*<div class="diagram-header">\\s*<span class="diagram-title">([^<]*)</span>\\s*<span class="diagram-badge">[^<]*</span>\\s*</div>\\s*<pre class="mermaid" data-title="([^"]*)">')
        fora_do_padrao = []
        for corpo in sorted(GERADORES.glob('*_body.html')):
            html = corpo.read_text(encoding='utf-8')
            n_blocos = len(extrair_blocos_mermaid(html))
            encaixados = [m for m in padrao.finditer(html) if m.group(1) == m.group(2)]
            if len(encaixados) != n_blocos:
                fora_do_padrao.append(corpo.name)
        self.assertEqual(fora_do_padrao, [], f'Blocos Mermaid fora do .diagram-box: {fora_do_padrao}')

    def test_paginas_compiladas_tem_um_cabecalho_por_diagrama(self):
        duplicados = []
        for pagina in sorted(GERADORES.parent.glob('*/treinamento-*.html')):
            html = pagina.read_text(encoding='utf-8')
            if html.count('class="diagram-header"') != html.count('class="diagram-svg-wrap"'):
                duplicados.append(pagina.parent.name)
        self.assertEqual(duplicados, [], f'Páginas com cabeçalho de diagrama duplicado: {duplicados}')

    def test_cache_sem_svg_orfao(self):
        """Todo SVG do cache corresponde a um bloco Mermaid em uso; apague os que sobrarem."""
        em_uso = {calcular_hash_mermaid(b['codigo']) for corpo in GERADORES.glob('*_body.html') for b in extrair_blocos_mermaid(corpo.read_text(encoding='utf-8'))}
        orfaos = sorted((s.name for s in (GERADORES / 'cache_diagramas').glob('*.svg') if s.stem not in em_uso))
        self.assertEqual(orfaos, [], f'SVGs órfãos em cache_diagramas/: {orfaos}')

class TestFundoDoQuadroDeDiagrama(unittest.TestCase):
    """Os SVGs são gerados com o tema escuro do Mermaid (-t dark) e fundo transparente:
    textos e setas em lightgrey só ficam legíveis sobre fundo escuro, em qualquer tema da página."""

    def test_svg_wrap_tem_fundo_escuro_fixo(self):
        css = (GERADORES / 'base.css').read_text(encoding='utf-8')
        regra = re.search('\\.diagram-svg-wrap\\s*\\{([^}]*)\\}', css)
        self.assertIsNotNone(regra)
        fundo = re.search('background(?:-color)?\\s*:\\s*([^;]+);', regra.group(1))
        self.assertIsNotNone(fundo, '.diagram-svg-wrap precisa declarar fundo')
        valor = fundo.group(1).strip()
        token = re.fullmatch('var\\((--[\\w-]+)\\)', valor)
        if token:
            tokens = (GERADORES / 'tokens.css').read_text(encoding='utf-8')
            valores = re.findall(re.escape(token.group(1)) + '\\s*:\\s*([^;]+);', tokens)
            self.assertTrue(valores, f'{token.group(1)} não declarado em tokens.css')
        else:
            valores = [valor]
        for v in (v.strip() for v in valores):
            self.assertRegex(v, '^#[0-9A-Fa-f]{6}$', 'fundo precisa ser uma cor fixa por tema')
            r, g, b = (int(v[i:i + 2], 16) for i in (1, 3, 5))
            self.assertLess(0.2126 * r + 0.7152 * g + 0.0722 * b, 60, f'fundo precisa ser escuro: {v}')
if __name__ == '__main__':
    unittest.main()
