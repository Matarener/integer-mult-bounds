#!/usr/bin/env python3
"""Record the sum event 24438 writes into register 39.

Register 359 starts at 1. The trace stops before event 24438 and computes
the sum from the values present at that event.
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
TARGET = 39
SOURCE = 359
MARKER = "PASS_QQ16_FAULT_SUM sum=0 no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_QQ16_FAULT_SUM " + message)


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
    last = {}
    for index, event in enumerate(events[:FAULT]):
        if event[0] != "scalar":
            continue
        before = {TARGET: state[TARGET], SOURCE: state[SOURCE]}
        apply(state, event[1])
        for register, old in before.items():
            if state[register] != old:
                last[register] = index
    return state, last


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
    require('if event[0] == "scalar":' in checker, "the scalar guard moved")
    require('["scalar", ["add", ["L", 39], ["L", 359], 4, 1], 1]' in checker, "the fault binding moved")
    packet = json.loads(gzip.decompress(CERTIFICATE.read_bytes()))
    events = expand(packet)
    require(len(events) == 26099, "the expanded word changed length")
    require(events[FAULT] == ["scalar", ["add", ["L", 39], ["L", 359], 4, 1], 1], "the fault event moved")
    gate = events[FAULT][1]
    coefficient = Fraction(gate[3], gate[4])
    helper, last = trace(events, 359)
    data, _ = trace(events, 112)
    contribution = coefficient * helper[SOURCE]
    total = helper[TARGET] + contribution
    require(helper[SOURCE] == 1, "register 359 had left 1")
    require(helper[TARGET] == -4, "register 39 had left -4")
    require(last[SOURCE] == 24433 and last[TARGET] == 24284, "the operands were rewritten")
    require(contribution == 4 and total == 0, "the sum left 0")
    require(data[SOURCE] == 0 and data[TARGET] == 0, "the data register reached an operand")
    return {
        "event": FAULT,
        "target": TARGET,
        "target_before": str(helper[TARGET]),
        "target_last_write": last[TARGET],
        "source": SOURCE,
        "source_before": str(helper[SOURCE]),
        "source_last_write": last[SOURCE],
        "coefficient": str(coefficient),
        "contribution": str(contribution),
        "sum": str(total),
        "data_target": str(data[TARGET]),
        "data_source": str(data[SOURCE]),
        "literal_target": str(256 * helper[TARGET]),
        "literal_source": str(256 * helper[SOURCE]),
        "literal_sum": str(256 * total),
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
