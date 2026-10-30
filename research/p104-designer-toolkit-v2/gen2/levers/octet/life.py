"""LEVERBANK copy of OCTLIFE/life.py (octet route engine; lane dir untouched).
OCTLIFE lifetime engine (copies; PUREX/purex2 + gen2 untouched).  No env at import.
Generalises PUREX's joint dim-0 solve to octet words:
 - Ys act as sources and stop at 3/6/7: the leading dim-0 ADDs into Ys (Ctx.zy) are KEPT in the body (purex2 dropped and re-solved them,
   which is only valid when Ys are never read); the Z block (I + Delta on U) runs before them.  A[r,s] is computed on the full body.
 - selfreq: required finals of Ys := the input word's own finals (residual-only builds have no signal; the levers must keep every Y final).
 - census_octet: early ends of bottom riders at their OCTET frame O (dim 4, h climbs g -> O), survivors = X mains stopping at O inside one
   segment of their frame chain (prev frame <= O <= next frame); per-octet exhaustive survivor subset, exact chain-tax net.
Exactness: every word is replayed symbolically; finals must equal req on every register (value check), plus dag.realise legality."""
import sys, os, gzip, json, collections, itertools, time
from fractions import Fraction as Q
HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..')); TK = W
for p in (TK + '/gen2', TK, TK + '/synth', W + '/infra', HERE):
    if p in sys.path: sys.path.remove(p)
    sys.path.insert(0, p)
import purex as PX
from purex import addf, replay, dy
import purex2 as P2
from ee0 import solve
import kernel2net as KN

def span_set(b):
    z = {0}
    for v in b: z |= {x ^ v for x in z}
    return frozenset(z)

def rref(vs):
    rows = []
    for v in vs:
        for r in rows:
            if v ^ r < v: v ^= r
        if v:
            rows = [r ^ v if r ^ v < r else r for r in rows] + [v]
    return tuple(sorted(rows, reverse=True))

class Ctx2(PX.Ctx):
    def __init__(s, w, selfreq=False):
        PX.Ctx.__init__(s, w)
        s.body = s.zy + s.body; s.zy = []            # Ys are sources: keep their dim-0 ADDs
        if selfreq:
            F, _ = replay(s.body + s.f9, s.n, s.no)
            for r in range(s.n):
                if s.role(r) == 'Y': s.req[r] = {k: v for k, v in F[r].items() if v}
        s.SP = [span_set(b) for b in s.d['frames']]

    def chain_dims(s, r):
        if not hasattr(s, 'wch'): s.wch = KN.chains(s.w); s.wdim = [len(b) for b in s.w['frames']]
        return [s.wdim[f] for f in s.wch[r]]

    def timeline(s):
        """x-values after each body op; frame chains; per-register op index list"""
        n = s.n; role = s.role
        X = {r: ({r: Q(1)} if role(r) == 'X' else {}) for r in range(n + s.no)}
        cur = dict(s.init); hist = collections.defaultdict(list); last = {}
        for r in range(n): hist[r].append((-1, s.init[r], dict(X[r])))
        for i, o in enumerate(s.body):
            op, r, src, q, f = o[:5]
            if op == 'ADD': addf(X[r], X[src], Q(q))
            elif op == 'COPY': X[r] = {c: v * Q(q) for c, v in X[src].items()}
            elif op in ('INIT', 'CLEAR'): X[r] = {}
            elif op == 'SCALE': X[r] = {c: v * Q(q) for c, v in X[r].items()}
            for x in ([r, src] if op in ('ADD', 'COPY') else [r]):
                if x is not None and x < n:
                    hist[x].append((i, f, dict(X[x]))); last[x] = i; cur[x] = f
        s.X = X; s.hist = hist; s.last = last
        s.readby = collections.defaultdict(set)
        for o in s.body:
            if o[0] == 'ADD': s.readby[o[2]].add(o[1])
        fin = {r: s.d['regs'][str(r)][2] for r in range(n)}
        s.fin = fin
        s.chains = {}
        for r in range(n):
            fs = [s.init[r]]
            for (i, f, _) in hist[r][1:]:
                if f != fs[-1]: fs.append(f)
            for o in s.f9:
                pass
            if fin[r] != fs[-1]: fs.append(fin[r])
            s.chains[r] = fs

