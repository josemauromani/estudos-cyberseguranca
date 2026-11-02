#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_owasp_web.py
Testes automatizados para o Estudo 12: OWASP-Top-10-Web
"""

import json
import re
import sqlite3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402

TOP10_2025 = [
    ("A01:2025", "Broken Access Control"),
    ("A02:2025", "Security Misconfiguration"),
    ("A03:2025", "Software Supply Chain Failures"),
    ("A04:2025", "Cryptographic Failures"),
    ("A05:2025", "Injection"),
    ("A06:2025", "Insecure Design"),
    ("A07:2025", "Authentication Failures"),
    ("A08:2025", "Software or Data Integrity Failures"),
    ("A09:2025", "Security Logging and Alerting Failures"),
    ("A10:2025", "Mishandling of Exceptional Conditions"),
]


def banco_sqlite(d):
    con = sqlite3.connect(":memory:")
    for tabela, t in d["banco"].items():
        con.execute("CREATE TABLE {} ({})".format(tabela, ", ".join(t["colunas"])))
        con.executemany("INSERT INTO {} VALUES ({})".format(tabela, ", ".join("?" * len(t["colunas"]))), t["linhas"])
    return con


class TestOwaspWeb(unittest.TestCase):
    """Valida a estrutura, o conteúdo, os dados do playground e a compilação do estudo OWASP-Top-10-Web."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "owasp_top_10_web_body.html"
        self.compiled_path = self.root / "OWASP-Top-10-Web" / "treinamento-owasp-top-10-web.html"
        self.portal_path = self.root / "index.html"

    def _dados(self):
        body = self.body_path.read_text(encoding="utf-8")
        m = re.search(r'<script type="application/json" id="ow-dados">(.*?)</script>', body, re.S)
        self.assertIsNotNone(m, "Bloco JSON #ow-dados ausente no body")
        return json.loads(m.group(1))

    # ----------------------------------------------------------------- arquivos
    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        termos = [
            "OWASP Top 10:2025", "2021", "SSRF", "SQL injection", "UNION", "cega", "baseada em tempo",
            "prepared statements", "ORM", "XSS", "refletido", "armazenado", "DOM", "Content Security Policy",
            "codificação de saída", "sanitização", "allowlist", "BOLA", "IDOR", "CSRF", "SameSite", "HttpOnly",
            "Secure", "upload",
        ]
        termos += [nome for _, nome in TOP10_2025]
        for termo in termos:
            self.assertIn(termo, content, f"Termo obrigatório ausente: {termo}")

    # -------------------------------------------------------------------- dados
    def test_top10_2025_exato(self):
        d = self._dados()
        self.assertEqual([(c["id"], c["nome"]) for c in d["top10"]], TOP10_2025)
        for c in d["top10"]:
            self.assertTrue(c["resumo"].strip() and c["de_2021"].strip(), c["id"])

    def test_banco_e_consultas(self):
        d = self._dados()
        self.assertIn("{termo}", d["sql_modelo"])
        self.assertIn("?", d["sql_parametrizado"])
        self.assertNotIn("{termo}", d["sql_parametrizado"])
        produtos = d["banco"]["produtos"]
        ativo = produtos["colunas"].index("ativo")
        self.assertTrue(any(l[ativo] == 0 for l in produtos["linhas"]), "precisa de produto inativo")
        self.assertIn("email", d["banco"]["clientes"]["colunas"])
        con = banco_sqlite(d)
        normal = con.execute(d["sql_modelo"].replace("{termo}", "caixa")).fetchall()
        self.assertTrue(normal, "a busca normal precisa achar algo")
        todos_ativos = con.execute(d["sql_modelo"].replace("{termo}", "")).fetchall()
        injetado = con.execute(d["sql_modelo"].replace("{termo}", "' OR 1=1 --")).fetchall()
        self.assertGreater(len(injetado), len(todos_ativos), "OR 1=1 deve revelar os inativos")
        param = con.execute(d["sql_parametrizado"], ("%' OR 1=1 --%",)).fetchall()
        self.assertEqual(param, [], "parametrizado, o payload vira texto literal")

    def test_pedidos_e_usuario(self):
        d = self._dados()
        dono = d["usuario_logado"]["cliente_id"]
        pedidos = d["pedidos"]
        self.assertTrue(any(p["cliente_id"] == dono for p in pedidos))
        self.assertTrue(any(p["cliente_id"] != dono for p in pedidos), "precisa de pedido de outro cliente")
        self.assertGreaterEqual(len(d["missoes"]), 5)

    # ---------------------------------------------------------------- compilado
    def test_simulador_estrutura(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        for marcador in ("ow-lab", 'id="ow-dados"', "ow-sql", "ow-xss", "ow-bola", "ow-missoes", 'sandbox=""',
                         "executarBuscaOwasp", "analisarComentarioOwasp", "consultarPedidoOwasp", "restaurarOwasp"):
            self.assertIn(marcador, content, marcador)
        ini = content.index("var OW = JSON.parse")
        motor = content[ini:content.index("</script>", ini)]
        self.assertNotIn("innerHTML", motor)
        self.assertNotIn("eval(", motor)

    def test_componentes_pedagogicos(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        self.assertIn('class="callout', content)
        self.assertIn('class="terminal-box', content)
        self.assertIn('class="diagram-svg-wrap', content)
        self.assertNotIn('<pre class="mermaid"', content)
        self.assertEqual(content.count('class="checklist-item"'), 7)
        self.assertGreaterEqual(content.count('class="quiz-item"'), 6)
        self.assertIn('class="facts-grid', content)
        self.assertIn('initChecklist("owasp-web")', content)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn("OWASP-Top-10-Web/treinamento-owasp-top-10-web.html", content)
        self.assertIn('data-slug="OWASP-Top-10-Web"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)


if __name__ == "__main__":
    unittest.main()
