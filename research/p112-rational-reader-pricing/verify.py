"""Exact fixtures for the arbitrary-rational three-query proof. Apache-2.0."""

import argparse
import itertools
import json
from collections import Counter
from fractions import Fraction
from hashlib import sha1, sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT = "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read(path, limit=1_048_576):
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    need(len(raw) <= limit, "input capacity exceeded")
    return raw


def authenticate(raw, pin):
    need(sha256(raw).hexdigest() == pin["sha256"], "source SHA256 mismatch")
    blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
    need(
        sha1(blob, usedforsecurity=False).hexdigest() == pin["git_blob"],
        "source Git blob mismatch",
    )


def load():
    meta = json.loads(read(HERE / "SOURCES.json", 32768))
    pins = [r for r in meta["files"] if r["usage"] == "input"]
    need(len(pins) == 1 and pins[0]["path"] == INPUT, "live source inventory")
    raw = read(ROOT / INPUT)
    authenticate(raw, pins[0])
    rows = json.loads(raw)["recipes"]
    need(type(rows) is list and len(rows) == 112, "112 source recipes")
    need(all(type(r["port"]) is int for r in rows), "integer ports")
    need(sorted(r["port"] for r in rows) == list(range(112)), "source port IDs")
    labels = [r["q"] for r in sorted(rows, key=lambda r: r["port"])]
    need(all(type(q) is int and 0 < q < 512 for q in labels), "nine-bit labels")
    need(len(set(labels)) == 112, "distinct source labels")
    raw = read(HERE / "RETAINED-RANK32.json", 32768)
    authenticate(raw, meta["retained_rank32"])
    groups = json.loads(raw)["orthonormal_groups"]
    need(type(groups) is list and len(groups) == 16, "sixteen groups")
    need(
        all(type(g) is list and len(g) in (4, 6, 8) for g in groups), "even group sizes"
    )
    need(all(type(p) is int for g in groups for p in g), "integer group ports")
    need(sorted(p for g in groups for p in g) == list(range(112)), "partition")
    for g in groups:
        need(
            all(
                (labels[p] & labels[q]).bit_count() % 2 == int(p == q)
                for p in g
                for q in g
            ),
            "group Gram identity",
        )
    return labels, groups


def rank(rows, width):
    need(0 <= width <= 224 and len(rows) <= 224, "rank capacity")
    pivots = [0] * width
    for original in rows:
        need(type(original) is int and 0 <= original < 1 << width, "binary row")
        value = original
        for bit in range(width - 1, -1, -1):
            if value >> bit & 1:
                if pivots[bit]:
                    value ^= pivots[bit]
                else:
                    pivots[bit] = value
                    break
    return sum(bool(p) for p in pivots)


def tariff(labels, source, reader):
    need(len(source) <= 112 and len(reader) <= 112, "closure capacity")
    rows = [
        sum(
            ((labels[p] & labels[q]).bit_count() % 2) << j for j, q in enumerate(reader)
        )
        for p in source
    ]
    return rank(rows, len(reader))


def geometry(groups):
    planes = [g[i : i + 2] for g in groups for i in range(0, len(g), 2)]
    owners = {p: plane for plane in planes for p in plane}
    supports = [g[side::2] for g in groups for side in (0, 1)]
    return owners, supports


def determinant(m):
    need(len(m) == 3 and all(len(row) == 3 for row in m), "three by three matrix")
    return (
        m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
        - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
        + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
    )


def inverse(m):
    d = determinant(m)
    need(d != 0, "singular query basis")
    result = []
    for i in range(3):
        row = []
        for j in range(3):
            rr = [k for k in range(3) if k != j]
            cc = [k for k in range(3) if k != i]
            minor = m[rr[0]][cc[0]] * m[rr[1]][cc[1]]
            minor -= m[rr[0]][cc[1]] * m[rr[1]][cc[0]]
            row.append(Fraction((-1) ** (i + j) * minor, d))
        result.append(row)
    need(
        all(
            sum(result[i][k] * m[k][j] for k in range(3)) == int(i == j)
            for i in range(3)
            for j in range(3)
        ),
        "inverse identity",
    )
    return result


