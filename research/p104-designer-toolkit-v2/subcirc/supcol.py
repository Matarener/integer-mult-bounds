"""supcol.py (SUBCIRC: PRINCIPLES psolve.py with architecture axes as flags: --kA, --endlow, --anybirth, --nojunk, --maxextra)
psolve.py WORD G [--out plan.pkl] [--enum K]: PRINCIPLE-ONLY solver for the market column over frame G (members = the H registers that visit G).
Every member event is stripped (pdata.py); the solver sees only geometry (frames, the cone of non-member registers over G, served-Y chains) and the
residual D. It knows FOUR things and nothing else (no pairing rule, no proxy rule, no birth rule, no matching, no frame list of the swarm's members):
  P1 cost  : a member costs tax(chain) = D ln D - sum r ln r over its chain dims; a Y stop costs its marginal tax on the Y's chain.
  P3 nest  : a chain has one frame per dim, frames ascending and NESTED; reads/deliveries only at a common frame; content-in-frame
             (a register at frame f holds only content of frames below f), so a member can deliver to Y only at a Y frame containing every frame it read at.
  P2 span  : (x) at a meeting frame where no member ends, the departures span exactly the arrivals' content; each Y's need is the sum of what its
             deliverers hand it (direct sum over read frames); (junk) a member born above F0 at frame phi is free only if the co-present junk sinks
             (0-born members, pre-loadable at F0; Y stops) have adjoint rank >= the generic rank of the newborns' adjoints (support = the Ys its group feeds).
  P4 geom  : candidate frames = the word's frames (cone over G, served-Y frames) and joins of read frames (new frames allowed).
Search: CP-SAT (1 worker) over group structures x birth options; objective = exact P1 tax. Prints the optimum, its degeneracy, the runner-up, and
compares with the swarm's column."""
import sys, os, math, itertools, argparse, pickle, collections
import numpy as np
sys.path[:0] = [os.path.dirname(os.path.abspath(__file__)), os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'alignbuild')]
import pdata
import rp
from rp import P
from life import rref, tax

SC = 10000
JUNK = 'outflow'

def rank_mod(vs):
    if not vs: return 0
    return len(rp.rref(np.array(vs, dtype=np.int64) % P)[1]) if hasattr(rp, 'rref') else np.linalg.matrix_rank(np.array(vs, dtype=float))

