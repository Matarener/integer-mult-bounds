#!/usr/bin/env python3
"""Separate span-enumeration and annihilator checks. Apache-2.0."""

import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def check(ok, reason):
    if not ok:
        raise ValueError(reason)


def load(path, digest=None):
    with path.open("rb") as stream:
        raw = stream.read(1048577)
    check(len(raw) <= 1048576, "independent input capacity")
    if digest is not None:
        check(hashlib.sha256(raw).hexdigest() == digest, "independent source drift")
    return json.loads(raw)


def binary_span(vectors):
    check(len(vectors) <= 112, "independent span capacity")
    values = {0}
    for v in vectors:
        check(0 <= v < 512, "independent label domain")
        values |= {x ^ v for x in values}
        check(len(values) <= 512, "independent span bound")
    return values


def tiny_binary():
    allowed = [
        (r, c)
        for r in range(4)
        for c in range(4)
        if ((1, 1, 0, 1), (1, 1, 0, 1), (1, 0, 1, 1), (0, 1, 1, 1))[r][c]
    ]
    requests = (((2, 3), 3), ((0, 1, 2), 3), ((1, 3), 4), ((0, 3), 8))
    complete, pair_feasible = 0, 0
    for mask in range(1 << 12):
        columns = [0] * 4
        for i, (r, c) in enumerate(allowed):
            if mask >> i & 1:
                columns[c] |= 1 << r
        passes = [
            target in binary_span([columns[i] for i in indices])
            for indices, target in requests
        ]
        pair_feasible += int(passes[0] and passes[2] and passes[3])
        complete += int(all(passes))
    check(complete == 0 and pair_feasible > 0, "raw GF2 support completion")
    return {
        "raw_queries_including_shrunk_support": 4096,
        "pair_feasible": pair_feasible,
        "completions": complete,
    }


def gf4_span(columns):
    table = ((0, 0, 0, 0), (0, 1, 2, 3), (0, 2, 3, 1), (0, 3, 1, 2))
    check(len(columns) <= 3, "GF4 enumeration capacity")
    values = set()
    for scalars in itertools.product(range(4), repeat=len(columns)):
        v = [0] * 4
        for scalar, column in zip(scalars, columns, strict=True):
            for i in range(4):
                v[i] ^= table[scalar][column[i]]
        values.add(tuple(v))
    return values


def tiny_quaternary():
    targets = ((1, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1))
    pair_feasible, complete = 0, 0
    for a, b, c, d, e in itertools.product((1, 2, 3), repeat=5):
        q = ((1, 1, a, 0), (1, 1, 0, b), (0, 0, 1, c), (1, 1, d, e))
        if not all(
            target in gf4_span((q[2 - j], q[3])) for j, target in enumerate(targets)
        ):
            continue
        pair_feasible += 1
        complete += int(targets[0] in gf4_span(q[:3]))
    check((pair_feasible, complete) == (9, 0), "independent GF4 obstruction")
    return {
        "normalized_queries": 243,
        "pair_feasible": pair_feasible,
        "completions": complete,
    }


def source():
    raw = load(
        ROOT.parent.parent
        / "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json",
        "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa",
    )
    groups = load(
        ROOT / "RETAINED-RANK32.json",
        "2e990b02186660c68d9d38cabc864d662b01458b3eafeab774a8b8406bbfb57b",
    )["orthonormal_groups"]
    labels = [r["q"] for r in raw["recipes"]]
    check(len(labels) == 112 and len(groups) == 16, "independent geometry shape")
    check(
        sorted(x for g in groups for x in g) == list(range(112)),
        "independent partition",
    )
    planes, targets, sizes = {}, [], []
    for g in groups:
        check(0 < len(g) <= 8 and len(g) % 2 == 0, "independent even group")
        for p in g:
            check(
                all((labels[p] & labels[q]).bit_count() % 2 == int(p == q) for q in g),
                "independent Gram group",
            )
        for i in range(0, len(g), 2):
            for p in g[i : i + 2]:
                planes[p] = frozenset(g[i : i + 2])
        for parity in range(2):
            targets.append(frozenset(g[parity::2]))
            sizes.append(len(g))
    return labels, planes, targets, sizes


