"""SIGPIN sigb.py: D3-style rebuild of #6030's SIGNAL events from the signal rules alone (per root).
Roots (one per k; owned lifetimes joined by owned COPY hand-offs and by public relays at a shared frame) come from the word itself.
STRIP (mode):
  reads : every owned->public ADD of the root's lifetimes (except relay reads), [--stops: plus every public stop left empty]
  feeds : every public->owned ADD/COPY into the root's lifetimes (except relay feeds); a COPY into a fresh INIT'd lifetime is rebuilt as an ADD,
          [--fanin: plus the public->public ADDs into a COPY feeder at its H_k stop, the feeder then COPYs nothing: the root reads the partners itself]
REBUILD (rules; no swarm coefficient, time or (register, frame) incidence of a stripped event is read back):
  R-READ  : candidate p += c * L for EVERY public register p co-present with root lifetime L at any frame of L's chain (existing stops;
            with --stops also every public register whose chain has a gap a -> b with a < f < b, idle and co-present: a new stop at f).
  R-FEED  : candidate L += c * p for EVERY public register p co-present with L at its INIT frame / any frame (existing stops).
  time    : settled rule: the event goes after the source's last write in the window (and after the dest's last event, 'late'),
            or right at the start of the window ('early'); --time chooses.
  coeff   : one exact solve mod p (rank printed: UNIQUE iff rank = #candidates), rational reconstruction, dyadic check.
Then legal.check + exact kappa; the rebuilt event multiset is compared with the stripped one.
usage: sigb.py WORD OUT.json.gz --root K --mode reads|feeds [--stops] [--time late|early] [--no-write]"""
import sys, gzip, json, argparse, collections
import numpy as np
from fractions import Fraction
import os
HERE = os.path.dirname(os.path.abspath(__file__))   # alignbuild/: self-contained copy (no lane-dir imports)
sys.path[:0] = [HERE]
W = os.path.dirname(HERE)   # repo root (only used for default paths)
import rp
from rp import P
from life import rref, dot
from routing import gcols
S = rp.S

def lifetimes(w, prog):
    """owned lifetimes: list of dict(reg, t0, t1, stays=[(frame, ta, tb)]) ; lid_at(t, reg) -> index"""
    n = len(w['initial']); L = []; cur = {}
    for t, e in enumerate(prog):
        if e[0] == 'INIT' and e[1] >= n:
            cur[e[1]] = len(L); L.append(dict(reg=e[1], t0=t, t1=len(prog), stays=[[e[2], t, len(prog)]]))
        elif e[0] == 'MOVE' and e[1] >= n:
            l = L[cur[e[1]]]; l['stays'][-1][2] = t; l['stays'].append([e[3], t, len(prog)])
        elif e[0] == 'CLEAR' and e[1] >= n:
            l = L[cur[e[1]]]; l['t1'] = t; l['stays'][-1][2] = t
    return L

def lid_at(L, reg, t):
    for i, l in enumerate(L):
        if l['reg'] == reg and l['t0'] <= t <= l['t1']: return i

def roots_of(w, prog, L):
    """union lifetimes by owned COPY (owned<-owned) and by public relays: public p reads lifetime A then feeds lifetime B at the same frame."""
    n = len(w['initial']); uf = list(range(len(L)))
    def find(x):
        while uf[x] != x: uf[x] = uf[uf[x]]; x = uf[x]
        return x
    lastread = {}   # public p -> (lifetime, frame) of its last owned read
    relays = set()
    for t, e in enumerate(prog):
        if e[0] in ('ADD', 'COPY'):
            d, s = e[1], e[2]
            if d >= n and s >= n: uf[find(lid_at(L, d, t))] = find(lid_at(L, s, t))
            elif s >= n and d < n: lastread[d] = (lid_at(L, s, t), e[4], t)
            elif d >= n and s < n and s in lastread:
                la, fa, ta = lastread[s]; lb = lid_at(L, d, t)
                if fa == e[4] and find(la) != find(lb) and any(st[0] == e[4] for st in L[lb]['stays']):
                    uf[find(lb)] = find(la); relays.add((s, ta, t))
    G = collections.defaultdict(list)
    for i in range(len(L)): G[find(i)].append(i)
    return [sorted(v) for k, v in sorted(G.items())], relays

def stays_pub(w, prog):
    n = len(w['initial']); st = {r: [[w['initial'][r], -1, len(prog)]] for r in range(n)}
    for t, e in enumerate(prog):
        if e[0] == 'MOVE' and e[1] < n: st[e[1]][-1][2] = t; st[e[1]].append([e[3], t, len(prog)])
    return st

