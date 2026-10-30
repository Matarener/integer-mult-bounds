#!/usr/bin/env python3
"""Read the scalar changes of register 356 before event 19156.

Register 359 starts at 1. The trace records the two source reads. The value
of register 354 at event 24284 is not followed.
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
CUT = 19156
FIRST = 11809
SECOND = 16017
SOURCE = 356
MARKER = "PASS_QQ16_LATER_HALF value=1/2 no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_QQ16_LATER_HALF " + message)


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
            reads[360] = state[360]
        if index == SECOND:
            reads[292] = state[292]
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
    require(events[FIRST][1] == ["add", ["L", 356], ["L", 360], 1, 1], "the copy moved")
    require(events[SECOND - 1][1] == ["add", ["L", 292], ["L", 356], 1, 1], "the preceding copy moved")
    require(events[SECOND][1] == ["add", ["L", 356], ["L", 292], -1, 2], "the halving moved")
    helper, helper_changes, reads = trace(events, 359)
    data, data_changes, _ = trace(events, 112)
    require(helper_changes == [(FIRST, "1"), (SECOND, "1/2")], "the source path moved")
    require(data_changes == [], "the data register reached register 356")
    require(reads[360] == 1 and reads[292] == 1, "a source read moved")
    require(helper[SOURCE] == Fraction(1, 2), "the value before event 19156 moved")
    return {
        "register": SOURCE,
        "before_index": CUT,
        "value": str(helper[SOURCE]),
        "data_contribution": str(data[SOURCE]),
        "first_write": FIRST,
        "first_from": 360,
        "first_read": str(reads[360]),
        "second_write": SECOND,
        "second_from": 292,
        "second_read": str(reads[292]),
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
