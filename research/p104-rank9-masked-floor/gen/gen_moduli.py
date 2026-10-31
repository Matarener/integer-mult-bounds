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
facts = []; steps = []
def add(step, f): steps.append(step); facts.append(f); return len(facts) - 1
covset = set(C)
root = {c: c for c in C}; members = {c: [c] for c in C}; rf = {}     # rf[c] = fact index of (root[c], c)
def fact_of(u, v):
    """index of a fact (u, v) for u, v in the same class (derived from root facts)."""
    r = root[u]; assert root[v] == r
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
quadsC = [[C[j] for j in q] for q in quads]
ok = all(len({root[c] for c in q}) == 1 for q in quadsC)
qf = []
for q in quadsC:
    r = root[q[0]]
    qf.append([r] + [(rf[c] if c != r else -1) for c in q])
json.dump({'rep': k, 'rels': [list(R[i]) for i in usedl], 'origin': [list(relo[R[i]]) for i in usedl], 'cov': sorted(covset),
           'steps': [list(s) for s in steps], 'facts': len(facts), 'quads': quadsC, 'quadfacts': qf, 'ok': ok,
           'table': [[c, root[c], rf.get(c, -1) if c != root[c] else -1] for c in sorted(covset)]}, open(outp, 'w'))
print('rep', k, 'used relations', len(usedl), 'steps', len(steps), 'quads', len(quads), 'ok', ok)
