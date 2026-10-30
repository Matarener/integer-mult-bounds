#!/usr/bin/env python3
"""Certify one four-call partial-observation saving on arbitrary dirty inputs.

Produced by Nick Petalas. Apache-2.0.
"""

import hashlib
import json
import sys
from itertools import combinations_with_replacement, product
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
SOURCE = "research/partial-observation-boundaries/README.md"
SOURCE_HASH = "72ddf7a70241b4b02749361149287772dc39def8d86ec6ffd5eddeaf2470609c"
# Coordinate order is d0, d1, w0, w1. Each gate is (destination, source).
ADAPTERS = ((2, 3), (3, 2), (0, 2), (0, 3), (1, 2), (1, 3))
CHILDREN = ((0, 0, 0), (1, 0, 1), (1, 0, 0), (1, 0, 0))
PARTIAL_MASKS = (3, 1, 3, 3)
FULL_MASKS = (3, 3, 3, 3)
# Five gaps: before child 1 and after children 1, 2, 3, 4.
PARTIAL_WORD = ((), (), ((3, 2),), (), ((2, 3),))
FULL_WORD = ((), ((2, 3),), ((3, 2),), (), ((1, 3),))
EAGER_WORD = ((), ((2, 3),), ((3, 2),), ((2, 3),), ((2, 3),))
FINAL_ROWS = (5, 6, 4, 8)


def require(condition, message):
    """Retain mathematical checks when Python assertions are disabled."""
    if not condition:
        raise ValueError(message)


def validate_schedule(schedule):
    require(len(schedule) == 5, "a schedule must have five gaps")
    require(sum(map(len, schedule)) <= 4, "adapter count exceeds fixture bound")
    require(
        all(gate in ADAPTERS for gap in schedule for gate in gap),
        "gate lies outside the six-adapter alphabet",
    )


def matrix_trace(schedule):
    """Propagate all four independent input coefficients simultaneously."""
    validate_schedule(schedule)
    rows = [1, 2, 4, 8]
    for destination, source in schedule[0]:
        rows[destination] ^= rows[source]
    trace = []
    for index, (output, source, target) in enumerate(CHILDREN):
        rows[output] ^= rows[2 + source]
        rows[2 + target] ^= rows[3 - target]
        for destination, source in schedule[index + 1]:
            rows[destination] ^= rows[source]
        trace.append(tuple(rows))
    return tuple(trace)


def reference_rows():
    rows = [1, 2, 4, 8]
    trace = []
    for output, source, _target in CHILDREN:
        rows[output] ^= 1 << (2 + source)
        trace.append(tuple(rows))
    return tuple(trace)


def matrix_accepts(trace, masks):
    require(len(trace) == len(masks) == 4, "four boundaries are required")
    expected = reference_rows()
    observed = all(
        not (mask & (1 << output)) or row[output] == wanted[output]
        for row, wanted, mask in zip(trace, expected, masks, strict=True)
        for output in range(2)
    )
    return observed and trace[-1] == expected[-1]


def literal_accepts(schedule, masks, initial):
    """Separate interpreter on bits, with explicit indivisible child bodies."""
    d0, d1, w0, w1 = initial
    registers = [d0, d1, w0, w1]
    expected = [d0, d1]
    good = True
    for gap in range(5):
        if gap:
            if gap == 1:
                registers[0] ^= registers[2]
                registers[2] ^= registers[3]
                expected[0] ^= w0
            else:
                registers[1] ^= registers[2]
                expected[1] ^= w0
                if gap == 2:
                    registers[3] ^= registers[2]
                else:
                    registers[2] ^= registers[3]
        for destination, source in schedule[gap]:
            registers[destination] = (registers[destination] + registers[source]) % 2
        if gap:
            for output in range(2):
                if masks[gap - 1] & (1 << output):
                    good = good and registers[output] == expected[output]
    return good and registers == [*expected, w0, w1]


def schedules_of_size(count):
    require(count in (0, 1, 2), "only the complete shorter-word domain is used")
    for gaps in combinations_with_replacement(range(5), count):
        for gates in product(ADAPTERS, repeat=count):
            schedule = [[] for _ in range(5)]
            for gap, gate in zip(gaps, gates, strict=True):
                schedule[gap].append(gate)
            yield tuple(tuple(gap) for gap in schedule)


