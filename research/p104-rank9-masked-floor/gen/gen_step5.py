"""T1 step 5 certificate (signs => Gram on covered pairs) for one framed type, for RankNine.Step5.
Gauge along a BFS tree of the covered-pair graph, then peeling with R1 4-cycles and two-term 3-cycles; every new
undirected edge gives a directed fact and its reversal.  N = 1/4 on covered codes via quadruple rows (checked against
the moduli table and the sign certificate's classes).  usage: gen_step5.py rep moduli.json signs.json out.json"""
import sys, json, time
from collections import defaultdict
sys.path.insert(0, '.')
from p104lib import frames, IDX, ORTH, N, RT, P as PL104
T0 = time.time()
k = int(sys.argv[1]); dm = json.load(open(sys.argv[2])); ds = json.load(open(sys.argv[3])); outp = sys.argv[4]
FR = [tuple(IDX[q] for q in f) for f in frames()]
reps = [r for r in json.load(open('orbitsW.json')) if r['frame']]
m = int(reps[k]['mask']); Z = [i for i in range(N) if m >> i & 1]; Zs = set(Z)
FZ = [fi for fi, f in enumerate(FR) if all(i in Zs for i in f)]
def code(a, b): return 104 * min(a, b) + max(a, b)
def E(a, b): return (min(a, b), max(a, b))
def dot(a, b): return sum(x * y for x, y in zip(RT[PL104[a]], RT[PL104[b]]))
root = {c: r for c, r, _ in dm['table']}; entry = {c: e for e, (c, r, _) in enumerate(dm['table'])}
Kof = {r: j for j, r in enumerate(ds['classes'])}
# quadruples (also the N = 1/4 table)
quadOf = {}; QR = []
for fi in FZ:
    F = FR[fi]
    for t in Z:
        if t in F: continue
        ks = [j for j in range(8) if not ORTH[t][F[j]]]
        cs = [code(t, F[j]) for j in ks]
        if any(c not in quadOf for c in cs):
            jq = len(QR); QR.append([t, fi] + ks + [entry[c] for c in cs] + [Kof[root[cs[0]]]])
            for l, c in enumerate(cs): quadOf.setdefault(c, (jq, l))
cov = set(E(c // 104, c % 104) for c in quadOf)
NTi = {}; NT = []
def nt(a, b):
    c = code(a, b)
    if c not in NTi: NTi[c] = len(NT); jq, l = quadOf[c]; NT.append([c, jq, l])
    return NTi[c]
# relations
R1 = []; TRI = []
for fi in FZ:
    F = FR[fi]; Fs = set(F); T = {x: frozenset(j for j in range(8) if not ORTH[x][F[j]]) for x in Z if x not in Fs}
    for t in T:
        for s in T:
            if s <= t: continue
            com = T[t] & T[s]
            if len(com) != 2: continue
            ka, kb = sorted(com)
            if ORTH[t][s]: R1.append((t, s, fi, ka, kb))
            elif E(t, s) in cov: TRI.append((t, s, fi, ka, kb))
adj = defaultdict(list)
for a, b in cov: adj[a].append(b); adj[b].append(a)
verts = sorted(adj); V = [verts[0]]; par = {verts[0]: 0}; idx = {verts[0]: 0}
for x in V:
    for y in sorted(adj[x]):
        if y not in idx: idx[y] = len(V); par[y] = idx[x]; V.append(y)
assert len(V) == len(verts), 'covered graph not connected'
facts = []; fidx = {}; steps = []
def addf(x, y, st):
    fidx[(x, y)] = len(facts); facts.append((x, y)); steps.append(st + [0] * (14 - len(st)))
def addrev(x, y):
    addf(y, x, [1, fidx[(x, y)], nt(x, y)])
known = set()
TN = [0] * len(V)
for i in range(1, len(V)):
    p, v = V[par[V[i]]], V[i]
    TN[i] = nt(p, v); addf(p, v, [0, i]); addrev(p, v); known.add(E(p, v))
# cycles: list of (kind, data, edges)
cyc = []
for (t, s, fi, ka, kb) in R1:
    F = FR[fi]; a, b = F[ka], F[kb]
    es = [E(t, a), E(a, s), E(s, b), E(b, t)]
    if all(e in cov for e in es): cyc.append(('r1', (t, s, fi, ka, kb), es))
for (t, y, fi, ka, kb) in TRI:
    F = FR[fi]
    for (kx, ko) in ((ka, kb), (kb, ka)):
        a = F[kx]; es = [E(t, a), E(a, y), E(t, y)]
        cyc.append(('tri', (t, y, fi, kx, ko), es))
byedge = defaultdict(list)
for ci, c in enumerate(cyc):
    for e in c[2]: byedge[e].append(ci)
unk = [sum(1 for e in c[2] if e not in known) for c in cyc]
q = [ci for ci, u in enumerate(unk) if u == 1]
def derive(ci, e):
    kind, (t, s, fi, ka, kb), _ = cyc[ci]; F = FR[fi]
    if kind == 'r1':
        a, b = F[ka], F[kb]
        x = e[0] if e[0] in (t, s) and e[1] in (a, b) else e[1]; w = e[1] if x == e[0] else e[0]
        s2 = x; t2 = s if x == t else t; kb2 = ka if w == a else kb; ka2 = kb if w == a else ka
        a2, b2 = F[ka2], F[kb2]
        assert dot(t2, a2) * dot(a2, s2) == -(dot(t2, b2) * dot(b2, s2)) and dot(t2, b2) != 0
        addf(b2, s2, [2, t2, s2, fi, ka2, kb2, fidx[(t2, a2)], fidx[(a2, s2)], fidx[(t2, b2)]]); addrev(b2, s2)
    else:
        a, b = F[ka], F[kb]; y = s
        ns = lambda t_, y_: [nt(t_, a), nt(a, y_), nt(t_, b), nt(b, y_), nt(t_, y_)]
        if e == E(t, y):
            assert dot(t, a) * dot(a, y) == 9 * dot(t, y)
            addf(t, y, [3, t, y, fi, ka, kb, fidx[(t, a)], fidx[(a, y)]] + ns(t, y)); addrev(t, y)
        else:
            t2, y2 = (t, y) if e == E(a, y) else (y, t)
            assert dot(t2, a) * dot(a, y2) == 9 * dot(t2, y2) and dot(t2, a) != 0
            addf(a, y2, [4, t2, y2, fi, ka, kb, fidx[(t2, a)], fidx[(t2, y2)]] + ns(t2, y2)); addrev(a, y2)
while q:
    ci = q.pop()
    if unk[ci] != 1: continue
    e = next(e for e in cyc[ci][2] if e not in known)
    derive(ci, e); known.add(e)
    for cj in byedge[e]:
        unk[cj] -= 1
        if unk[cj] == 1: q.append(cj)
left = len(cov) - len(known)
assert left == 0, 'peeling left %d edges' % left
II = [0] * 104
for i, x in enumerate(V): II[x] = i
for i, x in enumerate(V): assert II[V[i]] == i
json.dump({'rep': k, 'V': V, 'PL': [par[x] for x in V], 'II': II, 'TN': TN, 'NQ': QR, 'NT': NT,
           'FS': [list(f) for f in facts], 'ST': steps}, open(outp, 'w'))
print('[%6.1fs] STEP5 OK type %d vertices %d covered %d facts %d quads %d ntable %d' % (
    time.time() - T0, k, len(V), len(cov), len(facts), len(QR), len(NT)), flush=True)
