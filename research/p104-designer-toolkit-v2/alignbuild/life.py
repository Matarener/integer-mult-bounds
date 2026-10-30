"""ALIGNLAW life.py: per-helper lifetime ledger of a word (LAWFIRST split R0 = F - L), Shapley birth/end split, frame classification.
usage: life.py WORD OUT.pkl     (venv python -B; no env at import; read-only)
Per public helper h: chain dims, birth frame, end frame, L_h = tax(0,mid,9) - tax(actual), Shapley split into Lb (birth) and Le (end),
birth/end frame class: Operp(r) (octet dual, dim 5), O(r) (octet frame, dim 4), other; co-newborns / co-enders at the frame; signal flag (touches owned)."""
import sys, gzip, json, math, pickle, collections
import os
TK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [TK, TK + '/synth']

def tax(ds):
    sd = sorted(set(ds)); D = sd[-1] - sd[0]
    return 0.0 if D == 0 else sum((b - a) * math.log(D / (b - a)) for a, b in zip(sd, sd[1:]))
def rref(vs):
    b = []
    for v in vs:
        for x in b:
            if v ^ x < v: v ^= x
        if v: b = [x ^ v if x ^ v < x else x for x in b] + [v]
    return tuple(sorted(b, reverse=True))
def dot(a, b): return bin(a & b).count('1') & 1
def perp(B): return rref([v for v in range(1, 512) if all(dot(v, x) == 0 for x in B)])
D3 = [120, 85, 75, 51, 102, 30, 45]; T = 384

def octets(w, role):
    n = len(w['initial']); X = [r for r in range(n) if role(r) == 'X']
    port = {r: w['frames'][w['initial'][r]][0] for r in X}
    P = sorted(set(port.values()))
    cos = {v: min(v ^ d for d in D3 + [0]) for v in P}
    oc = {v: min(cos[v], min(v ^ T ^ d for d in D3 + [0])) for v in P}
    mem = collections.defaultdict(list)
    for v in P: mem[oc[v]].append(v)
    keys = sorted(mem); O = {k: rref(mem[k]) for k in keys}
    return keys, O, {k: perp(O[k]) for k in keys}, port, oc

def ledger(w):
    import kernel2net as KN
    n = len(w['initial']); role = KN.roles(w); fb = w['frames']; dim = [len(b) for b in fb]; span = [rref(b) for b in fb]
    keys, O, G, port, oc = octets(w, role)
    Oinv = {O[k]: i for i, k in enumerate(keys)}; Ginv = {G[k]: i for i, k in enumerate(keys)}
    ch = KN.chains(w)   # r -> list of frame indices
    otouch = set()
    for e in w['program']:
        if e[0] in ('ADD', 'COPY') and (e[1] >= n or e[2] >= n): otouch.add(e[1]); otouch.add(e[2])
    def fclass(f):
        s = span[f]
        if s in Oinv: return 'O%d' % Oinv[s]
        if s in Ginv: return 'G%d' % Ginv[s]
        return 'd%d' % dim[f]
    rows = {}
    born = collections.defaultdict(list); ends = collections.defaultdict(list)
    for r, c in ch.items():
        if r >= n or role(r) != 'H': continue
        ds = [dim[f] for f in c]; sd = tuple(sorted(set(ds)))
        mid = tuple(d for d in sd if 0 < d < 9)
        a = tax(sd); full = tax((0,) + mid + (9,))
        b0 = sd[0] > 0; e9 = sd[-1] < 9
        if b0 and e9:
            # Shapley over the two moves {birth late, end early}
            Lb = 0.5 * ((full - tax(mid + (9,))) + (tax((0,) + mid) - tax(mid)))
            Le = 0.5 * ((full - tax((0,) + mid)) + (tax(mid + (9,)) - tax(mid)))
        else:
            Lb = full - a if b0 else 0.0; Le = full - a if e9 else 0.0
        rows[r] = dict(r=r, sd=sd, chain=list(c), F=full, A=a, L=full - a, Lb=Lb, Le=Le, bf=c[0], ef=c[-1],
                       bcls=fclass(c[0]), ecls=fclass(c[-1]), sig=r in otouch, b0=b0, e9=e9)
        if b0: born[c[0]].append(r)
        if e9: ends[c[-1]].append(r)
    for r, x in rows.items():
        x['kb'] = len(born[x['bf']]) if x['b0'] else 0
        x['ke'] = len(ends[x['ef']]) if x['e9'] else 0
    mains = {}
    for r, c in ch.items():
        if r < n and role(r) in 'XY':
            ds = tuple(sorted(set(dim[f] for f in c))); mains[r] = dict(role=role(r), sd=ds, tax=tax(ds), chain=list(c), cls=[fclass(f) for f in c])
    return dict(rows=rows, born=dict(born), ends=dict(ends), mains=mains, keys=keys, O=O, G=G, span=span, dim=dim, fcls={f: fclass(f) for f in range(len(fb))})

if __name__ == '__main__':
    import dag as Dg
    w = Dg.load(sys.argv[1]); R = ledger(w)
    pickle.dump(R, open(sys.argv[2], 'wb'))
    rows = R['rows']
    F = sum(x['F'] for x in rows.values()); A = sum(x['A'] for x in rows.values())
    print('helpers %d F %.1f actual %.1f L %.1f  (births %d Lb %.1f, ends %d Le %.1f)' % (len(rows), F, A, F - A,
          sum(x['b0'] for x in rows.values()), sum(x['Lb'] for x in rows.values()), sum(x['e9'] for x in rows.values()), sum(x['Le'] for x in rows.values())))
    for sig in (False, True):
        S = [x for x in rows.values() if x['sig'] == sig]
        print(' signal=%s: n %d F %.1f A %.1f L %.1f' % (sig, len(S), sum(x['F'] for x in S), sum(x['A'] for x in S), sum(x['L'] for x in S)))
    c = collections.defaultdict(lambda: [0, 0.0])
    for x in rows.values():
        if x['b0']: k = ('birth', x['bcls'][0], x['kb'] >= 4); c[k][0] += 1; c[k][1] += x['Lb']
        if x['e9']: k = ('end', x['ecls'][0], x['ke'] >= 3); c[k][0] += 1; c[k][1] += x['Le']
    for k, v in sorted(c.items()): print('  %-24s n %3d L %.1f' % (k, v[0], v[1]))
