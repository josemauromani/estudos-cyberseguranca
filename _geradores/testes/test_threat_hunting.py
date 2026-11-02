#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_threat_hunting.py
Testes automatizados para o Estudo 47: Threat-Hunting

A Caçada Guiada guarda a frota fictícia, as hipóteses, as fontes de dados e a
detecção sugerida num bloco JSON. Este teste espelha em Python a expansão dos
grupos em eventos, a contagem por frequência (stack counting) e a pontuação do
JavaScript para validar que o implante aparece na cauda longa quando o
agrupamento é feito pelo campo certo e some no ruído quando não é.
"""

import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402

LIMIAR = 3  # limiar padrão da cauda longa, em estações


# ----------------------------------------------------- espelho do motor JS
def substituir(texto, estacao):
    return (str(texto).replace("{host}", estacao["nome"])
            .replace("{usuario}", estacao["usuario"])
            .replace("{rid}", str(estacao["rid"])))


def hosts_do_grupo(d, g):
    """Espelho de hostsDoGrupo: '*' é a frota toda, menos as estações em 'exceto'."""
    nomes = [e["nome"] for e in d["estacoes"]] if g["hosts"] == "*" else list(g["hosts"])
    exceto = set(g.get("exceto", []))
    return [n for n in nomes if n not in exceto]


def expandir(d, fonte_id):
    """Espelho de expandirEventos: cada grupo vira um evento por estação."""
    fonte = fonte_por_id(d, fonte_id)
    por_nome = {e["nome"]: e for e in d["estacoes"]}
    eventos = []
    for gi, g in enumerate(fonte.get("grupos", [])):
        for h in hosts_do_grupo(d, g):
            est = por_nome[h]
            eventos.append({
                "host": h,
                "grupo": gi,
                "malicioso": g["malicioso"],
                "valores": {k: substituir(v, est) for k, v in g["valores"].items()},
            })
    return eventos


def empilhar(d, fonte_id, campo, limiar=LIMIAR):
    """Espelho de empilharCaca: agrupa por valor, conta estações distintas e ocorrências."""
    linhas = {}
    for e in expandir(d, fonte_id):
        v = e["valores"][campo]
        ln = linhas.setdefault(v, {"valor": v, "hosts": set(), "ocorrencias": 0, "maliciosos": 0, "grupos": set()})
        ln["hosts"].add(e["host"])
        ln["ocorrencias"] += 1
        ln["maliciosos"] += 1 if e["malicioso"] else 0
        ln["grupos"].add(e["grupo"])
    res = sorted(linhas.values(), key=lambda ln: (len(ln["hosts"]), ln["ocorrencias"], ln["valor"]))
    for ln in res:
        ln["estacoes"] = len(ln["hosts"])
        ln["cauda"] = ln["estacoes"] <= limiar
    return res


def avaliar_achado(linha):
    """Espelho de avaliarAchado: 2 se a linha é só implante, 1 se mistura, 0 se é legítima."""
    if linha["maliciosos"] == 0:
        return 0
    return 2 if linha["maliciosos"] == linha["ocorrencias"] else 1


def fonte_por_id(d, fid):
    return next(f for f in d["fontes"] if f["id"] == fid)


def hipotese_por_id(d, hid):
    return next(h for h in d["hipoteses"] if h["id"] == hid)


def campo_por_id(fonte, cid):
    return next(c for c in fonte["campos"] if c["id"] == cid)


def tem_implante(d, fonte_id):
    return any(g["malicioso"] for g in fonte_por_id(d, fonte_id).get("grupos", []))


def pontuar(d, primeira_hipotese, hipotese, primeira_fonte, fonte, campo, achado):
    """Espelho de pontuarCaca. achado é o valor da linha marcada ou None (hipótese refutada)."""
    p_hip = hipotese_por_id(d, primeira_hipotese)["pontos"]
    p_fonte = fonte_por_id(d, primeira_fonte)["pontos"].get(hipotese, 0)
    p_campo = campo_por_id(fonte_por_id(d, fonte), campo)["pontos"]
    if achado is None:
        p_achado = 0 if tem_implante(d, fonte) else 2
    else:
        linha = next(ln for ln in empilhar(d, fonte, campo) if ln["valor"] == achado)
        p_achado = avaliar_achado(linha)
    return {"hipotese": p_hip, "fonte": p_fonte, "campo": p_campo, "achado": p_achado,
            "total": p_hip + p_fonte + p_campo + p_achado}


def valor_do_implante(d, fonte_id, campo):
    linhas = [ln for ln in empilhar(d, fonte_id, campo) if ln["maliciosos"]]
    return linhas


class TestThreatHunting(unittest.TestCase):
    """Valida a estrutura, o conteúdo, a Caçada Guiada e a compilação do estudo 47."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "threat_hunting_body.html"
        self.compiled_path = self.root / "Threat-Hunting" / "treinamento-threat-hunting.html"
        self.portal_path = self.root / "index.html"

    def _dados(self):
        body = self.body_path.read_text(encoding="utf-8")
        m = re.search(r'<script type="application/json" id="th-dados">(.*?)</script>', body, re.S)
        self.assertIsNotNone(m, "Bloco JSON #th-dados ausente no body")
        return json.loads(m.group(1))

    # ------------------------------------------------------------ estrutura
    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_seis_secoes_obrigatorias(self):
        body = self.body_path.read_text(encoding="utf-8")
        ids = re.findall(r'<section class="study-section" id="([\w-]+)"', body)
        self.assertEqual(len(ids), 6, ids)
        self.assertEqual(ids[2:], ["simulador", "checklist", "quiz", "fatos"])
        compilado = self.compiled_path.read_text(encoding="utf-8")
        for n in range(1, 7):
            self.assertIn(f"Seção {n} de {len(ids)}", compilado)
        self.assertIn('data-slug="threat-hunting"', body)

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        termos = ["threat hunting", "caça por hipótese", "caça por indicador", "hipótese testável", "PEAK",
                  "Prepare", "Execute", "Act with Knowledge", "linha de base", "stack counting", "cauda longa",
                  "Pirâmide da Dor", "Hunting Maturity Model", "comprometimento presumido", "normalizar",
                  "EDR", "Sysmon", "Velociraptor", "4698", "4697", "7045", "4624", "Get-ScheduledTask",
                  "Group-Object", "dcount", "T1053.005", "T1543.003", "TA0003", "documentação da caça",
                  "inconclusiva", "confirmada", "refutada", "lacuna de visibilidade", "Sigma",
                  "Estudo 16", "Estudo 17", "Estudo 18", "Estudo 36", "Estudo 46", "Estudo 48"]
        for termo in termos:
            self.assertIn(termo, content, f"Termo obrigatório ausente: {termo}")

    def test_coerencia_com_o_catalogo(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        info = ESTUDOS_DADOS["Threat-Hunting"]
        self.assertIn(info["simulador_nome"], content)
        self.assertIn(info["pergunta_chave"], content)
        for fato in info["fatos"]:
            self.assertIn(fato, content, fato)

    def test_ponte_com_engenharia_de_deteccao(self):
        body = self.body_path.read_text(encoding="utf-8")
        fim = body[body.index('id="fatos"'):body.index("</article>")]
        self.assertIn("Estudo 46", fim)
        self.assertIn("vira detecção", fim)

    # ---------------------------------------------------------------- dados
    def test_dados_ficticios_e_bem_formados(self):
        d = self._dados()
        nomes = [e["nome"] for e in d["estacoes"]]
        self.assertEqual(len(nomes), 30)
        self.assertEqual(len(nomes), len(set(nomes)))
        self.assertEqual(len({e["rid"] for e in d["estacoes"]}), 30)
        for f in d["fontes"]:
            self.assertIn("h_tarefa", f["pontos"])
            self.assertIn("h_servico", f["pontos"])
            for g in f.get("grupos", []):
                self.assertEqual(set(g["valores"]), {c["id"] for c in f["campos"]}, f["id"])
                for h in hosts_do_grupo(d, g):
                    self.assertIn(h, nomes)
                self.assertTrue(g["nota"])
            texto = json.dumps(f, ensure_ascii=False)
            for dom in re.findall(r"https?://([A-Za-z][\w.-]*)", texto):
                self.assertTrue(dom.endswith(".example"), dom)
        self.assertIn(".example", d["contexto"])
        tipos = {h["tipo"] for h in d["hipoteses"]}
        self.assertEqual(tipos, {"hipotese", "indicador", "vaga"})
        for h in d["hipoteses"]:
            self.assertEqual(h["testavel"], h["tipo"] == "hipotese")
            self.assertTrue(h["feedback"])

    def test_pontuacao_das_hipoteses_e_fontes(self):
        d = self._dados()
        self.assertEqual({h["id"]: h["pontos"] for h in d["hipoteses"]},
                         {"h_tarefa": 3, "h_servico": 2, "h_hash": 1, "h_vaga": 0})
        adequadas = {hid: [f["id"] for f in d["fontes"] if f["pontos"][hid] > 0] for hid in ("h_tarefa", "h_servico")}
        self.assertEqual(adequadas, {"h_tarefa": ["edr_tarefas", "evt_4698"], "h_servico": ["evt_7045"]})
        self.assertEqual(fonte_por_id(d, "edr_tarefas")["pontos"]["h_tarefa"], 3)
        self.assertEqual(fonte_por_id(d, "evt_4698")["pontos"]["h_tarefa"], 2, "4698 só enxerga a janela de retenção")
        for fid in ("evt_4624", "sysmon3"):
            f = fonte_por_id(d, fid)
            self.assertEqual(f.get("grupos", []), [], "fontes inadequadas não são consultáveis")
            self.assertTrue(f["feedback"]["h_tarefa"] and f["feedback"]["h_servico"])
        # toda fonte adequada tem dados e um campo que vale os 2 pontos
        for fid in ("edr_tarefas", "evt_4698", "evt_7045"):
            f = fonte_por_id(d, fid)
            self.assertTrue(f["grupos"])
            self.assertEqual(max(c["pontos"] for c in f["campos"]), 2)

    def test_frota_expandida(self):
        d = self._dados()
        self.assertEqual(len(expandir(d, "edr_tarefas")), 30 * 5 + 26 + 8 + 2 + 1 + 1 + 2)
        self.assertEqual(len(expandir(d, "evt_4698")), 60 + 1 + 1 + 2)
        self.assertEqual(len(expandir(d, "evt_7045")), 30 + 26 + 30 + 1 + 2)
        implantadas = sorted({e["host"] for e in expandir(d, "edr_tarefas") if e["malicioso"]})
        self.assertEqual(implantadas, d["estacoes_comprometidas"])
        self.assertEqual(len(implantadas), 2)
        self.assertFalse(tem_implante(d, "evt_7045"), "a hipótese de serviço deve ser refutada")

    # ------------------------------------------------------- stack counting
    def test_implante_na_cauda_longa_pelo_comando(self):
        d = self._dados()
        for fid, cauda_esperada in (("edr_tarefas", 4), ("evt_4698", 3)):
            with self.subTest(fonte=fid):
                linhas = empilhar(d, fid, "Comando")
                cauda = [ln for ln in linhas if ln["cauda"]]
                self.assertEqual(len(cauda), cauda_esperada)
                impl = [ln for ln in linhas if ln["maliciosos"]]
                self.assertEqual(len(impl), 1)
                self.assertTrue(impl[0]["cauda"])
                self.assertEqual(impl[0]["estacoes"], 2)
                self.assertEqual(avaliar_achado(impl[0]), 2)
                self.assertIn("\\Users\\Public\\", impl[0]["valor"])
                # raro não é malicioso: há legítimos na cauda junto com o implante
                self.assertGreaterEqual(sum(1 for ln in cauda if not ln["maliciosos"]), 2)
        # na linha de base, os comandos comuns estão em toda a frota
        topo = empilhar(d, "edr_tarefas", "Comando")[-1]
        self.assertEqual(topo["estacoes"], 30)

    def test_campos_de_alta_cardinalidade_afogam_o_implante(self):
        d = self._dados()
        esperado = {("edr_tarefas", "TaskName"): 35, ("edr_tarefas", "Autor"): 33, ("evt_4698", "Autor"): 33,
                    ("evt_4698", "TaskName"): 4, ("evt_7045", "ImagePath"): 2, ("evt_7045", "ServiceName"): 2,
                    ("evt_7045", "Conta"): 0}
        for (fid, campo), n in esperado.items():
            with self.subTest(fonte=fid, campo=campo):
                self.assertEqual(sum(1 for ln in empilhar(d, fid, campo) if ln["cauda"]), n)
        # o nome da tarefa leva o SID do usuário: uma linha por estação, o implante some no meio
        nomes = empilhar(d, "edr_tarefas", "TaskName")
        self.assertGreaterEqual(sum(1 for ln in nomes if ln["estacoes"] == 1), 30)
        self.assertEqual(campo_por_id(fonte_por_id(d, "edr_tarefas"), "TaskName")["pontos"], 0)
        # agrupando por autor, o implante se mistura às tarefas legítimas do mesmo usuário
        autores = [ln for ln in empilhar(d, "edr_tarefas", "Autor") if ln["maliciosos"]]
        self.assertEqual(len(autores), 2)
        self.assertTrue(all(avaliar_achado(ln) == 1 for ln in autores))

    def test_limiar_muda_a_cauda(self):
        d = self._dados()
        self.assertEqual(sum(ln["cauda"] for ln in empilhar(d, "edr_tarefas", "Comando", 1)), 2)
        self.assertEqual(sum(ln["cauda"] for ln in empilhar(d, "edr_tarefas", "Comando", 8)), 5)
        self.assertEqual(sum(ln["cauda"] for ln in empilhar(d, "edr_tarefas", "Comando", 30)), 11)

    # ------------------------------------------------------------ pontuação
    def test_pontuacao_da_cacada(self):
        d = self._dados()
        impl = valor_do_implante(d, "edr_tarefas", "Comando")[0]["valor"]
        ideal = pontuar(d, "h_tarefa", "h_tarefa", "edr_tarefas", "edr_tarefas", "Comando", impl)
        self.assertEqual(ideal["total"], 10)
        # refutar quando o implante está na fonte custa o achado
        self.assertEqual(pontuar(d, "h_tarefa", "h_tarefa", "edr_tarefas", "edr_tarefas", "Comando", None)["achado"], 0)
        # marcar um raro legítimo é falso positivo
        legit = next(ln for ln in empilhar(d, "edr_tarefas", "Comando") if ln["cauda"] and not ln["maliciosos"])
        self.assertEqual(pontuar(d, "h_tarefa", "h_tarefa", "edr_tarefas", "edr_tarefas", "Comando", legit["valor"])["achado"], 0)
        # começar por um IOC e por uma fonte errada pesa na nota, mesmo achando o implante
        r = pontuar(d, "h_hash", "h_tarefa", "evt_4624", "evt_4698", "Comando",
                    valor_do_implante(d, "evt_4698", "Comando")[0]["valor"])
        self.assertEqual((r["hipotese"], r["fonte"], r["campo"], r["achado"]), (1, 0, 2, 2))
        # hipótese de serviço: refutar com a fonte certa é o resultado correto
        r = pontuar(d, "h_servico", "h_servico", "evt_7045", "evt_7045", "ImagePath", None)
        self.assertEqual(r["total"], 9)
        rara = next(ln for ln in empilhar(d, "evt_7045", "ImagePath") if ln["cauda"])
        self.assertEqual(pontuar(d, "h_servico", "h_servico", "evt_7045", "evt_7045", "ImagePath", rara["valor"])["achado"], 0)

    def test_deteccao_sugerida_pega_so_o_implante(self):
        d = self._dados()
        for hid, det in d["deteccoes"].items():
            with self.subTest(hipotese=hid):
                self.assertIn("attack.t1053.005" if hid == "h_tarefa" else "attack.t1543.003", det["sigma"])
                self.assertIn("level: high", det["sigma"])
                for p in det["padroes"]:
                    self.assertIn(p, det["sigma"])
                for fid in det["fontes_validacao"]:
                    f = fonte_por_id(d, fid)
                    for g in f["grupos"]:
                        valor = g["valores"][det["campo"]].lower()
                        casou = any(p.lower() in valor for p in det["padroes"])
                        self.assertEqual(casou, g["malicioso"], (fid, g["valores"][det["campo"]]))
        self.assertEqual(set(d["deteccoes"]), {"h_tarefa", "h_servico"})

    # ------------------------------------------------------------ simulador
    def test_simulador_estrutura(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        for marcador in ("th-lab", 'id="th-dados"', "th-hipoteses", "th-fontes", "th-campo", "th-limiar",
                         "th-pilha", "th-placar", "th-registro", "th-deteccao", "expandirEventos", "empilharCaca",
                         "avaliarAchado", "pontuarCaca", "registrarHipoteseCaca", "escolherFonteCaca", "agruparCaca",
                         "marcarAchadoCaca", "refutarHipoteseCaca", "reiniciarCaca"):
            self.assertIn(marcador, content, marcador)
        self.assertRegex(content, r'<label[^>]*for="th-campo"')
        self.assertRegex(content, r'<label[^>]*for="th-limiar"')
        self.assertRegex(content, r'<fieldset[^>]*id="th-hipoteses"')
        self.assertRegex(content, r'<fieldset[^>]*id="th-fontes"')
        ini = content.index("var TH = JSON.parse")
        motor = content[ini:content.index("</script>", ini)]
        self.assertNotIn("innerHTML", motor)
        self.assertNotIn("eval(", motor)
        self.assertNotIn("new Function", motor)
        self.assertNotIn("fetch(", motor)
        self.assertNotIn("XMLHttpRequest", motor)

    def test_componentes_pedagogicos(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        self.assertIn('class="callout', content)
        self.assertIn('class="terminal-box', content)
        self.assertIn('class="diagram-svg-wrap', content)
        self.assertNotIn('<pre class="mermaid"', content)
        self.assertEqual(content.count('class="checklist-item"'), 7)
        self.assertGreaterEqual(content.count('class="quiz-item"'), 6)
        self.assertIn('class="facts-grid', content)
        self.assertIn('initChecklist("threat-hunting")', content)
        self.assertNotIn("cdn.", content.lower().replace("cdnjs", ""))

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn("Threat-Hunting/treinamento-threat-hunting.html", content)
        self.assertIn('data-slug="Threat-Hunting"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)


if __name__ == "__main__":
    unittest.main()
