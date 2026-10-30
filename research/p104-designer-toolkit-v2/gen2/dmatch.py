"""translation-coherent pairing: readers paired along directions of a fixed 2-dim subspace D (p_j ^ p_x in D)"""
import grp, geo, rt, sys, random, collections
P = geo.PORTS; O = geo.ORTH; idx = {p: i for i, p in enumerate(P)}; m = geo.m
def dmatch(Dv, need18=False, seed=0):
    import networkx as nx
    G = nx.Graph(); rnd = random.Random(seed)
    for a in range(m):
        for d in Dv:
            b = idx.get(P[a] ^ d)
            if b is None or b < a: continue
            if O[a, b]: continue
            cn = int((O[a] & O[b]).sum())
            if need18 and cn != 18: continue
            G.add_edge(a, b, weight=1 + rnd.random() * 1e-3)
    M = {}
    for a, b in nx.max_weight_matching(G, maxcardinality=True): M[a] = b; M[b] = a
    return M
if __name__ == '__main__':
    D0 = [45, 30, 51]
    for nm, M in [('swarm', grp.swarm_matching()), ('D0 any', dmatch(D0)), ('D0 18', dmatch(D0, True)), ('D0 any s1', dmatch(D0, seed=1))]:
        print(nm, 'matched', len(M), 'same as swarm', sum(1 for a in M if grp.swarm_matching().get(a) == M[a]))
        grp.run(M, tag=nm)
    # random 2-dim D of even weight vectors
    rnd = random.Random(5); ev = [v for v in range(1, 512) if bin(v).count('1') % 2 == 0]
    for t in range(6):
        a, b = rnd.sample(ev, 2); M = dmatch([a, b, a ^ b]); print('rand D', a, b, 'matched', len(M)); grp.run(M, tag='randD')
