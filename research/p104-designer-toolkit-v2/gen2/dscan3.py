"""Y-matching on D0; helper edges along D0 plus one extra direction d (all even d).  Writes JSON lines."""
import edges, dmatch, rt, geo, hgreedy, json, sys
P = geo.PORTS; O = geo.ORTH; m = geo.m; idx = {p: i for i, p in enumerate(P)}
D0 = [45, 30, 51]; M = dmatch.dmatch(D0)
def hedges(dirs):
    H = []; seen = {(min(a, b), max(a, b)) for a, b in M.items()}
    for d in dirs:
        for a in range(m):
            b = idx.get(P[a] ^ d)
            if b is None or O[a, b]: continue
            e = (min(a, b), max(a, b))
            if e in seen: continue
            seen.add(e); H.append(e)
    return H
if __name__ == "__main__":
    out = open(sys.argv[1], "w")
    base = hgreedy.inst(M, hedges(D0)); r = hgreedy.ev(base); out.write(json.dumps(dict(d=None, R0=r)) + '\n'); out.flush()
    for d in range(1, 512):
        if bin(d).count('1') % 2 or d in D0: continue
        for order in ('after', 'before'):
            dirs = D0 + [d] if order == 'after' else [d] + D0
            H = hedges(dirs)
            if len(H) == len(hedges(D0)): break
            I = hgreedy.inst(M, H); r = hgreedy.ev(I)
            out.write(json.dumps(dict(d=d, order=order, nh=len(H), R0=r)) + '\n'); out.flush()
