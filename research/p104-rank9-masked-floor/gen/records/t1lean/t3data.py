"""T3 record (Lean `RankNine.T3D`) for a framed type without special line, on the zm of its T1 record:
line certificates for every line outside zm (rank 7 over zm, `lineOK`), pair certificates for the glued rows
O' = lines outside Z over the mask sm = zm ∪ OL (`pcOK`), bad pairs, match / five checks replayed (as
gen/emit_glue.py, which wrote the old Cert/Glue<k>.lean with zm = Z).  Writes the record as a number stream
(field order of T3Decode).  usage: python3 t1lean/t3data.py k t1cert.json out.txt"""
import sys, os, json, time
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEN = os.path.normpath(os.path.join(BASE, '..'))
sys.path.insert(0, GEN); os.chdir(GEN)
from p104lib import ORTH, P, RT, N as NL, frames, IDX
from rank_cert import cert, rootv, check
k = int(sys.argv[1]); c1 = json.load(open(sys.argv[2])); out = sys.argv[3]
T0 = time.time()
reps = [r for r in json.load(open('orbitsW.json')) if r['frame']]
m = int(reps[k]['mask']); Z = [i for i in range(NL) if m >> i & 1]; Zs = set(Z)
ZM = sorted(c1['ZM']); ZMs = set(ZM); zm = sum(1 << x for x in ZM)
assert ZMs <= Zs
def dot(a, b): return sum(x * y for x, y in zip(rootv(a), rootv(b)))
def G3(a, b, c):
    x, y, z = dot(a, b), dot(a, c), dot(b, c)
    return 5832 + 2 * x * y * z - 18 * (x * x + y * y + z * z)
badl = []; LT = []
for v in range(NL):
    if v in ZMs: continue
    rv = rootv(v); k0 = next(i for i in range(9) if rv[i])
    c = cert([x for x in ZM if ORTH[x][v]], [k0])
    if c is None: badl.append(v); continue
    assert check(*c) and all(x in ZMs and dot(v, x) == 0 for x in c[0])
    LT.append((v, k0) + tuple(c))
if len(badl) > 1 or (badl and badl[0] in Zs and os.environ.get('T3POOR') != '1'):
    print('T3 %d NOPIN %s' % (k, badl), flush=True); sys.exit(2)
OL = [v for v in range(NL) if v not in ZMs and v not in badl]; OLs = set(OL); sm = zm | sum(1 << x for x in OL)
U = badl[0] if badl else 104
SP = (0, 0, 0, 0, ([], [], [], 0, 0), ([], [], [], 0, 0)); GC = []; BsL = []
if badl:     # special line U outside Z (as gen/emit_glue.py + gen/emit_t3.py)
    ku = next(i for i in range(9) if rootv(U)[i]); X0 = [x for x in ZM if ORTH[x][U]]
    good = [(s_, cert(X0 + [s_], [ku])) for s_ in OL if ORTH[s_][U]]
    good = [(s_, c) for s_, c in good if c is not None]
    for s_, c in good: assert check(*c) and all((x in ZMs or x == s_) and ORTH[x][U] for x in c[0])
    sp = next(((s1, s2, c1, c2) for s1, c1 in good for s2, c2 in good if s1 < s2 and ORTH[s1][s2]), None)
    if sp is None: print('T3 %d NOSPECIAL %d' % (k, U), flush=True); sys.exit(2)
    SP = (sp[0], sp[1], ku, ku, sp[2], sp[3]); GC = [(s_, ku, c) for s_, c in good]
    G = [s_ for s_, _, _ in GC]
    BsL = sorted([s_ for s_ in range(NL) if s_ != U and not any(ORTH[s_][v] for v in G)] + [U])
    if not (len(set(G)) >= 5 and len(BsL) <= 4): print('T3 %d SPECIALFAIL G %d BsL %s' % (k, len(G), BsL)); sys.exit(2)
Op = [v for v in range(NL) if v not in Zs]
T = []; bad = []
for a in range(len(Op)):
    for b in range(a + 1, len(Op)):
        v, w = Op[a], Op[b]; rv, rw = rootv(v), rootv(w)
        k0, k1 = next((i, j) for i in range(9) for j in range(i + 1, 9) if rv[i] * rw[j] - rv[j] * rw[i])
        c = cert([x for x in ZM + OL if ORTH[x][v] and ORTH[x][w]], [k0, k1])
        if c is None: bad.append((v, w)); continue
        X, N, No, D, pm = c
        assert check(X, N, No, D, pm) and all((x in ZMs or x in OLs) and dot(v, x) == 0 and dot(w, x) == 0 for x in X)
        T.append((v, w, k0, k1, X, N, No, D, pm))
deg = {}
for p in bad:
    for x in p: deg[x] = deg.get(x, 0) + 1
assert max(deg.values(), default=0) <= 1, 'matching fails'
def planB(a, a2, b, b2, e):
    t = lambda x, y: G3(x, y, e) != 0
    return (t(a, b) and t(a2, b)) or (t(a, b) and t(a, b2)) or (t(a2, b2) and t(a2, b)) or (t(a2, b2) and t(a, b2))
for p in bad:
    for q in bad:
        for e in Op:
            if len({p[0], p[1], q[0], q[1], e}) < 5: continue
            assert planB(p[0], p[1], q[0], q[1], e), ('plan', p, q, e)
FR = [tuple(IDX[q] for q in f) for f in frames()]
fi = next(i for i, f in enumerate(FR) if all(x in ZMs for x in f))
s = []
def nat(x): s.append(int(x))
def zint(x): s.append(2 * x if x >= 0 else -2 * x - 1)          # integers zig-zag encoded
def lst(l): nat(len(l)); s.extend(int(v) for v in l)
def rcert(X, N, No, D, pm):
    lst(X); nat(len(N))
    for r in N: nat(len(r)); [zint(x) for x in r]
    nat(len(No)); [zint(x) for x in No]; zint(D); nat(pm)
nat(fi); nat(zm); nat(sm); lst(OL); lst(Op)
nat(len(bad)); [s.extend(p) for p in bad]
nat(len(T))
for v, w, k0, k1, X, N, No, D, pm in T: nat(v); nat(w); nat(k0); nat(k1); rcert(X, N, No, D, pm)
nat(len(LT))
for v, k0, X, N, No, D, pm in LT: nat(v); nat(k0); rcert(X, N, No, D, pm)
nat(U); nat(SP[0]); nat(SP[1]); nat(SP[2]); nat(SP[3]); rcert(*SP[4]); rcert(*SP[5])
nat(len(GC))
for s_, k0, c in GC: nat(s_); nat(k0); rcert(*c)
lst(BsL)
open(out, 'w').write(' '.join(map(str, s)) + '\n')
print('T3 %d U %d frame %d |OL| %d |O| %d pairs %d bad %d lines %d numbers %d %.0fs' % (k, U, fi, len(OL), len(Op), len(T), len(bad), len(LT), len(s), time.time() - T0), flush=True)
