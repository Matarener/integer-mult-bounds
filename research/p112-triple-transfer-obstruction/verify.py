#!/usr/bin/env python3
"""Exact three-target support obstruction and bounded literal census. Apache-2.0."""

import argparse
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"
DATA_HASH = "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"
GROUP_HASH = "2e990b02186660c68d9d38cabc864d662b01458b3eafeab774a8b8406bbfb57b"
Q = ((1, 1, 0, 1), (1, 1, 0, 1), (1, 0, 1, 1), (0, 1, 1, 1))
U2 = ((0, 0, -2, 2), (1, 1, -1, 0), (0, -2, 0, 2), (-2, 0, 0, 2))
TARGET = ((1, 1, 0, 0), (1, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1))


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def read_json(path, digest=None):
    with path.open("rb") as stream:
        raw = stream.read((1 << 20) + 1)
    require(len(raw) <= 1 << 20, "input capacity")
    if digest is not None:
        require(hashlib.sha256(raw).hexdigest() == digest, "source drift")
    return json.loads(raw, object_pairs_hook=unique_object)


def add(a, b, field):
    return a ^ b if field in (4, 8) else (a + b) % field


def mul(a, b, field):
    if field not in (4, 8):
        return a * b % field
    value, top, polynomial = 0, field, 7 if field == 4 else 11
    for _ in range(3):
        if b & 1:
            value ^= a
        b >>= 1
        a <<= 1
        if a & top:
            a ^= polynomial
    return value


def inverse(a, field):
    require(a != 0 and field in (2, 3, 4, 5, 7, 8), "inverse domain")
    result = 1
    for _ in range(field - 2):
        result = mul(result, a, field)
    require(mul(a, result, field) == 1, "inverse invariant")
    return result


def rank(columns, field):
    require(field in (2, 3, 4, 5, 7, 8), "rank field")
    require(len(columns) <= 8 and all(len(c) == 4 for c in columns), "rank capacity")
    require(
        all(type(x) is int and 0 <= x < field for c in columns for x in c),
        "rank domain",
    )
    rows = [[c[r] for c in columns] for r in range(4)]
    pivot = 0
    for col in range(len(columns)):
        found = next((r for r in range(pivot, 4) if rows[r][col]), None)
        if found is None:
            continue
        rows[pivot], rows[found] = rows[found], rows[pivot]
        scale = inverse(rows[pivot][col], field)
        rows[pivot] = [mul(x, scale, field) for x in rows[pivot]]
        for r in range(pivot + 1, 4):
            scale = rows[r][col]
            if field not in (4, 8):
                scale = -scale % field
            rows[r] = [
                add(a, mul(scale, b, field), field)
                for a, b in zip(rows[r], rows[pivot], strict=True)
            ]
        pivot += 1
    return pivot


def field_census(field):
    require(field in (2, 4, 8), "characteristic-two census field")
    axes = ((1, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1))
    candidates, pairs, completions = 0, 0, 0
    for a, b, c, d, e in itertools.product(range(1, field), repeat=5):
        columns = [(1, 1, a, 0), (1, 1, 0, b), (0, 0, 1, c), (1, 1, d, e)]
        candidates += 1
        if not all(
            rank([columns[2 - j], columns[3], axis], field) == 2
            for j, axis in enumerate(axes)
        ):
            continue
        pairs += 1
        edge_rank = rank(columns[:3], field)
        require(edge_rank == 2, "normalized triangle rank")
        if rank([*columns[:3], axes[0]], field) == edge_rank:
            completions += 1
    require(completions == 0, "unexpected characteristic-two completion")
    return {
        "field": field,
        "candidates": candidates,
        "pair_feasible": pairs,
        "completions": completions,
    }


def binary_basis(values):
    basis = {}
    require(len(values) <= 112 and all(0 <= x < 512 for x in values), "binary capacity")
    for value in values:
        for _ in range(9):
            if not value:
                break
            pivot = value.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = value
                break
            value ^= basis[pivot]
        else:
            require(value == 0, "binary elimination exhaustion")
    return tuple(basis[p] for p in sorted(basis, reverse=True))


def geometry():
    data = read_json(HERE.parent.parent / DATA, DATA_HASH)
    retained = read_json(HERE / "RETAINED-RANK32.json", GROUP_HASH)
    require([r["port"] for r in data["recipes"]] == list(range(112)), "port order")
    labels = tuple(r["q"] for r in data["recipes"])
    groups = retained["orthonormal_groups"]
    require(len(groups) == 16, "group count")
    require(
        sorted(p for group in groups for p in group) == list(range(112)), "partition"
    )
    planes, targets, sizes = [0] * 112, [], []
    for group in groups:
        require(0 < len(group) <= 8 and len(group) % 2 == 0, "even group")
        require(
            all(
                (labels[p] & labels[q]).bit_count() % 2 == int(p == q)
                for p in group
                for q in group
            ),
            "Gram-I group",
        )
        for offset in range(0, len(group), 2):
            pair = sum(1 << p for p in group[offset : offset + 2])
            for p in group[offset : offset + 2]:
                planes[p] = pair
        for side in range(2):
            targets.append(sum(1 << p for p in group[side::2]))
            sizes.append(len(group))
    return labels, planes, targets, sizes


def support_basis(mask, labels, planes, cache):
    if mask not in cache:
        require(0 <= mask < 1 << 112 and len(cache) < 250000, "support capacity")
        closure = 0
        for p in range(112):
            if mask >> p & 1:
                closure |= planes[p]
        cache[mask] = binary_basis([labels[p] for p in range(112) if closure >> p & 1])
    return cache[mask]


