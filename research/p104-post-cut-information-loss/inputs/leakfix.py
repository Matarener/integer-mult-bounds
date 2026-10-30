"""Exact test of mid-word corrections for PR5718-shape helper-split leak classes.  Apache-2.0.

Python 3.12, standard library only.  Extends Nick Petalas's PR6040 census (`inputs/shapesplit.py`, pinned), which
builds on Matarener's PR5994 census and flyingviper's PR5718 split shape.

Setting (PR6040).  A class is (cut after event i, chart F, helper p of a boundary group (U, V)).  A new independent
helper z replaces p after the cut; its output column is d = S_i e_p (S = suffix columns of the original word).  The
class "leaks" when d is nonzero on O = {public roles whose final chart is not V}.

Corrections.  Insert chart-local events ADD r' += q f after an event t >= i, where f is a field whose value in
the split word is a pure multiple of z (zero non-z part), and r' is any field at the same chart at time t.  By the
product telescoping identity  prod(I+D_k)A - prod A = sum_k (orig suffix after t_k) D_k (corrected state at t_k),
and because such an ADD only adds multiples of z (so every non-z part is unchanged), the corrected z-column is

    d' = d + sum_k mu_k v_k,   v_k = S_{t_k} e_{r'_k}  (suffix column of the ORIGINAL word),

with mu_k = q_k * (z-coefficient of f_k at t_k in the corrected word).  The non-z columns of the word are unchanged.
The non-z part of f in the split word is  row_f(t) - zc_f(t) * row_p(i),  where zc_f(t) is the coefficient with
which the content of field p at the cut reaches f at t (by linearity, the original word is the split word with
z := row_p(i)).  Hence:

  * first-order sources: fields with zero non-z part and zc != 0 in the uncorrected split word; each correction
    from such a source can take any mu (corrections in time order, each q chosen after the earlier ones);
  * necessary superset: also fields whose whole split-word value is zero (zc = 0, row = 0), which can only carry z
    after an earlier correction wrote into them.  Any correction program whose sources are pure-z fields has its
    v_k inside this superset span.

Decision per class: is d_O in -span{(v_k)_O}?  If so, the pairing of PR6040 (functional_witness) is tested with
rho = d'_p, which is either fixed by the solution or free (when a combination with zero O-part moves the p
coordinate).  'single' = one correction suffices (some v_O proportional to d_O).

Scope: the z-part necessary condition of PR6040 only.  Corrections whose source carries non-z content, the non-z
part of the split normalization, native maps, caller, compiler and outer checks are not modelled.
"""
from collections import defaultdict
from fractions import Fraction as Q
import importlib.util, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _load_shapesplit():
    name = 'pr6040_shapesplit'
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, HERE/'inputs'/'shapesplit.py')
    mod = importlib.util.module_from_spec(spec); sys.modules[name] = mod; spec.loader.exec_module(mod)
    return mod


SS = _load_shapesplit()
add, need = SS.add, SS.need


