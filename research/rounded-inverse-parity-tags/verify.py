"""Finite certificate and literal recovery controls. Writes only to stdout.

Produced by Nick Petalas. Apache-2.0.
"""

import hashlib
import json
import math
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from parity import (INPUT_BITS, MODES, OWNERS, SELECTED, collision_pair, decode,
                    directions, encode, forward, matrix, need, right_inverse)

ROOT = Path(__file__).resolve().parent
PACKAGE_FILES = ("MATRIX.json", "PROOF.md", "README.md", "SOURCES.json",
                 "TASK.json", "VERIFY.json", "parity.py", "verify.py")


def reference(rows, values):
    columns = tuple(zip(*rows))
    quotients = []
    for column in columns:
        value = Fraction(4 * sum(a * b for a, b in zip(column, values)), 13)
        rounded = math.floor(abs(value) + Fraction(1, 2))
        quotients.append(rounded if value >= 0 else -rounded)
    result = [16 * a for a in values]
    for j in range(MODES):
        for i in range(OWNERS):
            result[i] -= columns[j][i] * quotients[j]
    return tuple(result)


def signatures_and_collisions(rows, basis):
    candidates = directions(rows)
    signatures = {}
    for v, difference in candidates:
        left, right = collision_pair(rows, basis, v)
        need(left != right, "collision inputs must differ")
        expected = reference(rows, left)
        need(reference(rows, right) == expected, "literal collision reference")
        need(forward(rows, left) == expected, "forward left reference")
        need(forward(rows, right) == expected, "forward right reference")
        need(tuple(b - a for a, b in zip(left, right)) == difference,
             "collision difference")
        need(any(difference[i] % 2 for i in SELECTED),
             "literal five-coordinate separation")
        mask = sum((a % 2) << i for i, a in enumerate(difference))
        need(mask != 0, "undetectable coordinate collision")
        signatures.setdefault(mask, v)
    need(len(candidates) == 480 and len(signatures) == 128, "collision domain")
    return signatures, len(candidates)


def coverage(signatures):
    masks = tuple(sorted(signatures))
    tests = tuple(sum(((mask >> i) & 1) << j for j, mask in enumerate(masks))
                  for i in range(OWNERS))
    full = (1 << len(masks)) - 1
    selected_cover = 0
    for i in SELECTED:
        selected_cover |= tests[i]
    need(selected_cover == full, "five-coordinate upper bound")
    return masks, tests, full


def four_set_certificate(tests, full):
    histogram = Counter()
    count = 0
    for a in range(OWNERS - 3):
        for b in range(a + 1, OWNERS - 2):
            pair = tests[a] | tests[b]
            for c in range(b + 1, OWNERS - 1):
                triple = pair | tests[c]
                for d in range(c + 1, OWNERS):
                    uncovered = full & ~(triple | tests[d])
                    need(uncovered != 0, "four coordinates unexpectedly suffice")
                    histogram[uncovered.bit_count()] += 1
                    count += 1
    need(count == math.comb(OWNERS, 4), "complete four-set enumeration")
    need(min(histogram) == 4, "sharp best four-set coverage")
    return count, dict(sorted(histogram.items()))


def omission_controls(rows, basis, signatures, masks, tests, full):
    controls = []
    for omitted in SELECTED:
        retained = tuple(i for i in SELECTED if i != omitted)
        cover = 0
        for i in retained:
            cover |= tests[i]
        missing = full & ~cover
        need(missing != 0, "each selected coordinate must matter")
        index = (missing & -missing).bit_length() - 1
        v = signatures[masks[index]]
        left, right = collision_pair(rows, basis, v)
        need(forward(rows, left) == forward(rows, right), "omission collision")
        need(tuple(left[i] % 2 for i in retained) ==
             tuple(right[i] % 2 for i in retained), "omission parity agreement")
        need(left[omitted] % 2 != right[omitted] % 2, "omitted bit separates")
        for values in (left, right):
            output, tags = encode(rows, values)
            need(decode(rows, basis, output, tags) == values,
                 "omission-control decoder roundtrip")
        controls.append({"omitted": omitted, "direction": list(v),
                         "left": list(left), "right": list(right)})
    return controls


def decoder_checks(rows, basis):
    fixtures = [tuple(0 for _ in range(OWNERS))]
    fixtures += [tuple(int(i == j) for i in range(OWNERS)) for j in range(OWNERS)]
    for seed in range(16):
        fixtures.append(tuple(((i * i + seed * 19 * i + 7) % 43) - 21
                              for i in range(OWNERS)))
    for sign in (-1, 1):
        fixtures.append(tuple(sign * ((1 << (INPUT_BITS - 1)) + i)
                              for i in range(OWNERS)))
    for values in fixtures:
        output, tags = encode(rows, values)
        need(output == reference(rows, values), "decoder reference fixture")
        need(decode(rows, basis, output, tags) == values, "exact decoder roundtrip")
    need(len(fixtures) == 131, "decoder fixture census")
    return len(fixtures)


def invalid_inputs(rows, basis):
    zero = (0,) * OWNERS
    cases = (("input", zero[:-1], ()),
             ("input", (True,) + zero[1:], ()),
             ("input", (1 << INPUT_BITS,) + zero[1:], ()),
             ("decode", zero[:-1], (0,) * 5),
             ("decode", zero, (0,) * 4),
             ("decode", zero, (2,) + (0,) * 4),
             ("decode", zero, (1,) * 5))
    for kind, values, tags in cases:
        try:
            if kind == "input":
                encode(rows, values)
            else:
                decode(rows, basis, values, tags)
        except ValueError:
            continue
        raise ValueError("invalid input accepted: " + kind)
    return len(cases)


def file_hashes():
    result = {}
    for name in PACKAGE_FILES:
        path = ROOT / name
        need(path.is_file() and not path.is_symlink(), "regular package file")
        need(path.stat().st_size <= 1 << 20, "package-file size bound")
        result[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def main():
    rows = matrix()
    basis = right_inverse(rows)
    for j, (a, b, sign) in enumerate(basis):
        need(tuple(rows[a][k] + sign * rows[b][k] for k in range(MODES)) ==
             tuple(2 * int(k == j) for k in range(MODES)), "decoder right inverse")
    signatures, direction_count = signatures_and_collisions(rows, basis)
    masks, tests, full = coverage(signatures)
    four_sets, histogram = four_set_certificate(tests, full)
    controls = omission_controls(rows, basis, signatures, masks, tests, full)
    rounds = decoder_checks(rows, basis)
    rejected = invalid_inputs(rows, basis)
    receipt = {"status": "PASS_ROUNDED_INVERSE_PARITY_TAGS", "minimum_bits": 5,
               "selected_zero_based_owners": list(SELECTED),
               "signed_collision_directions": direction_count,
               "distinct_parity_signatures": len(masks),
               "four_coordinate_sets": four_sets,
               "four_set_uncovered_histogram": histogram,
               "omission_controls": controls, "decoder_roundtrips": rounds,
               "omission_control_roundtrips": 2 * len(controls),
               "rejected_input_classes": rejected,
               "two_unit_row_witnesses": basis,
               "package_sha256": file_hashes()}
    print(json.dumps(receipt, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
