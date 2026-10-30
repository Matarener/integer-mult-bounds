#!/usr/bin/env python3
"""Record scalar changes of register 39 from event 24438 through the end.

Register 359 starts at 1. The trace applies the fault addition and every
later scalar event.
"""

import gzip
import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
CHECKER = ROOT / "research/qq16-native-dirty-fault/verify.py"
CERTIFICATE = ROOT / "research/joint-query/certificate.json.gz"
START = 24438
TARGET = 39
MARKER = "PASS_QQ16_LATER_ZERO value=0 no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_QQ16_LATER_ZERO " + message)


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
    writes = []
    for index, event in enumerate(events):
        if index == START:
            entered = state[TARGET]
        if event[0] != "scalar":
            continue
        gate = event[1]
        before = state[TARGET]
        writing = index >= START and gate[1] == ["L", TARGET]
        if writing:
            require(gate[0] == "add" and gate[2][0] == "L", "a non-add writes register 39")
            coefficient = Fraction(gate[3], gate[4])
            source_value = state[reg(gate[2])]
        apply(state, gate)
        if writing:
            writes.append({
                "index": index,
                "source": gate[2][1],
                "coefficient": str(coefficient),
                "source_value": str(source_value),
                "contribution": str(coefficient * source_value),
                "value": str(state[TARGET]),
            })
        if index >= START and state[TARGET] != before:
            changes.append([index, str(state[TARGET])])
    return state, entered, changes, writes


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
    require(events[START] == ["scalar", ["add", ["L", 39], ["L", 359], 4, 1], 1], "the fault event moved")
    suffix = Counter(event[0] for event in events[START:])
    require(dict(suffix) == {
        "scalar": 1412,
        "residual_adapter": 240,
        "native_line": 8,
        "phase": 1,
    }, "the suffix inventory moved")
    helper, entered, changes, writes = trace(events, 359)
    data, data_entered, data_changes, data_writes = trace(events, 112)
    require(entered == -4, "register 39 did not enter the fault at -4")
    require(changes == [[24438, "0"]], "the later value changes moved")
    require(helper[TARGET] == 0, "register 39 did not finish at 0")
    require(len(writes) == 6, "the additions into register 39 moved")
    require(all(row["contribution"] == "0" for row in writes[1:]), "a later addition contributed")
    require(data_entered == 0 and data_changes == [] and data[TARGET] == 0, "the data register reached register 39")
    require(all(row["contribution"] == "0" for row in data_writes), "the data register contributed to a later addition")
    return {
        "register": TARGET,
        "from_index": START,
        "through_index": len(events) - 1,
        "scalar_events": suffix["scalar"],
        "changes": changes,
        "writes": writes,
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
