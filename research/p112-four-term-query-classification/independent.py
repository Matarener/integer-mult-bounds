"""Separate raw-Gram and integer-minor replay. Nick Petalas. Apache-2.0."""

import hashlib
import itertools as it
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

HOME = Path(__file__).absolute().parent
ROOT = HOME.parents[1]


def check(ok, message):
    if not ok:
        raise ValueError(message)


def load(path):
    check(path.absolute() == path.resolve() and path.is_file(), "input alias")
    with path.open("rb") as stream:
        raw = stream.read(1048577)
    check(len(raw) <= 1048576, "input size")
    return json.loads(raw)


def authenticate():
    rows = [r for r in load(HOME / "SOURCES.json")["files"] if r["usage"] == "input"]
    check(len(rows) == 9, "source count")
    for row in rows:
        p = ROOT / row["path"]
        check(
            p.is_relative_to(ROOT) and p.absolute() == p.resolve() and p.is_file(),
            "source alias",
        )
        with p.open("rb") as stream:
            raw = stream.read(1048577)
        check(len(raw) <= 1048576, "source size")
        check(hashlib.sha256(raw).hexdigest() == row["sha256"], "source hash")


def det(a, b, c):
    return (
        a[0] * (b[1] * c[2] - b[2] * c[1])
        - a[1] * (b[0] * c[2] - b[2] * c[0])
        + a[2] * (b[0] * c[1] - b[1] * c[0])
    )


def rational_rank(columns):
    if any(det(*c) for c in it.combinations(columns, 3)):
        return 3
    if any(
        a[i] * b[j] != a[j] * b[i]
        for a, b in it.combinations(columns, 2)
        for i, j in it.combinations(range(3), 2)
    ):
        return 2
    return int(any(any(c) for c in columns))


def gf2_basis(columns, width):
    rows = [0] * width
    for c in columns:
        for bit in range(width - 1, -1, -1):
            if c >> bit & 1:
                if rows[bit]:
                    c ^= rows[bit]
                else:
                    rows[bit] = c
                    break
    return tuple(x for x in rows if x)


def projective_checks(expected):
    points = [
        (int(i & 1), int(i >> 1 & 1), int(i >> 2 & 1)) for i in (1, 2, 4, 3, 5, 6, 7)
    ]
    lines = {
        tuple(c)
        for c in it.combinations(range(7), 3)
        if det(*(points[i] for i in c)) == 0
    }
    check(len(lines) == 6, "non-Fano integer incidences")
    autos = [
        p
        for p in it.permutations(range(7))
        if {tuple(sorted(p[i] for i in line)) for line in lines} == lines
    ]
    marks = [(0, 1, 2), (0, 1, 4), (0, 3, 4), (3, 4, 5)]
    seen = set()
    for mark, size in zip(marks, (4, 12, 12, 1), strict=True):
        orbit = {tuple(sorted(p[i] for i in mark)) for p in autos}
        check(len(orbit) == size and not (seen & orbit), "independent orbit")
        seen |= orbit
    check(seen == set(it.combinations(range(7), 3)) - lines, "orbit completeness")
    requests = 0
    for row in expected["binary_transfers"]:
        mark, queries, new = row["marks"], row["queries"], row["new"]
        # Cramer's rule checks normalized source supports independently.
        matrix = [points[i] for i in mark]
        divisor = det(*matrix)
        check(divisor != 0, "marked basis")
        for qi, candidate in zip(queries, new, strict=True):
            coefficients = []
            for j in range(3):
                replaced = list(matrix)
                replaced[j] = points[qi]
                coefficients.append(Fraction(det(*replaced), divisor))
            check(
                all(not x or y for x, y in zip(candidate, coefficients, strict=True)),
                "source containment",
            )
        for subset in range(16):
            old = [points[q] for i, q in enumerate(queries) if subset >> i & 1]
            columns = [
                sum(x << j for j, x in enumerate(new[i]))
                for i in range(4)
                if subset >> i & 1
            ]
            for j, target in enumerate(mark):
                if rational_rank([*old, points[target]]) == rational_rank(old):
                    check(
                        len(gf2_basis([*columns, 1 << j], 3))
                        == len(gf2_basis(columns, 3)),
                        "integer-minor reader implication",
                    )
                requests += 1
    check(requests == 96, "transfer request coverage")
    return len(autos), len(seen), requests


