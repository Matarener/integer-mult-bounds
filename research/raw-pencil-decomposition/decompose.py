"""Extract exact Kronecker blocks. Ali Romman with OpenAI Codex. Apache-2.0."""
import field_source as a


def tr(M, n):
    return a.columns(M, n)


def mm(A, B, n, f):
    return a.columns([a.mv(A, a.column(B, j), f) for j in range(n)], len(A))


def sub(A, r, c):
    return [row[c:] for row in A[r:]]


def span(vs, n, f):
    rows, piv = a.rref(vs, n, f)
    return rows[:len(piv)]


def solve(rows, n, f):
    rr, piv = a.rref(rows, n, f)
    if any(not any(r[:n]) and r[n] for r in rr):
        raise ValueError('inconsistent splitting equations')
    x = [0] * n
    for i, j in enumerate(piv):
        x[j] = rr[i][n]
    return x


def split(A, B, m, n, U, W, C, D, b, c, f):
    """Split an embedded summand of shape c by b with linear projections."""
    size = b * n + c * m
    eq = []
    def add(terms, rhs):
        row = [0] * (size + 1)
        for j, x in terms:
            row[j] = f.add[row[j]][x]
        row[-1] = rhs
        eq.append(row)
    for i in range(b):
        for j in range(b):
            add([(i*n+k, U[k][j]) for k in range(n)], int(i == j))
    for i in range(c):
        for j in range(c):
            add([(b*n+i*m+k, W[k][j]) for k in range(m)], int(i == j))
    for X, Y in ((A, C), (B, D)):
        for i in range(c):
            for j in range(n):
                add([(b*n+i*m+k, X[k][j]) for k in range(m)] +
                    [(k*n+j, f.neg[Y[i][k]]) for k in range(b)], 0)
    x = solve(eq, size, f)
    F = [x[i*n:(i+1)*n] for i in range(b)]
    G = [x[b*n+i*m:b*n+(i+1)*m] for i in range(c)]
    Q = a.columns([a.column(U, j) for j in range(b)] + a.kernel(F, n, f), n)
    R = a.columns([a.column(W, j) for j in range(c)] + a.kernel(G, m, f), m)
    Ri = a.inverse(R, f)
    X, Y = (mm(Ri, mm(Z, Q, n, f), n, f) for Z in (A, B))
    for Z, model in ((X, C), (Y, D)):
        if ([r[:b] for r in Z[:c]] != model or
                any(any(r[b:]) for r in Z[:c]) or any(any(r[:b]) for r in Z[c:])):
            raise ArithmeticError('split identity failed')
    return X, Y, R, Q


def chain(A, B, m, n, f):
    for e in range(min(m, n - 1) + 1):
        eq = []
        for k in range(e + 2):
            for i in range(m):
                row = [0] * ((e + 1) * n)
                if k <= e:
                    row[k*n:(k+1)*n] = A[i]
                if k:
                    row[(k-1)*n:k*n] = B[i]
                eq.append(row)
        ker = a.kernel(eq, (e + 1) * n, f)
        if ker:
            v = ker[0]
            U = a.columns([[f.mul[f.neg[1] if i % 2 else 1][x]
                            for x in v[(e-i)*n:(e-i+1)*n]] for i in range(e+1)], n)
            W = mm(A, U, e+1, f)
            W = [r[:e] for r in W]
            C = [[int(i == j) for j in range(e+1)] for i in range(e)]
            D = [[int(i+1 == j) for j in range(e+1)] for i in range(e)]
            return e, split(A, B, m, n, U, W, C, D, e+1, e, f)
    return None


def trim(p):
    p = list(p)
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return p


def padd(p, q, f):
    return trim([f.add[p[i] if i < len(p) else 0][q[i] if i < len(q) else 0]
                 for i in range(max(len(p), len(q)))])


def pmul(p, q, f):
    r = [0] * (len(p)+len(q)-1)
    for i, x in enumerate(p):
        for j, y in enumerate(q):
            r[i+j] = f.add[r[i+j]][f.mul[x][y]]
    return trim(r)


def pdiv(p, q, f):
    p, q = trim(p), trim(q)
    if q == [0]:
        raise ValueError('zero divisor')
    out = [0] * max(1, len(p)-len(q)+1)
    while p != [0] and len(p) >= len(q):
        j = len(p)-len(q)
        c = f.mul[p[-1]][f.inv[q[-1]]]
        out[j] = c
        for i, x in enumerate(q):
            p[i+j] = f.add[p[i+j]][f.neg[f.mul[c][x]]]
        p = trim(p)
    return trim(out), p


