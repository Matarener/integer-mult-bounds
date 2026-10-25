"""Fresh table-based finite model. No predecessor executable is imported.

Chris R / Clear1nsight with substantial OpenAI Codex assistance. Apache-2.0.
Definitions retain Nick Petalas, David Arias and the E8/P112 lineage.
"""

import ast
from fractions import Fraction
from itertools import combinations, product

SIMPLE = ((1, -1, -1, -1, -1, -1, -1, 1), (2, 2, 0, 0, 0, 0, 0, 0),
          (-2, 2, 0, 0, 0, 0, 0, 0), (0, -2, 2, 0, 0, 0, 0, 0),
          (0, 0, -2, 2, 0, 0, 0, 0), (0, 0, 0, -2, 2, 0, 0, 0),
          (0, 0, 0, 0, -2, 2, 0, 0), (0, 0, 0, 0, 0, -2, 2, 0))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b, strict=True))


def canonical(row):
    return row if next(x for x in row if x) > 0 else tuple(-x for x in row)


def basis(values, width=9):
    rows = [0] * width
    for value in values:
        for j in range(width - 1, -1, -1):
            if value >> j & 1:
                if rows[j]:
                    value ^= rows[j]
                else:
                    rows[j] = value
                    break
    return [row for row in rows if row]


def span(rows):
    values = [0]
    for row in rows:
        values += [x ^ row for x in values]
    return values


def solve(matrix, columns):
    """Exact dense simultaneous solve, independent of triangular source formulas."""
    n = len(matrix)
    a = [[Fraction(x) for x in row] + [Fraction(c[i]) for c in columns]
         for i, row in enumerate(matrix)]
    for j in range(n):
        p = next(i for i in range(j, n) if a[i][j])
        a[j], a[p] = a[p], a[j]
        scale = a[j][j]
        a[j] = [x / scale for x in a[j]]
        for i in range(n):
            if i != j:
                scale = a[i][j]
                a[i] = [x - scale * y for x, y in zip(a[i], a[j], strict=True)]
    return [tuple(row[j] for row in a) for j in range(n, len(a[0]))]


def reconstruct(table, geometry):
    assignments = ast.parse(geometry).body
    literal = next(ast.literal_eval(n.value) for n in assignments
                   if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == 'SIMPLE' for t in n.targets))
    require(literal == SIMPLE, 'simple-system definition binding')
    lines = table.decode().splitlines()
    live = [tuple(map(int, line.split())) for line in lines[2:114]]
    original_labels = list(map(int, lines[0].split()))
    frame = [tuple(2 * (i == a) + s * 2 * (i == a + 1) for i in range(8))
             for a in (0, 2, 4, 6) for s in (-1, 1)]
    roots = sorted(live + frame)
    shell = {tuple(2 * (k == i) + s * (k == j) for k in range(8))
             for i, j in combinations(range(8), 2) for s in (-2, 2)}
    shell.update((1, *t) for t in product((-1, 1), repeat=7) if sum(t) % 4 == 3)
    require(roots == sorted(shell) and len(roots) == 120, 'full E8 root patterns')
    coordinates = solve(list(zip(*SIMPLE, strict=True)), roots)
    require(all(x.denominator == 1 for c in coordinates for x in c), 'integral coordinates')
    coordinates = [tuple(map(int, c)) for c in coordinates]
    require(all(tuple(sum(c[i] * SIMPLE[i][j] for i in range(8)) for j in range(8)) == r
                for r, c in zip(roots, coordinates, strict=True)), 'exact coordinate equations')
    require(all(min(c) >= 0 or max(c) <= 0 for c in coordinates), 'simple-coordinate signs')
    labels = [1 + sum((x % 2) << (i + 1) for i, x in enumerate(c)) for c in coordinates]
    require(len(set(labels)) == 120 and all(x & 1 for x in labels), 'full affine labels')
    require([x for r, x in zip(roots, labels) if r not in frame] == original_labels,
            'original caller label convention')
    live_mask = sum(1 << i for i, r in enumerate(roots) if r in live)
    require(live_mask.bit_count() == 112 and live == sorted(live), 'literal P112 frame')
    require(all(sum(r[i] * r[j] for r in live) == 112 * (i == j)
                for i in range(8) for j in range(8)), 'evaluation Gram')
    return roots, labels, coordinates, live_mask


def annihilators(n, dimension):
    """Unique reduced row-echelon annihilators, highest pivot convention."""
    for pivots in combinations(range(n), n - dimension):
        choices = []
        for pivot in pivots:
            free = [j for j in range(pivot) if j not in pivots]
            choices.append([(1 << pivot) | sum(((c >> k) & 1) << j
                            for k, j in enumerate(free)) for c in range(1 << len(free))])
        yield from product(*choices)


def kernels(labels, ambient):
    locations = {x: i for i, x in enumerate(span(ambient))}
    inside = [(i, locations[x]) for i, x in enumerate(labels) if x in locations]
    return [sum(1 << i for i, x in inside if (h & x).bit_count() % 2 == 0)
            for h in range(1 << len(ambient))]


def masks(ker, rows):
    for annihilator in rows:
        mask = ker[0]
        for h in annihilator:
            mask &= ker[h]
        yield mask


def projective_fibers(roots, a, b):
    from math import gcd
    fibers = {}
    for i, r in enumerate(roots):
        x, y = dot(a, r), dot(b, r)
        if x or y:
            divisor = gcd(x, y)
            key = canonical((x // divisor, y // divisor))
            fibers[key] = fibers.get(key, 0) | (1 << i)
    return fibers


def all_a2(roots):
    lookup = {r: i for i, r in enumerate(roots)}
    planes = set()
    for i, j in combinations(range(120), 2):
        pairing = dot(roots[i], roots[j])
        if abs(pairing) != 4:
            continue
        third = canonical(tuple(x - (1 if pairing > 0 else -1) * y
                                for x, y in zip(roots[i], roots[j], strict=True)))
        require(third in lookup, 'A2 third root')
        planes.add(tuple(sorted((i, j, lookup[third]))))
    require(len(planes) == 1120, 'complete A2 plane inventory')
    fibers = set()
    for plane in sorted(planes):
        a, b = (roots[i] for i in plane[:2])
        classes = projective_fibers(roots, a, b)
        require(sorted(m.bit_count() for m in classes.values()) == [1, 1, 1, 27, 27, 27],
                'all nonzero A2 projective classes')
        fibers.update(m for m in classes.values() if m.bit_count() == 27)
    require(len(fibers) == 3360, 'distinct large A2 fibers')
    return sorted(planes), sorted(fibers)
