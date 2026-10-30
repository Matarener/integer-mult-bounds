"""MARKETS copy of SIGFUSE/B/realB.py (+ --dirs D3 order). SIGFUSE route B prototype: RELAYTOP allh pipeline + 8 ROOT SOURCES.
Root k enters the residual network as a source at its descent line <l_k> (like a port at <p_i>): one helper c_k reads -4*root_k at <l_k> once
(H<-O, one per root) and is then an ordinary relay source; reader j wants coefficient C2_jk/2 on it (same magnitude as the E entries).
Model -> frontgen (c_k empty, STAR copies still emitted => value_ok) -> sigfuse.fuse_share(forced c_k hosts) removes the copies the network now covers.
usage: python -B route_b.py SEED OUT.json.gz [--no-roots] [--dirs 51,30,45,75,120,102,85]   (env set only in main)
(toolkit copy of SIGFUSE/B/realB.py + MARKETS/realM.py; gen2.py drives it)"""
import sys, os, time, collections, json
HERE = os.path.dirname(os.path.abspath(__file__)); TK = os.path.dirname(HERE)
for p in (TK, os.path.join(TK, 'synth'), os.path.join(os.path.dirname(TK), 'infra'), HERE):
    if p not in sys.path: sys.path.insert(0, p)
import numpy as np
import geo
L = [7, 25, 52, 82, 491, 448, 67, 137]; K = 8; m = geo.m
RA = dict(pairdirs=True, hedges='d3', theta=None, lam=4.0, rounds=2)   # RULEAUDIT (opt-in): --no-pairdirs, --hedges anyN, --theta a,b,.., --lam L, --rounds R; defaults = shipped
def hedges_any(nh, minc=1):
    """RULEAUDIT: helper edges over ANY non-orthogonal reader pair (not only D3 translates), greedy by newly covered entries (same assignment rule as inst2)"""
    P = geo.PORTS; O = np.array(geo.ORTH[:, :m] if geo.ORTH.shape[1] > m else geo.ORTH, dtype=bool)
    pa, pb = zip(*[(a, b) for a in range(m) for b in range(a + 1, m) if not O[a, b]]); pa = np.array(pa); pb = np.array(pb)
    done = np.zeros((m, m), dtype=bool); H = []; alive = np.ones(len(pa), dtype=bool)
    for _ in range(nh):
        A = O & ~done; c = (A[pa] & A[pb]).sum(1); c[~alive] = -1; k = int(c.argmax())
        if c[k] < minc: break
        a, b = int(pa[k]), int(pb[k]); H.append((a, b)); alive[k] = False
        com = A[a] & A[b]; done[a] |= com; done[b] |= com
    return H
GSHAPE = 'ent'   # GENUPGRADE: rt.build gain shape; --gshape taxW = exact chain-tax marginal (Lemma 4), opt-in
def patch_geo():
    R = np.zeros((m, m + K)); O = np.zeros((m, m + K), dtype=int)
    R[:, :m] = geo.RES; O[:, :m] = geo.ORTH
    for j in range(m):
        for k in range(K):
            c = int(geo.C2[j][k]); assert (c != 0) == (not geo.par(L[k], geo.PORTS[j])), 'Lemma H'
            if c: R[j, m + k] = c / 2.0; O[j, m + k] = 1
    geo.RES = R; geo.ORTH = O
