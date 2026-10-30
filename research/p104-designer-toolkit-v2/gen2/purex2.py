"""PUREX joint junk solve for end-early (DAG level, exact Fractions).  usage: python -B purex2.py IN OUT [--max N] [--dims 8] [--xstops] [--skip H,..] [--lawprune] [--dyfix]
Enders from purex.Ctx.census.  Program = Z (dim-0 block) + body(with cleanups) + F9(minus ender ops) + fixes.
Z = I + Delta on rows U (Ys, enders, F9 registers whose finals carry ender/Y symbols or a wrong own coefficient), solved JOINTLY:
  final[r] = F0[r] + sum_s A[r,s] Delta_s   (A[r,s] = coefficient of dim-0 symbol s in F0[r], F0 = finals with Z = I)
  rows E u Y: all dim-0 coordinates exact;  F9 rows in U: bad coordinates (E u Y symbols) zero and own coefficient 1.
Z is then realised as dim-0 ADDs with NON-pure sources (sequential, each row solved against the current values), dyadic only.
F9 rows' remaining residue (x and F9-helper symbols) is cancelled at the end of F9 from clean registers.  No env at import."""
import sys, os, gzip, json, collections, time
from fractions import Fraction as Q
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import purex as PX

class PurexFail(SystemExit):
    """GENUPGRADE: a SystemExit (same message, rc 1 when uncaught: default behaviour unchanged) carrying the lemma class and the culprit sets for --lawprune"""
    def __init__(self, msg, cls='other', **info): SystemExit.__init__(self, msg); self.cls = cls; self.info = info

class Inconsistent(ValueError):
    def __init__(self, msg, r, cols): ValueError.__init__(self, msg); self.r = r; self.cols = cols
from purex import addf, replay, dy

def gauss_solve(rows, rhs, prefer=()):
    """rectangular exact solve: rows {r: {unknown: a}}, rhs {r: {col: v}}; Gauss-Jordan, pivots prefer unknowns in `prefer`, free unknowns = 0.
    returns X {unknown: {col: v}}; raises ValueError on inconsistency."""
    piv = {}; pref = set(prefer)
    for r, a0 in rows.items():
        a = dict(a0); b = dict(rhs.get(r, {}))
        while True:
            hit = [u for u in a if u in piv]
            if not hit: break
            u = hit[0]; f = a[u]; pa, pb = piv[u]
            addf(a, pa, -f); addf(b, pb, -f)
        if not a:
            if b: raise Inconsistent('inconsistent row %s cols %s' % (r, list(b)[:4]), r, list(b))
            continue
        u = min(a, key=lambda x: (x not in pref, x))
        f = a[u]; a = {x: v / f for x, v in a.items()}; b = {x: v / f for x, v in b.items()}
        for q in list(piv):
            pa, pb = piv[q]
            if u in pa:
                g = pa[u]; addf(pa, a, -g); addf(pb, b, -g)
        piv[u] = (a, b)
    return {u: b for u, (a, b) in piv.items()}

