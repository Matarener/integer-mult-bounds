#!/usr/bin/env python3
"""Two-helper zero-frame shears: feedback never helps, for every target count.

Model of PR1306/PR2567: registers h0, h1, y0..y(T-1); a gate (d, s) is
register[d] ^= register[s] at unit cost; restricted words have no gate with a
helper destination and a target source. The map is (h, y) -> (h, y + K h).
For row counts a, b, c of (1,0), (0,1), (1,1) in K, PROOF.md shows that both
minima equal f(K) = a + b + c + min(c, 2).

Checks (standard library only):
  witnesses  every K for T = 1..8: an explicit restricted word of length f(K)
             computes exactly the shear (all dirty inputs, by linearity)
  bfs        exact unrestricted and restricted BFS for T = 1, 2, 3 against f
  pr2567     f against the pinned 2x4, 2x5 and 2x6 certified minima
  controls   mutated words and a wrong formula are rejected

Produced by Nick Petalas. Apache-2.0.
"""
import hashlib
import json
from pathlib import Path
import sys

PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]
PR2567 = ROOT / "research/bit-zero-frame-feedback-to-8-registers/CERTIFICATE.json"
PR2567_SHA256 = "c47b7a294fd5ac6a9379e8967ecda48f4ef1428b7efeddca93fb8c3b03b8adfc"
H = 2
MAX_WITNESS_T = 8
MAX_BFS_T = 3


def require(cond, msg):
    if not cond:
        raise AssertionError(msg)


def rows_of(K, T):
    """Row i of K as a 2-bit mask (bit j = helper j), K[i][j] = bit i*H + j."""
    return [(K >> (H * i)) & 3 for i in range(T)]


def formula(K, T):
    r = rows_of(K, T)
    c = r.count(3)
    return r.count(1) + r.count(2) + c + min(c, 2)


def shear(K, T):
    """Target matrix as a tuple of register rows (bit e = coefficient of register e)."""
    out = [1 << j for j in range(H)]
    for i, row in enumerate(rows_of(K, T)):
        out.append((1 << (H + i)) | row)
    return tuple(out)


def apply_word(word, n):
    rows = [1 << e for e in range(n)]
    for d, s in word:
        require(d != s and 0 <= d < n and 0 <= s < n, "bad gate")
        rows[d] ^= rows[s]
    return tuple(rows)


def restricted(word):
    return all(not (d < H and s >= H) for d, s in word)


def witness(K, T):
    """Restricted word of length f(K): direct reads, then one shared h0 ^= h1 block when c >= 2."""
    rows = rows_of(K, T)
    c = rows.count(3)
    word = [(H + i, row - 1) for i, row in enumerate(rows) if row in (1, 2)]
    both = [H + i for i, row in enumerate(rows) if row == 3]
    if c >= 2:
        word += [(0, 1)] + [(y, 0) for y in both] + [(0, 1)]
    else:
        word += [g for y in both for g in ((y, 0), (y, 1))]
    return word


def check_witnesses():
    total = 0
    for T in range(1, MAX_WITNESS_T + 1):
        n = H + T
        for K in range(1 << (H * T)):
            w = witness(K, T)
            require(restricted(w), "witness uses feedback")
            require(len(w) == formula(K, T), "witness length differs from f")
            require(apply_word(w, n) == shear(K, T), "witness computes a different map")
            total += 1
    return total


def bfs_distances(T, restricted_only, horizon):
    n = H + T
    gens = [(d, s) for d in range(n) for s in range(n)
            if d != s and not (restricted_only and d < H and s >= H)]
    start = tuple(1 << e for e in range(n))
    dist = {start: 0}
    frontier = [start]
    for depth in range(1, horizon + 1):
        nxt = []
        for m in frontier:
            for d, s in gens:
                rows = list(m)
                rows[d] ^= rows[s]
                t = tuple(rows)
                if t not in dist:
                    dist[t] = depth
                    nxt.append(t)
        frontier = nxt
    return dist


def check_bfs():
    compared = 0
    for T in range(1, MAX_BFS_T + 1):
        horizon = max(formula(K, T) for K in range(1 << (H * T)))
        full = bfs_distances(T, False, horizon)
        rest = bfs_distances(T, True, horizon)
        for K in range(1 << (H * T)):
            m = shear(K, T)
            require(full.get(m) == formula(K, T), f"unrestricted minimum differs T={T} K={K}")
            require(rest.get(m) == formula(K, T), f"restricted minimum differs T={T} K={K}")
            compared += 1
    return compared


def check_pr2567():
    data = PR2567.read_bytes()
    require(hashlib.sha256(data).hexdigest() == PR2567_SHA256, "PR2567 certificate hash")
    cert = json.loads(data)
    compared = 0
    seen = []
    for shape in cert["shapes"]:
        if shape["helpers"] != H:
            continue
        T = shape["targets"]
        costs = [int(ch, 16) for ch in shape["costs_hex"]]
        require(len(costs) == 1 << (H * T), "PR2567 cost table size")
        for K, cost in enumerate(costs):
            require(cost == formula(K, T), f"PR2567 cost differs T={T} K={K}")
            compared += 1
        seen.append(T)
    require(seen == [4, 5, 6], "expected PR2567 shapes 2x4, 2x5, 2x6")
    return compared


def check_controls():
    T, K = 3, 0b111111  # three (1,1) rows: f = 5
    w = witness(K, T)
    require(apply_word(w[:-1], H + T) != shear(K, T), "truncated word accepted")
    require(apply_word([(1, 0)] + w[1:], H + T) != shear(K, T), "wrong shared gate accepted")
    require(not restricted(w + [(0, H)]), "feedback gate not detected")
    full = bfs_distances(T, False, 5)
    require(full.get(shear(K, T)) != bin(K).count("1"), "weight formula wt(K) was not rejected")
    return 4


def main():
    w = check_witnesses()
    b = check_bfs()
    p = check_pr2567()
    c = check_controls()
    print(f"PASS_TWO_HELPER_ZERO_FRAME_FEEDBACK witnesses={w} bfs={b} pr2567={p} "
          f"controls={c} feedback_gains=0 no_new_kappa")


if __name__ == "__main__":
    sys.exit(main())
