#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_python_seguranca.py
Testes automatizados para o Estudo 35: Python-para-Seguranca
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402


# ------------------------------------------------------------------ gerador (espelho do JavaScript)
def literal_regex(p):
    barras_finais = len(p) - len(p.rstrip("\\"))
    if "\n" not in p and barras_finais % 2 == 0:
        if '"' not in p:
            return 'r"' + p + '"'
        if "'" not in p:
            return "r'" + p + "'"
    return json.dumps(p, ensure_ascii=False)


def literal_texto(s):
    if '"' in s and "'" not in s and "\\" not in s and "\n" not in s:
        return "'" + s + "'"
    return json.dumps(s, ensure_ascii=False)


def grupos(p):
    return re.findall(r"\(\?P<([A-Za-z_]\w*)>", p)


def gerar_codigo(d, cfg):
    rep = bool(cfg["reputacao"]) and cfg["campo"] == "ip"
    coluna = cfg["campo"] or "linha"
    L = ["# Detector gerado pelo Montador do Estudo 35", "import re"]
    if cfg["saida"] == "csv":
        L.append("import csv")
    if cfg["saida"] == "json":
        L.append("import json")
    if rep:
        L.append("import os")
    if cfg["saida"] == "csv":
        L.append("import sys")
    L += ["from collections import Counter", "",
          "PADRAO = re.compile(" + literal_regex(cfg["padrao"]) + ")",
          "LIMIAR = " + str(cfg["limiar"])]
    if rep:
        lab = "{" + ", ".join(json.dumps(k) + ": " + str(v) for k, v in d["reputacao_lab"].items()) + "}"
        L += ['CHAVE = os.environ.get("ABUSEIPDB_KEY")  # nunca escreva a chave no código',
              "REPUTACAO_LAB = " + lab,
              "",
              "",
              "def reputacao(ip):",
              '    """Pontuação de abuso de 0 a 100. Sem chave, usa os dados do laboratório."""',
              "    if not CHAVE:",
              "        return REPUTACAO_LAB.get(ip, 0)",
              "    import requests",
              "    resposta = requests.get(",
              '        "https://api.abuseipdb.com/api/v2/check",',
              '        headers={"Key": CHAVE, "Accept": "application/json"},',
              '        params={"ipAddress": ip, "maxAgeInDays": 90},',
              "        timeout=10,",
              "    )",
              "    if resposta.status_code == 429:",
              '        espera = resposta.headers.get("Retry-After", "60")',
              '        raise SystemExit(f"Limite da API atingido; tente de novo em {espera} s.")',
              "    resposta.raise_for_status()",
              '    return resposta.json()["data"]["abuseConfidenceScore"]',
              ""]
    L += ["",
          "contagem = Counter()",
          'with open("' + cfg["fonte"] + '", encoding="utf-8") as arquivo:',
          "    for linha in arquivo:",
          '        linha = linha.rstrip("\\n")']
    if cfg["filtro"]:
        L += ["        if " + literal_texto(cfg["filtro"]) + " not in linha:",
              "            continue"]
    L += ["        m = PADRAO.search(linha)",
          "        if m is None:",
          "            continue",
          "        valor = " + ('m.group("' + cfg["campo"] + '")' if cfg["campo"] else "m.group(0)"),
          "        if valor is not None:",
          "            contagem[valor] += 1",
          "",
          "suspeitos = [(valor, total) for valor, total in contagem.most_common() if total >= LIMIAR]",
          ""]
    if cfg["saida"] == "alerta":
        L += ["if not suspeitos:",
              '    print("Nenhum valor atingiu o limiar.")',
              "for valor, total in suspeitos:"]
        L.append('    print(f"ALERTA {valor}: {total} ocorrência(s), reputação {reputacao(valor)}/100")' if rep
                 else '    print(f"ALERTA {valor}: {total} ocorrência(s)")')
    elif cfg["saida"] == "csv":
        cab = '["' + coluna + '", "total"' + (', "reputacao"' if rep else "") + "]"
        L += ['saida = csv.writer(sys.stdout, lineterminator="\\n")',
              "saida.writerow(" + cab + ")",
              "for valor, total in suspeitos:",
              "    saida.writerow([valor, total" + (", reputacao(valor)" if rep else "") + "])"]
    else:
        item = '{"' + coluna + '": valor, "total": total' + (', "reputacao": reputacao(valor)' if rep else "") + "}"
        L += ["print(json.dumps(",
              "    [" + item + " for valor, total in suspeitos],",
              "    ensure_ascii=False, indent=2,",
              "))"]
    return "\n".join(L) + "\n"


def executar_script(d, codigo):
    with tempfile.TemporaryDirectory() as pasta:
        for nome, linhas in d["logs"].items():
            Path(pasta, nome).write_text("\n".join(linhas) + "\n", encoding="utf-8")
        Path(pasta, "detector.py").write_text(codigo, encoding="utf-8")
        amb = {k: v for k, v in os.environ.items() if k != "ABUSEIPDB_KEY"}
        amb["PYTHONIOENCODING"] = "utf-8"
        r = subprocess.run([sys.executable, "-I", "detector.py"], cwd=pasta, capture_output=True, text=True,
                           encoding="utf-8", env=amb, timeout=30)
        if r.returncode != 0:
            raise AssertionError("o script gerado falhou:\n" + r.stderr)
        return r.stdout


