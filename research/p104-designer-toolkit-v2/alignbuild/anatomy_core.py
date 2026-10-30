"""alignbuild.anatomy_core -- per-side ledger of ANY word of the octet class (BULKGEN; `tk anatomy WORD`).  Read-only; no env at import.

Sections (label EXACT = chain tax / invoice law arithmetic on the word; MODEL = counterfactual with feasibility not checked):
  1 invoice law   gapmap.components: R0 per class (X mains, Y mains, owned staging, H signal, H residual bottom/central/top), predicted kappa (EXACT)
  2 skeleton      source (X) and routing (Y) main chains: n, tax, park stops (stops strictly between birth and end frame) (EXACT chain tax)
  3 lifetimes     ALIGNLAW attrib: every H lifetime (late birth / early end, Shapley split of L = F - A) by mechanism (markets / twins at hubs / other ends /
                  signal births / other births) with ENABLING-stop cost and net (EXACT tax, MODEL for the enabling set via endanat.py's exact replay)
  4 hubs          HUBCOST ledger per octet frame O_r: Xst/Hst/end/O-net/d8/cpy/NET (MODEL: feasibility not checked; HUBDROP says every public hub is forced)
  5 signal        H signal R0 + owned staging + hub up-departure d8 stops (the d8 column of 4)
  6 copies        pure crossing copies (H registers d0.g.hp.d9) and the COPY events; hub-forced copy interaction = the cpy column of 4
Frame classes come from fcls.py (tiling-relative, E / T=384), so section 3-6 labels are valid for words that share the #6030 frame geometry."""
import os, sys, json, gzip, math, hashlib, pickle, collections

HERE = os.path.dirname(os.path.abspath(__file__))
TK = os.path.dirname(HERE)


def _paths():
    for p in (HERE, TK + '/synth', TK + '/gen2', TK + '/surgery', TK):
        if p not in sys.path: sys.path.insert(0, p)


def load(spec):
    for p in (spec, os.path.join(TK, 'words', spec + '.json.gz'), os.path.join(TK, 'words', spec)):
        if os.path.isfile(p):
            op = gzip.open if p.endswith('.gz') else open
            with op(p, 'rt') as fh: return os.path.abspath(p), json.load(fh)
    raise SystemExit('anatomy: no such word %r' % spec)


def content_sha(w):
    return hashlib.sha256(json.dumps(w, sort_keys=True).encode()).hexdigest()[:16]


def tax(ds):
    sd = sorted(set(ds)); D = sd[-1] - sd[0]
    return 0.0 if D == 0 else sum((b - a) * math.log(D / (b - a)) for a, b in zip(sd, sd[1:]))


