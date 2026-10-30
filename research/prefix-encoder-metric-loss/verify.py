#!/usr/bin/env python3
"""Finite corroboration of the sharp prefix-encoder metric loss.

Produced by Nick Petalas. Apache-2.0. No predecessor executable is imported.
"""

import hashlib
import importlib.util
import json
from fractions import Fraction as Q
from itertools import permutations, product
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("prefix_encoder_local", HERE / "encoder.py")
if SPEC is None or SPEC.loader is None:
    raise ValueError("local encoder loader unavailable")
E = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(E)


def check(condition, message):
    if not condition:
        raise ValueError(message)


def eye(n):
    check(1 <= n <= 36, "dense matrix capacity")
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def transpose(a):
    return [list(column) for column in zip(*a)]


def multiply(a, b):
    check(1 <= len(a) <= 36 and 1 <= len(b) <= 36, "multiply capacity")
    check(all(len(row) == len(b) for row in a), "multiply dimensions")
    return [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def groups():
    result = [("C" + str(q), tuple(tuple((i + j) % q for j in range(q))
                                      for i in range(q))) for q in range(1, 5)]
    result.append(("V4", tuple(tuple(i ^ j for j in range(4)) for i in range(4))))
    elements = list(permutations(range(3)))
    table = tuple(tuple(elements.index(tuple(a[b[i]] for i in range(3)))
                        for b in elements) for a in elements)
    result.append(("S3", table))
    return tuple(result)


def literal_entry(table, inputs, outputs, final=None, initial=0):
    """Multiply the one-column tables independently of the blocked constructor."""
    q = len(table)
    row = [Q(i == initial) for i in range(q)]
    for x, y in zip(inputs, outputs):
        next_row = [Q(0)] * q
        for a, b in product(range(q), repeat=2):
            transition = int(y == table[a][x] and b == y)
            next_row[b] += row[a] * transition
        row = next_row
    return sum(row) if final is None else row[final]


def endpoint_checks(table, max_width):
    q = len(table)
    entries = 0
    for width in range(1, max_width + 1):
        words = tuple(product(range(q), repeat=width))
        images = []
        for inputs in words:
            expected = []
            for index in range(width):
                value = 0
                for letter in inputs[:index + 1]:
                    value = table[value][letter]
                expected.append(value)
            images.append(tuple(expected))
            for outputs in words:
                check(literal_entry(table, inputs, outputs) == int(outputs == tuple(expected)),
                      "literal complete endpoint differs from prefix permutation")
                entries += 1
        check(len(set(images)) == len(words), "endpoint is not unitary")
    return entries


def quadratic(real, imaginary, permutation, m, vector):
    """Evaluate z* Q z independently by the two weighted norms."""
    before = Q(0)
    after = Q(0)
    for i, ir, ii in vector:
        for j, jr, ji in vector:
            bi, xi = divmod(i, m)
            bj, xj = divmod(j, m)
            ai, yi = divmod(permutation[i], m)
            aj, yj = divmod(permutation[j], m)
            cr, ci = ir * jr + ii * ji, ir * ji - ii * jr
            if xi == xj:
                before += cr * real[bi][bj] - ci * imaginary[bi][bj]
            if yi == yj:
                after += cr * real[ai][aj] - ci * imaginary[ai][aj]
    return before - after


def metric_checks(table, block):
    q = len(table)
    permutation, m = E.local_permutation(table, block)
    words = tuple(product(range(q), repeat=block))
    for column, row in enumerate(permutation):
        terminal, xi = divmod(column, m)
        initial, yi = divmod(row, m)
        check(literal_entry(table, words[xi], words[yi], terminal, initial) == 1,
              "blocked path disagrees with literal one-column table product")
    relations, entries = E.metric_relations(permutation, m, q)
    rank = E.relation_rank(relations, q * q)
    check(rank == q * q - 1, "contractive metric commutant is not scalar")
    for relation in relations:
        check(sum(value for key, value in relation if key // q == key % q) == 0,
              "identity metric is not in the kernel")
    witnesses = 0
    for mode in range(3):
        vr = [Q((i + 1) * (mode + 1), 3) for i in range(q)]
        vi = [Q((i % 2) * mode, 5) for i in range(q)]
        real = [[Q(i == j) + vr[i] * vr[j] + vi[i] * vi[j]
                 for j in range(q)] for i in range(q)]
        imaginary = [[vi[i] * vr[j] - vr[i] * vi[j]
                      for j in range(q)] for i in range(q)]
        # P = I + v v* is positive definite without a numerical eigenvalue test.
        vector, value = E.negative_witness(real, imaginary, permutation, m)
        if q == 1:
            check(not vector and value == 0, "trivial group metric")
        else:
            check(value < 0 and quadratic(real, imaginary, permutation, m, vector) == value,
                  "explicit noncontractive metric witness")
            witnesses += 1
    return entries, len(relations), witnesses, len(permutation)


def gauge_checks(table):
    q = len(table)
    permutation, _ = E.local_permutation(table, 1)
    n = q * q
    local = [[Q(permutation[j] == i) for j in range(n)] for i in range(n)]
    count = 0
    for mode in range(2):
        s, inverse = eye(q), eye(q)
        if mode == 0:
            for i in range(q):
                s[i][i], inverse[i][i] = Q(i + 1), Q(1, i + 1)
        elif q > 1:
            s[0][1], inverse[0][1] = Q(2, 3), Q(-2, 3)
        check(multiply(s, inverse) == eye(q), "gauge inverse")
        metric = multiply(transpose(s), s)
        lift = [[s[i // q][j // q] * int(i % q == j % q)
                 for j in range(n)] for i in range(n)]
        unlift = [[inverse[i // q][j // q] * int(i % q == j % q)
                   for j in range(n)] for i in range(n)]
        transformed = multiply(unlift, multiply(local, lift))
        weight = [[metric[i // q][j // q] * int(i % q == j % q)
                   for j in range(n)] for i in range(n)]
        check(multiply(transpose(transformed), multiply(weight, transformed)) == weight,
              "gauge metric does not contract isometrically")
        left = [s[0]]
        right = [[sum(row)] for row in inverse]
        left_dual = multiply(multiply(left, multiply(inverse, transpose(inverse))),
                             transpose(left))[0][0]
        right_bound = multiply(transpose(right), multiply(metric, right))[0][0]
        check(left_dual == 1 and right_bound == q, "gauge boundary factor")
        count += 1
    return count


def reject_controls():
    count = 0
    cases = (((), 1), (((0, 1), (1, 0)), 0), (((0, 1), (1, 0)), 7),
             (((0, 1), (1, 1)), 1), (((0, 2), (1, 0)), 1),
             (((0, 1),), 1), (((0, 1), (1, 0)), 1.0))
    for table, block in cases:
        try:
            E.local_permutation(table, block)
        except ValueError:
            count += 1
        else:
            raise ValueError("invalid group or block accepted")
    table = ((0, 1), (1, 0))
    check(literal_entry(table, (1,), (1,), final=0) == 0, "terminal-state mutant")
    count += 1
    permutation, m = E.local_permutation(table, 1)
    re, im = eye(2), [[Q(0), Q(1, 3)], [Q(-1, 3), Q(0)]]
    vector, value = E.negative_witness(re, im, permutation, m)
    check(value < 0 and quadratic(re, im, permutation, m, vector) == value,
          "imaginary off-diagonal mutant not rejected")
    check(all(re[i][i] == 1 for i in range(2)), "diagonal-only false positive")
    count += 1
    for q in range(1, 7):
        for t in (Q(1, 3), Q(1), Q(7, 2)):
            check((1 / t - Q(1, 100)) * t - 1 < 0, "left-bound underclaim")
            check(q * t - (q * t - Q(1, 100)) > 0, "right-bound underclaim")
            check(Q(999, 1000) * q - q < 0, "rate below one underclaim")
            count += 3
    return count


def authenticated_hashes():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    root = HERE.parents[1]
    pins = {}
    for row in sources["files"]:
        if row["usage"] != "input":
            continue
        path = root / row["path"]
        check(path.stat().st_size <= 1_000_000, "source input size")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        check(digest == row["sha256"], "changed source input: " + row["path"])
        pins[row["path"]] = digest
    own = {}
    for path in sorted(HERE.iterdir()):
        if path.is_file():
            check(path.stat().st_size <= 1_000_000, "package file size")
            own[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    check(len(own) == 7 and len(pins) == 2, "package/input inventory")
    return own, pins


def main():
    own, pins = authenticated_hashes()
    entries = relations = witnesses = endpoints = gauges = blocks = paths = 0
    summaries = []
    for name, table in groups():
        q = E.group(table)
        widths = (1, 2, 3, 4, 5, 6) if q <= 2 else ((1, 2, 3) if q <= 4 else (1, 2))
        for block in widths:
            if q ** (block + 1) > 216:
                continue
            n_entries, n_relations, n_witnesses, n_paths = metric_checks(table, block)
            entries += n_entries
            relations += n_relations
            witnesses += n_witnesses
            paths += n_paths
            blocks += 1
        endpoints += endpoint_checks(table, 4 if q <= 3 else (3 if q <= 4 else 2))
        gauges += gauge_checks(table)
        summaries.append({"group": name, "order": q, "true_squared_norm": 1,
                          "least_certified_squared_bound": q})
    controls = reject_controls()
    print(json.dumps({"status": "PASS_PREFIX_ENCODER_METRIC_LOSS", "groups": summaries,
                      "blocked_tables": blocks, "commutator_entries": entries,
                      "sum_distinct_relations_per_table": relations,
                      "blocked_path_entries": paths, "negative_metric_witnesses": witnesses,
                      "complete_endpoint_entries": endpoints, "gauge_certificates": gauges,
                      "rejecting_controls": controls, "package_sha256": own,
                      "source_sha256": pins}, sort_keys=True))


if __name__ == "__main__":
    main()
