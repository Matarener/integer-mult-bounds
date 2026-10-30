"""RETAINOP retain.py: R-RETAIN (retained-operand stop drop) as an AUTOMATED builder step -- the edit swarm PR #6167 made by hand (r245g -> W6167).
Pattern.  A register s (usually an owned root) has a MIDDLE stop f (chain ... -> f -> g ...) whose events are ALL reads r += c s by other registers.
Today r sits at f for those reads.  Move the READ to g (the frame s occupies next): s goes straight to g (the stop at f is gone), and each reader r
gets a stop at g inserted just before f (r: pf -> g -> f).  The price is r's extra stop; the gain is s's dropped stop (both exact via the invoice
jl terms).  What blocks the plain move: r's OTHER adds at f before the read (r += c' q, q transient at f) are stranded because r is not at f yet.
Those operands are RETAINED: INIT h@f, COPY h = q at the old add's slot (q unchanged, value exact), and after r arrives at f (MOVE g->f right after
its last read) ADD r += c' h, CLEAR h.  If q is still at f and unwritten at arrival the add is just delayed (no copy, mode 'delay').
Preconditions (all checked): s stop at f is middle and every event inside is ADD x += c s (x != s); each reader's stop at f starts with a MOVE (not birth);
inside (r's MOVE-in, last read) the only events of r are the s-reads and ADD r += c' q at f (r never a source, never moved/scaled there); a helper slot
(owned index >= n) is free over the retention interval.  Legality + exact kappa are decided by IncrWord (the arbiter); accept only LEGAL and kappa up.
Variants per site: move r to g at its old MOVE-in time (mv=ra) or just before its first read (mv=late).
usage: retain.py WORD OUT.json.gz [--max N] [--dry] [--census]     (no env at import; hoist.py untouched)"""
import sys, os, json, gzip, math, bisect, collections
W = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')); TK = W
HERE = os.path.dirname(os.path.abspath(__file__))

def _paths():
    for p in (TK,):
        if p not in sys.path: sys.path.insert(0, p)

def _jl(ds): return sum(abs(y - x) * math.log(abs(y - x)) for x, y in zip(ds, ds[1:]) if y != x)

def _cost(r, ds, live):
    D = ds[-1] - ds[0]; helper = r not in live and r - 112 not in live
    return (D * math.log(D) if helper and D > 0 else 0) - _jl(ds)

class Idx:
    """per-register lifetimes (public: one; owned >= n: one per INIT..CLEAR), chains [(frame, tin, tout)], per-register event times"""
    def __init__(s, w):
        prog = w['program']; n = s.n = len(w['initial']); s.prog = prog; s.dim = [len(b) for b in w['frames']]; s.live = set(w['live'])
        s.ev = collections.defaultdict(list); s.wr = collections.defaultdict(list); s.lts = collections.defaultdict(list)
        for r in range(n): s.lts[r].append(dict(t0=-1, t1=len(prog), ch=[[w['initial'][r], -1, len(prog)]]))
        for t, e in enumerate(prog):
            k = e[0]
            if k == 'MOVE':
                lt = s.lt_at(e[1], t); lt['ch'][-1][2] = t; lt['ch'].append([e[3], t, len(prog)]); s.ev[e[1]].append(t); continue
            if k == 'INIT': s.lts[e[1]].append(dict(t0=t, t1=len(prog), ch=[[e[2], t, len(prog)]]))
            if k == 'ADD' or k == 'COPY': s.ev[e[1]].append(t); s.ev[e[2]].append(t)
            else: s.ev[e[1]].append(t)
            if k in ('ADD', 'COPY', 'SCALE', 'INIT', 'CLEAR'): s.wr[e[1]].append(t)
            if k == 'CLEAR':
                lt = s.lt_at(e[1], t); lt['t1'] = t; lt['ch'][-1][2] = t
    def lt_at(s, r, t):
        for lt in s.lts[r]:
            if lt['t0'] <= t <= lt['t1']: return lt
    def frame_at(s, q, t):
        lt = s.lt_at(q, t)
        if lt is None: return None
        for f, a, b in lt['ch']:
            if a < t < b: return f
    def unwritten(s, q, t0, t1):
        W_ = s.wr[q]; i = bisect.bisect_right(W_, t0); return not (i < len(W_) and W_[i] <= t1)