def tax(ds): return KN.tax_dims(ds)

def octet_frames(c):
    """octet label per X register and octet frame bases (from the word's ports; octets = D3 coset + ^384 partner)"""
    D3 = [120, 85, 75, 51, 102, 30, 45]
    P = c.d['meta']['ports']; live = c.d['meta']['live']
    cos = {i: min(P[i] ^ d for d in D3 + [0]) for i in range(len(P))}
    oc = {i: min(cos[i], min(P[i] ^ 384 ^ d for d in D3 + [0])) for i in range(len(P))}
    xo = {live[i]: oc[i] for i in range(len(P))}; xp = {live[i]: P[i] for i in range(len(P))}
    Of = {}
    for o in set(oc.values()): Of[o] = list(rref([P[i] for i in range(len(P)) if oc[i] == o]))
    return xo, xp, Of

def census_octet(c, dimO=4, allow_xread=False, verbose=True, maxsub=4096, exclude=()):
    """bottom riders ending at their octet frame O.  returns enders [dict(h, t, f(frame basis list), use[(X, coef, t)])], info"""
    c.timeline(); n = c.n; role = c.role
    xo, xp, Of = octet_frames(c)
    OfS = {o: span_set(b) for o, b in Of.items()}
    readX = {h for h in range(n) if role(h) == 'H' and any(role(r) in ('X', 'O') for r in c.readby[h])}
    groups = collections.defaultdict(lambda: dict(N=[], S=[]))
    for h in range(n):
        if role(h) != 'H' or h not in c.born0 or h not in c.last: continue
        if h in readX and not allow_xread: continue
        if h in exclude: continue
        i = c.last[h]; v = c.X[h]
        if not v: continue
        os_ = {xo[x] for x in v}
        if len(os_) != 1: continue
        o = os_.pop(); g = c.body[i][4]
        if not c.SP[g] <= OfS[o] or c.dim[g] >= dimO: continue
        ch = c.chain_dims(h)
        if ch[-1] != 9: continue
        new = [d for d in ch[:-1]] + [dimO]
        sv = tax(ch) - tax(new)
        if sv <= 0: continue
        groups[o]['N'].append((h, i, v, sv))
    for x in range(n):
        if role(x) != 'X': continue
        H = c.hist[x]; ch = c.chain_dims(x)
        for k in range(len(H)):
            ti, fa, val = H[k]; tn, fb = (H[k + 1][0], H[k + 1][1]) if k + 1 < len(H) else (len(c.body), c.fin[x])
            if not val: continue
            os_ = {xo[y] for y in val}
            if len(os_) != 1: continue
            o = os_.pop()
            if c.SP[fa] <= OfS[o] <= c.SP[fb] and c.dim[fa] < dimO < c.dim[fb]:
                # X stop cost: dims of its chain with dimO inserted
                cost = tax(sorted(set(ch + [dimO]))) - tax(ch)
                groups[o]['S'].append((x, ti, tn, val, cost))
    out = []; info = collections.Counter()
    for o, G in sorted(groups.items()):
        Nn, S = G['N'], G['S']
        if not Nn or not S: continue
        best = (0.0, (), [])
        Ss = S if len(S) <= 12 else sorted(S, key=lambda z: z[4])[:12]
        for k in range(1, len(Ss) + 1):
            for sub in itertools.combinations(Ss, k):
                if len({z[0] for z in sub}) < k: continue
                cst = sum(z[4] for z in sub); gain = -cst; sel = []
                for (h, i, v, sv) in Nn:
                    us = [z for z in sub if z[2] > i]
                    if not us: continue
                    a = solve(v, [z[3] for z in us])
                    if a is None: continue
                    co = {us[t][0]: -q for t, q in a.items() if q}
                    if not all(dy(q) for q in co.values()): continue
                    t = max([i] + [us[t][1] for t in a if a[t]])
                    if any(z[2] <= t for z in us if z[0] in co): continue
                    gain += sv; sel.append((h, t, co, sv))
                if gain > best[0] + 1e-9: best = (gain, sub, sel)
        g, sub, sel = best
        if g <= 0: continue
        info['octets'] += 1; info['survivors'] += len({z[0] for z in sub if any(z[0] in s_[2] for s_ in sel)}); info['net'] += g
        for (h, t, co, sv) in sel:
            out.append(dict(h=h, t=t, f=list(Of[o]), use=[(x, a, t) for x, a in co.items()], save=sv))
        info['enders'] += len(sel)
    if verbose: print('census_octet', dict(info), flush=True)
    return out, info

