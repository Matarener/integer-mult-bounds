#!/usr/bin/env python3
"""Minor and exhaustive-XOR corroboration. Nick Petalas, Apache-2.0."""

import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent


def check(value, message):
    if not value:
        raise ValueError(message)


def load(path, digest=None):
    with path.open("rb") as stream:
        raw = stream.read((1 << 20) + 1)
    check(len(raw) <= 1 << 20, "independent input capacity")
    if digest:
        check(hashlib.sha256(raw).hexdigest() == digest, "independent source drift")
    return json.loads(raw)


def minor(columns, rows):
    size = len(rows)
    check(1 <= size <= 4 and len(columns) == size, "independent minor capacity")
    total = 0
    for permutation in itertools.permutations(range(size)):
        inversions = sum(
            permutation[i] > permutation[j]
            for i in range(size)
            for j in range(i + 1, size)
        )
        term = (-1) ** inversions
        for i, j in enumerate(permutation):
            term *= columns[j][rows[i]]
        total += term
    return total


def catalogues():
    axes = [tuple(int(r == i) for r in range(4)) for i in range(4)]
    edges = []
    for i in range(4):
        for j in range(i + 1, 4):
            edge = [0] * 4
            edge[i], edge[j] = 1, -1
            edges.append(tuple(edge))
    graph = axes + edges
    intervals = [
        tuple(int(start <= r < stop) for r in range(4))
        for start in range(4)
        for stop in range(start + 2, 5)
    ]
    network = []
    order = [0, 4, 7, 8, 1, 2, 3, 5, 6, 9]
    for j in order:
        a, b, c, d = graph[j]
        network.append((a + b + c + d, -b - c - d, -c, -d))
    check(network[:4] == axes, "independent tree-coordinate inverse")
    return {"graph": graph, "interval": axes + intervals, "network": network}


def independent_subsets(columns, target=None):
    result = [(0, int(target is not None))]
    for size in range(1, 5 - int(target is not None)):
        for indices in itertools.combinations(range(10), size):
            selected = [columns[j] for j in indices]
            if target is not None:
                selected.append(target)
            rank = len(selected)
            if any(
                minor(selected, rows) for rows in itertools.combinations(range(4), rank)
            ):
                result.append((sum(1 << j for j in indices), rank))
    return result


def xor_solutions(columns):
    vectors = [sum((value % 2) << r for r, value in enumerate(c)) for c in columns]
    images = [0] * 1024
    for mask in range(1, 1024):
        low = mask & -mask
        images[mask] = images[mask ^ low] ^ vectors[low.bit_length() - 1]
    return [
        [mask for mask, image in enumerate(images) if image == 1 << axis]
        for axis in range(4)
    ]


def check_dictionary(columns, expected):
    counts = {"-1": 0, "0": 0, "1": 0}
    for size in range(1, 5):
        for indices in itertools.combinations(range(10), size):
            for rows in itertools.combinations(range(4), size):
                value = minor([columns[i] for i in indices], rows)
                check(value in (-1, 0, 1), "independent non-TU minor")
                counts[str(value)] += 1
    bases = independent_subsets(columns)
    augmented = [
        independent_subsets(columns, tuple(int(r == a) for r in range(4)))
        for a in range(4)
    ]
    solutions = xor_solutions(columns)
    stream = bytearray()
    for active in range(1024):
        rank = max(size for mask, size in bases if not mask & ~active)
        for axis in range(4):
            added = max(size for mask, size in augmented[axis] if not mask & ~active)
            rational = added <= rank
            binary = any(not mask & ~active for mask in solutions[axis])
            check(rational == binary, "independent rational/binary span")
            stream.append(rational)
    check(counts == expected["minors"], "independent minor receipt")
    check(sum(stream) == expected["feasible_per_field"], "independent feasible count")
    check(len(stream) == expected["requests_per_field"], "independent request count")
    check(
        hashlib.sha256(stream).hexdigest() == expected["span_sha256"],
        "independent span digest",
    )
    return solutions


