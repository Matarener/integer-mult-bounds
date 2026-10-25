"""Reconstruct the witness directly from literal rows. Apache-2.0.

Shares source authentication and JSON reading, but imports no geometry,
primary support-rank, determinant or witness-checking implementation.
"""

from fractions import Fraction
from itertools import combinations, product

import common


def literal_model():
    raw = common.authenticated_inputs()[common.DATA].decode().splitlines()
    labels = tuple(map(int, raw[0].split()))
    live = tuple(tuple(map(int, row.split())) for row in raw[2:114])
    common.require(
        len(labels) == len(set(labels)) == len(live) == 112, "literal model inventory"
    )
    roots, frame = set(), set()
    for i, j in combinations(range(8), 2):
        for sign in (-2, 2):
            row = tuple(2 if k == i else sign if k == j else 0 for k in range(8))
            roots.add(max(row, tuple(-x for x in row)))
            if i % 2 == 0 and j == i + 1:
                frame.add(max(row, tuple(-x for x in row)))
    for row in product((-1, 1), repeat=8):
        if row.count(-1) % 2 == 0:
            roots.add(max(row, tuple(-x for x in row)))
    common.require(
        len(roots) == 120 and len(frame) == 8 and tuple(sorted(roots - frame)) == live,
        "separate root reconstruction",
    )
    return tuple(sorted(roots)), live, labels


def binary_rank(values):
    rows = [0] * 9
    for item in values:
        value = item
        for bit in range(9):
            if value >> bit & 1:
                if rows[bit]:
                    value ^= rows[bit]
                else:
                    rows[bit] = value
                    break
    return sum(x != 0 for x in rows)


def rational_rank(matrix):
    width = len(matrix[0])
    common.require(len(matrix) == 112 and width in (4, 8, 12), "rational rank domain")
    basis = {}
    for original in matrix:
        row = [Fraction(x) for x in original]
        common.require(len(row) == width, "rank row width")
        for pivot in range(width):
            if not row[pivot]:
                continue
            if pivot in basis:
                scale = row[pivot]
                row = [a - scale * b for a, b in zip(row, basis[pivot], strict=True)]
            else:
                scale = row[pivot]
                basis[pivot] = tuple(x / scale for x in row)
                break
    return len(basis)


def bareiss(matrix):
    rows = [row[:] for row in matrix]
    common.require(
        len(rows) == 11 and all(len(row) == 11 for row in rows),
        "Bareiss minor dimensions",
    )
    sign, previous = 1, 1
    for k in range(10):
        pivot = next((i for i in range(k, 11) if rows[i][k]), None)
        if pivot is None:
            return 0
        if pivot != k:
            rows[k], rows[pivot] = rows[pivot], rows[k]
            sign = -sign
        entry = rows[k][k]
        for i in range(k + 1, 11):
            for j in range(k + 1, 11):
                value = rows[i][j] * entry - rows[i][k] * rows[k][j]
                common.require(value % previous == 0, "Bareiss exact division")
                rows[i][j] = value // previous
            rows[i][k] = 0
        previous = entry
    return sign * rows[10][10]


def piece_columns(data, roots, live, labels):
    columns, ranks, sizes, multiplicity = [], [], [], [0] * 112
    for piece in data["pieces"]:
        indices = piece["live_indices"]
        common.require(
            0 < len(indices) <= 20
            and indices == sorted(set(indices))
            and all(type(i) is int and 0 <= i < 112 for i in indices),
            "independent index domain",
        )
        common.require(
            len(piece["values"]) == len(indices)
            and all(type(v) is int and abs(v) == 1 for v in piece["values"]),
            "independent value domain",
        )
        common.require(
            piece["labels"] == [labels[i] for i in indices],
            "independent literal labels",
        )
        mask = sum(1 << roots.index(live[i]) for i in indices)
        common.require(
            piece["full_root_mask"] == f"{mask:030x}", "independent mask binding"
        )
        column = [0] * 112
        for i, value in zip(indices, piece["values"], strict=True):
            column[i] = value
            multiplicity[i] += 1
        ranks.append(binary_rank(labels[i] for i in indices))
        sizes.append(len(indices))
        columns.append(column)
    common.require(
        ranks == [4, 5, 6, 6] and sizes == [6, 12, 20, 18],
        "independent support profile",
    )
    common.require(
        max(multiplicity) == 1 and sum(multiplicity) == 56,
        "independent disjoint support",
    )
    return columns


def check(data):
    roots, live, labels = literal_model()
    common.require(
        data["normal_numerator"] == [0, 0, 0, 0, 0, 0, 2, -2]
        and data["normal_denominator"] == 4,
        "literal independent normal",
    )
    common.require(
        data["schema_version"] == 1
        and len(data["pieces"]) == 4
        and data["piece_coefficients"] == [1, 1, 1, 1],
        "independent schema",
    )
    columns = piece_columns(data, roots, live, labels)
    matrix = [
        list(root) + [column[i] for column in columns] for i, root in enumerate(live)
    ]
    common.require(
        all(2 * sum(row[8:]) == row[6] - row[7] for row in matrix),
        "independent coefficient identity",
    )
    common.require(
        [
            rational_rank([row[:8] for row in matrix]),
            rational_rank([row[8:] for row in matrix]),
            rational_rank(matrix),
        ]
        == [8, 4, 11],
        "independent rational ranks",
    )
    minor = data["joint_rank_minor"]
    det = bareiss(
        [[matrix[i][j] for j in minor["columns"]] for i in minor["live_rows"]]
    )
    common.require(det == minor["determinant"] == -512, "independent exact minor")


def main():
    check(common.read_json(common.HERE / "WITNESS.json"))
    print("PASS_P112_RANK4_COUNTEREXAMPLE_INDEPENDENT identities=112 ranks=8,4,11")


if __name__ == "__main__":
    main()
