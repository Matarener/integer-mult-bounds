"""Sign step of T1 as CNF (for an LRAT certificate), when the F2 elimination of gen_signs.py does not force the
magnitude bits.  Variables (bit + 1): bit c < TAG = sign of N at code c (1 = negative), bit TAG + K = magnitude bit
of quadruple class K (1 = |N| = 1/2).  Clauses (each forbids one 0/1 pattern on the atoms of a checked row):
* quadruple row (codes c1..c4, class K): allowed (s1..s4, m) are m = 0, no minus, or m = 1, exactly one minus;
* relation row (codes c1..c4 with classes K1..K4): sign parity even (patterns on s1..s4), and
  m_K1 + m_K2 = m_K3 + m_K4 (patterns on the four magnitude bits);
* goal: some class has magnitude bit 1.  UNSAT => every class has N = 1/4.
Rows are those of gen_signs.py (same JSON fields).  usage: sign_cnf.py rep moduli.json out.cnf out.json"""
import sys, json, os
sys.path.insert(0, '.')
from p104lib import frames, IDX, ORTH, N
k = int(sys.argv[1]); d = json.load(open(sys.argv[2])); outc, outj = sys.argv[3], sys.argv[4]
FR = [tuple(IDX[q] for q in f) for f in frames()]
reps = [r for r in json.load(open('orbitsW.json')) if r['frame']]
m = int(reps[k]['mask']); Z = [i for i in range(N) if m >> i & 1]
if os.environ.get('DROP'):
    _dr = set(map(int, os.environ['DROP'].split(','))); Z = [i for i in Z if i not in _dr]
Zs = set(Z)
FZ = [fi for fi, f in enumerate(FR) if all(i in Zs for i in f)]
def code(a, b): return 104 * min(a, b) + max(a, b)
root = {c: r for c, r, _ in d['table']}; entry = {c: e for e, (c, r, _) in enumerate(d['table'])}
TAG = 10816
quads = {}; rels = {}
for fi in FZ:
    F = FR[fi]
    for t in Z:
        if t in F: continue
        ks = [j for j in range(8) if not ORTH[t][F[j]]]
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
for r in R: assert all(root.get(c) in Kof for c in r[5])
nK = len(qroots)
def allowedQ(b): s = sum(b[:4]); return (b[4] == 0 and s == 0) or (b[4] == 1 and s == 1)
def bits(p, n): return [p >> i & 1 for i in range(n)]
cls = []; org = []
def forbid(atoms, b):   # clause: some atom differs from pattern b
    cls.append([(a + 1) if bi == 0 else -(a + 1) for a, bi in zip(atoms, b)])
for j, (t, fi, ks, cs) in enumerate(Q):
    atoms = list(cs) + [TAG + Kof[root[cs[0]]]]
    for p in range(32):
        b = bits(p, 5)
        if not allowedQ(b): forbid(atoms, b); org.append(['q', j, p])
for j, (t, s, fi, ka, kb, rc) in enumerate(R):
    for p in range(16):
        b = bits(p, 4)
        if sum(b) % 2: forbid(list(rc), b); org.append(['p', j, p])
    mat = [TAG + Kof[root[c]] for c in rc]
    for p in range(16):
        b = bits(p, 4)
        if b[0] + b[1] != b[2] + b[3]: forbid(mat, b); org.append(['m', j, p])
cls.append([TAG + K + 1 for K in range(nK)]); org.append(['g'])
with open(outc, 'w') as f:
    f.write('p cnf %d %d\n' % (TAG + nK, len(cls)))
    for c in cls: f.write(' '.join(map(str, c)) + ' 0\n')
json.dump({'rep': k, 'classes': qroots, 'origin': org,
           'quads': [[t, fi] + ks + [entry[c] for c in cs] + [Kof[root[cs[0]]]] for (t, fi, ks, cs) in Q],
           'rels': [[t, s, fi, ka, kb] + [entry[c] for c in rc] + [Kof[root[c]] for c in rc] for (t, s, fi, ka, kb, rc) in R]},
          open(outj, 'w'))
print('rep %d quads %d relations %d classes %d clauses %d' % (k, len(Q), len(R), nK, len(cls)), flush=True)
