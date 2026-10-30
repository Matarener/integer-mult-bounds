"""Independent Hamilton action on every dirty basis column. Apache-2.0."""


def group_product(g, h):
    sign = (g // 4) ^ (h // 4)
    a, b = g % 4, h % 4
    if not a or not b:
        basis = a + b
    elif a == b:
        basis, sign = 0, sign ^ 1
    else:
        basis = 6 - a - b
        sign ^= int((a, b) not in ((1, 2), (2, 3), (3, 1)))
    return basis + 4 * sign


def action(roles, word, column):
    values = [0] * roles
    values[column // 8] = 1 << (column % 8)
    for label, u, v in word:
        total = 0
        for a in range(roles):
            if v >> a & 1:
                total ^= values[a]
        change = total
        for h in range(8):
            if total >> h & 1:
                change ^= 1 << group_product(label, h)
        for a in range(roles):
            if u >> a & 1:
                values[a] ^= change
    return tuple(values)


def matrix_action(matrix, column):
    result = []
    for row in matrix:
        value = 0
        for g in range(8):
            if row[column // 8] >> g & 1:
                value ^= 1 << group_product(g, column % 8)
        result.append(value)
    return tuple(result)
