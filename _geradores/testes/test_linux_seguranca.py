#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_linux_seguranca.py
Testes automatizados para o Estudo 34: Linux-para-Seguranca
"""

import ipaddress
import json
import re
import sys
import unittest
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402

RE_FALHA = re.compile(r"Failed password for (?:invalid user )?\S+ from (\S+) port")
RE_SUCESSO = re.compile(r"Accepted password for (\S+) from (\S+) port")


class TestLinuxSeguranca(unittest.TestCase):
    """Valida a estrutura, o conteúdo, o sistema de arquivos e a compilação do estudo Linux-para-Seguranca."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "linux_para_seguranca_body.html"
        self.compiled_path = self.root / "Linux-para-Seguranca" / "treinamento-linux-para-seguranca.html"
        self.portal_path = self.root / "index.html"

    def _dados(self):
        body = self.body_path.read_text(encoding="utf-8")
        m = re.search(r'<script type="application/json" id="lx-dados">(.*?)</script>', body, re.S)
        self.assertIsNotNone(m, "Bloco JSON #lx-dados ausente no body")
        return json.loads(m.group(1))

    def _auth(self, d):
        return d["fs"]["/var/log/auth.log"]["conteudo"].split("\n")

    # ----------------------------------------------------------------- arquivos
    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        termos = [
            "FHS", "/etc/passwd", "/etc/shadow", "SUID", "SGID", "sticky bit", "umask", "chmod", "sudoers", "NOPASSWD",
            "GTFOBins", "auth.log", "/var/log/secure", "journalctl", "ps aux", "ss -tlnp", "lsof", "crontab",
            "/etc/cron.d", "systemd", "authorized_keys", "yescrypt", "T1548.001", "T1053.003", "T1110",
            "T1543.002", "T1098.004",
        ]
        for termo in termos:
            self.assertIn(termo, content, f"Termo obrigatório ausente: {termo}")

    # ------------------------------------------------------- sistema de arquivos
    def test_sistema_de_arquivos_valido(self):
        d = self._dados()
        fs = d["fs"]
        self.assertIn("/", fs)
        for caminho, no in fs.items():
            with self.subTest(caminho=caminho):
                self.assertTrue(caminho.startswith("/"))
                self.assertIn(no["tipo"], ("arquivo", "dir"))
                self.assertRegex(no["modo"], r"^[0-7]{4}$")
                self.assertTrue(no["dono"] and no["grupo"])
                if caminho != "/":
                    pai = caminho.rsplit("/", 1)[0] or "/"
                    self.assertIn(pai, fs, f"diretório pai ausente: {pai}")
                    self.assertEqual(fs[pai]["tipo"], "dir")
                if no["tipo"] == "arquivo":
                    self.assertIsInstance(no.get("conteudo", ""), str)
        textos = [n.get("conteudo", "") for n in fs.values()] + list(d["saidas"].values())
        for ip in set(re.findall(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", "\n".join(textos))):
            end = ipaddress.ip_address(ip)
            doc = any(end in ipaddress.ip_network(r) for r in ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24"))
            self.assertTrue(end.is_private or end.is_loopback or end.is_unspecified or doc, f"IP real: {ip}")

    # ------------------------------------------------------------------ missões
    def test_missao_suid(self):
        d = self._dados()
        suid = [c for c, n in d["fs"].items() if n["tipo"] == "arquivo" and int(n["modo"], 8) & 0o4000]
        fora = [c for c in suid if c not in d["suid_padrao"]]
        self.assertEqual(fora, [d["missoes"]["suid"]])
        self.assertGreaterEqual(len(suid), 6, "precisa de SUID legítimos como ruído")

    def test_missao_forca_bruta(self):
        d = self._dados()
        linhas = self._auth(d)
        falhas = Counter(m.group(1) for l in linhas for m in [RE_FALHA.search(l)] if m)
        ip, n = falhas.most_common(1)[0]
        self.assertEqual(ip, d["missoes"]["ip"])
        self.assertGreaterEqual(n, 20)
        self.assertGreaterEqual(len(falhas), 3, "precisa de outras origens como ruído")
        entradas = [m.groups() for l in linhas for m in [RE_SUCESSO.search(l)] if m]
        self.assertIn((d["missoes"]["conta"], ip), entradas)
        invalid = [l for l in linhas if "invalid user" in l and ip in l]
        self.assertTrue(invalid, "a linha 'invalid user' desloca a coluna do IP")
        for l in invalid:
            campos = l.split()
            self.assertEqual(campos[12], ip, "$13 nas linhas com invalid user")
            self.assertEqual(campos[-4], ip, "$(NF-3) funciona nos dois formatos")
        normal = next(l for l in linhas if RE_FALHA.search(l) and "invalid user" not in l and ip in l)
        self.assertEqual(normal.split()[10], ip, "$11 nas linhas comuns")

    def test_missao_permissao(self):
        d = self._dados()
        alvo = d["fs"][d["missoes"]["permissao"]]
        self.assertEqual(alvo["tipo"], "dir")
        self.assertTrue(int(alvo["modo"], 8) & 0o002, "o diretório começa gravável por todos")

    def test_missao_cron(self):
        d = self._dados()
        cron = [c for c, n in d["fs"].items() if c.startswith("/etc/cron.d/") and n["tipo"] == "arquivo"]
        self.assertGreaterEqual(len(cron), 2, "precisa de um cron legítimo como ruído")
        malicioso = [c for c in cron if re.search(r"curl[^|]*\|\s*(ba)?sh", d["fs"][c]["conteudo"])]
        self.assertEqual(malicioso, [d["missoes"]["cron"]])

    # ---------------------------------------------------------------- compilado
    def test_simulador_estrutura(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        for marcador in ("lx-lab", 'id="lx-dados"', "lx-terminal", "lx-entrada", "lx-missoes",
                         "executarComandoLinux", "verificarMissaoLinux", "restaurarLinux"):
            self.assertIn(marcador, content, marcador)
        ini = content.index("var LX = JSON.parse")
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
        self.assertIn('initChecklist("linux-seguranca")', content)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn("Linux-para-Seguranca/treinamento-linux-para-seguranca.html", content)
        self.assertIn('data-slug="Linux-para-Seguranca"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)


if __name__ == "__main__":
    unittest.main()
