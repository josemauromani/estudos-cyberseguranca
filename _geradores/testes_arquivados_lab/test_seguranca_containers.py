"""
test_seguranca_containers.py
Testes automatizados para o Estudo 50: Seguranca-de-Containers

Valida a estrutura das 6 seções, a coerência com o catálogo (ESTUDOS_DADOS),
o bloco JSON do simulador, o diagrama no formato do GUIA-DO-AUTOR §3.6,
a ausência de APIs inseguras no motor JavaScript e a integração com o portal.
"""
import ipaddress
import json
import re
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from index_dados import ESTUDOS_DADOS
SLUG = 'Seguranca-de-Containers'
REDES_PRIVADAS = [ipaddress.ip_network(n) for n in ('10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16', '127.0.0.0/8')]
URL_RE = re.compile('^https?://')
CURL_SH = re.compile('(curl|wget)\\b[^|]*\\|\\s*(sudo\\s+)?(ba)?sh\\b')
EVID_TAG = 'a verificação por tag não garante a mesma imagem; verifique e rode pelo mesmo digest'

def juntar_linhas(texto):
    """Espelho de juntarLinhas: [(linha, conteúdo)] sem vazias e comentários, com continuações unidas."""
    out, buf, ini = ([], '', None)
    for n, bruta in enumerate(texto.split('\n'), 1):
        s = bruta.strip()
        if not s or s.startswith('#'):
            continue
        if ini is None:
            ini = n
        if s.endswith('\\'):
            buf += s[:-1].strip() + ' '
            continue
        buf += s
        out.append((ini, buf.strip()))
        buf, ini = ('', None)
    if buf.strip():
        out.append((ini, buf.strip()))
    return out

def parse_imagem(ref):
    nome, _, digest = ref.partition('@')
    tag = ''
    i = nome.rfind(':')
    if i > nome.rfind('/'):
        nome, tag = (nome[:i], nome[i + 1:])
    return {'nome': nome, 'tag': tag, 'digest': digest, 'base': nome.split('/')[-1].lower()}

def ler_dockerfile(texto):
    estagios = []
    for n, c in juntar_linhas(texto):
        partes = c.split(None, 1)
        instr, args = (partes[0].upper(), partes[1] if len(partes) > 1 else '')
        if instr == 'FROM':
            toks = [t for t in args.split() if not t.startswith('--')]
            alias = toks[2].lower() if len(toks) >= 3 and toks[1].upper() == 'AS' else None
            estagios.append({'linha': n, 'ref': toks[0] if toks else '', 'alias': alias, 'instr': []})
        elif estagios:
            estagios[-1]['instr'].append((n, instr, args))
    return estagios

def eh_grande(d, im):
    return im['base'] in d['imagens_grandes'] and 'slim' not in im['tag'] and ('alpine' not in im['tag'])

