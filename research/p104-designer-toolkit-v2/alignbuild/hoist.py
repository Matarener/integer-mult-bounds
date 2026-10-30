"""GENUPGRADE hoist.py: H-HOIST (gauge stop drop) as an AUTOMATED builder step -- the edit IOROOT2 did by hand with prep.py (r2b -> r245g).
Rule (IOROOT2 hoistcensus, RULEMINE sec 1 companion): a public stop (p, f) whose events are all reads p += c q can be dropped if every source q
has the SAME value (no write to q in between) at a time s when q sits at p's previous or next frame g and p can sit at g at s.
Construction (value-exact by Lemma 7 commutation; legality + exact kappa decided by IncrWord, the arbiter):
  g = next: drop MOVE prev->f, the reads at f and MOVE f->g; insert MOVE prev->g at min(first slot, old MOVE-in time); reads of p at prev after
            that point (F0 pre-reads etc.) move just before it; each read becomes ADD p += c q at g just after its slot event s.
  g = prev: drop MOVE prev->f, the reads, MOVE f->next; reads become ADD at g after event s; MOVE prev->next at the old MOVE-out time (or right after
            the last moved read if later); reads of p at prev after the first slot move before it.
A site is accepted only if the word is LEGAL (all finals exact) and kappa strictly up; re-census after each accepted site.
usage: hoist.py WORD OUT.json.gz [--max N] [--dry]     (no env at import; the copied census leaves IOROOT2/hoistcensus.py untouched)"""
import sys, os, json, gzip, math, bisect, collections
HERE = os.path.dirname(os.path.abspath(__file__)); W = os.path.dirname(HERE); TK = W

def _paths():
    for p in (HERE, TK):
        if p not in sys.path: sys.path.insert(0, p)

def sites(w):
    """copy of IOROOT2/hoistcensus.py as a function -> list of dict(save, p, j, f, g, gi, slots, evs, srcmv)"""
    _paths(); import sigside as sigb
    prog = w['program']; fr = w['frames']; n = len(w['initial']); dim = [len(b) for b in fr]
    L = sigb.lifetimes(w, prog); st = sigb.stays_pub(w, prog); live = set(w['live'])
    def jl(ds): return sum(abs(y - x) * math.log(abs(y - x)) for x, y in zip(ds, ds[1:]) if y != x)
    def cost(r, ds):
        D = ds[-1] - ds[0]; helper = r not in live and r - 112 not in live
        return (D * math.log(D) if helper and D > 0 else 0) - jl(ds)
    ev = collections.defaultdict(list); wr = collections.defaultdict(list); loc = collections.defaultdict(list)
    for t, e in enumerate(prog):
        if e[0] == 'MOVE':
            if e[1] >= n: loc[e[1]].append((t, e[3]))
            continue
        if e[0] == 'INIT': loc[e[1]].append((t, e[2]))
        for r in sigb.S.regfields(e): ev[r].append(t)
        if e[0] in ('ADD', 'COPY', 'SCALE', 'INIT', 'CLEAR'): wr[e[1]].append(t)
    def frame_at(q, s):
        if q < n:
            for f, a, b in st[q]:
                if a < s < b: return f
            return None
        xs = loc[q]; i = bisect.bisect_right([x[0] for x in xs], s) - 1
        if i < 0: return None
        return xs[i][1] if sigb.lid_at(L, q, s) is not None else None
    def unwritten(q, t0, t1):
        a, b = min(t0, t1), max(t0, t1); W_ = wr[q]; i = bisect.bisect_right(W_, a); return not (i < len(W_) and W_[i] <= b)
    out = []
    for p in range(n):
        ch = st[p]; ds = [dim[f] for f, _, _ in ch]
        for j in range(1, len(ch) - 1):
            f, a, b = ch[j]; evs = [t for t in ev[p] if a < t < b]
            if not evs or any(prog[t][0] != 'ADD' or prog[t][1] != p for t in evs): continue
            srcs = {prog[t][2] for t in evs}
            prev_last = max([t for t in wr[p] if t < a] + [-1]); next_first = min([t for t in ev[p] if t > b] + [len(prog)])
            srcmv = [t for t in ev[p] if prev_last < t < a and t not in wr[p]]
            for gi in (j - 1, j + 1):
                g = ch[gi][0]; ok = True; slots = []
                for q in srcs:
                    tq = [t for t in evs if prog[t][2] == q]; found = None
                    for s in sorted({prev_last + 1, next_first - 1} | {x + 1 for x in ev[q] if prev_last < x < next_first} | {x for x in ev[q] if prev_last < x < next_first}):
                        if not (prev_last < s < next_first): continue
                        if frame_at(q, s) == g and all(unwritten(q, s, t) for t in tq): found = s; break
                    if found is None: ok = False; break
                    slots.append((q, found))
                if ok:
                    out.append(dict(save=cost(p, ds) - cost(p, ds[:j] + ds[j + 1:]), p=p, j=j, f=f, g=g, gi=gi, a=a, b=b, prev=ch[j - 1][0], nxt=ch[j + 1][0],
                                    slots=slots, evs=evs, srcmv=srcmv, chain=''.join(map(str, ds))))
    out.sort(key=lambda x: -x['save'])
    return out

