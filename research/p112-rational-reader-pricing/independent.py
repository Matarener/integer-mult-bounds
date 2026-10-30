"""Separate set-partition and rational-elimination check. Apache-2.0."""

import itertools
import json
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def check(ok, message):
    if not ok:
        raise ValueError(message)


def bounded_json(path, limit):
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    check(len(raw) <= limit, "bounded input")
    return json.loads(raw), raw


def pattern_rows():
    result = set()
    for partition in ((0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 1, 2)):
        blocks = max(partition) + 1
        for zero, minus in itertools.product(range(-1, blocks), repeat=2):
            if zero == minus and zero != -1:
                continue
            values, generic = [], 2
            for block in range(blocks):
                if block == zero:
                    values.append(0)
                elif block == minus:
                    values.append(-1)
                else:
                    values.append(generic)
                    generic += 1
            result.add(tuple(values[b] for b in partition))
    check(len(result) == 37, "37 set-partition patterns")
    return sorted(result)


def solve_inverse(matrix):
    check(len(matrix) == 3 and all(len(row) == 3 for row in matrix), "matrix shape")
    rows = [
        [Fraction(x) for x in row] + [Fraction(i == j) for j in range(3)]
        for i, row in enumerate(matrix)
    ]
    for col in range(3):
        pivot = next((i for i in range(col, 3) if rows[i][col]), None)
        if pivot is None:
            return None
        rows[col], rows[pivot] = rows[pivot], rows[col]
        scale = rows[col][col]
        rows[col] = [x / scale for x in rows[col]]
        for i in range(3):
            if i != col:
                scale = rows[i][col]
                rows[i] = [
                    x - scale * y for x, y in zip(rows[i], rows[col], strict=True)
                ]
    check(
        all(rows[i][j] == int(i == j) for i in range(3) for j in range(3)),
        "elimination identity",
    )
    return [row[3:] for row in rows]


def supports(points):
    rows = []
    for i in range(3):
        others = [j for j in range(3) if j != i]
        j, k = others
        rows.append(
            {
                c
                for c, value in enumerate(
                    (points[j][1] - points[k][1], points[k][0] - points[j][0])
                )
                if value
            }
        )
    return rows


def patterns_check():
    counts = Counter()
    corners = tuple(itertools.product((0, -1), repeat=2))
    triangles = tuple(itertools.permutations(corners, 3))
    for xs, ys in itertools.product(pattern_rows(), repeat=2):
        points = list(zip(xs, ys, strict=True))
        if len(set(xs)) < 2 or len(set(ys)) < 2 or len(set(points)) < 3:
            continue
        readers = supports(points)
        both = sum(len(r) == 2 for r in readers)
        counts[str(both)] += 1
        if both == 3:
            check(len(set(xs)) == 3 and len(set(ys)) == 3, "full reader differences")
            check(any(x not in (0, -1) for x in xs), "generic full source")
            continue
        witnesses = 0
        for triangle in triangles:
            if any(
                points[i][j] + z == 0 and triangle[i][j] + z != 0
                for i in range(3)
                for j in range(2)
                for z in (0, 1)
            ):
                continue
            new = supports(triangle)
            if any(not new[i].issubset(readers[i]) for i in range(3)):
                continue
            inv = solve_inverse([(*p, 1) for p in triangle])
            check(inv is not None, "triangle nonsingularity")
            check(
                all(x.denominator == 1 for row in inv for x in row), "integer readers"
            )
            witnesses += 1
        check(witnesses > 0, "mixed pattern has dominated integer triangle")
    return dict(sorted(counts.items()))


def dense_binary_rank(matrix):
    check(len(matrix) <= 112, "binary row capacity")
    width = len(matrix[0]) if matrix else 0
    check(width <= 112 and all(len(row) == width for row in matrix), "binary shape")
    rows, pivots = [list(row) for row in matrix], 0
    for col in range(width):
        hit = next((i for i in range(pivots, len(rows)) if rows[i][col]), None)
        if hit is None:
            continue
        rows[pivots], rows[hit] = rows[hit], rows[pivots]
        for i in range(pivots + 1, len(rows)):
            if rows[i][col]:
                rows[i] = [x ^ y for x, y in zip(rows[i], rows[pivots], strict=True)]
        pivots += 1
    return pivots


