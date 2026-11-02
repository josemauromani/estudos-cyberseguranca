#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testes das Trilhas 8, 9 e 10 (módulos 34–45) e de suas ligações no portal."""

import re
import sys
import tempfile
import unittest
from pathlib import Path

GERADORES_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GERADORES_DIR))

from index_dados import CARREIRAS, CERTIFICACOES, ESTUDOS_DADOS, NECESSIDADES, ROTA_VAGA, TRILHAS  # noqa: E402

from build_index import gerar_index_html, render_rota_vaga  # noqa: E402

NOVOS = [
    "Linux-para-Seguranca",
    "Python-para-Seguranca",
    "PowerShell-e-Windows-Interno",
    "Laboratorio-Domestico-e-Portfolio",
    "Active-Directory-Fundamentos",
    "Ataques-e-Defesa-no-AD",
    "PAM-e-Acessos-Privilegiados",
    "Identidade-Hibrida-e-Nuvem",
    "Ransomware-Prevencao-a-Recuperacao",
    "Gestao-de-Crise-e-Comunicacao",
    "Exercicios-Tabletop",
    "Backup-Imutavel-e-Recuperacao",
]

NOMES_CARREIRAS = {c["nome"] for c in CARREIRAS.values()}


class TestCatalogoNovo(unittest.TestCase):
    def test_posicoes_34_a_45(self):
        self.assertEqual(list(ESTUDOS_DADOS)[33:45], NOVOS)
        self.assertEqual([ESTUDOS_DADOS[s]["trilha"] for s in NOVOS], [8] * 4 + [9] * 4 + [10] * 4)

    def test_trilhas_novas(self):
        esperado = {
            8: ("Ferramentas & Automação do Analista", "#475569", "slate"),
            9: ("Identidade Corporativa & Active Directory", "#4F46E5", "indigo"),
            10: ("Resiliência, Crise & Ransomware", "#C2410C", "orange"),
        }
        for tid, (nome, cor, cor_nome) in esperado.items():
            with self.subTest(trilha=tid):
                info = TRILHAS[tid]
                self.assertEqual((info["id"], info["nome"], info["cor"], info["cor_nome"]), (tid, nome, cor, cor_nome))

    def test_modulo_37_tem_todas_as_carreiras(self):
        self.assertEqual(set(ESTUDOS_DADOS["Laboratorio-Domestico-e-Portfolio"]["carreiras"]), NOMES_CARREIRAS)

    def test_carreiras_dos_modulos_existem(self):
        for slug, dados in ESTUDOS_DADOS.items():
            with self.subTest(slug=slug):
                self.assertLessEqual(set(dados["carreiras"]), NOMES_CARREIRAS)

    def test_trilha_10_nao_colide_com_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            html = gerar_index_html(output_path=Path(tmp) / "index.html").read_text(encoding="utf-8")
        for slug in NOVOS:
            m = re.search(rf'id="estudo-{re.escape(slug)}"\s+data-slug="[^"]*"\s+data-trilha="(\d+)"', html)
            self.assertIsNotNone(m, slug)
            self.assertNotEqual(m.group(1), "1", slug)
            if slug in NOVOS[8:]:
                self.assertEqual(m.group(1), "10", slug)
        self.assertIn('data-value="10"', html)


