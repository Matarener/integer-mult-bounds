#!/usr/bin/env python3
"""Enumerate the complete fixed-schedule binary aggregate solution space."""

import hashlib
import importlib.util
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SPEC = importlib.util.spec_from_file_location("two_burst_algebra", PACKAGE / "algebra.py")
ALGEBRA = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ALGEBRA)
a = ALGEBRA


def authenticated_inputs():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    result = {}
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        path = ROOT / row["path"]
        a.require(path.stat().st_size <= 1024 * 1024, "input size")
        raw = path.read_bytes()
        a.require(hashlib.sha256(raw).hexdigest() == row["sha256"], "input digest")
        result[path.name] = raw
    a.require(len(result) == 3, "declared source inventory")
    return result


def check_upper(calls, witness, columns, target):
    a.require(witness["order"] == [1, 3, 2, 4, 0, 5], "upper full order")
    a.require(witness["gaps"] == [2, 4], "upper gaps")
    matrices = witness["matrices"]
    groups = witness["rank_one_queries"]
    a.require(len(matrices) == len(groups) == 2, "upper burst inventory")
    aggregate = 0
    for i in range(2):
        matrix, total = a.pack(matrices[i]), 0
        a.require(len(groups[i]) == 4, "four attaining queries")
        for rows in groups[i]:
            query = a.pack(rows)
            a.require(a.rank(query) == 1, "query rank")
            a.require(a.multiply(query, query) == 0, "query square zero")
            total ^= query
        a.require(total == matrix, "attaining aggregate sum")
        a.require(a.rank(matrix) == 4, "attaining aggregate rank")
        aggregate |= matrix << (64 * i)
    a.require(a.linear_image(columns, aggregate) == target, "all endpoint coefficients")
    return aggregate


def check_rank():
    # Independent kernel cardinalities for every 3-by-3 matrix, with five
    # identity coordinates. These cover all ranks and every pivot location.
    for word in range(512):
        rows = [(word >> (3 * i)) & 7 for i in range(3)]
        kernel = sum(all((r & x).bit_count() % 2 == 0 for r in rows)
                     for x in range(8))
        expected = 8 - (kernel.bit_length() - 1)
        embedded = rows + [1 << i for i in range(3, 8)]
        a.require(a.rank(a.pack(embedded)) == expected, "kernel/rank control")
    return 512


def reject(function):
    try:
        function()
    except ValueError:
        return
    raise ValueError("negative control accepted")


def controls(calls, witness, columns, target, particular, null):
    reject(lambda: a.pack([0] * 7 + [256]))
    reject(lambda: a.build_system(calls, list(reversed(witness["order"])), [2, 4]))
    reject(lambda: a.build_system(calls, witness["order"], [1, 4]))
    broken = json.loads(json.dumps(witness))
    broken["matrices"][0][0] ^= 1
    reject(lambda: check_upper(calls, broken, columns, target))
    broken = json.loads(json.dumps(witness))
    broken["rank_one_queries"][0][0] = [1] + [0] * 7
    reject(lambda: check_upper(calls, broken, columns, target))
    reject(lambda: a.affine_space([0] * 128, 1))
    a.require(a.linear_image(columns, particular ^ 1) != target,
              "changed aggregate must lose endpoint")
    # A constant-only screen accepts this altered pair; higher coefficients reject it.
    changed = particular ^ 1 ^ (1 << 64)
    discrepancy = a.linear_image(columns, changed) ^ target
    a.require(discrepancy != 0 and discrepancy & a.MASK == 0,
              "constant-only false positive")
    small = [0]
    value = 0
    for i in range(1, 8):
        value ^= null[(i & -i).bit_length() - 1]
        small.append(value)
    a.require(len(set(small)) == 8, "Gray enumeration control")
    return 9


def enumerate_pairs(particular, null):
    a.require(len(null) == 24, "complete 24-dimensional domain")
    histogram = [[0] * 9 for _ in range(9)]
    current = particular
    for index in range(1 << 24):
        if index:
            current ^= null[(index & -index).bit_length() - 1]
        left = a.rank(current & a.MASK)
        right = a.rank(current >> 64)
        a.require(left + right >= 8, "rank-sum lower bound failed")
        histogram[left][right] += 1
    a.require(sum(map(sum, histogram)) == (1 << 24), "complete enumeration count")
    a.require(histogram[4][4] > 0, "attaining rank pair")
    return {f"{i},{j}": count for i, row in enumerate(histogram)
            for j, count in enumerate(row) if count}


def main():
    a.require(sys.version_info >= (3, 12), "Python 3.12 required")
    inputs = authenticated_inputs()
    source = json.loads(inputs["SOURCE-WORD.json"])
    calls = source["calls"][:6]
    witness = json.loads(inputs["CERTIFICATES.json"])["two_burst"]
    columns, target = a.build_system(calls, witness["order"], witness["gaps"])
    particular, null, free = a.affine_space(columns, target)
    a.require(len(free) == 24, "coefficient rank 104")
    check_upper(calls, witness, columns, target)
    rank_cases = check_rank()
    control_count = controls(calls, witness, columns, target, particular, null)
    histogram = enumerate_pairs(particular, null)
    hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
              for path in sorted(PACKAGE.iterdir()) if path.is_file()}
    result = {"status": "PASS_TWO_BURST_THIN_RANK", "field": "F2",
              "full_order": witness["order"], "gaps": witness["gaps"],
              "coefficient_equations": 1728, "coefficient_rank": 104,
              "free_coordinates": free, "particular": hex(particular),
              "null_basis": [hex(v) for v in null], "solutions": 1 << 24,
              "minimum_rank_sum": 8, "attaining_square_zero_queries": 8,
              "rank_pair_histogram": histogram, "rank_controls": rank_cases,
              "negative_and_enumeration_controls": control_count,
              "package_sha256": hashes,
              "input_sha256": {name: hashlib.sha256(raw).hexdigest()
                               for name, raw in sorted(inputs.items())}}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
