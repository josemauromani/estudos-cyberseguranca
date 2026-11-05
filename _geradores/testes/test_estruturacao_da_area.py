#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_estruturacao_da_area.py
Testes automatizados para o Estudo 60: Estruturacao-da-Area-de-Seguranca

O simulador Alocador de Programa guarda num bloco JSON as seis funções do NIST
CSF 2.0, as seis frentes de investimento (cada uma com os pontos necessários
para subir um nível em cada função que ela afeta), os quatro modelos de SOC
(interno, MSSP, MDR e híbrido, com custo, efeito em níveis e riscos) e três
cenários fictícios (varejo, fintech regulada e indústria com OT), cada um com
orçamento, perfil atual, perfil alvo, exigências, um plano de exemplo e uma
armadilha comum. Este teste espelha em Python o cálculo do motor JavaScript:
o perfil alcançado por função, as exigências não atendidas, os riscos
residuais e a recusa da alocação inválida (acima do orçamento, negativa ou não
inteira), sem calcular perfil.
"""

import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402
from navegador import CHROME, executar  # noqa: E402

SLUG = "Estruturacao-da-Area-de-Seguranca"
SECOES = ["introducao", "maturidade", "time-e-sourcing", "conscientizacao", "fusoes-e-aquisicoes", "simulador",
          "checklist", "quiz", "fatos"]
FUNCOES = ["GV", "ID", "PR", "DE", "RS", "RC"]
FRENTES = ["identidade", "vulnerabilidades", "deteccao", "resiliencia", "conscientizacao", "grc"]
SOURCING = ["interno", "mssp", "mdr", "hibrido"]
CENARIOS = ["varejo", "fintech", "industria"]
AVISO_ORCAMENTO = "A alocação passa do orçamento"
NORMA_FINTECH = "Res. CMN 4.893/2021"
CITA_NORMA = re.compile(r"\bRes\.|Resolução|Circular|\bLei\b|\bnorma\b", re.I)


# ============================================================ regras
def aplicar_plano(dados, cenario_id, sourcing, alocacao):
    """Espelho de aplicarPlano.

    nivel(f) = min(4, atual[f] + efeito do sourcing em f + soma(alocacao[frente] // pontos_por_nivel[f]))
    para cada frente que afeta f. O orçamento das frentes é o do cenário menos o custo do sourcing.
    Alocação acima do disponível, negativa, não inteira ou com frente desconhecida: ValueError (o motor
    mostra a mensagem e não calcula o perfil)."""
    cenario = next((c for c in dados["cenarios"] if c["id"] == cenario_id), None)
    if cenario is None:
        raise ValueError(f"cenário desconhecido: {cenario_id}")
    if sourcing not in dados["sourcing"]:
        raise ValueError(f"modelo de SOC desconhecido: {sourcing}")
    frentes = {f["id"]: f for f in dados["frentes"]}
    for frente, pontos in alocacao.items():
        if frente not in frentes:
            raise ValueError(f"frente desconhecida: {frente}")
        if isinstance(pontos, bool) or not isinstance(pontos, int) or pontos < 0:
            raise ValueError(f"pontos inválidos em {frente}: {pontos!r}")
    disponivel = cenario["orcamento"] - dados["sourcing"][sourcing]["custo"]
    if sum(alocacao.values()) > disponivel:
        raise ValueError("a alocação passa do orçamento")
    efeitos_soc = dados["sourcing"][sourcing]["efeitos"]
    alcancado = {}
    for f in dados["funcoes"]:
        ganho = efeitos_soc.get(f, 0)
        for frente in dados["frentes"]:
            if f in frente["efeitos"]:
                ganho += alocacao.get(frente["id"], 0) // frente["efeitos"][f]
        alcancado[f] = min(4, cenario["perfil_atual"][f] + ganho)
    return {
        "perfil_alcancado": alcancado,
        "exigencias_nao_atendidas": [e["motivo"] for e in cenario["exigencias"]
                                     if alcancado[e["funcao"]] < e["nivel_minimo"]],
        "riscos_residuais": [f for f in dados["funcoes"] if alcancado[f] < cenario["perfil_alvo"][f]]
                            + list(dados["sourcing"][sourcing]["riscos"]),
    }


class TestEstruturacaoDaArea(unittest.TestCase):
    """Estrutura, conteúdo, simulador e compilação do estudo 60."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "estruturacao_da_area_de_seguranca_body.html"
        self.compiled_path = self.root / SLUG / "treinamento-estruturacao-da-area-de-seguranca.html"
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
        m = re.search(r'<script type="application/json" id="est-dados">(.*?)</script>', self._body(), re.S)
        self.assertIsNotNone(m, "Bloco JSON #est-dados ausente no body")
        return json.loads(m.group(1))

    def _cenario(self, d, cid):
        return next(c for c in d["cenarios"] if c["id"] == cid)

    def _motor(self):
        content = self._compilado()
        ini = content.index('JSON.parse(document.getElementById("est-dados")')
        return content[ini:content.index("</script>", ini)]

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
        self.assertIn('data-slug="estruturacao-da-area-de-seguranca"', body)

    def test_coerencia_com_o_catalogo(self):
        content = self._compilado()
        info = ESTUDOS_DADOS[SLUG]
        self.assertIn(info["simulador_nome"], content)
        self.assertIn(info["pergunta_chave"], content)
        self.assertIn(info["subtitulo"], self.portal_path.read_text(encoding="utf-8"))
        self.assertEqual(len(info["fatos"]), 4)
        for fato in info["fatos"]:
            self.assertIn(fato, content, fato)

    def test_metadados(self):
        info = ESTUDOS_DADOS[SLUG]
        self.assertEqual(info["titulo"], "Estruturação da Área de Segurança: Maturidade, Time e Sourcing")
        self.assertEqual(info["subtitulo"], "Plano de 90 dias, perfis do NIST CSF 2.0, desenho do time, SOC interno, "
                                            "MSSP e MDR, conscientização e aquisições")
        self.assertEqual(info["trilha"], 14)
        self.assertEqual(info["nist"], "Govern")
        self.assertEqual(info["mitre"], "N/A (estruturação e sourcing)")
        self.assertEqual(info["carreiras"], ["GRC & Auditoria"])
        self.assertEqual(info["tempo_minutos"], 50)
        self.assertEqual(info["nivel"], "avancado")
        self.assertEqual(info["simulador_nome"], "Alocador de Programa")
        self.assertEqual(info["pergunta_chave"],
                         "Você chegou como primeiro CISO da empresa. O que acontece nos primeiros 90 dias?")
        self.assertEqual(info["fatos"], ["Perfil atual e perfil alvo (NIST CSF 2.0)", "Níveis (tiers) 1 a 4",
                                         "SOC interno, MSSP, MDR e híbrido", "Plano de 90 dias"])

    # ------------------------------------------------------------ conteúdo
    def test_termos_chave(self):
        body = self._body()
        for termo in ("90 dias", "perfil atual", "perfil alvo", "Tier 1", "Tier 4", "CMMI", "C2M2", "SOC interno",
                      "MSSP", "MDR", "híbrido", "SLA", "plano de saída", "taxa de reporte", "due diligence",
                      "federação", "risco herdado"):
            self.assertIn(termo, body, termo)

    def test_pontes(self):
        body = self._body()
        antes = body[:body.index('id="simulador"')]
        for ref in ("Estudo 15", "Estudo 16", "Estudo 41", "Estudo 57", "Estudo 59"):
            self.assertIn(ref, antes, ref)
        fim = self._secao("fatos")
        for ref in ("Trilha 14", "61 módulos"):
            self.assertIn(ref, fim, ref)

    def test_referencias(self):
        fim = self._secao("fatos")
        for ref in ("NIST CSF 2.0", "CSWP 29", "Quick-Start Guide"):
            self.assertIn(ref, fim, ref)

    def test_sem_marcas_de_fornecedor_e_de_perfis(self):
        secao = self._secao("time-e-sourcing")
        for marca in ("CrowdStrike", "SentinelOne", "Splunk", "QRadar", "Microsoft Sentinel", "Arctic Wolf"):
            self.assertNotIn(marca.lower(), secao.lower(), f"sourcing é ensinado por modelo, não por marca: {marca}")
        body = self._body()
        # marcas escritas em partes para que a varredura de termos proibidos no repositório não as encontre
        for proibido in ("F" "63", "A" "93"):
            self.assertNotIn(proibido, body, proibido)
        self.assertNotIn("primeiro programa", body.lower())

    # ---------------------------------------------------------------- dados
    def test_dados_do_simulador(self):
        d = self._dados()
        self.assertIn("fictíci", d["contexto"])
        texto = json.dumps(d, ensure_ascii=False)
        for host in re.findall(r"\b[\w-]+(?:\.[\w-]+)*\.(?:com|net|org|io|br)\b", texto):
            self.fail(f"domínio real nos dados: {host}")
        self.assertEqual(d["funcoes"], FUNCOES)
        self.assertEqual(set(d["nomes_funcoes"]), set(FUNCOES))

        self.assertEqual([f["id"] for f in d["frentes"]], FRENTES)
        for f in d["frentes"]:
            with self.subTest(frente=f["id"]):
                self.assertTrue(f["nome"].strip())
                self.assertTrue(f["efeitos"])
                for funcao, ppn in f["efeitos"].items():
                    self.assertIn(funcao, FUNCOES)
                    self.assertIsInstance(ppn, int)
                    self.assertNotIsInstance(ppn, bool)
                    self.assertGreater(ppn, 0)

        self.assertEqual(sorted(d["sourcing"]), sorted(SOURCING))
        for sid, s in d["sourcing"].items():
            with self.subTest(sourcing=sid):
                self.assertTrue(s["nome"].strip())
                self.assertIsInstance(s["custo"], int)
                self.assertGreater(s["custo"], 0)
                for funcao, niveis in s["efeitos"].items():
                    self.assertIn(funcao, FUNCOES)
                    self.assertIsInstance(niveis, int)
                    self.assertGreaterEqual(niveis, 0)
                self.assertIsInstance(s["riscos"], list)
                self.assertTrue(s["riscos"])
                for r in s["riscos"]:
                    self.assertIsInstance(r, str)
                    self.assertTrue(r.strip())
        custos = {k: v["custo"] for k, v in d["sourcing"].items()}
        self.assertLess(custos["mssp"], custos["mdr"], "custo relativo: MSSP < MDR")
        self.assertLess(custos["mdr"], custos["hibrido"], "custo relativo: MDR < híbrido")
        self.assertLess(custos["hibrido"], custos["interno"], "custo relativo: híbrido < interno")

        self.assertEqual([c["id"] for c in d["cenarios"]], CENARIOS)
        for c in d["cenarios"]:
            with self.subTest(cenario=c["id"]):
                self.assertTrue(c["nome"].strip())
                self.assertTrue(c["descricao"].strip())
                self.assertIsInstance(c["orcamento"], int)
                for chave in ("perfil_atual", "perfil_alvo"):
                    self.assertEqual(set(c[chave]), set(FUNCOES), chave)
                    for nivel in c[chave].values():
                        self.assertIn(nivel, range(1, 5))
                for f in FUNCOES:
                    self.assertGreaterEqual(c["perfil_alvo"][f], c["perfil_atual"][f])
                self.assertTrue(c["exigencias"])
                for e in c["exigencias"]:
                    self.assertIn(e["funcao"], FUNCOES)
                    self.assertIn(e["nivel_minimo"], range(1, 5))
                    self.assertLessEqual(e["nivel_minimo"], c["perfil_alvo"][e["funcao"]])
                    self.assertGreater(e["nivel_minimo"], c["perfil_atual"][e["funcao"]], "exigência já atendida")
                    self.assertTrue(e["motivo"].strip())
                for chave in ("solucao_exemplo", "armadilha"):
                    plano = c[chave]
                    self.assertIn(plano["sourcing"], SOURCING)
                    self.assertTrue(set(plano["alocacao"]) <= set(FRENTES))
                    self.assertLess(d["sourcing"][plano["sourcing"]]["custo"], c["orcamento"])
                self.assertIn(c["armadilha"]["falha_esperada"], [e["motivo"] for e in c["exigencias"]])
                self.assertTrue(c["armadilha"]["licao"].strip())

    # ------------------------------------------------------------ motor
    def test_regras_espelhadas(self):
        d = self._dados()
        for c in d["cenarios"]:
            with self.subTest(cenario=c["id"]):
                ex = c["solucao_exemplo"]
                res = aplicar_plano(d, c["id"], ex["sourcing"], ex["alocacao"])
                self.assertEqual(set(res), {"perfil_alcancado", "exigencias_nao_atendidas", "riscos_residuais"})
                self.assertEqual(set(res["perfil_alcancado"]), set(FUNCOES))
                self.assertEqual(res["exigencias_nao_atendidas"], [])
                riscos_soc = d["sourcing"][ex["sourcing"]]["riscos"]
                self.assertEqual(res["riscos_residuais"][-len(riscos_soc):], riscos_soc,
                                 "o risco do modelo de SOC fica, mesmo no plano que atende tudo")
                arm = c["armadilha"]
                res = aplicar_plano(d, c["id"], arm["sourcing"], arm["alocacao"])
                self.assertIn(arm["falha_esperada"], res["exigencias_nao_atendidas"])

    def test_calculo_por_funcao(self):
        d = self._dados()
        c = d["cenarios"][0]
        vazio = aplicar_plano(d, c["id"], "mssp", {})
        efeitos = d["sourcing"]["mssp"]["efeitos"]
        for f in FUNCOES:
            self.assertEqual(vazio["perfil_alcancado"][f], min(4, c["perfil_atual"][f] + efeitos.get(f, 0)), f)
        frente = d["frentes"][0]
        funcao, ppn = next(iter(frente["efeitos"].items()))
        disponivel = c["orcamento"] - d["sourcing"]["mssp"]["custo"]
        self.assertGreaterEqual(disponivel, ppn * 2)
        um = aplicar_plano(d, c["id"], "mssp", {frente["id"]: ppn * 2 - 1})["perfil_alcancado"][funcao]
        self.assertEqual(um, min(4, vazio["perfil_alcancado"][funcao] + 1), "pontos abaixo do degrau não sobem nível")
        cheio = aplicar_plano(d, c["id"], "mssp", {frente["id"]: disponivel})
        self.assertEqual(cheio["perfil_alcancado"][funcao], 4, "o nível para no 4")
        lacunas = [x for x in cheio["riscos_residuais"] if x in FUNCOES]
        self.assertEqual(lacunas, [f for f in FUNCOES if cheio["perfil_alcancado"][f] < c["perfil_alvo"][f]])
        self.assertNotIn(funcao, lacunas)

    def test_alocacao_invalida(self):
        d = self._dados()
        c = d["cenarios"][0]
        disponivel = c["orcamento"] - d["sourcing"]["mdr"]["custo"]
        aplicar_plano(d, c["id"], "mdr", {"identidade": disponivel})  # no limite, aceita
        for ruim in ({"identidade": disponivel + 1}, {"identidade": disponivel, "grc": 1}, {"grc": -5},
                     {"grc": 2.5}, {"grc": "10"}, {"grc": True}, {"marketing": 5}):
            with self.subTest(alocacao=ruim), self.assertRaises(ValueError):
                aplicar_plano(d, c["id"], "mdr", ruim)
        with self.assertRaises(ValueError):
            aplicar_plano(d, c["id"], "terceirizado", {})
        with self.assertRaises(ValueError):
            aplicar_plano(d, "banco", "mdr", {})

        motor = self._motor()
        self.assertIn(AVISO_ORCAMENTO, motor)
        ini = motor.index("window.aplicarPlano = function(cenarioId, sourcing, alocacao)")
        corpo = motor[ini:motor.index("\n    };", ini)]
        recusa = corpo.index(AVISO_ORCAMENTO)
        calculo = corpo.index("perfil_alcancado")
        self.assertLess(recusa, calculo, "a recusa vem antes do cálculo do perfil")
        self.assertIn("Number.isInteger", corpo[:calculo])
        self.assertIn("return null", corpo[recusa:calculo], "alocação inválida não calcula perfil")

    def test_exigencia_regulatoria_fundamentada(self):
        d = self._dados()
        fintech = self._cenario(d, "fintech")
        citam = [e for e in fintech["exigencias"] if CITA_NORMA.search(e["motivo"])]
        self.assertTrue(citam, "a fintech regulada tem exigência da norma vigente")
        for e in citam:
            self.assertIn(NORMA_FINTECH, e["motivo"], e["motivo"][:60])
        texto = json.dumps(d, ensure_ascii=False)
        self.assertNotIn("4.658", texto, "a Res. CMN 4.658/2018 foi revogada pela 4.893/2021")
        for outro in ("varejo", "industria"):
            for e in self._cenario(d, outro)["exigencias"]:
                self.assertNotIn("4.893", e["motivo"], "a norma do BCB não se aplica a quem não é regulado por ele")
        lab = self._secao("simulador")
        self.assertIn(NORMA_FINTECH, lab, "o corpo explica a exigência no texto do cenário")
        self.assertIn("plano de ação e de resposta", lab)
        self.assertIn("Estudo 54", lab)

    # ------------------------------------------------------------ simulador
    def test_simulador_sem_apis_inseguras(self):
        content = self._compilado()
        self.assertIn('id="est-dados"', content)
        motor = self._motor()
        for proibido in ("innerHTML", "outerHTML", "eval(", "new Function", "fetch(", "XMLHttpRequest", "WebSocket",
                         "document.write", "localStorage"):
            self.assertNotIn(proibido, motor, proibido)
        for marcador in ("est-lab", "est-cenario", "est-sourcing", "est-alocacao", "est-disponivel", "est-aviso",
                         "est-resultado", "est-aplicar"):
            self.assertIn(marcador, content, marcador)
        self.assertIn("textContent", motor)
        self.assertIn("createElement", motor)
        self.assertIn("não é receita única", motor, "o feedback diz que o exemplo é didático")

    def test_campos_nao_sao_recriados(self):
        """Os campos de alocação existem uma vez; digitar só atualiza o 'disponível', sem recriar controles."""
        motor = self._motor()
        ini = motor.index("function atualizarDisponivel()")
        corpo = motor[ini:motor.index("\n    }", ini)]
        for proibido in ("replaceChildren", "removeChild", "appendChild"):
            self.assertNotIn(proibido, corpo, proibido)

    @unittest.skipUnless(CHROME, "Chrome ausente")
    def test_motor_no_navegador_igual_ao_espelho(self):
        """No navegador: o motor JS dá o mesmo resultado que o espelho Python e recusa a alocação inválida."""
        d = self._dados()
        r = executar(self._compilado(), r"""
          const D = JSON.parse(document.getElementById('est-dados').textContent);
          const out = {planos: {}};
          D.cenarios.forEach(function(c) {
            out.planos[c.id] = {
              exemplo: aplicarPlano(c.id, c.solucao_exemplo.sourcing, c.solucao_exemplo.alocacao),
              armadilha: aplicarPlano(c.id, c.armadilha.sourcing, c.armadilha.alocacao)
            };
          });
          out.acima = aplicarPlano('varejo', 'mdr', {identidade: 1000});
          out.avisoAcima = document.getElementById('est-aviso').textContent;
          out.negativo = aplicarPlano('varejo', 'mdr', {grc: -5});
          out.fracao = aplicarPlano('varejo', 'mdr', {grc: 2.5});
          out.semTabela = document.querySelectorAll('#est-resultado table').length;
          // interface: digitar atualiza o disponível sem recriar o campo nem tirar o foco dele
          document.getElementById('est-soc-mdr').click();
          const campo = document.querySelector('#est-alocacao input');
          campo.focus();
          campo.value = '999';
          campo.dispatchEvent(new Event('input', {bubbles: true}));
          out.focoMantido = document.activeElement === campo;
          out.disponivel = document.getElementById('est-disponivel').textContent;
          document.getElementById('est-aplicar').click();
          out.avisoUi = document.getElementById('est-aviso').textContent;
          out.tabelaUi = document.querySelectorAll('#est-resultado table').length;
          campo.value = '0';
          campo.dispatchEvent(new Event('input', {bubbles: true}));
          document.getElementById('est-aplicar').click();
          out.tabelaOk = document.querySelectorAll('#est-resultado table').length;
          __fim(out);
        """)
        self.assertEqual(r["erros"], [])
        s = r["saida"]
        for c in d["cenarios"]:
            with self.subTest(cenario=c["id"]):
                for chave, plano in (("exemplo", c["solucao_exemplo"]), ("armadilha", c["armadilha"])):
                    self.assertEqual(s["planos"][c["id"]][chave],
                                     aplicar_plano(d, c["id"], plano["sourcing"], plano["alocacao"]), chave)
        self.assertIsNone(s["acima"])
        self.assertIn(AVISO_ORCAMENTO, s["avisoAcima"])
        self.assertIsNone(s["negativo"])
        self.assertIsNone(s["fracao"])
        self.assertEqual(s["semTabela"], 0)
        self.assertTrue(s["focoMantido"])
        self.assertIn("-", s["disponivel"], "disponível ao vivo fica negativo acima do orçamento")
        self.assertIn(AVISO_ORCAMENTO, s["avisoUi"])
        self.assertEqual(s["tabelaUi"], 0, "alocação inválida não mostra perfil")
        self.assertEqual(s["tabelaOk"], 1)

    def test_componentes_pedagogicos(self):
        body = self._body()
        content = self._compilado()
        self.assertIn('<pre class="mermaid"', body)
        self.assertIn('class="diagram-svg-wrap', content)
        self.assertNotIn('<pre class="mermaid"', content)
        self.assertIn('class="callout', content)
        self.assertIn('class="facts-grid', content)
        self.assertIn(content.count('class="checklist-item"'), range(4, 9))
        checklist = self._secao("checklist")
        self.assertIn("Plano de 90 dias", checklist)
        for item in ("stakeholders", "perfil atual", "top 5 riscos", "quick wins", "roadmap", "reporte"):
            self.assertIn(item, checklist.lower(), item)
        self.assertGreaterEqual(content.count('class="quiz-item"'), 6)
        self.assertIn('initChecklist("estruturacao-da-area-de-seguranca")', content)

    def test_portal_mostra_o_60(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn(f"{SLUG}/treinamento-estruturacao-da-area-de-seguranca.html", content)
        self.assertIn(f'data-slug="{SLUG}"', content)


if __name__ == "__main__":
    unittest.main()
