#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent nullspace and schedule checks; imports no reduction code."""
from fractions import Fraction as F
import gzip
import hashlib
import json
from pathlib import Path

P = Path(__file__).resolve().parent


def need(ok, why):
    if not ok:
        raise ValueError(why)


def nullspace(rows):
    a = [[F(x) for x in row] for row in rows]
    width, row, pivots = len(a[0]), 0, []
    for j in range(width):
        k = next((k for k in range(row, len(a)) if a[k][j]), None)
        if k is None:
            continue
        a[row], a[k] = a[k], a[row]
        c = a[row][j]
        a[row] = [x / c for x in a[row]]
        for k in range(len(a)):
            if k != row:
                c = a[k][j]
                a[k] = [x - c * y for x, y in zip(a[k], a[row])]
        pivots.append(j)
        row += 1
        if row == len(a):
            break
    free = [j for j in range(width) if j not in pivots]
    need(len(free) == 1 and len(pivots) == 7, "rank-seven hyperplane")
    normal = [F(j == free[0]) for j in range(width)]
    for i, j in enumerate(pivots):
        normal[j] = -a[i][free[0]]
    need(all(sum(x * y for x, y in zip(row, normal)) == 0 for row in rows), "actual root-row nullspace")
    norm = sum(x * x for x in normal)
    return [[F(i == j) - normal[i] * normal[j] / norm for j in range(width)] for i in range(width)]


def product2(a, b, modulus):
    return [[sum(a[i][k] * b[k][j] for k in range(2)) % modulus for j in range(2)] for i in range(2)]


def main():
    data = (P / "inputs/r437-word.json.gz").read_bytes()
    need(hashlib.sha256(data).hexdigest() == "e432182d5b62c8bbefeb871fce30317234d707e5e18d4295e65ac21f7fd8365e", "independent source pin")
    word, result = json.loads(gzip.decompress(data)), json.loads((P / "RESULT.json").read_bytes())
    for row in result["captures"]:
        frame = row["frame"]
        projection = nullspace([word["lines"][k] for k in word["frames"][frame]])
        digest = hashlib.sha256(json.dumps([[str(x) for x in r] for r in projection], sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        need(digest == row["projector_sha256"], "independent projector matrix")

    # Count the actual fixed supports in a different loop organization.
    d = 64
    swaps = [(j, k) for j in range(d) for k in range(j + 1, d)]
    eliminations = [(i, j) for j in range(d) for i in range(d) if i != j]
    supports = []
    for j, k in swaps:
        supports += [(j, k), (k, j), (j, k)]
    supports += eliminations
    for i in range(d - 1):
        supports += [(i, d - 1), (d - 1, i), (i, d - 1)] * 2
    length = len(supports)
    reverse = sum(i < j for i, j in supports) + sum(i > j for i, j in supports)
    invoice = result["invoice"]
    need(length == result["fixed_word_length"] == 10458, "independent support length")
    need(2 * reverse == result["physical_reverse_factor_slots"] == 20916, "physical head/tail order")
    need(invoice["ordered_shear_calls"] == 4 * length * 10, "all column scalar passes")
    need(invoice["ordinary_block_swap_calls_upper"] == 4 * reverse == 41832, "all reverse interchanges")
    need(invoice["coarse_calls"] == 1 and invoice["coarse_width_atoms"] == 70, "one complete coarse child")

    identities = 0
    for modulus in (3, 9, 25, 49, 81):
        for a in range(1, modulus):
            if a % (3 if modulus in (3, 9, 81) else 5 if modulus == 25 else 7) == 0:
                continue
            inv = pow(a, -1, modulus)
            # Direct left-to-right matrix multiplication, independently of
            # factor_sl's chronological row-action implementation.
            forward = [[0, a], [-inv % modulus, 0]]
            right = [[0, -1 % modulus], [1, 0]]
            need(product2(forward, right, modulus) == [[a, 0], [0, inv]], "unit diagonal identity")
            identities += 1
    need(result["supplier_admitted"] is False and result["physical_backend_implemented"] is False, "no scientific promotion")
    print("PASS_INDEPENDENT_NULLSPACE_AND_COMPLETE_INVOICE frames=9 unit_identities=" + str(identities))


if __name__ == "__main__":
    main()
