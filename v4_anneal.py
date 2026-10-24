# V4 step 3: simulated annealing over EXACT plane-port decoders M = sum_k u_k v_k^T (over F2, 112 ports).
# Constraint (mask): M_pp = 1; M_pq = 0 if p != q and planes E(p), E(q) are non-orthogonal or equal; else free.
# Cost: sum_k tariff_k, tariff_k = rank_F2 of the pairing between span(planes of supp u_k) and span(planes of supp v_k).
# Objective during search: cost + lam * (#violated fixed entries); only states with 0 violations count as decoders.
# Every reported decoder is re-verified from scratch (mask + tariffs) before it is written.
# Usage: python v4_anneal.py <seed> <seconds> <start: id|color|mix>
import json, os, random, sys, time, math
from v4lib import *
seed, budget, start = int(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
rng = random.Random(seed); T0 = time.time()
labels, pairs = load_geometry(); planes = [(labels[a], labels[b]) for a, b in pairs]; NP = len(planes); NPORT = 112
E = [0] * NPORT
for i, (a, b) in enumerate(pairs): E[a] = i; E[b] = i
ORTH = [[i != j and all(dot(x, y) == 0 for x in planes[i] for y in planes[j]) for j in range(NP)] for i in range(NP)]
target = [1 << p for p in range(NPORT)]
fixed = [sum(1 << q for q in range(NPORT) if not ORTH[E[p]][E[q]]) for p in range(NPORT)]   # same plane / non-orth / diag
portmask = [0] * NP
for p in range(NPORT): portmask[E[p]] |= 1 << p
pc = int.bit_count
_tc = {}
def pmask(u):
    m = 0
    for i in range(NP):
        if u & portmask[i]: m |= 1 << i
    return m
def span_of(m):
    vs = []
    for i in range(NP):
        if m >> i & 1: vs += planes[i]
    return span(vs)
_sc = {}
def tariff(ma, mr):
    key = (ma, mr)
    t = _tc.get(key)
    if t is None:
        sa = _sc.get(ma) or _sc.setdefault(ma, span_of(ma)); sr = _sc.get(mr) or _sc.setdefault(mr, span_of(mr))
        t = pair_rank(sa, sr) if ma and mr else 0
        if len(_tc) > 2_000_000: _tc.clear()
        _tc[key] = t
    return t

def verify(terms):
    rows = [0] * NPORT
    for u, v in terms:
        for p in range(NPORT):
            if u >> p & 1: rows[p] ^= v
    viol = sum(pc((rows[p] ^ target[p]) & fixed[p]) for p in range(NPORT))
    cost = sum(tariff(pmask(u), pmask(v)) for u, v in terms if u and v)
    return viol, cost

# ---------- start states ----------
def start_identity(): return [(1 << p, 1 << p) for p in range(NPORT)]
def start_color():
    # greedy partition of planes into mutually orthogonal classes; 2 terms per class (one per port slot)
    order = list(range(NP)); rng.shuffle(order); cls = []
    for i in order:
        for c in cls:
            if all(ORTH[i][j] for j in c): c.append(i); break
        else: cls.append([i])
    terms = []
    for c in cls:
        for slot in (0, 1):
            u = 0
            for i in c: u |= 1 << pairs[i][slot]
            terms.append((u, u))
    return terms
terms = {'id': start_identity, 'color': start_color}.get(start, lambda: start_identity() if rng.random() < .5 else start_color())()
v0, c0 = verify(terms); assert v0 == 0, 'start state must be a valid decoder'
print('seed', seed, 'start', start, 'terms', len(terms), 'cost', c0, flush=True)

# ---------- state ----------
U = [u for u, v in terms]; V = [v for u, v in terms]
rows = [0] * NPORT
for u, v in terms:
    for p in range(NPORT):
        if u >> p & 1: rows[p] ^= v
UA = [pmask(u) for u in U]; VA = [pmask(v) for v in V]; TT = [tariff(a, b) if a and b else 0 for a, b in zip(UA, VA)]
viol = sum(pc((rows[p] ^ target[p]) & fixed[p]) for p in range(NPORT)); cost = sum(TT)
best = (cost, [(u, v) for u, v in zip(U, V)]) if viol == 0 else (10**9, None)
OUT = f'anneal_{seed}.json'
def save_best():
    vv, cc = verify(best[1]); assert vv == 0 and cc == best[0], (vv, cc, best[0])
    json.dump({'seed': seed, 'start': start, 'cost': cc, 'terms': len(best[1]),
               'decoder': [[hex(u), hex(v)] for u, v in best[1]], 'verified': True, 'elapsed': round(time.time() - T0)},
              open(OUT, 'w'))
save_best()

def row_delta(p, x):   # violation change if rows[p] ^= x
    f = fixed[p]; r = rows[p]; t = target[p]
    return pc(((r ^ x) ^ t) & f) - pc((r ^ t) & f)

lam = 4.0; Tmax, Tmin = 1.5, 0.05; MAXTERMS = 160
steps = 0; last_print = T0; accepted = 0
while time.time() - T0 < budget:
    frac = (time.time() - T0) / budget
    # cyclic schedule: 20 cycles of cooling
    ph = (frac * 20) % 1.0
    temp = Tmax * (Tmin / Tmax) ** ph
    for _ in range(2000):
        steps += 1
        k = rng.randrange(len(U)) if U else None
        mv = rng.random()
        if mv < 0.40 and U:            # flip one bit of u_k  -> row p ^= v_k
            p = rng.randrange(NPORT); nu = U[k] ^ (1 << p)
            dv = row_delta(p, V[k]); na = pmask(nu); nt = tariff(na, VA[k]) if nu and V[k] else 0
            dc = nt - TT[k]
            if dc + lam * dv <= 0 or rng.random() < math.exp(-(dc + lam * dv) / temp):
                rows[p] ^= V[k]; U[k] = nu; UA[k] = na; TT[k] = nt; viol += dv; cost += dc; accepted += 1
        elif mv < 0.80 and U:          # flip one bit of v_k  -> rows p in u_k ^= e_q
            q = rng.randrange(NPORT); nv = V[k] ^ (1 << q); x = 1 << q
            u = U[k]; dv = 0; p = 0
            while u:
                if u & 1: dv += row_delta(p, x)
                u >>= 1; p += 1
            nb = pmask(nv); nt = tariff(UA[k], nb) if U[k] and nv else 0; dc = nt - TT[k]
            if dc + lam * dv <= 0 or rng.random() < math.exp(-(dc + lam * dv) / temp):
                u = U[k]; p = 0
                while u:
                    if u & 1: rows[p] ^= x
                    u >>= 1; p += 1
                V[k] = nv; VA[k] = nb; TT[k] = nt; viol += dv; cost += dc; accepted += 1
        elif mv < 0.90 and U:          # delete term k
            u, v = U[k], V[k]; dv = 0; p = 0; uu = u
            while uu:
                if uu & 1: dv += row_delta(p, v)
                uu >>= 1; p += 1
            dc = -TT[k]
            if dc + lam * dv <= 0 or rng.random() < math.exp(-(dc + lam * dv) / temp):
                uu = u; p = 0
                while uu:
                    if uu & 1: rows[p] ^= v
                    uu >>= 1; p += 1
                for L in (U, V, UA, VA, TT): L[k] = L[-1]; L.pop()
                viol += dv; cost += dc; accepted += 1
        elif len(U) < MAXTERMS:        # add a term fixing a violated entry (or a random one)
            bad = [p for p in range(NPORT) if (rows[p] ^ target[p]) & fixed[p]]
            if bad:
                p = rng.choice(bad); w = (rows[p] ^ target[p]) & fixed[p]
                qs = [q for q in range(NPORT) if w >> q & 1]; q = rng.choice(qs)
            else:
                p, q = rng.randrange(NPORT), rng.randrange(NPORT)
            u, v = 1 << p, 1 << q
            dv = row_delta(p, v); ua, va = pmask(u), pmask(v); nt = tariff(ua, va); dc = nt
            if dc + lam * dv <= 0 or rng.random() < math.exp(-(dc + lam * dv) / temp):
                rows[p] ^= v; U.append(u); V.append(v); UA.append(ua); VA.append(va); TT.append(nt)
                viol += dv; cost += dc; accepted += 1
        if viol == 0 and cost < best[0]:
            best = (cost, [(u, v) for u, v in zip(U, V) if u and v]); save_best()
            print('%6.0fs NEW BEST cost %d terms %d' % (time.time() - T0, cost, len(best[1])), flush=True)
    # adapt penalty: keep the walk near feasibility
    lam = min(60.0, lam * 1.02) if viol > 20 else max(3.0, lam * 0.995)
    if time.time() - last_print > 60:
        last_print = time.time()
        print('%6.0fs steps %d acc %.3f temp %.3f lam %.2f | cur cost %d viol %d terms %d | best %d' %
              (time.time() - T0, steps, accepted / steps, temp, lam, cost, viol, len(U), best[0]), flush=True)
        json.dump({'seed': seed, 'elapsed': round(time.time() - T0), 'steps': steps, 'best': best[0], 'cur_cost': cost,
                   'cur_viol': viol}, open(f'anneal_{seed}.progress.json', 'w'))
print('DONE seed', seed, 'best verified decoder cost', best[0], flush=True)
