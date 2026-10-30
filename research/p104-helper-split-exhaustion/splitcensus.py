"""Exact census of PR5599-type helper splits on a P104 word.  Apache-2.0.

Prepared for Matarener with Claude (Anthropic), via Claude Code.  Python 3.12, standard library only.
Criterion (PR5599 PROOF.md, section 1): a helper group shares boundary charts (U, V); at a cut after event i and a
strictly intermediate chart F, a row a over the fields at F and a column b over the fields at F must satisfy
aP = c and Sb = d with c, d supported on the group and a.b = c.d = 1 (P = prefix rows, S = suffix columns).
The census evaluates every group, every intermediate chart and every cut after an event that touches the chart
(between two such events the prefix rows and suffix columns of the fields at F do not change), computes the whole
subspaces A = {a : aP supported in the input support} and B = {b : Sb supported in the output support}, and decides
exactly over Q whether some pair has a.b = c.d != 0.  `in_support`/`out_support` = 'group' (the PR5599 contract) or
'boundary' (every public role whose initial chart is U / whose final chart is V; a relaxation).
"""
from collections import defaultdict
from fractions import Fraction as Q
import gzip, json


def need(ok, why):
    if not ok:
        raise ValueError(why)


def read(path):
    raw = open(path, 'rb').read()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)


def spans(w):
    out = []
    for basis in w['frames']:
        s = {0}
        for v in basis:
            need(type(v) is int and 0 < v < 512 and v not in s, 'independent binary basis')
            s |= {x ^ v for x in s}
        out.append(frozenset(s))
    return out


def add(dst, src, q):
    for k, v in src.items():
        x = dst.get(k, 0) + q * v
        if x:
            dst[k] = x
        else:
            dst.pop(k, None)


def dot(u, v):
    return sum(q * v.get(k, 0) for k, q in u.items())


def groups_of(w):
    n = w['public']; main = set(w['live']) | {r + 112 for r in w['live']}
    g = defaultdict(set)
    for r in range(n):
        if r not in main:
            g[(w['initial'][r], w['final'][r])].add(r)
    return g


def pure_subspace(vecs, roles, support):
    """Basis of {x over roles : (sum x_r vecs[r]) supported in `support`}, as (coefficient dict, image dict) pairs.
    Gaussian elimination on the coordinates outside the support; zero-image combinations are included."""
    pivots, out = [], []
    for r in roles:
        outside = {k: v for k, v in vecs[r].items() if k not in support}
        coef = {r: Q(1)}
        for key, prow, pcoef in pivots:
            if key in outside:
                s = -outside[key]; add(outside, prow, s); add(coef, pcoef, s)
        if outside:
            key = min(outside); s = 1 / outside[key]
            pivots.append((key, {k: v * s for k, v in outside.items()}, {k: v * s for k, v in coef.items()}))
        else:
            img = {}
            for x, q in coef.items():
                add(img, vecs[x], q)
            out.append((coef, img))
    return out


def left_kernel(M, rows, cols):
    """Basis of {x in Q^rows : x M = 0}; M given as dict (i,j)->Q."""
    vecs = {i: {j: M[(i, j)] for j in range(cols) if M.get((i, j))} for i in range(rows)}
    return [coef for coef, img in pure_subspace(vecs, list(range(rows)), set())]


def decide(A, B):
    """Exact decision: does some a in span A, b in span B satisfy a.b = c.d != 0 ?  Returns (kind, witness or None).
    kinds: 'witness', 'F1zero' (a.b = 0 on A x B), 'F2zero' (c.d = 0 on A x B), 'mismatch' (both forms nonzero, no pair)."""
    kA, kB = len(A), len(B)
    F1 = {(i, j): dot(A[i][0], B[j][0]) for i in range(kA) for j in range(kB)}
    F2 = {(i, j): dot(A[i][1], B[j][1]) for i in range(kA) for j in range(kB)}
    G = {k: F1[k] - F2[k] for k in F1}
    if not any(F1.values()):
        return 'F1zero', None
    if not any(F2.values()):
        return 'F2zero', None
    # (ii) some x with xG = 0 and xF1 != 0 ?
    for x in left_kernel(G, kA, kB):
        v = [sum(x.get(i, 0) * F1[(i, j)] for i in range(kA)) for j in range(kB)]
        if any(v):
            return 'witness', build(A, B, x, F1, G)
    # (i) some 2x2 minor form u_i v_j - u_j v_i (u = xG, v = xF1) not identically zero ?  Test on e_k and e_k+e_l.
    probes = [{k: Q(1)} for k in range(kA)] + [{k: Q(1), l: Q(1)} for k in range(kA) for l in range(k + 1, kA)]
    for x in probes:
        u = [sum(x.get(i, 0) * G[(i, j)] for i in range(kA)) for j in range(kB)]
        v = [sum(x.get(i, 0) * F1[(i, j)] for i in range(kA)) for j in range(kB)]
        if any(u[i] * v[j] - u[j] * v[i] for i in range(kB) for j in range(i + 1, kB)):
            return 'witness', build(A, B, x, F1, G)
    return 'mismatch', None


