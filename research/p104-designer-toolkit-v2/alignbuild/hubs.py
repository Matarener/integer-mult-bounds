"""HUBRULES hubbuild2.py: rebuild EVERY event at a hub/end frame g from geometry + rules, any arrival/departure schedule (generalises hubbuild.py).
Kept: all MOVEs (chains = geometry), every event at other frames.  No swarm event at g is read.
  H1 span conservation (PROVED): any ADD/SCALE block is invertible on the co-present rows.
  H2 departures pinned (EXACT): D = target - replay(word without g events) = sum_s Phi_s(t_dep) (x) (dep_s - arr_s), solved jointly.
  H3 keep-what-is-needed (construction): before s departs, the present span V is split V = W + <dep_s> with W a hyperplane that contains
     V cap (future departures + enders' e_a + future arrivals); rows move along dep_s onto W (r -> r - phi(r) dep_s).  This is the twin rule in
     block form: a leftover a register keeps is exactly what a later arrival or departure can absorb.
  H4 enders: after the last departure the enders' rows must span <e_a>; a final block sets them to e_a.
  Blocks are realised by dyadic Gaussian elimination (ADD + SCALE), inserted just before each departure MOVE.
usage: hubbuild2.py WORD g OUT.json.gz [--quiet]"""
import sys, gzip, json, argparse, collections
import numpy as np
import os
HERE = os.path.dirname(os.path.abspath(__file__))   # alignbuild/: self-contained copy (no lane-dir imports)
sys.path[:0] = [HERE]
W = os.path.dirname(HERE)   # repo root (only used for default paths)
import rp
from rp import P
from mktbuild import colvec
S = rp.S

def vm(c, Bm):
    """(c @ Bm) mod P without int64 overflow"""
    out = np.zeros(Bm.shape[1], dtype=np.int64)
    for ci, row in zip(c, Bm): out = (out + (int(ci) % P) * (row % P)) % P
    return out
def fr(a): return rp.ratrec(int(a) % P)
def unit(x): return x is not None and x != 0 and rp.dyadic(x) and abs(x.numerator) == 1
def lab(c, role, n):
    r = role(c)
    return ('x%d' % c) if r == 'X' else ('y%d' % c) if r == 'Y' else ('h%d' % c) if c < n else ('o%d' % c)
def show(row, role, n): return ' '.join('%s:%s' % (lab(int(c), role, n), fr(row[c])) for c in np.flatnonzero(row % P))
def rank(M): return len(rp.rref(np.asarray(M) % P)[1]) if len(M) else 0
def coords(v, Bm):
    """x with x Bm = v (Bm rows independent) or None"""
    return rp.solve(Bm.T % P, v % P)

def psolve(Am, b, rng):
    """a solution of Am x = b mod P; seed-dependent column order (rng None or first try: identity) -> different basic solutions"""
    m = Am.shape[1]; perm = list(range(m))
    if not getattr(rng, 'ident', False): rng.shuffle(perm)
    x_ = rp.solve(Am[:, perm] % P, b)
    if x_ is None: return None
    x = np.zeros(m, dtype=np.int64)
    for i, p in enumerate(perm): x[p] = x_[i]
    return x

def odd(x):
    """dyadic x = 2^e * o (o odd integer) -> (e, o)"""
    num, den = x.numerator, x.denominator; e = -(den.bit_length() - 1)
    while num % 2 == 0: num //= 2; e += 1
    return e, num

