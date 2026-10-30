"""Independent integer-lattice specification of the audited E8 configurations.

@CubeJerry, with OpenAI Codex assistance. Apache-2.0.
No predecessor executable is imported.
"""
from itertools import combinations, product
from math import gcd


def roots():
    """Enumerate norm-eight vectors in the doubled E8 lattice by norm budget."""
    inventory = []
    for parity in (0, 1):
        alphabet = tuple(x for x in range(-2, 3) if x % 2 == parity)
        # Meet in the middle: lattice membership, not a hard-coded root list.
        halves = tuple(product(alphabet, repeat=4))
        by_norm = {}
        for row in halves:
            by_norm.setdefault(sum(x*x for x in row), []).append(row)
        for norm, lefts in by_norm.items():
            for left in lefts:
                for right in by_norm.get(8 - norm, ()):
                    row = left + right
                    if sum(row) % 4 == 0:
                        inventory.append(row)
    signed = tuple(sorted(inventory))
    lines = tuple(row for row in signed if row > tuple(-x for x in row))
    return signed, lines


def dot(a, b):
    return sum(x*y for x, y in zip(a, b, strict=True))


def projection(row, anchor):
    """Primitive integer representative of 8r-(r.f)f, with positive leading term."""
    projected = tuple(8*x - dot(row, anchor)*y for x, y in zip(row, anchor))
    divisor = gcd(*projected)
    if divisor == 0 or divisor & (divisor - 1):
        raise ValueError("projection normalization is not a dyadic unit")
    primitive = tuple(x // divisor for x in projected)
    return max(primitive, tuple(-x for x in primitive))


def fixed_geometry():
    signed, lines = roots()
    anchor = (2, 2, 0, 0, 0, 0, 0, 0)
    f = lines.index(anchor)
    orthogonal = tuple(tuple(j for j, b in enumerate(lines) if dot(a, b) == 0)
                       for a in lines)
    neighbors = tuple(i for i, row in enumerate(lines) if i != f and dot(row, anchor))
    directions = tuple(sorted({projection(lines[i], anchor) for i in neighbors}))
    return signed, lines, f, orthogonal, neighbors, directions


def matrices():
    """Every case before the S3 rank condition; dependent triples remain explicit."""
    _, lines, f, orthogonal, neighbors, directions = fixed_geometry()
    anchor = lines[f]
    yield ("S1",), tuple(lines[i] for i in orthogonal[f])
    for u in range(len(lines)):
        if u == f:
            continue
        yield ("A2", u), (anchor, lines[u])
        common = tuple(i for i in orthogonal[f] if i in orthogonal[u])
        yield ("S2", u), tuple(lines[i] for i in common)
    for u, v in combinations(neighbors, 2):
        yield ("A3", u, v), (anchor, lines[u], lines[v])
        # Orthogonal complements are generated even for dependent triples.
        common = tuple(i for i in orthogonal[f] if i in orthogonal[u] and i in orthogonal[v])
        yield ("S3", u, v), tuple(lines[i] for i in common)
    for i, j, k in combinations(range(len(directions)), 3):
        yield ("W2", i, j, k), (directions[i], directions[j], directions[k])


def transport_numerator(target):
    """Return 4T, T an explicit dyadic isometry taking the anchor to target."""
    odd = target[0] % 2 != 0
    support = (0, 1) if odd else tuple(i for i, x in enumerate(target) if x)
    if len(support) != 2:
        raise ValueError("invalid integer-root support")
    i, j = support
    permutation = (i, j) + tuple(k for k in range(8) if k not in support)
    signs = [1] * 8
    signs[i] = 1 if target[i] > 0 else -1
    signs[j] = 1 if target[j] > 0 else -1
    if signs[i] * signs[j] == -1:
        signs[next(k for k in range(8) if k not in support)] = -1
    p = [[0] * 8 for _ in range(8)]
    for col, row in enumerate(permutation):
        p[row][col] = signs[row]
    if not odd:
        return [[4*x for x in row] for row in p]
    intermediate = tuple(2*signs[k] if k in support else 0 for k in range(8))
    h = tuple(a-b for a, b in zip(intermediate, target))
    # H_h = I-hh^T/4; multiply the signed permutation on the right.
    return [[sum((4*(row == mid)-h[row]*h[mid])*p[mid][col]
                 for mid in range(8)) for col in range(8)] for row in range(8)]
