"""Search other perfect matchings of the 112 P112 ports for a smaller plane-graph colouring / clique.

Model (PR2471/PR2484): ports i,j can be matched iff q_i.q_i = q_j.q_j = 1 and q_i.q_j = 0.
Planes are adjacent in G iff not orthogonal (some basis pairing is 1).  A proper colouring of G
by c classes gives a scalar fit of rank 2c; a clique of size w forces rank >= 2w.
"""
import json, random, sys, time
from pathlib import Path
ROOT = Path(r"D:\Math\integer-mult-bounds")
sys.path.insert(0, str(ROOT / "research/paired-plane-minrank-bracket-audit"))
import verify as V

archive = (ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz").read_bytes()
matching = (ROOT / "research/paired-plane-scalar-mask-obstruction/PR1825-CERTIFICATE.json").read_bytes()
labels, pairs0, orth0 = V.load_model(archive, matching)
dot = V.parity_dot
N = 112
ok = [[i != j and dot(labels[i], labels[i]) == 1 and dot(labels[j], labels[j]) == 1 and dot(labels[i], labels[j]) == 0
       for j in range(N)] for i in range(N)]


def graph(pairs):
    basis = [(labels[a], labels[b]) for a, b in pairs]
    n = len(pairs)
    return [[i != j and any(dot(x, y) for x in basis[i] for y in basis[j]) for j in range(n)] for i in range(n)]


def dsatur(adj, rng=None, tries=1):
    n = len(adj)
    best = n
    for t in range(tries):
        colour = [-1] * n
        sat = [set() for _ in range(n)]
        deg = [sum(r) for r in adj]
        noise = [rng.random() if rng else 0 for _ in range(n)]
        for _ in range(n):
            v = max((u for u in range(n) if colour[u] < 0), key=lambda u: (len(sat[u]), deg[u], noise[u]))
            c = 0
            while c in sat[v]:
                c += 1
            colour[v] = c
            for u in range(n):
                if adj[v][u]:
                    sat[u].add(c)
        best = min(best, max(colour) + 1)
    return best


def clique_greedy(adj, rng, tries=30):
    n = len(adj)
    best = 0
    for _ in range(tries):
        order = list(range(n))
        rng.shuffle(order)
        order.sort(key=lambda u: -sum(adj[u]) + rng.random() * 6)
        cl = []
        for v in order:
            if all(adj[v][u] for u in cl):
                cl.append(v)
        best = max(best, len(cl))
    return best


def score(pairs, rng):
    adj = graph(pairs)
    return dsatur(adj, rng, 4), adj


def main(seed, seconds):
    rng = random.Random(seed)
    pairs = [tuple(p) for p in pairs0]
    adj = graph(pairs)
    assert [[bool(x) for x in r] for r in adj] == [[(i != j) and not orth0[i][j] for j in range(56)] for i in range(56)]
    cur, _ = score(pairs, rng)
    best, best_pairs = cur, list(pairs)
    print('start colouring classes', cur, 'clique>=', clique_greedy(adj, rng), flush=True)
    t0, temp, it = time.time(), 1.0, 0
    while time.time() - t0 < seconds:
        it += 1
        i, j = rng.sample(range(56), 2)
        (a, b), (c, d) = pairs[i], pairs[j]
        opts = [((a, c), (b, d)), ((a, d), (b, c))]
        rng.shuffle(opts)
        for p, q in opts:
            if ok[p[0]][p[1]] and ok[q[0]][q[1]]:
                new = list(pairs)
                new[i], new[j] = p, q
                s, _ = score(new, rng)
                if s <= cur or rng.random() < pow(2.718, (cur - s) / temp):
                    pairs, cur = new, s
                    if s < best:
                        best, best_pairs = s, list(new)
                        print('t=%.0fs it=%d new best classes=%d' % (time.time() - t0, it, s), flush=True)
                break
        temp = max(0.05, temp * 0.9995)
    adj = graph(best_pairs)
    print('final best classes', best, 'clique>=', clique_greedy(adj, rng, 200), 'iterations', it, flush=True)
    json.dump({'seed': seed, 'classes': best, 'pairs': best_pairs},
              open(Path(__file__).with_name('best-%d.json' % seed), 'w'))


if __name__ == '__main__':
    main(int(sys.argv[1]), float(sys.argv[2]))
