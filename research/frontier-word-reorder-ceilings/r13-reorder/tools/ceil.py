"""Stage-1 dependency-respecting ceiling (dims relaxation, coupled).

Valid relaxation of: any linear extension of the exact conflict poset + any frame
assignment (subspaces; warps' frames free, dims preserved; C0 ops pinned).
Variables: level of every op (one-hot), per register a level path s->f (flow).
Constraints: ops sharing a register in consecutive conflict groups are level-monotone
(hub variables); an op's level must be on every one of its registers' paths; domains
pruned by subspace bounds and forced frames. Objective: sum (b-a)^(1-C) over climbs.
Usage: python ceil.py SIDE C TIME [mip]"""
import sys, time
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
from poset import *
import numpy as np, scipy.sparse as sp, highspy

def domains(w, p, groups):
    c = w['canonical']; fr = c['frames']
    import os
    PINW = os.environ.get('PINW') == '1'
    lows, lowd, ups, upd, pinned = bounds(w, p, groups, relax_warps=not PINW)
    pos = preds_succs(p, groups)
    dom = {}
    for i, e in enumerate(p):
        if e[0] == 'center':
            continue
        dom[i] = set(range(lowd[i], upd[i]+1))
        if PINW and e[0] == 'warp': dom[i] = {len(fr[e[3]])}
    # forced frames per L register
    seg = defaultdict(dict)
    for r, gl in groups.items():
        if r[0] != 'L': continue
        sg = 0
        for t, ops in gl:
            if p[ops[0]][0] == 'warp':
                for j in ops: seg[j][r] = None
                sg += 1; continue
            for j in ops: seg[j][r] = sg
    def regs(i):
        return [(r[1], seg[i][r]) for r, k in pos[i].items() if r[0] == 'L' and seg[i][r] is not None]
    changed = True; it = 0
    while changed:
        it += 1; changed = False
        forced = defaultdict(dict)
        for i, D in dom.items():
            if len(D) == 1:
                d = next(iter(D))
                if p[i][0] != 'warp' and len(lows[i]) == d:
                    for r in regs(i):
                        forced[r][d] = span(lows[i])
        for i, D in dom.items():
            if p[i][0] == 'warp':
                continue
            lo, hi = span(lows[i]), span(ups[i]); new = set()
            for l in D:
                ok = True
                for r in regs(i):
                    for d, Y in forced[r].items():
                        if d == l and not (lo <= Y <= hi): ok = False
                        if d < l and not (Y <= hi): ok = False
                        if d > l and not (lo <= Y): ok = False
                if ok: new.add(l)
            if new != D:
                assert new, ('empty domain', i)
                dom[i] = new; changed = True
        # dims propagation through conflict groups
        for r, gl in groups.items():
            if r[0] != 'L': continue
            for (t0, a), (t1, b) in zip(gl, gl[1:]):
                m = min(min(dom[j]) for j in a if j in dom)
                for j in b:
                    if j in dom:
                        nd = {l for l in dom[j] if l >= m}
                        if nd != dom[j]: dom[j] = nd; changed = True
            for (t0, a), (t1, b) in reversed(list(zip(gl, gl[1:]))):
                M = max(max(dom[j]) for j in b if j in dom)
                for j in a:
                    if j in dom:
                        nd = {l for l in dom[j] if l <= M}
                        if nd != dom[j]: dom[j] = nd; changed = True
    return dom, pos, lows, ups