def sites(w, wide=False):
    """list of dict(save, s, f, g, readers=[...]) ; save = model R0 drop (jl terms, positive = better)"""
    I = Idx(w); prog = I.prog; n = I.n; out = []
    for s in list(I.lts):
        for lt in I.lts[s]:
            ch = lt['ch']
            for j in range(1, len(ch) - 1):
                f, a, b = ch[j]; g = ch[j + 1][0]
                if not wide and not (I.dim[ch[j - 1][0]] <= I.dim[f] <= I.dim[g] or I.dim[ch[j - 1][0]] >= I.dim[f] >= I.dim[g]): continue   # model (jl) is only a stop-cost for monotone runs
                evs = [t for t in I.ev[s] if a < t < b]
                if not evs or any(not (prog[t][0] == 'ADD' and prog[t][2] == s and prog[t][1] != s) for t in evs): continue
                byr = collections.defaultdict(list)
                for t in evs: byr[prog[t][1]].append(t)
                readers = []; ok = True; save = _cost(s, [I.dim[x[0]] for x in ch], I.live) - _cost(s, [I.dim[x[0]] for k, x in enumerate(ch) if k != j], I.live)
                for r, rt in byr.items():
                    rl = I.lt_at(r, rt[0]); k = next((k for k, (rf, ra, rb) in enumerate(rl['ch']) if ra < rt[0] < rb), None)
                    if k is None or k < 1 or rl['ch'][k][0] != f: ok = False; break
                    ra = rl['ch'][k][1]; pf = rl['ch'][k - 1][0]; mv = prog[ra]
                    if mv[0] != 'MOVE' or mv[1] != r: ok = False; break
                    tl = max(rt); st = []
                    for t in I.ev[r]:
                        if not ra < t < tl or t in rt: continue
                        e = prog[t]
                        if e[0] == 'ADD' and e[1] == r and e[2] != r and e[2] != s and e[4] == f: st.append(t)
                        else: ok = False; break
                    if not ok: break
                    # an r-event at the arrival slot itself (after tl) is fine; r must not be read by others in the window (ev[r] holds those too -> rejected above)
                    if not wide and not (I.dim[pf] <= I.dim[g] <= I.dim[f] or I.dim[pf] >= I.dim[g] >= I.dim[f]): ok = False; break
                    ds = [I.dim[x[0]] for x in rl['ch']]; ds2 = ds[:k] + [I.dim[g]] + ds[k:]
                    save += _cost(r, ds, I.live) - _cost(r, ds2, I.live)
                    readers.append(dict(r=r, ra=ra, pf=pf, tl=tl, reads=sorted(rt), stranded=st))
                if ok: out.append(dict(save=save, s=s, f=f, g=g, a=a, b=b, prev=ch[j - 1][0], readers=readers, chain=''.join(map(str, [I.dim[x[0]] for x in ch]))))
    out.sort(key=lambda x: -x['save'])
    return out