def realise(Mx, regs, g, t):
    """events turning rows V into Mx V (Mx k x k mod P, must be dyadic): forward Euclid over Z[1/2] (no row swaps: registers keep their
    identity), back substitution, then E Mx = Delta  ->  apply SCALE Delta first, then the inverse ops in reverse order.  -> (events, None) or (None, why)"""
    from fractions import Fraction as Q
    k = len(regs); Mf = [[fr(Mx[i, j]) for j in range(k)] for i in range(k)]
    if any(x is None or (x != 0 and not rp.dyadic(x)) for row in Mf for x in row): return None, 'block matrix not dyadic'
    A = [[Q(x) for x in row] for row in Mf]; ops = []
    def add(i, kk, c):
        if c == 0: return
        for jj in range(k): A[i][jj] += c * A[kk][jj]
        ops.append((i, kk, c))
    for j in range(k):
        while True:
            nz = [i for i in range(j, k) if A[i][j] != 0]
            if not nz: return None, 'singular column %d' % j
            if len(nz) == 1: break
            m = min(nz, key=lambda i: abs(odd(A[i][j])[1]))
            em, om = odd(A[m][j])
            for i in nz:
                if i == m: continue
                ei, oi = odd(A[i][j]); tq = round(Q(oi, om))
                add(i, m, -Q(2) ** (ei - em) * tq)
        m = nz[0]
        if m != j: add(j, m, Q(1)); add(m, j, Q(-1))
    for j in range(k - 1, -1, -1):
        for i in range(j):
            if A[i][j] != 0:
                c = -A[i][j] / A[j][j]
                if not rp.dyadic(c): return None, 'back-substitution nondyadic (pivot %s)' % A[j][j]
                add(i, j, c)
    ev = []
    for i in range(k):
        if A[i][i] != 1:
            if not rp.dyadic(A[i][i]): return None, 'diagonal nondyadic'
            ev.append((t, ['SCALE', regs[i], rp.fstr(A[i][i]), g]))
    for i, kk, c in reversed(ops): ev.append((t, ['ADD', regs[i], regs[kk], rp.fstr(-c), g]))
    return ev, None

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('word'); ap.add_argument('g', type=int); ap.add_argument('out'); ap.add_argument('--quiet', action='store_true'); ap.add_argument('--tries', type=int, default=200); ap.add_argument('--drop', default=''); ap.add_argument('--owned', action='store_true')
    a = ap.parse_args()
    path, w0 = S.load_word(a.word); w = json.loads(json.dumps(w0)); n = len(w['initial']); R = rp.nreg(w); g = a.g
    role = S.roles_of(w); say = (lambda *x: None) if a.quiet else print
    for r_ in [int(x) for x in a.drop.split(',') if x]:      # remove r_'s stop at g: MOVE a->g ... MOVE g->b  becomes  MOVE a->b at the old departure time
        pg = w['program']; i1 = next(i for i, e in enumerate(pg) if e[0] == 'MOVE' and e[1] == r_ and e[3] == g)
        i2 = next(i for i, e in enumerate(pg) if i > i1 and e[0] == 'MOVE' and e[1] == r_)
        assert pg[i2][2] == g
        pg[i2] = ['MOVE', r_, pg[i1][2], pg[i2][3], pg[i2][4]]; del pg[i1]
        say('  dropped the g stop of', r_)
    dropped = [e for e in w['program'] if e[0] in ('ADD', 'COPY', 'SCALE') and e[-1] == g]
    prog = [e for e in w['program'] if not (e[0] in ('ADD', 'COPY', 'SCALE') and e[-1] == g)]
    w['program'] = prog; tl = rp.timelines(w, prog); T = len(prog)
    M = sorted(r for r in range(R) if any(f == g for _, _, f in tl[r]))
    if any(r >= n for r in M) and not a.owned: print('RESULT: owned register(s) at g %s: not built' % [r for r in M if r >= n]); return
    if any(sum(1 for _, _, f in tl[r] if f == g) > 1 for r in M): print('RESULT: a member visits g twice: not built'); return
    iv = {r: [(t0, t1) for t0, t1, f in tl[r] if f == g][0] for r in M}
    N = [r for r in M if r < n and w['final'][r] == g]; non = [r for r in M if r not in N]
    CLR = set(s_ for s_ in non if prog[iv[s_][1]][0] == 'CLEAR')     # owned registers cleared at g: free departure
    PIN = [s_ for s_ in non if s_ not in CLR]
    say('g', g, 'enders', N, 'members', non, '| swarm events at g', len(dropped))
    # arrival rows (value at arrival is unaffected by g events up to that time, given the replay is causal; checked at the end)
    snap = {}
    for r in M: snap.setdefault(max(iv[r][0], 0) + (1 if iv[r][0] >= 0 else 0), []).append(r)
    A_end, sn = rp.replay(w, prog, snap=snap)
    arrt = {r: max(iv[r][0], 0) + (1 if iv[r][0] >= 0 else 0) for r in M}
    ARR = {r: sn[arrt[r]][r] % P for r in M}
    Tg = rp.target(w); D = (Tg - A_end) % P
    # ---- H2 departures, joint
    k = len(PIN); NS = set(N); rows = [r for r in range(R) if r not in NS]
    if k:
        Phi = np.array([colvec(prog, iv[s][1], s, R) for s in PIN]).T % P
        E_, piv = rp.rref(Phi[rows].T)
        if len(piv) < k: print('RESULT: Phi dependent (rank %d < %d): departures not pinned' % (len(piv), k)); return
        pr = [rows[i] for i in piv]
        aug = np.concatenate([Phi[pr] % P, np.eye(k, dtype=np.int64)], axis=1); Er, _ = rp.rref(aug); Pinv = Er[:, k:] % P
        delta = np.zeros((k, R), dtype=np.int64)
        for i in range(k):
            for j in range(k): delta[i] = (delta[i] + Pinv[i, j] * D[pr[j]]) % P
        chk = np.zeros((len(rows), R), dtype=np.int64)
        for i in range(k): chk = (chk + Phi[rows, i][:, None] * delta[i][None, :] % P) % P
        if ((chk - D[rows]) % P).any():
            print('RESULT: residual not explained by member departures (rows %s)' % [rows[i] for i in np.flatnonzero(((chk - D[rows]) % P).any(1))][:8]); return
        DEP = {s: (ARR[s] + delta[i]) % P for i, s in enumerate(PIN)}
    else: DEP = {}
    for s in PIN: say("  pinned dep", role(s), s, show(DEP[s], role, n)[:300])
    for a_ in N:
        if D[a_].any() and not ((D[a_] - (np.eye(R, dtype=np.int64)[a_] - ARR[a_])) % P == 0).all(): pass
    FIN = {a_: np.eye(R, dtype=np.int64)[a_] for a_ in N}
    def schedule(rng, verbose):
        # ---- time-ordered schedule
        evs = sorted([(arrt[r], 0, r) for r in M] + [(iv[s][1], 1, s) for s in non])
        present = []; Cur = {}; ins = []; nblocks = 0; report = []
        for idx, (t, kind, r) in enumerate(evs):
            if kind == 0:
                present.append(r); Cur[r] = ARR[r].copy()
                if r < n and rank([Cur[x] for x in present]) < len(present): return None, ('RESULT: arrival of %d is dependent on the present rows' % r)
                continue
            s = r; V = np.array([Cur[x] for x in present]) % P
            if verbose: say("  departure", s, "t", t, "present", present, "rank V", rank(V), "rank V+dep", rank(np.vstack([V, DEP[s][None, :]])))
            si0 = present.index(s); others = [i for i in range(len(present)) if i != si0]
            rkV = rank(V); rkO = rank(V[others]) if others else 0
            if s in CLR and rkO == rkV:          # cleared register holds nothing the others lack: no events
                present.remove(s); report.append('clear %d: 0 events' % s); continue
            if s not in CLR and rkO == rkV:      # redundant row: s := dep using the others, nothing else changes
                cso = coords((DEP[s] - V[si0]) % P, V[others])
                if cso is None:
                    if verbose: say('   dbg redundant', s, present, rkV, rkO, rank(np.vstack([V[others], DEP[s][None, :]])), 'arr779 eq dep', not ((ARR.get(779, DEP[s]) - DEP[s]) % P).any())
                    return None, ('RESULT: H1 fails, departure of %d outside the present span' % s)
                ev = []
                for j_, x in zip(others, cso):
                    if x:
                        f_ = fr(x)
                        if not rp.dyadic(f_): return None, ('RESULT: departure row of %d not a dyadic combination' % s)
                        ev.append((t, ['ADD', s, present[j_], rp.fstr(f_), g]))
                if ev: ins += ev; nblocks += 1
                Cur[s] = DEP[s].copy(); present.remove(s); report.append('dep %d (redundant): %d events' % (s, len(ev))); continue
            if s in CLR: DEP[s] = V[si0].copy()     # cleared and unique: it takes its own row away (H3 checks that nobody needs it)
            cs = coords(DEP[s], V)
            if cs is None: return None, ('RESULT: H1 fails, departure of %d outside the present span at t%d' % (s, t))
            fut = evs[idx + 1:]
            Xn = [DEP[x] for (_, kd, x) in fut if kd == 1 and x not in CLR] + [FIN[x] for x in N]
            Fa = [ARR[x] for (_, kd, x) in fut if kd == 0]
            def inter(XFl):
                XF = np.array(XFl) % P
                Mx = np.vstack([V, (-XF) % P])
                Er, pv = rp.rref(Mx.T % P); kk = Mx.shape[0]; free = [j for j in range(kk) if j not in pv]
                out = []
                for f_ in free:
                    z = np.zeros(kk, dtype=np.int64); z[f_] = 1
                    for i, c in enumerate(pv): z[c] = (-Er[i, f_]) % P
                    if z[:len(present)].any(): out.append(z[:len(present)])
                return out
            phi = None
            for XFl in (Xn + Fa, Xn):        # keep V cap (X+F) (safe); fallback keep only V cap X (later arrivals may resupply; replay decides)
                Ic = inter(XFl)
                Am = np.array(Ic + [cs]) % P; b = np.zeros(len(Ic) + 1, dtype=np.int64); b[-1] = 1
                phi = psolve(Am, b, rng)
                if phi is not None: break
            if phi is None: return None, ('RESULT: H3 fails at departure of %d (t%d): the departing row is needed later' % (s, t))
            # dyadic phi: basic solution, else search the affine family phi0 + null(Am)
            def dy(v): return all(x == 0 or rp.dyadic(fr(x)) for x in v)
            if not dy(phi):
                nul = []
                Er2, pv2 = rp.rref(Am)
                for f_ in [j for j in range(len(present)) if j not in pv2]:
                    z = np.zeros(len(present), dtype=np.int64); z[f_] = 1
                    for i, c in enumerate(pv2): z[c] = (-Er2[i, f_]) % P
                    nul.append(z)
                # try to zero the non-dyadic entries using the null directions one at a time (cheap heuristic)
                for z in nul:
                    for i in range(len(present)):
                        if not (phi[i] == 0 or rp.dyadic(fr(phi[i]))) and z[i]:
                            cand = (phi - phi[i] * pow(int(z[i]), P - 2, P) % P * z) % P
                            if dy(cand) or sum(1 for x in cand if x and not rp.dyadic(fr(x))) < sum(1 for x in phi if x and not rp.dyadic(fr(x))): phi = cand
            if not dy(phi): return None, ('RESULT: no dyadic split W at departure of %d (phi %s)' % (s, [str(fr(x)) for x in phi]))
            si = present.index(s); ev = []; Vc = V.copy()
            if cs[si] == 0:
                jl = [i for i in range(len(present)) if cs[i] and i != si and rp.dyadic(fr(cs[i]))]; j = jl[0] if getattr(rng, 'ident', False) else jl[rng.randrange(len(jl))]
                ev.append((t, ['ADD', present[j], s, '1', g])); Vc[j] = (Vc[j] + Vc[si]) % P
                cs = coords(DEP[s], Vc)
                # phi refers to the old basis: recompute phi on the new basis (phi(r) is basis-free: phi_new_j = phi(r_j + r_s))
                phi = phi.copy(); phi[j] = (phi[j] + phi[si]) % P
            css = [fr(x) for x in cs]
            if not all(x is None or x == 0 or rp.dyadic(x) for x in css) or css[si] in (None, 0): return None, ('RESULT: departure row of %d not a dyadic combination' % s)
            if css[si] != 1: ev.append((t, ['SCALE', s, rp.fstr(css[si]), g]))
            for i, x in enumerate(css):
                if i != si and x: ev.append((t, ['ADD', s, present[i], rp.fstr(x), g]))
            for i, x in enumerate(present):
                if i != si and phi[i]:
                    c = fr((-phi[i]) % P); ev.append((t, ['ADD', x, s, rp.fstr(c), g]))
            # new rows by direct replay of ev on Vc
            Cn = {x: V[i].copy() for i, x in enumerate(present)}
            for _, e in ev:
                if e[0] == 'SCALE': Cn[e[1]] = Cn[e[1]] * rp.qm(e[2]) % P
                else: Cn[e[1]] = (Cn[e[1]] + Cn[e[2]] * rp.qm(e[3])) % P
            if ((Cn[s] - DEP[s]) % P).any(): return None, ('RESULT: internal: departure row mismatch for %d' % s)
            Rn = np.array([Cn[x] for x in present if x != s]) % P
            Wb = np.vstack([Rn, DEP[s][None, :]])
            if rank(Wb) < rkV: return None, ('RESULT: block loses content at departure of %d' % s)
            if ev: ins += ev; nblocks += 1
            Cur.update(Cn); present.remove(s)
            report.append('dep %d: %d events; enders now %s' % (s, len(ev), ' | '.join('%d: %s' % (x, show(Cur[x], role, n)[:90]) for x in present if x in NS)))
        # ---- final block on enders
        V = np.array([Cur[x] for x in N]) % P
        Mf = []
        for x in N:
            c = coords(FIN[x], V)
            if c is None: return None, ('RESULT: H4 fails, e_%d not in the enders\' final span' % x)
            Mf.append(c)
        Mf = np.array(Mf) % P
        if (Mf != np.eye(len(N), dtype=np.int64)).any():
            tlast = max(t for t, _, _ in evs) + 1
            ev, why = realise(Mf, N, g, tlast)
            if ev is None: return None, ('RESULT: final ender block fails: %s' % why)
            ins += ev; nblocks += 1
        return ins, nblocks, report
    import random
    res = None; fails = collections.Counter()
    for seed in range(a.tries):
        rr = random.Random(seed); rr.ident = (seed == 0)
        out = schedule(rr, seed == 0)
        if out[0] is not None: res = out; say('  schedule found at seed', seed); break
        fails[out[1].split(' at ')[0][:60]] += 1
    if res is None: print('RESULT: no schedule in %d tries:' % a.tries, dict(fails)); return
    ins, nblocks, report = res; evs_ = None
    for line in report: say('  ', line)
    prog2 = rp.insert(prog, ins); w['program'] = prog2
    Af, _ = rp.replay(w, prog2); Dd = (Tg - Af) % P
    if Dd.any(): print('RESULT: replay residual rows', [int(r) for r in np.flatnonzero(Dd.any(1))][:8]); return
    S.C.activate(w); rep = S.C.legal.check(w)
    if not rep['ok']: print('RESULT: ILLEGAL', rep['violations'][:2]); return
    kp = S.C.X.kappa(*S.C.X.invoice(rep)); S.C.activate(w0); k0 = S.C.X.kappa(*S.C.X.invoice(S.C.legal.check(w0)))
    print('RESULT: LEGAL kappa %.15f base %.15f diff %+.3e | events at g rebuilt %d in %d blocks vs swarm %d | program %d vs %d'
          % (kp, k0, kp - k0, len(ins), nblocks, len(dropped), len(prog2), len(w0['program'])))
    with gzip.open(a.out, 'wt') as fh: json.dump(w, fh)

if __name__ == '__main__': main()