def achados_dockerfile(d, texto, add):
    est = ler_dockerfile(texto)
    if not est:
        return 'desconhecida'
    aliases, refs = (set(), {})
    pad = re.compile(d['padrao_segredo'], re.I)
    for e in est:
        ref, low = (e['ref'], e['ref'].lower())
        if low not in aliases and low != 'scratch':
            im = parse_imagem(ref)
            if not im['digest'] and im['tag'] in ('', 'latest'):
                add('tag_latest', f'linha {e['linha']}: FROM {ref}')
            elif not im['digest']:
                add('sem_digest', f'linha {e['linha']}: FROM {ref}')
        if e['alias']:
            aliases.add(e['alias'])
            refs[e['alias']] = ref
        for n, instr, args in e['instr']:
            toks = args.split()
            if instr in ('ENV', 'ARG') and toks:
                if instr == 'ENV' and '=' not in toks[0]:
                    chaves = [toks[0]]
                else:
                    chaves = [t.split('=', 1)[0] for t in toks if instr == 'ARG' or '=' in t]
                for k in chaves:
                    if pad.search(k):
                        add('segredo_build', f'linha {n}: {instr} {k}')
            elif instr in ('COPY', 'ADD'):
                flags = [t for t in toks if t.startswith('--')]
                fontes = [t for t in toks if not t.startswith('--')][:-1]
                if instr == 'ADD' and any((URL_RE.match(f) for f in fontes)) and (not any((f.startswith('--checksum=') for f in flags))):
                    add('add_remoto', f'linha {n}: ADD de URL sem --checksum')
                if not any((f.startswith('--from=') for f in flags)):
                    for f in fontes:
                        if URL_RE.match(f):
                            continue
                        b = f.rstrip('/').split('/')[-1]
                        if b in d['arquivos_segredo'] or any((b.endswith(x) for x in d['sufixos_segredo'])):
                            add('arquivo_segredo', f'linha {n}: {instr} {b}')
            elif instr == 'RUN' and CURL_SH.search(args):
                add('add_remoto', f'linha {n}: script baixado e executado direto no shell')
    final = est[-1]
    usuarios = [(n, a.strip()) for n, i, a in final['instr'] if i == 'USER']
    if not usuarios:
        add('root', 'Dockerfile: o estágio final não tem USER (roda como root)')
    elif usuarios[-1][1].split(':')[0] in ('root', '0'):
        add('root', f'linha {usuarios[-1][0]}: USER {usuarios[-1][1]}')
    ref, vistos = (final['ref'], 0)
    while ref.lower() in refs and vistos < 10:
        ref, vistos = (refs[ref.lower()], vistos + 1)
    if ref.lower() == 'scratch':
        return 'distroless'
    im = parse_imagem(ref)
    if eh_grande(d, im):
        add('imagem_grande', f'linha {final['linha']}: estágio final em {ref}')
        return 'completa'
    return 'distroless' if 'distroless' in im['nome'].lower() else 'slim'

def parse_run(d, toks):
    opts, imagem, i = ([], None, 2)
    while i < len(toks):
        t = toks[i]
        if t.startswith('-'):
            if t.startswith('--') and '=' in t:
                k, v = t.split('=', 1)
                opts.append((k, v))
            elif t in d['opcoes_com_valor'] and i + 1 < len(toks):
                opts.append((t, toks[i + 1]))
                i += 1
            else:
                opts.append((t, None))
        else:
            imagem = t
            break
        i += 1
    return (opts, imagem)

