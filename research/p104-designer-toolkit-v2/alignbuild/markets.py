"""ALIGNLAW fullbuild.py: rebuild ALL events of the market members at octet dual G from the rules (no member event of the word is kept).
Inputs taken from the word: geometry (G, the d6/d7/d8 frame table), the pieces = non-member registers that stop at a d6 frame containing G, and the residual
D = target - replay(word without any member event) (what the members must deliver). Construction (rules, module docstring sec 4):
  R1 served Ys = Ys with nonzero residual; D_k = sum_i C_ki * row(piece i, last moment at its d6 frame) (solved);
  R2 pieces are paired by a perfect matching whose pairs lie in a dim-7 frame G+p_i+p_j inside both served Ys' Q (searched over all matchings);
  R3 per pair one member reads each piece at its d6 frame, the pair butterflies at the d7 frame (closed form), each delivers to one Y at Q (dim 8);
  R4 one member per pair is a 0-born proxy, the other is born at G (both orientations tried); junk: clique Ys pre-read proxies at F0, newborns load into
     proxies at G (coefficients solved, linear); R5 cleanup of members at the end at F9 against unit rows.
usage: fullbuild.py WORD G OUT.json.gz [--readtime last|first]"""
import sys, os, gzip, json, itertools, argparse, collections
import numpy as np
from fractions import Fraction as Q
import os
HERE = os.path.dirname(os.path.abspath(__file__))   # alignbuild/: self-contained copy (no lane-dir imports)
sys.path[:0] = [HERE]
W = os.path.dirname(HERE)   # repo root (only used for default paths)
import rp
from rp import P, qm
from life import rref, perp
from mktbuild import colvec
S = rp.S

EXTRA = []
def inv(a): return pow(int(a) % P, P - 2, P)
def frac(a):
    fr = rp.ratrec(int(a) % P)
    return fr

