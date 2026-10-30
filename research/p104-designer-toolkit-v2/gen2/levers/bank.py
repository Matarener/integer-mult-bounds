"""LEVERBANK: composable early-end levers for route-B block-form words (copies of lane code; lane dirs untouched).  No env at import.

Every realised lever of the Oct-27 lanes is the SAME kind of object: an extra ender dict  e = {h, t, f, use=[(R, coef, t)]}  handed to
purex2's joint dim-0 solve together with purex2's own census enders (`purex.Ctx.census`).  So levers compose at ONE point, the purex
stage, before k2sa / evretime (purex2 asserts the block form `no body op after F9`, so it cannot run after polish).

Levers (spec strings, see stack.py):
  own:H@G      OWNEDRANK  park the root (whose chain can hold G: l_k in G, G inside H_k) at frame G, end rider H at G against the parked copy.
               Precondition: x(H) after its last body op is a dyadic multiple of x(R_k).  Changes: +1 owned field/lifetime per parked frame,
               paid unchanged, staging entropy  r ln r - a ln a - b ln b  (4.78 at dim 4).  Resource: rider H, (root, frame G).
  own:auto     same, greedy over all riders/roots on EXISTING frames, net = saving - staging > 0, nested chain per root.
  hub:R,R,../X,X,..[@b,b,..]  TWINBOTTOM  riders cleaned against ONE shared holder set at hub frame M (default M = span of the riders'
               last frames); each holder pays one split at dim M.  Resource: riders, holder windows (one new stop per window).
  relay:H[:dmax]  DEADRIDERS/FANIN  single rider ended at the cheapest frame M (<= dmax) against <= 3 routed holders (A < M < B windows).
  relay:auto[:dmax]  greedy over all riders, net > 0.
  skip:H,H     drop these purex2 census enders (GEN2SWEEP's recovery for 'rows needing dim-0 correction').
Conflicts (recorded, the later lever is dropped): same rider twice (incl. a census ender), a holder window asked for two different new stop
frames, a root asked for a non-nested frame set.  Same holder window at the SAME frame is sharing (paid once), not a conflict."""
import sys, os, collections, itertools, math
from fractions import Fraction as Q
HERE = os.path.dirname(os.path.abspath(__file__)); G2 = os.path.dirname(HERE); TK = os.path.dirname(G2)
for p in (TK, os.path.join(TK, 'synth'), G2):
    if p not in sys.path: sys.path.insert(0, p)
import purex as PX, purex2 as P2
from purex import addf, dy
from ee0 import solve


# ---------------------------------------------------------------- span helpers (copies of DEADRIDERS/mile.py)
def rref(vs):
    b = []
    for v in vs:
        for x in b:
            if v ^ x < v: v ^= x
        if v: b = [x ^ v if x ^ v < x else x for x in b]; b.append(v)
    return tuple(sorted(b, reverse=True))

def red(v, b):
    for x in b:
        if v ^ x < v: v ^= x
    return v

def sub(a, b): return all(red(v, b) == 0 for v in a)

def spanset(b):
    s = {0}
    for v in b: s |= {x ^ v for x in s}
    return frozenset(s)

def ent(js): return sum(j * math.log(j) for j in js if j > 1)


# ---------------------------------------------------------------- OWNEDRANK (copy of OWNEDRANK/gen2c/ownend.py)
def roots_of(d, n):
    fr = d['frames']; out = {}; ops = d['ops']
    for i, o in enumerate(ops):
        op, r, s = o[0], o[1], o[2]
        if op == 'INIT' and r >= n: out[r] = dict(O=r, init=i, H=o[4], gath=[], reads=[], clear=None)
        elif op in ('ADD', 'COPY') and r >= n and s is not None and s < n: out[r]['gath'].append(i)
        elif op in ('ADD', 'COPY') and s is not None and s >= n: out[s]['reads'].append(i)
        elif op == 'CLEAR' and r >= n: out[r]['clear'] = i
    for R in out.values():
        assert len(R['reads']) == 1, ('root with several reads', R)
        R['line'] = ops[R['reads'][0]][4]; R['l'] = fr[R['line']][0]
    return out

