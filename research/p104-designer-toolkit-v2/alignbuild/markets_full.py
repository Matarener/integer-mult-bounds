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
DBG = [False]
ENDERS = []
RELAY = {}
MU = {}
WIN = {}
CLS = {}
HUBS = set()
OPT_HUBRELAX = [False]
OPT_GATE = [False]
OPT_F9 = [False]
OWNEDG = []
OPT_NORELAYJ = [False]
NTRIAL = [4000]
MAXOR = [0]
GATE_SET = set()
R9 = set()
GATE_T = {}
COMPACT = [True]
TAILINFO = {}

def _minsupport(vecs, b, order):
    """solve b = sum x_c vecs[c] (columns), backward-eliminate columns in `order` (indices) while still solvable. -> dict c->x or None
    REBUILDSPEED (exact; the removal DECISIONS are the same, the final solve is the original rp.solve): Ax=b depends only on the row space of [A|b] and
    rref is unique, so everything runs on the reduced rows E of the full system (<= m+1 rows).  Removal test on a basic form (pivot columns = unit
    columns, free columns the rest): column c can go iff b stays in the span without it, i.e. c is free; or c is the pivot of row i and either some
    kept free column j has E[i,j] != 0 (exchange the pivot to j) or E[i,b] == 0 (the row dies).  One vectorised pivot per exchange instead of a full
    rref per test."""
    m = len(vecs)
    if m == 0: return {} if not b.any() else None
    Mx = np.concatenate([np.array(vecs).T % P, (b % P).reshape(-1, 1)], axis=1)
    E, piv = rp.rref(Mx)
    if m in piv: return None
    E = E.copy(); pivrow = {c: i for i, c in enumerate(piv)}
    ispiv = np.zeros(m, dtype=bool); ispiv[list(piv)] = True; inkeep = np.ones(m, dtype=bool)
    for c in order:
        if c == 0 or not inkeep[c]: continue
        if c not in pivrow: inkeep[c] = False; continue
        i = pivrow[c]
        cand = np.flatnonzero((E[i, :m] != 0) & inkeep & ~ispiv)
        if len(cand):
            j = int(cand[0]); E[i] = E[i] * pow(int(E[i, j]), P - 2, P) % P
            cc = E[:, j].copy(); cc[i] = 0; nzr = np.flatnonzero(cc)
            if len(nzr): E[nzr] = (E[nzr] - (cc[nzr, None] * E[i][None, :]) % P) % P
            del pivrow[c]; pivrow[j] = i; ispiv[c] = False; ispiv[j] = True; inkeep[c] = False
        elif E[i, m] % P == 0:
            E[i] = 0; del pivrow[c]; ispiv[c] = False; inkeep[c] = False
    ks = [int(k) for k in np.flatnonzero(inkeep)]
    x = rp.solve(E[:, ks], E[:, m]) if ks else np.zeros(0, dtype=np.int64)
    return {k: int(v) for k, v in zip(ks, x) if v}

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
    if not cand: print('  DBG compact: no co-present time; bps', len(bps), 'M', M, 'pcs', pcs); return None
    if len(cand) > nsample: cand = [cand[round(i * (len(cand) - 1) / (nsample - 1))] for i in range(nsample)]
    ext = {t: [r for r in range(len(tl)) if r not in set(M) and r not in set(pcs) and present(r, t)] for t in cand}
    snap = {t: list(M) + list(pcs) + ext[t] for t in cand if t < Tn}
    A_end, sn = rp.replay(w2, prog3, snap=snap)
    Tg = rp.target(w2); best = None
    for t in cand:
        rows = sn[t] if t < Tn else {r: A_end[r].copy() for r in list(M) + list(pcs) + ext[t]}
        plan = _seq_plan(rows, M, pcs, Tg, F9)
        if plan is None and ext[t]:
            ex = [r for r in ext[t] if rows[r].any()]; print('  compact: retry with %d extra F9-present rows' % len(ex))
            plan = _seq_plan(rows, M, list(pcs) + ex, Tg, F9)
        if plan is not None and (best is None or len(plan) < len(best[1])): best = (t, plan)
    if best is None: print('  DBG compact: plan None at', cand, 'M', M, 'pcs', pcs); return None
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


