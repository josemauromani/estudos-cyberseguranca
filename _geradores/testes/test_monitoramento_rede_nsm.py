#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_monitoramento_rede_nsm.py
Testes automatizados para o Estudo 48: Monitoramento-de-Rede-NSM

O Analisador de Conexões guarda um conn.log e um dns.log fictícios, no formato
do Zeek, num bloco JSON. Este teste espelha em Python a expansão das séries em
conexões, o agrupamento por par origem–destino, as métricas de beaconing
(intervalo médio, jitter e estabilidade do tamanho), as métricas de túnel DNS
(comprimento, entropia e nomes distintos) e as contagens de acertos e falsos
positivos do JavaScript, para validar que os limiares padrão geram os falsos
positivos esperados e que existe um ajuste que pega só o que é malicioso.
"""

import base64
import ipaddress
import json
import math
import re
import sys
import unittest
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402

REDES_PRIVADAS = [ipaddress.ip_network(n) for n in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16")]
REDES_DOC = [ipaddress.ip_network(n) for n in ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24")]
ALFABETO_B32 = "abcdefghijklmnopqrstuvwxyz234567"


# ----------------------------------------------------- espelho do motor JS
def privado(ip):
    a = ipaddress.ip_address(ip)
    return any(a in n for n in REDES_PRIVADAS)


def expandir_conexoes(d):
    """Espelho de expandirConexoes: cada série vira uma conexão por instante (t0 + intervalos acumulados)."""
    conns = []
    for s in d["series"]:
        t = s["t0"]
        offs = [t]
        for iv in s["intervalos"]:
            t += iv
            offs.append(t)
        for k, off in enumerate(offs):
            conns.append({"serie": s["id"], "off": off, "orig_h": s["orig_h"], "resp_h": s["resp_h"],
                          "resp_p": s["resp_p"], "proto": s["proto"], "orig_bytes": s["orig_bytes"][k],
                          "resp_bytes": s["resp_bytes"][k], "beacon": s["rotulo"] == "beacon"})
    conns.sort(key=lambda c: (c["off"], c["serie"]))
    return conns


def casa_excecao(c, e):
    return all(c[k] == e[k] for k in ("orig_h", "resp_h", "resp_p") if k in e)


def chave(c, agrupar):
    if agrupar == "par":
        return "%s → %s:%s/%s" % (c["orig_h"], c["resp_h"], c["resp_p"], c["proto"])
    if agrupar == "destino":
        return "* → %s:%s/%s" % (c["resp_h"], c["resp_p"], c["proto"])
    return "%s → *" % c["orig_h"]


def mediana(v):
    s = sorted(v)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def agrupar_conexoes(d, cfg):
    """Espelho de agruparConexoes: filtra (externos, exceções), agrupa e mede cada grupo."""
    exc = [e for e in d["excecoes"] if e["id"] in cfg.get("excecoes", [])]
    grupos, ignoradas = {}, 0
    for c in expandir_conexoes(d):
        if (cfg.get("so_externos") and privado(c["resp_h"])) or any(casa_excecao(c, e) for e in exc):
            ignoradas += 1
            continue
        grupos.setdefault(chave(c, cfg["agrupar"]), []).append(c)
    res = []
    for k, cs in grupos.items():
        offs = [c["off"] for c in cs]
        ivs = [offs[i + 1] - offs[i] for i in range(len(offs) - 1)]
        n = len(cs)
        media = sum(ivs) / len(ivs) if ivs else 0
        jitter = 100 * math.sqrt(sum((x - media) ** 2 for x in ivs) / len(ivs)) / media if ivs and media > 0 else 0
        med = mediana([c["orig_bytes"] for c in cs])
        estab = 100 * sum(1 for c in cs if abs(c["orig_bytes"] - med) <= 0.10 * med) / n
        beacons = sorted({c["serie"] for c in cs if c["beacon"]})
        alerta = (n >= cfg["min_conexoes"] and len(ivs) > 0 and media <= cfg["max_intervalo"]
                  and jitter <= cfg["max_jitter"] and estab >= cfg["min_estabilidade"])
        res.append({"chave": k, "n": n, "media": media, "jitter": jitter, "estab": estab,
                    "series": sorted({c["serie"] for c in cs}), "beacons": beacons, "alerta": alerta})
    res.sort(key=lambda g: (not g["alerta"], g["jitter"], g["chave"]))
    return res, ignoradas


def placar_conexoes(d, grupos):
    """Espelho de placarConexoes: alertas com beacon, falsos positivos e beacons perdidos."""
    todos = {s["id"] for s in d["series"] if s["rotulo"] == "beacon"}
    alertas = [g for g in grupos if g["alerta"]]
    vp = [g for g in alertas if g["beacons"]]
    fp = [g for g in alertas if not g["beacons"]]
    vistos = {b for g in vp for b in g["beacons"]}
    return {"vp": len(vp), "fp": len(fp), "fn": len(todos - vistos), "fp_series": sorted(s for g in fp for s in g["series"])}


def base_dominio(q):
    return ".".join(q.split(".")[-2:])


def subdominio(q):
    return ".".join(q.split(".")[:-2])


def entropia(s):
    """Espelho de entropiaShannon: bits por caractere do subdomínio, sem os pontos."""
    s = s.replace(".", "")
    if not s:
        return 0.0
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in Counter(s).values())


def agrupar_dns(d, cfg):
    """Espelho de agruparDns: agrupa o dns.log por domínio base e mede os subdomínios."""
    g = {}
    for r in d["dns"]:
        g.setdefault(base_dominio(r[2]), []).append(r)
    res = []
    for base, rs in g.items():
        subs = [subdominio(r[2]) for r in rs]
        n = len(rs)
        distintos = len({r[2] for r in rs})
        comp = sum(len(s) for s in subs) / n
        ent = sum(entropia(s) for s in subs) / n
        rotulo = d["dominios"].get(base, {"rotulo": "benigno"})["rotulo"]
        alerta = (distintos >= cfg["dns_min_distintos"] and comp >= cfg["dns_min_comprimento"]
                  and ent >= cfg["dns_min_entropia"])
        res.append({"base": base, "n": n, "distintos": distintos, "comp": comp, "ent": ent, "rotulo": rotulo,
                    "alerta": alerta, "origens": sorted({r[1] for r in rs}), "qtypes": Counter(r[3] for r in rs)})
    res.sort(key=lambda x: (not x["alerta"], -x["ent"], x["base"]))
    return res


def placar_dns(grupos):
    """Espelho de placarDns: só o túnel conta como acerto; o domínio de C2 não é túnel."""
    return {"vp": sum(1 for g in grupos if g["alerta"] and g["rotulo"] == "tunel"),
            "fp": sum(1 for g in grupos if g["alerta"] and g["rotulo"] != "tunel"),
            "fn": sum(1 for g in grupos if not g["alerta"] and g["rotulo"] == "tunel"),
            "fp_bases": [g["base"] for g in grupos if g["alerta"] and g["rotulo"] != "tunel"]}


def decodificar_base32(rotulo):
    """Espelho de decodificarBase32: texto legível ou None (rótulos curtos não carregam dados)."""
    if len(rotulo) < 16 or any(ch not in ALFABETO_B32 for ch in rotulo):
        return None
    pad = "=" * (-len(rotulo) % 8)
    try:
        bruto = base64.b32decode(rotulo.upper() + pad)
    except Exception:
        return None
    legiveis = sum(1 for b in bruto if b in (9, 10, 13) or 32 <= b < 127)
    return bruto.decode("ascii", "replace") if bruto and legiveis / len(bruto) >= 0.9 else None


IDEAL = {"so_externos": True, "max_intervalo": 240, "max_jitter": 35, "min_estabilidade": 80, "excecoes": ["exc-ntp"]}


class TestMonitoramentoRedeNSM(unittest.TestCase):
    """Valida a estrutura, o conteúdo, o Analisador de Conexões e a compilação do estudo 48."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "monitoramento_de_rede_nsm_body.html"
        self.compiled_path = self.root / "Monitoramento-de-Rede-NSM" / "treinamento-monitoramento-de-rede-nsm.html"
        self.portal_path = self.root / "index.html"

    def _dados(self):
        body = self.body_path.read_text(encoding="utf-8")
        m = re.search(r'<script type="application/json" id="nsm-dados">(.*?)</script>', body, re.S)
        self.assertIsNotNone(m, "Bloco JSON #nsm-dados ausente no body")
        return json.loads(m.group(1))

    def _cfg(self, d, **extra):
        cfg = dict(d["padrao"])
        cfg.update(extra)
        return cfg

    # ------------------------------------------------------------ estrutura
    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_seis_secoes_obrigatorias(self):
        body = self.body_path.read_text(encoding="utf-8")
        ids = re.findall(r'<section class="study-section" id="([\w-]+)"', body)
        self.assertEqual(len(ids), 6, ids)
        self.assertEqual(ids[2:], ["simulador", "checklist", "quiz", "fatos"])
        for n in range(1, 7):
            self.assertIn(f"Seção 0{n}", body)
        self.assertIn('data-slug="monitoramento-de-rede-nsm"', body)

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        termos = ["Network Security Monitoring", "NSM", "Zeek", "PCAP", "NetFlow", "IPFIX", "RFC 7011",
                  "conn.log", "dns.log", "ssl.log", "id.orig_h", "id.resp_h", "id.resp_p", "orig_bytes",
                  "resp_bytes", "conn_state", "qtype_name", "answers", "server_name", "zeek-cut",
                  "beaconing", "jitter", "coeficiente de variação", "túnel DNS", "entropia", "Shannon",
                  "base32", "TXT", "JA3", "JA4", "SNI", "TLS 1.3", "TAP", "SPAN", "amostragem",
                  "RITA", "nfdump", "tcpdump", "T1071", "T1071.004", "T1048", "exceção documentada",
                  "Estudo 07", "Estudo 02", "Estudo 46", "Estudo 47", "Estudo 49", "RFC 5737", "LGPD"]
        for termo in termos:
            self.assertIn(termo, content, f"Termo obrigatório ausente: {termo}")

    def test_coerencia_com_o_catalogo(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        info = ESTUDOS_DADOS["Monitoramento-de-Rede-NSM"]
        self.assertIn(info["simulador_nome"], content)
        self.assertIn(info["pergunta_chave"], content)
        for fato in info["fatos"]:
            self.assertIn(fato, content, fato)

    def test_diferenca_para_o_modulo_07_e_ponte_da_trilha(self):
        body = self.body_path.read_text(encoding="utf-8")
        intro = body[:body.index('id="simulador"')]
        self.assertIn("assinatura", intro)
        self.assertIn("Estudo 07", intro)
        fim = body[body.index('id="fatos"'):body.index("</article>")]
        self.assertIn("Estudo 47", fim)
        self.assertIn("Estudo 49", fim)

    # ---------------------------------------------------------------- dados
    def test_pcap_rotativo_nao_para_apos_48_arquivos(self):
        """Com -G, o -W encerra o tcpdump ao atingir o limite: a retenção de 48 h vem da limpeza por idade."""
        body = self.body_path.read_text(encoding="utf-8")
        self.assertNotIn("-W 48", body)
        self.assertIn("-mmin +2880 -delete", body)

    def test_dados_ficticios_e_bem_formados(self):
        d = self._dados()
        self.assertIn(".example", d["contexto"])
        self.assertIn("RFC 5737", d["contexto"])
        ips = set()
        for s in d["series"]:
            n = len(s["intervalos"]) + 1
            for campo in ("orig_bytes", "resp_bytes", "duracao"):
                self.assertEqual(len(s[campo]), n, (s["id"], campo))
            self.assertTrue(all(iv > 0 for iv in s["intervalos"]), s["id"])
            self.assertLess(s["t0"] + sum(s["intervalos"]), d["janela_s"], s["id"])
            self.assertIn(s["rotulo"], ("beacon", "benigno"))
            self.assertTrue(s["nota"])
            self.assertIn(s["orig_h"], d["hosts"], "toda origem é um host conhecido da Ipê Store")
            self.assertTrue(privado(s["orig_h"]))
            ips.update([s["orig_h"], s["resp_h"]])
            if "ssl" in s:
                self.assertTrue(s["ssl"]["server_name"].endswith(".example"))
        for r in d["dns"]:
            self.assertEqual(len(r), 5)
            self.assertTrue(r[2].endswith(".example"), r[2])
            self.assertIn(r[1], d["hosts"])
            ips.add(r[1])
            if r[3] == "A":
                ips.add(r[4])
        for ip in ips:
            a = ipaddress.ip_address(ip)
            self.assertTrue(privado(ip) or a.is_loopback or any(a in n for n in REDES_DOC), ip)
        self.assertEqual(len({s["id"] for s in d["series"]}), len(d["series"]))
        self.assertEqual(sorted(s["id"] for s in d["series"] if s["rotulo"] == "beacon"), ["beacon-fin03", "beacon-ven07"])
        self.assertEqual({k: v["rotulo"] for k, v in d["dominios"].items() if v["rotulo"] != "benigno"},
                         {"dados-cdn.example": "tunel", "onedrive-relatorios.example": "c2"})
        self.assertEqual({e["id"] for e in d["excecoes"]}, {"exc-ntp", "exc-edr", "exc-zabbix"})

    def test_conn_log_tem_volume_de_uma_hora(self):
        d = self._dados()
        conns = expandir_conexoes(d)
        self.assertEqual(len(conns), sum(len(s["intervalos"]) + 1 for s in d["series"]))
        self.assertGreater(len(conns), 600)
        self.assertEqual(len(d["dns"]), 362)
        self.assertEqual(d["inicio_ts"], 1793620800, "02/11/2026 09:00 em UTC-3")

    # ------------------------------------------------------------ beaconing
    def test_metricas_dos_pares(self):
        d = self._dados()
        grupos, _ = agrupar_conexoes(d, self._cfg(d))
        por_serie = {g["series"][0]: g for g in grupos}
        self.assertEqual(len(grupos), len(d["series"]), "agrupar por par: um grupo por série")
        fin, ven = por_serie["beacon-fin03"], por_serie["beacon-ven07"]
        for g in (fin, ven):
            self.assertAlmostEqual(g["media"], 60, delta=3, msg="o implante fala a cada 60 s")
            self.assertGreaterEqual(g["estab"], 95, "check-ins quase do mesmo tamanho")
        self.assertLess(fin["jitter"], 10)
        self.assertTrue(20 < ven["jitter"] < 30, ven["jitter"])
        for sid in ("ntp-lnx01", "pdv-gateway", "zabbix-10", "zabbix-20", "zabbix-30"):
            self.assertLess(por_serie[sid]["jitter"], 1, sid)
        self.assertLess(por_serie["pdv-gateway"]["estab"], 30, "o lote de vendas muda de tamanho")
        for g in grupos:
            if g["series"][0].startswith(("nav-", "erp-")):
                self.assertGreater(g["jitter"], 70, g["chave"])

    def test_limiares_padrao_contam_os_falsos_positivos(self):
        d = self._dados()
        grupos, ign = agrupar_conexoes(d, self._cfg(d))
        p = placar_conexoes(d, grupos)
        self.assertEqual((p["vp"], p["fp"], p["fn"]), (1, 11, 1))
        self.assertEqual(ign, 0)
        fps = p["fp_series"]
        self.assertIn("ntp-lnx01", fps)
        self.assertIn("pdv-gateway", fps)
        self.assertEqual(sum(1 for s in fps if s.startswith("edr-")), 6)
        self.assertEqual(sum(1 for s in fps if s.startswith("zabbix-")), 3)

    def test_cada_ajuste_remove_um_tipo_de_falso_positivo(self):
        d = self._dados()
        casos = [({"so_externos": True}, 8, "zabbix-"), ({"max_intervalo": 240}, 5, "edr-"),
                 ({"min_estabilidade": 80}, 10, "pdv-"), ({"excecoes": ["exc-edr", "exc-zabbix"]}, 2, "edr-")]
        for extra, fp, removido in casos:
            with self.subTest(ajuste=extra):
                p = placar_conexoes(d, agrupar_conexoes(d, self._cfg(d, **extra))[0])
                self.assertEqual(p["fp"], fp)
                self.assertFalse(any(s.startswith(removido) for s in p["fp_series"]))
        # jitter maior recupera o beacon de jitter alto sem trazer navegação
        p = placar_conexoes(d, agrupar_conexoes(d, self._cfg(d, max_jitter=35))[0])
        self.assertEqual((p["vp"], p["fn"], p["fp"]), (2, 0, 11))

    def test_ntp_so_sai_com_excecao_documentada(self):
        d = self._dados()
        sem_excecao = dict(IDEAL, excecoes=[])
        p = placar_conexoes(d, agrupar_conexoes(d, self._cfg(d, **sem_excecao))[0])
        self.assertEqual((p["vp"], p["fp"], p["fn"]), (2, 1, 0))
        self.assertEqual(p["fp_series"], ["ntp-lnx01"])
        grupos, ign = agrupar_conexoes(d, self._cfg(d, **IDEAL))
        p = placar_conexoes(d, grupos)
        self.assertEqual((p["vp"], p["fp"], p["fn"]), (2, 0, 0))
        self.assertEqual(ign, 180 + 57, "zabbix interno + NTP por exceção")

    def test_agrupamento_errado_esconde_o_beacon(self):
        d = self._dados()
        for agrupar in ("destino", "origem"):
            with self.subTest(agrupar=agrupar):
                grupos, _ = agrupar_conexoes(d, self._cfg(d, **dict(IDEAL, agrupar=agrupar)))
                p = placar_conexoes(d, grupos)
                self.assertEqual((p["vp"], p["fn"]), (0, 2))
                com_beacon = [g for g in grupos if g["beacons"]]
                self.assertTrue(all(g["jitter"] > 40 for g in com_beacon), [g["jitter"] for g in com_beacon])
        destino = agrupar_conexoes(d, self._cfg(d, agrupar="destino"))[0]
        c2 = next(g for g in destino if g["beacons"])
        self.assertEqual(c2["beacons"], ["beacon-fin03", "beacon-ven07"])
        self.assertLess(c2["media"], 40, "duas séries intercaladas parecem mais rápidas e irregulares")

    # ------------------------------------------------------------- túnel DNS
    def test_dns_limiares_padrao_e_ajuste(self):
        d = self._dados()
        p = placar_dns(agrupar_dns(d, self._cfg(d)))
        self.assertEqual((p["vp"], p["fp"], p["fn"]), (1, 2, 0))
        self.assertEqual(sorted(p["fp_bases"]), ["antivirus-nuvem.example", "anuncios-rastreio.example"])
        for extra in ({"dns_min_comprimento": 40}, {"dns_min_entropia": 4.0}):
            with self.subTest(ajuste=extra):
                self.assertEqual(placar_dns(agrupar_dns(d, self._cfg(d, **extra)))["fp"], 0)
                self.assertEqual(placar_dns(agrupar_dns(d, self._cfg(d, **extra)))["vp"], 1)
        # exigir volume demais perde o túnel
        self.assertEqual(placar_dns(agrupar_dns(d, self._cfg(d, dns_min_distintos=200)))["fn"], 1)

    def test_metricas_do_tunel_dns(self):
        d = self._dados()
        grupos = {g["base"]: g for g in agrupar_dns(d, self._cfg(d))}
        t = grupos["dados-cdn.example"]
        self.assertEqual(t["origens"], ["10.20.3.13"])
        self.assertEqual(t["qtypes"], Counter({"TXT": 120}))
        self.assertEqual(t["distintos"], 120)
        self.assertGreater(t["comp"], 55)
        self.assertGreater(t["ent"], 4.2)
        av = grupos["antivirus-nuvem.example"]
        self.assertLess(av["ent"], 4.0, "hexadecimal: no máximo 4 bits por caractere")
        self.assertLess(grupos["ipestore.example"]["ent"], 3.0)
        self.assertEqual(grupos["onedrive-relatorios.example"]["alerta"], False, "C2 por A não é túnel")

    def test_tunel_carrega_as_notas_fiscais(self):
        d = self._dados()
        rotulos = [r[2].split(".")[0] for r in d["dns"] if base_dominio(r[2]) == "dados-cdn.example"]
        texto = "".join(decodificar_base32(x) or "" for x in rotulos)
        self.assertTrue(texto.startswith("NF-e EXPORTADA"), texto[:40])
        self.assertGreater(texto.count("nfe;"), 80)
        self.assertTrue(all(len(x) == 56 for x in rotulos))
        for r in d["dns"]:
            if base_dominio(r[2]) != "dados-cdn.example":
                self.assertIsNone(decodificar_base32(r[2].split(".")[0]), r[2])

    # ------------------------------------------------------------- pivôs
    def test_dns_liga_o_ip_do_beacon_ao_dominio(self):
        d = self._dados()
        ip = next(s["resp_h"] for s in d["series"] if s["id"] == "beacon-fin03")
        nomes = {r[2] for r in d["dns"] if r[3] == "A" and r[4] == ip}
        self.assertEqual(nomes, {"sync.onedrive-relatorios.example"})
        self.assertEqual({r[1] for r in d["dns"] if r[2] in nomes}, {"10.20.3.13", "10.20.7.17"})

    def test_ja3_e_indicio_nao_prova(self):
        d = self._dados()
        beacon = next(s for s in d["series"] if s["id"] == "beacon-fin03")["ssl"]
        iguais = [s["id"] for s in d["series"] if s["rotulo"] == "benigno" and s.get("ssl", {}).get("ja3") == beacon["ja3"]]
        self.assertGreaterEqual(len(iguais), 6, "a mesma impressão aparece em software legítimo")
        self.assertTrue(any(s.startswith("edr-") for s in iguais))
        self.assertTrue(re.fullmatch(r"[0-9a-f]{32}", beacon["ja3"]))
        self.assertTrue(re.fullmatch(r"t1[23]d\d{4}h[12]_[0-9a-f]{12}_[0-9a-f]{12}", beacon["ja4"]))
        nav = [s["ssl"]["ja3"] for s in d["series"] if s["id"].startswith("nav-")]
        self.assertTrue(all("varia" in j for j in nav), "navegadores embaralham as extensões TLS")

    # ------------------------------------------------------------ simulador
    def test_simulador_estrutura(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        for marcador in ("nsm-lab", 'id="nsm-dados"', "nsm-connlog", "nsm-dnslog", "nsm-agrupar",
                         "nsm-min-conexoes", "nsm-max-intervalo", "nsm-max-jitter", "nsm-min-estab",
                         "nsm-externos", "nsm-excecoes", "nsm-placar-conn", "nsm-grupos",
                         "nsm-dns-min-distintos", "nsm-dns-min-comp", "nsm-dns-min-ent", "nsm-placar-dns",
                         "nsm-dominios", "expandirConexoes", "agruparConexoes", "placarConexoes",
                         "agruparDns", "placarDns", "entropiaShannon", "decodificarBase32",
                         "analisarConexoesNsm", "analisarDnsNsm", "restaurarPadraoNsm"):
            self.assertIn(marcador, content, marcador)
        for campo in ("nsm-agrupar", "nsm-min-conexoes", "nsm-max-intervalo", "nsm-max-jitter", "nsm-min-estab",
                      "nsm-externos", "nsm-dns-min-distintos", "nsm-dns-min-comp", "nsm-dns-min-ent"):
            self.assertRegex(content, r'<label[^>]*for="%s"' % campo)
        ini = content.index("var NSM = JSON.parse")
        motor = content[ini:content.index("</script>", ini)]
        for proibido in ("innerHTML", "eval(", "new Function", "fetch(", "XMLHttpRequest", "WebSocket"):
            self.assertNotIn(proibido, motor, proibido)

    def test_componentes_pedagogicos(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        self.assertIn('class="callout', content)
        self.assertIn('class="terminal-box', content)
        self.assertIn('class="diagram-svg-wrap', content)
        self.assertNotIn('<pre class="mermaid"', content)
        self.assertEqual(content.count('class="checklist-item"'), 7)
        self.assertGreaterEqual(content.count('class="quiz-item"'), 6)
        self.assertIn('class="facts-grid', content)
        self.assertIn('initChecklist("monitoramento-de-rede-nsm")', content)
        self.assertNotIn("cdn.", content.lower().replace("cdnjs", "").replace("cdn.example", ""))

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn("Monitoramento-de-Rede-NSM/treinamento-monitoramento-de-rede-nsm.html", content)
        self.assertIn('data-slug="Monitoramento-de-Rede-NSM"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)


if __name__ == "__main__":
    unittest.main()