def xreplay(ops, n, no, role):
    X = [({r: Q(1)} if role(r) == 'X' else {}) for r in range(n)] + [{} for _ in range(no)]
    lastx = {}; lasti = {}
    for i, o in enumerate(ops):
        op, r, s, q = o[0], o[1], o[2], o[3]
        if op in ('INIT', 'CLEAR'): X[r] = {}
        elif op == 'SCALE': X[r] = {c: v * Q(q) for c, v in X[r].items()}
        elif op == 'COPY': X[r] = {c: v * Q(q) for c, v in X[s].items()}
        else: addf(X[r], X[s], Q(q))
        if op in ('INIT', 'CLEAR'): continue
        for x in ([r, s] if op in ('ADD', 'COPY') else [r]):
            if x is not None: lastx[x] = dict(X[x]); lasti[x] = i
    return X, lastx, lasti

def park(w, plan):
    """plan {root O: [frames]} -> (new word with the root parked on those frames (nested), {(O,g): parked register})."""
    import dag as D
    d = D.decompile(w, forms=False); n = d['meta']['npub']; no = d['meta']['nowned']; fr = d['frames']
    SP = [spanset(b) for b in fr]
    R = roots_of(d, n); ops = [list(o) for o in d['ops']]
    nxt = n + no; ins = collections.defaultdict(list); parked = {}; repl = {}
    f9 = max(range(len(fr)), key=lambda f: len(fr[f]))
    first_f9 = next(i for i, o in enumerate(ops) if o[0] == 'ADD' and o[4] == f9)
    tail = []
    for O, gs in sorted(plan.items()):
        r = R[O]; gs = sorted(set(gs), key=lambda g: -len(fr[g]))
        chain = [r['H']] + gs + [r['line']]
        for a, b in zip(chain, chain[1:]):
            if not (SP[b] <= SP[a]) or len(fr[b]) >= len(fr[a]): raise SystemExit('park: frames not a strict descending chain %s' % chain)
        last = max(r['gath']) if r['gath'] else r['init']
        holder = O
        for g in gs:
            N = nxt; nxt += 1
            ins[last] += [['INIT', N, None, None, g, None], ['COPY', N, holder, '1', g, None]]
            parked[(O, g)] = holder; holder = N
        repl[r['reads'][0]] = holder; repl[r['clear']] = holder
        for g in gs: tail.append(['CLEAR', parked[(O, g)], None, None, g, None])
    new = []
    for i, o in enumerate(ops):
        if i == first_f9: new += tail
        if i in repl:
            if o[0] == 'CLEAR': o[1] = repl[i]
            else: o[2] = repl[i]
        new.append(o); new += ins.get(i, [])
    d2 = dict(d); d2['ops'] = new; d2['regs'] = {k: list(v) for k, v in d['regs'].items()}
    meta = dict(d['meta']); meta['nowned'] = nxt - n
    if 'owned_fields' in meta: meta['owned_fields'] = nxt - n
    d2['meta'] = meta
    for r_ in range(n + no, nxt): d2['regs'][str(r_)] = ['owned', None, None]
    w2, rep = D.realise(d2, schedule='lazy', verify=True)
    if rep['undelivered']: raise SystemExit('park: undelivered %s' % (rep['undelivered'][:3],))
    vp = dict(w.get('verifier_profile') or {}); vp['owned_fields'] = nxt - n
    w2['verifier_profile'] = vp
    return w2, parked, rep


