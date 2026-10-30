"""LEVERBANK driver: purex2 + composable early-end levers in ONE joint dim-0 solve (bank.py docstring has the lever grammar).
usage: python -B stack.py IN(route-B block-form word, e.g. o1 / o1y) OUT [--dims 4,8] [--xstops] [--lever SPEC]... [--report OUT.json]
  SPEC: own:H@G | own:auto | hub:R,R/X,X[@b,..] | relay:H[:dmax] | relay:auto[:dmax] | skip:H,H     (several: repeat --lever or ';'-join)
With no --lever the output is purex2's word bit-for-bit (content sha; tests/leverbank_test.py).  TK_FREE_BOUNDS is set in main() only."""
import sys, os, gzip, json, collections
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)


def main(argv=None):
    os.environ['TK_FREE_BOUNDS'] = '1'
    a = sys.argv[1:] if argv is None else list(argv); inp, out = a[0], a[1]
    import bank
    import kernel2net as KN, incr
    from tkcommon import profile_of
    dims = set(int(x) for x in a[a.index('--dims') + 1].split(',')) if '--dims' in a else None
    specs = [a[i + 1] for i, x in enumerate(a) if x == '--lever']
    w = json.load(gzip.open(inp))
    c, dag, w1, rep = bank.stack(w, specs, dims=dims, xstops='--xstops' in a)
    w2, rr = c.D.realise(dag, schedule='lazy', verify=True)
    print('undelivered', rr['undelivered'][:3], 'value_errors', len(rr['value_errors']))
    if rr['undelivered']: raise SystemExit('LEVERBANK: undelivered %s' % (rr['undelivered'][:3],))
    w2['verifier_profile'] = dict(w1.get('verifier_profile') or {})
    n = len(w2['initial'])
    if rep['levers'] and any(x['kind'] == 'own' for x in rep['levers']):
        life = sum(1 for e in w2['program'] if e[0] == 'INIT'); peak = live = 0
        for e in w2['program']:
            if e[0] == 'INIT': live += 1; peak = max(peak, live)
            elif e[0] == 'CLEAR': live -= 1
        w2['verifier_profile'].update(lifetimes=life, peak=peak)
    paid = sum(abs(len(w2['frames'][e[3]]) - len(w2['frames'][e[2]])) for e in w2['program'] if e[0] == 'MOVE' and e[1] >= n)
    r0 = KN.r0(w2)
    iw = incr.IncrWord(w2, profile=profile_of(w)[0])
    rep.update(R0=round(r0[1], 3), R0cls={k: round(v, 2) for k, v in r0[0].items()}, events=len(w2['program']), paid=paid,
               legal=bool(iw.legal_all), viol=len(iw.viol), kappa='%.16f' % iw.kappa, value_errors=len(rr['value_errors']))
    print('LEVERS', json.dumps(rep['levers']))
    if rep['conflicts']: print('CONFLICTS', json.dumps(rep['conflicts'], default=str))
    print('R0', rep['R0cls'], rep['R0'], 'events', rep['events'], 'paid', paid)
    print('legal', iw.legal_all, 'viol', len(iw.viol), iw.viol[:3], 'kappa %.13f' % iw.kappa, flush=True)
    c.D.save(w2, out); print('wrote', out)
    if '--report' in a: json.dump(rep, open(a[a.index('--report') + 1], 'w'), indent=1, default=str)


if __name__ == '__main__': sys.exit(main())
