#!/usr/bin/env python3
"""Read the native channel word for an I-G/2 correction of one coefficient.

The witness is one program. This replay follows its additions and records
whether X0's coefficient in Y34 ever leaves 1/2. It does not import the
channel checker.
"""

import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
CHANNEL = ROOT / "research/p104-native-channel"
MARKER = (
    "PASS_P104_CHANNEL_CORRECTION_ABSENT opcodes=5 "
    "flag0=1/2 unchanged no_new_kappa"
)
OPCODES = ("add", "copy", "erase", "transport", "zero")


def fail(message):
    raise SystemExit("FAIL_P104_CHANNEL_CORRECTION_ABSENT " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "research/p104-native-channel/EXPECTED.json",
        "research/p104-native-channel/TASK.json",
        "research/p104-native-channel/inputs/LOWRANK-WITNESS.json",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def coefficient_trace(program, names):
    state = {name: {name: Fraction(1)} for name in names}
    seen = []
    for index, event in enumerate(program):
        op = event[0]
        if op == "transport":
            pass
        elif op == "zero":
            state[event[1]] = {}
        elif op == "erase":
            state.pop(event[1], None)
        elif op == "copy":
            _op, reg, src, _frame = event
            state[reg] = dict(state[src])
        elif op == "add":
            _op, reg, src, coeff, _frame = event
            coeff = Fraction(str(coeff))
            state.setdefault(reg, {})
            for origin, value in list(state.get(src, {}).items()):
                updated = state[reg].get(origin, Fraction(0)) + coeff * value
                if updated:
                    state[reg][origin] = updated
                else:
                    state[reg].pop(origin, None)
        else:
            fail("unknown event " + op)
        if state.get("Y34", {}).get("X0"):
            seen.append((index, state["Y34"]["X0"]))
    return seen


def evaluate():
    authenticate()
    expected = json.loads((CHANNEL / "EXPECTED.json").read_text(encoding="utf-8"))
    task = json.loads((CHANNEL / "TASK.json").read_text(encoding="utf-8"))
    witness = json.loads((CHANNEL / "inputs/LOWRANK-WITNESS.json").read_text(encoding="utf-8"))
    require("No I-G/2 side correction" in expected["scope"], "the expected scope changed")
    blocker = task["open_questions"][0]["blocked_by"]
    require(blocker == "No complete compatible side word or fully charged profile supplied.", "the side-word blocker changed")
    require(sorted(witness) == ["final_frames", "initial_frames", "program"], "the witness gained a section")
    counts = Counter(event[0] for event in witness["program"])
    require(set(counts) == set(OPCODES), "an unexpected opcode appeared")
    require(counts["add"] == expected["scalar_events"]["add"], "the add count left the receipt")
    require(sum(counts.values()) == 4058, "the program length changed")
    trace = coefficient_trace(witness["program"], list(witness["initial_frames"]))
    values = sorted({str(value) for _index, value in trace})
    require(trace and trace[0][0] == 2815 and values == ["1/2"], "the coefficient did not stay at 1/2")
    return {
        "witness_keys": sorted(witness),
        "opcodes": {name: counts[name] for name in OPCODES},
        "correction_opcodes": 0,
        "scope_excludes_correction": True,
        "side_word_supplied": False,
        "flag0": {
            "first_event": trace[0][0],
            "final_coefficient": "1/2",
            "distinct_values": values,
        },
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