# ---------------------------------------------------------------- replay index (copy of FANIN/fplan.Pre; TWINBOTTOM prep/windows)
class Pre:
    def __init__(s, c):
        s.c = c; n = c.n; role = c.role; body = c.body
        s.B = [rref(b) for b in c.d['frames']]
        X = {r: ({r: Q(1)} if r < n and role(r) == 'X' else {}) for r in range(n + c.no)}
        ver = collections.defaultdict(list); opsof = collections.defaultdict(list)
        for r in range(n): ver[r].append((-1, dict(X[r])))
        for i, o in enumerate(body):
            op, r, src, q, f = o[:5]
            if op == 'ADD': addf(X[r], X[src], Q(q))
            elif op == 'COPY': X[r] = {k: v * Q(q) for k, v in X[src].items()}
            elif op in ('INIT', 'CLEAR'): X[r] = {}
            elif op == 'SCALE': X[r] = {k: v * Q(q) for k, v in X[r].items()}
            if r < n: ver[r].append((i, dict(X[r]))); opsof[r].append((i, f))
            if op in ('ADD', 'COPY') and src is not None and src < n: opsof[src].append((i, f))
        s.ver = ver; s.opsof = opsof
        s.win = []          # (r, A, Bf, i_lastA, t_firstB, rdims, k-th window)
        for r in range(n):
            if role(r) == 'Y': continue
            for k, wd in enumerate(s.windows(r)): s.win.append(wd)
    def windows(s, r):
        c = s.c; seq = []
        for i, f in s.opsof[r]:
            if not seq or seq[-1][0] != f: seq.append([f, i, i])
            else: seq[-1][2] = i
        seq = [[c.init[r], -1, -1]] + seq if (not seq or seq[0][0] != c.init[r]) else seq
        fin = c.d['regs'][str(r)][2]
        rdims = [c.dim[c.init[r]]] + [c.dim[f] for _, f in s.opsof[r]] + [c.dim[fin]]
        out = []
        for k, (A, i0, i1) in enumerate(seq):
            Bf, t1 = (seq[k + 1][0], seq[k + 1][1]) if k + 1 < len(seq) else (fin, len(c.body))
            if Bf != A: out.append((r, A, Bf, i1, t1, rdims))
        return out
    def vat(s, r, t):
        cc = {}
        for tt, x in s.ver[r]:
            if tt <= t: cc = x
            else: break
        return cc
    def rider(s, h):
        import kernel2net as KN
        c = s.c; dim = c.dim
        if not s.opsof[h]: return None
        th, g = s.opsof[h][-1]; v = {k: x for k, x in s.vat(h, th).items() if c.role(k) == 'X'}
        fin = c.d['regs'][str(h)][2]
        hd = [dim[c.init[h]]] + [dim[f] for _, f in s.opsof[h]] + [dim[fin]]
        return dict(h=h, th=th, g=g, v=v, base=KN.tax_dims(hd), keep=[x for x in hd if x <= dim[g]], hd=hd)

    def plan_relay(s, h, dmax=8, maxh=3, allow=None):
        """DEADRIDERS mile.plan / FANIN fplan.plan: cheapest frame M (dim <= dmax) and <= maxh routed holders cleaning rider h."""
        import kernel2net as KN
        c = s.c; dim = c.dim; B = s.B
        ri = s.rider(h)
        if ri is None or not ri['v']: return None
        th, g, v = ri['th'], ri['g'], ri['v']
        cands = []
        for (r, A, Bf, i1, t1, rdims) in s.win:
            if r == h or t1 <= th: continue
            if allow is not None and r not in allow: continue
            cc = s.vat(r, i1)
            if not cc or not set(cc) & set(v): continue
            M1 = rref(list(B[g]) + list(B[A]))
            if len(M1) > dmax or not sub(M1, B[Bf]) or dim[Bf] <= dim[g]: continue
            cands.append((r, A, Bf, i1, t1, cc, rdims))
        best = None
        for k in range(1, maxh + 1):
            for S in itertools.combinations(cands, k):
                if len({x[0] for x in S}) < k: continue
                M = rref(list(B[g]) + [x for y in S for x in B[y[1]]]); dM = len(M)
                if dM > dmax or dM <= dim[g]: continue
                if not all(dim[y[1]] <= dM < dim[y[2]] and sub(M, B[y[2]]) for y in S): continue
                tins = max([th] + [y[3] for y in S])
                if tins >= min(y[4] for y in S): continue
                sol = solve(v, [y[5] for y in S])
                if sol is None: continue
                co = {S[j][0]: a for j, a in sol.items() if a}
                if not all(dy(a) for a in co.values()): continue
                cost = sum((KN.tax_dims(y[6] + [dM]) - KN.tax_dims(y[6])) if dim[y[1]] < dM else 0.0 for y in S if y[0] in co)
                sav = ri['base'] - KN.tax_dims(ri['keep'] + [dM]); net = sav - cost
                if best is None or net > best['net']:
                    best = dict(h=h, M=M, dM=dM, tins=tins, co=co, net=net, sav=sav, cost=cost,
                                stops={y[0]: (y[1], y[2], y[3]) for y in S if y[0] in co and dim[y[1]] < dM})
            if best: break
        return best

    def plan_hub(s, riders, holders, Mb=None):
        """TWINBOTTOM hubmile.plan_hub: all riders against one shared holder set at M; one split per holder."""
        import kernel2net as KN
        c = s.c; B = s.B; dim = c.dim
        rinfo = [s.rider(h) for h in riders]
        if any(r is None for r in rinfo): raise SystemExit('hub: rider without ops')
        M = rref(list(Mb)) if Mb else rref([x for ri in rinfo for x in B[ri['g']]])
        dM = len(M); tmax = max(ri['th'] for ri in rinfo)
        hw = {}
        for r in holders:
            for (r_, A, Bf, i1, t1, rd) in s.windows(r):
                if t1 <= tmax: continue
                cc = s.vat(r, i1)
                if dim[A] <= dM < dim[Bf] and sub(B[A], M) and sub(M, B[Bf]) and cc:
                    cost = 0.0 if dim[A] == dM else KN.tax_dims(rd + [dM]) - KN.tax_dims(rd)
                    hw[r] = dict(A=A, Bf=Bf, i1=i1, t1=t1, cc=cc, cost=cost); break
        missing = [r for r in holders if r not in hw]
        if missing: raise SystemExit('hub: holders without a window through M: %s' % missing)
        tins = max([ri['th'] for ri in rinfo] + [x['i1'] for x in hw.values()])
        if tins >= min(x['t1'] for x in hw.values()): raise SystemExit('hub: no common time slot')
        hs = list(hw); use = collections.Counter(); plans = []
        for ri in rinfo:
            sol = solve(ri['v'], [hw[r]['cc'] for r in hs])
            if sol is None: raise SystemExit('hub: rider %d not covered' % ri['h'])
            co = {hs[j]: a for j, a in sol.items() if a}
            if not all(dy(a) for a in co.values()): raise SystemExit('hub: non-dyadic cover for %d' % ri['h'])
            for r in co: use[r] += 1
            plans.append(dict(h=ri['h'], co=co, sav=ri['base'] - KN.tax_dims(ri['keep'] + [dM])))
        cost = sum(hw[r]['cost'] for r in use); sav = sum(p['sav'] for p in plans)
        stops = {r: (hw[r]['A'], hw[r]['Bf'], hw[r]['i1']) for r in use if hw[r]['cost'] > 0}
        return dict(M=M, dM=dM, tins=tins, plans=plans, cost=cost, sav=sav, net=sav - cost, mult=dict(use), stops=stops)