def leak_classes(w, in_kind='empty'):
    """Re-run the PR6040 forward/backward census, keeping for each class its A, d (full column) and row_p(i).
    Returns (classes, counts); counts must equal SS.census(w, in_kind)[0]."""
    n = w['public']; m = w.get('owned_fields', max(e[1] for e in w['program']) + 1 - n); N = n + m
    prog = w['program']; S = SS.spans(w); dims = [len(f) for f in w['frames']]
    groups = SS.groups_of(w)
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
                A = SS.pure_subspace(rows, roles, insup[g])
                hp = [p for p in sorted(groups[g] & at[F]) if any(coef.get(p) for coef, img in A)]
                if not any(img for coef, img in A) or not hp:
                    counts['no_helper_prefix'] += 1
                    continue
                snaps[i].append((F, g, hp, A, {p: dict(rows[p]) for p in hp}))
    pivots = {p for v in snaps.values() for (F, g, hp, A, rp) in v for p in hp}
    fin = {p: w['final'][p] for p in pivots}
    outside = {p: {r for r in range(n) if w['final'][r] != fin[p]} for p in pivots}
    keep = {p: outside[p] | {p} for p in pivots}
    cols = [{r: Q(1)} if r < n else {} for r in range(N)]
    classes = []
    for i in range(len(prog) - 1, -1, -1):
        for (F, g, hp, A, rp) in snaps.get(i, []):
            for p in hp:
                d = {k: x for k, x in cols[p].items() if k in keep[p]}
                leak = sum(1 for k in d if k in outside[p])
                free = {r for r in range(n) if r not in keep[p]}
                if leak:
                    counts['kind_leak'] += 1; kind = 'leak'
                else:
                    kind = 'witness' if SS.functional_witness(A, p, free, d.get(p, Q(0))) else 'pairing'
                    counts['kind_' + kind] += 1
                classes.append({'cut_after': i, 'frame': F, 'group': g, 'pivot': p, 'kind': kind, 'leak': leak,
                                'ranks': [dims[F] - dims[g[0]], dims[g[1]] - dims[F]],
                                'A': A, 'd': d, 'dall': dict(cols[p]), 'row_p': rp[p], 'outside': outside[p], 'free': free})
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
    classes.sort(key=lambda c: (c['cut_after'], c['frame'], c['pivot']))
    return classes, dict(counts)


def source_intervals(w, cuts, superset=False, mode='carrier'):
    """For each (cut i, pivot p) in `cuts` -> list of (field f, chart X, t0, t1): f has zero non-z part in the split
    word at chart X after every event t in [t0, t1], and (unless superset) a nonzero z-coefficient.
    One shared forward pass over the original word; z-coefficients zc are tracked per (i, p)."""
    n = w['public']; m = w.get('owned_fields', max(e[1] for e in w['program']) + 1 - n); N = n + m
    prog = w['program']
    rows = [{r: Q(1)} if r < n else {} for r in range(N)]
    cur = list(w['initial']) + [None] * m
    starts = defaultdict(list)
    for key in cuts:
        starts[key[0]].append(key)
    zc = {}            # key -> {field: coefficient}
    rowp = {}          # key -> row_p(i)
    holders = defaultdict(set)   # field -> keys with zc[key][field] != 0
    opened = {}        # key -> {field: (chart, t0)}
    out = defaultdict(list)

    def pure(key, f):
        c = zc[key].get(f, 0)
        if c == 0:
            return superset and not rows[f] and cur[f] is not None
        if mode == 'carrier':       # original value zero: split value = c * (z - row_p(i))
            return not rows[f]
        rp = rowp[key]
        if len(rows[f]) != len(rp):
            return False
        return all(rows[f].get(k) == c * v for k, v in rp.items())

    def refresh(key, f, t):
        """Update the open interval of f for key after event t."""
        o = opened[key]
        if f in o:
            X, t0 = o[f]
            if not pure(key, f) or cur[f] != X:
                out[key].append((f, X, t0, t - 1)); del o[f]
        if f not in o and cur[f] is not None and pure(key, f):
            o[f] = (cur[f], t)

    for t, e in enumerate(prog):
        op, r = e[0], e[1]
        changed = {r}
        if op == 'MOVE':
            cur[r] = e[3]
        elif op == 'INIT':
            rows[r] = {}; cur[r] = e[2]
        elif op == 'CLEAR':
            rows[r] = {}; cur[r] = None
        elif op == 'SCALE':
            rows[r] = {k: v * Q(e[-2]) for k, v in rows[r].items()}
        elif op == 'COPY':
            rows[r] = {k: v * Q(e[-2]) for k, v in rows[e[2]].items()}
        else:
            add(rows[r], rows[e[2]], Q(e[-2]))
        # z-coefficient propagation, same linear action on the scalar zc[key][*]
        aff = set(holders.get(r, ()))
        if op in ('ADD', 'COPY'):
            aff |= holders.get(e[2], set())
        for key in aff:
            z = zc[key]; old = z.get(r, 0)
            if op in ('INIT', 'CLEAR'):
                new = 0
            elif op == 'SCALE':
                new = old * Q(e[-2])
            elif op == 'COPY':
                new = Q(e[-2]) * z.get(e[2], 0)
            elif op == 'ADD':
                new = old + Q(e[-2]) * z.get(e[2], 0)
            else:
                new = old
            if new:
                z[r] = new; holders[r].add(key)
            else:
                z.pop(r, None); holders[r].discard(key)
        # interval bookkeeping for keys whose purity of r may have changed
        check = aff if not superset else set(opened)
        for key in check:
            refresh(key, r, t)
        # new cuts start after event t
        for key in starts.get(t, ()):
            i, p = key
            zc[key] = {p: Q(1)}; holders[p].add(key); rowp[key] = dict(rows[p]); opened[key] = {}
            if superset:
                for f in range(N):
                    if cur[f] is not None and not rows[f] and f != p:
                        opened[key][f] = (cur[f], t)
            refresh(key, p, t)
    T = len(prog) - 1
    for key, o in opened.items():
        for f, (X, t0) in o.items():
            out[key].append((f, X, t0, T))
    return out


