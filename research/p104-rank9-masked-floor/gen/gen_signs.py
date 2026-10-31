"""T1 sign step certificate (F2) for one framed type, for the Lean checker RankNine.Signs.
Input: the moduli certificate JSON of gen_moduli.py (code table: code -> class root).
Variables: sign bit of N at each code (bit = code), magnitude bit of each quadruple class (bit = 10816 + K).
Rows: relation (t, s, f, ka, kb): sign parity of its 4 codes = 0; quadruple (t, f, k1..k4): sign parity of its 4 codes
+ magnitude bit of its class = 0.  For every class K the output lists a set of rows whose XOR is the single bit of K
(so the magnitude bit is 0 and N = 1/4 on the class).  usage: gen_signs.py rep moduli.json out.json"""
import sys, json, time
sys.path.insert(0, '.')
from p104lib import frames, IDX, ORTH, N
T0 = time.time()
k = int(sys.argv[1]); d = json.load(open(sys.argv[2])); outp = sys.argv[3]
FR = [tuple(IDX[q] for q in f) for f in frames()]
reps = [r for r in json.load(open('orbitsW.json')) if r['frame']]
m = int(reps[k]['mask']); Z = [i for i in range(N) if m >> i & 1]; Zs = set(Z)
FZ = [fi for fi, f in enumerate(FR) if all(i in Zs for i in f)]
def code(a, b): return 104 * min(a, b) + max(a, b)
root = {c: r for c, r, _ in d['table']}; entry = {c: e for e, (c, r, _) in enumerate(d['table'])}
TAG = 10816
# quadruple rows and relation rows (unique by code content)
quads = {}; rels = {}
for fi in FZ:
    F = FR[fi]
    for t in Z:
        if t in F: continue
        ks = [j for j in range(8) if not ORTH[t][F[j]]]
        assert len(ks) == 4
        cs = tuple(code(t, F[j]) for j in ks)
        quads.setdefault(tuple(sorted(cs)), (t, fi, ks, cs))
        for s in Z:
            if s <= t or s in F or not ORTH[t][s]: continue
            com = [j for j in ks if not ORTH[s][F[j]]]
            if len(com) == 2:
                ka, kb = com; a, b = F[ka], F[kb]
                rc = (code(t, a), code(s, a), code(t, b), code(s, b))
                rels.setdefault(tuple(sorted(rc)), (t, s, fi, ka, kb, rc))
Q = list(quads.values()); R = list(rels.values())
qroots = sorted(set(root[q[3][0]] for q in Q)); Kof = {r: j for j, r in enumerate(qroots)}
for q in Q: assert len({root[c] for c in q[3]}) == 1
for r in R: assert all(root.get(c) in Kof for c in r[5]), 'relation code outside quadruple classes'
nK = len(qroots)
rows = []
for q in Q:
    v = 0
    for c in q[3]: v ^= 1 << c
    rows.append(v ^ (1 << (TAG + Kof[root[q[3][0]]])))
nQd = len(rows)
for r in R:
    v = 0
    for c in r[5]: v ^= 1 << c
    rows.append(v)
print('[%6.1fs] type %d quads %d relations %d classes %d' % (time.time() - T0, k, len(Q), len(R), nK), flush=True)
# elimination on code bits (< TAG) with row-history bitmasks; constraints (rows with no code bits) are reduced on
# the class bits at once, and the scan stops as soon as all class bits are forced
piv = {}; tb = {}; ncons = 0
for i, v in enumerate(rows):
    h = 1 << i
    while v & ((1 << TAG) - 1):
        b = (v & ((1 << TAG) - 1)).bit_length() - 1
        if b in piv: pv, ph = piv[b]; v ^= pv; h ^= ph
        else: piv[b] = (v, h); break
    else:
        v >>= TAG; ncons += 1
        while v:
            b = v.bit_length() - 1
            if b in tb: pv, ph = tb[b]; v ^= pv; h ^= ph
            else: tb[b] = (v, h); break
        if len(tb) == nK: break
print('[%6.1fs] constraints %d, rows scanned %d' % (time.time() - T0, ncons, i + 1), flush=True)
assert len(tb) == nK, 'magnitude bits not forced'
for b in sorted(tb):            # back-substitute to unit vectors
    v, h = tb[b]
    for c in sorted(tb):
        if c < b and v >> c & 1: cv, ch = tb[c]; v ^= cv; h ^= ch
    tb[b] = (v, h)
combos = []
for K in range(nK):
    v, h = tb[K]; assert v == 1 << K
    combos.append([i for i in range(len(rows)) if h >> i & 1])
Kq = []
for K in range(nK):            # a designated quadruple row for every class (its magnitude is 1/16 or 1/4)
    Kq.append(next(i for c in combos for i in c if i < nQd and Kof[root[Q[i][3][0]]] == K) if any(
        i < nQd and Kof[root[Q[i][3][0]]] == K for c in combos for i in c) else next(i for i in range(nQd) if Kof[root[Q[i][3][0]]] == K))
used = sorted(set(i for c in combos for i in c) | set(Kq))
print('[%6.1fs] combo sizes total %d max %d, rows used %d of %d' % (time.time() - T0, sum(map(len, combos)), max(map(len, combos)), len(used), len(rows)), flush=True)
for K, c in enumerate(combos):
    v = 0
    for i in c: v ^= rows[i]
    assert v == 1 << (TAG + K)
uq = [i for i in used if i < nQd]; ur = [i for i in used if i >= nQd]
new = {i: j for j, i in enumerate(uq + ur)}
json.dump({'rep': k, 'classes': qroots,
           'quads': [[t, fi] + ks + [entry[c] for c in cs] + [Kof[root[cs[0]]]] for (t, fi, ks, cs) in (Q[i] for i in uq)],
           'rels': [[t, s, fi, ka, kb] + [entry[c] for c in rc] + [Kof[root[c]] for c in rc] for (t, s, fi, ka, kb, rc) in (R[i - nQd] for i in ur)],
           'classQuad': [new[i] for i in Kq], 'combos': [[new[i] for i in c] for c in combos]}, open(outp, 'w'))
print('[%6.1fs] SIGNS OK type %d rows %d+%d' % (time.time() - T0, k, len(uq), len(ur)), flush=True)