def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument('word'); ap.add_argument('out')
    ap.add_argument('--root', type=int, required=True); ap.add_argument('--mode', choices=['reads', 'feeds'], required=True)
    ap.add_argument('--time', default='late', choices=['late', 'early', 'first', 'all']); ap.add_argument('--stops', action='store_true')
    ap.add_argument('--no-write', action='store_true'); ap.add_argument('--freebounds', action='store_true'); ap.add_argument('--regs', default=''); ap.add_argument('--list', action='store_true')
    a = ap.parse_args(argv)
    path, w = S.load_word(a.word); w = json.loads(json.dumps(w)); n = len(w['initial']); R = rp.nreg(w)
    fr = w['frames']; dim = [len(b) for b in fr]; prog0 = w['program']
    L = lifetimes(w, prog0); roots, relays = roots_of(w, prog0, L)
    moving = [g for g in roots if any(len(L[i]['stays']) > 1 for i in g) or any(dim[L[i]['stays'][0][0]] == 8 for i in g)]
    if a.list:
        for k, g in enumerate(roots):
            print(k, [(L[i]['reg'], [(f, dim[f]) for f, _, _ in L[i]['stays']]) for i in g])
        print('relays', sorted(relays)); return
    G = roots[a.root]
    if a.regs: G = [i for i in G if L[i]['reg'] in set(map(int, a.regs.split(',')))]
    Gs = set(G); regs = {L[i]['reg'] for i in G}
    print('root %d lifetimes %s' % (a.root, [(L[i]['reg'], [(f, dim[f]) for f, _, _ in L[i]['stays']]) for i in G]))
    relay_t = {x[1] for x in relays} | {x[2] for x in relays}
    # ---------------- strip
    kill = set(); copyfeed = set()
    for t, e in enumerate(prog0):
        if e[0] not in ('ADD', 'COPY') or t in relay_t: continue
        d, s = e[1], e[2]
        if a.mode == 'reads' and s >= n and d < n and lid_at(L, s, t) in Gs: kill.add(t)
        if a.mode == 'feeds' and d >= n and s < n and lid_at(L, d, t) in Gs:
            kill.add(t)
            if e[0] == 'COPY': copyfeed.add(t)
    stripped = [prog0[t] for t in sorted(kill)]
    prog1 = [e for t, e in enumerate(prog0) if t not in kill]
    # COPY feeds replaced: the lifetime must be zero there (INIT just before, no write in between) -- checked
    st1 = stays_pub(w, prog1)
    dropped = []
    if a.stops:
        # drop public stops left with no event (non-initial, non-final)
        evc = collections.Counter(); cur = {r: w['initial'][r] for r in range(n)}; sidx = {r: 0 for r in range(n)}
        for e in prog1:
            if e[0] == 'MOVE':
                if e[1] < n: sidx[e[1]] += 1
                continue
            for r in S.regfields(e):
                if r < n: evc[(r, sidx[r])] += 1
        killmv = set(); newmv = {}
        for r in range(n):
            ch = st1[r]
            for j in range(1, len(ch) - 1):
                if evc[(r, j)] == 0 and any(ch[j][0] == L[i]['stays'][q][0] for i in G for q in range(len(L[i]['stays']))):
                    # only stops at a frame of this root's chain are signal stops
                    ti, to = ch[j][1], ch[j][2]
                    killmv.add(ti); newmv[to] = ['MOVE', r, ch[j - 1][0], ch[j + 1][0], prog1[to][4]]
                    dropped.append((r, ch[j][0], dim[ch[j][0]]))
        prog1 = [newmv.get(t, e) for t, e in enumerate(prog1) if t not in killmv]
        st1 = stays_pub(w, prog1)
    print('stripped %d events (%d COPY feeds), %d empty stops %s' % (len(kill), len(copyfeed), len(dropped), dropped))
    w1 = dict(w); w1['program'] = prog1
    L1 = lifetimes(w1, prog1)
    # match lifetimes by (reg, order of INIT)
    order0 = collections.defaultdict(list)
    for i, l in enumerate(L): order0[l['reg']].append(i)
    order1 = collections.defaultdict(list)
    for i, l in enumerate(L1): order1[l['reg']].append(i)
    G1 = sorted(order1[L[i]['reg']][order0[L[i]['reg']].index(i)] for i in G)
    writes = collections.defaultdict(list); evts = collections.defaultdict(list)
    for t, e in enumerate(prog1):
        if e[0] in ('ADD', 'COPY', 'SCALE', 'INIT', 'CLEAR'): writes[e[1]].append(t)
        if e[0] != 'MOVE':
            for r in S.regfields(e): evts[r].append(t)
    sub = lambda x, y: x != y and rref(list(fr[x]) + list(fr[y])) == rref(list(fr[y]))
    import math
    def tax(ds):
        D = ds[-1] - ds[0]; return (D * math.log(D) if D > 0 else 0) - sum((y - x) * math.log(y - x) for x, y in zip(ds, ds[1:]) if y > x)
    plan = []    # (dest, src, frame, t_insert, newstop None | (gap index j, MOVE index pb), cost)
    for i in G1:
        l = L1[i]; o = l['reg']
        for (f, ta, tb) in l['stays']:
            for p in range(n):
                ch = st1[p]
                for j, (g, pa, pb) in enumerate(ch):
                    if g != f: continue
                    lo, hi = max(ta, pa) + 1, min(tb, pb)
                    if lo > hi: continue
                    if a.mode == 'reads':
                        lw = max([t for t in writes[o] if t < hi] + [-1])
                        if a.time == 'all':     # every value segment of the window: boundaries at p's events and L's writes
                            ts = sorted({lo} | {t + 1 for t in evts[p] + writes[o] if lo <= t < hi})
                            for t_ in ts: plan.append((p, o, f, t_, None, 0.0))
                            continue
                        t_ = lo if a.time == 'first' else (max(lo, lw + 1) if a.time == 'early' else max(lo, max([t for t in evts[p] if t < hi] + [lw]) + 1))
                        if t_ <= hi: plan.append((p, o, f, t_, None, 0.0))
                    else:
                        lw = max([t for t in writes[p] if t < hi] + [-1])
                        firstread = min([t for t in evts[o] if lo <= t < hi and prog1[t][2] == o and prog1[t][1] != o] + [hi])
                        t_ = max(lo, lw + 1)
                        if t_ <= firstread: plan.append((o, p, f, t_, None, 0.0))
                if not a.stops: continue
                # R-STOP: public p idle in a gap g0 -> g1 with g0 < f < g1 gets a new stop at f if the solve needs it
                for j in range(len(ch) - 1):
                    g0, pa, pb = ch[j]; g1 = ch[j + 1][0]
                    if not (sub(g0, f) and sub(f, g1)): continue
                    lastev = max([t for t in evts[p] if t < pb] + [-1]); nextev = min([t for t in evts[p] if t > pb] + [len(prog1)])
                    lo, hi = max(lastev, ta) + 1, min(nextev, tb)
                    if lo > hi: continue
                    ds = [dim[x[0]] for x in ch]; cost = tax(ds[:j + 1] + [dim[f]] + ds[j + 1:]) - tax(ds)
                    if a.mode == 'reads':
                        lw = max([t for t in writes[o] if t < hi] + [-1]); t_ = max(lo, lw + 1)
                        if t_ <= hi: plan.append((p, o, f, t_, (j, pb), cost))
                    else:
                        firstread = min([t for t in evts[o] if lo <= t < hi and prog1[t][2] == o and prog1[t][1] != o] + [hi])
                        t_ = lo
                        if t_ <= firstread: plan.append((o, p, f, t_, (j, pb), cost))
    plan.sort(key=lambda x: (x[5], x[3]))          # cheapest first: rref's pivot columns = greedy min-cost basis
    print('rule candidates: %d (%d need a new stop)' % (len(plan), sum(1 for x in plan if x[4])))
    def build(coefs, stops=True):
        ins = collections.defaultdict(list); delete = set(); gaps = collections.defaultdict(list)
        for i, (d, s, f, t_, ns, cost) in enumerate(plan):
            c = coefs[i]
            if c == 0: continue
            ins[t_].append((1, ['ADD', d, s, str(c), f]))
            if ns is not None and stops:
                p = d if a.mode == 'reads' else s
                gaps[(p, ns[1])].append((dim[f], f, t_))
        for (p, pb), L_ in gaps.items():
            fs = sorted(set((df, f) for df, f, t_ in L_)); old = prog1[pb]; delete.add(pb)
            if len(fs) > 1: raise ValueError('two new stops in one gap of %d' % p)
            f = fs[0][1]; ts = [t_ for df, f_, t_ in L_]
            ins[min(ts)].append((0, ['MOVE', p, old[2], f, old[4]]))
            ins[max(ts)].append((2, ['MOVE', p, f, old[3], old[4]]))
        out = []; pos = {}
        for t in range(len(prog1) + 1):
            for k, e in sorted(ins.get(t, []), key=lambda x: x[0]):
                if e[0] == 'ADD': pos[(e[1], e[2], t)] = len(out)
                out.append(e)
            if t < len(prog1) and t not in delete: out.append(prog1[t])
        return out, pos
    progP, pos = build(['0'] * len(plan), stops=False)
    idx = [pos[(d, s, t_)] for (d, s, f, t_, ns, cost) in plan]
    snapreq = collections.defaultdict(list)
    for i, t in enumerate(idx): snapreq[t].append(plan[i][1])
    A0, snaps = rp.replay(w1, progP, snap=snapreq)
    Tgt = rp.target(w1); Dc = (Tgt - A0) % P
    print('residual entries after strip: %d' % int(np.count_nonzero(Dc)))
    gq = collections.defaultdict(list)
    for i, t in enumerate(idx): gq[t].append(plan[i][0])
    GC = gcols(progP, gq, R, True)
    cols = [np.outer(GC[(t, plan[i][0])], snaps[t][plan[i][1]]) % P for i, t in enumerate(idx)]
    rows_ = sorted(set(np.nonzero(Dc.any(1))[0]) | {r for c in cols for r in np.nonzero(c.any(1))[0]})
    cc = sorted(set(np.nonzero(Dc.any(0))[0]) | {r for c in cols for r in np.nonzero(c.any(0))[0]})
    Aeq = np.array([c[np.ix_(rows_, cc)].ravel() for c in cols]).T % P if cols else np.zeros((1, 0), dtype=np.int64)
    b = Dc[np.ix_(rows_, cc)].ravel()
    x = rp.solve(Aeq, b); rank = len(rp.rref(Aeq)[1]) if cols else 0
    print('unknowns %d rank %d %s; system %s' % (len(plan), rank, 'UNIQUE' if rank == len(plan) else 'NOT unique (free vars 0)', 'consistent' if x is not None else 'INCONSISTENT'))
    if x is None: print('RESULT: UNSOLVABLE'); return 'UNSOLVABLE'
    coef = []
    for v in x:
        q = rp.ratrec(int(v)) if v else Fraction(0)
        if q is None or (q != 0 and not rp.dyadic(q)): print('RESULT: NONDYADIC', v, q); return 'NONDYADIC'
        coef.append(q)
    used = [(plan[i][0], plan[i][1], plan[i][2], dim[plan[i][2]], str(coef[i]), bool(plan[i][4])) for i in range(len(plan)) if coef[i] != 0]
    print('new stops used: %d, cost %.2f' % (sum(1 for i in range(len(plan)) if coef[i] != 0 and plan[i][4]), sum(plan[i][5] for i in range(len(plan)) if coef[i] != 0)))
    print('rule events (dest, src, frame, dim, coeff, newstop):', used)
    print('swarm events (dest, src, frame, dim, coeff, op):', [(e[1], e[2], e[4], dim[e[4]], e[3], e[0]) for e in stripped])
    try: prog2, _ = build([c if c != 0 else 0 for c in coef])
    except ValueError as ex: print('RESULT: SCHEDULE', ex); return 'SCHEDULE'
    w2 = dict(w); w2['program'] = prog2
    A2, _ = rp.replay(w2, prog2)
    if ((Tgt - A2) % P).any(): print('RESULT: VALUE-MISMATCH after build'); return 'VALUE'
    S.C.activate(w2); rep = S.C.legal.check(w2)
    BOUNDS = ('Fixed operation bound', 'Public inventory bound')
    if not rep['ok'] and not (a.freebounds and all(v[1] in BOUNDS for v in rep['violations'])): print('RESULT: ILLEGAL', rep['violations'][:4]); return 'ILLEGAL'
    if not rep['ok']: print('bounds-only violations (convention literals, --freebounds):', rep['violations'][:3]); rep = dict(rep); rep['ok'] = True
    kap = S.C.X.kappa(*S.C.X.invoice(rep))
    S.C.activate(w); r0 = dict(S.C.legal.check(w)); r0['ok'] = True; k0 = S.C.X.kappa(*S.C.X.invoice(r0))
    def chains(prog):
        c = {r: [w['initial'][r]] for r in range(n)}
        for e in prog:
            if e[0] == 'MOVE' and e[1] < n: c[e[1]].append(e[3])
        return c
    c0, c2 = chains(prog0), chains(prog2)
    diff = [(r, [dim[f] for f in c0[r]], [dim[f] for f in c2[r]]) for r in range(n) if c0[r] != c2[r]]
    sw = sorted((e[1], e[2], e[4], str(Fraction(e[3]))) for e in stripped); mine = sorted((u[0], u[1], u[2], u[4]) for u in used)
    match = sw == mine
    print('chains differing from base: %d %s' % (len(diff), diff[:6]))
    print('RESULT: LEGAL kappa %.15f (base %.15f, diff %+.3e) events %d (base %d) MATCH=%s' % (kap, k0, kap - k0, len(prog2), len(prog0), match))
    if not a.no_write:
        with gzip.open(a.out, 'wt') as fh: json.dump(w2, fh)
    return dict(kappa=kap, base=k0, match=match, rank=rank, ncand=len(plan), used=used)

if __name__ == '__main__': main()
