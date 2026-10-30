"""IOROOT2 iob2.py (copy of IOROOT iob.py + --strip-ev, --feed-regs, --keep-root-reads):  black-box re-solve of one root's RETURN side (reads + pure couriers) by exact linear algebra with a min-cost stop search.
Extends SIGPIN sigb.py (reads mode, --stops, time 'all'):
  STRIP : every owned->public read of the root family (relay hand-offs kept), every event of the PURE signal helpers whose owned contacts are all in
          this family (couriers; their chains collapse to one jump initial->final), every public stop left empty on a touched register.
  CANDS : p += c * L for every public p co-present with family lifetime L at any frame of L's chain (existing stop, cost 0) or idle in a gap a < f < b
          (new stop, cost = exact marginal chain tax), at every value segment of the window.  --insert LT:FRAME adds a descent stop (see below).
  SOLVE : exact mod p; stop groups chosen by cost-sorted rref (greedy), then a ban-and-resolve improvement loop over the used new stops.
  BUILD : legal.check + exact kappa vs the base.
--insert LTREG:F[:TMOVE] : the family lifetime with owned register LTREG (its LAST stay before the landing) gets an extra stop at frame F (index, or
          '+v1,v2,..' basis to append a frame) between its current frame and the next one; the extra MOVE goes at TMOVE (default: just before the first
          read in the next frame, i.e. as late as possible).
usage: iob.py WORD OUT.json.gz --root K [--strip-pure] [--insert ...] [--improve N] [--no-write]"""
import sys, gzip, json, argparse, collections, math, time
import numpy as np
from fractions import Fraction
import os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE]
import sigside as sigb, rp
from rp import P
from life import rref
from routing import gcols
S = rp.S

def tax(ds):
    D = ds[-1] - ds[0]
    return (D * math.log(D) if D > 0 else 0) - sum((y - x) * math.log(y - x) for x, y in zip(ds, ds[1:]) if y > x)

def chain_tax_total(w, prog):
    n = len(w['initial']); dim = [len(b) for b in w['frames']]
    c = {r: [dim[w['initial'][r]]] for r in range(n)}
    for e in prog:
        if e[0] == 'MOVE' and e[1] < n: c[e[1]].append(dim[e[3]])
    return sum(tax(v) for v in c.values())

def span_key(fr, f):
    return tuple(rref([[int((v >> i) & 1) for i in range(9)] for v in fr[f]])) if False else frozenset(_span(fr[f]))
def _span(B):
    out = {0}
    for b in B: out |= {x ^ b for x in out}
    return out

def sym_events(w, prog, L, Gs):
    """sig1-style replay: x-content + helper junk (res) vs owned-symbol content (sym).  Returns the set of event indices t of public->public
    ADD/COPY whose SOURCE holds only symbols of lifetimes in Gs (no residual content) at t."""
    n = len(w['initial']); live = list(w['live']); col = {r: c for c, r in enumerate(live)}; dimf = [len(b) for b in w['frames']]
    res = {}; js = {}
    for r in live: res[r] = {('x', col[r]): Fraction(1)}
    for r in range(n):
        if r not in res and dimf[w['initial'][r]] > 0: res[r] = {('h', r): Fraction(1)}
    def add(D, S_, q):
        out = dict(D)
        for k, v in S_.items():
            x = out.get(k, 0) + q * v
            if x: out[k] = x
            else: out.pop(k, None)
        return out
    out = set()
    for t, e in enumerate(prog):
        op = e[0]
        if op in ('INIT', 'CLEAR'): res[e[1]] = {}; js[e[1]] = {}; continue
        if op == 'MOVE': continue
        if op == 'SCALE':
            q = Fraction(e[2]); res[e[1]] = {k: v * q for k, v in res.get(e[1], {}).items()}; js[e[1]] = {k: v * q for k, v in js.get(e[1], {}).items()}; continue
        d, s_, q = e[1], e[2], Fraction(e[3])
        if s_ >= n and d < n:
            li = sigb.lid_at(L, s_, t); src_r, src_s = {}, {li: Fraction(1)}
        else:
            src_r, src_s = res.get(s_, {}), js.get(s_, {})
        if s_ < n and d < n and not src_r and src_s and set(src_s) <= Gs: out.add(t)
        if op == 'COPY': res[d] = {}; js[d] = {}
        res[d] = add(res.get(d, {}), src_r, q); js[d] = add(js.get(d, {}), src_s, q)
    return out

