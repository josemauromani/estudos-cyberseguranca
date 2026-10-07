"""Testes unitários para o gerador do Portal Central (build_index.py e index_dados.py)."""

import os
import sys
import unittest
from pathlib import Path

# Adiciona o diretório _geradores ao sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from build_index import gerar_index_html
from index_dados import CARREIRAS, ESTUDOS_DADOS, FUNCOES_NIST, NECESSIDADES, TRILHAS


class TestIndexDados(unittest.TestCase):
    """Testa a integridade e completude dos metadados ricos em index_dados.py."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.estudos_txt = self.root / "_geradores" / "estudos.txt"

    def test_estudos_dados_has_28_entries(self):
        """Verifica se ESTUDOS_DADOS possui exatamente 28 estudos."""
        self.assertEqual(len(ESTUDOS_DADOS), 28, "ESTUDOS_DADOS deve conter exatamente 28 estudos.")

    def test_estudos_slugs_match_estudos_txt_exactly(self):
        """Verifica se todos os 28 slugs em ESTUDOS_DADOS coincidem exatamente com estudos.txt."""
        self.assertTrue(self.estudos_txt.exists(), "estudos.txt deve existir.")
        slugs_txt = set()
        for linha in self.estudos_txt.read_text(encoding="utf-8").splitlines():
            linha = linha.strip()
            if linha and not linha.startswith("#"):
                slug = linha.split("|")[0].strip()
                slugs_txt.add(slug)

        self.assertEqual(len(slugs_txt), 28)
        self.assertEqual(
            set(ESTUDOS_DADOS.keys()),
            slugs_txt,
            f"Slugs divergentes entre index_dados.py e estudos.txt: {set(ESTUDOS_DADOS.keys()) ^ slugs_txt}",
        )

    def test_estudos_dados_schema_fields(self):
        """Verifica se cada estudo possui todos os campos obrigatórios com tipos corretos."""
        required_fields = {
            "titulo": str,
            "subtitulo": str,
            "trilha": int,
            "nist": str,
            "mitre": str,
            "carreiras": list,
            "tempo_minutos": int,
            "pergunta_chave": str,
            "simulador_nome": str,
            "fatos": list,
        }
        for slug, dados in ESTUDOS_DADOS.items():
            for campo, tipo in required_fields.items():
                self.assertIn(campo, dados, f"Estudo '{slug}' ausente de campo obrigatório: '{campo}'")
                self.assertIsInstance(
                    dados[campo],
                    tipo,
                    f"Campo '{campo}' no estudo '{slug}' deve ser do tipo {tipo.__name__}, obteve {type(dados[campo]).__name__}",
                )
            self.assertTrue(1 <= dados["trilha"] <= 6, f"Trilha inválida em {slug}: {dados['trilha']}")
            self.assertGreater(dados["tempo_minutos"], 0, f"Tempo deve ser positivo em {slug}")
            self.assertTrue(len(dados["carreiras"]) > 0, f"Lista de carreiras vazia em {slug}")
            self.assertTrue(len(dados["fatos"]) > 0, f"Lista de fatos vazia em {slug}")

    def test_trilhas_definition(self):
        """Verifica se as 6 trilhas estruturantes estão cadastradas com cor e descrição."""
        self.assertEqual(len(TRILHAS), 6, "TRILHAS deve ter exatamente 6 registros.")
        for tid in range(1, 7):
            self.assertIn(tid, TRILHAS, f"Trilha ID {tid} ausente em TRILHAS.")
            info = TRILHAS[tid]
            self.assertEqual(info["id"], tid)
            self.assertTrue(len(info["nome"]) > 0)
            self.assertTrue(info["cor"].startswith("#"))
            self.assertTrue(len(info["descricao"]) > 0)

    def test_carreiras_and_funcoes_nist(self):
        """Verifica perfis profissionais e funções NIST CSF 2.0."""
        self.assertGreaterEqual(len(CARREIRAS), 5, "Deve haver ao menos 5 carreiras estruturadas.")
        nist_funcoes_esperadas = {"Govern", "Identify", "Protect", "Detect", "Respond", "Recover"}
        self.assertEqual(set(FUNCOES_NIST.keys()), nist_funcoes_esperadas)

    def test_necessidades_list(self):
        """Verifica se a lista de desafios práticos/necessidades mapeia slugs válidos."""
        self.assertGreaterEqual(len(NECESSIDADES), 10, "Deve haver pelo menos 10 necessidades mapeadas.")
        slugs_validos = set(ESTUDOS_DADOS.keys())
        for item in NECESSIDADES:
            self.assertIn("desafio", item)
            self.assertIn("slug", item)
            self.assertIn(item["slug"], slugs_validos, f"Slug inválido em necessidade: {item['slug']}")


class TestBuildIndex(unittest.TestCase):
    """Testa a geração e conteúdo do portal central index.html."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.output_index = self.root / "index.html"

    def test_gerar_index_creates_valid_portal(self):
        """Testa geração de index.html com estatísticas, busca, filtros e acessibilidade."""
        gerado = gerar_index_html(output_path=self.output_index)
        self.assertTrue(self.output_index.exists(), "index.html deve existir na raiz.")
        self.assertEqual(gerado, self.output_index)

        conteudo = self.output_index.read_text(encoding="utf-8")

        # Metadados e cabeçalho
        self.assertIn("<!DOCTYPE html>", conteudo)
        self.assertIn("Estudos de Cibersegurança", conteudo)
        self.assertIn("José Mauro da Silva Brandão", conteudo)

        # Estatísticas do masthead
        self.assertIn("28", conteudo)  # 28 estudos
        self.assertIn("6", conteudo)   # 6 trilhas
        self.assertIn("simuladores", conteudo.lower())

        # Seções principais
        self.assertTrue(
            "escolha pela necessidade" in conteudo.lower() or "por necessidade" in conteudo.lower(),
            "Seção de necessidades deve estar presente",
        )
        self.assertIn("STRIDE", conteudo)
        self.assertIn("search-input", conteudo)

        # Suporte a temas e persistência segura
        self.assertIn("data-theme", conteudo)
        self.assertIn("localStorage", conteudo)
        self.assertIn("safeStorageGet", conteudo)
        self.assertIn("safeStorageSet", conteudo)
        self.assertIn("cs_done_", conteudo)
        self.assertIn("cs_theme", conteudo)

        # Filtros interativos e busca com remoção de acentos
        self.assertIn("filtro", conteudo.lower())
        self.assertIn("removerAcentos", conteudo)
        self.assertIn("card", conteudo)
        self.assertIn("highlight-pulse", conteudo)
        self.assertIn("pulseHighlight", conteudo)


if __name__ == "__main__":
    unittest.main()
