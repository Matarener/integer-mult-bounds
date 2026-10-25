"""Bounded exact binary and full formal Q8 arithmetic. Apache-2.0."""
from functools import reduce
from operator import xor

MAX_ROLES = 8
MAX_CALLS = 24
BASIS = (1, 3, 5, 17, 15, 51, 85, 255)
TABLE = ((0, 1, 2, 3), (1, 4, 3, 6),
         (2, 7, 4, 1), (3, 2, 5, 4))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def parity(n):
    return n.bit_count() & 1


def rank(rows):
    pivots = {}
    for value in rows:
        for _ in range(value.bit_length() + 1):
            if not value:
                break
            pivot = value.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = value
                break
            value ^= pivots[pivot]
    return len(pivots)


def mul(a, b):
    require(type(a) is int and type(b) is int and 0 <= a < 256
            and 0 <= b < 256, 'group-algebra byte domain')
    result = 0
    for g in range(8):
        for h in range(8):
            if (a >> g) & (b >> h) & 1:
                result ^= 1 << (TABLE[g & 3][h & 3] ^ (g & 4) ^ (h & 4))
    return result


def coordinates(value):
    result = 0
    for mask in range(256):
        if reduce(xor, (BASIS[k] for k in range(8) if mask >> k & 1), 0) == value:
            result = mask
            break
    else:
        raise ValueError('basis does not span')
    return result


def validate(roles, word):
    require(type(roles) is int and 1 <= roles <= MAX_ROLES, 'role capacity')
    require(type(word) is tuple and len(word) <= MAX_CALLS, 'call capacity')
    for gate in word:
        require(type(gate) is tuple and len(gate) == 3, 'gate shape')
        g, u, v = gate
        require(type(g) is int and g in (1, 2), 'positive paid label')
        require(type(u) is int and type(v) is int and 0 < u < 1 << roles
                and 0 < v < 1 << roles and parity(u & v), 'rank-one idempotent')


def endpoint(roles, word):
    validate(roles, word)
    result = [[int(a == b) for b in range(roles)] for a in range(roles)]
    for g, u, v in word:
        row = [reduce(xor, (result[a][b] for a in range(roles) if v >> a & 1), 0)
               for b in range(roles)]
        for a in range(roles):
            if u >> a & 1:
                result[a] = [old ^ mul(1 ^ (1 << g), value)
                             for old, value in zip(result[a], row, strict=True)]
    return result


def bm(a, b):
    return tuple(reduce(xor, (b[k] for k in range(len(b)) if row >> k & 1), 0)
                 for row in a)


def bx(a, b):
    require(len(a) == len(b), 'matrix shape')
    return tuple(x ^ y for x, y in zip(a, b, strict=True))


def identity(size):
    return tuple(1 << a for a in range(size))


def call_matrices(roles, word):
    validate(roles, word)
    n = len(word)
    x = tuple(sum(1 << k for k in range(n) if word[k][1] >> a & 1)
              for a in range(roles))
    y = tuple(gate[2] for gate in word)
    ell = tuple(sum(parity(word[b][2] & word[a][1]) << a for a in range(b))
                for b in range(n))
    ei = tuple((1 << a) if word[a][0] == 1 else 0 for a in range(n))
    ej = bx(identity(n), ei)
    h = bx(ell, bm(bm(ei, ell), ej))
    hp = bx(ell, bm(bm(ej, ell), ei))
    return x, y, ell, ei, ej, h, hp


def coefficient(matrix, bit):
    return tuple(sum(((coordinates(value) >> bit) & 1) << b
                     for b, value in enumerate(row)) for row in matrix)


def lower_bound(t):
    require(type(t) is int and 1 <= t <= 1_000_000, 'target domain')
    bound = (5 * t + 1) // 2
    return bound + ((bound - t) & 1)


def allowed_counts(t, ni, nj):
    require(type(t) is int and 1 <= t <= 1_000_000, 'target domain')
    require(type(ni) is int and type(nj) is int
            and 0 <= ni <= 3_000_000 and 0 <= nj <= 3_000_000, 'count domain')
    return (2 * ni + nj >= 4 * t and 2 * ni + 3 * nj >= 6 * t
            and (ni - t) % 2 == 0 and nj % 2 == 0)
