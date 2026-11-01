#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_protecao_dados_conteudo.py
Testes automatizados para o Estudo 29: Protecao-de-Dados-e-Conteudo

O motor do Gateway de Conteúdo é reimplementado aqui em Python, com as mesmas
regras do JavaScript, para validar os dados e os vereditos esperados.
"""

import copy
import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402

SEVERIDADE = {"permitir": 0, "quarentena": 1, "bloquear": 2}
RE_CPF = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")
RE_CARTAO = re.compile(r"\b(?:\d[ -]?){12,18}\d\b")
RE_URL = re.compile(r"https?://[^\s<>\"']+")


# ------------------------------------------------------------------ detectores
def cpf_valido(texto):
    d = re.sub(r"\D", "", texto)
    if len(d) != 11 or len(set(d)) == 1:
        return False
    for n in (9, 10):
        s = sum(int(d[i]) * (n + 1 - i) for i in range(n))
        r = s % 11
        if int(d[n]) != (0 if r < 2 else 11 - r):
            return False
    return True


def luhn_valido(texto):
    d = [int(x) for x in re.sub(r"\D", "", texto)][::-1]
    total = 0
    for i, x in enumerate(d):
        if i % 2:
            x *= 2
            if x > 9:
                x -= 9
        total += x
    return total % 10 == 0


def dominio(endereco):
    return endereco.split("@")[-1].lower()


def org(dom):
    return ".".join(dom.lower().split(".")[-2:])


def maior(*vereditos):
    return max((v for v in vereditos if v), key=lambda v: SEVERIDADE[v])


# ---------------------------------------------------------------------- motor
def antispam(d, item, pol):
    if item["tipo"] != "email-entrada":
        return None
    info = {}
    if pol["bloquear_lista"] and item["lista_bloqueio"]:
        info["veredito"] = "bloquear"
        return info
    de = dominio(item["de"])
    spf_alinhado = item["spf"] == "pass" and org(dominio(item["envelope"])) == org(de)
    dkim_alinhado = item["dkim"] == "pass" and org(item["dkim_dominio"]) == org(de)
    info["dmarc"] = "pass" if (spf_alinhado or dkim_alinhado) else "fail"
    veredito = "permitir"
    if info["dmarc"] == "fail" and pol["respeitar_dmarc"]:
        veredito = {"reject": "bloquear", "quarantine": "quarentena", "none": "permitir"}[item["dmarc_politica"]]
    texto = (item["assunto"] + " " + item["corpo"]).lower()
    pontos = sum(r["pontos"] for r in d["regras_spam"] if r["termo"] in texto)
    if item["idade_dominio_dias"] < d["idade_dominio_novo"]:
        pontos += d["pontos_dominio_novo"]
    info["pontos"] = pontos
    if pontos >= pol["limiar_spam"]:
        veredito = maior(veredito, "quarentena")
    info["veredito"] = veredito
    return info


def dlp(d, item, pol):
    if item["tipo"] == "email-entrada":
        return None
    info = {}
    if item["tipo"] == "email-saida" and dominio(item["para"]) == d["dominio_interno"]:
        info["veredito"] = "permitir"
        return info
    texto = (item.get("assunto", "") + " " + item["corpo"])
    cpfs = {re.sub(r"\D", "", m) for m in RE_CPF.findall(texto)
            if not pol["validar_cpf"] or cpf_valido(m)}
    cartoes = {re.sub(r"\D", "", m) for m in RE_CARTAO.findall(texto)
               if not pol["validar_luhn"] or luhn_valido(m)}
    palavras = [p for p in pol["palavras_chave"] if p.strip() and p.strip().lower() in texto.lower()]
    info.update(cpfs=len(cpfs), cartoes=len(cartoes), palavras=len(palavras))
    veredito = "permitir"
    if palavras:
        veredito = "quarentena"
    if cartoes or len(cpfs) >= pol["limiar_cpf"]:
        veredito = "bloquear"
    info["veredito"] = veredito
    return info


def filtro_url(d, item, pol):
    urls = [item["url"]] if item["tipo"] == "upload" else RE_URL.findall(item["corpo"])
    veredito = "permitir"
    cats = []
    for u in urls:
        host = re.sub(r"^https?://", "", u).split("/")[0].split(":")[0].lower()
        cat = d["dominios"].get(org(host), "nao-categorizado")
        cats.append(cat)
        if cat in pol["categorias_bloqueadas"]:
            veredito = maior(veredito, "bloquear")
        elif cat == "nao-categorizado":
            veredito = maior(veredito, "quarentena")
    return {"veredito": veredito, "categorias": cats}


def processar(d, item, pol):
    estagios = [antispam(d, item, pol), dlp(d, item, pol), filtro_url(d, item, pol)]
    return maior(*[e["veredito"] for e in estagios if e]), estagios


class TestProtecaoDadosConteudo(unittest.TestCase):
    """Valida a estrutura, o conteúdo, o motor e a compilação do estudo Protecao-de-Dados-e-Conteudo."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "protecao_de_dados_e_conteudo_body.html"
        self.compiled_path = (self.root / "Protecao-de-Dados-e-Conteudo"
                              / "treinamento-protecao-de-dados-e-conteudo.html")
        self.portal_path = self.root / "index.html"

    def _dados(self):
        body = self.body_path.read_text(encoding="utf-8")
        m = re.search(r'<script type="application/json" id="cdc-dados">(.*?)</script>', body, re.S)
        self.assertIsNotNone(m, "Bloco JSON #cdc-dados ausente no body")
        return json.loads(m.group(1))

    def _item(self, d, item_id):
        return next(i for i in d["itens"] if i["id"] == item_id)

    # ------------------------------------------------------------- detectores
    def test_detectores_de_checksum(self):
        self.assertTrue(cpf_valido("274.618.903-87"))
        self.assertFalse(cpf_valido("123.456.789-00"))
        self.assertFalse(cpf_valido("111.111.111-11"))
        self.assertTrue(luhn_valido("4111 1111 1111 1111"))
        self.assertFalse(luhn_valido("4000 1234 5678 9010"))
        self.assertEqual(org("mail.fornecedor-embalagens.example"), "fornecedor-embalagens.example")

    # ---------------------------------------------------------------- arquivos
    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        termos = [
            "em uso", "em trânsito", "em repouso", "classificação da informação", "DLP de rede",
            "DLP de endpoint", "CASB", "regex", "dígito verificador", "Luhn", "dicionário", "EDM",
            "falso positivo", "falso negativo", "quarentena", "SPF", "RFC 7208", "DKIM", "RFC 6376",
            "DMARC", "RFC 7489", "alinhamento", "p=none", "p=quarantine", "p=reject", "DNSBL",
            "SWG", "categoria", "inspeção TLS", "LGPD", "T1566", "T1567",
        ]
        for termo in termos:
            self.assertIn(termo, content, f"Termo obrigatório ausente: {termo}")

    # -------------------------------------------------------------------- dados
    def test_dados_validos(self):
        d = self._dados()
        pol = d["politica_padrao"]
        self.assertEqual(len(d["itens"]), 8)
        ids = [i["id"] for i in d["itens"]]
        self.assertEqual(len(ids), len(set(ids)))
        for cat in pol["categorias_bloqueadas"]:
            self.assertIn(cat, d["categorias"])
        for dom, cat in d["dominios"].items():
            self.assertTrue(dom.endswith(".example"), f"{dom} deve usar o domínio reservado .example")
            self.assertIn(cat, d["categorias"])
        self.assertTrue(d["dominio_interno"].endswith(".example"))
        tipos = set()
        for item in d["itens"]:
            with self.subTest(item=item["id"]):
                tipos.add(item["tipo"])
                self.assertIn(item["esperado"], SEVERIDADE)
                self.assertTrue(item["titulo"].strip())
                self.assertTrue(item["licao"].strip())
                self.assertTrue(item["corpo"].strip())
                for campo in ("de", "para", "envelope", "dkim_dominio", "url"):
                    if campo in item:
                        self.assertTrue(dominio(item[campo]).split("/")[0].endswith(".example") or
                                        re.sub(r"^https?://", "", item[campo]).split("/")[0].endswith(".example"),
                                        f"{item['id']}.{campo}")
                if item["tipo"] == "email-entrada":
                    self.assertIn(item["spf"], d["resultados_spf"])
                    self.assertIn(item["dkim"], d["resultados_dkim"])
                    self.assertIn(item["dmarc_politica"], {"none", "quarantine", "reject"})
                if item["tipo"] == "upload":
                    self.assertTrue(item["arquivo"].strip())
        self.assertEqual(tipos, {"email-entrada", "email-saida", "upload"})

    def test_vereditos_esperados_com_politica_padrao(self):
        d = self._dados()
        vistos = set()
        for item in d["itens"]:
            with self.subTest(item=item["id"]):
                veredito, _ = processar(d, item, d["politica_padrao"])
                self.assertEqual(veredito, item["esperado"])
                vistos.add(veredito)
        self.assertEqual(vistos, set(SEVERIDADE))

    def test_dmarc_reject_e_dominio_parecido(self):
        d = self._dados()
        pol = d["politica_padrao"]
        bec = antispam(d, self._item(d, "bec-troca-conta"), pol)
        self.assertEqual(bec["dmarc"], "fail")
        self.assertEqual(bec["veredito"], "bloquear")
        parecido = antispam(d, self._item(d, "dominio-parecido"), pol)
        self.assertEqual(parecido["dmarc"], "pass", "o domínio parecido é do atacante e passa no DMARC")
        self.assertEqual(processar(d, self._item(d, "dominio-parecido"), pol)[0], "bloquear")
        news = self._item(d, "newsletter-parceiro")
        self.assertEqual(news["dmarc_politica"], "none")
        self.assertEqual(antispam(d, news, pol)["dmarc"], "fail")

    def test_validacao_de_cpf_evita_falso_positivo(self):
        d = self._dados()
        item = self._item(d, "relatorio-pedidos")
        pol = copy.deepcopy(d["politica_padrao"])
        self.assertEqual(processar(d, item, pol)[0], "permitir")
        pol["validar_cpf"] = False
        self.assertEqual(processar(d, item, pol)[0], "bloquear")
        planilha = dlp(d, self._item(d, "planilha-cpfs"), d["politica_padrao"])
        self.assertEqual(planilha["cpfs"], 3, "só os 3 CPFs com dígito verificador correto contam")

    def test_luhn_e_cartoes_mascarados(self):
        d = self._dados()
        pol = d["politica_padrao"]
        backup = dlp(d, self._item(d, "backup-drive-pessoal"), pol)
        self.assertEqual(backup["cartoes"], 2, "o número que falha no Luhn não conta")
        conciliacao = dlp(d, self._item(d, "conciliacao-gateway"), pol)
        self.assertEqual(conciliacao["cartoes"], 0)

    # ---------------------------------------------------------------- compilado
    def test_simulador_estrutura(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        for marcador in ("cdc-lab", 'id="cdc-dados"', "cdc-pipeline", "cdc-politicas", "cdc-veredito",
                         "selecionarItemConteudo", "processarConteudo", "restaurarConteudo"):
            self.assertIn(marcador, content, marcador)
        ini = content.index("var CDC = JSON.parse")
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
        self.assertIn('initChecklist("protecao-dados-conteudo")', content)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn("Protecao-de-Dados-e-Conteudo/treinamento-protecao-de-dados-e-conteudo.html", content)
        self.assertIn('data-slug="Protecao-de-Dados-e-Conteudo"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)


if __name__ == "__main__":
    unittest.main()
