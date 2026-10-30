"""Check the literal P112 rank-4,5,6,6 counterexample. Apache-2.0."""

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

import common


def determinant(matrix):
    size = len(matrix)
    common.require(
        1 <= size <= 12 and all(len(r) == size for r in matrix), "determinant dimension"
    )
    rows, result = [[Fraction(x) for x in r] for r in matrix], Fraction(1)
    for column in range(size):
        pivot = next((i for i in range(column, size) if rows[i][column]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            rows[column], rows[pivot] = rows[pivot], rows[column]
            result = -result
        entry = rows[column][column]
        result *= entry
        for i in range(column + 1, size):
            scale = rows[i][column] / entry
            rows[i] = [
                a - scale * b for a, b in zip(rows[i], rows[column], strict=True)
            ]
    return result


def piece_columns(data, roots, live, labels):
    common.require(len(data["pieces"]) == 4, "four pieces")
    columns, occupied, ranks, sizes = [], set(), [], []
    for piece in data["pieces"]:
        indices, values = piece["live_indices"], piece["values"]
        common.require(
            0 < len(indices) <= 20 and len(indices) == len(values),
            "piece size/value shape",
        )
        common.require(
            all(type(i) is int and 0 <= i < 112 for i in indices)
            and indices == sorted(set(indices)),
            "live indices",
        )
        common.require(
            all(type(v) is int and abs(v) == 1 for v in values),
            "literal nonzero coefficients",
        )
        common.require(not occupied.intersection(indices), "disjoint pieces")
        occupied.update(indices)
        actual_labels = [labels[roots.index(live[i])] for i in indices]
        common.require(piece["labels"] == actual_labels, "literal labels")
        mask = sum(1 << roots.index(live[i]) for i in indices)
        common.require(piece["full_root_mask"] == f"{mask:030x}", "root-mask binding")
        basis = piece["binary_basis"]
        common.require(
            len(basis) <= 6 and all(type(v) is int and 0 < v < 512 for v in basis),
            "binary basis domain",
        )
        span = {0}
        for row in basis:
            span |= {v ^ row for v in tuple(span)}
        rank = common.rank_labels(actual_labels)
        common.require(
            rank == len(basis) == common.rank_labels(basis)
            and all(v in span for v in actual_labels),
            "binary support basis",
        )
        column = [0] * 112
        for i, value in zip(indices, values, strict=True):
            column[i] = value
        columns.append(column)
        ranks.append(rank)
        sizes.append(len(indices))
    common.require(
        ranks == [4, 5, 6, 6] and sizes == [6, 12, 20, 18], "claimed rank/size profile"
    )
    return columns, occupied


def check(data, model):
    g, roots, live, labels, _ = model
    common.require(data["schema_version"] == 1, "witness schema")
    normal = tuple(data["normal_numerator"])
    denominator = data["normal_denominator"]
    common.require(
        normal == (0, 0, 0, 0, 0, 0, 2, -2) and denominator == 4, "literal frame normal"
    )
    common.require(normal in roots and normal not in live, "removed-frame membership")
    common.require(data["piece_coefficients"] == [1, 1, 1, 1], "piece combination")
    columns, occupied = piece_columns(data, roots, live, labels)
    for i, root in enumerate(live):
        value = Fraction(g.dot(root, normal), denominator)
        common.require(sum(c[i] for c in columns) == value, "literal codeword identity")
        common.require((i in occupied) == bool(value), "exact root-word support")
    common.require(len(occupied) == 56, "frame-word support")
    matrix = [list(root) + [c[i] for c in columns] for i, root in enumerate(live)]
    # Exact nonzero 11-minor supplies the lower bound; this relation supplies upper.
    common.require(
        all(row[6] - row[7] == 2 * sum(row[8:]) for row in matrix),
        "joint rank upper relation",
    )
    minor = data["joint_rank_minor"]
    row_ids, cols = minor["live_rows"], minor["columns"]
    common.require(
        len(row_ids) == len(set(row_ids)) == 11
        and all(type(i) is int and 0 <= i < 112 for i in row_ids),
        "minor rows",
    )
    common.require(
        len(cols) == len(set(cols)) == 11
        and all(type(i) is int and 0 <= i < 12 for i in cols),
        "minor columns",
    )
    det = determinant([[matrix[i][j] for j in cols] for i in row_ids])
    common.require(
        type(minor["determinant"]) is int and det == minor["determinant"] and det != 0,
        "nonzero joint rank minor",
    )
    return {
        "schema_version": 1,
        "piece_ranks": [4, 5, 6, 6],
        "piece_sizes": [6, 12, 20, 18],
        "normal_type": "removed-frame root",
        "support_size": 56,
        "coefficient_values": [-1, 1],
        "code_rank": 8,
        "piece_rank": 4,
        "joint_rank": 11,
        "intersection_dimension": 1,
        "joint_minor_determinant": int(det),
        "coefficient_identities": 112,
        "standard_weyl_premise_required": False,
        "new_kappa": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--witness", type=Path, default=common.HERE / "WITNESS.json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    data = common.read_json(args.witness)
    observed = check(data, common.model())
    observed["witness_sha256"] = hashlib.sha256(args.witness.read_bytes()).hexdigest()
    if args.output:
        with args.output.open("x") as stream:
            stream.write(json.dumps(observed, indent=2) + "\n")
    else:
        common.require(
            common.same_json(observed, common.read_json(common.HERE / "RESULT.json")),
            "result receipt mismatch",
        )
    print("PASS_P112_RANK4_COUNTEREXAMPLE")


if __name__ == "__main__":
    main()