# ---------------------------------------------------------------- 3 lifetimes
def attribute(L, A):
    """ALIGNLAW attrib.py as a function: L = life.ledger(w), A = endanat.compute(w).  Returns rows by mechanism (n, L gross, enabling n/cost/dedicated, net lo/hi)"""
    rows = L['rows']; dim = L['dim']; fc = L['fcls']; mains = L['mains']
    allch = {r: x['chain'] for r, x in rows.items()}
    for r, m in mains.items(): allch[r] = m['chain']
    role = lambda r: 'H' if r in rows else mains[r]['role']
    visit = collections.defaultdict(set)
    for r, ch in allch.items():
        for f in ch: visit[f].add(r)
    en = collections.defaultdict(set); shared = set()
    anat = {x['h']: x for x in A['rows']}

    def endmech(h):
        x = rows[h]; a = anat.get(h); c = fc[x['ef']]
        if a is None: return 'end?'
        if not a['okpub']: return 'end-owned-fed'
        if not a['D']: return 'end-inert'
        if a['Dx'] >= 40: return 'end-wide-courier'
        roles = {s['role'] for s in a['sup']}
        if c.startswith('O'): return 'end-hub@O' + ('(X)' if 'X' in roles else '(mates)')
        if x['ke'] >= 2 and dim[x['ef']] == 8: return 'end-relay@8'
        return 'end-small@d%d' % dim[x['ef']]

    for h, a in anat.items():
        for s in a.get('sup') or []:
            r = s['r']; f = rows[h]['ef']; ch = allch[r]
            if f in ch and ch[0] != f and ch[-1] != f:
                en[(r, f)].add(endmech(h))
                if s['nonend'] > 0: shared.add((r, f))

    def birthmech(r):
        x = rows[r]; c = fc[x['bf']]
        if c.startswith('G'): return 'birth-market@G'
        if x['sig']: return 'birth-signal@d%d' % dim[x['bf']]
        return 'birth-other@%s' % (c if c[0] == 'O' else 'd%d' % dim[x['bf']])

    for f, c in fc.items():
        if not c.startswith('G'): continue
        for r in visit.get(f, ()):
            ch = allch[r]
            if ch[0] != f and ch[-1] != f: en[(r, f)].add('birth-market@G')
    G = collections.defaultdict(lambda: [0, 0.0])
    for r, x in rows.items():
        if x['b0']: k = birthmech(r); G[k][0] += 1; G[k][1] += x['Lb']
        if x['e9']: k = endmech(r); G[k][0] += 1; G[k][1] += x['Le']
    C = collections.defaultdict(lambda: [0, 0.0]); Cd = collections.Counter(); byrole = collections.Counter()
    per = collections.defaultdict(list)
    for (r, f), ms in en.items(): per[r].append((f, ms))
    for r, L2 in per.items():
        ch = allch[r]; sd = tuple(sorted(set(dim[f] for f in ch)))
        drop = {dim[f] for f, _ in L2}
        c = tax(sd) - tax(tuple(d for d in sd if d not in drop))
        ms = sorted(set(m for _, s in L2 for m in s))
        ded = all((r, f) not in shared for f, _ in L2)
        for m in ms:
            C[m][0] += 1; C[m][1] += c / len(ms)
            if ded: Cd[m] += c / len(ms)
        byrole[role(r)] += c
    out = []
    for k in sorted(G, key=lambda k: -G[k][1]):
        out.append(dict(mechanism=k, n=G[k][0], L=G[k][1], en_n=C[k][0], en_cost=C[k][1], en_dedicated=Cd[k], net_lo=G[k][1] - C[k][1], net_hi=G[k][1] - Cd[k]))
    return dict(rows=out, total_L=sum(G[k][1] for k in G), enabling_cost=sum(v[1] for v in C.values()), enabling_by_role={k: round(v, 3) for k, v in byrole.items()})


def group_mechanisms(rows):
    """collapse attrib rows into the requested groups: markets / twins (hub ends) / ends (other) / signal births / other births"""
    g = collections.OrderedDict((k, dict(n=0, L=0.0, en_cost=0.0, net_lo=0.0, net_hi=0.0)) for k in ('markets', 'twins', 'ends', 'signal', 'births'))
    for r in rows:
        m = r['mechanism']
        k = 'markets' if m == 'birth-market@G' else 'twins' if m.startswith('end-hub@O') else 'signal' if m.startswith('birth-signal') else 'births' if m.startswith('birth-') else 'ends'
        for f in ('n', 'L', 'en_cost', 'net_lo', 'net_hi'): g[k][f] += r[f]
    return g


def lifetimes(w, use_cache=True, cache_dir=None):
    """life ledger + exact end anatomy (cached by content sha: the replay is minutes) + attribution"""
    _paths()
    import life as Life, endanat
    cache_dir = cache_dir or os.path.join(HERE, 'out', 'cache'); sha = content_sha(w)
    L = Life.ledger(w); src = 'computed'
    cf = os.path.join(cache_dir, 'anat_%s.pkl' % sha); seed = os.path.join(HERE, 'data', 'anat_%s.pkl' % sha)
    A = None
    for f in (seed, cf):
        if use_cache and os.path.exists(f):
            try: A = pickle.load(open(f, 'rb')); src = 'cache:' + os.path.basename(f); break
            except Exception: A = None
    if A is None:
        A = endanat.compute(w)
        try: os.makedirs(cache_dir, exist_ok=True); pickle.dump(A, open(cf, 'wb'))
        except OSError: pass
    at = attribute(L, A)
    rows = L['rows']
    at['helpers'] = len(rows); at['births'] = sum(x['b0'] for x in rows.values()); at['ends'] = sum(x['e9'] for x in rows.values())
    at['groups'] = group_mechanisms(at['rows']); at['anat_source'] = src
    return at, L


# ---------------------------------------------------------------- 2 skeleton / mains
def mains(L):
    out = {}
    for role in 'XY':
        ms = [m for m in L['mains'].values() if m['role'] == role]
        stops = sum(max(0, len(m['chain']) - 2) for m in ms)
        out[role] = dict(n=len(ms), tax=sum(m['tax'] for m in ms), stops=stops, moved=sum(1 for m in ms if len(m['chain']) > 1))
    return out


