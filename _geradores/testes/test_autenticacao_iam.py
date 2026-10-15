#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_autenticacao_iam.py
Testes automatizados para o Estudo 04: Autenticacao-e-IAM
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402


class TestAutenticacaoIAM(unittest.TestCase):
    """Valida a estrutura, conteúdo e compilação do estudo Autenticacao-e-IAM."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "autenticacao_e_iam_body.html"
        self.compiled_path = self.root / "Autenticacao-e-IAM" / "treinamento-autenticacao-e-iam.html"
        self.portal_path = self.root / "index.html"

    def test_body_and_compiled_files_exist(self):
        """Verifica se o fragmento body e o treinamento final compilado existem."""
        self.assertTrue(self.body_path.exists(), "O arquivo _geradores/autenticacao_e_iam_body.html deve existir.")
        self.assertTrue(self.compiled_path.exists(), "O arquivo Autenticacao-e-IAM/treinamento-autenticacao-e-iam.html deve existir.")

    def test_teoria_e_conceitos_fundamentais(self):
        """Verifica se os conceitos obrigatórios de IAM, senhas, MFA, OAuth, JWT, RBAC e ABAC estão presentes."""
        self.assertTrue(self.compiled_path.exists())
        content = self.compiled_path.read_text(encoding="utf-8")

        termos_obrigatorios = [
            "IAAA",
            "Menor Privilégio",
            "Argon2",
            "bcrypt",
            "TOTP",
            "FIDO2",
            "WebAuthn",
            "OAuth 2.0",
            "PKCE",
            "OpenID Connect",
            "JWT",
            "Header",
            "Payload",
            "Signature",
            "RBAC",
            "ABAC",
        ]
        for termo in termos_obrigatorios:
            self.assertIn(termo, content, f"O termo obrigatório '{termo}' deve estar presente no conteúdo.")

    def test_simulador_lab_jwt_e_rbac(self):
        """Verifica se o laboratório interativo com decodificador JWT e matriz RBAC está estruturado no HTML."""
        self.assertTrue(self.compiled_path.exists())
        content = self.compiled_path.read_text(encoding="utf-8")

        self.assertIn("jwt-rbac-lab", content)
        self.assertIn("decodificarTokenJwt", content)
        self.assertIn("injetarAtaqueNone", content)
        self.assertIn("avaliarPermissoesRbac", content)
        self.assertIn("assinarTokenSimulado", content)

    def test_componentes_pedagogicos(self):
        """Verifica a presença de checklists, quizzes e callouts padronizados."""
        self.assertTrue(self.compiled_path.exists())
        content = self.compiled_path.read_text(encoding="utf-8")

        self.assertIn('class="callout', content)
        self.assertIn('class="checklist', content)
        self.assertIn('class="quiz-item', content)
        self.assertIn('class="facts-grid', content)
        self.assertTrue(
            "initChecklist('autenticacao-iam')" in content or 'initChecklist("autenticacao-iam")' in content,
            "Chamada initChecklist('autenticacao-iam') deve estar presente no script."
        )

    def test_integracao_com_portal_index(self):
        """Verifica se o portal index.html aponta Autenticacao-e-IAM como Disponível com link ativo."""
        self.assertTrue(self.portal_path.exists())
        content = self.portal_path.read_text(encoding="utf-8")

        self.assertIn("Autenticacao-e-IAM/treinamento-autenticacao-e-iam.html", content)
        self.assertIn('data-slug="Autenticacao-e-IAM"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)
        self.assertIn("Módulos Compilados", content)


if __name__ == "__main__":
    unittest.main()
