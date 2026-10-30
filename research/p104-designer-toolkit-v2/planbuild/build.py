"""PLANBUILD build.py: PLAN -> WORD realiser (from scratch: no #6030 ids). Input = a pm3/pm4 pick on the pm2 population (plan.population()).
Engine = SKELGEN skeloct / OCTETGEN octet.py transposition (EXACT): bottom = pm2's piece network N forward + F9 Bennett restore; top = pm2's
dual network DN transposed (D = Finv L F J => D^T), landings L^T at g_a.  Per arrival k (piece live rect, dual live rect, dual sink a):
  b (own)  : the dual rect register lands at a itself (t=0 lander): in primal it descends to g_a and reads the piece register.
  a (own)  : a newborn landing carrier, IDENTIFIED (QUADHUB composition): the piece register climbs g_a -> perp(g_R) and is read there.
  c        : newborn landing carrier kept: a copy (0, dg, dH, 9).
  d (own)  : t=0 lander + exact fusion: ident3 (rect register H, only read in primal) or d2g (piece register H, never a bottom source, read only by
             this landing; plays d / lam from F0 on; J-trick for extra junk symbols in J[a]).
  a' (alt) : the SECOND holder at g. Not realisable without a sink (ONEADD merge-sink lemma); --alt refill emits q += p / q -= p and lets the
             value check show the failure.  Otherwise alt options and unfusable d are re-planned (pass 2) to the cheapest own option a / b / c
             under F1 (one crossing per register) -- reported as 'unrealisable options re-planned'.
Checks (every run): realised R0 == plan.evaluate() of the EFFECTIVE pick (no hubs); Y x-residue == signal term (C2 S4 / 2) on all 104 rows;
every X / helper at its required final form; IncrWord legality (residual-only words: 3 expected violations = no owned lifetime + absent signal).
PLANBUILD5 (flags, default path unchanged): --force-only a,b,.. / --force-d force the naive d fusion (ident3) also at second holders; --repair = exact F9 REPAIR: every non-Y register that ends off its
required form gets the unique covector solution (sum x_q F_q = req - F_r), the dirty block map A = I + X (det 1) is factored into DYADIC elementary additions (Euclid on odd parts + SL2 scale identity),
then additions from the clean registers; all are F9 events (R0 0). A Y coefficient = unrepairable (no op, value check shows it). --defer = DEFERRED CANCEL variant (re-add f_B - f_0 to the fused register before the
bottom restore, remove after; --defer-late / --nojfix variants): never better than --repair alone in the census (pb5b). --list-miss prints the unrealisable d sites.
usage: build.py PICK OUT.json.gz [--alt refill] [--fb-b] [--no-jtrick] [--noyfuse] [--force-only A,B] [--repair]   (env only in main; 1-3 s, --repair on >100 forced sites minutes)"""
import sys, os, collections, json, gzip, time, pickle, io, contextlib
from fractions import Fraction as Fr
W = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')); TK = W
HERE = TK + '/planbuild'
for p in (TK, TK + '/synth', W + '/infra', TK + '/gen2', HERE):
    if p not in sys.path: sys.path.insert(0, p)
import numpy as np
import plan

def addf(d, s, q):
    for c, v in s.items():
        t = d.get(c, 0) + q * v
        if t: d[c] = t
        else: d.pop(c, None)

def RES(j, i):
    import geo
    return Fr(geo.RES[j, i]).limit_denominator(8)

def model(pick, alt=None, log=print):
    """build the realiser model from pm2's population and the pick. returns M (skeloct layout) + eff (effective pick) + fallbacks"""
    import rt
    import copy
    B = copy.deepcopy(plan.population()); N, DN = B['N'], B['DN']; meta = B['meta']   # the realiser adds carriers/landing stops: keep the plan population pristine
    dsrc = {o[1] for o in DN.ops}; bsrc = {o[1] for o in N.ops}
    arr_k = {}; kof = {}
    for k, (prid, drid, dk) in enumerate(B['arr']): kof[dk] = k
    # bottom: pm2's N, SHARE semantics (one piece register per live rect serves all its blocks)
    bops = list(N.ops); extra = []; pre = []
    arr = []
    for (prid, k) in [B['dmeta'][dk] for dk in range(len(B['dmeta']))]:
        arr.append((prid, k, N.rects[prid]['reg']))
    # dual sinks = pm2's dsnk order (dk); exact coefficients (skeloct convention: c_j = -res_ji / (sc v_i))
    dmeta = []; dcoef = []
    for dk, (prid, k) in enumerate(B['dmeta']):
        R = N.rects[prid]; mm = meta[k]; a0 = next(iter(R['A'])); js = mm[3]
        c = {j: -RES(j, a0) / (R['sc'] * R['v'][a0]) for j in js}
        for b_ in R['A']:
            for j in js: assert -RES(j, b_) == c[j] * R['sc'] * R['v'][b_], 'rank1'
        dmeta.append(('a', R['reg'], prid)); dcoef.append(c)
    DI = rt.Inst([[p] for p in __import__('geo').PORTS], [list(N.rects[prid]['g']) for (prid, k) in B['dmeta']], {})
    # per dual rect: lander + carrier roles from the pick
    eff = {}; fb = collections.Counter(); role_of = {}
    for k, o in pick.items():
        prid, drid, dk = B['arr'][k]; p = ('b', N.rects[prid]['reg']); d = ('d', DN.rects[drid]['reg'])
        if o[0] in 'ab' and o[1] not in (p, d):
            if alt and o[0] == 'a': role_of[dk] = ('alta', o[1][1]); eff[k] = o; continue
            fb[('alt' + o[0], 'c')] += 1; role_of[dk] = ('c',); eff[k] = ('c',); continue
        if o[0] == 'd' and alt and o[2] == d and o[1] != p:     # shared-piece fusion at the SECOND holder q (with a sink, --alt sink): decided in assemble
            role_of[dk] = ('dfuse', k, o[1][1]); eff[k] = o; continue
        if o[0] == 'd' and (o[1], o[2]) != (p, d):
            fb[('altd', 'c')] += 1; role_of[dk] = ('c',); eff[k] = ('c',); continue
        if o[0] == 'd':
            role_of[dk] = ('dfuse', k); eff[k] = o      # decided in assemble (exact identification or fallback to b)
            continue
        role_of[dk] = (o[0],); eff[k] = o
    first = {}
    for dk, r in role_of.items():
        if r[0] in ('b', 'dfuse'):
            drid = B['arr'][kof[dk]][1]; assert drid not in first, ('two landers', drid); first[drid] = dk
    # dual landings (exact coefficients)
    dops = list(DN.ops); lands = []
    DF0 = DI.frame([])
    for rid in sorted(DN.live):
        R = DN.rects[rid]
        for a in sorted(R['B'], key=lambda a: (a != first.get(rid), a)):
            nb = (a != first.get(rid))
            reg = R['reg']
            if nb:
                reg = DN.newreg('H', DF0[0], 0); DN.stop(reg, R['g'], len(R['g'])); dops.append((reg, R['reg'], Fr(1), R['g'], len(R['g'])))
            j0 = next(iter(R['A'])); lamc = dcoef[a][j0] / (R['sc'] * R['v'][j0])
            for j in R['A']: assert dcoef[a][j] == lamc * R['sc'] * R['v'][j], 'dual rank1'
            Q = DI.frame(list(rt.perp(DI.snkb[a]))); DN.stop(reg, Q[0], Q[1]); lands.append((a, reg, lamc, Q[0], R['reg'], R['g'], nb))
    log('pick roles', dict(collections.Counter(r[0] for r in role_of.values())), 'fallbacks', dict(fb), 'landers', len(first))
    return dict(I=None, N=N, DN=DN, meta=meta, arr=arr, bops=bops, extra=extra, pre=pre, feeders={}, DI=DI, dmeta=dmeta, dcoef=dcoef,
                dops=dops, lands=lands, role_of=role_of, eff=eff, fb=fb, B=B, kof=kof)

