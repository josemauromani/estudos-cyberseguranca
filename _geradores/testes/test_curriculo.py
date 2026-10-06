"""Testes de integridade do catálogo curricular e documentação pedagógica."""

import unittest
from pathlib import Path


class TestCurriculo(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.estudos_file = self.root / "_geradores" / "estudos.txt"
        self.curriculo_file = self.root / "_geradores" / "CURRICULO.md"
        self.guia_file = self.root / "_geradores" / "GUIA-DO-AUTOR.md"

    def test_estudos_txt_contains_28_valid_entries(self):
        """Verifica se estudos.txt existe e possui exatamente 28 registros válidos com 7 campos."""
        self.assertTrue(self.estudos_file.exists(), "estudos.txt deve existir")

        lines = [
            line.strip()
            for line in self.estudos_file.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        ]
        self.assertEqual(len(lines), 28, f"Esperava 28 estudos, encontrou {len(lines)}")

        slugs = set()
        for line in lines:
            parts = [p.strip() for p in line.split("|")]
            self.assertEqual(len(parts), 7, f"Linha inválida (esperado 7 campos): {line}")
            slug, titulo, pasta, arq, trilha, cor, nist = parts

            self.assertNotIn(slug, slugs, f"Slug duplicado: {slug}")
            slugs.add(slug)

            self.assertTrue(
                1 <= int(trilha) <= 6, f"Trilha inválida em {slug}: {trilha} (deve ser 1 a 6)"
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


if __name__ == "__main__":
    unittest.main()
