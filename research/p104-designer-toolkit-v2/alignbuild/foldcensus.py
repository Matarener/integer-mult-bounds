"""RULEMINE census.py: sites of the SHADOW-RELAY FOLD rule in a word (read-only).
Rule (R-FOLD): root group G (owned lifetimes joined by owned COPY / public relays) has chain frames c_0 > c_1 > ... (subspace order, time order).
A public helper H is a SHADOW RELAY of consecutive root frames (a,b) iff
  (i)  H reads root content (ADD H += owned lifetime of G) while at frame b (the root's lower frame, a root stay),
  (ii) after that read H's remaining frame chain is f_1 < ... < f_m (strictly increasing spans) with every f_i != b, f_m == a, and
       S(b) < S(f_i) < S(a) for i<m   (all nested inside the root's gap a->b),
  (iii) a, b consecutive stays of the root chain.
Then H's jump multiset == that of the root descending a -> f_{m-1} -> ... -> f_1 -> b, and the fold saves  staging(a->b) = tax of the shallow jump
(PROVED identity, IOROOT sec 1).  Ceiling (R0 units) = (d_a-d_b) ln-structure: cost = D ln D - jl-sum... computed as
  save = root_cost(shallow) + relay_cost - root_cost(deep)  with the chain-tax formula of fusecensus (owned: -jl; helper: D ln D - jl).
usage: census.py WORD  (prints one line per site, 'NONE' if none)."""
import sys, math, collections
import os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE]
import sigside as sigb
S = sigb.S
def jl(ds): return sum((abs(y - x)) * math.log(abs(y - x)) for x, y in zip(ds, ds[1:]) if y != x)
def sites(path):
    _, w = S.load_word(path); prog = w['program']; fr = w['frames']; n = len(w['initial']); dim = [len(b) for b in fr]
    sp = {}
    def span(f):
        if f not in sp:
            out = {0}
            for b in fr[f]: out |= {x ^ b for x in out}
            sp[f] = frozenset(out)
        return sp[f]
    L = sigb.lifetimes(w, prog); roots, relays = sigb.roots_of(w, prog, L); st = sigb.stays_pub(w, prog)
    lid = {}
    for k, G in enumerate(roots):
        for i in G: lid[i] = k
    # root chain per group: stays in time order, dedupe consecutive
    rchain = []
    for G in roots:
        ss = sorted((s[1], s[0]) for i in G for s in L[i]['stays'])
        c = []
        for _, f in ss:
            if not c or c[-1] != f: c.append(f)
        rchain.append(c)
    out = []
    # reads of root by public registers: (t, H, k, frame)
    for t, e in enumerate(prog):
        if e[0] != 'ADD' or e[1] >= n or e[2] < n: continue
        H = e[1]; fb = e[4]
        i = sigb.lid_at(L, e[2], t)
        if i is None: continue
        k = lid[i]; rc = rchain[k]
        if fb not in rc: continue
        j = rc.index(fb)
        if j == 0: continue
        a = rc[j - 1]                                  # root frame above b
        if not span(fb) < span(a): continue
        # H's later chain
        later = [f for f, ta, tb in st[H] if tb > t and ta >= t - 0]
        cur = [f for f, ta, tb in st[H] if ta <= t < tb]
        if not cur or cur[0] != fb: continue
        if not later: continue
        climb = later
        if climb[-1] != a: continue
        mid = climb[:-1]
        ok = all(span(fb) < span(f) < span(a) for f in mid) and all(span(climb[x]) < span(climb[x + 1]) for x in range(len(climb) - 1)) and span(fb) < span(climb[0])
        if not ok: continue
        full = [f for f, _, _ in st[H]]
        ds = [dim[f] for f in full]
        D = ds[-1] - ds[0]
        rel_cost = (D * math.log(D) if D > 0 else 0) - jl(ds)
        shallow = -jl([dim[a], dim[fb]]); deep = -jl([dim[x] for x in [a] + mid[::-1] + [fb]])
        save = rel_cost + shallow - deep
        out.append(dict(root=k, H=H, a=a, b=fb, mid=mid, chain=''.join(map(str, ds)), rel_cost=rel_cost, save=save, t=t))
    seen = set(); res = []
    for o in out:
        key = (o['H'], o['a'], o['b'])
        if key not in seen: seen.add(key); res.append(o)
    return res, rchain, dim
if __name__ == '__main__':
    res, rchain, dim = sites(sys.argv[1])
    for o in res:
        print('site root %d H%d gap %d(d%d)->%d(d%d) mid %s chain %s relay_tax %.2f ceiling %.2f' % (o['root'], o['H'], o['a'], dim[o['a']], o['b'], dim[o['b']], o['mid'], o['chain'], o['rel_cost'], o['save']))
    if not res: print('NONE')
