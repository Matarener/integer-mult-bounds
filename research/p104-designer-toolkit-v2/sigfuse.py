"""sigfuse.py IN OUT [--no-price] [--max-lifetimes N]      word -> word post-pass: fuse the owned-register SIGNAL into the mains (SIGFUSE, Oct 27).
Scope [toolkit GENERATOR post-pass / signal fusion].  No env at import; main() sets TK_FREE_BOUNDS=1 like real.py (generated words need new-value literals).

WHAT IT DOES for the derivation):
  A STAR copy u(j,k) is a private helper 0 -> <l_k> (reads 2C_jk root_k) -> Q_j (Y_j reads it) -> F9 (T-trick restore): chain (0,1,8,9), R0 = 9 ln 9 - 7 ln 7 = 6.15.
  R0 law: R0(reg) = D ln D - sum r ln r = D * H(jumps/D).  A NEW register pays its whole D-entropy; a new STOP on an existing register only pays the entropy of
  splitting one jump, r ln r - a ln a - b ln b, and nothing if it lands on an existing stop.  So the signal is carried by the reader itself:
  Y_j (single jump 0 -> Q_j) stops ONCE at a line <v_j>, v_j in Q_j and in every H_k it reads (v_j perp p_j and u_k for all k in K_j; always exists since
  dim <p_j,u_K>^perp = 8-|K_j| >= 2), and reads ALL its roots there: Y_j += 2C_jk root_k.  Cost 8 ln 8 - 7 ln 7 = 3.01 per Y for |K_j| = 3..6 copies.
  An owned root's chain is one jump H_k -> <v> (R0 0) but must be NESTED; lines of different readers are not nested, so root k gets one LIFETIME per distinct
  line among its readers (refill from the same feeders: events only, R0 0).  Lines are chosen by greedy set cover to share lifetimes.
  Value preservation: copies are deleted (all their ops), Y's residual reads that preceded the root block are moved after it (checked commuting: the source is
  not written in between), dim-0 junk loads are stripped and RE-SOLVED by exact replay (Y_j += -J h at frame 0, every helper born at frame 0).
API: fuse(w, max_lifetimes=None) -> (word, report).  Generators call it on any word whose signal is STAR copies (helper reads root once, read once by one Y)."""
import sys, os, json, gzip, math, collections, itertools
from fractions import Fraction as Q
HERE = os.path.dirname(os.path.abspath(__file__))
for p in (HERE, os.path.join(HERE, 'synth')):
    if p not in sys.path: sys.path.insert(0, p)
import dag as D

par = lambda a, b: bin(a & b).count('1') & 1

def _span(b):
    s = {0}
    for v in b: s |= {x ^ v for x in s}
    return s

def _perp_of(basis):
    return [x for x in range(1, 512) if all(par(x, y) == 0 for y in basis)]

