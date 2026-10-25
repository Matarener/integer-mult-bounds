#!/usr/bin/env python3
"""Separate sparse-operator and dense-geometry check. No primary checker import."""

import itertools
import json
from collections import Counter
from fractions import Fraction
from hashlib import sha1, sha256
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[1]


def require(ok, label):
    if not ok:
        raise ValueError(label)


def read(path, limit):
    with path.open("rb") as handle:
        data = handle.read(limit + 1)
    require(len(data) <= limit, "input bound")
    return data


def check_pin(data, pin):
    require(sha256(data).hexdigest() == pin["sha256"], "SHA256 binding")
    framed = b"blob " + str(len(data)).encode() + b"\0" + data
    require(
        sha1(framed, usedforsecurity=False).hexdigest() == pin["git_blob"],
        "Git blob binding",
    )


def dense_rank(matrix):
    require(len(matrix) <= 16 and all(len(row) <= 16 for row in matrix), "rank bound")
    a = [row[:] for row in matrix]
    r = 0
    for col in range(len(a[0]) if a else 0):
        pivot = next((i for i in range(r, len(a)) if a[i][col]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        for i in range(r + 1, len(a)):
            if a[i][col]:
                a[i] = [x ^ y for x, y in zip(a[i], a[r], strict=True)]
        r += 1
    return r


def gram(vectors, left, right):
    return [
        [
            sum(x * y for x, y in zip(vectors[i], vectors[j], strict=True)) % 2
            for j in right
        ]
        for i in left
    ]


def sparse_sum(parts):
    result = Counter()
    for scale, support in parts:
        for p in support:
            result[p] += scale
    return {p: value for p, value in result.items() if value}


def reconstruct(groups, cert):
    halves = [g[::2] for g in groups] + [g[1::2] for g in groups]
    mates = {}
    for g in groups:
        for a, b in zip(g[::2], g[1::2], strict=True):
            mates[a], mates[b] = b, a
    qrows, ucols, changed = [], [], set()
    require(len(cert["replacements"]) == 3, "three replacements")
    for item in cert["replacements"]:
        i, j = item["groups"]
        for side in range(2):
            a, b = halves[i + 16 * side], halves[j + 16 * side]
            z = (
                item["seed_ports"]
                if side == 0
                else [mates[p] for p in item["seed_ports"]]
            )
            if item["recipe"] == "star":
                queries = [
                    sparse_sum([(1, z)]),
                    sparse_sum([(1, a), (-1, z)]),
                    sparse_sum([(1, b), (-1, z)]),
                ]
                outputs = [
                    sparse_sum([(1, a), (1, b)]),
                    sparse_sum([(1, a)]),
                    sparse_sum([(1, b)]),
                ]
            else:
                require(item["recipe"] == "chain", "recipe")
                queries = [
                    sparse_sum([(1, a), (-1, z)]),
                    sparse_sum([(1, z)]),
                    sparse_sum([(1, a), (1, b), (-1, z)]),
                ]
                outputs = [
                    sparse_sum([(1, a), (-1, b)]),
                    sparse_sum([(1, a)]),
                    sparse_sum([(1, b)]),
                ]
            qrows.extend(queries)
            ucols.extend(outputs)
            changed.update((i + 16 * side, j + 16 * side))
    for k, support in enumerate(halves):
        if k not in changed:
            qrows.append(sparse_sum([(1, support)]))
            ucols.append(sparse_sum([(1, support)]))
    return halves, mates, qrows, ucols


def operator_check(halves, qrows, ucols):
    matrix = [[0] * 112 for _ in range(112)]
    for query, output in zip(qrows, ucols, strict=True):
        for i, u in output.items():
            for j, q in query.items():
                matrix[i][j] += u * q
    channel = {p: c for c, support in enumerate(halves) for p in support}
    require(
        all(
            matrix[i][j] == int(channel[i] == channel[j])
            for i in range(112)
            for j in range(112)
        ),
        "whole exact operator",
    )
    # All source columns and arbitrary additive dirty-target columns.
    for col in range(224):
        source = [int(col == p) for p in range(112)]
        dirty = [int(col == 112 + p) for p in range(112)]
        totals = [sum(q * source[p] for p, q in query.items()) for query in qrows]
        actual = dirty[:]
        for total, output in zip(totals, ucols, strict=True):
            for p, u in output.items():
                actual[p] += u * total
        expected = [
            dirty[p] + sum(matrix[p][j] * source[j] for j in range(112))
            for p in range(112)
        ]
        require(actual == expected, "source/dirty-target column")
    return matrix


def basis_classes():
    vectors = (
        (1, 0, 0),
        (0, 1, 0),
        (1, 1, 0),
        (0, 0, 1),
        (1, 0, -1),
        (0, 1, -1),
        (1, 1, -1),
    )
    counts = Counter()
    for ids in itertools.combinations(range(7), 3):
        a = [[Fraction(x) for x in vectors[k]] for k in ids]
        rank, determinant = 0, Fraction(1)
        for col in range(3):
            pivot = next((r for r in range(rank, 3) if a[r][col]), None)
            if pivot is None:
                continue
            a[rank], a[pivot] = a[pivot], a[rank]
            value = a[rank][col]
            determinant *= value
            a[rank] = [x / value for x in a[rank]]
            for r in range(rank + 1, 3):
                factor = a[r][col]
                a[r] = [x - factor * y for x, y in zip(a[r], a[rank], strict=True)]
            rank += 1
        counts[str(int(abs(determinant)) if rank == 3 else 0)] += 1
    require(dict(counts) == {"1": 28, "0": 6, "2": 1}, "separate basis classification")


def run():
    meta = json.loads(read(P / "SOURCES.json", 32768))
    pin = next(row for row in meta["files"] if row["usage"] == "input")
    data = read(ROOT / pin["path"], 2097152)
    check_pin(data, pin)
    recipes = sorted(json.loads(data)["recipes"], key=lambda x: x["port"])
    vectors = [[(r["q"] >> bit) & 1 for bit in range(9)] for r in recipes]
    data = read(P / "RETAINED-RANK32.json", 32768)
    check_pin(data, meta["retained_rank32"])
    groups = json.loads(data)["orthonormal_groups"]
    cert = json.loads(read(P / "CERTIFICATE.json", 16384))
    halves, mates, queries, outputs = reconstruct(groups, cert)
    matrix = operator_check(halves, queries, outputs)
    self_cost, reader_cost, ranks = 0, 0, Counter()
    for query, output in zip(queries, outputs, strict=True):
        source = sorted(set(query) | {mates[p] for p in query})
        reader = sorted(set(output) | {mates[p] for p in output})
        self_cost += dense_rank(gram(vectors, source, source))
        r = dense_rank(gram(vectors, source, reader))
        reader_cost += r
        ranks[str(r)] += 1
    require((self_cost, reader_cost) == (218, 244), "separate source/reader bills")
    require(dict(ranks) == {"4": 12, "8": 18, "6": 4, "7": 4}, "separate histogram")
    for a, b in itertools.combinations(range(32), 2):
        union = sorted(
            set(halves[a] + halves[b]) | {mates[p] for p in halves[a] + halves[b]}
        )
        r = dense_rank(gram(vectors, union, union))
        require(2 * r >= 2 * (len(halves[a]) + len(halves[b])), "496 half-basis bounds")
    for i in range(112):
        for j in range(112):
            for a in range(2):
                for b in range(2):
                    x, y = (i, mates[i])[a], (j, mates[j])[b]
                    dot = (
                        sum(s * t for s, t in zip(vectors[x], vectors[y], strict=True))
                        % 2
                    )
                    require(matrix[i][j] * dot == int(i == j and a == b), "binary lift")
    basis_classes()
    expected = json.loads(read(P / "RESULT.json", 65536))
    require(
        expected["actual_source_reader_sum"] == reader_cost
        and expected["source_self_gram_sum"] == self_cost,
        "published separate receipts",
    )
    return {
        "status": "PASS_EXTERNAL_QUERY_INDEPENDENT",
        "queries": len(queries),
        "self_gram": self_cost,
        "reader_bill": reader_cost,
        "source_and_dirty_columns": 224,
        "pairs": 496,
        "formal_triples": 35,
    }


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