def inst2(H, roots_src=True, M=None):
    import rt, hgreedy
    P = geo.PORTS; O = geo.ORTH; E = geo.RES; S = m + (K if roots_src else 0)
    srcv = list(P) + (L if roots_src else [])
    done = {j: set() for j in range(m)}; snk = []; C = {}; sw = []; meta = []
    kinds = [(j, x, 'Y') for j, x in sorted((M or {}).items()) if j < x] + [(j, x, 'H') for (j, x) in H if not (M and M.get(j) == x)]   # RULEAUDIT --yedges: Y-pair edges first (Ys stop at Q_e)
    for (j, x, kd) in kinds:
        com = [i for i in range(S) if O[j, i] and O[x, i] and i not in done[j] and i not in done[x]]
        for cls in (1, -1):
            pc = [i for i in com if E[j, i] * E[x, i] * cls > 0]
            if not pc: continue
            C[len(snk)] = {i: (1 if E[j, i] > 0 else -1) for i in pc}; snk.append([P[j], P[x]]); sw.append(2); meta.append(('e', j, x, cls, kd))
        done[j] |= set(com); done[x] |= set(com)
    for j in range(m):
        pv = [i for i in range(S) if O[j, i] and i not in done[j]]
        if pv: C[len(snk)] = {i: (1 if E[j, i] > 0 else -1) for i in pv}; snk.append([P[j]]); sw.append(1); meta.append(('s', j))
    for k, u in enumerate(hgreedy.U):
        C[len(snk)] = {i: int(geo.S4[k][i]) for i in range(m) if geo.S4[k][i]}; snk.append([u]); sw.append(1); meta.append(('r', k))
    I = rt.Inst([[p] for p in srcv], snk, C); I.sw = sw; I.meta = meta
    I.readers = [[mm[1]] if mm[0] == 's' else ([] if mm[0] == 'r' else [mm[1], mm[2]]) for mm in meta]
    return I
D3 = [120, 85, 75, 51, 102, 30, 45]
DORD = None
def model(seed, roots_src=True):
    import rt, allh, edges
    D = DORD or D3
    hs = RA['hedges']; H = allh.hedges(D) if hs == 'd3' else hedges_any(int(hs[3:] or 144))
    I = inst2(H, roots_src, M=(__import__('dmatch').dmatch(D) if RA.get('yedges') else None))
    kw = {} if RA['theta'] is None else dict(theta=RA['theta'])
    N, _ = rt.build(I, lam=RA['lam'], seed=seed, land=False, pairdirs=set(D) if RA['pairdirs'] else None, gshape=GSHAPE, rounds=RA['rounds'], **kw); yt = edges.land(N, I)
    return N, I, rt.r0(N)[1] + yt
def hubplan(N):
    def build(bk, ctx):
        fid = ctx['fid']; F9 = ctx['F9']; hidx = {}
        def ref(r):
            if isinstance(r, tuple): return r
            Rg = N.regs[r]
            if Rg['role'] == 'X' and Rg['tag'] < m: return ('X', Rg['tag'])
            if r not in hidx: hidx[r] = len(hidx)
            return ('H', hidx[r])
        order = sorted(range(len(N.ops)), key=lambda t: (N.ops[t][4], t)); seq = []; restore = []
        for h, t in enumerate(order):
            d, s, q, fk, dim = N.ops[t]
            seq.append(dict(kind='g', dst=ref(d), src=ref(s), coef=q, frame=fid(list(fk)), dim=dim, h=h))
        for o in reversed(seq):
            if o['dst'][0] != 'Y': restore.append(dict(dst=o['dst'], src=o['src'], coef=-o['coef'], frame=F9))
        out = dict(hubs=None, ops=[], seq=seq, pre=[], restore=restore, info=dict(relaytop=True, ops=len(seq)))
        N._seq = [(o['dst'], o['src']) for o in sorted(seq, key=lambda o: (o['dim'], o['h']))]
        N._ck = {hidx[r]: N.regs[r]['tag'] - m for r in hidx if N.regs[r]['role'] == 'X' and N.regs[r]['tag'] >= m}
        rr = getattr(N, 'rootreads', None)
        if rr: out['rootreads'] = {k: [(ref(r), q) for r, q in v] for k, v in rr.items()}
        out['hubs'] = list(range(len(hidx))); out['info']['hubs'] = len(hidx)
        return out
    return build
