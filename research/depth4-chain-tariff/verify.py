#!/usr/bin/env python3
"""Verify the depth-four dirty chain count-vector classification for m = 2..5.

Standard library only. The calls are z_l += B_l z_{l-1} (l = 1..4) with x = z_0
immutable, dirty z_1..z_3 and y = z_4. A word is correct for (m, c) when its
interval subword counts N_ij (1 <= i <= j <= 4) vanish mod m, except N_14 = c.

Checks:
  1. every Pareto witness word: counts, interval conditions, an independent
     UT5(Z/m) product and literal dirty replay with noncommuting maps;
  2. completeness for words of any length:
       m = 2: the two-middle-call lemma, checked on a bounded box;
       m = 3, 4: the outer-free relaxation has no solution on the ideals
                 missed by the Pareto set (1s and 4s unbounded);
       m = 5: the balanced vector (5,5,5,5) is infeasible;
  3. a second engine (direct interval-state DP) on bounded boxes, compared
     with the exact reduction engine vector by vector;
  4. positive and negative controls, and a generated source-hash receipt.
"""
import hashlib
import itertools
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent

INTERVALS = [(i, j) for i in range(1, 5) for j in range(i, 5)]
PARETO = {
    2: [(2, 4, 4, 2)],
    3: [(3, 3, 9, 3), (3, 6, 6, 3), (3, 9, 3, 3)],
    4: [(4, 4, 8, 4), (4, 8, 4, 4)],
    5: [(10, 5, 5, 5), (5, 10, 5, 5), (5, 5, 10, 5), (5, 5, 5, 10)],
}
# (n2, n3) pairs with n1, n4 unbounded that a non-dominating vector can have.
MISSED_MIDDLE = {3: [(3, 3), (3, 6), (6, 3)], 4: [(4, 4)]}
# Outer-free middle pairs that must be feasible (positive controls).
HIT_MIDDLE = {3: [(3, 9), (6, 6), (9, 3)], 4: [(4, 8), (8, 4)]}
# Direct-DP boxes: top count per letter.  Engine A is compared wherever every
# count is at most ENGINE_A_CAP (its cost grows binomially).
BOX = {2: (6, 6, 6, 6), 3: (6, 6, 6, 6), 4: (8, 4, 4, 8)}
ENGINE_A_CAP = 6


def require(cond, msg):
    if not cond:
        raise SystemExit(f"FAIL: {msg}")


def target(m, c):
    return {k: (c % m if k == (1, 4) else 0) for k in INTERVALS}


def interval_counts(word, m):
    """Interval subword counts by the append recurrence."""
    n = {k: 0 for k in INTERVALS}
    for letter in word:
        for i in range(letter - 1, 0, -1):
            n[(i, letter)] = (n[(i, letter)] + n[(i, letter - 1)]) % m
        n[(letter, letter)] = (n[(letter, letter)] + 1) % m
    return n


def ut5_product(word, m):
    """Independent check: product of elementary matrices I + E_{l,l-1}."""
    mat = [[int(r == s) for s in range(5)] for r in range(5)]
    for letter in word:
        # left-multiply by I + E_{letter, letter-1}: row letter += row letter-1
        mat[letter] = [(a + b) % m for a, b in zip(mat[letter], mat[letter - 1])]
    return mat


def mat_mul(a, b, m):
    return [[sum(a[i][k] * b[k][j] for k in range(len(b))) % m
             for j in range(len(b[0]))] for i in range(len(a))]


