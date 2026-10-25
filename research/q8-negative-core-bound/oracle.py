"""Independent Hamilton packet action and finite three-role meet. Apache-2.0."""

from itertools import product

RIGHT_I = (1, 4, 7, 2, 5, 0, 3, 6)
RIGHT_J = (2, 3, 4, 5, 6, 7, 0, 1)
LEFT_I = (1, 4, 3, 6, 5, 0, 7, 2)
LEFT_J = (2, 7, 4, 1, 6, 3, 0, 5)


def permutation_table(permutation):
    return tuple(sum(((packet >> h) & 1) << permutation[h] for h in range(8))
                 for packet in range(256))


def compose(a, b):
    return tuple(a[b[k]] for k in range(8))


def group_permutations():
    identity = tuple(range(8))
    z = compose(LEFT_I, LEFT_I)
    k = compose(LEFT_I, LEFT_J)
    return (identity, LEFT_I, LEFT_J, k, z, compose(z, LEFT_I),
            compose(z, LEFT_J), compose(z, k))


def binary_product(a, b):
    n = len(a)
    return tuple(sum((sum(((a[r] >> k) & 1) * ((b[k] >> c) & 1)
                         for k in range(n)) % 2) << c for c in range(n))
                 for r in range(n))


def span_rank(rows):
    span = {0}
    for row in rows:
        span |= {x ^ row for x in span}
    return len(span).bit_length() - 1


def endpoint(rows, labels):
    """Full formal T*A, left action, independently of the quotient algebra."""
    n = len(rows)
    state = [[(rows[r] >> c) & 1 for c in range(n)] for r in range(n)]
    tables = {1: permutation_table(LEFT_I), 2: permutation_table(LEFT_J)}
    for call, label in enumerate(labels):
        delta = [packet ^ tables[label][packet] for packet in state[call]]
        for r in range(n):
            if rows[r] >> call & 1:
                state[r] = [a ^ b for a, b in zip(state[r], delta, strict=True)]
    return tuple(tuple(row) for row in state)


def physical_endpoint(word, width):
    state = [[int(r == c) for c in range(width)] for r in range(width)]
    tables = {1: permutation_table(LEFT_I), 2: permutation_table(LEFT_J)}
    for u, v, label in word:
        accumulated = [0] * width
        for k in range(width):
            if v >> k & 1:
                accumulated = [a ^ b for a, b in zip(accumulated, state[k], strict=True)]
        delta = [p ^ tables[label][p] for p in accumulated]
        for k in range(width):
            if u >> k & 1:
                state[k] = [a ^ b for a, b in zip(state[k], delta, strict=True)]
    return tuple(tuple(row) for row in state)


def grams(n):
    choices = []
    for r in range(n):
        others = tuple(c for c in range(n) if c != r)
        choices.append(tuple((1 << r) | sum(((v >> k) & 1) << c
                                           for k, c in enumerate(others))
                             for v in range(1 << (n - 1))))
    return product(*choices)


def factors():
    return tuple((u, v, label) for u in range(1, 8) for v in range(1, 8)
                 if (u & v).bit_count() % 2 for label in range(2))


def step(state, factor, tables):
    u, v, label = factor
    result = []
    for row in state:
        packet = 0
        for k in range(3):
            if u >> k & 1:
                packet ^= (row >> (8 * k)) & 255
        delta = packet ^ tables[label][packet]
        result.append(row ^ sum(delta << (8 * k) for k in range(3) if v >> k & 1))
    return tuple(result)


def ball(tables):
    identity = (1, 1 << 8, 1 << 16)
    seen, frontier = {identity}, {identity}
    for _ in range(3):
        following = {step(state, factor, tables) for state in frontier for factor in factors()}
        frontier = following - seen
        seen |= frontier
    return seen


def target_right(state, target, tables):
    return tuple(sum(tables[g][(row >> (8 * k)) & 255] << (8 * k)
                     for k, g in enumerate(target)) for row in state)


def native_bytes(states):
    """Convert Hamilton packets to the retained native encoding before sorting."""
    permutation = (0, 2, 4, 6, 1, 3, 5, 7)
    conversion = permutation_table(permutation)
    converted = [tuple(sum(conversion[(row >> (8 * k)) & 255] << (8 * k)
                           for k in range(3)) for row in state) for state in states]
    return b"".join(b"".join(row.to_bytes(4, "little") for row in (*state, 0))
                    for state in sorted(converted))


def complete_meet():
    right_i = permutation_table(RIGHT_I)
    right_j = permutation_table(RIGHT_J)
    forward = (right_i, right_j)
    backward = tuple(tuple(t[t[t[p]]] for p in range(256)) for t in forward)
    prefix, inverse = ball(forward), ball(backward)
    # Right multiplication by g sends h to h*g, independently of the C++ table.
    group = group_permutations()
    right_groups = tuple(permutation_table(tuple(group[h][g] for h in range(8)))
                         for g in range(8))
    wanted = [{target_right(state, target, right_groups) for state in inverse}
              for target in ((5, 5, 5), (5, 5, 6))]
    hits = [0, 0]
    candidates = 0
    for state in prefix:
        for current in (state, *(step(state, f, forward) for f in factors())):
            for k in range(2):
                hits[k] += current in wanted[k]
            candidates += 1
    return {"inverse": inverse, "prefix": prefix, "hits": hits, "candidates": candidates}