# ---------------------------------------------------------------- 4 hubs, 6 copies (HUBCOST ledger.py as a function)
def hub_ledger(w):
    _paths()
    import rp, fcls as F
    fr = w['frames']; tl = rp.timelines(w); n = len(w['initial']); LV = set(w['live'])
    role = lambda r: 'O' if r >= n else ('X' if r in LV else ('Y' if r - 112 in LV else 'H'))
    cls = {}
    def fc(f):
        if f not in cls: cls[f] = F.cls(fr[f])
        return cls[f]
    chains = {r: [f for _, _, f in tl[r]] for r in tl}
    # copies: pure crossing copies d0.g.hp.d9 (COPYFREE cc1); hub sharer M of a copy = first register (id order) other than c visiting g and an O frame
    copies = []
    for r, ch in sorted(chains.items()):
        if r >= n or role(r) != 'H': continue
        seq = [(fc(f)[0], f) for f in ch if not fc(f)[0].startswith('d1')]    # a dim-1 relay stop does not make a copy impure (COPYFREE c2 chains omit it)
        if [c for c, _ in seq] != ['d0', 'g', 'hp', 'd9']: continue
        copies.append(dict(c=r, g=seq[1][1], hp=seq[2][1]))
    share = {}
    for x in copies:
        M = [r for r, ch in sorted(chains.items()) if r != x['c'] and x['g'] in ch and any(fc(f)[0] == 'O' for f in ch)]
        x['M'] = M
        if M: share.setdefault(M[0], x)
    TC = tax([0, 3, 6, 9])
    Ofr = collections.defaultdict(list)
    for f in range(len(fr)):
        if len(fr[f]) == 4 and fc(f)[0] == 'O': Ofr[fc(f)[1]].append(f)
    TOT = collections.Counter(); rows = []
    for o, Os in sorted(Ofr.items()):
        Os = set(Os); c = collections.Counter(); k = collections.Counter()
        for r in range(n):
            ch = chains.get(r)
            if not ch or not Os & set(ch): continue
            ds = [len(fr[f]) for f in ch]; rl = role(r)
            new = [dm for f, dm in zip(ch, ds) if f not in Os]
            ender = ch[-1] in Os
            if ender: new = new + [9]
            dn = tax(sorted(set(new))) - tax(ds)
            if ender: c['end'] -= dn; k['E'] += 1
            else: c[rl + 'st'] -= dn; k[rl] += 1
            i = max(j for j, f in enumerate(ch) if f in Os)
            if i + 1 < len(ch) and ds[i + 1] == 8 and rl != 'O':
                c['d8'] += tax(ds) - tax(ds[:i + 1] + ds[i + 2:])
            if r in share and share[r]['g'] in ch and 8 not in ds:
                j = ch.index(share[r]['g']); fl = ds[:j + 1] + [6, 9]
                df = tax(sorted(set(fl))) - tax(ds) - TC
                c['cpy'] += -(df - dn); k['cp'] += 1
        c['O-net'] = c['Xst'] + c['Hst'] + c['end']; c['NET'] = c['O-net'] + c['cpy']
        for kk, v in c.items(): TOT[kk] += v
        for kk, v in k.items(): TOT['n' + kk] += v
        rows.append(dict(octet=o, frames=sorted(Os), nX=k['X'], nH=k['H'], nE=k['E'], ncp=k['cp'], **{kk: round(c[kk], 4) for kk in ('Xst', 'Hst', 'end', 'O-net', 'd8', 'cpy', 'NET')}))
    tot = dict(nX=TOT['nX'], nH=TOT['nH'], nE=TOT['nE'], ncp=TOT['ncp'], **{kk: round(TOT[kk], 4) for kk in ('Xst', 'Hst', 'end', 'O-net', 'd8', 'cpy', 'NET')})
    ncopy_ev = sum(1 for e in w['program'] if e[0] == 'COPY')
    return dict(rows=rows, total=tot, copies=dict(n_pure_crossing=len(copies), with_hub_sharer=sum(1 for x in copies if x['M']), copy_events=ncopy_ev, copy_registers=len({e[1] for e in w['program'] if e[0] == 'COPY'})))


