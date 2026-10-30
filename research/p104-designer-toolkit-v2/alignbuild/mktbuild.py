"""ALIGNLAW mktbuild.py: build the market at octet dual G (frame index) FROM THE RULES, on #6030 with that market's junk structure stripped.
RULES used (module docstring sec 4): M1 the reader clique of G = Ys whose q_j lies in O_r; M2 k = |clique| members are proxies: 0-born, F0 -> G directly,
pre-read at F0 by every clique Y (coefficients UNKNOWN); M3 the other members are born at G; their junk is loaded into the proxies at G (coefficients UNKNOWN);
everything else in the word is kept. The unknown coefficients are solved exactly (linear: every inserted event reads a register that is still pure junk),
mod p = 2^31-1, rational reconstruction, then legal.check + exact kappa.  The swarm's own pre-read / load events are DELETED first (not copied).
usage: mktbuild.py WORD G_FRAME OUT.json.gz [--proxies a,b,c] [--clique y1,y2..] [--seed S]
  --proxies: which members are proxies (default: rule choice = the k members with the smallest id among those NOT born at G in the word is NOT used;
             default picks k members at random with --seed, to test that the rule does not depend on the swarm's choice)"""
import sys, os, gzip, json, random, argparse, collections
import numpy as np
import os
HERE = os.path.dirname(os.path.abspath(__file__))   # alignbuild/: self-contained copy (no lane-dir imports)
sys.path[:0] = [HERE]
W = os.path.dirname(HERE)   # repo root (only used for default paths)
import rp
from rp import P, qm
from life import rref, perp, octets
S = rp.S

