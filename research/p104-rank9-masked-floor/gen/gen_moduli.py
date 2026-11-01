"""Generate the T1 moduli certificate of one type for the Lean checker RankNine.Moduli.run.
Codes: unordered pair {a, b} of lines -> 104*min + max.  A relation (x, p, y, q) means N_x N_p = N_y N_q.
Output (JSON): rels (only the used ones, with their geometric origin t, s, frame, a, b), cov, steps (flat:
tag, args; tag 0 seed i j oi oj, 1 prop i o k, 2 trans k l, 3 symm k), and for every quadruple the fact indices
(root, e) of its four codes.  usage: gen_moduli.py rep out.json   (env DROP)"""
import sys, os, json
sys.path.insert(0, '.')
k = int(sys.argv[1]); outp = sys.argv[2]
sys.argv = ['x', str(k)]
src = open('logker.py').read(); exec(src[:src.index('rng = np.random')])
def code(a, b): return 104 * min(a, b) + max(a, b)
C = [code(*pr) for pr in pairs]          # pair index -> code
# relations with origin
relo = {}
for F in FZ:
    fi = FR.index(F) if False else None
FRi = {tuple(sorted(f)): i for i, f in enumerate(FR)}
for F in FZ:
    Fs = set(F)
    for t in Z:
        if t in Fs: continue
        Tt = [f for f in F if not ORTH[t][f]]
        for s in Z:
            if s <= t or s in Fs or not ORTH[t][s]: continue
            com = [f for f in Tt if not ORTH[s][f]]
            if len(com) == 2:
                a, b = com
                key = (code(t, a), code(s, a), code(t, b), code(s, b))
                relo.setdefault(key, (t, s, FRi[tuple(sorted(F))], a, b))
R = list(relo)
def orient(o, r):
    x, p, y, q = r
    return [(x, p, y, q), (p, x, y, q), (x, p, q, y), (p, x, q, y), (y, q, x, p), (q, y, x, p), (y, q, p, x), (q, y, p, x)][o % 8]
used = {}; usedl = []
def ui(ri):
    if ri not in used: used[ri] = len(usedl); usedl.append(ri)
    return used[ri]