FREEB = [False]
COMPACT = [True]   # compact member tail (module flag; main --legacy turns it off)
TAILINFO = {}
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('word'); ap.add_argument('G', type=int); ap.add_argument('out')
    ap.add_argument('--readtime', default='last'); ap.add_argument('--orient', default='auto'); ap.add_argument('--k', type=int); ap.add_argument('--allsub', action='store_true'); ap.add_argument('--freebounds', action='store_true'); ap.add_argument('--legacy', action='store_true')
    a = ap.parse_args(); FREEB[0] = a.freebounds
    if a.legacy: COMPACT[0] = False
    path, w0 = S.load_word(a.word); w = json.loads(json.dumps(w0)); n = len(w['initial']); R = rp.nreg(w)
    fr = w['frames']; dim = [len(b) for b in fr]; span = [rref(b) for b in fr]; G = a.G; SG = span[G]
    live = w['live']; Ys = [r + 112 for r in live]; Yset = set(Ys); F0 = w['initial'][Ys[0]]
    role = S.roles_of(w); prog0 = w['program']; tl0 = rp.timelines(w)
    contains = lambda big, small: rref(list(big) + list(small)) == big
    fidx = collections.defaultdict(list)
    for i, s in enumerate(span): fidx[s].append(i)
    M = sorted(r for r in range(n) if role(r) == 'H' and any(f == G for _, _, f in tl0[r]))
    Mset = set(M)
    # ---- strip every member event
    prog = [e for e in prog0 if not any(x in Mset for x in S.regfields(e))]
    F9 = {m: w['final'][m] for m in M}
    for m in M: w['initial'][m] = G
    w['program'] = prog
    tl = rp.timelines(w, prog)
    # pieces: non-member, non-Y public registers with a stop at a d6 frame containing G
    pieces = []
    for r in range(n):
        if r in Mset or r in Yset: continue
        for t0, t1, f in tl[r]:
            if dim[f] == 6 and contains(span[f], SG): pieces.append((r, f, t0, min(t1, len(prog) - 1)))
    print('G', G, 'members', M, 'pieces', [(p, f) for p, f, _, _ in pieces])
    tr = {}
    for p, f, t0, t1 in pieces: tr.setdefault(t1 if a.readtime == 'last' else t0 + 1, []).append(p)
    A_end, snaps = rp.replay(w, prog, snap=tr)
    Tgt = rp.target(w); D = (Tgt - A_end) % P
    bad = [r for r in range(R) if D[r].any() and r not in Yset and r not in Mset]
    served = [y for y in Ys if D[y].any()]
    EXTRA[:] = [r for r in bad if w['initial'][r] == F0]
    print('served Ys (nonzero residual):', served, '| other rows with residual:', bad[:8])
    prow = {}
    for p, f, t0, t1 in pieces:
        t = t1 if a.readtime == 'last' else t0 + 1; prow[p] = snaps[t][p]
    nonJ = np.ones(R, dtype=bool); nonJ[M] = False
    pl = [p for p, _, _, _ in pieces]
    Aeq = np.array([prow[p][nonJ] for p in pl]).T % P
    C = {}
    for y in served:
        x = rp.solve(Aeq, D[y][nonJ])
        if x is None: print('RESULT: R1 fails, Y', y, 'not in the span of piece rows'); return
        C[y] = {p: int(v) for p, v in zip(pl, x) if v}
        print('  Y', y, 'needs', {p: str(frac(v)) for p, v in C[y].items()})
    pf = {p: f for p, f, _, _ in pieces}; pt = {p: (t0, t1) for p, f, t0, t1 in pieces}
    Qf = {y: w['final'][y] for y in served}
    # ---- R2: matchings
    def pairframe(i, j):
        s = rref(list(span[pf[i]]) + list(span[pf[j]]))
        return fidx[s][0] if len(s) == 7 and fidx.get(s) else None
    def matchings(L):
        if not L: yield []; return
        a0 = L[0]
        for k in range(1, len(L)):
            for rest in matchings(L[1:k] + L[k + 1:]): yield [(a0, L[k])] + rest
    sols = []
    used = sorted(set(p for y in served for p in C[y]))
    print('pieces used:', used)
    for mt in matchings(used):
        ok = True; plan = []
        for i, j in mt:
            g = pairframe(i, j)
            ys = [y for y in served if C[y].get(i) or C[y].get(j)]
            if len(ys) == 1 and all(contains(span[Qf[ys[0]]], span[pf[q]]) for q in (i, j)):   # R2b: single-Y pair meets at the Y's own Q (7-port rule)
                plan.append((i, j, None, ys[0], ys[0])); continue
            if g is None or len(ys) != 2 or not all(contains(span[Qf[y]], span[g]) for y in ys): ok = False; break
            k, l = ys; det = (C[k].get(i, 0) * C[l].get(j, 0) - C[k].get(j, 0) * C[l].get(i, 0)) % P
            if det == 0: ok = False; break
            plan.append((i, j, g, k, l))
        if ok and sum(len(C[y]) for y in served) == sum(1 for pl_ in plan for y in set(pl_[3:5]) for p in pl_[0:2] if C[y].get(p)): sols.append(plan)
    print('R2: matchings satisfying the pair rule:', len(sols))
    if not sols: print('RESULT: R2 fails'); return
    for si, plan in enumerate(sols):
        print('  matching', si, [(i, j, g, k, l) for i, j, g, k, l in plan])
    # ---- build for each matching / orientation until legal
    for si, plan in enumerate(sols):
        kk = len(served) if a.k is None else a.k
        mem_ = list(M)[:2 * len(plan)]
        for orient in itertools.combinations(mem_, kk):
            orient = set(orient)
            res = build(w, w0, prog, plan, C, M, F0, F9, Qf, pf, pt, served, dim, tl, orient, a.readtime)
            if res is None: continue
            w3, msg = res
            print('  matching', si, 'orient', orient, msg)
            if w3 is not None:
                if not a.allsub or not os.path.exists(a.out):
                    with gzip.open(a.out, 'wt') as fh: json.dump(w3, fh)
                if not a.allsub: return
    print('RESULT: no orientation realises')

