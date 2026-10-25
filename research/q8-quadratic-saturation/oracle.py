"""Independent signed-Hamilton action on every dirty input column. Apache-2.0."""


def hamilton(a, b):
    w, x, y, z = a
    s, t, u, v = b
    return (w*s-x*t-y*u-z*v, w*t+x*s+y*v-z*u,
            w*u-x*v+y*s+z*t, w*v+x*u-y*t+z*s)


def group_table():
    positive = tuple(tuple(int(k == j) for k in range(4)) for j in range(4))
    elements = positive + tuple(tuple(-x for x in q) for q in positive)
    return tuple(tuple(elements.index(hamilton(a, b)) for b in elements) for a in elements)


def action(word, roles, column):
    table = group_table()
    state = [int(k == column // 8) << (column % 8) for k in range(roles)]
    for u, v, g in word:
        value = 0
        for k in range(roles):
            if v >> k & 1:
                value ^= state[k]
        moved = 0
        for h in range(8):
            if value >> h & 1:
                moved ^= 1 << table[g][h]
        for k in range(roles):
            if u >> k & 1:
                state[k] ^= value ^ moved
    return tuple(state)


def span_rank(vectors):
    """Explicit finite span, independent of pivot elimination; <=8 generators."""
    if len(vectors) > 8 or any(type(x) is not int or not 0 <= x < 1 << 16 for x in vectors):
        raise ValueError("span capacity")
    span = {0}
    for vector in vectors:
        span |= {x ^ vector for x in tuple(span)}
    return len(span).bit_length() - 1