# ---------------------------------------------------------------- spec parsing
def parse(specs):
    out = []
    for s in specs:
        for part in [x for x in s.replace(';', ' ').split() if x]:
            kind, _, arg = part.partition(':')
            if kind not in ('own', 'hub', 'relay', 'skip'): raise SystemExit('unknown lever %r (own, hub, relay, skip)' % part)
            out.append((kind, arg))
    return out


class Ledger:
    """resources consumed by enders: riders (exclusive), holder windows -> new-stop frame (one frame per window), root park frames."""
    def __init__(s): s.riders = {}; s.stops = {}; s.log = []
    def take(s, lever, riders, stops):
        bad = [('rider', h, s.riders[h]) for h in riders if h in s.riders]
        for key, M in stops.items():
            if key in s.stops and s.stops[key][0] != M: bad.append(('stop', key, s.stops[key][1]))
        if bad: s.log.append(dict(lever=lever, conflict=bad)); return False
        for h in riders: s.riders[h] = lever
        for key, M in stops.items(): s.stops.setdefault(key, (M, lever))
        return True


def read_by_xo(c):
    """helpers read by an X main or an owned register (purex.Ctx.census 'bad'): their content is in an X/O final, so they cannot end early."""
    bad = set()
    for o in c.body:
        if o[0] in ('ADD', 'COPY') and o[2] is not None and c.role(o[1]) in ('X', 'O') and c.role(o[2]) == 'H': bad.add(o[2])
    return bad