def mrank(vs):
    """exact rank mod P of a list of int64 vectors (Gaussian elimination)"""
    M = [list(map(int, v)) for v in vs]
    r = 0; ncol = len(M[0]) if M else 0
    for c in range(ncol):
        piv = next((i for i in range(r, len(M)) if M[i][c] % P), None)
        if piv is None: continue
        M[r], M[piv] = M[piv], M[r]; iv = pow(M[r][c], P - 2, P)
        M[r] = [x * iv % P for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] % P:
                f = M[i][c]; M[i] = [(a - f * b) % P for a, b in zip(M[i], M[r])]
        r += 1
        if r == len(M): break
    return r

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('word'); ap.add_argument('G', type=int); ap.add_argument('--out'); ap.add_argument('--enum', type=int, default=200)
    ap.add_argument('--maxextra', type=int, default=1); ap.add_argument('--junk', default='outflow'); ap.add_argument('--tmax', type=float, default=60)
    ap.add_argument('--kA', type=int, default=3); ap.add_argument('--endlow', action='store_true'); ap.add_argument('--anybirth', action='store_true'); ap.add_argument('--nojunk', action='store_true')
    a = ap.parse_args()
    global JUNK; JUNK = a.junk
    d = pdata.load(a.word, a.G)
    G = d['G']; dim = d['dim']; span = d['span']; served = d['served']; F0 = d['F0']
    inside = lambda big, small: rref(list(span[big]) + list(span[small])) == span[big]
    insp = lambda bigspan, small: rref(list(bigspan) + list(span[small])) == tuple(bigspan)
    # ---- delivery frames: frames of served Ys that contain G (P3: a member reaches G-cone content only inside them)
    yfr = {y: [(f, x, t0, t1) for f, x, t0, t1 in d['ych'][y] if x >= dim[G] and inside(f, G)] for y in served}
    # ---- read frames: cone frames contained in at least one delivery frame (content-in-frame + nesting prune; P3)
    cone = d['cone']
    allread = sorted(set(f for _, f, _, _ in cone))
    rf = [f for f in allread if any(inside(Q, f) and dim[Q] > dim[f] for y in served for Q, _, _, _ in yfr[y])]
    print('P3 prune: read frames %d -> %d (%s); delivery frames %s' % (len(allread), len(rf), rf, {y: [f for f, _, _, _ in v] for y, v in yfr.items()}))
    # ---- P2(x): decompose each Y's need over the read frames' row spaces (direct-sum check)
    w = d['w']; R = d['R']; M = d['M']
    nonM = np.ones(R, dtype=bool); nonM[M] = False
    snapt = collections.defaultdict(list)
    for r, f, t0, t1 in cone:
        if f in rf: snapt[t1].append(r)
    _, snaps = rp.replay(w, d['prog'], snap=snapt)
    rows = [(f, r, snaps[t1][r][nonM] % P) for r, f, t0, t1 in cone if f in rf]
    Aeq = np.array([v for _, _, v in rows]).T % P
    tot = mrank([v for _, _, v in rows]); per = {f: mrank([v for g, _, v in rows if g == f]) for f in rf}
    print('P2 direct sum over read frames: rank(all) %d vs sum of per-frame ranks %d %s' % (tot, sum(per.values()), per))
    u = {}
    for y in served:
        x = rp.solve(Aeq, d['D'][y][nonM] % P)
        if x is None: print('RESULT: Y', y, 'need not in the span of readable content (P2 fails)'); return
        for (f, r, v), c in zip(rows, x):
            if c: u[(y, f)] = (u.get((y, f), 0) + int(c) * v) % P
    u = {k: v for k, v in u.items() if v.any()}
    S = {y: sorted(f for (yy, f) in u if yy == y) for y in served}
    rfr = {f: mrank([u[(y, f)] for y in served if (y, f) in u]) for f in rf}
    print('needs: S_y =', S, '| readers needed per frame (rank of the Ys\' components):', rfr)
    # ---- enumerate groups: read-frame set A, meeting frame F = join(A), members (read frame or None, target Y)
    groups = []
    for kA in range(1, a.kA + 1):
        for A in itertools.combinations([f for f in rf if rfr[f] > 0], kA):
            Fs = rref([v for f in A for v in span[f]])
            if kA == 1: F = A[0]
            else:
                F = next((i for i, s in enumerate(span) if s == Fs), None)
                if F is None: F = ('new', Fs)
            dF = len(Fs)
            if dF > 8: continue
            Ys_ok = [y for y in served if any(rref(list(span[Q]) + list(Fs)) == span[Q] and dim[Q] >= dF for Q, _, _, _ in yfr[y])]
            # target vectors D_y|A (zero vector -> that Y is not a target of this group)
            vec = {y: sum((u.get((y, f), 0) for f in A), np.zeros(R, dtype=np.int64)[nonM]) % P for y in Ys_ok}
            Ys_ok = [y for y in Ys_ok if vec[y].any()]
            cdim = sum(rfr[f] for f in A)
            for m in range(cdim, cdim + 1 + a.maxextra):
                for K in itertools.combinations_with_replacement(Ys_ok, m):
                    if mrank([vec[y] for y in K]) != cdim: continue
                    # every Y whose need touches A must be served by this group? No: only the Ys in K get D_y|A; cover constraint is global.
                    # readers: assign rfr[f] readers per frame among the m members; extra members are non-readers that may pass one read frame
                    readers = [f for f in A for _ in range(rfr[f])]
                    groups.append(dict(A=A, F=F, dF=dF, K=K, readers=readers, m=m))
    print('groups enumerated:', len(groups))
    # ---- member options per group slot: (dims, born_frame, passes) ; route = birth, [G], [read frame], [F], Q, F9
    dG = dim[G]
    global A_ENDLOW, A_ANYB, CONEF
    A_ENDLOW = a.endlow; A_ANYB = a.anybirth
    CONEF = sorted(set((f, dim[f]) for _, f, _, _ in cone) | set((f, dim[f]) for y in served for f, x, _, _ in d['ych'][y] if 0 < x < 9))
    def insideF(big, small):
        sb = span[big] if not isinstance(big, tuple) else big[1]
        return rref(list(sb) + list(span[small])) == tuple(sb)
    def Qdim(y, F_):
        Fs = span[F_] if not isinstance(F_, tuple) else F_[1]
        cand = [x for Q, x, _, _ in yfr[y] if rref(list(span[Q]) + list(Fs)) == span[Q] and x > len(Fs)]
        if not cand and any(rref(list(span[Q]) + list(Fs)) == span[Q] and x == len(Fs) for Q, x, _, _ in yfr[y]): return len(Fs)   # deliver at F itself
        return min(cand) if cand else None
    def opts(g, slot):
        f = g['readers'][slot] if slot < len(g['readers']) else None
        y = g['K'][slot]; dq = Qdim(y, g['F'])
        if dq is None: return []
        dr = dim[f] if f is not None else None
        out = []
        passes = [] if f is None else [f]
        if f is None:   # a non-reader may pass one read frame of A (to sit with a newborn there) or none
            passes_opts = [[]] + [[ff] for ff in g['A'] if g['dF'] > dim[ff]]
        else: passes_opts = [passes]
        for ps in passes_opts:
            lo = [dim[p] for p in ps]
            mid = sorted(set(lo + ([g['dF']] if (not ps or g['dF'] > max(lo)) else []) + [dq]))
            body = sorted(set(mid + [9]))
            frames_seq = ps + ([g['F']] if (not ps or g['dF'] > max(lo)) else [])
            out.append(('Z', [0] + body, F0, tuple(frames_seq)))                       # 0-born, no G stop
            out.append(('P', [0, dG] + body, F0, (G,) + tuple(frames_seq)))           # 0-born with a G stop
            out.append(('N5', [dG] + body, G, (G,) + tuple(frames_seq)))              # born at G
            first = frames_seq[0]
            out.append(('Nb', body, first, tuple(frames_seq)))                       # born at its first frame (read frame or F)
            if A_ENDLOW:   # axis (a): end at the delivery dim (no F9 stop); x-cleanup NOT modelled (optimistic relaxation)
                for kind, dims, born, frs in list(out):
                    if dims[-1] == 9 and dims[-2] == dq and dq < 9: out.append((kind + 'L', dims[:-1], born, frs))
            if A_ANYB:     # axis (b): born at any cone frame strictly below the first frame and above G or F0 (nesting-checked by dim only)
                for (cf, cdim) in CONEF:
                    if cdim < dim[first] and cdim not in (0, dG) and insideF(first, cf):
                        out.append(('Na%d' % cf, sorted(set([cdim] + body)), cf, tuple(frames_seq)))
        return out
    from ortools.sat.python import cp_model
    mdl = cp_model.CpModel(); obj = []
    sg = [mdl.NewBoolVar('g%d' % i) for i in range(len(groups))]
    X = []   # (gi, slot, kind, dims, born, frames, var)
    for gi, g in enumerate(groups):
        for s in range(g['m']):
            os_ = opts(g, s)
            if not os_: mdl.Add(sg[gi] == 0); continue
            vs = []
            for kind, dims, born, frs in os_:
                v = mdl.NewBoolVar(''); vs.append(v); X.append((gi, s, kind, dims, born, frs, v))
                obj.append(int(round(tax(dims) * SC)) * v)
            mdl.Add(sum(vs) == sg[gi])
    # cover (P2 x): every (y, f in S_y) delivered exactly once
    for y in served:
        for f in S[y]:
            mdl.Add(sum(sg[gi] for gi, g in enumerate(groups) if f in g['A'] and y in g['K']) == 1)
        # a group feeding y with frames outside S_y only is excluded by construction (vec != 0)
    # junk (P2 junk-aware, generic-rank / Koenig form) at every frame where a birth can happen
    supp = lambda g: tuple(sorted(set(g['K'])))
    phis = set([G]) | set(born for _, _, kind, _, born, _, _ in X if kind.rstrip('L') not in ('Z', 'P'))
    # Y stops as sinks: marginal tax of inserting phi into a served Y's chain, if nestable and the dim is free
    ystop = {}
    for y in served:
        ch = [(f, x) for f, x, _, _ in d['ych'][y]]
        for phi in phis:
            ps = span[phi] if not isinstance(phi, tuple) else phi[1]; dp = len(ps)
            if not isinstance(phi, tuple) and any(f == phi for f, _ in ch):   # SUBCIRC: the Y already VISITS phi -> free sink (timing not modelled: optimistic)
                v = mdl.NewBoolVar(''); mdl.Add(v == 1); ystop[(y, phi)] = (v, 0.0); continue
            if any(x == dp for _, x in ch): continue
            lo = [f for f, x in ch if x < dp]; hi = [f for f, x in ch if x > dp]
            if not lo or not hi: continue
            if rref(list(ps) + list(span[lo[-1]])) != tuple(ps) or rref(list(span[hi[0]]) + list(ps)) != span[hi[0]]: continue
            mt = tax(sorted([x for _, x in ch] + [dp])) - tax([x for _, x in ch])
            v = mdl.NewBoolVar(''); ystop[(y, phi)] = (v, mt); obj.append(int(round(mt * SC)) * v)
    print('Y-stop sink options (nestable):', {k: round(v[1], 3) for k, v in ystop.items()})
    for phi in (phis if not a.nojunk else []):
        newb = [(gi, v) for gi, s, kind, dims, born, frs, v in X if (kind.rstrip('L') in ('N5', 'Nb') or kind.startswith('Na')) and born == phi]
        if not newb: continue
        sinks = [v for gi, s, kind, dims, born, frs, v in X if kind.rstrip('L') in ('Z', 'P') and phi in frs]
        if JUNK == 'outflow':   # P2 (junk, JR transposed): newborn columns must lie in ker(outflow map of ALL registers at phi) => #0-born at phi >= rank(outflow)
            newb = [(gi, v) for gi, s, kind, dims, born, frs, v in X if ((kind.rstrip('L') in ('N5', 'Nb') or kind.startswith('Na')) and born == phi) or (kind.rstrip('L') in ('Z', 'P') and phi in frs)]
        ys = [ystop[(y, phi)][0] for y in served if (y, phi) in ystop]
        if JUNK == 'span':   # P2 (junk, exact form): newborn columns of the invertible block at phi must lie in ker(Phi_phi) with an invertible newborn part
            # <=> the 0-born registers at phi (plus Y stops) carry the WHOLE outflow rank of phi. Generic rank = matching onto the Ys reached.
            nbv = [v for _, v in newb]; anyb = mdl.NewBoolVar(''); mdl.AddMaxEquality(anyb, nbv)
            present = [(gi, v) for gi, s, kind, dims, born, frs, v in X if ((kind.rstrip('L') in ('N5', 'Nb') or kind.startswith('Na')) and born == phi) or (kind.rstrip('L') in ('Z', 'P') and phi in frs)]
            zero = [(gi, v) for gi, s, kind, dims, born, frs, v in X if kind.rstrip('L') in ('Z', 'P') and phi in frs]
            asg = collections.defaultdict(list)
            for gi, v in zero:
                av = {y: mdl.NewBoolVar('') for y in supp(groups[gi])}
                mdl.Add(sum(av.values()) <= v)
                for y, b in av.items(): asg[y].append(b)
            for y in served:
                if (y, phi) in ystop: asg[y].append(ystop[(y, phi)][0])
                for gi, v in present:
                    if y in supp(groups[gi]): mdl.Add(sum(asg[y]) >= v + anyb - 1)
            continue
        T = {y: mdl.NewBoolVar('') for y in served}
        cs = []
        for gi, v in newb:
            c = mdl.NewBoolVar(''); cs.append(c)
            for y in supp(groups[gi]): mdl.Add(c >= v - T[y])
        mdl.Add(sum(T.values()) + sum(cs) <= sum(sinks) + sum(ys))
    mdl.Minimize(sum(obj))
    sol = cp_model.CpSolver(); sol.parameters.num_workers = 1; sol.parameters.max_time_in_seconds = a.tmax
    st = sol.Solve(mdl)
    print('status', sol.StatusName(st), 'optimum %.4f' % (sol.ObjectiveValue() / SC))
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE): return
    def decode():
        out = []
        for gi, g in enumerate(groups):
            if sol.Value(sg[gi]):
                mem = [(s, kind, dims, born, frs) for gi2, s, kind, dims, born, frs, v in X if gi2 == gi and sol.Value(v)]
                out.append((g, sorted(mem)))
        return out
    best = decode(); opt = sol.ObjectiveValue() / SC
    swarm = sorted(tuple(x for _, x in c) for c in d['swarm_chains'].values())
    mine = sorted(tuple(dims) for g, mem in best for _, _, dims, _, _ in mem)
    print('OPTIMUM structure:')
    for g, mem in best:
        print('  A', g['A'], 'F', g['F'] if not isinstance(g['F'], tuple) else 'NEW', 'dF', g['dF'], 'K', g['K'], '| members', [(k, dims) for _, k, dims, _, _ in mem])
    print('  Y stops used:', [(k, round(v[1], 3)) for k, v in ystop.items() if sol.Value(v[0])])
    print('optimum chain multiset', mine, 'tax %.4f' % sum(tax(c) for c in mine))
    print('swarm   chain multiset', swarm, 'tax %.4f' % sum(tax(c) for c in swarm))
    print('MATCH chain multiset:', mine == swarm, '| delta tax (opt - swarm) %+.4f' % (sum(tax(c) for c in mine) - sum(tax(c) for c in swarm)))
    # ---- degeneracy: count distinct optimal group structures, then the runner-up
    sigs = set(); plans = []
    for it in range(a.enum):
        sig = tuple(sorted((g['A'], g['K'], tuple(k for _, k, _, _, _ in mem)) for g, mem in decode()))
        if sig not in sigs: sigs.add(sig); plans.append(decode())
        # forbid this exact group selection + kinds
        lits = [sg[gi] for gi in range(len(groups)) if sol.Value(sg[gi])] + [v for *_, v in X if sol.Value(v)]
        mdl.AddBoolOr([l.Not() for l in lits])
        st = sol.Solve(mdl)
        if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE): print('exhausted after', it + 1); break
        val = sol.ObjectiveValue() / SC
        if val > opt + 1e-6:
            print('optimal structures (group sets x birth kinds): %d; RUNNER-UP %.4f (+%.4f):' % (len(sigs), val, val - opt))
            for g, mem in decode(): print('  A', g['A'], 'F', g['F'] if not isinstance(g['F'], tuple) else 'NEW', 'K', g['K'], [(k, dims) for _, k, dims, _, _ in mem])
            break
    if a.out:
        pickle.dump(dict(plans=plans, opt=opt, u={k: v for k, v in u.items()}, rows=[(f, r) for f, r, _ in rows], S=S), open(a.out, 'wb'))
        print('wrote', a.out, len(plans), 'optimal plans')

if __name__ == '__main__': main()