def run(w, enders, verbose=True, maxit=8):
    c = PX.Ctx(w); n, no, role = c.n, c.no, c.role
    E = {e['h']: e for e in enders}
    ins = collections.defaultdict(list)
    for e in enders:
        for R, a, t in e['use']: ins[t].append(['ADD', e['h'], R, str(a), e['f'], None])
    body = []
    for i, o in enumerate(c.body): body.append(list(o)); body += ins.get(i, [])
    f9 = [list(o) for o in c.f9 if o[1] not in E and o[2] not in E]
    S = c.born0                                   # dim-0 symbols (Y + 0-born helpers)
    Ys = {r for r in range(n) if role(r) == 'Y'}
    bad = set(E) | Ys
    t0 = time.time(); F0, _ = replay(body + f9, n, no)
    if verbose: print('F0 replay %.1fs' % (time.time() - t0), flush=True)
    A = {r: {s: v for s, v in F0[r].items() if s in S} for r in range(n)}
    R0 = {}
    for r in range(n):
        d = {k: F0[r].get(k, 0) - c.req[r].get(k, 0) for k in set(F0[r]) | set(c.req[r]) if k in S}
        R0[r] = {k: v for k, v in d.items() if v}
    K = set(E) | Ys
    def f9bad(r, fin):
        if r in K or role(r) not in ('H', 'X'): return False
        return any(k in bad for k in fin) or (role(r) == 'H' and fin.get(r, 0) != 1)
    U9 = {r for r in range(n) if f9bad(r, F0[r])}
    for it in range(maxit):
        U = K | U9
        if any(r not in S for r in U):
            print('CULPRIT', {r: [k for k in F0[r] if k in bad] for r in U if r not in S}, flush=True)
            raise PurexFail('PUREX2: rows needing dim-0 correction not born at 0: %s' % [r for r in U if r not in S][:6], 'L2_exit',
                            syms={r: [k for k in F0[r] if k in bad] for r in U if r not in S})
        # all rows of U fully constrained on every dim-0 column (square system A_UU Delta = -R0_U): Z invertible by construction
        cols = set()
        for r in U: cols |= set(R0[r])
        Delta = collections.defaultdict(dict)
        sysU = {r: {s: v for s, v in A[r].items() if s in U} for r in U}
        X = gauss_solve(sysU, {r: {t: v for t, v in ((t, -R0[r][t]) for t in R0[r])} for r in U}, prefer=())
        for s, b in X.items():
            for t, v in b.items():
                if v: Delta[s][t] = v
        # predicted finals of every register
        fin = {}; newbad = set()
        for r in range(n):
            f = dict(F0[r])
            for s, a in A[r].items():
                if s in Delta: addf(f, Delta[s], a)
            fin[r] = f
            if f9bad(r, f) and r not in U9: newbad.add(r)
        if verbose: print('iter', it, '|U9|', len(U9), 'Delta rows', len(Delta), 'nnz', sum(len(v) for v in Delta.values()), 'new bad', len(newbad), flush=True)
        if not newbad: break
        U9 |= newbad
    else: raise SystemExit('PUREX2: U closure did not converge')
    zops = realise_Z(c, Delta, S)
    return c, body, f9, zops, Delta

DYFIX = False   # GENUPGRADE --dyfix: complete the transvection elimination with the exact PB5 factoriser when the heuristic Euclid is stuck

def _dyfix(M, U, rowop):
    """reduce the CURRENT M (rows U) to I by dyadic elementary additions (gen2/dyadic.py = PLANBUILD5 _decompose, exact over Z[1/2], det 1);
    coefficients >= 2^15 are split into repeated additions (verifier: dyadic, |c|+1 < 2^16).  Recorded through rowop (so the program is exact)."""
    import dyadic
    idx = {r: k for k, r in enumerate(U)}
    A = [[Q(0)] * len(U) for _ in U]
    for r in U:
        for t, v in M[r].items(): A[idx[r]][idx[t]] = Q(v)
    BIG = Q(1 << 15)
    for i, j, t in dyadic._decompose(A):
        while abs(t) > BIG: st = BIG if t > 0 else -BIG; rowop(U[i], U[j], st); t -= st
        if t: rowop(U[i], U[j], t)
    print('DYFIX completed the Z elimination with the exact factoriser (%d rows)' % len(U), flush=True)

