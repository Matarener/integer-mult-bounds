"""Symmetry-reduced Lovász theta upper bound for alpha(H) = max lost-free |S|.

theta(H) = min lambda_max(A) over symmetric A with A_ii = 1, A_ij = 1 for non-adjacent i != j, A_ij free on
edges (Lovász). Restricting A to be constant on orbitals of the symmetry group keeps a valid upper bound
(and is exact for invariant optima). We minimise lambda_max over the edge-orbital coefficients by a simple
subgradient / step method. Prints the bound as it improves (progress.log style) to theta.log.
"""
import json, sys, time
from pathlib import Path
import numpy as np
import scipy.sparse as sp
from scipy.sparse.csgraph import connected_components
from scipy.sparse.linalg import eigsh, LinearOperator
import sdp_prep as P

HERE = Path(__file__).resolve().parent
LOG = open(HERE / "theta.log", "a", encoding="utf-8")
T0 = time.time()


def say(s):
    line = "[%s, %5.1f мин] %s" % (time.strftime("%H:%M:%S"), (time.time() - T0) / 60, s)
    print(line, flush=True); LOG.write(line + "\n"); LOG.flush()


n = P.nV
perms = json.load(open(HERE / "symmetry.json"))["perms"]
gens = [P.vertex_perm(p, P.linear_from_perm(p)) for p in perms]
ginv = [np.argsort(g).astype(np.int32) for g in gens]
say("генераторов группы: %d, вершин: %d" % (len(gens), n))


def orbits(gs):
    rows = np.concatenate([np.arange(n)] * len(gs)); cols = np.concatenate(gs)
    M = sp.coo_matrix((np.ones(len(rows), dtype=np.int8), (rows, cols)), shape=(n, n))
    return connected_components(M, directed=True, connection="weak")[1]


vorb = orbits(gens)
reps = sorted({int(vorb[i]) for i in range(n)})
rep_vertex = {o: int(np.where(vorb == o)[0][0]) for o in reps}

# BFS from each orbit representative with transversal stored as (parent, generator)
parent = np.full(n, -1, dtype=np.int64); via = np.full(n, -1, dtype=np.int64)
order = []
for o in reps:
    r = rep_vertex[o]; parent[r] = r; frontier = [r]; order.append(r)
    while frontier:
        nxt = []
        for x in frontier:
            for k, g in enumerate(gens):
                y = int(g[x])
                if parent[y] == -1:
                    parent[y] = x; via[y] = k; nxt.append(y); order.append(y)
        frontier = nxt


def transversal(x):
    """permutation t with t(rep) = x, as an array."""
    path = []
    while parent[x] != x:
        path.append(via[x]); x = int(parent[x])
    t = np.arange(n, dtype=np.int32)
    for k in reversed(path):
        t = gens[k][t]
    return t


# stabiliser orbits of each representative via random Schreier generators
rng = np.random.default_rng(0)
stab_label = {}
label_count = 0
for o in reps:
    r = rep_vertex[o]
    orbit_pts = np.where(vorb == o)[0]
    sch = []
    for _ in range(150):
        x = int(rng.choice(orbit_pts)); k = int(rng.integers(len(gens)))
        tx = transversal(x); y = int(gens[k][x]); ty = transversal(y)
        s = np.argsort(ty)[gens[k][tx]]          # ty^-1 g tx fixes r
        assert s[r] == r
        sch.append(s.astype(np.int32))
    lab = orbits(sch)
    _, lab = np.unique(lab, return_inverse=True)
    stab_label[o] = lab + label_count
    label_count += int(lab.max()) + 1
say("типов пар вершин (орбиталов, с запасом): %d" % label_count)

# orbital label matrix: row x = stab_label[orbit](t_x^{-1}(j)), built along the BFS tree
Lmat = np.zeros((n, n), dtype=np.int32)
for x in order:
    o = int(vorb[x])
    if parent[x] == x:
        Lmat[x] = stab_label[o]
    else:
        k = via[x]; p = int(parent[x])
        Lmat[x] = Lmat[p][ginv[k]]
# classify labels: diagonal / edge / non-edge (check consistency on samples)
K = label_count
kind = np.full(K, -1)
diag = np.unique(Lmat[np.arange(n), np.arange(n)])
kind[diag] = 0
verts = P.verts
for o in reps:
    r = rep_vertex[o]
    labs = stab_label[o]
    for j in range(n):
        lab = int(labs[j])
        if kind[lab] != -1:
            continue
        kind[lab] = 0 if j == r else (1 if P.conflict(verts[r], verts[j]) else 2)
# consistency spot-check of the label matrix against the conflict relation
for _ in range(4000):
    i, j = int(rng.integers(n)), int(rng.integers(n))
    lab = Lmat[i, j]
    assert (kind[lab] == 1) == bool(P.conflict(verts[i], verts[j])) or i == j
edge_labels = np.where(kind == 1)[0]
say("орбиталы: диагональ %d, рёбра %d, не-рёбра %d" % ((kind == 0).sum(), len(edge_labels), (kind == 2).sum()))

# start from the exact clique-partition point: same-port pairs get 1-112, every other entry 1 (lambda_max = 112)
c = np.ones(K, dtype=np.float64)
for o in reps:
    r = rep_vertex[o]; a = verts[r][0]
    for j in range(n):
        if verts[j][0] == a and j != r:
            c[int(stab_label[o][j])] = 1.0 - P.N


def lam_max(cvec):
    A = cvec.astype(np.float32)[Lmat]
    w, v = eigsh(LinearOperator((n, n), matvec=lambda z: A @ z.astype(np.float32), dtype=np.float32), k=1, which="LA", tol=1e-6)
    return float(w[0]), v[:, 0], A


best = None
step = 0.5
lam, v, A = lam_max(c)
say("старт: λ_max = %.3f (это граница |S| <= %.2f)" % (lam, lam))
best = (lam, c.copy())
for it in range(int(sys.argv[1]) if len(sys.argv) > 1 else 300):
    # subgradient of lambda_max w.r.t. edge coefficients: sum of v_i v_j over each orbital
    vv = v.astype(np.float64)
    grad = np.zeros(K)
    for s in range(0, n, 1024):
        blk = np.outer(vv[s:s + 1024], vv)
        grad += np.bincount(Lmat[s:s + 1024].ravel(), weights=blk.ravel(), minlength=K)
    g = np.zeros(K); g[edge_labels] = grad[edge_labels]
    nrm = np.linalg.norm(g)
    if nrm == 0: break
    trial = c - step * g / nrm
    lam_t, v_t, _ = lam_max(trial)
    if lam_t < lam:
        c, lam, v = trial, lam_t, v_t
        step *= 1.2
        if lam < best[0] - 1e-3:
            best = (lam, c.copy())
            say("θ <= %.3f (итерация %d)" % (lam, it))
    else:
        step *= 0.5
    if step < 1e-6: break
say("ИТОГ: численная граница θ <= %.3f" % best[0])
np.save(HERE / "theta_c.npy", best[1]); np.save(HERE / "theta_kind.npy", kind)