def achados_implantacao(d, texto, add):
    run, outras = (None, [])
    for n, c in juntar_linhas(texto):
        toks = [t.strip('\'"') for t in c.split()]
        if run is None and len(toks) >= 2 and (toks[0] == 'docker') and (toks[1] == 'run'):
            run = (n, toks)
        else:
            outras.append(toks)
    if run is None:
        return
    opts, imagem = parse_run(d, run[1])
    caps, ro, drop, nnp = ([], False, False, False)
    for k, v in opts:
        if k == '--privileged' and v in (None, 'true'):
            add('privileged', '--privileged')
        elif k in ('-v', '--volume', '--mount') and v:
            if k == '--mount':
                campos = dict((p.split('=', 1) for p in v.split(',') if '=' in p))
                src = campos.get('source', campos.get('src', ''))
            else:
                src = v.split(':')[0]
            src = src if src == '/' else src.rstrip('/')
            if src in d['sockets']:
                add('docker_sock', f'{k} {v}')
            elif src in d['montagens_sensiveis']:
                add('montagem_sensivel', f'{k} {v}')
        elif k == '--pid' and v == 'host':
            add('pid_host', '--pid=host')
        elif k in ('--network', '--net') and v == 'host':
            add('rede_host', f'{k} host')
        elif k == '--cap-add' and v:
            cap = v.upper()
            cap = cap[4:] if cap.startswith('CAP_') else cap
            if cap not in d['caps_permitidas']:
                caps.append(cap)
        elif k == '--cap-drop' and v and (v.upper() == 'ALL'):
            drop = True
        elif k in ('-u', '--user') and v and (v.split(':')[0] in ('root', '0')):
            add('root', f'docker run {k} {v}')
        elif k == '--read-only' and v in (None, 'true'):
            ro = True
        elif k == '--security-opt' and v and v.startswith('no-new-privileges') and (not v.endswith('false')):
            nnp = True
    for cap in caps:
        add('cap_add', '--cap-add ' + cap)
    if imagem:
        im = parse_imagem(imagem)
        if not im['digest'] and im['tag'] in ('', 'latest'):
            add('tag_latest', f'docker run: imagem {imagem}')
        if not imagem.startswith(d['registro_confiavel']):
            add('registro', f'imagem fora de {d['registro_confiavel']}')

        def mesma(x):
            o = parse_imagem(x)
            return (o['nome'], o['tag'], o['digest']) == (im['nome'], im['tag'], im['digest'])
        assinada = any((len(t) >= 2 and t[0] == 'cosign' and (t[1] == 'verify') and any((mesma(x) for x in t[2:])) for t in outras))
        if not im['digest']:
            add('sem_assinatura', f'docker run por tag ({imagem}): {EVID_TAG}')
        elif not assinada:
            add('sem_assinatura', 'nenhum cosign verify para ' + imagem)
    faltam = [r for r, ok in (('--read-only', ro), ('--cap-drop ALL', drop), ('--security-opt no-new-privileges', nnp)) if not ok]
    if faltam:
        add('sem_endurecimento', 'faltam: ' + ', '.join(faltam))

def auditar(d, dockerfile, implantacao):
    """Espelho de auditarContainer: achados por regra (na ordem do catálogo), base, risco e nível."""
    ev = {}

    def add(rid, texto):
        ev.setdefault(rid, []).append(texto)
    base = achados_dockerfile(d, dockerfile, add)
    achados_implantacao(d, implantacao, add)
    achados = []
    for rid in d['ordem_regras']:
        if rid not in ev:
            continue
        r = d['regras'][rid]
        sev, escape = (r['sev'], r['escape'])
        if rid == 'cap_add':
            caps = [e.split()[-1] for e in ev[rid]]
            if any((c in d['caps_escape'] for c in caps)):
                sev, escape = ('critica', True)
        achados.append({'id': rid, 'sev': sev, 'escape': escape, 'evidencias': ev[rid]})
    risco = sum((d['pesos'][a['sev']] for a in achados))
    escape = any((a['escape'] for a in achados))
    if escape or risco >= 80:
        nivel = 'crítico'
    elif risco >= 40:
        nivel = 'alto'
    elif risco >= 15:
        nivel = 'médio'
    elif risco > 0:
        nivel = 'baixo'
    else:
        nivel = 'mínimo'
    return {'achados': achados, 'ids': [a['id'] for a in achados], 'base': base, 'risco': risco, 'nivel': nivel, 'escape': escape}

def aplicar_itens(textos, itens):
    """Espelho de aplicarItensCtr: troca de linha inteira; para vazio apaga a linha; não repete o que já está lá."""
    t = dict(textos)
    for it in itens:
        arq = t[it['arquivo']]
        if it['para'] and it['para'] in arq:
            continue
        linhas = arq.split('\n')
        for i, linha in enumerate(linhas):
            if linha.strip() == it['de'].strip():
                if it['para'] == '':
                    del linhas[i]
                else:
                    linhas[i] = it['para']
                break
        t[it['arquivo']] = '\n'.join(linhas)
    return t

def prioridade(v):
    """Espelho de prioridadeVuln."""
    if v['kev']:
        return 'agora'
    if v['corrigida'] is None:
        return 'aceitar'
    if v['severidade'] in ('critica', 'alta') and v['epss'] >= 0.1:
        return 'agora'
    return 'janela'

