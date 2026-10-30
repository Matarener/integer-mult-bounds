"""ALL-HELPER edge cover on a 3-dim translation subspace D (7 directions): every non-orthogonal reader pair along D is a helper edge
(pieces land at Q_e, per-class absorb, Haar butterfly, climb to Q_j/Q_x); bottom stage-2 port pairs restricted to D directions (self-dual); 8 root sinks.
usage: allh.py OUT.jsonl  (scans the 162 'regular' 3-dim subspaces: max 4 ports per coset)"""
import rt, geo, hgreedy, edges, collections, json, sys, itertools
P = geo.PORTS; O = geo.ORTH; m = geo.m; idx = {p: i for i, p in enumerate(P)}
def hedges(dirs):
    H = []; seen = set()
    for d in dirs:
        for a in range(m):
            b = idx.get(P[a] ^ d)
            if b is None or O[a, b]: continue
            e = (min(a, b), max(a, b))
            if e in seen: continue
            seen.add(e); H.append(e)
    return H
def evalD(dirs, seeds=(0, 1), roots=True, pd=True, lam=4.0):
    I = hgreedy.inst({}, hedges(dirs), roots=roots); r = []
    for s in seeds:
        N, _ = rt.build(I, lam=lam, seed=s, land=False, pairdirs=set(dirs) if pd else None); yt = edges.land(N, I); r.append(round(rt.r0(N)[1] + yt))
    return r, I
def regular():
    ev = [v for v in range(1, 512) if bin(v).count('1') % 2 == 0]; seen = set(); out = []
    for a in ev:
        for b in ev:
            if b <= a or (a ^ b) < b: continue
            for c in ev:
                S = frozenset((a, b, a ^ b, c, a ^ c, b ^ c, a ^ b ^ c))
                if c in (a, b, a ^ b) or S in seen: continue
                seen.add(S); Sl = [0] + sorted(S)
                cos = collections.Counter(min(p ^ d for d in Sl) for p in P)
                if max(cos.values()) <= 4: out.append(sorted(S))
    return out
if __name__ == '__main__':
    f = open(sys.argv[1], 'w')
    for D in regular():
        r, I = evalD(D)
        f.write(json.dumps(dict(D=D, R0=r, edges=len(hedges(D)))) + '\n'); f.flush()
