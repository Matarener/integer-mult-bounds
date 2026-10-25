"""Separate coordinate and GF256 replay. Nick Petalas. Apache-2.0."""

import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
TRIPLES = list(itertools.combinations(range(6), 3))


def check(value, message):
    if not value:
        raise ValueError(message)


def load(path, limit=1_048_576):
    with path.open("rb") as stream:
        data = stream.read(limit + 1)
    check(len(data) <= limit, "independent input capacity")
    return json.loads(data)


def product(a, b):
    terms = [a << j for j in range(8) if b & (1 << j)]
    value = 0
    for term in terms:
        value ^= term
    for j in range(14, 7, -1):
        if value & (1 << j):
            value ^= 283 << (j - 8)
    return value


def embedding():
    root = next(
        x for x in range(1, 256) if product(product(x, x), product(x, x)) ^ x ^ 1 == 0
    )
    powers = [1, root, product(root, root), product(product(root, root), root)]
    result = []
    for mask in range(16):
        value = 0
        for j in range(4):
            if mask & (1 << j):
                value ^= powers[j]
        result.append(value)
    check(len(set(result)) == 16, "GF16 embedding injective")
    return result


def determinant(points, prime=0):
    """Use GF256 at zero, exact integers at -1, or the given prime."""
    value = 0
    for perm in itertools.permutations(range(3)):
        inversions = sum(perm[i] > perm[j] for i in range(3) for j in range(i + 1, 3))
        term = 1
        for row in range(3):
            term = (
                term * points[row][perm[row]]
                if prime
                else product(term, points[row][perm[row]])
            )
        if prime:
            value += (-1 if inversions % 2 else 1) * term
        else:
            value ^= term
    return value % prime if prime > 0 else value


def key(points, prime=0):
    return sum(
        (determinant([points[j] for j in t], prime) == 0) << i
        for i, t in enumerate(TRIPLES)
    )


def vector_rank(points, prime, inverse):
    rows = [list(p) for p in points]
    height = 0
    for col in range(3):
        first = next((j for j in range(height, len(rows)) if rows[j][col]), None)
        if first is None:
            continue
        rows[height], rows[first] = rows[first], rows[height]
        inv = pow(rows[height][col], -1, prime) if prime else inverse[rows[height][col]]
        rows[height] = [
            x * inv % prime if prime else product(x, inv) for x in rows[height]
        ]
        for j in range(height + 1, len(rows)):
            scale = rows[j][col]
            rows[j] = [
                (x - scale * y) % prime if prime else x ^ product(scale, y)
                for x, y in zip(rows[j], rows[height], strict=True)
            ]
        height += 1
    return height


def ranks(points, prime, inverse):
    return [
        vector_rank([points[j] for j in range(6) if mask >> j & 1], prime, inverse)
        for mask in range(64)
    ]


def library(embed):
    data = load(HERE / "TEMPLATES.json", 8192)
    check(data["field_polynomial"] == 19, "template field")
    templates = data["points"]
    check(len(templates) == 9, "nine template count")
    images = {}
    orbits = []
    for template in templates:
        check(
            len(template) == 6 and all(len(p) == 3 for p in template), "template shape"
        )
        check(
            all(type(x) is int and 0 <= x < 16 for p in template for x in p),
            "template values",
        )
        points = [[embed[x] for x in p] for p in template]
        check(all(any(p) for p in points), "nonzero embedded points")
        check(
            all(
                any(
                    product(a[j], b[k]) != product(a[k], b[j])
                    for j, k in itertools.combinations(range(3), 2)
                )
                for a, b in itertools.combinations(points, 2)
            ),
            "independent embedded pairs",
        )
        signatures = set()
        for order in itertools.permutations(range(6)):
            row = [points[j] for j in order]
            sig = key(row)
            signatures.add(sig)
            images.setdefault(sig, row)
        orbits.append(len(signatures))
    check(orbits == [1, 20, 10, 90, 120, 30, 60, 15, 6], "nine incidence orbits")
    check(len(images) == sum(orbits), "disjoint incidence types")
    return images, orbits


