"""Recover split local products. Ali Romman with OpenAI Codex. Apache-2.0."""
from itertools import product
from math import gcd
from vendor import local as a


def span(vectors, n, f):
    rows, pivots = a.rref(vectors, n, f)
    return rows[:len(pivots)]


def coordinate_map(basis, n, f):
    _, pivots = a.rref(basis, n, f)
    inv = a.inverse([[v[j] for v in basis] for j in pivots], f)

    def coordinates(v):
        c = a.mv(inv, [v[j] for j in pivots], f)
        if a.mv(a.columns(basis, n), c, f) != v:
            raise ArithmeticError('value is outside the declared subspace')
        return c

    return coordinates


def linear_combination(coefficients, matrices, f):
    n = len(matrices[0])
    return [[f.total(f.mul[c][m[i][j]] for c, m in zip(coefficients, matrices))
             for j in range(n)] for i in range(n)]


def split_algebra(table, unit, f):
    """Return the radical and primitive idempotents, or a residue rejection."""
    n = len(table)
    power = 1
    while power < n:
        power *= f.q
    radical = a.kernel(a.columns([a.algebra_power(table, e, power, unit, f)
                                 for e in a.identity(n)], n), n, f)
    qcols = [a.algebra_power(table, e, f.q, unit, f) for e in a.identity(n)]
    fixed = a.kernel([[f.add[qcols[j][i]][f.neg[int(i == j)]]
                       for j in range(n)] for i in range(n)], n, f)
    if len(radical) + len(fixed) != n:
        return None, 'nonsplit residue field'
    parts = [unit]
    for c in fixed:
        refined = []
        for e in parts:
            for scalar in range(f.q):
                shifted = [f.add[x][f.neg[f.mul[scalar][y]]] for x, y in zip(c, unit)]
                v = a.algebra_power(table, shifted, f.q - 1, unit, f)
                projector = [f.add[x][f.neg[y]] for x, y in zip(unit, v)]
                piece = a.tensor_value(table, e, projector, f)
                if any(piece):
                    refined.append(piece)
        parts = refined
        if len(parts) == len(fixed):
            break
    if len(parts) != len(fixed):
        raise ArithmeticError('primitive idempotent count')
    return (radical, parts), None


def regular_generator(matrices, radical, parts, f):
    n = len(matrices[0])
    seed = [0] * n
    radical_actions = [linear_combination(c, matrices, f) for c in radical]
    for e in parts:
        projector = linear_combination(e, matrices, f)
        block = span([a.column(projector, j) for j in range(n)], n, f)
        jm = span([a.mv(action, v, f) for action in radical_actions for v in block], n, f)
        if len(block) - len(jm) != 1:
            return None
        v = next(v for v in block if a.rank(jm + [v], f) > len(jm))
        seed = [f.add[x][y] for x, y in zip(seed, v)]
    matrix = a.columns([a.mv(m, seed, f) for m in matrices], n)
    if not a.determinant(matrix, f):
        raise ArithmeticError('component generators did not give a regular module')
    return matrix, seed


def product_model(types, f):
    models = [a.model(h, f)[0] for h in types]
    n = sum(map(len, models))
    table = [[[0] * n for _ in range(n)] for _ in range(n)]
    offset = 0
    for mu in models:
        for i, row in enumerate(mu):
            for j, value in enumerate(row):
                table[offset+i][offset+j][offset:offset+len(mu)] = value
        offset += len(mu)
    return table


