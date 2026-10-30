#!/usr/bin/env python3
"""Track the scalar coefficient of register 359 up to the fault.

Only scalar additions, scales and clears update the state. The trace stops
before event 24438 and does not follow the restoring source.
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
FAULT = 24438
REGISTER = 359
MARKER = "PASS_QQ16_CUT_COEFFICIENT coefficient=1 no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_QQ16_CUT_COEFFICIENT " + message)


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
    for index, event in enumerate(events[:FAULT]):
        if event[0] != "scalar":
            continue
        before = state[REGISTER]
        apply(state, event[1])
        if state[REGISTER] != before:
            changes.append((index, str(state[REGISTER])))
    return state, changes


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
    require("state[dst] *= Q(gate[2], gate[3])" in checker, "the scale rule moved")
    require("state[dst] += Q(gate[3], gate[4]) * state[src]" in checker, "the addition rule moved")
    require('if event[0] == "scalar":' in checker, "the scalar filter moved")
    require("cut_dirty == (-4, 1)" in checker, "the published cut pair moved")
    packet = json.loads(gzip.decompress(CERTIFICATE.read_bytes()))
    events = expand(packet)
    require(len(events) == 26099, "event count moved")
    require(events[FAULT][1][1:] == [["L", 39], ["L", 359], 4, 1], "fault operands moved")
    helper, helper_changes = trace(events, REGISTER)
    data, data_changes = trace(events, 112)
    require(helper_changes == [(9545, "-1"), (9549, "0"), (24433, "1")], "the coefficient path moved")
    require(data_changes == [], "the data register reached register 359")
    return {
        "register": REGISTER,
        "fault_index": FAULT,
        "coefficient": str(helper[REGISTER]),
        "paired_target": str(helper[39]),
        "data_contribution": str(data[REGISTER]),
        "sign_flip": 9545,
        "zeroed": 9549,
        "restored": 24433,
        "literal_value": str(256 * helper[REGISTER] + data[REGISTER]),
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