def inv(a): return pow(int(a) % P, P - 2, P)
def frac(a):
    fr = rp.ratrec(int(a) % P)
    return fr

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('word'); ap.add_argument('G', type=int); ap.add_argument('out')
    ap.add_argument('--readtime', default='last'); ap.add_argument('--orient', default='auto'); ap.add_argument('--k', type=int); ap.add_argument('--allsub', action='store_true'); ap.add_argument('--nochan', action='store_true'); ap.add_argument('--core', action='store_true'); ap.add_argument('--dbg', action='store_true'); ap.add_argument('--proxies', default=''); ap.add_argument('--maxsel', type=int, default=300); ap.add_argument('--wins', default=''); ap.add_argument('--hubrelax', action='store_true'); ap.add_argument('--gate', action='store_true'); ap.add_argument('--f9relax', action='store_true'); ap.add_argument('--norelayj', action='store_true'); ap.add_argument('--gaterelays', default=''); ap.add_argument('--ntrial', type=int, default=4000); ap.add_argument('--maxorient', type=int, default=0)
    ap.add_argument('--legacy', action='store_true'); a = ap.parse_args(); COMPACT[0] = not a.legacy; DBG[0] = a.dbg; OPT_HUBRELAX[0] = a.hubrelax; OPT_GATE[0] = a.gate; OPT_F9[0] = a.f9relax; OPT_NORELAYJ[0] = a.norelayj; NTRIAL[0] = a.ntrial; MAXOR[0] = a.maxorient; GATE_SET.update(int(x) for x in a.gaterelays.split(',') if x)
    path, w0 = S.load_word(a.word); w = json.loads(json.dumps(w0)); n = len(w['initial']); R = rp.nreg(w)
    fr = w['frames']; dim = [len(b) for b in fr]; span = [rref(b) for b in fr]; G = a.G; SG = span[G]
    live = w['live']; Ys = [r + 112 for r in live]; Yset = set(Ys); F0 = w['initial'][Ys[0]]
    role = S.roles_of(w); prog0 = w['program']; tl0 = rp.timelines(w)
    contains = lambda big, small: rref(list(big) + list(small)) == big
    fidx = collections.defaultdict(list)
    for i, s in enumerate(span): fidx[s].append(i)
    M = sorted(r for r in range(n) if role(r) == 'H' and any(f == G for _, _, f in tl0[r]))
    Mall = list(M)
    if a.core:   # MKT4 rule O1: market members = H registers with a market-form chain (dims within {0,5,6,7,8,9}, ends at F9); foreign visitors (couriers, dead ends) are residual skeleton
        okd = {0, 5, 6, 7, 8, 9}
        M = [r for r in M if {dim[f] for _, _, f in tl0[r]} <= okd and dim[w['final'][r]] == 9]
    Mset = set(M)
    R9.clear(); R9.update(r for r in range(n) if dim[w['final'][r]] == 9 and r not in Mset)
    ENDERS[:] = [r for r in Mall if r not in Mset and w['final'][r] == G and a.core]   # MKT4 rule O1: dead-end (0,5) proxies end at G pure: PURE SOURCES for the junk solve
    # owned lifetimes born AT G are members too (junk scratch): strip their events (INIT..CLEAR)
    ownedG = []; act = {}; dropi = set()
    if a.core:
        for t, e in enumerate(prog0):
            if e[0] == 'INIT' and e[1] >= n and e[2] == G: act[e[1]] = t; ownedG.append(e[1])
            if act:
                if any(x in act for x in S.regfields(e)) and e[0] not in ('INIT', 'CLEAR'): dropi.add(t)
                if e[0] == 'CLEAR' and e[1] in act: del act[e[1]]
    # ---- strip every member event
    prog = [e for t, e in enumerate(prog0) if t not in dropi and not any(x in Mset for x in S.regfields(e)) and not (e[0] in ('ADD', 'COPY') and any(x in ENDERS for x in S.regfields(e)))]
    OWNEDG[:] = ownedG
    if a.core: print('core members', M, '| foreign visitors kept', [r for r in Mall if r not in Mset], '| enders (pure sources)', ENDERS, '| owned lifetimes at G stripped', ownedG, '(%d events)' % len(dropi))
    F9 = {m: w['final'][m] for m in M}
    for m in M: w['initial'][m] = G
    w['program'] = prog
    tl = rp.timelines(w, prog)
    # pieces: non-member, non-Y public registers with a stop at a d6 frame containing G
    pieces = []
    for r in range(n):
        if r in Mset or r in Yset: continue
        if a.core and any(f == G for _, _, f in tl0[r]): continue   # a foreign visitor at G is a relay/ender, not a piece
        for t0, t1, f in tl[r]:
            if dim[f] == 6 and contains(span[f], SG): pieces.append((r, f, t0, min(t1, len(prog) - 1)))
    print('G', G, 'members', M, 'pieces', [(p, f) for p, f, _, _ in pieces])
    A_end, _ = rp.replay(w, prog)
    Tgt = rp.target(w); D = (Tgt - A_end) % P
    bad = [r for r in range(R) if D[r].any() and r not in Yset and r not in Mset]
    print('rows with residual (non-Y):', bad[:30], '| owned among them:', [r for r in bad if r >= n])
    bad = [r for r in bad if r < n]
    D0 = D.copy()
    # ---- MKT4 rule E1 (root channel): a dangling owned relay c (INIT at a non-Y dim-8 frame, readers still in the word, content written only by members) is a served target;
    #      its need x_c is read off the residual: D[r] = a_c[r] * x_c on the rows downstream of c (a_c = forward map of a unit in c)
    chans = []
    if not a.nochan:
        def consume(c, tI, frame, wend, kind):
            nonlocal D
            rd = [t for t, e in enumerate(prog) if e[0] in ('ADD', 'COPY') and e[2] == c and e[1] != c and t > tI]
            if not rd: return
            av = colvec(prog, tI + 1, c, R)
            rows = [r for r in range(R) if av[r] % P and r not in Mset]
            cnt = collections.Counter(); keep = {}
            for r in rows:
                v = D[r] * inv(av[r]) % P; k_ = v.tobytes(); cnt[k_] += 1; keep[k_] = v
            if not cnt: return
            kbest, nb = cnt.most_common(1)[0]; xc = keep[kbest]
            if not xc.any() or nb < 2: return
            D = (D - np.outer(av, xc)) % P
            if kind == 'hub': HUBS.add(c)
            chans.append(dict(c=c, a=av, x=xc, readers=[prog[t][1] for t in rd], nrows=len(rows), nagree=nb, frame=frame, win=(tI, min(wend, rd[0])), kind=kind))
            print('CHANNEL', kind, c, 'frame', frame, 'win', (tI, min(wend, rd[0])), 'direct readers', sorted(set(prog[t][1] for t in rd))[:6], '| rows downstream', len(rows), 'agree', nb)
        for c in range(n, R):   # (i) dangling owned relay: INIT at a dim-8 frame, written only by members
            if not tl[c] or dim[tl[c][0][2]] != 8: continue
            if any(e[0] in ('ADD', 'COPY') and e[1] == c and e[2] != c for e in prog): continue
            consume(c, tl[c][0][0], tl[c][0][2], tl[c][0][1], 'owned')
        for c in [r for r in range(n) if D[r].any() and r not in Yset and r not in Mset]:   # (ii) public non-Y hub with residual and a dim-8 stop
            for t0_, t1_, f_ in tl[c]:
                if dim[f_] == 8:
                    consume(c, t0_, f_, t1_, 'hub'); break
    bad2 = [r for r in range(R) if D[r].any() and r not in Yset and r not in Mset]
    served = [y for y in Ys if D[y].any()]
    direct = sorted(set(r for ch in chans for r in ch['readers'] + ([ch['c']] if ch['kind'] == 'hub' else []) if r < n and w['initial'][r] == F0))
    EXTRA[:] = [r for r in direct if r not in served and (r in Yset or r in bad or any(ch['c'] == r for ch in chans))] if chans else [r for r in bad if w['initial'][r] == F0]
    print('served Ys (nonzero residual):', served, '| other rows with residual:', bad2[:8], '| clique extras (channel direct readers):', EXTRA)
    capT = min(ch['win'][1] for ch in chans) if chans else None
    # ---- MKT4 rule E2 (hub relay at G): an owned relay that sits at G after a channel hub's content was copied into it is a READABLE source for the members still at G
    #      (its row = alpha * hub row; alpha from a unit forward-simulated hub -> relay).  Row used by R1 = stripped row + alpha * x_hub (the delivery the members make into the hub).
    RELAY.clear(); RELAY_PRE = {}
    def fwd_alpha(tI, t_to, src, dst):
        v = {src: 1}
        for e in prog[tI:t_to]:
            o = e[0]
            if o in ('INIT', 'CLEAR'): v.pop(e[1], None); continue
            if o == 'MOVE': continue
            if o == 'SCALE':
                if e[1] in v: v[e[1]] = v[e[1]] * qm(e[2]) % P
                continue
            d_, s_, c_ = e[1], e[2], qm(e[3])
            if o == 'COPY':
                if s_ in v: v[d_] = v[s_] * c_ % P
                else: v.pop(d_, None)
            elif s_ in v: v[d_] = (v.get(d_, 0) + v[s_] * c_) % P
        return v.get(dst, 0)
    if a.core and chans:
        for c in range(R):   # owned relays AND foreign public visitors (couriers) that sit at G: their rows are readable by the members still at G
            if c in ownedG or c in Mset or c in ENDERS or c in Yset: continue
            for t0_, t1_, f_ in tl[c]:
                if f_ == G and t1_ > t0_ + 1: RELAY_PRE[c] = (t0_, min(t1_, len(prog) - 1))
    def tread(f, t0, t1):
        if a.readtime != 'last': return t0 + 1
        return min(t1, capT) if (capT is not None and t0 + 1 <= capT) else t1   # MKT4: a piece feeding a channel is read inside the channel's lifetime
    TR = {(p, f): tread(f, t0, t1) for p, f, t0, t1 in pieces}
    tr = {}
    for (p, f), t in TR.items(): tr.setdefault(t, []).append(p)
    for c, (t0_, t1_) in RELAY_PRE.items(): tr.setdefault(t1_, []).append(c)
    FR = (0.0, 0.25, 0.5, 0.75, 1.0)
    if a.dbg:
        for (p, f, t0, t1) in pieces:
            for fq in FR: tr.setdefault(t0 + 1 + int(fq * (min(t1, capT if capT else t1) - t0 - 1)), []).append(p)
    A_end, snaps = rp.replay(w, prog, snap=tr)
    prow = {(p, f): snaps[t][p] for (p, f), t in TR.items()}
    for c, (t0_, t1_) in RELAY_PRE.items():
        row = snaps[t1_][c] % P
        if not row.any(): continue
        vec = row.copy(); alpha = 0
        for ch in chans:
            al = fwd_alpha(ch['win'][0] + 1, t1_, ch['c'], c)
            if al: vec = (vec + al * ch['x']) % P; alpha = al
        prow[(c, -c)] = vec; TR[(c, -c)] = t1_; RELAY[c] = dict(t=t1_, t0=t0_, alpha=alpha)
        print('RELAY (E2) owned', c, 'at G, stay', (t0_, t1_), 'alpha', frac(alpha) if alpha else 0)
    if a.dbg:
        nJ_ = np.ones(R, dtype=bool); nJ_[M] = False
        tgd = [(ch['c'], ch['x']) for ch in chans] + [(y, D[y]) for y in served]
        for fq in FR:
            cols = []; 
            for (p, f, t0, t1) in pieces: cols.append(snaps[t0 + 1 + int(fq * (min(t1, capT if capT else t1) - t0 - 1))][p][nJ_])
            Ad = np.array(cols).T % P
            print('  dbg frac', fq, [(t_, rp.solve(Ad, v[nJ_]) is not None) for t_, v in tgd])
        print('  dbg piece intervals', [(p, f, t0, t1) for p, f, t0, t1 in pieces])
    nonJ = np.ones(R, dtype=bool); nonJ[M] = False; nonJ[ENDERS] = False
    pl = sorted(prow)                                   # (register, d6 frame)
    cls = collections.defaultdict(list)
    for (p, f) in pl: cls[f].append(p)
    cf = sorted(cls)
    Aeq = np.array([prow[q][nonJ] for q in pl]).T % P
    colof = {q: i_ for i_, q in enumerate(pl)}
    cfp = [f for f in cf if f >= 0]; cfr = [f for f in cf if f < 0]
    def options(b, kmax=4):
        """B1' (the unit is the d6 FRAME: a member passes each d6 frame once and may read any registers there). all minimum-support solutions of Aeq x = b
        over <= kmax d6 frames plus optional hub relays (read at G), returned as {frame: {register: coef}} (relay f = -c)"""
        for kk_ in range(1, kmax + 1):
            for nr in range(0, len(cfr) + 1):
                res = []
                for cmb in itertools.combinations(cfp, kk_):
                    for rl in itertools.combinations(cfr, nr):
                        fs = list(cmb) + list(rl)
                        cols = [colof[(p, f)] for f in fs for p in cls[f]]
                        x = rp.solve(Aeq[:, cols], b)
                        if x is None: continue
                        d = {}
                        for (c_, v) in zip(cols, x):
                            if int(v): p, f = pl[c_]; d.setdefault(f, {})[p] = int(v)
                        if len(d) == kk_ + nr: res.append(d)
                if res: return res
        return None
    tg = [(ch['c'], ch['x']) for ch in chans] + [(y, D[y]) for y in served]
    for t_, vec in tg:
        xf = rp.solve(Aeq, vec[nonJ]); print('  dbg target', t_, 'in full piece span:', xf is not None, '| nonzero x coords', int(np.count_nonzero(vec[nonJ])))
    OPT = {}
    for t_, vec in tg:
        OPT[t_] = options(vec[nonJ])
        if OPT[t_] is None: print('RESULT: R1 fails, target', t_, 'not in the span of 4 d6-frame classes'); return
        print('  target', t_, 'min frame-support', len(OPT[t_][0]), 'options', len(OPT[t_]), 'e.g.', {f: {p: str(frac(v)) for p, v in dd.items()} for f, dd in OPT[t_][0].items()})
    pf = {}; pt = {}
    Qf = {y: w['final'][y] for y in served}
    for ch in chans: Qf[ch['c']] = ch['frame']; WIN[ch['c']] = ch['win']
    served = served + [ch['c'] for ch in chans]
    def attempt(C):
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
        if sols: print('R2: pieces', used, 'matchings satisfying the pair rule:', len(sols))
        if not sols: return False
        for si, plan in enumerate(sols):
            print('  matching', si, [(i, j, g, k, l) for i, j, g, k, l in plan])
        # ---- build for each matching / orientation until legal
        for si, plan in enumerate(sols):
            kk = len(served) - len(ENDERS) if a.k is None else a.k
            mem_ = list(M)[:2 * len(plan)]
            for oi_, orient in enumerate(itertools.combinations(mem_, kk)):
                if MAXOR[0] and oi_ >= MAXOR[0]: break
                orient = set(orient)
                if a.proxies and orient != set(int(x) for x in a.proxies.split(',')): continue
                res = build(w, w0, prog, plan, C, M, F0, F9, Qf, pf, pt, served, dim, tl, orient, a.readtime)
                if res is None: print('  matching', si, 'orient', sorted(orient), 'None', flush=True); continue
                w3, msg = res
                print('  matching', si, 'orient', orient, msg)
                if w3 is not None:
                    if not a.allsub or not os.path.exists(a.out):
                        with gzip.open(a.out, 'wt') as fh: json.dump(w3, fh)
                    if not a.allsub: return True
        return False


    order = [t_ for t_, _ in tg]
    def selections(i=0, cur=None, un=frozenset(), dirs=None):
        cur = {} if cur is None else cur; dirs = {} if dirs is None else dirs
        if i == len(order): yield dict(cur), dict(dirs); return
        for o in OPT[order[i]]:
            u2 = un | set(f for f in o if f >= 0)
            if len(u2) > len(M): continue
            d2 = dict(dirs); ok = True
            for f, dd in o.items():
                if f not in d2: d2[f] = dd; continue
                ref = d2[f]
                if set(ref) != set(dd): ok = False; break
                p0 = min(ref)
                if any((dd[p] * ref[p0] - ref[p] * dd[p0]) % P for p in ref): ok = False; break   # class direction must be common to all targets using the frame
            if not ok: continue
            cur[order[i]] = o
            yield from selections(i + 1, cur, u2, d2)
        cur.pop(order[i], None)
    nsel = 0
    for Cf, dirs in selections():
        nsel += 1
        if nsel > a.maxsel: break
        # class-level pseudo pieces: key = lead register; reads = [(register, ratio, read time)]
        pf.clear(); pt.clear(); CLS.clear(); C = {}
        MU.clear()
        for f, ref in dirs.items():
            if f < 0: continue
            p0 = min(ref); CLS[p0] = [(p, ref[p] * inv(ref[p0]) % P, TR[(p, f)]) for p in sorted(ref)]
            pf[p0] = f; tt_ = [TR[(p, f)] for p in ref]; pt[p0] = (min(tt_), max(tt_))
        for t_, o in Cf.items():
            C[t_] = {}
            for f, dd in o.items():
                if f < 0: MU.setdefault(t_, {})[-f] = dd[-f] % P; continue
                C[t_][min(dirs[f])] = dd[min(dirs[f])] % P
        if attempt(C): return
    print('RESULT: no selection/matching/orientation realises (tried %d selections)' % nsel)

