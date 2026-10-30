"""Independent dense checks and rejecting controls. Apache-2.0."""

import copy
import itertools
import runpy
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace

# run_path reads the named .py directly, without consulting its import bytecode.
v = SimpleNamespace(**runpy.run_path(str(Path(__file__).with_name('verify.py'))))


def reject(function, message):
    try:
        function()
    except ValueError as error:
        v.require(message in str(error), 'unexpected control rejection: ' + str(error))
        return
    raise ValueError('control admitted: ' + message)


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def scale(a, q):
    return a[0] * q, a[1] * q


def times_i(a):
    return -a[1], a[0]


def dense(program, column, bits):
    """Separate Fraction evaluator using C(a,b)=(a+b +/- i(a-b))/2."""
    state = [(Fraction(int(x == column)), Fraction(0)) for x in range(1 << bits)]
    for gate in program:
        result = list(state)
        if gate[0] == 'M':
            units = ((1, 0), (0, 1), (-1, 0), (0, -1))
            for x, (y, phase) in enumerate(gate[1]):
                a, b = state[x]
                c, d = units[phase]
                result[y] = (a * c - b * d, a * d + b * c)
        else:
            _, bit, sign = gate
            for x in range(1 << bits):
                if not x >> bit & 1:
                    y = x | (1 << bit)
                    total = add(state[x], state[y])
                    difference = times_i(add(state[x], scale(state[y], -1)))
                    result[x] = scale(add(total, scale(difference, sign)), Fraction(1, 2))
                    result[y] = scale(add(total, scale(difference, -sign)), Fraction(1, 2))
        state = result
    return tuple(state)


def full_matrix(program, bits):
    return tuple(dense(program, x, bits) for x in range(1 << bits))


def fraction_column(program, column, bits):
    initial = tuple((int(x == column), 0) for x in range(1 << bits))
    vector, denominator = v.apply(program, initial)
    return tuple((Fraction(a, 1 << denominator), Fraction(b, 1 << denominator))
                 for a, b in vector)


def dense_intertwining(matrix, pauli, output):
    v.require(len(matrix) <= 4, 'small dense control capacity')
    p, x, z = pauli
    phase, shift, mask = output
    for column in range(len(matrix)):
        unit = ((1, 0), (0, 1), (-1, 0), (0, -1))[
            (p + 2 * (z & column).bit_count()) % 4]
        lhs = tuple((a * unit[0] - b * unit[1], a * unit[1] + b * unit[0])
                    for a, b in matrix[column ^ x])
        rhs = [(Fraction(0), Fraction(0))] * len(matrix)
        for row, (a, b) in enumerate(matrix[column]):
            unit = ((1, 0), (0, 1), (-1, 0), (0, -1))[
                (phase + 2 * (mask & row).bit_count()) % 4]
            rhs[row ^ shift] = (a * unit[0] - b * unit[1], a * unit[1] + b * unit[0])
        v.require(lhs == tuple(rhs), 'independent dense Pauli intertwining')
    return len(matrix)


def dense_criterion():
    # Every word of length <=3 in five generators, with paired bit patterns.
    swap = ('M', tuple(((x & 1) << 1 | x >> 1, 0) for x in range(4)))
    phase = ('M', tuple((x, x & 1) for x in range(4)))
    flip = ('M', tuple((x ^ 1, 0) for x in range(4)))
    gates = (('C', 0, 1), ('C', 1, -1), swap, phase, flip)
    programs = [()]
    for length in range(1, 4):
        programs.extend(itertools.product(gates, repeat=length))
    cache, by_certificate, by_matrix = {}, {}, {}
    columns, relations = 0, 0
    for program in programs:
        matrix = full_matrix(program, 2)
        for x in range(4):
            v.require(fraction_column(program, x, 2) == matrix[x], 'dense column equality')
            columns += 1
        table = v.program_table(program, cache, 2)
        for pauli, output in zip(v.identity(2), table, strict=True):
            relations += dense_intertwining(matrix, pauli, output)
        anchor = v.canonical_vector(v.apply(program, ((1, 0), (0, 0), (0, 0), (0, 0))))
        certificate = (table, anchor)
        if certificate in by_certificate:
            v.require(by_certificate[certificate] == matrix, 'certificate implies matrix')
        if matrix in by_matrix:
            v.require(by_matrix[matrix] == certificate, 'matrix implies certificate')
        by_certificate[certificate], by_matrix[matrix] = matrix, certificate
        v.equal_certificate(program + v.adjoint(program), (), cache, 2)
    v.require(len(programs) == 156 and columns == 624, 'complete small-word coverage')
    return {'programs': len(programs), 'full_columns': columns,
            'distinct_matrices': len(by_matrix), 'inverse_checks': len(programs),
            'dense_tableau_relations': relations}


