"""Rigorous relaxation of the arrival-pair bound (see arrivals_lb.py docstring).
For a fixed port q: every subspace Y containing q gives a pair (n(Y), o(Y)) = (#ports in Y, #ports in Y^perp).
A chain <q> = Y_1 < Y_2 < ... yields cost  sum_i (o_i - o_{i+1}) / n_i  (o_{last+1} = 0),
with n nondecreasing and o nonincreasing along the chain.  We minimise over ALL sequences of achievable pairs
(one per dimension, monotone), ignoring nestedness -> a valid lower bound for f(<q>).
Enumeration: Y of dim 2..4 directly (quotient by q), Y of dim 5..8 via Z = Y^perp inside P_q (dim 4..1)."""
import json, sys, itertools, time
from fractions import Fraction as Fr
N = json.load(open('NORMALIZERS.json')); qs = [p['q'] for p in N['ports']]; P = len(qs)
dot = lambda u, v: bin(u & v).count('1') & 1
isport = [0] * 512
for x in qs: isport[x] = 1
def span(vs):
    s = {0}
    for v in vs:
        if v not in s: s |= {x ^ v for x in s}
    return s
def basis_complement(vs, n=9):
    """extend list vs (independent) to a basis of F2^9; return the extra vectors"""
    b = []; piv = []
    def red(v):
        for x in b: v = min(v, v ^ x)
        return v
    for v in vs:
        r = red(v)
        if r: b.append(r)
    extra = []
    for i in range(n):
        r = red(1 << i)
        if r: b.append(r); extra.append(1 << i)
    return extra
def subspaces(gens, kmax):
    """yield (k, rows) for all subspaces of span(gens) of dim 1..kmax (streaming, constant memory)"""
    m = len(gens)
    def vec(bits):
        v = 0
        for i in range(m):
            if bits >> i & 1: v ^= gens[i]
        return v
    for k in range(1, kmax + 1):
        for pivots in itertools.combinations(range(m), k):
            frees = [[c for c in range(pivots[j] + 1, m) if c not in pivots] for j in range(k)]
            for choice in itertools.product(*[range(1 << len(f)) for f in frees]):
                rows = []
                for j in range(k):
                    bits = 1 << pivots[j]
                    for t, c in enumerate(frees[j]):
                        if choice[j] >> t & 1: bits |= 1 << c
                    rows.append(vec(bits))
                yield k, rows
def run(Q):
    q = qs[Q]
    pairs = {1: {(1, sum(1 for x in qs if dot(x, q) == 0))}}
    # Y = <q> + W, W from a complement of q, dim 1..3
    comp = basis_complement([q])
    for k, rows in subspaces(comp, 3):
        Y = span([q] + rows)
        n = sum(isport[x] for x in Y)
        o = sum(1 for x in qs if all(dot(x, y) == 0 for y in rows) and dot(x, q) == 0)
        pairs.setdefault(k + 1, set()).add((n, o))
    # Z inside P_q = q^perp, dim 1..4  ->  Y = Z^perp of dim 8..5
    Pq = [v for v in range(1, 512) if dot(v, q) == 0]
    gens = []
    sp = {0}
    for v in Pq:
        if v not in sp: gens.append(v); sp |= {x ^ v for x in sp}
    for k, rows in subspaces(gens, 4):
        Z = span(rows)
        o = sum(isport[x] for x in Z)
        n = sum(1 for x in qs if all(dot(x, z) == 0 for z in rows))
        pairs.setdefault(9 - k, set()).add((n, o))
    # no pruning: keep every achievable (n, o) pair, so any real chain is representable exactly
    for d in pairs: pairs[d] = sorted(pairs[d], key=lambda t: (-t[0], -t[1]))
    # DP over dims: state (n, o) after choosing a pair at the current top dim; cost so far
    states = {(1, pairs[1][0][1]): Fr(0)}
    best = None
    for d in range(2, 9):
        new = dict(states)
        for (n0, o0), c0 in states.items():
            for n, o in pairs[d]:
                if n < n0 or o > o0: continue
                c = c0 + Fr(o0 - o, n0)
                key = (n, o)
                if key not in new or c < new[key]: new[key] = c
        states = new
    # finish: all remaining receivers assigned to last subspace
    best = min(c + Fr(o, n) for (n, o), c in states.items())
    return best, {d: pairs[d][:6] for d in pairs}
t0 = time.time()
Qlist = [int(x) for x in sys.argv[1:]] or [0]
import os
done = set()
if os.path.exists('results.jsonl'):
    for line in open('results.jsonl'):
        try: done.add(json.loads(line)['q'])
        except Exception: pass
for line in open(__file__.replace('arrivals_lb2.py', 'lb_done_from_logs.txt')) if os.path.exists(__file__.replace('arrivals_lb2.py', 'lb_done_from_logs.txt')) else []:
    done.add(int(line.split()[0]))
for Q in Qlist:
    if Q in done: continue
    b, fr = run(Q)
    print('q=%d  lower bound f(<q>) >= %s = %.4f   (%.0fs)' % (Q, b, float(b), time.time() - t0), flush=True)
    with open('results.jsonl', 'a') as fh: fh.write(json.dumps(dict(q=Q, num=b.numerator, den=b.denominator)) + chr(10))
    if Q == Qlist[0]:
        for d in sorted(fr): print('   dim', d, 'Pareto (n, o):', fr[d])