def plan_A(B, k):
    prid, drid, dk = B['arr'][k]; N, DN = B['N'], B['DN']
    return ('b', N.rects[prid]['reg']), ('d', DN.rects[drid]['reg']), len(N.rects[prid]['g']), 9 - len(DN.rects[drid]['g']), B['meta'][B['dmeta'][dk][1]][0]

def dual_check(M):
    DN = M['DN']; F = sorted(range(len(M['dops'])), key=lambda t: (M['dops'][t][4], t)); ops = [M['dops'][t] for t in F]
    val = {}
    for r, Rg in DN.regs.items(): val[r] = {('y', Rg['tag']): Fr(1)} if Rg['role'] == 'X' else {('h', r): Fr(1)}
    S = collections.defaultdict(dict)
    for (d, s, q, fk, dim) in ops: addf(val[d], val[s], q)
    for (a, reg, lamc, Q, *_r) in M['lands']: addf(S[a], val[reg], lamc)
    for (d, s, q, fk, dim) in reversed(ops): addf(val[d], val[s], -q)
    for r, Rg in DN.regs.items():
        want = {('y', Rg['tag']): Fr(1)} if Rg['role'] == 'X' else {('h', r): Fr(1)}
        assert val[r] == want, ('dual restore', r)
    J = {}
    for a in range(len(M['dmeta'])):
        y = {c[1]: v for c, v in S[a].items() if c[0] == 'y'}
        assert y == M['dcoef'][a], ('dual sink', a)
        J[a] = {c[1]: v for c, v in S[a].items() if c[0] == 'h'}
    return ops, J

DEFER = '--defer' in sys.argv or '--defer2' in sys.argv
DEFER2 = '--defer2' in sys.argv      # PLANBUILD5 three-stage view correction: R := bottom view beta before J^T, R := f_B before the restore, R := unit after
RMAP = {int(a_): int(r_) for a_, r_ in json.load(open(sys.argv[sys.argv.index('--rsink-map') + 1])).items()} if '--rsink-map' in sys.argv else {}   # PLANBUILD5: a' site (dual sink index) -> N register id used as the RESIDENT sink Z
REPAIR = '--repair' in sys.argv
DEFERJ = '--defer-late' not in sys.argv   # corrections go right after F^T (before J^T), so J^T reads of R see the f_B content
JFIX = ('--jfix' in sys.argv or ('--defer' in sys.argv and '--defer2' not in sys.argv)) and '--nojfix' not in sys.argv     # PLANBUILD5: a fused (ident3) register keeps its J^T junk cleaning for every OTHER sink
DEFER_STAT = {}

def _step(F, o):
    d, s, q = o[1], o[2], Fr(o[3]); t = F[d]
    for c, v in F[s].items():
        x = t.get(c, 0) + q * v
        if x: t[c] = x
        else: t.pop(c, None)

def _cov(ops, upto, C):
    """x with sum_r x_r * F_r(after ops[:upto]) = C (covector pass: v[s] -= q v[d] over the ops in forward order; exact, M is unitriangular)"""
    v = dict(C)
    for o in ops[:upto]:
        vd = v.get(o[1])
        if vd:
            x = v.get(o[2], 0) - Fr(o[3]) * vd
            if x: v[o[2]] = x
            else: v.pop(o[2], None)
    return v

