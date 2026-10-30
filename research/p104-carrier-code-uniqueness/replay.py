"""Certificate replay and code facts for the length-8 P104 decoding code.  Apache-2.0.

Prepared for Matarener with Claude (Anthropic), via Claude Code.  Python 3.12, standard library only.

replay() re-runs the enumeration of code8.Model along a pre-order certificate written by gen8.py.  At every internal
node it recomputes ALL canonical consistent options of the named port and descends into one subtree per option; at a
dead node it checks that the named port has none; at a solution leaf it back-substitutes the solution.  The port named
by the certificate is only a branching choice: below any node the set of completions is the disjoint union over the
options of the chosen port, so any choice gives a complete enumeration (PROOF.md, section 3).  Root options are spread
over the part files by option index modulo the number of parts, exactly as gen8.py splits them.
"""
import gzip
import itertools
import time

from code8 import Model, dot


def tokens(path):
    raw = open(path, 'rb').read()
    if path.endswith('.gz'):
        raw = gzip.decompress(raw)
    return iter([x for x in raw.decode('ascii').split('\n') if x])


def replay(ports, streams, nparts, log=print):
    """Replay certificate parts; streams maps part numbers (a subset of range(nparts)) to token iterators."""
    parts = sorted(streams)
    if not parts or not set(parts) <= set(range(nparts)):
        raise ValueError('bad part selection')
    M = Model(ports)
    st = {p: {'internal': 0, 'dead': 0, 'solutions': 0} for p in parts}
    sols = []; t0 = time.time(); last = [t0]

    def node(d, rest, cls, s, rec):
        if time.time() - last[0] > 60:
            last[0] = time.time()
            log('replay progress %.0fs %s' % (time.time() - t0, st))
        x = next(s, None)
        if x is None:
            raise ValueError('certificate ends early')
        if x == 's':
            if rest:
                raise ValueError('solution token with unassigned ports')
            if len(M.pivots) != M.NV:
                raise ValueError('free variables at a solution leaf')
            rec['solutions'] += 1; sols.append(M.solution()); return
        kind, j = x.split(); j = int(j)
        if j not in rest:
            raise ValueError('port %d is not free' % j)
        opts = M.options(j, cls)
        if kind == 'd':
            if opts:
                raise ValueError('dead node at port %d has %d options' % (j, len(opts)))
            rec['dead'] += 1; return
        if kind != 'n' or not opts:
            raise ValueError('bad internal node at port %d' % j)
        rec['internal'] += 1
        for c in opts:
            mk = M.mark()
            if not M.apply(j, c):
                raise ValueError('option lost consistency')
            node(d + 1, rest - {j}, M.merged(j, c, cls), s, rec)
            M.undo(mk)

    rest = frozenset(M.others); cls = {t: i for i, t in enumerate(M.T)}
    roots = {p: next(streams[p], None) for p in parts}
    if len(set(roots.values())) != 1 or not str(roots[parts[0]]).startswith('n '):
        raise ValueError('parts disagree on the root')
    j = int(roots[parts[0]].split()[1]); opts = M.options(j, cls)
    root = {'port': j, 'options': len(opts)}
    for i, c in enumerate(opts):
        p = i % nparts
        if p not in streams:
            continue
        st[p]['root_options'] = st[p].get('root_options', 0) + 1
        mk = M.mark()
        if not M.apply(j, c):
            raise ValueError('root option lost consistency')
        node(1, rest - {j}, M.merged(j, c, cls), streams[p], st[p])
        M.undo(mk)
    for p in parts:
        st[p]['internal'] += 1                      # the root node, counted in every part as gen8.py does
        if next(streams[p], None) is not None:
            raise ValueError('trailing tokens in part %d' % p)
    return M, root, st, sols


def code_basis(M, x):
    """rows w_t (t in the clique T) of the code from a solution vector x of the model"""
    basis = []
    for t in M.T:
        row = [0] * M.N; row[t] = 1
        for m in M.nonconf[t]:
            row[m] = x[M.var[t, m]]
        basis.append(row)
    return basis


