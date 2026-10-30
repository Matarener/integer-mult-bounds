"""YROUTE yb.py: D3-style rebuild of the ROUTING side on #6030 from the routing rules alone.
STRIP (for the chosen sites): every direct read ADD Y += c*s of a site, and every Y stop left with no event (the dedicated low stops):
  MOVE Y a->f + MOVE Y f->b  become  MOVE Y a->b.
REBUILD (rules only; the swarm's frames, times, Ys and coefficients of the stripped reads are not read back):
  Y-set  : the Ys with a nonzero residual row after the strip (target law).
  pool   : the stripped sources (pieces shared by >= 2 octets).
  RX     : Y_j reads s at s's EXIT frame w.r.t. q_j = the last frame of s's chain inside Q_j = q_j^perp (rule R1x).
  stop   : if the exit frame is not on Y_j's chain, Y_j gets a stop there (nesting checked: prev < g < next).
  time   : 'last' convention: the latest moment both are at g (before s leaves g and before Y's next event).
  coeff  : one unknown per feasible (Y_j, s); solved exactly (linear, mod p, rational reconstruction); zero-coefficient reads and
           their stops are removed.
Then legal.check + exact kappa vs base; chains compared with the base word.
usage: yb.py WORD OUT.json.gz --pair P,O | --sites s:y,...  [--alt s:y:frame ...] [--pool all]
  --alt: override the rule frame for (s, y) (beat-it probes only)."""
import sys, gzip, json, pickle, argparse, collections
import numpy as np
from fractions import Fraction
import os
HERE = os.path.dirname(os.path.abspath(__file__))   # alignbuild/: self-contained copy (no lane-dir imports)
sys.path[:0] = [HERE]
W = os.path.dirname(HERE)   # repo root (only used for default paths)
import rp
from rp import P
from life import rref, perp, dot, tax
S = rp.S
Yd = HERE + '/data/'

def colvec(prog, t0, d, R):
    v = np.zeros(R, dtype=np.int64); v[d] = 1
    for e in prog[t0:]:
        o = e[0]
        if o == 'MOVE': continue
        if o in ('INIT', 'CLEAR'): v[e[1]] = 0; continue
        if o == 'SCALE': v[e[1]] = v[e[1]] * rp.qm(e[2]) % P; continue
        a, b = e[1], e[2]
        if o == 'COPY': v[a] = v[b] * rp.qm(e[3]) % P
        else: v[a] = (v[a] + v[b] * rp.qm(e[3])) % P
    return v

def freplay(prog, R, snap):
    A = np.eye(R); out = {}
    for t, e in enumerate(prog):
        if t in snap: out[t] = A[snap[t]].copy()
        o = e[0]
        if o == 'MOVE': continue
        if o in ('INIT', 'CLEAR'): A[e[1]] = 0; continue
        if o == 'SCALE': A[e[1]] *= float(Fraction(e[2])); continue
        c = float(Fraction(e[3]))
        if o == 'COPY': A[e[1]] = A[e[2]] * c
        else: A[e[1]] += A[e[2]] * c
    return A, out

def fcol(prog, t0, d, R):
    v = np.zeros(R); v[d] = 1
    for e in prog[t0:]:
        o = e[0]
        if o == 'MOVE': continue
        if o in ('INIT', 'CLEAR'): v[e[1]] = 0; continue
        if o == 'SCALE': v[e[1]] *= float(Fraction(e[2])); continue
        c = float(Fraction(e[3]))
        if o == 'COPY': v[e[1]] = v[e[2]] * c
        else: v[e[1]] += v[e[2]] * c
    return v