def all_small_paulis():
    program = (('C', 0, 1), ('M', ((0, 0), (1, 1))), ('C', 0, -1))
    matrix = full_matrix(program, 1)
    table = v.program_table(program, {}, 1)
    checked = 0
    for p, x, z in itertools.product(range(4), range(2), range(2)):
        checked += dense_intertwining(matrix, (p, x, z), v.image(table, (p, x, z)))
    return checked


def phase_and_gate_controls(word, archive):
    item = archive['transports'][0]
    actual = v.recipe_program(item['recipe'])
    expected = v.adjoint(v.chart(tuple(item['old']))) + v.chart(tuple(item['new']))
    cache = {}
    v.equal_certificate(actual, expected, cache)
    for phase in (1, 2, 3):
        scalar = ('M', tuple((x, phase) for x in range(v.SIZE)))
        mutant = actual + (scalar,)
        v.require(v.program_table(mutant, cache) == v.program_table(expected, cache),
                  'global phase is invisible to tableau')
        reject(lambda m=mutant: v.equal_certificate(m, expected, cache), 'global phase mismatch')
    wrong_c = tuple(('C', g[1], -g[2]) if g[0] == 'C' else g for g in actual)
    reject(lambda: v.equal_certificate(wrong_c, expected, cache), 'Pauli covariance mismatch')
    missing = tuple(g for g in actual if g[0] != 'C')
    reject(lambda: v.equal_certificate(missing, expected, cache), 'Pauli covariance mismatch')
    wrong_frame = v.adjoint(v.chart(tuple(item['old']))) + v.chart((8,))
    reject(lambda: v.equal_certificate(actual, wrong_frame, cache), 'Pauli covariance mismatch')
    bad = copy.deepcopy(archive)
    bad['transports'][0]['events'] = bad['transports'][1]['events']
    reject(lambda: v.bind(word, bad), 'occurrence recipe binding')
    bad = copy.deepcopy(archive)
    bad['transports'].pop()
    reject(lambda: v.bind(word, bad), 'native inventory')
    return 8


def boundary_controls():
    reject(lambda: v.inverse_mapping(((0, 0), (0, 0))), 'bijective monomial')
    reject(lambda: v.chart((1, 1)), 'independent frame')
    reject(lambda: v.c_table(v.identity(2), 2, 1), 'C stage argument')
    reject(lambda: v.program_table((('C', 0, 1),) * 23, {}, 2), 'program capacity')
    # A cubic sign is outside the Clifford alphabet; its derivative is not Pauli.
    cubic = tuple((x, 2 * int(x == 7)) for x in range(8))
    reject(lambda: v.monomial_table(cubic), 'Pauli phase identity')
    # X fixes the all-ones vector, but does not equal I. An anchor alone is insufficient.
    ones = ((1, 0),) * 4
    x = (('M', tuple((j ^ 1, 0) for j in range(4))),)
    v.require(v.apply(x, ones) == v.apply((), ones), 'anchor-only false positive fixture')
    v.require(v.program_table(x, {}, 2) != v.identity(2), 'tableau distinguishes anchor collision')
    v.require(not v.same_json({'rank': 1}, {'rank': True}), 'typed receipt comparison')
    return 7


def main():
    word, archive = v.read_sources(v.ROOT)
    result = dense_criterion()
    result['pauli_relations'] = all_small_paulis()
    result['native_rejecting_controls'] = phase_and_gate_controls(word, archive)
    result['boundary_controls'] = boundary_controls()
    print('PASS_P104_NATIVE_CONTROLS', result)


if __name__ == '__main__':
    main()
