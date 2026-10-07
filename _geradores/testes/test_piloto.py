"""Testes unitários para o Módulo Piloto: Fundamentos-Ciber (treinamento e simulador STRIDE)."""

import unittest
from pathlib import Path


class TestModuloPiloto(unittest.TestCase):
    """Valida a integridade, conteúdo didático e interatividade do módulo piloto."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.piloto_html = self.root / "Fundamentos-Ciber" / "treinamento-fundamentos-ciber.html"
        self.body_html = self.root / "_geradores" / "fundamentos_ciber_body.html"
        self.index_html = self.root / "index.html"

    def test_piloto_arquivo_compilado_existe(self):
        """Verifica se o treinamento piloto compilado existe no destino esperado."""
        self.assertTrue(
            self.piloto_html.exists(),
            f"Arquivo compilado não encontrado: {self.piloto_html}",
        )
        self.assertGreater(
            self.piloto_html.stat().st_size,
            5000,
            "Arquivo compilado deve ter tamanho substancial com conteúdo e assets inlined.",
        )

    def test_piloto_teoria_e_conceitos_fundamentais(self):
        """Verifica se a fundamentação teórica contém os pilares CIA, DAD e defesa em profundidade."""
        self.assertTrue(self.piloto_html.exists(), "Treinamento piloto deve existir para teste de conteúdo.")
        content = self.piloto_html.read_text(encoding="utf-8")

        termos_obrigatorios = [
            "Tríade CIA",
            "Confidencialidade",
            "Integridade",
            "Disponibilidade",
            "Divulgação",
            "Alteração",
            "Destruição",
            "Menor Privilégio",
            "Defesa em Profundidade",
        ]
        for termo in termos_obrigatorios:
            self.assertIn(
                termo.lower(),
                content.lower(),
                f"Termo conceitual obrigatório ausente: '{termo}'",
            )

    def test_piloto_categorias_stride_completas(self):
        """Verifica se todas as 6 categorias da metodologia STRIDE e mitigações estão presentes."""
        self.assertTrue(self.piloto_html.exists(), "Treinamento piloto deve existir para teste de STRIDE.")
        content = self.piloto_html.read_text(encoding="utf-8")

        categorias_stride = [
            "Spoofing",
            "Tampering",
            "Repudiation",
            "Information Disclosure",
            "Denial of Service",
            "Elevation of Privilege",
        ]
        for cat in categorias_stride:
            self.assertIn(
                cat.lower(),
                content.lower(),
                f"Categoria STRIDE ausente no conteúdo: '{cat}'",
            )

    def test_piloto_componentes_design_system(self):
        """Verifica a presença dos componentes canônicos (.callout, .lab-box, .checklist, .quiz-item)."""
        self.assertTrue(self.piloto_html.exists(), "Treinamento piloto deve existir para teste de componentes.")
        content = self.piloto_html.read_text(encoding="utf-8")

        componentes = [
            "hero-header",
            "callout",
            "lab-box",
            "checklist",
            "quiz-item",
            "terminal-box",
            "facts-grid",
        ]
        for comp in componentes:
            self.assertIn(
                comp,
                content,
                f"Classe de componente CSS obrigatória ausente no HTML: '{comp}'",
            )

    def test_piloto_simulador_stride_canvas_interativo(self):
        """Verifica se o Simulador STRIDE Canvas interativo possui elementos de controle e script JS."""
        self.assertTrue(self.piloto_html.exists(), "Treinamento piloto deve existir para teste do simulador.")
        content = self.piloto_html.read_text(encoding="utf-8")

        self.assertIn("STRIDE Canvas", content, "O título do simulador STRIDE Canvas deve estar presente.")
        self.assertIn("<script>", content, "Treinamento deve conter bloco de script para o simulador.")

        # Elementos interativos do simulador
        termos_simulador = [
            "stride-asset-select",
            "stride-threats-container",
            "stride-summary",
            "selecionarAtivo",
        ]
        for termo in termos_simulador:
            self.assertIn(
                termo,
                content,
                f"Elemento/função interativa do simulador STRIDE ausente: '{termo}'",
            )

    def test_portal_index_integra_modulo_piloto_disponivel(self):
        """Verifica se index.html reflete o status 'Disponível' com link ativo para o módulo piloto."""
        self.assertTrue(self.index_html.exists(), "index.html deve existir.")
        content = self.index_html.read_text(encoding="utf-8")

        self.assertIn(
            "Fundamentos-Ciber/treinamento-fundamentos-ciber.html",
            content,
            "index.html deve conter link relativo ativo para o módulo piloto compilado.",
        )
        self.assertIn(
            "Disponível",
            content,
            "index.html deve exibir badge 'Disponível' para o estudo piloto.",
        )


if __name__ == "__main__":
    unittest.main()