def defer_fix(ops, pB, i0, i1, targets, XS, YS, F9, log):
    """PLANBUILD5 DEFERRED CANCEL. A fused register R is read by the bottom forward with content f_B (pi + delta0 ...), by the bottom restore with f_0
    (F^T has cancelled delta0). Before the restore R gets f_B - f_0 added back by F9 events; after the restore R gets (F - required) removed again by
    F9 events. The coefficient vectors are exact (covector pass over the ops so far); sources must be X / helper registers (Y registers have no F9
    stop: a Y coefficient is recorded as UNREPAIRABLE and the op is NOT emitted, so the value check shows it). DEFER_STAT records the cost classes."""
    n = 1 + max(max(o[1], o[2] if o[2] is not None else 0) for o in ops)
    F = [{r: Fr(1)} for r in range(n)]
    for o in ops[:pB]: _step(F, o)
    fB = {r: dict(F[r]) for r in targets}
    cls = lambda r: 'X' if r in XS else 'Y' if r in YS else 'H'
    def fix(upto, want, tag):
        res = []; stat = collections.Counter(); Fc = _forms(ops, upto, [], n)
        for r in targets:
            cur = Fc[r]
            C = {c: want[r].get(c, 0) - cur.get(c, 0) for c in set(want[r]) | set(cur) if want[r].get(c, 0) != cur.get(c, 0)}
            if not C: continue
            x = _cov(ops[:upto] + res, upto + len(res), C)
            if x.get(r): stat['self'] += 1; DEFER_STAT.setdefault('missing', []).append((tag, r, 'self', str(x[r])))
            for q, v in sorted(x.items()):
                if q == r: continue
                if cls(q) == 'Y': stat['!Y'] += 1; DEFER_STAT.setdefault('missing', []).append((tag, r, q, 'Y', str(v))); continue
                o = ['ADD', r, q, str(v), list(F9), None]; res.append(o); _step(Fc, o); stat[cls(q)] += 1
        return res, stat
    new1, st1 = fix(i0, fB, 'pre')
    if '--debug-defer' in sys.argv:
        Fq = _forms(ops, i0, new1, n); F0q = _forms(ops, pB, [], n)
        # the restore starts after i1-segment's J^T: the restore ops are the last (i1-i0') ops; here compare at i0 (+pre)
        dif = [(r, len(Fq[r]), len(F0q[r]), len(set(Fq[r]) ^ set(F0q[r]))) for r in range(n) if Fq[r] != F0q[r] and r in DEFER_STAT.get('bot', ())]
        print('DEBUG-DEFER registers differing between end-of-B and start-of-restore (after pre):', len(dif), dif[:30])
    mid = ops[:i0] + new1 + ops[i0:i1]
    new2, st2 = fix(len(mid), {r: {r: Fr(1)} for r in targets}, 'post') if False else _post(mid, targets, n, F9, cls)
    DEFER_STAT.update(pre=dict(st1), post=dict(st2), npre=len(new1), npost=len(new2))
    log('deferred cancel: targets', len(targets), 'pre', dict(st1), 'post', dict(st2))
    return mid + new2 + ops[i1:]

def defer_fix2(ops, pF0, pB0, pU, i0, i1, targets, XS, YS, F9, log):
    """three view corrections of every fused register R (all F9 events, exact covector solves): (1) after F^T, before J^T: R := beta = f_B - delta0 (the bottom view the J^T reads of a shared R need);
    (2) before the bottom restore: R := f_B (B^-1 is then an exact inverse on the bottom); (3) after the restore: R := unit."""
    n = 1 + max(max(o[1], o[2] if o[2] is not None else 0) for o in ops)
    F = [{r: Fr(1)} for r in range(n)]
    for o in ops[:pF0]: _step(F, o)
    f0 = {r: dict(F[r]) for r in targets}
    for o in ops[pF0:pB0]: _step(F, o)
    fB = {r: dict(F[r]) for r in targets}
    beta = {r: {c: fB[r].get(c, 0) - (f0[r].get(c, 0) - (1 if c == r else 0)) for c in set(fB[r]) | set(f0[r]) if fB[r].get(c, 0) - (f0[r].get(c, 0) - (1 if c == r else 0)) != 0} for r in targets}
    cls = lambda r: 'X' if r in XS else 'Y' if r in YS else 'H'
    def stage(cur_ops, want, tag):
        res = []; stat = collections.Counter(); Fc = _forms(cur_ops, len(cur_ops), [], n)
        for r in targets:
            cur = Fc[r]; C = {c: want[r].get(c, 0) - cur.get(c, 0) for c in set(want[r]) | set(cur) if want[r].get(c, 0) != cur.get(c, 0)}
            if not C: continue
            x = _cov(cur_ops + res, len(cur_ops) + len(res), C)
            for q, v in sorted(x.items()):
                if q == r: stat['self'] += 1; continue
                if cls(q) == 'Y': stat['!Y'] += 1; continue
                o = ['ADD', r, q, str(v), list(F9), None]; res.append(o); _step(Fc, o); stat[cls(q)] += 1
        return res, stat
    c1, s1 = stage(ops[:pU], beta, 'beta')
    a = ops[:pU] + c1 + ops[pU:i0]
    c2, s2 = stage(a, fB, 'fB')
    b = a + c2 + ops[i0:i1]
    c3, s3 = stage(b, {r: {r: Fr(1)} for r in targets}, 'unit')
    log('defer2: targets', len(targets), 'beta', dict(s1), 'fB', dict(s2), 'unit', dict(s3))
    DEFER_STAT.update(n1=len(c1), n2=len(c2), n3=len(c3))
    return b + c3 + ops[i1:]

def _forms(ops, upto, extra, n):
    F = [{r: Fr(1)} for r in range(n)]
    for o in ops[:upto]: _step(F, o)
    for o in extra: _step(F, o)
    return F

def _post(mid, targets, n, F9, cls):
    res = []; stat = collections.Counter(); Fc = _forms(mid, len(mid), [], n)
    for r in targets:
        cur = Fc[r]; want = {r: Fr(1)}
        C = {c: want.get(c, 0) - cur.get(c, 0) for c in set(want) | set(cur) if want.get(c, 0) != cur.get(c, 0)}
        if not C: continue
        x = _cov(mid + res, len(mid) + len(res), C)
        for q, v in sorted(x.items()):
            if q == r: stat['self'] += 1; continue
            if cls(q) == 'Y': stat['!Y'] += 1; DEFER_STAT.setdefault('missing', []).append(('post', r, q, 'Y', str(v))); continue
            o = ['ADD', r, q, str(v), list(F9), None]; res.append(o); _step(Fc, o); stat[cls(q)] += 1
    return res, stat

FORCEONLY = {int(x) for x in sys.argv[sys.argv.index('--force-only') + 1].split(',')} if '--force-only' in sys.argv else set()
SINK = False   # set in main from '--alt sink'

