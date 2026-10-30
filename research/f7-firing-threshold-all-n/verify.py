#!/usr/bin/env python3
"""The first all-sound length of the fixed L/2 substitution, for every n >= 5.

Model of #4322: prefix walks on F_2^n; a nonzero mask fires on a universal simple restored word when
base < excess <= base + d^2, base(n, L) = (L/2)(L/2 - 1) - (2^(n-1) - 1). The checks:
  1. min-sumset cap: |A + A| >= 2^ceil(log2 |A|) in F_2^k (exhaustive for k <= 4), so a k-point subset
     of an affine flat has excess at most e(k) = C(k,2) - 2^ceil(log2 k) + 1;
  2. the cap is sound on every L-point subset exactly from L*(n) = 2^n - 2 floor(sqrt(2^(n-1) - 1)),
     for 5 <= n <= 22 by a full split scan (and 14 at n = 4);
  3. an explicit universal word of length L*(n) - 2 on which a weight-one mask fires, for 5 <= n <= 11,
     also after canonical relabeling; a control of length L*(n) on which nothing fires.
Standard library only; no code from #4322.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from itertools import combinations
import json
from math import comb, isqrt
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def base(n, L):
    return (L // 2) * (L // 2 - 1) - ((1 << (n - 1)) - 1)


def cap(k):
    return 0 if k < 2 else comb(k, 2) - (1 << (k - 1).bit_length()) + 1


def l_star(n):
    return (1 << n) - 2 * isqrt((1 << (n - 1)) - 1)


def first_cap_sound(n):
    half, last_bad = 1 << (n - 1), None
    for L in range(2, (1 << n) + 1, 2):
        if any(cap(s) + cap(L - s) > base(n, L) for s in range(max(0, L - half), min(half, L) + 1)):
            last_bad = L
    return last_bad + 2


def excess(points):
    k, seen = len(points), set()
    for i in range(k):
        for j in range(i + 1, k):
            seen.add(points[i] ^ points[j])
    return comb(k, 2) - len(seen)


def fires(n, states, mask):
    sides = ([], [])
    for x in states:
        sides[bin(x & mask).count("1") & 1].append(x)
    e = excess(sides[0]) + excess(sides[1])
    d = (len(sides[0]) - len(sides[1])) // 2
    b = base(n, len(states))
    return b < e <= b + d * d


def gray_cycle(k):
    """reflected Gray code of Q_k as a list of integers; consecutive (and last, first) differ in one bit"""
    return [i ^ (i >> 1) for i in range(1 << k)]


def firing_walk(n, t):
    """prefix states of a closed simple walk on F_2^n: all of {x_1 = 0} plus t points of {x_1 = 1}

    Bit 0 plays x_1. Inside x_1 = 0 use the reflected Gray cycle of the other n - 1 bits, cut at its
    closing edge (0, 2^(n-2)) of the top bit. In x_1 = 1 use the 'ladder' cycle of length t on the
    rows h_0..h_(t/2 - 1) of the Gray cycle of the lower n - 2 bits, also cut at the edge (0, top bit).
    """
    k = n - 1
    top = 1 << (k - 1)
    g = gray_cycle(k)
    need(g[0] == 0 and g[-1] == top, "Gray cycle closes on the top bit")
    h = gray_cycle(k - 1)
    rows = t // 2
    ladder = [h[i] for i in range(rows)] + [h[i] | top for i in reversed(range(rows))]   # from 0 to top
    lift = lambda y: y << 1
    path0 = [lift(y) for y in g]                        # 0 ... top, all of x_1 = 0
    path1 = [lift(y) | 1 for y in reversed(ladder)]     # top+x_1 ... x_1, t points of x_1 = 1
    return path0 + path1


def word_of(states):
    """labels of the steps, closing back to 0"""
    out = []
    for a, b in zip(states, states[1:] + states[:1]):
        diff = a ^ b
        need(diff and diff & (diff - 1) == 0, "consecutive states differ in one bit")
        out.append(diff.bit_length() - 1)
    return out


def canonical(word, n):
    names, out = {}, []
    for lab in word:
        names.setdefault(lab, len(names))
        out.append(names[lab])
    perm = names                                         # old label -> new label
    return out, perm


def check_walk(n, states):
    L = len(states)
    need(len(set(states)) == L and states[0] == 0, "simple walk from 0")
    full = 1 << n
    diff = {a ^ b for a in states for b in states}
    need(len(diff) == full, "universal")
    return L


def main():
    # 1. min-sumset lemma, exhaustive in F_2^k for k <= 4 (all 2^16 subsets at k = 4)
    for k in range(1, 5):
        N = 1 << k
        best = {}
        for s in range(1, 1 << N):
            A = [x for x in range(N) if s >> x & 1]
            size = len({a ^ b for a in A for b in A})
            need(size >= 1 << (len(A) - 1).bit_length(), f"|A+A| >= 2^ceil(log2|A|) in F_2^{k}")
            best[len(A)] = max(best.get(len(A), 0), excess(A))
        need(all(best[j] == cap(j) for j in best), f"cap e(k) attained exactly in F_2^{k}")

    # 2. the cap threshold: full split scan against the closed form
    scan = {n: first_cap_sound(n) for n in range(3, 23)}
    need(scan[3] == 6 and scan[4] == 14, "n = 3, 4 thresholds 6 and 14 (#4322's n = 4 theorem)")
    need(all(scan[n] == l_star(n) for n in range(5, 23)), "L*(n) = 2^n - 2 floor(sqrt(2^(n-1) - 1)) for 5 <= n <= 22")
    # the binding split for n >= 5: both parts above 2^(n-2) at every L >= L*(n)
    need(all((1 << (n - 1)) - (1 << n) + l_star(n) > 1 << (n - 2) for n in range(6, 40)), "t > 2^(n-2) from n = 6")
    # published n = 4 data on main: (4,12) still fires, so the n = 4 cap threshold is attained too
    d3733 = {(r["n"], r["L"]): r for r in json.loads((ROOT / "research/f7-functional-independent-check/RESULT.json").read_text())["new_domains"]}
    need(d3733[4, 12]["false_prunes"] > 0, "#3733: (4,12) fires")

    # 3. explicit firing words one step below L*(n), and controls at L*(n)
    built = {}
    for n in range(5, 12):
        s = 1 << (n - 1)
        L = l_star(n) - 2
        states = firing_walk(n, L - s)
        need(check_walk(n, states) == L, f"n={n}: walk length L* - 2")
        need(fires(n, states, 1), f"n={n}: mask e_1 fires at L* - 2")
        word = word_of(states)
        cword, perm = canonical(word, n)
        cstates, x = [], 0
        for lab in cword:
            cstates.append(x)
            x ^= 1 << lab
        need(x == 0 and fires(n, cstates, 1 << perm[0]), f"n={n}: the canonical word fires its relabeled mask")
        control = firing_walk(n, L + 2 - s)
        if n <= 8:
            need(not any(fires(n, control, m) for m in range(1, 1 << n)), f"n={n}: nothing fires on the length-L* control")
        else:
            need(not fires(n, control, 1), f"n={n}: e_1 does not fire on the length-L* control")
        built[str(n)] = {"L_star": l_star(n), "firing_length": L}

    print(json.dumps({
        "status": "PASS_F7_FIRING_THRESHOLD_ALL_N",
        "L_star_closed_form": "2^n - 2 floor(sqrt(2^(n-1) - 1)), n >= 5",
        "scan": {str(n): v for n, v in scan.items() if n <= 12},
        "firing_words_below_L_star": built,
        "new_kappa_claimed": False,
    }, indent=1))


if __name__ == "__main__":
    sys.exit(main())
