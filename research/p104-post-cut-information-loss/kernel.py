"""Left-kernel tracker for the P104 linear words: which fields' contents are linearly redundant at each event.
Apache-2.0.  Python 3.12, standard library only.

A word acts on N = n + m fields; public field r < n starts as the input coordinate x_r, owned fields start empty.
Write W(t) for the N x n matrix of field values (rows = linear forms in the inputs) after event t, and
K(t) = {c in Q^N : c W(t) = 0} for its left kernel.  Field p is *redundant* at t when some c in K(t) has c_p != 0,
i.e. row_p(t) lies in the span of the other fields' rows.  K evolves by exact rules (README, Lemma 2):

  ADD   r += q f   (W' = (I + q e_r e_f^T) W):  c_f <- c_f - q c_r            (c' = c A^{-1})
  SCALE r *= s, s != 0:                        c_r <- c_r / s
  INIT/CLEAR r   (row r := 0):    K' = (K  cap {c_r = 0})  +  span{e_r}
  COPY  r := q f (row r := q row_f):  K' = {c : c - c_r e_r + q c_r e_f in K, and that vector has r-coordinate 0}
                                      = {k + c_r (e_r - q e_f) : k in K, k_r = 0}   (needs f != r)
  MOVE: values unchanged.

The basis is kept in reduced echelon form (pivot coordinate -> sparse vector); its support is the redundant set.
"""
from fractions import Fraction as Q


def need(ok, why):
    if not ok:
        raise SystemExit('FAIL: ' + why)


class Kernel:
    def __init__(self, N, empty):
        self.vecs = [{f: Q(1)} for f in sorted(empty)]     # list of sparse vectors (not necessarily echelon)
        self.N = N

    # -- helpers ------------------------------------------------------------------------------------------------
    def _cap_zero(self, r):
        """Replace the basis by a basis of K cap {c_r = 0}."""
        hit = [v for v in self.vecs if v.get(r)]
        keep = [v for v in self.vecs if not v.get(r)]
        if hit:
            b = hit[0]; br = b[r]
            for v in hit[1:]:
                s = v[r] / br
                u = dict(v)
                for k, x in b.items():
                    y = u.get(k, 0) - s * x
                    if y: u[k] = y
                    else: u.pop(k, None)
                keep.append(u)
        self.vecs = keep

    def apply(self, e):
        op, r = e[0], e[1]
        if op == 'ADD':
            f, q = e[2], Q(e[-2])
            need(f != r, 'ADD with distinct source')
            for v in self.vecs:
                cr = v.get(r)
                if cr:
                    y = v.get(f, 0) - q * cr
                    if y: v[f] = y
                    else: v.pop(f, None)
        elif op == 'SCALE':
            s = Q(e[-2]); need(s != 0, 'nonzero SCALE')
            for v in self.vecs:
                if r in v: v[r] = v[r] / s
        elif op in ('INIT', 'CLEAR'):
            self._cap_zero(r)
            self.vecs.append({r: Q(1)})
        elif op == 'COPY':
            f, q = e[2], Q(e[-2])
            need(f != r, 'COPY with distinct source')
            self._cap_zero(r)
            u = {r: Q(1)}
            if q: u[f] = -q
            self.vecs.append(u)
        elif op == 'MOVE':
            pass
        else:
            need(False, 'unknown op ' + op)

    def support(self):
        s = set()
        for v in self.vecs:
            s.update(v)
        return s


def run(w, cuts):
    """cuts: set of event indices i.  Returns {i: (dim K(i), frozenset support K(i))} for the state after event i."""
    n = w['public']; prog = w['program']
    m = w.get('owned_fields', max(e[1] for e in prog) + 1 - n); N = n + m
    K = Kernel(N, range(n, N))
    out = {}
    for i, e in enumerate(prog):
        K.apply(e)
        if i in cuts:
            out[i] = (len(K.vecs), frozenset(K.support()))
    return out, K


def chart_local(vecs, inside):
    """Basis of {sum a_j vecs[j]} with every coordinate outside `inside` zero (exact elimination)."""
    rows = [dict(v) for v in vecs]
    out = []
    while rows:
        v = rows.pop()
        bad = [k for k in v if k not in inside]
        if not bad:
            if v: out.append(v)
            continue
        k = min(bad); x = v[k]
        nxt = []
        for u in rows:
            y = u.get(k)
            if y:
                s = y / x; u = dict(u)
                for kk, xx in v.items():
                    z = u.get(kk, 0) - s * xx
                    if z: u[kk] = z
                    else: u.pop(kk, None)
            nxt.append(u)
        rows = nxt
    return out


def _act(v, e):
    """Apply one event to a column vector v over fields (the forward action on z-coefficients)."""
    op, r = e[0], e[1]
    if op in ('INIT', 'CLEAR'):
        v.pop(r, None)
    elif op == 'SCALE':
        if r in v: v[r] *= Q(e[-2])
    elif op == 'COPY':
        y = Q(e[-2]) * v.get(e[2], 0)
        if y: v[r] = y
        else: v.pop(r, None)
    elif op == 'ADD':
        y = v.get(r, 0) + Q(e[-2]) * v.get(e[2], 0)
        if y: v[r] = y
        else: v.pop(r, None)


def closure_intervals(w, i, p):
    """Upper bound on the insertion points usable by a correction program whose every inserted batch reads an
    orig-zero chart-local combination c (c in K(t), supported on one chart X) into targets at X.  Such a batch adds
    (c . beta'(t)) (z - row_p(i)) to targets at X, where beta' is the z-coefficient column of the corrected word,
    and leaves every orig row unchanged.  beta'(t) lies in beta(t) + D(t), where D(t) is the forward image of the
    unit columns of all earlier usable targets.  A point (t, X) is usable only if some c in K_X(t) pairs nonzero
    with beta(t) or with D(t); then all fields at X join D.  Returns [(label, X, t, t)] usable points (as
    single-event intervals) and the final dim D."""
    n = w['public']; prog = w['program']
    m = w.get('owned_fields', max(e[1] for e in prog) + 1 - n); N = n + m
    K = Kernel(N, range(n, N))
    cur = list(w['initial']) + [None] * m
    beta = None; D = []; out = []; cache = None
    for t, e in enumerate(prog):
        op, r = e[0], e[1]
        K.apply(e)
        if op == 'MOVE': cur[r] = e[3]
        elif op == 'INIT': cur[r] = e[2]
        elif op == 'CLEAR': cur[r] = None
        if beta is not None:
            _act(beta, e)
            for d in D:
                _act(d, e)
            D = [d for d in D if d]
        if t == i:
            beta = {p: Q(1)}
        if t < i:
            continue
        supp = K.support()
        key = (tuple(sorted(supp)), tuple(cur[f] for f in sorted(supp)), tuple(tuple(sorted(v.items())) for v in K.vecs))
        if cache is None or cache[0] != key:
            charts = {}
            for f in supp:
                if cur[f] is not None:
                    charts.setdefault(cur[f], set()).add(f)
            loc = {X: chart_local(K.vecs, fs) for X, fs in charts.items()}
            cache = (key, {X: B for X, B in loc.items() if B})
        for X, B in cache[1].items():
            usable = any(sum(x * beta.get(f, 0) for f, x in c.items()) for c in B) or \
                any(sum(x * d.get(f, 0) for f, x in c.items()) for c in B for d in D)
            if usable:
                out.append(('comb', X, t, t))
                have = set()
                for d in D:
                    if len(d) == 1: have.update(d)
                for f in range(N):
                    if cur[f] == X and f not in have:
                        D.append({f: Q(1)})
    return out, len(D)