class TestLigacoesNovas(unittest.TestCase):
    def test_principais_da_rota_intactos(self):
        self.assertEqual({c["id"]: c["principais"] for c in ROTA_VAGA}, {
            "solucoes": ["Segmentacao-e-Firewall", "Seguranca-em-Endpoints-EDR", "Protecao-de-Dados-e-Conteudo", "Seguranca-de-Redes-Defesa"],
            "banco_dados": ["Seguranca-de-Bancos-de-Dados"],
            "ingles": ["Ingles-Tecnico-Ciber"],
            "normas": ["PCI-DSS", "ISO-27001-e-27002", "Gestao-de-Riscos-TI"],
            "resposta_incidentes": ["Resposta-a-Incidentes"],
            "controles": ["ISO-27001-e-27002"],
            "formacao": ["Certificacoes-e-Carreira"],
        })

    def test_apoios_novos(self):
        esperado = {
            "solucoes": ["Linux-para-Seguranca", "PowerShell-e-Windows-Interno"],
            "controles": ["Active-Directory-Fundamentos", "PAM-e-Acessos-Privilegiados"],
            "resposta_incidentes": ["Ransomware-Prevencao-a-Recuperacao", "Gestao-de-Crise-e-Comunicacao"],
            "formacao": ["Laboratorio-Domestico-e-Portfolio"],
        }
        apoio = {c["id"]: c["apoio"] for c in ROTA_VAGA}
        for cid, novos in esperado.items():
            with self.subTest(competencia=cid):
                self.assertEqual(apoio[cid][-len(novos):], novos)
        for cid in set(apoio) - set(esperado):
            self.assertFalse(set(apoio[cid]) & set(NOVOS), cid)

    def test_necessidades_novas(self):
        esperado = [
            ("Preciso investigar um servidor Linux suspeito pela linha de comando", "Linux-para-Seguranca", "Ferramentas", "🐧"),
            ("Preciso automatizar a triagem de logs e consultar a reputação de IPs", "Python-para-Seguranca", "Automação", "🐍"),
            ("Preciso reconstruir uma intrusão a partir dos eventos do Windows", "PowerShell-e-Windows-Interno", "Ferramentas", "🪟"),
            ("Preciso montar um laboratório e um portfólio para entrevistas", "Laboratorio-Domestico-e-Portfolio", "Carreira", "🧪"),
            ("Preciso entender Kerberos e a herança de GPOs no Active Directory", "Active-Directory-Fundamentos", "Identidade", "🏛️"),
            ("Preciso detectar Kerberoasting e fechar caminhos até Domain Admin", "Ataques-e-Defesa-no-AD", "Identidade", "🕸️"),
            ("Preciso controlar e auditar contas de administrador", "PAM-e-Acessos-Privilegiados", "Identidade", "🗝️"),
            ("Preciso escrever políticas de acesso condicional no Entra ID", "Identidade-Hibrida-e-Nuvem", "Identidade", "☁️"),
            ("Preciso conter um ataque de ransomware e retomar a operação", "Ransomware-Prevencao-a-Recuperacao", "Resiliência", "🔒"),
            ("Preciso coordenar a crise e comunicar o incidente à ANPD", "Gestao-de-Crise-e-Comunicacao", "Resiliência", "📣"),
            ("Preciso conduzir um exercício tabletop com a diretoria", "Exercicios-Tabletop", "Resiliência", "🎲"),
            ("Preciso garantir que o backup sobreviva a um admin de domínio comprometido", "Backup-Imutavel-e-Recuperacao", "Resiliência", "💾"),
        ]
        obtido = [(n["desafio"], n["slug"], n["categoria"], n["icone"]) for n in NECESSIDADES if n["slug"] in NOVOS]
        self.assertEqual(obtido, esperado)

    def test_certificacoes_novas(self):
        esperado = {
            "GSEC": ["Linux-para-Seguranca", "PowerShell-e-Windows-Interno", "Active-Directory-Fundamentos"],
            "Security+": ["PAM-e-Acessos-Privilegiados", "Ransomware-Prevencao-a-Recuperacao", "Backup-Imutavel-e-Recuperacao"],
            "CISSP": ["Active-Directory-Fundamentos", "PAM-e-Acessos-Privilegiados", "Backup-Imutavel-e-Recuperacao"],
            "CISM": ["Gestao-de-Crise-e-Comunicacao", "Exercicios-Tabletop"],
            "CEH": ["Ataques-e-Defesa-no-AD"],
            "CCSP": [],
        }
        for c in CERTIFICACOES:
            with self.subTest(sigla=c["sigla"]):
                self.assertEqual([m for m in c["modulos"] if m in NOVOS], esperado[c["sigla"]])
                n = len(esperado[c["sigla"]])
                if n:
                    self.assertEqual(c["modulos"][-n:], esperado[c["sigla"]])

    def test_chips_de_apoio_novos_tem_data_slug(self):
        html = render_rota_vaga(ROTA_VAGA, {})
        ini = html.index('id="vaga-controles"')
        artigo = html[ini:html.index("</article>", ini)]
        self.assertIn('data-slug="Active-Directory-Fundamentos"', artigo)
        self.assertIn('data-slug="PAM-e-Acessos-Privilegiados"', artigo)


class TestDocumentacao(unittest.TestCase):
    def test_rotas_por_perfil_no_curriculo(self):
        txt = (GERADORES_DIR / "CURRICULO.md").read_text(encoding="utf-8")
        rotas = [
            "01 -> 02 -> 34 -> 36 -> 05 -> 06 -> 07 -> 10 -> 39 -> 16 -> 17 -> 18 -> 42",
            "01 -> 02 -> 34 -> 04 -> 11 -> 12 -> 13 -> 38 -> 39 -> 14 -> 15",
            "01 -> 03 -> 04 -> 35 -> 06 -> 12 -> 13 -> 21 -> 41 -> 22 -> 24",
            "01 -> 08 -> 40 -> 09 -> 25 -> 26 -> 27 -> 28 -> 43 -> 44",
            "01 -> 02 -> 06 -> 36 -> 10 -> 16 -> 18 -> 42 -> 45 -> 19 -> 20",
            "01 -> 34 -> 36 -> 05 -> 06 -> 07 -> 10 -> 29 -> 30 -> 38 -> 40 -> 25 -> 26 -> 31 -> 18 -> 42 -> 43 -> 32 -> 37 -> 33",
        ]
        for rota in rotas:
            with self.subTest(rota=rota):
                self.assertIn(f"`{rota}`", txt)


if __name__ == "__main__":
    unittest.main()
