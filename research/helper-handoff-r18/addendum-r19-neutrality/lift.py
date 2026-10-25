"""R19 priced-lift relay screen on the #4610 word.

Generalises R18 relay.py: a hand-off of helper h at frame F (time j) needs every register holding h_in at F
and (h_in,()) in the Q-span of rows at F.  R18 required this with the EXISTING frames (0 hits).  Here a
register r that is not at F may be LIFTED: between r's previous anchor (scalar op / warp, frame P) and its
next anchor (frame N) r has only climbs, which can be re-timed and re-chosen; if span(P) <= F <= span(N)
the chain becomes P -> F -> N.  Its paid rank mass is unchanged; cost = f-sum(new chain) - f-sum(old chain)
(0 when the old chain already visits F).  Net = g(dF-d0, d1-dF) - sum lift costs, f(x) = x^(1-C).
Usage: lift.py forward|backward [maxmand]"""
import sys, gzip, json, bisect, math
from collections import Counter, defaultdict
from fractions import Fraction as Q
from pathlib import Path
R = Path.home()/'imb-r19'
sys.path.insert(0, str(R/'research/kappa-causal-continuation/buffer-borrowing'))
import verify_buffers as v
w = json.loads(gzip.decompress((R/'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz').read_bytes()))
c = w['canonical']; fr = c['frames']; SP = [frozenset(v.span(f)) if f else frozenset({0}) for f in fr]
C = 0.00302728825
import os; DIAG = os.environ.get('DIAG') == '1'
def f(x): return x ** (1 - C) if x > 0 else 0.0
def g(a, b): return f(a) + f(b) - f(a + b)
def dim(F): return len(fr[F])

def timelines(prog):
    anch = defaultdict(list); clb = defaultdict(list)
    for j, e in enumerate(prog):
        k = e[0]
        if k == 'scalar':
            gg, frame = e[1:]
            for r in gg[1:3]:
                if isinstance(r, list): anch[tuple(r)].append((j, frame, frame))
        elif k == 'warp':
            anch[tuple(e[1])].append((j, e[3], e[4]))
        elif k == 'climb':
            clb[('L', e[2])].append((j, e[3], e[4], e[5]))
        elif k == 'center':
            anch[('C', e[1])].append((j, e[2], e[3]))
    return anch, clb

def lift_cost(r, j, F, anch, clb):
    """cost to have r at frame F right after event j (None if impossible)."""
    if r[0] != 'L': return None
    i = r[1]; A = anch[r]; idx = [a[0] for a in A]
    p = bisect.bisect_right(idx, j)
    P = A[p - 1][2] if p else c['start'][i]
    N = A[p][1] if p < len(A) else c['final'][i]
    lo = A[p - 1][0] if p else -1; hi = A[p][0] if p < len(A) else 10**9
    chain = [x for x in clb[r] if lo < x[0] < hi]
    visited = {P} | {x[2] for x in chain}
    if F in visited: return 0.0
    if not (SP[P] <= SP[F] <= SP[N]): return None
    old = sum(f(x[3]) for x in chain)
    return f(dim(F) - dim(P)) + f(dim(N) - dim(F)) - old

def reduce(x, piv):
    x = dict(x)
    for k, rr in piv:
        a = x.get(k)
        if a:
            for kk, vv in rr.items():
                nv = x.get(kk, Q(0)) - a * vv
                if nv: x[kk] = nv
                else: x.pop(kk, None)
    return x

def addpiv(vec, piv):
    x = reduce(vec, piv)
    if not x: return False
    k = next(iter(x)); a = x[k]; x = {kk: vv / a for kk, vv in x.items()}
    for k2, r2 in piv:
        b = r2.get(k)
        if b:
            for kk, vv in x.items():
                nv = r2.get(kk, Q(0)) - b * vv
                if nv: r2[kk] = nv
                else: r2.pop(kk, None)
    piv.append((k, x)); return True

