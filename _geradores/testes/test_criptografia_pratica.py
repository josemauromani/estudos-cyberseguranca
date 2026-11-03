#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_criptografia_pratica.py
Testes automatizados para o Estudo 03: Criptografia-Pratica
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402


class TestCriptografiaPratica(unittest.TestCase):
    """Valida a estrutura, conteúdo e compilação do estudo Criptografia-Pratica."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "criptografia_pratica_body.html"
        self.compiled_path = self.root / "Criptografia-Pratica" / "treinamento-criptografia-pratica.html"
        self.portal_path = self.root / "index.html"

    def test_body_and_compiled_files_exist(self):
        """Verifica se o fragmento body e o treinamento final compilado existem."""
        self.assertTrue(self.body_path.exists(), "O arquivo _geradores/criptografia_pratica_body.html deve existir.")
        self.assertTrue(self.compiled_path.exists(), "O arquivo Criptografia-Pratica/treinamento-criptografia-pratica.html deve existir.")

    def test_teoria_e_conceitos_fundamentais(self):
        """Verifica se os conceitos obrigatórios de criptografia simétrica, assimétrica, hashes e PKI estão presentes."""
        self.assertTrue(self.compiled_path.exists())
        content = self.compiled_path.read_text(encoding="utf-8")

        termos_obrigatorios = [
            "Kerckhoffs",
            "AES",
            "GCM",
            "RSA",
            "Curvas Elípticas",
            "Diffie-Hellman",
            "SHA-256",
            "Argon2",
            "X.509",
            "Autoridade Certificadora",
            "OCSP",
            "Forward Secrecy",
        ]
        for termo in termos_obrigatorios:
            self.assertIn(termo, content, f"O termo obrigatório '{termo}' deve estar presente no conteúdo.")

    def test_simulador_lab_cifras_web_crypto(self):
        """Verifica se o laboratório interativo com Web Crypto API está estruturado no HTML."""
        self.assertTrue(self.compiled_path.exists())
        content = self.compiled_path.read_text(encoding="utf-8")

        self.assertIn("crypto-lab", content)
        self.assertIn("calcularHashReal", content)
        self.assertIn("cifrarAesGcm", content)
        self.assertIn("decifrarAesGcm", content)
        self.assertIn("window.crypto.subtle", content)

    def test_componentes_pedagogicos(self):
        """Verifica a presença de checklists, quizzes e callouts padronizados."""
        self.assertTrue(self.compiled_path.exists())
        content = self.compiled_path.read_text(encoding="utf-8")

        self.assertIn('class="callout', content)
        self.assertIn('class="checklist', content)
        self.assertIn('class="quiz-item', content)
        self.assertIn('class="facts-grid', content)
        self.assertIn("initChecklist('criptografia-pratica')", content)
        self.assertGreaterEqual(content.count('class="quiz-item'), 4)

    def test_secao_ciclo_de_certificados(self):
        """A seção de ciclo de vida de certificados fica logo antes do laboratório."""
        body = self.body_path.read_text(encoding="utf-8")
        abertura = '<section class="study-section" id="ciclo-de-certificados" data-tipo="teoria">'
        self.assertIn(abertura, body)
        ini = body.index(abertura)
        fim = body.index("</section>", ini)
        secao = body[ini:fim]
        resto = body[fim + len("</section>"):]
        self.assertIn('id="laboratorio-cripto"', resto.split("<section", 1)[1].split(">", 1)[0])
        for termo in [
            "CLM", "ACME", "RFC 8555", "SC-081",
            "15 de março de 2026", "200 dias", "15 de março de 2027", "100 dias",
            "15 de março de 2029", "47 dias", "398 dias", "10 dias",
            "CBOM", "FIPS 203", "ML-KEM", "FIPS 204", "ML-DSA", "FIPS 205", "SLH-DSA",
            "agosto de 2024", "colher agora, decifrar depois", "cripto-agilidade",
        ]:
            self.assertIn(termo, secao, f"A seção deve conter '{termo}'.")

    def test_referencias_clm(self):
        """Os fatos essenciais citam as fontes oficiais do ciclo de certificados."""
        body = self.body_path.read_text(encoding="utf-8")
        fatos = body[body.index('id="fatos-essenciais"'):]
        for termo in ["cabforum.org", "RFC 8555", "csrc.nist.gov"]:
            self.assertIn(termo, fatos)

    def test_integracao_com_portal_index(self):
        """Verifica se o portal index.html aponta Criptografia-Pratica como Disponível com link ativo."""
        self.assertTrue(self.portal_path.exists())
        content = self.portal_path.read_text(encoding="utf-8")

        self.assertIn("Criptografia-Pratica/treinamento-criptografia-pratica.html", content)
        self.assertIn('data-slug="Criptografia-Pratica"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)
        self.assertIn("Módulos Compilados", content)


if __name__ == "__main__":
    unittest.main()