facts = []; steps = []; LX = []   # lattice terms: (used relation index, coefficient + 32768)
def add(step, f): steps.append(step); facts.append(f); return len(facts) - 1
covset = set(C[j] for q in quads for j in q) if os.environ.get('QCOV', '1') == '1' else set(C)   # zero step proves N != 0 only on quadruple pairs
root = {c: c for c in C}; members = {c: [c] for c in C}; rf = {}     # rf[c] = fact index of (root[c], c)
def fact_of(u, v):
    """index of a fact (u, v) for u, v in the same class (derived from root facts)."""
    r = root[u]; assert root[v] == r
    if u == v and len(members[r]) == 1:
        return add((4, len(LX) // 2 % 65536, len(LX) // 2 // 65536, 0), (u, u))   # empty lattice step: N_u^2 = N_u^2
    if u == v:
        w = next(m for m in members[r] if m != r)
        a = rf[w]; b = add((3, a), (w, r))                       # (w, r)
        if u == r: return add((2, a, b), (r, r))
        c = add((2, rf[u], b), (u, r)) if False else None
    if u == r: return rf[v]
    su = add((3, rf[u]), (u, r))
    if v == r: return su
    return add((2, su, rf[v]), (u, v))
def merge(u, v, fi):
    """fact fi = (u, v) with u, v in different classes: re-root the smaller class at root[u]."""
    ru, rv = root[u], root[v]
    if len(members[ru]) < len(members[rv]):
        fi = add((3, fi), (v, u)); u, v, ru, rv = v, u, rv, ru
    # (ru, v)
    f_ru_v = fi if u == ru else add((2, rf[u], fi), (ru, v))
    old = {w: rf.get(w) for w in members[rv]}
    for w in members[rv]:
        if w == v: nf = f_ru_v
        else:
            # (v, w) in old class rv
            if v == rv: f_vw = old[w]
            else:
                sv = add((3, old[v]), (v, rv))
                f_vw = sv if w == rv else add((2, sv, old[w]), (v, w))
            nf = add((2, f_ru_v, f_vw), (ru, w))
        rf[w] = nf; root[w] = ru
    members[ru] += members[rv]; del members[rv]
# seeds
byplus = {}
for ri, r in enumerate(R):
    for o in range(8):
        x, p, y, q = orient(o, r); byplus.setdefault((x, p, y, q), (ri, o))
for (x, p, y, q), (ri, o) in list(byplus.items()):
    j = byplus.get((x, q, y, p))
    if j and root[x] != root[y] and p in covset and q in covset:
        fi = add((0, ui(ri), ui(j[0]), o, j[1]), (x, y)); merge(x, y, fi)
changed = True
while changed:
    changed = False
    for ri, r in enumerate(R):
        for o in range(8):
            x, p, y, q = orient(o, r)
            if root[x] == root[y] and root[p] != root[q] and x in covset:
                fx = fact_of(x, y); fi = add((1, ui(ri), o, fx), (p, q)); merge(p, q, fi); changed = True
def closure():
    changed = True
    while changed:
        changed = False
        for ri, r in enumerate(R):
            for o in range(8):
                x, p, y, q = orient(o, r)
                if root[x] == root[y] and root[p] != root[q] and x in covset:
                    fx = fact_of(x, y); fi = add((1, ui(ri), o, fx), (p, q)); merge(p, q, fi); changed = True
quadsC = [[C[j] for j in q] for q in quads]
ok = all(len({root[c] for c in q}) == 1 for q in quadsC)
nlat = 0
if not ok and os.environ.get('LAT', '1') == '1':
    # lattice seeds: 2(e_u - e_v) as an integer combination of relations whose four codes are covered
    import math
    def eg(a, b):
        if b == 0: return (1, 0)
        q_, r_ = divmod(a, b); s_, t_ = eg(b, r_); return (t_, s_ - q_ * t_)
    def lin(a, x, b, y):
        o = {}
        for j in set(x) | set(y):
            c = a * x.get(j, 0) + b * y.get(j, 0)
            if c: o[j] = c
        return o
    piv = {}
    def padd(v, w):
        while v:
            h = max(v)
            if v[h] < 0: v = {j: -c for j, c in v.items()}; w = {j: -c for j, c in w.items()}
            if h not in piv: piv[h] = (v, w); return
            pv, pw = piv[h]; a, b = pv[h], v[h]
            if b % a == 0:
                f = b // a; v = lin(1, v, -f, pv); w = lin(1, w, -f, pw)
            else:
                g = math.gcd(a, b); xx, yy = eg(a, b)
                piv[h] = (lin(xx, pv, yy, v), lin(xx, pw, yy, w)); v = lin(b // g, pv, -(a // g), v); w = lin(b // g, pw, -(a // g), w)
    for ri, r in enumerate(R):
        if all(c in covset for c in r):
            v = {}
            for c, e in zip(r, (1, 1, -1, -1)): v[c] = v.get(c, 0) + e
            padd({c: e for c, e in v.items() if e}, {ri: 1})
    def member(v):
        w = {}
        while v:
            h = max(v)
            if h not in piv or v[h] % piv[h][0][h]: return None
            f = v[h] // piv[h][0][h]; v = lin(1, v, -f, piv[h][0]); w = lin(1, w, f, piv[h][1])
        return w
    while not ok:
        q = next(q for q in quadsC if len({root[c] for c in q}) > 1)
        c = next(c for c in q[1:] if root[c] != root[q[0]])
        w = member({c: 2, q[0]: -2})
        assert w is not None, ('not in lattice', c, q[0])
        a = len(LX) // 2
        for ri, e in sorted(w.items()):
            assert abs(e) < 32768; LX += [ui(ri), e + 32768]
        fi = add((4, a % 65536, a // 65536, len(w)), (c, q[0])); merge(c, q[0], fi); nlat += 1
        closure()
        ok = all(len({root[c] for c in q}) == 1 for q in quadsC)
qf = []
for q in quadsC:
    r = root[q[0]]
    qf.append([r] + [(rf[c] if c != r else -1) for c in q])
json.dump({'rep': k, 'rels': [list(R[i]) for i in usedl], 'origin': [list(relo[R[i]]) for i in usedl], 'cov': sorted(covset),
           'steps': [list(s) for s in steps], 'lat': LX, 'facts_uv': [list(f) for f in facts], 'facts': len(facts), 'quads': quadsC, 'quadfacts': qf, 'ok': ok,
           'table': [[c, root[c], rf.get(c, -1) if c != root[c] else -1] for c in sorted(covset)]}, open(outp, 'w'))
print('rep', k, 'used relations', len(usedl), 'steps', len(steps), 'lattice seeds', nlat, 'terms', len(LX) // 2, 'quads', len(quads), 'ok', ok)