def literal_inputs():
    meta, _ = bounded_json(HERE / "SOURCES.json", 32768)
    source = "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"
    pin = next(r for r in meta["files"] if r["path"] == source)
    data, raw = bounded_json(ROOT / source, 1048576)
    check(sha256(raw).hexdigest() == pin["sha256"], "literal source hash")
    retained, raw = bounded_json(HERE / "RETAINED-RANK32.json", 32768)
    check(sha256(raw).hexdigest() == meta["retained_rank32"]["sha256"], "retained hash")
    rows = sorted(data["recipes"], key=lambda row: row["port"])
    check(len(rows) == 112, "literal width")
    labels = [[(r["q"] >> k) & 1 for k in range(9)] for r in rows]
    groups = retained["orthonormal_groups"]
    check(
        len(groups) == 16 and sorted(p for g in groups for p in g) == list(range(112)),
        "literal partition",
    )
    check(all(len(g) in (4, 6, 8) for g in groups), "literal group capacities")
    return labels, groups


def cost(labels, source, target):
    matrix = [
        [
            sum(x * y for x, y in zip(labels[p], labels[q], strict=True)) % 2
            for q in target
        ]
        for p in source
    ]
    return dense_binary_rank(matrix)


def fixture_check(labels, groups, record):
    pair, seed = record["pair"], record["seed"]
    check(len(pair) == 2 and all(0 <= x < 32 for x in pair), "fixture query pair")
    check(len(seed) <= 16, "fixture seed capacity")
    halves = [g[side::2] for g in groups for side in (0, 1)]
    a, b = [[int(p in halves[c]) for p in range(112)] for c in pair]
    z = [int(p in seed) for p in range(112)]
    matrix = [[Fraction(x) for x in row] for row in record["formal_matrix"]]
    inv = solve_inverse(matrix)
    check(inv is not None, "rational basis nonsingularity")
    q = [
        [row[0] * a[p] + row[1] * b[p] + row[2] * z[p] for p in range(112)]
        for row in matrix
    ]
    u = [[inv[0][i] * a[p] + inv[1][i] * b[p] for p in range(112)] for i in range(3)]
    for p in range(112):
        delivered = [sum(u[i][p] * q[i][j] for i in range(3)) for j in range(112)]
        check(
            delivered == [a[p] * a[j] + b[p] * b[j] for j in range(112)],
            "exact delivered operator row",
        )
    planes = [g[i : i + 2] for g in groups for i in range(0, len(g), 2)]
    bills = []
    for source, reader in zip(q, u, strict=True):
        s = [p for plane in planes if any(source[j] for j in plane) for p in plane]
        t = [p for plane in planes if any(reader[j] for j in plane) for p in plane]
        bills.append(cost(labels, s, t))
    check(bills == record["term_tariffs"], "actual rectangular tariffs")
    check(sum(bills) == record["actual"] >= record["baseline"], "fixture floor")


def run():
    labels, groups = literal_inputs()
    expected, _ = bounded_json(HERE / "RESULT.json", 65536)
    counts = patterns_check()
    check(
        counts == expected["support_classification"]["reader_pattern_histogram"],
        "separate pattern classification",
    )
    histogram = Counter()
    for a, b in itertools.combinations(range(32), 2):
        ga, gb = groups[a // 2], groups[b // 2]
        union = sorted(set(ga + gb))
        r = cost(labels, union, union)
        check(r >= max(len(ga), len(gb)), "actual group-rank lower bound")
        histogram[f"{len(ga) + len(gb)}:{r}"] += 1
    check(dict(histogram) == expected["pair_geometry_histogram"], "496 pair geometries")
    fixtures = expected["rational_fixtures"]
    check(len(fixtures) == 18, "fixture count")
    for record in fixtures:
        fixture_check(labels, groups, record)
    return {
        "status": "PASS_SEPARATE_RATIONAL_READER_CHECK",
        "errors": 0,
        "pattern_histogram": counts,
        "pairs": 496,
        "rational_fixtures": 18,
    }


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
