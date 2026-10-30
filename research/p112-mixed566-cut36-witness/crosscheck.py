"""Separate root/label and coefficient-constraint reconstruction. Apache-2.0."""

import hashlib
import json
from fractions import Fraction
from itertools import combinations, product
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent


def check(condition, message):
    if not condition:
        raise ValueError(message)


def reconstructed_roots():
    roots = set()
    for occupied in combinations(range(8), 2):
        for negative in (False, True):
            vector = tuple(
                2
                if i == occupied[0]
                else (-2 if negative else 2)
                if i == occupied[1]
                else 0
                for i in range(8)
            )
            roots.add(vector)
    for signs in product((1, -1), repeat=7):
        vector = (1,) + signs
        if vector.count(-1) % 2 == 0:
            roots.add(vector)
    check(len(roots) == 120, "independent full-root inventory")
    return sorted(roots)


def inverse_simple_matrix():
    simple = (
        (1, -1, -1, -1, -1, -1, -1, 1),
        (2, 2, 0, 0, 0, 0, 0, 0),
        (-2, 2, 0, 0, 0, 0, 0, 0),
        (0, -2, 2, 0, 0, 0, 0, 0),
        (0, 0, -2, 2, 0, 0, 0, 0),
        (0, 0, 0, -2, 2, 0, 0, 0),
        (0, 0, 0, 0, -2, 2, 0, 0),
        (0, 0, 0, 0, 0, -2, 2, 0),
    )
    rows = [
        [Fraction(simple[j][i]) for j in range(8)]
        + [Fraction(i == j) for j in range(8)]
        for i in range(8)
    ]
    for column in range(8):
        pivot = next(i for i in range(column, 8) if rows[i][column])
        rows[column], rows[pivot] = rows[pivot], rows[column]
        scale = rows[column][column]
        rows[column] = [x / scale for x in rows[column]]
        for i in range(8):
            if i != column:
                scale = rows[i][column]
                rows[i] = [
                    x - scale * y for x, y in zip(rows[i], rows[column], strict=True)
                ]
    return [row[8:] for row in rows]


def binary_dimension(values):
    span = {0}
    for value in values:
        span.update(x ^ value for x in tuple(span))
    check(len(span) <= 512 and len(span).bit_count() == 1, "binary span cardinality")
    return len(span).bit_length() - 1


def integer_rank(matrix):
    check(
        1 <= len(matrix) <= 120 and all(len(r) == 8 for r in matrix),
        "constraint matrix shape",
    )
    pivots = {}
    for original in matrix:
        row = list(original)
        for column in range(8):
            if not row[column]:
                continue
            if column not in pivots:
                divisor = gcd(*row)
                pivots[column] = [x // divisor for x in row]
                break
            pivot = pivots[column]
            row = [
                pivot[column] * x - row[column] * y
                for x, y in zip(row, pivot, strict=True)
            ]
            divisor = gcd(*row)
            if divisor:
                row = [x // divisor for x in row]
    return len(pivots)


def independent_model():
    roots = reconstructed_roots()
    inverse = inverse_simple_matrix()
    labels = []
    for root in roots:
        coordinates = [
            sum(x * y for x, y in zip(row, root, strict=True)) for row in inverse
        ]
        check(
            all(x.denominator == 1 for x in coordinates),
            "integral independent coordinates",
        )
        labels.append(1 + 2 * sum((int(x) % 2) << j for j, x in enumerate(coordinates)))
    frame = {
        tuple(2 if j == i else sign if j == i + 1 else 0 for j in range(8))
        for i in (0, 2, 4, 6)
        for sign in (-2, 2)
    }
    live = {i for i, root in enumerate(roots) if root not in frame}
    return roots, labels, live


def main():
    path = HERE / "WITNESS.json"
    check(path.is_file() and not path.is_symlink(), "regular witness input")
    raw = path.read_bytes()
    check(len(raw) <= 200_000, "witness byte bound")
    witness = json.loads(raw)
    roots, labels, live = independent_model()
    cut = set(witness["cut_full_indices"])
    check(len(live) == 112 and len(cut) == 36 and cut <= live, "independent live cut")
    pieces = witness["pieces"]
    supports = [set(piece["support_full_indices"]) for piece in pieces]
    check([len(s) for s in supports] == [10, 16, 16], "independent support sizes")
    check(all(s <= live - cut for s in supports), "independent residual membership")
    check(
        all(not a & b for a, b in combinations(supports, 2)), "independent disjointness"
    )
    check(
        [binary_dimension([labels[i] for i in s]) for s in supports] == [5, 6, 6],
        "independent binary dimensions",
    )
    q = [dict(zip(p["support_full_indices"], p["values"], strict=True)) for p in pieces]
    normals = [roots[i] for i in witness["normal_full_indices"]]
    for i in live - cut:
        for j in range(2):
            evaluation = sum(x * y for x, y in zip(roots[i], normals[j], strict=True))
            check(
                evaluation
                == sum(
                    p["coefficient_column"][j] * v.get(i, 0)
                    for p, v in zip(pieces, q, strict=True)
                ),
                "independent coefficient identity",
            )
    constraints = [list(roots[i]) for i in sorted(live - cut - set().union(*supports))]
    for values in q:
        anchor = min(values)
        for i in sorted(set(values) - {anchor}):
            constraints.append(
                [
                    values[anchor] * x - values[i] * y
                    for x, y in zip(roots[i], roots[anchor], strict=True)
                ]
            )
    check(integer_rank([roots[i] for i in live - cut]) == 8, "injective retained code")
    check(
        integer_rank(constraints) == 6,
        "eight minus six gives exactly two-dimensional intersection",
    )
    receipt = {
        "status": "PASS_SEPARATE_COEFFICIENT_CONSTRAINT_CHECK",
        "constraint_rows": len(constraints),
        "constraint_rank": 6,
        "intersection_dimension": 2,
        "witness_sha256": hashlib.sha256(
            (HERE / "WITNESS.json").read_bytes()
        ).hexdigest(),
    }
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
