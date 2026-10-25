"""Bounded exact F2[Q8] arithmetic, independent of the retained native engine."""

from itertools import product


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dot(a, b):
    return (a & b).bit_count() % 2


def group_table():
    axes = ((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1))
    elements = [tuple(s * x for x in a) for a in axes for s in (1, -1)]
    result = []
    for a in elements:
        row = []
        w, x, y, z = a
        for b in elements:
            v, p, q, r = b
            c = (
                w * v - x * p - y * q - z * r,
                w * p + x * v + y * r - z * q,
                w * q - x * r + y * v + z * p,
                w * r + x * q - y * p + z * v,
            )
            row.append(elements.index(c))
        result.append(row)
    return result


GROUP = group_table()


def ring_table():
    result = [[0] * 256 for _ in range(256)]
    for a in range(256):
        for b in range(256):
            value = 0
            for g in range(8):
                if a >> g & 1:
                    for h in range(8):
                        if b >> h & 1:
                            value ^= 1 << GROUP[g][h]
            result[a][b] = value
    return result


MULTIPLY = ring_table()


def identity(r):
    return tuple(int(a == b) for a in range(r) for b in range(r))


def diagonal(target):
    r = len(target)
    return tuple(1 << target[a] if a == b else 0 for a in range(r) for b in range(r))


def factor(call, r):
    u, v, g = call
    return tuple(
        int(a == b) ^ ((1 ^ (1 << g)) if u >> a & v >> b & 1 else 0)
        for a in range(r)
        for b in range(r)
    )


def matmul(a, b, r):
    out = []
    for row in range(r):
        for col in range(r):
            value = 0
            for k in range(r):
                value ^= MULTIPLY[a[row * r + k]][b[k * r + col]]
            out.append(value)
    return tuple(out)


def evaluate(word, r):
    result = identity(r)
    for call in word:
        result = matmul(result, factor(call, r), r)
    return result


def alphabet(r):
    require(1 <= r <= 4, "alphabet role limit")
    return tuple(
        (u, v, g)
        for u in range(1, 1 << r)
        for v in range(1, 1 << r)
        if dot(u, v)
        for g in (2, 4)
    )


def validate(word, target):
    r = len(target)
    require(1 <= r <= 12 and len(word) <= 48, "role/call limit")
    require(all(type(g) is int and 0 <= g < 8 for g in target), "target label")
    for call in word:
        require(len(call) == 3, "call shape")
        u, v, g = call
        require(all(type(x) is int for x in call), "call integer type")
        require(0 < u < 1 << r and 0 < v < 1 << r, "call vector")
        require(g in (2, 4) and dot(u, v) == 1, "positive idempotent call")
    require(evaluate(word, r) == diagonal(target), "full dirty endpoint")


def direct_word(target):
    spellings = ((), (2, 2), (2,), (2, 2, 2), (4,), (4, 4, 4), (2, 4), (4, 2))
    return tuple(
        (1 << a, 1 << a, g) for a, label in enumerate(target) for g in spellings[label]
    )


def diagonal_target(matrix, r):
    if any(matrix[a * r + b] for a in range(r) for b in range(r) if a != b):
        return None
    labels = [matrix[a * r + a] for a in range(r)]
    if any(x == 0 or x & (x - 1) for x in labels):
        return None
    return tuple(x.bit_length() - 1 for x in labels)


def short_words():
    for r, horizon in ((1, 7), (2, 3), (3, 2)):
        letters = alphabet(r)
        for depth in range(horizon + 1):
            for word in product(letters, repeat=depth):
                yield r, word
