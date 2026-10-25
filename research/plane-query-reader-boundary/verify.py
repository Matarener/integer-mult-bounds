#!/usr/bin/env python3
"""Check the one-binary-seed P112 reader-boundary result. Apache-2.0."""

import itertools
import json
from collections import Counter
from fractions import Fraction
from hashlib import sha1, sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"
DIRECTIONS = (
    (1, 0, 0),
    (0, 1, 0),
    (1, 1, 0),
    (0, 0, 1),
    (1, 0, -1),
    (0, 1, -1),
    (1, 1, -1),
)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def bounded(path, limit=1048576):
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    need(len(raw) <= limit, "input capacity exceeded")
    return raw


def authenticate(raw, pin):
    need(sha256(raw).hexdigest() == pin["sha256"], "source SHA256 differs")
    blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
    need(
        sha1(blob, usedforsecurity=False).hexdigest() == pin["git_blob"],
        "source Git blob differs",
    )


def load():
    meta = json.loads(bounded(HERE / "SOURCES.json", 32768))
    pins = [r for r in meta["files"] if r["usage"] == "input"]
    need(len(pins) == 1 and pins[0]["path"] == SOURCE, "live input inventory")
    raw = bounded(ROOT / SOURCE, 2097152)
    authenticate(raw, pins[0])
    recipes = json.loads(raw)["recipes"]
    need(len(recipes) == 112, "port count")
    need(sorted(r["port"] for r in recipes) == list(range(112)), "port IDs")
    labels = [r["q"] for r in sorted(recipes, key=lambda r: r["port"])]
    need(all(type(x) is int and 0 < x < 512 for x in labels), "nine-bit labels")
    need(len(set(labels)) == 112, "distinct labels")
    raw = bounded(HERE / "RETAINED-RANK32.json", 32768)
    authenticate(raw, meta["retained_rank32"])
    groups = json.loads(raw)["orthonormal_groups"]
    need(len(groups) == 16, "group count")
    need(
        all(isinstance(g, list) and len(g) in (4, 6, 8) for g in groups),
        "even group sizes",
    )
    need(all(type(p) is int for g in groups for p in g), "integer ports")
    need(sorted(p for g in groups for p in g) == list(range(112)), "partition")
    for g in groups:
        need(
            all(
                (labels[x] & labels[y]).bit_count() % 2 == int(x == y)
                for x in g
                for y in g
            ),
            "orthonormal group",
        )
    cert = json.loads(bounded(HERE / "CERTIFICATE.json", 16384))
    return labels, groups, cert


def binary_basis(rows, width):
    need(0 <= width <= 112 and len(rows) <= 224, "elimination capacity")
    pivots = [0] * width
    for original in rows:
        need(type(original) is int and 0 <= original < 1 << width, "binary row")
        value = original
        for bit in range(width - 1, -1, -1):
            if value & (1 << bit):
                if pivots[bit]:
                    value ^= pivots[bit]
                else:
                    pivots[bit] = value
                    break
    return tuple(x for x in pivots if x)


def pairing_rank(labels, source, target):
    left = binary_basis([labels[p] for p in source], 9)
    right = binary_basis([labels[p] for p in target], 9)
    rows = [
        sum(((x & y).bit_count() % 2) << j for j, y in enumerate(right)) for x in left
    ]
    return len(binary_basis(rows, len(right)))


def geometry(groups):
    planes = [g[k : k + 2] for g in groups for k in range(0, len(g), 2)]
    owners = {p: plane for plane in planes for p in plane}
    supports = [g[side::2] for g in groups for side in (0, 1)]
    channels = {p: c for c, support in enumerate(supports) for p in support}
    return planes, owners, supports, channels


