#!/usr/bin/env python3
"""Record scalar changes of register 39 from event 24284 through 24437.

Register 359 starts at 1. The trace applies event 24284 and stops before
event 24438.
"""

import gzip
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
CHECKER = ROOT / "research/qq16-native-dirty-fault/verify.py"
CERTIFICATE = ROOT / "research/joint-query/certificate.json.gz"
START = 24284
END = 24437
TARGET = 39
MARKER = "PASS_QQ16_HELD_FOUR value=-4 no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_QQ16_HELD_FOUR " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def reg(token):
    kind, index = token
    require(type(index) is int and kind in ("L", "C"), "register type")
    return index + 704 * (kind == "C")


def apply(state, gate):
    kind, destination = gate[0], reg(gate[1])
    if kind == "clear":
        state[destination] = Fraction(0)
    elif kind == "scale":
        state[destination] *= Fraction(gate[2], gate[3])
    else:
        require(kind == "add", "scalar kind")
        source = reg(gate[2])
        state[destination] += Fraction(gate[3], gate[4]) * state[source]


def expand(packet):
    result = []
    for event in packet["programs"]["F_0"]:
        if event[0] == "retained_core":
            result.extend(packet["core_words"]["forward"])
        elif event[0] in ("cover_sweep", "private_sweep"):
            result.extend(event[2])
        else:
            result.append(event)
    return result


def trace(events, seed):
    state = [Fraction(0)] * 712
    state[seed] = Fraction(1)
    entered = None
    changes = []
    for index, event in enumerate(events[:END + 1]):
        if event[0] != "scalar":
            continue
        if index == START:
            entered = state[TARGET]
        before = state[TARGET]
        apply(state, event[1])
        if state[TARGET] != before and index >= START:
            changes.append([index, str(state[TARGET])])
    return state, entered, changes


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "research/qq16-native-dirty-fault/verify.py",
        "research/joint-query/certificate.json.gz",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def evaluate():
    authenticate()
    checker = CHECKER.read_text(encoding="utf-8")
    require("state[dst] += Q(gate[3], gate[4]) * state[src]" in checker, "the addition rule moved")
    require("state[dst] *= Q(gate[2], gate[3])" in checker, "the scale rule moved")
    require('if event[0] == "scalar":' in checker, "the scalar guard moved")
    require('need(len(result) == 26099' in checker, "the event count moved")
    packet = json.loads(gzip.decompress(CERTIFICATE.read_bytes()))
    events = expand(packet)
    require(len(events) == 26099, "the expanded word changed length")
    window = events[START:END + 1]
    require(len(window) == 154 and all(event[0] == "scalar" for event in window), "the window is no longer 154 scalar events")
    require(events[START][1][:3] == ["add", ["L", 39], ["L", 354]], "the doubling addition moved")
    require(events[END + 1] == ["scalar", ["add", ["L", 39], ["L", 359], 4, 1], 1], "the fault event moved")
    helper, entered, changes = trace(events, 359)
    data, data_entered, data_changes = trace(events, 112)
    require(entered == -2, "register 39 did not enter the window at -2")
    require(changes == [[24284, "-4"]], "the window changes moved")
    require(helper[TARGET] == -4, "register 39 did not finish at -4")
    require(data_entered == 0 and data_changes == [] and data[TARGET] == 0, "the data register reached register 39")
    return {
        "register": TARGET,
        "from_index": START,
        "through_index": END,
        "scalar_events": len(window),
        "changes": changes,
        "value_before": str(entered),
        "value": str(helper[TARGET]),
        "data_contribution": str(data[TARGET]),
        "literal_value": str(256 * helper[TARGET]),
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
