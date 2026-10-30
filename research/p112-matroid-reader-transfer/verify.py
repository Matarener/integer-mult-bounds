#!/usr/bin/env python3
"""Finite corroboration of the labelled-matroid reader floor. Apache-2.0."""

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"
DATA_HASH = "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"
FIXTURE_HASH = "2e990b02186660c68d9d38cabc864d662b01458b3eafeab774a8b8406bbfb57b"


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


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


def mul(a, b, field):
    if field == 0:
        return a * b
    require(field == 4 and type(a) is int and type(b) is int, "GF4 operand")
    require(0 <= a < 4 and 0 <= b < 4, "GF4 range")
    result = 0
    for _ in range(2):
        if b & 1:
            result ^= a
        b >>= 1
        a <<= 1
        if a & 4:
            a ^= 7
    return result


def add(a, b, field):
    return a ^ b if field == 4 else a + b


def negative(a, field):
    return a if field == 4 else -a


def inverse(a, field):
    require(a != 0 and field in (0, 4), "nonzero field inverse")
    return mul(a, a, 4) if field == 4 else Fraction(1, a)


def solve(columns, target, field):
    """A particular solution, or None; free variables are zero."""
    height, width = len(target), len(columns)
    require(field in (0, 4) and 1 <= height <= 16 and width <= 15, "solve capacity")
    require(all(len(c) == height for c in columns), "column shape")
    if field == 4:
        require(
            all(type(x) is int and 0 <= x < 4 for c in columns for x in c), "GF4 input"
        )
        require(all(type(x) is int and 0 <= x < 4 for x in target), "GF4 target")
    rows = [[c[r] for c in columns] + [target[r]] for r in range(height)]
    pivots = []
    for col in range(width):
        found = next((r for r in range(len(pivots), height) if rows[r][col]), None)
        if found is None:
            continue
        pivot = len(pivots)
        rows[pivot], rows[found] = rows[found], rows[pivot]
        scale = inverse(rows[pivot][col], field)
        rows[pivot] = [mul(x, scale, field) for x in rows[pivot]]
        for r in range(height):
            if r != pivot:
                scale = negative(rows[r][col], field)
                rows[r] = [
                    add(a, mul(scale, b, field), field)
                    for a, b in zip(rows[r], rows[pivot], strict=True)
                ]
        pivots.append(col)
    if any(not any(row[:width]) and row[width] for row in rows):
        return None
    result = [0] * width
    for r, col in enumerate(pivots):
        result[col] = rows[r][width]
    return result


def extend_basis(basis, column, field):
    value = list(column)
    for pivot, row in basis:
        scale = negative(value[pivot], field)
        value = [
            add(a, mul(scale, b, field), field) for a, b in zip(value, row, strict=True)
        ]
    pivot = next((i for i, x in enumerate(value) if x), None)
    if pivot is None:
        return basis
    scale = inverse(value[pivot], field)
    value = tuple(mul(x, scale, field) for x in value)
    return tuple(sorted((*basis, (pivot, value))))


def ranks(columns, field):
    require(len(columns) == 15 and all(len(c) == 5 for c in columns), "rank capacity")
    bases = [()] * (1 << 15)
    for mask in range(1, 1 << 15):
        bit = mask & -mask
        bases[mask] = extend_basis(
            bases[mask ^ bit], columns[bit.bit_length() - 1], field
        )
    return bytes(len(b) for b in bases)


def dictionary(parameter, field=0):
    require(field in (0, 4), "dictionary field")
    unit = [tuple(int(i == j) for i in range(5)) for j in range(5)]
    edges = [(0, 4, 1), (0, 4, parameter), (1, 4, 1), (2, 4, 1), (3, 4, 1), (1, 2, 1)]
    columns = unit + [
        tuple(
            add(int(r == i), negative(gain if r == j else 0, field), field)
            for r in range(5)
        )
        for i, j, gain in edges
    ]
    return columns + unit[:4]


def determinant(rows):
    size = len(rows)
    require(1 <= size <= 5 and all(len(row) == size for row in rows), "minor capacity")
    work = [list(row) for row in rows]
    divisor, sign = 1, 1
    for c in range(size - 1):
        pivot = next((r for r in range(c, size) if work[r][c]), None)
        if pivot is None:
            return 0
        if pivot != c:
            work[c], work[pivot] = work[pivot], work[c]
            sign = -sign
        value = work[c][c]
        for r in range(c + 1, size):
            for j in range(c + 1, size):
                numerator = work[r][j] * value - work[r][c] * work[c][j]
                require(numerator % divisor == 0, "Bareiss division")
                work[r][j] = numerator // divisor
        divisor = value
    return sign * work[-1][-1]