def patterns():
    """All equality/zero patterns of three rationals relative to 0 and -1."""
    result = []
    for row in itertools.product((0, -1, 2, 3, 4), repeat=3):
        generic = list(dict.fromkeys(x for x in row if x not in (0, -1)))
        if generic == list(range(2, 2 + len(generic))):
            result.append(row)
    need(len(result) <= 125, "pattern capacity")
    return result


def reader_supports(points):
    return [
        (
            points[(i + 1) % 3][1] != points[(i + 2) % 3][1],
            points[(i + 1) % 3][0] != points[(i + 2) % 3][0],
        )
        for i in range(3)
    ]


def domination(points):
    old = reader_supports(points)
    for grid in itertools.product(((0, 0), (0, -1), (-1, 0), (-1, -1)), repeat=3):
        matrix = [(*p, 1) for p in grid]
        if abs(determinant(matrix)) != 1:
            continue
        if any(
            points[i][k] in (0, -1) and grid[i][k] != points[i][k]
            for i in range(3)
            for k in range(2)
        ):
            continue
        new = reader_supports(grid)
        if all(not new[i][k] or old[i][k] for i in range(3) for k in range(2)):
            inv = inverse(matrix)
            need(
                all(x.denominator == 1 for row in inv for x in row),
                "integral dominating readers",
            )
            need(
                all(
                    points[i][k] + z != 0 or grid[i][k] + z == 0
                    for i in range(3)
                    for k in range(2)
                    for z in (0, 1)
                ),
                "pointwise source support domination",
            )
            return grid
    raise ValueError("mixed reader pattern lacks an integral domination")


def classify():
    inventory, counts = [], Counter()
    for xs, ys in itertools.product(patterns(), repeat=2):
        points = tuple(zip(xs, ys, strict=True))
        if len(set(xs)) == 1 or len(set(ys)) == 1 or len(set(points)) != 3:
            continue  # These patterns force every realization to be singular.
        readers = reader_supports(points)
        need(all(any(r) for r in readers), "nonzero reader directions")
        both = sum(all(r) for r in readers)
        if both == 3:
            need(len(set(xs)) == len(set(ys)) == 3, "three full-reader pattern")
            need(any(x not in (0, -1) for x in xs), "full source group")
            certificate = None
        else:
            need(both in (1, 2), "mixed reader classification")
            certificate = domination(points)
        counts[str(both)] += 1
        inventory.append([points, both, certificate])
    raw = json.dumps(inventory, separators=(",", ":")).encode()
    return {
        "patterns_per_coordinate": len(patterns()),
        "reader_pattern_histogram": dict(sorted(counts.items())),
        "inventory_sha256": sha256(raw).hexdigest(),
    }


