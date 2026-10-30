#!/usr/bin/env python3
"""Exact finite controls for the regular-query theorem. Nick Petalas, Apache-2.0."""

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
DATA_PATH = "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"
DATA_HASH = "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"
FIXTURE_HASH = "2e990b02186660c68d9d38cabc864d662b01458b3eafeab774a8b8406bbfb57b"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def read_json(path, limit, digest=None):
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    require(len(raw) <= limit, "input capacity")
    if digest is not None:
        require(hashlib.sha256(raw).hexdigest() == digest, "source drift")
    return json.loads(raw, object_pairs_hook=unique_object)


def solve(columns, target, modulus=0):
    """Return one exact solution, with free variables zero, or None."""
    height, width = len(target), len(columns)
    require(1 <= height <= 4 and width <= 10, "solve capacity")
    require(all(len(c) == height for c in columns), "column shape")
    require(modulus in (0, 2, 3, 5), "coefficient field")
    rows = [
        [Fraction(c[r]) for c in columns] + [Fraction(target[r])] for r in range(height)
    ]
    if modulus:
        require(
            all(x.denominator == 1 for row in rows for x in row),
            "nonintegral finite-field entry",
        )
        rows = [[int(x) % modulus for x in row] for row in rows]
    pivots = []
    for col in range(width):
        found = next((r for r in range(len(pivots), height) if rows[r][col]), None)
        if found is None:
            continue
        pivot = len(pivots)
        rows[pivot], rows[found] = rows[found], rows[pivot]
        inverse = (
            pow(rows[pivot][col], -1, modulus) if modulus else 1 / rows[pivot][col]
        )
        rows[pivot] = [x * inverse for x in rows[pivot]]
        if modulus:
            rows[pivot] = [x % modulus for x in rows[pivot]]
        for r in range(height):
            if r != pivot:
                scale = rows[r][col]
                rows[r] = [
                    a - scale * b for a, b in zip(rows[r], rows[pivot], strict=True)
                ]
                if modulus:
                    rows[r] = [x % modulus for x in rows[r]]
        pivots.append(col)
    if any(not any(row[:width]) and row[width] for row in rows):
        return None
    result = [0] * width
    for r, col in enumerate(pivots):
        result[col] = rows[r][width]
    return result


def determinant(rows):
    """Fraction-free elimination, independent of the rectangular solver."""
    size = len(rows)
    require(1 <= size <= 4 and all(len(r) == size for r in rows), "minor capacity")
    work = [list(row) for row in rows]
    previous, sign = 1, 1
    for col in range(size - 1):
        pivot = next((r for r in range(col, size) if work[r][col]), None)
        if pivot is None:
            return 0
        if pivot != col:
            work[col], work[pivot] = work[pivot], work[col]
            sign = -sign
        value = work[col][col]
        for r in range(col + 1, size):
            for c in range(col + 1, size):
                numerator = work[r][c] * value - work[r][col] * work[col][c]
                require(numerator % previous == 0, "Bareiss exact division")
                work[r][c] = numerator // previous
        previous = value
    return sign * work[-1][-1]


def dictionaries():
    unit = [tuple(int(i == j) for i in range(4)) for j in range(4)]
    graph = unit + [
        tuple(int(r == i) - int(r == j) for r in range(4))
        for i, j in itertools.combinations(range(4), 2)
    ]
    interval = unit + [
        tuple(int(i <= r <= j) for r in range(4))
        for i in range(4)
        for j in range(i + 1, 4)
    ]
    order = [0, 4, 7, 8] + [i for i in range(10) if i not in (0, 4, 7, 8)]
    basis = [graph[i] for i in order[:4]]
    network = []
    for col in order:
        solution = solve(basis, graph[col])
        require(solution is not None, "tree basis")
        require(all(x.denominator == 1 for x in solution), "integral network")
        network.append(tuple(map(int, solution)))
    return {"graph": graph, "interval": interval, "network": network}


def dictionary_receipt(columns):
    require(
        len(columns) == 10 and all(len(c) == 4 for c in columns), "dictionary capacity"
    )
    minors = {"-1": 0, "0": 0, "1": 0}
    for size in range(1, 5):
        for selected in itertools.combinations(columns, size):
            for rows in itertools.combinations(range(4), size):
                value = determinant([[c[r] for c in selected] for r in rows])
                require(value in (-1, 0, 1), "non-TU dictionary")
                minors[str(value)] += 1
    hashes = [hashlib.sha256() for _ in range(4)]
    feasible = 0
    for mask in range(1 << 10):
        active = [c for j, c in enumerate(columns) if mask >> j & 1]
        for axis in range(4):
            target = tuple(int(axis == r) for r in range(4))
            decisions = [solve(active, target, p) is not None for p in (0, 2, 3, 5)]
            require(len(set(decisions)) == 1, "field-dependent axis span")
            feasible += decisions[0]
            for stream, decision in zip(hashes, decisions, strict=True):
                stream.update(bytes([decision]))
    digests = [stream.hexdigest() for stream in hashes]
    require(len(set(digests)) == 1, "span stream mismatch")
    return {
        "minors": minors,
        "requests_per_field": 4096,
        "feasible_per_field": feasible,
        "span_sha256": digests[0],
    }


