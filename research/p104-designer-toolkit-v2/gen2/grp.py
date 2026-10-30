"""RELAYTOP experiment G: reader-coherent sinks.  A fixed reader matching M; entries (j,i) with i common to j and its partner go to pair sinks
(pair, sign class) servable inside Q_j cap Q_j' (both Y mains stop there: Y<-piece reads by each Y with its own coefficient);
private entries go to single-reader sinks.  Bottom greedy as rt.build with sink weights; landings at the sink's Q (dim 7 for pairs, 8 singles)."""
import rt, geo, collections, pickle, sys
import networkx as nx
P = geo.PORTS; O = geo.ORTH; E = geo.RES; m = geo.m
def swarm_matching():
    R = pickle.load(open(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)),'data','m5827.pkl'), 'rb'))
    st, dimf, JF, ro = R['stops'], R['dimf'], R['JF'], R['roles']; M = {}
    for r in st:
        if ro[r] != 'Y': continue
        for f, _, _ in st[r]:
            if dimf[f] == 7 and len(JF[f]) == 2: a, b = sorted(JF[f]); M[a] = b; M[b] = a
    return M
def mw_matching(score):
    G = nx.Graph()
    for a in range(m):
        for b in range(a + 1, m):
            s = score(a, b)
            if s is not None: G.add_edge(a, b, weight=s)
    M = {}
    for a, b in nx.max_weight_matching(G, maxcardinality=True): M[a] = b; M[b] = a
    return M
def inst(M):
    snk = []; C = {}; sw = []; meta = []
    done = set()
    for j in range(m):
        if j in done: continue
        k = M.get(j)
        if k is None:
            C[len(snk)] = {i: (1 if E[j, i] > 0 else -1) for i in range(m) if O[j, i]}; snk.append([P[j]]); sw.append(1); meta.append(('s', j)); done.add(j); continue
        done |= {j, k}
        com = [i for i in range(m) if O[j, i] and O[k, i]]
        for cls in (1, -1):
            C[len(snk)] = {i: (1 if E[j, i] > 0 else -1) for i in com if E[j, i] * E[k, i] * cls > 0}; snk.append([P[j], P[k]]); sw.append(2); meta.append(('p', j, k))
        for a in (j, k):
            C[len(snk)] = {i: (1 if E[a, i] > 0 else -1) for i in range(m) if O[a, i] and i not in com}; snk.append([P[a]]); sw.append(1); meta.append(('s', a))
    I = rt.Inst([[p] for p in P], snk, C); I.sw = sw; I.meta = meta
    I.readers = [[mm[1]] if mm[0] == 's' else [mm[1], mm[2]] for mm in meta]
    return I
def ytax(M):
    return sum(rt.tax([0, 7, 8]) if j in M else 0.0 for j in range(m))
def run(M, K=7, lam=4.0, th=(0, 0, 6, 4, 3, 2, 2, 2, 1), tag=''):
    I = inst(M); N, st = rt.build(I, K=K, lam=lam, theta=th, land=True)
    by, R0 = rt.r0(N); yt = ytax(M)
    land = sum(1 for r in N.regs.values() if r['role'] == 'H')
    print(tag, 'K', K, 'lam', lam, 'R0', round(R0 + yt), {k: round(v) for k, v in by.items()}, 'Y', round(yt), 'regs', len(N.regs), 'live', len(N.live),
          'mean rect', st[-1][-1], 'eff', round(4992 / (R0 + yt), 3), flush=True)
    return N, R0 + yt
if __name__ == '__main__':
    Ms = dict(swarm=swarm_matching(),
              c18=mw_matching(lambda a, b: 1 if (not O[a, b] and (O[a] & O[b]).sum() == 18) else None),
              maxcommon=mw_matching(lambda a, b: int((O[a] & O[b]).sum())),
              orth24=mw_matching(lambda a, b: int((O[a] & O[b]).sum()) if O[a, b] else None))
    for name, M in Ms.items():
        print(name, 'matched', len(M))
        for lam in (4.0, 8.0):
            run(M, lam=lam, tag=name)