def realise(c, enders, verbose=True):
    """purex2 joint solve on Ctx2 (zy kept), F9 fixes; returns (dag, ops)"""
    c2 = c; enders = list(enders); dropped = []
    while True:
        try:
            cc, body, f9, zops, Delta = P2.run(c2.w, enders, verbose=verbose, ctx=c2); break
        except P2.NotBorn0 as ex:
            hs = {e['h'] for e in enders}; culprit = set()
            for r, ks in ex.rows.items(): culprit |= (ks & hs)
            if not culprit: raise SystemExit('LIFE: not-born-0 rows with no ender symbol %s' % list(ex.rows.items())[:4])
            dropped += sorted(culprit); enders = [e for e in enders if e['h'] not in culprit]
            if verbose: print('drop enders contaminating non-0-born rows', sorted(culprit), 'rows', sorted(ex.rows)[:8], flush=True)
    c.dropped = dropped; c.enders_used = enders
    E = {e['h']: e for e in enders}
    ops = P2.finish(cc, body, f9, zops, E, verbose=verbose)
    bad = [o for o in ops if o[0] == 'ADD' and not dy(o[3])]
    if bad: raise SystemExit('LIFE: non-dyadic %s' % bad[:4])
    dag = dict(cc.d); dag['ops'] = ops; dag['regs'] = {k: list(v) for k, v in cc.d['regs'].items()}
    dag['frames'] = list(cc.d['frames'])
    for h, e in E.items():
        f = e['f']
        if isinstance(f, list):
            key = tuple(f)
            idx = next((k for k, b in enumerate(dag['frames']) if tuple(b) == key), None)
            if idx is None: dag['frames'].append(list(f)); idx = len(dag['frames']) - 1
            f = idx
        dag['regs'][str(h)][2] = f
    return dag, ops

def to_word(c, dag, prof_word):
    import dag as D, incr
    from tkcommon import profile_of
    fr = dag['frames']; ops = []
    for o in dag['ops']:
        o = list(o)
        if isinstance(o[4], list):
            key = tuple(o[4]); idx = next((k for k, b in enumerate(fr) if tuple(b) == key), None)
            if idx is None: fr.append(list(o[4])); idx = len(fr) - 1
            o[4] = idx
        ops.append(o)
    dag['ops'] = ops
    w2, rep = D.realise(dag, schedule='lazy', verify=True)
    w2['verifier_profile'] = dict(c.w.get('verifier_profile') or {})
    # own value check against c.req (selfreq aware)
    F, _ = replay(ops, c.n, c.no)
    badv = []
    for r in range(c.n):
        d = {k: F[r].get(k, 0) - c.req[r].get(k, 0) for k in set(F[r]) | set(c.req[r])}
        if any(d.values()): badv.append(r)
    return w2, rep, badv

def census_realise(c, verbose=True, **kw):
    """census -> realise; enders that contaminate non-0-born rows are excluded and the census RE-OPTIMISED (survivor subsets) until stable"""
    excl = set()
    for it in range(12):
        en, info = census_octet(c, exclude=excl, verbose=verbose, **kw)
        dag, ops = realise(c, en, verbose=verbose)
        if not c.dropped: return dag, ops, en, info
        excl |= set(c.dropped)
        if verbose: print('re-census excluding', len(excl), flush=True)
    raise SystemExit('LIFE: census/realise did not stabilise')
