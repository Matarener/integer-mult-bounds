# V4 structured search: exact minimum cost of a LOCAL plane-port decoder on a small group G of planes.
# Local decoder: M_G (2|G| x 2|G| over F2) = sum_k u_k v_k^T with all supports inside G's ports;
#   M_pp = 1, M_pq = 0 if p != q and planes non-orthogonal or equal, free if orthogonal.
# Cost = sum_k tariff_k, tariff = rank_F2 pairing(span planes(supp u_k), span planes(supp v_k)).
# Why it matters: if some group G has min cost < 4|G|, a GLOBAL decoder cheaper than 224 exists at once
#   (block-diagonal: G's local decoder, the other planes at 4 each, zeros between blocks are always allowed).
# Tariff-0 terms touch only free entries (orthogonal spans), so an optimal decoder uses <= 4|G|-1 nonzero terms.
# Usage: python v4_groups.py <chunk> <nchunks> <workers>
import itertools, json, sys, time, os, multiprocessing as mp
from v4lib import *
labels, pairs = load_geometry(); planes = [(labels[a], labels[b]) for a, b in pairs]; NP = len(planes)
ORTH = [[i != j and all(dot(x, y) == 0 for x in planes[i] for y in planes[j]) for j in range(NP)] for i in range(NP)]
def sp(D): return span([v for i in D for v in planes[i]])
def gr(D): s = sp(D); return pair_rank(s, s)

def solve_group(G, time_limit=30.0):
    from ortools.sat.python import cp_model
    G = list(G); g = len(G); m = 2 * g
    table = [0] * (4 ** g)                       # index = A + 2^g * R  (A, R local plane masks)
    for A in range(1, 2 ** g):
        sA = sp([G[i] for i in range(g) if A >> i & 1])
        for R in range(1, 2 ** g):
            table[A + (R << g)] = pair_rank(sA, sp([G[i] for i in range(g) if R >> i & 1]))
    fixed = {}
    for p in range(m):
        for q in range(m):
            i, j = p // 2, q // 2
            if p == q: fixed[p, q] = 1
            elif i == j or not ORTH[G[i]][G[j]]: fixed[p, q] = 0
    K = 4 * g - 1
    md = cp_model.CpModel(); one = md.NewBoolVar('one'); md.Add(one == 1)
    u = [[md.NewBoolVar('') for _ in range(m)] for _ in range(K)]
    v = [[md.NewBoolVar('') for _ in range(m)] for _ in range(K)]
    prods = {key: [] for key in fixed}
    for k in range(K):
        for (p, q) in fixed:
            z = md.NewBoolVar('')
            md.AddBoolAnd([u[k][p], v[k][q]]).OnlyEnforceIf(z)
            md.AddBoolOr([u[k][p].Not(), v[k][q].Not()]).OnlyEnforceIf(z.Not())
            prods[p, q].append(z)
    for key, t in fixed.items():
        md.AddBoolXOr(prods[key] + ([] if t else [one]))
    cost = []; idx = []
    for k in range(K):
        a = []; b = []
        for i in range(g):
            x = md.NewBoolVar(''); md.AddMaxEquality(x, [u[k][2 * i], u[k][2 * i + 1]]); a.append(x)
            y = md.NewBoolVar(''); md.AddMaxEquality(y, [v[k][2 * i], v[k][2 * i + 1]]); b.append(y)
        ix = md.NewIntVar(0, 4 ** g - 1, '')
        md.Add(ix == sum((1 << i) * a[i] for i in range(g)) + sum((1 << (g + i)) * b[i] for i in range(g)))
        c = md.NewIntVar(0, 9, ''); md.AddElement(ix, table, c); cost.append(c); idx.append(ix)
    for k in range(K - 1): md.Add(idx[k] >= idx[k + 1])          # symmetry breaking
    md.Add(sum(cost) <= 4 * g)
    md.Minimize(sum(cost))
    s = cp_model.CpSolver(); s.parameters.max_time_in_seconds = time_limit; s.parameters.num_workers = 1
    st = s.Solve(md)
    res = {'G': G, 'status': s.StatusName(st), 'best': None, 'bound': int(s.BestObjectiveBound()) if st != cp_model.MODEL_INVALID else None}
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        terms = []
        for k in range(K):
            U = [s.Value(u[k][p]) for p in range(m)]; V = [s.Value(v[k][q]) for q in range(m)]
            if any(U) and any(V): terms.append((U, V))
        # independent re-verification
        Mx = [[0] * m for _ in range(m)]
        for U, V in terms:
            for p in range(m):
                if U[p]:
                    for q in range(m): Mx[p][q] ^= V[q]
        ok = all(Mx[p][q] == t for (p, q), t in fixed.items())
        cc = 0
        for U, V in terms:
            A = sum(1 << i for i in range(g) if U[2 * i] or U[2 * i + 1]); R = sum(1 << i for i in range(g) if V[2 * i] or V[2 * i + 1])
            cc += table[A + (R << g)]
        res.update(best=cc, verified=ok, terms=[[''.join(map(str, U)), ''.join(map(str, V))] for U, V in terms])
        assert ok, ('verification failed', G)
    return res

def groups():
    gs = [(i,) for i in range(NP)]
    gs += list(itertools.combinations(range(NP), 2))
    gs += list(itertools.combinations(range(NP), 3))
    deg = [(i, j) for i, j in itertools.combinations(range(NP), 2) if gr([i, j]) < 4]
    adj = {i: set() for i in range(NP)}
    for i, j in deg: adj[i].add(j); adj[j].add(i)
    quads = set()
    for i, j in deg:
        for k in adj[i] | adj[j]:
            for l in adj[i] | adj[j] | adj[k]:
                q = tuple(sorted({i, j, k, l}))
                if len(q) == 4: quads.add(q)
    quads = sorted(quads, key=lambda q: (gr(q), q))[:5000]     # most degenerate quads first
    return gs + quads

if __name__ == '__main__':
    chunk, nch, W = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    T0 = time.time()
    # self-test: a single plane must cost exactly 4 (the known per-plane floor)
    t = solve_group((0,), 60)
    print('self-test single plane:', t['status'], t['best'], flush=True); assert t['best'] == 4 and t['status'] == 'OPTIMAL'
    allg = groups(); mine = allg[chunk::nch]
    print('groups total', len(allg), 'this chunk', len(mine), flush=True)
    out = open(f'groups_{chunk}.jsonl', 'w'); n = 0; cheap = 0; unk = 0
    with mp.get_context('spawn').Pool(W) as pool:   # spawn: no fork after the solver started threads
        for r in pool.imap_unordered(solve_group, mine, chunksize=4):
            n += 1; g = len(r['G'])
            if r['best'] is not None and r['best'] < 4 * g: cheap += 1; print('CHEAPER GROUP FOUND', r, flush=True)
            if r['best'] is not None and r['best'] >= 4 * g and (r['bound'] is None or r['bound'] < 4 * g): unk += 1   # saving not excluded
            out.write(json.dumps(r) + '\n'); out.flush()
            if n % 200 == 0 or n == len(mine):
                print('%6.0fs %d / %d groups, cheaper than 4/plane: %d, saving not excluded (timeout): %d' % (time.time() - T0, n, len(mine), cheap, unk), flush=True)
    print('DONE chunk', chunk, 'groups', n, 'of', len(mine), 'cheaper', cheap, 'saving not excluded', unk, flush=True)
