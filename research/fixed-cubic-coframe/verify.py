#!/usr/bin/env python3
"""Exact finite corroboration of the fixed cubic coframe theorem. Apache-2.0."""

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
from itertools import combinations
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rank(rows, width):
    require(0 <= width <= 64 and len(rows) <= 64, "rank capacity")
    pivots = [0] * width
    count = 0
    for row in rows:
        require(type(row) is int and 0 <= row < 1 << width, "binary row")
        for bit in range(width - 1, -1, -1):
            if row >> bit & 1:
                if pivots[bit]:
                    row ^= pivots[bit]
                else:
                    pivots[bit] = row
                    count += 1
                    break
    return count


def omega(x, y, m):
    mask = (1 << m) - 1
    return (((x & mask) & (y >> m)).bit_count()
            + ((y & mask) & (x >> m)).bit_count()) % 2


def transport(v, m):
    mask = (1 << m) - 1
    x, z = v & mask, v >> m
    return z | ((x ^ z) << m)


def validate_chart(rows, m):
    require(type(m) is int and 1 <= m <= 32, "chart dimension")
    require(len(rows) == m and rank(rows, 2 * m) == m, "chart rank")
    require(all(omega(x, y, m) == 0 for x, y in combinations(rows, 2)),
            "chart isotropy")


def distances(rows, m):
    validate_chart(rows, m)
    boundary = [1 << (m + j) for j in range(m)]
    moved = [transport(v, m) for v in rows]
    return rank(rows + boundary, 2 * m) - m, rank(rows + moved, 2 * m) - m