def _minsupport(vecs, b, order):
    """solve b = sum x_c vecs[c] (columns), backward-eliminate columns in `order` (indices) while still solvable. -> dict c->x or None"""
    keep = list(range(len(vecs)))
    def sol(ks):
        if not ks: return {} if not b.any() else None
        x = rp.solve(np.array([vecs[k] for k in ks]).T % P, b)
        return None if x is None else {k: int(v) for k, v in zip(ks, x)}
    s = sol(keep)
    if s is None: return None
    for c in order:
        if c in keep and c != 0:
            k2 = [k for k in keep if k != c]; s2 = sol(k2)
            if s2 is not None: keep, s = k2, s2
    return {k: v for k, v in s.items() if v}

def compact_tail(w2, prog3, M, F9m, pcs, nsample=7):
    """Event-economical member cleanup (the swarm's form): ONE batch of member-member / piece-to-member ADDs (+ SCALE) placed at the time the members and the
    pieces are co-present at F9 (before the pieces are themselves cleaned), instead of one ADD per residual coordinate at the very end.
    Solves, member by member (greedy order), T[m] = a*row[m] + sum x_c row[c], c in pieces + unprocessed members + finished members (their unit rows).
    returns list of (t, event) or None."""
    if len(set(F9m[m] for m in M)) != 1: return None
    F9 = F9m[M[0]]; tl = rp.timelines(w2, prog3); Tn = len(prog3)
    def present(r, t): return any(a < t <= b and f == F9 for a, b, f in tl[r])
    bps = sorted(set(x for r in list(M) + list(pcs) for a, b, f in tl[r] if f == F9 for x in (a + 1, b)))
    cand = [t for t in bps if t <= Tn and all(present(r, t) for r in list(M) + list(pcs))]
    if not cand: return None
    if len(cand) > nsample: cand = [cand[round(i * (len(cand) - 1) / (nsample - 1))] for i in range(nsample)]
    snap = {t: list(M) + list(pcs) for t in cand if t < Tn}
    A_end, sn = rp.replay(w2, prog3, snap=snap)
    Tg = rp.target(w2); best = None
    for t in cand:
        rows = sn[t] if t < Tn else {r: A_end[r].copy() for r in list(M) + list(pcs)}
        plan = _seq_plan(rows, M, pcs, Tg, F9)
        if plan is not None and (best is None or len(plan) < len(best[1])): best = (t, plan)
    if best is None: return None
    TAILINFO['t'] = best[0]; TAILINFO['n'] = len(best[1]); TAILINFO['cand'] = len(cand)
    return [(best[0], e) for e in best[1]]

def _seq_plan(rows, M, pcs, Tg, F9):
    cur = {m: rows[m].copy() % P for m in M}; rem = list(M); done = []; ops = []
    while rem:
        bestm = None
        for m in rem:
            names = [('a', m)] + [('p', p) for p in pcs] + [('m', x) for x in rem if x != m] + [('d', x) for x in done]
            vecs = [cur[m]] + [rows[p] % P for p in pcs] + [cur[x] for x in rem if x != m] + [Tg[x] % P for x in done]
            b = Tg[m] % P
            for order in (list(range(len(names) - 1, 0, -1)), list(range(1, len(names)))):
                s = _minsupport(vecs, b, order)
                if s is None: break
                if 0 not in s: continue
                fr = {k: rp.ratrec(v) for k, v in s.items()}
                if not all(rp.dyadic(f) for f in fr.values()): continue
                cost = len(s) - (1 if s[0] == 1 else 0) + (0 if s[0] == 1 else 1) - 1 + (1 if s[0] != 1 else 0)
                cost = sum(1 for k in s if k != 0) + (1 if rp.ratrec(s[0]) != 1 else 0)
                if bestm is None or cost < bestm[0]: bestm = (cost, m, names, s, fr)
        if bestm is None: return None
        _, m, names, s, fr = bestm
        if fr[0] != 1: ops.append(['SCALE', m, rp.fstr(fr[0]), F9])
        for k in sorted(s):
            if k: ops.append(['ADD', m, names[k][1], rp.fstr(fr[k]), F9])
        cur[m] = Tg[m] % P; rem.remove(m); done.append(m)
    return ops

