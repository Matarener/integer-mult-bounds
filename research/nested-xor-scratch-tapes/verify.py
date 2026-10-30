"""Execute the new nested controllers; never replay a predecessor verifier.

Produced by Nick Petalas. Apache-2.0.
"""

import argparse
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))

from machine import (
    BLANK, SEP, compile_machine, compile_visits, invoice, need, visits,
)

PACKAGE_FILES = (
    "README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
    "RESULT.json", "machine.py", "verify.py",
)


def frame(records, origin):
    tape = {origin: SEP, origin - 2: 1, origin - 1: 3}
    position = origin
    for record in records:
        for bit in record:
            need(type(bit) is int and bit in (0, 1), "binary fixture")
            position += 1
            tape[position] = bit
        position += 1
        tape[position] = SEP
    tape[position + 1] = 0
    tape[position + 2] = SEP
    return tape, position


def execute(machine, tapes, origins, limit):
    """Only symbol lookup, finite-state dispatch, writes and unit head moves."""
    need(type(limit) is int and 0 <= limit <= 1_000_000, "step capacity")
    work = [dict(tapes[0]), dict(tapes[1])]
    heads = list(origins)
    minimum, maximum = list(origins), list(origins)
    state = 0
    for steps in range(limit + 1):
        if state == machine.halt:
            return work, tuple(heads), steps, minimum, maximum
        need(steps < limit, "transition budget exhausted")
        a = work[0].get(heads[0], BLANK)
        b = work[1].get(heads[1], BLANK)
        action = machine.table.get((state, a, b))
        need(action is not None and len(action) == 5, "blocked finite control")
        state, w0, w1, m0, m1 = action
        need(type(state) is int and 0 <= state <= machine.halt, "state range")
        for i, value, move in ((0, w0, m0), (1, w1, m1)):
            need(type(move) is int and move in (-1, 0, 1), "nonunit head move")
            if value is not None:
                need(type(value) is int and 0 <= value < 4, "alphabet write")
                work[i][heads[i]] = value
            heads[i] += move
            minimum[i] = min(minimum[i], heads[i])
            maximum[i] = max(maximum[i], heads[i])
    raise ValueError("unreachable exhausted execution")


def check_case(h, delta, width, *, basis=None, candidate=None):
    n = 1 << h
    if basis is None:
        records = [tuple((i * 3 + j + (i >> (j % 3))) % 2
                         for j in range(width)) for i in range(n)]
        dirty = tuple((j + 1) % 2 for j in range(width))
    else:
        records = [tuple(int(i == basis) for _ in range(width)) for i in range(n)]
        dirty = tuple(int(basis == n) for _ in range(width))
    origins = (11, -7)
    initial, end0 = frame(records, origins[0])
    scratch, end1 = frame([dirty], origins[1])
    expected, _ = frame([records[i ^ delta] for i in range(n)], origins[0])
    bill = invoice(h, delta, width)
    machine = candidate if candidate is not None else compile_machine(h, delta)
    result, heads, steps, minimum, maximum = execute(
        machine, (initial, scratch), origins, bill["steps"] + 2000)
    need(result == [expected, scratch], "permutation, dirt or exterior mismatch")
    need(heads == origins, "head return mismatch")
    need(steps == bill["steps"], "exact transition invoice mismatch")
    need(minimum == list(origins), "crossed a left exterior")
    need(maximum[0] <= end0 and maximum[1] <= end1, "crossed a right exterior")
    return steps


def check_schedules():
    cases = strict = 0
    smallest = None
    largest = 0
    for h in range(10):
        n = 1 << h
        for delta in range(n):
            order = visits(h, delta)
            tokens = list(range(n + 1))
            position = travel = 0
            for address in order:
                travel += abs(address - position)
                position = address
                tokens[address], tokens[n] = tokens[n], tokens[address]
            travel += position
            need(tokens == [i ^ delta for i in range(n)] + [n], "token endpoint")
            bill = invoice(h, delta, 2)
            need(travel == bill["record_crossings"], "independent travel sum")
            need(len(order) == bill["record_swaps"], "swap count")
            if delta:
                gain = bill["saved_record_crossings"]
                need(gain >= n - 2, "uniform improvement inequality")
                strict += int(gain > 0)
                if h == 9:
                    smallest = gain if smallest is None else min(smallest, gain)
                    largest = max(largest, gain)
            cases += 1
    return {"cases": cases, "strict_improvements": strict,
            "n512_saved_crossings_min": smallest,
            "n512_saved_crossings_max": largest}


def rejected(action):
    try:
        action()
    except ValueError:
        return 1
    raise ValueError("a rejection control was accepted")


def controls():
    order = visits(2, 2)
    n = 4
    roots = order[:n // 2]
    wrong_order = roots + tuple(v for a in roots for v in (a ^ 2, a))
    wrong = compile_visits(2, 2, wrong_order)
    missing = compile_visits(2, 2, order[:-1])
    good = compile_machine(2, 2)
    bad_move = dict(good.table)
    bad_move[0, SEP, SEP] = (1, None, None, 2, 1)
    bad_write = dict(good.table)
    bad_write[0, SEP, SEP] = (1, 7, None, 1, 1)
    fixture, _ = frame([(0,)] * 4, 0)
    scratch, _ = frame([(1,)], 0)
    broken = dict(fixture)
    broken[0] = BLANK
    checks = (
        lambda: check_case(2, 2, 1, basis=0, candidate=wrong),
        lambda: check_case(2, 2, 1, basis=0, candidate=missing),
        lambda: check_case(2, 2, 1, basis=0, candidate=compile_machine(2, 1)),
        lambda: execute(replace(good, table=bad_move), (fixture, scratch), (0, 0), 50),
        lambda: execute(replace(good, table=bad_write), (fixture, scratch), (0, 0), 50),
        lambda: execute(good, (broken, scratch), (0, 0), 50),
        lambda: execute(good, (fixture, scratch), (0, 0), 0),
        lambda: compile_machine(9, 256),
        lambda: compile_machine(10, 1),
        lambda: compile_machine(3, 8),
        lambda: compile_machine(True, 1),
        lambda: invoice(2, 1, -1),
    )
    return sum(rejected(action) for action in checks)


def science():
    schedules = check_schedules()
    cases = transitions = basis_cases = 0
    for h in range(6):
        for delta in range(1 << h):
            for width in range(4):
                transitions += check_case(h, delta, width)
                cases += 1
    for h in range(4):
        for delta in range(1 << h):
            for basis in range((1 << h) + 1):
                transitions += check_case(h, delta, 1, basis=basis)
                basis_cases += 1
    for delta, width in ((1, 3), (16, 2)):
        transitions += check_case(9, delta, width)
        cases += 1
    return {"status": "PASS_NESTED_XOR_SCRATCH_TAPES", "schedules": schedules,
            "payload_cases": cases, "basis_cases": basis_cases,
            "executed_unit_transitions": transitions,
            "rejecting_controls": controls(),
            "examples": [invoice(2, 2, 1), invoice(9, 1, 3), invoice(9, 16, 2)]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-result", action="store_true")
    args = parser.parse_args()
    result = science()
    expected = json.loads((PACKAGE / "RESULT.json").read_text())
    need(result == expected, "complete RESULT payload differs")
    hashes = {name: sha256((PACKAGE / name).read_bytes()).hexdigest()
              for name in PACKAGE_FILES}
    receipt = {"result": result, "package_sha256": hashes}
    print(json.dumps(receipt if args.emit_result else result, sort_keys=True))


if __name__ == "__main__":
    main()