# ---------------------------------------------------------------- driver
def anatomy(spec, with_lifetimes=True, use_cache=True):
    """full anatomy dict of a word (path or name in words/)"""
    _paths()
    path, w = load(spec)
    import gapmap
    comp = gapmap.components(w)
    out = dict(word=os.path.basename(path), content_sha=content_sha(w), regs=len(w['initial']), events=len(w['program']))
    R0 = comp['R0']; os_ = comp['owned']
    out['invoice'] = dict(R0=R0, total=comp['total'], exact_total=comp['exact_total'], counts=comp['counts'], owned=os_ if isinstance(os_, dict) else {}, kappa_pred=None)
    try: out['invoice']['kappa_pred'] = gapmap.pred_kappa(comp['total'], (os_.get('paid') if isinstance(os_, dict) and 'paid' in os_ else gapmap.LAW_PAID0))
    except Exception: pass
    if with_lifetimes:
        at, L = lifetimes(w, use_cache)
        out['skeleton'] = mains(L); out['lifetimes'] = at
    else:
        import life as Life
        out['skeleton'] = mains(Life.ledger(w))
    hl = hub_ledger(w)
    out['hubs'] = hl['rows']; out['hubs_total'] = hl['total']; out['copies'] = hl['copies']
    h = comp['R0']
    out['signal'] = dict(H_signal_R0=h.get('H signal (touch owned)'), owned_staging_R0=h.get('owned (O)'), hub_up_departure_d8=hl['total']['d8'], H_signal_n=comp['counts'].get('Hsig'))
    return out


def fmt(a):
    L = []
    L.append('anatomy %s  (content sha %s, %d regs, %d events)' % (a['word'], a['content_sha'], a['regs'], a['events']))
    iv = a['invoice']
    L.append('== 1 invoice law (EXACT): R0 by class; total R0 %.1f (exact replay %.1f)%s' % (iv['total'], iv['exact_total'], '  predicted kappa %.7f' % iv['kappa_pred'] if iv.get('kappa_pred') else ''))
    for k, v in iv['R0'].items(): L.append('   %-32s %9.1f' % (k, v))
    sk = a['skeleton']
    L.append('== 2 skeleton / mains (EXACT chain tax): X (sources) n %d tax %.1f park stops %d | Y (readers/routing) n %d tax %.1f stops %d' % (sk['X']['n'], sk['X']['tax'], sk['X']['stops'], sk['Y']['n'], sk['Y']['tax'], sk['Y']['stops']))
    if 'lifetimes' in a:
        lt = a['lifetimes']
        L.append('== 3 lifetimes by mechanism: %d helpers, %d late births, %d early ends, total L %.1f, enabling cost %.1f  [anat: %s]' % (lt['helpers'], lt['births'], lt['ends'], lt['total_L'], lt['enabling_cost'], lt['anat_source']))
        L.append('   %-16s %5s %8s %6s %8s   %8s %8s' % ('group', 'n', 'L gross', 'en.cost', '', 'net lo', 'net hi'))
        for k, v in lt['groups'].items(): L.append('   %-16s %5d %8.1f %8.1f %8s   %8.1f %8.1f' % (k, v['n'], v['L'], v['en_cost'], '', v['net_lo'], v['net_hi']))
        L.append('   by mechanism:')
        for r in lt['rows']: L.append('     %-26s n %3d L %7.1f | enabling %3d cost %6.1f | net %7.1f..%7.1f' % (r['mechanism'], r['n'], r['L'], r['en_n'], r['en_cost'], r['net_lo'], r['net_hi']))
    t = a['hubs_total']
    L.append('== 4 hubs (HUBCOST, MODEL): %d octet frames; O-net %.1f (Xst %.1f Hst %.1f end %.1f) + cpy %.1f = NET %.1f ; d8 (signal column) %.1f' % (len(a['hubs']), t['O-net'], t['Xst'], t['Hst'], t['end'], t['cpy'], t['NET'], t['d8']))
    s = a['signal']
    L.append('== 5 signal: H signal R0 %s (n %s), owned staging %s, hub up-departure d8 %.1f' % (None if s['H_signal_R0'] is None else round(s['H_signal_R0'], 1), s['H_signal_n'], None if s['owned_staging_R0'] is None else round(s['owned_staging_R0'], 1), s['hub_up_departure_d8']))
    c = a['copies']
    L.append('== 6 copies: pure crossing copies %d (with a hub sharer %d), COPY events %d, COPY destination registers %d ; hub-forced copy interaction %.1f' % (c['n_pure_crossing'], c['with_hub_sharer'], c['copy_events'], c['copy_registers'], t['cpy']))
    return '\n'.join(L)