def realize_parallel(Cg, regs, G, scratch=None):
    """new_rows = (I + C) old_rows realised at one time as ADD events (+ scratch scaling events when det != 1).
    Gauss-Jordan on U = I + C with dyadic coefficients (random elimination orders); a pivot that cannot be set to 1 by adding a later row is scaled to 1 through the owned scratch
    o (COPY o <- r; ADD r <- o -1; ADD r <- o f), so any invertible dyadic U is realisable with ONE owned scratch lifetime at G.
    ops O_1..O_m reduce U to I, so U = O_1^-1 ... O_m^-1 and the events are O_m^-1 first."""
    from fractions import Fraction as Fq
    import random as rnd
    n_ = len(regs); ix = {r: i for i, r in enumerate(regs)}
    U0 = [[Fq(int(i == j)) for j in range(n_)] for i in range(n_)]
    for (d, s_), v in Cg.items():
        fr = rp.ratrec(v)
        if fr is None: return None
        U0[ix[d]][ix[s_]] += fr
    isd = lambda c: (c.denominator & (c.denominator - 1)) == 0 and abs(c) + 1 < 2 ** 16 and abs(c.numerator) < 2 ** 16
    for trial in range(80):
        order = list(range(n_))
        if trial: rnd.Random(trial).shuffle(order)
        U = [row[:] for row in U0]; ops = []; ok = True
        for k, j in enumerate(order):
            if U[j][j] != 1:
                cand = [i for i in order[k + 1:] if U[i][j] != 0]
                if cand:
                    i = cand[0]; c = (1 - U[j][j]) / U[i][j]
                    for q in range(n_): U[j][q] += c * U[i][q]
                    ops.append(('add', j, i, c))
                elif U[j][j] != 0:   # pivot row already isolated: scale it to 1 (needs the scratch)
                    f = U[j][j]
                    for q in range(n_): U[j][q] /= f
                    ops.append(('scale', j, None, f))
                else: ok = False; break
            for i in range(n_):
                if i != j and U[i][j] != 0:
                    c = -U[i][j]
                    for q in range(n_): U[i][q] += c * U[j][q]
                    ops.append(('add', i, j, c))
        if not ok: continue
        if any(U[i][j] != int(i == j) for i in range(n_) for j in range(n_)): continue
        evs = []
        for (kind, i, j, c) in reversed(ops):
            if kind == 'add':
                c2 = -c
                if not isd(c2): ok = False; break
                evs.append(['ADD', regs[i], regs[j], rp.fstr(c2), G])
            else:   # inverse of dividing the row by f is multiplying by f
                if scratch is None or not isd(c): ok = False; break
                evs += [['COPY', scratch, regs[i], '1', G], ['ADD', regs[i], scratch, '-1', G], ['ADD', regs[i], scratch, rp.fstr(c), G]]
        if ok: return evs
    return None

