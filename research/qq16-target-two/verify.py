#!/usr/bin/env python3
"""Read the scalar changes of register 39 before event 23304.

Register 359 starts at 1. The trace records the two source reads and does
not follow register 18.
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
CUT = 23304
FIRST = 23237
SECOND = 23278
SOURCE = 39
MARKER = "PASS_QQ16_TARGET_TWO value=-2 no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_QQ16_TARGET_TWO " + message)


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
    reads = {}
    for index, event in enumerate(events[:CUT]):
        if event[0] != "scalar":
            continue
        if index == FIRST:
            reads[18] = state[18]
        if index == SECOND:
            reads[343] = state[343]
        before = state[SOURCE]
        apply(state, event[1])
        if state[SOURCE] != before:
            changes.append((index, str(state[SOURCE])))
    return state, changes, reads


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
    require(events[FIRST][1] == ["add", ["L", 39], ["L", 18], 1, 1], "the first write moved")
    require(events[SECOND][1] == ["add", ["L", 39], ["L", 343], -1, 2], "the second write moved")
    helper, helper_changes, reads = trace(events, 359)
    data, data_changes, _ = trace(events, 112)
    require(helper_changes == [(FIRST, "-4"), (SECOND, "-2")], "the target path moved")
    require(data_changes == [], "the data register reached register 39")
    require(reads[18] == -4 and reads[343] == -4, "a source read moved")
    require(helper[SOURCE] == -2, "the value before event 23304 moved")
    return {
        "register": SOURCE,
        "before_index": CUT,
        "value": str(helper[SOURCE]),
        "data_contribution": str(data[SOURCE]),
        "first_write": FIRST,
        "first_value": "-4",
        "first_from": 18,
        "first_read": str(reads[18]),
        "second_write": SECOND,
        "second_from": 343,
        "second_read": str(reads[343]),
        "second_coefficient": "-1/2",
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