def assemble(M, log=print):
    """primal op list + register table (skeloct.assemble, identifications driven by the pick roles)"""
    import rt, geo
    P = geo.PORTS; m = geo.m
    N, DN = M['N'], M['DN']
    w0 = json.load(gzip.open(TK + '/words/5827.json.gz')); live = list(w0['live']); ports = list(w0['ports']); assert ports == P
    XR = {i: live[i] for i in range(m)}; YR = {j: live[j] + 112 for j in range(m)}
    used = set(XR.values()) | set(YR.values()); nxt = [224]
    def newh():
        while nxt[0] in used: nxt[0] += 1
        r = nxt[0]; used.add(r); nxt[0] += 1; return r
    bmap = {}
    for r, Rg in N.regs.items(): bmap[r] = XR[Rg['tag']] if Rg['role'] == 'X' else newh()
    dmap = {}
    for r, Rg in DN.regs.items(): dmap[r] = YR[Rg['tag']] if Rg['role'] == 'X' else newh()
    F0 = (); F9 = rt.rref([1 << b for b in range(9)])
    pf = lambda fk: rt.perp(fk) if fk else F9
    dops, J = dual_check(M)
    S_of = {a: bmap[mm[1]] for a, mm in enumerate(M['dmeta'])}
    ro = M['role_of']
    ident = {}; ident2 = {}; ident3 = {}; fac = collections.defaultdict(lambda: Fr(1)); bfac = collections.defaultdict(lambda: Fr(1))
    dsrc = {o[1] for o in dops}
    bfw = list(M['pre']) + [M['bops'][t] for t in sorted(range(len(M['bops'])), key=lambda t: (M['bops'][t][4], t))] + list(M['extra'])
    bsrc = {o[1] for o in bfw}
    miss = collections.Counter(); refill = []; forced = set()
    for (a, reg, lamc, Q, rreg, g, nb) in M['lands']:
        r = ro[a][0]
        if r == 'alta':     # second holder q at g: refilled q += p at g after the bottom, read in place of p; q -= p at F9 (exactness judged by the value check)
            assert nb
            q = ro[a][1]; pr = M['dmeta'][a][1]; gfr = N.regs[pr]['frames'][-1]
            assert any(f == gfr for f in N.regs[q]['frames']), 'alt holder not at g'
            refill.append((bmap[q], bmap[pr], gfr, (bmap[RMAP[a]] if a in RMAP else (newh() if SINK else None)))); S_of[a] = bmap[q]
            ident[reg] = (a, rreg, lamc, g); continue
        if r == 'a':
            assert nb
            assert J[a].get(reg) == lamc and all(reg not in J[b] for b in J if b != a), 'ident junk'
            ident[reg] = (a, rreg, lamc, g)
        elif r == 'dfuse':
            k = ro[a][1]; b = M['dmeta'][a][1]; qalt = ro[a][2] if len(ro[a]) > 2 else None
            if qalt is not None:      # second-holder fusion: q is refilled with pi through a sink and plays the piece register b below
                pr_ = b; b = qalt; gfr_ = N.regs[pr_]['frames'][-1]; S_of[a] = bmap[b]
            single = all(M['lands'][0] is not None for _ in [0]) and sum(1 for x in M['lands'] if x[4] == rreg) == 1
            readers_b = [x for x in S_of if S_of[x] == S_of[a]]
            # d3 (ident3): rect register only READ in primal (never a dual source, no carriers): replaced by the piece register / lam
            if DN.regs[reg]['role'] == 'H' and reg not in dsrc:
                fr = sorted({pf(o[3]) for o in dops if o[0] == reg}, key=len); spans = [rt.span_set(f) for f in fr]
                okn = all(spans[t] <= spans[t + 1] for t in range(len(spans) - 1)) and (not fr or set(rt.span_set(N.regs[b]['frames'][-1])) <= spans[0])
                if okn:
                    ident3[reg] = (a, lamc)
                    if qalt is not None: refill.append((bmap[b], bmap[pr_], gfr_, (bmap[RMAP[a]] if a in RMAP else (newh() if SINK else None))))
                    continue
            # d2g (ident2 generalised): piece register b is a 0-born helper, never a bottom source, read only by this landing (J[a] = {d: lam});
            # b plays d / lam from F0 on (= the composite with initial(d) = lam h_b, initial(S_a) = 0); d may be a dual source / have carriers.
            # A Y main d: the Y register plays b scaled by lam instead.
            # J-trick (--no-jtrick to disable): extra junk symbols h' in J[a] are allowed for an H d; their J^T reads of the fused register are
            # emitted after every J^T write into it (it then holds h_b + pi) and corrected by h' += v f after the bottom restore (f = h_b).
            jok = J[a].get(reg) == lamc and (J[a] == {reg: lamc} or ('--no-jtrick' not in sys.argv and DN.regs[reg]['role'] == 'H'))
            if N.regs[b]['role'] == 'H' and b not in bsrc and readers_b == [a] and jok and M['dmeta'][a][0] == 'a':
                if qalt is None and DN.regs[reg]['role'] == 'H':
                    ident2[reg] = (a, b, lamc); dmap[reg] = bmap[b]; fac[bmap[b]] = 1 / lamc; continue
                elif qalt is None and '--noyfuse' not in sys.argv:
                    ident2[reg] = (a, b, lamc); bmap[b] = dmap[reg]; bfac[b] = lamc; S_of[a] = dmap[reg]; continue
            if '--force-d' in sys.argv or a in FORCEONLY:       # PLANBUILD3 experiment: naive sharing of the piece register and the dual register (value check shows the residue); PLANBUILD5: also at second holders (refill through the sink)
                ident3[reg] = (a, lamc); forced.add(reg)
                if qalt is not None: refill.append((bmap[b], bmap[pr_], gfr_, (bmap[RMAP[a]] if a in RMAP else (newh() if SINK else None))))
                continue
            why = ('dsrc' if reg in dsrc else '') + ('psrc' if b in bsrc else '') + ('pX' if N.regs[b]['role'] == 'X' else '') + ('shared' if len(readers_b) > 1 else '') + ('J' if J[a] != {reg: lamc} else '')
            if qalt is not None: S_of[a] = bmap[pr_]; M['eff'][k] = ('c',); miss['d(alt)->c ' + why] += 1; M.setdefault('misssite', {})[a] = ('alt', reg, b, why); continue
            miss['d->b ' + why] += 1; M['eff'][k] = ('b', ('d', reg)); M.setdefault('misssite', {})[a] = ('own', reg, b, why)
    for reg, (a, lamc) in ident3.items(): dmap[reg] = S_of[a]; fac[S_of[a]] = 1 / lamc
    if '--debug' in sys.argv:
        for reg in forced: print('DEBUG forced dual', reg, 'dmap', dmap[reg], 'own sink', ident3[reg], 'J entries', [(b, str(J[b][reg])) for b in J if reg in J[b]], 'role', DN.regs[reg]['role'], 'dsrc-ops', sum(1 for o in dops if o[1] == reg), 'dst-ops', sum(1 for o in dops if o[0] == reg))
    if miss: log('identification misses', dict(miss))
    M['miss'] = miss
    if '--list-miss' in sys.argv: print('MISSSITES', json.dumps({str(a): v for a, v in sorted(M.get('misssite', {}).items())}))
    isid = lambda o: o[0] in ident and o[1] == ident[o[0]][1] and o[2] == 1
    ops = []
    def add(d, s, q, f): ops.append(['ADD', d, s, str(Fr(q)), list(f), None])
    def addt(d, s, q, f): add(d, s, q * fac[d] / fac[s], f)
    def addl(d, s, q, f): add(d, s, q * fac[d], f)
    for o in dops:                                   # 1. F0 block: transposed dual restore
        if isid(o) or (o[0] in ident3 and o[0] not in forced): continue
        (d, s, q, fk, dim) = o; addt(dmap[s], dmap[d], -q, F0)
    pF0 = len(ops)
    for (d, s, q, fk, dim) in bfw: add(bmap[d], bmap[s], q * bfac[d] / bfac[s], fk)          # 2. bottom forward
    pB0 = len(ops)
    for (qq, pp, gfr, zz) in refill:                                       # 2b. refill the second holders at g
        if zz is not None: add(zz, qq, 1, gfr); add(qq, zz, -1, gfr)       #     --alt sink: the displaced content w moves to a fresh sink Z (0,g,9) first: Z += q; q -= Z
        add(qq, pp, 1, gfr)
    pB = len(ops)
    tl = [(len(pf(Q)), dmap[reg], S_of[a], lamc, pf(Q)) for (a, reg, lamc, Q, *_r) in M['lands'] if reg not in ident and reg not in ident2 and reg not in ident3]
    for (_, d, s, q, f) in sorted(tl, key=lambda x: x[0]): addl(d, s, q, f)   # 3. L^T
    for o in reversed(dops):                         # 4. F^T
        (d, s, q, fk, dim) = o
        if isid(o): a, rreg, lamc, g = ident[d]; addl(dmap[rreg], S_of[a], lamc, pf(fk)); continue
        addt(dmap[s], dmap[d], q, pf(fk))
    pU = len(ops)
    fusedS = {ident2[h][0]: dmap[h] for h in ident2}            # sink a -> fused register (b playing d / lam)
    late = []; post = []; jops = []
    for a, Ja in J.items():                          # 5. F9: J^T (reads of a fused register last), bottom restore, J-trick corrections
        for h, v in Ja.items():
            if h in ident or (h in ident3 and (ident3[h][0] == a or not JFIX)) or (h in ident2 and ident2[h][0] == a): continue
            if a in fusedS: late.append((dmap[h], S_of[a], -v)); post.append((dmap[h], S_of[a], v)); continue
            jops.append((dmap[h], S_of[a], -v))
    if JFIX and forced:       # PLANBUILD5: a fused register is cleaned of its own J junk BEFORE any other J^T op reads it (it then holds the bottom view); dependency order, cycles fall back to input order
        FS = {dmap[r] for r in forced}; tot_ = collections.Counter(d_ for (d_, s_, q_) in jops if d_ in FS); done_ = collections.Counter()
        rest = list(jops); jops = []
        while rest:
            for t_, (d_, s_, q_) in enumerate(rest):
                if s_ not in FS or done_[s_] == tot_[s_]: break
            else: t_ = 0
            d_, s_, q_ = rest.pop(t_); jops.append((d_, s_, q_))
            if d_ in FS: done_[d_] += 1
    for (d_, s_, q_) in jops: addl(d_, s_, q_, F9)
    for (d_, s_, q_) in late: addl(d_, s_, q_, F9)
    for (qq, pp, gfr, zz) in refill:
        add(qq, pp, -1, F9)
        if zz is not None: add(qq, zz, 1, F9); add(zz, qq, -1, F9)
    i0 = pU if (DEFERJ and not DEFER2) else len(ops)
    for (d, s, q, fk, dim) in reversed(bfw): add(bmap[d], bmap[s], -q * bfac[d] / bfac[s], F9)
    i1 = len(ops)
    if DEFER and forced:                # PLANBUILD5 deferred cancel: keep delta0 in the fused registers through the bottom restore reads, cancel it afterwards
        DEFER_STAT['bot'] = set(bmap.values())
        if DEFER2: ops = defer_fix2(ops, pF0, pB0, pU, i0, i1, sorted({dmap[r] for r in forced}), set(XR.values()), set(YR.values()), F9, log)
        else: ops = defer_fix(ops, pB0, i0, i1, sorted({dmap[r] for r in forced}), set(XR.values()), set(YR.values()), F9, log)
    for (d_, s_, q_) in post: addl(d_, s_, q_, F9)
    log('identified: carriers', len(ident), 'ident2', len(ident2), 'ident3', len(ident3))
    return dict(fusedreg=sorted({dmap[r] for r in forced}), ops=ops, XR=XR, YR=YR, used=used, ck={}, bmap=bmap, dmap=dmap, n=max(used) + 1, live=live, ports=ports, w0=w0, F9=F9)

