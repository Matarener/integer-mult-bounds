"""T1 zero step as CNF in the exact clause format of RankNine/T2Zero.lean (t2zero_cnf.py with s0 = none):
rows R = Z (dead), frames INSIDE Z (never degenerate, §13.25), columns s in Z.  For t in Z \\ E, s in Z \\ E:
M_ts = sum_{f in E} M_tf M_fs / M_ff over the terms f (t, s not orthogonal to f).  Variables ('z', t, s) <-> M_ts = 0,
('p', t, f, s) <-> M_tf M_fs != 0.  Clauses: d (product definitions), A (M_ts != 0 or t = s => some term), B_i
(M_ts = 0 or t ⊥ s => not exactly term i).  build(k) returns (VT, VID, cls, org, Z, FZ)."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, BASE)
from p104lib import frames, IDX, ORTH, N
FR = [tuple(IDX[q] for q in f) for f in frames()]
rw = [r for r in json.load(open(os.path.join(BASE, 'orbitsW.json'))) if r['frame']]
def build(k, cols=None):
    m = int(os.environ['T1MASK']) if os.environ.get('T1MASK') else int(rw[k]['mask'])
    R = [i for i in range(N) if m >> i & 1]; Rs = set(R)
    S = R if cols is None else cols
    FZ = [i for i, E in enumerate(FR) if all(e in Rs for e in E)]
    if os.environ.get('T1XF'):     # stage-3 extra valid frames (rows orthogonal to their outside lines only)
        xs = {frozenset(E) for E in json.load(open(os.environ['T1XF']))}
        FZ += [i for i, E in enumerate(FR) if frozenset(E) in xs and i not in FZ]
    VT = []; VID = {}
    def var(key):
        if key not in VID: VID[key] = len(VT) + 1; VT.append(list(key))
        return VID[key]
    def z(t, s):
        if t == s: return None
        if ORTH[t][s]: return 'Z'
        return var(('z', t, s))
    cls = []; org = []; done_p = set()
    def add(cl, o): cls.append(cl); org.append(o)
    for fi in FZ:
        E = FR[fi]; Es = set(E)
        outE = [e for e in E if e not in Rs]
        for t in R:
            if t in Es: continue
            if any(not ORTH[t][o] for o in outE): continue
            for s in S:
                if s in Es: continue
                terms = []
                for f in E:
                    if ORTH[t][f] or ORTH[f][s]: continue
                    pv = var(('p', t, f, s))
                    if pv not in done_p:
                        done_p.add(pv); a, b = z(t, f), z(f, s)
                        add([-pv, -a], ['d', pv, 0]); add([-pv, -b], ['d', pv, 1]); add([pv, a, b], ['d', pv, 2])
                    terms.append(pv)
                zt = z(t, s)
                if zt is None: add(terms, ['A', fi, t, s]); continue
                if zt != 'Z': add([zt] + terms, ['A', fi, t, s])
                for i, ti in enumerate(terms):
                    add(([-zt] if zt != 'Z' else []) + [-ti] + [tj for j, tj in enumerate(terms) if j != i], ['B', fi, t, s, i])
    return VT, VID, cls, org, R, FZ, m
if __name__ == '__main__':
    import time
    for k in map(int, sys.argv[1].split(',')):
        t0 = time.time(); VT, VID, cls, org, R, FZ, m = build(k)
        print(k, 'frames', len(FZ), 'vars', len(VT), 'clauses', len(cls), '%.1fs' % (time.time() - t0))
