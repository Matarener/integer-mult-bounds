"""library.py LIST OUT.jsonl : SUBCIRC variant library (secondary deliverable). For every word in LIST (paths) that shares #6030's register numbering:
legal.check (fast oracle), exact kappa (price_exact), and the per-register diff vs #6030: frame chain (frames identified by SPAN, so re-appended
tables still match) and dim chain, with the EXACT per-register invoice term g_r(k0) = 18[helper] span^(1-k0) - 18 sum jumps^(1-k0) (SUBCIRC sec 1).
Owned MOVE multisets compared as a whole.  Output one JSON line per word."""
import sys, os, json, gzip, math, collections
sys.path[:0] = [os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')) + '/infra', os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))]
import legal, price_exact as X, tkcommon as C
BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')) + '/words/6030.json.gz'
def load(p): return json.load(gzip.open(p))
def cload(p):
    return C.load(p)[1]   # activates the word's verifier profile (runtime)
def spankey(b):
    s = {0}
    for v in b: s |= {x ^ v for x in s}
    return frozenset(s)
def chains(w):
    n = len(w['initial']); K = [spankey(b) for b in w['frames']]; dim = [len(b) for b in w['frames']]
    ch = {r: [w['initial'][r]] for r in range(n)}; own = []
    for e in w['program']:
        if e[0] == 'MOVE':
            if e[1] < n: ch[e[1]].append(e[3])
            else: own.append((len(w['frames'][e[2]]), len(w['frames'][e[3]])))
    return {r: (tuple(K[f] for f in c), tuple(dim[f] for f in c)) for r, c in ch.items()}, sorted(own)
def g(dims, helper, k):
    e = 1 - k; js = [abs(b - a) for a, b in zip(dims, dims[1:])]
    return 18 * ((dims[-1] - dims[0]) ** e if helper and dims[-1] > dims[0] else 0) - 18 * sum(j ** e for j in js if j)
def main(lst, out):
    b = cload(BASE); cb, ob = chains(b); n = len(b['initial']); live = set(b['live']); main_ = live | {r + 112 for r in live}
    rep = legal.check(b); k0 = X.kappa(*X.invoice(rep))
    bid = {k: i for i, k in enumerate(spankey(x) for x in b['frames'])}
    fo = open(out, 'w')
    for p in [l.strip() for l in open(lst) if l.strip()]:
        try: w = cload(p)
        except Exception as ex: continue
        if not isinstance(w, dict) or 'program' not in w or abs(len(w.get('initial', [])) - n) > 12: continue
        try:
            cw, ow = chains(w)
        except Exception: continue
        same = sum(1 for r in range(min(n, len(cw))) if cw[r] == cb[r])
        if same < 700: continue
        try:
            rw = legal.check(w); kw = X.kappa(*X.invoice(rw)); ok = rw['ok']
        except Exception as ex: ok = False; kw = None
        diffs = []
        for r in range(max(n, len(cw))):
            a = cb.get(r); c = cw.get(r)
            if a == c: continue
            hel = r < n and r not in main_
            da = None if a is None else g(a[1], hel, k0); dc = None if c is None else g(c[1], hel, k0)
            diffs.append(dict(r=r, base_dims=None if a is None else a[1], var_dims=None if c is None else c[1],
                              base_frames=None if a is None else [bid.get(x, -1) for x in a[0]], var_frames=None if c is None else [bid.get(x, -1) for x in c[0]],
                              dims_same=(a is not None and c is not None and a[1] == c[1]), dg=None if (da is None or dc is None) else dc - da))
        dT = collections.Counter(); dP = collections.Counter()
        for x in diffs:
            for dims, sg in ((x['base_dims'], -1), (x['var_dims'], 1)):
                if dims is None: continue
                for a_, b_ in zip(dims, dims[1:]):
                    if a_ != b_: dP[abs(b_ - a_)] += 18 * sg
                if x['r'] < n and x['r'] not in main_ and dims[-1] > dims[0]: dT[dims[-1] - dims[0]] += 18 * sg
        T0, P0 = X.invoice(rep); T1 = collections.Counter(T0); P1 = collections.Counter(P0); T1.update(dT); P1.update(dP)
        kpred = X.kappa({k: v for k, v in T1.items() if v}, {k: v for k, v in P1.items() if v}) if ow == ob else None
        fo.write(json.dumps(dict(path=p, dk_pred=None if kpred is None else kpred - k0, n=len(cw), legal=ok, viol=None if ok else str(rw['violations'][:2]) if 'rw' in dir() else None, kappa=kw, dk=None if kw is None else kw - k0,
                                 owned_same=(ow == ob), ndiff=len(diffs), diffs=diffs)) + '\n'); fo.flush()
if __name__ == '__main__': main(sys.argv[1], sys.argv[2])