def local_rows(a, b, z, recipe):
    need(len(a) == len(b) == len(z) == 112, "local vector width")
    if recipe == "star":
        return (
            [
                z,
                [x - y for x, y in zip(a, z, strict=True)],
                [x - y for x, y in zip(b, z, strict=True)],
            ],
            (1, 1, 0),
            (1, 0, 1),
        )
    need(recipe == "chain", "recipe alphabet")
    return (
        [
            [x - y for x, y in zip(a, z, strict=True)],
            z,
            [x + y - w for x, y, w in zip(a, b, z, strict=True)],
        ],
        (1, 1, 0),
        (-1, 0, 1),
    )


def construct(groups, cert):
    _, owners, supports, _ = geometry(groups)
    need(
        cert["schema_version"] == 1 and cert["apply_both_sides"] is True,
        "certificate version and side policy",
    )
    replacements = cert["replacements"]
    need(type(replacements) is list and len(replacements) == 3, "three replacements")
    queries, decoders, used = [], [], set()
    for item in replacements:
        pair = item["groups"]
        need(type(pair) is list and len(pair) == 2, "group pair")
        need(all(type(g) is int and 0 <= g < 16 for g in pair), "group IDs")
        i, j = pair
        need(i != j and not used.intersection(pair), "disjoint group pairs")
        used.update(pair)
        seed = item["seed_ports"]
        need(type(seed) is list and 1 <= len(seed) <= 16, "seed capacity")
        need(all(type(p) is int for p in seed), "integer seed ports")
        need(len(set(seed)) == len(seed), "duplicate seed")
        need(set(seed) <= set(supports[2 * i] + supports[2 * j]), "seed side")
        for side in (0, 1):
            aa, bb = supports[2 * i + side], supports[2 * j + side]
            zz = (
                seed
                if side == 0
                else [next(p for p in owners[x] if p != x) for x in seed]
            )
            a, b, z = [
                [int(p in support) for p in range(112)] for support in (aa, bb, zz)
            ]
            local, ua, ub = local_rows(a, b, z, item["recipe"])
            for k, row in enumerate(local):
                queries.append(row)
                decoders.append(
                    [ua[k] if p in aa else ub[k] if p in bb else 0 for p in range(112)]
                )
    for c, support in enumerate(supports):
        if c // 2 not in used:
            row = [int(p in support) for p in range(112)]
            queries.append(row)
            decoders.append(row)
    need(len(queries) == len(decoders) == 38, "query count")
    return queries, decoders


def invoice(labels, groups, queries, decoders):
    _, owners, _, _ = geometry(groups)
    details = []
    for query, decoder in zip(queries, decoders, strict=True):
        source = sorted({r for p, x in enumerate(query) if x for r in owners[p]})
        reader = sorted({r for p, x in enumerate(decoder) if x for r in owners[p]})
        details.append(
            {
                "source_closure": source,
                "reader_closure": reader,
                "self_rank": pairing_rank(labels, source, source),
                "reader_rank": pairing_rank(labels, source, reader),
            }
        )
    return details


def identities(labels, groups, queries, decoders):
    _, owners, _, channel = geometry(groups)
    for i in range(112):
        for j in range(112):
            value = sum(u[i] * q[j] for u, q in zip(decoders, queries, strict=True))
            need(value == int(channel[i] == channel[j]), "exact integer UQ=K")
    forced = 0
    for i in range(112):
        for j in range(112):
            orthogonal = all(
                (labels[x] & labels[y]).bit_count() % 2 == 0
                for x in owners[i]
                for y in owners[j]
            )
            if i == j or not orthogonal:
                forced += 1
                need(int(channel[i] == channel[j]) == int(i == j), "strict scalar mask")
            for a in range(2):
                for b in range(2):
                    value = int(channel[i] == channel[j]) * (
                        (labels[owners[i][a]] & labels[owners[j][b]]).bit_count() % 2
                    )
                    need(value == int(i == j and a == b), "expanded I224")
    return forced


def determinant(m):
    return (
        m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
        - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
        + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
    )