def check_shorter_words():
    counts = []
    partial_hits = []
    executions = 0
    inputs = tuple(product((0, 1), repeat=4))
    for count in range(3):
        seen = hits = 0
        for schedule in schedules_of_size(count):
            trace = matrix_trace(schedule)
            partial = matrix_accepts(trace, PARTIAL_MASKS)
            full = matrix_accepts(trace, FULL_MASKS)
            bit_partial = bit_full = True
            for initial in inputs:
                bit_partial &= literal_accepts(schedule, PARTIAL_MASKS, initial)
                bit_full &= literal_accepts(schedule, FULL_MASKS, initial)
                executions += 2
            require(
                partial == bit_partial and full == bit_full,
                "coefficient and literal interpreters disagree",
            )
            require(
                not full, "a full-observation word with at most two adapters exists"
            )
            require(
                not partial or count == 2, "partial observation uses fewer than two"
            )
            hits += partial
            seen += 1
        counts.append(seen)
        partial_hits.append(hits)
    require(counts == [1, 30, 540], "shorter-word enumeration is incomplete")
    return counts, partial_hits, executions


def check_controls():
    trace = matrix_trace(PARTIAL_WORD)
    require(not matrix_accepts(trace, FULL_MASKS), "the hidden output was not tested")
    require(
        trace[1][1] ^ reference_rows()[1][1] == 8,
        "the hidden second-boundary error must equal incoming w1",
    )
    omitted = (*PARTIAL_WORD[:-1], ())
    require(
        not matrix_accepts(matrix_trace(omitted), PARTIAL_MASKS),
        "missing final workspace restoration was accepted",
    )
    moved = ((), (), (), PARTIAL_WORD[2], PARTIAL_WORD[4])
    require(
        not matrix_accepts(matrix_trace(moved), PARTIAL_MASKS),
        "moving the first adapter past child 3 was accepted",
    )
    require(
        literal_accepts(PARTIAL_WORD, FULL_MASKS, (0, 0, 0, 0)),
        "the clean-input false-positive control changed",
    )
    require(
        not literal_accepts(PARTIAL_WORD, FULL_MASKS, (0, 0, 0, 1)),
        "a dirty input must expose the hidden-output error",
    )
    try:
        matrix_trace(((), (), ((2, 0),), (), ()))
    except ValueError as error:
        require("alphabet" in str(error), "invalid gate failed for the wrong reason")
    else:
        raise ValueError("output-to-workspace feedback was accepted")
    return 6


def main():
    require(not sys.argv[1:], "the verifier takes no arguments")
    with (ROOT / SOURCE).open("rb") as stream:
        source = stream.read(32769)
    require(len(source) <= 32768, "source contract exceeds the declared size bound")
    require(
        hashlib.sha256(source).hexdigest() == SOURCE_HASH,
        "the pinned predecessor contract changed",
    )
    require(reference_rows()[-1] == FINAL_ROWS, "both output updates must be w0")
    for schedule, masks in (
        (PARTIAL_WORD, PARTIAL_MASKS),
        (FULL_WORD, FULL_MASKS),
        (EAGER_WORD, FULL_MASKS),
    ):
        require(matrix_accepts(matrix_trace(schedule), masks), "positive word failed")
        for initial in product((0, 1), repeat=4):
            require(literal_accepts(schedule, masks, initial), "dirty input failed")
    counts, hits, executions = check_shorter_words()
    controls = check_controls()
    files = ("README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
    hashes = {
        name: hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest()
        for name in files
    }
    receipt = {
        "claim_type": "finite exact certificate with a scoped algebraic proof",
        "partial_adapter_minimum": 2,
        "full_adapter_minimum": 3,
        "complete_xor_bills": {"partial": 10, "full": 11, "eager": 12},
        "shorter_word_counts_by_adapter_count": counts,
        "partial_hits_by_adapter_count": hits,
        "full_hits_through_two_adapters": 0,
        "literal_shorter_program_executions": executions,
        "literal_positive_program_executions": 48,
        "semantic_controls": controls,
        "partial_coefficient_trace": matrix_trace(PARTIAL_WORD),
        "full_coefficient_trace": matrix_trace(FULL_WORD),
        "python": sys.version.split()[0],
        "source_sha256": SOURCE_HASH,
        "package_sha256": hashes,
    }
    print(json.dumps(receipt, sort_keys=True, indent=2))
    print("PASS_FOUR_CALL_PRODUCTIVE_OBSERVATIONS partial=2 full=3 xor=10/11")


if __name__ == "__main__":
    main()
