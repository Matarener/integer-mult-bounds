"""Frame retime of a fixed P104 circuit (PR5907 schema: 29 owned fields with several lifetimes), after the CrocSwap
designer toolkit's dims_relax.py / lattice_retime.py (research/p104-designer-toolkit), re-implemented for this schema.

Fixed: event order and operands.  Free: the subspace of F2^9 at every ADD/COPY-equal-frame cluster (a cluster is a set of
(register, lifetime, stop) linked by common-chart ADD/COPY).  Pinned: literal ports (X initial) and output hyperplanes (Y final).
Chains: public stops strictly ascending, owned strictly descending; with --stopfree a stop may equal its predecessor
(its MOVE is then deleted).  Objective: linearised kappa from exact marginal tables (x18 forward calls).

  python3 retime.py WORD.json.gz dims    [--tl S] [--stopfree]           ceiling of the dimension relaxation
  python3 retime.py WORD.json.gz lattice [--tl S] [--stopfree] --out W   exact-lattice solve, realised word re-priced exactly
Prepared for Matarener with Claude (Anthropic), via Claude Code.  Apache-2.0.
"""
import collections, gzip, json, os, sys, time
from ortools.sat.python import cp_model
import p104

ARG = lambda k, d: sys.argv[sys.argv.index(k)+1] if k in sys.argv else d
STOPFREE = '--stopfree' in sys.argv
MAXQ = int(ARG('--maxq', 5))


def build(w):
    n, m = w['public'], w['owned_fields']
    parent = {}
    def find(x):
        while parent.setdefault(x, x) != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    life = collections.defaultdict(int); stop = collections.defaultdict(int)
    chain = {}
    for r in range(n):
        chain[(r, 0)] = [((r, 0, 0), w['initial'][r])]
    for e in w['program']:
        op, r = e[0], e[1]
        if op == 'INIT':
            life[r] += 1; stop[r] = 0; chain[(r, life[r])] = [((r, life[r], 0), e[2])]
        elif op == 'MOVE':
            stop[r] += 1; chain[(r, life[r])].append(((r, life[r], stop[r]), e[3]))
        elif op in ('ADD', 'COPY'):
            s = e[2]
            parent[find((r, life[r], stop[r]))] = find((s, life[s], stop[s]))
        else:
            find((r, life[r], stop[r]))
    cf = {}
    for key, ch in chain.items():
        for node, f in ch:
            c = find(node)
            if c in cf and cf[c] != f:
                raise ValueError('cluster with two frames')
            cf[c] = f
    links = []
    for key, ch in chain.items():
        for (n1, f1), (n2, f2) in zip(ch, ch[1:]):
            links.append((find(n1), find(n2), key[0]))
    return dict(chain=chain, cf=cf, links=links, find=find)


def tables(w):
    """Exact-linear weights: at the base crossing k0, margin = sum_T d^(1-k0) - sum_P d^(1-k0) is linear in the counts and
    a change raises kappa iff it raises the margin.  Weights are 18 * d^(1-k0) (18 forward calls), scaled by 1e9."""
    paid, helpers, _ = p104.replay(w)
    P, T = p104.invoice(paid, helpers)
    k0 = p104.kappa(P, T)[0]
    t = 1-float(k0)
    wt = {d: round(1e9*18*d**t) for d in range(1, 10)}
    import math
    slope = sum(n*r**t*math.log(r) for r, n in P.items())-sum(n*r**t*math.log(r) for r, n in T.items())
    global TO_KAPPA
    TO_KAPPA = 1/(1e9*(-slope)) if slope < 0 else 1/(1e9*slope)
    return wt, wt, k0


def span_of(basis):
    s = {0}
    for v in basis:
        if v not in s:
            s |= {x ^ v for x in s}
    return s


def basis_of(s):
    b, sp = [], {0}
    for v in sorted(s):
        if v not in sp:
            b.append(v); sp |= {x ^ v for x in sp}
    return b


