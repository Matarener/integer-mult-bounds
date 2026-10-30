#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Observe the complete unchanged RootPlan, including retained erased cells."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "research/encoded-minimum-root-prefix"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate():
    rows = json.loads((HERE / "SOURCES.json").read_text())["files"]
    live = tuple(row for row in rows if row["usage"] == "input")
    need(len(live) == 5, "complete five-file source closure")
    for row in live:
        raw = (ROOT / row["path"]).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row["sha256"], row["path"])
    return len(live)


def envelope(values, dimension, divisor, guard, spacing):
    p, selected, left, right, coefficients, rows, _ = values
    b, u, v = p.bit_length(), coefficients.bit_length(), rows.bit_length()
    c, h = (divisor - 1).bit_length(), dimension - 1
    z = left + selected * spacing + right
    return 8 + max(1994 * b, c * h * b, z + u + v + b + guard)


def decode(count):
    from words import RIGHT
    physical = getattr(count.tape, "physical", count.tape)
    raw = physical.cells
    end = raw.index(RIGHT, 1)
    need(end >= 2 and all(bit in (0, 1) for bit in raw[1:end]), "canonical Count")
    return sum(bit << i for i, bit in enumerate(raw[1:end]))


def snapshot(counts):
    return tuple((bytes(count.tape.cells), count.tape.head) for count in counts)


class Observation:
    def __init__(self, tapes):
        need(len(tapes) == 285 and len({id(t) for t in tapes}) == 285,
             "256 scratch tapes and 29 distinct fields")
        self.tapes = tapes
        self.slots = {id(tape): i for i, tape in enumerate(tapes)}
        self.initial = [len(tape.cells) for tape in tapes]
        self.exact = self.initial[:]
        self.bound = self.initial[:]
        self.writes = 0
        self.active = False

    def begin(self, capacity):
        self.bound = [max(old, capacity) for old in self.bound]
        self.active = True

    def write(self, original, tape, symbol):
        if not self.active:
            return original(tape, symbol)
        need(id(tape) in self.slots, "no unaccounted numerical tape writes")
        original(tape, symbol)
        i = self.slots[id(tape)]
        self.exact[i] = max(self.exact[i], tape.head + 1)
        self.writes += 1
        need(len(tape.cells) == self.exact[i], "exact per-tape high-water identity")
        need(len(tape.cells) <= self.bound[i], "complete caller extent envelope")

    def finish(self):
        self.active = False
        need([len(tape.cells) for tape in self.tapes] == self.exact,
             "physical identities hold after the complete call and clear")


def warm(tapes):
    from words import BLANK, LEFT
    # Prepare erased backing before observation. No execution is changed.
    for i in (0, 255, 256, 284):
        tape = tapes[i]
        for _ in range(9001 + i):
            tape.append(0)
        tape.clear()
        need(tape.cells[0] == LEFT and all(v == BLANK for v in tape.cells[1:]),
             "warm backing is entirely erased")


def execute(plan, values, spacing, observer):
    from cardinal_counts import Count
    from words import BLANK
    counts = tuple(Count.literal(value) for value in values)
    before = snapshot(counts)
    capacity = envelope(values, plan.dimension, plan.level_divisor,
                        plan.guard_exponent, spacing)
    observer.begin(capacity)
    try:
        result = plan.compute(*counts)
        need(result is plan and plan.closed and not plan.pool.live, "successful whole planner")
        need(snapshot(counts) == before, "all seven borrowed inputs preserved")
        need(decode(plan.count("K")) == spacing, "declared spacing is actual output K")
        need(all(decode(plan.count(name)) >= 0 for name in plan.roles), "all 29 fields canonical")
        record = {"capacity": capacity, "fast": plan.fast,
                  "max_extent": max(len(t.cells) for t in observer.tapes),
                  "retained_total": sum(len(t.cells) for t in observer.tapes)}
        plan.clear()
        need(all(tape.read() == BLANK for tape in observer.tapes), "all owned bodies cleared")
        observer.finish()
    finally:
        observer.active = False
        for count in counts:
            count.close()
    return record