def literal_geometry():
    data = load(ROOT / "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json")
    labels = [r["q"] for r in data["recipes"]]
    check(
        len(labels) == 112 and all(type(x) is int and 0 <= x < 512 for x in labels),
        "literal labels",
    )
    groups = load(ROOT / "research/p112-nonfano-affine-reader/RETAINED-RANK32.json")[
        "orthonormal_groups"
    ]
    check(
        len(groups) == 16 and sorted(p for g in groups for p in g) == list(range(112)),
        "partition",
    )
    mates = [None] * 112
    targets, prices = [], []
    for group in groups:
        check(0 < len(group) <= 8 and len(group) % 2 == 0, "even group")
        for i, p in enumerate(group):
            check(
                all(
                    (labels[p] & labels[q]).bit_count() % 2 == int(p == q)
                    for q in group
                ),
                "group Gram identity",
            )
            mates[p] = group[i ^ 1]
        for side in (0, 1):
            targets.append(group[side::2])
            prices.append(len(group))
    return labels, mates, targets, prices


def direct_case(triple, labels, mates, targets, prices):
    selected = [targets[i] for i in triple]
    ports = [p for g in selected for p in g]
    check(len(ports) <= 12, "rectangular case capacity")
    sources = sorted({p for x in ports for p in (x, mates[x])})
    check(len(sources) <= 24, "source row capacity")
    raw_columns = [
        tuple(
            sum(
                ((labels[s] & labels[p]).bit_count() % 2) << j
                for j, s in enumerate(sources)
            )
            for p in (x, mates[x])
        )
        for x in ports
    ]
    ranks, bases = [0], [()]
    for subset in range(1, 1 << len(ports)):
        index = subset.bit_length() - 1
        old = subset ^ (1 << index)
        base = gf2_basis(bases[old] + raw_columns[index], len(sources))
        bases.append(base)
        ranks.append(len(base))
    edges = []
    for group, pair in zip(selected, ((0, 1), (0, 2), (1, 2)), strict=True):
        edges.extend([pair] * len(group))
    best, witness = 100, -1
    for state in range(1 << len(ports)):
        readers = [0] * 4
        for j, pair in enumerate(edges):
            chosen = (
                tuple(k for k in range(4) if k not in pair) if state >> j & 1 else pair
            )
            for k in chosen:
                readers[k] |= 1 << j
        cost = sum(ranks[subset] for subset in readers)
        if cost < best:
            best, witness = cost, state
    original = sum(prices[i] for i in triple)
    check(best >= original, "independent dense floor")
    return [*triple, original, best, witness], 1 << len(ports)


def full_identity(targets):
    triple = (0, 2, 4)
    a = [[int(p in targets[t]) for p in range(112)] for t in triple]
    # Nonzero values on spectators test cancellation beyond the target span.
    w = [Fraction((p * 7 % 11) - 5, 3) for p in range(112)]
    queries = [
        [a[0][p] + a[1][p] - a[2][p] for p in range(112)],
        [a[0][p] - a[1][p] + a[2][p] for p in range(112)],
        [-a[0][p] + a[1][p] + a[2][p] for p in range(112)],
        [a[0][p] + a[1][p] + a[2][p] for p in range(112)],
    ]
    readers = [
        [Fraction(a[0][p] + a[1][p], 2) - w[p] for p in range(112)],
        [Fraction(a[0][p] + a[2][p], 2) - w[p] for p in range(112)],
        [Fraction(a[1][p] + a[2][p], 2) - w[p] for p in range(112)],
        w,
    ]
    # Independent target-coordinate gauges and query rescalings preserve supports.
    diagonal = [
        2 if a[0][p] else -3 if a[1][p] else 5 if a[2][p] else 7 for p in range(112)
    ]
    for p in range(112):
        for q in range(112):
            value = sum(
                readers[i][p] * diagonal[p] * Fraction(queries[i][q], diagonal[q])
                for i in range(4)
            )
            check(value == sum(c[p] * c[q] for c in a), "literal gauged operator")
    return 112 * 112


def main():
    authenticate()
    expected = load(HOME / "RESULT.json")
    projective = projective_checks(expected["marked_classification"])
    labels, mates, targets, prices = literal_geometry()
    stream, histogram, states = hashlib.sha256(), Counter(), 0
    for triple in it.combinations(range(32), 3):
        row, count = direct_case(triple, labels, mates, targets, prices)
        stream.update((json.dumps(row, separators=(",", ":")) + "\n").encode())
        histogram[row[4] - row[3]] += 1
        states += count
    result = expected["MMM"]
    check(stream.hexdigest() == result["stream_sha256"], "all-triple stream")
    check(states == result["expanded_states"], "all-triple states")
    check(
        {str(k): v for k, v in sorted(histogram.items())}
        == result["minimum_excess_histogram"],
        "dense excess histogram",
    )
    print(
        "PASS_INDEPENDENT_FOUR_TERM_TRIPLE",
        json.dumps(
            {
                "projective": projective,
                "triples": 4960,
                "states": states,
                "stream_sha256": stream.hexdigest(),
                "full_operator_entries": full_identity(targets),
            },
            sort_keys=True,
        ),
    )


if __name__ == "__main__":
    main()