def realise_Z(c, Delta, S):
    """dim-0 ADDs realising V0 = M = I + Delta (rows U): transvection-only Gaussian elimination T_k..T_1 M = I with dyadic pivot moves,
    program = reversed elimination with negated coefficients (V <- T V per ADD)."""
    U = [r for r in Delta if Delta[r]]; Us = set(U)
    M = {r: dict(Delta[r]) for r in U}
    for r in U: M[r][r] = M[r].get(r, 0) + 1
    for r in U:
        if not M[r][r]: del M[r][r]
    el = []
    def rowop(i, j, q):                       # row_i += q row_j
        rj = M[j] if j in M else {j: Q(1)}
        addf(M[i], rj, q); el.append((i, j, q))
    for r in U:                               # non-U columns: pure sources
        for t in [t for t in M[r] if t not in Us]: rowop(r, t, -M[r][t])
    def odd(q):
        n = abs(q.numerator)
        while n % 2 == 0: n //= 2
        return n
    def p2(q): return q != 0 and odd(q) == 1
    def fixpivot(j, K):
        if not K: return False
        for _ in range(200):
            m = M[j].get(j, 0)
            if m == 1: return True
            for k in K:
                a = M[k].get(j, 0)
                if a and dy((1 - m) / a): rowop(j, k, (1 - m) / a); return M[j].get(j, 0) == 1
            if p2(m):                                   # make some row's entry a power of two using the pivot row
                k = K[0]; b = M[k][j]; pw = Q(1) if b > 0 else Q(-1)
                rowop(k, j, (pw - b) / m); continue
            # Euclid on column j among j and K: reduce the entry with the largest odd part
            ent = [(odd(M[x][j]), x) for x in [j] + K if M[x].get(j, 0)]
            ent.sort(); (oy, y), (ox, x) = ent[0], ent[-1]
            if ox == oy and x == y: return False
            a, b = M[x][j], M[y][j]
            ra = a / b; n = round(ra)                   # integer quotient of dyadic ratio after scaling
            sc = Q(1)
            while (ra * sc).denominator != 1: sc *= 2
            nn = Q(round(ra * sc)) / sc if False else None
            # choose q dyadic with |odd(a - q b)| < |odd(a)|: q = round(A/B) * 2^(alpha-beta)
            def split(v):
                e = 0; num, den = v.numerator, v.denominator
                while num % 2 == 0: num //= 2; e += 1
                while den % 2 == 0: den //= 2; e -= 1
                return num, e
            A_, al = split(a); B_, be = split(b)
            nq = round(Q(A_, B_)); q = Q(nq) * (Q(2) ** (al - be))
            if nq == 0: return False
            rowop(x, y, -q)
            if x in K and not M[x].get(j, 0): K = [k for k in K if k != x]
            if not K: return False
        return False
    pend = list(U); stuck = 0
    while pend:
        ps = set(pend); cc = collections.Counter(t for r in U for t in M[r] if t in ps)
        def score(j):
            rn = sum(1 for t in M[j] if t in ps and t != j)
            return (M[j].get(j, 0) != 1, rn * (cc[j] - 1), j)
        j = min(pend, key=score); pend.remove(j)
        if M[j].get(j, 0) != 1:
            ok = fixpivot(j, [k for k in pend if k != j and M[k].get(j, 0)])
            if not ok:
                pend.append(j); stuck += 1
                if DYFIX and stuck > len(pend) + 1: _dyfix(M, U, rowop); pend = []; break
                if stuck > 3 * len(pend) + 3: raise PurexFail('PUREX2: elimination stuck at %d columns' % len(pend), 'dyadic_stuck', pend=list(pend))
                if stuck > len(pend) + 1: raise PurexFail('PUREX2: elimination stuck at %d columns' % len(pend), 'dyadic_stuck', pend=list(pend))
                continue
        stuck = 0
        for i in U:
            if i != j and M[i].get(j, 0): rowop(i, j, -M[i][j])
    assert all(M[r] == {r: 1} for r in U), 'elimination did not reach I'
    bad = [q for _, _, q in el if not dy(q)]
    if bad: raise SystemExit('PUREX2: non-dyadic elimination coefficient %s' % bad[:3])
    return [['ADD', i, j, str(-q), c.Z, None] for i, j, q in reversed(el)]

def finish(c, body, f9, zops, E, verbose=True):
    n, no, role = c.n, c.no, c.role
    prog = zops + body + f9
    F, _ = replay(prog, n, no)
    todo = {}; badY = []
    for r in range(n):
        d = {k: F[r].get(k, 0) - c.req[r].get(k, 0) for k in set(F[r]) | set(c.req[r])}; d = {k: v for k, v in d.items() if v}
        if not d: continue
        if role(r) == 'Y' or r in E:
            badY.append((r, role(r), len(d)))
        else: todo[r] = d
    if badY: raise PurexFail('PUREX2: non-F9 residue %s' % badY[:6], 'nonF9_residue', rows=[r for r, _, _ in badY])
    fixes = []
    while todo:
        ready = [r for r, df in todo.items() if not any(k in todo for k in df) and df.get(r, 0) == 0]
        if not ready: raise PurexFail('PUREX2: cyclic/own F9 residue (%d), e.g. %s' % (len(todo), [(r, {k: str(v) for k, v in list(df.items())[:3]}) for r, df in list(todo.items())[:3]]), 'F9_cyclic',
                                      syms=sorted({k for df in todo.values() for k in df}))
        for r in ready:
            fixes += [['ADD', r, k, str(-v), c.F9, None] for k, v in sorted(todo[r].items())]; del todo[r]
    return prog + fixes