def geometry():
    data = read_json(PACKAGE.parent.parent / DATA_PATH, 1 << 20, DATA_HASH)
    fixture = read_json(PACKAGE / "RETAINED-RANK32.json", 32768, FIXTURE_HASH)
    recipes = data["recipes"]
    require(len(recipes) == 112, "port count")
    require([r["port"] for r in recipes] == list(range(112)), "port ordering")
    labels = [r["q"] for r in recipes]
    require(all(type(q) is int and 0 < q < 512 for q in labels), "binary labels")
    groups = fixture["orthonormal_groups"]
    require(len(groups) == 16, "group count")
    require(all(len(g) in (4, 6, 8) for g in groups), "even group sizes")
    require(all(type(p) is int for g in groups for p in g), "port type")
    require(sorted(p for g in groups for p in g) == list(range(112)), "partition")
    indicators, planes, group_sizes = [], [None] * 112, []
    for group in groups:
        for i in group:
            for j in group:
                require(
                    (labels[i] & labels[j]).bit_count() % 2 == (i == j), "Gram-I group"
                )
        for offset in range(0, len(group), 2):
            plane = tuple(group[offset : offset + 2])
            for port in plane:
                planes[port] = plane
        for side in range(2):
            indicators.append(tuple(int(p in group[side::2]) for p in range(112)))
            group_sizes.append(len(group))
    return labels, planes, indicators, group_sizes


def binary_rank(rows):
    require(
        len(rows) <= 224 and all(type(x) is int and 0 <= x < 1 << 224 for x in rows),
        "binary rank capacity",
    )
    basis = {}
    for row in rows:
        for _ in range(224):
            if not row:
                break
            pivot = row.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = row
                break
            row ^= basis[pivot]
        else:
            raise ValueError("binary elimination exhausted")
    return len(basis)


def tariff(query, reader, labels, planes):
    require(
        len(query) == len(reader) == len(labels) == len(planes) == 112, "tariff shape"
    )
    source = sorted({p for i, value in enumerate(query) if value for p in planes[i]})
    sink = sorted({p for i, value in enumerate(reader) if value for p in planes[i]})
    rows = [
        sum(((labels[p] & labels[q]).bit_count() % 2) << j for j, q in enumerate(sink))
        for p in source
    ]
    return binary_rank(rows)


def check_operator(queries, readers, indicators, modulus=0):
    require(1 <= len(queries) == len(readers) <= 32, "operator term capacity")
    require(
        all(len(v) == 112 for v in queries + readers + indicators), "operator shape"
    )
    for p in range(112):
        for q in range(112):
            actual = sum(u[p] * v[q] for u, v in zip(readers, queries, strict=True))
            expected = sum(a[p] * a[q] for a in indicators)
            require(
                (actual - expected) % modulus == 0 if modulus else actual == expected,
                "operator mismatch",
            )
    return 112 * 112


def expanded_identity(labels, planes, indicators):
    membership = [next(j for j, a in enumerate(indicators) if a[p]) for p in range(112)]
    for p in range(112):
        for q in range(112):
            for i in range(2):
                for j in range(2):
                    value = int(membership[p] == membership[q])
                    value *= (
                        labels[planes[p][i]] & labels[planes[q][j]]
                    ).bit_count() % 2
                    require(value == int(p == q and i == j), "expanded identity")
    return 224 * 224


def make_factorization(columns, indicators):
    scales = (2, 3, 5, 7)
    factors = tuple(Fraction((-1) ** j * (j + 1), j % 3 + 1) for j in range(10))
    scaled = [
        tuple(scales[r] * factors[j] * c[r] for r in range(4))
        for j, c in enumerate(columns)
    ]
    queries = [
        tuple(sum(c[r] * indicators[r][p] for r in range(4)) for p in range(112))
        for c in scaled
    ]
    readers = [[Fraction(0)] * 112 for _ in range(10)]
    for port in range(112):
        tail = [
            Fraction(((port + 1) * (j + 2)) % 7 - 3, j % 3 + 1) for j in range(4, 10)
        ]
        axis = next((r for r in range(4) if indicators[r][port]), None)
        if axis is not None:
            chosen = next(j for j in range(4, 10) if scaled[j][axis])
            tail = [
                Fraction(int(j == chosen), scaled[chosen][axis]) for j in range(4, 10)
            ]
        residual = [
            indicators[r][port] - sum(tail[j - 4] * scaled[j][r] for j in range(4, 10))
            for r in range(4)
        ]
        head = solve(scaled[:4], residual)
        require(head is not None, "axis basis lost")
        for j, value in enumerate(head + tail):
            readers[j][port] = value
    return queries, readers


