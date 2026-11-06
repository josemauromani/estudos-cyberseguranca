"""Páginas compiladas em dia com o catálogo: 'Estudo NN de <total>' e anterior/próximo."""
import re
import sys
import unittest
from pathlib import Path
TESTES = Path(__file__).resolve().parent
GERADORES = TESTES.parent
sys.path.insert(0, str(GERADORES))
from html import escape
from chassi import info_modulo
from index_dados import ESTUDOS_DADOS
from montar import carregar_catalogo_estudos
RAIZ = GERADORES.parent

class TestCompiladosAtualizados(unittest.TestCase):

    def test_paginas_compiladas_refletem_total_e_vizinhos(self):
        desatualizadas = []
        catalogo = carregar_catalogo_estudos()
        for slug in ESTUDOS_DADOS:
            c = catalogo.get(slug)
            arq = RAIZ / c['pasta'] / c['arquivo_html'] if c else None
            if arq is None or not arq.exists():
                continue
            html = arq.read_text(encoding='utf-8')
            info = info_modulo(slug)
            rotulo = re.search('<div class="toc-rotulo">([^<]*)</div>', html)
            if not rotulo or f'de {len(ESTUDOS_DADOS)}' not in rotulo.group(1):
                desatualizadas.append(slug)
                continue
            for viz in (info.anterior, info.proximo):
                if viz and f'href="{escape(viz[2], quote=True)}"' not in html:
                    desatualizadas.append(slug)
                    break
        self.assertEqual(desatualizadas, [], 'rode ./_geradores/gerar.sh todos')
if __name__ == '__main__':
    unittest.main()
