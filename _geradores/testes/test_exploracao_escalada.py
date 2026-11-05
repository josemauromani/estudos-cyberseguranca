#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_exploracao_escalada.py
Testes automatizados para o Estudo 62: Exploracao-e-Escalada-de-Privilegio

Módulo de detecção e defesa: a cadeia de ataque vista pelo defensor. O simulador
"Console do Defensor" pede que cada evento de log seja classificado por etapa da
cadeia e por controle que o barraria. Este teste espelha o motor avaliar() em Python.
"""

import ipaddress
import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402

SLUG = "Exploracao-e-Escalada-de-Privilegio"
SECOES = ["introducao", "reconhecimento", "exploracao-web", "acesso-e-shell", "escalada-linux",
          "escalada-windows", "simulador", "checklist", "quiz", "fatos"]
REDES_DOCUMENTACAO = [ipaddress.ip_network(n) for n in ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24")]
REDES_PRIVADAS = [ipaddress.ip_network(n) for n in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16")]


def avaliar(dados, escolhas):
    """Espelho de avaliar() do motor JavaScript."""
    r = {"total": len(dados["eventos"]), "estagios_ok": 0, "controles_ok": 0, "acertos": 0, "por_evento": {}}
    for ev in dados["eventos"]:
        esc = escolhas.get(ev["id"], {"estagio": "", "controle": ""})
        e_ok = esc.get("estagio") == ev["estagio"]
        c_ok = esc.get("controle") == ev["controle"]
        r["estagios_ok"] += e_ok
        r["controles_ok"] += c_ok
        r["acertos"] += e_ok and c_ok
        r["por_evento"][ev["id"]] = {"estagio_ok": e_ok, "controle_ok": c_ok}
    return r


class TestExploracaoEscalada(unittest.TestCase):
    """Estrutura, conteúdo, simulador e compilação do estudo 62."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "exploracao_e_escalada_de_privilegio_body.html"
        self.compiled_path = self.root / SLUG / "treinamento-exploracao-e-escalada-de-privilegio.html"
        self.portal_path = self.root / "index.html"

    def _body(self):
        return self.body_path.read_text(encoding="utf-8")

    def _compilado(self):
        return self.compiled_path.read_text(encoding="utf-8")

    def _secao(self, sid):
        body = self._body()
        ini = body.index(f'id="{sid}"')
        fim = body.find('<section class="study-section"', ini)
        return body[ini:fim if fim >= 0 else body.index("</article>")]

    def _dados(self):
        m = re.search(r'<script type="application/json" id="exp-dados">(.*?)</script>', self._body(), re.S)
        self.assertIsNotNone(m, "Bloco JSON #exp-dados ausente no body")
        return json.loads(m.group(1))

    # ------------------------------------------------------------ estrutura
    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_secoes(self):
        body = self._body()
        ids = re.findall(r'<section class="study-section" id="([\w-]+)"', body)
        self.assertEqual(ids, SECOES)
        compilado = self._compilado()
        for n in range(1, len(SECOES) + 1):
            self.assertIn(f"Seção {n} de {len(SECOES)}", compilado)
        self.assertIn('data-slug="exploracao-e-escalada-de-privilegio"', body)

    def test_coerencia_com_o_catalogo(self):
        content = self._compilado()
        info = ESTUDOS_DADOS[SLUG]
        self.assertIn(info["simulador_nome"], content)
        self.assertIn(info["pergunta_chave"], content)
        self.assertIn(info["subtitulo"], self.portal_path.read_text(encoding="utf-8"))
        for fato in info["fatos"]:
            self.assertIn(fato, content, fato)

    # ------------------------------------------------------------ conteúdo
    def test_termos_chave(self):
        body = self._body()
        for termo in ("nmap", "-sV", "NSE", "Burp", "Proxy", "Repeater", "Intruder", "injeção de comando",
                      "reverse shell", "bind shell", "Metasploit", "meterpreter", "egress", "sudo", "SUID",
                      "cron", "capabilities", "auditd", "SeImpersonatePrivilege", "caminho sem aspas",
                      "4688", "4673", "7045"):
            self.assertIn(termo, body, termo)

    def test_etica_e_defesa(self):
        intro = self._secao("introducao")
        self.assertIn('class="callout law"', intro)
        for t in ("autorização por escrito", "Lei nº 12.737/2012", "Estudo 14"):
            self.assertIn(t, intro, t)
        for sid in SECOES[1:6]:
            sec = self._secao(sid)
            self.assertIn('class="callout tip"', sec, sid)
            self.assertIn("Como o defensor vê", sec, sid)

    def test_pontes(self):
        body = self._body()
        antes = body[:body.index('id="simulador"')]
        for ref in ("Estudo 06", "Estudo 12", "Estudo 14", "Estudo 36", "Estudo 48", "Estudo 61"):
            self.assertIn(ref, antes, ref)

    def test_cenario_ficticio(self):
        body = self._body()
        for ip in re.findall(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])", body):
            try:
                addr = ipaddress.ip_address(ip)
            except ValueError:
                continue
            ok = any(addr in r for r in REDES_DOCUMENTACAO + REDES_PRIVADAS)
            self.assertTrue(ok, f"IP fora de RFC 5737/1918: {ip}")
        self.assertTrue(re.search(r"[\w.-]+\.ipestore\.example|lab-web01|lab-win01", body))
        for dom in re.findall(r"[\w-]+(?:\.[\w-]+)*\.example\b", body):
            self.assertTrue(dom.endswith("ipestore.example"), dom)

    # ---------------------------------------------------------------- dados
    def test_dados_do_simulador(self):
        d = self._dados()
        self.assertEqual(set(d["estagios"]), {"reconhecimento", "exploracao", "acesso", "escalada"})
        self.assertEqual(set(d["controles"]), {"superficie", "validacao", "egress", "hardening"})
        self.assertIsInstance(d["eventos"], list)
        contagem = {k: 0 for k in d["estagios"]}
        ids = set()
        for ev in d["eventos"]:
            with self.subTest(evento=ev.get("id")):
                for campo in ("id", "fonte", "linha", "explicacao"):
                    self.assertTrue(str(ev[campo]).strip(), campo)
                self.assertIn(ev["estagio"], d["estagios"])
                self.assertIn(ev["controle"], d["controles"])
                self.assertNotIn(ev["id"], ids)
                ids.add(ev["id"])
                contagem[ev["estagio"]] += 1
        for k, n in contagem.items():
            self.assertGreaterEqual(n, 2, k)

    def test_motor_espelhado(self):
        d = self._dados()
        gab = {ev["id"]: {"estagio": ev["estagio"], "controle": ev["controle"]} for ev in d["eventos"]}
        r = avaliar(d, gab)
        self.assertEqual(r["acertos"], r["total"])
        self.assertEqual(r["estagios_ok"], r["total"])
        self.assertEqual(r["controles_ok"], r["total"])
        ev0 = d["eventos"][0]
        troca = {k: dict(v) for k, v in gab.items()}
        troca[ev0["id"]]["estagio"] = next(e for e in d["estagios"] if e != ev0["estagio"])
        r2 = avaliar(d, troca)
        self.assertEqual(r2["acertos"], r["total"] - 1)
        self.assertFalse(r2["por_evento"][ev0["id"]]["estagio_ok"])
        self.assertTrue(r2["por_evento"][ev0["id"]]["controle_ok"])
        self.assertEqual(avaliar(d, {})["acertos"], 0)

    def test_simulador_sem_apis_inseguras(self):
        body = self._body()
        ini = body.index('id="exp-dados"')
        scripts = re.findall(r"<script(?![^>]*application/json)[^>]*>(.*?)</script>", body[ini:], re.S)
        self.assertTrue(scripts, "script do simulador ausente")
        motor = "\n".join(scripts)
        self.assertIn("function avaliar", motor)
        for proibido in ("innerHTML", "eval", "fetch", "btoa", "atob"):
            self.assertNotIn(proibido, motor, proibido)

    def test_componentes_pedagogicos(self):
        body = self._body()
        self.assertIn('<pre class="mermaid"', body)
        self.assertIn(self._compilado().count('class="checklist-item"'), range(4, 9))
        self.assertGreaterEqual(self._compilado().count('class="quiz-item"'), 6)


if __name__ == "__main__":
    unittest.main()