def main(argv=None):
    os.environ['TK_FREE_BOUNDS'] = '1'
    global DORD
    argv = sys.argv if argv is None else ['x'] + list(argv)
    seed = int(argv[1]); out = argv[2]; roots_src = '--no-roots' not in argv
    if '--dirs' in argv: DORD = [int(x) for x in argv[argv.index('--dirs') + 1].split(',')]
    global GSHAPE
    if '--gshape' in argv: GSHAPE = argv[argv.index('--gshape') + 1]
    if '--no-pairdirs' in argv: RA['pairdirs'] = False
    if '--yedges' in argv: RA['yedges'] = True
    if '--hedges' in argv: RA['hedges'] = argv[argv.index('--hedges') + 1]
    if '--theta' in argv: RA['theta'] = tuple(int(x) for x in argv[argv.index('--theta') + 1].split(','))
    if '--lam' in argv: RA['lam'] = float(argv[argv.index('--lam') + 1])
    if '--rounds' in argv: RA['rounds'] = int(argv[argv.index('--rounds') + 1])
    BL = None
    if '--gauge' in argv or '--uz' in argv:   # root gauge (MOONSHOT3): --gauge 0..15 (clique*2+flip) or --uz JSON [[u,z],..]; default path untouched
        import blindcode, hgreedy
        uz = [tuple(x) for x in json.loads(argv[argv.index('--uz') + 1])] if '--uz' in argv else blindcode.gauge_uz(int(argv[argv.index('--gauge') + 1]))
        BL = blindcode.make(uz); assert BL is not None, 'invalid gauge'
        geo.C2 = BL[0]; geo.S4 = BL[1]; globals()['L'] = BL[2]; hgreedy.U = BL[3]
    patch_geo()
    from tkcommon import load, profile_of
    import dag as D, incr, sigfuse
    from synth import gen as G, sample as SM, mainhub as MHB
    import kernel2net as KN
    t = time.time(); N, I, mr0 = model(seed, roots_src); print('model R0', round(mr0), 'ops', len(N.ops), '%.0fs' % (time.time() - t), flush=True)
    anchor = '5756'; p, w0 = load(anchor); profile = profile_of(w0)[0]
    spec = dict(SM.anchor_spec(anchor, profile), front='generated', back='generated:star', helpers='mainhub'); spec.pop('body', None)
    if BL:
        import synth.frontgen as FG
        FG.load_code = lambda: (BL[1].tolist(), BL[0].tolist())
        spec['roots'] = [dict(r, u=BL[3][k], line=BL[2][k]) for k, r in enumerate(spec['roots'])]
    MHB.apply = hubplan(N)
    w, info = G.build_word(spec)
    print('value_ok', info['value_ok'], 'helpers', info.get('helpers'), flush=True)
    if w is None: return 1
    D.save(w, out.replace('.json.gz', '_pre.json.gz'))
    print('pre R0', {k: round(v, 1) for k, v in KN.r0(w)[0].items()}, round(KN.r0(w)[1], 1), flush=True)
    w2, rep = sigfuse.fuse_share(w, forced=find_ck(w, N) if roots_src else None)
    for k, v in rep.items(): print('%s: %s' % (k, v))
    by, tot = KN.r0(w2); print('R0 out', {k: round(v, 1) for k, v in by.items()}, round(tot, 1))
    iw = incr.IncrWord(w2, profile=profile)
    print('legal', iw.legal_all, 'violations', len(iw.viol), 'bad native pairs', len(iw.bad_pairs), 'kappa %.13f' % iw.kappa, flush=True)
    if iw.viol: print(iw.viol[:4])
    D.save(w2, out); print('wrote', out)
def find_ck(w, N):
    """map the model's root-source helpers c_k to word registers: the RT path emits the hub seq ops consecutively after the dim-0 junk loads"""
    import dag as D
    d = D.decompile(w, forms=False); n = d['meta']['npub']; live = sorted(d['meta']['live']); fr = d['frames']
    ops = [o for o in d['ops'] if not (o[0] == 'ADD' and o[1] < n and (o[1] - 112) in set(live) and len(fr[o[4]]) == 0)]
    hmap = {}
    for (dr, sr), o in zip(N._seq, ops):
        for ref, reg in ((dr, o[1]), (sr, o[2])):
            if ref[0] == 'X': assert reg == live[ref[1]], ('X map', ref, reg)
            elif ref[0] == 'Y': assert reg == live[ref[1]] + 112, ('Y map', ref, reg)
            else:
                assert hmap.setdefault(ref[1], reg) == reg, ('H map', ref, reg)
    return {hmap[h]: k for h, k in N._ck.items() if h in hmap}
if __name__ == '__main__': sys.exit(main())
