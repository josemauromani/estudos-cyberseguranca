"""Garante o nome do projeto e a ausência do nome do autor no repositório."""
import subprocess
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
PROIBIDOS = ("José Mauro", "Brandão", "Stelling", "Estudos de Cibersegurança", "Estudos em Cibersegurança")
PREFIXOS_IGNORADOS = ("docs/superpowers/", ".agents/", "perfis-linkedin/", ".superpowers/")
ESTE_ARQUIVO = "_geradores/testes/test_marca.py"


def listar_arquivos():
    saida = subprocess.run(
        ["git", "ls-files"], cwd=RAIZ, capture_output=True, text=True, check=True
    ).stdout
    return [
        caminho
        for caminho in saida.splitlines()
        if caminho != ESTE_ARQUIVO and not caminho.startswith(PREFIXOS_IGNORADOS)
    ]


def ler_texto(caminho):
    try:
        return (RAIZ / caminho).read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None


class TestMarca(unittest.TestCase):
    def test_sem_nome_antigo_nem_autor(self):
        achados = []
        for caminho in listar_arquivos():
            texto = ler_texto(caminho)
            if texto is None:
                continue
            achados.extend(f"{caminho}: {t}" for t in PROIBIDOS if t in texto)
        self.assertEqual(achados, [], "Termos proibidos encontrados:\n" + "\n".join(achados))

    def test_nome_novo_presente(self):
        self.assertIn("# Mapa da Cibersegurança", ler_texto("README.md"))
        self.assertIn("Mapa da Cibersegurança", ler_texto("index.html"))
        modulo = ler_texto("Fundamentos-Ciber/treinamento-fundamentos-ciber.html")
        self.assertRegex(modulo, r"— Mapa da Cibersegurança</title>")

    def test_varredura_ignora_a_si_mesma_e_binarios(self):
        arquivos = listar_arquivos()
        self.assertNotIn(ESTE_ARQUIVO, arquivos)
        for caminho in arquivos:
            ler_texto(caminho)  # não deve levantar erro (inclui .woff2)


if __name__ == "__main__":
    unittest.main()