def prune(A):
    XY = set(A['XR'].values()) | set(A['YR'].values()); n0 = A['n']
    act = sorted({r for o in A['ops'] for r in (o[1], o[2]) if r is not None and r < n0 and r not in XY})
    mp = {r: 224 + t for t, r in enumerate(act)}
    if any(v in XY for v in mp.values()): raise SystemExit('prune: id clash')
    for r in XY: mp[r] = r
    A['ops'] = [[o[0], mp[o[1]], (mp[o[2]] if o[2] is not None else None)] + o[3:] for o in A['ops']]
    A['used'] = XY | set(range(224, 224 + len(act))); A['n'] = 224 + len(act)
    A['mp'] = mp
    A['bmap'] = {k: mp.get(v, v) for k, v in A['bmap'].items()}; A['dmap'] = {k: mp.get(v, v) for k, v in A['dmap'].items()}
    return A

def _odd(a):
    """a in Z[1/2], a != 0: (s, odd integer o) with a = 2^s o"""
    p, q = a.numerator, a.denominator          # q a power of two
    s = -(q.bit_length() - 1)
    while p % 2 == 0: p //= 2; s += 1
    return s, p

def _decompose(A):
    for extra in (24, 88, 216, 472):
        try: return _decompose1(A, extra)
        except AssertionError as e:
            if str(e) != 'scale overflow': raise
    raise AssertionError('scale overflow')

