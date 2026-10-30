"""Lift a dims-level solution (levels per op) to subspace frames.
Nodes (R, seg, level) merged by ops; chain order within each (R, seg)."""
import sys, json, os
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
from poset import *

class UF:
    def __init__(s): s.p = {}
    def f(s, x):
        s.p.setdefault(x, x)
        while s.p[x] != x:
            s.p[x] = s.p[s.p[x]]; x = s.p[x]
        return x
    def u(s, a, b):
        a, b = s.f(a), s.f(b)
        if a != b: s.p[a] = b

def segments(p, groups):
    seg = defaultdict(dict); nseg = {}
    for r, gl in groups.items():
        if r[0] != 'L': continue
        sg = 0
        for t, ops in gl:
            if p[ops[0]][0] == 'warp':
                for j in ops: seg[j][r[1]] = ('W', sg)
                sg += 1; continue
            for j in ops: seg[j][r[1]] = sg
        nseg[r[1]] = sg
    return seg, nseg

def setup(w, side, levels):
    c = w['canonical']; fr = c['frames']
    p, groups = build(w, side)
    lows, lowd, ups, upd, pinned = bounds(w, p, groups, relax_warps=False)
    seg, nseg = segments(p, groups)
    uf = UF(); fixed = {}; lo = defaultdict(list); hi = defaultdict(list)
    lev = {}
    for r in range(632):
        uf.f((r, 0, len(fr[c['start'][r]])))
        fixed[(r, 0, len(fr[c['start'][r]]))] = tuple(fr[c['start'][r]])
        k = nseg.get(r, 0); fixed[(r, k, len(fr[c['final'][r]]))] = tuple(fr[c['final'][r]]); uf.f((r, k, len(fr[c['final'][r]])))
    for i, e in enumerate(p):
        if e[0] == 'center': continue
        l = levels[i]
        if e[0] == 'warp':
            R = e[1][1]; k = seg[i][R][1]
            assert len(fr[e[3]]) == l
            fixed[(R, k, l)] = tuple(fr[e[3]]); fixed[(R, k+1, l)] = tuple(fr[e[4]]); uf.f((R, k, l)); uf.f((R, k+1, l))
            continue
        nodes = [(R, seg[i][R], l) for R in seg[i]]
        for a in nodes[1:]: uf.u(nodes[0], a)
        if not nodes: continue
        lo[nodes[0]].append(lows[i]); hi[nodes[0]].append(ups[i])
        if i in pinned: fixed[nodes[0]] = pinned[i]
    return p, groups, uf, fixed, lo, hi, nseg

def lift(w, side, levels):
    p, groups, uf, fixed, lo, hi, nseg = setup(w, side, levels)
    comp = defaultdict(set)
    for x in list(uf.p): comp[uf.f(x)].add(x)
    L = defaultdict(list); H = defaultdict(list); F = {}
    for x, b in lo.items(): L[uf.f(x)] += b
    for x, b in hi.items(): H[uf.f(x)] += b
    clashes = []
    for x, b in fixed.items():
        k = uf.f(x)
        if k in F and span(F[k]) != span(b): clashes.append(('fixed clash', x)); continue
        F[k] = b
    # chain neighbours
    chains = defaultdict(set)
    for (r, k, l) in uf.p: chains[r, k].add(l)
    below = defaultdict(set); above = defaultdict(set)
    for (r, k), ls in chains.items():
        ls = sorted(ls)
        for a, b in zip(ls, ls[1:]):
            A, B = uf.f((r, k, a)), uf.f((r, k, b)); below[B].add(A); above[A].add(B)
    lvl = {k: next(iter(v))[2] for k, v in comp.items()}
    assert all(all(x[2] == lvl[k] for x in v) for k, v in comp.items())
    order = sorted(comp, key=lambda k: lvl[k])
    X = {}; fails = list(clashes)
    # static upper bound per component: meet of his, fixed, and fixed uppers above (transitively later)
    for k in order:
        need = join(*(L[k]), *(X[b] for b in below[k] if b in X), *( [F[k]] if k in F else []))
        up = tuple(1 << i for i in range(9))
        for b in H[k]: up = meet(up, b)
        if not span(need) <= span(up) or len(need) > lvl[k]:
            fails.append((k, lvl[k], len(need), len(up))); X[k] = need; continue
        if len(need) < lvl[k]:
            if k in F: fails.append((k, 'fixed dim')); X[k] = need; continue
            # extend preferring vectors needed by components above
            cand = []
            for a in above[k]:
                for b in L[a]: cand += list(b)
                if a in F: cand += list(F[a])
            cur = list(need); su = span(up)
            for v in cand + list(up):
                if len(cur) >= lvl[k]: break
                if v in su and len(join(cur, [v])) > len(cur): cur = list(join(cur, [v]))
            need = tuple(cur)
            if len(need) < lvl[k]: fails.append((k, 'cannot extend')); 
        X[k] = need
    return X, fails, comp, lvl

if __name__ == '__main__':
    side = sys.argv[1]; sol = json.load(open(sys.argv[2]))
    levels = {int(k): v for k, v in sol['levels'].items()}
    w = load(); X, fails, comp, lvl = lift(w, side, levels)
    print('components', len(comp), 'fails', len(fails))
    for f in fails[:20]: print(f)