def own_auto_plan(w, census_riders, maxroot=8):
    """greedy OWNEDRANK census on EXISTING frames: rider h (H, born 0, not a census ender), last body op at g, root k with l_k in g and g inside H_k,
    x(h) dyadic multiple of x(R_k); net = chain-cut saving - incremental staging entropy of the root's nested chain."""
    import kernel2net as KN, dag as D
    c = PX.Ctx(w); n = c.n; P = Pre(c); dim = c.dim
    d0 = c.d; R = roots_of(d0, n); fr = d0['frames']; SP = [spanset(b) for b in fr]
    _, lastx, _ = xreplay(c.body, n, c.no, c.role)
    Rx = {O: lastx.get(O, {}) for O in R}
    cand = []; xo = read_by_xo(c)
    for h in range(n):
        if c.role(h) != 'H' or c.init[h] != c.Z or h in census_riders or h in xo: continue
        ri = P.rider(h)
        if ri is None or not ri['v']: continue
        g = ri['g']
        if ri['hd'][-1] != max(dim) or dim[g] >= 8: continue
        for O, r in R.items():
            if r['l'] not in SP[g] or not SP[g] <= SP[r['H']] or g == r['H'] or not Rx[O]: continue
            xr = Rx[O]; k0 = next(iter(xr)); al = ri['v'].get(k0, 0) / xr[k0]
            res = dict(ri['v']); addf(res, xr, -al)
            if res or not dy(al): continue
            cand.append(dict(h=h, g=g, O=O, sav=ri['base'] - KN.tax_dims(ri['keep'])))
    chains = collections.defaultdict(set); plan = []
    def stagecost(O, gs):
        top = dim[R[O]['H']]; ds = [top] + sorted({dim[g] for g in gs}, reverse=True) + [1]
        return ent([top - 1]) - ent([a - b for a, b in zip(ds, ds[1:])])
    while True:
        best = None
        for x in cand:
            if any(p['h'] == x['h'] for p in plan): continue
            gs = chains[x['O']] | {x['g']}
            ordered = sorted(gs, key=lambda g: -dim[g])
            ok = len({dim[g] for g in gs}) == len(gs) and all(SP[b] <= SP[a] for a, b in zip(ordered, ordered[1:]))
            if not ok: continue
            net = x['sav'] - (stagecost(x['O'], gs) - stagecost(x['O'], chains[x['O']]))
            if net > 1e-9 and (best is None or net > best[0]): best = (net, x)
        if best is None: break
        net, x = best; chains[x['O']].add(x['g']); plan.append(dict(x, net=net))
    return plan