def build(w, w0, prog, plan, C, M, F0, F9, Qf, pf, pt, served, dim, tl, orient, readtime):
    R = rp.nreg(w); n = len(w['initial'])
    w = json.loads(json.dumps(w)); ins = []   # (t, event)
    mem = list(M); slot = {}; prox = []; newb = []
    for pi, (i, j, g, k, l) in enumerate(plan):
        ma, mb = mem[2 * pi], mem[2 * pi + 1]
        # coefficients (exact mod P): m_a = pi_i + beta pi_j -> Y_k (delta1); m_b = gamma m_a + pi_j... closed form
        if g is None:
            for m_ in (ma, mb): (prox if m_ in orient else newb).append(m_)
            t_i, t_j = (pt[i][1], pt[j][1]) if readtime == 'last' else (pt[i][0] + 1, pt[j][0] + 1)
            tY = next(t0 for t0, t1, f in tl[k] if f == Qf[k])
            for m, q, tq in ((ma, i, t_i), (mb, j, t_j)):
                fr_ = rp.ratrec(C[k][q])
                if not rp.dyadic(fr_): return (None, 'single nondyadic')
                ins.append((tq, ['MOVE', m, w['initial'][m], pf[q], False])); ins.append((tq, ['ADD', m, q, '1', pf[q]]))
                td = max(tq, tY + 1)
                ins.append((td, ['MOVE', m, pf[q], Qf[k], False])); ins.append((td, ['ADD', k, m, rp.fstr(fr_), Qf[k]]))
                ins.append((td, ['MOVE', m, Qf[k], F9[m], False]))
            continue
        x, y_, u, v = C[k].get(i, 0), C[k].get(j, 0), C[l].get(i, 0), C[l].get(j, 0)
        if x == 0: k, l = l, k; x, y_, u, v = u, v, x, y_
        if x == 0: return None
        beta = y_ * inv(x) % P; d1 = x; d2 = (v - u * beta) % P
        if d2 == 0: return None
        gamma = u * inv(d2) % P
        co = [rp.ratrec(c) for c in (beta, gamma, d1, d2)]
        if not all(c is None or c == 0 or rp.dyadic(c) for c in co) or any(c is None for c in co): return (None, 'butterfly nondyadic %s' % (co,))
        beta_, gamma_, d1_, d2_ = co
        for m_ in (ma, mb): (prox if m_ in orient else newb).append(m_)
        t_i, t_j = (pt[i][1], pt[j][1]) if readtime == 'last' else (pt[i][0] + 1, pt[j][0] + 1)
        ins.append((t_i, ['MOVE', ma, w['initial'][ma], pf[i], False])); ins.append((t_i, ['ADD', ma, i, '1', pf[i]]))
        ins.append((t_j, ['MOVE', mb, w['initial'][mb], pf[j], False])); ins.append((t_j, ['ADD', mb, j, '1', pf[j]]))
        t7 = max(t_i, t_j)
        ins.append((t7, ['MOVE', ma, pf[i], g, False])); ins.append((t7, ['MOVE', mb, pf[j], g, False]))
        if beta_: ins.append((t7, ['ADD', ma, mb, rp.fstr(beta_), g]))
        if gamma_: ins.append((t7, ['ADD', mb, ma, rp.fstr(gamma_), g]))
        for m, yy, dd in ((ma, k, d1_), (mb, l, d2_)):
            tY = next(t0 for t0, t1, f in tl[yy] if f == Qf[yy])
            td = max(t7, tY + 1)
            ins.append((td, ['MOVE', m, g, Qf[yy], False])); ins.append((td, ['ADD', yy, m, rp.fstr(dd), Qf[yy]]))
            ins.append((td, ['MOVE', m, Qf[yy], F9[m], False]))
    # proxies: initial F0, MOVE F0 -> G at t=0 (after the F0 pre-reads, solved below)
    G = w['initial'][M[0]]
    for m in prox: w['initial'][m] = F0
    tG = min(t for t, e in ins)
    pre = [(tG, ['MOVE', m, F0, G, False]) for m in prox]
    # the members' MOVE events above used w['initial'] = G as the source frame: fix for proxies (they are at G after the t=0 move)
    prog2 = rp.insert(prog, pre + ins); w2 = dict(w); w2['program'] = prog2
    # ---- junk (linear): Y += x * p at t=0 (before the proxy MOVE), p += y * h at G right after the proxy MOVEs
    clique = served + [r for r in EXTRA if r not in served]
    idxM = next(t for t, e in enumerate(prog2) if e[0] == 'MOVE' and e[1] in prox and e[3] == G)
    tl2 = rp.timelines(w2, prog2)
    yend = {yy: next(t1 for t0, t1, f in tl2[yy] if f == F0) for yy in clique}
    # pre-read slots: t=0, after every read OF the pre-reader while it sits at F0 (its adjoint changes there), and the last F0 moment
    slots = {}
    for yy in clique:
        lim = min(yend[yy], idxM); ss = {0, lim}
        for t, e in enumerate(prog2[:lim]):
            if e[0] in ('ADD', 'COPY') and e[2] == yy: ss.add(t + 1)
        slots[yy] = sorted(ss)
    J = [(t, yy, p, F0) for p in prox for yy in clique for t in slots[yy]]
    gl = idxM + len(prox)
    J += [(gl, p, h, G) for p in prox for h in newb] + [(gl, h1, h2, G) for h1 in newb for h2 in newb if h1 != h2]
    snapt = sorted(set(t for t, _, _, _ in J))
    A_end, sn = rp.replay(w2, prog2, snap={t: [s for tt, d, s, f in J if tt == t] for t in snapt})
    Dj = (rp.target(w2) - A_end) % P
    xs = {}
    for s in sorted(set(s for _, _, s, _ in J)):
        rows_ = [(ii, q) for ii, q in enumerate(J) if q[2] == s]
        cols = [colvec(prog2, t, d, R) for ii, (t, d, s_, f) in rows_]
        keep_rows = [r for r in range(R) if r not in set(M)]   # member rows are cleaned at the end at F9 (R5); every other row must match
        x = rp.solve((np.array(cols).T % P)[keep_rows], Dj[keep_rows, s] % P)
        if x is None: return (None, 'junk unsolvable for source %d' % s)
        for (ii, _), v in zip(rows_, x): xs[ii] = int(v)
    jins = []
    for ii, (t, d, s, f) in enumerate(J):
        if not xs.get(ii): continue
        fr = rp.ratrec(xs[ii])
        if not rp.dyadic(fr): return (None, 'junk nondyadic')
        jins.append((t, ['ADD', d, s, rp.fstr(fr), f]))
    prog3 = rp.insert(prog2, jins); w2['program'] = prog3
    if COMPACT[0]:
        pcs = sorted(set(x for pl_ in plan for x in pl_[0:2]))
        try: ct = compact_tail(w2, prog3, list(M), F9, pcs)
        except Exception as ex: ct = None; print('  compact_tail error %r' % ex)
        if ct is not None: prog3 = rp.insert(prog3, ct); w2['program'] = prog3; print('  compact tail: %d events at t=%d (%d candidate times)' % (TAILINFO['n'], TAILINFO['t'], TAILINFO['cand']))
        else: print('  compact tail: not found, falling back to the per-coordinate cleanup')
    # ---- cleanup at the end against unit rows (iterative)
    A, _ = rp.replay(w2, prog3); Tg = rp.target(w2)
    zero_ok = set(r for r in range(n) if dim[w['final'][r]] == 9)
    app = []
    CL = list(M) + [r for r in range(n) if r not in set(M) and r in zero_ok and ((A[r] - Tg[r]) % P).any()]
    for it in range(20):
        changed = False
        for m in CL:
            diff = (A[m] - Tg[m]) % P
            for s in np.flatnonzero(diff):
                s = int(s)
                if s == m or s not in zero_ok or not ((A[s] - Tg[s]) % P == 0).all(): continue
                c = (-diff[s]) % P; fr = rp.ratrec(c)
                if not rp.dyadic(fr): return (None, 'cleanup nondyadic')
                ev = ['ADD', m, s, rp.fstr(fr), w['final'][m]]; app.append(ev); rp.step(A, ev); changed = True
        if not changed: break
    # member-member block: ADD-only Gaussian elimination at F9 (all members co-present there at the end)
    Ms = list(M); idx = {m: i for i, m in enumerate(Ms)}
    other_left = [m for m in Ms if any(int(c) not in idx for c in np.flatnonzero((A[m] - Tg[m]) % P))]
    if not other_left:
        def add(dst, src, c):
            fr = rp.ratrec(c % P)
            if fr is None or not rp.dyadic(fr): return False
            ev = ['ADD', dst, src, rp.fstr(fr), F9[dst]]; app.append(ev); rp.step(A, ev); return True
        for j, mj in enumerate(Ms):
            if A[mj, mj] % P != 1:
                src = next((mi for mi in Ms if mi != mj and A[mi, mj] % P), None)
                if src is None: return (None, 'cleanup: pivot %d unreachable' % mj)
                c = (1 - A[mj, mj]) * inv(A[src, mj]) % P
                if not add(mj, src, c): return (None, 'cleanup nondyadic pivot')
            for mi in Ms:
                if mi != mj and A[mi, mj] % P:
                    if not add(mi, mj, -A[mi, mj] % P): return (None, 'cleanup nondyadic elim')
    left = [(m, [int(c) for c in np.flatnonzero((A[m] - Tg[m]) % P)][:6]) for m in M if ((A[m] - Tg[m]) % P).any()]
    if left: return (None, 'cleanup leaves %s' % left[:3])
    w2['program'] = prog3 + app
    S.C.activate(w2); rep = S.C.legal.check(w2)
    if not rep['ok'] and FREEB[0] and all(v[1] in ('Fixed operation bound', 'Public inventory bound') for v in rep['violations']):
        rep = dict(rep); rep['ok'] = True; print('bounds-only violations (convention literals, --freebounds):', rep['violations'][:2])
    if not rep['ok']:
        Af, _ = rp.replay(w2, w2['program']); Dd = (rp.target(w2) - Af) % P
        rows_bad = [(r, [int(c) for c in np.flatnonzero(Dd[r])][:8]) for r in range(R) if Dd[r].any()][:4]
        return (None, 'ILLEGAL %s | residual rows/cols %s' % (rep['violations'][:1], rows_bad))
    k = S.C.X.kappa(*S.C.X.invoice(rep)); S.C.activate(w0); k0 = S.C.X.kappa(*S.C.X.invoice(S.C.legal.check(w0)))
    return (w2, 'RESULT: LEGAL kappa %.14f base %.14f diff %+.3e events %d base %d (member events %d)' % (k, k0, k - k0, len(w2['program']), len(w0['program']),
            sum(1 for e in w2['program'] if any(x in set(M) for x in S.regfields(e)))))

if __name__ == '__main__': main()
