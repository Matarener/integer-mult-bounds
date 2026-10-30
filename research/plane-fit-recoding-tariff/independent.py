#!/usr/bin/env python3
"""Separate explicit-vector geometry and complete two-query recoding census.

Does not import the primary checker. Nick Petalas. Apache-2.0.
"""

import json
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def check(ok, message):
    if not ok:
        raise ValueError(message)


def dense_rank(matrix, modulus):
    check(len(matrix) <= 112 and all(len(row) <= 112 for row in matrix), "rank bounds")
    rows = [list(row) for row in matrix]
    pivot_row = 0
    for column in range(len(rows[0])):
        candidates = [
            i for i in range(pivot_row, len(rows)) if rows[i][column] % modulus
        ]
        if not candidates:
            continue
        i = candidates[0]
        rows[pivot_row], rows[i] = rows[i], rows[pivot_row]
        scale = pow(rows[pivot_row][column] % modulus, -1, modulus)
        rows[pivot_row] = [x * scale % modulus for x in rows[pivot_row]]
        for i in range(len(rows)):
            if i != pivot_row:
                scale = rows[i][column] % modulus
                rows[i] = [
                    (x - scale * y) % modulus
                    for x, y in zip(rows[i], rows[pivot_row], strict=True)
                ]
        pivot_row += 1
    return pivot_row


def inputs():
    meta = json.loads((HERE / "SOURCES.json").read_text())
    pin = next(row for row in meta["files"] if row["usage"] == "input")
    with (ROOT / pin["path"]).open("rb") as stream:
        raw = stream.read(2097153)
    check(len(raw) <= 2097152, "selected byte capacity")
    check(sha256(raw).hexdigest() == pin["sha256"], "selected input hash")
    recipes = json.loads(raw)["recipes"]
    label_by_port = {row["port"]: row["q"] for row in recipes}
    check(sorted(label_by_port) == list(range(112)), "literal port IDs")
    vectors = [[int(bit) for bit in f"{label_by_port[p]:09b}"] for p in range(112)]
    raw = (HERE / "RETAINED-RANK32.json").read_bytes()
    check(sha256(raw).hexdigest() == meta["retained_rank32"]["sha256"], "retained hash")
    groups = json.loads(raw)["orthonormal_groups"]
    check(
        len(groups) == 16 and sorted(p for g in groups for p in g) == list(range(112)),
        "complete group partition",
    )
    return vectors, groups


def gram(vectors, ports):
    return [
        [
            sum(x * y for x, y in zip(vectors[i], vectors[j], strict=True)) % 2
            for j in ports
        ]
        for i in ports
    ]


def two_by_two_census(weights, costs):
    checked = 0
    minima = {}
    for prime in (2, 3, 5):
        invertible = [
            (a, b, c, d)
            for a, b, c, d in product(range(prime), repeat=4)
            if (a * d - b * c) % prime
        ]
        check(
            len(invertible) == (prime * prime - 1) * (prime * prime - prime),
            "complete GL2 census",
        )
        minimum = 224
        for i, j in combinations(range(32), 2):
            original = weights[i] + weights[j]
            for a, b, c, d in invertible:
                charge = 0
                for x, y in ((a, b), (c, d)):
                    active = set()
                    if x:
                        active.add(i // 2)
                    if y:
                        active.add(j // 2)
                    charge += costs[tuple(sorted(active))]
                total = 224 - original + charge
                check(total >= 224, "invertible two-query recoding undercuts theorem")
                minimum = min(minimum, total)
                checked += 1
        minima[str(prime)] = minimum
    check(checked == 496 * (6 + 48 + 480), "exact recoding count")
    return checked, minima


def main():
    vectors, groups = inputs()
    costs = {}
    for n in (1, 2):
        for indices in combinations(range(16), n):
            ports = [p for i in indices for p in groups[i]]
            costs[indices] = dense_rank(gram(vectors, ports), 2)
    weights = []
    for i, group in enumerate(groups):
        check(
            gram(vectors, group)
            == [[int(i == j) for j in range(len(group))] for i in range(len(group))],
            "literal group identity",
        )
        check(costs[(i,)] == len(group), "literal full-plane rank")
        weights.extend([len(group), len(group)])
    check(sum(weights) == 224, "attained tariff")
    supports = [g[side::2] for g in groups for side in (0, 1)]
    channel = {p: i for i, support in enumerate(supports) for p in support}
    matrix = [[int(channel[i] == channel[j]) for j in range(112)] for i in range(112)]
    for prime in (2, 3, 5):
        check(dense_rank(matrix, prime) == 32, "literal rank32")
    check(dense_rank(gram(vectors, list(range(112))), 2) == 9, "full closure rank9")
    check(
        sum(dense_rank(gram(vectors, support), 2) for support in supports) == 112,
        "representative-only undercharge control",
    )
    count, minima = two_by_two_census(weights, costs)
    print(
        "PASS_INDEPENDENT_RECODING_TARIFF "
        + json.dumps(
            {
                "errors": 0,
                "literal_tariff": 224,
                "two_query_recodings": count,
                "field_minima": minima,
                "dense_geometry_sets": len(costs) + 1,
                "literal_rank_fields": [2, 3, 5],
                "no_new_kappa": True,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