def build(A, B, x, F1, G):
    """Explicit a, b, c, d with a.b = c.d = 1 from a probe x (exact)."""
    kA, kB = len(A), len(B)
    u = [sum(x.get(i, 0) * G[(i, j)] for i in range(kA)) for j in range(kB)]
    v = [sum(x.get(i, 0) * F1[(i, j)] for i in range(kA)) for j in range(kB)]
    y = [Q(0)] * kB
    if not any(u):
        y[next(j for j in range(kB) if v[j])] = Q(1)
    else:
        kk = next(j for j in range(kB) if u[j])
        j = next(j for j in range(kB) if u[kk] * v[j] - u[j] * v[kk])
        y[j] += u[kk]; y[kk] -= u[j]
    a, c, b, d = {}, {}, {}, {}
    for i, q in x.items():
        add(a, A[i][0], q); add(c, A[i][1], q)
    for j, q in enumerate(y):
        if q:
            add(b, B[j][0], q); add(d, B[j][1], q)
    s = dot(a, b)
    need(s != 0 and s == dot(c, d), 'witness pairing')
    b = {k: v / s for k, v in b.items()}; d = {k: v / s for k, v in d.items()}
    return a, b, c, d


def census(w, in_support='group', out_support='group', cut_range=None, log=None):
    """Full census.  Returns a dict of counts and the list of nontrivial classes with their kind."""
    n = w['public']; m = w.get('owned_fields', max(e[1] for e in w['program']) + 1 - n); N = n + m
    prog = w['program']; S = spans(w); dims = [len(f) for f in w['frames']]
    groups = groups_of(w)
    valid = {g: {f for f in range(len(S)) if S[g[0]] < S[f] < S[g[1]]} for g in groups}
    insup = {g: set(rs) | ({r for r in range(n) if w['initial'][r] == g[0]} if in_support == 'boundary' else set()) for g, rs in groups.items()}
    outsup = {g: set(rs) | ({r for r in range(n) if w['final'][r] == g[1]} if out_support == 'boundary' else set()) for g, rs in groups.items()}
    lo, hi = cut_range if cut_range else (0, len(prog) - 1)
    rows = [{r: Q(1)} if r < n else {} for r in range(N)]
    cur = list(w['initial']) + [None] * m
    at = defaultdict(set)
    for r in range(n):
        at[cur[r]].add(r)
    snaps = defaultdict(list); counts = defaultdict(int)
    for i, e in enumerate(prog):
        op, r = e[0], e[1]
        if op == 'MOVE':
            at[e[2]].discard(r); at[e[3]].add(r); cur[r] = e[3]; touched = (e[2], e[3])
        elif op == 'INIT':
            rows[r] = {}; cur[r] = e[2]; at[e[2]].add(r); touched = (e[2],)
        elif op == 'CLEAR':
            rows[r] = {}; at[e[2]].discard(r); cur[r] = None; touched = (e[2],)
        elif op == 'SCALE':
            rows[r] = {k: v * Q(e[-2]) for k, v in rows[r].items()}; touched = (cur[r],)
        elif op == 'COPY':
            rows[r] = {k: v * Q(e[-2]) for k, v in rows[e[2]].items()}; touched = (cur[r],)
        else:
            add(rows[r], rows[e[2]], Q(e[-2])); touched = (cur[r],)
        if not (lo <= i <= hi):
            continue
        for F in set(touched):
            if F is None or not at[F]:
                continue
            roles = sorted(at[F])
            for g in groups:
                if F not in valid[g] or not (groups[g] & at[F]):
                    continue
                counts['evaluations'] += 1
                A = pure_subspace(rows, roles, insup[g])
                if not any(img for coef, img in A):
                    counts['no_pure_prefix'] += 1
                    continue
                snaps[i].append((F, g, roles, A))
        if log and i % 5000 == 0:
            log('forward %d/%d evaluations %d snapshots %d' % (i, len(prog), counts['evaluations'], sum(len(v) for v in snaps.values())))
    cols = [{r: Q(1)} if r < n else {} for r in range(N)]
    classes = []
    for i in range(len(prog) - 1, -1, -1):
        for (F, g, roles, A) in snaps.get(i, []):
            B = pure_subspace(cols, roles, outsup[g])
            if not any(img for coef, img in B):
                counts['no_pure_suffix'] += 1
                continue
            kind, wit = decide(A, B)
            counts['kind_' + kind] += 1
            rec = {'cut_after': i, 'frame': F, 'group': list(g), 'ranks': [dims[F] - dims[g[0]], dims[g[1]] - dims[F]],
                   'roles_at_frame': len(roles), 'dim_A': sum(1 for c_, img in A if img), 'dim_B': sum(1 for c_, img in B if img),
                   'kind': kind}
            if wit:
                a, b, c, d = wit
                rec['witness'] = {k: {str(r): str(q) for r, q in v.items()} for k, v in zip('abcd', wit)}
                rec['pivots'] = sorted(groups[g] & set(roles))
            classes.append(rec)
        e = prog[i]; op, r = e[0], e[1]
        if op in ('INIT', 'CLEAR'):
            cols[r] = {}
        elif op == 'COPY':
            add(cols[e[2]], cols[r], Q(e[-2])); cols[r] = {}
        elif op == 'SCALE':
            cols[r] = {k: v * Q(e[-2]) for k, v in cols[r].items()}
        elif op == 'ADD':
            add(cols[e[2]], cols[r], Q(e[-2]))
        if log and i % 5000 == 0:
            log('backward %d classes %d' % (i, len(classes)))
    counts['groups'] = len(groups); counts['helpers'] = sum(len(v) for v in groups.values())
    counts['witnesses'] = sum(1 for c_ in classes if c_['kind'] == 'witness')
    return dict(counts), sorted(classes, key=lambda c_: (c_['cut_after'], c_['frame']))


