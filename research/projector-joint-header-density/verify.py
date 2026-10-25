#!/usr/bin/env python3
"""Exact joint rank-one header counts. Produced by Nick Petalas. Apache-2.0."""

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
from itertools import product
import json
from math import comb, prod
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
LOCAL_FILES = ("README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
PAIR_CASES = tuple((q, m) for q, top in ((2, 7), (3, 5), (4, 4), (5, 3))
                   for m in range(1, top + 1))
HEADER_CASES = ((2, 2), (3, 2), (4, 2), (5, 2),
                (2, 3), (3, 3), (4, 3), (2, 4))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def field(q):
    """F4 is F2[x]/(x^2+x+1), encoded by two coefficient bits."""
    need(q in (2, 3, 4, 5), "unsupported executable field")
    add = tuple(tuple((a ^ b) if q == 4 else (a + b) % q
                      for b in range(q)) for a in range(q))
    multiply = []
    for a in range(q):
        row = []
        for b in range(q):
            if q == 4:
                value = (a if b & 1 else 0) ^ ((a << 1) if b & 2 else 0)
                if value & 4:
                    value ^= 7
            else:
                value = a * b % q
            row.append(value)
        multiply.append(tuple(row))
    mul = tuple(multiply)
    neg = tuple(next(b for b in range(q) if add[a][b] == 0) for a in range(q))
    inv = (0,) + tuple(next(b for b in range(1, q) if mul[a][b] == 1)
                       for a in range(1, q))
    for a, b, c in product(range(q), repeat=3):
        need(mul[a][add[b][c]] == add[mul[a][b]][mul[a][c]], "distributivity")
        need(mul[a][mul[b][c]] == mul[mul[a][b]][c], "associativity")
    return add, mul, neg, inv


def joint_fraction(q, m, k):
    need(q >= 2 and 1 <= m <= 128 and 0 <= k <= m, "formula domain")
    if k == 0:
        return Fraction(1)
    return Fraction((q - 1) ** k * (q ** (m - k) * (q - 1) ** k - (-1) ** k),
                    q ** k * (q ** m - 1))


def full_distribution(q, m):
    need(q >= 2 and 1 <= m <= 128, "distribution domain")
    # Counts ordered (a,b) with a.b=1 and exactly s nonzero a_i b_i.
    return [comb(m, s) * (q - 1) ** s *
            (((q - 1) ** s - (-1) ** s) // q) * (2 * q - 1) ** (m - s)
            for s in range(m + 1)]


def scalar_census(q, m, tables):
    add, mul, _, _ = tables
    need(q ** (2 * m) <= 100000, "scalar census capacity")
    vectors = tuple(product(range(q), repeat=m))
    masks = Counter()
    for a in vectors:
        for b in vectors:
            total = 0
            mask = 0
            for i in range(m):
                value = mul[a[i]][b[i]]
                total = add[total][value]
                mask |= int(value != 0) << i
            if total == 1:
                masks[mask] += 1
    return masks


def inverse(matrix, tables):
    add, mul, neg, inv = tables
    n = len(matrix)
    need(1 <= n <= 16 and all(len(row) == n for row in matrix), "matrix dimensions")
    rows = [list(row) + [int(i == j) for j in range(n)]
            for i, row in enumerate(matrix)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if rows[i][j]), None)
        if pivot is None:
            return None
        rows[j], rows[pivot] = rows[pivot], rows[j]
        scale = inv[rows[j][j]]
        rows[j] = [mul[scale][value] for value in rows[j]]
        for i in range(n):
            if i != j:
                scale = neg[rows[i][j]]
                rows[i] = [add[x][mul[scale][y]] for x, y in zip(rows[i], rows[j])]
    need(all(rows[i][j] == int(i == j) for i in range(n) for j in range(n)),
         "elimination endpoint")
    return tuple(tuple(row[n:]) for row in rows)


def header_census(q, m, tables):
    """Enumerate full matrices, independently of the scalar-pair generator."""
    need(q ** (m * m) <= 300000, "header census capacity")
    mul = tables[1]
    masks, fibers = Counter(), Counter()
    for flat in product(range(q), repeat=m * m):
        matrix = tuple(flat[i * m:(i + 1) * m] for i in range(m))
        undo = inverse(matrix, tables)
        if undo is None:
            continue
        a, b = matrix[0], tuple(row[0] for row in undo)
        mask = sum(int(mul[a[i]][b[i]] != 0) << i for i in range(m))
        masks[mask] += 1
        fibers[(a, b)] += 1
    expected_gl = prod(q ** m - q ** j for j in range(m))
    need(sum(masks.values()) == expected_gl, "complete GL cardinality")
    need(len(set(fibers.values())) == 1, "equal row/column fibers")
    need(len(fibers) == (q ** m - 1) * q ** (m - 1), "all scalar pairs reached")
    return masks, next(iter(fibers.values()))


def check_counts(q, m, masks, scale):
    total_pairs = (q ** m - 1) * q ** (m - 1)
    need(sum(masks.values()) == scale * total_pairs, "total count")
    observed = [sum(count for mask, count in masks.items() if mask.bit_count() == s)
                for s in range(m + 1)]
    need(observed == [scale * count for count in full_distribution(q, m)],
         "complete success-count distribution")
    # Test every prescribed subset, not only the first k coordinates.
    for subset in range(1 << m):
        count = sum(value for mask, value in masks.items() if mask & subset == subset)
        need(Fraction(count, scale * total_pairs) == joint_fraction(q, m, subset.bit_count()),
             "joint fraction for prescribed subset")
    return {"q": q, "m": m, "pairs": total_pairs, "scale": scale,
            "distribution": observed,
            "all_good": masks.get((1 << m) - 1, 0)}


def header_from_pair(a, b, tables):
    """Construct the surjection used in the written proof."""
    _, mul, neg, inv = tables
    m = len(a)
    need(1 <= m <= 12 and len(b) == m and any(b), "pair dimensions")
    pivot = next(j for j in range(m) if b[j])
    rows = [tuple(a)]
    for i in range(m):
        if i != pivot:
            row = [int(i == j) for j in range(m)]
            row[pivot] = neg[mul[b[i]][inv[b[pivot]]]]
            rows.append(tuple(row))
    undo = inverse(rows, tables)
    need(undo is not None and tuple(row[0] for row in undo) == tuple(b),
         "constructed header has the prescribed inverse column")
    return rows, undo


def cover_witnesses(tables):
    witnesses = 0
    for q, m in product((2, 3, 4, 5), range(2, 13)):
        add, mul, neg, _ = tables[q]
        if q == 2 and m % 2 == 0:
            pairs = [((1,) * (m - 1) + (0,),) * 2,
                     ((0,) * (m - 1) + (1,),) * 2]
        else:
            b = [value for _ in range((m - 1) // 2) for value in (1, neg[1])]
            if m % 2:
                b.append(1)
            else:
                x = next(value for value in range(q) if value not in (0, 1))
                b.extend((x, add[1][neg[x]]))
            pairs = [((1,) * m, tuple(b))]
        union = 0
        for a, b in pairs:
            rows, undo = header_from_pair(a, b, tables[q])
            mask = sum(int(mul[rows[0][i]][undo[i][0]] != 0) << i for i in range(m))
            union |= mask
            witnesses += 1
        need(union == (1 << m) - 1, "complete one-or-two-header cover")
    return witnesses


def controls(tables):
    ternary = scalar_census(3, 2, tables[3])
    joint = Fraction(ternary[3], sum(ternary.values()))
    marginal = Fraction(sum(n for mask, n in ternary.items() if mask & 1), 24)
    need(joint == Fraction(1, 6) and joint != marginal ** 2,
         "independent-request shortcut must fail")
    binary = scalar_census(2, 4, tables[2])
    need(not any(mask.bit_count() % 2 == 0 for mask in binary), "binary parity support")
    singles = sum(n for mask, n in binary.items() if mask.bit_count() == 1)
    need(singles == 108 and singles != comb(4, 1), "zero products have three realizations")
    two = scalar_census(2, 2, tables[2])
    duplicate_good = sum(n for mask, n in two.items() if mask & 1)
    need(duplicate_good == 3 and two[3] == 0,
         "duplicated request violates the orthogonality premise")
    need(tables[4][1][2][2] != (2 * 2) % 4, "F4 cannot use Z/4 multiplication")
    corrupted = binary.copy()
    corrupted[1] += 1
    try:
        check_counts(2, 4, corrupted, 1)
    except ValueError as error:
        need(str(error) == "total count", "wrong rejection path")
    else:
        raise ValueError("one-count corruption was accepted")
    return 6


def scientific_result():
    tables = {q: field(q) for q in (2, 3, 4, 5)}
    pair_rows = []
    for q, m in PAIR_CASES:
        masks = scalar_census(q, m, tables[q])
        pair_rows.append(check_counts(q, m, masks, 1))
    header_rows = []
    for q, m in HEADER_CASES:
        masks, scale = header_census(q, m, tables[q])
        header_rows.append(check_counts(q, m, masks, scale))
    return {"scalar_cases": pair_rows, "header_cases": header_rows,
            "controls": controls(tables), "cover_witnesses": cover_witnesses(tables)}


def digest(path):
    need(path.is_file() and path.stat().st_size <= 1000000, "bounded regular input")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_hashes():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    live = [row for row in sources["files"] if row["usage"] == "input"]
    need(len(live) == 2, "exact source inventory")
    result = {}
    for row in live:
        value = digest(ROOT / row["path"])
        need(value == row["sha256"], "changed live source: " + row["path"])
        result[row["path"]] = value
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-receipt", type=Path,
                        help="create one new receipt outside the checkout")
    args = parser.parse_args()
    inputs = source_hashes()
    result = scientific_result()
    receipt = {"schema_version": 1, "claim_type": "scoped counting proof with finite corroboration",
               "inputs": inputs, "files": {name: digest(PACKAGE / name) for name in LOCAL_FILES},
               "result": result}
    if args.write_receipt:
        destination = args.write_receipt.resolve()
        need(not destination.is_relative_to(ROOT), "receipt output must be outside checkout")
        with destination.open("x", encoding="utf-8") as output:
            output.write(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    else:
        expected = json.loads((PACKAGE / "RESULT.json").read_text())
        need(receipt == expected, "receipt does not match exact bytes and recomputed counts")
    print("PASS_PROJECTOR_JOINT_HEADER_DENSITY " + json.dumps({
        "scalar_pairs": sum(row["pairs"] for row in result["scalar_cases"]),
        "headers": sum(row["pairs"] * row["scale"] for row in result["header_cases"]),
        "controls": result["controls"]}, sort_keys=True))


if __name__ == "__main__":
    main()