def apply(w, S):
    """build the hoisted program for site S (see module doc) -> new word dict"""
    prog = w['program']; p = S['p']; a, b = S['a'], S['b']; nextg = S['gi'] > S['j']
    rm = {a, b} | set(S['evs'])
    ins = collections.defaultdict(list)                 # insert before original index
    reads = collections.defaultdict(list)
    for q, s in S['slots']:
        for t in S['evs']:
            if prog[t][2] == q: reads[s + 1].append(['ADD', p, q, prog[t][3], S['g']])   # q is at g right AFTER event s (an owned arrival MOVE may be event s)
    s0 = min(s for _, s in S['slots']); smax = max(s for _, s in S['slots'])
    if nextg:
        tm = min(s0, a)
        mv = [t for t in S['srcmv'] if t >= tm]
        for t in mv: ins[tm].append(prog[t]); rm.add(t)
        ins[tm].append(['MOVE', p, S['prev'], S['g']] + list(prog[a][4:]))
        for s, es in reads.items(): ins[s] += es
    else:
        mv = [t for t in S['srcmv'] if t >= s0]
        for t in mv: ins[s0].append(prog[t]); rm.add(t)
        for s, es in reads.items(): ins[s] += es
        tm = b if smax + 1 < b else smax + 1
        ins[tm].append(['MOVE', p, S['prev'], S['nxt']] + list(prog[b][4:]))
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

def main(argv=None):
    a = sys.argv[1:] if argv is None else list(argv); inp, out = a[0], a[1]
    mx = int(a[a.index('--max') + 1]) if '--max' in a else 50
    w = json.load(gzip.open(inp))
    if not os.environ.get('TK_PROFILE'):      # a hoisted word keeps its input's inventory: judge it under the INPUT word's profile
        _paths(); import tkcommon as _C; os.environ['TK_PROFILE'] = _C.profile_of(w)[0]
    ok0, k0, v0 = judge(w)
    print('base legal %s kappa %.15f' % (ok0, k0), flush=True)
    acc = []; tried = set()
    for it in range(mx):
        ss = [s for s in sites(w) if s['save'] > 1e-9 and (s['p'], s['f'], s['g']) not in tried]
        print('round %d: %d positive sites %s' % (it, len(ss), [(round(s['save'], 2), s['p'], s['chain'], s['f'], s['g']) for s in ss[:6]]), flush=True)
        if not ss or '--dry' in a: break
        hit = False
        for S in ss:
            tried.add((S['p'], S['f'], S['g']))
            w2 = apply(w, S); ok, k, v = judge(w2)
            print('  site p%d %s drop %d -> read at %d: legal %s kappa %.15f (d %+.3e) %s' % (S['p'], S['chain'], S['f'], S['g'], ok, k, k - k0, v if not ok else ''), flush=True)
            if ok and k > k0 + 1e-15:
                w, k0 = w2, k; acc.append(dict(p=S['p'], f=S['f'], g=S['g'], save=S['save'], kappa=k)); hit = True; break
        if not hit: break
    if acc:
        with gzip.open(out, 'wt') as fh: json.dump(w, fh)
    print('HOIST accepted %d sites, kappa %.15f %s' % (len(acc), k0, acc), flush=True)
    return 0

if __name__ == '__main__': sys.exit(main())
