#!/usr/bin/env python3
"""Separate finite audit: image-set ranks and shortest paths over F2 matrices.

No imports from verify.py or predecessor code. The finite shortest-path check
is independent evidence, not a substitute for the all-field written proof.
Prepared for @CubeJerry with OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction
import hashlib
import heapq
import itertools
import json
from pathlib import Path
import tarfile

PACKAGE = Path(__file__).resolve().parent
REPO = PACKAGE.parents[1]


def check(ok, message):
    if not ok:
        raise ValueError(message)


def image_rank(matrix):
    """Dimension from cardinality of the image, without pivot elimination."""
    image = set()
    for coefficients in itertools.product((0, 1), repeat=len(matrix)):
        image.add(tuple(sum(c*row[j] for c, row in zip(coefficients, matrix)) % 2
                        for j in range(len(matrix[0]))))
    size = len(image)
    check(size & (size-1) == 0, "image cardinality is a power of two")
    return size.bit_length()-1


def read_geometry():
    source = REPO / "research/community-frontier1094-audit/selected-replay.tar.gz"
    check(hashlib.sha256(source.read_bytes()).hexdigest() ==
          "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6", "archive")
    with tarfile.open(source, "r:gz") as tf:
        stream = tf.extractfile("candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json")
        check(stream is not None, "member")
        raw = stream.read()
    check(hashlib.sha256(raw).hexdigest() ==
          "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa", "member digest")
    data = json.loads(raw)
    labels = [None]*112
    for recipe in data["recipes"]:
        labels[recipe["port"]] = tuple((recipe["q"] >> i) & 1 for i in range(9))
    raw = (REPO / "research/paired-plane-port-matching-seed6c563a/CERTIFICATE.json").read_bytes()
    check(hashlib.sha256(raw).hexdigest() ==
          "4fd648f7b5178bff5441bf364d58234b7bc1a43b924bc6da03013c948f1473b1", "matching digest")
    planes = json.loads(raw)["matching"]
    check(sorted(itertools.chain.from_iterable(planes)) == list(range(112)), "port partition")
    return labels, planes


def geometry_classes():
    labels, planes = read_geometry()
    histogram, tables = Counter(), {}
    all_tables = bytearray()
    for i, j in itertools.combinations(range(56), 2):
        ports = planes[i]+planes[j]
        g = [[sum(a*b for a, b in zip(labels[u], labels[v])) % 2 for v in ports] for u in ports]
        check([row[:2] for row in g[:2]] == [[1, 0], [0, 1]], "first Gram")
        check([row[2:] for row in g[2:]] == [[1, 0], [0, 1]], "second Gram")
        c = image_rank([row[2:] for row in g[:2]])
        r = image_rank(g)
        key = f"{c},{r}"
        histogram[key] += 1
        spans = {1: (0, 1), 2: (2, 3), 3: (0, 1, 2, 3)}
        table = {(a, b): image_rank([[g[x][y] for y in spans[b]] for x in spans[a]])
                 for a, b in itertools.product((1, 2, 3), repeat=2)}
        if key in tables:
            check(tables[key] == table, "class has a single tariff table")
        tables[key] = table
        all_tables.extend(table[a, b] for a, b in itertools.product((1, 2, 3), repeat=2))
    return histogram, tables, hashlib.sha256(all_tables).hexdigest()


def mask(vector):
    return (1 if vector & 3 else 0) + (2 if vector & 12 else 0)


def atoms(table):
    result = []
    for u, v in itertools.product(range(1, 16), repeat=2):
        a = sum(((u >> i) & 1)*((v >> j) & 1) << (4*i+j)
                for i, j in itertools.product(range(4), repeat=2))
        result.append((a, table[mask(u), mask(v)]))
    check(len({a for a, _ in result}) == 225, "225 distinct binary rank-one matrices")
    return sorted(result, key=lambda pair: (pair[1], pair[0]))


def shortest_identity(table):
    """Exact nonnegative shortest path; any finite binary factor list is a walk."""
    generators = atoms(table)
    target = sum(1 << (5*i) for i in range(4))
    distances = [10**9]*65536
    distances[0] = 0
    queue = [(0, 0)]
    settled = 0
    while queue:
        distance, matrix = heapq.heappop(queue)
        if distance != distances[matrix]:
            continue
        settled += 1
        if matrix == target:
            return distance, settled
        for atom, price in generators:
            nxt, candidate = matrix ^ atom, distance+price
            if candidate < distances[nxt]:
                distances[nxt] = candidate
                heapq.heappush(queue, (candidate, nxt))
    raise ValueError("identity is unreachable")


def rational_inverse(matrix):
    n = len(matrix)
    a = [[Fraction(x) for x in row] + [Fraction(i == j) for j in range(n)]
         for i, row in enumerate(matrix)]
    for j in range(n):
        pivot = next(i for i in range(j, n) if a[i][j])
        a[j], a[pivot] = a[pivot], a[j]
        d = a[j][j]
        a[j] = [x/d for x in a[j]]
        for i in range(n):
            if i != j:
                d = a[i][j]
                a[i] = [x-d*y for x, y in zip(a[i], a[j])]
    return [row[n:] for row in a]


def fixture_checks():
    a = [[1, 2, 6, 0], [0, 1, 3, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    b = rational_inverse(a)
    check(b == [[1, -2, 0, 0], [0, 1, -3, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
          "exact cofactor-cancellation inverse")
    # Six columns encoded independently from the primary fixture constructor.
    left = [[1, 0, -1, 0, 0, 0], [0, 1, 0, 0, -1, 0],
            [1, 0, 0, -1, 0, 0], [0, 1, 0, 0, 0, -1]]
    right = [[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0],
             [1, 0, 0, 0], [0, 0, 0, 1], [0, 1, 0, 0]]
    product = [[sum(left[i][k]*right[k][j] for k in range(6)) for j in range(4)] for i in range(4)]
    check(product == [[int(i == j) for j in range(4)] for i in range(4)], "six-term identity")
    masked = [[sum(left[i][k]*right[k][j] for k in range(2)) for j in range(4)] for i in range(4)]
    check(masked == [[1, 0, 1, 0], [0, 1, 0, 1], [1, 0, 1, 0], [0, 1, 0, 1]], "masked endpoint")
    check(image_rank(masked) == 2, "free off-diagonal fit need not have rank four")


def main():
    histogram, tables, digest = geometry_classes()
    receipt = json.loads((PACKAGE / "RESULT.json").read_text())
    check(dict(histogram) == receipt["cross_rank_joint_rank_histogram"], "geometry inventory")
    check(digest == receipt["tariff_table_sha256"], "complete tariff digest")
    outcomes = {}
    for key, table in sorted(tables.items()):
        distance, settled = shortest_identity(table)
        check(distance == 8, "shortest-path identity cost")
        outcomes[key] = {"minimum": distance, "settled_states": settled}
    # Mutation changes the actual optimization, not just an expected string.
    cheap = dict(tables["1,4"])
    cheap[1, 1] = 1
    distance, _ = shortest_identity(cheap)
    check(distance == 6, "undercharged self-copy is detected by the independent optimum")
    fixture_checks()
    print(json.dumps(outcomes, sort_keys=True))
    print("PASS_INDEPENDENT_TWO_PLANE_F2 paths=5 matrices_per_graph=65536 atoms=225 "
          "minimum=8 undercharge_control=6 no_new_kappa")


if __name__ == "__main__":
    main()