def history(reduced, warmed):
    import planner
    from cardinal_counts import Count
    from records import Tape

    class Reduced(planner.MinimumRootPlan):
        def parameters(self, precision):
            return tuple(Count.literal(value) for value in (8, 1, 1, 1, 32))

    cls = Reduced if reduced else planner.MinimumRootPlan
    plan = cls(2, 1, 6, guard_exponent=2)
    tapes = (*plan.pool.tapes, *plan.roles.values())
    if warmed:
        warm(tapes)
    observer = Observation(tapes)
    original = Tape.write
    cases = ((9, 8, 0, 0, 1, 1, 0), (9, 8, 7, 3, 13, 5, 0),
             (9, 0, 0, 0, 1, 1, 0)) if reduced else ((2, 0, 1, 0, 3, 5, 0),)
    records = []
    try:
        Tape.write = lambda tape, symbol: observer.write(original, tape, symbol)
        for values in cases:
            records.append(execute(plan, values, 1, observer))
    finally:
        observer.active = False
        Tape.write = original
    if warmed:
        need(records[-1]["max_extent"] > records[-1]["capacity"],
             "reject forgetting preexisting erased backing")
    if reduced:
        need([record["fast"] for record in records] == [True, True, False],
             "complete fast and direct branches exercised")
    return {"reduced_parameters": reduced, "warm": warmed, "calls": records,
            "writes": observer.writes, "peak_leases": plan.pool.peak}


def symbolic_controls():
    checks = 0
    for p in range(2, 66):
        b = p.bit_length()
        need(4 * b + 6 < 2 ** (b + 3), "parameter logarithm envelope")
        need((p ** 997 + 1) ** 2 < 2 ** (1994 * b + 2), "uncropped cap product")
        for g in (0, 2, 17, 210000):
            need((p + 2 * p * (1 << g) + 3).bit_length() <= b + g + 3,
                 "work precision envelope")
            checks += 1
    lower_bounds = 0
    for left in (0, 1, 2, 7, 31, 4096, 65536):
        count = 1 << left
        need(count.bit_length() + 2 == left + 3, "necessary address-power field extent")
        if left >= 4096:
            values = (2, 0, left, 0, 1, 1, 0)
            wrong = envelope((2, 0, left.bit_length(), 0, 1, 1, 0), 2, 6, 2, 1)
            need(count.bit_length() + 2 > wrong, "reject digit-only side-width accounting")
            need(count.bit_length() + 2 <= envelope(values, 2, 6, 2, 1), "numeric address bound")
        lower_bounds += 1
    return {"parameter_checks": checks, "address_lower_bound_fixtures": lower_bounds}


def cleanup_sources():
    # These five authenticated loaders own all extracted source trees.
    for name in ("source", "native_sources", "phase_sources", "leaf_sources", "retained"):
        module = sys.modules.get(name)
        temporary = getattr(module, "_temporary", None)
        need(isinstance(temporary, tempfile.TemporaryDirectory), "known source-tree owner")
        temporary.cleanup()


def main():
    started = time.monotonic()
    inputs = authenticate()
    sys.path.insert(0, str(SOURCE))
    controls = symbolic_controls()
    try:
        histories = [history(False, False), history(True, False), history(True, True)]
    finally:
        cleanup_sources()
    need(sum(len(row["calls"]) for row in histories) == 7, "seven complete planner calls")
    names = ("PROOF.md", "README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
    files = tuple(HERE / name for name in names)
    receipt = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in files}
    print(json.dumps({"status": "PASS_ROOTPLAN_BACKING_ENVELOPE", "source_inputs": inputs,
                      "controls": controls, "histories": histories, "sha256": receipt,
                      "elapsed_seconds": round(time.monotonic() - started, 3)}, indent=2))


if __name__ == "__main__":
    main()