class Span:
    """Incremental exact row-echelon basis over Q for sparse dict vectors; coordinate order given by `order`."""
    def __init__(self, order):
        self.rank = {k: j for j, k in enumerate(order)}
        self.piv = {}   # pivot coordinate -> normalized vector

    def reduce(self, v):
        v = dict(v)
        while v:
            k = min(v, key=self.rank.__getitem__)
            if k not in self.piv:
                return v, k
            add(v, self.piv[k], -v[k])
        return v, None

    def insert(self, v):
        v, k = self.reduce(v)
        if k is None:
            return False
        s = 1 / v[k]
        self.piv[k] = {x: y * s for x, y in v.items()}
        return True


def correction_spans(w, classes, intervals):
    """One backward pass.  For every class, the span of v = S_t e_{r'} restricted to O + {p}, over insertion times t
    in a source interval and r' at the source's chart.  Also flags a single-correction (v_O proportional to d_O)."""
    n = w['public']; m = w.get('owned_fields', max(e[1] for e in w['program']) + 1 - n); N = n + m
    prog = w['program']
    # chart membership after each event, reconstructed forward then walked backward
    cur = list(w['initial']) + [None] * m
    for e in prog:
        if e[0] == 'MOVE': cur[e[1]] = e[3]
        elif e[0] == 'INIT': cur[e[1]] = e[2]
        elif e[0] == 'CLEAR': cur[e[1]] = None
    at = defaultdict(set)
    for f in range(N):
        if cur[f] is not None:
            at[cur[f]].add(f)
    byclass = {}
    active_at = defaultdict(list)    # t1 -> list of (class index, f, X, t0)
    for ci, c in enumerate(classes):
        key = (c['cut_after'], c['pivot'])
        O = c['outside']; p = c['pivot']
        order = sorted(O) + sorted(r for r in range(n) if r not in O)
        byclass[ci] = {'span': Span(order), 'seen': set(), 'single': None, 'n_vectors': 0, 'O': O,
                       'dO': {k: x for k, x in c['d'].items() if k in O}, 'd': c['dall']}
        for (f, X, t0, t1) in intervals.get(key, ()):
            active_at[t1].append((ci, f, X, t0))
    live = []   # currently open (ci, f, X, t0)
    version = [0] * N
    cols = [{r: Q(1)} if r < n else {} for r in range(N)]
    for t in range(len(prog) - 1, -1, -1):
        # state: cols = suffix after event t, membership = after event t
        live.extend(active_at.get(t, ()))
        still = []
        for item in live:
            ci, f, X, t0 = item
            if t < t0:
                continue
            still.append(item)
            B = byclass[ci]
            for r2 in at[X]:
                tag = (r2, version[r2])
                if tag in B['seen']:
                    continue
                B['seen'].add(tag)
                v = cols[r2]
                if not v:
                    continue
                B['n_vectors'] += 1
                O = B['O']; vO = {k: x for k, x in v.items() if k in O}
                dO = B['dO']
                if B['single'] is None and vO and set(vO) == set(dO):
                    k0 = next(iter(dO)); s = -dO[k0] / vO[k0]
                    if all(dO[k] + s * vO[k] == 0 for k in dO):
                        rest = dict(B['d']); add(rest, v, s)
                        if rest:   # z must still reach a V-final role (no erasure of the new helper)
                            B['single'] = {'after_event': t, 'target': r2, 'source': f, 'chart': X, 'mu': str(s)}
                B['span'].insert(v)
        live = still
        e = prog[t]; op, r = e[0], e[1]
        # reverse membership of event t
        if op == 'MOVE':
            at[e[3]].discard(r); at[e[2]].add(r)
        elif op == 'INIT':
            at[e[2]].discard(r)
        elif op == 'CLEAR':
            at[e[2]].add(r)
        # suffix columns before event t
        if op in ('INIT', 'CLEAR'):
            cols[r] = {}; version[r] += 1
        elif op == 'COPY':
            add(cols[e[2]], cols[r], Q(e[-2])); cols[r] = {}; version[r] += 1; version[e[2]] += 1
        elif op == 'SCALE':
            cols[r] = {k: v * Q(e[-2]) for k, v in cols[r].items()}; version[r] += 1
        elif op == 'ADD':
            add(cols[e[2]], cols[r], Q(e[-2])); version[e[2]] += 1
    return byclass


