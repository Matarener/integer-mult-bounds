"""gen2 stage 1: RELAYTOP edge-cover top.  Toolkit copy of RELAYTOP/real.py restricted to the production mode
`allh:D1,..,D7:SEED` (every D3-direction non-orthogonal reader pair is a helper edge, 8 root sinks via the frontgen 'rootreads' channel,
D3 self-dual port pairs) -> frontgen word on the 5756 anchor spec.   Output = allh_d3 (kappa .0025498457553 at seed 0).
usage: python -B relaytop.py SEED OUT.json.gz [--dirs 120,85,75,51,102,30,45]   (env set only in main)"""
import sys, os, time
HERE = os.path.dirname(os.path.abspath(__file__)); TK = os.path.dirname(HERE)
for p in (TK, os.path.join(TK, 'synth'), os.path.join(os.path.dirname(TK), 'infra'), HERE):
    if p not in sys.path: sys.path.insert(0, p)
D3 = [120, 85, 75, 51, 102, 30, 45]

def hubplan(N):
    def build(bk, ctx):
        fid = ctx['fid']; F9 = ctx['F9']
        hidx = {}
        def ref(r):
            if isinstance(r, tuple): return r
            Rg = N.regs[r]
            if Rg['role'] == 'X': return ('X', Rg['tag'])
            if r not in hidx: hidx[r] = len(hidx)
            return ('H', hidx[r])
        order = sorted(range(len(N.ops)), key=lambda t: (N.ops[t][4], t))
        seq = []; restore = []
        for h, t in enumerate(order):
            d, s, q, fk, dim = N.ops[t]
            seq.append(dict(kind='g', dst=ref(d), src=ref(s), coef=q, frame=fid(list(fk)), dim=dim, h=h))
        for o in reversed(seq):
            if o['dst'][0] != 'Y': restore.append(dict(dst=o['dst'], src=o['src'], coef=-o['coef'], frame=F9))
        out = dict(hubs=None, ops=[], seq=seq, pre=[], restore=restore, info=dict(relaytop=True, ops=len(seq)))
        rr = getattr(N, 'rootreads', None)
        if rr: out['rootreads'] = {k: [(ref(r), q) for r, q in v] for k, v in rr.items()}
        out['hubs'] = list(range(len(hidx))); out['info']['hubs'] = len(hidx)
        return out
    return build

def model(seed, D=None):
    import rt, allh, hgreedy, edges, valcheck
    D = list(D or D3)
    I = hgreedy.inst({}, allh.hedges(D), roots=True)
    N, _ = rt.build(I, lam=4.0, seed=int(seed), land=False, pairdirs=set(D)); yt = edges.land(N, I)
    print('model R0', round(rt.r0(N)[1] + yt), 'badY', valcheck.check(N, I), flush=True)
    return N

def main(argv=None):
    os.environ['TK_FREE_BOUNDS'] = '1'
    a = sys.argv[1:] if argv is None else list(argv)
    seed = int(a[0]); out = a[1]
    D = [int(x) for x in a[a.index('--dirs') + 1].split(',')] if '--dirs' in a else None
    from tkcommon import load, profile_of
    import dag as DG, incr
    from synth import gen as G, sample as SM, mainhub as MHB
    import kernel2net as K
    anchor = '5756'; p, w0 = load(anchor); profile = profile_of(w0)[0]
    spec = SM.anchor_spec(anchor, profile)
    N = model(seed, D); MHB.apply = hubplan(N)
    spec = dict(spec, front='generated', back='generated:star', helpers='mainhub'); spec.pop('body', None)
    t = time.time(); w, info = G.build_word(spec)
    print('value_ok', info['value_ok'], 'helpers', info.get('helpers'), '%.1fs' % (time.time() - t), flush=True)
    if w is None: return 1
    by, tot = K.r0(w)
    print('R0 by role', {k: round(v, 1) for k, v in by.items()}, 'events', len(w['program']), flush=True)
    iw = incr.IncrWord(w, profile=profile)
    print('legal', iw.legal_all, 'violations', len(iw.viol), 'bad native pairs', len(iw.bad_pairs), 'kappa %.13f' % iw.kappa, flush=True)
    DG.save(w, out); print('wrote', out)
    return 0

if __name__ == '__main__':
    sys.exit(main())
