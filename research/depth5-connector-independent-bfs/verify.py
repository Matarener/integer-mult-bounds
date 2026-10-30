#!/usr/bin/env python3
"""Independent check of #4281's depth-five chain connector minima and witnesses.

Call l is z_l += B_l z_{l-1}. A positive word is correct for residue c exactly when its product
of I + E[l][l-1] in the unitriangular group mod m is I + c E[D][0] (#4281's Lemma 1, here in
lower-triangular form). This file: a standard-library BFS for the small cases, a check of every
vendored witness by that product and by a literal replay with random noncommuting 2x2 maps, and
a check of the recorded C runs (bfs.c) for the large ones. No code from #4281.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
import hashlib
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
WITNESS_SHA256 = "ea320e9f069de8864952ad4b5e492875c1102bd1d12074f606b8aad2b54fe254"
EXPECTED_BFS = {(4, 2): {1: 12}, (4, 3): {1: 18, 2: 18}, (4, 4): {1: 20, 2: 20, 3: 20},
                (5, 2): {1: 16}}
EXPECTED_C = {(4, 5): {1: 25, 2: 25, 3: 25, 4: 25}, (5, 3): {1: 24, 2: 24}, (5, 4): {1: 28, 2: 24, 3: 28}}


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def product(word, m, depth):
    """strictly lower entries of prod (I + E[l][l-1]) applied in word order, mod m"""
    x = [[int(i == j) for j in range(depth + 1)] for i in range(depth + 1)]
    for ch in word:
        l = int(ch)
        x[l] = [(a + b) % m for a, b in zip(x[l], x[l - 1])]
    return x


def correct(word, m, c, depth=5):
    x = product(word, m, depth)
    return all(x[i][j] == (c % m if (i, j) == (depth, 0) else 0) for i in range(depth + 1) for j in range(i))


def literal(word, m, c, rng):
    """replay with dirty registers in (Z/m)^2 and random 2x2 maps; z_1..z_4 restored, y += c B5..B1 x"""
    def mul(a, b):
        return [[sum(a[i][k] * b[k][j] for k in range(2)) % m for j in range(2)] for i in range(2)]

    def app(a, v):
        return [sum(a[i][k] * v[k] for k in range(2)) % m for i in range(2)]
    B = {l: [[rng.randrange(m) for _ in range(2)] for _ in range(2)] for l in range(1, 6)}
    z0 = [[rng.randrange(m) for _ in range(2)] for _ in range(6)]
    z = [v[:] for v in z0]
    for ch in word:
        l = int(ch)
        z[l] = [(a + b) % m for a, b in zip(z[l], app(B[l], z[l - 1]))]
    chain = mul(B[5], mul(B[4], mul(B[3], mul(B[2], B[1]))))
    gain = app(chain, z0[0])
    return z[:5] == z0[:5] and z[5] == [(a + c * b) % m for a, b in zip(z0[5], gain)]


def bfs(m, depth):
    """exact distances from the identity to every I + c E[depth][0]"""
    rows = [(i, j) for i in range(1, depth + 1) for j in range(i)]
    pos = {cell: k for k, cell in enumerate(rows)}

    def step(s, l):
        d = [(s // m ** k) % m for k in range(len(rows))]
        for j in range(l - 1):
            d[pos[l, j]] = (d[pos[l, j]] + d[pos[l - 1, j]]) % m
        d[pos[l, l - 1]] = (d[pos[l, l - 1]] + 1) % m
        return sum(v * m ** k for k, v in enumerate(d))
    targets = {c * m ** pos[depth, 0]: c for c in range(1, m)}
    seen, frontier, dist, found = {0}, [0], 0, {}
    while frontier and len(found) < m - 1:
        dist += 1
        nxt = []
        for s in frontier:
            for l in range(1, depth + 1):
                r = step(s, l)
                if r not in seen:
                    seen.add(r)
                    nxt.append(r)
                    if r in targets:
                        found[targets[r]] = dist
        frontier = nxt
    return found


def main():
    raw = (HERE / "vendor/witnesses.json").read_bytes()
    need(hashlib.sha256(raw).hexdigest() == WITNESS_SHA256, "vendored witnesses.json")
    data = json.loads(raw)
    rng = random.Random(4281)

    # exact minima, standard library
    for (depth, m), want in EXPECTED_BFS.items():
        need(bfs(m, depth) == want, f"BFS depth {depth} m {m}")

    # every 5m witness: length, call multiplicities, product, literal replay
    count = 0
    for m_s, row in data["witnesses"].items():
        m = int(m_s)
        for c_s, word in row.items():
            c = int(c_s)
            need(len(word) == 5 * m and all(word.count(str(l)) == m for l in range(1, 6)), f"({m},{c}) shape")
            need(correct(word, m, c), f"({m},{c}) product")
            need(all(literal(word, m, c, rng) for _ in range(3)), f"({m},{c}) literal replay")
            count += 1
    need(count == 173, "173 witnesses")
    need(all(sorted(map(int, data["witnesses"][str(m)])) == list(range(1, m)) for m in range(9, 21)), "full rows 9..20")

    # the three m = 4 words read back from #4281's BFS
    m4 = {int(c): w for c, w in data["m4_minimal_words"].items()}
    need({c: len(w) for c, w in m4.items()} == {1: 28, 2: 24, 3: 28}, "m=4 word lengths")
    need(all(correct(w, 4, c) and literal(w, 4, c, rng) for c, w in m4.items()), "m=4 words correct")

    # recorded runs of bfs.c (built and run as in the README); local evidence, not replayed here
    runs, text = {}, (HERE / "evidence/BFS-RUNS.txt").read_text()
    need(f"bfs.c (SHA256 {hashlib.sha256((HERE / 'bfs.c').read_bytes()).hexdigest()})" in text, "runs recorded for this bfs.c")
    for line in text.splitlines():
        if " c=" in line and line.startswith("M="):
            f = dict(kv.split("=") for kv in line.split())
            runs.setdefault((int(f["D"]), int(f["M"])), {})[int(f["c"])] = int(f["dist"])
    need(all(runs.get(k) == v for k, v in EXPECTED_C.items()), "recorded C runs give #4281's minima")
    need(all(runs.get(k) == v for k, v in EXPECTED_BFS.items()), "C runs agree with the Python BFS")

    # controls: a dropped call and an adjacent swap of noncommuting calls are rejected
    w = data["witnesses"]["14"]["1"]
    need(not correct(w[1:], 14, 1), "control: dropped call")
    k = next(i for i in range(len(w) - 1) if abs(int(w[i]) - int(w[i + 1])) == 1)
    need(not correct(w[:k] + w[k + 1] + w[k] + w[k + 2:], 14, 1), "control: adjacent noncommuting swap")

    print(json.dumps({
        "status": "PASS_DEPTH5_CONNECTOR_INDEPENDENT_BFS",
        "python_bfs": {f"depth{d}_m{m}": v for (d, m), v in EXPECTED_BFS.items()},
        "c_bfs_recorded": {f"depth{d}_m{m}": v for (d, m), v in EXPECTED_C.items()},
        "witnesses": count,
        "m4_words": 3,
        "new_kappa_claimed": False,
    }, indent=1))


if __name__ == "__main__":
    sys.exit(main())
