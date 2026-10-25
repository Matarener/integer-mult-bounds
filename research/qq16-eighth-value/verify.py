#!/usr/bin/env python3
"""Read register 280 immediately before the second write into register 354.

Register 359 starts at 1. The trace stops before event 19679 and does not
follow the register that first writes register 280.
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
CUT = 19679
ADJUST = 19671
SOURCE = 280
MARKER = "PASS_QQ16_EIGHTH_VALUE value=-1/8 no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_QQ16_EIGHTH_VALUE " + message)


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
    changes = []
    target_at_adjust = None
    for index, event in enumerate(events[:CUT]):
        if event[0] != "scalar":
            continue
        if index == ADJUST:
            target_at_adjust = state[354]
        before = state[SOURCE]
        apply(state, event[1])
        if state[SOURCE] != before:
            changes.append((index, str(state[SOURCE])))
    return state, changes, target_at_adjust


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
    packet = json.loads(gzip.decompress(CERTIFICATE.read_bytes()))
    events = expand(packet)
    require(events[19133][1][:3] == ["add", ["L", 280], ["L", 274]], "the first write moved")
    require(events[ADJUST][1] == ["add", ["L", 280], ["L", 354], -1, 2], "the adjustment moved")
    require(events[CUT][1][:3] == ["add", ["L", 354], ["L", 280]], "the consuming addition moved")
    helper, helper_changes, target_at_adjust = trace(events, 359)
    data, data_changes, _ = trace(events, 112)
    coefficient = Fraction(events[CUT][1][3], events[CUT][1][4])
    require(helper_changes == [(19133, "-1/4"), (ADJUST, "-1/8")], "the source path moved")
    require(data_changes == [], "the data register reached register 280")
    require(target_at_adjust == Fraction(-1, 4), "register 354 had changed before the adjustment")
    require(helper[354] == Fraction(-1, 4), "register 354 had already received the second quarter")
    require(coefficient * helper[SOURCE] == Fraction(-1, 4), "the addition no longer contributes -1/4")
    return {
        "register": SOURCE,
        "before_index": CUT,
        "value": str(helper[SOURCE]),
        "data_contribution": str(data[SOURCE]),
        "first_write": 19133,
        "first_value": "-1/4",
        "second_write": ADJUST,
        "second_from": 354,
        "coefficient": str(coefficient),
        "contribution": str(coefficient * helper[SOURCE]),
        "literal_value": str(256 * helper[SOURCE]),
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
