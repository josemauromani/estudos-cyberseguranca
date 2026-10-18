"""
Testes unitários para o módulo de compilação de diagramas Mermaid (_geradores/diagramas.py).
"""
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Garantir import do diretório _geradores
sys.path.insert(0, str(Path(__file__).parent.parent))

from diagramas import (
    extrair_blocos_mermaid,
    calcular_hash_mermaid,
    gerar_svg_mermaid,
    obter_ou_gerar_svg,
    processar_diagramas_html,
)


class TestDiagramasMermaid(unittest.TestCase):

    def test_extrair_blocos_mermaid(self):
        html = """
        <div>
          <h2>Módulo 1</h2>
          <pre class="mermaid" data-title="Fluxo PDP e PEP">
flowchart TD
    A --> B
          </pre>
          <p>Texto intermediário</p>
          <pre class="mermaid">
flowchart LR
    C --> D
          </pre>
        </div>
        """
        blocos = extrair_blocos_mermaid(html)
        self.assertEqual(len(blocos), 2)

        # Primeiro bloco com data-title
        b1 = blocos[0]
        self.assertIn("A --> B", b1["codigo"])
        self.assertEqual(b1["titulo"], "Fluxo PDP e PEP")
        self.assertEqual(b1["atributos"].get("data-title"), "Fluxo PDP e PEP")
        self.assertIn('<pre class="mermaid" data-title="Fluxo PDP e PEP">', b1["bloco_completo"])

        # Segundo bloco sem data-title
        b2 = blocos[1]
        self.assertIn("C --> D", b2["codigo"])
        self.assertEqual(b2["titulo"], "")
        self.assertIn('<pre class="mermaid">', b2["bloco_completo"])

    def test_calcular_hash_mermaid_determinismo(self):
        c1 = "flowchart TD\n    A --> B"
        c2 = "  \n\n  flowchart TD\n    A --> B \n\t "
        h1 = calcular_hash_mermaid(c1)
        h2 = calcular_hash_mermaid(c2)

        self.assertEqual(h1, h2)
        self.assertEqual(len(h1), 12)

        # Validar cálculo esperado
        esperado = hashlib.sha256(c1.strip().encode("utf-8")).hexdigest()[:12]
        self.assertEqual(h1, esperado)

    def test_obter_ou_gerar_svg_cache_existente(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            cache_dir = Path(tmp_dir)
            codigo = "flowchart TD\n    X --> Y"
            hash_id = calcular_hash_mermaid(codigo)
            svg_file = cache_dir / f"{hash_id}.svg"
            svg_content_mock = '<svg id="teste">SVG CACHEADO</svg>'
            svg_file.write_text(svg_content_mock, encoding="utf-8")

            with patch("diagramas.gerar_svg_mermaid") as mock_gerar:
                svg_retorno, retorno_hash = obter_ou_gerar_svg(codigo, cache_dir)
                mock_gerar.assert_not_called()
                self.assertEqual(retorno_hash, hash_id)
                self.assertEqual(svg_retorno, svg_content_mock)

    def test_obter_ou_gerar_svg_gera_quando_inexistente(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            cache_dir = Path(tmp_dir)
            codigo = "flowchart TD\n    A --> B"
            hash_id = calcular_hash_mermaid(codigo)
            svg_file = cache_dir / f"{hash_id}.svg"

            def mock_gerar_impl(cod, caminho, cfg):
                caminho.write_text('<svg id="gerado">OK</svg>', encoding="utf-8")
                return True

            with patch("diagramas.gerar_svg_mermaid", side_effect=mock_gerar_impl) as mock_gerar:
                svg_retorno, retorno_hash = obter_ou_gerar_svg(codigo, cache_dir)
                self.assertTrue(mock_gerar.called)
                self.assertEqual(retorno_hash, hash_id)
                self.assertEqual(svg_retorno, '<svg id="gerado">OK</svg>')
                self.assertTrue(svg_file.exists())

    def test_processar_diagramas_html_substituicao(self):
        html = """
        <section>
          <h3>Diagrama de Decisão</h3>
          <pre class="mermaid" data-title="Fluxo de Decisão">
flowchart TD
    A --> B
          </pre>
        </section>
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            cache_dir = Path(tmp_dir)
            codigo = "flowchart TD\n    A --> B"
            hash_id = calcular_hash_mermaid(codigo)
            svg_file = cache_dir / f"{hash_id}.svg"
            svg_file.write_text('<svg class="diagram-test"><g>nodes</g></svg>', encoding="utf-8")

            html_processado = processar_diagramas_html(html, cache_dir)

            # Não deve mais conter o <pre class="mermaid"> original
            self.assertNotIn('<pre class="mermaid"', html_processado)

            # Deve conter a estrutura .diagram-box
            self.assertIn('<div class="diagram-box">', html_processado)
            self.assertIn('<div class="diagram-header">', html_processado)
            self.assertIn('<span class="diagram-title">Fluxo de Decisão</span>', html_processado)
            self.assertIn('<span class="diagram-badge">Mermaid Arquitetura</span>', html_processado)
            self.assertIn('<div class="diagram-svg-wrap" role="img" aria-label="Fluxo de Decisão">', html_processado)
            self.assertIn('<svg class="diagram-test"><g>nodes</g></svg>', html_processado)

    def test_fallback_quando_cli_falha(self):
        html = """
        <div>
          <pre class="mermaid" data-title="Diagrama com Erro">
flowchart TD
    INVALIDO $$$
          </pre>
        </div>
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            cache_dir = Path(tmp_dir)

            with patch("diagramas.gerar_svg_mermaid", return_value=False):
                html_processado = processar_diagramas_html(html, cache_dir)
                # Como o CLI falhou e não há cache, o bloco original é preservado
                self.assertIn('<pre class="mermaid" data-title="Diagrama com Erro">', html_processado)
                self.assertIn("INVALIDO $$$", html_processado)
                self.assertNotIn('<div class="diagram-box">', html_processado)

    def test_gerar_svg_mermaid_chamada_cli(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            caminho_svg = tmp_path / "diagrama.svg"
            config_puppeteer = tmp_path / "puppeteer-config.json"
            config_puppeteer.write_text('{"args": ["--no-sandbox"]}', encoding="utf-8")

            with patch("diagramas.subprocess.run") as mock_run:
                def fake_run(cmd, *args, **kwargs):
                    idx = cmd.index("-o")
                    out_path = Path(cmd[idx + 1])
                    out_path.write_text('<svg>MOCK</svg>', encoding="utf-8")
                    mock_res = MagicMock()
                    mock_res.returncode = 0
                    return mock_res

                mock_run.side_effect = fake_run
                sucesso = gerar_svg_mermaid("flowchart TD\n A --> B", caminho_svg, config_puppeteer)
                self.assertTrue(sucesso)
                self.assertTrue(caminho_svg.exists())
                self.assertEqual(caminho_svg.read_text(encoding="utf-8"), '<svg>MOCK</svg>')

                # Verificar argumentos da chamada do subprocesso
                args, kwargs = mock_run.call_args
                cmd = args[0]
                self.assertIn("npx", cmd)
                self.assertIn("@mermaid-js/mermaid-cli", cmd)
                self.assertIn("-p", cmd)
                self.assertIn("-b", cmd)
                self.assertIn("transparent", cmd)
                self.assertIn("-t", cmd)
                self.assertIn("dark", cmd)


if __name__ == "__main__":
    unittest.main()
