"""Independent full-convolution Q8 arithmetic and finite census oracle."""

from itertools import product


def require(condition, message):
    if not condition:
        raise ValueError(message)


def hamilton(a, b):
    w, x, y, z = a
    v, p, q, r = b
    return (
        w * v - x * p - y * q - z * r,
        w * p + x * v + y * r - z * q,
        w * q - x * r + y * v + z * p,
        w * r + x * q - y * p + z * v,
    )


def tables():
    axes = [(1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)]
    elements = [tuple(sign * x for x in axis) for axis in axes for sign in (1, -1)]
    group = [[elements.index(hamilton(a, b)) for b in elements] for a in elements]
    multiply = [[0] * 256 for _ in range(256)]
    for a in range(1, 256):
        low = a & -a
        g = low.bit_length() - 1
        for b in range(256):
            term = 0
            for h in range(8):
                if b >> h & 1:
                    term ^= 1 << group[g][h]
            multiply[a][b] = multiply[a ^ low][b] ^ term
    return group, multiply


def identity(r):
    return tuple(1 if a == b else 0 for a in range(r) for b in range(r))


def factors(r, inverse=False):
    require(1 <= r <= 4, "role limit")
    return [
        tuple(
            (int(a == b) ^ ((1 ^ (1 << g)) if u >> a & v >> b & 1 else 0))
            for a in range(r)
            for b in range(r)
        )
        for u in range(1, 1 << r)
        for v in range(1, 1 << r)
        if (u & v).bit_count() % 2
        for g in (2 + int(inverse), 4 + int(inverse))
    ]


def matmul(a, b, r, multiply):
    out = []
    for row in range(r):
        for col in range(r):
            value = 0
            for mid in range(r):
                value ^= multiply[a[row * r + mid]][b[mid * r + col]]
            out.append(value)
    return tuple(out)


def diagonal(target):
    r = len(target)
    return tuple(1 << target[a] if a == b else 0 for a in range(r) for b in range(r))


def pack(a, r):
    return b"".join(
        bytes(a[row * r : (row + 1) * r]) + b"\0" * (4 - r) for row in range(r)
    ) + b"\0" * (16 - 4 * r)


def unpack(data, r):
    require(len(data) == 16, "state size")
    require(
        all(x == 0 for row in range(r) for x in data[4 * row + r : 4 * row + 4]),
        "column padding",
    )
    require(not any(data[4 * r :]), "row padding")
    return tuple(data[4 * row + col] for row in range(r) for col in range(r))


def ball(r, depth, inverse, multiply):
    require(0 <= depth <= (2 if r == 4 else 3), "oracle stored depth limit")
    seen = {identity(r)}
    frontier = seen
    alphabet = factors(r, inverse)
    for _ in range(depth):
        following = {matmul(a, f, r, multiply) for a in frontier for f in alphabet}
        frontier = following - seen
        seen |= following
    return seen


def target_lists():
    out = {}
    for r in (3, 4):
        for target in product((0, 2, 3, 4, 5), repeat=r):
            active = r - target.count(0)
            negative = target.count(3) + target.count(5)
            if (
                r == 3
                and active == 3
                and negative >= 2
                or r == 4
                and active == 3
                and negative == 2
                or r == 4
                and active == 2
                and negative == 2
            ):
                out[target] = active + 2 * negative
    return out


def representative(target):
    direct = tuple(sorted(target))
    swap = {0: 0, 2: 4, 3: 5, 4: 2, 5: 3}
    return min(direct, tuple(sorted(swap[x] for x in target)))


def direct_word(target):
    r = len(target)
    alphabet = factors(r)
    labels = [
        (u, v, g)
        for u in range(1, 1 << r)
        for v in range(1, 1 << r)
        if (u & v).bit_count() % 2
        for g in (2, 4)
    ]
    word = []
    for coordinate, g in enumerate(target):
        for _ in range(3 if g in (3, 5) else int(g != 0)):
            word.append(
                alphabet[labels.index((1 << coordinate, 1 << coordinate, g & ~1))]
            )
    return word