def closed(support, planes):
    return frozenset(q for p in support for q in planes[p])


def invoice(left, right, labels, planes, spans, kernels, costs):
    lports, rports = closed(left, planes), closed(right, planes)
    key = lports, rports
    if key not in costs:
        check(len(costs) < 250000, "independent cost cache bound")
        if lports not in spans:
            spans[lports] = binary_span([labels[p] for p in lports])
        if rports not in kernels:
            kernel = set(range(512))
            for p in rports:
                kernel = {x for x in kernel if (x & labels[p]).bit_count() % 2 == 0}
            kernels[rports] = kernel
        space = spans[lports]
        intersection = len(space & kernels[rports])
        check(
            intersection > 0 and intersection & (intersection - 1) == 0,
            "annihilator intersection power of two",
        )
        costs[key] = len(space).bit_length() - intersection.bit_length()
    return costs[key]


def literal_census(data):
    labels, planes, targets, sizes = data
    histogram, digest, count = Counter(), hashlib.sha256(), 0
    best, spans, kernels, costs = None, {}, {}, {}
    for a in range(32):
        for b in range(32):
            if b == a:
                continue
            for c in range(b + 1, 32):
                if c == a:
                    continue
                am, bm, cm = targets[a], targets[b], targets[c]
                for p in sorted(am):
                    qs = (am | bm, am | cm, bm | cm, am | bm | cm)
                    us = (
                        frozenset((p,)) | cm,
                        frozenset((p,)) | bm,
                        am,
                        (am - {p}) | bm | cm,
                    )
                    terms = [
                        invoice(q, u, labels, planes, spans, kernels, costs)
                        for q, u in zip(qs, us, strict=True)
                    ]
                    bill, original = sum(terms), sizes[a] + sizes[b] + sizes[c]
                    histogram[bill - original] += 1
                    digest.update(bytes((a, b, c, p, original, *terms)))
                    candidate = (bill - original, bill, a, b, c, p, terms, original)
                    if best is None or candidate < best:
                        best = candidate
                    count += 1
    check(best is not None and count == 52080, "independent census completeness")
    gap, bill, a, b, c, p, terms, original = best
    return {
        "cases": count,
        "histogram_bill_minus_original": {
            str(k): v for k, v in sorted(histogram.items())
        },
        "stream_sha256": digest.hexdigest(),
        "best": {
            "targets": [a, b, c],
            "switched_port": p,
            "bill": bill,
            "original": original,
            "gap": gap,
            "terms": terms,
        },
    }


def operator(data, best):
    _, _, targets, _ = data
    a, b, c = (targets[j] for j in best["targets"])
    p0 = best["switched_port"]
    source_rows, reader_rows = [], []
    for p in range(112):
        source_rows.append(
            (int(p in a | b), int(p in a | c), int(p in b | c), int(p in a | b | c))
        )
        if p == p0:
            reader_rows.append((1, 1, -1, 0))
        elif p in a:
            reader_rows.append((0, 0, -2, 2))
        elif p in b:
            reader_rows.append((0, -2, 0, 2))
        elif p in c:
            reader_rows.append((-2, 0, 0, 2))
        else:
            reader_rows.append((0, 0, 0, 0))
    for r in range(112):
        for s in range(112):
            expected = 2 * int(any(r in t and s in t for t in (a, b, c)))
            actual = sum(reader_rows[r][j] * source_rows[s][j] for j in range(4))
            check(actual == expected, "independent literal operator")
    return 12544


def main():
    expected = load(ROOT / "RESULT.json")
    data = source()
    result = literal_census(data)
    check(result == expected["literal_census"], "independent full census mismatch")
    receipt = {
        "raw_GF2": tiny_binary(),
        "normalized_GF4": tiny_quaternary(),
        "literal_census": result,
        "literal_operator_entries": operator(data, result["best"]),
    }
    print(json.dumps(receipt, sort_keys=True))
    print("PASS_INDEPENDENT_TRIPLE_TRANSFER errors=0 cases=52080")


if __name__ == "__main__":
    main()