def minor_receipt():
    zero, one = dictionary(0), dictionary(1)
    histogram = {}
    allowed = {(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)}
    for size in range(1, 6):
        for cols in itertools.combinations(range(15), size):
            for rows in itertools.combinations(range(5), size):
                a = determinant([[zero[c][r] for c in cols] for r in rows])
                b = determinant([[one[c][r] for c in cols] for r in rows]) - a
                require((a, b) in allowed, "non-near-unimodular minor")
                key = f"{a},{b}"
                histogram[key] = histogram.get(key, 0) + 1
    return histogram


def span_receipt(rank_bytes):
    stream = bytearray()
    for mask in range(1 << 11):
        for j in range(4):
            axis = 1 << (11 + j)
            others = sum(1 << (11 + k) for k in range(4) if k != j)
            reader = rank_bytes[mask | axis] == rank_bytes[mask]
            source = rank_bytes[mask | others | axis] > rank_bytes[mask | others]
            stream.extend((reader, source))
    return {
        "requests": 16384,
        "sha256": hashlib.sha256(stream).hexdigest(),
        "reader_feasible": sum(stream[::2]),
        "source_feasible": sum(stream[1::2]),
    }


def geometry(labels, groups):
    n = len(labels)
    require(
        1 <= n <= 112 and sorted(p for g in groups for p in g) == list(range(n)),
        "partition",
    )
    require(all(type(x) is int and 0 < x < 512 for x in labels), "label domain")
    planes, indicators, sizes = [()] * n, [], []
    for group in groups:
        require(len(group) > 0 and len(group) % 2 == 0, "even group")
        require(
            all(
                (labels[p] & labels[q]).bit_count() % 2 == int(p == q)
                for p in group
                for q in group
            ),
            "Gram-I group",
        )
        for offset in range(0, len(group), 2):
            for p in group[offset : offset + 2]:
                planes[p] = tuple(group[offset : offset + 2])
        for side in range(2):
            indicators.append(tuple(int(p in group[side::2]) for p in range(n)))
            sizes.append(len(group))
    return labels, planes, indicators, sizes


def literal_geometry():
    data = read_json(HERE.parent.parent / DATA, 1 << 20, DATA_HASH)
    fixture = read_json(HERE / "RETAINED-RANK32.json", 32768, FIXTURE_HASH)
    require([r["port"] for r in data["recipes"]] == list(range(112)), "port order")
    return geometry([r["q"] for r in data["recipes"]], fixture["orthonormal_groups"])


def binary_rank(rows):
    require(
        len(rows) <= 112 and all(type(r) is int and 0 <= r < 1 << 112 for r in rows),
        "binary capacity",
    )
    basis = {}
    for row in rows:
        for _ in range(112):
            if not row:
                break
            pivot = row.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = row
                break
            row ^= basis[pivot]
        else:
            raise ValueError("binary elimination exhaustion")
    return len(basis)


def tariff(query, reader, source):
    labels, planes, _, _ = source
    require(len(query) == len(reader) == len(labels), "tariff shape")
    left = sorted({p for i, x in enumerate(query) if x for p in planes[i]})
    right = sorted({p for i, x in enumerate(reader) if x for p in planes[i]})
    return binary_rank(
        [
            sum(
                ((labels[p] & labels[q]).bit_count() % 2) << j
                for j, q in enumerate(right)
            )
            for p in left
        ]
    )


def make_factors(parameter, targets):
    columns = dictionary(parameter)[:11]
    n = len(targets[0])
    external = tuple(Fraction((p * 3) % 7 - 3, 2) for p in range(n))
    embedding = [*targets, external]
    basis = ()
    for p in range(n):
        basis = extend_basis(basis, [v[p] for v in embedding], 0)
    require(len(basis) == 5, "external embedding not injective")
    queries = [
        tuple(sum(c[j] * embedding[j][p] for j in range(5)) for p in range(n))
        for c in columns
    ]
    readers = [[Fraction(0)] * n for _ in columns]
    for p in range(n):
        tail = [Fraction(((p + 1) * (j + 1)) % 11 - 5, j % 3 + 1) for j in range(6)]
        for i in range(5):
            readers[i][p] = (targets[i][p] if i < 4 else 0) - sum(
                columns[5 + j][i] * tail[j] for j in range(6)
            )
        for j in range(6):
            readers[5 + j][p] = tail[j]
    return queries, readers