def source_geometry(labels, groups):
    owners, supports = geometry(groups)
    channels = {p: c for c, g in enumerate(supports) for p in g}
    checks = 0
    for p, q, i, j in itertools.product(range(112), range(112), range(2), range(2)):
        value = int(channels[p] == channels[q])
        value *= (labels[owners[p][i]] & labels[owners[q][j]]).bit_count() % 2
        need(value == int(p == q and i == j), "expanded I224 identity")
        checks += 1
    histogram = Counter()
    for a, b in itertools.combinations(range(32), 2):
        ga, gb = groups[a // 2], groups[b // 2]
        union = sorted(set(ga + gb))
        r = tariff(labels, union, union)
        need(r >= max(len(ga), len(gb)), "contained group identity rank")
        need(2 * max(len(ga), len(gb)) >= len(ga) + len(gb), "full-reader floor")
        histogram[f"{len(ga) + len(gb)}:{r}"] += 1
    need(sum(histogram.values()) == 496, "complete query-pair coverage")
    return checks, dict(sorted(histogram.items()))


def fixture(labels, groups, pair, seed, matrix):
    need(len(pair) == 2 and pair[0] != pair[1], "two distinct queries")
    need(all(type(c) is int and 0 <= c < 32 for c in pair), "query IDs")
    owners, supports = geometry(groups)
    a, b = [[int(p in supports[c]) for p in range(112)] for c in pair]
    union = set(groups[pair[0] // 2] + groups[pair[1] // 2])
    need(type(seed) is list and len(seed) == len(set(seed)) <= 16, "binary seed")
    need(all(type(p) is int and p in union for p in seed), "seed domain")
    z = [int(p in seed) for p in range(112)]
    formal = [a, b, z]
    need(
        rank([sum(v << j for j, v in enumerate(row)) for row in formal], 112) == 3,
        "seed is genuinely external",
    )
    inv = inverse(matrix)
    queries = [
        [sum(matrix[t][k] * formal[k][p] for k in range(3)) for p in range(112)]
        for t in range(3)
    ]
    readers = [
        [inv[0][t] * a[p] + inv[1][t] * b[p] for p in range(112)] for t in range(3)
    ]
    need(
        all(
            sum(readers[t][p] * queries[t][q] for t in range(3))
            == a[p] * a[q] + b[p] * b[q]
            for p in range(112)
            for q in range(112)
        ),
        "exact rational UQ identity",
    )
    bills = []
    for q, u in zip(queries, readers, strict=True):
        source = sorted({j for p in range(112) if q[p] for j in owners[p]})
        target = sorted({j for p in range(112) if u[p] for j in owners[p]})
        bills.append(tariff(labels, source, target))
    baseline = sum(len(groups[c // 2]) for c in pair)
    need(sum(bills) >= baseline, "rational replacement beats claimed floor")
    return {
        "pair": pair,
        "seed": seed,
        "formal_matrix": [[str(x) for x in row] for row in matrix],
        "seed_coefficients_nonzero": sum(bool(row[2]) for row in matrix),
        "term_tariffs": bills,
        "baseline": baseline,
        "actual": sum(bills),
    }


def run():
    labels, groups = load()
    checks, pairs = source_geometry(labels, groups)
    matrices = [
        [(1, 0, 0), (0, 1, 0), (0, 0, 1)],
        [(1, 0, 0), (0, 0, 1), (0, 1, 1)],
        [(0, 0, 1), (-1, 0, 1), (0, -1, 1)],
        [(Fraction(1, 3), Fraction(2, 5), 1), (-1, 0, 1), (0, -1, 1)],
        [(0, -1, 1), (-1, 0, 1), (Fraction(2, 7), Fraction(3, 5), 1)],
        [(0, 0, 1), (-1, 0, 1), (0, Fraction(5, 2), 1)],
    ]
    fixtures = []
    for pair in ([0, 1], [0, 2], [22, 28]):
        seed = [groups[pair[0] // 2][0]]
        for matrix in matrices:
            fixtures.append(fixture(labels, groups, pair, seed, matrix))
    return {
        "status": "PASS_P112_RATIONAL_THREE_QUERY_FLOOR",
        "errors": 0,
        "literal_global_tariff": 224,
        "expanded_identity_entries": checks,
        "pairs": 496,
        "pair_geometry_histogram": pairs,
        "support_classification": classify(),
        "rational_fixtures": fixtures,
        "no_native_supplier_or_kappa_claim": True,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    actual = run()
    if args.write:
        (HERE / "RESULT.json").write_text(json.dumps(actual, indent=2) + "\n")
    else:
        expected = json.loads(read(HERE / "RESULT.json", 65536))
        need(actual == expected, "result receipt differs")
    print(
        json.dumps(
            {k: v for k, v in actual.items() if k != "rational_fixtures"},
            sort_keys=True,
        )
    )
