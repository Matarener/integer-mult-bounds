#!/usr/bin/env python3
"""Read register 357 immediately before the first write into register 360.

Register 359 starts at 1. The trace stops before event 9564 and records the
read of that initial value. Later uses of register 360 are not followed.
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
CUT = 9564
LOAD = 9544
SCALE = 9561
SOURCE = 357
MARKER = "PASS_QQ16_ORIGIN_ONE value=1 no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_QQ16_ORIGIN_ONE " + message)


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
    read_value = None
    for index, event in enumerate(events[:CUT]):
        if event[0] != "scalar":
            continue
        if index == LOAD:
            read_value = state[359]
        before = state[SOURCE]
        apply(state, event[1])
        if state[SOURCE] != before:
            changes.append((index, str(state[SOURCE])))
    return state, changes, read_value


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
    packet = json.loads(gzip.decompress(CERTIFICATE.read_bytes()))
    events = expand(packet)
    require(events[LOAD][1] == ["add", ["L", 357], ["L", 359], -2, 1], "the load moved")
    require(events[SCALE][1] == ["scale", ["L", 357], 1, -2], "the scale moved")
    require(events[CUT][1][:3] == ["add", ["L", 360], ["L", 357]], "the first write moved")
    helper, helper_changes, read_value = trace(events, 359)
    data, data_changes, _ = trace(events, 112)
    coefficient = Fraction(events[CUT][1][3], events[CUT][1][4])
    require(helper_changes == [(LOAD, "-2"), (SCALE, "1")], "the source path moved")
    require(data_changes == [], "the data register reached register 357")
    require(read_value == 1, "register 359 had already changed")
    require(helper[360] == 0, "register 360 already held a value")
    require(coefficient * helper[SOURCE] == 1, "the addition no longer writes 1")
    return {
        "register": SOURCE,
        "before_index": CUT,
        "value": str(helper[SOURCE]),
        "data_contribution": str(data[SOURCE]),
        "loaded_at": LOAD,
        "loaded_from": 359,
        "loaded_value": "-2",
        "scaled_at": SCALE,
        "scale": "-1/2",
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