def pairing(a, b):
    return sum(((a >> bit) % 2) * ((b >> bit) % 2) for bit in range(9)) % 2


def explicit_rank(matrix):
    work = [list(row) for row in matrix]
    height = len(work)
    width = len(work[0]) if height else 0
    check(height <= 224 and width <= 224, "independent rank capacity")
    pivot = 0
    for col in range(width):
        found = next((r for r in range(pivot, height) if work[r][col]), None)
        if found is None:
            continue
        work[pivot], work[found] = work[found], work[pivot]
        for r in range(pivot + 1, height):
            if work[r][col]:
                work[r] = [
                    (a + b) % 2 for a, b in zip(work[r], work[pivot], strict=True)
                ]
        pivot += 1
    return pivot


def source():
    data = load(
        HERE.parent.parent
        / "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json",
        "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa",
    )
    fixture = load(
        HERE / "RETAINED-RANK32.json",
        "2e990b02186660c68d9d38cabc864d662b01458b3eafeab774a8b8406bbfb57b",
    )
    labels = [row["q"] for row in data["recipes"]]
    groups = fixture["orthonormal_groups"]
    check(
        sorted(itertools.chain.from_iterable(groups)) == list(range(112)),
        "independent partition",
    )
    halves, paired = [], {}
    for group in groups:
        check(len(group) % 2 == 0, "independent even group")
        for i, j in itertools.product(group, repeat=2):
            check(pairing(labels[i], labels[j]) == int(i == j), "independent Gram-I")
        halves.extend([set(group[::2]), set(group[1::2])])
        for offset in range(0, len(group), 2):
            plane = group[offset : offset + 2]
            for port in plane:
                paired[port] = plane
    return labels, halves, paired


def bill(query, reader, labels, paired):
    rows = set(itertools.chain.from_iterable(paired[i] for i in range(112) if query[i]))
    cols = set(
        itertools.chain.from_iterable(paired[i] for i in range(112) if reader[i])
    )
    return explicit_rank(
        [[pairing(labels[i], labels[j]) for j in sorted(cols)] for i in sorted(rows)]
    )


def literal_readers(columns, halves):
    selected = [halves[i] for i in (0, 1, 2, 30)]
    row_scale = [2, 3, 5, 7]
    col_scale = [Fraction((-1) ** j * (j + 1), j % 3 + 1) for j in range(10)]
    queries = [
        [
            sum(
                row_scale[r] * col_scale[j] * column[r]
                for r in range(4)
                if p in selected[r]
            )
            for p in range(112)
        ]
        for j, column in enumerate(columns)
    ]
    readers = [[Fraction(0)] * 112 for _ in range(10)]
    for port in range(112):
        target = [int(port in half) for half in selected]
        tail = [
            Fraction(((port + 1) * (j + 2)) % 7 - 3, j % 3 + 1) for j in range(4, 10)
        ]
        if any(target):
            axis = target.index(1)
            chosen = next(j for j in range(4, 10) if columns[j][axis])
            tail = [
                Fraction(
                    int(j == chosen),
                    row_scale[axis] * col_scale[chosen] * columns[chosen][axis],
                )
                for j in range(4, 10)
            ]
        for r in range(4):
            residual = target[r] - sum(
                tail[j - 4] * row_scale[r] * col_scale[j] * columns[j][r]
                for j in range(4, 10)
            )
            readers[r][port] = residual / (row_scale[r] * col_scale[r])
        for j in range(4, 10):
            readers[j][port] = tail[j - 4]
    return queries, readers, selected


