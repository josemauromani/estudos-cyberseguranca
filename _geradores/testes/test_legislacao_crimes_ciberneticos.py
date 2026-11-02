#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_legislacao_crimes_ciberneticos.py
Testes automatizados para o Estudo 56: Legislacao-e-Crimes-Ciberneticos

O simulador Enquadramento de Casos guarda num bloco JSON os tipos penais (com
o dispositivo do Código Penal), o catálogo de registros que podem ser pedidos
(com o destinatário certo, o prazo de guarda do Marco Civil e a exigência de
ordem judicial), o catálogo de passos de preservação de provas e os casos
fictícios da Ipê Pay e da Ipê Store. Este teste espelha em Python as regras do
motor JavaScript: correção do tipo penal, classificação de cada registro
pedido (acerto, faltou, destinatário errado, desnecessário ou prazo de guarda
vencido), correção da ordem dos passos de preservação e pontuação por caso.
Também impede o módulo de afirmar números de pena não conferidos.
"""

import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402

SLUG = "Legislacao-e-Crimes-Ciberneticos"
TIPOS = ("invasao", "furto_fraude", "fraude_eletronica", "nao_crime")
DESTINOS = ("propria_empresa", "provedor_conexao", "provedor_aplicacao")
REGISTROS = {
    # id → (destino correto, prazo de guarda em dias pelo Marco Civil, exige ordem judicial)
    "logs_internos": ("propria_empresa", None, False),
    "conexao": ("provedor_conexao", 365, True),
    "aplicacao": ("provedor_aplicacao", 180, True),
    "conteudo": ("provedor_aplicacao", None, True),
}
ORDEM_CANONICA = ["isolar", "fixar", "coletar_hash", "registrar", "analisar_copia", "comunicar"]

# id → (tipo penal, registros esperados, dias desde o fato, ordem correta dos passos)
GABARITO = {
    "C1": ("invasao", {"logs_internos", "aplicacao", "conexao"}, 40,
           ["isolar", "fixar", "coletar_hash", "registrar", "analisar_copia", "comunicar"]),
    "C2": ("fraude_eletronica", {"logs_internos", "aplicacao", "conteudo", "conexao"}, 10,
           ["fixar", "coletar_hash", "registrar", "comunicar"]),
    "C3": ("furto_fraude", {"logs_internos", "aplicacao", "conexao"}, 20,
           ["fixar", "coletar_hash", "registrar", "analisar_copia", "comunicar"]),
    "C4": ("nao_crime", {"logs_internos"}, 5,
           ["isolar", "fixar", "coletar_hash", "registrar", "analisar_copia"]),
    "C5": ("invasao", {"logs_internos", "conexao"}, 240,
           ["isolar", "coletar_hash", "registrar", "analisar_copia", "comunicar"]),
}


# ============================================================ regras
def prazo_vencido(registro, dias):
    """Espelho de prazoVencido: só registros com prazo de guarda do Marco Civil vencem."""
    prazo = registro.get("prazo_dias")
    return prazo is not None and dias > prazo


def corrigir_tipo(caso, escolha):
    """Espelho de corrigirTipo."""
    return escolha == caso["tipo"]


def classificar_registros(caso, escolhas, catalogo):
    """Espelho de classificarRegistros: escolhas = {registro: destino}."""
    res = {}
    for rid in caso["registros"]:
        if rid not in escolhas:
            res[rid] = "faltou"
        elif escolhas[rid] != catalogo[rid]["destino"]:
            res[rid] = "destinatario_errado"
        else:
            res[rid] = "acerto"
    for rid in escolhas:
        if rid in caso["registros"] or rid not in catalogo:
            continue
        res[rid] = "vencido" if prazo_vencido(catalogo[rid], caso["dias_desde_fato"]) else "desnecessario"
    return res


def corrigir_ordem(caso, ordem):
    """Espelho de corrigirOrdem: posições certas e acerto total."""
    certa = caso["ordem_correta"]
    posicoes = sum(1 for a, b in zip(ordem, certa) if a == b)
    return {"posicoes": posicoes, "total": len(certa), "ok": list(ordem) == list(certa)}


def mover(ordem, i, delta):
    """Espelho de moverPasso: troca o passo i com o vizinho; fora dos limites, nada muda."""
    j = i + delta
    nova = list(ordem)
    if 0 <= i < len(nova) and 0 <= j < len(nova):
        nova[i], nova[j] = nova[j], nova[i]
    return nova


def corrigir_caso(caso, catalogo, tipo, escolhas, ordem):
    """Espelho de corrigirCaso: 1 ponto pelo tipo, 1 pelos registros sem erro, 1 pela ordem."""
    t = corrigir_tipo(caso, tipo)
    r = classificar_registros(caso, escolhas, catalogo)
    o = corrigir_ordem(caso, ordem)
    reg_ok = all(s == "acerto" for s in r.values())
    return {"tipo_ok": t, "registros": r, "registros_ok": reg_ok, "ordem": o,
            "pontos": int(t) + int(reg_ok) + int(o["ok"])}


class TestLegislacaoCrimesCiberneticos(unittest.TestCase):
    """Estrutura, conteúdo, simulador e compilação do estudo 56."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "legislacao_e_crimes_ciberneticos_body.html"
        self.compiled_path = self.root / SLUG / "treinamento-legislacao-e-crimes-ciberneticos.html"
        self.portal_path = self.root / "index.html"

    def _body(self):
        return self.body_path.read_text(encoding="utf-8")

    def _dados(self):
        m = re.search(r'<script type="application/json" id="lcc-dados">(.*?)</script>', self._body(), re.S)
        self.assertIsNotNone(m, "Bloco JSON #lcc-dados ausente no body")
        return json.loads(m.group(1))

    def _caso(self, d, cid):
        return next(c for c in d["casos"] if c["id"] == cid)

    def _gabarito_escolhas(self, d, caso):
        return {rid: d["registros"][rid]["destino"] for rid in caso["registros"]}

    # ------------------------------------------------------------ estrutura
    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_seis_secoes_obrigatorias(self):
        body = self._body()
        ids = re.findall(r'<section class="study-section" id="([\w-]+)"', body)
        self.assertEqual(len(ids), 6, ids)
        self.assertEqual(ids[2:], ["simulador", "checklist", "quiz", "fatos"])
        for n in range(1, 7):
            self.assertIn(f"Seção 0{n}", body)
        self.assertIn('data-slug="legislacao-e-crimes-ciberneticos"', body)

    def test_coerencia_com_o_catalogo(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        info = ESTUDOS_DADOS[SLUG]
        self.assertIn(info["simulador_nome"], content)
        self.assertIn(info["pergunta_chave"], content)
        for fato in info["fatos"]:
            self.assertIn(fato, content, fato)

    def test_fato_do_catalogo_atualizado(self):
        fatos = ESTUDOS_DADOS[SLUG]["fatos"]
        self.assertIn("Fraude eletrônica: art. 171 §2º-A (redação de 2026)", fatos)
        self.assertFalse(any("171" in f and "14.155" in f for f in fatos), "fato do 171 §2º-A desatualizado")

    def test_pontes_com_os_estudos_vizinhos(self):
        body = self._body()
        intro = body[:body.index('id="simulador"')]
        for ref in ("Estudo 19", "Estudo 27", "Estudo 55"):
            self.assertIn(ref, intro, ref)
        fim = body[body.index('id="fatos"'):body.index("</article>")]
        for ref in ("Trilha 13", "Estudo 54", "Estudo 57"):
            self.assertIn(ref, fim, ref)

    # ------------------------------------------------- fatos normativos
    def test_dispositivos_e_normas_conferidos(self):
        body = self._body()
        for termo in ("Lei 12.737/2012", "Lei 14.155/2021", "Lei 15.397/2026", "Lei 12.965/2014", "art. 154-A",
                      "§4º-B", "§4º-C", "§2º-A", "§2º-B", "art. 13", "art. 15", "1 ano", "6 meses",
                      "158-A a 158-F", "Decreto 11.856/2023", "Decreto 12.573/2025", "ordem judicial",
                      "reclusão de 1 a 4 anos", "cadeia de custódia", "hash"):
            self.assertIn(termo, body, termo)

    def test_pena_do_furto_mediante_fraude_atualizada(self):
        body = self._body()
        self.assertNotIn("4 a 8", body, "a pena do art. 155 §4º-B não é mais 4 a 8 anos")
        self.assertIsNotNone(re.search(r"§4º-B[^<]{0,200}4 a 10 anos", body), "§4º-B com reclusão de 4 a 10 anos")
        pena = self._dados()["tipos"]["furto_fraude"]["pena"]
        self.assertIn("4 a 10 anos", pena)
        self.assertIn("Lei 15.397/2026", pena)

    def test_sem_numero_de_pena_para_a_fraude_eletronica(self):
        body = self._body()
        self.assertIsNone(re.search(r"§2º-A[^.<]{0,160}\d+\s+a\s+\d+\s+anos", body),
                          "não citar pena do art. 171 §2º-A (não conferida por transcrição)")
        pena = self._dados()["tipos"]["fraude_eletronica"]["pena"]
        self.assertIsNone(re.search(r"\d+\s+a\s+\d+\s+anos", pena))
        self.assertIn("texto vigente", pena)
        self.assertIn("Lei 15.397/2026", pena)

    def test_aviso_de_conferencia_e_de_material_educativo(self):
        body = self._body()
        self.assertIn("planalto.gov.br", body)
        self.assertIn("02/11/2026", body)
        self.assertIn("Código Penal compilado", body)
        self.assertIn("não é orientação jurídica", body)

    # ---------------------------------------------------------------- dados
    def test_dados_ficticios_e_bem_formados(self):
        d = self._dados()
        self.assertIn("fictíci", d["contexto"])
        texto = json.dumps(d, ensure_ascii=False)
        for host in re.findall(r"\b[\w-]+(?:\.[\w-]+)*\.(?:com|net|org|io|br)\b", texto):
            self.fail(f"domínio real nos dados: {host}")
        self.assertIsNone(re.search(r"\d{3}\.\d{3}\.\d{3}-\d{2}", texto), "sem CPF nos dados")
        self.assertIsNone(re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", texto), "sem endereço IP nos dados")
        self.assertEqual(sorted(d["tipos"]), sorted(TIPOS))
        for tid, t in d["tipos"].items():
            with self.subTest(tipo=tid):
                for campo in ("nome", "dispositivo", "pena", "nucleo"):
                    self.assertTrue(t[campo].strip(), campo)
        self.assertEqual(sorted(d["destinos"]), sorted(DESTINOS))
        self.assertEqual({k: (v["destino"], v["prazo_dias"], v["ordem_judicial"]) for k, v in d["registros"].items()},
                         REGISTROS)
        for rid, r in d["registros"].items():
            with self.subTest(registro=rid):
                self.assertTrue(r["nome"].strip() and r["fundamento"].strip())
        self.assertIn("art. 13", d["registros"]["conexao"]["fundamento"])
        self.assertIn("art. 15", d["registros"]["aplicacao"]["fundamento"])
        self.assertEqual(sorted(d["passos"]), sorted(ORDEM_CANONICA))
        self.assertEqual(d["ordem_canonica"], ORDEM_CANONICA)
        for pid, p in d["passos"].items():
            with self.subTest(passo=pid):
                self.assertTrue(p["texto"].strip() and p["fundamento"].strip())
        self.assertEqual([c["id"] for c in d["casos"]], list(GABARITO))
        for c in d["casos"]:
            with self.subTest(caso=c["id"]):
                tipo, regs, dias, ordem = GABARITO[c["id"]]
                self.assertEqual(c["tipo"], tipo)
                self.assertEqual(set(c["registros"]), regs)
                self.assertEqual(c["dias_desde_fato"], dias)
                self.assertEqual(c["ordem_correta"], ordem)
                for campo in ("titulo", "empresa", "relato", "vestigio", "explicacao_tipo", "explicacao_registros"):
                    self.assertTrue(c[campo].strip(), campo)
                self.assertIn(c["empresa"], ("Ipê Pay", "Ipê Store"))
                # ordem correta respeita a ordem canônica da cadeia de custódia
                self.assertEqual(ordem, [p for p in ORDEM_CANONICA if p in ordem])
                # ordem inicial embaralhada: mesmos passos, outra sequência
                self.assertEqual(sorted(c["ordem_inicial"]), sorted(ordem))
                self.assertNotEqual(c["ordem_inicial"], ordem)
                # nenhum registro esperado com prazo de guarda vencido
                for rid in c["registros"]:
                    self.assertFalse(prazo_vencido(d["registros"][rid], dias), rid)
        self.assertEqual({c["tipo"] for c in d["casos"]}, set(TIPOS), "os casos cobrem os quatro enquadramentos")

    # ------------------------------------------------------------ motor
    def test_prazos_de_guarda(self):
        d = self._dados()
        r = d["registros"]
        self.assertFalse(prazo_vencido(r["aplicacao"], 180))
        self.assertTrue(prazo_vencido(r["aplicacao"], 181))
        self.assertFalse(prazo_vencido(r["conexao"], 365))
        self.assertTrue(prazo_vencido(r["conexao"], 366))
        self.assertFalse(prazo_vencido(r["logs_internos"], 5000))
        self.assertFalse(prazo_vencido(r["conteudo"], 5000))

    def test_gabarito_completo_vale_tres_pontos_por_caso(self):
        d = self._dados()
        total = 0
        for c in d["casos"]:
            with self.subTest(caso=c["id"]):
                res = corrigir_caso(c, d["registros"], c["tipo"], self._gabarito_escolhas(d, c), c["ordem_correta"])
                self.assertEqual(res["pontos"], 3)
                total += res["pontos"]
        self.assertEqual(total, 15)

    def test_ordem_inicial_sem_mexer(self):
        d = self._dados()
        pos = {c["id"]: corrigir_ordem(c, c["ordem_inicial"]) for c in d["casos"]}
        self.assertEqual({k: (v["posicoes"], v["total"], v["ok"]) for k, v in pos.items()},
                         {"C1": (0, 6, False), "C2": (1, 4, False), "C3": (0, 5, False), "C4": (0, 5, False),
                          "C5": (0, 5, False)})

    def test_mover_passos(self):
        o = ["a", "b", "c"]
        self.assertEqual(mover(o, 0, 1), ["b", "a", "c"])
        self.assertEqual(mover(o, 2, -1), ["a", "c", "b"])
        self.assertEqual(mover(o, 0, -1), o, "primeiro passo não sobe")
        self.assertEqual(mover(o, 2, 1), o, "último passo não desce")
        self.assertEqual(o, ["a", "b", "c"], "não altera a lista original")

    def test_golpe_da_falsa_central_e_fraude_eletronica_e_nao_furto(self):
        d = self._dados()
        c2 = self._caso(d, "C2")
        esc = {"logs_internos": "propria_empresa", "conexao": "provedor_aplicacao", "aplicacao": "provedor_aplicacao"}
        res = corrigir_caso(c2, d["registros"], "furto_fraude", esc, c2["ordem_inicial"])
        self.assertFalse(res["tipo_ok"])
        self.assertEqual(res["registros"], {"logs_internos": "acerto", "aplicacao": "acerto", "conteudo": "faltou",
                                            "conexao": "destinatario_errado"})
        self.assertEqual(res["pontos"], 0)
        self.assertIn("induzid", c2["explicacao_tipo"])

    def test_registro_de_aplicacao_vencido(self):
        d = self._dados()
        c5 = self._caso(d, "C5")
        esc = self._gabarito_escolhas(d, c5)
        esc["aplicacao"] = "provedor_aplicacao"
        res = corrigir_caso(c5, d["registros"], "invasao", esc, c5["ordem_correta"])
        self.assertEqual(res["registros"]["aplicacao"], "vencido")
        self.assertFalse(res["registros_ok"])
        self.assertEqual(res["pontos"], 2)
        self.assertIn("6 meses", c5["explicacao_registros"])

    def test_pedido_desnecessario_de_conteudo(self):
        d = self._dados()
        c4 = self._caso(d, "C4")
        esc = {"logs_internos": "propria_empresa", "conteudo": "provedor_aplicacao"}
        res = corrigir_caso(c4, d["registros"], "nao_crime", esc, c4["ordem_correta"])
        self.assertEqual(res["registros"], {"logs_internos": "acerto", "conteudo": "desnecessario"})
        self.assertEqual(res["pontos"], 2)
        # registro desconhecido é ignorado
        self.assertEqual(classificar_registros(c4, {"logs_internos": "propria_empresa", "xyz": "propria_empresa"},
                                               d["registros"]), {"logs_internos": "acerto"})

    def test_furto_por_app_e_invasao(self):
        d = self._dados()
        c3, c1 = self._caso(d, "C3"), self._caso(d, "C1")
        self.assertFalse(corrigir_tipo(c3, "fraude_eletronica"))
        self.assertTrue(corrigir_tipo(c3, "furto_fraude"))
        self.assertIn("§4º-C", c3["explicacao_tipo"], "vítima idosa: aumento do §4º-C")
        self.assertTrue(corrigir_tipo(c1, "invasao"))
        res = classificar_registros(c1, {"logs_internos": "provedor_conexao"}, d["registros"])
        self.assertEqual(res, {"logs_internos": "destinatario_errado", "aplicacao": "faltou", "conexao": "faltou"})

    # ------------------------------------------------------------ diagrama
    def test_diagrama_no_formato_do_guia(self):
        body = self._body()
        caixas = re.findall(
            r'<div class="diagram-box">\s*<div class="diagram-header">\s*'
            r'<span class="diagram-title">([^<]+)</span>.*?'
            r'<pre class="mermaid" data-title="([^"]+)">',
            body, re.S)
        self.assertGreaterEqual(len(caixas), 1, "falta um .diagram-box com cabeçalho e Mermaid")
        for titulo, data_title in caixas:
            self.assertEqual(titulo.strip(), data_title.strip())

    # ------------------------------------------------------------ simulador
    def test_simulador_sem_apis_inseguras(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        self.assertIn('id="lcc-dados"', content)
        ini = content.index("JSON.parse(document.getElementById(\"lcc-dados\")")
        motor = content[ini:content.index("</script>", ini)]
        for proibido in ("innerHTML", "outerHTML", "eval(", "new Function", "fetch(", "XMLHttpRequest", "WebSocket",
                         "document.write", "localStorage"):
            self.assertNotIn(proibido, motor, proibido)
        for marcador in ("lcc-lab", "lcc-casos", "lcc-caso", "lcc-placar", "prazoVencido", "corrigirTipo",
                         "classificarRegistros", "corrigirOrdem", "moverPasso", "corrigirCaso"):
            self.assertIn(marcador, content, marcador)
        self.assertIn("aria-label", motor)
        self.assertIn("textContent", motor)
        self.assertIn('"radio"', motor, "tipo penal escolhido por botões de opção")
        self.assertIn('"checkbox"', motor, "registros escolhidos por caixas de seleção")

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        termos = ["invasão de dispositivo informático", "fraude eletrônica", "furto mediante fraude",
                  "Marco Civil da Internet", "provedor de conexão", "provedor de aplicação", "registros de conexão",
                  "registros de acesso a aplicações", "ordem judicial", "cadeia de custódia", "hash", "SHA-256",
                  "PNCiber", "E-Ciber", "Ipê Pay", "Ipê Store", "boletim de ocorrência", "induzid", "ANPD"]
        for termo in termos:
            self.assertIn(termo, content, f"Termo obrigatório ausente: {termo}")

    def test_componentes_pedagogicos(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        self.assertIn('class="callout', content)
        self.assertIn('class="diagram-svg-wrap', content)
        self.assertNotIn('<pre class="mermaid"', content)
        self.assertEqual(content.count('class="checklist-item"'), 7)
        self.assertGreaterEqual(content.count('class="quiz-item"'), 6)
        self.assertIn('class="facts-grid', content)
        self.assertIn('initChecklist("legislacao-e-crimes-ciberneticos")', content)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn(f"{SLUG}/treinamento-legislacao-e-crimes-ciberneticos.html", content)
        self.assertIn(f'data-slug="{SLUG}"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)


if __name__ == "__main__":
    unittest.main()
