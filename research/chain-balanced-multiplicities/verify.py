#!/usr/bin/env python3
"""Exact balanced multiplicities of the unsigned depth-three chain.

A balanced word has m copies of each letter 1, 2, 3. It is correct for
target c exactly when N12 = N23 = 0 and N13 = c modulo m, where Nij counts
scattered subwords i(i+1)...j (credited interval identity, research/chain-tariff).
This script counts those words for every m in 2..MAX_M and every c, checks
the counts by two independent models, and certifies that the m-1 nonzero
residues have pairwise distinct counts for 3 <= m <= MAX_M.
"""

import hashlib
import json
import sys
from itertools import combinations
from math import comb, factorial
from pathlib import Path

MAX_M = 24
GAP_MAX_M = 7
LITERAL_MAX_M = 5
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_CHAIN_BALANCED_MULTIPLICITIES"


def check(condition, message):
    """Raise even under python -O."""
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def chrono_residues(m):
    """Chronological DP: map (N12, N23, N13) mod m to word counts."""
    size = m * m * m
    cells = [(p, q, r) for p in range(m) for q in range(m) for r in range(m)]
    on_two = [[((p + a) % m * m + q) * m + r for p, q, r in cells]
              for a in range(m + 1)]
    on_three = [[(p * m + (q + b) % m) * m + (r + p) % m for p, q, r in cells]
                for b in range(m + 1)]
    layer = {(0, 0, 0): [1] + [0] * (size - 1)}
    for _ in range(3 * m):
        new = {}
        for (a, b, c), vec in layer.items():
            moves = ((a < m, (a + 1, b, c), None),
                     (b < m, (a, b + 1, c), on_two[a]),
                     (c < m, (a, b, c + 1), on_three[b]))
            for allowed, key, perm in moves:
                if not allowed:
                    continue
                out = new.setdefault(key, [0] * size)
                for i, x in enumerate(vec):
                    if x:
                        out[i if perm is None else perm[i]] += x
        layer = new
    vec = layer[(m, m, m)]
    return {cells[i]: x for i, x in enumerate(vec) if x}


def gap_residues(m):
    """Independent model by the 1s and 3s preceding each 2.

    With A_k ones and B_k threes before the k-th 2, N12 = sum A_k,
    N23 = sum (m - B_k) and N13 = sum A_k (m - B_k). Gap j between
    consecutive 2s holds dA ones and dB threes in C(dA+dB, dA) orders.
    """
    states = {(0, 0, 0, 0, 0): 1}
    for _ in range(m):
        new = {}
        for (a, b, s12, s23, s13), w in states.items():
            for a2 in range(a, m + 1):
                for b2 in range(b, m + 1):
                    key = (a2, b2, (s12 + a2) % m, (s23 + m - b2) % m,
                           (s13 + a2 * (m - b2)) % m)
                    weight = w * comb(a2 - a + b2 - b, a2 - a)
                    new[key] = new.get(key, 0) + weight
        states = new
    out = {}
    for (a, b, s12, s23, s13), w in states.items():
        key = (s12, s23, s13)
        out[key] = out.get(key, 0) + w * comb(2 * m - a - b, m - a)
    return out


def literal_residues(m):
    """Enumerate every literal balanced word and count its subwords."""
    out = {}
    positions = range(3 * m)
    for ones in combinations(positions, m):
        rest = [i for i in positions if i not in ones]
        for twos in combinations(rest, m):
            word = [3] * (3 * m)
            for i in ones:
                word[i] = 1
            for i in twos:
                word[i] = 2
            n1 = n12 = n2 = n23 = n13 = 0
            for letter in word:
                if letter == 1:
                    n1 += 1
                elif letter == 2:
                    n12 += n1
                    n2 += 1
                else:
                    n13 += n12
                    n23 += n2
            key = (n12 % m, n23 % m, n13 % m)
            out[key] = out.get(key, 0) + 1
    return out


def depth_two_counts(m):
    """Control: one-source depth-two words B^m A^m, N_BA mod m."""
    out = [0] * m
    for bs in combinations(range(2 * m), m):
        seen = 0
        total = 0
        for i in range(2 * m):
            if i in bs:
                seen += 1
            else:
                total += seen
        out[total % m] += 1
    return out


def balanced_vector(residues, m):
    return [residues.get((0, 0, c), 0) for c in range(m)]


def unit_stabilizer(m, w):
    return [u for u in range(1, m) if all(w[u * c % m] == w[c]
            for c in range(m)) and any(u * v % m == 1 for v in range(m))]


def check_models():
    for m in range(2, GAP_MAX_M + 1):
        chrono = chrono_residues(m)
        check(chrono == gap_residues(m), f"gap model differs at m={m}")
        if m <= LITERAL_MAX_M:
            check(chrono == literal_residues(m), f"literal differs at m={m}")
        total = factorial(3 * m) // factorial(m) ** 3
        check(sum(chrono.values()) == total, f"mass at m={m}")


def check_depth_two_control():
    """At prime p the depth-two nonzero counts are equal (PR4236 law)."""
    for p in (2, 3, 5, 7):
        counts = depth_two_counts(p)
        expected = (comb(2 * p, p) - 2) // p
        check(counts[1:] == [expected] * (p - 1), f"depth-two control p={p}")
        check(len(unit_stabilizer(p, counts)) == p - 1,
              f"depth-two stabilizer p={p}")


def build_table():
    table = {}
    for m in range(2, MAX_M + 1):
        residues = chrono_residues(m)
        total = factorial(3 * m) // factorial(m) ** 3
        check(sum(residues.values()) == total, f"mass at m={m}")
        table[m] = balanced_vector(residues, m)
    return table


def certificate(table):
    rows = []
    for m in range(3, MAX_M + 1):
        w = table[m]
        nonzero = w[1:]
        check(len(set(nonzero)) == m - 1, f"repeated nonzero count at m={m}")
        check(unit_stabilizer(m, w) == [1], f"nontrivial stabilizer m={m}")
        low = min(range(1, m), key=lambda c: w[c])
        high = max(range(1, m), key=lambda c: w[c])
        rows.append({"m": m, "argmin_c": low, "argmax_c": high})
    return rows


def check_controls(table):
    exceptional = {(2, 1), (3, 2), (4, 3)}
    for m in range(2, MAX_M + 1):
        for c in range(1, m):
            zero = table[m][c] == 0
            check(zero == ((m, c) in exceptional), f"positivity at {(m, c)}")
    forged = dict(table)
    forged[5] = [table[5][0], 1, 1, 1, 1]
    rejected = True
    try:
        certificate(forged)
        rejected = False
    except SystemExit:
        pass
    check(rejected, "forged equal counts were accepted")


def receipt(table, rows):
    body = {"marker": MARKER, "max_m": MAX_M,
            "balanced_counts": {str(m): [str(x) for x in w]
                                for m, w in table.items()},
            "distinct_nonzero_certificate": rows}
    text = json.dumps(body, indent=1, sort_keys=True) + "\n"
    return body, text


def main():
    check_models()
    check_depth_two_control()
    table = build_table()
    rows = certificate(table)
    check_controls(table)
    body, text = receipt(table, rows)
    result_path = PACKAGE / "RESULT.json"
    if "--write" in sys.argv[1:]:
        result_path.write_text(text, encoding="utf-8")
    stored = json.loads(result_path.read_text(encoding="utf-8"))
    check(stored == body, "RESULT.json differs from recomputation")
    digest = hashlib.sha256(text.encode()).hexdigest()
    print(f"{MARKER} max_m={MAX_M} result_sha256={digest}")


if __name__ == "__main__":
    main()
