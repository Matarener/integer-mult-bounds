"""Stage-2 construction MIP: exact chain cost with subspace frames on restricted domains.
Free ops choose a frame from D'(x) = dom(x) ∩ (backbone frames of its registers ∪ {current frame});
per register-segment backbone gap a path over used candidates; conflict-group dims monotonicity.
Usage: python construct.py SIDE C TIME [wide]"""
import sys, time, json, os
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
from backbone import *
import numpy as np, scipy.sparse as sp, highspy

def build_mip(w, side, C, wide=False):
    S = domains(w, side); prof, chains = backbone(S)
    p, groups, dom, seg, Fm = S['p'], S['groups'], S['dom'], S['seg'], S['Fm']
    cur = {i: Fm.lab(w['canonical']['frames'][p[i][2]]) for i in dom}
    for i in dom:
        if cur[i] not in dom[i]: cur[i] = min(dom[i], key=lambda X: Fm.dims[X])
    bb = {key: set(ch) for key, ch in chains.items()}
    keys_of = {i: [(R, k) for R, k in seg[i].items() if isinstance(k, int)] for i in dom}
    GLOBAL = set().union(*bb.values()) | set(cur.values())
    D = {}
    for i, d in dom.items():
        if len(d) == 1: D[i] = set(d); continue
        allowed = set().union(*(bb[key] for key in keys_of[i])) | {cur[i]}
        if wide == 'medium': allowed = GLOBAL
        D[i] = (d & allowed) if wide != True else set(d)
        D[i].add(cur[i])
    # gaps
    def gap_of(key, X):
        ch = chains[key]
        if X in bb[key]: return None
        for a, b in zip(ch, ch[1:]):
            if Fm.le(a, X) and Fm.le(X, b): return (a, b)
        raise AssertionError((key, X))
    nv = 0; cost = []; integ = []
    def var(c=0.0, it=True):
        nonlocal nv; cost.append(c); integ.append(it); nv += 1; return nv-1
    free = {i for i in D if len(dom[i]) > 1}
    V = {(i, X): var() for i in free for X in sorted(D[i])}
    gapc = defaultdict(set); need = []   # (V var, key, gap, X)
    for (i, X), v in V.items():
        for key in keys_of[i]:
            g = gap_of(key, X)
            if g is not None: gapc[key, g].add(X); need.append((v, key, g, X))
    rows, cols, vals, lb, ub = [], [], [], [], []
    def row(ent, lo, hi):
        k = len(lb)
        for j, a in ent: rows.append(k); cols.append(j); vals.append(a)
        lb.append(lo); ub.append(hi)
    for i in free: row([(V[i, X], 1) for X in D[i]], 1, 1)
    arcs = {}; inflow = defaultdict(list); f = lambda x: x**(1-C)
    for (key, (a, b)), K in gapc.items():
        nodes = [a] + sorted(K, key=lambda X: Fm.dims[X]) + [b]
        out = defaultdict(list); inl = defaultdict(list)
        for u in nodes:
            for v_ in nodes:
                if u != v_ and Fm.dims[u] < Fm.dims[v_] and Fm.spans[u] < Fm.spans[v_]:
                    j = var(f(Fm.dims[v_]-Fm.dims[u])); arcs[key, u, v_] = j
                    out[u].append(j); inl[v_].append(j)
                    if v_ in K: inflow[key, v_].append(j)
        for u in nodes:
            ent = [(j, 1) for j in out[u]] + [(j, -1) for j in inl[u]]
            rhs = 1 if u == a else (-1 if u == b else 0)
            row(ent, rhs, rhs)
    const = 0.0
    for key, ch in chains.items():
        segs = [(a, b) for a, b in zip(ch, ch[1:])]
        for a, b in segs:
            if (key, (a, b)) not in gapc: const += f(Fm.dims[b]-Fm.dims[a])
    for v, key, g, X in need:
        row([(v, 1)] + [(j, -1) for j in inflow[key, X]], -np.inf, 0)
    # monotonicity over conflict groups (dims cumulative), hubs
    def cum(i, l):  # list of (var, coef) and constant for P(dim f(i) <= l)
        d = D[i]
        if i not in free: return [], 1.0 if Fm.dims[next(iter(d))] <= l else 0.0
        return [(V[i, X], 1) for X in d if Fm.dims[X] <= l], 0.0
    nh = 0
    for r, gl in groups.items():
        if r[0] != 'L': continue
        for (t0, A), (t1, B) in zip(gl, gl[1:]):
            A = [j for j in A if j in D]; B = [j for j in B if j in D]
            if not A or not B: continue
            if max(Fm.dims[X] for j in A for X in D[j]) <= min(Fm.dims[X] for j in B for X in D[j]): continue
            lo = min(Fm.dims[X] for j in A+B for X in D[j]); hi = max(Fm.dims[X] for j in A+B for X in D[j])
            nh += 1
            for l in range(lo, hi):
                H = var(0.0, False)
                for j in A:
                    e, c0 = cum(j, l); row(e+[(H, -1)], -c0, np.inf)
                for k in B:
                    e, c0 = cum(k, l); row([(H, 1)]+[(x, -a) for x, a in e], c0, np.inf)
    M = dict(free=free, S=S, chains=chains, D=D, V=V, arcs=arcs, cur=cur, nv=nv, cost=np.array(cost), integ=integ, const=const,
             A=sp.csc_matrix((vals, (rows, cols)), shape=(len(lb), nv)), lb=lb, ub=ub, nh=nh)
    return M