def inverse3(matrix):
    d = determinant(matrix)
    need(d != 0, "singular formal basis")
    result = []
    for i in range(3):
        row = []
        for j in range(3):
            rr, cc = [k for k in range(3) if k != j], [k for k in range(3) if k != i]
            minor = (
                matrix[rr[0]][cc[0]] * matrix[rr[1]][cc[1]]
                - matrix[rr[0]][cc[1]] * matrix[rr[1]][cc[0]]
            )
            row.append(Fraction((-1) ** (i + j) * minor, d))
        result.append(row)
    need(
        all(
            sum(result[i][k] * matrix[k][j] for k in range(3)) == int(i == j)
            for i in range(3)
            for j in range(3)
        ),
        "inverse identity",
    )
    return result


def classify():
    counts, half = Counter(), []
    for ids in itertools.combinations(range(7), 3):
        matrix = [DIRECTIONS[k] for k in ids]
        d = determinant(matrix)
        counts[str(abs(d))] += 1
        if not d:
            continue
        inv = inverse3(matrix)
        readers = [x for row in inv[:2] for x in row]
        if abs(d) == 1:
            need(all(x in (-1, 0, 1) for x in readers), "integral reader alphabet")
        else:
            need(abs(d) == 2, "basis determinant alphabet")
            need(all(abs(x) == Fraction(1, 2) for x in readers), "half readers")
            half.append(list(ids))
    need(dict(counts) == {"0": 6, "1": 28, "2": 1}, "35 basis classification")
    need(half == [[2, 4, 5]], "unique half-integral basis")
    return dict(sorted(counts.items())), half


def pair_bounds(labels, groups):
    _, _, supports, _ = geometry(groups)
    histogram = Counter()
    for ca, cb in itertools.combinations(range(32), 2):
        ga, gb = ca // 2, cb // 2
        union = sorted(set(groups[ga] + groups[gb]))
        r = pairing_rank(labels, union, union)
        baseline = len(groups[ga]) + len(groups[gb])
        need(r >= max(len(groups[ga]), len(groups[gb])), "contained identity rank")
        need(2 * r >= baseline, "half-integral reader floor")
        need(
            len(supports[ca]) * 2 + len(supports[cb]) * 2 == baseline,
            "original expanded identity size",
        )
        histogram[f"{baseline}:{r}"] += 1
    need(sum(histogram.values()) == 496, "all literal query pairs")
    return dict(sorted(histogram.items()))


def run():
    labels, groups, cert = load()
    queries, decoders = construct(groups, cert)
    forced = identities(labels, groups, queries, decoders)
    rows = invoice(labels, groups, queries, decoders)
    classification, half = classify()
    pairs = pair_bounds(labels, groups)
    source_bill = sum(r["self_rank"] for r in rows)
    reader_bill = sum(r["reader_rank"] for r in rows)
    need(source_bill == 218 and reader_bill == 244, "separate charge receipts")
    return {
        "status": "PASS_EXTERNAL_QUERY_READER_BOUNDARY",
        "errors": 0,
        "queries": len(queries),
        "integer_factor_entries": 112**2,
        "forced_mask_entries": forced,
        "expanded_binary_entries": 224**2,
        "literal_baseline": 224,
        "source_self_gram_sum": source_bill,
        "actual_source_reader_sum": reader_bill,
        "reader_rank_histogram": dict(
            sorted(Counter(str(r["reader_rank"]) for r in rows).items())
        ),
        "basis_absolute_determinants": classification,
        "half_basis": half,
        "query_pairs": 496,
        "pair_baseline_union_rank_histogram": pairs,
        "term_invoices": rows,
        "no_native_supplier_or_kappa_claim": True,
    }


if __name__ == "__main__":
    actual = run()
    expected = json.loads(bounded(HERE / "RESULT.json", 65536))
    need(actual == expected, "result receipt differs")
    print(
        json.dumps(
            {k: v for k, v in actual.items() if k != "term_invoices"}, sort_keys=True
        )
    )