def gcols(prog, req, R, exact=True):
    """backward pass: {(t, y): column y of the forward map from just AFTER event t to the end} for t -> [y] in req (mod p if exact, else float)"""
    G = np.eye(R, dtype=np.int64) if exact else np.eye(R); out = {}
    for t in range(len(prog) - 1, -1, -1):
        for y in req.get(t, ()): out[(t, y)] = G[:, y].copy()
        e = prog[t]; o = e[0]
        if o == 'MOVE': continue
        if o in ('INIT', 'CLEAR'): G[:, e[1]] = 0; continue
        if o == 'SCALE':
            if exact: G[:, e[1]] = G[:, e[1]] * rp.qm(e[2]) % P
            else: G[:, e[1]] *= float(Fraction(e[2]))
            continue
        a, b = e[1], e[2]
        if exact:
            c = rp.qm(e[3]); G[:, b] = (G[:, b] + c * G[:, a]) % P
        else:
            c = float(Fraction(e[3])); G[:, b] += c * G[:, a]
        if o == 'COPY': G[:, a] = 0
    return out

def chains(w, prog):
    n = len(w['initial']); c = {r: [w['initial'][r]] for r in range(n)}
    for e in prog:
        if e[0] == 'MOVE' and e[1] < n: c[e[1]].append(e[3])
    return c

