"""RELAYTOP top v2: EDGE-COVER TOP (translation-coherent reader pairs, mains and helpers as dim-7 relays).
Readers are paired along the directions of a 2-dim subspace D (p_x = p_j + d, d in D).  One perfect matching = Y-edges (both Y mains stop at
Q_e = Q_j cap Q_x and read the edge's pieces there: Y<-piece reads, the Y-pair principle); every other D-edge is a HELPER edge: the edge's pieces land at Q_e,
are absorbed into one register per ratio class, butterfly (Haar pair) at Q_e, and the two results climb to Q_j and Q_x (one landing per reader per edge).
Entries are assigned edge by edge (Y-edges first): a port common to both endpoints and still unassigned for both goes to the edge's ratio-class sink; the rest are private sinks.
Bottom = rt.build on these sinks (land=False); landing done here with exact ops."""
import collections, rt, geo, grp, dmatch
from fractions import Fraction as Fr
P = geo.PORTS; O = geo.ORTH; E = geo.RES; m = geo.m
idx = {p: i for i, p in enumerate(P)}
res = lambda y, a: Fr(geo.RES[y, a]).limit_denominator(8)

def make_inst(D, M, helper=True, cap=None):
    """D: direction list; M: Y matching dict.  Returns Inst with meta per sink: ('s', j) | ('e', j, x, cls, kind) kind in Y/H"""
    edges = []
    for j, x in M.items():
        if j < x: edges.append((j, x, 'Y'))
    if helper:
        seen = {(min(a, b), max(a, b)) for a, b, _ in edges}
        for a in range(m):
            for d in D:
                b = idx.get(P[a] ^ d)
                if b is None or O[a, b]: continue
                e = (min(a, b), max(a, b))
                if e in seen: continue
                seen.add(e); edges.append((e[0], e[1], 'H'))
    done = {j: set() for j in range(m)}
    snk, C, sw, meta = [], {}, [], []
    for (j, x, kind) in edges:
        com = [i for i in range(m) if O[j, i] and O[x, i] and i not in done[j] and i not in done[x]]
        if cap is not None and kind == 'H' and len(com) < cap: continue
        for cls in (1, -1):
            pc = [i for i in com if E[j, i] * E[x, i] * cls > 0]
            if not pc: continue
            C[len(snk)] = {i: (1 if E[j, i] > 0 else -1) for i in pc}; snk.append([P[j], P[x]]); sw.append(2); meta.append(('e', j, x, cls, kind))
        done[j] |= set(com); done[x] |= set(com)
    for j in range(m):
        pv = [i for i in range(m) if O[j, i] and i not in done[j]]
        if pv:
            C[len(snk)] = {i: (1 if E[j, i] > 0 else -1) for i in pv}; snk.append([P[j]]); sw.append(1); meta.append(('s', j))
    I = rt.Inst([[p] for p in P], snk, C); I.sw = sw; I.meta = meta
    I.readers = [[mm[1]] if mm[0] == 's' else [mm[1], mm[2]] for mm in meta]
    return I

def rho(R, y):
    a = next(iter(R['A'])); return R['sc'] * R['v'][a] / res(y, a)

def land(N, I):
    F0 = I.frame([])
    arr = collections.defaultdict(list)          # sink -> [(reg, rect)]
    for rid in sorted(N.live):
        R = N.rects[rid]
        for t, k in enumerate(sorted(R['B'])):
            if t == 0: reg = R['reg']
            else:
                reg = N.newreg('H', F0[0], 0); N.stop(reg, R['g'], len(R['g'])); N.op(reg, R['reg'], 1, R['g'])
            Q = I.frame(list(rt.perp(I.snkb[k]))); N.stop(reg, Q[0], Q[1]); arr[k].append((reg, R))
    hedge = collections.defaultdict(dict)
    yst = set(); N.rootreads = collections.defaultdict(list)
    for k, lst in arr.items():
        mm = I.meta[k]; Q = I.frame(list(rt.perp(I.snkb[k])))
        if mm[0] == 'r':              # root sink: the owned root k reads each landed piece at H_k (q so that root gets S_ki/4 x_i)
            for reg, R in lst:
                a = next(iter(R['A'])); q = Fr(int(geo.S4[mm[1]][a]), 4) / (R['sc'] * R['v'][a])
                for b in R['A']: assert Fr(int(geo.S4[mm[1]][b]), 4) == q * R['sc'] * R['v'][b]
                N.rootreads[mm[1]].append((reg, q))
            continue
        if mm[0] == 's' or mm[4] == 'Y':
            if mm[0] == 'e': yst |= {mm[1], mm[2]}
            for reg, R in lst:
                for y in I.readers[k]:
                    a = next(iter(R['A'])); N.op(('Y', y), reg, -res(y, a) / (R['sc'] * R['v'][a]), Q[0])
            continue
        j = mm[1]
        acc, R0 = lst[0]; s0 = rho(R0, j)
        for reg, R in lst[1:]: N.op(acc, reg, s0 / rho(R, j), Q[0])
        hedge[(mm[1], mm[2])][mm[3]] = (acc, s0, Q)
    for (j, x), d in hedge.items():
        Qj = I.frame(list(rt.perp([P[j]]))); Qx = I.frame(list(rt.perp([P[x]])))
        if 1 in d and -1 in d:
            (a, ra, Q), (b, rb, _) = d[1], d[-1]
            N.op(a, b, ra / rb, Q[0]); N.op(b, a, -rb / (2 * ra), Q[0])
            N.stop(a, Qj[0], 8); N.op(('Y', j), a, -1 / ra, Qj[0])
            N.stop(b, Qx[0], 8); N.op(('Y', x), b, 2 / rb, Qx[0])
        else:
            cls = 1 if 1 in d else -1; a, ra, Q = d[cls]
            nb = N.newreg('H', F0[0], 0); N.stop(nb, Q[0], 7); N.op(nb, a, 1, Q[0])
            N.stop(a, Qj[0], 8); N.op(('Y', j), a, -1 / ra, Qj[0])
            N.stop(nb, Qx[0], 8); N.op(('Y', x), nb, -cls / ra, Qx[0])
    ytax = sum(rt.tax([0, 7, 8]) if y in yst else 0.0 for y in range(m))
    return ytax

def run(D, M=None, lam=4.0, seed=0, helper=True, cap=None, tag='', check=False):
    M = M or dmatch.dmatch(D)
    I = make_inst(D, M, helper=helper, cap=cap)
    N, st = rt.build(I, lam=lam, seed=seed, land=False)
    Rb = rt.r0(N)[1]
    yt = land(N, I); by, R0 = rt.r0(N)
    ne = collections.Counter(mm[4] if mm[0] == 'e' else 's' for mm in I.meta)
    out = dict(tag=tag, D=D, seed=seed, sinks=dict(ne), bottom=round(Rb), total=round(R0 + yt), X=round(by.get('X', 0)), H=round(by.get('H', 0)), Y=round(yt))
    if check:
        import valcheck; out['badY'] = valcheck.check(N, I)
    print(out, flush=True)
    return N, I, R0 + yt