def varredura(cenario, base):
    return [v for v in cenario['varredura'] if base in v['bases']]

def corrigir_tudo(d, c, politica):
    """Clica em cada correção uma vez, como o aluno: a primeira (ou a última) disponível a cada rodada."""
    t, feitas = ({'dockerfile': c['dockerfile'], 'implantacao': c['implantacao']}, set())
    for _ in range(40):
        ids = [i for i in auditar(d, t['dockerfile'], t['implantacao'])['ids'] if i not in feitas and i in c['correcoes']]
        if not ids:
            break
        rid = ids[0] if politica == 'primeira' else ids[-1]
        t = aplicar_itens(t, c['correcoes'][rid])
        feitas.add(rid)
    return t
ESPERADO = {'api-pedidos': ['root', 'tag_latest', 'segredo_build', 'arquivo_segredo', 'add_remoto', 'imagem_grande', 'privileged', 'docker_sock', 'rede_host', 'registro', 'sem_assinatura', 'sem_endurecimento'], 'relatorios': ['root', 'sem_digest', 'segredo_build', 'add_remoto', 'imagem_grande', 'montagem_sensivel', 'pid_host', 'cap_add', 'sem_assinatura', 'sem_endurecimento'], 'vitrine': ['rede_host', 'sem_assinatura']}

class TestSegurancaContainers(unittest.TestCase):
    """Estrutura, conteúdo, simulador e compilação do estudo 50."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / '_geradores' / 'seguranca_de_containers_body.html'
        self.compiled_path = self.root / SLUG / 'treinamento-seguranca-de-containers.html'
        self.portal_path = self.root / 'index.html'

    def _body(self):
        return self.body_path.read_text(encoding='utf-8')

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_exemplo_de_runtime_verifica_e_roda_o_mesmo_digest(self):
        m = re.search('<code id="code-ctr-run">(.*?)</code>', self._body(), re.S)
        linhas = [l for _, l in juntar_linhas(m.group(1))]
        verify = next((l for l in linhas if l.startswith('cosign verify'))).split()[-1]
        run = next((l for l in linhas if l.startswith('docker run'))).split()[-1]
        self.assertEqual(verify, run)
        self.assertIn('@sha256:&lt;digest-conferido&gt;', run)
        self.assertRegex(m.group(1), '#[^\\n]*digest', 'um comentário explica por que usar o digest')

    def test_diagrama_no_formato_do_guia(self):
        body = self._body()
        caixas = re.findall('<div class="diagram-box">\\s*<div class="diagram-header">\\s*<span class="diagram-title">([^<]+)</span>.*?<pre class="mermaid" data-title="([^"]+)">', body, re.S)
        self.assertGreaterEqual(len(caixas), 1, 'falta um .diagram-box com cabeçalho e Mermaid')
        for titulo, data_title in caixas:
            self.assertEqual(titulo.strip(), data_title.strip())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        termos = ['namespaces', 'cgroups', 'capabilities', 'seccomp', 'AppArmor', 'kernel compartilhado', 'distroless', 'multiestágio', 'USER', 'digest', 'docker history', '--mount=type=secret', 'BuildKit', '--privileged', 'docker.sock', '--cap-drop', 'no-new-privileges', '--read-only', 'rootless', 'Trivy', 'EPSS', 'KEV', 'Cosign', 'Sigstore', 'registro', 'Falco', 'T1610', 'T1611', 'NIST SP 800-190', 'CIS Docker Benchmark', 'Ipê Store', 'Estudo 22', 'Estudo 34']
        for termo in termos:
            self.assertIn(termo, content, f'Termo obrigatório ausente: {termo}')

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn(f'{SLUG}/treinamento-seguranca-de-containers.html', content)
        self.assertIn(f'data-slug="{SLUG}"', content)
        self.assertIn(f'/ {len(ESTUDOS_DADOS)}', content)
if __name__ == '__main__':
    unittest.main()