def culprits(ex, E):
    """enders named by a failure (GENUPGRADE --lawprune).  L2_exit = Exit Lemma (TWINBREAK L2): a public e_h-holder not born at dim 0 cannot be pre-cancelled,
    so the enders whose symbols it carries are dropped; L1 = inconsistent joint solve (twin/slot law, TWINBREAK L1): drop the row if it is an ender, else the
    ender columns of its residue; dyadic_stuck / nonF9 / F9_cyclic: the enders among the stuck rows / residue symbols."""
    if isinstance(ex, Inconsistent):
        return ('L1_slot', {ex.r} & set(E) or set(ex.cols) & set(E))
    cls = getattr(ex, 'cls', None); info = getattr(ex, 'info', {})
    if cls == 'L2_exit': return cls, {k for ks in info['syms'].values() for k in ks if k in E}
    if cls == 'dyadic_stuck': return cls, set(info['pend']) & set(E)
    if cls == 'nonF9_residue': return cls, set(info['rows']) & set(E)
    if cls == 'F9_cyclic': return cls, set(info['syms']) & set(E)
    return cls or 'other', set()

def lawprune(w, en):
    """run + finish; on a lemma-attributed failure drop the named enders and retry (at most len(en) rounds).  Prints one LAWPRUNE line per round."""
    for it in range(len(en) + 1):
        E = {e['h']: e for e in en}
        try:
            c, body, f9, zops, Delta = run(w, en)
            ops = finish(c, body, f9, zops, E)
            if it: print('LAWPRUNE solved after %d rounds, enders %d' % (it, len(en)), flush=True)
            return c, body, f9, zops, Delta, ops, en
        except (PurexFail, Inconsistent) as ex:
            cls, drop = culprits(ex, E)
            print('LAWPRUNE round %d class %s drop %s' % (it, cls, sorted(drop)), flush=True)
            if not drop: raise
            en = [e for e in en if e['h'] not in drop]
    raise SystemExit('PUREX2: lawprune did not converge')

def main(argv=None):
    os.environ['TK_FREE_BOUNDS'] = '1'
    a = sys.argv[1:] if argv is None else list(argv); inp, out = a[0], a[1]
    maxn = int(a[a.index('--max') + 1]) if '--max' in a else None
    dims = set(int(x) for x in a[a.index('--dims') + 1].split(',')) if '--dims' in a else None
    import kernel2net as KN, incr
    from tkcommon import profile_of
    w = json.load(gzip.open(inp)); c0 = PX.Ctx(w)
    if '--census-relax' in a: PX.RELAX.update(x for x in a[a.index('--census-relax') + 1].split(',') if x)   # RULEAUDIT (opt-in)
    en = c0.census(maxn=maxn, xstops='--xstops' in a, dims=dims)
    if '--skip' in a: sk = set(int(x) for x in a[a.index('--skip') + 1].split(',')); en = [e for e in en if e['h'] not in sk]
    print('enders', len(en), collections.Counter(c0.dim[e['f']] for e in en), flush=True)
    global DYFIX
    DYFIX = '--dyfix' in a
    if '--lawprune' in a:                      # GENUPGRADE (opt-in): on a failure, drop exactly the enders the violated law names and re-solve (never-lose; a config that solves is untouched)
        c, body, f9, zops, Delta, ops, en = lawprune(w, en)
    else:
        c, body, f9, zops, Delta = run(w, en)
        E = {e['h']: e for e in en}
        ops = finish(c, body, f9, zops, E)
    bad = [o for o in ops if o[0] == 'ADD' and not dy(o[3])]
    if bad: raise SystemExit('PUREX2: non-dyadic %s' % bad[:4])
    E = {e['h']: e for e in en}
    dag = dict(c.d); dag['ops'] = ops; dag['regs'] = {k: list(v) for k, v in c.d['regs'].items()}
    for h, e in E.items(): dag['regs'][str(h)][2] = e['f']
    w2, rep = c.D.realise(dag, schedule='lazy', verify=True)
    print('zops', len(zops), 'undelivered', rep['undelivered'][:3])
    w2['verifier_profile'] = dict(w.get('verifier_profile') or {})
    print('R0', {k: round(v, 1) for k, v in KN.r0(w2)[0].items()}, round(KN.r0(w2)[1], 1), 'events', len(w2['program']))
    iw = incr.IncrWord(w2, profile=profile_of(w)[0])
    print('legal', iw.legal_all, 'viol', len(iw.viol), iw.viol[:3], 'kappa %.13f' % iw.kappa, flush=True)
    c.D.save(w2, out); print('wrote', out)

if __name__ == '__main__': sys.exit(main())