def subspaces_between(L, U):
    comp, sp = [], set(L)
    for v in sorted(U):
        if v not in sp:
            comp.append(v); sp |= {x ^ v for x in sp}
    k = len(comp)
    seen = {frozenset([0])}; frontier = [frozenset([0])]; allsub = [frozenset([0])]
    while frontier:
        nf = []
        for S in frontier:
            for v in range(1, 1 << k):
                if v in S: continue
                T = frozenset(S | {x ^ v for x in S})
                if T not in seen:
                    seen.add(T); nf.append(T); allsub.append(T)
        frontier = nf
    out = []
    for S in allsub:
        full = set(L)
        for v in S:
            lv = 0
            for i in range(k):
                if v >> i & 1: lv ^= comp[i]
            full |= {x ^ lv for x in L}
        out.append(frozenset(full))
    return out


def main():
    path, mode = sys.argv[1], sys.argv[2]
    TL = float(ARG('--tl', 300))
    w = p104.read(path)
    n = w['public']; live = set(w['live']); mainr = live | {r+112 for r in live}
    B = build(w); cf, links, find = B['cf'], B['links'], B['find']
    fr = p104.spans(w); dimf = lambda f: len(w['frames'][f])
    cwP, cwT, k0 = tables(w)
    print('tables cwP', cwP, 'cwT', cwT, 'clusters', len(cf), 'links', len(links), flush=True)
    A = set()
    for r in live:
        A.add(find((r, 0, 0)))
    last = {key: ch[-1][0] for key, ch in B['chain'].items()}
    for r in live:
        A.add(find(last[(r+112, 0)]))
    up = collections.defaultdict(list); dn = collections.defaultdict(list)
    for a, b, r in links:
        lo, hi = (a, b) if r < n else (b, a)
        up[lo].append(hi); dn[hi].append(lo)
    def reach(adj, s):
        seen = {s}; st = [s]
        while st:
            x = st.pop()
            for y in adj[x]:
                if y not in seen:
                    seen.add(y); st.append(y)
        return seen
    Ls = collections.defaultdict(list); Us = collections.defaultdict(list)
    for a in A:
        for c in reach(up, a): Ls[c].append(a)
        for c in reach(dn, a): Us[c].append(a)
    M = cp_model.CpModel()
    helpers = [r for r in range(n) if r not in mainr]
    if mode == 'dims':
        D = {}
        for c in cf:
            if c in A:
                lo = hi = dimf(cf[c])
            else:
                L = span_of([v for a in Ls[c] for v in w['frames'][cf[a]]])
                U = None
                for a in Us[c]:
                    s = set(fr[cf[a]]); U = s if U is None else U & s
                lo = len(L).bit_length()-1; hi = (len(U).bit_length()-1) if U is not None else 9
            D[c] = M.NewIntVar(lo, hi, '')
        getD = lambda c: D[c]
    else:
        dom, x, D = {}, {}, {}
        for c in cf:
            nat = frozenset(fr[cf[c]])
            if c in A:
                dom[c] = [nat]
            else:
                L = span_of([v for a in Ls[c] for v in w['frames'][cf[a]]])
                U = None
                for a in Us[c]:
                    s = set(fr[cf[a]]); U = s if U is None else U & s
                if U is None: U = set(range(512))
                Lb, Ub = basis_of(L), basis_of(U)
                if len(Ub)-len(Lb) <= MAXQ:
                    d = set(subspaces_between(Lb, Ub))
                else:
                    d = {frozenset(L), frozenset(U)} | {f for f in fr if L <= f <= U}
                d.add(nat); dom[c] = sorted(d, key=lambda s: (len(s), sorted(s)[:8]))
            xs = []
            for i, S in enumerate(dom[c]):
                x[c, i] = M.NewBoolVar(''); xs.append(x[c, i])
            M.AddExactlyOne(xs)
            dims = [len(S).bit_length()-1 for S in dom[c]]
            D[c] = M.NewIntVar(min(dims), max(dims), '')
            M.Add(D[c] == sum(dm*x[c, i] for i, dm in enumerate(dims)))
        for a, b, r in links:
            lo, hi = (a, b) if r < n else (b, a)
            for i, S in enumerate(dom[lo]):
                ok = [x[hi, j] for j, T in enumerate(dom[hi]) if (S <= T if STOPFREE else S < T)]
                M.AddBoolOr(ok+[x[lo, i].Not()])
            for j, T in enumerate(dom[hi]):
                ok = [x[lo, i] for i, S in enumerate(dom[lo]) if (S <= T if STOPFREE else S < T)]
                M.AddBoolOr(ok+[x[hi, j].Not()])
        print('domains total', sum(len(d) for d in dom.values()), 'max', max(len(d) for d in dom.values()), flush=True)
    tab = ([0] if STOPFREE else [])+[cwP[d] for d in range(1, 10)]
    tabT = [cwT[d] for d in range(1, 10)]
    obj = []
    off = 0 if STOPFREE else 1
    for a, b, r in links:
        lo, hi = (a, b) if r < n else (b, a)
        M.Add(D[hi] >= D[lo]+off)
        dl = M.NewIntVar(off, 9, ''); M.Add(dl == D[hi]-D[lo])
        cst = M.NewIntVar(0, max(tab), ''); M.AddElement(dl-off, tab, cst); obj.append(-cst)
    for r in helpers:
        a, b = find((r, 0, 0)), find(last[(r, 0)])
        rk = M.NewIntVar(1, 9, ''); M.Add(rk == D[b]-D[a])
        g = M.NewIntVar(0, max(tabT), ''); M.AddElement(rk-1, tabT, g); obj.append(g)
    M.Maximize(sum(obj))
    nat = 0
    for a, b, r in links:
        lo, hi = (a, b) if r < n else (b, a); nat -= cwP[dimf(cf[hi])-dimf(cf[lo])]
    for r in helpers:
        nat += cwT[dimf(cf[find(last[(r, 0)])])-dimf(cf[find((r, 0, 0))])]
    for c in cf:
        M.AddHint(D[c], dimf(cf[c]))
    S = cp_model.CpSolver(); S.parameters.max_time_in_seconds = TL
    S.parameters.num_workers = int(os.environ.get('THREADS', '4'))
    st = S.Solve(M)
    print(mode, 'stopfree' if STOPFREE else 'strict', S.StatusName(st), 'margin ceiling %.0f found %.0f (x1e-9)  ~dkappa ceiling %.3e found %.3e' %
          (S.BestObjectiveBound()-nat, S.ObjectiveValue()-nat, (S.BestObjectiveBound()-nat)*TO_KAPPA, (S.ObjectiveValue()-nat)*TO_KAPPA if st in (cp_model.OPTIMAL, cp_model.FEASIBLE) else float('nan')), flush=True)
    if mode != 'lattice' or st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return
    chosen = {c: next(dom[c][i] for i in range(len(dom[c])) if S.BooleanValue(x[c, i])) for c in cf}
    changed = sum(1 for c in cf if chosen[c] != frozenset(fr[cf[c]]))
    w2 = json.loads(json.dumps(w)); ftab = {}
    for i in range(len(w['frames'])):
        ftab.setdefault(frozenset(fr[i]), i)
    def fid(Sx):
        if Sx not in ftab:
            w2['frames'].append(basis_of(Sx)); ftab[Sx] = len(w2['frames'])-1
        return ftab[Sx]
    life = collections.defaultdict(int); stop = collections.defaultdict(int); newp = []
    for e in w['program']:
        e = list(e); op, r = e[0], e[1]
        if op == 'MOVE':
            a = find((r, life[r], stop[r])); stop[r] += 1; b = find((r, life[r], stop[r]))
            e[2] = fid(chosen[a]); e[3] = fid(chosen[b])
            if chosen[a] == chosen[b]:
                continue
        elif op == 'INIT':
            life[r] += 1; stop[r] = 0; e[2] = fid(chosen[find((r, life[r], 0))])
        elif op == 'CLEAR':
            e[2] = fid(chosen[find((r, life[r], stop[r]))])
        else:
            e[-1] = fid(chosen[find((r, life[r], stop[r]))])
        newp.append(e)
    w2['program'] = newp
    w2['initial'] = [fid(chosen[find((r, 0, 0))]) for r in range(n)]
    w2['final'] = [fid(chosen[find(last[(r, 0)])]) for r in range(n)]
    print('clusters changed', changed, 'frames', len(w['frames']), '->', len(w2['frames']), 'events', len(newp), flush=True)
    try:
        info = p104.price(w2)
        print('REALISED', json.dumps({k: str(v) for k, v in info.items()}), 'gain %.3e' % float(info['kappa_lo']-k0), flush=True)
    except p104.Illegal as ex:
        print('REALISED ILLEGAL', ex, flush=True)
    out = ARG('--out', None)
    if out:
        with gzip.open(out, 'wt') as f:
            json.dump(w2, f)


if __name__ == '__main__':
    main()
