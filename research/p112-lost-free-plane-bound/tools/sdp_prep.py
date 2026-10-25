"""Structure of the conflict graph H on (port, plane) pairs and its symmetry reduction.

Vertices: (a, r), r.q_a = 0, r.r = 1 (128 per port, 14,336 total). Lost-free S with planes = independent
set in H, where (a,r)-(a,r') conflict for r != r', and (a,r)-(b,s) conflict when q_a.q_b = 0 and the planes
<q_a,r>, <q_b,s> are not orthogonal. alpha(H) = max lost-free |S|.
Group: isometries from symmetry.json act by (a, r) -> (p(a), M r).
"""
import importlib.util, json, random, sys, time
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
ROOT = Path(r"D:\Math\integer-mult-bounds")
spec = importlib.util.spec_from_file_location("v", ROOT / "research/paired-plane-minrank-bracket-audit/verify.py")
V = importlib.util.module_from_spec(spec); spec.loader.exec_module(V)
q, _, _ = V.load_model((ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz").read_bytes(),
                       (ROOT / "research/paired-plane-scalar-mask-obstruction/PR1825-CERTIFICATE.json").read_bytes())
dot = V.parity_dot
N = 112
R = [[r for r in range(1, 512) if dot(r, q[a]) == 0 and dot(r, r) == 1] for a in range(N)]
verts = [(a, r) for a in range(N) for r in R[a]]
index = {v: i for i, v in enumerate(verts)}
nV = len(verts)


def conflict(u, v):
    (a, r), (b, s) = u, v
    if a == b:
        return r != s
    if dot(q[a], q[b]):
        return False
    return dot(q[a], s) or dot(r, q[b]) or dot(r, s)


def linear_from_perm(p):
    import symmetry as S
    imgs = [q[p[q.index(b)]] for b in S.B]
    table = [S.image(imgs, S.coord[v]) for v in range(512)]
    return table


def vertex_perm(p, table):
    return np.array([index[(p[a], table[r])] for (a, r) in verts], dtype=np.int32)


def uf_orbits(n, gens):
    parent = np.arange(n)
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for g in gens:
        for i in range(n):
            a, b = find(i), find(int(g[i]))
            if a != b: parent[a] = b
    return np.array([find(i) for i in range(n)])


if __name__ == "__main__":
    t0 = time.time()
    deg = [sum(conflict(verts[0], v) for v in verts)]
    print("vertices", nV, flush=True)
    perms = json.load(open(HERE / "symmetry.json"))["perms"]
    gens = []
    for p in perms:
        table = linear_from_perm(p)
        g = vertex_perm(p, table)
        assert len(set(g.tolist())) == nV
        gens.append(g)
    # sanity: generators preserve conflicts on a random sample of pairs
    rng = random.Random(0)
    for _ in range(3000):
        i, j = rng.randrange(nV), rng.randrange(nV)
        g = gens[rng.randrange(len(gens))]
        assert conflict(verts[i], verts[j]) == conflict(verts[g[i]], verts[g[j]])
    orb = uf_orbits(nV, gens)
    reps = sorted(set(orb.tolist()))
    sizes = {int(r): int((orb == r).sum()) for r in reps}
    print("vertex orbits:", len(reps), "sizes:", sorted(sizes.values()), "%.0fs" % (time.time() - t0), flush=True)
    # degrees per orbit representative
    for rpt in reps:
        u = verts[int(np.where(orb == rpt)[0][0])]
        d = sum(conflict(u, v) for v in verts)
        print("orbit size %d: conflict degree %d" % (sizes[rpt], d), flush=True)
    json.dump({"orbit": orb.tolist()}, open(HERE / "vertex_orbits.json", "w"))
