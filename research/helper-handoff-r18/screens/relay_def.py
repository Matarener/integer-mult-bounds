"""R18 relay screen (generalises R16 split.py).

Relay lemma.  At a time t, helper h (input variable h_in) sits at frame F strictly between its
start and final dims with climbs ahead.  Let R_F = registers whose current frame index is F.
If (a) every register whose row mentions h_in (any warp word) is in R_F, and
   (b) h_in occurs only with the trivial word and (h_in, ()) lies in the Q-span of the rows of R_F,
then a FRESH arbitrary helper h' that STARTS at frame F can be inserted, and free scalar ops at F
realise the substitution tau = swap(h_in, h'_in) on the whole state.  Every later op is linear, so the
final state is tau(original final): register h ends holding h'_in (transformed F -> final) and the
new register ends at F holding h_in (transformed start -> F).  Paid climbs are unchanged; the
rank-k productive target splits into (dimF - d0) + (d1 - dimF).
This script only SCREENS for such points (exact rows over Q)."""
import sys, gzip, json
from collections import Counter, defaultdict
from fractions import Fraction as Q
from pathlib import Path
R13 = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(R13/'research/kappa-causal-continuation/buffer-borrowing'))
import verify_buffers as v
w = json.loads(gzip.decompress((R13/'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz').read_bytes()))
c = w['canonical']; fr = c['frames']
def dim(f): return len(fr[f]) if f is not None else -1

def in_span(target, vecs):
    """exact: is target (dict) in Q-span of vecs (list of dicts)?"""
    piv = []  # list of (pivot key, row dict) reduced
    def reduce(x):
        x = dict(x)
        for k, r in piv:
            a = x.get(k)
            if a:
                for kk, vv in r.items():
                    nv = x.get(kk, Q(0)) - a*vv
                    if nv: x[kk] = nv
                    else: x.pop(kk, None)
        return x
    for vec in vecs:
        x = reduce(vec)
        if x:
            k = next(iter(x)); a = x[k]; x = {kk: vv/a for kk, vv in x.items()}
            # keep piv fully reduced w.r.t. new pivot
            for i, (k2, r2) in enumerate(piv):
                b = r2.get(k)
                if b:
                    for kk, vv in x.items():
                        nv = r2.get(kk, Q(0)) - b*vv
                        if nv: r2[kk] = nv
                        else: r2.pop(kk, None)
            piv.append((k, x))
    return reduce(target)

def screen(side, relax=False):
    back = side == 'backward'; prog = w['programs'][side]
    rows = {('L', i): v.identity(('L', i)) for i in range(632)}; rows['C', 0] = v.identity(('C', 0))
    cur = {('L', i): f for i, f in enumerate(c['start'])}; cur['C', 0] = None
    inv = defaultdict(set)
    for r, row in rows.items():
        for (var, wd) in row: inv[var].add(r)
    atF = defaultdict(set)
    for r, f in cur.items(): atF[f].add(r)
    def setf(r, f):
        atF[cur[r]].discard(r); cur[r] = f; atF[f].add(r)
    climbs_left = Counter(e[2] for e in prog if e[0] == 'climb')
    helpers = [('L', i) for i in range(224, 632)]
    best = {}; seen = set(); found = defaultdict(set); first = {}; nspan = 0; npass_a = Counter()
    for j, e in enumerate(prog):
        k = e[0]
        if k == 'scalar':
            g, frame = e[1:]; t = tuple(g[1])
            old = {var for (var, wd) in rows[t]}
            if g[0] == 'clear': rows[t] = {}; setf(t, frame)
            elif g[0] == 'copy': rows[t] = dict(rows[tuple(g[2])])
            elif g[0] == 'add': v.add(rows[t], rows[tuple(g[2])], Q(g[3], g[4]))
            else: q = Q(g[2], g[3]); rows[t] = {a: q*x for a, x in rows[t].items()}
            new = {var for (var, wd) in rows[t]}
            for var in old - new: inv[var].discard(t)
            for var in new - old: inv[var].add(t)
        elif k == 'warp':
            _, r, op, old_f, new_f = e; t = tuple(r); rows[t] = v.warp(rows[t], op, back); setf(t, new_f)
        elif k == 'climb':
            i = e[2]; setf(('L', i), e[4]); climbs_left[i] -= 1
        elif k == 'center':
            setf(('C', e[1]), e[3])
        else:
            continue
        # check every helper (cheap filter (a) first)
        for h in helpers:
            i = h[1]
            if climbs_left[i] <= 0: continue
            F = cur[h]; d = dim(F); d0 = dim(c['start'][i])
            if not d0 < d: continue
            hold = inv[h]
            if not hold <= atF[F]: continue
            npass_a[i] += 1
            key = (i, d)
            if key in found and not relax: continue
            if (i, d, len(atF[F])) in seen: continue
            seen.add((i, d, len(atF[F])))
            # (b) trivial words only, span
            if any(wd != () for r in hold for (var, wd) in rows[r] if var == h): continue
            nspan += 1
            res = in_span({(h, ()): Q(1)}, [rows[r] for r in atF[F]])
            if not res:
                found[i].add(d); first.setdefault(key, (j, sorted(atF[F]), len(hold)))
            else:
                # deficiency: residual of h's own row against the OTHER registers at F
                rr = in_span(rows[h], [rows[r] for r in atF[F] if r != h])
                dv = len({var for (var, wd) in rr} - {h})
                if dv < best.get(i, (99,))[0]: best[i] = (dv, d, j, len(atF[F]))
    tot = Counter()
    for i, ds in found.items():
        for d in ds: tot[(dim(c['start'][i]), d, dim(c['final'][i]))] += 1
    print(side, 'helpers with a relay point:', len(found), 'options', sum(tot.values()), dict(sorted(tot.items())),
          '| (a)-passes helpers', len(npass_a), 'span checks', nspan, flush=True)
    for key, val in sorted(first.items())[:40]:
        print('  ', key, 'event', val[0], 'holders', val[2], 'R_F', val[1][:8], len(val[1]))
    print(side, 'deficiency histogram (min #foreign input vars left in h after cancelling with co-framed rows):', Counter(b[0] for b in best.values()))
    for i, b in sorted(best.items(), key=lambda kv: kv[1])[:15]: print('   h', i, 'deficiency,dim,event,|R_F|', b)
    return found, first

if __name__ == '__main__':
    for side in sys.argv[1:] or ('forward', 'backward'):
        screen(side)
