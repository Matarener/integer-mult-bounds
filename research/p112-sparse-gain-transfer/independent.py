"""Independent literal premises and controls; no producer imports or searches.

The quantified graph and gain-transfer arguments are audited in
INDEPENDENT-PROOF.md. This script does not claim to formalize that proof.
"""
from pathlib import Path
from hashlib import sha256
from collections import Counter
from fractions import Fraction as F
import argparse
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RECEIPT = HERE / "INDEPENDENT-RESULT.json"
PINS = {
    "research/p112-rational-decoder-gate/CANDIDATE.json":
    "dc5fbe51f9cd3a14361256ac136736bffb18971d0247b891accf0d2ee060d06b",
    "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json":
    "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa",
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def transpose(a):
    return list(map(list, zip(*a)))


def multiply(a, b):
    return [[sum((x*y for x, y in zip(row, col)), F(0))
             for col in zip(*b)] for row in a]


def rank(a):
    a = [list(map(F, row)) for row in a]
    r = 0
    for j in range(len(a[0])):
        pivot = next((i for i in range(r, len(a)) if a[i][j]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        q = a[r][j]
        a[r] = [x/q for x in a[r]]
        for i in range(r+1, len(a)):
            q = a[i][j]
            a[i] = [x-q*y for x, y in zip(a[i], a[r])]
        r += 1
        if r == len(a):
            break
    return r


def binary_rank(rows):
    basis = {}
    for value in rows:
        while value:
            pivot = value.bit_length()-1
            if pivot not in basis:
                basis[pivot] = value
                break
            value ^= basis[pivot]
    return len(basis)


def gf4mul(a, b):
    out = 0
    while b:
        if b & 1:
            out ^= a
        b >>= 1
        a <<= 1
        if a & 4:
            a ^= 7
    return out


def gf4sum(values):
    out = 0
    for value in values:
        out ^= value
    return out


def bridge_controls():
    # Six independent triangle columns and one bridge, on six scalar ports.
    edges = [(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3), (0, 3)]
    q = [[F(i in edge) for edge in edges] for i in range(6)]
    c = [[F(i == j or i == j+3) for j in range(3)] for i in range(6)]
    d = [[F(x, 2) for x in row] for row in
         [[1, 1, -1], [-1, 1, 1], [1, -1, 1]] * 2]
    r0 = multiply(d, transpose(c)) + [[F(0)] * 6]
    k = list(map(F, ["-1/2", "1/2", "-1/2", "-1/2", "1/2", "-1/2", "1"]))
    target = multiply(c, transpose(c))
    need(rank(q) == 6 and rank([row[:6] for row in q]) == 6, "bridge rank and unique null direction")
    need(multiply(q, [[x] for x in k]) == [[0]] * 6, "literal bridge kernel")
    need(multiply(q, r0) == target, "particular bridge endpoint")
    # These are coefficient identities in arbitrary z, not a finite sampling
    # claim. Zero-target ambient columns merely extend z and r0 by zeros.
    for i in range(3):
        need(r0[i] == r0[i+3] and k[i] == k[i+3], "all-reader repeated-row identity")
    merged = [[q[i][j]+q[i][j+3] for j in range(3)] + [q[i][6]] for i in range(6)]
    coefficient_queries = [[1, 0, 1, 1], [1, 1, 0, 0], [0, 1, 1, 0]]
    need(merged == multiply(c, coefficient_queries), "coalesced coefficient-space two-sparsity")
    need(all(sum(bool(coefficient_queries[i][j]) for i in range(3)) <= 2 for j in range(4)), "scalar-demand query bound")
    # An additional zero-target ambient coordinate exercises arbitrary readers.
    z = list(map(F, ["1/3", "-2", "0", "5/2", "-7/3", "1", "4/5"]))
    readers = [[*(x+k[i]*z[j] for j, x in enumerate(row)), k[i]*z[6]]
               for i, row in enumerate(r0)]
    full_target = [row+[F(0)] for row in target]
    need(multiply(q, readers) == full_target, "ambient asymmetric bridge endpoint")
    need(multiply(merged, readers[:3]+[readers[6]]) == full_target, "coalesced exact ambient endpoint")
    bad = [row[:] for row in readers]
    bad[0][0] += 1
    need(multiply(q, bad) != full_target, "nonzero reader mutation must break endpoint")
    bad_kernel = k[:]
    bad_kernel[3] *= -1
    need(multiply(q, [[x] for x in bad_kernel]) != [[0]] * 6, "kernel-sign mutation must fail")
    return {"query_rank": 6, "nullity": 1, "coalesced_queries": 4,
            "universal_row_pair_identities": 3, "ambient_control_columns": 7}


def run():
    inputs = []
    for path, digest in PINS.items():
        raw = (ROOT/path).read_bytes()
        need(sha256(raw).hexdigest() == digest, "literal input " + path)
        inputs.append(json.loads(raw))
    candidate, data = inputs
    labels = {r["port"]: r["q"] for r in data["recipes"]}
    groups, marks = candidate["groups"], candidate["factor_supports"]
    owner = {p: g for g, group in enumerate(groups) for p in group}
    mark = {p: j for j, support in enumerate(marks) for p in support}
    need(len(owner) == sum(map(len, groups)) == 112, "physical partition")
    need(len(mark) == sum(map(len, marks)) == 112 and set(mark) == set(owner), "disjoint target partition")
    need(len(marks) == 57 and Counter(map(len, marks)) == {1: 3, 2: 53, 3: 1}, "canonical mark sizes")
    expanded = [(p, labels[q]) for p in sorted(owner) for q in groups[owner[p]]]
    need(len(expanded) == 334, "whole physical expansion dimension")
    free = {tuple(pair) for pair in candidate["orthogonal_group_pairs"]}
    literal_free = {(g, h) for g in range(len(groups)) for h in range(g+1, len(groups))
                    if all((labels[p] & labels[q]).bit_count() % 2 == 0
                           for p in groups[g] for q in groups[h])}
    need(free == literal_free, "free group pairs equal entire-space orthogonality")
    def allowed(p, q):
        return tuple(sorted((owner[p], owner[q]))) in free
    for i, (p, a) in enumerate(expanded):
        for j, (q, b) in enumerate(expanded):
            pairing = (a & b).bit_count() % 2
            actual = int(mark[p] == mark[q])*pairing
            need(actual == int(i == j), "literal expanded endpoint I334")
            # Each allowed scalar entry can be an independent indeterminate:
            # its coefficient in the expanded matrix is identically zero.
            if allowed(p, q):
                need(pairing == 0, "arbitrary free coefficient disappears")
            else:
                need(int(p == q)*pairing == int(i == j), "universal strict-mask expanded entry")
    prices = []
    for support in marks:
        vectors = [labels[p] for g in sorted({owner[p] for p in support}) for p in groups[g]]
        pairing = [sum(((a & b).bit_count() % 2) << j for j, b in enumerate(vectors)) for a in vectors]
        prices.append(binary_rank(pairing))
    need(Counter(prices) == {3: 3, 6: 53, 7: 1} and sum(prices) == 334, "singleton, paired and residual whole-group prices")
    residual_mark = next(i for i, support in enumerate(marks) if len(support) == 3)
    need(prices[residual_mark] == 7, "residual three-copy term is fully charged")
    residual_support = marks[residual_mark]
    residual_unit = [p for p in residual_support if len(groups[owner[p]]) == 1]
    residual_pair = [p for p in residual_support if p not in residual_unit]
    need(len(residual_unit) == 1 and len(residual_pair) == 2, "literal residual pair/unit split")
    full_reader = [labels[p] for g in sorted({owner[p] for p in residual_support}) for p in groups[g]]
    split_prices = []
    for part in [residual_pair, residual_unit]:
        full_source = [labels[p] for g in sorted({owner[p] for p in part}) for p in groups[g]]
        rows = [sum(((a & b).bit_count() % 2) << j for j, b in enumerate(full_reader)) for a in full_source]
        split_prices.append(binary_rank(rows))
    need(split_prices == [6, 1] and sum(split_prices) == prices[residual_mark], "two-port local completion preserves residual price")
    need(set(residual_pair).isdisjoint(residual_unit) and set(residual_pair+residual_unit) == set(residual_support), "split source sum retains original complete reader")

    # A three-copy mark on an arbitrary-gain tree needs a genuine row gauge.
    original = [[1, 0], [-1, 2], [0, 1]]
    need([sum(row) for row in original] == [1, 1, 1], "rational three-mark recovery")
    base = [[1, 0], [1, 1], [0, 1]]
    need(all(gf4sum(row[j] for row in base) == 0 for j in range(2)), "ungauged switching annihilator")
    need(gf4sum([1, 1, 1]) != 0, "ungauged three-mark failure")
    gauge = [1, 3, 2]
    shifted = [[gf4mul(gauge[i], value) for value in row] for i, row in enumerate(base)]
    recovered = [gf4sum(gf4mul(value, coefficient) for value, coefficient in zip(row, [1, 3])) for row in shifted]
    need(recovered == [1, 1, 1], "GF4 gauge exact three-copy endpoint")
    need([[bool(x) for x in row] for row in shifted] == [[bool(x) for x in row] for row in original], "query support preserved")

    # Unit-grounded tree: singleton demands require no shared-support premise.
    grounded = [[F(1), F(1)], [F(0), F(-2)]]
    need(multiply(grounded, [[F(1, 2)], [F(-1, 2)]]) == [[0], [1]], "rational grounded singleton")
    grounded_binary = [[1, 1], [0, 1]]
    need([gf4sum(row) for row in grounded_binary] == [0, 1], "grounded singleton over characteristic two")

    # A strict-fit tree transfer deliberately changes allowed off-diagonal
    # coefficients. The only forbidden off-diagonal pair is (0,2).
    strict_q = [[F(1), F(0)], [F(2), F(1)], [F(0), F(3)]]
    strict_r = [[F(1), F(0), F(0)], [F(0), F(1), F(1, 3)]]
    strict_m = multiply(strict_q, strict_r)
    new_q = [[1, 0], [2, 1], [0, 3]]
    new_r = [[1, 0, 0], [0, 1, 2]]
    new_m = [[gf4sum(gf4mul(a, b) for a, b in zip(row, col))
              for col in zip(*new_r)] for row in new_q]
    need(all(strict_m[i][i] == new_m[i][i] == 1 for i in range(3)), "changed-free strict diagonal")
    need(strict_m[0][2] == strict_m[2][0] == new_m[0][2] == new_m[2][0] == 0, "changed-free forbidden entries")
    need([[bool(x) for x in row] for row in strict_q] == [[bool(x) for x in row] for row in new_q], "changed-free source supports")
    need([[bool(x) for x in row] for row in strict_r] == [[bool(x) for x in row] for row in new_r], "changed-free reader supports")
    need(strict_m[1][2] == F(1, 3) and new_m[1][2] == 2, "free entry genuinely changes")
    # Parallel links are distinct graph edges; a digon may be unbalanced.
    digon = [[1, 1], [1, 2]]
    digon_reader = [[3, 2], [2, 2]]
    need([[gf4sum(gf4mul(a, b) for a, b in zip(row, col)) for col in zip(*digon_reader)]
          for row in digon] == [[1, 0], [0, 1]], "unbalanced parallel digon exact recovery")

    # Common recovery is an extra premise when queries are dependent.
    u = [[1, 1, 0], [0, 0, 1]]
    v = [[1, 0], [0, 1], [1, 1]]
    common = {i for i, row in enumerate(v) if row[0] and row[1]}
    need(multiply(u, v) == [[1, 1], [1, 1]] and common == {2}, "dependent distinct-reader control")
    need(rank([[u[i][2], 1] for i in range(2)]) > rank([[u[i][2]] for i in range(2)]), "common support cannot recover mark")
    bridge = bridge_controls()
    return {"status": "PASS_INDEPENDENT_SPARSE_GAIN_PREMISES",
            "input_sha256": PINS, "canonical_marks": 57,
            "mark_size_counts": {str(k): v for k, v in sorted(Counter(map(len, marks)).items())},
            "canonical_price_profile": {str(k): v for k, v in sorted(Counter(prices).items())},
            "expanded_identity_dimension": 334, "expanded_entries_checked": 334**2,
            "strict_mask_free_group_pairs": len(free),
            "strict_mask_free_scalar_entries": sum(allowed(p, q) for p in owner for q in owner),
            "strict_mask_symbolic_expanded_entries_checked": 334**2,
            "two_port_completion_residual_charges": split_prices,
            "bridge_controls": bridge,
            "controls": ["three-copy GF4 row gauge and ungauged failure", "grounded singleton",
                         "literal residual three-copy invoice seven", "failed common-recovery premise",
                         "residual two-port completion costs six plus one",
                         "strict-fit transfer changes free entries", "unbalanced parallel digon",
                         "universal bridge row-pair identities", "ambient exact coalesced endpoint",
                         "reader and kernel-sign mutation rejection"],
            "scope": "Literal geometry and bounded algebra controls; quantified transfer arguments are the accompanying written proof."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    result = run()
    if args.write_receipt:
        RECEIPT.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8", newline="\n")
    else:
        need(result == json.loads(RECEIPT.read_text(encoding="utf-8")), "immutable independent receipt mismatch")
    print(json.dumps(result, indent=2))