def check_literal(columns, solutions, geometry, expected):
    labels, halves, paired = geometry
    queries, readers, selected = literal_readers(columns, halves)
    new_readers = [[0] * 112 for _ in range(10)]
    new_queries = [
        [sum(c[r] for r in range(4) if p in selected[r]) % 2 for p in range(112)]
        for c in columns
    ]
    for port in range(112):
        target = next((i for i in range(4) if port in selected[i]), None)
        if target is not None:
            active = sum(1 << j for j in range(10) if readers[j][port])
            choice = next(mask for mask in solutions[target] if not mask & ~active)
            for j in range(10):
                new_readers[j][port] = (choice >> j) % 2
    for p, q in itertools.product(range(112), repeat=2):
        target = int(any(p in h and q in h for h in selected))
        actual = sum(readers[j][p] * queries[j][q] for j in range(10))
        binary = sum(new_readers[j][p] * new_queries[j][q] for j in range(10)) % 2
        check(actual == target and binary == target, "independent literal operator")
    before = [bill(queries[j], readers[j], labels, paired) for j in range(10)]
    after = [bill(new_queries[j], new_readers[j], labels, paired) for j in range(10)]
    check(
        before == expected["before"] and after == expected["after"],
        "independent literal bills",
    )
    check(sum(after) >= expected["floor"], "independent floor")
    check(
        all(
            not new_readers[j][p] or readers[j][p]
            for j in range(10)
            for p in range(112)
        ),
        "independent reader containment",
    )
    return 25088


def expanded_control(geometry):
    labels, halves, paired = geometry
    expanded = []
    for p in range(112):
        for a in range(2):
            row = []
            for q in range(112):
                same = any(p in half and q in half for half in halves)
                row.extend(
                    int(same) * pairing(labels[paired[p][a]], labels[paired[q][b]])
                    for b in range(2)
                )
            expanded.append(row)
    check(
        expanded == [[int(i == j) for j in range(224)] for i in range(224)],
        "independent expanded entries",
    )
    check(explicit_rank(expanded) == 224, "independent expanded rank")


def pairing_contraction(expected):
    labels = [1, 2, 4, 8] + [15 - (1 << j) for j in range(4)]
    matrix = [[pairing(a, b) for b in labels] for a in labels]
    check(explicit_rank(matrix) == 4, "independent separating pairing rank")
    for start in (0, 4):
        check(
            [row[start : start + 4] for row in matrix[start : start + 4]]
            == [[int(i == j) for j in range(4)] for i in range(4)],
            "independent separating Gram-I4",
        )
    for row in range(1, 8):
        if matrix[row][0]:
            matrix[row] = [
                (a + b) % 2 for a, b in zip(matrix[row], matrix[0], strict=True)
            ]
    quotient = [row[1:] for row in matrix[1:]]
    columns = list(zip(*quotient, strict=True))
    check(
        len(set(columns)) == 7 and all(any(c) for c in columns),
        "independent seven points",
    )
    check(explicit_rank(quotient) == 3, "independent Fano quotient rank")
    lines = [
        list(t)
        for t in itertools.combinations(range(7), 3)
        if all(sum(columns[j][r] for j in t) % 2 == 0 for r in range(7))
    ]
    check(lines == expected["Fano_lines"] and len(lines) == 7, "independent Fano lines")
    check(
        expected["TU_pairing_signing_exists"] is False, "independent comparison scope"
    )


def main():
    receipt = load(HERE / "RESULT.json")
    check(
        type(receipt["whole_K_floor"]) is int and receipt["whole_K_floor"] == 224,
        "independent whole-K floor",
    )
    geometry = source()
    expanded_control(geometry)
    pairing_contraction(receipt["nonregular_pairing"])
    for name, columns in catalogues().items():
        solutions = check_dictionary(columns, receipt["dictionaries"][name])
        check_literal(columns, solutions, geometry, receipt["factorizations"][name])
    triangle = [(1, 1, 0), (1, 0, 1), (0, 1, 1)]
    check(minor(triangle, (0, 1, 2)) == -2, "independent determinant-two control")
    check(
        all(sum(c) % 2 == 0 for c in triangle), "independent binary even-span control"
    )
    check(
        [
            sum(Fraction(s, 2) * triangle[j][r] for j, s in enumerate((1, 1, -1)))
            for r in range(3)
        ]
        == [1, 0, 0],
        "independent rational triangle control",
    )
    print(
        "PASS_INDEPENDENT_REGULAR_QUERY_FLOOR minors=3000 "
        "requests=12288 literal_entries=75264"
    )


if __name__ == "__main__":
    main()
