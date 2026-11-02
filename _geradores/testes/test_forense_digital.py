#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_forense_digital.py
Testes automatizados para o Estudo 19: Forense-Digital
"""

import hashlib
import ipaddress
import json
import re
import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402

FUSOS = {"UTC": 0, "UTC-3": 3}
FMT = "%Y-%m-%d %H:%M:%S"


def utc(evento):
    """Normaliza o horário armazenado para UTC (espelhado no JavaScript)."""
    t = datetime.strptime(evento["ts_armazenado"], FMT)
    return t + timedelta(hours=FUSOS[evento["fuso"]])


class TestForenseDigital(unittest.TestCase):
    """Valida a estrutura, o conteúdo, a timeline, a integridade e a compilação do estudo Forense-Digital."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "forense_digital_body.html"
        self.compiled_path = self.root / "Forense-Digital" / "treinamento-forense-digital.html"
        self.portal_path = self.root / "index.html"

    def _dados(self):
        body = self.body_path.read_text(encoding="utf-8")
        m = re.search(r'<script type="application/json" id="fd-dados">(.*?)</script>', body, re.S)
        self.assertIsNotNone(m, "Bloco JSON #fd-dados ausente no body")
        return json.loads(m.group(1))

    def _pergunta(self, d, pid):
        return next(p for p in d["perguntas"] if p["id"] == pid)

    # ----------------------------------------------------------------- arquivos
    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        termos = [
            "ISO/IEC 27037", "RFC 3227", "ordem de volatilidade", "cadeia de custódia", "158-A", "Lei 13.964/2019",
            "bloqueador de escrita", "SHA-256", "E01", "Prefetch", "Amcache", "Shimcache", "$MFT",
            "$STANDARD_INFORMATION", "$FILE_NAME", "timestomping", "T1070.006", "$UsnJrnl", "LNK", "Registro",
            "T1547.001", "7045", "Plaso", "Timesketch", "Volatility", "UTC", "BitLocker",
        ]
        for termo in termos:
            self.assertIn(termo, content, f"Termo obrigatório ausente: {termo}")

    # ---------------------------------------------------------------- custódia
    def test_hash_registrado_e_o_sha256_da_evidencia(self):
        c = self._dados()["custodia"]
        self.assertEqual(hashlib.sha256(c["texto_evidencia"].encode("utf-8")).hexdigest(), c["sha256"])
        for campo in ("item", "coletado_por", "data_coleta", "ferramenta"):
            self.assertTrue(c[campo].strip(), campo)

    # ------------------------------------------------------------------ eventos
    def test_eventos_validos(self):
        d = self._dados()
        eventos = d["eventos"]
        self.assertGreaterEqual(len(eventos), 20)
        ids = [e["id"] for e in eventos]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreaterEqual(len({e["fonte"] for e in eventos}), 8)
        self.assertIn("UTC-3", {e["fuso"] for e in eventos}, "deve haver fonte em horário local")
        for e in eventos:
            with self.subTest(evento=e["id"]):
                self.assertIn(e["fonte"], d["fontes"])
                self.assertIn(e["fuso"], FUSOS)
                utc(e)
                self.assertTrue(e["descricao"].strip())
                self.assertIsInstance(e["invasor"], bool)
                texto = e["descricao"] + " " + json.dumps(e.get("detalhes", {}))
                for ip in re.findall(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", texto):
                    end = ipaddress.ip_address(ip)
                    doc = any(end in ipaddress.ip_network(r) for r in ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24"))
                    self.assertTrue(end.is_private or doc, f"IP real: {ip}")
        self.assertTrue(any(e["invasor"] for e in eventos) and any(not e["invasor"] for e in eventos))

    def test_horario_local_engana_sem_normalizar(self):
        d = self._dados()
        exf = next(e for e in d["eventos"] if e["tipo"] == "exfiltracao")
        rclone = next(e for e in d["eventos"] if e["invasor"] and e["tipo"] == "execucao" and "rclone" in e["descricao"].lower())
        self.assertEqual(exf["fuso"], "UTC-3")
        self.assertLess(exf["ts_armazenado"], rclone["ts_armazenado"], "sem normalizar, a saída parece anterior ao rclone")
        self.assertGreater(utc(exf), utc(rclone), "normalizado, a saída vem depois do rclone")

    def test_respostas_derivam_dos_dados(self):
        d = self._dados()
        ev = d["eventos"]
        primeira = min((e for e in ev if e["invasor"] and e["tipo"] == "execucao"), key=utc)
        self.assertEqual(self._pergunta(d, "primeira_execucao")["correta"], primeira["id"])
        exf = next(e for e in ev if e["tipo"] == "exfiltracao")
        self.assertEqual(self._pergunta(d, "exfiltracao")["correta"], utc(exf).strftime("%Y-%m-%dT%H:%M:%SZ"))
        persist = [e for e in ev if e["invasor"] and e["tipo"] == "persistencia" and e["fonte"] == "Registro"]
        self.assertEqual(len(persist), 1)
        self.assertEqual(self._pergunta(d, "persistencia")["correta"], persist[0]["id"])
        stomp = [e for e in ev if "mft" in e and e["mft"]["si_criado"] < e["mft"]["fn_criado"]]
        self.assertEqual(len(stomp), 1)
        self.assertEqual(self._pergunta(d, "timestomping")["correta"], stomp[0]["id"])
        for p in d["perguntas"]:
            with self.subTest(pergunta=p["id"]):
                valores = [o["valor"] for o in p["opcoes"]]
                self.assertIn(p["correta"], valores)
                self.assertEqual(len(valores), len(set(valores)))
                self.assertGreaterEqual(len(valores), 3)
                self.assertTrue(p["explicacao"].strip())
        legit = [e for e in ev if not e["invasor"] and e["tipo"] == "persistencia"]
        self.assertTrue(legit, "precisa de persistência legítima como distrator")

    # ---------------------------------------------------------------- compilado
    def test_simulador_estrutura(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        for marcador in ("fd-lab", 'id="fd-dados"', "fd-evidencia", "fd-fontes", "fd-timeline", "fd-perguntas",
                         "verificarIntegridadeForense", "carregarFonteForense", "alternarFusoForense",
                         "marcarEventoForense", "conferirMarcacoesForense", "verificarRespostasForense", "restaurarForense"):
            self.assertIn(marcador, content, marcador)
        ini = content.index("var FD = JSON.parse")
        motor = content[ini:content.index("</script>", ini)]
        self.assertNotIn("innerHTML", motor)
        self.assertIn("crypto.subtle", motor)

    def test_componentes_pedagogicos(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        self.assertIn('class="callout', content)
        self.assertIn('class="terminal-box', content)
        self.assertIn('class="diagram-svg-wrap', content)
        self.assertNotIn('<pre class="mermaid"', content)
        self.assertEqual(content.count('class="checklist-item"'), 7)
        self.assertGreaterEqual(content.count('class="quiz-item"'), 6)
        self.assertIn('class="facts-grid', content)
        self.assertIn('initChecklist("forense-digital")', content)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn("Forense-Digital/treinamento-forense-digital.html", content)
        self.assertIn('data-slug="Forense-Digital"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)


if __name__ == "__main__":
    unittest.main()
