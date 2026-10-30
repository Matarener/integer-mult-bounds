"""JOINTFRAMES milestone pass: LATE BIRTH AT Y-MEETING FRAMES (exact word edit).

Principle (rank criterion, EXACT): a helper h born at frame g holds pure junk j_h until its first use; its junk column J_h (adjoint of h's initial
value to the Y finals) must be cancelled by pure-junk loads z += c h into registers co-present at g.  A Y main Y_j has the fixed adjoint e_j,
so if every Y_j in supp(J_h) sits at g (Y_j's chain passes g), the loads Y_j -= J_h[j] h at g cancel the junk exactly and h can be born at g.
Y chains must be nested; one Y stop at g serves every helper born at g whose junk reaches Y_j.  Helpers born at g exist from time 0, so all the
Y visits are done in one block right after the dim-0 junk-load block (Y only acts at F0 and Q_j in the route-B words).

Greedy: per helper saving = tax(chain) - tax(chain from first-use frame); Y cost = marginal tax of inserting g into Y_j's nested chain.
usage: python -B ylate.py IN OUT [--cap K] [--min-gain G]"""
import os
import sys, collections, math, gzip, json
TK = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
for p in (TK, TK + '/synth', __import__('os').path.dirname(__import__('os').path.abspath(__file__))):
    if p not in sys.path: sys.path.insert(0, p)
from fractions import Fraction as Q
import jsupp

Hf = lambda x: x * math.log(x) if x > 0 else 0.0
def tax(ds):
    ds = sorted(set(ds)); D = ds[-1] - ds[0]
    return Hf(D) - sum(Hf(b - a) for a, b in zip(ds, ds[1:])) if D > 0 else 0.0

def spans(w):
    out = []
    for b in w['frames']:
        s = {0}
        for v in b: s |= {x ^ v for x in s}
        out.append(frozenset(s))
    return out

def plan(path, cap=4, min_gain=0.0, verbose=True):
    w, dg, ops, first, J, dim = jsupp.junkcols(path)
    n = len(w['initial']); fr = spans(w)
    import dag as D
    role = D.role_fn(w); P = w['program']
    # word-level chains and first-use event index / frame per helper (program indices)
    chain = {r: [w['initial'][r]] for r in range(n)}
    fuse = {}
    for i, e in enumerate(P):
        if e[0] == 'MOVE':
            if e[1] < n: chain[e[1]].append(e[3])
        elif e[0] in ('ADD', 'COPY'):
            d, s, f = e[1], e[2], e[4]
            if dim[f] == 0 and d < n and role(d) == 'Y': continue     # junk load
            for r in (d, s):
                if r < n and role(r) == 'helper' and r not in fuse: fuse[r] = (i, f)
        elif e[0] == 'SCALE':
            r = e[1]
            if r < n and role(r) == 'helper' and r not in fuse: fuse[r] = (i, e[3])
    Qj = {r: w['final'][r] for r in range(n) if role(r) == 'Y'}
    cand = []
    for h, (i, g) in fuse.items():
        if dim[g] == 0: continue
        Jh = J.get(h, {})
        if not Jh or len(Jh) > cap: continue
        if any(role(y) != 'Y' for y in Jh): continue
        if not all(fr[g] <= fr[Qj[y]] for y in Jh): continue
        ch = [dim[f] for f in chain[h]]
        k = next(t for t, f in enumerate(chain[h]) if f == g)
        if any(dim[f] != 0 for f in chain[h][:1]) or any(not (fr[f] <= fr[g]) for f in chain[h][:k]): continue
        sav = tax(ch) - tax(ch[k:])
        if sav <= 0: continue
        cand.append((h, g, sav, Jh))
    # greedy Y chains (frame ids), nested
    ych = collections.defaultdict(list)   # y -> list of frames (sorted by dim)
    def ycost(c): return tax([0] + [dim[f] for f in c] + [8])
    def insert(c, g):
        if g in c: return c
        if any(dim[f] == dim[g] for f in c): return None
        nc = sorted(c + [g], key=lambda f: dim[f])
        for a, b in zip(nc, nc[1:]):
            if not fr[a] < fr[b]: return None
        return nc
    chosen = []; left = list(cand)
    while left:
        best = None
        for t, (h, g, sav, Jh) in enumerate(left):
            dc = 0.0; ok = True
            for y in Jh:
                nc = insert(ych[y], g)
                if nc is None: ok = False; break
                dc += ycost(nc) - ycost(ych[y])
            if not ok: continue
            gain = sav - dc
            if best is None or gain > best[0]: best = (gain, t)
        if best is None or best[0] <= min_gain: break
        gain, t = best; h, g, sav, Jh = left.pop(t)
        for y in Jh: ych[y] = insert(ych[y], g)
        chosen.append((h, g, sav, Jh, gain))
        # drop now-infeasible candidates lazily (re-tested each round)
    ytax = sum(ycost(c) for c in ych.values())
    if verbose:
        print('candidates', len(cand), 'chosen', len(chosen), 'helper saving %.1f' % sum(c[2] for c in chosen), 'Y tax %.1f' % ytax,
              'net model R0 %.1f' % (sum(c[2] for c in chosen) - ytax), 'Ys used', len(ych))
        print(' birth dims', sorted(collections.Counter(dim[c[1]] for c in chosen).items()))
    return w, chosen, {y: c for y, c in ych.items() if c}, dim, fr