def fuse(w, max_lifetimes=None, verbose=True, mode='one', prune=True):
    d = D.decompile(w, forms=False)
    meta = d['meta']; n = meta['npub']; live = set(meta['live']); ops = [list(o) for o in d['ops']]
    fr = d['frames']; dim = lambda f: len(fr[f]) if isinstance(f, int) else len(f)
    isY = lambda r: r < n and (r - 112) in live
    isH = lambda r: r < n and r not in live and not isY(r)
    rep = collections.OrderedDict()
    # ---- roots and root block
    inits = [i for i, o in enumerate(ops) if o[0] == 'INIT']; clears = [i for i, o in enumerate(ops) if o[0] == 'CLEAR']
    b0, b1 = inits[0], clears[-1]
    roots = collections.OrderedDict()
    for i in inits:
        r = ops[i][1]; j = next(c for c in clears if c > i and ops[c][1] == r)
        roots.setdefault(r, []).append((i, j))
    assert all(len(v) == 1 for v in roots.values()), 'sigfuse: one lifetime per root expected on input'
    H = {r: ops[v[0][0]][4] for r, v in roots.items()}
    u = {r: _perp_of(fr[H[r]])[0] for r in roots}
    fills = {r: [ops[t] for t in range(i, j) if ops[t][0] == 'ADD' and ops[t][1] == r] for r, [(i, j)] in roots.items()}
    # ---- STAR copies: helper reads one root once, is read by exactly one Y at dim>0; every other op of it is at dim 0 or at the end frame (restore)
    touch = collections.defaultdict(list)
    for i, o in enumerate(ops):
        if o[0] in ('ADD', 'COPY'):
            touch[o[1]].append(i); touch[o[2]].append(i)
    F9 = max(range(len(fr)), key=lambda f: len(fr[f]))
    copies = {}
    for i, o in enumerate(ops):
        if o[0] == 'ADD' and o[2] in roots and isH(o[1]):
            c = o[1]; rd = [t for t in touch[c] if ops[t][2] == c and isY(ops[t][1]) and dim(ops[t][4]) > 0]
            own = [t for t in touch[c] if ops[t][2] in roots]
            other = [t for t in touch[c] if t not in rd and t not in own and not (dim(ops[t][4]) == 0 or ops[t][4] == F9)]
            if len(rd) == 1 and len(own) == 1 and not other:
                copies[c] = dict(k=o[2], coef=Q(o[3]) * Q(ops[rd[0]][3]), y=ops[rd[0]][1], tread=rd[0])
    rep['roots'] = len(roots); rep['star_copies'] = len(copies)
    # ---- Y's residual reads before the root block must move after it: check commuting
    written_after = collections.defaultdict(list)
    for i, o in enumerate(ops):
        if o[0] in ('ADD', 'COPY', 'SCALE', 'INIT', 'CLEAR'): written_after[o[1]].append(i)
    late = []; bad_y = set()
    for i in range(b0):
        o = ops[i]
        if o[0] == 'ADD' and isY(o[1]) and dim(o[4]) > 0:
            s = o[2]
            if any(i < t <= b1 for t in written_after[s]): bad_y.add(o[1])
            late.append(i)
    K = collections.defaultdict(dict)
    for c, v in copies.items():
        if v['y'] not in bad_y: K[v['y']][v['k']] = (c, v['coef'])
    groups = collections.defaultdict(lambda: collections.defaultdict(list))   # root -> line -> [(y, coef)]
    line = {}; elim = set()
    if mode == 'multi':
        # lines: v perp p_j and u_k (k in K_j); greedy cover for shared lifetimes.  ONE stop hosts all K_j, but costs extra owned lifetimes (see notes: priced fatal)
        pj = {y: meta['ports'][sorted(live).index(y - 112)] for y in K}
        cand = {y: set(x for x in range(1, 512) if par(x, pj[y]) == 0 and all(par(x, u[k]) == 0 for k in K[y])) for y in K}
        todo = set(K)
        while todo:
            best = max(range(1, 512), key=lambda x: (sum(1 for y in todo if x in cand[y]), -x))
            grp = [y for y in todo if best in cand[y]]
            if not grp: break
            for y in grp: line[y] = best
            todo -= set(grp)
        for y, kk in K.items():
            if y not in line: continue
            for k, (c, q) in kk.items(): groups[k][line[y]].append((y, q)); elim.add(c)
    else:
        elim_pending = set(copies)
        # mode 'one': one lifetime per root (owned descents are paid without credit).  Every frame on root k's chain contains l_k and u_k'.l_k = 1 for k' != k,
        # so a climbing register can host at most ONE root: Y_j hosts one of its roots at <l_k> (its chain 0 -> <l_k> -> Q_j).
        load = collections.Counter()
        firstf = {}                                   # Y's first frame after the root block (dim>0): the host stop <l_k> must lie inside it
        for i in sorted(set(late)) + list(range(b1 + 1, len(ops))):
            o = ops[i]
            if o[0] in ('ADD', 'COPY') and isY(o[1]) and dim(o[4]) > 0 and o[1] not in firstf and o[2] not in elim_pending: firstf[o[1]] = o[4]
        for y, kk in sorted(K.items()):
            ok = [k for k in kk if y not in firstf or set(_span(fr[ops[roots[k][0][1]][4]])) <= _span(fr[firstf[y]])]
            if not ok: continue
            k = min(ok, key=lambda k: (load[k], k)); load[k] += 1
            c, q = kk[k]
            groups[k]['bottom'].append((y, q)); elim.add(c); line[y] = k
    rep['hosting_Y'] = len(line); rep['eliminated_copies'] = len(elim)
    rep['lifetimes'] = len(roots) if mode == 'one' else sum(len(g) for g in groups.values()) + sum(1 for r in roots if any(cv['k'] == r and c not in elim for c, cv in copies.items()))
    if max_lifetimes and rep['lifetimes'] > max_lifetimes: raise SystemExit('sigfuse: %d lifetimes > cap %d' % (rep['lifetimes'], max_lifetimes))
    # ---- rebuild the op list
    def keep(o):
        if o[0] in ('ADD', 'COPY') and (o[1] in elim or o[2] in elim): return False
        if o[0] == 'ADD' and isY(o[1]) and dim(o[4]) == 0: return False        # junk loads: re-solved below
        return True
    lateset = set(late) if line else set()
    pre = [ops[i] for i in range(b0) if i not in lateset and keep(ops[i])]
    blk = []; prevj = b0 - 1
    for r, [(i, j)] in sorted(roots.items(), key=lambda kv: kv[1][0][0]):
        blk += [ops[t] for t in range(prevj + 1, i) if keep(ops[t])]          # ops between root windows (e.g. STAR carriers of the next root)
        prevj = j
        mid = [ops[t] for t in range(i + 1, j) if keep(ops[t]) and not (ops[t][0] == 'ADD' and ops[t][1] == r)]   # surviving copy reads + non-root ops
        rest_reads = [o for o in mid if o[0] == 'ADD' and o[2] == r]
        others = [o for o in mid if not (o[0] == 'ADD' and o[2] == r)]
        blk += others
        hosted = groups.get(r, {})
        if mode == 'one':
            bf = ops[j][4]
            blk += [['INIT', r, None, None, H[r], None]] + [list(f) for f in fills[r]] + rest_reads
            blk += [['ADD', y, r, str(q), bf, None] for (y, q) in hosted.get('bottom', [])] + [['CLEAR', r, None, None, bf, None]]
            continue
        if rest_reads:
            blk += [['INIT', r, None, None, H[r], None]] + [list(f) for f in fills[r]] + rest_reads + [['CLEAR', r, None, None, ops[j][4], None]]
        for v, ys in sorted(hosted.items()):
            blk += [['INIT', r, None, None, H[r], None]] + [list(f) for f in fills[r]]
            blk += [['ADD', y, r, str(q), [v], None] for (y, q) in ys]
            blk += [['CLEAR', r, None, None, [v], None]]
    post = [ops[i] for i in sorted(lateset) if keep(ops[i])] + [ops[i] for i in range(b1 + 1, len(ops)) if keep(ops[i])]
    body = pre + blk + post
    # ---- junk re-solve (exact replay)
    F, _ = D.apply_forms(body, meta); req = D.required(meta); junk = []; bad = []
    for r in range(n + meta['nowned']):
        diff = {c: F[r].get(c, 0) - req[r].get(c, 0) for c in set(F[r]) | set(req[r])}; diff = {c: v for c, v in diff.items() if v}
        if not diff: continue
        if isY(r) and all(isH(c) for c in diff):
            for c, v in sorted(diff.items()): junk.append(['ADD', r, c, str(-v), d['regs'][str(c)][1], None])
        else: bad.append((r, len(diff)))
    rep['junk_loads'] = len(junk); rep['undelivered_before_junk'] = bad[:10]
    dag2 = dict(d); dag2['ops'] = junk + body
    w2, rr = D.realise(dag2, schedule='lazy', verify=True)
    rep['undelivered'] = rr['undelivered'][:5]
    vp = dict(w.get('verifier_profile') or {}); vp['lifetimes'] = sum(1 for e in w2['program'] if e[0] == 'INIT')
    w2['verifier_profile'] = vp
    for k in ('owned_fields',):
        if k in w: w2[k] = w[k]
    if prune:      # freed copies are dead helpers now: drop them (LEGALIZE's value-preserving prune, renumbers; helper count is a hard cap <= 542)
        import legalize
        w2, removed = legalize.prune_dead_helpers(w2); rep['pruned_helpers'] = len(removed)
    nmain = 2 * len(live); rep['helpers'] = len(w2['initial']) - nmain; rep['public'] = len(w2['initial'])
    rep['events'] = len(w2['program'])
    return w2, rep