def build(w, w0, prog, plan, C, M, F0, F9, Qf, pf, pt, served, dim, tl, orient, readtime):
    R = rp.nreg(w); n = len(w['initial'])
    w = json.loads(json.dumps(w)); ins = []   # (t, event)
    mem = list(M); slot = {}; prox = []; newb = []
    def reads(m, i):
        """member m enters the d6 frame pf[i] at the first read and reads every register of the class (ratio coefficients, each at its own read time)"""
        tmin = min(t for _, _, t in CLS[i]); ins.append((tmin, ['MOVE', m, w['initial'][m], pf[i], False]))
        for p, r_, t in sorted(CLS[i], key=lambda z: z[2]):
            fr_ = rp.ratrec(r_)
            if fr_ is None or not (fr_ == 1 or rp.dyadic(fr_)): return None
            ins.append((t, ['ADD', m, p, rp.fstr(fr_), pf[i]]))
        return pt[i][1]
    Gf = w['initial'][M[0]]
    asg = {}
    for c_ in RELAY:
        for tg_, mu_ in MU.items():
            if c_ not in mu_: continue
            for pi_, (i_, j_, g_, k_, l_) in enumerate(plan):
                if g_ is None or tg_ not in (k_, l_) or k_ in WIN or l_ in WIN: continue
                if min(min(t for _, _, t in CLS[i_]), min(t for _, _, t in CLS[j_])) > RELAY[c_]['t']: asg[(c_, tg_)] = pi_; break
            else: return (None, 'relay %d: no eligible pair (members still at G) for target %d' % (c_, tg_))
    for pi, (i, j, g, k, l) in enumerate(plan):
        ma, mb = mem[2 * pi], mem[2 * pi + 1]
        # coefficients (exact mod P): m_a = pi_i + beta pi_j -> Y_k (delta1); m_b = gamma m_a + pi_j... closed form
        if g is None:
            for m_ in (ma, mb): (prox if m_ in orient else newb).append(m_)
            t_i, t_j = pt[i][1], pt[j][1]
            tY = next(t0 for t0, t1, f in tl[k] if f == Qf[k])
            for m, q, tq in ((ma, i, t_i), (mb, j, t_j)):
                fr_ = rp.ratrec(C[k][q])
                if not rp.dyadic(fr_): return (None, 'single nondyadic')
                if reads(m, q) is None: return (None, 'class ratio nondyadic')
                td = max(tq, tY + 1)
                if k in WIN and td > WIN[k][1]: return (None, 'channel window missed (single) td %d >= %d' % (td, WIN[k][1]))
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
        for c_ in RELAY:
            muk = MU.get(k, {}).get(c_, 0) if asg.get((c_, k)) == pi else 0
            mul = MU.get(l, {}).get(c_, 0) if asg.get((c_, l)) == pi else 0
            if muk or mul:
                uu = muk * inv(d1) % P; rb = (mul * inv(d2) - gamma * uu) % P; ra = (uu - beta * rb) % P
                for m_, r_ in ((ma, ra), (mb, rb)):
                    if r_:
                        fr2 = rp.ratrec(r_)
                        if fr2 is None or not rp.dyadic(fr2): return (None, 'relay coefficient nondyadic')
                        ins.append((RELAY[c_]['t'], ['ADD', m_, c_, rp.fstr(fr2), Gf]))
        for m_ in (ma, mb): (prox if m_ in orient else newb).append(m_)
        t_i, t_j = pt[i][1], pt[j][1]
        if reads(ma, i) is None or reads(mb, j) is None: return (None, 'class ratio nondyadic')
        t7 = max(t_i, t_j)
        ins.append((t7, ['MOVE', ma, pf[i], g, False])); ins.append((t7, ['MOVE', mb, pf[j], g, False]))
        if beta_: ins.append((t7, ['ADD', ma, mb, rp.fstr(beta_), g]))
        if gamma_: ins.append((t7, ['ADD', mb, ma, rp.fstr(gamma_), g]))
        for m, yy, dd in ((ma, k, d1_), (mb, l, d2_)):
            tY = next(t0 for t0, t1, f in tl[yy] if f == Qf[yy])
            td = max(t7, tY + 1)
            if yy in WIN and td > WIN[yy][1]: return (None, 'channel window missed td %d >= %d (t7 %d)' % (td, WIN[yy][1], t7))
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
    clique = [y for y in served if y < n] + [r for r in EXTRA if r not in served]
    idxM = next(t for t, e in enumerate(prog2) if e[0] == 'MOVE' and e[1] in prox and e[3] == G)
    gl = idxM + len(prox)
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
    if ENDERS:   # O1: ender e = pure source: F0 pre-reads by the clique Ys and by the F0-born proxies; at G it cleans the members before they leave
        for p in prox:
            lim = min(next(t1 for t0, t1, f in tl2[p] if f == F0), idxM); ss = {0, lim}
            for t, e in enumerate(prog2[:lim]):
                if e[0] in ('ADD', 'COPY') and e[2] == p: ss.add(t + 1)
            slots[p] = sorted(ss)
        for e_ in ENDERS:
            J += [(t, d, e_, F0) for d in clique + list(prox) for t in slots[d]]
    gl = idxM + len(prox)
    J += [(gl, p, h, G) for p in prox for h in newb] + [(gl, h1, h2, G) for h1 in newb for h2 in newb if h1 != h2]
    J += [(gl, m, e_, G) for e_ in ENDERS for m in list(prox) + list(newb)]
    if RELAY and ENDERS:   # E2': the owned relay at G is a free-cleanup SINK (an owned lifetime needs no unit end row): it may load from the ender and from the members still at G; the ender is also cleaned off those members then
        dep = {m: next(i for i, e in enumerate(prog2) if e[0] == 'MOVE' and e[1] == m and e[2] == G) for m in list(prox) + list(newb)}
        for c_ in RELAY:
            t_out = next(i for i, e in enumerate(prog2) if e[0] == 'MOVE' and e[1] == c_ and e[2] == G)
            late = [m for m in dep if dep[m] > t_out]
            if OPT_GATE[0] and GATE_SET and c_ not in GATE_SET: continue
            if OPT_GATE[0]:   # MKTO2 O2: relay = junk GATE.  the owned scratch is loaded (before any member is modified) with a combination u of PURE newborn / ender coordinates and added to the relay at its stay
                t_clr = next((i for i, e in enumerate(prog2) if e[0] == 'CLEAR' and e[1] == OWNEDG[0]), t_out)
                t_g = min(t_out, t_clr)   # the gate must read the scratch before its CLEAR
                GATE_T[c_] = t_g
                J += [(t_g, c_, s_, G) for s_ in list(ENDERS) + list(newb)]
            elif not OPT_NORELAYJ[0]:
                J += [(t_out, c_, s_, G) for s_ in list(ENDERS) + late]
            J += [(t_out, m, e_, G) for e_ in ENDERS for m in late]
    Sg = set(list(prox) + list(newb) + list(ENDERS))
    # ---- the G-slot is ONE PARALLEL update (I + C).  C must be unitriangular in some order sigma (dest earlier than source) so that it is realised by pure-source transvections
    #      (a cyclic C needs the owned scratch to keep pure copies: ALIGNLAW-style swap).  sigma by the backward greedy: the register placed last is the one whose column is solvable with all others as dests.
    A_end0, _ = rp.replay(w2, prog2); Dj0 = (rp.target(w2) - A_end0) % P
    cc0 = {}
    for ii, (t, d, s_, f) in enumerate(J): cc0[ii] = colvec(prog2, t, d, R)
    def col_ok(s_, allowed):
        rows_ = [ii for ii, q in enumerate(J) if q[2] == s_ and not (q[0] == gl and q[3] == G and q[1] in Sg and q[1] not in allowed)]
        kr = [r for r in range(R) if (r not in set(M) or s_ in ENDERS) and not ((OPT_HUBRELAX[0] and r in HUBS or OPT_F9[0] and r in R9) and s_ not in ENDERS)]
        if not rows_: return not Dj0[kr, s_].any()
        return rp.solve((np.array([cc0[ii] for ii in rows_]).T % P)[kr], Dj0[kr, s_] % P) is not None
    rem = [r for r in Sg if r not in ENDERS]; back = list(ENDERS); cyc = False
    # MKTO2: exhaustive subset DP instead of the first-fit backward greedy (first-fit placed the F0-born proxies LAST, which forbids them as dests of the newborn columns)
    memo = {}
    def fplace(remset):
        if not remset: return []
        if remset in memo: return memo[remset]
        res = None
        for r in sorted(remset, key=lambda z: (z in newb, z)):
            if col_ok(r, set(remset) - {r}):
                sub = fplace(remset - {r})
                if sub is not None: res = [r] + sub; break
        memo[remset] = res
        return res
    order_back = fplace(frozenset(rem))
    if order_back is None:
        cyc = True
        while rem:
            pick = next((r for r in rem if col_ok(r, set(rem) - {r})), None)
            if pick is None: break
            rem.remove(pick); back.append(pick)
    else:
        back += order_back; rem = []
        print('    G-slot acyclic order (DP) found: modified last -> first', order_back, flush=True)
    sigma = {r: i for i, r in enumerate(reversed(back))}    # smaller = modified earlier
    if cyc:
        print('    G-slot needs a CYCLIC parallel update for', sorted(rem), '-> searching det(I + C) = 1 solutions (pure copies = the owned scratch)', flush=True)
    else:
        J = [q for q in J if not (q[0] == gl and q[3] == G and q[1] in Sg and q[2] in Sg and not sigma[q[1]] < sigma[q[2]])]
    Jsrc = sorted(set(s_ for _, _, s_, _ in J))
    Yset_dbg = set(served)
    if DBG[0]:
        for c_ in RELAY:
            ev_c = [(i, e) for i, e in enumerate(prog2) if c_ in e[1:3] and isinstance(e[1], int)]
            print('    DBG relay events', ev_c[:14], flush=True)
        for hb in HUBS:
            ev_h = [(i, e[:4]) for i, e in enumerate(prog2) if e[0] in ('ADD', 'COPY') and e[1] == hb and i > 13000]
            ev_r = [(i, e[:4]) for i, e in enumerate(prog2) if e[0] in ('ADD', 'COPY') and e[2] == hb and i > 13000]
            print('    DBG hub', hb, 'writes', ev_h[:10], 'reads', ev_r[:10], flush=True)
            vv = np.zeros(R, dtype=np.int64); vv[133] = 1; seen_ = {}
            for tt_, e_ in enumerate(prog2[13440:], 13440):
                o_ = e_[0]
                if o_ == 'MOVE': continue
                if o_ in ('INIT', 'CLEAR'): vv[e_[1]] = 0; continue
                if o_ == 'SCALE': vv[e_[1]] = vv[e_[1]] * qm(e_[2]) % P
                elif o_ == 'COPY': vv[e_[1]] = vv[e_[2]] * qm(e_[3]) % P
                else: vv[e_[1]] = (vv[e_[1]] + vv[e_[2]] * qm(e_[3])) % P
                if vv[e_[1]] and e_[1] not in seen_: seen_[e_[1]] = (tt_, e_[:4], str(frac(vv[e_[1]])))
                if tt_ > 13470: break
            print('    DBG hubtrace', sorted(seen_.items(), key=lambda z: z[1][0])[:14], flush=True)
            for (d_, t_) in ((773, 13448), (133, 13446), (133, 13440), (709, 13454)):
                vh = colvec(prog2, t_, d_, R); rr = np.flatnonzero(vh % P)
                print('    DBG probe', d_, 't', t_, 'nnz', len(rr), 'special', {int(r): str(frac(vh[r])) for r in rr if int(r) in (709, 733, 773, 133, 149, 159, 222, 695, 697)}, 'nonY', [int(r) for r in rr if not (112 <= r < 240)][:12], flush=True)
            for d_ in (699, 701, 695, 767):
                vh = colvec(prog2, gl, d_, R); rr = np.flatnonzero(vh % P)
                print('    DBG dest', d_, 'response nnz', len(rr), 'special', {int(r): str(frac(vh[r])) for r in rr if int(r) in (709, 733, 773, 133, 149, 159, 222)}, 'nonY', [int(r) for r in rr if not (112 <= r < 240)][:12], flush=True)
        kr_ = [r for r in range(R) if r not in set(M) and not (OPT_HUBRELAX[0] and r in HUBS or OPT_F9[0] and r in R9)]
        for tag, sel in (('slotA members', [ii for ii, q in enumerate(J) if q[0] == gl and q[3] == G and q[1] in Sg and q[2] in newb]), ('relay dests', [ii for ii, q in enumerate(J) if q[1] in RELAY and q[2] in newb])):
            vs = {}
            for ii in sel: vs.setdefault((J[ii][0], J[ii][1]), cc0[ii])
            if not vs: continue
            Vm = np.array([v[kr_] for v in vs.values()]).T % P
            rws = [r for r in range(len(kr_)) if Vm[r].any()]
            cnt_ = collections.Counter((dim[w['final'][kr_[r]]] if kr_[r] < n else -1) for r in rws)
            print('    DBG', tag, 'response rows by final dim', dict(cnt_), 'Ys', [kr_[r] for r in rws if kr_[r] in Yset_dbg][:5], flush=True)
            print('    DBG', tag, 'dests', [k for k in vs], 'response rows', [kr_[r] for r in rws][:20], 'rank', len(rp.rref(Vm)[1]), flush=True)
        selU = [ii for ii, q in enumerate(J) if q[3] == G and ((q[0] == gl and q[1] in Sg and q[2] in newb) or (q[1] in RELAY and q[2] in newb))]
        VU = {}
        for ii in selU: VU.setdefault((J[ii][0], J[ii][1]), cc0[ii])
        Vu = np.array([v[kr_] for v in VU.values()]).T % P
        print('    DBG union rank', len(rp.rref(Vu)[1]), 'of', len(VU), 'dests; ranks without each', {k: len(rp.rref(np.array([v[kr_] for kk, v in VU.items() if kk != k]).T % P)[1]) for k in VU}, flush=True)
        Dj0n = Dj0[kr_]
        print('    DBG own-column response rows per newborn', {s_: [kr_[r] for r in np.flatnonzero(Dj0[kr_, s_])][:12] for s_ in newb}, flush=True)
    if DBG[0]:
        print('    DBG Sg', sorted(Sg), 'prox', prox, 'newb', newb, 'gl', gl, 'idxM', idxM, 'RELAY', {c: RELAY[c] for c in RELAY}, flush=True)
        for s_ in Jsrc:
            ev_ = [(ii, q[0], q[1], q[3]) for ii, q in enumerate(J) if q[2] == s_]
            print('    DBG src', s_, 'n events', len(ev_), 'G-slot dests', sorted(q[2-1] for q in J if q[2] == s_ and q[0] == gl and q[3] == G), 'other', [(q[0], q[1], q[3]) for q in J if q[2] == s_ and not (q[0] == gl and q[3] == G)][:6], flush=True)
    colcache = {}
    for ii, (t, d, s_, f) in enumerate(J): colcache[ii] = colvec(prog2, t, d, R)
    xs = collections.defaultdict(int)
    keep_all = [r for r in range(R) if r not in set(M)]
    prog3 = prog2
    def mk_jins(xs):
        jins = []; Cg = {}; gate = {}
        for ii, (t, d, s_, f) in enumerate(J):
            if not xs.get(ii): continue
            if t == gl and f == G and d in Sg and s_ in Sg: Cg[(d, s_)] = xs[ii]; continue
            if OPT_GATE[0] and d in GATE_T and t == GATE_T[d]:
                gate.setdefault(d, {})[s_] = xs[ii]; continue
            fr = rp.ratrec(xs[ii])
            if fr is None or not rp.dyadic(fr): return None, 'junk nondyadic'
            jins.append((t, ['ADD', d, s_, rp.fstr(fr), f]))
        if gate:
            scr = OWNEDG[0]
            for c_, gs in gate.items():
                for s_, v in gs.items():
                    fr = rp.ratrec(v)
                    if fr is None or not rp.dyadic(fr): return None, 'gate nondyadic'
                    jins.append((gl, ['ADD', scr, s_, rp.fstr(fr), G]))
                jins.append((GATE_T[c_], ['ADD', c_, scr, '1', G]))
        if Cg:
            if not cyc:
                for (d, s_) in sorted(Cg, key=lambda q: (sigma[q[0]], sigma[q[1]])):   # dests in sigma order: every source is still pure when used
                    fr = rp.ratrec(Cg[(d, s_)])
                    if fr is None or not rp.dyadic(fr): return None, 'junk nondyadic (G slot)'
                    jins.append((gl, ['ADD', d, s_, rp.fstr(fr), G]))
            else:
                seq = realize_parallel(Cg, sorted(Sg), G, None if OPT_GATE[0] else (OWNEDG[0] if OWNEDG else None))
                if seq is None: return None, 'G-slot parallel update not realisable by dyadic transvections'
                jins += [(gl, e_) for e_ in seq]
        return jins, None
    if not cyc:
        for rnd in range(4):
            A_end, _ = rp.replay(w2, prog3); Dj = (rp.target(w2) - A_end) % P
            bad_cols = [c_ for c_ in Jsrc if Dj[[r for r in keep_all if not ((OPT_HUBRELAX[0] and r in HUBS or OPT_F9[0] and r in R9) and c_ not in ENDERS)], c_].any() or (c_ in ENDERS and Dj[:, c_].any())]   # only the columns the junk events can act on; defects of F9 rows are cleaned later
            if not bad_cols: break
            if DBG[0]:
                print('    junk round', rnd, 'bad cols', bad_cols[:12], flush=True)
                for c_ in bad_cols[:3]: print('      col', c_, 'residual rows', [(int(r), str(frac(Dj[r, c_]))) for r in np.flatnonzero(Dj[:, c_])][:10], 'events', [(q[0], q[1], str(frac(xs[ii]))) for ii, q in enumerate(J) if q[2] == c_ and xs.get(ii)][:12], flush=True)
            for s_ in Jsrc:
                rows_ = [ii for ii, q in enumerate(J) if q[2] == s_]
                kr = [r for r in range(R) if (r not in set(M) or s_ in ENDERS) and not ((OPT_HUBRELAX[0] and r in HUBS or OPT_F9[0] and r in R9) and s_ not in ENDERS)]
                x = rp.solve((np.array([colcache[ii] for ii in rows_]).T % P)[kr], Dj[kr, s_] % P)
                if x is None: return (None, 'junk unsolvable for source %d (round %d)' % (s_, rnd))
                for ii, v in zip(rows_, x): xs[ii] = (xs[ii] + int(v)) % P
            jins, err = mk_jins(xs)
            if jins is None: return (None, err)
            prog3 = rp.insert(prog2, jins)
        else:
            return (None, 'junk solve did not converge')
    else:
        import random as _r
        rng = _r.Random(12345); X0 = {}; NUL = {}
        for s_ in Jsrc:
            rows_ = [ii for ii, q in enumerate(J) if q[2] == s_]
            kr = [r for r in range(R) if (r not in set(M) or s_ in ENDERS) and not ((OPT_HUBRELAX[0] and r in HUBS or OPT_F9[0] and r in R9) and s_ not in ENDERS)]
            Aq = (np.array([colcache[ii] for ii in rows_]).T % P)[kr]; bq = Dj0[kr, s_] % P
            E_, piv = rp.rref(np.concatenate([Aq, bq.reshape(-1, 1)], axis=1))
            if len(rows_) in piv: return (None, 'junk unsolvable for source %d' % s_)
            x0 = np.zeros(len(rows_), dtype=np.int64)
            for i_, c_ in enumerate(piv): x0[c_] = E_[i_, len(rows_)]
            free = [c_ for c_ in range(len(rows_)) if c_ not in piv]; nl = []
            for f_ in free:
                v = np.zeros(len(rows_), dtype=np.int64); v[f_] = 1
                for i_, c_ in enumerate(piv): v[c_] = (-E_[i_, f_]) % P
                nl.append(v)
            X0[s_] = (rows_, x0); NUL[s_] = nl
        nfree = sum(len(v) for v in NUL.values())
        print('    cyclic search: free parameters', nfree, 'per source', {k: len(v) for k, v in NUL.items()}, flush=True)
        from fractions import Fraction as Fq
        zc = [1, -1, qm('1/2'), qm('-1/2'), 2, -2]
        found = None; CNT = collections.Counter()
        for trial in range(NTRIAL[0]):
            xs2 = collections.defaultdict(int)
            for s_ in Jsrc:
                rows_, x0 = X0[s_]; x = x0.copy()
                for v in NUL[s_]:
                    if rng.random() < 0.25: x = (x + zc[rng.randrange(len(zc))] % P * v) % P
                for ii, val in zip(rows_, x): xs2[ii] = int(val)
            Cg = {(J[ii][1], J[ii][2]): xs2[ii] for ii in xs2 if xs2[ii] and J[ii][0] == gl and J[ii][3] == G and J[ii][1] in Sg and J[ii][2] in Sg}
            ok = True; Ud = {}
            for k_, v in Cg.items():
                fr = rp.ratrec(v)
                if fr is None or not rp.dyadic(fr): ok = False; break
                Ud[k_] = fr
            if not ok: CNT['nondy'] += 1; continue
            regs_ = sorted(Sg); ix = {r: i for i, r in enumerate(regs_)}; n2 = len(regs_)
            Mx = [[Fq(int(i == j)) for j in range(n2)] for i in range(n2)]
            for (d, s_), fr in Ud.items(): Mx[ix[d]][ix[s_]] += fr
            det = Fq(1)
            for c_ in range(n2):
                pv = next((r for r in range(c_, n2) if Mx[r][c_] != 0), None)
                if pv is None: det = Fq(0); break
                if pv != c_: Mx[c_], Mx[pv] = Mx[pv], Mx[c_]; det = -det
                det *= Mx[c_][c_]
                for r in range(c_ + 1, n2):
                    f_ = Mx[r][c_] / Mx[c_][c_]
                    for q in range(c_, n2): Mx[r][q] -= f_ * Mx[c_][q]
            CNT['det0' if det == 0 else 'det%s' % det] += 1
            if det == 0: continue
            jins, err = mk_jins(xs2)
            if jins is None: CNT['real_fail'] += 1; continue
            found = (xs2, jins); break
        print('    cyclic stats', dict(CNT), flush=True)
        if found is None: return (None, 'cyclic G-slot: no det=1 dyadic solution found in the sampled null space (nfree %d)' % nfree)
        xs = found[0]; prog3 = rp.insert(prog2, found[1])
        print('    cyclic search: invertible solution found at trial', trial, 'det', det, 'scratch events', sum(1 for e_ in found[1] if e_[1][0] == 'COPY'), flush=True)
    w2['program'] = prog3
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
    Ms = list(M) + [r for r in CL if r not in set(M) and ((A[r] - Tg[r]) % P).any()]; idx = {m: i for i, m in enumerate(Ms)}   # block = members + F9 rows still defective (e.g. a hub)
    other_left = [m for m in Ms if any(int(c) not in idx for c in np.flatnonzero((A[m] - Tg[m]) % P))]
    if not other_left:
        import random as _rnd
        A0 = A.copy(); best = None
        for trial in range(40):
            order = list(Ms)
            if trial: _rnd.Random(trial).shuffle(order)
            A[:] = A0; app2 = []; ok = True
            def add(dst, src, c):
                fr = rp.ratrec(c % P)
                if fr is None or not rp.dyadic(fr): return False
                ev = ['ADD', dst, src, rp.fstr(fr), w['final'][dst]]; app2.append(ev); rp.step(A, ev); return True
            for jj, mj in enumerate(order):
                if A[mj, mj] % P != 1:
                    later = [mi for mi in order[jj + 1:] if A[mi, mj] % P]
                    if not later: ok = False; break
                    if not any(add(mj, src, (1 - A[mj, mj]) * inv(A[src, mj]) % P) for src in later[:1]): ok = False; break
                for mi in order:
                    if mi != mj and A[mi, mj] % P:
                        if not add(mi, mj, -A[mi, mj] % P): ok = False; break
                if not ok: break
            if ok and not any(((A[m] - Tg[m]) % P).any() for m in Ms): best = app2; break
        if best is not None: app.extend(best)
    left = [(m, [int(c) for c in np.flatnonzero((A[m] - Tg[m]) % P)][:6]) for m in Ms if ((A[m] - Tg[m]) % P).any()]
    if left: return (None, 'cleanup leaves %s' % left[:3])
    w2['program'] = prog3 + app
    S.C.activate(w2); rep = S.C.legal.check(w2)
    if not rep['ok']:
        Af, _ = rp.replay(w2, w2['program']); Dd = (rp.target(w2) - Af) % P
        rows_bad = [(r, [int(c) for c in np.flatnonzero(Dd[r])][:8]) for r in range(R) if Dd[r].any()][:4]
        return (None, 'ILLEGAL %s | residual rows/cols %s' % (rep['violations'][:1], rows_bad))
    k = S.C.X.kappa(*S.C.X.invoice(rep)); S.C.activate(w0); k0 = S.C.X.kappa(*S.C.X.invoice(S.C.legal.check(w0)))
    return (w2, 'RESULT: LEGAL kappa %.14f base %.14f diff %+.3e events %d base %d (member events %d)' % (k, k0, k - k0, len(w2['program']), len(w0['program']),
            sum(1 for e in w2['program'] if any(x in set(M) for x in S.regfields(e)))))

if __name__ == '__main__': main()
