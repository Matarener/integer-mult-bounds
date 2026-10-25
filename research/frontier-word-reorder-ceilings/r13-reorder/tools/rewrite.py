"""Stage 3 probe: one-step non-commuting swaps with exact correction ADDs at thin helper visits.
Swap x=(A+=cB) with its adjacent conflicting neighbour q (first conflicting op after / last before):
  next q=(B+=dE): q; x; A+=-cd E          next q=(D+=eA): q; D+=ec B; x
  prev q=(B+=dE): x; q; A+=cd E           prev q=(D+=eA): x; q; D+=-ec B
Each candidate program is re-optimised by construct.py (medium domains) and replay-checked if better."""
import sys, json, time, os
from fractions import Fraction as Q
from copy import deepcopy
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
from load import *
from poset import reg_types

def conflict(e1, e2):
    t1 = dict(); t2 = dict()
    for r, t in reg_types(e1): t1[r] = t
    for r, t in reg_types(e2): t2[r] = t
    for r in set(t1) & set(t2):
        if not (t1[r] == t2[r] and t1[r] in 'TS'): return True
    return False

def add(a, b, q, frame):
    q = Q(q); return ['scalar', ['add', ['L', a], ['L', b], q.numerator, q.denominator], frame]

def is_LL_add(e):
    return e[0] == 'scalar' and e[1][0] == 'add' and e[1][1][0] == 'L' and e[1][2][0] == 'L'

def swap(prog, k, direction):
    """prog: event list incl. climbs (climbs ignored/dropped). Returns new list or None."""
    ev = [e for e in prog if e[0] != 'climb']
    # map index k (in ev)
    x = ev[k]; assert is_LL_add(x)
    A, B = x[1][1][1], x[1][2][1]; c = Q(x[1][3], x[1][4])
    rng = range(k+1, len(ev)) if direction == 'next' else range(k-1, -1, -1)
    for j in rng:
        if ev[j][0] in ('phase', 'adapter', 'residual_adapter'): continue
        if conflict(x, ev[j]): break
    else: return None
    q = ev[j]
    if not is_LL_add(q): return None
    D, E = q[1][1][1], q[1][2][1]; d = Q(q[1][3], q[1][4])
    f0 = x[2]
    if D == B and E != A:        # q writes x's source
        corr = add(A, E, (-c*d if direction == 'next' else c*d), f0)
    elif E == A and D != B:      # q reads x's target
        corr = add(D, B, (c*d if direction == 'next' else -c*d), f0)
    else: return None
    new = ev[:]
    if direction == 'next':
        # remove x, insert after q: q; [corr]; x  (order matters only for the reads-target case)
        del new[k]; jj = j-1
        ins = [corr, x] if E == A else [x, corr]
        new[jj+1:jj+1] = ins
    else:
        del new[k]
        new[j:j] = [x]  # x before q
        new[j+2:j+2] = [corr]
    return new, (k, j, direction, x[1], q[1], corr[1])

def thin_sites(w, side):
    c = w['canonical']; prog = w['programs'][side]
    ev = [e for e in prog if e[0] != 'climb']
    visits = defaultdict(list)
    for k, e in enumerate(ev):
        if e[0] == 'scalar':
            for r in roles(e):
                if e[2] not in (c['start'][r], c['final'][r]): visits[r, e[2]].append(k)
    return [(r, f, ks[0]) for (r, f), ks in visits.items() if len(ks) <= int(__import__('os').environ.get('MAXK', 1)) and r >= int(__import__('os').environ.get('RMIN', 224)) and is_LL_add(ev[ks[0]])]

ROOTP = __import__('pathlib').Path.home()/'imb-r13'
sys.path.insert(0, str(ROOTP/'research/warp-interface-20261022'))
from warp_merge import synthesize

def cost_of(c, ev, C=0.00302):
    try: out = synthesize(c, ev)
    except ValueError: return None, None
    prof = Counter(e[5] for e in out if e[0] == 'climb')
    return sum(n*r**(1-C) for r, n in prof.items()), prof

SPANS = {}
def local_cost(c, ev, regs, C=0.00302):
    """Chain cost restricted to registers regs; None if any chain is not nested (warps reset)."""
    if not SPANS:
        for i, b in enumerate(c['frames']): SPANS[i] = span(b)
    tot = 0.0
    for r in regs:
        cur = c['start'][r]
        seq = []
        for e in ev:
            if e[0] == 'scalar' and r in roles(e): seq.append(('s', e[2]))
            elif e[0] == 'warp' and e[1][1] == r: seq.append(('w', e[3], e[4]))
        seq.append(('s', c['final'][r]))
        for t in seq:
            new = t[1]
            if new != cur:
                if not SPANS[cur] < SPANS[new]: return None
                tot += (len(c['frames'][new]) - len(c['frames'][cur]))**(1-C)
            cur = t[2] if t[0] == 'w' else new
    return tot

def screen(w, side, site, direction):
    c = w['canonical']; prog = w['programs'][side]
    r, f, k = site
    res = swap(prog, k, direction)
    if res is None: return []
    new, info = res
    visits = defaultdict(set)
    for e in new:
        if e[0] == 'scalar':
            for rr in roles(e): visits[rr].add(e[2])
    # locate x and corr in new
    xi = [i for i, e in enumerate(new) if e is not None and e[0] == 'scalar' and e[1] == info[3]]
    ci = [i for i, e in enumerate(new) if e[0] == 'scalar' and e[1] == info[5]]
    if len(ci) != 1: return []
    ci = ci[0]
    A = info[3][1][1]; B = info[3][2][1]
    others = visits[A] - {f}
    out = []
    xs = [i for i in xi]
    corr_regs = (info[5][1][1], info[5][2][1])
    copt = (visits[corr_regs[0]] & visits[corr_regs[1]]) | {0, 1}
    regs = {A, B, *corr_regs}
    ev0 = [e for e in prog if e[0] != 'climb']
    base = local_cost(c, ev0, regs)
    for xf in sorted(others | {f}):
        for cf in sorted(copt):
            ev = [e[:] for e in new]
            for i in xs: ev[i] = [ev[i][0], ev[i][1], xf]
            ev[ci] = [ev[ci][0], ev[ci][1], cf]
            cst = local_cost(c, ev, regs)
            if cst is not None and cst < base - 1e-9:
                full, prof = cost_of(c, ev)
                if full is not None: out.append((full, xf, cf, prof))
    return out, info

if __name__ == '__main__':
    side = sys.argv[1]; part, nparts = int(sys.argv[2]), int(sys.argv[3])
    w = load(); c = w['canonical']
    base, bprof = cost_of(c, [e for e in w['programs'][side] if e[0] != 'climb'])
    print('base', base, dict(bprof), flush=True)
    sites = thin_sites(w, side)[part::nparts]; best = []
    t = time.time()
    for n, s in enumerate(sites):
        for d in ('next', 'prev'):
            r = screen(w, side, s, d)
            if not r: continue
            res, info = r
            for cst, xf, cf, prof in res:
                if cst < base - 1e-9:
                    print('GAIN', base-cst, s, d, xf, cf, dict(prof), info, flush=True)
        if n % 20 == 0: print('progress', n, len(sites), time.time()-t, flush=True)
