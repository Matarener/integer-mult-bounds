#!/usr/bin/env python3
"""Bounded exact corroboration of the written unique-write batching proof.

No predecessor executable is imported. No output files are written.
Copyright 2026 Nick Petalas. Apache-2.0.
"""

import hashlib
import itertools
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
from batching import (
    MAX_CELLS, checked_word, execute, first_conflict, safe_order,
)


def require(condition: bool, description: str) -> None:
    if not condition:
        raise ValueError(description)


def operators(cells: int, word: tuple) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Independent formal-column replay; row bits encode arbitrary input data."""
    entry = tuple(1 << i for i in range(cells))
    serial = list(entry)
    snapshot = list(entry)
    for target, source in word:
        serial[target] = serial[target] ^ serial[source]
        snapshot[target] = snapshot[target] ^ entry[source]
    return tuple(serial), tuple(snapshot)


def has_cycle(cells: int, word: tuple) -> bool:
    """Independent Boolean reachability closure, without using the planner."""
    rows = [0] * cells
    for target, source in word:
        rows[source] |= 1 << target
    for middle in range(cells):
        for source in range(cells):
            if rows[source] >> middle & 1:
                rows[source] |= rows[middle]
    return any(row >> i & 1 for i, row in enumerate(rows))


def check_word(cells: int, word: tuple, totals: dict) -> None:
    serial, snapshot = operators(cells, word)
    conflict = first_conflict(cells, word)
    require((conflict is None) == (serial == snapshot), "snapshot criterion")
    totals["words"] += 1
    totals["safe" if conflict is None else "unsafe"] += 1
    if conflict is not None:
        require(word[conflict.first][0] == word[conflict.second][1], "conflict edge")
        require(conflict.first < conflict.second, "chronological conflict")
        require((serial[conflict.output] ^ snapshot[conflict.output]) >> conflict.basis & 1,
                "formal basis discrepancy")
        witness = tuple(int(i == conflict.basis) for i in range(cells))
        left = execute(cells, word, witness, snapshot=False)
        right = execute(cells, word, witness, snapshot=True)
        require(left[conflict.output] != right[conflict.output], "literal witness")
        totals["literal_witnesses"] += 1
    order = safe_order(cells, word)
    cycle = has_cycle(cells, word)
    require((order is None) == cycle, "safe ordering iff acyclic")
    if order is not None:
        require(sorted(order) == list(range(len(word))), "event permutation")
        changed = tuple(word[i] for i in order)
        require(first_conflict(cells, changed) is None, "planner contract")
        left, right = operators(cells, changed)
        require(left == right == snapshot, "planner preserves snapshot endpoint")
    else:
        totals["cyclic_words"] += 1


def exhaustive(totals: dict) -> None:
    """All ordered unique-destination words on 1..5 cells."""
    for cells in range(1, 6):
        for length in range(cells + 1):
            for targets in itertools.permutations(range(cells), length):
                choices = tuple(tuple(s for s in range(cells) if s != t) for t in targets)
                for sources in itertools.product(*choices):
                    word = tuple(zip(targets, sources))
                    check_word(cells, word, totals)


def payload_fixtures() -> int:
    count = 0
    words = (((1, 0), (2, 1)), ((2, 1), (1, 0)), ((0, 1), (1, 0)), ())
    for word in words:
        for values in itertools.product(range(4), repeat=3):
            rows, snap = operators(3, word)
            for snapshot, matrix in ((False, rows), (True, snap)):
                expected = []
                for row in matrix:
                    value = 0
                    for column in range(3):
                        if row >> column & 1:
                            value ^= values[column]
                    expected.append(value)
                require(execute(3, word, values, snapshot=snapshot) == tuple(expected),
                        "dirty multi-bit execution")
                count += 1
    return count


def rejection_controls() -> int:
    cases = ((True, ()), (0, ()), (MAX_CELLS + 1, ()), (2, None),
             (2, ((0,),)), (2, ((0, 2),)), (2, ((0, True),)),
             (2, ((0, 0),)), (2, ((0, 1), (0, 1))), (2, ((-1, 1),)))
    for cells, word in cases:
        try:
            checked_word(cells, word)
        except ValueError:
            continue
        raise ValueError("invalid word accepted")
    invalid = ((0,), (0, -1), (0, True), (0, 1 << 256), None)
    for values in invalid:
        try:
            execute(2, ((1, 0),), values, snapshot=False)
        except ValueError:
            continue
        raise ValueError("invalid payload accepted")
    try:
        execute(2, (), (0, 0), snapshot=1)
    except ValueError:
        return len(cases) + len(invalid) + 1
    raise ValueError("non-Boolean execution mode accepted")


def boundary_controls() -> dict:
    chain = tuple((i, i - 1) for i in range(1, MAX_CELLS))
    conflict = first_conflict(MAX_CELLS, chain)
    require(conflict is not None and conflict.second == 1, "long-chain witness")
    order = safe_order(MAX_CELLS, chain)
    require(order == tuple(reversed(range(len(chain)))), "long-chain schedule")
    reversed_chain = tuple(chain[i] for i in order)
    require(first_conflict(MAX_CELLS, reversed_chain) is None, "long-chain safety")
    cycle = chain + ((0, MAX_CELLS - 1),)
    require(safe_order(MAX_CELLS, cycle) is None, "long-cycle obstruction")
    require(execute(2, ((1, 0),), (1 << 255, 7), snapshot=False)
            == (1 << 255, (1 << 255) ^ 7), "max payload bit")
    # Without unique destinations, the first discrepancy can cancel later.
    repeated = ((1, 0), (2, 1)) * 4
    serial, snapshot = operators(3, repeated)
    require(serial == snapshot == (1, 2, 4), "repeated-write cancellation boundary")
    return {"long_chain_cells": MAX_CELLS, "long_cycle_cells": MAX_CELLS,
            "repeated_write_cancellation_events": len(repeated), "controls": 6}


def file_hashes() -> dict:
    paths = sorted(p for p in PACKAGE.iterdir() if p.is_file())
    require(len(paths) <= 16, "bounded package inventory")
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def main() -> None:
    totals = {"words": 0, "safe": 0, "unsafe": 0,
              "literal_witnesses": 0, "cyclic_words": 0}
    exhaustive(totals)
    result = {"status": "PASS_UNIQUE_WRITE_XOR_BATCHING", "claim_type": "scoped proof",
              "exact_operator_census": totals, "dirty_payload_executions": payload_fixtures(),
              "invalid_input_rejections": rejection_controls(), "boundaries": boundary_controls(),
              "package_sha256": file_hashes()}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