def decoding_rows(basis, ports):
    """for an F_3 space with a decoding vector at every port: the vector w_l with w_l[l] = 1, zero on conflicts of l
    (unique when the space restricted to the closed conflict neighbourhood is injective); None if some port fails"""
    N = len(ports); k = len(basis); rows = []
    for l in range(N):
        cols = [l] + [m for m in range(N) if m != l and dot(ports[l], ports[m])]
        A = [[basis[i][c] for i in range(k)] + [1 if c == l else 0] for c in cols]
        piv = []; r = 0
        for c in range(k):
            p = next((i for i in range(r, len(A)) if A[i][c]), None)
            if p is None:
                continue
            A[r], A[p] = A[p], A[r]; inv = pow(A[r][c], -1, 3); A[r] = [(v * inv) % 3 for v in A[r]]
            for i in range(len(A)):
                if i != r and A[i][c]:
                    f = A[i][c]; A[i] = [(v - f * y) % 3 for v, y in zip(A[i], A[r])]
            piv.append(c); r += 1
        if len(piv) != k or any(not any(row[:k]) and row[k] for row in A):
            return None
        a = [0] * k
        for i, c in enumerate(piv):
            a[c] = A[i][k]
        rows.append([sum(a[i] * basis[i][m] for i in range(k)) % 3 for m in range(N)])
    return rows


def rref3(vecs):
    basis = []; piv = []
    for v in vecs:
        v = [x % 3 for x in v]
        for b, p in zip(basis, piv):
            if v[p]:
                k = v[p]; v = [(x - k * y) % 3 for x, y in zip(v, b)]
        nz = [i for i, x in enumerate(v) if x]
        if nz:
            p = nz[0]; k = pow(v[p], -1, 3); v = [(x * k) % 3 for x in v]
            for i, b in enumerate(basis):
                if b[p]:
                    kk = b[p]; basis[i] = [(x - kk * y) % 3 for x, y in zip(b, v)]
            basis.append(v); piv.append(p)
    return basis


def weight_distribution(basis):
    """Hamming weights of all nonzero vectors of the F_3 span of `basis` (rows linearly independent)"""
    dist = {}
    for coef in itertools.product((0, 1, 2), repeat=len(basis)):
        if not any(coef):
            continue
        v = [sum(c * b[m] for c, b in zip(coef, basis)) % 3 for m in range(len(basis[0]))]
        w = sum(1 for x in v if x); dist[w] = dist.get(w, 0) + 1
    return dist


def sign_equivalent(M1, M2):
    """is there a diagonal d in {1, 2}^N with M2[l][m] = d_l^-1 M1[l][m] d_m for all l, m?"""
    N = len(M1)
    if any((M1[l][m] == 0) != (M2[l][m] == 0) for l in range(N) for m in range(N)):
        return False
    d = [0] * N
    for s in range(N):
        if d[s]:
            continue
        d[s] = 1; stack = [s]
        while stack:
            l = stack.pop()
            for m in range(N):
                if M1[l][m] and l != m:
                    want = (d[l] * M2[l][m] * pow(M1[l][m], -1, 3)) % 3
                    if d[m] == 0:
                        d[m] = want; stack.append(m)
                    elif d[m] != want:
                        return False
    return all(M2[l][m] == (pow(d[l], -1, 3) * M1[l][m] * d[m]) % 3 for l in range(N) for m in range(N))


def max_ports_in_codim(ports, codim):
    """f(9 - codim): the largest number of ports inside a subspace of codimension `codim` of F_2^9 (= Y^perp, dim Y = codim)"""
    best = 0; seen = set()
    for Y in itertools.combinations(range(1, 512), codim):
        span = {0}
        for y in Y:
            span |= {s ^ y for s in span}
        if len(span) != 1 << codim:
            continue
        key = frozenset(span)
        if key in seen:
            continue
        seen.add(key)
        best = max(best, sum(1 for q in ports if all(not dot(q, y) for y in Y)))
    return best
