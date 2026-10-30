"""hubclean.py WORD g1,g2,..: SUBCIRC hub superopt, phase 1 (arrivals pinned). HUBRULES: the enders' leftovers v_a are forced and the late visitors must
span V = span{v_a} with pure rows (H4, PROVED-necessary). The architecture: those cleaners pay a g stop of 2.70 each (X 12349 / H 012349: mu(3,4,9)).
Architecture-free question: is there ANY register (any role) that could visit g after the accumulation block at a cheaper MARGINAL stop
mu(a, dim g, b) (its neighbouring stops f_a < g < f_b, nesting checked), holding at that time a row whose x-part lies in V and whose non-x part is zero
(pure, H4) -- or more weakly, an x-part with a nonzero component in V?  Prints current cleaners' marginal and every cheaper candidate."""
import os
import sys, math, collections
import numpy as np
W = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path[:0] = [W + '/surgery']
import rp
from rp import P
S = rp.S
def mu(a, d, b):
    H = lambda x: x * math.log(x) if x > 0 else 0.0
    return H(b - a) - H(d - a) - H(b - d)
def sp(b):
    s = {0}
    for v in b: s |= {x ^ v for x in s}
    return frozenset(s)
def mrank(vs):
    M = [list(map(int, v)) for v in vs]; r = 0
    if not M: return 0
    for c in range(len(M[0])):
        piv = next((i for i in range(r, len(M)) if M[i][c] % P), None)
        if piv is None: continue
        M[r], M[piv] = M[piv], M[r]; iv = pow(M[r][c], P - 2, P); M[r] = [x * iv % P for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] % P:
                f = M[i][c]; M[i] = [(a - f * b) % P for a, b in zip(M[i], M[r])]
        r += 1
        if r == len(M): break
    return r
NOTIME = '--notime' in sys.argv
path, w = S.load_word(sys.argv[1]); n = len(w['initial']); role = S.roles_of(w); tl = rp.timelines(w); prog = w['program']
dim = [len(b) for b in w['frames']]; SP = [sp(b) for b in w['frames']]; live = w['live']; xcols = np.zeros(rp.nreg(w), dtype=bool); xcols[live] = True
lastev = collections.defaultdict(int); firstev = {}
for t, e in enumerate(prog):
    if e[0] in ('ADD', 'COPY', 'SCALE'):
        for r in S.regfields(e):
            lastev[(r, e[-1])] = max(lastev[(r, e[-1])], t); firstev.setdefault((r, e[-1]), t)
for g in [int(x) for x in sys.argv[2].split(',')]:
    dg = dim[g]
    M = sorted(r for r in range(n) if any(f == g for _, _, f in tl[r]))
    iv = {r: [(t0, t1) for t0, t1, f in tl[r] if f == g][0] for r in M}
    N = [r for r in M if w['final'][r] == g]; non = [r for r in M if r not in N]
    early = [r for r in non if iv[r][0] < min(iv[x][1] for x in non)]
    lastE = max(iv[r][1] for r in early); late = [r for r in non if iv[r][0] > lastE]
    snap = collections.defaultdict(list)
    for r in late: snap[iv[r][0] + 1].append(r)
    # candidate windows: consecutive stops (fa, fb) of any public non-member register with dim fa < dg < dim fb, fa in g in fb, transition after lastE possible
    cands = []
    for r in range(n):
        if r in M: continue
        st = tl[r]
        for (a0, a1, fa), (b0, b1, fb) in zip(st, st[1:]):
            if not (dim[fa] < dg < dim[fb] and SP[fa] <= SP[g] <= SP[fb]): continue
            la = lastev.get((r, fa), a0); fb_first = firstev.get((r, fb), b1)
            # the g visit must sit in (last event at fa, first event at fb) and after the accumulation block
            if fb_first <= lastE and not NOTIME: continue
            t = max(la, lastE) + 1
            cands.append((mu(dim[fa], dg, dim[fb]), r, fa, fb, t)); snap[t].append(r)
    _, sn = rp.replay(w, snap=snap)
    Vrows = [sn[iv[r][0] + 1][r] for r in late]
    Vx = [np.where(xcols, v, 0) % P for v in Vrows]; rV = mrank(Vx)
    cur = []
    for r in late:
        st = [(f, dim[f]) for _, _, f in tl[r]]; k = [f for f, _ in st].index(g)
        cur.append((r, role(r), ''.join(str(d) for _, d in st), round(mu(st[k - 1][1], dg, st[k + 1][1]), 3) if 0 < k < len(st) - 1 else None))
    print('   nesting-feasible windows around g (any time):', len(cands), 'marginals', sorted(collections.Counter(round(c[0],3) for c in cands).items()))
    print('== g', g, 'dim', dg, 'enders', N, 'late cleaners (r, role, chain, marginal g-stop)', cur, 'rank V', rV, 'accum end', lastE)
    best = collections.Counter()
    for m_, r, fa, fb, t in sorted(cands):
        if m_ > 2.71: continue
        row = sn[t][r] % P; x = np.where(xcols, row, 0) % P; junk = bool((np.where(xcols, 0, row) % P).any())
        inV = mrank(Vx + [x]) == rV and x.any(); touchV = mrank(Vx + [x]) > rV if False else None
        # component in V: rank of V + x restricted to g's ports vs V
        print('   cand', role(r), r, 'stops', (fa, dim[fa]), '->', (fb, dim[fb]), 'marginal %.3f' % m_, 't', t, '| x nonzero', bool(x.any()), 'x in V', inV, 'junk', junk)
        if inV and not junk: best[r] += 1
    print('   PURE candidates with x in V and marginal < 2.70:', dict(best))