def check_witness(w, cut, F, a, b, c, d, group):
    """Exact check of one witness against the word (prefix functional and suffix direction), independent of census()."""
    n = w['public']; m = w.get('owned_fields', max(e[1] for e in w['program']) + 1 - n); N = n + m
    rows = [{r: Q(1)} if r < n else {} for r in range(N)]
    cur = list(w['initial']) + [None] * m
    for e in w['program'][:cut + 1]:
        op, r = e[0], e[1]
        if op == 'MOVE': cur[r] = e[3]
        elif op == 'INIT': rows[r] = {}; cur[r] = e[2]
        elif op == 'CLEAR': rows[r] = {}; cur[r] = None
        elif op == 'SCALE': rows[r] = {k: v * Q(e[-2]) for k, v in rows[r].items()}
        elif op == 'COPY': rows[r] = {k: v * Q(e[-2]) for k, v in rows[e[2]].items()}
        else: add(rows[r], rows[e[2]], Q(e[-2]))
    need(all(cur[r] == F for r in set(a) | set(b)), 'witness fields at the intermediate chart')
    total = {}
    for r, q in a.items():
        add(total, rows[r], q)
    need(total == c and set(c) <= group, 'prefix functional equals c inside the group')
    col = [b.get(r, Q(0)) for r in range(N)]
    for e in w['program'][cut + 1:]:
        op, r = e[0], e[1]
        if op in ('INIT', 'CLEAR'): col[r] = Q(0)
        elif op == 'SCALE': col[r] *= Q(e[-2])
        elif op == 'COPY': col[r] = Q(e[-2]) * col[e[2]]
        elif op == 'ADD': col[r] += Q(e[-2]) * col[e[2]]
    need({r: x for r, x in enumerate(col) if x} == d and set(d) <= group, 'suffix direction equals d inside the group')
    need(dot(a, b) == dot(c, d) == 1, 'unit pairings')