def _decompose1(A, extra):
    """A: rows over Z[1/2] (m x m, list of lists of Fractions, det 1). Returns elementary row ops (i, j, t), t DYADIC Fraction [row_i += t row_j], that reduce A to I.
    Integer-scaled sparse rows (value = n / 2^SC); connected components eliminated independently; Euclid on the odd parts only when no unit pivot exists (a unit pivot, the diagonal
    first, needs no division); the leftover unit diagonal (product 1) is fixed across components by diag(d, 1/d) = W(d) W(-1), W(t) = U(t) L(-1/t) U(t)."""
    m = len(A); SC = max([(v.denominator.bit_length() - 1) for r in A for v in r if v] + [0]) + extra
    one = 1 << SC
    R = [{c: int(v * one) for c, v in enumerate(r) if v} for r in A]; ops = []
    for r in R:
        pass
    def odd(n):
        low = (n & -n).bit_length() - 1
        return low, n >> low
    par = list(range(m))
    def find(a):
        while par[a] != a: par[a] = par[par[a]]; a = par[a]
        return a
    for i in range(m):
        for c in R[i]: par[find(i)] = find(c)
    comp = collections.defaultdict(list)
    for i in range(m): comp[find(i)].append(i)
    def add(i, j, t):                                  # row_i += t row_j, t dyadic Fraction
        if t == 0: return
        tn, td = t.numerator, t.denominator
        assert (td & (td - 1)) == 0, ('non-dyadic', t)
        sh = td.bit_length() - 1; Ri = R[i]
        for c, v in R[j].items():
            w = v * tn
            if sh:
                assert w & (td - 1) == 0, 'scale overflow'
                w >>= sh
            x = Ri.get(c, 0) + w
            if x: Ri[c] = x
            else: Ri.pop(c, None)
        ops.append((i, j, t))
    for members in comp.values():
        members.sort(key=lambda i: len(R[i]))            # sparse rows first (less fill)
        for jj, j in enumerate(members):
            while True:
                nz = [i for i in members[jj:] if R[i].get(j)]
                assert nz, 'singular'
                if len(nz) == 1: break
                p = min(nz, key=lambda i: (abs(odd(R[i][j])[1]), i != j))      # a unit pivot (prefer the diagonal) if there is one
                sp, op = odd(R[p][j])
                for i in nz:
                    if i == p: continue
                    si, oi = odd(R[i][j])
                    qq = oi // op                           # floor division on the odd parts: remainder |r| < |op|
                    if qq: add(i, p, -Fr(qq) * Fr(2) ** (si - sp))
            p = nz[0]
            if p != j:
                assert not R[j].get(j), 'pivot'
                add(j, p, Fr(1)); add(p, j, -Fr(R[p][j], R[j][j]))
        for j in members:
            assert abs(odd(R[j][j])[1]) == 1, ('pivot not a unit', R[j][j])
        for j in reversed(members):
            for i in members:
                if i != j and R[i].get(j): add(i, j, -Fr(R[i][j], R[j][j]))
    P = Fr(1)
    for j in range(m): P *= Fr(R[j][j], one)
    assert P == 1, ('det', P)
    def W(i, j, t): add(i, j, t); add(j, i, -1 / t); add(i, j, t)
    for j in range(m - 1):
        d = Fr(R[j][j], one)
        if d != 1:
            W(j, j + 1, Fr(-1)); W(j, j + 1, 1 / d)       # diag(1/d, d) = W(1/d) W(-1)
    assert all(R[i] == {i: one} for i in range(m)), 'decompose'
    return ops

