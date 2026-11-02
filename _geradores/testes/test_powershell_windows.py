#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_powershell_windows.py
Testes automatizados para o Estudo 36: PowerShell-e-Windows-Interno
"""

import base64
import ipaddress
import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402

SYSMON = "Microsoft-Windows-Sysmon/Operational"
PSLOG = "Microsoft-Windows-PowerShell/Operational"


def basename(caminho):
    return caminho.replace("/", "\\").split("\\")[-1]


class TestPowerShellWindows(unittest.TestCase):
    """Valida a estrutura, o conteúdo, os eventos e a compilação do estudo PowerShell-e-Windows-Interno."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "powershell_e_windows_interno_body.html"
        self.compiled_path = self.root / "PowerShell-e-Windows-Interno" / "treinamento-powershell-e-windows-interno.html"
        self.portal_path = self.root / "index.html"

    def _dados(self):
        body = self.body_path.read_text(encoding="utf-8")
        m = re.search(r'<script type="application/json" id="ps-dados">(.*?)</script>', body, re.S)
        self.assertIsNotNone(m, "Bloco JSON #ps-dados ausente no body")
        return json.loads(m.group(1))

    def _eventos(self, d, log, eid):
        return [e for e in d["eventos"] if e["LogName"] == log and e["Id"] == eid]

    def _ps_malicioso(self, d):
        return next(e for e in self._eventos(d, SYSMON, 1)
                    if basename(e["Image"]).lower() == "powershell.exe" and " -enc " in e["CommandLine"].lower())

    # ----------------------------------------------------------------- arquivos
    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        termos = [
            "Verbo-Substantivo", "Get-Command", "Get-Help", "Get-Member", "pipeline de objetos", "Where-Object",
            "Select-Object", "Group-Object", "Get-WinEvent", "FilterHashtable", "4624", "4625", "4648", "4672",
            "4688", "4720", "4732", "4698", "7045", "1102", "LogonType", "Sysmon", "4104", "ScriptBlock",
            "HKLM", "HKCU", "execution policy", "AMSI", "Constrained Language Mode", "PowerShell v2",
            "T1059.001", "T1547.001", "T1136.001", "T1543.003", "T1566.001", "ToXml",
        ]
        for termo in termos:
            self.assertIn(termo, content, f"Termo obrigatório ausente: {termo}")

    # -------------------------------------------------------------------- dados
    def test_eventos_validos(self):
        d = self._dados()
        logs = {"Security", "System", SYSMON, PSLOG}
        self.assertEqual({e["LogName"] for e in d["eventos"]}, logs)
        for e in d["eventos"]:
            with self.subTest(evento=(e["LogName"], e["Id"], e["TimeCreated"])):
                self.assertRegex(e["TimeCreated"], r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")
                self.assertIsInstance(e["Id"], int)
                self.assertTrue(e["Message"].strip())
        textos = json.dumps(d, ensure_ascii=False)
        for ip in set(re.findall(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", textos)):
            end = ipaddress.ip_address(ip)
            doc = any(end in ipaddress.ip_network(r) for r in ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24"))
            self.assertTrue(end.is_private or end.is_loopback or end.is_unspecified or doc, f"IP real: {ip}")
        for tipo in ("servicos", "usuarios", "membros_admin", "processos", "conexoes"):
            self.assertTrue(d[tipo], tipo)

    def test_scriptblock_decodifica_o_enc(self):
        d = self._dados()
        ps = self._ps_malicioso(d)
        b64 = ps["CommandLine"].split()[-1]
        decodificado = base64.b64decode(b64).decode("utf-16-le")
        blocos = [e["ScriptBlockText"] for e in self._eventos(d, PSLOG, 4104)]
        self.assertIn(decodificado, blocos, "o 4104 mostra o script que o -enc escondia")
        self.assertGreaterEqual(len(blocos), 2, "precisa de um 4104 legítimo como ruído")

    def test_respostas_derivam_dos_dados(self):
        d = self._dados()
        r = d["respostas"]
        ps = self._ps_malicioso(d)
        self.assertEqual(r["processo_pai"], basename(ps["ParentImage"]))
        conexoes = [e for e in self._eventos(d, SYSMON, 3) if e["ProcessId"] == ps["ProcessId"]]
        self.assertEqual(len(conexoes), 1)
        self.assertEqual(r["destino"], "{}:{}".format(conexoes[0]["DestinationIp"], conexoes[0]["DestinationPort"]))
        criadas = self._eventos(d, "Security", 4720)
        self.assertEqual([e["TargetUserName"] for e in criadas], [r["conta"]])
        run = [(k, v) for chave in d["registro"].values() for k, v in chave.items()]
        fora = [k for k, v in run if k not in d["run_conhecidos"]]
        self.assertEqual(fora, [r["run"]])
        self.assertGreaterEqual(len(run), 3, "precisa de valores Run legítimos")
        servico = [e for e in self._eventos(d, "System", 7045) if e["ServiceName"] == r["run"]]
        self.assertTrue(servico, "o mesmo binário também vira serviço (T1543.003)")

    # ---------------------------------------------------------------- compilado
    def test_simulador_estrutura(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        for marcador in ("ps-lab", 'id="ps-dados"', "ps-console", "ps-entrada", "ps-perguntas",
                         "executarComandoPowerShell", "verificarPerguntaPowerShell", "restaurarPowerShell"):
            self.assertIn(marcador, content, marcador)
        ini = content.index("var PS = JSON.parse")
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
        self.assertIn('initChecklist("powershell-windows")', content)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn("PowerShell-e-Windows-Interno/treinamento-powershell-e-windows-interno.html", content)
        self.assertIn('data-slug="PowerShell-e-Windows-Interno"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)


if __name__ == "__main__":
    unittest.main()