def screen(side, maxmand=4):
    back = side == 'backward'; prog = w['programs'][side]
    anch, clb = timelines(prog)
    rows = {('L', i): v.identity(('L', i)) for i in range(632)}; rows['C', 0] = v.identity(('C', 0))
    cur = {('L', i): fm for i, fm in enumerate(c['start'])}; cur['C', 0] = None
    inv = defaultdict(set)
    for r, row in rows.items():
        for (var, wd) in row: inv[var].add(r)
    atF = defaultdict(set)
    for r, fm in cur.items(): atF[fm].add(r)
    def setf(r, fm): atF[cur[r]].discard(r); cur[r] = fm; atF[fm].add(r)
    climbs_left = Counter(e[2] for e in prog if e[0] == 'climb')
    helpers = [('L', i) for i in range(224, 632)]
    seen = set(); diag = {}; hver = Counter()
    best = {}            # (i, dF) -> (net, j, mandatory, extra)
    mandhist = Counter(); stats = Counter()
    for j, e in enumerate(prog):
        k = e[0]
        if k == 'scalar':
            gg, frame = e[1:]; t = tuple(gg[1]); hver[t[1]] += 1
            old = {var for (var, wd) in rows[t]}
            if gg[0] == 'clear': rows[t] = {}; setf(t, frame)
            elif gg[0] == 'copy': rows[t] = dict(rows[tuple(gg[2])])
            elif gg[0] == 'add': v.add(rows[t], rows[tuple(gg[2])], Q(gg[3], gg[4]))
            else: q = Q(gg[2], gg[3]); rows[t] = {a: q * x for a, x in rows[t].items()}
            new = {var for (var, wd) in rows[t]}
            for var in old - new: inv[var].discard(t)
            for var in new - old: inv[var].add(t)
        elif k == 'warp':
            _, r, op, of, nf = e; t = tuple(r); rows[t] = v.warp(rows[t], op, back); setf(t, nf)
        elif k == 'climb':
            setf(('L', e[2]), e[4]); climbs_left[e[2]] -= 1
        elif k == 'center':
            setf(('C', e[1]), e[3])
        else:
            continue
        if j + 1 < len(prog) and prog[j + 1][0] == 'climb' and prog[j + 1][2] == e[2] if k == 'climb' else False:
            pass
        for h in helpers:
            i = h[1]
            if climbs_left[i] <= 0: continue
            F = cur[h]; dF = dim(F); d0 = dim(c['start'][i]); d1 = dim(c['final'][i])
            if not d0 < dF: continue
            gain = g(dF - d0, d1 - dF)
            mand = inv[h] - atF[F]
            stats['points'] += 1
            if len(mand) > maxmand: stats['too many holders'] += 1; continue
            mandhist[min(len(mand), 10)] += 1
            cost = 0.0; ok = True
            for r in mand:
                lc = lift_cost(r, j, F, anch, clb)
                if lc is None: ok = False; break
                cost += lc
                if cost >= gain: break
            if not ok: stats['holder not liftable'] += 1; continue
            if cost >= gain: stats['holder lifts exceed gain'] += 1; continue
            if any(wd != () for r in inv[h] for (var, wd) in rows[r] if var == h): stats['nontrivial word'] += 1; continue
            key = (i, dF)
            if key in best and best[key][0] >= gain - cost: continue
            dkey = (i, F, hver[i], frozenset(mand))
            if DIAG and dkey in seen: continue
            seen.add(dkey)
            cmand = cost
            piv = []
            for r in atF[F] | mand: addpiv(rows[r], piv)
            target = {(h, ()): Q(1)}
            res = reduce(target, piv); extra = []
            if res:
                stats['span check needs extra'] += 1
                vars_ = {var for (var, wd) in res}
                cands = set()
                for var in vars_: cands |= inv[var]
                cands -= atF[F] | mand
                priced = []
                for r in cands:
                    lc = lift_cost(r, j, F, anch, clb)
                    if lc is not None and (DIAG or cost + lc < gain): priced.append((lc, r))
                priced.sort()
                for lc, r in priced:
                    if cost + lc >= gain and not DIAG: break
                    if addpiv(rows[r], piv):
                        extra.append(r); cost += lc
                        res = reduce(target, piv)
                        if not res: break
                if DIAG:
                    nv = len({var for (var, wd) in res})
                    dk = (i, dF); val = (cost if not res else 99.0, nv, len(extra), j, gain, cmand)
                    if dk not in diag or val < diag[dk]: diag[dk] = val
                if res or cost >= gain: stats['span fails within budget'] += 1; continue
            stats['NET POSITIVE'] += 1
            best[key] = (gain - cost, j, sorted(mand), extra, gain, cost)
    print(side, 'points', stats['points'], dict(stats), 'mandatory-lift histogram', dict(sorted(mandhist.items())), flush=True)
    if DIAG:
        print(side, 'DIAG per (helper,dF): min total lift cost to complete the span (99 = unliftable residual)')
        hist = Counter()
        for (i, dF), (tc, nv, ne, j, gain, cm) in sorted(diag.items(), key=lambda kv: kv[1][0] - kv[1][4]):
            hist[(dF, 'net<=-%.3f' % (round((tc - gain) * 1000) / 1000) if tc < 90 else 'residual-unliftable')] += 1
        best_rows = sorted(diag.items(), key=lambda kv: kv[1][0] - kv[1][4])[:25]
        for (i, dF), (tc, nv, ne, j, gain, cm) in best_rows:
            print('   h%d dF=%d gain %.5f holder-cost %.5f total %.5f net %.5f residual-vars %d extra %d event %d' % (i, dF, gain, cm, tc, gain - tc, nv, ne, j))
        print(side, 'DIAG count', len(diag), 'unliftable', sum(1 for x in diag.values() if x[0] > 90))
    tot = Counter((dim(c['start'][i]), dF, dim(c['final'][i])) for (i, dF) in best)
    print(side, 'helpers with a net-positive priced hand-off:', len({i for i, _ in best}), dict(sorted(tot.items())))
    for key, val in sorted(best.items(), key=lambda kv: -kv[1][0])[:40]:
        print('  ', key, 'net %.6f gain %.6f cost %.6f event %d mand %s extra %s' % (val[0], val[4], val[5], val[1], val[2], val[3]))
    return best

if __name__ == '__main__':
    side = sys.argv[1]; mm = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    screen(side, mm)
