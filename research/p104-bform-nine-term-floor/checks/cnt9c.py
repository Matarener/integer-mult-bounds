# B-form Case II census (dim9-frames BFORM3.md): the repo's P104 case-(b) multi-big census (cnt9b.py of
# research/nine-term-outside-colspace) with the column tau-classes EXTENDED by the 104 port classes O(l_z) = B0[z]
# ("port-root terms": y_j || r_z, z in B, column labels inside l_z^perp).  Everything else is cnt9b verbatim.
# usage: cnt9c.py P104 VARIANT   VARIANT: V0 = cnt9b control (distinct survivors, no ports)
#   V1 = survivors may repeat, no ports;  V2 = survivors may repeat + distinct, pairwise non-orthogonal ports;
#   V3 = survivors and ports may repeat, no orthogonality condition (most relaxed).
# Logs EVERY configuration whose bigs reach sigma >= 8 together with the filter verdict.  Apache-2.0.
import sys
VAR = sys.argv[2]
sys.argv = sys.argv[:2]
from m9lib import *
T0 = time.time()
print('START cnt9c', VAR, flush=True)
cliques = [sum(1 << t for t in c) for c in pickle.load(open(f'cliques_{unit}.pkl', 'rb')) if len(c) in (7, 8)]
csz = {Cq: pc(Cq) for Cq in cliques}
lb22 = pickle.load(open(f'cnt_{unit}.pkl', 'rb'))['lb22']
pairs = [(R, W) for (R, W), x in lb22.items() if x <= 7]
print('compatible (rep, plane) pairs', len(pairs), 'survivors', len(surv), flush=True)
portcls = {}
for z in range(v):
    co = inv[B0[z]]; portcls[co] = z
assert len(portcls) == v and not (set(portcls) & set(surv))
print('port classes', len(portcls), 'sizes', sorted({pc(cls[c]) for c in portcls}), flush=True)
nonorth = lambda z, w: G[z][w] != 0
USEP = VAR in ('V2', 'V3')
def jset(Xs):
    for r in range(2, len(Xs) + 1):
        for J in itertools.combinations(Xs, r):
            X = full
            for x in J: X &= x
            if lb(X) > 9 - r: return False
    return True
def jadd(Xs, x):
    for r in range(1, len(Xs) + 1):
        for J in itertools.combinations(Xs, r):
            X = x
            for y in J: X &= y
            if lb(X) > 9 - (r + 1): return False
    return True
def extend(Z, others):
    out = {Z}; level = {Z}
    while level:
        nxt = set()
        for Y in level:
            Ys = set(Y)
            for x in ks:
                if x in Ys: continue
                Y2 = tuple(sorted(Ys | {x ^ y for y in Ys} | {x}))
                if Y2 in out or Y2 in nxt: continue
                if C(Y2) != full and jadd(others, C(Y2)): nxt.add(Y2)
        out |= nxt; level = nxt
    return out
def ok_assign(vals):
    S = [c for k, c in vals if k == 's']; Pp = [portcls[c] for k, c in vals if k == 'p']
    if VAR == 'V0' and len(set(S)) < len(S): return False
    if VAR == 'V2':
        if len(set(Pp)) < len(Pp) or len(Pp) > 4: return False
        if any(not nonorth(a, b) for a, b in itertools.combinations(Pp, 2)): return False
    return True
t0 = time.time(); alive = []; nconf = 0; nhit = 0; nport = 0; last = time.time()
for (R, W) in pairs:
    if R == W: continue
    nbrs = [W3 for (R3, W3) in pairs if R3 == R and W3 not in (R, W)]
    bigsets = []
    def grow(pl, cs):
        bigsets.append(tuple(pl))
        for i, x in enumerate(cs):
            if jadd([C(P) for P in pl], C(x)): grow(pl + [x], cs[i + 1:])
    grow([R, W], [x for x in nbrs if x > W])
    for planes in bigsets:
        exts = [extend(P, [C(Q) for Q in planes if Q != P]) for P in planes]
        for Zs in itertools.product(*exts):
            Xs = [C(Z) for Z in Zs]
            if not jset(Xs): continue
            nconf += 1
            dims = [(len(Z) + 1).bit_length() - 1 for Z in Zs]
            S0s = []
            for Z, d in zip(Zs, dims):
                o = [('s', s) for s in surv if rk(full ^ C(Z), full ^ cls[s]) == 8 - d]
                if USEP: o += [('p', c) for c in portcls if rk(full ^ C(Z), full ^ cls[c]) == 8 - d]
                S0s.append(o)
            for taus in itertools.product(*[[0, 1] if S else [0] for S in S0s]):
                sigb = sum(min(6, d - 2 + t) for d, t in zip(dims, taus)); nb = len(Zs)
                if sigb < 8: continue
                idx = [i for i in range(nb) if taus[i]]
                for vals in itertools.product(*[S0s[i] for i in idx]):
                    if not ok_assign(vals): continue
                    nhit += 1; hasp = any(k == 'p' for k, c in vals); nport += hasp
                    m = dict(zip(idx, vals))
                    terms = [(full ^ Xs[i], full ^ (cls[m[i][1]] if taus[i] else 0)) for i in range(nb)]
                    terms += [(full, full)] * (9 - len(terms))
                    cover = 0
                    for r_, a_ in terms: cover |= r_ & a_
                    if cover != full: verdict = 'dead(D)'
                    elif all(sum(1 for r_, a_ in terms if r_ & Cq and a_ & Cq) >= csz[Cq] for Cq in cliques): verdict = 'ALIVE'
                    else: verdict = 'dead(C)'
                    print('CAND', VAR, 'Zs', [list(Z) for Z in Zs], 'dims', dims, 'taus', list(taus), 'sig', sigb,
                          'classes', [(k, c if k == 's' else 'port%d' % portcls[c]) for k, c in vals], verdict, flush=True)
                    if verdict == 'ALIVE': alive.append((Zs, taus, vals))
            if time.time() - last > 30:
                print('HEARTBEAT', round(time.time() - T0), 'configs', nconf, 'hits', nhit, 'alive', len(alive), flush=True); last = time.time()
    print('pair', R, W, 'configs so far', nconf, 'sigma>=8 assignments', nhit, 'with port class', nport, 'alive', len(alive), round(time.time() - t0), flush=True)
print('DONE', VAR, 'big configurations', nconf, 'sigma>=8 assignments', nhit, 'with port class', nport, 'ALIVE', len(alive), flush=True)
for a in alive: print('ALIVE', VAR, a, flush=True)
pickle.dump(alive, open(f'cnt9c_{unit}_{VAR}.pkl', 'wb'))