def model(w, side, C):
    c = w['canonical']; fr = c['frames']
    p, groups = build(w, side)
    dom, pos, lows, ups = domains(w, p, groups)
    s = {i: len(fr[c['start'][i]]) for i in range(632)}; f = {i: len(fr[c['final'][i]]) for i in range(632)}
    nv = 0; cost = []; W = {}
    def var(cst=0.0):
        nonlocal nv; cost.append(cst); nv += 1; return nv-1
    for i, D in dom.items():
        for l in sorted(D): W[i, l] = var()
    U = {}
    for r in range(632):
        for a in range(s[r], f[r]+1):
            for b in range(a+1, f[r]+1):
                U[r, a, b] = var((b-a)**(1-C))
    rows, cols, vals, lb, ub = [], [], [], [], []
    def row(ent, lo, hi):
        k = len(lb)
        for j, v in ent: rows.append(k); cols.append(j); vals.append(v)
        lb.append(lo); ub.append(hi)
    for i, D in dom.items(): row([(W[i, l], 1) for l in D], 1, 1)
    for r in range(632):
        S, F = s[r], f[r]
        for l in range(S, F+1):
            out = [(U[r, l, b], 1) for b in range(l+1, F+1)]; inn = [(U[r, a, l], -1) for a in range(S, l)]
            rhs = 1 if l == S else (-1 if l == F else 0)
            if S < F: row(out+inn, rhs, rhs)
    # op level must be on path of each register
    for i, D in dom.items():
        for r, k in pos[i].items():
            if r[0] != 'L': continue
            R = r[1]
            for l in D:
                if l == s[R] or l == f[R]: continue
                assert s[R] < l < f[R], (i, R, l)
                row([(W[i, l], 1)]+[(U[R, a, l], -1) for a in range(s[R], l)], -np.inf, 0)
    # monotonicity via hubs
    nh = 0
    for r, gl in groups.items():
        if r[0] != 'L': continue
        for (t0, a), (t1, b) in zip(gl, gl[1:]):
            a = [j for j in a if j in dom]; b = [j for j in b if j in dom]
            levels = sorted(set().union(*(dom[j] for j in a+b)))
            lo, hi = levels[0], levels[-1]
            if all(max(dom[j]) <= min(dom[k]) for j in a for k in b): continue
            H = {l: var() for l in range(lo, hi)}; nh += 1
            for l in range(lo, hi):
                for j in a:   # cum_j(l) >= H(l)
                    row([(W[j, x], 1) for x in dom[j] if x <= l]+[(H[l], -1)], 0, np.inf)
                for k in b:   # H(l) >= cum_k(l)
                    row([(H[l], 1)]+[(W[k, x], -1) for x in dom[k] if x <= l], 0, np.inf)
    A = sp.csc_matrix((vals, (rows, cols)), shape=(len(lb), nv))
    return dict(p=p, groups=groups, dom=dom, W=W, U=U, A=A, lb=lb, ub=ub, cost=np.array(cost), nv=nv, nh=nh, s=s, f=f)

def solve(M, mip, tl):
    h = highspy.Highs(); h.setOptionValue('output_flag', True); h.setOptionValue('threads', 1)
    h.setOptionValue('time_limit', float(tl))
    if not mip:
        h.setOptionValue('solver', 'ipm'); h.setOptionValue('run_crossover', 'on')
    lp = highspy.HighsLp(); nv = M['nv']; A = M['A']
    lp.num_col_ = nv; lp.num_row_ = A.shape[0]; lp.col_cost_ = M['cost']
    lp.col_lower_ = np.zeros(nv); lp.col_upper_ = np.ones(nv)
    inf = highspy.kHighsInf
    lp.row_lower_ = np.array([x if x != -np.inf else -inf for x in M['lb']]); lp.row_upper_ = np.array([x if x != np.inf else inf for x in M['ub']])
    lp.a_matrix_.format_ = highspy.MatrixFormat.kColwise; lp.a_matrix_.start_ = A.indptr; lp.a_matrix_.index_ = A.indices; lp.a_matrix_.value_ = A.data
    if mip:
        integ = [highspy.HighsVarType.kContinuous]*nv
        for j in list(M['W'].values())+list(M['U'].values()): integ[j] = highspy.HighsVarType.kInteger
        lp.integrality_ = integ
    h.passModel(lp); h.run()
    return h

def dump(M, h, path):
    import json
    x = h.getSolution().col_value
    lev = {i: max(D, key=lambda l: x[M['W'][i, l]]) for i, D in M['dom'].items()}
    paths = {}
    prof = Counter()
    for (r, a, b), j in M['U'].items():
        if x[j] > 0.5: prof[b-a] += 1; paths.setdefault(r, []).append((a, b))
    json.dump(dict(levels=lev, paths={r: sorted(v) for r, v in paths.items()}, profile=dict(prof)), open(path, 'w'))
    return lev, paths, prof

if __name__ == '__main__':
    side = sys.argv[1]; C = float(sys.argv[2]); tl = float(sys.argv[3]); mip = len(sys.argv) > 4
    t = time.time(); w = load(); M = model(w, side, C)
    print('model vars', M['nv'], 'rows', M['A'].shape[0], 'hubs', M['nh'], 't', time.time()-t, flush=True)
    h = solve(M, mip, tl); info = h.getInfo()
    cur = sum(n*r**(1-C) for r, n in {1:2201,2:412,3:510,4:127,5:40}.items())
    obj = info.objective_function_value
    print('status', h.modelStatusToString(h.getModelStatus()), 'obj', obj, 'mip_dual_bound', getattr(info, 'mip_dual_bound', None), flush=True)
    print('current non-centre local cost', cur, 'LB', obj, 'headroom/local', cur-obj, 'linearized dC', 18*(cur-obj)/247222)
    if mip: print("profile", dict(sorted(dump(M, h, f"/Users/joelpulikkan/imb-harness/r13/mip-{side}"+("-pinw" if __import__("os").environ.get("PINW")=="1" else "")+".json")[2].items())))