def mat_add(a, b, m):
    return [[(x + y) % m for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def literal_replay(word, m, c, rng, dim=2):
    """Run the word on dirty registers with random dim x dim maps over Z/m."""
    rand = lambda r, s: [[rng.randrange(m) for _ in range(s)] for _ in range(r)]
    maps = {l: rand(dim, dim) for l in range(1, 5)}
    init = [rand(dim, 1) for _ in range(5)]
    reg = [[row[:] for row in v] for v in init]
    for letter in word:
        reg[letter] = mat_add(reg[letter], mat_mul(maps[letter], reg[letter - 1], m), m)
    for l in range(4):
        if reg[l] != init[l]:
            return False
    chain = init[0]
    for l in range(1, 5):
        chain = mat_mul(maps[l], chain, m)
    want = mat_add(init[4], [[(c * v) % m for v in row] for row in chain], m)
    return reg[4] == want


def check_word(word, m, c, n):
    require([word.count(l) for l in range(1, 5)] == list(n), f"counts {m},{c},{n}")
    require(interval_counts(word, m) == target(m, c), f"intervals {m},{c},{n}")
    prod = ut5_product(word, m)
    for r in range(5):
        for s in range(5):
            want = 1 if r == s else (c % m if (r, s) == (4, 0) else 0)
            require(prod[r][s] == want, f"UT5 product {m},{c},{n}")


# ---- Engine A: exact reduction over the middle letters --------------------
#
# A word is determined, for all interval counts, by: the interleaving of its
# 2s and 3s; u_i = number of 1s before the i-th 2; r_j = number of 4s after
# the j-th 3.  With A[i][j] = 1 when the i-th 2 precedes the j-th 3:
#   N12 = sum u, N13 = sum_i u_i b_i (b = A 1), N23 = 1'A1,
#   N34 = sum r, N24 = sum_j r_j a_j (a = A'1), N14 = u'A r,
#   N11 = n1, N22 = n2, N33 = n3, N44 = n4.
# Exact counts: u nondecreasing in [0, n1], r nonincreasing in [0, n4].
# Outer-free relaxation (n1, n4 unbounded): u, r arbitrary residue vectors,
# because nondecreasing integer lifts exist and 1s after the last 2 (4s before
# the first 3) change only N11 (N44).

def patterns(n2, n3):
    for pos in itertools.combinations(range(n2 + n3), n2):
        s = set(pos)
        yield [2 if k in s else 3 for k in range(n2 + n3)]


def pattern_matrix(pat):
    twos = threes = 0
    seen2 = []          # number of 2s before each 3
    for letter in pat:
        if letter == 2:
            twos += 1
        else:
            seen2.append(twos)
            threes += 1
    # A[i][j] = 1 iff i < seen2[j]
    return [[int(i < seen2[j]) for j in range(threes)] for i in range(twos)]


def monotone(length, top, decreasing=False):
    for combo in itertools.combinations_with_replacement(range(top + 1), length):
        yield combo[::-1] if decreasing else combo


def reduced_values(m, n, outer_free):
    """Set of N14 residues over correct-except-N14 words (None if N23 fails)."""
    n1, n2, n3, n4 = n
    if not outer_free and (n1 % m or n4 % m):
        return set()
    if n2 % m or n3 % m:
        return set()
    values = set()
    for pat in patterns(n2, n3):
        a = pattern_matrix(pat)
        if sum(map(sum, a)) % m:
            continue
        b = [sum(row) for row in a]
        col = [sum(a[i][j] for i in range(n2)) for j in range(n3)]
        if outer_free:
            us = itertools.product(range(m), repeat=n2)
            rs = itertools.product(range(m), repeat=n3)
        else:
            us = monotone(n2, n1)
            rs = monotone(n3, n4, decreasing=True)
        good_u = [u for u in us if sum(u) % m == 0
                  and sum(x * y for x, y in zip(u, b)) % m == 0]
        good_r = [r for r in rs if sum(r) % m == 0
                  and sum(x * y for x, y in zip(r, col)) % m == 0]
        if not good_u or not good_r:
            continue
        for u in good_u:
            ua = [sum(u[i] * a[i][j] for i in range(n2)) % m for j in range(n3)]
            for r in good_r:
                values.add(sum(x * y for x, y in zip(ua, r)) % m)
    return values


# ---- Engine B: direct DP over interval states ------------------------------

def dp_box(m, top):
    """Reachable interval-residue states for every count vector in [0,top]^4."""
    keys = [(1, 2), (2, 3), (3, 4), (1, 3), (2, 4), (1, 4)]
    table = {(0, 0, 0, 0): {(0,) * 6}}
    for a in itertools.product(range(top[0] + 1), range(top[1] + 1),
                               range(top[2] + 1), range(top[3] + 1)):
        if a == (0, 0, 0, 0):
            continue
        out = set()
        for l in range(4):
            if a[l] == 0:
                continue
            prev = list(a)
            prev[l] -= 1
            prev = tuple(prev)
            for st in table[prev]:
                n12, n23, n34, n13, n24, n14 = st
                if l == 1:
                    n12 = (n12 + prev[0]) % m
                elif l == 2:
                    n13 = (n13 + n12) % m
                    n23 = (n23 + prev[1]) % m
                elif l == 3:
                    n14 = (n14 + n13) % m
                    n24 = (n24 + n23) % m
                    n34 = (n34 + prev[2]) % m
                out.add((n12, n23, n34, n13, n24, n14))
        table[a] = out
    return table, keys


def dominates(n, p):
    return all(x >= y for x, y in zip(n, p))


def main():
    witnesses = json.loads((HERE / "witnesses.json").read_text())
    rng = random.Random(20261021)
    replays = 0

    # 1. witnesses for every (m, c, Pareto vector)
    for m, vecs in PARETO.items():
        for c in range(1, m):
            for n in vecs:
                key = f"{m},{c},{''.join(map(str, n))}"
                word = [int(ch) for ch in witnesses[key]]
                check_word(word, m, c, n)
                for _ in range(3):
                    require(literal_replay(word, m, c, rng), f"replay {key}")
                    replays += 1
    require(len(witnesses) == sum(len(v) * (m - 1) for m, v in PARETO.items()),
            "witness inventory")

    # 2a. m = 2 lemma: exactly two 2s (or two 3s) force N14 = 0.  Proof in
    #     README; here: engine A with n2 = 2 over a box of n1, n3, n4, and the
    #     mirror image (word reversal, l -> 5 - l) sends n3 = 2 to n2 = 2.
    for n1, n3, n4 in itertools.product((2, 4, 6), repeat=3):
        vals = reduced_values(2, (n1, 2, n3, n4), outer_free=False)
        require(1 not in vals, f"m=2 lemma n=({n1},2,{n3},{n4})")
    word = [int(ch) for ch in witnesses["2,1,2442"]]
    mirror = [5 - l for l in reversed(word)]
    require(interval_counts(mirror, 2) == target(2, 1), "mirror symmetry")

    # 2b. m = 3, 4: outer-free relaxation on every missed middle pair.
    for m, pairs in MISSED_MIDDLE.items():
        for n2, n3 in pairs:
            vals = reduced_values(m, (0, n2, n3, 0), outer_free=True)
            require(vals <= {0}, f"outer-free m={m} ({n2},{n3}) hits {vals}")
        for n2, n3 in HIT_MIDDLE[m]:
            vals = reduced_values(m, (0, n2, n3, 0), outer_free=True)
            require(vals == set(range(m)), f"control m={m} ({n2},{n3}) {vals}")

    # 2c. m = 5: the balanced vector misses every nonzero target, and the
    #     outer-free relaxation is not enough (control: it does hit).
    vals5 = reduced_values(5, (5, 5, 5, 5), outer_free=False)
    require(vals5 <= {0}, f"m=5 balanced hits {vals5}")
    require(reduced_values(5, (0, 5, 5, 0), outer_free=True) == set(range(5)),
            "m=5 outer-free control")

    # 3. engine B versus engine A and the claimed up-closure on boxes.
    compared = cross = 0
    for m, top in BOX.items():
        table, keys = dp_box(m, top)
        for n in itertools.product(*(range(m, t + 1, m) for t in top)):
            reach = table[n]
            for c in range(1, m):
                want = (0, 0, 0, 0, 0, c)
                direct = want in reach
                claimed = any(dominates(n, p) for p in PARETO[m])
                require(direct == claimed, f"box m={m} n={n} c={c}")
                if max(n) <= ENGINE_A_CAP:
                    exact = c in reduced_values(m, n, outer_free=False)
                    require(exact == direct, f"engines disagree m={m} n={n} c={c}")
                    cross += 1
                compared += 1

    # 4. negative controls
    bad = [int(ch) for ch in witnesses["4,1,4484"]]
    swapped = bad[:]
    i = next(k for k in range(len(bad) - 1) if bad[k] != bad[k + 1])
    swapped[i], swapped[i + 1] = swapped[i + 1], swapped[i]
    require(interval_counts(swapped, 4) != target(4, 1), "swap control")
    require(interval_counts(bad, 4) != target(4, 2), "residue control")
    require(not all(literal_replay(bad, 4, 2, random.Random(s)) for s in range(8)),
            "replay control")
    require(reduced_values(4, (4, 4, 4, 4), outer_free=False) <= {0}, "floor control")
    require(reduced_values(3, (3, 6, 6, 3), outer_free=False) == {0, 1, 2},
            "exact engine control")

    # receipt
    hashes = {}
    for path in sorted(HERE.iterdir()):
        if path.is_file() and path.suffix in {".py", ".json", ".md"}:
            hashes[f"package/{path.name}"] = hashlib.sha256(path.read_bytes()).hexdigest()
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for row in sources["files"]:
        actual = hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest()
        require(actual == row["sha256"], f"input hash mismatch: {row['path']}")
        hashes[row["path"]] = actual
    receipt = {"pareto": {str(m): v for m, v in PARETO.items()},
               "witnesses": len(witnesses), "replays": replays,
               "box_comparisons": compared, "engine_cross_checks": cross, "sha256": hashes}
    digest = hashlib.sha256(json.dumps(receipt, sort_keys=True).encode()).hexdigest()
    print(json.dumps(receipt, sort_keys=True, indent=1))
    print(f"PASS_DEPTH4_CHAIN_TARIFF witnesses={len(witnesses)} replays={replays} "
          f"box_comparisons={compared} cross_checks={cross} receipt_sha256={digest}")


if __name__ == "__main__":
    sys.exit(main())
