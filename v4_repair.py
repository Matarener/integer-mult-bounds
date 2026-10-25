# Repair the CP-SAT near-decoder (few violated mask entries) into an EXACT decoder with extra rank-1 terms,
# then recompute the true total tariff and re-verify the whole mask from scratch.
import json, sys
from collections import defaultdict
from v4lib import *
labels, pairs = load_geometry(); planes = [(labels[a], labels[b]) for a, b in pairs]; NP = len(planes); NPORT = 112
E = [0] * NPORT
for i, (a, b) in enumerate(pairs): E[a] = i; E[b] = i
ORTH = [[i != j and all(dot(x, y) == 0 for x in planes[i] for y in planes[j]) for j in range(NP)] for i in range(NP)]
fixed = {(p, q): int(p == q) for p in range(NPORT) for q in range(NPORT) if p == q or E[p] == E[q] or not ORTH[E[p]][E[q]]}
def pm(w): return sorted({E[p] for p in range(NPORT) if w >> p & 1})
def spn(ps): return span([v for i in ps for v in planes[i]])
def tariff(U, V): return pair_rank(spn(pm(U)), spn(pm(V))) if U and V else 0
def matrix(terms):
    rows = [0] * NPORT
    for U, V in terms:
        for p in range(NPORT):
            if U >> p & 1: rows[p] ^= V
    return rows
res = json.load(open(sys.argv[1]))
terms = [(int(u, 16), int(v, 16)) for u, v in res['terms']]
rows = matrix(terms)
bad = [(p, q) for (p, q), t in fixed.items() if (rows[p] >> q & 1) != t]
base = sum(tariff(U, V) for U, V in terms)
print('solution: terms', len(terms), 'true cost', base, 'violated entries', len(bad))
# candidate repairs
byrow = defaultdict(int); bycol = defaultdict(int)
for p, q in bad: byrow[p] |= 1 << q; bycol[q] |= 1 << p
def group(d, as_rows):
    g = defaultdict(int)                          # identical pattern -> merged index set
    for k, w in d.items(): g[w] |= 1 << k
    return [((idx, w) if as_rows else (w, idx)) for w, idx in g.items()]
options = {
    'per row': [(1 << p, w) for p, w in byrow.items()],
    'per column': [(w, 1 << q) for q, w in bycol.items()],
    'rows merged': group(byrow, True),
    'columns merged': group(bycol, False),
}
best = None
for name, fix in options.items():
    full = terms + fix
    r2 = matrix(full); viol = sum(1 for (p, q), t in fixed.items() if (r2[p] >> q & 1) != t)
    cost = sum(tariff(U, V) for U, V in full)
    print('%-15s fix terms %3d  fix cost %3d  -> total %d, violations after repair %d' % (name, len(fix), cost - base, cost, viol))
    if viol == 0 and (best is None or cost < best[0]): best = (cost, name, full)
if best:
    cost, name, full = best
    json.dump({'cost': cost, 'repair': name, 'terms': [[hex(u), hex(v)] for u, v in full], 'verified_mask': True},
              open('v4_repaired_decoder.json', 'w'))
    print('BEST EXACT DECODER: cost %d via %s  (known best 224; to tie the word need <= 160-164)' % (cost, name))
print('violated cells:', [(p, q, E[p], E[q], fixed[(p, q)]) for p, q in bad][:40])
