"""Subspace domains for every op (fixed warps, pinned C ops), pruned to fixpoint by
forced-frame chain compatibility on every register segment."""
import sys, time
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
sys.path.insert(0, str(__import__('pathlib').Path.home()/'imb-r13/research/scalar-reorder-20261022'))
from lift import *
from intervals import complete_interval

class Frames:
    def __init__(s, fr):
        s.spans = [span(b) for b in fr]; s.dims = [len(b) for b in fr]; s.fb = [list(b) for b in fr]
        s.labels = {x: i for i, x in enumerate(s.spans)}
    def lab(s, b):
        x = span(b)
        if x not in s.labels:
            s.labels[x] = len(s.spans); s.spans.append(x); s.dims.append(len(b)); s.fb.append(list(join(b)))
        return s.labels[x]
    def le(s, a, b): return s.dims[a] <= s.dims[b] and s.spans[a] <= s.spans[b]
    def comp(s, a, b): return s.le(a, b) or s.le(b, a)

def domains(w, side, max_gap=6, relax_warps=False):
    c = w['canonical']; fr = c['frames']
    p, groups = build(w, side)
    lows, lowd, ups, upd, pinned = bounds(w, p, groups, relax_warps=relax_warps)
    seg, nseg = segments(p, groups)
    Fm = Frames(fr); st = {}; cache = {}; dom = {}
    for i, e in enumerate(p):
        if e[0] in ('center', 'warp'): continue
        if i in pinned:
            dom[i] = {Fm.lab(pinned[i])}; continue
        key = (lows[i], ups[i])
        if key not in cache:
            a = Fm.lab(lows[i]); b = Fm.lab(ups[i])
            cache[key] = complete_interval(Fm.spans, Fm.dims, Fm.fb, (a,), (b,), st, max_gap=max_gap)
        dom[i] = set(cache[key])
    # register-segment membership
    members = defaultdict(list)
    for i in dom:
        for R, k in seg[i].items():
            if isinstance(k, int): members[R, k].append(i)
    ends = defaultdict(set)
    for R in range(632):
        ends[R, 0].add(c['start'][R]); ends[R, nseg.get(R, 0)].add(c['final'][R])
    for i, e in enumerate(p):
        if e[0] == 'warp' and not relax_warps:
            R = e[1][1]; k = seg[i][R][1]; ends[R, k].add(e[3]); ends[R, k+1].add(e[4])
    changed = True; rounds = 0
    while changed:
        changed = False; rounds += 1
        forced = defaultdict(set)
        for key in members:
            forced[key] |= ends[key]
            for i in members[key]:
                if len(dom[i]) == 1: forced[key] |= dom[i]
        for i, D in dom.items():
            if len(D) == 1: continue
            keys = [(R, k) for R, k in seg[i].items() if isinstance(k, int)]
            nd = {X for X in D if all(Fm.comp(X, Y) for key in keys for Y in forced[key])}
            # must lie between segment start and end
            if nd != D:
                assert nd, ('empty', i)
                dom[i] = nd; changed = True
    return dict(p=p, groups=groups, dom=dom, seg=seg, nseg=nseg, members=members, ends=ends, Fm=Fm, lows=lows, ups=ups, stats=st, rounds=rounds)

if __name__ == '__main__':
    t = time.time(); w = load(); S = domains(w, sys.argv[1] if len(sys.argv) > 1 else 'forward')
    dom = S['dom']; Fm = S['Fm']
    print('t', time.time()-t, 'rounds', S['rounds'], S['stats'])
    print('free ops', sum(len(v) > 1 for v in dom.values()), 'total dom', sum(len(v) for v in dom.values()))
    cand = {key: set().union(*(dom[i] for i in m)) | S['ends'][key] for key, m in S['members'].items()}
    arcs = sum(1 for v in cand.values() for a in v for b in v if Fm.dims[a] < Fm.dims[b] and Fm.spans[a] < Fm.spans[b])
    print('max cand', max(map(len, cand.values())), 'sum cand', sum(map(len, cand.values())), 'arcs', arcs)
