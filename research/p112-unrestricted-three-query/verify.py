"""Support domination for unrestricted three-query replacements. Apache-2.0."""

import argparse
import itertools
import json
from fractions import Fraction as F
from hashlib import sha1, sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT = "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"
GRID = ((0, 0), (0, -1), (-1, 0), (-1, -1))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read(path, limit=1_048_576):
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    need(len(raw) <= limit, "input capacity")
    return raw


def authenticate(raw, pin):
    need(sha256(raw).hexdigest() == pin["sha256"], "source SHA256")
    header = b"blob " + str(len(raw)).encode() + b"\0"
    need(
        sha1(header + raw, usedforsecurity=False).hexdigest() == pin["git_blob"],
        "source Git blob",
    )


def load():
    meta = json.loads(read(HERE / "SOURCES.json", 32768))
    pins = [row for row in meta["files"] if row["usage"] == "input"]
    need(len(pins) == 1 and pins[0]["path"] == INPUT, "source inventory")
    raw = read(ROOT / INPUT)
    authenticate(raw, pins[0])
    recipes = json.loads(raw)["recipes"]
    need(type(recipes) is list and len(recipes) == 112, "112 recipes")
    need(all(type(row["port"]) is int for row in recipes), "integer ports")
    need(sorted(row["port"] for row in recipes) == list(range(112)), "port IDs")
    labels = [row["q"] for row in sorted(recipes, key=lambda row: row["port"])]
    need(all(type(q) is int and 0 < q < 512 for q in labels), "nine-bit labels")
    need(len(set(labels)) == 112, "distinct labels")
    raw = read(HERE / "RETAINED-RANK32.json", 32768)
    authenticate(raw, meta["retained_rank32"])
    groups = json.loads(raw)["orthonormal_groups"]
    need(type(groups) is list and len(groups) == 16, "sixteen groups")
    need(all(type(g) is list and len(g) in (4, 6, 8) for g in groups), "groups")
    need(all(type(p) is int for g in groups for p in g), "integer group ports")
    need(sorted(p for g in groups for p in g) == list(range(112)), "partition")
    for group in groups:
        need(
            all(
                (labels[p] & labels[q]).bit_count() % 2 == int(p == q)
                for p in group
                for q in group
            ),
            "orthonormal group",
        )
    return labels, groups


def determinant(matrix):
    need(len(matrix) == 3 and all(len(row) == 3 for row in matrix), "3x3 matrix")
    a, b, c = matrix
    return (
        a[0] * (b[1] * c[2] - b[2] * c[1])
        - a[1] * (b[0] * c[2] - b[2] * c[0])
        + a[2] * (b[0] * c[1] - b[1] * c[0])
    )


def inverse(matrix):
    divisor = determinant(matrix)
    need(divisor != 0, "singular basis")
    result = []
    for i in range(3):
        row = []
        for j in range(3):
            rr = [k for k in range(3) if k != j]
            cc = [k for k in range(3) if k != i]
            minor = matrix[rr[0]][cc[0]] * matrix[rr[1]][cc[1]]
            minor -= matrix[rr[0]][cc[1]] * matrix[rr[1]][cc[0]]
            row.append(F((-1) ** (i + j) * minor, divisor))
        result.append(row)
    need(
        all(
            sum(result[i][k] * matrix[k][j] for k in range(3)) == int(i == j)
            for i in range(3)
            for j in range(3)
        ),
        "inverse identity",
    )
    return result


def compatible(points, candidate):
    return all(
        points[i][axis] != points[j][axis] or candidate[i][axis] == candidate[j][axis]
        for axis in range(2)
        for i, j in ((0, 1), (0, 2), (1, 2))
    )


def triangle(points):
    need(len(points) == 3 and all(len(p) == 2 for p in points), "three points")
    need(determinant([(*p, 1) for p in points]) != 0, "collinear points")
    for candidate in itertools.permutations(GRID, 3):
        if compatible(points, candidate):
            need(abs(determinant([(*p, 1) for p in candidate])) == 1, "unimodular")
            return candidate
    raise ValueError("no support-dominating triangle")


def classify():
    partitions = ((0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 1, 2))
    records = []
    for x, y in itertools.product(partitions, repeat=2):
        points = tuple(zip(x, y, strict=True))
        if len(set(points)) < 3:
            continue
        # Only the equality pattern matters, not collinearity of representatives.
        witnesses = [
            c for c in itertools.permutations(GRID, 3) if compatible(points, c)
        ]
        need(bool(witnesses), "equality-pattern witness")
        for candidate in witnesses:
            need(abs(determinant([(*p, 1) for p in candidate])) == 1, "grid rank")
            for axis in range(2):
                for value in {p[axis] for p in points}:
                    old_zero = [i for i in range(3) if points[i][axis] == value]
                    new_seed = -candidate[old_zero[0]][axis]
                    need(
                        all(new_seed + candidate[i][axis] == 0 for i in old_zero),
                        "all old query zeros retained",
                    )
        records.append({"x": list(x), "y": list(y), "witnesses": len(witnesses)})
    need(len(records) == 13, "thirteen equality classes")
    return records


def factors(a, b, seed, matrix):
    need(len(a) == len(b) == len(seed) == 112, "factor capacity")
    need(all(v in (0, 1) for v in a + b), "binary indicators")
    need(all(not (x and y) for x, y in zip(a, b, strict=True)), "disjoint indicators")
    inv = inverse(matrix)
    queries = [
        [
            matrix[i][0] * a[p] + matrix[i][1] * b[p] + matrix[i][2] * seed[p]
            for p in range(112)
        ]
        for i in range(3)
    ]
    readers = [
        [inv[0][i] * a[p] + inv[1][i] * b[p] for p in range(112)] for i in range(3)
    ]
    return queries, readers


