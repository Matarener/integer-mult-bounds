#!/usr/bin/env python3
"""Independent check of the depth-three and depth-four chain-connector tables of #4249, #4263, #4280.

Call l is z_l += B_l z_{l-1}. A positive word is correct for residue c exactly when its product of
I + E[l][l-1] in the unitriangular group mod m is I + c E[D][0]. Checked here with separate code:
#4249's depth-three construction for every m <= 400 and every residue, and BFS minima for small m;
#4263's depth-four words (6 <= m <= 32); #4280's row-model records (33 <= m <= 64), decoded into
words from Lemma 2's definitions; and BFS minima at depth four for m <= 4. No code from those PRs.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
import hashlib
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
VENDORED = {
    "vendor/pr4263-witnesses.json": "d4f5725e936e2a08fa6f680679359c21301c0a59a96e6228a42ecdfd642a012c",
    "vendor/pr4280-witnesses.json": "581474c1a9726240d9e852e143b188be0b2b904a575a49e354a118390c04db14",
}
WORD_6_5 = "111122133232123233"   # #4249's PROOF.md, Lemma 3


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def correct(word, m, c, depth):
    x = [[int(i == j) for j in range(depth + 1)] for i in range(depth + 1)]
    for ch in word:
        l = int(ch)
        x[l] = [(a + b) % m for a, b in zip(x[l], x[l - 1])]
    return all(x[i][j] == (c % m if (i, j) == (depth, 0) else 0) for i in range(depth + 1) for j in range(i))


def literal(word, m, c, depth, rng):
    """dirty registers in (Z/m)^2, random 2x2 maps: z_1..z_(D-1) restored, y += c B_D...B_1 x"""
    mul = lambda a, b: [[sum(a[i][k] * b[k][j] for k in range(2)) % m for j in range(2)] for i in range(2)]
    app = lambda a, v: [sum(a[i][k] * v[k] for k in range(2)) % m for i in range(2)]
    B = {l: [[rng.randrange(m) for _ in range(2)] for _ in range(2)] for l in range(1, depth + 1)}
    z0 = [[rng.randrange(m) for _ in range(2)] for _ in range(depth + 1)]
    z = [v[:] for v in z0]
    for ch in word:
        l = int(ch)
        z[l] = [(a + b) % m for a, b in zip(z[l], app(B[l], z[l - 1]))]
    chain = B[1]
    for l in range(2, depth + 1):
        chain = mul(B[l], chain)
    gain = app(chain, z0[0])
    return z[:depth] == z0[:depth] and z[depth] == [(a + c * b) % m for a, b in zip(z0[depth], gain)]


def bfs(m, depth):
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


def depth3_word(m, c):
    """#4249's Lemma 3 word, with its stated choice of a for c = m - 1"""
    if c <= m - 2:
        a, t = 1, c
    else:
        a = 2 if m % 2 else (m // 2 - 1 if m % 4 == 0 else m // 2 - 2)
        t = (-pow(a, -1, m)) % m
    need(1 <= a <= m // 2 and 1 <= t <= m - 2 and (t * a - c) % m == 0, f"parameters at ({m},{c})")
    return "1" * a + "2" + "3" * t + "1" * (m - 2 * a) + "2" + "1" * a + "2" * (m - t - 2) + "3" + "2" * t + "3" * (m - t - 1)


def decode_rowmodel(rec, m):
    """#4280's Lemma 2: lambda's column heights give the 2/3 path; rho and beta place calls 1 and 4"""
    rows = rec["rows"] + [0] * (m - len(rec["rows"]))
    rho = rec["rho"] + [0] * (m - len(rec["rho"]))
    need(rows == sorted(rows, reverse=True) and rows[0] == m and rho == sorted(rho, reverse=True), "shapes")
    f = [m - sum(1 for l in rows if l >= p) for p in range(1, m + 1)]   # calls 2 before the p-th call 3
    ones = {m - r: rho[r - 1] - (rho[r] if r < m else 0) for r in range(1, m + 1)}   # keyed by calls 2 before
    ones[m] = m - rho[0]                                            # level 0: after every call 2
    fours = {int(b): k for b, k in rec["beta"].items()}
    fours[0] = fours.get(0, 0) + m - sum(fours.values())
    out, n2, n3 = ["4"] * fours[0], 0, 0
    for p in range(m + 1):
        for _ in range((f[p] if p < m else m) - n2):
            out += ["1"] * ones.get(n2, 0) + ["2"]
            n2 += 1
        if p < m:
            n3 += 1
            out += ["3"] + ["4"] * fours.get(n3, 0)
    out += ["1"] * ones.get(m, 0)
    return "".join(out)


def main():
    for rel, digest in VENDORED.items():
        need(hashlib.sha256((HERE / rel).read_bytes()).hexdigest() == digest, f"vendored {rel}")
    rng = random.Random(4280)

    # depth three (#4249): exact minima for m <= 8, the construction for every m <= 400
    for m in range(2, 9):
        exceptions = {(2, 1), (3, 2), (4, 3)}
        need(bfs(m, 3) == {c: (4 * m if (m, c) in exceptions else 3 * m) for c in range(1, m)}, f"depth-3 BFS m={m}")
    words3 = 0
    for m in range(5, 401):
        for c in range(1, m):
            w = WORD_6_5 if (m, c) == (6, 5) else depth3_word(m, c)
            need(len(w) == 3 * m and correct(w, m, c, 3), f"depth-3 word ({m},{c})")
            words3 += 1
    need(all(literal(depth3_word(m, c), m, c, 3, rng) for m in (5, 8, 12, 97) for c in range(1, m)), "depth-3 literal replays")

    # depth four: BFS minima at m <= 4 (#4249's table), the 4m floor, and the witnesses
    need([bfs(m, 4) for m in (2, 3, 4)] == [{1: 12}, {1: 18, 2: 18}, {1: 20, 2: 20, 3: 20}], "depth-4 BFS m=2..4")
    w4263 = json.loads((HERE / "vendor/pr4263-witnesses.json").read_text())["witnesses"]
    w4280 = json.loads((HERE / "vendor/pr4280-witnesses.json").read_text())["witnesses"]
    table = {}
    for m_s, row in w4263.items():
        for c_s, w in row.items():
            table[int(m_s), int(c_s)] = (w, "4263")
    for m_s, row in w4280.items():
        for c_s, rec in row.items():
            table[int(m_s), int(c_s)] = (decode_rowmodel(rec, int(m_s)), "4280")
    need(set(table) == {(m, c) for m in range(6, 65) for c in range(1, m)}, "every (m, c) with 6 <= m <= 64")
    for (m, c), (w, src) in table.items():
        need(len(w) == 4 * m and all(w.count(str(l)) == m for l in range(1, 5)), f"#{src} ({m},{c}) balanced")
        need(correct(w, m, c, 4), f"#{src} ({m},{c}) product")
    need(all(literal(w, m, c, 4, rng) for (m, c), (w, _) in table.items() if c in (1, m - 1)), "depth-4 literal replays")

    # controls: a perturbed row-model record and a dropped call are rejected
    rec = dict(w4280["37"]["5"])
    rec["rho"] = [rec["rho"][0] - 1] + rec["rho"][1:]
    need(not correct(decode_rowmodel(rec, 37), 37, 5, 4), "control: changed rho(1)")
    need(not correct(table[20, 3][0][1:], 20, 3, 4), "control: dropped call")

    print(json.dumps({
        "status": "PASS_CHAIN_CONNECTOR_TABLES_CHECK",
        "depth3": {"bfs_m": "2..8", "construction_words": words3, "m_range": "5..400"},
        "depth4": {"bfs": {"2": 12, "3": 18, "4": 20}, "witnesses_4263": sum(len(r) for r in w4263.values()),
                   "records_4280": sum(len(r) for r in w4280.values()), "m_range": "6..64"},
        "new_kappa_claimed": False,
    }, indent=1))


if __name__ == "__main__":
    sys.exit(main())
