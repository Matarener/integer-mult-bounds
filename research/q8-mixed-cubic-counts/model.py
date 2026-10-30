"""Exact binary call-space arithmetic. Nick Petalas. Apache-2.0."""

from itertools import product


def require(ok, message):
    if not ok:
        raise ValueError(message)


def identity(n):
    return tuple(1 << k for k in range(n))


def add(a, b):
    require(len(a) == len(b), "matrix row mismatch")
    return tuple(x ^ y for x, y in zip(a, b, strict=True))


def multiply(a, b):
    require(len(a) <= 16 and len(b) <= 16, "matrix capacity")
    require(all(0 <= row < 1 << len(b) for row in a), "matrix shape")
    out = []
    for row in a:
        value = 0
        for k in range(len(b)):
            if row >> k & 1:
                value ^= b[k]
        out.append(value)
    return tuple(out)


def rank(rows):
    require(len(rows) <= 16 and all(0 <= x < 1 << 16 for x in rows), "rank capacity")
    pivots = [0] * 16
    result = 0
    for original in rows:
        row = original
        for k in range(15, -1, -1):
            if not row >> k & 1:
                continue
            if pivots[k]:
                row ^= pivots[k]
            else:
                pivots[k] = row
                result += 1
                break
    return result


def validate(roles, word):
    require(type(roles) is int and 1 <= roles <= 6, "role domain")
    require(isinstance(word, (list, tuple)) and len(word) <= 16, "word capacity")
    for gate in word:
        require(isinstance(gate, (list, tuple)) and len(gate) == 3, "gate shape")
        u, v, label = gate
        require(all(type(x) is int for x in gate), "gate integer domain")
        require(0 < u < 1 << roles and 0 < v < 1 << roles, "vector domain")
        require(label in (0, 1) and (u & v).bit_count() % 2 == 1, "paid gate domain")


def call_matrices(roles, word):
    validate(roles, word)
    n = len(word)
    x = tuple(sum(((u >> r) & 1) << k for k, (u, _, _) in enumerate(word))
              for r in range(roles))
    y = tuple(v for _, v, _ in word)
    a = multiply(y, x)
    lower = tuple(row & ((1 << k) - 1) for k, row in enumerate(a))
    ei = tuple((1 << k) if label == 0 else 0 for k, (_, _, label) in enumerate(word))
    ej = add(identity(n), ei)
    forbidden = multiply(multiply(ei, lower), ej)
    h = add(lower, forbidden)
    correction = multiply(multiply(multiply(ei, lower), lower), ej)
    cubic = add(multiply(h, h), correction)
    return x, y, lower, h, correction, cubic


def predicted(roles, word):
    x, y, _, h, _, cubic = call_matrices(roles, word)
    return (multiply(x, y), multiply(multiply(x, h), y),
            multiply(multiply(x, cubic), y))


def count_constraints(ti, tj, ni, nj):
    require(all(type(x) is int and 0 <= x <= 64 for x in (ti, tj, ni, nj)),
            "count domain")
    t = ti + tj
    require(1 <= t <= 32, "target capacity")
    return (ni >= ti and nj >= tj and (ni - ti) % 2 == 0 and (nj - tj) % 2 == 0
            and ni + nj >= 2 * t and 2 * ni + nj >= 3 * t and ni + 2 * nj >= 3 * t)


def count_floor(ti, tj):
    require(type(ti) is int and type(tj) is int and 1 <= ti + tj <= 16
            and min(ti, tj) >= 0, "floor domain")
    t = ti + tj
    return min(ni + nj for ni, nj in product(range(3 * t + 1), repeat=2)
               if count_constraints(ti, tj, ni, nj))
