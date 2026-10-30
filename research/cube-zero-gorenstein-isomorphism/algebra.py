"""Exact cube-zero local algebra classification over bounded odd prime fields.

Produced by Nick Petalas. Apache-2.0.
"""

from itertools import product


def need(condition, message):
    if not condition:
        raise ValueError(message)


def transpose(a):
    return [list(row) for row in zip(*a)]


def eye(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def mm(a, b, p):
    return [[sum(x * y for x, y in zip(row, col)) % p
             for col in zip(*b)] for row in a]


def mv(a, v, p):
    return [sum(x * y for x, y in zip(row, v)) % p for row in a]


def rref(a, p):
    a = [row[:] for row in a]
    pivots = []
    for j in range(len(a[0])):
        candidates = [i for i in range(len(pivots), len(a)) if a[i][j]]
        if not candidates:
            continue
        k = len(pivots)
        i = candidates[0]
        a[k], a[i] = a[i], a[k]
        a[k] = [(x * pow(a[k][j], -1, p)) % p for x in a[k]]
        for i in range(len(a)):
            if i != k:
                c = a[i][j]
                a[i] = [(x - c * y) % p for x, y in zip(a[i], a[k])]
        pivots.append(j)
        if len(pivots) == len(a):
            break
    return a, pivots


def inverse(a, p):
    n = len(a)
    b, pivots = rref([row + unit for row, unit in zip(a, eye(n))], p)
    need(pivots[:n] == list(range(n)), "singular matrix")
    return [row[n:] for row in b]


def kernel(a, p):
    b, pivots = rref(a, p)
    free = [j for j in range(len(a[0])) if j not in pivots]
    basis = []
    for j in free:
        v = [0] * len(a[0])
        v[j] = 1
        for i, k in enumerate(pivots):
            v[k] = -b[i][j] % p
        basis.append(v)
    return basis


def span_basis(vectors, p):
    if not vectors:
        return []
    _, pivots = rref(transpose(vectors), p)
    return [vectors[j] for j in pivots]


def determinant(a, p):
    a = [row[:] for row in a]
    value = 1
    for j in range(len(a)):
        candidates = [i for i in range(j, len(a)) if a[i][j]]
        if not candidates:
            return 0
        i = candidates[0]
        if i != j:
            a[i], a[j] = a[j], a[i]
            value = -value
        pivot = a[j][j]
        value = value * pivot % p
        for i in range(j + 1, len(a)):
            c = a[i][j] * pow(pivot, -1, p) % p
            a[i] = [(x - c * y) % p for x, y in zip(a[i], a[j])]
    return value


def multiply(t, a, b, p):
    n = len(t)
    return [sum(a[i] * b[j] * t[i][j][k]
                for i in range(n) for j in range(n)) % p
            for k in range(n)]


def algebra_power(t, a, exponent, unit, p):
    result = unit[:]
    for j in range(exponent.bit_length() - 1, -1, -1):
        result = multiply(t, result, result, p)
        if (exponent >> j) & 1:
            result = multiply(t, result, a, p)
    return result


def validate(t, p):
    need(type(p) is int and 3 <= p <= 31 and p % 2 == 1,
         "odd prime in [3,31] required")
    need(all(p % d for d in range(2, p)), "prime required")
    need(type(t) is list and 3 <= len(t) <= 10, "dimension in [3,10] required")
    n = len(t)
    need(all(type(row) is list and len(row) == n for row in t), "table shape")
    need(all(type(v) is list and len(v) == n for row in t for v in row),
         "table coefficient shape")
    need(all(type(x) is int and 0 <= x < p
             for row in t for v in row for x in v), "canonical coefficients")
    need(all(t[i][j] == t[j][i] for i in range(n) for j in range(n)),
         "commutativity")
    basis = eye(n)
    for i, j, k in product(range(n), repeat=3):
        need(multiply(t, t[i][j], basis[k], p)
             == multiply(t, basis[i], t[j][k], p), "associativity")
    equations = [[t[i][j][k] for i in range(n)] + [int(j == k)]
                 for j in range(n) for k in range(n)]
    rows, pivots = rref(equations, p)
    need(pivots == list(range(n)), "unique unit required")
    unit = [rows[i][-1] for i in range(n)]
    need(all(multiply(t, unit, v, p) == v for v in basis), "unit")
    return unit


def recover_form(t, p):
    unit = validate(t, p)
    n = len(t)
    exponent = next(p ** e for e in range(n + 1) if p ** e >= n)
    powers = [algebra_power(t, v, exponent, unit, p) for v in eye(n)]
    radical = kernel(transpose(powers), p)
    need(len(radical) == n - 1, "split local residue required")
    square = span_basis([multiply(t, a, b, p)
                         for a in radical for b in radical], p)
    need(len(square) == 1, "radical square must have dimension one")
    s = square[0]
    need(all(not any(multiply(t, a, s, p)) for a in radical), "radical cube")
    lifts = span_basis([s] + radical, p)[1:]
    chart = transpose([unit] + lifts + [s])
    chart_inverse = inverse(chart, p)
    form = []
    for a in lifts:
        row = []
        for b in lifts:
            coordinates = mv(chart_inverse, multiply(t, a, b, p), p)
            need(not any(coordinates[:-1]), "product outside radical square")
            row.append(coordinates[-1])
        form.append(row)
    need(determinant(form, p) != 0, "socle larger than radical square")
    return form, chart


def pairing(b, u, v, p):
    return sum(x * y for x, y in zip(u, mv(b, v, p))) % p


def combine(a, b, x, y, p):
    return [(a * s + b * t) % p for s, t in zip(x, y)]


def orthogonal_basis(b, p):
    remaining = eye(len(b))
    columns = []
    for _ in range(len(b)):
        pivots = [i for i, v in enumerate(remaining) if pairing(b, v, v, p)]
        if pivots:
            v = remaining.pop(pivots[0])
        else:
            pairs = [(i, j) for i in range(len(remaining))
                     for j in range(i + 1, len(remaining))
                     if pairing(b, remaining[i], remaining[j], p)]
            need(bool(pairs), "degenerate residual form")
            i, j = pairs[0]
            v = combine(1, 1, remaining[i], remaining[j], p)
            remaining.pop(i)
        norm = pairing(b, v, v, p)
        need(norm != 0, "odd characteristic pivot")
        remaining = [combine(1, -pairing(b, v, w, p) * pow(norm, -1, p),
                             w, v, p) for w in remaining]
        columns.append(v)
    return columns


def normalize_form(b, p):
    r = len(b)
    det = determinant(b, p)
    need(det != 0 and all(b[i][j] == b[j][i]
                         for i in range(r) for j in range(r)), "symmetric unit form")
    nonsquare = next(x for x in range(2, p) if pow(x, (p - 1) // 2, p) == p - 1)
    square = pow(det, (p - 1) // 2, p) == 1
    scale = nonsquare if r % 2 and not square else 1
    c = [[scale * x % p for x in row] for row in b]
    columns = orthogonal_basis(c, p)
    for k in range(r - 1):
        a = pairing(c, columns[k], columns[k], p)
        d = pairing(c, columns[k + 1], columns[k + 1], p)
        choices = [(u, v) for u in range(p) for v in range(p)
                   if (a * u * u + d * v * v) % p == 1]
        need(bool(choices), "binary form must represent one")
        u, v = choices[0]
        x, y = columns[k], columns[k + 1]
        columns[k] = combine(u, v, x, y, p)
        columns[k + 1] = combine(-d * v, a * u, x, y, p)
    last = pairing(c, columns[-1], columns[-1], p)
    target = nonsquare if r % 2 == 0 and not square else 1
    roots = [x for x in range(1, p) if last * x * x % p == target]
    need(bool(roots), "last square class")
    columns[-1] = [(roots[0] * x) % p for x in columns[-1]]
    matrix = transpose(columns)
    canonical = eye(r)
    canonical[-1][-1] = target
    need(mm(mm(transpose(matrix), c, p), matrix, p) == canonical,
         "complete congruence certificate")
    signature = [r, int(r % 2 == 0 and not square)]
    return signature, matrix, pow(scale, -1, p)


def canonical_chart(t, p):
    form, chart = recover_form(t, p)
    signature, matrix, socle_scale = normalize_form(form, p)
    n = len(t)
    block = eye(n)
    for i in range(n - 2):
        for j in range(n - 2):
            block[i + 1][j + 1] = matrix[i][j]
    block[-1][-1] = socle_scale
    return signature, mm(chart, block, p)


def isomorphism(t, other, p):
    left, a = canonical_chart(t, p)
    right, b = canonical_chart(other, p)
    if left != right:
        return None
    return mm(b, inverse(a, p), p)