def tariff(left, right, labels, planes, bases, cache):
    key = left, right
    if key not in cache:
        require(len(cache) < 250000, "tariff capacity")
        source = support_basis(left, labels, planes, bases)
        reader = support_basis(right, labels, planes, bases)
        rows = [
            sum(((a & b).bit_count() % 2) << j for j, b in enumerate(reader))
            for a in source
        ]
        cache[key] = len(binary_basis(rows))
    return cache[key]


def census(source):
    labels, planes, targets, sizes = source
    histogram, stream, best = Counter(), bytearray(), None
    bases, costs = {}, {}
    for a in range(32):
        others = [i for i in range(32) if i != a]
        for b, c in itertools.combinations(others, 2):
            am, bm, cm = targets[a], targets[b], targets[c]
            for p in range(112):
                if not am >> p & 1:
                    continue
                require(am.bit_count() >= 2, "split target capacity")
                queries = (am | bm, am | cm, bm | cm, am | bm | cm)
                readers = ((1 << p) | cm, (1 << p) | bm, am, (am ^ (1 << p)) | bm | cm)
                terms = [
                    tariff(q, u, labels, planes, bases, costs)
                    for q, u in zip(queries, readers, strict=True)
                ]
                floor = sizes[a] + sizes[b] + sizes[c]
                bill = sum(terms)
                histogram[bill - floor] += 1
                stream.extend((a, b, c, p, floor, *terms))
                candidate = (bill - floor, bill, a, b, c, p, terms, floor)
                if best is None or candidate < best:
                    best = candidate
    require(best is not None and sum(histogram.values()) == 52080, "complete census")
    gap, bill, a, b, c, p, terms, floor = best
    return {
        "cases": 52080,
        "histogram_bill_minus_original": {
            str(k): v for k, v in sorted(histogram.items())
        },
        "stream_sha256": hashlib.sha256(stream).hexdigest(),
        "best": {
            "targets": [a, b, c],
            "switched_port": p,
            "bill": bill,
            "original": floor,
            "gap": gap,
            "terms": terms,
        },
    }


def literal_operator(source, best):
    labels, planes, targets, _ = source
    a, b, c = (targets[i] for i in best["targets"])
    special = best["switched_port"]
    rows_q, rows_u2, target_rows = [], [], []
    for p in range(112):
        x, y, z = (mask >> p & 1 for mask in (a, b, c))
        w = int(bool(x or y or z) and p != special)
        rows_q.append((x + y, x + z, y + z, x + y + z))
        rows_u2.append((x + y - z - w, x - y + z - w, -x + y + z - w, 2 * w))
        target_rows.append((x, y, z))
    for p in range(112):
        for r in range(112):
            actual = sum(rows_u2[p][i] * rows_q[r][i] for i in range(4))
            expected = 2 * sum(target_rows[p][j] * target_rows[r][j] for j in range(3))
            require(actual == expected, "literal operator mismatch")
    ports = [
        next(p for p in range(112) if a >> p & 1 and p != special),
        special,
        next(p for p in range(112) if b >> p & 1),
        next(p for p in range(112) if c >> p & 1),
    ]
    qr = rank(list(zip(*(rows_q[p] for p in ports), strict=True)), 3)
    ur = rank(
        [
            tuple(x % 3 for x in c)
            for c in zip(*(rows_u2[p] for p in ports), strict=True)
        ],
        3,
    )
    require((qr, ur) == (3, 4), "literal witness restriction ranks")
    terms = []
    for i in range(4):
        qm = sum(1 << p for p in range(112) if rows_q[p][i])
        um = sum(1 << p for p in range(112) if rows_u2[p][i])
        terms.append(tariff(qm, um, labels, planes, {}, {}))
    require(terms == best["terms"], "actual operator support invoice")
    return {
        "entries": 12544,
        "query_rank": qr,
        "reader_rank": ur,
        "actual_terms": terms,
    }


def witness():
    for p in range(4):
        for r in range(4):
            require(
                sum(U2[p][i] * Q[r][i] for i in range(4)) == 2 * TARGET[p][r],
                "four-port rational operator",
            )
    odd = []
    for field in (3, 5, 7):
        u = [tuple(mul(x % field, inverse(2, field), field) for x in row) for row in U2]
        qc = list(zip(*Q, strict=True))
        uc = list(zip(*u, strict=True))
        require(rank(qc, field) == 3 and rank(uc, field) == 4, "factor ranks")
        odd.append({"field": field, "query_rank": 3, "reader_rank": 4})
    for row in (0, 2, 3):
        for col in range(4):
            # The unsplit reader choice has an actual GF2 support transfer.
            require(
                sum((U2[row][i] // 2) * Q[col][i] for i in range(4)) % 2
                == TARGET[row][col],
                "unsplit positive control",
            )
    return {
        "integer_operator_entries": 16,
        "odd_fields": odd,
        "unsplit_GF2_positive_entries": 12,
        "characteristic_two": [field_census(field) for field in (2, 4, 8)],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--compute", action="store_true", help="print without comparing RESULT.json"
    )
    args = parser.parse_args()
    source = geometry()
    result = {"witness": witness(), "literal_census": census(source)}
    result["literal_operator"] = literal_operator(
        source, result["literal_census"]["best"]
    )
    if not args.compute:
        require(result == read_json(HERE / "RESULT.json"), "result mismatch")
    print(json.dumps(result, sort_keys=True))
    print("PASS_TRIPLE_TRANSFER_OBSTRUCTION errors=0 cases=52080")


if __name__ == "__main__":
    main()
