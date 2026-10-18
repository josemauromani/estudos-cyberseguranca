"""Testes unitários para o compilador de treinamentos standalone (montar.py)."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Adiciona o diretório _geradores ao sys.path para importação
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    from montar import (
        carregar_catalogo_estudos,
        encontrar_estudo_por_slug_ou_arquivo,
        montar_treinamento,
    )
except ImportError:
    carregar_catalogo_estudos = None
    encontrar_estudo_por_slug_ou_arquivo = None
    montar_treinamento = None


class TestMontar(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.geradores_dir = self.root / "_geradores"
        self.montar_py = self.geradores_dir / "montar.py"

    def test_montar_treinamento_creates_standalone_html(self):
        """Verifica a compilação completa de um treinamento standalone com inlining de assets."""
        self.assertIsNotNone(montar_treinamento, "montar_treinamento deve ser importável de montar.py")

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            body = tmp_path / "teste_body.html"
            body.write_text(
                "<section class=\"intro\"><h1>Conteúdo de Teste</h1><p>Parágrafo de teste prático.</p></section>",
                encoding="utf-8",
            )

            output = tmp_path / "treinamento-teste.html"
            res = montar_treinamento(
                body_html_path=body,
                output_path=output,
                titulo="Treinamento Teste",
                meta={"slug": "teste-ciber", "trilha": "1"},
            )

            self.assertIsInstance(res, Path, "montar_treinamento deve retornar uma instância de Path")
            self.assertTrue(res.exists(), "O arquivo HTML de saída deve existir")
            self.assertEqual(res.resolve(), output.resolve(), "Path retornado deve corresponder ao caminho de saída")

            content = res.read_text(encoding="utf-8")

            # Estrutura HTML5 e cabeçalho semântico
            self.assertIn("<!DOCTYPE html>", content)
            self.assertIn('<html lang="pt-BR">', content)
            self.assertIn('<meta charset="UTF-8">', content)
            self.assertIn('name="viewport"', content)
            self.assertIn("Treinamento Teste", content)
            self.assertIn("Conteúdo de Teste", content)

            # Inlining de CSS e JS
            self.assertIn("<style>", content)
            self.assertIn("</style>", content)
            self.assertIn("--ground", content)
            self.assertIn("--t1-blue", content)

            self.assertIn("<script>", content)
            self.assertIn("</script>", content)
            self.assertIn("initTheme", content)
            self.assertIn("initChecklist", content)

            # Elementos de navegação e acessibilidade
            self.assertIn('data-slug="teste-ciber"', content)
            self.assertIn('href="../index.html"', content)
            self.assertIn("← Painel de Estudos", content)
            self.assertIn("theme-toggle-btn", content)
            self.assertIn("Trilha 1", content)

            # Rodapé com créditos
            self.assertIn("study-footer", content)
            self.assertIn("José Mauro da Silva Brandão", content)

    def test_montar_treinamento_creates_missing_parent_dirs(self):
        """Verifica se o compilador cria automaticamente diretórios pais inexistentes."""
        self.assertIsNotNone(montar_treinamento, "montar_treinamento deve ser importável")

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            body = tmp_path / "teste_body.html"
            body.write_text("<p>Teste de diretório aninhado.</p>", encoding="utf-8")

            nested_output = tmp_path / "nova_pasta" / "subpasta" / "treinamento.html"
            res = montar_treinamento(body, nested_output, titulo="Treinamento Aninhado")

            self.assertTrue(res.exists())
            self.assertTrue(res.parent.exists())

    def test_carregar_catalogo_estudos(self):
        """Verifica se carregar_catalogo_estudos faz o parse correto de estudos.txt."""
        self.assertIsNotNone(carregar_catalogo_estudos, "carregar_catalogo_estudos deve ser importável")

        catalogo = carregar_catalogo_estudos()
        self.assertIsInstance(catalogo, dict)
        self.assertGreaterEqual(len(catalogo), 28)
        self.assertIn("Fundamentos-Ciber", catalogo)

        item = catalogo["Fundamentos-Ciber"]
        self.assertEqual(item["slug"], "Fundamentos-Ciber")
        self.assertEqual(item["pasta"], "Fundamentos-Ciber")
        self.assertEqual(item["trilha_num"], "1")
        self.assertEqual(item["cor_tema"], "#2563EB")
        self.assertEqual(item["nist_fn"], "Identify")

    def test_encontrar_estudo_por_slug_ou_arquivo(self):
        """Verifica a busca flexível de estudos por slug, nome de pasta ou arquivo body."""
        self.assertIsNotNone(encontrar_estudo_por_slug_ou_arquivo, "encontrar_estudo deve ser importável")

        estudo1 = encontrar_estudo_por_slug_ou_arquivo("Fundamentos-Ciber")
        self.assertIsNotNone(estudo1)
        self.assertEqual(estudo1["slug"], "Fundamentos-Ciber")

        # Busca via formato snake_case do body: fundamentos_ciber_body.html
        estudo2 = encontrar_estudo_por_slug_ou_arquivo("fundamentos_ciber_body.html")
        self.assertIsNotNone(estudo2)
        self.assertEqual(estudo2["slug"], "Fundamentos-Ciber")

        # Busca via nome simples
        estudo3 = encontrar_estudo_por_slug_ou_arquivo("redes_e_protocolos")
        self.assertIsNotNone(estudo3)
        self.assertEqual(estudo3["slug"], "Redes-e-Protocolos")

    def test_montar_treinamento_resolves_metadata_from_estudos_txt(self):
        """Verifica se metadados são resolvidos automaticamente a partir do nome do arquivo body."""
        self.assertIsNotNone(montar_treinamento, "montar_treinamento deve ser importável")

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            body = tmp_path / "fundamentos_ciber_body.html"
            body.write_text("<p>Fragmento de teste para Fundamentos-Ciber.</p>", encoding="utf-8")

            output = tmp_path / "treinamento-fundamentos-ciber.html"
            res = montar_treinamento(body, output)

            content = res.read_text(encoding="utf-8")
            self.assertIn('data-slug="Fundamentos-Ciber"', content)
            self.assertIn("Tríade CIA, Ameaças e Modelagem STRIDE", content)
            self.assertIn("Trilha 1", content)

    def test_cli_execution(self):
        """Verifica a execução de montar.py como script de linha de comando."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            body = tmp_path / "criptografia_pratica_body.html"
            body.write_text("<section><h1>Criptografia</h1></section>", encoding="utf-8")

            output = tmp_path / "saida-cli.html"

            cmd = [
                sys.executable,
                str(self.montar_py),
                str(body),
                str(output),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, f"CLI falhou: {result.stderr}")
            self.assertTrue(output.exists(), "Arquivo compilado via CLI deve existir")
            content = output.read_text(encoding="utf-8")
            self.assertIn("<!DOCTYPE html>", content)
            self.assertIn("Criptografia Simétrica, Assimétrica", content)

    def test_montar_treinamento_com_diagrama_mermaid(self):
        """Verifica a integração e pré-compilação de diagramas Mermaid em montar_treinamento."""
        self.assertIsNotNone(montar_treinamento, "montar_treinamento deve ser importável")

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            body = tmp_path / "diagrama_body.html"
            body.write_text(
                '<pre class="mermaid" data-title="Teste">flowchart TD\nA-->B</pre>',
                encoding="utf-8",
            )

            output = tmp_path / "treinamento-diagrama.html"
            res = montar_treinamento(
                body_html_path=body,
                output_path=output,
                titulo="Treinamento com Diagrama",
            )

            self.assertTrue(res.exists())
            content = res.read_text(encoding="utf-8")

            self.assertIn("diagram-box", content)
            self.assertIn("diagram-header", content)
            self.assertIn("Teste", content)
            self.assertIn("diagram-svg-wrap", content)
            self.assertIn("<svg", content)

    def test_cli_com_recompilar_diagramas(self):
        """Verifica a execução do CLI com flag --recompilar-diagramas."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            body = tmp_path / "diagrama_cli_body.html"
            body.write_text(
                '<pre class="mermaid" data-title="CLI Teste">flowchart LR\nA-->B</pre>',
                encoding="utf-8",
            )
            output = tmp_path / "saida-cli-diagrama.html"

            cmd = [
                sys.executable,
                str(self.montar_py),
                str(body),
                str(output),
                "--recompilar-diagramas",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, f"CLI falhou: {result.stderr}")
            self.assertTrue(output.exists())
            content = output.read_text(encoding="utf-8")
            self.assertIn("diagram-box", content)
            self.assertIn("CLI Teste", content)
            self.assertIn("<svg", content)


if __name__ == "__main__":
    unittest.main()