class TestPythonSeguranca(unittest.TestCase):
    """Valida a estrutura, o conteúdo, o gerador de código, os logs e a compilação do estudo Python-para-Seguranca."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "python_para_seguranca_body.html"
        self.compiled_path = self.root / "Python-para-Seguranca" / "treinamento-python-para-seguranca.html"
        self.portal_path = self.root / "index.html"

    def _dados(self):
        body = self.body_path.read_text(encoding="utf-8")
        m = re.search(r'<script type="application/json" id="py-dados">(.*?)</script>', body, re.S)
        self.assertIsNotNone(m, "Bloco JSON #py-dados ausente no body")
        return json.loads(m.group(1))

    # ----------------------------------------------------------------- arquivos
    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        termos = [
            "re.search", "re.match", "re.finditer", "re.compile", "(?P&lt;", "quantificador", "âncora",
            "Counter", "most_common", "requests", "timeout", "raise_for_status", "429", "Retry-After",
            "variável de ambiente", "AbuseIPDB", "VirusTotal", "JSON", "CSV", "T1059.006", "invalid user",
            "Estudo 34", "web-loja01",
        ]
        for termo in termos:
            self.assertIn(termo, content, f"Termo obrigatório ausente: {termo}")

    # -------------------------------------------------------------------- dados
    def test_logs_e_regex_de_referencia(self):
        d = self._dados()
        self.assertEqual(set(d["logs"]), {"auth.log", "access.log"})
        ips = re.findall(r"\b(\d{1,3}(?:\.\d{1,3}){3})\b", "\n".join(sum(d["logs"].values(), [])))
        for ip in ips:
            self.assertTrue(ip.startswith(("10.", "192.0.2.", "198.51.100.", "203.0.113.")), ip)
        ref = re.compile(d["regex_referencia"])
        falhas = [l for l in d["logs"]["auth.log"] if "Failed password" in l]
        self.assertTrue(any("invalid user" in l for l in falhas) and any("invalid user" not in l for l in falhas))
        self.assertEqual([ref.search(l).group("ip") for l in falhas], d["ips_falhas"])
        self.assertTrue(any("Accepted password for deploy from 198.51.100.23" in l for l in d["logs"]["auth.log"]),
                        "mesmo incidente do Estudo 34")

    def test_presets_validos(self):
        d = self._dados()
        for p in d["regex_prontas"]:
            with self.subTest(regex=p["id"]):
                self.assertIn(p["fonte"], d["logs"])
                re.compile(p["padrao"])
                self.assertTrue(grupos(p["padrao"]))
                self.assertTrue(any(re.search(p["padrao"], l) for l in d["logs"][p["fonte"]]))

    def test_exemplos_executam_de_verdade(self):
        d = self._dados()
        saidas = set()
        for ex in d["exemplos"]:
            with self.subTest(exemplo=ex["nome"]):
                cfg = ex["cfg"]
                if cfg["campo"]:
                    self.assertIn(cfg["campo"], grupos(cfg["padrao"]))
                codigo = gerar_codigo(d, cfg)
                compile(codigo, "detector.py", "exec")
                self.assertEqual(executar_script(d, codigo), ex["saida"])
                saidas.add(cfg["saida"])
        self.assertEqual(saidas, {"alerta", "csv", "json"})
        self.assertTrue(any(ex["cfg"]["reputacao"] for ex in d["exemplos"]))
        self.assertTrue(any('"' in ex["saida"] for ex in d["exemplos"] if ex["cfg"]["saida"] == "csv"),
                        "um exemplo de CSV precisa de aspas para testar o escape")

    def test_forca_bruta_e_invasao(self):
        d = self._dados()
        ex = {e["id"]: e for e in d["exemplos"]}
        self.assertEqual(ex["forca_bruta"]["saida"].splitlines(),
                         ["ALERTA 198.51.100.23: 14 ocorrência(s)", "ALERTA 203.0.113.77: 6 ocorrência(s)"])
        self.assertIn("198.51.100.23", ex["invasao"]["saida"])
        self.assertIn("203.0.113.50", ex["varredura"]["saida"])

    def test_literais_seguros(self):
        for p in ['a"b', "a'b", "a\"'b", "fim\\", "fim\\\\", "simples"]:
            with self.subTest(padrao=p):
                self.assertEqual(eval(literal_regex(p)), p)  # noqa: S307 (somente literais gerados pelo teste)
        for s in ['" 404 ', "Failed password", "a'b\"c"]:
            self.assertEqual(eval(literal_texto(s)), s)  # noqa: S307

    # ---------------------------------------------------------------- compilado
    def test_simulador_estrutura(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        for marcador in ("py-lab", 'id="py-dados"', "py-missoes", "py-testador", "py-regex", "py-correspondencias",
                         "py-montador", "py-codigo", "py-saida", "testarRegexPython", "montarDetectorPython",
                         "restaurarPython"):
            self.assertIn(marcador, content, marcador)
        ini = content.index("var PY = JSON.parse")
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
        self.assertIn('initChecklist("python-seguranca")', content)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn("Python-para-Seguranca/treinamento-python-para-seguranca.html", content)
        self.assertIn('data-slug="Python-para-Seguranca"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)


if __name__ == "__main__":
    unittest.main()