def transfer(columns, readers, indicators):
    result = [[0] * 112 for _ in columns]
    for port in range(112):
        target = [a[port] for a in indicators]
        if not any(target):
            continue
        active = [j for j, reader in enumerate(readers) if reader[port]]
        solution = solve([columns[j] for j in active], target, 2)
        require(solution is not None, "support transfer failed")
        for j, value in zip(active, solution, strict=True):
            result[j][port] = value
    require(
        all(
            not value or readers[j][p]
            for j, row in enumerate(result)
            for p, value in enumerate(row)
        ),
        "reader support grew",
    )
    return result


def factorization_receipt(columns, source):
    labels, planes, all_indicators, sizes = source
    selected = [0, 1, 2, 30]
    indicators = [all_indicators[j] for j in selected]
    queries, readers = make_factorization(columns, indicators)
    entries = check_operator(queries, readers, indicators)
    converted = transfer(columns, readers, indicators)
    binary_queries = [
        tuple(sum(c[r] * indicators[r][p] for r in range(4)) % 2 for p in range(112))
        for c in columns
    ]
    entries += check_operator(binary_queries, converted, indicators, 2)
    before = [
        tariff(q, u, labels, planes) for q, u in zip(queries, readers, strict=True)
    ]
    after = [
        tariff(q, u, labels, planes)
        for q, u in zip(binary_queries, converted, strict=True)
    ]
    require(all(a <= b for a, b in zip(after, before, strict=True)), "tariff grew")
    floor = sum(sizes[j] for j in selected)
    require(sum(after) >= floor, "literal reader floor")
    require(
        any(
            readers[j][p] == 0 and indicators[j][p]
            for j in range(4)
            for p in range(112)
        ),
        "nonaxis transfer missing",
    )
    outside = [p for p in range(112) if not any(a[p] for a in indicators)]
    cancellations = sum(bool(u[p]) for u in readers for p in outside)
    require(cancellations > 0, "global cancellation control missing")
    return {
        "targets": selected,
        "floor": floor,
        "before": before,
        "after": after,
        "operator_entries": entries,
        "outside_reader_nonzeros": cancellations,
    }


def nonregular_boundary():
    columns = [(1, 1, 0), (1, 0, 1), (0, 1, 1)]
    target = (1, 0, 0)
    rational = solve(columns, target)
    require(
        rational == [Fraction(1, 2), Fraction(1, 2), Fraction(-1, 2)],
        "odd triangle solve",
    )
    require(solve(columns, target, 2) is None, "nonregular control failed")
    value = determinant([[c[r] for c in columns] for r in range(3)])
    require(abs(value) == 2, "non-TU minor missing")
    return {
        "determinant": value,
        "rational_axis": list(map(str, rational)),
        "binary_axis_feasible": False,
        "meaning": "transfer failure, not a cheaper decoder",
    }


def nonregular_pairing():
    """The query-TU hypothesis does not require a TU-signable pairing."""
    labels = [1, 2, 4, 8, 14, 13, 11, 7]
    for start in (0, 4):
        for i in range(start, start + 4):
            for j in range(start, start + 4):
                require(
                    (labels[i] & labels[j]).bit_count() % 2 == (i == j),
                    "separating Gram-I4 group",
                )
    rows = [
        sum(((a & b).bit_count() % 2) << j for j, b in enumerate(labels))
        for a in labels
    ]
    require(binary_rank(rows) == 4, "separating pairing rank")
    quotient = [label >> 1 for label in labels[1:]]
    require(sorted(quotient) == list(range(1, 8)), "Fano contraction")
    lines = [
        list(triple)
        for triple in itertools.combinations(range(7), 3)
        if quotient[triple[0]] ^ quotient[triple[1]] ^ quotient[triple[2]] == 0
    ]
    require(len(lines) == 7, "Fano line count")
    return {
        "labels": labels,
        "groups": [list(range(4)), list(range(4, 8))],
        "binary_pairing_rank": 4,
        "contracted_column": 0,
        "contracted_labels": quotient,
        "Fano_lines": lines,
        "TU_pairing_signing_exists": False,
        "reason": "column contraction is F7, "
        "nonrepresentable outside characteristic two",
    }


def compute():
    source = geometry()
    labels, planes, indicators, sizes = source
    baseline = [tariff(a, a, labels, planes) for a in indicators]
    require(baseline == sizes and sum(baseline) == 224, "literal sharpness")
    examples = dictionaries()
    return {
        "status": "PASS_REGULAR_QUERY_FLOOR",
        "whole_K_floor": 224,
        "expanded_entries": expanded_identity(labels, planes, indicators),
        "dictionaries": {name: dictionary_receipt(c) for name, c in examples.items()},
        "factorizations": {
            name: factorization_receipt(c, source) for name, c in examples.items()
        },
        "nonregular_boundary": nonregular_boundary(),
        "nonregular_pairing": nonregular_pairing(),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print recomputed receipt")
    args = parser.parse_args()
    result = compute()
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        expected = read_json(PACKAGE / "RESULT.json", 32768)
        require(
            json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True),
            "receipt mismatch",
        )
        print("PASS_REGULAR_QUERY_FLOOR dictionaries=3 all_fields scoped_no_new_kappa")


if __name__ == "__main__":
    main()
