#!/usr/bin/env python3
"""Exact order-seventeen Clifford construction and sharp eight-rank witness.

Prepared by apoursh with substantial OpenAI Codex assistance. Apache-2.0.
Nick Petalas retains PR6192's rank cap and Bell-conjugation method;
Ross Richardson retains the earlier cubic/Pauli-character lineage.
No predecessor executable code is imported.
"""

import hashlib
import json
from functools import reduce
from math import gcd, lcm
from pathlib import Path

PHASES = ((1, 0), (0, 1), (-1, 0), (0, -1))
A = ((0, 0, 0, 1), (0, 0, 1, 0), (0, 1, 0, 1), (1, 0, 1, 1))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def gmul(x, y):
    return x[0] * y[0] - x[1] * y[1], x[0] * y[1] + x[1] * y[0]


def canonical(rows, denominator=1):
    need(denominator > 0 and rows and all(len(row) == len(rows) for row in rows),
         'positive denominator and square matrix')
    common = reduce(gcd, (v for row in rows for entry in row for v in entry), denominator)
    return tuple(tuple((x // common, y // common) for x, y in row) for row in rows), denominator // common


def identity(size):
    return canonical([[(int(i == j), 0) for j in range(size)] for i in range(size)])


def multiply(left, right):
    a, da = left
    b, db = right
    need(len(a) == len(b), 'equal matrix sizes')
    columns = tuple(zip(*b, strict=True))
    output = []
    for row in a:
        out = []
        for column in columns:
            real = imag = 0
            for x, y in zip(row, column, strict=True):
                p, q = gmul(x, y)
                real += p
                imag += q
            out.append((real, imag))
        output.append(out)
    return canonical(output, da * db)


def adjoint(matrix):
    rows, denominator = matrix
    return canonical([[(x, -y) for x, y in column] for column in zip(*rows, strict=True)], denominator)


def scale_phase(matrix, phase):
    rows, denominator = matrix
    return canonical([[gmul(PHASES[phase % 4], x) for x in row] for row in rows], denominator)


def sum_matrices(matrices):
    denominator = lcm(*(den for unused, den in matrices))
    size = len(matrices[0][0])
    out = [[(0, 0) for j in range(size)] for i in range(size)]
    for rows, den in matrices:
        factor = denominator // den
        for i, row in enumerate(rows):
            for j, (real, imag) in enumerate(row):
                x, y = out[i][j]
                out[i][j] = x + factor * real, y + factor * imag
    return canonical(out, denominator)


def is_zero(matrix):
    return all(entry == (0, 0) for row in matrix[0] for entry in row)


def trace(matrix):
    rows, denominator = matrix
    return sum(rows[i][i][0] for i in range(len(rows))), sum(rows[i][i][1] for i in range(len(rows))), denominator


def powers(matrix, exponent):
    output = [identity(len(matrix[0]))]
    for unused in range(exponent):
        output.append(multiply(matrix, output[-1]))
    return output


def construct_u(omit_edge=False):
    rows = []
    for x in range(16):
        bits = [(x >> j) & 1 for j in range(4)]
        quadratic = bits[1] * bits[2] + bits[2] * bits[3]
        if not omit_edge:
            quadratic += bits[0] * bits[3]
        rows.append([PHASES[(-1 + bits[3] + 2 * quadratic + 2 * (x & y).bit_count()) % 4]
                     for y in range(16)])
    return canonical(rows, 4)


def pauli(x, z):
    rows = [[(0, 0) for unused in range(16)] for unused in range(16)]
    for column in range(16):
        rows[column ^ x][column] = PHASES[((x & z).bit_count() + 2 * (column & z).bit_count()) % 4]
    return canonical(rows)


def pauli_action(unitary):
    lookup = {}
    for x in range(16):
        for z in range(16):
            positive = pauli(x, z)
            lookup[positive] = (x, z, 1)
            lookup[scale_phase(positive, 2)] = (x, z, -1)
    images = []
    for index in range(8):
        operator = pauli(1 << index, 0) if index < 4 else pauli(0, 1 << (index - 4))
        image = multiply(multiply(unitary, operator), adjoint(unitary))
        need(image in lookup, 'complete signed Pauli image')
        x, z, sign = lookup[image]
        images.append({'x': x, 'z': z, 'sign': sign})
    columns = [item['x'] | item['z'] << 4 for item in images]
    symplectic = [sum(((column >> row) & 1) << j for j, column in enumerate(columns))
                  for row in range(8)]
    return images, symplectic


def binary_identity(size):
    return [1 << i for i in range(size)]


def binary_multiply(left, right):
    out = []
    for row in left:
        value = 0
        for j, other in enumerate(right):
            if row >> j & 1:
                value ^= other
        out.append(value)
    return out


def binary_transpose(rows):
    return [sum(((row >> j) & 1) << i for i, row in enumerate(rows)) for j in range(len(rows))]


def binary_rank(rows, width):
    rows = list(rows)
    position = 0
    for column in range(width):
        pivot = next((i for i in range(position, len(rows)) if rows[i] >> column & 1), None)
        if pivot is None:
            continue
        rows[position], rows[pivot] = rows[pivot], rows[position]
        for i in range(len(rows)):
            if i != position and rows[i] >> column & 1:
                rows[i] ^= rows[position]
        position += 1
    return position


def binary_inverse(rows):
    size = len(rows)
    augmented = [row | (1 << (size + i)) for i, row in enumerate(rows)]
    for j in range(size):
        pivot = next((i for i in range(j, size) if augmented[i] >> j & 1), None)
        need(pivot is not None, 'invertible binary matrix')
        augmented[j], augmented[pivot] = augmented[pivot], augmented[j]
        for i in range(size):
            if i != j and augmented[i] >> j & 1:
                augmented[i] ^= augmented[j]
    result = [row >> size for row in augmented]
    need(binary_multiply(rows, result) == binary_identity(size), 'binary inverse residual')
    return result


def binary_power(rows, exponent):
    result = binary_identity(len(rows))
    for unused in range(exponent):
        result = binary_multiply(rows, result)
    return result


def check_symplectic(rows):
    half = len(rows) // 2
    form = [1 << (i + half) for i in range(half)] + [1 << i for i in range(half)]
    return binary_multiply(binary_multiply(rows, form), binary_transpose(rows)) == form


def native_rank(rows):
    half = len(rows) // 2
    return binary_rank([row >> half for row in rows[:half]], half)


def bell_witness(active):
    embedded = binary_identity(16)
    coordinates = list(range(4)) + list(range(8, 12))
    for i, row in enumerate(active):
        embedded[coordinates[i]] = sum(((row >> j) & 1) << coordinates[j] for j in range(8))
    v = binary_identity(16)
    for j in range(4):
        v[j], v[j + 8] = v[j + 8], v[j]
    for control in range(4):
        target = control + 4
        v[target] ^= v[control]
        v[control + 8] ^= v[target + 8]
    need(check_symplectic(v) and check_symplectic(embedded), 'Bell and embedded symplectic maps')
    w = binary_multiply(binary_multiply(binary_inverse(v), embedded), v)
    expected_b = [(1 << i) | sum((A[i][j] ^ int(i == j)) << (j + 4) for j in range(4))
                  for i in range(4)] + [(1 << i) | (1 << (i + 4)) for i in range(4)]
    need([row >> 8 for row in w[:8]] == expected_b, 'Bell B block agrees with closed formula')
    need(native_rank(w) == 8 and check_symplectic(w), 'sharp eight-qubit native rank')
    need(binary_rank([row ^ (1 << i) for i, row in enumerate(w)], 16) == 8, 'Bell defect rank')
    need(binary_power(w, 17) == binary_identity(16), 'Bell symplectic order divides seventeen')
    return w, expected_b, native_rank(embedded)


def controls(unitary, power_list, symplectic, spectator_rank):
    outcomes = []
    wrong_phase = scale_phase(unitary, 1)
    wrong_powers = powers(wrong_phase, 17)
    need(wrong_powers[17] == scale_phase(identity(16), 1), 'wrong phase has seventeenth power iI')
    need(not is_zero(sum_matrices(wrong_powers[:17])), 'wrong phase rejected by Phi17')
    outcomes.append('wrong_global_phase_fails_Phi17')
    edge_mutant = construct_u(omit_edge=True)
    need(multiply(edge_mutant, adjoint(edge_mutant)) == identity(16), 'edge mutant stays unitary')
    need(not is_zero(sum_matrices(powers(edge_mutant, 16))), 'omitted CZ edge rejected by Phi17')
    outcomes.append('missing_CZ_edge_fails_Phi17')
    need(not is_zero(sum_matrices(power_list[:16])), 'truncated polynomial rejected')
    outcomes.append('truncated_polynomial_nonzero')
    traces = [trace(matrix) for matrix in power_list[:17]]
    need(all(imag == 0 and real % den == 0 for real, imag, den in traces), 'integral real traces')
    tensor_trace = sum((real // den) ** 2 for real, unused, den in traces)
    need(tensor_trace == 272, 'order-seventeen tensor is not primitive: Phi17 trace 272')
    outcomes.append('tensor_square_order17_but_not_Phi17_by_trace')
    need(spectator_rank == 4, 'identity spectators alone do not attain rank eight')
    outcomes.append('spectators_without_Bell_keep_native_rank_four')
    asymmetric = list(symplectic)
    asymmetric[4] ^= 1 << 5
    need(not check_symplectic(asymmetric), 'asymmetric phase prediction rejected')
    outcomes.append('asymmetric_phase_matrix_not_symplectic')
    companion = [[(0, 0) for unused in range(16)] for unused in range(16)]
    for i in range(15):
        companion[i + 1][i] = (1, 0)
    for row in companion:
        row[15] = (-1, 0)
    companion = canonical(companion)
    need(is_zero(sum_matrices(powers(companion, 16))), 'companion has correct polynomial')
    need(multiply(companion, adjoint(companion)) != identity(16), 'companion is not unitary')
    outcomes.append('cyclotomic_companion_fails_unitarity')
    return outcomes


def source_hashes(package):
    pins = json.loads((package / 'SOURCE-PINS.json').read_text())
    need(pins['source_pr'] == 6192 and pins['head'] == '91df334ccd2a4bc9959e311f118ac8aaf967ffc2',
         'expected predecessor identity')
    need(len(pins['files']) == 2, 'two retained predecessor documents')
    result = {}
    for record in pins['files']:
        path = Path(record['path'])
        need(not path.is_absolute() and '..' not in path.parts, 'relative source path')
        digest = hashlib.sha256((package / path).read_bytes()).hexdigest()
        need(digest == record['sha256'], 'retained source digest: ' + str(path))
        result[str(path)] = digest
    return result


def main():
    sources = source_hashes(Path(__file__).resolve().parent)
    unitary = construct_u()
    need(multiply(unitary, adjoint(unitary)) == identity(16), 'complete exact unitarity')
    power_list = powers(unitary, 17)
    need(power_list[17] == identity(16), 'actual order seventeen')
    need(is_zero(sum_matrices(power_list[:17])), 'actual whole-bank Phi17')
    need(trace(unitary) == (-4, 0, 4), 'actual trace minus one')
    need(all(matrix[1] == 4 and trace(matrix) == (-4, 0, 4) for matrix in power_list[1:17]),
         'all sixteen primitive powers have denominator four and trace minus one')
    images, symplectic = pauli_action(unitary)
    expected = [1 << (i + 4) for i in range(4)] + [
        (1 << i) | sum(A[i][j] << (j + 4) for j in range(4)) for i in range(4)]
    need(symplectic == expected and all(item['sign'] == 1 for item in images), 'stated signed Pauli action')
    need(check_symplectic(symplectic), 'binary symplectic identity')
    need(binary_power(symplectic, 17) == binary_identity(8), 'binary order seventeen')
    need(binary_rank([row ^ (1 << i) for i, row in enumerate(symplectic)], 8) == 8,
         'active symplectic defect eight')
    need(native_rank(symplectic) == 4, 'active native rank four')
    w, b, spectator_rank = bell_witness(symplectic)
    result = {'schema_version': 1, 'active_qubits': 4, 'matrix_dimension': 16,
              'actual_order': 17, 'Phi17_zero': True, 'trace': '-1',
              'primitive_powers_checked': 16, 'signed_Pauli_images': images,
              'symplectic_rows': symplectic, 'active_defect_rank': 8, 'active_B_rank': 4,
              'Bell_symplectic_rows': w, 'Bell_B_rows': b, 'Bell_B_rank': 8,
              'controls': controls(unitary, power_list, symplectic, spectator_rank),
              'source_sha256': sources,
              'scope': 'finite construction; eight-qubit polynomial identity follows by tensor and conjugation; no physical invoice or new kappa'}
    print(json.dumps(result, sort_keys=True))
    print('PASS_ORDER_SEVENTEEN_CLIFFORD')


if __name__ == '__main__':
    main()
