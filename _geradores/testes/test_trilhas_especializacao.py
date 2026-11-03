#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testes das Trilhas 11, 12 e 13 (módulos 46–57) e de suas ligações no portal."""

import re
import sys
import tempfile
import unittest
from pathlib import Path

GERADORES_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GERADORES_DIR))

from index_dados import (  # noqa: E402
    CARREIRAS,
    CERTIFICACOES,
    ESTUDOS_DADOS,
    NECESSIDADES,
    ROTA_VAGA,
    ROTULO_ANALISTA_SI,
    TRILHAS,
)

from build_index import gerar_index_html, render_rota_vaga  # noqa: E402

NOVOS = [
    "Engenharia-de-Deteccao",
    "Threat-Hunting",
    "Monitoramento-de-Rede-NSM",
    "SOAR-e-Automacao-de-Resposta",
    "Seguranca-de-Containers",
    "Seguranca-em-Kubernetes",
    "Infraestrutura-como-Codigo-Segura",
    "Deteccao-e-Resposta-em-Nuvem",
    "Regulacao-Setor-Financeiro",
    "Fraude-em-Pagamentos-e-Pix",
    "Legislacao-e-Crimes-Ciberneticos",
    "Gestao-de-Riscos-de-Terceiros",
]

NIST_NOVOS = [
    "Detect",
    "Detect",
    "Detect",
    "Respond",
    "Protect",
    "Protect",
    "Protect",
    "Detect / Respond",
    "Govern",
    "Detect / Protect",
    "Govern",
    "Govern",
]

NOMES_CARREIRAS = {c["nome"] for c in CARREIRAS.values()}

# Perfis aceitos em cada rota da spec §3.2 -> módulos novos daquela rota
ROTAS_NOVAS = {
    ("Blue Team & Defesa", "Operações SOC & Resposta"): [
        "Monitoramento-de-Rede-NSM", "Engenharia-de-Deteccao", "Threat-Hunting", "SOAR-e-Automacao-de-Resposta",
    ],
    ("Red Team & Pentest",): ["Seguranca-de-Containers", "Seguranca-em-Kubernetes"],
    ("AppSec & DevSecOps",): [
        "Seguranca-de-Containers", "Seguranca-em-Kubernetes", "Infraestrutura-como-Codigo-Segura", "Deteccao-e-Resposta-em-Nuvem",
    ],
    ("GRC & Auditoria",): [
        "Gestao-de-Riscos-de-Terceiros", "Legislacao-e-Crimes-Ciberneticos", "Regulacao-Setor-Financeiro", "Fraude-em-Pagamentos-e-Pix",
    ],
    ("Perícia Forense & Malware",): [
        "Monitoramento-de-Rede-NSM", "Threat-Hunting", "Deteccao-e-Resposta-em-Nuvem", "Legislacao-e-Crimes-Ciberneticos",
    ],
    (ROTULO_ANALISTA_SI,): ["Regulacao-Setor-Financeiro", "Gestao-de-Riscos-de-Terceiros", "SOAR-e-Automacao-de-Resposta"],
}


class TestCatalogoEspecializacao(unittest.TestCase):
    def test_posicoes_46_a_57(self):
        self.assertEqual(list(ESTUDOS_DADOS)[45:57], NOVOS)
        self.assertEqual([ESTUDOS_DADOS[s]["trilha"] for s in NOVOS], [11] * 4 + [12] * 4 + [13] * 4)
        self.assertEqual([ESTUDOS_DADOS[s]["nist"] for s in NOVOS], NIST_NOVOS)

    def test_trilhas_novas(self):
        esperado = {
            11: ("Detecção Avançada & Threat Hunting", "#A21CAF", "fuchsia"),
            12: ("Nuvem, Containers & Kubernetes", "#0F766E", "teal"),
            13: ("Setor Regulado no Brasil", "#4D7C0F", "lime"),
        }
        for tid, (nome, cor, cor_nome) in esperado.items():
            with self.subTest(trilha=tid):
                t = TRILHAS[tid]
                self.assertEqual((t["id"], t["nome"], t["cor"], t["cor_nome"]), (tid, nome, cor, cor_nome))

    def test_carreiras_dos_modulos_novos_existem(self):
        for slug in NOVOS:
            for rotulo in ESTUDOS_DADOS[slug]["carreiras"]:
                with self.subTest(slug=slug, rotulo=rotulo):
                    self.assertIn(rotulo, NOMES_CARREIRAS)

    def test_modulos_novos_tem_carreira_das_rotas(self):
        for perfis, slugs in ROTAS_NOVAS.items():
            for slug in slugs:
                with self.subTest(perfis=perfis, slug=slug):
                    self.assertTrue(set(perfis) & set(ESTUDOS_DADOS[slug]["carreiras"]))

    def test_trilhas_11_a_13_nao_colidem_com_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            html = gerar_index_html(output_path=Path(tmp) / "index.html").read_text(encoding="utf-8")
        for slug in NOVOS:
            with self.subTest(slug=slug):
                m = re.search(rf'id="estudo-{re.escape(slug)}"\s+data-slug="[^"]*"\s+data-trilha="(\d+)"', html)
                self.assertIsNotNone(m)
                self.assertEqual(m.group(1), str(ESTUDOS_DADOS[slug]["trilha"]))
                self.assertNotEqual(m.group(1), "1")
        for valor in ("11", "12", "13"):
            self.assertIn(f'<div class="grupo" data-trilha="{valor}"', html)