def decide(c, B):
    """Return (kind, rho) for one leak class.  'unreachable': no correction combination clears d on O;
    'erased': only by removing z from every V-final output (the new helper would have no target); otherwise the
    PR6040 pairing outcome ('witness' / 'pairing') with rho = d'_p fixed or 'free'."""
    p = c['pivot']; O = c['outside']; sp = B['span']
    r, k = sp.reduce(c['dall'])           # O coordinates come first in the elimination order
    if k is not None and k in O:
        return 'unreachable', None
    W = [v for piv, v in sp.piv.items() if piv not in O]   # zero O-part: free moves of d' on V-final roles
    if not r and not W:
        return 'erased', None
    rho_free = any(v.get(p) for v in W)
    A = c['A']; free = c['free']
    if rho_free:
        L1 = [coef.get(p, Q(0)) for coef, img in A]
        L2 = [img.get(p, Q(0)) for coef, img in A]
        L3 = [{k2: v for k2, v in img.items() if k2 in free} for coef, img in A]
        ok = any(L1) and (any(L3) or any(L2))
        return ('witness' if ok else 'pairing'), 'free'
    rho = r.get(p, Q(0))
    if not any(v for v in W) and not {x for x in r if x != p} and rho == 0:
        return 'erased', None
    return ('witness' if SS.functional_witness(A, p, free, rho) else 'pairing'), str(rho)


def run(w, in_kind='empty', superset=False, only_leak=True, mode='carrier', select=None):
    """mode 'carrier': sources whose ORIGINAL value is zero while carrying p's cut content (their split value is a
    multiple of z - row_p(i), the full defect direction); mode 'purez': sources whose split value is a multiple of z
    (PR6040's suggested r += q*new; fixes only the z-part)."""
    classes, counts = leak_classes(w, in_kind)
    todo = [c for c in classes if c['kind'] == 'leak'] if only_leak else classes
    if select:
        todo = [c for c in todo if select(c)]
    cuts = sorted({(c['cut_after'], c['pivot']) for c in todo})
    iv = source_intervals(w, cuts, superset, mode)
    spans = correction_spans(w, todo, iv)
    res = []
    for ci, c in enumerate(todo):
        B = spans[ci]
        kind, rho = decide(c, B)
        res.append({'cut_after': c['cut_after'], 'frame': c['frame'], 'pivot': c['pivot'], 'group': list(c['group']),
                    'ranks': c['ranks'], 'leak': c['leak'], 'sources': len(iv.get((c['cut_after'], c['pivot']), ())),
                    'vectors': B['n_vectors'], 'span_rank': len(B['span'].piv), 'kind': kind, 'rho': rho,
                    'single': B['single']})
    return counts, res, iv

