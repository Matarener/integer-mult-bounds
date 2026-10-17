"""Search covers of the 112 P112 labels by orthonormal k-groups minimising the group-graph colouring.

Mask (kport-group-scalar-endpoint-audit / Discussion 1587): K_ii = 1, K_ij = 0 unless the groups of
i and j are distinct and orthogonal.  A colouring by c classes gives supports = sum over classes of the
largest group size in the class (one support per position); a clique of groups forces I_(sum sizes).
Usage: search.py k seed seconds
"""
import json, random, sys, time
from pathlib import Path
ROOT = Path(r"D:\Math\integer-mult-bounds")
import importlib.util
spec = importlib.util.spec_from_file_location("pr2484", ROOT / "research/paired-plane-minrank-bracket-audit/verify.py")
V = importlib.util.module_from_spec(spec); spec.loader.exec_module(V)
archive = (ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz").read_bytes()
matching = (ROOT / "research/paired-plane-scalar-mask-obstruction/PR1825-CERTIFICATE.json").read_bytes()
labels, _, _ = V.load_model(archive, matching)
dot = V.parity_dot
N = 112
O = [[i != j and dot(labels[i], labels[j]) == 0 for j in range(N)] for i in range(N)]


def initial(k, rng):
    """Random greedy partition into orthonormal k-groups; leftovers become smaller groups."""
    for _ in range(10000):
        rest = list(range(N)); rng.shuffle(rest); groups = []
        while rest:
            g = [rest.pop()]
            for x in list(rest):
                if len(g) == k: break
                if all(O[x][y] for y in g):
                    g.append(x); rest.remove(x)
            groups.append(g)
        sizes = sorted(len(g) for g in groups)
        if sizes.count(k) >= N // k - 1:
            return groups
    raise SystemExit("no initial cover")


def group_orth(a, b):
    return all(O[x][y] for x in a for y in b)


def supports_of(groups, colour):
    classes = {}
    for g, c in zip(groups, colour):
        classes.setdefault(c, []).append(g)
    return sum(max(len(g) for g in cl) for cl in classes.values())


def colour_cost(groups, rng, tries=3):
    n = len(groups)
    adj = [[i != j and not group_orth(groups[i], groups[j]) for j in range(n)] for i in range(n)]
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
        s = supports_of(groups, colour)
        if best is None or s < best[0]: best = (s, colour)
    return best


def main(k, seed, seconds):
    rng = random.Random(seed)
    groups = initial(k, rng)
    cur = colour_cost(groups, rng)[0]
    best, bestg = cur, [list(g) for g in groups]
    print("k", k, "groups", len(groups), "sizes", sorted(len(g) for g in groups)[:3], "start supports", cur, flush=True)
    t0 = time.time(); temp = 2.0; it = 0
    while time.time() - t0 < seconds:
        it += 1
        a, b = rng.sample(range(len(groups)), 2)
        x, y = rng.choice(groups[a]), rng.choice(groups[b])
        ga = [z for z in groups[a] if z != x] + [y]
        gb = [z for z in groups[b] if z != y] + [x]
        if not (all(O[y][z] for z in ga if z != y) and all(O[x][z] for z in gb if z != x)):
            continue
        new = list(groups); new[a], new[b] = ga, gb
        s = colour_cost(new, rng)[0]
        if s <= cur or rng.random() < pow(2.718, (cur - s) / temp):
            groups, cur = new, s
            if s < best:
                best, bestg = s, [list(g) for g in new]
                print("t=%.0f it=%d supports=%d" % (time.time() - t0, it, s), flush=True)
        temp = max(0.1, temp * 0.9995)
    print("final best supports", best, "iterations", it, flush=True)
    json.dump({"k": k, "supports": best, "groups": bestg}, open(Path(__file__).with_name("best-k%d-s%d.json" % (k, seed)), "w"))


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3]))
