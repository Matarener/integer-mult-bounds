"""Bounded exact binary, quaternion and quotient arithmetic. Apache-2.0."""

MAX_ROLES = 16
MAX_CALLS = 48


def require(ok, message):
    if not ok:
        raise ValueError(message)


def validate(word, roles):
    require(type(roles) is int and 1 <= roles <= MAX_ROLES, "role bound")
    require(len(word) <= MAX_CALLS, "call bound")
    for gate in word:
        require(len(gate) == 3, "gate shape")
        u, v, g = gate
        require(all(type(x) is int for x in gate), "gate integer type")
        require(0 < u < 1 << roles and 0 < v < 1 << roles, "vector range")
        require(g in (1, 2), "positive i/j labels only")
        require((u & v).bit_count() % 2 == 1, "rank-one idempotence")


def multiply(a, b):
    out = []
    for row in a:
        value = 0
        for k, other in enumerate(b):
            if row >> k & 1:
                value ^= other
        out.append(value)
    return tuple(out)


def rank(rows):
    require(len(rows) <= MAX_ROLES * 8, "rank row bound")
    require(all(type(row) is int and 0 <= row < 1 << (MAX_ROLES * 8) for row in rows),
            "rank vector bound")
    basis = {}
    for original in rows:
        value = original
        for bit in range(MAX_ROLES * 8 - 1, -1, -1):
            if value >> bit & 1:
                if bit in basis:
                    value ^= basis[bit]
                else:
                    basis[bit] = value
                    break
    return len(basis)


def group_product(g, h):
    a, b = g & 3, h & 3
    negative = (a, b) in ((1, 1), (2, 2), (3, 3), (2, 1), (3, 2), (1, 3))
    return (a ^ b) | (((g >> 2) ^ (h >> 2) ^ negative) << 2)


def shift(packet, g):
    return sum(1 << group_product(g, h) for h in range(8) if packet >> h & 1)


def full_endpoint(word, roles):
    validate(word, roles)
    matrix = [tuple(1 if a == b else 0 for b in range(roles)) for a in range(roles)]
    for u, v, g in word:
        combined = []
        for c in range(roles):
            value = 0
            for k in range(roles):
                if v >> k & 1:
                    value ^= matrix[k][c]
            combined.append(value ^ shift(value, g))
        matrix = [tuple(value ^ (combined[c] if u >> a & 1 else 0)
                        for c, value in enumerate(row)) for a, row in enumerate(matrix)]
    return tuple(matrix)


def quotient_product(left, right):
    require(type(left) is int and type(right) is int, "quotient integer type")
    require(0 <= left < 32 and 0 <= right < 32, "quotient range")
    table = {(1, 1): 8, (2, 2): 8, (1, 2): 16, (2, 1): 24}
    value = 0
    for a in range(5):
        for b in range(5):
            if (left >> a & 1) and (right >> b & 1):
                value ^= (1 << b) if a == 0 else (1 << a) if b == 0 else table.get((a, b), 0)
    return value


def images():
    i, j, z = 3, 5, 9
    k = quotient_product(i, j)
    return (1, i, j, k, z, quotient_product(z, i),
            quotient_product(z, j), quotient_product(z, k))


def project(matrix):
    out = []
    group_images = images()
    for row in matrix:
        projected = []
        for packet in row:
            value = 0
            for g, image in enumerate(group_images):
                if packet >> g & 1:
                    value ^= image
            projected.append(value)
        out.append(tuple(projected))
    return tuple(out)


def polynomial(word, roles):
    """All-i specialization in F2[x]/(x^4), with x=[i]+1."""
    validate(word, roles)
    require(all(g == 1 for _, _, g in word), "cyclic polynomial label")
    coefficients = [tuple(1 << k for k in range(roles))] + [(0,) * roles] * 3
    for u, v, _ in word:
        projector = tuple(v if u >> k & 1 else 0 for k in range(roles))
        coefficients = [coefficients[0]] + [tuple(a ^ b for a, b in zip(
            coefficients[d], multiply(projector, coefficients[d - 1]), strict=True))
            for d in range(1, 4)]
    return tuple(coefficients)


def gram(word):
    return tuple(sum(((v & u).bit_count() % 2) << k for k, (u, _, _) in enumerate(word))
                 for _, v, _ in word)


def chronological(rows, labels):
    return tuple(sum(((rows[b] >> a) & 1) << a for a in range(b)
                     if (labels[b], labels[a]) != (1, 2)) for b in range(len(rows)))