def _basis_of(sp):
    b = []; cur = {0}
    for v in sorted(sp):
        if v not in cur: b.append(v); cur |= {x ^ v for x in cur}
    return b

def _dy(q): return q.denominator & (q.denominator - 1) == 0

def fuse_share(w, prune=True, gen_frames=True, forced=None):
    """mode 'share' (round 2): phase reorder + SHARED hosts.
    1. phase 1 = the dependency cone of the root feeders, closed under non-commuting predecessors and chain nesting; phase 3 = every other pre-root op + the post-root ops.
       Roots live between them, so registers whose work is all in phase 3 are still at frame 0 while roots are alive.
    2. exact Y-propagation P_h of a value injected into h at the start of phase 3.  h hosts root k iff supp(P_h) are readers of k and P_h is proportional to their
       needed coefficients 2C_jk (dyadic ratio a): ONE stop <l_k> on h delivers root k to |supp| readers (signal shared through the residual network).
       Every host carries one root (section 4 law); disjoint supports per root; then each Y hosts one leftover root itself.
    3. residue of the injections in non-Y registers is cancelled at the end (all at F9) from clean registers; Y junk re-solved at frame 0."""
    import math
    d = D.decompile(w, forms=False)
    meta = d['meta']; n = meta['npub']; live = set(meta['live']); ops = [list(o) for o in d['ops']]; fr = d['frames']
    SP = [frozenset(_span(b)) for b in fr]
    spid = {}
    for i_, sp_ in enumerate(SP): spid.setdefault(sp_, i_)
    dim = lambda f: len(fr[f]); isY = lambda r: r < n and (r - 112) in live; isX = lambda r: r in live
    isH = lambda r: r < n and not isX(r) and not isY(r)
    f_ = lambda r: r * math.log(r) if r > 0 else 0.0
    rep = collections.OrderedDict()
    inits = [i for i, o in enumerate(ops) if o[0] == 'INIT']; clears = [i for i, o in enumerate(ops) if o[0] == 'CLEAR']; b0, b1 = inits[0], clears[-1]
    roots = collections.OrderedDict()
    for i in inits:
        r = ops[i][1]; roots[r] = (i, next(c for c in clears if c > i and ops[c][1] == r))
    H = {r: ops[i][4] for r, (i, j) in roots.items()}; bot = {r: ops[j][4] for r, (i, j) in roots.items()}
    lk = {r: fr[bot[r]][0] for r in roots}; assert all(dim(bot[r]) == 1 for r in roots)
    fills = {r: [list(ops[t]) for t in range(i, j) if ops[t][0] == 'ADD' and ops[t][1] == r] for r, (i, j) in roots.items()}
    feeders = set(o[2] for o in sum(fills.values(), []))
    # STAR copies
    touch = collections.defaultdict(list)
    for i, o in enumerate(ops):
        if o[0] in ('ADD', 'COPY'): touch[o[1]].append(i); touch[o[2]].append(i)
    F9 = max(range(len(fr)), key=lambda f: len(fr[f]))
    copies = {}
    for i, o in enumerate(ops):
        if o[0] == 'ADD' and o[2] in roots and isH(o[1]):
            c = o[1]; rd = [t for t in touch[c] if ops[t][2] == c and isY(ops[t][1]) and dim(ops[t][4]) > 0]
            other = [t for t in touch[c] if t not in rd and ops[t][2] not in roots and not (dim(ops[t][4]) == 0 or ops[t][4] == F9)]
            if len(rd) == 1 and not other and sum(1 for t in touch[c] if ops[t][2] in roots) == 1:
                copies[c] = dict(k=o[2], need=Q(o[3]) * Q(ops[rd[0]][3]), y=ops[rd[0]][1], qy=Q(ops[rd[0]][3]))
    need = collections.defaultdict(dict)
    for c, v in copies.items(): need[v['k']][v['y']] = (v['need'], c)
    junk = lambda o: o[0] == 'ADD' and isY(o[1]) and dim(o[4]) == 0
    pre = [i for i in range(b0) if not junk(ops[i]) and ops[i][0] in ('ADD', 'COPY')]
    assert all(ops[i][0] in ('ADD', 'COPY') or junk(ops[i]) for i in range(b0)), 'sigfuse share: unexpected op kind before the root block'
    # ---- 1. phase split
    cone = set(); nd = set(feeders)
    for i in reversed(pre):
        if ops[i][1] in nd: cone.add(i); nd.add(ops[i][2])
    seed = set(cone)
    for it in range(100):
        S = set(); WS = set(); RS = set()
        for i in reversed(pre):
            o = ops[i]
            if i in seed or o[1] in RS or o[2] in WS: S.add(i); WS.add(o[1]); RS.add(o[2])
        last = {}
        for i in sorted(S):
            for r in ops[i][1:3]: last[r] = ops[i][4]
        for r, fl in fills.items():
            for o in fl: last[o[2]] = o[4]          # feeders sit at H_k during the root block
        add = set(i for i in pre if i not in S and any(r in last and not SP[last[r]] <= SP[ops[i][4]] for r in ops[i][1:3]))
        if not add: break
        seed |= add
    else: raise SystemExit('sigfuse share: phase closure did not converge')
    P1 = sorted(S); P3 = [i for i in pre if i not in S] + [i for i in range(b1 + 1, len(ops))]
    rep['phase1_ops'] = len(P1); rep['phase3_pre_ops'] = len(pre) - len(P1)
    fprev = {}
    for i in P1:
        for r in ops[i][1:3]: fprev[r] = ops[i][4]
    fnext = {}
    for i in P3:
        if ops[i][0] in ('ADD', 'COPY'):
            for r in ops[i][1:3]: fnext.setdefault(r, ops[i][4])
    # ---- 2. exact Y-propagation from the start of phase 3
    PV = collections.defaultdict(dict)
    for i in reversed(P3):
        o = ops[i]
        if o[0] != 'ADD' or dim(o[4]) == 0 or o[1] in copies or o[2] in copies: continue
        dd, s_, q = o[1], o[2], Q(o[3])
        if isY(dd): PV[s_][dd] = PV[s_].get(dd, 0) + q
        else:
            for y, v in list(PV.get(dd, {}).items()):
                t = PV[s_].get(y, 0) + q * v
                if t: PV[s_][y] = t
                else: PV[s_].pop(y, None)
    readP1 = set(ops[i][2] for i in P1)          # read inside the feeder cone: an injected residue would reach the roots' own symbols (cyclic residue)
    cand = []
    for h, pv in PV.items():
        if not isH(h) or h in copies or not pv or h in feeders or h in readP1: continue
        fp = fprev.get(h); fn = fnext.get(h)
        if fn is None: continue
        A = SP[fp] if fp is not None else frozenset([0])
        for k in roots:
            t = need[k]
            if not set(pv) <= set(t) or not A <= SP[H[k]]: continue
            g = frozenset(A | {x ^ lk[k] for x in A})
            if not g <= SP[fn] or g == SP[fn]: continue
            if not gen_frames and len(A) > 1: continue
            da = int(math.log2(len(A))); dg = da + 1; db = dim(fn)
            cost = f_(db - da) - f_(dg - da) - f_(db - dg)
            for a in sorted(set(t[y][0] / pv[y] for y in pv)):
                if _dy(a): cand.append((k, h, pv, a, cost, g))
    rep["cand_options"] = len(cand); rep["cand_hosts"] = len(set(c[1] for c in cand)); rep["pv_regs"] = sum(1 for h, pv in PV.items() if isH(h) and pv and h not in copies); rep["pv_regs_readP1"] = sum(1 for h, pv in PV.items() if isH(h) and pv and h not in copies and h in readP1); rep["pv_regs_single_root"] = sum(1 for h, pv in PV.items() if isH(h) and pv and h not in copies and any(set(pv) <= set(need[k]) for k in roots))
    # greedy: an injection a*P_h adds to delivered[k][j]; reader j's copy is saved when delivered == need (non-exact readers keep a copy with the residual coefficient)
    dl = collections.defaultdict(lambda: collections.defaultdict(Q))
    usedh = set(); hosts = collections.defaultdict(list); chain = collections.defaultdict(list); sav = 0.0
    rootreg = {k: r for k, r in enumerate(roots)}                 # sign-code index k -> owned register (frontgen order)
    for h, k in sorted((forced or {}).items()):                     # builder-designated root sources c_k: read -4*root_k at <l_k> once
        r = rootreg[k]; ok = fprev.get(h) is None and h not in readP1 and h not in feeders and fnext.get(h) is not None and lk[r] in SP[fnext[h]]
        pv = PV.get(h, {}); extra = [y for y in pv if y not in need[r]]
        rep.setdefault('forced', []).append((h, k, ok, len(pv), len(extra)))
        if not ok or extra: continue
        usedh.add(h); hosts[r].append((h, Q(-4), SP[bot[r]]))
        for y, v in pv.items(): dl[r][y] += -4 * v
    def score(c):
        k, h, pv, a, cost, g = c; t = need[k]; dk = dl[k]; s_ = 0
        for y, v in pv.items():
            was = dk[y] == t[y][0]; now = dk[y] + a * v == t[y][0]
            s_ += (now and not was) - (was and not now)
        return 6.15 * s_ - cost
    live_c = list(cand)
    while True:
        live_c = [c for c in live_c if c[1] not in usedh and all(c[5] <= x or x <= c[5] for x in chain[c[0]])]
        if not live_c: break
        best = max(live_c, key=lambda c: (score(c), -c[1]))
        sc = score(best)
        if sc <= 0: break
        k, h, pv, a, cost, g = best
        usedh.add(h); hosts[k].append((h, a, g)); sav += sc
        if g not in chain[k]: chain[k].append(g)
        for y, v in pv.items(): dl[k][y] += a * v
    rep['root_chain_frames'] = {str(k): sorted(int(math.log2(len(g))) for g in v) for k, v in chain.items()}
    rep['helper_hosts'] = len(usedh)
    resid = {(k, y): need[k][y][0] - dl[k][y] for k in roots for y in need[k]}
    rep['helper_hosted_copies'] = sum(1 for v in resid.values() if v == 0)
    ny = 0
    for y in sorted(set(v['y'] for v in copies.values())):
        if fprev.get(y) is not None or fnext.get(y) is None: continue
        ks = [k for k in roots if y in need[k] and resid[(k, y)] != 0 and lk[k] in SP[fnext[y]]]
        if not ks: continue
        k = min(ks, key=lambda k: (len(hosts[k]), k)); hosts[k].append((y, resid[(k, y)], SP[bot[k]])); resid[(k, y)] = Q(0); ny += 1
    elim = set(need[k][y][1] for (k, y), v in resid.items() if v == 0)
    adj = {need[k][y][1]: v / copies[need[k][y][1]]['qy'] for (k, y), v in resid.items() if v != 0}   # surviving copies carry the residual
    rep['Y_hosts'] = ny; rep['eliminated_copies'] = len(elim); rep['model_saving_R0'] = round(sav + ny * 3.14, 1)
    for c, q in adj.items(): assert _dy(q)
    keep = lambda o: not (o[0] in ('ADD', 'COPY') and (o[1] in elim or o[2] in elim))
    body = [ops[i] for i in P1]; prevj = b0 - 1
    for r, (i, j) in roots.items():
        body += [list(ops[t]) for t in range(prevj + 1, i) if keep(ops[t])]      # ops between root windows (STAR carriers of the next root)
        prevj = j
        mid = [list(ops[t]) for t in range(i + 1, j) if keep(ops[t]) and not (ops[t][0] == 'ADD' and ops[t][1] == r)]
        for o in mid:
            if o[1] in adj: o[3] = str(adj[o[1]])
        assert all(o[0] == 'ADD' and o[2] == r for o in mid), 'sigfuse share: non-root op inside a root window'
        body += [['INIT', r, None, None, H[r], None]] + fills[r] + [['ADD', h, r, str(a), (spid[g] if g in spid else _basis_of(g)), None] for h, a, g in sorted(hosts[r], key=lambda t: -len(t[2])) if len(g) > 2] + mid + [['ADD', h, r, str(a), bot[r], None] for h, a, g in hosts[r] if len(g) == 2] + [['CLEAR', r, None, None, bot[r], None]]
    body += [ops[i] for i in P3 if keep(ops[i])]
    # ---- 3. corrections: non-Y residue at the end (F9), Y junk at frame 0
    F, _ = D.apply_forms(body, meta); req = D.required(meta)
    dev = {}
    for r in range(n + meta['nowned']):
        df = {c: F[r].get(c, 0) - req[r].get(c, 0) for c in set(F[r]) | set(req[r])}; df = {c: v for c, v in df.items() if v}
        if df: dev[r] = df
    jl = []; bad = []
    for r, df in list(dev.items()):
        if isY(r):
            if all(isH(c) for c in df):
                jl += [['ADD', r, c, str(-v), d['regs'][str(c)][1], None] for c, v in sorted(df.items())]; del dev[r]
            else: bad.append(r)
        elif r >= n: bad.append(r)
    if bad: raise SystemExit('sigfuse share: value error on Y/owned %s' % bad[:8])
    rep['Y_bad'] = bad[:8]; rep['junk_loads'] = len(jl); rep['corrected_regs'] = len(dev)
    fixes = []; todo = dict(dev)
    while todo:
        ready = [r for r, df in todo.items() if not any(c in todo for c in df)]
        if not ready: raise SystemExit('sigfuse share: cyclic residue (%d regs)' % len(todo))
        for r in ready:
            fixes += [['ADD', r, c, str(-v), F9, None] for c, v in sorted(todo[r].items())]; del todo[r]
    rep['correction_events'] = len(fixes)
    dag2 = dict(d); dag2['ops'] = jl + body + fixes
    w2, rr = D.realise(dag2, schedule='lazy', verify=True)
    rep['undelivered'] = rr['undelivered'][:5]
    vp = dict(w.get('verifier_profile') or {}); vp['lifetimes'] = sum(1 for e in w2['program'] if e[0] == 'INIT'); w2['verifier_profile'] = vp
    if 'owned_fields' in w: w2['owned_fields'] = w['owned_fields']
    if prune:
        import legalize
        w2, removed = legalize.prune_dead_helpers(w2); rep['pruned_helpers'] = len(removed)
    rep['helpers'] = len(w2['initial']) - 2 * len(live); rep['events'] = len(w2['program'])
    return w2, rep