def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument('word'); ap.add_argument('out')
    ap.add_argument('--root', type=int, required=True); ap.add_argument('--strip-pure', action='store_true')
    ap.add_argument('--insert', action='append', default=[]); ap.add_argument('--improve', type=int, default=30)
    ap.add_argument('--no-write', action='store_true'); ap.add_argument('--flex', action='store_true'); ap.add_argument('--strip-sym', action='store_true'); ap.add_argument('--first-hop', action='store_true'); ap.add_argument('--root-frames-only', action='store_true'); ap.add_argument('--keep-sym', default=''); ap.add_argument('--f0', action='store_true'); ap.add_argument('--strip-regs', default=''); ap.add_argument('--pairs-any', action='store_true'); ap.add_argument('--f9x', action='store_true'); ap.add_argument('--f0-wide', action='store_true'); ap.add_argument('--diag', action='store_true'); ap.add_argument('--ban', default=''); ap.add_argument('--f9x-regs', default=''); ap.add_argument('--newton', type=int, default=0); ap.add_argument('--relocate', action='append', default=[]); ap.add_argument('--keep-pure', default=''); ap.add_argument('--strip-ev', default=''); ap.add_argument('--feed-regs', default=''); ap.add_argument('--feed-all', action='store_true'); ap.add_argument('--only-reads', default=''); ap.add_argument('--roots', default=''); ap.add_argument('--keep-stops', default='')
    a = ap.parse_args(argv)
    t00 = time.time()
    path, w = S.load_word(a.word); w = json.loads(json.dumps(w)); n = len(w['initial']); R = rp.nreg(w)
    fr = w['frames']; prog0 = w['program']
    for spec in a.relocate:   # REG:T1:T2 (original indices): move the lifetime of owned REG that is alive at its first INIT after ... (the first one) to [T1, T2]
        reg, T1, T2 = map(int, spec.split(':'))
        L0 = sigb.lifetimes(w, prog0)
        l = [x for x in L0 if x['reg'] == reg][int(spec.split(':')[3]) if spec.count(':') > 2 else 0] if False else [x for x in L0 if x['reg'] == reg][0]
        ids = [t for t in range(l['t0'], l['t1'] + 1) if prog0[t][0] != 'MOVE' and reg in S.regfields(prog0[t]) or (prog0[t][0] == 'MOVE' and prog0[t][1] == reg)]
        body = [prog0[t] for t in ids if prog0[t][0] != 'CLEAR']; clr = [prog0[t] for t in ids if prog0[t][0] == 'CLEAR']
        idset = set(ids); newp = []
        for t, e in enumerate(prog0):
            if t == T1: newp += body
            if t == T2: newp += clr
            if t not in idset: newp.append(e)
        prog0 = newp; w['program'] = prog0
        print('relocated owned %d lifetime [%d,%d] -> [%d,%d] (%d events)' % (reg, l['t0'], l['t1'], T1, T2, len(ids)))
    L = sigb.lifetimes(w, prog0); roots, relays = sigb.roots_of(w, prog0, L)
    G = roots[a.root] if not a.roots else [i for k in map(int, a.roots.split(',')) for i in roots[k]]; Gs = set(G)
    relay_t = {x[1] for x in relays} | {x[2] for x in relays}
    sp = [frozenset(_span(b)) for b in fr]
    print('root %d lifetimes %s' % (a.root, [(L[i]['reg'], [(f, len(fr[f]), x, y) for f, x, y in L[i]['stays']]) for i in G]))
    # ---------------- pure helpers of this family (no residual content ever; every owned contact in the family)
    keyof = {}; cnt = collections.Counter()
    for i, l in enumerate(L): cnt[l['reg']] += 1; keyof[(l['reg'], cnt[l['reg']])] = i
    pure = set()
    if a.strip_pure:
        D = __import__('pickle').load(open(os.path.join(HERE, 'data', 'sig1_6030.pkl'), 'rb'))
        keep = set(map(int, a.keep_pure.split(','))) if a.keep_pure else set()
        for r in D['pure']:
            lts = set()
            for (f, c, o) in D['stops'][r]: lts |= set(o)
            idx = {keyof.get(x) for x in lts if isinstance(x, tuple)}
            if idx and idx <= Gs and r not in keep: pure.add(r)
    if a.strip_regs: pure |= set(map(int, a.strip_regs.split(',')))
    print('pure couriers stripped:', sorted(pure))
    # ---------------- strip
    kill = set(); stripped = []
    for t, e in enumerate(prog0):
        if e[0] in ('ADD', 'COPY', 'SCALE') and t not in relay_t:
            if e[0] != 'SCALE':
                d, s = e[1], e[2]
                if s >= n and d < n and sigb.lid_at(L, s, t) in Gs and (not a.only_reads or t in set(map(int, a.only_reads.split(','))) ): kill.add(t)
                if d in pure or s in pure: kill.add(t)
            elif e[1] in pure: kill.add(t)
        if e[0] == 'MOVE' and e[1] in pure: kill.add(t)
    if a.strip_sym:
        se = sym_events(w, prog0, L, Gs) - relay_t
        if a.first_hop:
            readers = {e[1] for t, e in enumerate(prog0) if e[0] == 'ADD' and e[2] >= n and e[1] < n and sigb.lid_at(L, e[2], t) in Gs and t not in relay_t}
            se = {t for t in se if prog0[t][2] in readers}
            print('first-hop readers', sorted(readers))
        if a.root_frames_only:
            rf = {f for i in G for f, _, _ in L[i]['stays']} | {int(x.split(':')[1]) for x in a.insert if not x.split(':')[1].startswith('+')}
            se = {t for t in se if prog0[t][4] in rf}
        if a.keep_sym: se -= set(map(int, a.keep_sym.split(',')))
        print('symbol-only public events stripped: %d %s' % (len(se), sorted(se))); kill |= se
    if a.strip_ev:
        xe = set(map(int, a.strip_ev.split(','))); print('explicit events stripped:', [(t, prog0[t]) for t in sorted(xe)]); kill |= xe
    stripped = [prog0[t] for t in sorted(kill) if prog0[t][0] != 'MOVE']
    prog1 = []
    for t, e in enumerate(prog0):
        if t in kill: continue
        prog1.append(e)
    # collapsed pure helpers: one MOVE initial -> final at the time of their first original MOVE
    firstmv = {}
    for t, e in enumerate(prog0):
        if e[0] == 'MOVE' and e[1] in pure and e[1] not in firstmv: firstmv[e[1]] = t
    if pure:
        ins = collections.defaultdict(list)
        for r in pure:
            if w['initial'][r] != w['final'][r]: ins[firstmv[r]].append(['MOVE', r, w['initial'][r], w['final'][r], prog0[firstmv[r]][4]])
        out = []
        for t, e in enumerate(prog0):
            out += ins.get(t, [])
            if t not in kill: out.append(e)
        prog1 = out
    touched = {e[1] for e in stripped if e[1] < n} | {e[2] for e in stripped if e[0] != 'SCALE' and e[2] < n}
    # ---------------- descent insertions
    for spec in a.insert:
        parts = spec.split(':'); reg = int(parts[0]); f = parts[1]
        if f.startswith('+'):
            vs = [int(x) for x in f[1:].split(',')]; fr.append(vs); sp.append(frozenset(_span(vs))); f = len(fr) - 1
        else: f = int(f)
        Lc = sigb.lifetimes(w, prog1)
        mine = [l for l in Lc if l['reg'] == reg]; orig = [i for i, l in enumerate(L) if l['reg'] == reg]
        l = [mine[q] for q, i in enumerate(orig) if i in Gs][0]
        # last stay before landing
        j = len(l['stays']) - 2
        fa, fb = l['stays'][j][0], l['stays'][j + 1][0]
        assert sp[f] < sp[fa] and sp[fb] < sp[f], ('insert frame not nested', fa, f, fb)
        tm = l['stays'][j][2]          # index of the MOVE fa -> fb
        ev = prog1[tm]; assert ev[0] == 'MOVE' and ev[1] == reg
        # second MOVE: as late as possible = just before the first event touching reg after tm
        t2 = (tm + 1 + int(parts[2][1:]) if parts[2].startswith('+') else int(parts[2])) if len(parts) > 2 else min([t for t in range(tm + 1, len(prog1)) if prog1[t][0] != 'MOVE' and reg in S.regfields(prog1[t])] + [len(prog1)])
        prog1 = prog1[:tm] + [['MOVE', reg, fa, f, ev[4]]] + prog1[tm + 1:t2] + [['MOVE', reg, f, fb, ev[4]]] + prog1[t2:]
        print('insert: owned %d %d(d%d) -> %d(d%d) -> %d(d%d), second MOVE at %d' % (reg, fa, len(fr[fa]), f, len(fr[f]), fb, len(fr[fb]), t2))
    dim = [len(b) for b in fr]
    w['frames'] = fr
    # ---------------- drop stops left empty on touched registers
    st1 = sigb.stays_pub(w, prog1)
    evc = collections.Counter(); sidx = {r: 0 for r in range(n)}
    for e in prog1:
        if e[0] == 'MOVE':
            if e[1] < n: sidx[e[1]] += 1
            continue
        for r in S.regfields(e):
            if r < n: evc[(r, sidx[r])] += 1
    killmv = set(); newmv = {}; dropped = []
    for r in sorted(touched - pure - (set(map(int, a.keep_stops.split(','))) if a.keep_stops else set())):
        ch = st1[r]; j = 1
        while j < len(ch) - 1:
            if evc[(r, j)] == 0:
                ti, to = ch[j][1], ch[j][2]
                if ti in killmv or ti in newmv:   # consecutive empty stops: merge into one jump
                    prev = newmv.pop(ti, None) or prog1[ti]
                    killmv.add(ti); newmv[to] = ['MOVE', r, prev[2], ch[j + 1][0], prog1[to][4]]
                else:
                    killmv.add(ti); newmv[to] = ['MOVE', r, ch[j - 1][0], ch[j + 1][0], prog1[to][4]]
                dropped.append((r, ch[j][0], dim[ch[j][0]]))
            j += 1
    prog1 = [newmv.get(t, e) for t, e in enumerate(prog1) if t not in killmv]
    st1 = sigb.stays_pub(w, prog1)
    print('stripped %d events, %d empty stops dropped %s' % (len(stripped), len(dropped), dropped))
    w1 = dict(w); w1['program'] = prog1
    L1 = sigb.lifetimes(w1, prog1)
    # family lifetimes in prog1 (same INIT order)
    order0 = collections.defaultdict(list); order1 = collections.defaultdict(list)
    for i, l in enumerate(L): order0[l['reg']].append(i)
    for i, l in enumerate(L1): order1[l['reg']].append(i)
    G1 = sorted(order1[L[i]['reg']][order0[L[i]['reg']].index(i)] for i in G)
    writes = collections.defaultdict(list); evts = collections.defaultdict(list)
    for t, e in enumerate(prog1):
        if e[0] in ('ADD', 'COPY', 'SCALE', 'INIT', 'CLEAR'): writes[e[1]].append(t)
        if e[0] != 'MOVE':
            for r in S.regfields(e): evts[r].append(t)
    sub = lambda x, y: sp[x] < sp[y]
    plan = []
    print("family stays", [(L1[i]["reg"], L1[i]["stays"]) for i in G1])
    for i in G1:
        l = L1[i]; o = l['reg']
        for (f, ta, tb) in l['stays']:
            for p in range(n):
                ch = st1[p]
                for j, (g, pa, pb) in enumerate(ch):
                    if g != f: continue
                    if a.flex:   # MOVE times are free: the stay may start after p's last event before it and end before p's next event after it
                        fa_ = max([t for t in evts[p] if t < pa] + [-1]) if pa >= 0 else pa
                        fb_ = min([t for t in evts[p] if t > pb] + [len(prog1)]) if pb < len(prog1) else pb
                        lo, hi = max(ta, fa_) + 1, min(tb, fb_)
                    else: lo, hi = max(ta, pa) + 1, min(tb, pb)
                    if lo > hi: continue
                    ts = sorted({lo} | {t + 1 for t in evts[p] + writes[o] if lo <= t < hi})
                    for t_ in ts:
                        hz = ('h', j, pa, pb) if (t_ <= pa or t_ > pb) else None
                        plan.append((p, o, f, t_, hz, 0.0))
                for j in range(len(ch) - 1):
                    g0, pa, pb = ch[j]; g1 = ch[j + 1][0]
                    if not (sub(g0, f) and sub(f, g1)): continue
                    lastev = max([t for t in evts[p] if t < pb] + [-1]); nextev = min([t for t in evts[p] if t > pb] + [len(prog1)])
                    lo, hi = max(lastev, ta) + 1, min(nextev, tb)
                    if lo > hi: continue
                    ds = [dim[x[0]] for x in ch]; cost = tax(ds[:j + 1] + [dim[f]] + ds[j + 1:]) - tax(ds)
                    ts = sorted({lo, hi} | {t + 1 for t in writes[o] if lo <= t < hi})
                    for t_ in ts: plan.append((p, o, f, t_, (j, pb), cost))
    if a.feed_regs or a.feed_all:
        # FEED candidates: owned family lifetime o += c * p for public p co-present with o at a frame of o's chain (existing stop of p, flex times)
        fregs = set(map(int, a.feed_regs.split(','))) if a.feed_regs else set(range(n)); nfd = 0
        for i in G1:
            l = L1[i]; o = l['reg']
            for (f, ta, tb) in l['stays']:
                for p in sorted(fregs):
                    for j, (g, pa, pb) in enumerate(st1[p]):
                        if g != f: continue
                        lo, hi = max(ta, pa) + 1, min(tb, pb)
                        if lo > hi: continue
                        ts = sorted({lo, hi} | {t + 1 for t in evts[p] + evts[o] if lo <= t < hi})
                        for t_ in ts: plan.append((o, p, f, t_, None, 0.0)); nfd += 1
        print('FEED candidates: %d' % nfd)
    if a.f0:
        # junk candidates: for every stripped public->public event d <- s, d += c * s at F0 (both 0-born, co-present at F0) -- the pre-read that
        # cancels s's initial-value junk in d; at every value segment of the co-presence window
        f0 = [f for f in range(len(fr)) if dim[f] == 0]
        pairs = {(e[1], e[2]) for e in stripped if e[0] in ('ADD', 'COPY') and e[1] < n and e[2] < n}
        if a.f0_wide:   # also every existing F0 event touching a register of a stripped pair (its pre-read partners)
            tch = {x for pr in pairs for x in pr}
            pairs |= {(e[1], e[2]) for e in prog1 if e[0] == 'ADD' and e[1] < n and e[2] < n and dim[e[4]] == 0 and (e[1] in tch or e[2] in tch)}
        nf0 = 0; pairt = collections.defaultdict(list)
        for t, e in enumerate(prog1):
            if e[0] == 'ADD' and (e[1], e[2]) in pairs: pairt[(e[1], e[2])].append(t)
        for d, s_ in pairs:
            for (g, pa, pb) in (st1[d] if a.pairs_any else st1[d][:1]):
                for (g2, qa, qb) in (st1[s_] if a.pairs_any else st1[s_][:1]):
                    if g != g2 or (dim[g] != 0 and not a.pairs_any): continue
                    lo, hi = max(pa, qa) + 1, min(pb, qb)
                    if lo > hi: continue
                    if a.f0_wide: ts = sorted({lo, hi} | {t for t in pairt.get((d, s_), ()) if lo <= t <= hi} | {t + 1 for t in pairt.get((d, s_), ()) if lo <= t + 1 <= hi})
                    else: ts = sorted({lo} | {t + 1 for t in evts[d] + writes[s_] if lo <= t < hi})
                    for t_ in ts: plan.append((d, s_, g, t_, None, 0.0)); nf0 += 1
        print('F0 junk candidates: %d for %d pairs' % (nf0, len(pairs)))
        f0regs = {x for pr in pairs for x in pr}; nb_ = len(plan)
        plan = [x for x in plan if not (x[4] is not None and x[4][0] == 'h' and x[0] in f0regs)]
        print('hoists dropped for F0-pair registers: %d' % (nb_ - len(plan)))
    if a.f9x:
        # F9 cleanup: every touched register that ends at F9 may subtract X_i (at F9, after X_i arrives) -- R content is x-content
        f9 = [f for f in range(len(fr)) if dim[f] == 9]; nx = 0
        rec = {e[1] for e in stripped if e[0] in ('ADD', 'COPY') and e[1] < n} | {e[2] for e in stripped if e[0] in ('ADD', 'COPY') and e[2] < n}
        if a.f9x_regs: rec |= set(map(int, a.f9x_regs.split(',')))
        for d in sorted(rec):
            g, pa, pb = st1[d][-1]
            if dim[g] != 9: continue
            for x in w['live']:
                gx, xa, xb = st1[x][-1]
                if gx != g: continue
                t_ = max(pa, xa, max(evts[d] + [0])) + 1
                if t_ <= len(prog1): plan.append((d, x, g, t_, None, 0.0)); nx += 1
        print('F9 x-cleanup candidates: %d' % nx)
    if a.ban:
        bn = set(map(int, a.ban.split(','))); plan = [x for x in plan if not (x[0] in bn and x[1] >= n)]
    # exactness: a candidate's SOURCE must not be perturbed (before its slot) by any candidate destination
    keep, tainted = rp.taint_ok(prog1, [(x[0], x[1], x[3], x[2]) for x in plan]) if not a.newton else ([(x[0], x[1], x[3], x[2]) for x in plan], {})
    ks = set(keep); nb = len(plan); plan = [x for x in plan if (x[0], x[1], x[3], x[2]) in ks]
    print('taint filter: %d -> %d candidates' % (nb, len(plan)))
    plan.sort(key=lambda x: (x[5], -x[3] if (x[4] is not None and x[4][0] != 'h') else x[3]))
    print('candidate dests:', sorted({(x[0], x[2], round(x[5], 2)) for x in plan})[:80])
    print('stripped receivers:', sorted({e[1] for e in stripped if e[0] != 'SCALE' and e[1] < n}))
    grp = {}
    for i, x in enumerate(plan):
        if x[4] is not None and x[4][0] != 'h': grp.setdefault((x[0], x[4][1], x[2]), []).append(i)
    print('candidates: %d (%d need a new stop; %d stop groups; %d retimed stays)' % (len(plan), sum(1 for x in plan if x[4] and x[4][0] != 'h'), len(grp), sum(1 for x in plan if x[4] and x[4][0] == 'h')))
    def build(coefs, stops=True):
        ins = collections.defaultdict(list); delete = set(); gaps = collections.defaultdict(list); hoist = collections.defaultdict(list)
        for i, (d, s, f, t_, ns, cost) in enumerate(plan):
            c = coefs[i]
            if c == 0: continue
            ins[t_].append((1, ['ADD', d, s, str(c), f]))
            if ns is not None and ns[0] == 'h':
                if stops: hoist[(d, ns[2], ns[3])].append(t_)
            elif ns is not None and stops: gaps[(d, ns[1])].append((dim[f], f, t_))
        relocated = set()
        for (p, pa, pb), ts in hoist.items():
            if min(ts) <= pa:
                if pa in delete or pa in relocated: raise ValueError('MOVE %d relocated twice' % pa)
                delete.add(pa); relocated.add(pa); ins[min(ts)].append((0, prog1[pa]))
            if max(ts) > pb:
                if pb in delete or pb in relocated: raise ValueError('MOVE %d relocated twice' % pb)
                delete.add(pb); relocated.add(pb); ins[max(ts)].append((2, prog1[pb]))
        for (p, pb), L_ in gaps.items():
            fs = sorted(set((df, f) for df, f, t_ in L_)); old = prog1[pb]
            if pb in delete: raise ValueError('gap MOVE %d also relocated' % pb)
            delete.add(pb)
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
    def linsys(cvec):
        progP, pos = build(cvec, stops=False)
        idx = [pos[(d, s, t_)] for (d, s, f, t_, ns, cost) in plan]
        snapreq = collections.defaultdict(list)
        for i, t in enumerate(idx): snapreq[t].append(plan[i][1])
        A0, snaps = rp.replay(w1, progP, snap=snapreq)
        Tgt = rp.target(w1); Dc = (Tgt - A0) % P
        print('residual entries after strip: %d' % int(np.count_nonzero(Dc)))
        gq = collections.defaultdict(list)
        for i, t in enumerate(idx): gq[t].append(plan[i][0])
        GC = gcols(progP, gq, R, True)
        rowsets = set(np.nonzero(Dc.any(1))[0]); colsets = set(np.nonzero(Dc.any(0))[0])
        gcv = [GC[(t, plan[i][0])] for i, t in enumerate(idx)]; snv = [snaps[t][plan[i][1]] for i, t in enumerate(idx)]
        for i in range(len(plan)):
            rowsets |= set(np.nonzero(gcv[i])[0]); colsets |= set(np.nonzero(snv[i])[0])
        rows_ = sorted(rowsets); cc = sorted(colsets)
        print('system rows %d cols %d unknowns %d -> %d equations' % (len(rows_), len(cc), len(plan), len(rows_) * len(cc)), '%.0fs' % (time.time() - t00), flush=True)
        # random projection of the equations (Schwartz-Zippel, entries < 2^20; a false verdict is caught by the exact replay check)
        U = len(plan); K = min(len(rows_) * len(cc), U + 40)
        rng = np.random.default_rng(12345)
        Gm = np.array([gcv[i][rows_] for i in range(U)], dtype=np.int64)   # U x nr
        Sm = np.array([snv[i][cc] for i in range(U)], dtype=np.int64)      # U x nc
        Dm = Dc[np.ix_(rows_, cc)] % P
        def mm(X, Y):   # X (a x m) < 2^31, Y (m x b) < 2^20 -> X @ Y mod P, chunked
            out = np.zeros((X.shape[0], Y.shape[1]), dtype=np.int64)
            for c0 in range(0, X.shape[1], 1024): out = (out + (X[:, c0:c0 + 1024] @ Y[c0:c0 + 1024]) % P) % P
            return out
        Um = rng.integers(0, 1 << 20, size=(len(rows_), K), dtype=np.int64); Vm = rng.integers(0, 1 << 20, size=(len(cc), K), dtype=np.int64)
        GU = mm(Gm, Um); SV = mm(Sm, Vm)                                   # U x K each
        lo = SV & 0xFFFF; hi = SV >> 16
        A = (((GU * lo) % P + ((GU * hi) % P) * 65536 % P) % P).T.copy()
        UD = mm(Dm.T.copy(), Um)                                          # nc x K : column k = D^T u_k
        bb = np.array([sum(int(x) * int(y) for x, y in zip(UD[:, k], Vm[:, k])) % P for k in range(K)], dtype=np.int64)
        print('projected system %d x %d' % A.shape, '%.0fs' % (time.time() - t00), flush=True)

        return A, bb, Dc, Dm, rows_, cc, gcv, snv, Tgt
    A, bb, Dc, Dm, rows_, cc, gcv, snv, Tgt = linsys(['0'] * len(plan))
    costs = np.array([x[5] for x in plan])
    def solve_with(allowed):
        cols = [i for i in range(len(plan)) if allowed[i]]
        x = rp.solve(A[:, cols], bb)
        if x is None: return None
        full = np.zeros(len(plan), dtype=np.int64); full[cols] = x
        return full
    def used_groups(x):
        return sorted({g for g, ids in grp.items() if any(x[i] for i in ids)})
    def gcost(gs):
        return sum(plan[grp[g][0]][5] for g in gs)
    allowed = np.ones(len(plan), dtype=bool)
    x = solve_with(allowed)
    if a.newton and x is not None:
        cur = x.copy()
        for itn in range(a.newton):
            A, bb, Dc, Dm, rows_, cc, gcv, snv, Tgt = linsys([str(int(v)) for v in cur])
            nz = int(np.count_nonzero(Dc)); print('newton %d: residual entries %d' % (itn, nz), flush=True)
            if nz == 0: break
            d = solve_with(allowed)
            if d is None: print('newton: step unsolvable'); x = None; break
            cur = (cur + d) % P
        x = cur if x is not None else None
    if x is None:
        if a.diag:
            bad = []
            for ri, r in enumerate(rows_):
                if not Dm[ri].any(): continue
                Ar = np.array([(gcv[i][r] * snv[i][cc]) % P for i in range(len(plan))]).T % P
                if rp.solve(Ar, Dm[ri]) is None:
                    bad.append(r)
            blocks = []; acc_b = []
            role = lambda r: ('X' if r in set(w['live']) else ('Y' if r - 112 in set(w['live']) else ('H' if r < n else 'O'))) + str(r)
            for ri, r in enumerate(rows_):
                if not Dm[ri].any() and not any(gcv[i][r] for i in range(len(plan))): continue
                Ar = np.array([(gcv[i][r] * snv[i][cc]) % P for i in range(len(plan))]).T % P
                blocks.append(Ar); acc_b.append(Dm[ri])
                if rp.solve(np.concatenate(blocks), np.concatenate(acc_b)) is None:
                    nzc = [c for j, c in enumerate(cc) if Dm[ri][j]]
                    print('DIAG first conflicting row', role(r), 'after', len(blocks), 'rows; deficit cols', [role(c) for c in nzc][:20], 'chain', [(f, dim[f]) for f, _, _ in st1[r]] if r < n else '-')
                    print('DIAG its events', [(t, e) for t, e in enumerate(prog1) if e[0] != 'MOVE' and r in S.regfields(e)][-12:])
                    break
            print('DIAG rows unsolvable on their own:', bad, 'support cols of first:', [c for c in cc if Dm[rows_.index(bad[0])][cc.index(c)]] if bad else None)
        print('RESULT: UNSOLVABLE'); return 'UNSOLVABLE'
    best = (gcost(used_groups(x)), x, set())
    print('greedy: groups %s cost %.3f' % (used_groups(x), best[0]), flush=True)
    # ban-and-resolve: try banning each used group (and pairs of the most expensive) while it lowers the cost
    banned = set(); it = 0
    improved = True
    while improved and it < a.improve:
        improved = False; it += 1
        ug = used_groups(best[1])
        for g in sorted(ug, key=lambda g: -plan[grp[g][0]][5]):
            al = allowed.copy()
            for gg in banned | {g}:
                for i in grp[gg]: al[i] = False
            x2 = solve_with(al)
            if x2 is None: continue
            c2 = gcost(used_groups(x2))
            if c2 < best[0] - 1e-9:
                best = (c2, x2, banned | {g}); banned = banned | {g}; improved = True
                print('  improve: ban %s -> cost %.3f groups %s' % (g, c2, used_groups(x2)), flush=True)
                break
    x = best[1]
    coef = []
    for v in x:
        q = rp.ratrec(int(v)) if v else Fraction(0)
        if q is None or (q != 0 and not rp.dyadic(q)): print('RESULT: NONDYADIC', v, q); return 'NONDYADIC'
        coef.append(q)
    used = [(plan[i][0], plan[i][1], plan[i][2], dim[plan[i][2]], str(coef[i]), bool(plan[i][4])) for i in range(len(plan)) if coef[i] != 0]
    print('new stops used: %d, est cost %.2f' % (len(used_groups(x)), best[0]))
    print('rule events (dest, src, frame, dim, coeff, newstop):', used)
    print('swarm events stripped (dest, src, frame, dim, coeff, op):', [(e[1], e[2], e[4], dim[e[4]], e[3], e[0]) for e in stripped][:60])
    try: prog2, _ = build([c if c != 0 else 0 for c in coef])
    except ValueError as ex: print('RESULT: SCHEDULE', ex); return 'SCHEDULE'
    w2 = dict(w); w2['program'] = prog2
    A2, _ = rp.replay(w2, prog2)
    if ((Tgt - A2) % P).any():
        bad = np.nonzero(((Tgt - A2) % P).any(1))[0]
        Ab, _ = rp.replay(w1, build([c if c != 0 else 0 for c in coef], stops=False)[0])
        print('mismatch rows', list(bad)[:20], 'no-stop build mismatch rows', list(np.nonzero(((Tgt - Ab) % P).any(1))[0])[:20])
        print('RESULT: VALUE-MISMATCH after build'); return 'VALUE'
    S.C.activate(w2); rep = S.C.legal.check(w2)
    if not rep['ok']: print('RESULT: ILLEGAL', rep['violations'][:4]); return 'ILLEGAL'
    kap = S.C.X.kappa(*S.C.X.invoice(rep))
    S.C.activate(w); w0 = json.loads(json.dumps(S.load_word(a.word)[1])); k0 = S.C.X.kappa(*S.C.X.invoice(S.C.legal.check(w0)))
    print('R0 chain tax: base %.2f new %.2f' % (chain_tax_total(w0, prog0), chain_tax_total(w2, prog2)))
    print('RESULT: LEGAL kappa %.15f (base %.15f, diff %+.3e) events %d (base %d)' % (kap, k0, kap - k0, len(prog2), len(prog0)))
    if not a.no_write:
        with gzip.open(a.out, 'wt') as fh: json.dump(w2, fh)
    return dict(kappa=kap, base=k0)

if __name__ == '__main__': main()
