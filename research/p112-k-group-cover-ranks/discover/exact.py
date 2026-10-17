"""Exact k-group covers (k = 3, 4) built from orthonormal frames; certify supports and clique bounds.

k = 4: 12 disjoint 8-frames give 24 tetrads in 12 orthogonal pairs; the 16 remaining labels are split
       into 4 orthonormal tetrads, chosen to maximise orthogonal pairing.
k = 3: pack disjoint orthonormal 6-sets (two triads each); remaining labels form triads + one singleton.
Each colour class of pairwise orthogonal groups yields max(group size) supports.
"""
import importlib.util, itertools, json, random, sys
from pathlib import Path
ROOT = Path(r"D:\Math\integer-mult-bounds")
spec = importlib.util.spec_from_file_location("pr2484", ROOT / "research/paired-plane-minrank-bracket-audit/verify.py")
V = importlib.util.module_from_spec(spec); spec.loader.exec_module(V)
labels, _, _ = V.load_model((ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz").read_bytes(),
                            (ROOT / "research/paired-plane-scalar-mask-obstruction/PR1825-CERTIFICATE.json").read_bytes())
dot = V.parity_dot
N = 112
O = [[i != j and dot(labels[i], labels[j]) == 0 for j in range(N)] for i in range(N)]
nb = [frozenset(j for j in range(N) if O[i][j]) for i in range(N)]


def cliques(size, pool=None):
    pool = set(range(N)) if pool is None else set(pool)
    out = []
    def grow(cl, cand):
        if len(cl) == size:
            out.append(tuple(cl)); return
        for u in sorted(cand):
            if u > cl[-1]:
                grow(cl + [u], cand & nb[u])
    for v in sorted(pool):
        grow([v], frozenset(u for u in nb[v] if u > v and u in pool))
    return out


def gorth(a, b):
    return all(O[x][y] for x in a for y in b)


def best_colouring(groups, rng, tries=3000):
    n = len(groups)
    adj = [[i != j and not gorth(groups[i], groups[j]) for j in range(n)] for i in range(n)]
    best = None
    for _ in range(tries):
        colour = [-1] * n; sat = [set() for _ in range(n)]; noise = [rng.random() for _ in range(n)]
        for _ in range(n):
            v = max((u for u in range(n) if colour[u] < 0), key=lambda u: (len(sat[u]), len(groups[u]), noise[u]))
            c = 0
            while c in sat[v]: c += 1
            colour[v] = c
            for u in range(n):
                if adj[v][u]: sat[u].add(c)
        cls = {}
        for g, c in zip(groups, colour): cls.setdefault(c, []).append(g)
        s = sum(max(len(g) for g in cl) for cl in cls.values())
        if best is None or s < best[0]: best = (s, colour)
    return best


def packing(size, rng, tries):
    sets = cliques(size)
    masks = [sum(1 << x for x in f) for f in sets]
    best = []
    for _ in range(tries):
        order = list(range(len(sets))); rng.shuffle(order); used = 0; sel = []
        for k in order:
            if not masks[k] & used: used |= masks[k]; sel.append(sets[k])
        if len(sel) > len(best): best = sel
    return best


def k4(rng):
    frames = json.load(open(r"C:\Temp\claude\D--Math\ccf2586c-02da-472d-b45d-4f476e9d7843\scratchpad\rematch\packing-1.json"))
    used = set(x for f in frames for x in f)
    rest = [x for x in range(N) if x not in used]
    best = None
    tets = cliques(4, rest)
    for combo in itertools.combinations(tets, 4):
        if len(set(x for t in combo for x in t)) != 16: continue
        groups = []
        for f in frames:
            groups += [list(f[:4]), list(f[4:])] if gorth(f[:4], f[4:]) else [list(f[:4]), list(f[4:])]
        groups += [list(t) for t in combo]
        s, colour = best_colouring(groups, rng, 200)
        if best is None or s < best[0]: best = (s, groups, colour)
    return best


def k3(rng):
    six = packing(6, rng, 3000)
    used = set(x for f in six for x in f)
    rest = [x for x in range(N) if x not in used]
    groups = []
    for f in six: groups += [list(f[:3]), list(f[3:])]
    best = None
    trip = cliques(3, rest)
    need_t = len(rest) // 3
    for combo in itertools.combinations(trip, need_t):
        cov = set(x for t in combo for x in t)
        if len(cov) != 3 * need_t: continue
        g = groups + [list(t) for t in combo] + [[x] for x in rest if x not in cov]
        s, colour = best_colouring(g, rng, 200)
        if best is None or s < best[0]: best = (s, g, colour)
    return best, len(six)


if __name__ == "__main__":
    rng = random.Random(0)
    k = int(sys.argv[1])
    if k == 4:
        s, groups, colour = k4(rng)
    else:
        (s, groups, colour), npack = k3(rng)
        print("disjoint orthonormal 6-sets", npack)
    print("k", k, "groups", len(groups), "sizes", sorted(set(len(g) for g in groups)), "supports", s, flush=True)
    json.dump({"k": k, "groups": groups, "colour": colour, "supports": s},
              open(Path(__file__).with_name("exact-k%d.json" % k), "w"))
