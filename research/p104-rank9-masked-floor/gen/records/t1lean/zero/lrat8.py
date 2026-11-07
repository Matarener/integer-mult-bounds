"""LRAT proof of the T1 zero step from the contagion chains (contag.py), by an own unit-propagation engine with
reasons (each lemma is RUP; hints = the reason closure of the conflict in trail order).  Lemmas per chain
S = [v, w1, .., wn]:  (-v | w_i) for i = 1..n, then (-v).  Final: the empty clause from the goal clause
(some off-diagonal edge of the cert edge table is zero).  Writes origin JSON (format of t2zero_cnf.py) and LRAT.
usage: python3 t1lean/zero/lrat8.py k cert.json chains.json out-origin.json out.lrat"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cnf8
k = int(sys.argv[1]); cert = json.load(open(sys.argv[2])); ch = json.load(open(sys.argv[3]))
t0 = time.time()
VT, VID, cls, org, R, FZ, m = cnf8.build(k)
goal = [VID[('z', x, y)] for x, y in cert['EDG'] if x != y]
cls.append(goal); org.append(['G'])
ncls = len(cls)
nv = len(VT)
val = [0] * (nv + 1); reason = [0] * (nv + 1); pos = [0] * (nv + 1); trail = []
W = {}                                   # literal -> list of clause ids watching it
C = [None] + cls                         # clause ids from 1
def watch(ci):
    c = C[ci]
    if len(c) >= 2:
        W.setdefault(c[0], []).append(ci); W.setdefault(c[1], []).append(ci)
def lv(l): x = val[abs(l)]; return x if l > 0 else -x
def assign(l, r):
    v = abs(l); val[v] = 1 if l > 0 else -1; reason[v] = r; pos[v] = len(trail); trail.append(v)
def propagate(qi):
    """propagate from trail index qi; return conflicting clause id or 0"""
    while qi < len(trail):
        v = trail[qi]; qi += 1
        fl = -v if val[v] > 0 else v          # literal that became false
        ws = W.get(fl, []); i = 0
        while i < len(ws):
            ci = ws[i]; c = C[ci]
            if c[0] == fl: c[0], c[1] = c[1], c[0]
            if lv(c[0]) == 1: i += 1; continue
            for j in range(2, len(c)):
                if lv(c[j]) != -1:
                    c[1], c[j] = c[j], c[1]; ws[i] = ws[-1]; ws.pop(); W.setdefault(c[1], []).append(ci); break
            else:
                if lv(c[0]) == -1: return ci
                assign(c[0], ci); i += 1
                continue
    return 0
def hints_of(conf):
    need = set(); st = [conf]; seen = set()
    while st:
        ci = st.pop()
        if ci in need: continue
        need.add(ci)
        for l in C[ci]:
            v = abs(l)
            if v not in seen and reason[v] and reason[v] != ci: seen.add(v); st.append(reason[v])
    h = sorted((ci for ci in need if ci != conf), key=lambda ci: min(pos[abs(l)] for l in C[ci] if reason[abs(l)] == ci))
    return h + [conf]
def backtrack(n):
    while len(trail) > n:
        v = trail.pop(); val[v] = 0; reason[v] = 0
for ci in range(1, ncls + 1):
    if len(C[ci]) >= 2: watch(ci)
out = []; nid = [ncls]; lvl0 = [0]
def unit_at0(l, ci):
    if lv(l) == 1: return 0
    if lv(l) == -1: return ci
    assign(l, ci); q = len(trail) - 1
    return propagate(q)
for ci in range(1, ncls + 1):
    if len(C[ci]) == 1:
        r = unit_at0(C[ci][0], ci)
        assert not r, 'level-0 conflict from original units'
def lemma(lits):
    """RUP-check lits on top of level 0, record it, add it; return (id, conflict at level 0 after adding)"""
    n0 = len(trail); conf = 0
    if any(lv(l) == 1 for l in lits): return None, 0      # already satisfied at level 0: not needed
    for l in lits:
        if lv(l) == 0: assign(-l, 0)
    conf = propagate(n0)
    assert conf, ('not RUP', lits)
    h = hints_of(conf)
    backtrack(n0)
    nid[0] += 1; i = nid[0]; C.append(list(lits)); out.append('%d %s 0 %s 0' % (i, ' '.join(map(str, lits)), ' '.join(map(str, h))))
    if len(lits) >= 2: watch(i); return i, 0
    return i, unit_at0(lits[0], i)
nl = 0
for S in ch['chains']:
    v = S[0]
    for w in S[1:]: lemma([-v, w]); nl += 1
    i, r = lemma([-v]); nl += 1
    if r: break
else:
    for l in goal: assert lv(l) == -1, ('goal literal not refuted', VT[abs(l) - 1])
    r = ncls
need = hints_of(r)
nid[0] += 1; out.append('%d 0 %s 0' % (nid[0], ' '.join(map(str, need))))
open(sys.argv[5], 'w').write('\n'.join(out) + '\n')
open(sys.argv[4], 'w').write(json.dumps({'name': 'T1_%d' % k, 's0': -1, 'm': m, 'VT': VT, 'origin': org, 'FZ': FZ}))     # C encoder (json.dump is pure Python)
print('LRAT T1_%d originals %d lemmas %d final hints %d (conflict clause %d) %.0fs' % (k, ncls, nl, len(need), r, time.time() - t0), flush=True)