def transfer(queries, readers, targets, representation):
    require(
        len(queries) == len(readers) == 11 and len(targets) == 4, "transfer capacity"
    )
    require(
        len(representation) == 15 and all(len(c) == 5 for c in representation),
        "representation shape",
    )
    n = len(targets[0])
    require(
        1 <= n <= 112 and all(len(v) == n for v in queries + readers + targets),
        "port shape",
    )
    qnew, unew = [[0] * n for _ in queries], [[0] * n for _ in readers]
    for p in range(n):
        values = [v[p] for v in targets]
        require(
            sum(bool(x) for x in values) <= 1 and all(x in (0, 1) for x in values),
            "disjoint targets",
        )
        if not any(values):
            continue
        zero = [i for i, q in enumerate(queries) if not q[p]]
        rows = [representation[i] for i in zero] + representation[11:]
        functional = solve(list(zip(*rows, strict=True)), [0] * len(zero) + values, 4)
        require(functional is not None, "source separation failed")
        for i in range(11):
            for j in range(5):
                qnew[i][p] ^= mul(functional[j], representation[i][j], 4)
        active = [i for i, u in enumerate(readers) if u[p]]
        axis = values.index(1)
        coefficients = solve(
            [representation[i] for i in active], representation[11 + axis], 4
        )
        require(coefficients is not None, "reader span failed")
        for i, coefficient in zip(active, coefficients, strict=True):
            unew[i][p] = coefficient
    require(
        all(not qnew[i][p] or queries[i][p] for i in range(11) for p in range(n)),
        "query support grew",
    )
    require(
        all(not unew[i][p] or readers[i][p] for i in range(11) for p in range(n)),
        "reader support grew",
    )
    return qnew, unew


def check_operator(queries, readers, targets, field):
    n = len(targets[0])
    require(1 <= n <= 112 and len(queries) == len(readers) == 11, "operator capacity")
    for p in range(n):
        for q in range(n):
            actual = 0
            for u, v in zip(readers, queries, strict=True):
                actual = add(actual, mul(u[p], v[q], field), field)
            require(actual == sum(a[p] * a[q] for a in targets), "operator mismatch")
    return n * n


def factor_receipt(parameter, source, selected):
    targets = [source[2][j] for j in selected]
    queries, readers = make_factors(parameter, targets)
    converted_q, converted_u = transfer(queries, readers, targets, dictionary(2, 4))
    entries = check_operator(queries, readers, targets, 0)
    entries += check_operator(converted_q, converted_u, targets, 4)
    before = [tariff(q, u, source) for q, u in zip(queries, readers, strict=True)]
    after = [
        tariff(q, u, source) for q, u in zip(converted_q, converted_u, strict=True)
    ]
    floor = sum(source[3][j] for j in selected)
    require(all(a <= b for a, b in zip(after, before, strict=True)), "tariff grew")
    require(sum(after) >= floor, "reader floor failed")
    outside = [p for p in range(len(targets[0])) if not any(a[p] for a in targets)]
    return {
        "parameter": parameter,
        "operator_entries": entries,
        "floor": floor,
        "before": before,
        "after": after,
        "outside_query_entries": sum(bool(q[p]) for q in queries for p in outside),
        "outside_reader_entries": sum(bool(u[p]) for u in readers for p in outside),
    }


def expanded_receipt(source, selected):
    labels, planes, indicators, _ = source
    membership = [
        next(j for j, a in enumerate(indicators) if a[p]) for p in range(len(labels))
    ]
    count = 0
    for p in range(len(labels)):
        for q in range(len(labels)):
            for i in range(2):
                for j in range(2):
                    value = (
                        int(membership[p] == membership[q])
                        * (labels[planes[p][i]] & labels[planes[q][j]]).bit_count()
                        % 2
                    )
                    require(value == int(p == q and i == j), "expanded identity")
                    restricted = value * int(membership[p] in selected)
                    require(
                        restricted
                        == int(p == q and i == j and membership[p] in selected),
                        "selected expansion",
                    )
                    count += 1
    return {
        "entries_each": count,
        "selected_rank": sum(source[3][j] for j in selected),
        "full_rank": 2 * len(labels),
    }


def compute():
    representations = [ranks(dictionary(t), 0) for t in (2, 3, -1)]
    representations.append(ranks(dictionary(2, 4), 4))
    require(len(set(representations)) == 1, "subset rank mismatch")
    source = literal_geometry()
    selected = [0, 2, 4, 6]
    small = geometry(
        [1 << j for j in range(8)] * 2, [list(range(8)), list(range(8, 16))]
    )
    fixtures = [factor_receipt(t, source, selected) for t in (2, 3, -1)]
    fixtures += [factor_receipt(t, small, [0, 1, 2, 3]) for t in (2, 3, -1)]
    return {
        "claim": "char2-representable-augmented-matroid-reader-floor",
        "minor_polynomials": minor_receipt(),
        "subset_count": 32768,
        "rank_sha256": hashlib.sha256(representations[0]).hexdigest(),
        "spans": span_receipt(representations[0]),
        "fixtures": fixtures,
        "expanded": expanded_receipt(source, selected),
        "literal_attaining_bill": sum(tariff(a, a, source) for a in source[2]),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print recomputed receipt")
    args = parser.parse_args()
    result = compute()
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        require(result == read_json(HERE / "RESULT.json", 65536), "receipt mismatch")
        print("PASS_MATROID_READER_TRANSFER subsets=32768 fixtures=6 no_new_kappa")


if __name__ == "__main__":
    main()
