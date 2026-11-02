#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_ia_ciber.py
Testes automatizados para o Estudo 24: IA-e-Ciberseguranca
"""

import itertools
import json
import re
import sys
import unicodedata
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402

LLM_TOP10_2025 = [
    ("LLM01:2025", "Prompt Injection"), ("LLM02:2025", "Sensitive Information Disclosure"), ("LLM03:2025", "Supply Chain"),
    ("LLM04:2025", "Data and Model Poisoning"), ("LLM05:2025", "Improper Output Handling"), ("LLM06:2025", "Excessive Agency"),
    ("LLM07:2025", "System Prompt Leakage"), ("LLM08:2025", "Vector and Embedding Weaknesses"), ("LLM09:2025", "Misinformation"),
    ("LLM10:2025", "Unbounded Consumption"),
]
DEFESAS = ["entrada", "separacao", "saida", "ferramentas", "segredo", "codificacao"]


def norm(t):
    return "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn").lower()


def simular(d, msg, defs):
    """Espelho do modelo simulado em JavaScript. defs: conjunto de defesas ligadas."""
    n = norm(msg)
    r = {"entrada_bloqueada": False, "contexto": [], "chamadas": [], "saida_modelo": "", "filtros": [], "saida_final": "",
         "xss": False, "vazou": []}
    if "entrada" in defs and re.search(d["regex_entrada"], n, re.A):
        r["entrada_bloqueada"] = True
        r["saida_final"] = d["textos"]["entrada_bloqueada"]
        return r
    prompt = [l.replace("{CUPOM}", d["cupom"]) for l in d["prompt_sistema"] if not ("segredo" in defs and "{CUPOM}" in l)]
    prompt_txt = "\n".join(prompt)
    partes = []
    for doc in d["documentos"]:
        if any(g in n for g in doc["gatilhos"]):
            r["contexto"].append(doc["id"])
            partes.append(doc["visivel"])
            if "separacao" not in defs and doc.get("injecao"):
                inj = doc["injecao"]
                if "ferramentas" in defs and not inj["destino"].endswith("@" + d["dominio_interno"]):
                    res = d["textos"]["email_bloqueado"]
                else:
                    res = "enviado"
                r["chamadas"].append(["enviar_email", inj["destino"], res])
    m = re.search(r"pedido\D{0,12}(\d{4})", n)
    if m:
        pid = int(m.group(1))
        ped = next((p for p in d["pedidos"] if p["id"] == pid), None)
        if ped is None or ("ferramentas" in defs and ped["cliente_id"] != d["sessao_cliente"]):
            res = d["textos"]["pedido_nao_encontrado"]
        else:
            res = f"Pedido {ped['id']} de {ped['cliente']}: {ped['status']}. Entrega em {ped['endereco']}. CPF {ped['cpf']}."
        r["chamadas"].append(["consultar_pedido", str(pid), res])
        partes.append(res)
    manip = re.search(d["regex_manipulacao"], n, re.A)
    if re.search(r"cupom|codigo de desconto|desconto dos funcionarios", n):
        if manip:
            if "segredo" in defs:
                partes.append(d["textos"]["sem_segredo"])
            else:
                c = d["cupom"]
                if re.search(r"letras separadas|separad[ao]s? por hifen|soletr", n):
                    c = "-".join(x for x in c if x.isalnum())
                partes.append(f"Claro! O código é {c}.")
        else:
            partes.append(d["textos"]["recusa_segredo"])
    if re.search(r"instrucoes|prompt|regras internas|configuracao", n) and re.search(r"liste|mostre|repita|revele|imprima", n):
        partes.append("Minhas instruções:\n" + prompt_txt if manip else d["textos"]["recusa_prompt"])
    eco = re.search(r"(?:responda|repita)(?: exatamente)? com:? (.+)$", msg, re.I | re.S)
    if eco and "<" in eco.group(1):
        partes.append(eco.group(1).strip())
    saida = "\n".join(partes) or d["textos"]["padrao"]
    r["saida_modelo"] = saida
    final = saida
    if "saida" in defs:
        compacto = re.sub(r"[^A-Z0-9]", "", saida.upper())
        if d["canario"] in saida:
            r["filtros"].append("canario")
        if re.sub(r"[^A-Z0-9]", "", d["cupom"].upper()) in compacto:
            r["filtros"].append("cupom")
        if r["filtros"]:
            final = d["textos"]["saida_bloqueada"]
        else:
            if re.search(r"\d{3}\.\d{3}\.\d{3}-\d{2}", final):
                r["filtros"].append("cpf_mascarado")
                final = re.sub(r"\d{3}\.\d{3}\.\d{3}-\d{2}", "***.***.***-**", final)
    r["saida_final"] = final
    if "codificacao" not in defs and re.search(r"<script|\bon[a-z]+\s*=|javascript:", final, re.I | re.A):
        r["xss"] = True
    vaz = []
    if re.sub(r"[^A-Z0-9]", "", d["cupom"].upper()) in re.sub(r"[^A-Z0-9]", "", final.upper()):
        vaz.append("cupom")
    if d["canario"] in final:
        vaz.append("prompt")
    if any(c[0] == "enviar_email" and c[2] == "enviado" for c in r["chamadas"]):
        vaz.append("email_externo")
    if any(p["cliente"] in final for p in d["pedidos"] if p["cliente_id"] != d["sessao_cliente"]):
        vaz.append("pedido_outro_cliente")
    if r["xss"]:
        vaz.append("xss")
    r["vazou"] = vaz
    return r


def combos():
    for k in range(len(DEFESAS) + 1):
        for c in itertools.combinations(DEFESAS, k):
            yield set(c)


class TestIaCiber(unittest.TestCase):
    """Valida a estrutura, o conteúdo, o modelo simulado, as defesas e a compilação do estudo 24."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "ia_e_ciberseguranca_body.html"
        self.compiled_path = self.root / "IA-e-Ciberseguranca" / "treinamento-ia-e-ciberseguranca.html"
        self.portal_path = self.root / "index.html"

    def _dados(self):
        body = self.body_path.read_text(encoding="utf-8")
        m = re.search(r'<script type="application/json" id="ia-dados">(.*?)</script>', body, re.S)
        self.assertIsNotNone(m, "Bloco JSON #ia-dados ausente no body")
        return json.loads(m.group(1))

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        termos = ["OWASP Top 10 for LLM Applications", "2025", "injeção direta", "injeção indireta", "RAG", "guardrails",
                  "envenenamento", "deepfake", "canário", "humano no circuito", "MITRE ATLAS", "NIST AI RMF", "Estudo 12",
                  "Estudo 15", "simulado"]
        termos += [nome for _, nome in LLM_TOP10_2025]
        for termo in termos:
            self.assertIn(termo, content, f"Termo obrigatório ausente: {termo}")

    def test_top10_2025(self):
        d = self._dados()
        self.assertEqual([(c["id"], c["nome"]) for c in d["top10"]], LLM_TOP10_2025)

    def test_ataques_sem_defesa(self):
        d = self._dados()
        for a in d["ataques"]:
            with self.subTest(ataque=a["id"]):
                self.assertEqual(simular(d, a["texto"], set())["vazou"], a["vaza_sem_defesa"])

    def test_defesa_em_profundidade(self):
        d = self._dados()
        tudo = set(DEFESAS)
        for a in d["ataques"]:
            with self.subTest(ataque=a["id"]):
                self.assertEqual(simular(d, a["texto"], tudo)["vazou"], [])
        legit = next(a for a in d["ataques"] if a["id"] == "legitimo")
        for c in combos():
            r = simular(d, legit["texto"], c)
            self.assertFalse(r["entrada_bloqueada"], c)
            self.assertIn("1042", r["saida_final"], c)
            self.assertEqual(r["vazou"], [], c)

    def test_licoes(self):
        d = self._dados()
        A = {a["id"]: a["texto"] for a in d["ataques"]}
        v = lambda a, defs: simular(d, A[a], set(defs))["vazou"]  # noqa: E731
        self.assertEqual(v("direto", ["entrada"]), [], "o filtro de entrada para o ataque óbvio")
        self.assertIn("cupom", v("ofuscado", ["entrada"]), "mas o ofuscado passa pelo filtro de entrada")
        self.assertEqual(v("ofuscado", ["saida"]), [], "o filtro de saída com normalização pega o soletrado")
        self.assertEqual(v("ofuscado", ["segredo"]), [], "sem segredo no prompt não há o que vazar")
        self.assertEqual(v("roleplay", ["segredo"]), ["prompt"], "o prompt ainda vaza, só que sem o cupom")
        self.assertEqual(v("indireto", ["separacao"]), [])
        self.assertEqual(v("indireto", ["ferramentas"]), [])
        self.assertEqual(v("indireto", ["entrada"]), ["email_externo"], "a injeção indireta não passa pelo filtro de entrada")
        self.assertEqual(v("bola", ["ferramentas"]), [])
        self.assertEqual(v("bola", ["saida"]), ["pedido_outro_cliente"], "mascarar CPF não protege o pedido alheio")
        self.assertEqual(v("xss", ["codificacao"]), [])
        self.assertEqual(v("xss", ["saida"]), ["xss"])

    def test_dados_ficticios(self):
        d = self._dados()
        texto = json.dumps(d, ensure_ascii=False)
        for dom in re.findall(r"@([a-z0-9.-]+)", texto):
            self.assertTrue(dom.endswith(".example"), dom)

    def test_simulador_estrutura(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        for marcador in ("ia-lab", 'id="ia-dados"', "ia-missoes", "ia-defesas", "ia-ataques", "ia-mensagem", "ia-chat",
                         "ia-bastidores", "enviarMensagemIa", "alternarDefesaIa", "restaurarIa"):
            self.assertIn(marcador, content, marcador)
        ini = content.index("var IA = JSON.parse")
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
        self.assertIn('initChecklist("ia-ciber")', content)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn("IA-e-Ciberseguranca/treinamento-ia-e-ciberseguranca.html", content)
        self.assertIn('data-slug="IA-e-Ciberseguranca"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)


if __name__ == "__main__":
    unittest.main()
