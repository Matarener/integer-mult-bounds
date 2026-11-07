"""T2 pair certificates and transport witnesses (Lean RankNine.T2Hand / T2Main).
For each of the 9 frameless representatives r_k (orbitsW entries without frame, Gram set zm = r_k):
  Y = 8 independent lines of r_k; for every c' in FL (flData order): X = 8 lines of r_k ∩ c' with det(dot X Y) != 0,
  J = adjugate (integer), dd = det.  Stream: Y(8), n, then per partner: c', X(8), J (64 zig-zag ints), zz(dd).
Also: witness table W (c, g, k) with g(r_k) ⊆ c, and the check flClosed (preimage under every g permutes FL).
usage: python3 t1lean/t2pair.py   (writes t1lean/records/t2-k/pairs.txt, t1lean/records/t2w.txt, log to stdout)"""
import sys, os, json, re, time
from fractions import Fraction
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(HERE)
LEAN = os.path.normpath(os.path.join(BASE, '..', '..', 'lean', 'RankNine'))
GEN = os.environ.get('GEN', os.path.normpath(os.path.join(BASE, '..')))
sys.path.insert(0, GEN)
from rank_cert import rootv
T0 = time.time()
def nats(name, fn):
    s = open(os.path.join(LEAN, fn)).read(); s = s[s.index('def %s' % name):]; s = s[s.index(':= [') + 4:]
    return s
FL = [int(x) for x in re.findall(r'\d+', nats('flData', 'FLData.lean').split(']')[0])]
gs = nats('grpData', 'GrpData.lean'); gs = gs[:gs.index(']]') + 1]
GRP = [list(map(int, re.findall(r'\d+', b))) for b in re.findall(r'\[([^\[\]]*)\]', gs)]
assert len(FL) == 1152 and len(GRP) == 384 and all(len(g) == 104 for g in GRP)
rw = [r for r in json.load(open(os.path.join(BASE, 'orbitsW.json'))) if not r['frame']]
R = [int(r['mask']) for r in rw]
def bits(m): return [x for x in range(104) if m >> x & 1]
def pre(g, c): return sum(1 << x for x in range(104) if c >> GRP[g][x] & 1)
FLs = set(FL)
ok = all(sorted(pre(g, c) for c in FL) == sorted(FL) for g in range(384))
print('flClosed', ok, '%.0fs' % (time.time() - T0), flush=True); assert ok
W = []
for c in FL:
    e = next(((g, k) for k in range(9) for g in range(384) if all(c >> GRP[g][x] & 1 for x in bits(R[k]))), None)
    assert e is not None; W.append((c,) + e)
print('W', len(W), '%.0fs' % (time.time() - T0), flush=True)
RD = os.path.join(HERE, 'records'); os.makedirs(RD, exist_ok=True)
open(os.path.join(RD, 't2w.txt'), 'w').write(' '.join(map(str, [len(W)] + [x for e in W for x in e])) + '\n')
open(os.path.join(RD, 't2reps.txt'), 'w').write(' '.join(map(str, [len(R)] + R)) + '\n')
RV = [rootv(x) for x in range(104)]
def dot(a, b): return sum(p * q for p, q in zip(RV[a], RV[b]))
def rank(rows):
    M = [list(map(Fraction, r)) for r in rows]; r = 0
    for col in range(9):
        p = next((i for i in range(r, len(M)) if M[i][col] != 0), None)
        if p is None: continue
        M[r], M[p] = M[p], M[r]
        for i in range(len(M)):
            if i != r and M[i][col] != 0:
                f = M[i][col] / M[r][col]; M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        r += 1
    return r
def indep8(cand):
    sel = []
    for x in cand:
        if rank([RV[y] for y in sel + [x]]) == len(sel) + 1: sel.append(x)
        if len(sel) == 8: return sel
    return None
def inv_det(D):
    n = 8; M = [[Fraction(v) for v in row] + [Fraction(int(i == j)) for j in range(n)] for i, row in enumerate(D)]
    det = Fraction(1)
    for col in range(n):
        p = next((i for i in range(col, n) if M[i][col] != 0), None)
        if p is None: return None, 0
        if p != col: M[col], M[p] = M[p], M[col]; det = -det
        det *= M[col][col]; pv = M[col][col]; M[col] = [a / pv for a in M[col]]
        for i in range(n):
            if i != col and M[i][col] != 0:
                f = M[i][col]; M[i] = [a - f * b for a, b in zip(M[i], M[col])]
    return [row[n:] for row in M], det
def zz(v): return 2 * v if v >= 0 else -2 * v - 1
for k in range(9):
    DROP = {int(a): set(b) for a, b in json.load(open(os.path.join(BASE, 't2hand', 't2drop.json'))).items()}
    C = [x for x in bits(R[k]) if x not in DROP.get(k, set())]; Y = indep8(C); assert Y   # Gram target zm
    out = list(Y) + [len(FL)]
    for c2 in FL:
        X = indep8([x for x in C if c2 >> x & 1]); assert X, (k, c2)
        D = [[dot(x, y) for y in Y] for x in X]; Dinv, det = inv_det(D); assert det != 0
        dd = int(det); J = [[int(v * det) for v in row] for row in Dinv]
        assert all((v * det).denominator == 1 for row in Dinv for v in row)
        assert all(sum(D[i][t] * J[t][j] for t in range(8)) == (dd if i == j else 0) for i in range(8) for j in range(8))
        out += [c2] + X + [zz(v) for row in J for v in row] + [zz(dd)]
    os.makedirs(os.path.join(RD, 't2-%d' % k), exist_ok=True)
    open(os.path.join(RD, 't2-%d' % k, 'pairs.txt'), 'w').write(' '.join(map(str, out)) + '\n')
    print('T2PAIR', k, '|C|', len(C), 'partners', len(FL), 'Y', Y, '%.0fs' % (time.time() - T0), flush=True)
print('ALL OK')