def paired_chart(m, a):
    require(type(m) is int and 1 <= m <= 32, "chart dimension")
    require(type(a) is int and 0 <= a <= m // 2, "pair count")
    rows = []
    for j in range(a):
        pair = (1 << (2 * j)) | (1 << (2 * j + 1))
        rows.extend((pair, pair << m))
    rows.extend(1 << (m + j) for j in range(2 * a, m))
    validate_chart(rows, m)
    return rows


def candidates(m):
    require(type(m) is int and 1 <= m <= 4, "enumeration dimension")
    for pivots in combinations(range(2 * m), m):
        free = [(i, j) for i, p in enumerate(pivots)
                for j in range(p + 1, 2 * m) if j not in pivots]
        require(len(free) <= 16, "RREF capacity")
        for mask in range(1 << len(free)):
            rows = [1 << p for p in pivots]
            for bit, (i, j) in enumerate(free):
                if mask >> bit & 1:
                    rows[i] |= 1 << j
            yield rows


def points(rows):
    require(len(rows) <= 4, "literal-set capacity")
    values = {0}
    for row in rows:
        values |= {value ^ row for value in values}
    return values


def validate_pair(m, a, b):
    require(all(type(v) is int for v in (m, a, b)), "pair integer types")
    require(1 <= m <= 32 and 0 <= a <= m and 0 <= b <= m, "pair range")
    require(2 * a + b >= m, "boundary triangle bound")
    require((m - b) % 2 == 0, "cubic parity")


def tariff_checks(m, pairs):
    count = 0
    q, delta = divmod(m, 2)
    for quarter in range(1, 4 * m + 1):
        threshold = Fraction(quarter, 4)
        for k in (Fraction(1, 3), Fraction(1), Fraction(2), Fraction(7, 2), Fraction(8)):
            endpoint = min(k * min(m, threshold),
                           2 * min(q, threshold) + k * min(delta, threshold))
            actual = min(2 * min(a, threshold) + k * min(b, threshold)
                         for a, b in pairs)
            require(actual == endpoint, "exact concave tariff optimum")
            count += 1
    return count


def exhaustive():
    records = []
    tariff_count = 0
    for m in range(1, 5):
        histogram = Counter()
        for rows in candidates(m):
            if any(omega(x, y, m) for x, y in combinations(rows, 2)):
                continue
            a, b = distances(rows, m)
            values = points(rows)
            moved = {transport(v, m) for v in values}
            literal_a = m - (sum(v & ((1 << m) - 1) == 0 for v in values).bit_length() - 1)
            common = values & moved
            literal_b = m - (len(common).bit_length() - 1)
            require((a, b) == (literal_a, literal_b), "literal distances")
            require({transport(v, m) for v in common} == common,
                    "intersection is invariant")
            validate_pair(m, a, b)
            histogram[a, b] += 1
        expected = 1
        for j in range(1, m + 1):
            expected *= (1 << j) + 1
        require(sum(histogram.values()) == expected, "complete Lagrangian inventory")
        efficient = {(a, b) for a, b in histogram
                     if not any(c <= a and d <= b and (c, d) != (a, b)
                                for c, d in histogram)}
        require(efficient == {(a, m - 2 * a) for a in range(m // 2 + 1)},
                "exact Pareto frontier")
        tariff_count += tariff_checks(m, histogram)
        records.append({"m": m, "lagrangians": expected,
                        "rank_pairs": [[a, b, n] for (a, b), n in sorted(histogram.items())]})
    return records, tariff_count


def constructions():
    count = 0
    for m in range(1, 33):
        for a in range(m // 2 + 1):
            rows = paired_chart(m, a)
            require(distances(rows, m) == (a, m - 2 * a), "attaining chart")
            count += 1
    return count


def gadd(x, y):
    return x[0] + y[0], x[1] + y[1]


def gmul(x, y):
    return x[0] * y[0] - x[1] * y[1], x[0] * y[1] + x[1] * y[0]


def gaussian(real, imag=0):
    return Fraction(real), Fraction(imag)


def multiply(a, b):
    n = len(a)
    require(n in (2, 4) and len(b) == n, "matrix capacity")
    require(all(len(row) == n for row in a + b), "square matrices")
    result = [[gaussian(0) for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            for k in range(n):
                result[i][j] = gadd(result[i][j], gmul(a[i][k], b[k][j]))
    return result


def adjoint(a):
    return [[(a[j][i][0], -a[j][i][1]) for j in range(len(a))]
            for i in range(len(a))]


def tensor(a, b):
    require(len(a) == len(b) == 2, "two-plane tensor capacity")
    return [[gmul(a[i // 2][j // 2], b[i % 2][j % 2]) for j in range(4)]
            for i in range(4)]


def identity(n):
    require(n in (2, 4), "identity capacity")
    return [[gaussian(i == j) for j in range(n)] for i in range(n)]


def column_supports(a):
    return [sum(a[i][j] != gaussian(0) for i in range(len(a)))
            for j in range(len(a))]


def native_fixture():
    h = [[gaussian(Fraction(1, 2), Fraction(1, 2)) for _ in range(2)]
         for _ in range(2)]
    h[1][1] = gaussian(Fraction(-1, 2), Fraction(-1, 2))
    phase = [[gaussian(-1), gaussian(0)], [gaussian(0), gaussian(0, -1)]]
    u = multiply(phase, h)
    x = [[gaussian(0), gaussian(1)], [gaussian(1), gaussian(0)]]
    z = [[gaussian(1), gaussian(0)], [gaussian(0), gaussian(-1)]]
    y = [[gaussian(0), gaussian(0, -1)], [gaussian(0, 1), gaussian(0)]]
    require(multiply(adjoint(u), u) == identity(2), "native unitarity")
    require(multiply(multiply(u, u), u) == identity(2), "actual cubic order")
    require(multiply(multiply(u, x), adjoint(u)) == z, "native X image")
    require(multiply(multiply(u, z), adjoint(u)) == y, "native Z image")
    cnot = [[gaussian(0) for _ in range(4)] for _ in range(4)]
    for j in range(4):
        cnot[j ^ ((j >> 1) & 1)][j] = gaussian(1)
    bell = multiply(cnot, tensor(h, identity(2)))
    doubled = tensor(u, u)
    changed = multiply(multiply(adjoint(bell), doubled), bell)
    require(multiply(adjoint(bell), bell) == identity(4), "Bell unitarity")
    require(column_supports(doubled) == [4] * 4, "baseline native rank two")
    require(column_supports(bell) == [2] * 4, "Bell boundary rank one")
    require(column_supports(changed) == [1] * 4, "changed native rank zero")
    require(multiply(multiply(bell, changed), adjoint(bell)) == doubled,
            "complete arbitrary-input forward identity")
    require(multiply(multiply(bell, adjoint(changed)), adjoint(bell)) == adjoint(doubled),
            "complete arbitrary-input inverse identity")
    require(multiply(bell, changed) != doubled, "missing exit control")
    encoded = [[[str(x), str(y)] for x, y in row] for row in changed]
    return {"conjugated_matrix": encoded, "forward_basis_columns": 4,
            "inverse_basis_columns": 4, "paid_boundary_ranks": [1, 1],
            "old_internal_rank": 2, "new_internal_rank": 0}


def controls():
    invalid_pairs = [(0, 0, 0), (33, 0, 0), (2, -1, 2), (2, 3, 0),
                     (2, 0, 0), (3, 1, 0), (2, 1, 1), (True, 0, 1)]
    rejected = 0
    for args in invalid_pairs:
        try:
            validate_pair(*args)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid rank pair accepted")
    for m, rows in ((0, []), (2, [1, 1]), (2, [1, 4]), (33, [])):
        try:
            validate_chart(rows, m)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid chart accepted")
    require(distances(paired_chart(2, 1), 2) == (1, 0), "coupling witness")
    require(all(distances(rows, 1)[1] == 1 for rows in ([1], [2], [3])),
            "one-copy obstruction")
    return rejected


def result():
    inventories, tariffs = exhaustive()
    evidence = {"schema_version": 1, "inventories": inventories,
                "lagrangians": sum(r["lagrangians"] for r in inventories),
                "concave_tariff_checks": tariffs, "constructions": constructions(),
                "rejections": controls(), "native": native_fixture()}
    root = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    evidence["source_sha256"] = {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
                                 for name in names}
    return evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-receipt", type=Path)
    args = parser.parse_args()
    evidence = result()
    rendered = json.dumps(evidence, indent=2, sort_keys=True) + "\n"
    root = Path(__file__).resolve().parent
    if args.write_receipt:
        require(not args.write_receipt.resolve().is_relative_to(root),
                "generate the receipt outside the package")
        args.write_receipt.write_text(rendered, encoding="utf-8")
    else:
        saved = json.loads((root / "RESULT.json").read_text(encoding="utf-8"))
        require(json.dumps(saved, sort_keys=True) == json.dumps(evidence, sort_keys=True),
                "generated evidence or source hashes differ from RESULT.json")
    print("PASS_FIXED_CUBIC_COFRAME", "lagrangians=" + str(evidence["lagrangians"]),
          "constructions=" + str(evidence["constructions"]),
          "concave_tariffs=" + str(evidence["concave_tariff_checks"]),
          "rejections=" + str(evidence["rejections"]))


if __name__ == "__main__":
    main()