def r0_by_role(w):
    import kernel2net as KN
    by, tot = KN.r0(w); return {k: round(v, 1) for k, v in by.items()}, tot

def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0]); ap.add_argument('inp'); ap.add_argument('out')
    ap.add_argument('--no-price', action='store_true'); ap.add_argument('--mode', default='one', choices=('one', 'multi', 'share')); ap.add_argument('--max-lifetimes', type=int); a = ap.parse_args(argv)
    os.environ.setdefault('TK_FREE_BOUNDS', '1')
    w = D.load(a.inp)
    w2, rep = fuse_share(w) if a.mode == 'share' else fuse(w, a.max_lifetimes, mode=a.mode)
    for k, v in rep.items(): print('%s: %s' % (k, v))
    print('R0 in ', r0_by_role(w)); print('R0 out', r0_by_role(w2))
    D.save(w2, a.out); print('wrote', a.out)
    if not a.no_price:
        import incr
        from tkcommon import profile_of
        iw = incr.IncrWord(w2, profile=profile_of(w)[0])
        print('legal', iw.legal_all, 'violations', len(iw.viol), 'bad native pairs', len(iw.bad_pairs), 'kappa %.13f' % iw.kappa)
        if iw.viol: print('first violations', iw.viol[:5])
    return 0

if __name__ == '__main__': sys.exit(main())
