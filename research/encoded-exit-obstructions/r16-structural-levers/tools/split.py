"""R16 lever screen: free helper splits. A rank-k helper h can be split at an intermediate frame F
(two independent productive helpers of ranks dim F - start and final - dim F, same paid climbs)
for free only if, at some point while h sits at F with climbs still ahead, h's row is pure
(only its own input variable) AND no other register (incl. owned C0) holds h's input variable.
Exact rows replay (verify_buffers primitives; rows are frame-independent in the native semantics)."""
import sys, gzip, json
from collections import Counter, defaultdict
from fractions import Fraction as Q
from pathlib import Path
R13 = Path.home()/'imb-r13'
sys.path.insert(0, str(R13/'research/kappa-causal-continuation/buffer-borrowing'))
import verify_buffers as v
w = json.loads(gzip.decompress((R13/'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz').read_bytes()))
c = w['canonical']; fr = c['frames']
def dim(f): return len(fr[f])
for side in ('forward', 'backward'):
    back = side == 'backward'; prog = w['programs'][side]
    rows = {('L', i): v.identity(('L', i)) for i in range(632)}; rows['C', 0] = v.identity(('C', 0))
    cur = {('L', i): f for i, f in enumerate(c['start'])}
    inv = defaultdict(set)
    for r, row in rows.items():
        for (var, wd) in row: inv[var].add(r)
    def vars_of(row): return {var for (var, wd) in row}
    # remaining climbs per register from each position
    climbs_left = Counter(e[2] for e in prog if e[0] == 'climb')
    def clean(h):
        return vars_of(rows[h]) <= {h} and inv[h] <= {h}
    found = defaultdict(set); ever_clean_mid = Counter()
    for j, e in enumerate(prog):
        k = e[0]; changed = []
        if k == 'scalar':
            g, frame = e[1:]; t = tuple(g[1])
            old = vars_of(rows[t])
            if g[0] == 'clear': rows[t] = {}
            elif g[0] == 'copy': rows[t] = dict(rows[tuple(g[2])])
            elif g[0] == 'add': v.add(rows[t], rows[tuple(g[2])], Q(g[3], g[4]))
            else: q = Q(g[2], g[3]); rows[t] = {a: q*x for a, x in rows[t].items()}
            new = vars_of(rows[t])
            for var in old - new: inv[var].discard(t)
            for var in new - old: inv[var].add(t)
            changed = [t] + [var for var in old - new]
        elif k == 'warp':
            _, r, op, old_f, new_f = e; t = tuple(r); rows[t] = v.warp(rows[t], op, back); cur[t] = new_f
        elif k == 'climb':
            i = e[2]; cur['L', i] = e[4]; climbs_left[i] -= 1
            changed = [('L', i)]
        for h in changed:
            if h[0] != 'L' or h[1] < 224: continue
            i = h[1]; d = dim(cur[h]); d0 = dim(c['start'][i]); d1 = dim(c['final'][i])
            if d0 < d < d1 and climbs_left[i] > 0 and clean(h):
                found[i].add(d)
    tot = Counter(); 
    for i, ds in found.items():
        for d in ds: tot[(dim(c['start'][i]), d, dim(c['final'][i]))] += 1
    print(side, 'helpers with a free split point:', len(found), 'split options', sum(tot.values()), dict(sorted(tot.items())))