def replace(a, b, seed, matrix):
    need(all(row[2] != 0 for row in matrix), "three nonzero seed coefficients")
    normalized = [[F(v, row[2]) for v in row] for row in matrix]
    chosen = triangle([row[:2] for row in normalized])
    queries, readers = factors(a, b, seed, normalized)
    new_seed = []
    for p in range(112):
        zeros = [i for i in range(3) if queries[i][p] == 0]
        if not zeros or not (a[p] or b[p]):
            new_seed.append(0)
        else:
            axis = 0 if a[p] else 1
            new_seed.append(-chosen[zeros[0]][axis])
    new_queries, new_readers = factors(a, b, new_seed, [[*p, 1] for p in chosen])
    for old, new in ((queries, new_queries), (readers, new_readers)):
        need(
            all(old[i][p] != 0 or new[i][p] == 0 for i in range(3) for p in range(112)),
            "support containment",
        )
    need(
        all(v.denominator == 1 for row in new_readers for v in row), "integral readers"
    )
    return new_queries, new_readers


def binary_rank(rows, width):
    need(len(rows) <= 224 and 0 <= width <= 224, "rank capacity")
    pivots = [0] * width
    for row in rows:
        need(type(row) is int and 0 <= row < 1 << width, "binary row")
        for bit in range(width - 1, -1, -1):
            if row >> bit & 1:
                if pivots[bit]:
                    row ^= pivots[bit]
                else:
                    pivots[bit] = row
                    break
    return sum(bool(p) for p in pivots)


def closure(vector, owners):
    return sorted({q for p, value in enumerate(vector) if value for q in owners[p]})


def bill(labels, owners, queries, readers):
    total = 0
    for query, reader in zip(queries, readers, strict=True):
        source, target = closure(query, owners), closure(reader, owners)
        rows = [
            sum(
                ((labels[p] & labels[q]).bit_count() % 2) << j
                for j, q in enumerate(target)
            )
            for p in source
        ]
        total += binary_rank(rows, len(target))
    return total


def identity(a, b, queries, readers):
    need(
        all(
            sum(readers[i][p] * queries[i][q] for i in range(3))
            == a[p] * a[q] + b[p] * b[q]
            for p in range(112)
            for q in range(112)
        ),
        "exact pair operator",
    )


def fixture(labels, groups, pair, matrix, mode):
    supports = [group[side::2] for group in groups for side in (0, 1)]
    planes = [group[i : i + 2] for group in groups for i in range(0, len(group), 2)]
    owners = {p: plane for plane in planes for p in plane}
    a = [int(p in supports[pair[0]]) for p in range(112)]
    b = [int(p in supports[pair[1]]) for p in range(112)]
    seed = (
        [F(p % 3 == 0) for p in range(112)]
        if mode == "binary"
        else [F((p % 7) - 3, 2 + p % 5) for p in range(112)]
    )
    if mode != "binary":
        for i in range(3):
            port = supports[pair[0]][i % len(supports[pair[0]])]
            seed[port] = -F(matrix[i][0], matrix[i][2]) if matrix[i][2] else F(7, 3)
    queries, readers = factors(a, b, seed, matrix)
    identity(a, b, queries, readers)
    before = bill(labels, owners, queries, readers)
    floor = len(groups[pair[0] // 2]) + len(groups[pair[1] // 2])
    need(before >= floor, "reader floor")
    result = {"pair": list(pair), "seed": mode, "bill": before, "floor": floor}
    if all(row[2] != 0 for row in matrix):
        nq, nr = replace(a, b, seed, matrix)
        identity(a, b, nq, nr)
        after = bill(labels, owners, nq, nr)
        need(floor <= after <= before, "support-dominated integral bill")
        result["integral_bill"] = after
    return result


def run():
    labels, groups = load()
    matrices = (
        ((0, 0, 1), (0, -1, 1), (-1, 0, 1)),
        ((F(2, 3), F(-7, 5), 1), (F(2, 3), F(11, 7), 1), (F(13, 4), F(19, 9), 1)),
        ((0, 0, 2), (1, 2, -3), (2, 1, F(5, 7))),
        ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
        ((1, 0, 0), (0, 1, 1), (1, 2, 1)),
    )
    fixtures = [
        fixture(labels, groups, pair, matrix, mode)
        for pair in ((0, 1), (0, 2), (0, 31), (28, 31))
        for matrix in matrices
        for mode in ("binary", "rational-outside")
    ]
    return {
        "status": "PASS_UNRESTRICTED_THREE_QUERY",
        "errors": 0,
        "equality_classes": classify(),
        "fixtures": fixtures,
        "original_operator_entries": len(fixtures) * 112 * 112,
        "replacement_operator_entries": sum("integral_bill" in f for f in fixtures)
        * 112
        * 112,
        "exact_operator_entries": (
            len(fixtures) + sum("integral_bill" in f for f in fixtures)
        )
        * 112
        * 112,
        "literal_baseline_tariff": sum(2 * len(group) for group in groups),
        "scope": (
            "All-field written theorem; finite rational fixtures and equality-class "
            "check. No supplier or kappa."
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = run()
    encoded = json.dumps(result, indent=2) + "\n"
    if args.write:
        (HERE / "RESULT.json").write_text(encoded)
    else:
        need(read(HERE / "RESULT.json").decode() == encoded, "receipt mismatch")
    print(result["status"], "classes=13 fixtures=40 errors=0 baseline=224")


if __name__ == "__main__":
    main()