def repair_dirty(ops, Fm, req, n, YS, F9):
    """PLANBUILD5 exact F9 repair of the non-Y registers that end off their required form. Each dirty r gets the unique covector x_r with sum_q x_rq F_q = req_r - F_r
    (a Y coefficient = UNREPAIRABLE). The joint map A = I + X on the dirty block has det 1 (all ops are additions) and is factored into elementary additions
    (_decompose: also handles own-coefficient drift, the SL2 scale identity), followed by the additions from the clean registers. All F9 events."""
    dirty = [r for r in range(n) if r not in YS and Fm[r] != req[r]]
    bad = []; X = {}
    for r in dirty:
        C = {c: req[r].get(c, 0) - Fm[r].get(c, 0) for c in set(req[r]) | set(Fm[r]) if req[r].get(c, 0) != Fm[r].get(c, 0)}
        x = _cov(ops, len(ops), C)
        if any(q in YS for q in x): bad.append((r, 'Y', len(x))); continue
        X[r] = x
    D = sorted(X); idx = {r: t for t, r in enumerate(D)}; m = len(D)
    if '--debug-repair' in sys.argv:
        import pickle as _pk; _pk.dump(dict(D=D, X={r: {q: str(v) for q, v in X[r].items()} for r in D}), open(W + '/ext/PLANBUILD5/repairX.pkl', 'wb'))
    if not m: return dict(ops=[], bad=bad, dirty=len(dirty))
    BIG = Fr(1 << 15)
    def emit(new, d_, s_, t):
        while abs(t) >= BIG:                                                              # verifier: |coefficient| + 1 < 2^16 -> split large multipliers
            c = BIG if t > 0 else -BIG
            new.append(['ADD', d_, s_, str(c), list(F9), None]); t -= c
        if t: new.append(['ADD', d_, s_, str(t), list(F9), None])
    def matrix(S):
        ix = {r: i for i, r in enumerate(S)}; A = [[Fr(0)] * len(S) for _ in S]
        for r in S:
            A[ix[r]][ix[r]] += 1
            for q, v in X[r].items():
                if q in ix: A[ix[r]][ix[q]] += v
        return A
    # SCC condensation of "r reads q" (q dirty): a reader is processed before its sources (they are still old); singletons without self-coefficient need only their additions,
    # a cyclic SCC (det 1) is factored into dyadic elementary additions (_decompose), then the additions from outside the SCC.
    adj = {r: [q for q in X[r] if q in idx and q != r] for r in D}; order = []; seen = {}; low = {}; stack = []; onst = set(); cnt = [0]
    for root in D:
        if root in seen: continue
        work = [(root, iter(adj[root]))]; seen[root] = low[root] = cnt[0]; cnt[0] += 1; stack.append(root); onst.add(root)
        while work:
            v, it = work[-1]
            adv = False
            for w in it:
                if w not in seen:
                    seen[w] = low[w] = cnt[0]; cnt[0] += 1; stack.append(w); onst.add(w); work.append((w, iter(adj[w]))); adv = True; break
                elif w in onst: low[v] = min(low[v], seen[w])
            if adv: continue
            work.pop()
            if work: low[work[-1][0]] = min(low[work[-1][0]], low[v])
            if low[v] == seen[v]:
                comp = []
                while True:
                    w = stack.pop(); onst.discard(w); comp.append(w)
                    if w == v: break
                order.append(comp)
    new = []; eo_all = 0
    try:
        for comp in reversed(order):                                                      # readers first
            cs = set(comp)
            if len(comp) > 1 or comp[0] in X[comp[0]]:
                import time as _t; _t0 = _t.time()
                if '--debug-repair' in sys.argv: print('REPAIR scc start size', len(comp), 'nnz', sum(len(X[r]) for r in comp), flush=True)
                A = matrix(comp); eo = _decompose(A); eo_all += len(eo)
                if '--debug-repair' in sys.argv: print('REPAIR scc', len(comp), 'ops', len(eo), '%.1fs' % (_t.time() - _t0), 'max|t|', max([abs(t) for (_i, _j, t) in eo] or [0]), flush=True)
                for (i, j, t) in reversed(eo): emit(new, comp[i], comp[j], -t)
            for r in comp:
                for q, v in sorted(X[r].items()):
                    if q not in cs: emit(new, r, q, v)
    except AssertionError as e:
        return dict(ops=[], bad=bad + [('decompose', str(e), m)], dirty=len(dirty))
    if '--debug-repair' in sys.argv:
        print('REPAIR m', m, 'SCCs', len(order), 'cyclic', sum(1 for c_ in order if len(c_) > 1), 'decomposition ops', eo_all, 'total ops', len(new), 'nnz X', sum(len(X[r]) for r in D))
    return dict(ops=new, bad=bad, dirty=len(dirty))

def to_word(A, nowned=8):
    """residual-only word (no roots): Ys miss the signal; undelivered = the absent signal only"""
    import dag as D, geo, rt
    P = geo.PORTS; m = geo.m
    A = prune(A)
    n = A['n']; no = nowned; F9 = A['F9']; ops = A['ops']
    meta = dict(npub=n, nowned=no, live=A['live'], ports=A['ports'], public=n, schema=A['w0'].get('schema'), owned_fields=no)
    regs = {}
    XS = set(A['XR'].values()); YS = set(A['YR'].values())
    for r in range(n):
        if r in XS: i = A['live'].index(r); regs[str(r)] = ['X', [P[i]], list(F9)]
        elif r in YS: j = A['live'].index(r - 112); regs[str(r)] = ['Y', [], list(rt.perp([P[j]]))]
        else: regs[str(r)] = ['helper', [], list(F9)]
    for o in range(n, n + no): regs[str(o)] = ['owned', None, None]
    helpers = {r for r in A['used'] if r not in XS and r not in YS}
    Fm, _ = D.apply_forms(ops, meta); req = D.required(meta)
    if REPAIR:       # PLANBUILD5: final F9 repair of every dirty non-Y register by exact covector solve (sources: any non-Y register's CURRENT form, F9 events)
        A['repair'] = repair_dirty(ops, Fm, req, n, YS, A['F9'])
        ops = A['ops'] = ops + A['repair']['ops']; A['n_repair'] = len(A['repair']['ops'])
        Fm, _ = D.apply_forms(ops, meta)
    pre = []; nonh = collections.Counter()
    for j in range(m):
        y = A['YR'][j]; d = {c: Fm[y].get(c, 0) - req[y].get(c, 0) for c in set(Fm[y]) | set(req[y])}
        for c, v in sorted(d.items()):
            if not v: continue
            if c in helpers: pre.append(['ADD', y, c, str(-v), [], None])
            else: nonh[c] += 1
    # value check (EXACT): what the Ys still miss on the x columns must be exactly the signal term (C2 S4 / 2)_ji (residual-only build)
    sig = {(j, i): Fr(int(v), 2) for j, row in enumerate((geo.C2 @ geo.S4).astype(int).tolist()) for i, v in enumerate(row) if v}
    xcol = {A['live'][i]: i for i in range(m)}; bad = 0
    for j in range(m):
        y = A['YR'][j]
        for c in set(Fm[y]) | set(req[y]):
            if c in helpers: continue
            v = req[y].get(c, 0) - Fm[y].get(c, 0)
            want = sig.get((j, xcol[c]), 0) if c in xcol else 0
            if v != want: bad += 1
    A['sigcheck'] = bad
    # every non-Y register must end exactly at its required form (helpers restored, X mains = x_i)
    A['dirty'] = [r for r in range(n) if r not in YS and Fm[r] != req[r]]
    if '--debug' in sys.argv:
        for r in A['dirty'][:12]: print('  dirty', r, {c: str(Fm[r].get(c, 0) - req[r].get(c, 0)) for c in set(Fm[r]) | set(req[r]) if Fm[r].get(c, 0) != req[r].get(c, 0)})
        for r in A['dirty'][:12]:
            res = {c: Fm[r].get(c, 0) - req[r].get(c, 0) for c in set(Fm[r]) | set(req[r]) if Fm[r].get(c, 0) != req[r].get(c, 0)}
            print('  dirty-types', r, 'role', 'X' if r in XS else 'Y' if r in YS else 'H', 'resid symbols: X', sum(1 for c in res if c in XS), 'Y', sum(1 for c in res if c in YS), 'helper', sum(1 for c in res if c in helpers), 'other', sum(1 for c in res if c not in XS | YS | helpers))
    if '--debug-writes' in sys.argv:
        Fz = [{q: Fr(1)} for q in range(n)]
        want = set(A['dirty'][:3]) | {A['mp'].get(r, r) for r in A.get('fusedreg', [])}
        for i, o in enumerate(ops):
            if o[1] in want: print('WR', i, 'reg', o[1], '<-', o[2], 'q', o[3], 'dim', len(o[4]) if o[4] else 0, 'src', len(Fz[o[2]]), 'dst', len(Fz[o[1]]))
            _step(Fz, o)
        print('WR-END dirty', A['dirty'][:8], 'XR/YR sample', sorted(A['XR'].values())[:3])
    ops2 = pre + ops
    dag = dict(schema=D.SCHEMA, meta=meta, frames=[[]], regs=regs, ops=ops2, values=[], schedule=dict(hops=[]))
    w, rep = D.realise(dag, 'lazy', (), verify=True)
    w['verifier_profile'] = dict(public=n, owned_fields=no, lifetimes=sum(1 for o in ops2 if o[0] == 'INIT'), peak=1)
    return w, rep, nonh, len(pre), A

