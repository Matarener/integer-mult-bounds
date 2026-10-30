"""Small exact matrices for independent native-cut checks.

The scalar implementation is the unchanged, attributed predecessor file.
Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from itertools import product
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / 'vendor'))
from fields import Gaussian as G


def need(condition, message):
    if not condition:
        raise ValueError(message)


def eye(d):
    return tuple(tuple(G(int(i == j)) for j in range(d)) for i in range(d))


def zero(rows, columns):
    return [[G(0) for _ in range(columns)] for _ in range(rows)]


def mul(a, b):
    out = zero(len(a), len(b[0]))
    sparse = [[(j, v) for j, v in enumerate(row) if v] for row in b]
    for i, row in enumerate(a):
        for k, x in enumerate(row):
            if x:
                for j, y in sparse[k]:
                    out[i][j] = out[i][j] + x * y
    return tuple(map(tuple, out))


def adjoint(a):
    return tuple(tuple(G.pair(x.real, -x.imag) for x in col) for col in zip(*a))


def rank(a):
    basis = {}
    for vector in a:
        row = list(vector)
        for p, old in sorted(basis.items()):
            if row[p]:
                c = row[p]
                row = [x - c * y for x, y in zip(row, old)]
        p = next((j for j, x in enumerate(row) if x), None)
        if p is not None:
            c = row[p]
            basis[p] = tuple(x / c for x in row)
    return len(basis)


def tensor(a, b):
    return tuple(tuple(x * y for x in ar for y in br) for ar in a for br in b)


def power_tensor(a, f):
    out = ((G(1),),)
    for _ in range(f):
        out = tensor(out, a)
    return out


def matrix_key(a):
    return tuple((z.real, z.imag) for row in a for z in row)


def canonical(a):
    choices = [tuple(tuple(c * x for x in row) for row in a)
               for c in (G(1), G('i'), G(-1), G('-i'))]
    return min(choices, key=matrix_key)


def gate(n, kind, i=0, j=1):
    d = 1 << n
    if kind in ('S', 'X', 'CX', 'CZ'):
        a = zero(d, d)
        for x in range(d):
            y, phase = x, G(1)
            if kind == 'S' and (x >> i) & 1:
                phase = G('i')
            elif kind == 'X':
                y ^= 1 << i
            elif kind == 'CX' and (x >> i) & 1:
                y ^= 1 << j
            elif kind == 'CZ' and (x >> i) & (x >> j) & 1:
                phase = G(-1)
            a[y][x] = phase
        return tuple(map(tuple, a))
    need(kind == 'Q', 'gate kind')
    a = zero(d, d)
    for x in range(d):
        a[x][x] = G('1/2+1/2i')
        a[x ^ (1 << i)][x] = G('1/2-1/2i')
    return tuple(map(tuple, a))


def one_axis_cliffords():
    first = canonical(eye(2))
    found = {matrix_key(first): first}
    queue = [first]
    for a in queue:
        for g in (gate(1, 'S'), gate(1, 'Q')):
            b = canonical(mul(g, a))
            key = matrix_key(b)
            if key not in found:
                found[key] = b
                queue.append(b)
    need(len(queue) == 24, 'complete one-axis projective orbit')
    return queue


def fourier_rank(a):
    """Use conjugated diagonal Paulis, not the target tariff."""
    d = len(a)
    n = d.bit_length() - 1
    need(d == 1 << n and mul(adjoint(a), a) == eye(d), 'unitary power-of-two map')
    labels = []
    for j in range(n):
        z = tuple(tuple(G((-1 if (x >> j) & 1 else 1) if x == y else 0)
                        for y in range(d)) for x in range(d))
        b = mul(mul(a, z), adjoint(a))
        xs = []
        for col in range(d):
            rows = [row for row in range(d) if b[row][col]]
            need(len(rows) == 1, 'conjugated Pauli support')
            xs.append(rows[0] ^ col)
        need(len(set(xs)) == 1, 'Pauli translation')
        labels.append(xs[0])
    pivots = {}
    for x in labels:
        while x:
            p = x.bit_length() - 1
            if p not in pivots:
                pivots[p] = x
                break
            x ^= pivots[p]
    r = len(pivots)
    need(all(sum(bool(row[j]) for row in a) == 1 << r for j in range(d)),
         'independent support-rank check')
    return r


def equality_indices(d, f, k):
    return [j for j, word in enumerate(product(range(d), repeat=f))
            if all(word[2*t] == word[2*t+1] for t in range(k))]


def literal_cross(a, f, k):
    """Build only the literal cross block; use no stabilizer formula."""
    d = len(a)
    words = list(product(range(d), repeat=f))
    inside = [w for w in words if all(w[2*t] == w[2*t+1] for t in range(k))]
    outside = [w for w in words if any(w[2*t] != w[2*t+1] for t in range(k))]
    out = []
    for y in outside:
        row = []
        for x in inside:
            value = G(1)
            for u, v in zip(y, x):
                value = value * a[u][v]
            row.append(value)
        out.append(tuple(row))
    return tuple(out)


def bank_gate(registers, payload, kind, dst, src=None, coefficient=1):
    """Build a literal complete bank operation, including dirty directions."""
    v = len(payload)
    result = [list(row) for row in eye(registers * v)]
    if kind in ('apply', 'clear', 'copy'):
        for i in range(v):
            result[dst*v+i] = [G(0) for _ in range(registers * v)]
    if kind in ('apply', 'add', 'copy'):
        source = dst if kind == 'apply' else src
        for i in range(v):
            for j in range(v):
                result[dst*v+i][source*v+j] += coefficient * payload[i][j]
    else:
        need(kind == 'clear', 'bank operation kind')
    return tuple(map(tuple, result))


def cross_rank(a, inside, output_inside=None):
    selected = set(inside if output_inside is None else output_inside)
    return rank(tuple(tuple(row[j] for j in inside)
                      for i, row in enumerate(a) if i not in selected))