def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument('word'); ap.add_argument('out')
    ap.add_argument('--pair'); ap.add_argument('--sites'); ap.add_argument('--alt', action='append', default=[]); ap.add_argument('--pool', default='stripped')
    ap.add_argument('--absorb', action='store_true', help='probe mode: solve reads on x columns only, then rp.absorb_pure the junk residual');
    ap.add_argument('--yset', default='resid', choices=['resid', 'all', 'sites']);
    ap.add_argument('--all-sites', action='store_true'); ap.add_argument('--gn-free', action='store_true'); ap.add_argument('--count-only', action='store_true');
    ap.add_argument('--no-write', action='store_true'); ap.add_argument('--time', default='last', choices=['last', 'first', 'settled', 'swarm'])
    a = ap.parse_args(argv)
    path, w = S.load_word(a.word); w = json.loads(json.dumps(w)); n = len(w['initial']); R = rp.nreg(w)
    fr = w['frames']; dim = [len(b) for b in fr]; prog0 = w['program']
    Y1 = pickle.load(open(Yd + 'y1.pkl', 'rb')); Y4 = pickle.load(open(Yd + 'y4.pkl', 'rb')); ro = Y1['ro']
    ch0 = chains(w, prog0)
    q = {y: perp(rref(fr[ch0[y][-1]]))[0] for y in ro}
    inside = lambda f, v: all(dot(v, b) == 0 for b in fr[f])
    sub = lambda x, y: x != y and rref(list(fr[x]) + list(fr[y])) == rref(list(fr[y]))
    # ---------------- sites
    sites = set()   # (s, y, f)
    if a.pair:
        p, o = map(int, a.pair.split(','))
        for r in Y4:
            if r['p'] != p: continue
            for (y, f, yd, tr) in r['det']:
                if ro[y] == o: sites.add((r['s'], y, f))
    if a.all_sites:
        for r in Y4:
            for (y, f, yd, tr) in r['det']: sites.add((r['s'], y, f))
    if a.sites:
        want = {tuple(map(int, x.split(':'))) for x in a.sites.split(',')}
        for r in Y4:
            for (y, f, yd, tr) in r['det']:
                if (r['s'], y) in want: sites.add((r['s'], y, f))
    srcs = sorted({s for s, _, _ in sites}); dests = sorted({y for _, y, _ in sites})
    bigl = bool(set(srcs) & set(dests))
    if bigl: print('BILINEAR: stripped sources that are also destinations', sorted(set(srcs) & set(dests)), '-> Newton rounds')
    print('sites', sorted(sites)); print('sources', srcs, 'dest Ys', dests)
    # ---------------- strip
    kill = set()
    for t, e in enumerate(prog0):
        if e[0] == 'ADD' and (e[2], e[1], e[4]) in sites: kill.add(t)
    stripped_reads = [prog0[t] for t in sorted(kill)]
    prog1 = [(['__MARK__', e[1], e[2]] if t in kill else e) for t, e in enumerate(prog0)]
    # remove Y stops left empty
    def ev_at(prog, y, f):
        cur = w['initial'][y]; k = 0
        for e in prog:
            if e[0] == 'MOVE' and e[1] == y: cur = e[3]; continue
            if e[0] in ('MOVE', '__MARK__'): continue
            if y in S.regfields(e) and cur == f: k += 1
        return k
    dropped_stops = []
    for (s, y, f) in sorted(sites):
        if (y, f) in dropped_stops or f not in chains(w, prog1)[y]: continue
        if ev_at(prog1, y, f) == 0 and f not in (w['initial'][y], w['final'][y]):
            ti = next(t for t, e in enumerate(prog1) if e[0] == 'MOVE' and e[1] == y and e[3] == f)
            to = next(t for t, e in enumerate(prog1) if e[0] == 'MOVE' and e[1] == y and e[2] == f)
            prog1[to] = ['MOVE', y, prog1[ti][2], prog1[to][3], prog1[to][4]]
            del prog1[ti]; dropped_stops.append((y, f))
    swpos = {}; k = 0
    for e in prog1:
        if e[0] == '__MARK__': swpos[(e[1], e[2])] = k
        else: k += 1
    prog1 = [e for e in prog1 if e[0] != '__MARK__']
    print('stripped %d read events, %d Y stops %s' % (len(kill), len(dropped_stops), [(y, f, dim[f]) for y, f in dropped_stops]))
    w1 = dict(w); w1['program'] = prog1
    A1, _ = rp.replay(w1, prog1); Tgt = rp.target(w1); D = (Tgt - A1) % P
    resid_rows = [r for r in range(R) if D[r].any()]
    print('residual rows (rule Y-set):', resid_rows)
    Yset = [r for r in resid_rows if r in ro] if a.yset == 'resid' else (sorted(ro) if a.yset == 'all' else dests)
    assert set(Yset) <= set(ro), resid_rows
    pool = srcs if a.pool == 'stripped' else sorted({r['s'] for r in Y4})
    alt = {}
    for x in a.alt:
        s_, y_, g_ = map(int, x.split(':')); alt[(s_, y_)] = g_
    # ---------------- rule placement
    ch1 = chains(w1, prog1); tl = rp.timelines(w1, prog1)
    evts = collections.defaultdict(list)
    for t, e in enumerate(prog1):
        if e[0] != 'MOVE':
            for r in S.regfields(e): evts[r].append(t)
    plan = []   # (y, s, g, new_stop, insert index for read, (moveidx to retarget) )
    wr = collections.defaultdict(list)
    for t, e in enumerate(prog1):
        if e[0] in ('ADD', 'COPY', 'SCALE', 'INIT', 'CLEAR'): wr[e[1]].append(t)
    def pick(y, s, first, hi):
        # first = earliest insertion index with both at g; hi = latest (insert before hi)
        if a.time == 'first': return first
        if a.time == 'last': return hi
        if a.time == 'swarm': return swpos.get((y, s), first)
        lw = max([t for t in wr[s] if t < hi] + [-1])          # settled: after s's last write before the window closes
        return max(first, lw + 1)
    for y in Yset:
        for s in pool:
            if a.yset == 'sites' and (s, y) not in {(x[0], x[1]) for x in sites}: continue
            exits = [g for g in ch1[s] if inside(g, q[y])]
            if not exits or dim[exits[-1]] == 0: continue        # dim-0 (F0) reads are pre-loads, not routing reads
            g = alt.get((s, y), exits[-1])          # RX: last frame of s inside Q_j
            sv = [(t0, t1) for (t0, t1, f) in tl[s] if f == g]
            if not sv: continue
            sa, sb = sv[-1]
            if g in ch1[y]:
                yv = [(t0, t1) for (t0, t1, f) in tl[y] if f == g][0]
                lo, hi = max(sa, yv[0]), min(sb, yv[1])
                if lo >= hi: continue
                tt = pick(y, s, lo + 1, hi)
                if tt is not None and tt <= hi: plan.append((y, s, g, False, tt, None))
            else:
                k = None
                for i, (t0, t1, f) in enumerate(tl[y][:-1]):
                    nxt = tl[y][i + 1][2]
                    if sub(f, g) and sub(g, nxt): k = i
                if k is None: continue
                t0, t1, f = tl[y][k]
                lastev = max([t for t in evts[y] if t < t1] + [-1])
                ynext = min([t for t in evts[y] if t > t1] + [len(prog1)])
                mv = max(lastev, sa) + 1     # Y moves into g after its last event at f and after s has arrived at g (Y is idle in between)
                hi = min(sb, ynext)
                if not (lastev < hi and sa < hi and mv <= hi): continue
                tt = pick(y, s, mv, hi)
                if tt is not None and tt <= hi: plan.append((y, s, g, True, tt, (t1, mv, hi)))
    print('rule candidates: %d; at the stripped (Y, s): %s' % (len(plan), [(y, s, g, dim[g], ns, hi) for (y, s, g, ns, hi, m) in plan if (s, y) in {(x[0], x[1]) for x in sites}]))
    if a.count_only: return len(plan)
    # ---------------- build program with placeholder reads (coefficient 0) + stops
    def build(coef, est=None, strs=None):
        """coef None: placeholder reads only (MOVEs do not change values). Otherwise reads with nonzero coefficient + their stops.
        Several new stops of one Y in one gap are chained in dim order; a later stop's reads are delayed (inside their window, where s is
        settled and the Y idle, so values are unchanged) until the Y has left the earlier stop."""
        live_i = [i for i in range(len(plan)) if coef is None or coef[i] != 0]
        tread = {i: plan[i][4] for i in live_i}
        groups = collections.defaultdict(list)
        if coef is not None:
            for i in live_i:
                y, s, g, ns, hi, m = plan[i]
                if ns: groups[(y, m[0])].append(i)
        out_ins = []; delete = set(); key = {i: 1 for i in live_i}
        for (y, t1), ii in groups.items():
            old = prog1[t1]; gs = sorted({plan[i][2] for i in ii}, key=lambda g: dim[g]); delete.add(t1)
            prev = old[2]; tprev = None
            for j, g in enumerate(gs):
                gi = [i for i in ii if plan[i][2] == g]
                if j and not sub(gs[j - 1], g): raise ValueError('new stops not nested')
                mv = min(plan[i][5][1] for i in gi); tin = mv if tprev is None else max(mv, tprev)
                for i in gi:
                    if tread[i] < tin:
                        if tin > plan[i][5][2]: raise ValueError('stop order conflict')
                        tread[i] = tin
                    key[i] = 2 * j + 1
                out_ins.append((tin, 2 * j, ['MOVE', y, prev, g, old[4]]))
                prev = g; tprev = max(tread[i] for i in gi)
            out_ins.append((tprev, 2 * len(gs), ['MOVE', y, prev, old[3], old[4]]))
        for i in live_i:
            y, s, g, ns, hi, m = plan[i]
            c = (strs[i] if strs is not None else (str(int(est[i])) if est is not None else '0')) if coef is None else rp.fstr(coef[i])
            out_ins.append((tread[i], key[i], ['ADD', y, s, c, g]))
        by = collections.defaultdict(list)
        for t, k, e in out_ins: by[t].append((k, e))
        res = []; pos = {}
        for t in range(len(prog1) + 1):
            for k, e in sorted(by.get(t, []), key=lambda ke: ke[0]):
                if e[0] == 'ADD': pos[(e[1], e[2])] = len(res)
                res.append(e)
            if t < len(prog1) and t not in delete: res.append(prog1[t])
        return res, pos
    est = np.zeros(len(plan), dtype=np.int64); x = None
    for rnd in range(8):     # Newton on the exact (mod p) system; one round when no stripped source is itself a destination (linear case)
        progP, pos = build(None, est)
        idx = [pos[(y, s)] for (y, s, g, ns, hi, m) in plan]
        snapreq = collections.defaultdict(list)
        for i, t in enumerate(idx): snapreq[t].append(plan[i][1])
        A0, snaps = rp.replay(w1, progP, snap=snapreq)
        Dc = (Tgt - A0) % P
        if not Dc.any(): x = est; break
        gq = collections.defaultdict(list)
        for i, t in enumerate(idx): gq[t].append(plan[i][0])
        GC = gcols(progP, gq, R, True)
        rows_ = sorted(set(np.nonzero(Dc.any(1))[0]) | {int(r) for i, t in enumerate(idx) for r in np.nonzero(GC[(t, plan[i][0])])[0]})
        if len(plan) <= 300:
            cols = [np.outer(GC[(t, plan[i][0])], snaps[t][plan[i][1]]) % P for i, t in enumerate(idx)]
            cc = sorted(set(np.nonzero(Dc.any(0))[0]) | {r for c in cols for r in np.nonzero(c.any(0))[0]})
            if a.absorb: cc = [c for c in cc if c in set(w['live'])]
            Aeq = np.array([c[np.ix_(rows_, cc)].ravel() for c in cols]).T % P
            b = Dc[np.ix_(rows_, cc)].ravel()
        else:   # random column sketch (exactness is re-verified at the end)
            K = max(4, -(-3 * len(plan) // max(1, len(rows_))))
            Sk = np.random.RandomState(1).randint(0, 1000, size=(R, K)).astype(np.int64)
            Aeq = np.array([np.outer(GC[(t, plan[i][0])][rows_], (snaps[t][plan[i][1]] @ Sk) % P).ravel() % P for i, t in enumerate(idx)]).T % P
            b = ((Dc[rows_] @ Sk) % P).ravel()
            print('sketch: %d rows x %d columns' % (len(rows_), K))
        dx = rp.solve(Aeq, b)
        rank = len(rp.rref(Aeq)[1])
        print('round %d: unknowns %d, rank %d (%s), residual entries %d' % (rnd, len(plan), rank, 'UNIQUE' if rank == len(plan) else 'free vars set to 0', int(np.count_nonzero(Dc))))
        if dx is None: break
        est = (est + dx) % P     # always iterate: a stripped source may depend on a stripped read through Y<-Y work (transitive bilinearity)
    from fractions import Fraction
    coef = None
    if x is not None:
        coef = []
        for v in x:
            fr_ = rp.ratrec(int(v)) if v else Fraction(0)
            if fr_ is None or (fr_ != 0 and not rp.dyadic(fr_)): print('RESULT: nondyadic', v, fr_); return 'NONDYADIC'
            coef.append(fr_)
    else:
        # bilinear coupling (a stripped source is downstream of a stripped read via Y<-Y work): the linearisation at 0 is inconsistent.
        # Gauss-Newton over the reals (float replay), round to dyadics (1/64 grid), then EXACT mod-p verification of the rounded solution.
        cf = np.zeros(len(plan))
        for rnd in range(30 if a.gn_free else 10):
            progF, pos = build(None, None, [repr(float(v)) for v in cf])
            idx = [pos[(y, s)] for (y, s, g, ns, hi, m) in plan]
            AF, snF = freplay(progF, R, {t: plan[i][1] for i, t in enumerate(idx)})
            DF = rp.target(w1).astype(float) - AF
            err = float(np.abs(DF).max()); print('GN round %d: max residual %.3g' % (rnd, err))
            if err < 1e-9 and not (a.gn_free and rnd < 25 and np.abs(cf * 64 - np.round(cf * 64)).max() > 1e-6): break
            if a.gn_free and err < 1e-9: print('   float solution off the 1/64 grid; nonzero coefficients:', int((np.abs(cf) > 1e-6).sum())); cf = np.round(cf * 64) / 64
            gq = collections.defaultdict(list)
            for i, t in enumerate(idx): gq[t].append(plan[i][0])
            GF = gcols(progF, gq, R, False)
            rf = sorted(set(np.nonzero(np.abs(DF).sum(1) > 0)[0]) | {int(r) for i, t in enumerate(idx) for r in np.nonzero(GF[(t, plan[i][0])])[0]})
            K = max(8, -(-3 * len(plan) // max(1, len(rf))))
            Sf = np.random.RandomState(2).standard_normal((R, K))
            J = np.array([np.outer(GF[(t, plan[i][0])][rf], snF[t] @ Sf).ravel() for i, t in enumerate(idx)]).T
            dc = np.linalg.lstsq(J, (DF[rf] @ Sf).ravel(), rcond=None)[0]
            cf = (cf + dc) if (a.gn_free and rnd < 25) else np.round((cf + dc) * 64) / 64
        coef = [Fraction(int(round(v * 64)), 64) for v in cf]
        progX, _ = build(None, None, [str(c) for c in coef])
        Ax, _ = rp.replay(w1, progX)
        if ((Tgt - Ax) % P).any(): print('RESULT: UNSOLVABLE (Gauss-Newton rounded solution not exact)'); return 'UNSOLVABLE'
        print('Gauss-Newton: exact after rounding')
    used = [(plan[i][0], plan[i][1], plan[i][2], dim[plan[i][2]], str(coef[i])) for i in range(len(plan)) if coef[i] != 0]
    print('rule reads (Y, s, frame, dim, coeff):', used)
    try: prog2, _ = build(coef)
    except ValueError as ex: print('RESULT: SCHEDULE', ex); return 'SCHEDULE'
    w2 = dict(w); w2['program'] = prog2
    if a.absorb:
        p3, nins = rp.absorb_pure(w2, prog2)
        print('absorb_pure:', 'inserted %d' % nins if p3 is not None else ('FAILED %s' % (nins,)))
        if p3 is None: print('RESULT: ABSORB-FAILED'); return 'ABSORB-FAILED'
        prog2 = p3; w2['program'] = prog2
    S.C.activate(w2); rep = S.C.legal.check(w2)
    if not rep['ok']: print('RESULT: ILLEGAL', rep['violations'][:4]); return 'ILLEGAL'
    T_, P_ = S.C.X.invoice(rep); kap = S.C.X.kappa(T_, P_)
    S.C.activate(w); rep0 = S.C.legal.check(w); k0 = S.C.X.kappa(*S.C.X.invoice(rep0))
    ch2 = chains(w2, prog2)
    diff = [(r, [dim[f] for f in ch0[r]], [dim[f] for f in ch2[r]]) for r in range(n) if ch0[r] != ch2[r]]
    sw = sorted((e[1], e[2], e[4], dim[e[4]], e[3]) for e in stripped_reads)
    print('swarm reads (Y, s, frame, dim, coeff):', sw)
    print('registers whose chain differs from the base: %d %s' % (len(diff), diff[:8]))
    print('RESULT: LEGAL kappa %.15f (base %.15f, diff %+.3e) events %d (base %d)' % (kap, k0, kap - k0, len(prog2), len(prog0)))
    if not a.no_write:
        with gzip.open(a.out, 'wt') as fh: json.dump(w2, fh)
    match = sorted((y, s_, g, c) for (y, s_, g, d_, c) in used) == sorted((e[1], e[2], e[4], e[3]) for e in stripped_reads)
    return dict(kappa=kap, base=k0, nchdiff=len(diff), match=match, nsites=len(sites), nstops=len(dropped_stops), ncand=len(plan), rank=rank, used=used)

if __name__ == '__main__': main()
