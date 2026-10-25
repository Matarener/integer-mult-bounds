"""Exact common-cut36 counterexample for the P112 mixed566 predicate. Apache-2.0."""

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from types import ModuleType

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GEOMETRY = "research/p112-root-simplex-exclusion/geometry.py"
GEOMETRY_SHA = "b8ac379e41f5ad83bdb6c7f7c55129fc3d9c07801ea61591478f25d72ff0b021"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    require(path.is_file() and not path.is_symlink(), "regular JSON input")
    raw = path.read_bytes()
    require(len(raw) <= 200_000, "JSON size bound")
    return json.loads(raw)


def model(root=ROOT):
    source = root / GEOMETRY
    require(source.is_file() and not source.is_symlink(), "regular geometry input")
    raw = source.read_bytes()
    require(len(raw) < 100_000, "geometry byte bound")
    require(hashlib.sha256(raw).hexdigest() == GEOMETRY_SHA, "geometry SHA256")
    manifest = read_json(HERE / "SOURCES.json")
    inputs = [row for row in manifest["files"] if row["usage"] == "input"]
    require(len(inputs) == 1, "one live geometry input")
    require(inputs[0]["path"] == GEOMETRY, "geometry path")
    require(inputs[0]["sha256"] == GEOMETRY_SHA, "geometry manifest digest")
    module = ModuleType("authenticated_geometry")
    exec(compile(raw, GEOMETRY, "exec"), module.__dict__)  # noqa: S102 - pinned bytes
    roots, points, _, coordinates = module.root_data()
    labels = tuple(
        1 | sum((int(x) % 2) << (j + 1) for j, x in enumerate(c)) for c in coordinates
    )
    require(len(roots) == len(set(labels)) == 120, "full root/label bijection")
    live = tuple(i for i, r in enumerate(roots) if r in points)
    require(len(live) == 112, "P112 inventory")
    return roots, labels, live


def binary_rank(values):
    require(len(values) <= 120, "binary input size")
    pivots = [0] * 9
    for value in values:
        require(type(value) is int and 0 <= value < 512, "nine-bit label")
        for bit in range(8, -1, -1):
            if value >> bit & 1:
                if pivots[bit]:
                    value ^= pivots[bit]
                else:
                    pivots[bit] = value
                    break
    return sum(bool(value) for value in pivots)


def rational_rank(matrix):
    require(1 <= len(matrix) <= 120, "matrix row bound")
    width = len(matrix[0])
    require(1 <= width <= 11 and all(len(r) == width for r in matrix), "matrix shape")
    rows = [[Fraction(x) for x in row] for row in matrix]
    rank = 0
    for column in range(width):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][column]
        rows[rank] = [x / scale for x in rows[rank]]
        for i in range(rank + 1, len(rows)):
            scale = rows[i][column]
            rows[i] = [x - scale * y for x, y in zip(rows[i], rows[rank], strict=True)]
        rank += 1
    return rank


def indices(value, maximum, message):
    require(isinstance(value, list) and len(value) <= maximum, message)
    require(all(type(i) is int and 0 <= i < 120 for i in value), message)
    require(value == sorted(set(value)), message)
    return set(value)


def parse_witness(witness, live):
    require(isinstance(witness, dict), "witness object")
    require(
        set(witness)
        == {"schema_version", "normal_full_indices", "cut_full_indices", "pieces"},
        "witness fields",
    )
    require(
        type(witness["schema_version"]) is int and witness["schema_version"] == 1,
        "witness version",
    )
    normals = witness["normal_full_indices"]
    require(isinstance(normals, list) and len(normals) == 2, "two normals")
    require(all(type(i) is int and 0 <= i < 120 for i in normals), "normal indices")
    require(normals[0] != normals[1], "distinct normals")
    cut = indices(witness["cut_full_indices"], 36, "common cut")
    require(len(cut) == 36 and cut <= set(live), "36 live cut sites")
    pieces = witness["pieces"]
    require(isinstance(pieces, list) and len(pieces) == 3, "three pieces")
    for piece, size in zip(pieces, (10, 16, 16), strict=True):
        require(
            isinstance(piece, dict)
            and set(piece) == {"support_full_indices", "values", "coefficient_column"},
            "piece fields",
        )
        support = indices(piece["support_full_indices"], size, "piece support")
        require(
            len(support) == size and support <= set(live) - cut, "live residual support"
        )
        values, column = piece["values"], piece["coefficient_column"]
        require(isinstance(values, list) and len(values) == size, "piece value count")
        require(
            all(type(x) is int and 0 < abs(x) <= 8 for x in values),
            "nonzero exact piece values",
        )
        require(isinstance(column, list) and len(column) == 2, "coefficient column")
        require(
            all(type(x) is int and abs(x) <= 1 for x in column) and any(column),
            "exact coefficient column",
        )
    return normals, cut, pieces


def verify(witness, root=ROOT):
    roots, labels, live = model(root)
    normals, cut, pieces = parse_witness(witness, live)
    q = [
        {
            i: value
            for i, value in zip(p["support_full_indices"], p["values"], strict=True)
        }
        for p in pieces
    ]
    ranks = [binary_rank([labels[i] for i in v]) for v in q]
    require(ranks == [5, 6, 6], "binary support ranks 5,6,6")
    require(
        all(not set(q[i]) & set(q[j]) for i in range(3) for j in range(i)),
        "disjoint support",
    )
    evaluation = [
        tuple(sum(x * y for x, y in zip(r, roots[n], strict=True)) for n in normals)
        for r in roots
    ]
    union = {i for i in live if any(evaluation[i])}
    retained = set().union(*(set(v) for v in q))
    require(
        len(union) == 78 and union - cut == retained, "78 minus 36 equals retained42"
    )
    for i in set(live) - cut:
        actual = tuple(
            sum(
                p["coefficient_column"][j] * v.get(i, 0)
                for p, v in zip(pieces, q, strict=True)
            )
            for j in range(2)
        )
        require(actual == evaluation[i], "two exact restricted codeword identities")
    retained_rows = [i for i in live if i not in cut]
    code = [list(roots[i]) for i in retained_rows]
    piece_matrix = [[v.get(i, 0) for v in q] for i in retained_rows]
    joint = [a + b for a, b in zip(code, piece_matrix, strict=True)]
    dimensions = [rational_rank(m) for m in (code, piece_matrix, joint)]
    require(dimensions == [8, 3, 9], "exact code/piece/joint ranks")
    return {
        "status": "PASS_P112_MIXED566_CUT36_COUNTEREXAMPLE",
        "cut_size": len(cut),
        "live_union_size": len(union),
        "support_sizes": [len(v) for v in q],
        "binary_support_ranks": ranks,
        "retained_coordinates": len(retained_rows),
        "retained_nonzero_union": len(retained),
        "code_piece_joint_ranks": dimensions,
        "intersection_dimension": dimensions[0] + dimensions[1] - dimensions[2],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--witness", type=Path, default=HERE / "WITNESS.json")
    args = parser.parse_args()
    result = verify(read_json(args.witness))
    require(result == read_json(HERE / "RESULT.json"), "exact result receipt")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
