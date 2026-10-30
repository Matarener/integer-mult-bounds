"""helper edges chosen greedily by newly covered entries (any non-orth / orth pair), after a D Y-matching"""
import edges, dmatch, rt, geo, sys, collections
P = geo.PORTS; O = geo.ORTH; E = geo.RES; m = geo.m
def make(D, M, nh, dirs=None, minc=6):
    Ys = [(j, x) for j, x in M.items() if j < x]
    done = {j: set() for j in range(m)}
    for j, x in Ys:
        com = {i for i in range(m) if O[j, i] and O[x, i]}; done[j] |= com; done[x] |= com
    H = []
    cand = [(a, b) for a in range(m) for b in range(a + 1, m) if (dirs is None or (P[a] ^ P[b]) in dirs) and (a, b) not in Ys and M.get(a) != b]
    for _ in range(nh):
        best = None
        for a, b in cand:
            c = sum(1 for i in range(m) if O[a, i] and O[b, i] and i not in done[a] and i not in done[b])
            if best is None or c > best[0]: best = (c, a, b)
        if best is None or best[0] < minc: break
        c, a, b = best; H.append((a, b)); cand.remove((a, b))
        com = {i for i in range(m) if O[a, i] and O[b, i] and i not in done[a] and i not in done[b]}; done[a] |= com; done[b] |= com
    return H
U = [104, 162, 266, 289, 76, 42, 97, 127]   # root hyperplane normals u_k (derived from S4 supports)
def inst(M, H, roots=False):
    edges_ = [(j, x, 'Y') for j, x in M.items() if j < x] + [(a, b, 'H') for a, b in H]
    done = {j: set() for j in range(m)}; snk = []; C = {}; sw = []; meta = []
    for (j, x, kind) in edges_:
        com = [i for i in range(m) if O[j, i] and O[x, i] and i not in done[j] and i not in done[x]]
        for cls in (1, -1):
            pc = [i for i in com if E[j, i] * E[x, i] * cls > 0]
            if not pc: continue
            C[len(snk)] = {i: (1 if E[j, i] > 0 else -1) for i in pc}; snk.append([P[j], P[x]]); sw.append(2); meta.append(('e', j, x, cls, kind))
        done[j] |= set(com); done[x] |= set(com)
    for j in range(m):
        pv = [i for i in range(m) if O[j, i] and i not in done[j]]
        if pv: C[len(snk)] = {i: (1 if E[j, i] > 0 else -1) for i in pv}; snk.append([P[j]]); sw.append(1); meta.append(('s', j))
    if roots:
        for k, u in enumerate(U):
            C[len(snk)] = {i: int(geo.S4[k][i]) for i in range(m) if geo.S4[k][i]}; snk.append([u]); sw.append(1); meta.append(('r', k))
    I = rt.Inst([[p] for p in P], snk, C); I.sw = sw; I.meta = meta; I.readers = [[mm[1]] if mm[0] == 's' else ([] if mm[0] == 'r' else [mm[1], mm[2]]) for mm in meta]
    return I
def ev(I, seeds=3, eps=0.3, **kw):
    r = []
    for s in range(seeds):
        N, _ = rt.build(I, lam=4.0, seed=s, land=False, eps=eps, **kw); yt = edges.land(N, I); r.append(round(rt.r0(N)[1] + yt))
    return sorted(r)
if __name__ == '__main__':
    D = [int(x) for x in sys.argv[1].split(',')]; dirs = None if sys.argv[2] == 'any' else set(D)
    M = dmatch.dmatch(D)
    for nh in [int(x) for x in sys.argv[3].split(',')]:
        H = make(D, M, nh, dirs)
        I = inst(M, H); cov = sum(len(I.C[k]) * I.sw[k] for k, mm in enumerate(I.meta) if mm[0] == 'e' and mm[4] == 'H')
        print('D', D, 'dirs', sys.argv[2], 'nh', len(H), 'Hentries', cov, 'R0', ev(I), flush=True)
