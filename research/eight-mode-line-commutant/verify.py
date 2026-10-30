#!/usr/bin/env python3
"""Check the exact line commutant of the source eight-mode code.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The input recipes and mode matrix retain their source authors.
"""
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
SIZE = 512
PRIME = 1009


def need(test, message):
    if not test:
        raise ValueError(message)


def literal(word, x):
    """Apply a monomial circuit to one basis vector, including its phase."""
    phase = 0
    for event in word:
        tag = event[0]
        if tag == 'P':
            x = sum(((row & x).bit_count() % 2) << i
                    for i, row in enumerate(event[1]))
        elif tag == 'X':
            x ^= event[1]
        elif tag == 'phase':
            phase += event[1]
        elif tag == 'D':
            phase += sum(event[2][i] for i in range(9) if x >> i & 1)
            phase += 2 * sum(((event[1][i] >> (i + 1))
                              & (x >> (i + 1))).bit_count()
                             for i in range(9) if x >> i & 1)
        else:
            raise ValueError('Nonmonomial source gate')
    return x, phase % 4


def monomial(word):
    data = [literal(word, x) for x in range(SIZE)]
    need(data[0] == (0, 0), 'Common zero anchor')
    need({x for x, _ in data} == set(range(SIZE)), 'Permutation')
    need(all(phase in (0, 2) for _, phase in data), 'Real signs')
    return [(x, 1 if phase == 0 else -1) for x, phase in data]


def inverse(data):
    result = [None] * SIZE
    for x, (y, sign) in enumerate(data):
        result[y] = x, sign
    return result


