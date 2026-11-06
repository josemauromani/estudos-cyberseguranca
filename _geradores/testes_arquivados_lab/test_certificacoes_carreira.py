"""
test_certificacoes_carreira.py
Testes automatizados para o Estudo 33: Certificacoes-e-Carreira
"""
import json
import re
import sys
import unittest
from pathlib import Path
from urllib.parse import urlparse
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from index_dados import CERTIFICACOES, ESTUDOS_DADOS
GERADORES = Path(__file__).resolve().parent.parent
DOMINIO_OFICIAL = {'CEH': 'eccouncil.org', 'CISM': 'isaca.org', 'CISA': 'isaca.org', 'CRISC': 'isaca.org', 'CDPSE': 'isaca.org', 'CGEIT': 'isaca.org', 'CISSP': 'isc2.org', 'CCSP': 'isc2.org', 'GSEC': 'giac.org', 'Security+': 'comptia.org', 'ISFS': 'exin.com', 'PDPF/PDPP': 'exin.com', 'ITIL 4 F': 'peoplecert.org', 'CSFPC': 'certiprof.com', 'ISO 27001 LA': 'pecb.com', 'eJPT': 'ine.com', 'eCPPT': 'ine.com', 'OSCP': 'offsec.com'}
CAMPOS_PERFIL = ('anos_ti', 'anos_si', 'anos_gestao_si', 'anos_nuvem')

def catalogo():
    """slug -> número do módulo, na ordem de _geradores/estudos.txt."""
    numeros = {}
    for linha in (GERADORES / 'estudos.txt').read_text(encoding='utf-8').splitlines():
        if linha.strip() and (not linha.startswith('#')):
            numeros[linha.split('|')[0]] = len(numeros) + 1
    return numeros

def efetivo(perfil):
    """Gestão de segurança conta como segurança; segurança e nuvem contam como TI."""
    p = dict(perfil)
    p['anos_si'] = max(p.get('anos_si', 0), p.get('anos_gestao_si', 0))
    p['anos_ti'] = max(p.get('anos_ti', 0), p['anos_si'], p.get('anos_nuvem', 0))
    return p

def elegibilidade(cert, perfil):
    """Regra espelhada no JavaScript: 'conferir', 'sem-exigencia', 'elegivel' ou 'pendente'."""
    perfil = efetivo(perfil)
    req = cert['requisitos']
    if req.get('conferir'):
        return 'conferir'
    if not req:
        return 'sem-exigencia'
    if req.get('alternativa') and perfil.get('treinamento_oficial'):
        return 'elegivel'
    for campo in CAMPOS_PERFIL:
        if campo in req:
            minimo = req[campo]
            if campo == 'anos_si' and perfil.get('graduacao'):
                minimo -= req.get('desconto_graduacao', 0)
            if perfil.get(campo, 0) < minimo:
                return 'pendente'
    return 'elegivel'