def apply(w, S, mv='ra'):
    """build the retained-operand program for site S -> new word dict, or None if no helper slot / unsupported"""
    I = Idx(w); prog = w['program']; n = I.n; a, b, g, f = S['a'], S['b'], S['g'], S['f']
    rm = {a, b}; ins = collections.defaultdict(list)
    ins[a].append(['MOVE', S['s'], S['prev'], g] + list(prog[a][4:]))
    lifes = [(lt['t0'], lt['t1']) for r in I.lts if r >= n for lt in I.lts[r]]
    taken = []                                         # (idx, t_init, t_clear) of helpers we allocate
    def alloc(t0, t1):
        for h in range(n, n + 64):
            if all(o[1] < t0 or o[0] > t1 for o in [(lt['t0'], lt['t1']) for lt in I.lts.get(h, [])]) and all(x[0] != h or x[2] < t0 or x[1] > t1 for x in taken):
                taken.append((h, t0, t1)); return h
        return None
    for R in S['readers']:
        r, ra, tl = R['r'], R['ra'], R['tl']; t1 = R['reads'][0]
        rm.add(ra); rm.update(R['reads']); mt = ra if mv == 'ra' else t1
        mvr = prog[ra]
        if mv == 'ra': ins[ra].append(['MOVE', r, R['pf'], g] + list(mvr[4:]))
        else:
            if mt <= a: return None
            ins[t1].append(['MOVE', r, R['pf'], g] + list(mvr[4:]))
        for t in R['reads']: ins[t].append(['ADD', r, S['s'], prog[t][3], g])
        arr = [['MOVE', r, g, f] + list(mvr[4:])]; clr = []
        for t in R['stranded']:
            e = prog[t]; q = e[2]
            if I.frame_at(q, tl + 1) == f and I.unwritten(q, t, tl) and I.frame_at(q, t) == f:
                arr.append(['ADD', r, q, e[3], f]); rm.add(t)
            else:
                h = alloc(t, tl + 1)
                if h is None: return None
                rm.add(t); ins[t] += [['INIT', h, f], ['COPY', h, q, '1', f]]
                arr.append(['ADD', r, h, e[3], f]); clr.append(['CLEAR', h, f])
        ins[tl + 1] = ins[tl + 1] + arr + clr
    out = []
    for t, e in enumerate(prog):
        out += ins.get(t, [])
        if t not in rm: out.append(e)
    out += ins.get(len(prog), [])
    w2 = dict(w); w2['program'] = out
    return w2

def judge(w):
    _paths(); import incr
    from tkcommon import profile_of
    iw = incr.IncrWord(w, profile=profile_of(w)[0])
    return iw.legal_all, iw.kappa, iw.viol[:3]

def run(w, mx=50, dry=False, skip=(), log=print):
    """greedy: returns (word, kappa, accepted list).  skip = set of (s, f) frozen sites (e.g. root 2 frame 520)"""
    ok0, k0, v0 = judge(w); log('base legal %s kappa %.15f' % (ok0, k0)); acc = []; tried = set()
    for it in range(mx):
        ss = [x for x in sites(w) if x['save'] > 1e-9 and (x['s'], x['f'], x['g']) not in tried and (x['s'], x['f']) not in skip]
        log('round %d: %d positive sites %s' % (it, len(ss), [(round(x['save'], 2), x['s'], x['chain'], x['f'], x['g'], len(x['readers'])) for x in ss[:6]]))
        if not ss or dry: break
        hit = False
        for S in ss:
            tried.add((S['s'], S['f'], S['g'])); best = None
            for mv in ('ra', 'late'):
                w2 = apply(w, S, mv)
                if w2 is None: log('  site s%d f%d g%d mv=%s: not buildable' % (S['s'], S['f'], S['g'], mv)); continue
                ok, k, v = judge(w2)
                log('  site s%d %s drop %d -> read at %d mv=%s: legal %s kappa %.15f (d %+.3e) %s' % (S['s'], S['chain'], S['f'], S['g'], mv, ok, k, k - k0, v if not ok else ''))
                if ok and k > k0 + 1e-15 and (best is None or k > best[1]): best = (w2, k, mv)
            if best:
                w, k0 = best[0], best[1]; acc.append(dict(s=S['s'], f=S['f'], g=S['g'], save=S['save'], mv=best[2], kappa=k0)); hit = True; break
        if not hit: break
    return w, k0, acc

def main(argv=None):
    a = sys.argv[1:] if argv is None else list(argv); inp, out = a[0], a[1]
    mx = int(a[a.index('--max') + 1]) if '--max' in a else 50
    w = json.load(gzip.open(inp))
    skip = set()
    if '--skip' in a:
        for x in a[a.index('--skip') + 1].split(','): sreg, ff = x.split(':'); skip.add((int(sreg), int(ff)))
    if '--census' in a:
        for S in sites(w): print(round(S['save'], 3), 's', S['s'], 'chain', S['chain'], 'f', S['f'], 'g', S['g'], 'readers', [(R['r'], len(R['reads']), len(R['stranded'])) for R in S['readers']])
        return 0
    w, k0, acc = run(w, mx, '--dry' in a, skip)
    if acc:
        with gzip.open(out, 'wt') as fh: json.dump(w, fh)
    print('RETAIN accepted %d sites, kappa %.15f %s' % (len(acc), k0, acc), flush=True)
    return 0

if __name__ == '__main__': sys.exit(main())
