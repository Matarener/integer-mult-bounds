#!/usr/bin/env python3
"""Separate permutation-minor and hereditary-rank certificate. Apache-2.0."""

import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRODUCT = ((0, 0, 0, 0), (0, 1, 2, 3), (0, 2, 3, 1), (0, 3, 1, 2))


def check(condition, message):
    if not condition:
        raise ValueError(message)


def load(path, maximum):
    with path.open("rb") as stream:
        raw = stream.read(maximum + 1)
    check(len(raw) <= maximum, "input size")
    return json.loads(raw)


def columns(t, binary=False):
    basis = [tuple(int(r == c) for r in range(5)) for c in range(5)]
    edges = [(0, 4, 1), (0, 4, t), (1, 4, 1), (2, 4, 1), (3, 4, 1), (1, 2, 1)]
    result = basis.copy()
    for a, b, weight in edges:
        row = [0] * 5
        row[a], row[b] = 1, weight if binary else -weight
        result.append(tuple(row))
    return result + basis[:4]


def det(matrix, binary=False):
    size = len(matrix)
    check(
        1 <= size <= 5 and all(len(row) == size for row in matrix), "minor dimensions"
    )
    total = 0
    for permutation in itertools.permutations(range(size)):
        value = 1
        for r, c in enumerate(permutation):
            value = PRODUCT[value][matrix[r][c]] if binary else value * matrix[r][c]
        if binary:
            total ^= value
        else:
            inversions = sum(
                permutation[a] > permutation[b]
                for a in range(size)
                for b in range(a + 1, size)
            )
            total += (-1 if inversions % 2 else 1) * value
    return total


def minors_and_independent_sets():
    at_zero, at_one, at_omega = columns(0), columns(1), columns(2, True)
    histogram, independent, total = {}, {0: 0}, 0
    allowed = {(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)}
    for size in range(1, 6):
        for chosen in itertools.combinations(range(15), size):
            mask = sum(1 << c for c in chosen)
            for rows in itertools.combinations(range(5), size):
                matrix_zero = [[at_zero[c][r] for c in chosen] for r in rows]
                matrix_one = [[at_one[c][r] for c in chosen] for r in rows]
                a, value_one = det(matrix_zero), det(matrix_one)
                b = value_one - a
                check((a, b) in allowed, "polynomial minor class")
                value_four = det([[at_omega[c][r] for c in chosen] for r in rows], True)
                check(bool(value_four) == bool(a or b), "GF4 minor vanished")
                for t in (-1, 2, 3):
                    check(bool(a + b * t) == bool(a or b), "rational minor vanished")
                key = f"{a},{b}"
                histogram[key] = histogram.get(key, 0) + 1
                if a or b:
                    independent[mask] = size
                total += 1
    return histogram, independent, total


def hereditary_ranks(independent):
    result = bytearray(1 << 15)
    for mask in range(1, 1 << 15):
        best = independent.get(mask, 0)
        for bit in range(15):
            if mask & (1 << bit):
                best = max(best, result[mask ^ (1 << bit)])
        result[mask] = best
    return result


def span_stream(ranks):
    output = bytearray()
    for subset in range(2048):
        for target in range(4):
            marked = 1 << (target + 11)
            other_targets = (15 << 11) ^ marked
            output.append(int(ranks[subset] == ranks[subset | marked]))
            output.append(
                int(
                    ranks[subset | other_targets]
                    < ranks[subset | other_targets | marked]
                )
            )
    return {
        "requests": len(output),
        "sha256": hashlib.sha256(output).hexdigest(),
        "reader_feasible": sum(output[::2]),
        "source_feasible": sum(output[1::2]),
    }


def expanded_check():
    root = HERE.parent.parent
    data = root / "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"
    check(data.stat().st_size <= 1 << 20, "label input size")
    check((HERE / "RETAINED-RANK32.json").stat().st_size <= 32768, "fixture size")
    raw = data.read_bytes()
    check(
        hashlib.sha256(raw).hexdigest()
        == "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa",
        "label bytes",
    )
    fixture_raw = (HERE / "RETAINED-RANK32.json").read_bytes()
    check(
        hashlib.sha256(fixture_raw).hexdigest()
        == "2e990b02186660c68d9d38cabc864d662b01458b3eafeab774a8b8406bbfb57b",
        "fixture bytes",
    )
    labels = [row["q"] for row in json.loads(raw)["recipes"]]
    groups = json.loads(fixture_raw)["orthonormal_groups"]
    check(
        len(labels) == 112 and sorted(p for g in groups for p in g) == list(range(112)),
        "port partition",
    )
    planes, halves = {}, {}
    for group_number, group in enumerate(groups):
        check(len(group) > 0 and len(group) % 2 == 0, "group parity")
        for position, port in enumerate(group):
            planes[port] = group[2 * (position // 2) : 2 * (position // 2) + 2]
            halves[port] = group_number * 2 + position % 2
    count = 0
    for a in range(224):
        for b in range(224):
            p, i = divmod(a, 2)
            q, j = divmod(b, 2)
            gram = (labels[planes[p][i]] & labels[planes[q][j]]).bit_count() & 1
            full = int(halves[p] == halves[q]) * gram
            check(full == int(a == b), "full expansion entry")
            check(
                full * int(halves[p] in (0, 2, 4, 6))
                == int(a == b and halves[p] in (0, 2, 4, 6)),
                "selected expansion entry",
            )
            count += 1
    return count


def main():
    expected = load(HERE / "RESULT.json", 65536)
    histogram, independent, total = minors_and_independent_sets()
    check(histogram == expected["minor_polynomials"], "minor histogram mismatch")
    ranks = hereditary_ranks(independent)
    check(
        hashlib.sha256(ranks).hexdigest() == expected["rank_sha256"],
        "rank stream mismatch",
    )
    check(span_stream(ranks) == expected["spans"], "support-request stream mismatch")
    check(expanded_check() == expected["expanded"]["entries_each"], "expansion count")
    # Four distinct points on the e1,e5 line cannot be represented over F2.
    check(
        all(
            det([[columns(2)[c][r] for c in pair] for r in (0, 4)]) != 0
            for pair in itertools.combinations((0, 4, 5, 6), 2)
        ),
        "U2,4 witness",
    )
    print(f"PASS_INDEPENDENT_MATROID_READER minors={total} subsets=32768 no_new_kappa")


if __name__ == "__main__":
    main()