def stack(w, specs, dims=None, xstops=True, verbose=True, _retry=False):
    """apply the lever specs to route-B word w -> (dag ready to realise via c.D.realise, report).  Empty specs == purex2.main exactly."""
    import dag as D
    L = parse(specs); rep = dict(levers=[], conflicts=[], skipped=[])
    skip = set()
    for k, a in L:
        if k == 'skip': skip |= {int(x) for x in a.split(',') if x}
    # 1. owned parks (transform the word first; rider/holder ids are public and unchanged)
    c_pre = PX.Ctx(w)
    cen0 = {e['h'] for e in c_pre.census(xstops=xstops, dims=dims)} - skip
    own = []
    for k, a in L:
        if k != 'own': continue
        if a == 'auto' or a.startswith('auto'):
            for p in own_auto_plan(w, cen0 | {h for h, _ in own}): own.append((p['h'], p['g'])); rep['levers'].append(dict(kind='own', auto=True, h=p['h'], g=p['g'], root=p['O'], net_model=round(p['net'], 3)))
        else:
            h, g = (int(x) for x in a.split('@')); own.append((h, g))
            if not any(x.get('h') == h and x['kind'] == 'own' for x in rep['levers']): rep['levers'].append(dict(kind='own', h=h, g=g))
    ld = Ledger()
    for h in cen0: ld.riders[h] = 'purex2-census'
    w1 = w; parked = {}; who = {}
    if own:
        d0 = D.decompile(w, forms=False); n = d0['meta']['npub']; R = roots_of(d0, n); SP = [spanset(b) for b in d0['frames']]
        plan = collections.defaultdict(list)
        for h, g in own:
            ks = [O for O, r in R.items() if r['l'] in SP[g] and SP[g] <= SP[r['H']]]
            if len(ks) != 1: rep['conflicts'].append(dict(lever='own:%d@%d' % (h, g), conflict='roots %s' % ks)); continue
            if not ld.take('own:%d@%d' % (h, g), [h], {}): continue
            plan[ks[0]].append(g); who[h] = (ks[0], g)
        if plan:
            w1, parked, prep = park(w, plan)
            rep['park_value_errors'] = len(prep['value_errors'])
    w1 = dict(w1); w1['frames'] = [list(b) for b in w1['frames']]
    c0 = PX.Ctx(w1)
    en = [e for e in c0.census(xstops=xstops, dims=dims) if e['h'] not in skip]
    rep['skipped'] = sorted(skip)
    if verbose: print('census enders', len(en), dict(collections.Counter(c0.dim[e['f']] for e in en)), flush=True)
    P = Pre(c0); spans = {rref(b): i for i, b in enumerate(w1['frames'])}
    def frame_of(M):
        f = spans.get(M)
        if f is None: f = len(w1['frames']); w1['frames'].append(list(M)); spans[M] = f
        return f
    extra = []
    # 2. owned enders
    if who:
        Xe, lastx, lasti = xreplay(c0.body, c0.n, c0.no, c0.role)
        for h, (O, g) in who.items():
            P_ = parked[(O, g)]; xr = lastx[P_]; xh = lastx[h]
            k0 = next(iter(xr)); alpha = xh.get(k0, 0) / xr[k0]
            resid = dict(xh); addf(resid, xr, -alpha)
            if resid or not dy(alpha): raise SystemExit('own: rider %d x not proportional to root (alpha %s, residue %d)' % (h, alpha, len(resid)))
            tcopy = max(i for i, o in enumerate(c0.body) if o[0] == 'COPY' and o[2] == P_)
            t = max(lasti[h], tcopy)
            extra.append(dict(h=h, t=t, f=g, use=[(P_, -alpha, t)]))
            if verbose: print('own ender', h, 'frame', g, 'dim', c0.dim[g], 'root', O, 'parked', P_, 'alpha', alpha, flush=True)
    # 3. hubs and relays (plans on c0; new M frames appended to w1)
    for k, a in L:
        if k == 'hub':
            body, _, mb = a.partition('@'); rs, _, hs = body.partition('/')
            riders = [int(x) for x in rs.split(',')]; holders = [int(x) for x in hs.split(',')]
            Mb = [int(x) for x in mb.split(',')] if mb else None
            try: p = P.plan_hub(riders, holders, Mb=Mb)
            except SystemExit as e: rep['conflicts'].append(dict(lever='hub:' + a, conflict=str(e))); continue
            stops = {(r,) + st[:2]: p['M'] for r, st in p['stops'].items()}
            if not ld.take('hub:' + a, riders, stops): continue
            f = frame_of(p['M'])
            extra += [dict(h=q['h'], t=p['tins'], f=f, use=[(R_, -x, p['tins']) for R_, x in q['co'].items()]) for q in p['plans']]
            rep['levers'].append(dict(kind='hub', riders=riders, holders=holders, dM=p['dM'], net_model=round(p['net'], 3)))
        elif k == 'relay':
            parts = a.split(':'); dmax = int(parts[1]) if len(parts) > 1 else 8
            xo = read_by_xo(c0)
            hs = [h for h in range(c0.n) if c0.role(h) == 'H' and c0.init[h] == c0.Z and h not in xo] if parts[0] == 'auto' else [int(parts[0])]
            plans = []
            for h in hs:
                if h in ld.riders: continue
                if parts[0] == 'auto':
                    ri = P.rider(h)
                    if ri is None or not ri['v'] or c0.dim[ri['g']] >= dmax - 1: continue
                p = P.plan_relay(h, dmax=dmax, maxh=2 if parts[0] == 'auto' else 3)
                if p is None: continue
                if parts[0] == 'auto' and p['net'] <= 1e-9: continue
                plans.append(p)
            for p in sorted(plans, key=lambda p: -p['net']):
                stops = {(r,) + st[:2]: p['M'] for r, st in p['stops'].items()}
                if not ld.take('relay:%d' % p['h'], [p['h']], stops): continue
                f = frame_of(p['M'])
                extra.append(dict(h=p['h'], t=p['tins'], f=f, use=[(R_, -x, p['tins']) for R_, x in p['co'].items()]))
                rep['levers'].append(dict(kind='relay', h=p['h'], dM=p['dM'], net_model=round(p['net'], 3), auto=parts[0] == 'auto'))
    rep['conflicts'] += ld.log
    en_all = en + extra
    import signal
    def _alarm(*_): raise SystemExit('purex2 joint solve timed out (%d s; realise_Z fixpivot hang, GEN2SWEEP mode 3)' % tlim)
    tlim = 90
    def run_t(enders, vb):
        """P2.run with a wall limit when extra enders are present (purex2 can hang in realise_Z on some ender sets)."""
        if not extra or not hasattr(signal, 'SIGALRM'): return P2.run(w1, enders, verbose=vb)
        old_h = signal.signal(signal.SIGALRM, _alarm); signal.alarm(tlim)
        try: return P2.run(w1, enders, verbose=vb)
        finally: signal.alarm(0); signal.signal(signal.SIGALRM, old_h)
    def attempt(enders, vb):
        c_, body_, f9_, zops_, _ = run_t(enders, vb)
        return c_, P2.finish(c_, body_, f9_, zops_, {e['h']: e for e in enders}, verbose=vb)
    try: c, ops = attempt(en_all, verbose)
    except SystemExit as ex:
        # an extra ender breaks the joint dim-0 solve or the F9 fix: keep the extras greedily, one at a time
        if not extra: raise
        rep['conflicts'].append(dict(lever='joint-solve', conflict=str(ex)[:200])); keep = []
        for e in extra:
            try: attempt(en + keep + [e], False); keep.append(e)
            except SystemExit as ex2: rep['conflicts'].append(dict(lever='ender %d' % e['h'], conflict='dropped: ' + str(ex2)[:160]))
        extra = keep; en_all = en + extra
        lost = [h for h in who if h not in {e['h'] for e in extra}]
        if lost and not _retry:
            # a dropped OWNED ender would leave its root parked for nothing (staging cost, no saving): rebuild without those parks
            keep_own = ['own:%d@%d' % (h, who[h][1]) for h in who if h not in lost]
            rest = [x for x in specs if not any(p.startswith('own:') for p in x.replace(';', ' ').split())]
            c2, dag2, w2, rep2 = stack(w, keep_own + rest, dims=dims, xstops=xstops, verbose=verbose, _retry=True)
            rep2['conflicts'] = rep['conflicts'] + rep2['conflicts'] + [dict(lever='own', conflict='re-stacked without parks for dropped owned enders %s' % lost)]
            rep2['levers'] = [x for x in rep['levers'] if not (x['kind'] == 'own' and x.get('h') in lost)]
            return c2, dag2, w2, rep2
        c, ops = attempt(en_all, verbose)
    E = {e['h']: e for e in en_all}
    bad = [o for o in ops if o[0] == 'ADD' and not dy(o[3])]
    if bad: raise SystemExit('LEVERBANK: non-dyadic %s' % bad[:4])
    dag = dict(c.d); dag['ops'] = ops; dag['regs'] = {k_: list(v) for k_, v in c.d['regs'].items()}
    for h, e in E.items(): dag['regs'][str(h)][2] = e['f']
    rep['enders'] = len(en_all); rep['census'] = len(en); rep['extra'] = len(extra); rep['kept'] = [e['h'] for e in extra]
    kp = set(rep['kept'])
    for x in rep['levers']: x['kept'] = (x['h'] in kp) if 'h' in x else all(h in kp for h in x.get('riders', []))
    return c, dag, w1, rep