def colvec(prog, t0, d, R):
    """column d of the forward map from just before event t0 to the end"""
    v = np.zeros(R, dtype=np.int64); v[d] = 1
    for e in prog[t0:]:
        o = e[0]
        if o == 'MOVE': continue
        if o in ('INIT', 'CLEAR'): v[e[1]] = 0; continue
        if o == 'SCALE': v[e[1]] = v[e[1]] * qm(e[2]) % P; continue
        a, b = e[1], e[2]
        if o == 'COPY': v[a] = v[b] * qm(e[3]) % P
        else: v[a] = (v[a] + v[b] * qm(e[3])) % P
    return v

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('word'); ap.add_argument('G', type=int); ap.add_argument('out')
    ap.add_argument('--proxies'); ap.add_argument('--clique'); ap.add_argument('--seed', type=int, default=0); ap.add_argument('--k', type=int); ap.add_argument('--swarm', action='store_true'); ap.add_argument('--allY', action='store_true'); ap.add_argument('--late', action='store_true'); ap.add_argument('--nn', action='store_true')
    a = ap.parse_args()
    path, w = S.load_word(a.word); w = json.loads(json.dumps(w)); n = len(w['initial']); R = rp.nreg(w)
    dim = [len(b) for b in w['frames']]; prog = w['program']; G = a.G; live = w['live']; Ys = [r + 112 for r in live]
    F0 = w['initial'][Ys[0]]
    role = S.roles_of(w)
    tl = rp.timelines(w)
    M = sorted(r for r in range(n) if role(r) == 'H' and any(f == G for _, _, f in tl[r]))
    # M1: clique = Ys with q_j in O_r (O_r = perp(G))
    O = perp(rref(w['frames'][G]))
    def qj(y):
        last = w['final'][y]; return perp(rref(w['frames'][last]))[0]
    clique = [int(x) for x in a.clique.split(',')] if a.clique else [y for y in Ys if rref(list(O) + [qj(y)]) == O]
    k = a.k or len(clique)
    if a.swarm: prox = [m for m in M if w['initial'][m] != G]
    elif a.proxies: prox = [int(x) for x in a.proxies.split(',')]
    else: prox = sorted(random.Random(a.seed).sample(M, k))
    newb = [m for m in M if m not in prox]
    swarm_px = [m for m in M if w['initial'][m] != G]
    print('G', G, 'members', M, 'clique', clique, 'rule proxies', prox, 'newborns', newb, '| swarm proxies', swarm_px)
    Mset = set(M); Yset = set(Ys)
    # strip: F0 reads of members by anyone, member<-member loads at G
    keep = []; dropped = []
    for t, e in enumerate(prog):
        if e[0] in ('ADD', 'COPY') and e[2] in Mset and dim[e[-1]] == 0: dropped.append(e); continue
        if e[0] in ('ADD', 'COPY') and e[1] in Mset and e[2] in Mset and e[-1] == G: dropped.append(e); continue
        keep.append(e)
    # F0 writes into members are not allowed by the rule (proxies unwritten at F0)
    assert not any(e[0] in ('ADD', 'COPY') and e[1] in Mset and dim[e[-1]] == 0 for e in keep), 'member written at F0'
    # re-chain
    prog2 = []
    for e in keep:
        if e[0] == 'MOVE' and e[1] in Mset and e[3] == G and e[1] in newb: continue      # newborn: no F0 -> G move
        prog2.append(e)
    for m in newb: w['initial'][m] = G
    # proxies born at G in the word: start at F0, MOVE F0 -> G inserted at t=0 (they are idle until their first event)
    ins_moves = [['MOVE', m, F0, G, False] for m in prox if w['initial'][m] == G]
    for m in prox: w['initial'][m] = F0
    prog2 = ins_moves + prog2
    # newborns must have no event before they reach G (now: from the start) -- they are born at G, fine; check no F0-frame events remain
    w2 = dict(w); w2['program'] = prog2
    tl2 = rp.timelines(w2, prog2)
    # insertion slots
    first_ev = {}
    for t, e in enumerate(prog2):
        for r in S.regfields(e):
            if r in Mset and r not in first_ev and e[0] != 'MOVE': first_ev[r] = t
    lv_G = {}
    for m in M:
        for t0, t1, f in tl2[m]:
            if f == G: lv_G[m] = (t0, t1)
    INS = []   # (t, d, s, frame)
    yF0 = {y: next(t1 for t0, t1, f in tl2[y] if f == F0) for y in Ys}
    pre_ys = Ys if a.allY else clique
    for p in prox:
        tmv = lv_G[p][0]
        for y in pre_ys:
            INS.append((0, y, p, F0))
            if a.late:
                tl_ = min(tmv, yF0[y])
                if tl_ > 0: INS.append((tl_, y, p, F0))
    tmax = max(lv_G[p][0] for p in prox) + 1
    for p in prox:
        tin, tout = lv_G[p]
        for h in newb:
            t = tin + 1
            assert t <= tout and t <= first_ev.get(h, 10**9) and t <= lv_G[h][1], ('slot', p, h, tin, tout, first_ev.get(h))
            INS.append((t, p, h, G))
    if a.nn:
        for h1 in newb:
            for h2 in newb:
                if h1 != h2 and tmax <= first_ev.get(h2, 10**9): INS.append((tmax, h1, h2, G))
    # linear system per source symbol
    A_end, snaps = rp.replay(w2, prog2, snap={t: [s for (tt, d, s, f) in INS if tt == t] for t in set(x[0] for x in INS)})
    Tgt = rp.target(w2); D = (Tgt - A_end) % P
    srcs = sorted(set(s for _, _, s, _ in INS))
    other = [c for c in range(R) if c not in srcs and D[:, c].any()]
    print('residual columns outside the market sources:', other[:10], len(other))
    xs = {}
    ok = True
    for s in srcs:
        rows_ = [(i, x) for i, x in enumerate(INS) if x[2] == s]
        cols = []
        for i, (t, d, s_, f) in rows_:
            row = snaps[t][s_]
            assert row[s_] == 1 and np.count_nonzero(row) == 1, ('source not pure', s_, t)
            cols.append(colvec(prog2, t, d, R))
        Aeq = np.array(cols).T % P; b = D[:, s] % P
        x = rp.solve(Aeq, b)
        if x is None: print('  source', s, 'UNSOLVABLE (rank rule fails)'); ok = False; continue
        for (i, ins_), v in zip(rows_, x): xs[i] = int(v)
    if not ok: print('RESULT: infeasible'); return
    ins = []; nondy = 0
    for i, (t, d, s, f) in enumerate(INS):
        if xs.get(i, 0) == 0: continue
        fr = rp.ratrec(xs[i])
        if not rp.dyadic(fr): nondy += 1; print('  nondyadic', INS[i], fr); continue
        ins.append((t, ['ADD', d, s, rp.fstr(fr), f]))
    if nondy: print('RESULT: nondyadic solution'); return
    p3 = rp.insert(prog2, ins); w3 = dict(w2); w3['program'] = p3
    S.C.activate(w3); rep = S.C.legal.check(w3)
    print('inserted', len(ins), 'events (swarm had', len(dropped), 'dropped events)')
    if not rep['ok']: print('RESULT: ILLEGAL', rep['violations'][:3]); return
    T_, P_ = S.C.X.invoice(rep); kap = S.C.X.kappa(T_, P_)
    S.C.activate(w); rep0 = S.C.legal.check(w); k0 = S.C.X.kappa(*S.C.X.invoice(rep0))
    print('RESULT: LEGAL kappa %.14f (base %.14f, diff %+.3e) events %d (base %d)' % (kap, k0, kap - k0, len(p3), len(prog)))
    with gzip.open(a.out, 'wt') as fh: json.dump(w3, fh)
if __name__ == '__main__': main()
