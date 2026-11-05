#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_fundamentos_computacao.py
Testes automatizados para o Estudo 61: Fundamentos-de-Computacao-e-SO

O laboratório Inspetor de Bytes tem três abas: identificação de arquivo por
magic bytes, conversão texto/hexadecimal/Base64 e uma pilha simulada de
16 + 8 + 8 bytes (buffer, canário, endereço de retorno). Este teste espelha em
Python as regras do motor JavaScript. O tamanho da entrada conta bytes UTF-8,
não caracteres, e o Base64 faz ida e volta com acento (TextEncoder/TextDecoder).
"""

import base64
import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402
from navegador import CHROME, executar  # noqa: E402

SLUG = "Fundamentos-de-Computacao-e-SO"
SECOES = ["introducao", "memoria-e-processos", "kernel-e-syscalls", "binario-e-codificacoes",
          "arquivos-e-permissoes", "virtualizacao", "simulador", "checklist", "quiz", "fatos"]
ASSINATURAS = {"png": "89504E470D0A1A0A", "pdf": "255044462D", "zip": "504B0304", "elf": "7F454C46",
               "pe": "4D5A", "script": "2321"}
# extensões que um arquivo honesto de cada tipo costuma ter (PE vira .exe; script, .sh)
EXTENSOES = {"png": {"png"}, "pdf": {"pdf"}, "zip": {"zip"}, "elf": {"elf"}, "pe": {"exe", "dll"}, "script": {"sh"}}
TAM_BUFFER, TAM_CANARIO, TAM_RETORNO = 16, 8, 8


# ============================================================ regras
def identificar(hex_texto, assinaturas=ASSINATURAS):
    """Espelho de identificarAssinatura: tipo cujo prefixo casa (o mais longo primeiro); None se nenhum."""
    limpo = re.sub(r"[\s:]", "", hex_texto).upper()
    for tipo, prefixo in sorted(assinaturas.items(), key=lambda kv: -len(kv[1])):
        if limpo.startswith(prefixo):
            return tipo
    return None


def simular_pilha(entrada, canario, aslr):
    """Espelho de simularPilha: n conta bytes UTF-8 da entrada."""
    n = len(entrada.encode("utf-8"))
    if n <= TAM_BUFFER:
        return "normal"
    if canario:
        return "abortado_canario"
    if aslr:
        return "crash"
    if n >= TAM_BUFFER + TAM_RETORNO:
        return "controle_do_fluxo"
    return "crash"


def texto_para_hex(texto):
    """Espelho de textoParaHex: bytes UTF-8 em pares maiúsculos separados por espaço."""
    return " ".join(f"{b:02X}" for b in texto.encode("utf-8"))


def hex_para_texto(hex_texto):
    """Espelho de hexParaTexto: None se houver dígito fora de 0-9A-F, número ímpar de dígitos ou UTF-8 inválido."""
    limpo = re.sub(r"[\s:]", "", hex_texto)
    if len(limpo) % 2 != 0 or not re.fullmatch(r"[0-9a-fA-F]*", limpo):
        return None
    try:
        return bytes.fromhex(limpo).decode("utf-8")
    except UnicodeDecodeError:
        return None


def texto_para_base64(texto):
    """Espelho de textoParaBase64 (RFC 4648, com preenchimento)."""
    return base64.b64encode(texto.encode("utf-8")).decode("ascii")


def base64_para_texto(b64):
    """Espelho de base64ParaTexto: alfabeto padrão, '=' só no fim, comprimento coerente; None se inválido."""
    s = re.sub(r"\s", "", b64)
    m = re.fullmatch(r"([A-Za-z0-9+/]*)(={0,2})", s)
    if not m:
        return None
    dados, pad = m.groups()
    if len(dados) % 4 == 1 or (pad and (len(dados) + len(pad)) % 4 != 0):
        return None
    try:
        return base64.b64decode(dados + "=" * (-len(dados) % 4)).decode("utf-8")
    except (ValueError, UnicodeDecodeError):
        return None


def numero_do_estudo(slug):
    linhas = [l for l in (Path(__file__).resolve().parent.parent / "estudos.txt").read_text(encoding="utf-8").splitlines()
              if l.strip() and not l.startswith("#")]
    return [l.split("|")[0] for l in linhas].index(slug) + 1


class TestFundamentosComputacao(unittest.TestCase):
    """Estrutura, conteúdo, simulador e compilação do estudo 61."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "fundamentos_de_computacao_e_so_body.html"
        self.compiled_path = self.root / SLUG / "treinamento-fundamentos-de-computacao-e-so.html"
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
        m = re.search(r'<script type="application/json" id="comp-dados">(.*?)</script>', self._body(), re.S)
        self.assertIsNotNone(m, "Bloco JSON #comp-dados ausente no body")
        return json.loads(m.group(1))

    def _motor(self):
        content = self._compilado()
        ini = content.index('JSON.parse(document.getElementById("comp-dados")')
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
        self.assertIn('data-slug="fundamentos-de-computacao-e-so"', body)

    def test_coerencia_com_o_catalogo(self):
        content = self._compilado()
        info = ESTUDOS_DADOS[SLUG]
        self.assertIn(info["simulador_nome"], content)
        self.assertIn(info["pergunta_chave"], content)
        self.assertIn(info["subtitulo"], self.portal_path.read_text(encoding="utf-8"))
        for fato in info["fatos"]:
            self.assertIn(fato, content, fato)

    # ------------------------------------------------------------ conteúdo
    def test_termos_chave(self):
        body = self._body()
        for termo in ("pilha", "heap", "endereço de retorno", "buffer overflow", "ASLR", "DEP", "NX", "canário",
                      "kernel", "espaço de usuário", "chamada de sistema", "rootkit", "hexadecimal",
                      "little-endian", "UTF-8", "Base64", "codificação não é criptografia", "magic bytes", "UID",
                      "SID", "ACL", "SYSTEM", "setuid", "hipervisor", "tipo 1", "tipo 2", "namespaces", "cgroups"):
            self.assertIn(termo, body, termo)

    def test_pontes_sem_repetir(self):
        body = self._body()
        antes = body[:body.index('id="simulador"')]
        refs = ["Estudo 10", "Estudo 62"]
        for slug in ("Linux-para-Seguranca", "PowerShell-e-Windows-Interno", "Forense-Digital",
                     "Analise-Basica-de-Malware", "Seguranca-de-Containers"):
            refs.append(f"Estudo {numero_do_estudo(slug)}")
        self.assertEqual(numero_do_estudo("Seguranca-em-Endpoints-EDR"), 10)
        self.assertEqual(numero_do_estudo(SLUG), 61)
        for ref in refs:
            self.assertIn(ref, antes, ref)
        sec = self._secao("arquivos-e-permissoes")
        self.assertLessEqual(sec.count("<table"), 1)
        texto = re.sub(r"<[^>]+>", " ", sec)
        self.assertLessEqual(len(texto.split()), 600, "a seção é curta e aponta para os módulos 34 e 36")

    def test_referencias(self):
        fim = self._secao("fatos")
        for ref in ("RFC 4648", "ELF", "PE"):
            self.assertIn(ref, fim, ref)
        self.assertTrue("Intel" in fim or "AMD" in fim)

    # ---------------------------------------------------------------- dados
    def test_dados_do_simulador(self):
        d = self._dados()
        self.assertEqual(d["assinaturas"], ASSINATURAS)
        self.assertEqual(d["pilha"], {"buffer": 16, "canario": 8, "retorno": 8})
        arquivos = d["arquivos"]
        self.assertEqual(len(arquivos), 6)
        self.assertEqual(len({a["id"] for a in arquivos}), 6)
        falsas = 0
        for a in arquivos:
            with self.subTest(arquivo=a.get("id")):
                for campo in ("id", "nome", "hex", "tipo_real"):
                    self.assertTrue(a[campo].strip(), campo)
                self.assertIn(a["tipo_real"], d["assinaturas"])
                if a["nome"].rsplit(".", 1)[-1].lower() not in EXTENSOES[a["tipo_real"]]:
                    falsas += 1
        self.assertEqual(falsas, 1, "exatamente um arquivo com extensão falsa")
        self.assertEqual({a["tipo_real"] for a in arquivos}, set(ASSINATURAS), "um arquivo de cada tipo")

    def test_assinaturas_espelhadas(self):
        d = self._dados()
        for a in d["arquivos"]:
            self.assertEqual(identificar(a["hex"], d["assinaturas"]), a["tipo_real"], a["id"])
        self.assertIsNone(identificar("FFD8FF", d["assinaturas"]))
        self.assertIsNone(identificar("", d["assinaturas"]))

    def test_pilha_espelhada(self):
        self.assertEqual(simular_pilha("A" * 16, True, True), "normal")
        self.assertEqual(simular_pilha("A" * 17, True, False), "abortado_canario")
        self.assertEqual(simular_pilha("A" * 30, False, True), "crash")
        self.assertEqual(simular_pilha("A" * 20, False, False), "crash")
        self.assertEqual(simular_pilha("A" * 24, False, False), "controle_do_fluxo")

    def test_bytes_utf8(self):
        self.assertEqual(simular_pilha("ç" * 9, False, False), "crash")  # 18 bytes, não 9 caracteres
        self.assertEqual(simular_pilha("ç" * 8, True, True), "normal")   # 16 bytes
        self.assertEqual(base64.b64encode("ação".encode("utf-8")).decode(), "YcOnw6Nv")
        self.assertIn("YcOnw6Nv", self._body())
        motor = self._motor()
        self.assertIn("TextEncoder", self._secao_funcao(motor, "simularPilha"))
        self.assertIn("TextEncoder", self._secao_funcao(motor, "textoParaHex"))
        self.assertIn("TextEncoder", self._secao_funcao(motor, "textoParaBase64"))
        self.assertIn("TextDecoder", self._secao_funcao(motor, "hexParaTexto"))
        self.assertIn("TextDecoder", self._secao_funcao(motor, "base64ParaTexto"))

    def test_conversoes_espelhadas(self):
        self.assertEqual(texto_para_hex("ação"), "61 C3 A7 C3 A3 6F")
        self.assertEqual(hex_para_texto("61 C3 A7 C3 A3 6F"), "ação")
        self.assertEqual(hex_para_texto("61c3a7c3a36f"), "ação")
        self.assertEqual(texto_para_base64("ação"), "YcOnw6Nv")
        self.assertEqual(base64_para_texto("YcOnw6Nv"), "ação")
        for t in ("", "a", "ab", "abc", "ç" * 9):
            self.assertEqual(hex_para_texto(texto_para_hex(t)), t)
            self.assertEqual(base64_para_texto(texto_para_base64(t)), t)
        for ruim in ("zz", "6", "C3", "FF FE"):  # não hex, ímpar, UTF-8 truncado, UTF-8 inválido
            self.assertIsNone(hex_para_texto(ruim), ruim)
        for ruim in ("@@@", "A", "YcOnw6N=v", "YQ=", "Y===", "////", "YcOnw6Nv===", "=YQ"):
            self.assertIsNone(base64_para_texto(ruim), ruim)
        self.assertEqual(base64_para_texto("YQ=="), "a")
        self.assertEqual(base64_para_texto("YQ"), "a")

    @staticmethod
    def _secao_funcao(motor, nome):
        ini = motor.index(f"window.{nome} = function")
        return motor[ini:motor.index("\n    };", ini)]

    # ------------------------------------------------------------ simulador
    def test_simulador_sem_apis_inseguras(self):
        content = self._compilado()
        self.assertIn('id="comp-dados"', content)
        motor = self._motor()
        for proibido in ("innerHTML", "outerHTML", "eval(", "new Function", "fetch(", "XMLHttpRequest", "WebSocket",
                         "document.write", "localStorage", "btoa(", "atob("):
            self.assertNotIn(proibido, motor, proibido)
        for marcador in ("comp-lab", "comp-aba-assinatura", "comp-aba-decodificador", "comp-aba-pilha",
                         "comp-canario", "comp-aslr", "comp-pilha", "comp-resultado-pilha"):
            self.assertIn(marcador, content, marcador)
        self.assertIn('role="tablist"', content)
        self.assertIn("aria-selected", motor)
        self.assertIn("aria-label", content)
        self.assertIn("textContent", motor)
        self.assertIn("createElement", motor)

    @unittest.skipUnless(CHROME, "Chrome ausente")
    def test_motor_no_navegador(self):
        r = executar(self._compilado(), r"""
          const out = {};
          out.b64 = textoParaBase64('ação');
          out.volta = base64ParaTexto(out.b64);
          out.hex = textoParaHex('ç');
          out.hexVolta = hexParaTexto('c3 a7');
          out.hexInvalido = hexParaTexto('zz');
          out.b64Invalido = base64ParaTexto('@@@');
          out.sig = [identificarAssinatura('7F 45 4C 46 02'), identificarAssinatura('FFD8FF')];
          out.pilha = [simularPilha('A'.repeat(16), true, true), simularPilha('A'.repeat(17), true, false),
                       simularPilha('A'.repeat(30), false, true), simularPilha('A'.repeat(20), false, false),
                       simularPilha('A'.repeat(24), false, false), simularPilha('ç'.repeat(9), false, false)];
          __fim(out);
        """)
        self.assertEqual(r["erros"], [])
        s = r["saida"]
        self.assertEqual(s["b64"], "YcOnw6Nv")
        self.assertEqual(s["volta"], "ação")
        self.assertEqual(s["hex"], "C3 A7")
        self.assertEqual(s["hexVolta"], "ç")
        self.assertIsNone(s["hexInvalido"])
        self.assertIsNone(s["b64Invalido"])
        self.assertEqual(s["sig"], ["elf", None])
        self.assertEqual(s["pilha"], ["normal", "abortado_canario", "crash", "crash", "controle_do_fluxo", "crash"])

    def test_componentes_pedagogicos(self):
        body = self._body()
        content = self._compilado()
        self.assertIn('<pre class="mermaid"', body)
        self.assertIn('class="diagram-svg-wrap', content)
        self.assertIn('class="callout', content)
        self.assertIn('class="facts-grid', content)
        self.assertIn(content.count('class="checklist-item"'), range(4, 9))
        self.assertEqual(content.count('class="checklist-item"'), 6)
        self.assertGreaterEqual(content.count('class="quiz-item"'), 6)

    def test_portal_mostra_o_61(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn(f"{SLUG}/treinamento-fundamentos-de-computacao-e-so.html", content)


if __name__ == "__main__":
    unittest.main()
