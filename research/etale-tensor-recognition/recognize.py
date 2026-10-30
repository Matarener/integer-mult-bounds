"""Recognize finite etale multiplication in exact prime-field fixtures.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rref(rows, p):
    a = [list(row) for row in rows]
    pivots = []
    k = 0
    if not a:
        return a, pivots
    for j in range(len(a[0])):
        i = next((i for i in range(k, len(a)) if a[i][j] % p), None)
        if i is None:
            continue
        a[k], a[i] = a[i], a[k]
        inv = pow(a[k][j], -1, p)
        a[k] = [x * inv % p for x in a[k]]
        for i in range(len(a)):
            if i != k:
                c = a[i][j]
                a[i] = [(x - c * y) % p for x, y in zip(a[i], a[k])]
        pivots.append(j)
        k += 1
        if k == len(a):
            break
    return a, pivots


def rank(a, p):
    return len(rref(a, p)[1])


def nullspace(a, p):
    reduced, pivots = rref(a, p)
    n = len(a[0])
    out = []
    for j in range(n):
        if j in pivots:
            continue
        v = [0] * n
        v[j] = 1
        for k, i in enumerate(pivots):
            v[i] = -reduced[k][j] % p
        out.append(v)
    return out


def transpose(a):
    return [list(c) for c in zip(*a)]


def flat(a):
    return [x for row in a for x in row]


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def multiply(a, b, p):
    return [[sum(x * y for x, y in zip(r, c)) % p for c in zip(*b)] for r in a]


def matvec(a, v, p):
    return [sum(x * y for x, y in zip(row, v)) % p for row in a]


def add(a, b, p, scale=1):
    return [[(x + scale * y) % p for x, y in zip(r, s)] for r, s in zip(a, b)]


def inverse(a, p):
    n = len(a)
    b, pivots = rref([r + s for r, s in zip(a, identity(n))], p)
    require(pivots[:n] == list(range(n)), 'singular matrix')
    return [r[n:] for r in b]


def power(a, k, p):
    out = identity(len(a))
    while k:
        if k & 1:
            out = multiply(out, a, p)
        a = multiply(a, a, p)
        k //= 2
    return out


def combine(basis, coefficients, p):
    n = len(basis[0])
    out = [[0] * n for _ in range(n)]
    for c, a in zip(coefficients, basis):
        out = add(out, a, p, c)
    return out


def coordinates(basis, target, p):
    columns = [flat(a) for a in basis]
    n = len(columns)
    a, pivots = rref([list(row) + [v] for row, v in zip(zip(*columns), flat(target))], p)
    require(pivots == list(range(n)), 'target outside independent matrix basis')
    return [a[i][-1] for i in range(n)]


def evaluate(t, u, v, p):
    n = len(t)
    return [sum(u[i] * v[j] * t[i][j][k] for i in range(n) for j in range(n)) % p for k in range(n)]


def nucleus(t, p):
    n = len(t)
    equations = []
    for i in range(n):
        for j in range(n):
            for k in range(n):
                row = [0] * (2 * n * n)
                for a in range(n):
                    row[a * n + i] = (row[a * n + i] + t[a][j][k]) % p
                for b in range(n):
                    row[n * n + k * n + b] = (row[n * n + k * n + b] - t[i][j][b]) % p
                equations.append(row)
    kernel = nullspace(equations, p)
    X = [[[v[i * n + j] for j in range(n)] for i in range(n)] for v in kernel]
    Y = [[[v[n * n + i * n + j] for j in range(n)] for i in range(n)] for v in kernel]
    return X, Y


def primitive_parts(Y, frobenius, p):
    n = len(Y)
    fixed = nullspace(add(frobenius, identity(n), p, -1), p)
    parts = [identity(n)]
    for c in fixed:
        matrix = combine(Y, c, p)
        refined = []
        for h in parts:
            for scalar in range(p):
                shifted = add(matrix, identity(n), p, -scalar)
                block = multiply(h, add(identity(n), power(shifted, p - 1, p), p, -1), p)
                if any(flat(block)):
                    refined.append(block)
        parts = refined
    return parts


def transporter(t, X, Y, parts, p):
    n = len(t)
    u0, w0 = [0] * n, [0] * n
    for e in parts:
        ex = combine(X, coordinates(Y, e, p), p)
        u = next(c for c in zip(*ex) if any(c))
        w = next(c for c in zip(*e) if any(c))
        u0 = [(x + y) % p for x, y in zip(u0, u)]
        w0 = [(x + y) % p for x, y in zip(w0, w)]
    U = transpose([matvec(x, u0, p) for x in X])
    W = transpose([matvec(y, w0, p) for y in Y])
    phi = transpose([evaluate(t, u0, v, p) for v in identity(n)])
    V = inverse(multiply(inverse(W, p), phi, p), p)
    require(rank(U, p) == n, 'cyclic input construction')
    table = [[coordinates(Y, multiply(a, b, p), p) for b in Y] for a in Y]
    return dict(table=table, U=U, V=V, W=W, degrees=sorted(rank(e, p) for e in parts))


def recognize(t, p):
    require(p in (2, 3, 5, 7), 'unsupported fixture field')
    n = len(t)
    require(n > 0 and all(len(row) == n and all(len(v) == n for v in row) for row in t), 'tensor shape')
    require(all(type(x) is int and 0 <= x < p for row in t for v in row for x in v), 'field entries')
    X, Y = nucleus(t, p)
    if len(X) != n:
        return None, 'nucleus dimension'
    if rank([flat(a) for a in X], p) != n or rank([flat(a) for a in Y], p) != n:
        return None, 'nucleus projection'
    if any(multiply(a, b, p) != multiply(b, a, p) for a in Y for b in Y):
        return None, 'noncommutative nucleus'
    frobenius = transpose([coordinates(Y, power(a, p, p), p) for a in Y])
    if rank(frobenius, p) != n:
        return None, 'nilpotent nucleus'
    right = transpose([[t[i][j][k] for i in range(n) for k in range(n)] for j in range(n)])
    if rank(right, p) != n:
        return None, 'right kernel'
    parts = primitive_parts(Y, frobenius, p)
    return transporter(t, X, Y, parts, p), None
