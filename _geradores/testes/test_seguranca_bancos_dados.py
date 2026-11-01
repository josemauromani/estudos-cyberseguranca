#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_seguranca_bancos_dados.py
Testes automatizados para o Estudo 30: Seguranca-de-Bancos-de-Dados
"""

import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402

PRIVS = {"SELECT", "INSERT", "UPDATE", "DELETE"}


class TestSegurancaBancosDados(unittest.TestCase):
    """Valida a estrutura, o conteúdo e a compilação do estudo Seguranca-de-Bancos-de-Dados."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "seguranca_de_bancos_de_dados_body.html"
        self.compiled_path = self.root / "Seguranca-de-Bancos-de-Dados" / "treinamento-seguranca-de-bancos-de-dados.html"
        self.portal_path = self.root / "index.html"

    def _dados(self):
        body = self.body_path.read_text(encoding="utf-8")
        m = re.search(r'<script type="application/json" id="bd-dados">(.*?)</script>', body, re.S)
        self.assertIsNotNone(m, "Bloco JSON #bd-dados ausente no body")
        return json.loads(m.group(1))

    @staticmethod
    def _permitida(politica, role, acao, tabela):
        return acao in politica.get(role, {}).get(tabela, [])

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        termos = [
            "ACID", "DDL", "DML", "DCL", "GRANT", "REVOKE", "PUBLIC", "PostgreSQL 15",
            "Row-Level Security", "CREATE POLICY", "pgAudit", "SQL Server Audit",
            "Database Activity Monitoring", "TDE", "pgcrypto", "Dynamic Data Masking",
            "prepared statements", "CIS Benchmarks", "scram-sha-256", "OWASP",
        ]
        for termo in termos:
            self.assertIn(termo, content, f"Termo obrigatório ausente: {termo}")

    def test_esquema_e_roles(self):
        d = self._dados()
        self.assertEqual(set(d["tabelas"]), {"clientes", "pedidos", "pagamentos", "produtos"})
        self.assertEqual(set(d["roles"]), {"atendimento", "analista_bi", "financeiro", "app_loja"})
        for role, info in d["roles"].items():
            self.assertTrue(info["usuario"].strip(), role)
        self.assertIn(d["mascaramento"]["tabela"], d["tabelas"])
        self.assertIn(d["mascaramento"]["coluna"], d["tabelas"][d["mascaramento"]["tabela"]]["colunas"])
        self.assertIn(d["mascaramento"]["excecao"], d["roles"])

    def test_politicas_usam_roles_tabelas_e_privilegios_validos(self):
        d = self._dados()
        for nome in ("inicial", "alvo"):
            with self.subTest(politica=nome):
                for role, tabelas in d[nome].items():
                    self.assertIn(role, d["roles"])
                    for tabela, privs in tabelas.items():
                        self.assertIn(tabela, d["tabelas"])
                        self.assertLessEqual(set(privs), PRIVS)

    def test_estado_inicial_tem_privilegio_em_excesso(self):
        d = self._dados()
        excesso = [
            (r, t, p)
            for r, ts in d["inicial"].items() for t, ps in ts.items() for p in ps
            if not self._permitida(d["alvo"], r, p, t)
        ]
        self.assertGreaterEqual(len(excesso), 5, "o ponto de partida deve ser inseguro")
        self.assertIn("DELETE", d["inicial"]["app_loja"]["clientes"])
        self.assertIn("SELECT", d["inicial"]["analista_bi"]["pagamentos"])

    def test_consultas_e_resultado_esperado_no_alvo(self):
        d = self._dados()
        consultas = d["consultas"]
        self.assertEqual(len(consultas), 10)
        resultados = set()
        for q in consultas:
            with self.subTest(sql=q["sql"]):
                self.assertIn(q["role"], d["roles"])
                self.assertEqual(q["usuario"], d["roles"][q["role"]]["usuario"])
                self.assertIn(q["acao"], PRIVS)
                self.assertIn(q["tabela"], d["tabelas"])
                self.assertTrue(q["sql"].upper().startswith(q["acao"]))
                esperado = "permitida" if self._permitida(d["alvo"], q["role"], q["acao"], q["tabela"]) else "negada"
                self.assertEqual(q["esperado_no_alvo"], esperado)
                resultados.add(esperado)
                if q["acao"] == "SELECT":
                    self.assertTrue(q["resultado"], "SELECT precisa de linhas de exemplo")
        self.assertEqual(resultados, {"permitida", "negada"})

    def test_simulador_estrutura(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        for marcador in ("bd-lab", 'id="bd-dados"', "bd-matriz", "bd-console", "bd-auditoria",
                         "executarComandoSQL", "executarConsultasBD", "verificarMenorPrivilegio"):
            self.assertIn(marcador, content, marcador)
        ini = content.index("var BD = JSON.parse")
        motor = content[ini:content.index("</script>", ini)]
        self.assertNotIn("innerHTML", motor)

    def test_componentes_pedagogicos(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        self.assertIn('class="callout', content)
        self.assertIn('class="terminal-box', content)
        self.assertEqual(content.count('class="checklist-item"'), 7)
        self.assertGreaterEqual(content.count('class="quiz-item"'), 5)
        self.assertIn('class="facts-grid', content)
        self.assertIn('initChecklist("seguranca-bancos-dados")', content)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn("Seguranca-de-Bancos-de-Dados/treinamento-seguranca-de-bancos-de-dados.html", content)
        self.assertIn('data-slug="Seguranca-de-Bancos-de-Dados"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)
        self.assertIn("5 de 7 competências com módulo disponível", content)


if __name__ == "__main__":
    unittest.main()
