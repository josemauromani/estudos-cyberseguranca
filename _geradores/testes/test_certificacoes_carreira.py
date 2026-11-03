#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_certificacoes_carreira.py
Testes automatizados para o Estudo 33: Certificacoes-e-Carreira
"""

import json
import re
import sys
import unittest
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import CERTIFICACOES, ESTUDOS_DADOS  # noqa: E402

GERADORES = Path(__file__).resolve().parent.parent
DOMINIO_OFICIAL = {
    "CEH": "eccouncil.org",
    "CISM": "isaca.org",
    "CISA": "isaca.org",
    "CRISC": "isaca.org",
    "CDPSE": "isaca.org",
    "CISSP": "isc2.org",
    "CCSP": "isc2.org",
    "GSEC": "giac.org",
    "Security+": "comptia.org",
    "ISFS": "exin.com",
    "PDPF/PDPP": "exin.com",
    "ITIL 4 F": "peoplecert.org",
    "CSFPC": "certiprof.com",
    "ISO 27001 LA": "pecb.com",
    "eJPT": "ine.com",
    "eCPPT": "ine.com",
    "OSCP": "offsec.com",
}
CAMPOS_PERFIL = ("anos_ti", "anos_si", "anos_gestao_si", "anos_nuvem")


def catalogo():
    """slug -> número do módulo, na ordem de _geradores/estudos.txt."""
    numeros = {}
    for linha in (GERADORES / "estudos.txt").read_text(encoding="utf-8").splitlines():
        if linha.strip() and not linha.startswith("#"):
            numeros[linha.split("|")[0]] = len(numeros) + 1
    return numeros


def efetivo(perfil):
    """Gestão de segurança conta como segurança; segurança e nuvem contam como TI."""
    p = dict(perfil)
    p["anos_si"] = max(p.get("anos_si", 0), p.get("anos_gestao_si", 0))
    p["anos_ti"] = max(p.get("anos_ti", 0), p["anos_si"], p.get("anos_nuvem", 0))
    return p


def elegibilidade(cert, perfil):
    """Regra espelhada no JavaScript: 'conferir', 'sem-exigencia', 'elegivel' ou 'pendente'."""
    perfil = efetivo(perfil)
    req = cert["requisitos"]
    if req.get("conferir"):
        return "conferir"
    if not req:
        return "sem-exigencia"
    if req.get("alternativa") and perfil.get("treinamento_oficial"):
        return "elegivel"
    for campo in CAMPOS_PERFIL:
        if campo in req:
            minimo = req[campo]
            if campo == "anos_si" and perfil.get("graduacao"):
                minimo -= req.get("desconto_graduacao", 0)
            if perfil.get(campo, 0) < minimo:
                return "pendente"
    return "elegivel"


class TestCertificacoesCarreira(unittest.TestCase):
    """Valida a estrutura, o conteúdo, a coerência com o portal e a compilação do estudo Certificacoes-e-Carreira."""

    def setUp(self):
        self.root = GERADORES.parent
        self.body_path = GERADORES / "certificacoes_e_carreira_body.html"
        self.compiled_path = self.root / "Certificacoes-e-Carreira" / "treinamento-certificacoes-e-carreira.html"
        self.portal_path = self.root / "index.html"

    def _dados(self):
        body = self.body_path.read_text(encoding="utf-8")
        m = re.search(r'<script type="application/json" id="cert-dados">(.*?)</script>', body, re.S)
        self.assertIsNotNone(m, "Bloco JSON #cert-dados ausente no body")
        return json.loads(m.group(1))

    def _cert(self, d, sigla):
        return next(c for c in d["certificacoes"] if c["sigla"] == sigla)

    # ----------------------------------------------------------------- arquivos
    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        termos = [
            "Ciência da Computação", "Sistemas de Informação", "tecnólogo", "lato sensu", "stricto sensu",
            "360 horas", "CEH", "EC-Council", "CISM", "ISACA", "CISSP", "ISC2", "CCSP", "GSEC", "GIAC",
            "Security+", "CompTIA", "SY0-701", "Associate of ISC2", "CPE", "ISO/IEC 17024",
            "NICE Framework", "NIST SP 800-181", "Work Role", "TKS",
        ]
        for termo in termos:
            self.assertIn(termo, content, f"Termo obrigatório ausente: {termo}")

    # -------------------------------------------------------------------- dados
    def test_coerencia_com_a_matriz_do_portal(self):
        d = self._dados()
        self.assertEqual([c["sigla"] for c in d["certificacoes"]], [c["sigla"] for c in CERTIFICACOES])
        for portal in CERTIFICACOES:
            with self.subTest(cert=portal["sigla"]):
                cert = self._cert(d, portal["sigla"])
                self.assertEqual(cert["nome"], portal["nome"])
                self.assertEqual(cert["orgao"], portal["orgao"])
                cobertos = {m for dom in cert["dominios"] for m in dom["modulos"]}
                faltando = set(portal["modulos"]) - cobertos
                self.assertFalse(faltando, f"módulos do portal sem domínio: {faltando}")

    # ------------------------------------------------------------ fontes oficiais
    def test_fontes_oficiais(self):
        d = self._dados()
        self.assertEqual(d["conferido_em"], "novembro de 2026")
        for c in d["certificacoes"]:
            with self.subTest(cert=c["sigla"]):
                dominio = DOMINIO_OFICIAL[c["sigla"]]
                self.assertTrue(c["fontes"], "fontes vazia")
                for f in c["fontes"]:
                    self.assertTrue(f["titulo"].strip())
                    self.assertTrue(f["url"].startswith("https://"), f["url"])
                    host = urlparse(f["url"]).hostname or ""
                    self.assertTrue(host == dominio or host.endswith("." + dominio), f["url"])

    def test_site_oficial_coerente(self):
        d = self._dados()
        for c in CERTIFICACOES:
            with self.subTest(cert=c["sigla"]):
                self.assertEqual(c["site_oficial"], self._cert(d, c["sigla"])["fontes"][0]["url"])

    def test_fontes_no_cartao(self):
        body = self.body_path.read_text(encoding="utf-8")
        m = re.search(r"function cartaoCert\(c\) \{(.*?)\n    \}\n", body, re.S)
        self.assertIsNotNone(m)
        corpo = m.group(1)
        for trecho in ("Fontes oficiais: ", "/^https:\\/\\//.test(", "noopener noreferrer", "overflow-wrap: anywhere"):
            self.assertIn(trecho, corpo)
        self.assertNotIn("innerHTML", corpo)
        self.assertIn("Fontes conferidas em ", body)
        self.assertIn("CERT.conferido_em", body)

    def test_fatos_lista_sites_oficiais(self):
        body = self.body_path.read_text(encoding="utf-8")
        ini = body.index('id="fatos"')
        fatos = body[ini:body.index("</section>", ini)]
        for c in CERTIFICACOES:
            with self.subTest(cert=c["sigla"]):
                self.assertIn(c["site_oficial"], fatos)

    def test_modulos_pendentes_sinalizados(self):
        """Módulo sem página compilada aparece como pendente no planejador, como no portal."""
        paginas = {}
        for linha in (GERADORES / "estudos.txt").read_text(encoding="utf-8").splitlines():
            if linha.strip() and not linha.startswith("#"):
                campos = linha.split("|")
                paginas[campos[0]] = self.root / campos[2] / campos[3]
        d = self._dados()
        for slug, info in d["modulos"].items():
            with self.subTest(modulo=slug):
                self.assertEqual(info.get("pendente", False), not paginas[slug].exists())
        body = self.body_path.read_text(encoding="utf-8")
        rotulo = re.search(r"function rotuloModulo\(slug\) \{(.*?)\n    \}", body, re.S)
        self.assertIsNotNone(rotulo)
        self.assertIn("m.pendente", rotulo.group(1))
        self.assertIn("em elaboração", rotulo.group(1))

    def test_modulos_batem_com_o_catalogo(self):
        d = self._dados()
        numeros = catalogo()
        usados = {m for c in d["certificacoes"] for dom in c["dominios"] for m in dom["modulos"]}
        self.assertEqual(set(d["modulos"]), usados, "o dicionário de módulos deve ter exatamente os usados")
        for slug, info in d["modulos"].items():
            with self.subTest(modulo=slug):
                self.assertIn(slug, ESTUDOS_DADOS)
                self.assertEqual(info["numero"], numeros[slug])
                self.assertEqual(info["titulo"], ESTUDOS_DADOS[slug]["titulo"])

    def test_dominios_e_pesos(self):
        d = self._dados()
        esperados = {"Security+": 5, "CISSP": 8, "CCSP": 6, "CISM": 4, "CEH": 9,
                     "ISFS": 4, "PDPF/PDPP": 11, "ITIL 4 F": 7, "CSFPC": 9, "CISA": 5, "ISO 27001 LA": 7,
                     "eJPT": 4, "eCPPT": 6, "OSCP": 10, "CRISC": 4, "CDPSE": 4}
        com_pesos = ("Security+", "CISSP", "CCSP", "CISM", "CISA", "ISFS", "ITIL 4 F", "eJPT", "eCPPT", "CRISC", "CDPSE")
        entrada = ("Security+", "ISFS", "PDPF/PDPP", "ITIL 4 F", "CSFPC", "eJPT")
        for c in d["certificacoes"]:
            with self.subTest(cert=c["sigla"]):
                self.assertIn(c["nivel"], (1, 2, 3))
                if c["sigla"] in entrada:
                    self.assertEqual(c["nivel"], 1)
                for campo in ("foco", "experiencia", "manutencao", "nota_dominios"):
                    self.assertTrue(c[campo].strip(), campo)
                if c["sigla"] in esperados:
                    self.assertEqual(len(c["dominios"]), esperados[c["sigla"]])
                pesos = [dom["peso"] for dom in c["dominios"]]
                if c["sigla"] in com_pesos:
                    self.assertEqual(sum(pesos), 100)
                else:
                    self.assertTrue(all(p is None for p in pesos),
                                    "sem pesos inventados para CEH, GSEC, PDPF/PDPP, CSFPC e ISO 27001 LA")
                for dom in c["dominios"]:
                    self.assertTrue(dom["nome"].strip())
                    if dom.get("parcial") or not dom["modulos"]:
                        self.assertTrue(dom.get("nota", "").strip(), f"{dom['nome']} precisa de nota")

    def test_revisao_contra_fontes_oficiais(self):
        """Valores conferidos nas páginas dos emissores em 3 de novembro de 2026."""
        d = self._dados()
        pesos = lambda sigla: [dom["peso"] for dom in self._cert(d, sigla)["dominios"]]
        self.assertEqual(pesos("CISM"), [18, 20, 33, 29])  # job practice em vigor desde 3/11/2026
        self.assertEqual(pesos("CCSP"), [17, 20, 17, 16, 17, 13])
        self.assertEqual(pesos("CISSP"), [16, 10, 13, 13, 13, 12, 13, 10])
        self.assertEqual(pesos("CISA"), [18, 18, 12, 26, 26])
        self.assertEqual(pesos("CRISC"), [26, 22, 32, 20])
        self.assertEqual(pesos("CDPSE"), [20, 18, 23, 39])
        self.assertEqual(pesos("Security+"), [12, 22, 18, 28, 20])
        self.assertIn("3 de novembro de 2026", self._cert(d, "CISM")["nota_dominios"])
        self.assertIn("17 de novembro de 2026", self._cert(d, "Security+")["nota_dominios"])
        self.assertIn("15 de abril de 2027", self._cert(d, "CISSP")["nota_dominios"])
        # O mínimo anual de CPE da ISC2 é apenas sugerido; só o total do ciclo é exigido.
        for sigla, total in (("CISSP", "120"), ("CCSP", "90")):
            m = self._cert(d, sigla)["manutencao"]
            self.assertIn(total + " CPE a cada 3 anos", m)
            self.assertIn("sugere", m)
            self.assertNotIn("mínimo de", m)
        cism = self._cert(d, "CISM")
        self.assertIn("em até 5 anos depois da aprovação", cism["sem_experiencia"])
        self.assertNotIn("aceita a experiência obtida", cism["sem_experiencia"])
        self.assertIn("10 anos anteriores ao pedido", cism["experiencia"])
        self.assertIn("confira as dispensas na ISACA", cism["experiencia"])
        urls_cism = [f["url"] for f in cism["fontes"]]
        self.assertIn("https://www.isaca.org/credentialing/cism/get-cism-certified", urls_cism)
        self.assertIn("https://support.isaca.org/s/article/What-are-the-requirements-to-become-CISM-certified", urls_cism)
        # A lista de provas que renovam a OSCP+ não é publicada na página conferida: sem lista.
        self.assertNotIn("OSEP", self._cert(d, "OSCP")["manutencao"])
        self.assertIn("outra certificação qualificada da OffSec", self._cert(d, "OSCP")["manutencao"])
        cripto = [dom for dom in self._cert(d, "OSCP")["dominios"] if "criptografia" in dom["nome"]][0]
        self.assertEqual(cripto["modulos"], ["Criptografia-Pratica"])
        self.assertTrue(cripto.get("parcial"))
        self.assertNotIn("17%", cism["nota_dominios"])
        self.assertNotIn("30%", cism["nota_dominios"])
        body = self.body_path.read_text(encoding="utf-8")
        self.assertNotIn("ou em até 5 anos depois da aprovação", body)
        self.assertIn("3 dos 4 domínios", self._cert(d, "CISM")["experiencia"])
        # Números que a página oficial não confirma foram trocados por remissão à página.
        self.assertNotIn("120", self._cert(d, "CEH")["manutencao"])
        self.assertIn("página oficial", self._cert(d, "CEH")["manutencao"])
        self.assertNotIn("3 anos", self._cert(d, "CSFPC")["manutencao"])
        # O exame da PECB, segundo o manual do candidato, é dissertativo (em transição para múltipla escolha).
        self.assertIn("dissertativ", self._cert(d, "ISO 27001 LA")["nota_dominios"])
        self.assertIn("https://www.giac.org/renewal", [f["url"] for f in self._cert(d, "GSEC")["fontes"]])

    def test_ajustes_da_revisao_final(self):
        cert = self.body_path.read_text(encoding="utf-8")
        self.assertIn("CEH Practical", cert)
        self.assertIn("https://www.comptia.org/en-us/blog/introducing-comptia-securityx/", cert)
        for errado in ("site oficial do ISACA", "site oficial do ISC2", "site oficial do CompTIA"):
            self.assertNotIn(errado, cert)
        pent = (GERADORES / "pentest_metodologias_body.html").read_text(encoding="utf-8")
        for url in ("https://www.offsec.com/products/oscp-plus/", "https://www.offsec.com/blog/oscp-grading-update/"):
            self.assertIn(url, pent)
        self.assertIn("CEH Practical", pent)
        self.assertNotIn("Consulte o site da INE</td>", pent)

    def test_lacuna_e_cobertura_parcial(self):
        d = self._dados()
        ceh = self._cert(d, "CEH")
        lacunas = [dom["nome"] for dom in ceh["dominios"] if not dom["modulos"]]
        parciais = [dom["nome"] for dom in ceh["dominios"] if dom.get("parcial")]
        self.assertEqual(len(lacunas), 1)
        self.assertIn("sem fio", lacunas[0])
        self.assertEqual(len(parciais), 1)

    def test_requisitos_de_experiencia(self):
        d = self._dados()
        req = {c["sigla"]: c["requisitos"] for c in d["certificacoes"]}
        self.assertEqual(req["Security+"], {})
        self.assertEqual(req["GSEC"], {})
        self.assertEqual(req["CEH"]["anos_si"], 2)
        self.assertTrue(req["CEH"]["alternativa"].strip())
        self.assertEqual((req["CISSP"]["anos_si"], req["CISSP"]["desconto_graduacao"]), (5, 1))
        self.assertEqual((req["CCSP"]["anos_ti"], req["CCSP"]["anos_si"], req["CCSP"]["anos_nuvem"]), (5, 3, 1))
        for sigla in ("ISFS", "ITIL 4 F", "CSFPC"):
            self.assertEqual(req[sigla], {}, sigla)
        for sigla in ("CISM", "CISA", "ISO 27001 LA", "PDPF/PDPP"):
            self.assertEqual(req[sigla], {"conferir": True}, sigla)
            self.assertTrue(self._cert(d, sigla)["experiencia"].strip(), sigla)
        for c in d["certificacoes"]:
            if c["requisitos"]:
                self.assertTrue(c["sem_experiencia"].strip(), c["sigla"])

    def test_regra_de_elegibilidade(self):
        d = self._dados()
        iniciante = {"anos_ti": 0, "anos_si": 0, "anos_gestao_si": 0, "anos_nuvem": 0}
        self.assertEqual(elegibilidade(self._cert(d, "Security+"), iniciante), "sem-exigencia")
        self.assertEqual(elegibilidade(self._cert(d, "CISSP"), iniciante), "pendente")
        self.assertEqual(elegibilidade(self._cert(d, "CEH"), dict(iniciante, treinamento_oficial=True)), "elegivel")
        graduado = {"anos_ti": 6, "anos_si": 4, "anos_gestao_si": 0, "anos_nuvem": 0, "graduacao": True}
        self.assertEqual(elegibilidade(self._cert(d, "CISSP"), graduado), "elegivel")
        self.assertEqual(elegibilidade(self._cert(d, "CISSP"), dict(graduado, graduacao=False)), "pendente")
        self.assertEqual(elegibilidade(self._cert(d, "CCSP"), graduado), "pendente")
        self.assertEqual(elegibilidade(self._cert(d, "CCSP"), dict(graduado, anos_si=3, anos_nuvem=1)), "elegivel")
        # CISM: a ISACA publica dispensas de experiência; o planejador manda conferir.
        self.assertEqual(elegibilidade(self._cert(d, "CISM"), dict(graduado, anos_si=5, anos_gestao_si=5)), "conferir")
        # Anos em segurança contam como anos em TI, e anos em gestão de segurança contam como anos em segurança.
        so_seguranca = {"anos_ti": 0, "anos_si": 5, "anos_gestao_si": 0, "anos_nuvem": 1}
        self.assertEqual(elegibilidade(self._cert(d, "CCSP"), so_seguranca), "elegivel")

    def test_status_conferir(self):
        d = self._dados()
        veterano = {"anos_ti": 20, "anos_si": 20, "anos_gestao_si": 20, "anos_nuvem": 20,
                    "graduacao": True, "treinamento_oficial": True}
        for sigla in ("CISM", "CISA", "ISO 27001 LA", "PDPF/PDPP"):
            self.assertEqual(elegibilidade(self._cert(d, sigla), veterano), "conferir", sigla)
        self.assertEqual(elegibilidade(self._cert(d, "ISFS"), veterano), "sem-exigencia")
        body = self.body_path.read_text(encoding="utf-8")
        self.assertRegex(body, r'"conferir": \["Requisito em texto: confira na certificadora", "rgba\(')
        motor = re.search(r"function elegibilidade\(c\) \{(.*?)\n    \}", body, re.S)
        self.assertIsNotNone(motor)
        corpo = motor.group(1)
        self.assertIn('if (req.conferir) return { status: "conferir", faltas: [] };', corpo)
        self.assertLess(corpo.index("req.conferir"), corpo.index('"sem-exigencia"'))

    def test_textos_listam_todas_as_certificacoes_conferir(self):
        """O parágrafo antes do planejador e o CURRICULO citam todas as certificações com status "conferir"."""
        d = self._dados()
        conferir = [c["sigla"] for c in d["certificacoes"] if c["requisitos"].get("conferir")]
        self.assertIn("CISM", conferir)
        trajetorias = self._secao(self.body_path.read_text(encoding="utf-8"), "trajetorias")
        paragrafo = re.search(r"<p>\s*O planejador do laboratório a seguir.*?</p>", trajetorias, re.S)
        self.assertIsNotNone(paragrafo)
        curriculo = (GERADORES / "CURRICULO.md").read_text(encoding="utf-8")
        lista_curriculo = re.search(r"quando o requisito é descrito só em texto \(([^)]*)\)", curriculo)
        self.assertIsNotNone(lista_curriculo)
        for sigla in conferir:
            nome_curriculo = "ISO 27001 Lead Auditor" if sigla == "ISO 27001 LA" else sigla
            self.assertIn(sigla, paragrafo.group(0), f"Parágrafo do planejador sem {sigla}")
            self.assertIn(nome_curriculo, lista_curriculo.group(1), f"CURRICULO sem {sigla}")

    # ---------------------------------------------------------------- compilado
    def test_simulador_estrutura(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        for marcador in ("cert-lab", 'id="cert-dados"', "cert-selecao", "cert-perfil", "cert-resultado",
                         "cert-plano", "alternarCertificacao", "atualizarPerfilCert", "restaurarCert"):
            self.assertIn(marcador, content, marcador)
        ini = content.index("var CERT = JSON.parse")
        motor = content[ini:content.index("</script>", ini)]
        self.assertNotIn("innerHTML", motor)

    # ------------------------------------------------------------- trajetórias
    def _secao(self, body, sid):
        m = re.search(r'<section class="study-section" id="%s".*?</section>' % sid, body, re.S)
        self.assertIsNotNone(m, f"Seção {sid} ausente")
        return m.group(0)

    def test_secao_trajetorias_antes_do_laboratorio(self):
        body = self.body_path.read_text(encoding="utf-8")
        self.assertRegex(
            body,
            r'(?s)<section class="study-section" id="trajetorias" data-tipo="teoria">.*?</section>\s*'
            r'(<!--.*?-->\s*)?<section class="study-section" id="simulador" data-tipo="laboratorio">',
        )
        self.assertIn("Seção 7 de 7", self.compiled_path.read_text(encoding="utf-8"))

    def test_trajetorias_conteudo(self):
        sec = self._secao(self.body_path.read_text(encoding="utf-8"), "trajetorias")
        for termo in ("suporte", "CISO", "MBA", "Foundation", "EXIN", "CertiProf", "CQI/IRCA", "exemplo",
                      "GRC", "Privacidade", "Auditoria", "Técnico", "por onde começar",
                      "oito perfis", "Pentest", "eJPT", "eCPPT", "OSCP", "eCTHP", "SecurityX", "CASP+", "CTF"):
            self.assertIn(termo.lower(), sec.lower(), f"Termo ausente na seção trajetorias: {termo}")

    def test_trajetorias_lideranca_executiva(self):
        sec = self._secao(self.body_path.read_text(encoding="utf-8"), "trajetorias")
        for termo in ("Liderança executiva", "auditor", "DPO", "arquiteto", "CTO", "IAM", "mesma empresa",
                      "comunidade", "CISSP", "setor financeiro", "Estudo 59", "Estudo 60", "só 1 dos 5", "ilustra"):
            self.assertIn(termo.lower(), sec.lower(), f"Termo ausente: {termo}")
        linhas = [l for l in re.findall(r"<tr>.*?</tr>", sec, re.S) if "Liderança / CISO" in l]
        self.assertEqual(len(linhas), 1, "Linha Liderança / CISO ausente na tabela")
        for termo in ("CISM", "CRISC", "CISSP", "Estudo 25", "Estudo 26", "Estudo 58", "Estudo 59", "Estudo 60"):
            self.assertIn(termo, linhas[0])

    def test_trajetorias_linha_pentest(self):
        sec = self._secao(self.body_path.read_text(encoding="utf-8"), "trajetorias")
        self.assertNotIn("dois perfis", sec.lower())
        linhas = [l for l in re.findall(r"<tr>.*?</tr>", sec, re.S)
                  if re.match(r"<tr>\s*<td>[^<]*(<strong>)?[^<]*Pentest", l)]
        self.assertEqual(len(linhas), 1, "Linha Pentest ausente na tabela")
        for termo in ("eJPT", "eCPPT", "OSCP", "14 (Pentest"):
            self.assertIn(termo, linhas[0])
        self.assertIn("dezembro de 2024", sec)

    def test_checklist_e_quiz_33(self):
        body = self.body_path.read_text(encoding="utf-8")
        self.assertEqual(body.count('class="checklist-item"'), 8)
        self.assertGreaterEqual(body.count('class="quiz-item"'), 9)
        quiz = self._secao(body, "quiz")
        self.assertIn("Questão 8", quiz)
        self.assertIn("Questão 9", quiz)
        self.assertIn("prática", quiz.lower())

    def test_fatos_cita_securityx_e_ecthp(self):
        fatos = self._secao(self.body_path.read_text(encoding="utf-8"), "fatos")
        self.assertIn("https://www.comptia.org/en-us/certifications/securityx/", fatos)
        self.assertIn("https://ine.com/security/certifications/ecthp-certification", fatos)

    def test_trajetorias_sem_dados_pessoais(self):
        body = self.body_path.read_text(encoding="utf-8")
        self.assertNotIn("linkedin.com/in/", body)
        self.assertNotIn("lattes.cnpq.br", body)
        self.assertNotIn("%", self._secao(body, "trajetorias"))
        for marca in ("F" "63", "A" "93", "primeiro " "programa"):
            self.assertNotIn(marca.lower(), body.lower())

    def test_textos_de_vitrine_citam_as_certificacoes_novas(self):
        """Subtítulo do módulo 33, README e CURRICULO não podem ficar presos às seis certificações originais."""
        subtitulo = ESTUDOS_DADOS["Certificacoes-e-Carreira"]["subtitulo"]
        readme = (GERADORES.parent / "README.md").read_text(encoding="utf-8")
        curriculo = (GERADORES / "CURRICULO.md").read_text(encoding="utf-8")
        for sigla in ("CISA", "ISFS", "OSCP"):
            self.assertIn(sigla, subtitulo, f"Subtítulo do módulo 33 sem {sigla}")
            self.assertIn(sigla, readme, f"README sem {sigla}")
            self.assertIn(sigla, curriculo, f"CURRICULO sem {sigla}")

    def test_certificacoes_praticas(self):
        d = self._dados()
        iniciante = {"anos_ti": 0, "anos_si": 0, "anos_gestao_si": 0, "graduacao": False, "certificacoes": []}
        veterano = {"anos_ti": 20, "anos_si": 15, "anos_gestao_si": 10, "graduacao": True, "certificacoes": []}
        for sigla, nivel in (("eJPT", 1), ("eCPPT", 2), ("OSCP", 2)):
            with self.subTest(cert=sigla):
                cert = self._cert(d, sigla)
                self.assertEqual(cert["nivel"], nivel)
                self.assertEqual(cert["requisitos"], {})
                self.assertEqual(elegibilidade(cert, iniciante), "sem-exigencia")
                self.assertEqual(elegibilidade(cert, veterano), "sem-exigencia")

    def test_oscp_pre_requisitos_nao_sao_dominio_da_prova(self):
        oscp = self._cert(self._dados(), "OSCP")
        nomes = [dom["nome"] for dom in oscp["dominios"]]
        self.assertIn("Pré-requisitos recomendados (não é domínio da prova)", nomes)
        self.assertNotIn("Preparação recomendada: redes, Windows, Linux e scripting", nomes)
        self.assertIn("A aprovação concede as duas", oscp["manutencao"])  # pen-200: "earn both the OSCP and OSCP+"

    def test_sem_texto_de_doze(self):
        arquivos = list(GERADORES.glob("*_body.html")) + [GERADORES.parent / "README.md", GERADORES / "CURRICULO.md", GERADORES / "index_dados.py"]
        for a in arquivos:
            self.assertNotIn("12 certificações", a.read_text(encoding="utf-8"), a.name)

    def test_sem_texto_de_quinze(self):
        arquivos = list(GERADORES.glob("*_body.html")) + [GERADORES.parent / "README.md", GERADORES / "CURRICULO.md", GERADORES / "index_dados.py"]
        for a in arquivos:
            self.assertNotIn("15 certificações", a.read_text(encoding="utf-8"), a.name)

    def test_crisc_e_cdpse(self):
        d = self._dados()
        casos = {"CRISC": ("crisc", "crisc-exam-content-outline", "Lideranca-e-Programa-de-Seguranca"),
                 "CDPSE": ("cdpse", "cdpse-exam-content-outline", "LGPD-e-Privacidade")}
        for sigla, (slug, outline, modulo) in casos.items():
            with self.subTest(cert=sigla):
                c = self._cert(d, sigla)
                self.assertEqual((c["orgao"], c["nivel"], c["requisitos"]), ("ISACA", 3, {"conferir": True}))
                urls = [f["url"] for f in c["fontes"]]
                base = f"https://www.isaca.org/credentialing/{slug}"
                self.assertIn(base, urls)
                self.assertIn(f"{base}/{outline}", urls)
                self.assertIn("120", c["manutencao"])
                self.assertIn("3 anos", c["manutencao"])
                self.assertIn("3 anos", c["experiencia"])
                self.assertIn("10 anos", c["experiencia"])
                m = next(x for x in CERTIFICACOES if x["sigla"] == sigla)
                self.assertEqual(m["site_oficial"], base)
                self.assertGreaterEqual(len(m["modulos"]), 5)
                self.assertIn(modulo, m["modulos"])

    def test_tabela_certificacoes_da_secao(self):
        sec = self._secao(self.body_path.read_text(encoding="utf-8"), "certificacoes")
        tabela = re.search(r"<table.*?</table>", sec, re.S).group(0)
        for c in CERTIFICACOES:
            self.assertIn(f"<strong>{c['sigla']}</strong>", tabela, f"Sigla ausente na tabela: {c['sigla']}")
        self.assertEqual(len(CERTIFICACOES), 17)

    def test_componentes_pedagogicos(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        self.assertIn('class="callout', content)
        self.assertIn('class="diagram-svg-wrap', content)
        self.assertNotIn('<pre class="mermaid"', content)
        self.assertEqual(content.count('class="checklist-item"'), 8)
        self.assertGreaterEqual(content.count('class="quiz-item"'), 7)
        self.assertIn('class="facts-grid', content)
        self.assertIn('initChecklist("certificacoes-carreira")', content)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn("Certificacoes-e-Carreira/treinamento-certificacoes-e-carreira.html", content)
        self.assertIn('data-slug="Certificacoes-e-Carreira"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)


if __name__ == "__main__":
    unittest.main()
