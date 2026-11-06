"""
test_iot_ot.py
Testes automatizados para o Estudo 23: Seguranca-em-IoT-e-OT
"""
import json
import re
import struct
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from index_dados import ESTUDOS_DADOS
NIVEIS = ['0', '1', '2', '3', '3.5', '4', '5']
FUNCOES = {1: ('Read Coils', 'leitura'), 2: ('Read Discrete Inputs', 'leitura'), 3: ('Read Holding Registers', 'leitura'), 4: ('Read Input Registers', 'leitura'), 5: ('Write Single Coil', 'escrita'), 6: ('Write Single Register', 'escrita'), 15: ('Write Multiple Coils', 'escrita'), 16: ('Write Multiple Registers', 'escrita')}

def regra(n_origem, n_destino):
    """Devolve (decisao, regra) para um fluxo entre dois níveis Purdue, nos dois sentidos."""
    a, b = (float(n_origem), float(n_destino))
    ti = lambda x: x >= 4
    ot = lambda x: x <= 3
    if 5 in (a, b) and (not (a == 5 and b == 4 or (a == 4 and b == 5))):
        return ('bloquear', 'R4')
    if ti(a) and ot(b) or (ot(a) and ti(b)):
        return ('bloquear', 'R1')
    if 3.5 in (a, b) and a != b:
        outro = b if a == 3.5 else a
        return ('permitir', 'R3') if outro in (3, 4) else ('bloquear', 'R3')
    if ot(a) and ot(b):
        return ('permitir', 'R2') if abs(a - b) <= 1 else ('bloquear', 'R2')
    return ('permitir', 'R0')

def decodificar_modbus(hexa):
    """Espelho do decodificador Modbus TCP em JavaScript."""
    limpo = re.sub('[\\s:,-]', '', hexa)
    if not limpo or len(limpo) % 2 or (not re.fullmatch('[0-9A-Fa-f]+', limpo)):
        return {'erro': 'Hexadecimal inválido.'}
    b = bytes.fromhex(limpo)
    if len(b) < 8:
        return {'erro': 'Quadro curto demais: o cabeçalho MBAP tem 7 bytes, mais o código de função.'}
    tid, pid, tam = struct.unpack_from('>HHH', b, 0)
    unidade, fn = (b[6], b[7])
    r = {'transacao': tid, 'protocolo': pid, 'tamanho': tam, 'unidade': unidade, 'funcao': fn}
    if pid != 0:
        r['erro'] = 'Identificador de protocolo diferente de 0: não é Modbus.'
        return r
    if tam != len(b) - 6:
        r['erro'] = f'O campo de tamanho diz {tam}, mas há {len(b) - 6} bytes depois dele.'
        return r
    dados = b[8:]
    if fn & 128:
        r.update(nome='Exceção da função %d' % (fn & 127), tipo='excecao')
        if len(dados) != 1:
            r['erro'] = 'Resposta de exceção deve ter 1 byte de código.'
        else:
            r['detalhe'] = 'código de exceção %d' % dados[0]
        return r
    if fn not in FUNCOES:
        r['erro'] = 'Função %d não é tratada neste laboratório.' % fn
        return r
    r['nome'], r['tipo'] = FUNCOES[fn]
    try:
        if fn in (1, 2, 3, 4):
            ini, qtd = struct.unpack('>HH', dados)
            r['detalhe'] = f'endereço inicial {ini}, quantidade {qtd}'
        elif fn == 5:
            end, val = struct.unpack('>HH', dados)
            if val not in (65280, 0):
                r['erro'] = 'Valor de bobina deve ser FF00 (ligar) ou 0000 (desligar).'
                return r
            r['detalhe'] = f'bobina {end} → {('LIGAR' if val == 65280 else 'DESLIGAR')}'
        elif fn == 6:
            end, val = struct.unpack('>HH', dados)
            r['detalhe'] = f'registrador {end} ← {val}'
        else:
            ini, qtd, nbytes = struct.unpack_from('>HHB', dados, 0)
            valores = dados[5:]
            if nbytes != len(valores):
                r['erro'] = 'Contagem de bytes não confere.'
                return r
            if fn == 16:
                if nbytes != 2 * qtd:
                    r['erro'] = 'Contagem de bytes não confere com a quantidade de registradores.'
                    return r
                regs = [struct.unpack_from('>H', valores, 2 * i)[0] for i in range(qtd)]
                r['detalhe'] = f'registradores {ini} a {ini + qtd - 1} ← {regs}'
            else:
                if nbytes != (qtd + 7) // 8:
                    r['erro'] = 'Contagem de bytes não confere com a quantidade de bobinas.'
                    return r
                bits = [valores[i // 8] >> i % 8 & 1 for i in range(qtd)]
                r['detalhe'] = f'bobinas {ini} a {ini + qtd - 1} ← {bits}'
    except struct.error:
        r['erro'] = 'Dados da função com tamanho errado.'
    return r

class TestIotOt(unittest.TestCase):
    """Valida a estrutura, o conteúdo, o modelo Purdue, os fluxos, o Modbus e a compilação do estudo 23."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.body_path = self.root / '_geradores' / 'seguranca_em_iot_e_ot_body.html'
        self.compiled_path = self.root / 'Seguranca-em-IoT-e-OT' / 'treinamento-seguranca-em-iot-e-ot.html'
        self.portal_path = self.root / 'index.html'

    def test_body_and_compiled_files_exist(self):
        self.assertTrue(self.body_path.exists())
        self.assertTrue(self.compiled_path.exists())

    def test_teoria_e_conceitos_fundamentais(self):
        content = self.compiled_path.read_text(encoding='utf-8')
        termos = ['Modelo Purdue', 'DMZ industrial', 'SCADA', 'CLP', 'PLC', 'IHM', 'HMI', 'RTU', 'Modbus', '502', 'DNP3', '20000', 'BACnet', '47808', 'OPC UA', '4840', 'Stuxnet', 'Industroyer', 'Triton', 'IEC 62443', 'zonas', 'conduítes', 'Mirai', 'firmware', 'monitoramento passivo', 'diodo de dados', 'disponibilidade']
        for termo in termos:
            self.assertIn(termo, content, f'Termo obrigatório ausente: {termo}')

    def test_regras(self):
        self.assertEqual(regra('4', '1'), ('bloquear', 'R1'))
        self.assertEqual(regra('4', '3.5'), ('permitir', 'R3'))
        self.assertEqual(regra('3.5', '2'), ('bloquear', 'R3'))
        self.assertEqual(regra('3', '2'), ('permitir', 'R2'))
        self.assertEqual(regra('3', '1'), ('bloquear', 'R2'))
        self.assertEqual(regra('5', '3.5'), ('bloquear', 'R4'))
        self.assertEqual(regra('5', '4'), ('permitir', 'R0'))
        self.assertEqual(regra('1', '1'), ('permitir', 'R2'))

    def test_integracao_com_portal_index(self):
        content = self.portal_path.read_text(encoding='utf-8')
        self.assertIn('Seguranca-em-IoT-e-OT/treinamento-seguranca-em-iot-e-ot.html', content)
        self.assertIn('data-slug="Seguranca-em-IoT-e-OT"', content)
        self.assertIn(f'/ {len(ESTUDOS_DADOS)}', content)
if __name__ == '__main__':
    unittest.main()
