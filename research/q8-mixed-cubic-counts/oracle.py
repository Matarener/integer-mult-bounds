"""Independent Hamilton multiplication and faithful dirty action. Apache-2.0."""

from itertools import product

from model import require, validate

GROUP = ((0, 1, 2, 3, 4, 5, 6, 7),
         (1, 4, 3, 6, 5, 0, 7, 2),
         (2, 7, 4, 1, 6, 3, 0, 5),
         (3, 2, 5, 4, 7, 6, 1, 0),
         (4, 5, 6, 7, 0, 1, 2, 3),
         (5, 0, 7, 2, 1, 4, 3, 6),
         (6, 3, 0, 5, 2, 7, 4, 1),
         (7, 6, 1, 0, 3, 2, 5, 4))
BASIS = (1, 3, 5, 17, 15, 51, 85, 255)


def algebra(a, b):
    require(type(a) is int and type(b) is int and 0 <= a < 256 and 0 <= b < 256,
            "group algebra domain")
    out = 0
    for i, j in product(range(8), repeat=2):
        if (a >> i & 1) and (b >> j & 1):
            out ^= 1 << GROUP[i][j]
    return out


def coordinates():
    out = [0] * 256
    seen = set()
    for mask in range(256):
        value = 0
        for k in range(8):
            if mask >> k & 1:
                value ^= BASIS[k]
        require(value not in seen, "dependent augmentation basis")
        seen.add(value)
        out[value] = mask
    return tuple(out)


def left_generator(value, label):
    out = 0
    for k in range(8):
        if value >> k & 1:
            out ^= 1 << GROUP[label + 1][k]
    return out


def act(roles, word, source, group):
    validate(roles, word)
    require(type(source) is int and 0 <= source < roles and type(group) is int
            and 0 <= group < 8, "column domain")
    column = [0] * roles
    column[source] = 1 << group
    for u, v, label in word:
        read = 0
        for r in range(roles):
            if v >> r & 1:
                read ^= column[r]
        change = read ^ left_generator(read, label)
        for r in range(roles):
            if u >> r & 1:
                column[r] ^= change
    return tuple(column)


def coefficients(roles, word, conversion):
    out = [[0] * roles for _ in range(3)]
    for source in range(roles):
        column = act(roles, word, source, 0)
        for row, value in enumerate(column):
            c = conversion[value]
            for slot, bit in enumerate(((c >> 1 ^ c >> 2) & 1,
                                      (c >> 3) & 1, (c >> 5 ^ c >> 6) & 1)):
                out[slot][row] |= bit << source
    return tuple(tuple(rows) for rows in out)
