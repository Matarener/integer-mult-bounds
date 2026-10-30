"""Exact binary matrices and full polynomial words; no numerical evaluations.

Prepared for theon199 with substantial OpenAI Codex assistance. Apache-2.0.
"""
import itertools

N = 8
ZERO = (0,) * N
IDENTITY = tuple(1 << i for i in range(N))
CONSTANT = (0, 0, 0)
EXPONENTS = tuple(itertools.product(range(3), repeat=3))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def add(a, b):
    return tuple(x ^ y for x, y in zip(a, b))


def multiply(a, b):
    out = []
    for row in a:
        value = 0
        for j in range(N):
            if row & (1 << j):
                value ^= b[j]
        out.append(value)
    return tuple(out)


def rank(matrix):
    basis = {}
    for row in matrix:
        while row:
            pivot = row.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = row
                break
            row ^= basis[pivot]
    return len(basis)


def poly_add(a, b):
    result = dict(a)
    for exponent, matrix in b.items():
        result[exponent] = add(result.get(exponent, ZERO), matrix)
    return {key: value for key, value in result.items() if any(value)}


def poly_multiply(a, b):
    result = {}
    for x, ax in a.items():
        for y, by in b.items():
            exponent = tuple(i + j for i, j in zip(x, y))
            result[exponent] = add(result.get(exponent, ZERO), multiply(ax, by))
    return {key: value for key, value in result.items() if any(value)}


def encode(poly):
    result = 0
    for exponent, matrix in poly.items():
        require(all(0 <= x <= 2 for x in exponent), 'Exponent outside complete domain')
        offset = (9 * exponent[0] + 3 * exponent[1] + exponent[2]) * 64
        for i, row in enumerate(matrix):
            result ^= row << (offset + 8 * i)
    return result


def gate(call):
    p, r = tuple(call['p']), tuple(call['r'])
    base, eps = {CONSTANT: IDENTITY}, {CONSTANT: r}
    if call['stage'] < 3:
        exponent = tuple(int(j == call['stage']) for j in range(3))
        base[exponent] = p
        eps[exponent] = r  # P R = R, so (I+xP)(I+eR).
    return base, eps


def replay(calls, order):
    base, eps = {CONSTANT: IDENTITY}, {}
    for i in order:
        a, b = gate(calls[i])
        base, eps = (poly_multiply(a, base),
                     poly_add(poly_multiply(a, eps), poly_multiply(b, base)))
    return base, eps


def expected(calls):
    result = {CONSTANT: IDENTITY}
    for j in range(3):
        exponent = tuple(int(k == j) for k in range(3))
        target = add(calls[2*j]['p'], calls[2*j+1]['p'])
        result = poly_multiply({CONSTANT: IDENTITY, exponent: target}, result)
    return result


def gap_problem(calls, order, gap):
    """Return 64 linear columns and the full e-coefficient discrepancy.

    The product acts on column vectors, later gates multiplying on the left.
    x_j = D_j+1; e^2=0. A thin burst contributes suffix * Z * prefix.
    """
    wanted = expected(calls)
    base, eps = replay(calls, order)
    require(base == wanted, 'Wrong pure stage endpoint')
    prefix = suffix = {CONSTANT: IDENTITY}
    for i in order[:gap]:
        prefix = poly_multiply(gate(calls[i])[0], prefix)
    for i in order[gap:]:
        suffix = poly_multiply(gate(calls[i])[0], suffix)
    columns = []
    for i in range(N):
        for j in range(N):
            unit = list(ZERO)
            unit[i] = 1 << j
            columns.append(encode(poly_multiply(suffix, poly_multiply(
                {CONSTANT: tuple(unit)}, prefix))))
    return columns, encode(poly_add(wanted, eps))


def equation(columns, target, row):
    require(type(row) is int and 0 <= row < 27 * 64, 'Invalid equation index')
    return sum(((col >> row) & 1) << j for j, col in enumerate(columns)), (target >> row) & 1


def check_dual(columns, target, indices):
    require(indices and len(indices) == len(set(indices)), 'Empty or duplicate dual rows')
    lhs = rhs = 0
    for row in indices:
        a, b = equation(columns, target, row)
        lhs ^= a
        rhs ^= b
    require(lhs == 0 and rhs == 1, 'Dual does not sum to 0 = 1')


def check_source(data):
    calls = data['calls']
    require(len(calls) == 14 and sorted(data['order']) == list(range(14)), 'Source inventory')
    require([c['stage'] for c in calls] == [0,0,1,1,2,2] + [3]*8, 'Source stages')
    for i, call in enumerate(calls):
        p, r = tuple(call['p']), tuple(call['r'])
        require(len(p) == len(r) == N and all(type(v) is int and 0 <= v < 256 for v in p+r), 'Source encoding')
        require(rank(r) == 1 and multiply(r, r) == ZERO, 'Source query rank/nilpotence')
        if i < 6:
            require(rank(p) == 2 and multiply(p,p) == p, 'Source projector')
            require(multiply(p,r) == multiply(r,p) == r, 'Source compatibility')
        else:
            require(p == ZERO, 'Thin projector')
    wanted = expected(calls)
    require(replay(calls, data['order']) == (wanted, wanted), 'Source full polynomial identity')
    return calls
