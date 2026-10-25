# Exact gauge annealing of a plane-port decoder M = sum_k u_k v_k^T over F2.
# Move (i != j):  u_i <- u_i + u_j,  v_j <- v_j + v_i.   Then u_i' v_i^T + u_j v_j'^T = u_i v_i^T + u_j v_j^T (mod 2),
# so M is unchanged EXACTLY; only the plane supports, hence the tariffs, change.  Terms with u = 0 or v = 0 vanish.
# Usage: python v4_gauge.py <decoder.json> <seconds> <seed>
import json, math, random, sys, time
from v4lib import *
src, budget, seed = sys.argv[1], float(sys.argv[2]), int(sys.argv[3])
rng = random.Random(seed); T0 = time.time()
labels, pairs = load_geometry(); planes = [(labels[a], labels[b]) for a, b in pairs]; NP = len(planes); NPORT = 112
E = [0] * NPORT
for i, (a, b) in enumerate(pairs): E[a] = i; E[b] = i
ORTH = [[i != j and all(dot(x, y) == 0 for x in planes[i] for y in planes[j]) for j in range(NP)] for i in range(NP)]
fixed = {(p, q): int(p == q) for p in range(NPORT) for q in range(NPORT) if p == q or E[p] == E[q] or not ORTH[E[p]][E[q]]}
portmask = [0] * NP
for p in range(NPORT): portmask[E[p]] |= 1 << p
PB = [1 << E[p] for p in range(NPORT)]
def pm(w):
    m = 0
    while w:
        b = w & -w; m |= PB[b.bit_length() - 1]; w ^= b
    return m
_sc, _tc = {}, {}
def spn(m):
    if m not in _sc: _sc[m] = span([v for i in range(NP) if m >> i & 1 for v in planes[i]])
    return _sc[m]
def tariff(U, V):
    if not U or not V: return 0
    k = (pm(U), pm(V))
    if k not in _tc: _tc[k] = pair_rank(spn(k[0]), spn(k[1]))
    return _tc[k]
def verify(terms):
    rows = [0] * NPORT
    for U, V in terms:
        for p in range(NPORT):
            if U >> p & 1: rows[p] ^= V
    return sum(1 for (p, q), t in fixed.items() if (rows[p] >> q & 1) != t), sum(tariff(U, V) for U, V in terms)
d = json.load(open(src))
terms = [(int(u, 16), int(v, 16)) for u, v in d['terms']]
viol, cost = verify(terms); assert viol == 0, 'start decoder must be exact'
U = [u for u, v in terms]; V = [v for u, v in terms]; T = [tariff(u, v) for u, v in terms]
best = cost; best_terms = list(terms); print('seed', seed, 'start cost', cost, 'terms', len(terms), flush=True)
steps = 0; acc = 0; last = T0
while time.time() - T0 < budget:
    frac = (time.time() - T0) / budget; ph = (frac * 20) % 1.0; temp = 0.7 * (0.02 / 0.7) ** ph
    if ph < 0.06 and cost > best:      # new cycle: restart from the best decoder found so far
        U = [u for u, v in best_terms]; V = [v for u, v in best_terms]; T = [tariff(u, v) for u, v in best_terms]; cost = best
    for _ in range(5000):
        steps += 1
        i, j = rng.sample(range(len(U)), 2)
        if rng.random() < 0.5:   # u_i += u_j, v_j += v_i
            nu_i, nv_j = U[i] ^ U[j], V[j] ^ V[i]
            ti, tj = tariff(nu_i, V[i]), tariff(U[j], nv_j)
            dc = ti + tj - T[i] - T[j]
            if dc <= 0 or rng.random() < math.exp(-dc / temp):
                U[i], V[j], T[i], T[j] = nu_i, nv_j, ti, tj; cost += dc; acc += 1
        else:                    # symmetric variant: v_i += v_j, u_j += u_i
            nv_i, nu_j = V[i] ^ V[j], U[j] ^ U[i]
            ti, tj = tariff(U[i], nv_i), tariff(nu_j, V[j])
            dc = ti + tj - T[i] - T[j]
            if dc <= 0 or rng.random() < math.exp(-dc / temp):
                V[i], U[j], T[i], T[j] = nv_i, nu_j, ti, tj; cost += dc; acc += 1
        if cost < best:
            cur = [(u, v) for u, v in zip(U, V) if u and v]
            vv, cc = verify(cur); assert vv == 0 and cc == cost, (vv, cc, cost)
            best, best_terms = cost, cur
            print('%6.0fs NEW BEST %d (terms %d)' % (time.time() - T0, best, len(cur)), flush=True)
            json.dump({'cost': best, 'terms': [[hex(u), hex(v)] for u, v in cur], 'verified': True}, open('gauge_best_%d.json' % seed, 'w'))
    if time.time() - last > 30:
        last = time.time(); print('%6.0fs steps %d acc %.3f temp %.3f cur %d best %d' % (time.time() - T0, steps, acc / steps, temp, cost, best), flush=True)
print('DONE seed', seed, 'best', best, flush=True)