class TestCertificacoesCarreira(unittest.TestCase):
    """Valida a estrutura, o conteúdo, a coerência com o portal e a compilação do estudo Certificacoes-e-Carreira."""

    def setUp(self):
        self.root = GERADORES.parent
        self.body_path = GERADORES / 'certificacoes_e_carreira_body.html'
        self.compiled_path = self.root / 'Certificacoes-e-Carreira' / 'treinamento-certificacoes-e-carreira.html'
        self.portal_path = self.root / 'index.html'

    def _cert(self, d, sigla):
        return next((c for c in d['certificacoes'] if c['sigla'] == sigla))

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        termos = ['Ciência da Computação', 'Sistemas de Informação', 'tecnólogo', 'lato sensu', 'stricto sensu', '360 horas', 'CEH', 'EC-Council', 'CISM', 'ISACA', 'CISSP', 'ISC2', 'CCSP', 'GSEC', 'GIAC', 'Security+', 'CompTIA', 'SY0-701', 'Associate of ISC2', 'CPE', 'ISO/IEC 17024', 'NICE Framework', 'NIST SP 800-181', 'Work Role', 'TKS']
        for termo in termos:
            self.assertIn(termo, content, f'Termo obrigatório ausente: {termo}')

    def test_fontes_no_cartao(self):
        body = self.body_path.read_text(encoding='utf-8')
        m = re.search('function cartaoCert\\(c\\) \\{(.*?)\\n    \\}\\n', body, re.S)
        self.assertIsNotNone(m)
        corpo = m.group(1)
        for trecho in ('Fontes oficiais: ', '/^https:\\/\\//.test(', 'noopener noreferrer', 'overflow-wrap: anywhere'):
            self.assertIn(trecho, corpo)
        self.assertNotIn('innerHTML', corpo)
        self.assertIn('Fontes conferidas em ', body)
        self.assertIn('CERT.conferido_em', body)

    def test_fatos_lista_sites_oficiais(self):
        body = self.body_path.read_text(encoding='utf-8')
        ini = body.index('id="fatos"')
        fatos = body[ini:body.index('</section>', ini)]
        for c in CERTIFICACOES:
            with self.subTest(cert=c['sigla']):
                self.assertIn(c['site_oficial'], fatos)

    def test_ajustes_da_revisao_final(self):
        cert = self.body_path.read_text(encoding='utf-8')
        self.assertIn('CEH Practical', cert)
        self.assertIn('https://www.comptia.org/en-us/blog/introducing-comptia-securityx/', cert)
        for errado in ('site oficial do ISACA', 'site oficial do ISC2', 'site oficial do CompTIA'):
            self.assertNotIn(errado, cert)
        pent = (GERADORES / 'pentest_metodologias_body.html').read_text(encoding='utf-8')
        for url in ('https://www.offsec.com/products/oscp-plus/', 'https://www.offsec.com/blog/oscp-grading-update/'):
            self.assertIn(url, pent)
        self.assertIn('CEH Practical', pent)
        self.assertNotIn('Consulte o site da INE</td>', pent)

    def _secao(self, body, sid):
        m = re.search('<section class="study-section" id="%s".*?</section>' % sid, body, re.S)
        self.assertIsNotNone(m, f'Seção {sid} ausente')
        return m.group(0)

    def test_trajetorias_conteudo(self):
        sec = self._secao(self.body_path.read_text(encoding='utf-8'), 'trajetorias')
        for termo in ('suporte', 'CISO', 'MBA', 'Foundation', 'EXIN', 'CertiProf', 'CQI/IRCA', 'exemplo', 'GRC', 'Privacidade', 'Auditoria', 'Técnico', 'por onde começar', 'oito perfis', 'Pentest', 'eJPT', 'eCPPT', 'OSCP', 'eCTHP', 'SecurityX', 'CASP+', 'CTF'):
            self.assertIn(termo.lower(), sec.lower(), f'Termo ausente na seção trajetorias: {termo}')

    def test_trajetorias_lideranca_executiva(self):
        sec = self._secao(self.body_path.read_text(encoding='utf-8'), 'trajetorias')
        for termo in ('Liderança executiva', 'auditor', 'DPO', 'arquiteto', 'CTO', 'IAM', 'mesma empresa', 'comunidade', 'CISSP', 'setor financeiro', 'Estudo 59', 'Estudo 60', 'só 1 dos 5', 'ilustra'):
            self.assertIn(termo.lower(), sec.lower(), f'Termo ausente: {termo}')
        linhas = [l for l in re.findall('<tr>.*?</tr>', sec, re.S) if 'Liderança / CISO' in l]
        self.assertEqual(len(linhas), 1, 'Linha Liderança / CISO ausente na tabela')
        for termo in ('CISM', 'CRISC', 'CISSP', 'Estudo 25', 'Estudo 26', 'Estudo 58', 'Estudo 59', 'Estudo 60'):
            self.assertIn(termo, linhas[0])

    def test_trajetorias_linha_pentest(self):
        sec = self._secao(self.body_path.read_text(encoding='utf-8'), 'trajetorias')
        self.assertNotIn('dois perfis', sec.lower())
        linhas = [l for l in re.findall('<tr>.*?</tr>', sec, re.S) if re.match('<tr>\\s*<td>[^<]*(<strong>)?[^<]*Pentest', l)]
        self.assertEqual(len(linhas), 1, 'Linha Pentest ausente na tabela')
        for termo in ('eJPT', 'eCPPT', 'OSCP', '14 (Pentest'):
            self.assertIn(termo, linhas[0])
        self.assertIn('dezembro de 2024', sec)

    def test_checklist_e_quiz_33(self):
        body = self.body_path.read_text(encoding='utf-8')
        self.assertEqual(body.count('class="checklist-item"'), 8)
        self.assertGreaterEqual(body.count('class="quiz-item"'), 9)
        quiz = self._secao(body, 'quiz')
        self.assertIn('Questão 8', quiz)
        self.assertIn('Questão 9', quiz)
        self.assertIn('prática', quiz.lower())

    def test_fatos_cita_securityx_e_ecthp(self):
        fatos = self._secao(self.body_path.read_text(encoding='utf-8'), 'fatos')
        self.assertIn('https://www.comptia.org/en-us/certifications/securityx/', fatos)
        self.assertIn('https://ine.com/security/certifications/ecthp-certification', fatos)

    def test_trajetorias_sem_dados_pessoais(self):
        body = self.body_path.read_text(encoding='utf-8')
        self.assertNotIn('linkedin.com/in/', body)
        self.assertNotIn('lattes.cnpq.br', body)
        self.assertNotIn('%', self._secao(body, 'trajetorias'))
        for marca in ('F63', 'A93', 'primeiro programa'):
            self.assertNotIn(marca.lower(), body.lower())

    def test_textos_de_vitrine_citam_as_certificacoes_novas(self):
        """Subtítulo do módulo 33, README e CURRICULO não podem ficar presos às seis certificações originais."""
        subtitulo = ESTUDOS_DADOS['Certificacoes-e-Carreira']['subtitulo']
        readme = (GERADORES.parent / 'README.md').read_text(encoding='utf-8')
        curriculo = (GERADORES / 'CURRICULO.md').read_text(encoding='utf-8')
        for sigla in ('CISA', 'ISFS', 'OSCP'):
            self.assertIn(sigla, subtitulo, f'Subtítulo do módulo 33 sem {sigla}')
            self.assertIn(sigla, readme, f'README sem {sigla}')
            self.assertIn(sigla, curriculo, f'CURRICULO sem {sigla}')

    def test_sem_texto_de_doze(self):
        arquivos = list(GERADORES.glob('*_body.html')) + [GERADORES.parent / 'README.md', GERADORES / 'CURRICULO.md', GERADORES / 'index_dados.py']
        for a in arquivos:
            self.assertNotIn('12 certificações', a.read_text(encoding='utf-8'), a.name)

    def test_sem_texto_de_quinze(self):
        arquivos = list(GERADORES.glob('*_body.html')) + [GERADORES.parent / 'README.md', GERADORES / 'CURRICULO.md', GERADORES / 'index_dados.py']
        for a in arquivos:
            self.assertNotIn('15 certificações', a.read_text(encoding='utf-8'), a.name)

    def test_tabela_certificacoes_da_secao(self):
        sec = self._secao(self.body_path.read_text(encoding='utf-8'), 'certificacoes')
        tabela = re.search('<table.*?</table>', sec, re.S).group(0)
        for c in CERTIFICACOES:
            self.assertIn(f'<strong>{c['sigla']}</strong>', tabela, f'Sigla ausente na tabela: {c['sigla']}')
        self.assertEqual(len(CERTIFICACOES), 18)

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn('Certificacoes-e-Carreira/treinamento-certificacoes-e-carreira.html', content)
        self.assertIn('data-slug="Certificacoes-e-Carreira"', content)
        self.assertIn(f'/ {len(ESTUDOS_DADOS)}', content)
if __name__ == '__main__':
    unittest.main()
