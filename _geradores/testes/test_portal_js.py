#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comportamento do portal (T10) no Chrome headless: status, continuar, agrupar, filtros, visões, gaveta."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

TESTES = Path(__file__).resolve().parent
GERADORES = TESTES.parent
sys.path.insert(0, str(GERADORES))
sys.path.insert(0, str(TESTES))

from build_index import corpo_do_modulo, gerar_index_html  # noqa: E402
from contrato import extrair_secoes  # noqa: E402
from index_dados import CARREIRAS, CERTIFICACOES, ESTUDOS_DADOS, NIVEIS  # noqa: E402
from navegador import CHROME, executar  # noqa: E402

SLUG = "Threat-Hunting"
SECOES = [s.id for s in extrair_secoes(corpo_do_modulo(SLUG).read_text(encoding="utf-8"))]
CARD = f'[data-slug="{SLUG}"].mc'


def semear(**chaves) -> str:
    return ";".join(f"localStorage.setItem({json.dumps(k)},{json.dumps(v)})" for k, v in chaves.items())


@unittest.skipUnless(CHROME, "Chrome não encontrado")
class TestPortalJs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as tmp:
            cls.portal = gerar_index_html(output_path=Path(tmp) / "index.html").read_text(encoding="utf-8")

    def rodar(self, script, antes="", **kw):
        r = executar(self.portal, script, script_antes=antes, **kw)
        return r

    def status(self, antes):
        r = self.rodar(f"__fim(document.querySelector('{CARD} .mc-status').textContent)", antes)
        self.assertEqual(r["erros"], [])
        return r["saida"]

    def test_status_concluido_sem_leitura(self):
        self.assertIn("Concluído", self.status(semear(**{f"cs_done_{SLUG}": "true"})))

    def test_status_em_andamento_com_porcentagem(self):
        antes = semear(**{f"cs_read_{SLUG}": json.dumps(SECOES[:3])})
        self.assertEqual(len(SECOES), 6)
        self.assertIn("50% lido", self.status(antes))

    def test_status_por_checklist_sem_leitura(self):
        self.assertIn("0% lido", self.status(semear(**{f"cs_check_{SLUG}_chk-th-1": "true"})))

    def test_status_por_questao(self):
        self.assertIn("0% lido", self.status(semear(**{f"cs_quiz_{SLUG}_q1": "revisar"})))

    def test_nao_iniciado(self):
        self.assertIn("Não iniciado", self.status(""))

    def test_cs_read_corrompido_conta_zero(self):
        r = self.rodar(f"__fim(document.querySelector('{CARD} .mc-status').textContent)",
                       semear(**{f"cs_read_{SLUG}": "{x"}))
        self.assertEqual(r["erros"], [])
        self.assertIn("0% lido", r["saida"])

    def test_continuar_estudando(self):
        antes = semear(cs_last=json.dumps({"slug": SLUG, "secao": "simulador", "ts": 1}))
        r = self.rodar("const c=document.getElementById('continuar');"
                       "__fim({oculto:c.hidden,texto:c.textContent,href:(c.querySelector('a')||{}).href||''})", antes)
        self.assertEqual(r["erros"], [])
        self.assertFalse(r["saida"]["oculto"])
        self.assertIn(ESTUDOS_DADOS[SLUG]["titulo"], r["saida"]["texto"])
        self.assertIn("🧪 Laboratório", r["saida"]["texto"])
        self.assertIn("#simulador", r["saida"]["href"])

    def test_sem_cs_last_continuar_oculto(self):
        r = self.rodar("const c=document.getElementById('continuar');__fim({o:c.hidden,t:c.textContent.trim()})")
        self.assertTrue(r["saida"]["o"])
        self.assertEqual(r["saida"]["t"], "")

    def test_cs_last_invalido_nao_quebra(self):
        r = self.rodar("__fim(document.getElementById('continuar').hidden)", semear(cs_last="{x"))
        self.assertEqual(r["erros"], [])
        self.assertTrue(r["saida"])

    def test_agrupar_por_nivel(self):
        r = self.rodar("document.querySelector('[data-grupo=\"nivel\"]').click();"
                       "__fim({h:[...document.querySelectorAll('#grupos .grupo:not([hidden]) .grupo-cab h2')].map(e=>e.textContent),"
                       "p:document.querySelector('[data-grupo=\"nivel\"]').getAttribute('aria-pressed'),"
                       "n:document.querySelectorAll('#grupos .mc').length})")
        self.assertEqual(r["erros"], [])
        presentes = {d["nivel"] for d in ESTUDOS_DADOS.values()}
        self.assertEqual(r["saida"]["h"], [v for k, v in NIVEIS.items() if k in presentes])
        self.assertEqual(r["saida"]["p"], "true")
        self.assertEqual(r["saida"]["n"], len(ESTUDOS_DADOS))

    def test_grupo_mostra_concluidos(self):
        antes = semear(**{f"cs_done_{SLUG}": "true"})
        r = self.rodar(f"__fim(document.querySelector('{CARD}').closest('.grupo').querySelector('.grupo-cab .p').textContent)", antes)
        self.assertRegex(r["saida"], r"^1 de \d+ concluídos$")

    def _grupos(self, modo, extra=""):
        r = self.rodar(f"document.querySelector('[data-grupo=\"{modo}\"]').click();{extra}"
                       "const g={};document.querySelectorAll('#grupos .grupo').forEach(x=>{"
                       "g[x.querySelector('h2').textContent]=[...x.querySelectorAll('.mc')].map(c=>c.dataset.slug)});"
                       "__fim({g,ids:[...document.querySelectorAll('[id]')].map(e=>e.id).filter((v,i,a)=>a.indexOf(v)!==i),"
                       "ordem:[...document.querySelectorAll('#grupos .grupo-cab h2')].map(e=>e.textContent),"
                       "contagem:document.getElementById('contagem').textContent,"
                       "links:[...document.querySelectorAll('#grupos .mc')].every(c=>c.getAttribute('href')||c.classList.contains('pendente'))})")
        self.assertEqual(r["erros"], [])
        return r["saida"]

    def test_agrupar_por_perfil_repete_modulo_em_cada_perfil(self):
        out = self._grupos("perfil")
        self.assertEqual(out["ids"], [])
        self.assertTrue(out["links"])
        self.assertEqual(out["contagem"], f"{len(ESTUDOS_DADOS)} módulos")
        multi = next(sl for sl, d in ESTUDOS_DADOS.items()
                     if len(d["carreiras"]) > 1 and d["carreiras"][0] != d["carreiras"][1])
        for nome in ESTUDOS_DADOS[multi]["carreiras"]:
            self.assertIn(multi, out["g"][nome])
        for nome in {c for d in ESTUDOS_DADOS.values() for c in d["carreiras"]}:
            esperado = [sl for sl, d in ESTUDOS_DADOS.items() if nome in d["carreiras"]]
            self.assertEqual(sorted(out["g"][nome]), sorted(esperado), nome)
        self.assertIn("Analista de Segurança da Informação", out["g"])

    def test_perfil_segue_ordem_de_carreiras(self):
        out = self._grupos("perfil")
        nomes = [v["nome"] for v in CARREIRAS.values()]
        esperado = [n for n in nomes if n in out["ordem"]]
        self.assertEqual(out["ordem"], esperado)

    def test_nist_repete_modulo_protect_detect(self):
        out = self._grupos("nist")
        self.assertEqual(out["ids"], [])
        alvos = [sl for sl, d in ESTUDOS_DADOS.items() if d["nist"] == "Protect / Detect"]
        self.assertTrue(alvos)
        for sl in alvos:
            self.assertIn(sl, out["g"]["Protect"])
            self.assertIn(sl, out["g"]["Detect"])

    def test_perfil_busca_e_pendentes_afetam_todas_as_copias(self):
        multi = next(sl for sl, d in ESTUDOS_DADOS.items() if len(d["carreiras"]) > 1)
        antes = semear(**{f"cs_done_{multi}": "true"})
        r = self.rodar("document.querySelector('[data-grupo=\"perfil\"]').click();"
                       "const cb=document.getElementById('so-pendentes');cb.checked=true;cb.dispatchEvent(new Event('change',{bubbles:true}));"
                       f"const c=[...document.querySelectorAll('.mc[data-slug=\"{multi}\"]')];"
                       "__fim({n:c.length,ocultas:c.every(x=>x.hidden),contagem:document.getElementById('contagem').textContent,"
                       "gp:document.querySelector('[data-gp=\"concluidos\"]').textContent})", antes)
        self.assertEqual(r["erros"], [])
        self.assertGreater(r["saida"]["n"], 1)
        self.assertTrue(r["saida"]["ocultas"])
        self.assertEqual(r["saida"]["contagem"], f"{len(ESTUDOS_DADOS) - 1} módulos")
        self.assertEqual(r["saida"]["gp"], "1")

    def test_entradas_hostis_nao_quebram(self):
        antes = ("localStorage.setItem('cs_last',JSON.stringify({slug:'a\\nb',secao:'x',ts:1}));"
                 "history.replaceState(null,'','#v-a\\\\')")
        r = self.rodar(f"__fim(document.querySelector('{CARD} .mc-status').textContent)", antes)
        self.assertEqual(r["erros"], [])
        self.assertIn("Não iniciado", r["saida"])

    def test_so_pendentes(self):
        antes = semear(**{f"cs_done_{SLUG}": "true"})
        r = self.rodar(f"const c=document.querySelector('{CARD}');const antes=!c.hidden;"
                       "const cb=document.getElementById('so-pendentes');cb.checked=true;cb.dispatchEvent(new Event('change',{bubbles:true}));"
                       "__fim({antes,depois:!c.hidden,contagem:document.getElementById('contagem').textContent})", antes)
        self.assertEqual(r["erros"], [])
        self.assertTrue(r["saida"]["antes"])
        self.assertFalse(r["saida"]["depois"])
        self.assertIn(str(len(ESTUDOS_DADOS) - 1), r["saida"]["contagem"])

    def test_busca(self):
        r = self.rodar("const i=document.getElementById('busca');i.value='kubernetes';i.dispatchEvent(new Event('input',{bubbles:true}));"
                       "const vis=[...document.querySelectorAll('.mc')].filter(c=>!c.hidden);"
                       "__fim({n:vis.length,ok:vis.every(c=>c.dataset.busca.includes('kubernetes'))})")
        self.assertEqual(r["erros"], [])
        self.assertGreater(r["saida"]["n"], 0)
        self.assertTrue(r["saida"]["ok"])

    def test_atalho_barra_foca_busca(self):
        r = self.rodar("document.dispatchEvent(new KeyboardEvent('keydown',{key:'/',bubbles:true}));"
                       "__fim(document.activeElement.id)")
        self.assertEqual(r["saida"], "busca")

    def test_trocar_visao_e_hash(self):
        r = self.rodar("document.querySelector('a[data-view=\"rotas\"]').click();"
                       "__fim({v:[...document.querySelectorAll('section.view')].filter(s=>!s.hidden).map(s=>s.dataset.view),"
                       "h:location.hash,cur:document.querySelector('[aria-current=\"page\"]').dataset.view})")
        self.assertEqual(r["erros"], [])
        self.assertEqual(r["saida"], {"v": ["rotas"], "h": "#v-rotas", "cur": "rotas"})

    def test_voltar_ao_catalogo_ao_limpar_o_hash(self):
        r = self.rodar("document.querySelector('a[data-view=\"rotas\"]').click();"
                       "const vis=()=>[...document.querySelectorAll('section.view')].filter(s=>!s.hidden).map(s=>s.dataset.view);"
                       "const antes=vis();location.hash='';"
                       "setTimeout(()=>{const a=vis();location.hash='#estudo-x';"
                       "setTimeout(()=>__fim({antes,depois:a,outro:vis()}),200)},200)")
        self.assertEqual(r["erros"], [])
        self.assertEqual(r["saida"], {"antes": ["rotas"], "depois": ["catalogo"], "outro": ["catalogo"]})

    def test_todos_concluidos_com_so_pendentes_explica_e_limpar_desmarca(self):
        antes = semear(**{f"cs_done_{s}": "true" for s in ESTUDOS_DADOS})
        r = self.rodar("const cb=document.getElementById('so-pendentes');cb.checked=true;cb.dispatchEvent(new Event('change',{bubbles:true}));"
                       "const vazio=document.querySelector('.vazio, #vazio, [data-vazio]');"
                       "const msg=document.body.innerText;"
                       "const btn=[...document.querySelectorAll('button')].find(b=>/Limpar/.test(b.textContent)&&b.offsetParent);"
                       "const ok1=/Todos os módulos deste filtro estão concluídos/.test(msg);"
                       "const ruim=/Nenhum módulo encontrado com essa busca/.test(msg);"
                       "btn.click();"
                       "__fim({ok1,ruim,marcado:cb.checked,n:[...document.querySelectorAll('.mc')].filter(c=>!c.hidden).length})", antes)
        self.assertEqual(r["erros"], [])
        self.assertEqual(r["saida"]["ok1"], True)
        self.assertEqual(r["saida"]["ruim"], False)
        self.assertEqual(r["saida"]["marcado"], False)
        self.assertEqual(r["saida"]["n"], len(ESTUDOS_DADOS))

    def test_visao_restaurada_do_hash(self):
        r = executar(self.portal, "__fim([...document.querySelectorAll('section.view')].filter(s=>!s.hidden).map(s=>s.dataset.view))",
                     script_antes="history.replaceState(null,'','#v-progresso')")
        self.assertEqual(r["saida"], ["progresso"])

    def test_gaveta_do_menu_no_celular(self):
        r = self.rodar("const b=document.querySelector('.menu-toggle');b.click();"
                       "const aberta={c:document.body.classList.contains('menu-aberto'),a:b.getAttribute('aria-expanded')};"
                       "document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}));"
                       "__fim({aberta,fechada:{c:document.body.classList.contains('menu-aberto'),a:b.getAttribute('aria-expanded')},"
                       "foco:document.activeElement===b})", largura=400)
        self.assertEqual(r["erros"], [])
        self.assertEqual(r["saida"]["aberta"], {"c": True, "a": "true"})
        self.assertEqual(r["saida"]["fechada"], {"c": False, "a": "false"})
        self.assertTrue(r["saida"]["foco"])

    def test_gaveta_fecha_ao_escolher_visao_e_clicar_fora(self):
        r = self.rodar("const b=document.querySelector('.menu-toggle');b.click();"
                       "document.querySelector('a[data-view=\"vaga\"]').click();"
                       "const a={c:document.body.classList.contains('menu-aberto'),f:document.activeElement===b};"
                       "b.click();document.body.click();"
                       "__fim({a,fora:document.body.classList.contains('menu-aberto'),foco:document.activeElement===b})", largura=400)
        self.assertEqual(r["saida"]["a"], {"c": False, "f": True})
        self.assertFalse(r["saida"]["fora"])
        self.assertTrue(r["saida"]["foco"])

    def test_marcar_em_meu_progresso(self):
        r = self.rodar("document.querySelector('a[data-view=\"progresso\"]').click();"
                       f"const cb=document.querySelector('#progresso-lista input[data-slug=\"{SLUG}\"]');cb.click();"
                       f"__fim({{ls:localStorage.getItem('cs_done_{SLUG}'),st:document.querySelector('{CARD} .mc-status').textContent,"
                       "gp:document.querySelector('[data-gp=\"concluidos\"]').textContent,"
                       "txt:document.getElementById('progresso-texto').textContent})")
        self.assertEqual(r["erros"], [])
        self.assertEqual(r["saida"]["ls"], "true")
        self.assertIn("Concluído", r["saida"]["st"])
        self.assertEqual(r["saida"]["gp"], "1")
        self.assertTrue(r["saida"]["txt"].startswith("1 de "))
        r = self.rodar("document.querySelector('a[data-view=\"progresso\"]').click();"
                       f"const cb=document.querySelector('#progresso-lista input[data-slug=\"{SLUG}\"]');"
                       f"const antes=cb.checked;cb.click();__fim({{antes,ls:localStorage.getItem('cs_done_{SLUG}')}})",
                       semear(**{f"cs_done_{SLUG}": "true"}))
        self.assertEqual(r["saida"], {"antes": True, "ls": None})

    def test_progresso_global_em_andamento(self):
        antes = semear(**{f"cs_done_{SLUG}": "true", "cs_read_Segmentacao-e-Firewall": json.dumps(["x"])})
        r = self.rodar("__fim({c:document.querySelector('[data-gp=\"concluidos\"]').textContent,"
                       "a:document.querySelector('[data-gp=\"andamento\"]').textContent})", antes)
        self.assertEqual(r["saida"]["c"], "1")
        self.assertEqual(r["saida"]["a"], "1")

    def test_rotas_marcam_feito_e_proximo(self):
        antes = semear(**{f"cs_done_{SLUG}": "true"})
        r = self.rodar("const li=[...document.querySelectorAll('.rota-sugerida .rota-passo')];"
                       f"const f=li.filter(l=>l.classList.contains('feito')&&l.dataset.slug==='{SLUG}');"
                       "const p=document.querySelector('.rota-sugerida li.proximo');"
                       "const bloco=f.length?f[0].closest('.rota-sugerida'):null;"
                       "__fim({nf:f.length,prox:!!p,txt:bloco?bloco.querySelector('.rota-progresso-texto').textContent:'',"
                       "pp:bloco?bloco.querySelector('.rota-proximo').textContent:''})", antes)
        self.assertEqual(r["erros"], [])
        self.assertGreater(r["saida"]["nf"], 0)
        self.assertTrue(r["saida"]["prox"])
        self.assertRegex(r["saida"]["txt"], r"^1 de \d+ concluídos \(\d+%\)$")
        self.assertTrue(r["saida"]["pp"].startswith("Próximo módulo: "))

    def test_certificacoes_tambem(self):
        antes = semear(**{f"cs_done_{CERTIFICACOES[0]['modulos'][0]}": "true"})
        r = self.rodar("__fim(document.querySelectorAll('#secao-cert-painel li.feito').length)", antes)
        self.assertGreater(r["saida"], 0)

    def test_zerar_progresso_sem_dialogo_e_preserva_tema(self):
        antes = semear(**{f"cs_done_{SLUG}": "true", f"cs_read_{SLUG}": "[]", f"cs_check_{SLUG}_a": "true",
                          f"cs_quiz_{SLUG}_q": "errei", "cs_last": "{}", "cs_theme": "dark"})
        r = self.rodar("window.confirm=function(){window.__erros.push('confirm');return true};"
                       "window.alert=function(){window.__erros.push('alert')};"
                       "const b=document.getElementById('zerar-progresso');b.click();"
                       "const meio=Object.keys(localStorage).length;b.click();"
                       "__fim({meio,resto:Object.keys(localStorage).sort(),"
                       "st:document.querySelector('" + CARD + " .mc-status').textContent})", antes)
        self.assertEqual(r["erros"], [])
        self.assertEqual(r["saida"]["meio"], 6)
        self.assertEqual(r["saida"]["resto"], ["cs_theme"])
        self.assertIn("Não iniciado", r["saida"]["st"])

    def test_sem_localstorage_nao_quebra(self):
        antes = ("Object.defineProperty(window,'localStorage',{get:function(){throw new Error('bloqueado')}})")
        r = self.rodar("__fim(document.querySelector('" + CARD + " .mc-status').textContent)", antes)
        self.assertEqual([e for e in r["erros"] if "bloqueado" in e and "[CS]" not in e], [])
        self.assertIn("Não iniciado", r["saida"])


if __name__ == "__main__":
    unittest.main()
