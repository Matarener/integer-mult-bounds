"""LEVERBANK octet port: the same lever specs on an OCTET word (OCTETGEN m12 family), via the OCTLIFE engine copies in levers/octet/.
Base enders = OCTLIFE lever (a) (life.census_octet: bottom riders end at octet frames O, re-census on drops), then the bank levers
(own:auto / own:H@G, relay:H|auto, hub:..) are planned on the same Ctx2 (Ys are sources: their dim-0 ADDs stay in the body) and all
enders go through ONE life.realise (purex2 joint solve with ctx=, culprit drops) + to_word (own value check vs req).
usage: python -B octet_stack.py IN(m12) OUT [--lever SPEC].. [--no-census] [--selfreq] [--report R.json]   (TK_FREE_BOUNDS set in main only)"""
import sys, os, gzip, json, collections
HERE = os.path.dirname(os.path.abspath(__file__))


def main(argv=None):
    os.environ['TK_FREE_BOUNDS'] = '1'
    sys.path.insert(0, HERE + '/octet')
    import life as LF                     # puts levers/octet first: `purex`/`purex2` below are the OCTLIFE copies
    if HERE not in sys.path: sys.path.insert(1, HERE)
    import bank
    import kernel2net as KN, incr, dag as D
    from tkcommon import profile_of
    a = sys.argv[1:] if argv is None else list(argv); inp, out = a[0], a[1]
    specs = [a[i + 1] for i, x in enumerate(a) if x == '--lever']
    L = bank.parse(specs); rep = dict(levers=[], conflicts=[])
    w = json.load(gzip.open(inp))
    # owned parks first (word transform)
    own = []
    if any(k == 'own' for k, _ in L):
        c_pre = LF.Ctx2(w)
        for k, x in L:
            if k != 'own': continue
            if x.startswith('auto'):
                for p in bank.own_auto_plan(w, set()): own.append((p['h'], p['g'])); rep['levers'].append(dict(kind='own', auto=True, h=p['h'], g=p['g'], root=p['O'], net_model=round(p['net'], 3)))
            else: own.append(tuple(int(y) for y in x.split('@'))); rep['levers'].append(dict(kind='own', h=own[-1][0], g=own[-1][1]))
    w1 = w; who = {}; parked = {}
    if own:
        d0 = D.decompile(w, forms=False); n = d0['meta']['npub']; R = bank.roots_of(d0, n); SP = [bank.spanset(b) for b in d0['frames']]
        plan = collections.defaultdict(list)
        for h, g in own:
            ks = [O for O, r in R.items() if r['l'] in SP[g] and SP[g] <= SP[r['H']]]
            if len(ks) != 1: rep['conflicts'].append(dict(lever='own:%d@%d' % (h, g), conflict='roots %s' % ks)); continue
            plan[ks[0]].append(g); who[h] = (ks[0], g)
        if plan: w1, parked, _ = bank.park(w, plan)
    w1 = dict(w1); w1['frames'] = [list(b) for b in w1['frames']]
    c = LF.Ctx2(w1, selfreq='--selfreq' in a)
    base = []
    if '--no-census' not in a:
        base, info = LF.census_octet(c, verbose=False); rep['census_net_model'] = round(info['net'], 2)
    ld = bank.Ledger()
    for e in base: ld.riders[e['h']] = 'octet-census'
    extra = []
    if who:
        _, lastx, lasti = bank.xreplay(c.body, c.n, c.no, c.role)
        for h, (O, g) in who.items():
            if not ld.take('own:%d@%d' % (h, g), [h], {}): continue
            P_ = parked[(O, g)]; xr = lastx[P_]; xh = lastx[h]; k0 = next(iter(xr)); al = xh.get(k0, 0) / xr[k0]
            tcopy = max(i for i, o in enumerate(c.body) if o[0] == 'COPY' and o[2] == P_)
            t = max(lasti[h], tcopy); extra.append(dict(h=h, t=t, f=g, use=[(P_, -al, t)]))
    P = bank.Pre(c); spans = {bank.rref(b): i for i, b in enumerate(w1['frames'])}
    def frame_of(M):
        f = spans.get(M)
        if f is None: f = len(w1['frames']); w1['frames'].append(list(M)); spans[M] = f; c.d['frames'].append(list(M)); c.dim.append(len(M))
        return f
    xo = bank.read_by_xo(c)
    for k, x in L:
        if k == 'relay':
            parts = x.split(':'); dmax = int(parts[1]) if len(parts) > 1 else 8
            hs = [h for h in range(c.n) if c.role(h) == 'H' and c.init[h] == c.Z and h not in xo] if parts[0] == 'auto' else [int(parts[0])]
            plans = []
            for h in hs:
                if h in ld.riders: continue
                ri = P.rider(h)
                if ri is None or not ri['v'] or c.dim[ri['g']] >= dmax - 1: continue
                p = P.plan_relay(h, dmax=dmax, maxh=2)
                if p is not None and p['net'] > 1e-9: plans.append(p)
            for p in sorted(plans, key=lambda p: -p['net']):
                if not ld.take('relay:%d' % p['h'], [p['h']], {(r,) + st[:2]: p['M'] for r, st in p['stops'].items()}): continue
                f = frame_of(p['M']); extra.append(dict(h=p['h'], t=p['tins'], f=f, use=[(R_, -q, p['tins']) for R_, q in p['co'].items()]))
                rep['levers'].append(dict(kind='relay', h=p['h'], dM=p['dM'], net_model=round(p['net'], 3)))
        elif k == 'hub':
            body, _, mb = x.partition('@'); rs, _, hs = body.partition('/')
            try: p = P.plan_hub([int(y) for y in rs.split(',')], [int(y) for y in hs.split(',')], Mb=[int(y) for y in mb.split(',')] if mb else None)
            except SystemExit as ex: rep['conflicts'].append(dict(lever='hub:' + x, conflict=str(ex))); continue
            if not ld.take('hub:' + x, [q['h'] for q in p['plans']], {(r,) + st[:2]: p['M'] for r, st in p['stops'].items()}): continue
            f = frame_of(p['M']); extra += [dict(h=q['h'], t=p['tins'], f=f, use=[(R_, -y, p['tins']) for R_, y in q['co'].items()]) for q in p['plans']]
            rep['levers'].append(dict(kind='hub', riders=rs, net_model=round(p['net'], 3)))
    rep['conflicts'] += ld.log
    excl = set(); drops = []
    for it in range(12):                  # = life.census_realise: re-optimise the census without enders the joint solve drops
        try: dag, ops = LF.realise(c, base + extra, verbose=False)
        except SystemExit as ex:
            if not extra: raise
            rep['conflicts'].append(dict(lever='joint-solve', conflict=str(ex)[:200])); keep = []
            for e in extra:                # keep extras greedily (octet: an ender whose cleanup leaves non-F9 residue is dropped)
                try: LF.realise(c, base + keep + [e], verbose=False); keep.append(e)
                except SystemExit as ex2: rep['conflicts'].append(dict(lever='ender %d' % e['h'], conflict='dropped: ' + str(ex2)[:160]))
            extra = keep; dag, ops = LF.realise(c, base + extra, verbose=False)
        drops += list(c.dropped)
        bd = set(c.dropped) & {e['h'] for e in base}
        if not bd or '--no-census' in a: break
        excl |= bd; base, info = LF.census_octet(c, exclude=excl, verbose=False); rep['census_net_model'] = round(info['net'], 2)
        extra = [e for e in extra if e['h'] not in {b['h'] for b in base}]
    rep['dropped'] = drops; rep['kept'] = [e['h'] for e in extra]; rep['extra'] = len(extra); rep['base'] = len(base)
    w2, rr, badv = LF.to_word(c, dag, w)
    if own:
        life = sum(1 for e in w2['program'] if e[0] == 'INIT'); peak = live = 0
        for e in w2['program']:
            if e[0] == 'INIT': live += 1; peak = max(peak, live)
            elif e[0] == 'CLEAR': live -= 1
        w2['verifier_profile'].update(lifetimes=life, peak=peak, owned_fields=c.no)
    iw = incr.IncrWord(w2, profile=profile_of(w)[0])
    rep.update(R0=round(KN.r0(w2)[1], 3), events=len(w2['program']), value_bad=badv[:5], undelivered=len(rr['undelivered']), legal=bool(iw.legal_all), viol=len(iw.viol), kappa='%.16f' % iw.kappa)
    print('LEVERS', json.dumps(rep['levers'])); print('CONFLICTS', json.dumps(rep['conflicts'], default=str)[:800]); print('dropped', rep['dropped'])
    print('R0', rep['R0'], 'events', rep['events'], 'value-bad', badv[:5], 'undelivered', rep['undelivered'])
    print('legal', iw.legal_all, 'viol', len(iw.viol), iw.viol[:3], 'kappa %.13f' % iw.kappa, flush=True)
    if badv or rr['undelivered']: raise SystemExit('OCTET LEVERBANK: value check failed')
    D.save(w2, out); print('wrote', out)
    if '--report' in a: json.dump(rep, open(a[a.index('--report') + 1], 'w'), indent=1, default=str)


if __name__ == '__main__': sys.exit(main())
