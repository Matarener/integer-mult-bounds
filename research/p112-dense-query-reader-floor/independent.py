"""Separate coordinate/support check. Nick Petalas. Apache-2.0."""

import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, label):
    if not ok:
        raise ValueError(label)


def bounded_json(path, limit):
    with path.open("rb") as f:
        raw = f.read(limit + 1)
    require(len(raw) <= limit, "input size")
    return json.loads(raw)


def binary_rank(matrix):
    require(len(matrix) <= 16 and all(len(row) <= 16 for row in matrix), "rank limit")
    rows = [row[:] for row in matrix]
    width = len(rows[0]) if rows else 0
    pivot = 0
    for column in range(width):
        candidates = [i for i in range(pivot, len(rows)) if rows[i][column]]
        if not candidates:
            continue
        i = candidates[0]
        rows[i], rows[pivot] = rows[pivot], rows[i]
        for j in range(pivot + 1, len(rows)):
            if rows[j][column]:
                rows[j] = [x ^ y for x, y in zip(rows[j], rows[pivot], strict=True)]
        pivot += 1
    return pivot


def census():
    recipes = bounded_json(
        ROOT / "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json", 1_048_576
    )["recipes"]
    require(type(recipes) is list and len(recipes) == 112, "recipe capacity")
    vectors = {r["port"]: [(r["q"] >> bit) & 1 for bit in range(9)] for r in recipes}
    groups = bounded_json(HERE / "RETAINED-RANK32.json", 32768)["orthonormal_groups"]
    require(set(vectors) == set(range(112)) and len(groups) == 16, "geometry size")
    require(all(len(g) in (4, 6, 8) for g in groups), "group capacity")
    planes, halves = {}, []
    for group in groups:
        for j, port in enumerate(group):
            planes[port] = group[j - j % 2 : j - j % 2 + 2]
        halves.extend((group[::2], group[1::2]))
    counts = {}
    subsets = 0
    for a, b in itertools.combinations(halves, 2):
        require(len(a + b) <= 8, "support limit")
        source = sorted({q for p in a + b for q in planes[p]})
        for mask in range(1 << len(a + b)):
            support = [p for j, p in enumerate(a + b) if mask & (1 << j)]
            reader = sorted({q for p in support for q in planes[p]})
            matrix = [
                [
                    sum(x * y for x, y in zip(vectors[p], vectors[q], strict=True)) % 2
                    for p in source
                ]
                for q in reader
            ]
            bill = binary_rank(matrix)
            d_a, d_b = 2 * len(set(a) & set(support)), 2 * len(set(b) & set(support))
            require(bill >= d_a and bill >= d_b, "independent target columns")
            gap = 2 * bill - d_a - d_b
            counts[gap] = counts.get(gap, 0) + 1
            subsets += 1
    expected = bounded_json(HERE / "RESULT.json", 65536)
    require(subsets == expected["reader_support_subsets"], "subset receipt")
    require(
        {str(k): v for k, v in counts.items()}
        == expected["two_cost_minus_coverage_histogram"],
        "rank receipt",
    )
    return subsets


def field_checks():
    tuples, delivered = 0, 0
    for prime in (2, 3, 5, 7):
        slopes = list(range(1, prime))
        for coefficients in itertools.product(range(prime), repeat=len(slopes)):
            target = (
                sum(coefficients) % prime,
                sum(c * s for c, s in zip(coefficients, slopes, strict=True)) % prime,
            )
            if target in ((1, 0), (0, 1)):
                require(sum(c != 0 for c in coefficients) >= 2, "two active readers")
                delivered += 1
            tuples += 1
    return tuples, delivered


def partial_reader():
    raw = bounded_json(HERE / "RETAINED-RANK32.json", 32768)
    group = next(g for g in raw["orthonormal_groups"] if len(g) == 8)
    data = bounded_json(
        ROOT / "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json", 1_048_576
    )
    require(len(data["recipes"]) == 112, "partial-reader recipe capacity")
    labels = {r["port"]: r["q"] for r in data["recipes"]}
    eye = [
        [
            sum(((labels[p] >> bit) & 1) * ((labels[q] >> bit) & 1) for bit in range(9))
            % 2
            for q in group
        ]
        for p in group
    ]
    require(eye == [[int(i == j) for j in range(8)] for i in range(8)], "literal I8")
    self_cost = binary_rank(eye)
    actual = binary_rank([row[:2] for row in eye])
    require(actual == 2 < self_cost == len(group), "self versus actual cost")
    return {"self": self_cost, "actual": actual, "group": group}


def main():
    subsets = census()
    tuples, delivered = field_checks()
    partial = partial_reader()
    print(
        json.dumps(
            {
                "reader_subsets": subsets,
                "field_coefficient_tuples": tuples,
                "axis_deliveries": delivered,
                "partial_reader": partial,
            },
            sort_keys=True,
        )
    )
    print("PASS_SEPARATE_DENSE_READER_FLOOR")


if __name__ == "__main__":
    main()