def main():
    os.environ['TK_FREE_BOUNDS'] = '1'
    a = sys.argv[1:]; pk = pickle.load(open(a[0], 'rb')); out = a[1]
    g = lambda k, d: a[a.index(k) + 1] if k in a else d
    t0 = time.time()
    with contextlib.redirect_stdout(io.StringIO()): plan.population()
    global SINK
    SINK = g('--alt', None) == 'sink'
    M = model(pk, alt=g('--alt', None))
    A = assemble(M)
    redo = {k: o for k, o in M['eff'].items() if o != pk[k]}
    if redo and '--fb-b' not in a:      # pass 2: every unrealisable option becomes the cheapest own option: a (piece climbs, carrier identified), b (dual descends; one lander per rect), c
        import flagmodel as FM, rt
        with contextlib.redirect_stdout(io.StringIO()): B0 = plan.population()
        ch, role = FM.regs_of(B0); fch = {r: list(c) for r, c in ch.items()}; lander = set(); used = set()   # F1: one crossing per register (pm3/pm4)
        for k, o in M['eff'].items():
            if k in redo: continue
            _, _, dg, dH, _ = plan_A(B0, k)
            if o[0] in 'ab': used.add(o[1])
            if o[0] == 'd': used |= {o[1], o[2]}
            if o[0] == 'a': fch[o[1]].append(dH)
            elif o[0] in 'bd': lander.add(B0['arr'][k][1])
            if o[0] == 'b': fch[o[1]].append(dg)
            elif o[0] == 'd': fch[o[1]] = fch[o[1]] + fch[o[2]]
        pk2 = dict(M['eff']); nab = collections.Counter()
        for k, o in sorted(redo.items()):
            p, d, dg, dH, _ = plan_A(B0, k)
            opts = {'c': rt.tax([0, dg, dH, 9])}
            if p not in used: opts['a'] = FM.ftax(fch[p] + [dH], role[p]) - FM.ftax(fch[p], role[p])
            if B0['arr'][k][1] not in lander and d not in used: opts['b'] = FM.ftax(fch[d] + [dg], role[d]) - FM.ftax(fch[d], role[d])
            best = min(opts, key=opts.get); nab[(pk[k][0] + ('-own' if pk[k][0] != 'a' and pk[k][0] != 'b' or True else ''), best)] += 1
            if best == 'a': pk2[k] = ('a', p); fch[p].append(dH); used.add(p)
            elif best == 'b': pk2[k] = ('b', d); fch[d].append(dg); lander.add(B0['arr'][k][1]); used.add(d)
            else: pk2[k] = ('c',)
        print('pass 2: unrealisable options re-planned (input option, new option):', dict(nab), flush=True)
        fb1 = M['fb']; miss1 = M['miss']
        M = model(pk2, alt=g('--alt', None)); M['fb'] = collections.Counter({kk: v for kk, v in nab.items()}); A = assemble(M)
        M['miss'] = miss1 + M['miss']
    w, rep, nonh, npre, A = to_word(A)
    import dag as D
    D.save(w, out)
    import kernel2net as KN
    by, tot = KN.r0(w)
    print('R0 realised', {k: round(v, 2) for k, v in by.items()}, round(tot, 2), 'events', len(w['program']), 'junk loads', npre,
          'nonhelper residue', sum(nonh.values()), 'undelivered', len(rep['undelivered']), flush=True)
    with contextlib.redirect_stdout(io.StringIO()): ev = plan.evaluate(plan.population(), M['eff'], hubs=False, verbose=False)
    print('model R0 of the EFFECTIVE pick (no hubs) %.2f' % ev['R0'], {k: round(v, 2) for k, v in ev['tot'].items()}, '| realised - model %.4f' % (tot - ev['R0']), flush=True)
    with contextlib.redirect_stdout(io.StringIO()): ev0 = plan.evaluate(plan.population(), pk, hubs=False, verbose=False)
    print('model R0 of the INPUT pick (no hubs) %.2f; fallback cost %.2f' % (ev0['R0'], ev['R0'] - ev0['R0']), flush=True)
    print('value check: Y x-residue == signal term exactly on all 104 rows' if A['sigcheck'] == 0 else 'VALUE CHECK FAILED: %d entries' % A['sigcheck'],
          '| non-Y registers not at their required final form:', len(A['dirty']), A['dirty'][:5], flush=True)
    if REPAIR: print('F9 repair: dirty', A['repair']['dirty'], 'ops', len(A['repair']['ops']), 'unrepairable', A['repair']['bad'][:6], flush=True)
    if True:
        import incr
        from tkcommon import load, profile_of
        p, w5 = load('5756'); prof = profile_of(w5)[0]
        iw = incr.IncrWord(w, profile=prof)
        print('legal', iw.legal_all, 'viol', len(iw.viol), iw.viol[:3], 'kappa %.13f' % iw.kappa, flush=True)
    json.dump(dict(eff={str(k): list(map(str, v)) for k, v in M['eff'].items()}, fb={str(k): v for k, v in M['fb'].items()}, miss=dict(M['miss'])), open(out.replace('.json.gz', '.plan.json'), 'w'))
    print('wrote', out, '%.1fs' % (time.time() - t0))

if __name__ == '__main__': main()
