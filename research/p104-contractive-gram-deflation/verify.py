#!/usr/bin/env python3
"""Exact contractive Gram deflation certificate; standard library only."""

import argparse
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(vector):
    need(len(vector) == 8 and any(vector), "nonzero eight-coordinate root")
    first = next(x for x in vector if x)
    return tuple(x if first > 0 else -x for x in vector)


def dot(left, right):
    return sum(x * y for x, y in zip(left, right, strict=True))


def roots_and_missing(data):
    signs = data["signs"]
    need(isinstance(signs, list) and len(signs) == 16, "sixteen omitted lines")
    missing = set()
    for text in signs:
        need(isinstance(text, str) and len(text) == 8
             and set(text) <= {"+", "-"}, "invalid sign row")
        need(text.count("-") % 2 == 1, "half-spin parity")
        missing.add(canonical(tuple(1 if s == "+" else -1 for s in text)))
    need(len(missing) == 16, "duplicate omitted line")
    d8 = set()
    for i, j in itertools.combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            d8.add(tuple(row))
    half = {canonical((1, *tail)) for tail in itertools.product((-1, 1), repeat=7)
            if tail.count(-1) % 2 == 1}
    need(len(d8) == 56 and len(half) == 64, "root-shell sizes")
    need(missing <= half, "omitted line outside half shell")
    ports = sorted(d8 | (half - missing))
    need(len(ports) == 104 and all(dot(r, r) == 8 for r in ports), "port norms")
    return sorted(d8), ports, sorted(missing)


def projector_check(q):
    # Coordinates are doubled: D = I - q*q^T/8.
    matrix = [[8 * (i == j) - q[i] * q[j] for j in range(8)] for i in range(8)]
    need(dot(q, q) == 8, "projector normalization")
    need(all(sum(matrix[i][k] * matrix[k][j] for k in range(8))
             == 8 * matrix[i][j] for i in range(8) for j in range(8)),
         "idempotent projector")
    need(all(dot(row, q) == 0 for row in matrix), "projector kernel")
    need(sum(matrix[i][i] for i in range(8)) == 56, "rank-seven trace")


def witness(q, ports):
    projector_check(q)
    products = [dot(r, q) for r in ports]
    histogram = Counter()
    for left in products:
        for right in products:
            histogram[left * right] += 1
    # E_ij = numerator/64, for these doubled root coordinates.
    need(max(abs(n) for n in histogram) == 16, "sharp quarter error")
    need(set(histogram) <= {-16, 0, 16}, "coefficient error alphabet")
    return {"omitted_root_doubled": list(q), "nonzero_mode_entries": sum(x != 0 for x in products),
            "error_numerators_over_64": {str(k): histogram[k] for k in sorted(histogram)}}


def inequality_fixtures(d8):
    count = 0
    for vector in itertools.product((-1, 0, 1), repeat=8):
        norm = dot(vector, vector)
        if norm == 0:
            continue
        largest = max(abs(dot(root, vector)) for root in d8)
        # Actual D8 roots are root/2. No square roots enter this test.
        need(largest * largest >= 2 * norm, "D8 unit-direction floor")
        count += 1
    return count


def controls(data, ports):
    invalid_parity = {**data, "signs": ["++++++++", *data["signs"][1:]]}
    duplicate = {**data, "signs": [data["signs"][0], *data["signs"][:-1]]}
    rejected = []
    for name, mutant in (("wrong_half_spin_parity", invalid_parity),
                         ("duplicate_omitted_line", duplicate)):
        try:
            roots_and_missing(mutant)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("invalid input accepted: " + name)
    try:
        witness(ports[0], ports)
    except ValueError as error:
        need(str(error) == "sharp quarter error", "retained-root control diagnostic")
        rejected.append("deflating_a_retained_root_is_worse")
    else:
        raise ValueError("retained-root deflation accepted at quarter error")
    return rejected


def compute(package):
    data = json.loads((package / "MISSING.json").read_text())
    d8, ports, missing = roots_and_missing(data)
    witnesses = [witness(q, ports) for q in missing]
    files = ("README.md", "PROOF.md", "verify.py", "MISSING.json", "TASK.json", "VERIFY.json", "SOURCES.json")
    return {"schema_version": 1, "claim_type": "scoped proof", "sharp_max_entry_error": "1/4",
            "d8_root_lines": len(d8), "retained_root_lines": len(ports),
            "omitted_root_witnesses": len(witnesses), "witnesses": witnesses,
            "explicit_error_entries": len(witnesses) * len(ports) ** 2,
            "integer_direction_fixtures": inequality_fixtures(d8),
            "controls": controls(data, ports),
            "source_sha256": {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
                              for name in files}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write a generated receipt outside checkout")
    args = parser.parse_args()
    package = Path(__file__).resolve().parent
    result = compute(package)
    if args.output is not None:
        need(not args.output.resolve().is_relative_to(package.parents[1]),
             "receipt output must be outside checkout")
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    else:
        expected = json.loads((package / "RESULT.json").read_text())
        need(result == expected, "generated receipt differs")
    print("PASS_P104_CONTRACTIVE_GRAM_DEFLATION " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