def setup():
    for row in json.loads((HERE / 'INPUTS.json').read_text()):
        need(sha256((HERE / row['local']).read_bytes()).hexdigest()
             == row['sha256'], 'Source bytes: ' + row['local'])
    normal = json.loads((HERE / 'inputs/NORMALIZERS.json').read_bytes())
    provider = json.loads((HERE / 'inputs/PROVIDER.json').read_bytes())
    matrix = normal['mode_columns']
    need(len(matrix) == 8 and all(len(row) == 112 for row in matrix), 'Mode shape')
    need(all(value in (-1, 0, 1) for row in matrix for value in row), 'Mode values')
    need(all(sum(matrix[a][j] * matrix[b][j] for j in range(112))
             == (56 if a == b else 0) for a in range(8) for b in range(8)), 'M transpose M')
    ports = [monomial(row['K_word']) for row in normal['ports']]
    modes = [monomial(row['input_K']['literal_word'])
             for row in provider['mode_boundaries']]
    need(len(ports) == 112 and len(modes) == 8, 'Physical bank counts')
    # Check the literal circuits against a second published representation.
    for j, (data, source) in enumerate(zip(ports, normal['ports'])):
        need(source['port'] == j, 'Port order')
        for x, (y, sign) in enumerate(data):
            z = sum(((row & x).bit_count() % 2) << k
                    for k, row in enumerate(source['G_rows']))
            need(y == z and sign == (-1) ** ((source['Z_mask'] & z).bit_count() % 2),
                 'Port matrix and sign binding')
    for k, (data, source) in enumerate(zip(modes, provider['mode_boundaries'])):
        need(source['mode'] == k, 'Mode order')
        tab = source['input_K']['signed_tableau'][:9]
        need(all(z == 0 and phase % 2 == 0 for _, z, phase in tab), 'Linear signed mode')
        for x, (y, sign) in enumerate(data):
            expected, phase = 0, 0
            for bit, (column, _, exponent) in enumerate(tab):
                if x >> bit & 1:
                    expected ^= column
                    phase += exponent
            need(y == expected and sign == (-1) ** ((phase // 2) % 2),
                 'Mode tableau and literal binding')
    for data in ports + modes:
        need(all(data[x ^ 511] == (data[x][0] ^ 511, data[x][1])
                 for x in range(SIZE)), 'Characteristic positive control')
    return matrix, ports, modes, list(map(inverse, ports)), list(map(inverse, modes))


def coefficient_row(direction, witness, source):
    matrix, ports, modes, port_inverse, mode_inverse = source
    i, j, output = witness
    need(0 <= i < 112 and 0 <= j < 112 and 0 < output < SIZE, 'Witness address')
    row = [0] * 64
    for a in range(8):
        for b in range(8):
            coefficient = matrix[a][i] * matrix[b][j]
            if not coefficient:
                continue
            y, sign = ports[j][direction]
            for data in (mode_inverse[b], modes[a], port_inverse[i]):
                y, factor = data[y]
                sign *= factor
            row[8 * a + b] = coefficient * ((sign if y == output else 0)
                                            - (1 if direction == output else 0))
    return row


def rank_mod(rows, prime=PRIME):
    basis = {}
    for source in rows:
        row = [x % prime for x in source]
        for pivot, known in sorted(basis.items()):
            factor = row[pivot]
            if factor:
                row = [(x - factor * y) % prime for x, y in zip(row, known)]
        pivot = next((j for j, x in enumerate(row) if x), None)
        if pivot is not None:
            factor = pow(row[pivot], -1, prime)
            basis[pivot] = [x * factor % prime for x in row]
    return len(basis)


def determinant(rows):
    """Use rational row elimination, separate from the modular rank check."""
    data = [list(map(Fraction, row)) for row in rows]
    result = Fraction(1)
    for j in range(len(data)):
        pivot = next((k for k in range(j, len(data)) if data[k][j]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != j:
            data[j], data[pivot] = data[pivot], data[j]
            result = -result
        value = data[j][j]
        result *= value
        for k in range(j + 1, len(data)):
            factor = data[k][j] / value
            if factor:
                data[k] = [x - factor * y for x, y in zip(data[k], data[j])]
    return result


def main():
    need(all(PRIME % divisor for divisor in range(2, 32)), 'Prime modulus')
    source = setup()
    witnesses = json.loads((HERE / 'WITNESSES.json').read_text())
    need(set(witnesses) == {str(v) for v in range(1, 511)}, 'Every noncharacteristic line')
    digest = sha256()
    rows_one = None
    for direction in range(1, 511):
        addresses = witnesses[str(direction)]
        need(len(addresses) == 64 and len(set(map(tuple, addresses))) == 64, 'Witness count')
        rows = [coefficient_row(direction, address, source) for address in addresses]
        need(rank_mod(rows) == 64, 'Full commutator rank: ' + str(direction))
        digest.update(json.dumps([direction, rows], separators=(',', ':')).encode())
        if direction == 1:
            rows_one = rows
    det = determinant(rows_one)
    need(det != 0 and det.denominator == 1, 'Central rational determinant')
    mutant = [row[:] for row in rows_one]
    mutant[0] = [0] * 64
    need(rank_mod(mutant) < 64 and determinant(mutant) == 0, 'Deleted constraint control')
    need(all(not any(coefficient_row(511, address, source))
             for address in witnesses['1']), 'Characteristic kernel control')
    result = {'noncharacteristic_lines': 510, 'coefficient_dimension': 64,
              'constraint_rows': 510 * 64, 'characteristic_direction': 511,
              'characteristic_kernel_dimension': 64, 'other_kernel_dimension': 0,
              'central_determinant': str(det), 'modulus': PRIME,
              'reconstructed_rows_sha256': digest.hexdigest(),
              'width_scope': 'Every positive integer width; arbitrary complex scalar mode matrix',
              'no_new_kappa': True}
    if '--emit' in sys.argv:
        (HERE / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    else:
        need(result == json.loads((HERE / 'RESULT.json').read_text()), 'Result receipt')
    print(json.dumps(result, sort_keys=True))
    print('PASS_EIGHT_MODE_LINE_COMMUTANT')


if __name__ == '__main__':
    main()
