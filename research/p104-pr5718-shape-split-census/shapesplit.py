"""Exact census of PR5718-shape helper splits on a P104 word.  Apache-2.0.  Python 3.12, standard library only.

Prepared by Nick Petalas.  Extends the criterion and pure-subspace decision of Matarener's PR5994 census
(`research/p104-helper-split-exhaustion`, PR5599 PROOF.md section 1) to the shape of flyingviper's PR5718 split.

Model (one helper p of a boundary group g = (U, V), cut after event i, strictly intermediate chart F holding p):
  * input side: a combination a of the prefix rows of the fields at F with a_p != 0 and c = aP supported on the
    group, on roles whose initial chart is U, or (in_kind='empty', PR5718's rule) on every role whose initial chart
    is zero-dimensional;
  * a new independent helper z replaces p after the cut (unit injection b = e_p, as in PR5718); its z-direction
    reaches the outputs as d = S e_p (S = suffix columns of the original word);
  * output normalisation only at V: every role whose final chart is V (other than p) may be corrected freely, so d
    must vanish on O = {roles whose final chart is not V}; the pair needs a.b = c.d' != 0.
Classes whose d leaks into O are reported as `leak`: such a split needs a mid-word correction of that leak.
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


def groups_of(w):
    n = w['public']; main = set(w['live']) | {r + 112 for r in w['live']}
    g = defaultdict(set)
    for r in range(n):
        if r not in main:
            g[(w['initial'][r], w['final'][r])].add(r)
    return g


def pure_subspace(vecs, roles, support):
    """Basis of {x : sum x_r vecs[r] supported in `support`} as (coefficients, image) pairs; kernel vectors included."""
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


def functional_witness(A, p, free, rho):
    """Exact decision over the span of A.  With L1 = a_p, L2 = c_p, L3 = c on the free coordinates and rho = d_p, a
    split exists iff some a has L1 != 0 and (L3 != 0 or L1 = rho * L2): free coordinates of d' adjust c.d' at will,
    otherwise c.d' = rho * c_p must equal a.b = a_p."""
    L1 = [coef.get(p, Q(0)) for coef, img in A]
    L2 = [img.get(p, Q(0)) for coef, img in A]
    L3 = [{k: v for k, v in img.items() if k in free} for coef, img in A]
    if not any(L1):
        return False
    if any(L3):
        return True
    M = [L1[k] - rho * L2[k] for k in range(len(A))]       # is L1 nonzero on ker M ?
    if not any(M):
        return True
    j = next(k for k in range(len(A)) if M[k])
    return any(L1[k] * M[j] - L1[j] * M[k] for k in range(len(A)))


def census(w, in_kind='empty'):
    """Returns (counts, classes).  in_kind: 'boundary' (group + roles initial at U) or 'empty' (also every role
    initial at a zero-dimensional chart)."""
    n = w['public']; m = w.get('owned_fields', max(e[1] for e in w['program']) + 1 - n); N = n + m
    prog = w['program']; S = spans(w); dims = [len(f) for f in w['frames']]
    groups = groups_of(w)
    valid = {g: {f for f in range(len(S)) if S[g[0]] < S[f] < S[g[1]]} for g in groups}
    insup = {}
    for g, rs in groups.items():
        s = set(rs) | {r for r in range(n) if w['initial'][r] == g[0]}
        if in_kind == 'empty':
            s |= {r for r in range(n) if dims[w['initial'][r]] == 0}
        insup[g] = s
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
        for F in set(touched):
            if F is None or not at[F]:
                continue
            roles = sorted(at[F])
            for g in groups:
                if F not in valid[g] or not (groups[g] & at[F]):
                    continue
                counts['evaluations'] += 1
                A = pure_subspace(rows, roles, insup[g])
                hp = [p for p in sorted(groups[g] & at[F]) if any(coef.get(p) for coef, img in A)]
                if not any(img for coef, img in A) or not hp:
                    counts['no_helper_prefix'] += 1
                    continue
                snaps[i].append((F, g, hp, A))
    pivots = {p for v in snaps.values() for (F, g, hp, A) in v for p in hp}
    fin = {p: w['final'][p] for p in pivots}
    outside = {p: {r for r in range(n) if w['final'][r] != fin[p]} for p in pivots}
    keep = {p: outside[p] | {p} for p in pivots}
    cols = [{r: Q(1)} if r < n else {} for r in range(N)]
    classes = []
    for i in range(len(prog) - 1, -1, -1):
        for (F, g, hp, A) in snaps.get(i, []):
            for p in hp:
                d = {k: x for k, x in cols[p].items() if k in keep[p]}
                leak = sum(1 for k in d if k in outside[p])
                if leak:
                    counts['kind_leak'] += 1
                    kind = 'leak'
                else:
                    free = {r for r in range(n) if r not in keep[p]}
                    kind = 'witness' if functional_witness(A, p, free, d.get(p, Q(0))) else 'pairing'
                    counts['kind_' + kind] += 1
                classes.append({'cut_after': i, 'frame': F, 'group': list(g), 'pivot': p,
                                'ranks': [dims[F] - dims[g[0]], dims[g[1]] - dims[F]], 'kind': kind, 'leak': leak})
        e = prog[i]; op, r = e[0], e[1]
        if op in ('INIT', 'CLEAR'):
            cols[r] = {}
        elif op == 'COPY':
            add(cols[e[2]], cols[r], Q(e[-2])); cols[r] = {}
        elif op == 'SCALE':
            cols[r] = {k: v * Q(e[-2]) for k, v in cols[r].items()}
        elif op == 'ADD':
            add(cols[e[2]], cols[r], Q(e[-2]))
    counts['witnesses'] = sum(1 for c in classes if c['kind'] == 'witness')
    counts['pivots'] = len(pivots)
    return dict(counts), sorted(classes, key=lambda c: (c['cut_after'], c['frame'], c['pivot']))