def finite_fields(images, inverse):
    image_ranks = {k: ranks(v, 0, inverse) for k, v in images.items()}
    total = requests = 0
    for prime in (3, 5, 7):
        points = [(1, x, y) for x, y in itertools.product(range(3), repeat=2)]
        points += [(0, 1, y) for y in range(3)] + [(0, 0, 1)]
        axes = [(1, 0, 0), (0, 1, 0)]
        others = [p for p in points if p not in axes]
        for chosen in itertools.combinations(others, 4):
            old = list(chosen) + axes
            sig = key(old, prime)
            check(sig in images, "prime incidence represented in GF256")
            old_ranks = ranks(old, prime, inverse)
            check(old_ranks == image_ranks[sig], "all subset ranks preserved")
            for mask, axis in itertools.product(range(16), (4, 5)):
                other = 9 - axis
                span = old_ranks[mask | (1 << axis)] == old_ranks[mask]
                new_span = (
                    image_ranks[sig][mask | (1 << axis)] == image_ranks[sig][mask]
                )
                check(span == new_span, "reader request")
                zero = old_ranks[mask | (1 << other)] < old_ranks[mask | 48]
                new_zero = (
                    image_ranks[sig][mask | (1 << other)] < image_ranks[sig][mask | 48]
                )
                check(zero == new_zero, "source functional request")
                requests += 2
            total += 1
    return total, requests


def binary_rank(rows):
    rows = [row[:] for row in rows]
    height = 0
    width = len(rows[0]) if rows else 0
    for col in range(width):
        index = next((j for j in range(height, len(rows)) if rows[j][col]), None)
        if index is None:
            continue
        rows[height], rows[index] = rows[index], rows[height]
        for j in range(height + 1, len(rows)):
            if rows[j][col]:
                rows[j] = [
                    (a + b) % 2 for a, b in zip(rows[j], rows[height], strict=True)
                ]
        height += 1
    return height


def literal_bills():
    source = (
        HERE.parents[1] / "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"
    )
    data = load(source)
    labels = [
        [(r["q"] >> j) & 1 for j in range(9)]
        for r in sorted(data["recipes"], key=lambda r: r["port"])
    ]
    groups = load(HERE / "RETAINED-RANK32.json")["orthonormal_groups"]
    owner = {
        p: g[j : j + 2]
        for g in groups
        for j in range(0, len(g), 2)
        for p in g[j : j + 2]
    }
    indicators = [g[start::2] for g in groups for start in (0, 1)]
    rows = load(HERE / "RESULT.json")["literal_fixtures"]
    for receipt in rows:
        a, b = [set(indicators[i]) for i in receipt["pair"]]
        q = [[] for _ in range(4)]
        u = [[] for _ in range(4)]
        for p in range(112):
            c, d = (-1, 0, 1, 2)[p % 4], (0, 1, -1, 2)[p % 4]
            for i, value in enumerate(
                [int(p in a) + c, int(p in b) + c, c, int(p in a) + int(p in b) + 2 * c]
            ):
                q[i].append(value)
            for i, value in enumerate(
                [int(p in a) - d, int(p in b) - d, -int(p in a) - int(p in b), d]
            ):
                u[i].append(value)
        costs = []
        for source, reader in zip(q, u, strict=True):
            s = sorted({v for p in range(112) if source[p] for v in owner[p]})
            t = sorted({v for p in range(112) if reader[p] for v in owner[p]})
            gram = [
                [
                    sum(x * y for x, y in zip(labels[p], labels[r], strict=True)) % 2
                    for r in t
                ]
                for p in s
            ]
            costs.append(binary_rank(gram))
        check(costs == receipt["before"], "independent literal rectangular bills")
        check(sum(costs) >= receipt["floor"], "independent literal floor")
    return len(rows)


def seven_point_boundary(embed):
    rational = [(1, 1, 0), (1, 0, 1), (0, 1, 1)]
    check(determinant(rational, -1) == -2, "rational non-Fano minor minus two")
    tested = 0
    for a, c in itertools.product(embed[1:], repeat=2):
        b = product(a, c)
        check(
            determinant([(1, a, 0), (1, 0, b), (0, 1, c)]) == 0,
            "seven-point forced characteristic-two dependence",
        )
        tested += 1
    return tested


def main():
    embed = embedding()
    inverse = {a: next(b for b in embed[1:] if product(a, b) == 1) for a in embed[1:]}
    images, orbits = library(embed)
    configs, requests = finite_fields(images, inverse)
    bills = literal_bills()
    boundary = seven_point_boundary(embed)
    print(
        "PASS_INDEPENDENT_FOUR_TERM",
        json.dumps(
            {
                "orbits": orbits,
                "prime_configurations": configs,
                "subset_ranks": 64 * configs,
                "span_and_zero_requests": requests,
                "literal_bills": bills,
                "seven_point_controls": boundary,
            },
            sort_keys=True,
        ),
    )


if __name__ == "__main__":
    main()
