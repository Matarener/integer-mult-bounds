"""Three-direction dependent query support reduction. Nick Petalas. Apache-2.0."""

import argparse
import itertools
import json
from fractions import Fraction as F
from hashlib import sha1, sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT = "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"
BINARY = ((1, 0), (0, 1), (1, 1))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read(path, maximum=1_048_576):
    with path.open("rb") as stream:
        raw = stream.read(maximum + 1)
    need(len(raw) <= maximum, "input capacity")
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


def direction(vector):
    need(len(vector) == 2, "two coefficients")
    x, y = vector
    return (F(1), F(y, x)) if x else ((F(0), F(1)) if y else None)


def binary_directions(directions):
    need(2 <= len(directions) <= 3, "two or three projective directions")
    need(len(set(directions)) == len(directions), "distinct directions")
    fixed = {v: v for v in directions if not all(v)}
    remaining = [v for v in BINARY if v not in fixed.values()]
    result = dict(fixed)
    for v in directions:
        if v not in result:
            result[v] = remaining.pop(0)
    need(len(set(result.values())) == len(directions), "injective binary map")
    need(
        all(
            not mapped[j] or old[j] for old, mapped in result.items() for j in range(2)
        ),
        "source support inclusion",
    )
    return result


def binary_solution(directions, active, target):
    need(len(directions) <= 3 and 0 <= active < 1 << len(directions), "mask capacity")
    need(target in ((0, 0), (1, 0), (0, 1)), "target coordinate")
    for mask in range(1 << len(directions)):
        if mask & ~active:
            continue
        value = tuple(
            sum(v[j] for i, v in enumerate(directions) if mask >> i & 1) % 2
            for j in range(2)
        )
        if value == target:
            return mask
    raise ValueError("no support-dominated binary reader")


def replace(coefficients, readers, a, b):
    need(2 <= len(coefficients) <= 16 and len(readers) == len(coefficients), "list cap")
    need(len(a) == len(b) == 112, "indicator capacity")
    need(all(v in (0, 1) for v in a + b), "binary indicators")
    need(all(not (x and y) for x, y in zip(a, b, strict=True)), "disjoint indicators")
    need(all(len(row) == 112 for row in readers), "reader capacity")
    keys = [direction(v) for v in coefficients]
    directions = list(dict.fromkeys(v for v in keys if v is not None))
    mapping = binary_directions(directions)
    images = [mapping[v] for v in directions]
    queries = [[v[0] * x + v[1] * y for x, y in zip(a, b, strict=True)] for v in images]
    new_readers = [[0] * 112 for _ in directions]
    for p in range(112):
        active = sum(
            int(any(keys[i] == v and readers[i][p] for i in range(len(keys)))) << j
            for j, v in enumerate(directions)
        )
        mask = binary_solution(images, active, (a[p], b[p]))
        for j in range(len(directions)):
            new_readers[j][p] = (mask >> j) & 1
    for j, key in enumerate(directions):
        members = [i for i, k in enumerate(keys) if k == key]
        need(
            all(
                not new_readers[j][p] or any(readers[i][p] for i in members)
                for p in range(112)
            ),
            "grouped reader inclusion",
        )
    return queries, new_readers


def rank(rows, width):
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


def bill(labels, owners, queries, readers):
    total = 0
    for query, reader in zip(queries, readers, strict=True):
        source = sorted({q for p, v in enumerate(query) if v for q in owners[p]})
        target = sorted({q for p, v in enumerate(reader) if v for q in owners[p]})
        rows = [
            sum(
                ((labels[p] & labels[q]).bit_count() % 2) << j
                for j, q in enumerate(target)
            )
            for p in source
        ]
        total += rank(rows, len(target))
    return total


def identity(a, b, queries, readers, modulus=None):
    for p in range(112):
        for q in range(112):
            actual = sum(u[p] * v[q] for u, v in zip(readers, queries, strict=True))
            difference = actual - a[p] * a[q] - b[p] * b[q]
            need(
                (difference % modulus if modulus else difference) == 0, "pair identity"
            )


def rational_readers(coefficients, a, b, mode):
    n = len(coefficients)
    need(2 <= n <= 16 and mode in ("sparse", "cancelling"), "fixture capacity")
    pairs = [
        (i, j)
        for i, j in itertools.combinations(range(n), 2)
        if coefficients[i][0] * coefficients[j][1]
        != coefficients[i][1] * coefficients[j][0]
    ]
    need(bool(pairs), "rank-two queries")
    readers = [[F(0)] * 112 for _ in range(n)]
    for p in range(112):
        i, j = pairs[p % len(pairs)]
        if mode == "cancelling":
            for k in range(n):
                if k not in (i, j):
                    readers[k][p] = F((p + k) % 5 - 2, 1 + k % 3)
        x = a[p] - sum(readers[k][p] * coefficients[k][0] for k in range(n))
        y = b[p] - sum(readers[k][p] * coefficients[k][1] for k in range(n))
        s, t = coefficients[i], coefficients[j]
        det = s[0] * t[1] - s[1] * t[0]
        readers[i][p] = F(x * t[1] - y * t[0], det)
        readers[j][p] = F(s[0] * y - s[1] * x, det)
    return readers


def fixture(labels, groups, pair, directions, mode, duplicate):
    supports = [g[side::2] for g in groups for side in (0, 1)]
    planes = [g[i : i + 2] for g in groups for i in range(0, len(g), 2)]
    owners = {p: plane for plane in planes for p in plane}
    a = [int(p in supports[pair[0]]) for p in range(112)]
    b = [int(p in supports[pair[1]]) for p in range(112)]
    coefficients = list(directions)
    if duplicate:
        coefficients += [tuple(-F(2, 3) * x for x in v) for v in directions] + [(0, 0)]
    readers = rational_readers(coefficients, a, b, mode)
    queries = [
        [v[0] * x + v[1] * y for x, y in zip(a, b, strict=True)] for v in coefficients
    ]
    identity(a, b, queries, readers)
    nq, nr = replace(coefficients, readers, a, b)
    identity(a, b, nq, nr, 2)
    before, after = bill(labels, owners, queries, readers), bill(labels, owners, nq, nr)
    floor = len(groups[pair[0] // 2]) + len(groups[pair[1] // 2])
    need(floor <= after <= before, "sharp reader tariff floor")
    return {
        "pair": list(pair),
        "mode": mode,
        "queries": len(queries),
        "directions": len(directions),
        "before": before,
        "binary": after,
        "floor": floor,
    }


def run():
    labels, groups = load()
    choices = (
        ((1, 0), (0, 1)),
        ((1, 0), (F(2, 3), F(-7, 5))),
        ((1, 1), (1, -1)),
        ((1, 0), (0, 1), (1, 1)),
        ((1, 0), (1, 2), (1, 3)),
        ((1, 1), (1, -1), (F(3, 5), F(7, 4))),
    )
    fixtures = [
        fixture(labels, groups, pair, directions, mode, duplicate)
        for pair in ((0, 1), (0, 2), (0, 31), (28, 31))
        for directions in choices
        for mode in ("sparse", "cancelling")
        for duplicate in (False, True)
    ]
    return {
        "status": "PASS_DEPENDENT_READER_FLOOR",
        "errors": 0,
        "fixtures": fixtures,
        "exact_operator_entries": len(fixtures) * 2 * 112 * 112,
        "literal_baseline_tariff": sum(2 * len(g) for g in groups),
        "scope": "Written all-field theorem; finite tests; no supplier or kappa.",
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
    print(result["status"], f"fixtures={len(result['fixtures'])} errors=0 baseline=224")


if __name__ == "__main__":
    main()
