#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_active_directory.py
Testes automatizados para o Estudo 38: Active-Directory-Fundamentos
"""

import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402

MENSAGENS = ["AS-REQ", "AS-REP", "TGS-REQ", "TGS-REP", "AP-REQ", "AP-REP"]
ERROS_KERBEROS = {"KRB_AP_ERR_SKEW", "KDC_ERR_PREAUTH_FAILED", "KDC_ERR_S_PRINCIPAL_UNKNOWN", "KDC_ERR_CLIENT_REVOKED"}


def gpo_efetiva(g, ajustes):
    """Precedência LSDOU com ordem de link, Enforced e Block Inheritance (espelhada no JavaScript).

    Devolve {configuração: (valor, gpo vencedora)}.
    """
    enforced = set(ajustes.get("enforced", []))
    desativados = set(ajustes.get("desativados", []))
    bloqueios = set(ajustes.get("block", []))
    ordem = ajustes.get("ordem", {})
    conts = g["containers"]

    def links(c):
        nomes = ordem.get(c["id"], [l["gpo"] for l in c["links"]])
        return [n for n in nomes if c["id"] + ":" + n not in desativados]

    profundidade_bloqueio = max([i for i, c in enumerate(conts) if c["id"] in bloqueios], default=-1)
    sequencia = []
    for i, c in enumerate(conts):
        bloqueado = i < profundidade_bloqueio and c["tipo"] != "local"
        for n in reversed(links(c)):
            if c["id"] + ":" + n not in enforced and not bloqueado:
                sequencia.append(n)
    for c in reversed(conts):
        for n in reversed(links(c)):
            if c["id"] + ":" + n in enforced:
                sequencia.append(n)
    resultado = {}
    for n in sequencia:
        for chave, valor in g["gpos"][n]["valores"].items():
            resultado[chave] = (valor, n)
    return resultado


class TestActiveDirectory(unittest.TestCase):
    """Valida a estrutura, o conteúdo, a precedência de GPO, o Kerberos e a compilação do estudo Active-Directory-Fundamentos."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "active_directory_fundamentos_body.html"
        self.compiled_path = self.root / "Active-Directory-Fundamentos" / "treinamento-active-directory-fundamentos.html"
        self.portal_path = self.root / "index.html"

    def _dados(self):
        body = self.body_path.read_text(encoding="utf-8")
        m = re.search(r'<script type="application/json" id="ad-dados">(.*?)</script>', body, re.S)
        self.assertIsNotNone(m, "Bloco JSON #ad-dados ausente no body")
        return json.loads(m.group(1))

    # ----------------------------------------------------------------- arquivos
    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        termos = [
            "floresta", "domínio", "OU", "Global Catalog", "FSMO", "PDC Emulator", "RID Master", "LDAP",
            "LSDOU", "Enforced", "Block Inheritance", "ordem de link", "loopback", "KDC", "TGT", "SPN", "PAC",
            "krbtgt", "NTLM", "4768", "4769", "4771", "4776", "5 minutos", "gMSA", "Tier 0", "PAW",
            "Kerberoasting", "Golden Ticket", "Silver Ticket", "AS-REP roasting", "T1558.003", "pass-the-hash",
            "corp.ipestore.example",
        ]
        for termo in termos:
            self.assertIn(termo, content, f"Termo obrigatório ausente: {termo}")

    # ---------------------------------------------------------------------- GPO
    def test_estrutura_da_gpo(self):
        g = self._dados()["gpo"]
        tipos = [c["tipo"] for c in g["containers"]]
        self.assertEqual(tipos[:3], ["local", "site", "dominio"], "a cadeia segue a ordem LSDOU")
        self.assertTrue(all(t == "ou" for t in tipos[3:]))
        self.assertGreaterEqual(len(tipos), 5)
        usadas = [l["gpo"] for c in g["containers"] for l in c["links"]]
        self.assertEqual(sorted(usadas), sorted(g["gpos"]), "toda GPO tem exatamente um link")
        for nome, gpo in g["gpos"].items():
            with self.subTest(gpo=nome):
                self.assertTrue(gpo["nome"].strip())
                self.assertTrue(set(gpo["valores"]) <= set(g["configuracoes"]))
        self.assertTrue(any(len(c["links"]) >= 2 for c in g["containers"]), "algum container precisa de 2 links")

    def test_cenarios_de_gpo_batem_com_o_algoritmo(self):
        g = self._dados()["gpo"]
        self.assertGreaterEqual(len(g["cenarios"]), 4)
        for cen in g["cenarios"]:
            with self.subTest(cenario=cen["id"]):
                calc = gpo_efetiva(g, cen["ajustes"])
                for chave in g["configuracoes"]:
                    esperado = cen["esperado"][chave]
                    obtido = list(calc[chave]) if chave in calc else None
                    self.assertEqual(obtido, esperado, chave)

    def test_casos_pedagogicos_de_gpo(self):
        g = self._dados()["gpo"]
        cens = {c["id"]: c for c in g["cenarios"]}
        padrao = gpo_efetiva(g, cens["padrao"]["ajustes"])
        bloqueio = gpo_efetiva(g, cens["bloqueio"]["ajustes"])
        enforced = gpo_efetiva(g, cens["enforced"]["ajustes"])
        ordem = gpo_efetiva(g, cens["ordem"]["ajustes"])
        self.assertEqual(padrao["firewall"][0], "Ligado")
        self.assertEqual(bloqueio["firewall"], ("Desligado", "local-srv"), "bloquear herança devolve o firewall à política local")
        self.assertEqual(enforced["smbv1"][0], "Desabilitado")
        self.assertEqual(enforced["bloqueio"][1], "linha-base", "Enforced impõe todas as configurações da GPO")
        self.assertNotEqual(ordem["pslog"], padrao["pslog"], "inverter a ordem de link muda o resultado")

    # ------------------------------------------------------------------ Kerberos
    def test_mensagens_kerberos(self):
        k = self._dados()["kerberos"]
        self.assertEqual([m["id"] for m in k["mensagens"]], MENSAGENS)
        tecnicas = set()
        for m in k["mensagens"]:
            with self.subTest(mensagem=m["id"]):
                self.assertTrue(m["de"].strip() and m["para"].strip() and m["resumo"].strip())
                self.assertGreaterEqual(len(m["campos"]), 3)
                for r in m["riscos"]:
                    self.assertRegex(r["tecnica"], r"^T\d{4}(\.\d{3})?$")
                    self.assertTrue(r["titulo"].strip() and r["descricao"].strip())
                    tecnicas.add(r["tecnica"])
        self.assertTrue({"T1558.001", "T1558.002", "T1558.003", "T1558.004"} <= tecnicas)

    def test_cenarios_kerberos(self):
        k = self._dados()["kerberos"]
        ids = {c["id"] for c in k["cenarios"]}
        self.assertIn("normal", ids)
        self.assertGreaterEqual(len(ids), 5)
        for c in k["cenarios"]:
            with self.subTest(cenario=c["id"]):
                self.assertTrue(c["nome"].strip() and c["explicacao"].strip())
                self.assertTrue(c["para_em"] is None or c["para_em"] in MENSAGENS)
                self.assertTrue(c["erro"] is None or c["erro"] in ERROS_KERBEROS)
                if c["erro"]:
                    self.assertIsNotNone(c["para_em"])
                if c["ntlm"]:
                    self.assertEqual(c["evento"], "4776")
        self.assertTrue(any(c["ntlm"] for c in k["cenarios"]))
        self.assertTrue(any(c.get("alerta") for c in k["cenarios"] if c["para_em"] is None))

    # ---------------------------------------------------------------- compilado
    def test_simulador_estrutura(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        for marcador in ("ad-lab", 'id="ad-dados"', "ad-kerberos", "ad-mensagem", "ad-cenario", "ad-gpo",
                         "ad-gpo-resultado", "mostrarMensagemKerberos", "executarAutenticacaoKerberos",
                         "calcularGpoEfetiva", "aplicarCenarioGpo", "restaurarAd"):
            self.assertIn(marcador, content, marcador)
        ini = content.index("var AD = JSON.parse")
        motor = content[ini:content.index("</script>", ini)]
        self.assertNotIn("innerHTML", motor)

    def test_componentes_pedagogicos(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        self.assertIn('class="callout', content)
        self.assertIn('class="terminal-box', content)
        self.assertIn('class="diagram-svg-wrap', content)
        self.assertNotIn('<pre class="mermaid"', content)
        self.assertEqual(content.count('class="checklist-item"'), 7)
        self.assertGreaterEqual(content.count('class="quiz-item"'), 6)
        self.assertIn('class="facts-grid', content)
        self.assertIn('initChecklist("active-directory")', content)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn("Active-Directory-Fundamentos/treinamento-active-directory-fundamentos.html", content)
        self.assertIn('data-slug="Active-Directory-Fundamentos"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)


if __name__ == "__main__":
    unittest.main()
