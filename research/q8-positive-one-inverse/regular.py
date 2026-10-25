"""Faithful regular-action check using Hamilton coordinates, without model imports.

Nick Petalas. Apache-2.0.
"""

QUATERNIONS = (
    (1, 0, 0, 0),
    (-1, 0, 0, 0),
    (0, 1, 0, 0),
    (0, -1, 0, 0),
    (0, 0, 1, 0),
    (0, 0, -1, 0),
    (0, 0, 0, 1),
    (0, 0, 0, -1),
)


def multiply(left, right):
    a, b, c, d = left
    e, f, g, h = right
    return (
        a * e - b * f - c * g - d * h,
        a * f + b * e + c * h - d * g,
        a * g - b * h + c * e + d * f,
        a * h + b * g - c * f + d * e,
    )


def act(group, mask):
    result = 0
    for h, quaternion in enumerate(QUATERNIONS):
        if mask >> h & 1:
            result ^= 1 << QUATERNIONS.index(multiply(QUATERNIONS[group], quaternion))
    return result


def columns(word, roles):
    """Apply the reversed chronological factors to every dirty basis input."""
    results = []
    for source in range(roles * 8):
        values = [0] * roles
        values[source // 8] = 1 << (source % 8)
        for g, u, v in reversed(word):
            collected = 0
            for a in range(roles):
                if v >> a & 1:
                    collected ^= values[a]
            delta = act(g, collected) ^ collected
            for a in range(roles):
                if u >> a & 1:
                    values[a] ^= delta
        results.append(tuple(values))
    return tuple(results)


def formal_columns(matrix, roles):
    result = []
    for source in range(roles * 8):
        column = []
        for a in range(roles):
            value = 0
            coefficient = matrix[a * roles + source // 8]
            for g in range(8):
                if coefficient >> g & 1:
                    value ^= act(g, 1 << (source % 8))
            column.append(value)
        result.append(tuple(column))
    return tuple(result)