def apply(w, chosen, ych, dim):
    n = len(w['initial']); P = w['program']
    import dag as D
    role = D.role_fn(w)
    late = {h: (g, Jh) for h, g, sav, Jh, gain in chosen}
    # 1. drop the dim-0 junk loads of late helpers; drop their MOVEs up to the birth frame
    out = []; moved = {}
    last0 = max(i for i, e in enumerate(P) if e[0] in ('ADD', 'COPY', 'SCALE') and dim[e[-1]] == 0)
    cur = {}
    block_at = None
    for i, e in enumerate(P):
        if e[0] == 'ADD' and e[2] in late and dim[e[4]] == 0:
            assert role(e[1]) == 'Y', e; continue
        if e[0] == 'MOVE' and e[1] in late and not moved.get(e[1]):
            g = late[e[1]][0]
            if e[3] == g: moved[e[1]] = True
            continue
        if e[0] == 'MOVE' and e[1] in ych:
            assert e[2] == w['initial'][e[1]] and dim[e[2]] == 0, e
            out.append(['MOVE', e[1], ych[e[1]][-1], e[3], e[4]]); continue
        out.append(e)
        if i == last0: block_at = len(out)
    assert all(moved.get(h) for h in late), [h for h in late if not moved.get(h)]
    # 2. Y block: visit the chain, load the junk of every late helper born at each frame
    byg = collections.defaultdict(list)
    for h, (g, Jh) in late.items():
        for y, c in Jh.items(): byg[(y, g)].append((h, c))
    blk = []
    for y, c in sorted(ych.items()):
        prev = w['initial'][y]
        for f in c:
            blk.append(['MOVE', y, prev, f, False]); prev = f
            for h, cc in sorted(byg[(y, f)]):
                blk.append(['ADD', y, h, str(-cc), f])
    w2 = dict(w); w2['program'] = out[:block_at] + blk + out[block_at:]
    ini = list(w['initial'])
    for h, (g, Jh) in late.items(): ini[h] = g
    w2['initial'] = ini
    return w2

def main(argv=None):
    import os
    a = sys.argv[1:] if argv is None else list(argv); cap = int(a[a.index('--cap') + 1]) if '--cap' in a else 4
    mg = float(a[a.index('--min-gain') + 1]) if '--min-gain' in a else 0.0
    w, chosen, ych, dim, fr = plan(a[0], cap=cap, min_gain=mg)
    w2 = apply(w, chosen, ych, dim)
    import kernel2net as KN, tkcommon
    print('R0 in', round(KN.r0(w)[1], 1), 'out', {k: round(v, 1) for k, v in KN.r0(w2)[0].items()}, round(KN.r0(w2)[1], 1), 'events', len(w['program']), '->', len(w2['program']))
    print('rendezvous violations', KN.check_rendezvous(w2))
    tkcommon.save_canonical(w2, a[1]); print('wrote', a[1])
if __name__ == '__main__': main()
