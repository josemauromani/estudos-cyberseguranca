"""Testes de integridade do catálogo curricular e documentação pedagógica."""

import unittest
from pathlib import Path


class TestCurriculo(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.estudos_file = self.root / "_geradores" / "estudos.txt"
        self.curriculo_file = self.root / "_geradores" / "CURRICULO.md"
        self.guia_file = self.root / "_geradores" / "GUIA-DO-AUTOR.md"

    def test_estudos_txt_contains_33_valid_entries(self):
        """Verifica se estudos.txt existe e possui exatamente 33 registros válidos com 7 campos."""
        self.assertTrue(self.estudos_file.exists(), "estudos.txt deve existir")

        lines = [
            line.strip()
            for line in self.estudos_file.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        ]
        self.assertEqual(len(lines), 33, f"Esperava 33 estudos, encontrou {len(lines)}")

        slugs = set()
        for line in lines:
            parts = [p.strip() for p in line.split("|")]
            self.assertEqual(len(parts), 7, f"Linha inválida (esperado 7 campos): {line}")
            slug, titulo, pasta, arq, trilha, cor, nist = parts

            self.assertNotIn(slug, slugs, f"Slug duplicado: {slug}")
            slugs.add(slug)

            self.assertTrue(
                1 <= int(trilha) <= 7, f"Trilha inválida em {slug}: {trilha} (deve ser 1 a 7)"
            )
            self.assertTrue(
                cor.startswith("#"), f"Cor inválida em {slug}: {cor} (deve iniciar com #)"
            )
            self.assertTrue(len(titulo) > 0, f"Título curto vazio em {slug}")
            self.assertTrue(len(pasta) > 0, f"Pasta vazia em {slug}")
            self.assertTrue(
                arq.endswith(".html"), f"Arquivo HTML deve terminar em .html em {slug}: {arq}"
            )
            self.assertTrue(len(nist) > 0, f"NIST function vazia em {slug}")

    def test_curriculo_cobre_33_modulos_e_rota(self):
        """CURRICULO.md cita todos os slugs, a Trilha 7, a Rota 6 e os escopos ampliados."""
        txt = self.curriculo_file.read_text(encoding="utf-8")
        for linha in self.estudos_file.read_text(encoding="utf-8").splitlines():
            if linha.strip() and not linha.startswith("#"):
                self.assertIn(linha.split("|")[0].strip(), txt)
        self.assertIn("Trilha 7: Carreira & Formação", txt)
        self.assertIn("Rota 6: Analista de Segurança da Informação", txt)
        self.assertIn("ISO 31000", txt)
        self.assertIn("CIS Controls v8.1", txt)
        self.assertIn("800-61 Rev. 3", txt)

    def test_documentacao_pedagogica_exists(self):
        """Verifica se CURRICULO.md e GUIA-DO-AUTOR.md existem e têm conteúdo substancial."""
        self.assertTrue(self.curriculo_file.exists(), "CURRICULO.md deve existir")
        self.assertTrue(self.guia_file.exists(), "GUIA-DO-AUTOR.md deve existir")
        self.assertGreater(
            self.curriculo_file.stat().st_size, 1000, "CURRICULO.md deve conter conteúdo detalhado"
        )
        self.assertGreater(
            self.guia_file.stat().st_size, 1000, "GUIA-DO-AUTOR.md deve conter diretrizes completas"
        )

    def test_diagramas_mermaid_na_documentacao(self):
        """Verifica se README.md, CURRICULO.md e GUIA-DO-AUTOR.md possuem os diagramas e diretrizes Mermaid."""
        readme_file = self.root / "README.md"
        self.assertTrue(readme_file.exists(), "README.md deve existir")

        readme_txt = readme_file.read_text(encoding="utf-8")
        self.assertIn("```mermaid", readme_txt)
        self.assertIn("flowchart LR", readme_txt)
        self.assertIn("flowchart TD", readme_txt)
        self.assertIn("diagramas.py", readme_txt)
        self.assertIn("Rota Analista de Segurança da Informação", readme_txt)

        curriculo_txt = self.curriculo_file.read_text(encoding="utf-8")
        self.assertIn("```mermaid", curriculo_txt)
        self.assertIn("NIST CSF 2.0 (Funções Centrais)", curriculo_txt)
        self.assertIn("Govern (GV)", curriculo_txt)
        self.assertIn("Recover (RC)", curriculo_txt)

        guia_txt = self.guia_file.read_text(encoding="utf-8")
        self.assertIn("Diagramas Arquiteturais e Lógicos", guia_txt)
        self.assertIn('pre class="mermaid"', guia_txt)
        self.assertIn("cache_diagramas", guia_txt)
        self.assertIn("npx @mermaid-js/mermaid-cli", guia_txt)


if __name__ == "__main__":
    unittest.main()