def character_index(types, f):
    exponents = [f.q-1]
    for heights in types:
        n = f.p ** sum(heights)
        exponents.extend(n * (f.p ** h - 1) // 2 for h in heights)
    if f.p != 2 and len({tuple(h) for h in types}) < len(types):
        exponents.append((f.q-1)//2)
    return gcd(*exponents)


def check_certificate(t, cert, f):
    """Check literal products and the canonical character label."""
    try:
        a.validate_tensor(t, f)
        types = cert['types']
        if not types or types != sorted(types):
            return False
        if any(hs != sorted(hs) or any(type(h) is not int or h < 1 for h in hs) for hs in types):
            return False
        n = len(t)
        if sum(f.p ** sum(hs) for hs in types) != n:
            return False
        matrices = [cert[k] for k in ('U', 'V', 'W')]
        if any(len(m) != n or any(len(row) != n or any(type(x) is not int or not 0 <= x < f.q for x in row)
                                     for row in m) for m in matrices):
            return False
        if any(not a.determinant(m, f) for m in matrices):
            return False
        u, v, w = matrices
        mu = product_model(types, f)
        for i, j in product(range(n), repeat=2):
            if a.tensor_value(t, a.column(u, i), a.column(v, j), f) != a.mv(w, mu[i][j], f):
                return False
        g = character_index(types, f)
        delta = f.mul[a.determinant(w, f)][f.inv[f.mul[a.determinant(u, f)][a.determinant(v, f)]]]
        return cert['sl_orbit_count'] == g and cert['sl_orbit_label'] == f.power(delta, (f.q-1)//g)
    except (KeyError, TypeError, ValueError, IndexError):
        return False


def recognize(t, f):
    """Return a complete product certificate, or a mathematical rejection."""
    a.validate_tensor(t, f)
    n = len(t)
    equations = []
    for i, j, k in product(range(n), repeat=3):
        row = [0] * (2*n*n)
        for z in range(n):
            row[z*n+i] = f.add[row[z*n+i]][t[z][j][k]]
            row[n*n+k*n+z] = f.add[row[n*n+k*n+z]][f.neg[t[i][j][z]]]
        equations.append(row)
    basis = a.kernel(equations, 2*n*n, f)
    if len(basis) != n:
        return None, 'nucleus dimension'
    xb = [[b[i*n:(i+1)*n] for i in range(n)] for b in basis]
    yb = [[b[n*n+i*n:n*n+(i+1)*n] for i in range(n)] for b in basis]
    if any(a.rank([b[start:start+n*n] for b in basis], f) != n for start in (0, n*n)):
        return None, 'nucleus projection'
    if any(a.mm(x, y, f) != a.mm(y, x, f) for x in yb for y in yb):
        return None, 'noncommutative nucleus'
    if a.rank([[t[i][j][k] for j in range(n)] for i in range(n) for k in range(n)], f) != n:
        return None, 'right kernel'
    coordinates = coordinate_map([sum(m, []) for m in yb], n*n, f)
    table = [[coordinates(sum(a.mm(x, y, f), [])) for y in yb] for x in yb]
    unit = coordinates(sum(a.identity(n), []))
    split, reason = split_algebra(table, unit, f)
    if split is None:
        return None, reason
    radical, parts = split
    ux, wy = (regular_generator(ms, radical, parts, f) for ms in (xb, yb))
    if ux is None or wy is None:
        return None, 'nonregular nucleus module'
    u, u0 = ux
    w, _ = wy
    phi = a.columns([a.tensor_value(t, u0, e, f) for e in a.identity(n)], n)
    v = a.mm(a.inverse(phi, f), w, f)
    factors = []
    for e in parts:
        block = span([a.tensor_value(table, e, x, f) for x in a.identity(n)], n, f)
        coord = coordinate_map(block, n, f)
        local = [[coord(a.tensor_value(table, x, y, f)) for y in block] for x in block]
        cert, reason = a.recognize(local, f)
        if cert is None:
            return None, 'local factor: '+reason
        # Normalize the local output map to a unital algebra isomorphism.
        image_one = a.column(cert['W'], 0)
        multiply_one = a.columns([a.tensor_value(local, image_one, x, f)
                                  for x in a.identity(len(block))], len(block))
        sigma = a.mm(a.inverse(multiply_one, f), cert['W'], f)
        images = a.mm(a.columns(block, n), sigma, f)
        factors.append((cert['heights'], images))
    factors.sort(key=lambda item: item[0])
    change = a.columns([a.column(m, j) for _, m in factors for j in range(len(m[0]))], n)
    cert = {'types': [hs for hs, _ in factors], 'U': a.mm(u, change, f),
            'V': a.mm(v, change, f), 'W': a.mm(w, change, f)}
    g = character_index(cert['types'], f)
    du, dv, dw = (a.determinant(cert[k], f) for k in ('U', 'V', 'W'))
    cert['sl_orbit_count'] = g
    cert['sl_orbit_label'] = f.power(f.mul[dw][f.inv[f.mul[du][dv]]], (f.q-1)//g)
    if not check_certificate(t, cert, f):
        raise ArithmeticError('product certificate failed')
    return cert, None


def sl_transporter(first, second, f):
    one, why = recognize(first, f)
    if one is None:
        return None, 'first tensor: '+why
    two, why = recognize(second, f)
    if two is None:
        return None, 'second tensor: '+why
    if one['types'] != two['types'] or one['sl_orbit_label'] != two['sl_orbit_label']:
        return None, 'different special-linear orbits'
    types, n, length = one['types'], len(first), f.q-1
    du, dv, dw = [f.mul[a.determinant(one[k], f)][f.inv[a.determinant(two[k], f)]]
                  for k in ('U', 'V', 'W')]
    z = f.mul[f.mul[du][dv]][f.inv[dw]]
    primitive = next(x for x in range(1, f.q) if len({f.power(x, j) for j in range(length)}) == length)
    logz = next(j for j in range(length) if f.power(primitive, j) == z)
    generators = []
    offset = 0
    starts = []
    for hs in types:
        size = f.p ** sum(hs)
        starts.append((offset, size))
        for i, h in enumerate(hs):
            generators.append((size*(f.p**h-1)//2, ('scale', offset, hs, i)))
        offset += size
    repeated = next((i for i in range(1, len(types)) if types[i] == types[i-1]), None)
    if f.p != 2 and repeated is not None:
        generators.append((length//2, ('swap', repeated-1, repeated)))
    g, weights = length, []
    for exponent, _ in generators:
        g, x, y = a.bezout(g, exponent)
        weights = [x*c for c in weights]+[y]
    if logz % g:
        raise ArithmeticError('character witness failed')
    sigma = a.identity(n)
    for weight, (_, operation) in zip(weights, generators):
        coefficient = weight*(logz//g)
        if operation[0] == 'scale':
            _, start, hs, index = operation
            scalar = f.power(primitive, coefficient % length)
            for j, exps in enumerate(a.model(hs, f)[1]):
                sigma[start+j] = [f.mul[f.power(scalar, exps[index])][x] for x in sigma[start+j]]
        elif coefficient % 2:
            _, left, right = operation
            lstart, size = starts[left]
            rstart, _ = starts[right]
            for j in range(size):
                sigma[lstart+j], sigma[rstart+j] = sigma[rstart+j], sigma[lstart+j]
    size = starts[0][1]
    inverse_size = pow(size, -1, length)
    x = f.power(f.mul[du][f.inv[z]], inverse_size)
    y = f.power(f.mul[dv][f.inv[z]], inverse_size)
    out = {}
    for key, target, scalar in zip(('U', 'V', 'W'), ('F', 'G', 'H'), (x, y, f.mul[x][y])):
        middle = [[f.mul[scalar if i < size else 1][value] for value in row] for i, row in enumerate(sigma)]
        out[target] = a.mm(a.mm(two[key], middle, f), a.inverse(one[key], f), f)
    if any(a.determinant(m, f) != 1 for m in out.values()):
        raise ArithmeticError('special-linear determinant')
    for i, j in product(range(n), repeat=2):
        if a.tensor_value(second, a.column(out['F'], i), a.column(out['G'], j), f) != a.mv(out['H'], first[i][j], f):
            raise ArithmeticError('special-linear product')
    return out, None
