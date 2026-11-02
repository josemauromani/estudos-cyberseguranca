#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_backup_imutavel.py
Testes automatizados para o Estudo 45: Backup-Imutavel-e-Recuperacao
"""

import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from index_dados import ESTUDOS_DADOS  # noqa: E402


def atacar(d, a, perfil):
    """Espelho do motor em JavaScript: o que sobrevive a um atacante com Domain Admin."""
    dias = d["perfis"][perfil]["dias"]
    alcanca = (not a["rede_gerencia_isolada"]) or a["servidor_no_dominio"]
    console = alcanca and (a["servidor_no_dominio"] or (a["console_contas"] == "dominio" and not a["console_mfa"]))
    copias = {}
    for c in a["copias"]:
        if c == "nas_smb":
            copias[c] = ["perdida", "nas_dominio"]
        elif c == "site_remoto":
            copias[c] = ["perdida", "remoto_dominio"]
        elif c == "linux_endurecido":
            if a["linux_ssh_dominio"]:
                copias[c] = ["perdida", "ssh_dominio"]
            elif a["retencao_imutavel_dias"] < dias:
                copias[c] = ["perdida", "imutabilidade_expirou"]
            else:
                copias[c] = ["sobrevive", "imutavel"]
        elif c == "nuvem_object_lock":
            expostas = a["nuvem_credencial"] == "no_servidor" and console
            if a["object_lock_modo"] == "governance" and expostas:
                copias[c] = ["perdida", "governance_contornado"]
            elif a["retencao_imutavel_dias"] < dias:
                copias[c] = ["perdida", "imutabilidade_expirou"]
            else:
                copias[c] = ["sobrevive", "object_lock"]
        elif c == "fita_offline":
            if not a["fita_ejetada"] and console:
                copias[c] = ["perdida", "fita_conectada"]
            else:
                copias[c] = ["sobrevive", "air_gap"]
    sobrev = [c for c, v in copias.items() if v[0] == "sobrevive"]
    ad = a["backup_dc"] and a["dsrm_cofre"] and bool(sobrev)
    if not sobrev:
        status = "perdido"
    elif not ad:
        status = "sem_ad"
    elif not a["teste_restauracao"]:
        status = "nao_testado"
    else:
        status = "recuperavel"
    return {"console_comprometido": console, "copias": copias, "status": status}


def regra(d, a):
    midias = {"disco"} | {d["copias"][c]["midia"] for c in a["copias"]}
    return {"tres_copias": 1 + len(a["copias"]) >= 3, "duas_midias": len(midias) >= 2,
            "uma_fora": any(d["copias"][c]["fora"] for c in a["copias"]),
            "uma_imutavel_offline": any(c in ("linux_endurecido", "nuvem_object_lock") or (c == "fita_offline" and a["fita_ejetada"]) for c in a["copias"]),
            "zero_erros": bool(a["teste_restauracao"])}


class TestBackupImutavel(unittest.TestCase):
    """Valida a estrutura, o conteúdo, o motor de ataque e a compilação do estudo 45."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / "_geradores" / "backup_imutavel_e_recuperacao_body.html"
        self.compiled_path = self.root / "Backup-Imutavel-e-Recuperacao" / "treinamento-backup-imutavel-e-recuperacao.html"
        self.portal_path = self.root / "index.html"

    def _dados(self):
        body = self.body_path.read_text(encoding="utf-8")
        m = re.search(r'<script type="application/json" id="bk-dados">(.*?)</script>', body, re.S)
        self.assertIsNotNone(m, "Bloco JSON #bk-dados ausente no body")
        return json.loads(m.group(1))

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        termos = ["3-2-1-1-0", "WORM", "object lock", "governance", "compliance", "air gap", "imutabilidade",
                  "repositório Linux endurecido", "fora do domínio", "MFA", "DSRM", "restauração autoritativa",
                  "não autoritativa", "krbtgt", "recuperação de floresta", "ambiente isolado", "wbadmin", "ntdsutil",
                  "chattr +i", "put-object-lock-configuration", "Estudo 28", "Estudo 39", "Estudo 42"]
        for termo in termos:
            self.assertIn(termo, content, f"Termo obrigatório ausente: {termo}")

    def test_inicial_perde_tudo(self):
        d = self._dados()
        for p in d["perfis"]:
            r = atacar(d, d["arquitetura_inicial"], p)
            self.assertEqual(r["status"], "perdido", p)
            self.assertTrue(r["console_comprometido"])

    def test_referencia_sobrevive(self):
        d = self._dados()
        for p in d["perfis"]:
            r = atacar(d, d["arquitetura_referencia"], p)
            self.assertEqual(r["status"], "recuperavel", p)
            self.assertTrue(all(v[0] == "sobrevive" for v in r["copias"].values()), (p, r["copias"]))
        self.assertTrue(all(regra(d, d["arquitetura_referencia"]).values()))

    def test_licoes(self):
        d = self._dados()
        ref = d["arquitetura_referencia"]
        base = dict(ref, copias=["nuvem_object_lock"], servidor_no_dominio=True, nuvem_credencial="no_servidor")
        self.assertEqual(atacar(d, dict(base, object_lock_modo="governance"), "rapido")["copias"]["nuvem_object_lock"][1], "governance_contornado")
        self.assertEqual(atacar(d, dict(base, object_lock_modo="compliance"), "rapido")["copias"]["nuvem_object_lock"][0], "sobrevive")
        curta = dict(ref, retencao_imutavel_dias=14)
        self.assertEqual(atacar(d, curta, "rapido")["status"], "recuperavel")
        self.assertNotEqual(atacar(d, dict(curta, copias=["linux_endurecido"]), "paciente")["status"], "recuperavel", "o paciente espera a imutabilidade expirar")
        self.assertEqual(atacar(d, dict(ref, dsrm_cofre=False), "rapido")["status"], "sem_ad")
        self.assertEqual(atacar(d, dict(ref, teste_restauracao=False), "rapido")["status"], "nao_testado")
        self.assertFalse(atacar(d, dict(ref, servidor_no_dominio=False, console_contas="dominio", console_mfa=False, rede_gerencia_isolada=True), "rapido")["console_comprometido"],
                         "rede de gerência isolada impede o acesso ao console")
        self.assertTrue(atacar(d, dict(ref, servidor_no_dominio=True, console_mfa=True, console_contas="locais"), "rapido")["console_comprometido"],
                        "MFA no console não salva um servidor ingressado no domínio")
        self.assertGreater(d["perfis"]["paciente"]["dias"], d["perfis"]["rapido"]["dias"])

    def test_simulador_estrutura(self):
        content = self.compiled_path.read_text(encoding="utf-8")
        for marcador in ("bk-lab", 'id="bk-dados"', "bk-missoes", "bk-arquitetura", "bk-regra", "bk-resultado",
                         "atacarBackup", "executarAtaqueBackup", "restaurarBackup"):
            self.assertIn(marcador, content, marcador)
        ini = content.index("var BK = JSON.parse")
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
        self.assertIn('initChecklist("backup-imutavel")', content)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding="utf-8")
        self.assertIn("Backup-Imutavel-e-Recuperacao/treinamento-backup-imutavel-e-recuperacao.html", content)
        self.assertIn('data-slug="Backup-Imutavel-e-Recuperacao"', content)
        self.assertIn(f"/ {len(ESTUDOS_DADOS)}", content)


if __name__ == "__main__":
    unittest.main()
