#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_redes_protocolos.py
Testes automatizados para o Estudo 02: Redes-e-Protocolos
"""

import ipaddress
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402


def cidr(texto):
    """Espelho em Python do calcularCidr() do corpo (mesmas chaves de saída)."""
    try:
        if "/" not in texto:
            raise ValueError("sem prefixo")
        end, pref = texto.strip().split("/", 1)
        if not pref.isdigit() or not 0 <= int(pref) <= 32:
            raise ValueError("prefixo")
        partes = end.split(".")
        if len(partes) != 4 or not all(p.isdigit() and int(p) <= 255 for p in partes):
            raise ValueError("octeto")
        rede = ipaddress.ip_network(f"{end}/{pref}", strict=False)
    except ValueError:
        return {"erro": "Use o formato 192.168.1.10/24"}
    n = rede.prefixlen
    if n == 32:
        primeiro = ultimo = rede.network_address
        hosts = 1
    elif n == 31:
        primeiro, ultimo = rede.network_address, rede.broadcast_address
        hosts = 2
    else:
        primeiro = rede.network_address + 1
        ultimo = rede.broadcast_address - 1
        hosts = rede.num_addresses - 2
    return {
        "rede": str(rede.network_address),
        "broadcast": str(rede.broadcast_address),
        "mascara": str(rede.netmask),
        "prefixo": n,
        "hosts_uteis": hosts,
        "primeiro": str(primeiro),
        "ultimo": str(ultimo),
    }


class TestRedesProtocolos(unittest.TestCase):
    """Valida a estrutura, conteúdo e compilação do estudo Redes-e-Protocolos."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "redes_e_protocolos_body.html"
        self.compiled_path = self.root / "Redes-e-Protocolos" / "treinamento-redes-e-protocolos.html"
        self.portal_path = self.root / "index.html"

    def test_body_and_compiled_files_exist(self):
        """Verifica se o fragmento body e o treinamento final compilado existem."""
        self.assertTrue(self.body_path.exists(), "O arquivo _geradores/redes_e_protocolos_body.html deve existir.")
        self.assertTrue(self.compiled_path.exists(), "O arquivo Redes-e-Protocolos/treinamento-redes-e-protocolos.html deve existir.")

    def test_teoria_e_conceitos_fundamentais(self):
        """Verifica se os conceitos obrigatórios da pilha TCP/IP e protocolos estão presentes."""
        self.assertTrue(self.compiled_path.exists())
        content = self.compiled_path.read_text(encoding="utf-8")

        termos_obrigatorios = [
            "TCP/IP",
            "Modelo OSI",
            "Encapsulamento",
            "Handshake",
            "IPv4",
            "IPv6",
            "DNS",
            "ARP",
            "SYN",
            "ACK",
            "FIN",
            "RST",
        ]
        for termo in termos_obrigatorios:
            self.assertIn(termo, content, f"O termo obrigatório '{termo}' deve estar presente no conteúdo.")

    def test_simulador_inspetor_pacotes_interativo(self):
        """Verifica se o simulador de cabeçalhos e probe de portas está estruturado no HTML."""
        self.assertTrue(self.compiled_path.exists())
        content = self.compiled_path.read_text(encoding="utf-8")

        self.assertIn("packet-inspector", content)
        self.assertIn("simularHandshake", content)
        self.assertIn("testarPorta", content)
        self.assertIn("Visualizador de Cabeçalho", content)

    def test_componentes_pedagogicos(self):
        """Verifica a presença de checklists, quizzes e callouts padronizados."""
        self.assertTrue(self.compiled_path.exists())
        content = self.compiled_path.read_text(encoding="utf-8")

        self.assertIn('class="callout', content)
        self.assertIn('class="checklist', content)
        self.assertIn('class="quiz-item', content)
        self.assertIn('class="facts-grid', content)
        self.assertIn("initChecklist('redes-protocolos')", content)

    def test_integracao_com_portal_index(self):
        """Verifica se o portal index.html aponta Redes-e-Protocolos como Disponível com link ativo."""
        self.assertTrue(self.portal_path.exists())
        content = self.portal_path.read_text(encoding="utf-8")

        self.assertIn("Redes-e-Protocolos/treinamento-redes-e-protocolos.html", content)
        self.assertIn('data-slug="Redes-e-Protocolos"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)
        self.assertIn("Módulos Compilados", content)

    def _body(self):
        return self.body_path.read_text(encoding="utf-8")

    def test_secao_enderecamento(self):
        body = self._body()
        ids = re.findall(r'<section class="study-section" id="([^"]+)"', body)
        esperado = ["modelos-rede", "dissecacao-protocolos", "enderecamento-http-wifi",
                    "laboratorio-inspetor", "checklist-pratico", "questoes-fixacao", "fatos-essenciais"]
        self.assertEqual(ids, esperado)
        m = re.search(r'<section class="study-section" id="enderecamento-http-wifi" data-tipo="teoria">(.*?)</section>', body, re.S)
        self.assertIsNotNone(m)
        secao = m.group(1)
        for termo in ["CIDR", "máscara", "broadcast", "RFC 1918", "RFC 5737", "gateway", "NAT", "PAT",
                      "não é firewall", "GET", "POST", "HTTP/2", "HTTP/3", "Set-Cookie", "WPA2-PSK",
                      "802.1X", "WPA3", "SAE", "4-way handshake", "evil twin", "Estudo 05", "Estudo 12"]:
            self.assertIn(termo, secao, f"'{termo}' ausente na seção nova")

    def test_questoes_e_referencias_novas(self):
        body = self._body()
        self.assertGreaterEqual(body.count('class="quiz-item"'), 5)
        m = re.search(r'id="fatos-essenciais".*?</section>', body, re.S)
        for termo in ["RFC 4632", "RFC 1918", "RFC 9110", "IEEE 802.11", "WPA3"]:
            self.assertIn(termo, m.group(0))

    def test_cidr_espelhado(self):
        r = cidr("192.168.10.77/26")
        self.assertEqual(r["rede"], "192.168.10.64")
        self.assertEqual(r["broadcast"], "192.168.10.127")
        self.assertEqual(r["mascara"], "255.255.255.192")
        self.assertEqual(r["hosts_uteis"], 62)
        self.assertEqual(r["primeiro"], "192.168.10.65")
        self.assertEqual(r["ultimo"], "192.168.10.126")
        self.assertEqual(cidr("10.0.0.0/8")["hosts_uteis"], 16777214)
        self.assertIn("function calcularCidr(", self._body())

    def test_cidr_bordas_e_invalidos(self):
        self.assertEqual(cidr("203.0.113.4/31")["hosts_uteis"], 2)
        r = cidr("203.0.113.9/32")
        self.assertEqual(r["hosts_uteis"], 1)
        self.assertEqual(r["primeiro"], r["ultimo"])
        for ruim in ["10.0.0.1/33", "256.1.1.1/24", "10.0.0.1", ""]:
            self.assertIn("erro", cidr(ruim), ruim)
        body = self._body()
        self.assertIn("Use o formato 192.168.1.10/24", body)
        self.assertIn("RFC 3021", body)


if __name__ == "__main__":
    unittest.main()
