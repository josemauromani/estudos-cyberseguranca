#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes de Linha de Comando (CLI) e Documentação Principal
=========================================================
Valida a execução de _geradores/gerar.sh e a integridade do README.md raiz.
"""

from pathlib import Path
import os
import subprocess
import unittest

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
GERADORES_DIR = ROOT_DIR / "_geradores"
GERAR_SH = GERADORES_DIR / "gerar.sh"
README_MD = ROOT_DIR / "README.md"
ESTUDOS_TXT = GERADORES_DIR / "estudos.txt"


class TestCLI(unittest.TestCase):
    """Testes de validação do script mestre gerar.sh e do README.md."""

    def test_gerar_sh_is_executable_and_help(self):
        """Verifica se gerar.sh existe, tem permissão de execução e exibe ajuda."""
        self.assertTrue(GERAR_SH.exists(), f"Arquivo {GERAR_SH} não existe.")
        mode = GERAR_SH.stat().st_mode
        self.assertTrue(bool(mode & 0o111), "gerar.sh deve ter permissão de execução (chmod +x).")

        # Teste com argumento help
        result_help = subprocess.run(
            [str(GERAR_SH), "help"],
            cwd=str(ROOT_DIR),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result_help.returncode, 0, f"Falha ao executar gerar.sh help: {result_help.stderr}")
        self.assertIn("Uso:", result_help.stdout)
        self.assertIn("portal", result_help.stdout)
        self.assertIn("todos", result_help.stdout)

        # Teste com flag --help
        result_flag = subprocess.run(
            [str(GERAR_SH), "--help"],
            cwd=str(ROOT_DIR),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result_flag.returncode, 0)
        self.assertIn("Uso:", result_flag.stdout)

    def test_gerar_sh_portal(self):
        """Verifica se './_geradores/gerar.sh portal' regenera o index.html com sucesso."""
        self.assertTrue(GERAR_SH.exists(), "gerar.sh deve existir.")
        result = subprocess.run(
            [str(GERAR_SH), "portal"],
            cwd=str(ROOT_DIR),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, f"Erro na execução: {result.stderr}")
        saida = result.stdout.lower()
        self.assertTrue(
            "index.html gerado com sucesso" in result.stdout.lower() or "sucesso" in saida,
            f"Mensagem de sucesso esperada não encontrada na saída: {result.stdout}",
        )
        index_file = ROOT_DIR / "index.html"
        self.assertTrue(index_file.exists(), "index.html deve existir após execução de 'gerar.sh portal'.")

    def test_readme_contains_all_28_studies(self):
        """Verifica se README.md existe e contém referências a todos os 28 estudos."""
        self.assertTrue(README_MD.exists(), "README.md raiz deve existir.")
        readme_content = README_MD.read_text(encoding="utf-8")

        self.assertTrue(ESTUDOS_TXT.exists(), "estudos.txt deve existir.")
        estudos_linhas = [
            l.strip()
            for l in ESTUDOS_TXT.read_text(encoding="utf-8").splitlines()
            if l.strip() and not l.strip().startswith("#")
        ]
        self.assertEqual(len(estudos_linhas), 28, "Devem existir exatamente 28 estudos no catálogo.")

        # Verifica presença de cada estudo no README (por slug ou título)
        faltantes = []
        for linha in estudos_linhas:
            partes = [p.strip() for p in linha.split("|")]
            slug = partes[0]
            titulo = partes[1]
            if slug not in readme_content and titulo not in readme_content:
                faltantes.append(f"{slug} ({titulo})")

        self.assertEqual(
            faltantes,
            [],
            f"Os seguintes estudos não foram encontrados no README.md: {faltantes}",
        )

        # Verifica menções estruturais obrigatórias
        self.assertIn("Estudos de Cibersegurança", readme_content)
        self.assertIn("gerar.sh", readme_content)
        self.assertIn("index.html", readme_content)
        self.assertIn("NIST CSF 2.0", readme_content)

    def test_gerar_sh_todos(self):
        """Verifica a execução de './_geradores/gerar.sh todos'."""
        result = subprocess.run(
            [str(GERAR_SH), "todos"],
            cwd=str(ROOT_DIR),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, f"Erro na execução: {result.stderr}")
        self.assertIn("index.html gerado com sucesso", result.stdout)

    def test_gerar_sh_slug_inexistente(self):
        """Verifica se passar um slug sem fragmento body retorna erro e código diferente de zero."""
        result = subprocess.run(
            [str(GERAR_SH), "slug_inexistente_xyz_123"],
            cwd=str(ROOT_DIR),
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ERRO", result.stderr)

    def test_gerar_sh_slug_compilacao(self):
        """Verifica a compilação de um estudo específico quando seu fragmento body existe."""
        dummy_body = GERADORES_DIR / "dummy_teste_body.html"
        dummy_out = ROOT_DIR / "treinamento-dummy_teste.html"
        dummy_body.write_text("<section><h2>Teste Dummy</h2><p>Conteúdo de teste</p></section>", encoding="utf-8")
        self.addCleanup(lambda: dummy_body.unlink(missing_ok=True))
        self.addCleanup(lambda: dummy_out.unlink(missing_ok=True))

        result = subprocess.run(
            [str(GERAR_SH), "dummy_teste"],
            cwd=str(ROOT_DIR),
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, f"Erro na execução: {result.stderr}")
        self.assertIn("index.html gerado com sucesso", result.stdout)


if __name__ == "__main__":
    unittest.main()