def run(M, tl, start=True):
    h = highspy.Highs(); h.setOptionValue('output_flag', bool(os.environ.get('HVERB'))); h.setOptionValue('threads', 1); h.setOptionValue('time_limit', float(tl))
    h.setOptionValue('mip_rel_gap', 1e-7)
    lp = highspy.HighsLp(); nv = M['nv']; A = M['A']; inf = highspy.kHighsInf
    lp.num_col_ = nv; lp.num_row_ = A.shape[0]; lp.col_cost_ = M['cost']; lp.col_lower_ = np.zeros(nv); lp.col_upper_ = np.ones(nv)
    lp.row_lower_ = np.array([x if x != -np.inf else -inf for x in M['lb']]); lp.row_upper_ = np.array([x if x != np.inf else inf for x in M['ub']])
    lp.a_matrix_.format_ = highspy.MatrixFormat.kColwise; lp.a_matrix_.start_ = A.indptr; lp.a_matrix_.index_ = A.indices; lp.a_matrix_.value_ = A.data
    if not os.environ.get('LPONLY'):
        lp.integrality_ = [highspy.HighsVarType.kInteger if t else highspy.HighsVarType.kContinuous for t in M['integ']]
    else:
        h.setOptionValue('solver', 'ipm'); h.setOptionValue('run_crossover', 'off'); start = False
    h.passModel(lp)
    if start:
        sol = highspy.HighsSolution(); x = np.zeros(nv)
        for (i, X), v in M['V'].items(): x[v] = 1.0 if M['cur'][i] == X else 0.0
        sol.col_value = list(x)
        # only V given; HiGHS completes? provide partial via setSolution
        try: h.setSolution(sol)
        except Exception as ex: print('setSolution failed', ex)
    h.run(); return h

if __name__ == '__main__':
    side, C, tl = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]); wide = True if 'wide' in sys.argv else ('medium' if 'medium' in sys.argv else False)
    t = time.time(); w = load(); M = build_mip(w, side, C, wide)
    print('vars', M['nv'], 'rows', M['A'].shape[0], 'V', len(M['V']), 'arcs', len(M['arcs']), 'hubs', M['nh'], 'const', M['const'], 't', time.time()-t, flush=True)
    h = run(M, tl); info = h.getInfo(); x = h.getSolution().col_value
    obj = info.objective_function_value + M['const']
    curc = sum(n*r**(1-C) for r, n in {1:2201,2:412,3:510,4:127,5:40}.items())
    print('status', h.modelStatusToString(h.getModelStatus()), 'cost', obj, 'bound', (info.mip_dual_bound if not os.environ.get('LPONLY') else float('nan')) + M['const'], 'current', curc, flush=True)
    frames = {i: (max(d, key=lambda X: x[M['V'][i, X]]) if (i, next(iter(d))) in M['V'] else next(iter(d))) for i, d in M['D'].items()}
    Fm = M['S']['Fm']
    json.dump(dict(frames={i: Fm.fb[X] for i, X in frames.items()}, cost=obj), open(f'/Users/joelpulikkan/imb-harness/r13/cons-{side}{"-"+str(wide) if wide else ""}.json', 'w'))