def pgcd(p, q, f):
    while q != [0]:
        p, q = q, pdiv(p, q, f)[1]
    return [f.mul[f.inv[p[-1]]][x] for x in p]


def ppow(p, k, f, modulus=None):
    r = [1]
    while k:
        if k & 1:
            r = pmul(r, p, f)
            if modulus is not None:
                r = pdiv(r, modulus, f)[1]
        p = pmul(p, p, f)
        if modulus is not None:
            p = pdiv(p, modulus, f)[1]
        k //= 2
    return r


def factor(p, f):
    """Use deterministic Berlekamp splitting, with inseparable recursion."""
    p = trim(p)
    if len(p) == 1:
        return []
    p = [f.mul[f.inv[p[-1]]][x] for x in p]
    derivative = trim([f.mul[i % f.p][p[i]] for i in range(1, len(p))] or [0])
    if derivative == [0]:
        root = [f.power(p[i], f.q // f.p) for i in range(0, len(p), f.p)]
        return sorted(factor(root, f) * f.p)
    g = pgcd(p, derivative, f)
    if len(g) > 1:
        return sorted(factor(g, f) + factor(pdiv(p, g, f)[0], f))
    d = len(p)-1
    cols = []
    for j in range(d):
        v = ppow([0, 1], f.q*j, f, p)
        v += [0] * (d-len(v))
        v[j] = f.add[v[j]][f.neg[1]]
        cols.append(v)
    basis = a.kernel(a.columns(cols, d), d, f)
    parts = [p]
    for b in basis:
        for c in range(f.q):
            h = b[:]
            h[0] = f.add[h[0]][f.neg[c]]
            nxt = []
            for part in parts:
                g = pgcd(part, trim(h), f)
                nxt += [g, pdiv(part, g, f)[0]] if 1 < len(g) < len(part) else [part]
            parts = nxt
    if len(parts) != len(basis):
        raise ArithmeticError('Berlekamp split incomplete')
    return sorted(tuple(x) for x in parts)


def peval(p, T, f):
    n = len(T)
    out = [[0]*n for _ in range(n)]
    for c in reversed(p):
        out = mm(out, T, n, f)
        for i in range(n):
            out[i][i] = f.add[out[i][i]][c]
    return out


def minpoly(T, f):
    n = len(T)
    powers, P = [], a.identity(n)
    for d in range(n+1):
        flat = sum(P, [])
        ker = a.kernel(a.columns(powers + [flat], n*n), d+1, f)
        if ker:
            v = next(x for x in ker if x[-1])
            return [f.mul[f.inv[v[-1]]][x] for x in v]
        powers.append(flat)
        P = mm(P, T, n, f)
    raise ArithmeticError('minimal polynomial absent')


def companion(p, f):
    n = len(p)-1
    C = [[int(i == j+1) for j in range(n)] for i in range(n)]
    for i in range(n):
        C[i][-1] = f.neg[p[i]]
    return C


def primary(T, p, f):
    n = len(T)
    if not n:
        return [], []
    N = peval(p, T, f)
    power, previous, e = a.identity(n), None, 0
    while any(any(r) for r in power):
        previous, power = power, mm(power, N, n, f)
        e += 1
    j = next(j for j in range(n) if any(a.column(previous, j)))
    v = a.column(a.identity(n), j)
    vs = []
    d = (len(p)-1)*e
    for _ in range(d):
        vs.append(v)
        v = a.mv(T, v, f)
    U = a.columns(vs, n)
    C = companion(ppow(p, e, f), f)
    X, _, R, Q = split(T, a.identity(n), n, n, U, U, C, a.identity(d), d, d, f)
    if R != Q:
        raise ArithmeticError('operator split differs')
    blocks, V = primary(sub(X, d, d), p, f)
    return [(tuple(p), e)] + blocks, compose(Q, d, V, f)


def operator(T, f):
    n = len(T)
    if not n:
        return [], []
    fac = factor(minpoly(T, f), f)
    spaces, blocks = [], []
    for p in sorted(set(fac)):
        N = peval(ppow(p, fac.count(p), f), T, f)
        basis = a.kernel(N, n, f)
        V = a.columns(basis, n)
        d = len(basis)
        equations = []
        for v in basis:
            target = a.mv(T, v, f)
            equations.append(solve([row + [x] for row, x in zip(V, target)], d, f))
        restricted = a.columns(equations, d)
        bs, U = primary(restricted, p, f)
        spaces += [a.column(mm(V, U, d, f), j) for j in range(d)]
        blocks += bs
    return blocks, a.columns(spaces, n)


def compose(Q, d, V, f):
    n = len(Q)
    E = [[int(i == j) if i < d and j < d else
          V[i-d][j-d] if i >= d and j >= d else 0 for j in range(n)] for i in range(n)]
    return mm(Q, E, n, f)


def regular(A, B, f):
    n = len(A)
    basis = []
    while True:
        V = a.columns(basis, n)
        AV = mm(A, V, len(basis), f)
        eq = [r + [f.neg[x] for x in s] for r, s in zip(B, AV)]
        nxt = span([v[:n] for v in a.kernel(eq, n+len(basis), f)], n, f)
        if len(nxt) == len(basis):
            break
        basis = nxt
    d = len(basis)
    V = a.columns(basis, n)
    W = mm(A, V, d, f)
    BV = mm(B, V, d, f)
    N = a.columns([solve([r+[x] for r, x in zip(W, a.column(BV, j))], d, f)
                   for j in range(d)], d)
    X, Y, R, Q = split(A, B, n, n, V, W, a.identity(d), N, d, d, f)
    inf, U = primary(N, (0, 1), f)
    residualB = sub(Y, d, d)
    T = mm(a.inverse(residualB, f), sub(X, d, d), n-d, f)
    finite, Z = operator(T, f)
    localQ = [[U[i][j] if i < d and j < d else Z[i-d][j-d]
               if i >= d and j >= d else 0 for j in range(n)] for i in range(n)]
    BZ = mm(residualB, Z, n-d, f)
    localR = [[U[i][j] if i < d and j < d else BZ[i-d][j-d]
               if i >= d and j >= d else 0 for j in range(n)] for i in range(n)]
    return [('infinity', (), e) for _, e in inf] + [('finite', p, e) for p, e in finite], mm(R, localR, n, f), mm(Q, localQ, n, f)


def extract(A, B, m, n, f):
    hit = chain(A, B, m, n, f)
    if hit:
        e, (X, Y, R, Q) = hit
        c, b, tag = e, e+1, 'right'
    else:
        hit = chain(tr(A, n), tr(B, n), n, m, f)
        if not hit:
            if m != n:
                raise ArithmeticError('regular residue is not square')
            return regular(A, B, f)
        e, (Xt, Yt, Rt, Qt) = hit
        X, Y = tr(Xt, m), tr(Yt, m)
        R, Q = tr(a.inverse(Qt, f), m), tr(a.inverse(Rt, f), n)
        c, b, tag = e+1, e, 'left'
    blocks, R2, Q2 = extract(sub(X, c, b), sub(Y, c, b), m-c, n-b, f)
    return [(tag, (), e)] + blocks, compose(R, c, R2, f), compose(Q, b, Q2, f)


def model(blocks, f):
    pieces = []
    for tag, p, e in blocks:
        if tag in ('left', 'right'):
            A = [[int(i == j) for j in range(e+1)] for i in range(e)]
            B = [[int(i+1 == j) for j in range(e+1)] for i in range(e)]
            m, n = e, e+1
            if tag == 'left':
                A, B, m, n = tr(A, n), tr(B, n), n, m
        else:
            C = companion(ppow(p if tag == 'finite' else (0, 1), e, f), f)
            m = n = len(C)
            A, B = (C, a.identity(n)) if tag == 'finite' else (a.identity(n), C)
        pieces.append((A, B, m, n))
    m, n = sum(x[2] for x in pieces), sum(x[3] for x in pieces)
    A, B = [[0]*n for _ in range(m)], [[0]*n for _ in range(m)]
    r = c = 0
    for X, Y, h, w in pieces:
        for i in range(h):
            A[r+i][c:c+w], B[r+i][c:c+w] = X[i], Y[i]
        r, c = r+h, c+w
    return A, B, m, n


def check(A, B, m, n, cert, f):
    blocks, R, Q = cert
    X, Y, h, w = model(blocks, f)
    return ((h, w) == (m, n) and len(R) == m and all(len(r) == m for r in R)
            and len(Q) == n and all(len(r) == n for r in Q)
            and a.determinant(R, f) != 0 and a.determinant(Q, f) != 0
            and mm(A, Q, n, f) == mm(R, X, n, f)
            and mm(B, Q, n, f) == mm(R, Y, n, f))


def decompose(A, B, m, n, f):
    if not isinstance(f, a.Field) or any(type(x) is not int or x < 0 for x in (m, n)):
        raise ValueError('explicit field and nonnegative dimensions required')
    if any(len(M) != m or any(len(r) != n or any(type(x) is not int or not 0 <= x < f.q
           for x in r) for r in M) for M in (A, B)):
        raise ValueError('invalid coefficient matrix')
    cert = extract(A, B, m, n, f)
    if not check(A, B, m, n, cert, f):
        raise ArithmeticError('coefficient identity failed')
    return cert