class TestLigacoesEspecializacao(unittest.TestCase):
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
        self.assertEqual({c["id"]: c["apoio"] for c in ROTA_VAGA}, {
            "solucoes": ["Engenharia-Social-e-Phishing", "Linux-para-Seguranca", "PowerShell-e-Windows-Interno"],
            "banco_dados": ["OWASP-Top-10-Web"],
            "ingles": [],
            "normas": ["Resposta-a-Incidentes", "Regulacao-Setor-Financeiro", "Gestao-de-Riscos-de-Terceiros"],
            "resposta_incidentes": [
                "Operacoes-SOC-e-SIEM", "Forense-Digital", "Ransomware-Prevencao-a-Recuperacao",
                "Gestao-de-Crise-e-Comunicacao", "SOAR-e-Automacao-de-Resposta",
            ],
            "controles": ["Hardening-Sistemas", "Arquitetura-Zero-Trust", "Active-Directory-Fundamentos", "PAM-e-Acessos-Privilegiados", "Auditoria-de-TI"],
            "formacao": ["Laboratorio-Domestico-e-Portfolio"],
        })

    def test_necessidades_novas(self):
        esperado = [
            ("Preciso medir quais técnicas ATT&CK minhas regras realmente detectam", "Engenharia-de-Deteccao", "Detecção", "🎯"),
            ("Preciso procurar um invasor que nenhum alerta pegou", "Threat-Hunting", "Detecção", "🔦"),
            ("Preciso achar beaconing e túnel DNS no tráfego de rede", "Monitoramento-de-Rede-NSM", "Detecção", "📡"),
            ("Preciso automatizar a triagem sem bloquear o que não devia", "SOAR-e-Automacao-de-Resposta", "Detecção", "🤖"),
            ("Preciso revisar a segurança de uma imagem de container antes do deploy", "Seguranca-de-Containers", "Nuvem", "📦"),
            ("Preciso fechar o RBAC e isolar os pods de um cluster Kubernetes", "Seguranca-em-Kubernetes", "Nuvem", "☸️"),
            ("Preciso barrar recurso público ou sem criptografia antes do terraform apply", "Infraestrutura-como-Codigo-Segura", "Nuvem", "🏗️"),
            ("Preciso investigar uma chave de acesso vazada na nuvem", "Deteccao-e-Resposta-em-Nuvem", "Nuvem", "🔑"),
            ("Preciso adequar a política de segurança às exigências do Banco Central", "Regulacao-Setor-Financeiro", "Regulação", "🏦"),
            ("Preciso montar regras antifraude para transações Pix", "Fraude-em-Pagamentos-e-Pix", "Regulação", "💸"),
            ("Preciso saber o que guardar e como preservar provas de um crime cibernético", "Legislacao-e-Crimes-Ciberneticos", "Regulação", "⚖️"),
            ("Preciso avaliar o risco de um fornecedor crítico antes de contratar", "Gestao-de-Riscos-de-Terceiros", "Regulação", "🤝"),
        ]
        obtido = [(n["desafio"], n["slug"], n["categoria"], n["icone"]) for n in NECESSIDADES if n["slug"] in NOVOS]
        self.assertEqual(obtido, esperado)

    def test_certificacoes_novas(self):
        esperado = {
            "CCSP": ["Seguranca-de-Containers", "Seguranca-em-Kubernetes", "Infraestrutura-como-Codigo-Segura", "Deteccao-e-Resposta-em-Nuvem"],
            "GSEC": ["Monitoramento-de-Rede-NSM", "Seguranca-de-Containers"],
            "CISSP": ["Monitoramento-de-Rede-NSM", "Deteccao-e-Resposta-em-Nuvem", "Gestao-de-Riscos-de-Terceiros"],
            "CISM": ["Regulacao-Setor-Financeiro", "Gestao-de-Riscos-de-Terceiros"],
            "Security+": ["Engenharia-de-Deteccao", "Fraude-em-Pagamentos-e-Pix"],
            "CEH": ["Seguranca-em-Kubernetes"],
            "ISFS": ["Legislacao-e-Crimes-Ciberneticos"],
            "PDPF/PDPP": ["Gestao-de-Riscos-de-Terceiros", "Legislacao-e-Crimes-Ciberneticos"],
            "ITIL 4 F": ["Gestao-de-Riscos-de-Terceiros"],
            "CSFPC": ["Legislacao-e-Crimes-Ciberneticos"],
            "CISA": ["Gestao-de-Riscos-de-Terceiros"],
            "CRISC": ["Gestao-de-Riscos-de-Terceiros"],
            "CDPSE": ["Gestao-de-Riscos-de-Terceiros"],
        }
        self.assertTrue(set(esperado) <= {c["sigla"] for c in CERTIFICACOES})
        for c in CERTIFICACOES:
            with self.subTest(sigla=c["sigla"]):
                self.assertEqual([m for m in c["modulos"] if m in NOVOS], esperado.get(c["sigla"], []))

    def test_chips_de_apoio_normas_tem_data_slug(self):
        html = render_rota_vaga(ROTA_VAGA, {})

        def artigo(cid):
            m = re.search(rf'<article[^>]*id="vaga-{cid}".*?</article>', html, re.S)
            self.assertIsNotNone(m, cid)
            return m.group(0)

        normas = artigo("normas")
        self.assertIn('data-slug="Regulacao-Setor-Financeiro"', normas)
        self.assertIn('data-slug="Gestao-de-Riscos-de-Terceiros"', normas)
        self.assertIn('data-slug="SOAR-e-Automacao-de-Resposta"', artigo("resposta_incidentes"))


if __name__ == "__main__":
    unittest.main()
