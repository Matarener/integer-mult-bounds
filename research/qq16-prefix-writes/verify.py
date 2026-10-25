#!/usr/bin/env python3
"""Count prefix events whose destination is register 359.

The scan stops at event 24438. It records destinations and does not evaluate
the amplitude those writes produce.
"""

import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
CHECKER = ROOT / "research/qq16-native-dirty-fault/verify.py"
CERTIFICATE = ROOT / "research/joint-query/certificate.json.gz"
FAULT = 24438
REGISTER = 359
MARKER = "PASS_QQ16_PREFIX_WRITES writes=32 no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_QQ16_PREFIX_WRITES " + message)


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


def destination(event):
    """Published destination field. A climb's old frame is not a register."""
    kind = event[0]
    if kind == "scalar":
        return reg(event[1][1]), event[1][0]
    if kind == "climb":
        return event[2], "climb"
    if kind == "adapter":
        return event[2], "adapter"
    if kind == "residual_adapter":
        return event[2], "residual"
    if kind == "native_line":
        return reg(event[1]), "native_line"
    require(kind == "phase", "unknown event")
    return None, "phase"


def expand(packet):
    result = []
    for event in packet["programs"]["F_0"]:
        if event[0] == "retained_core":
            require(event[1:3] == ["forward", 0], "stage-zero forward core")
            result.extend(packet["core_words"]["forward"])
        elif event[0] in ("cover_sweep", "private_sweep"):
            result.extend(event[2])
        else:
            result.append(event)
    return result


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
    require("kind, dst = gate[0], reg(gate[1])" in checker, "the scalar destination moved")
    require("_, _, dst, old, new, _ = event" in checker, "the climb destination moved")
    require("_, direction, dst, _ = event" in checker, "the adapter destination moved")
    require('["scalar", ["add", ["L", 39], ["L", 359], 4, 1], 1]' in checker, "the fault event moved")
    packet = json.loads(gzip.decompress(CERTIFICATE.read_bytes()))
    require(packet["schema"] == "conserved-qq16-full-cover-native-words-v1", "packet schema")
    events = expand(packet)
    require(len(events) == 26099, "event count moved")
    require(events[FAULT] == ["scalar", ["add", ["L", 39], ["L", 359], 4, 1], 1], "fault binding moved")
    require(destination(events[FAULT])[0] == 39, "the fault writes a different register")
    writes = []
    for index, event in enumerate(events[:FAULT]):
        register, kind = destination(event)
        if register == REGISTER:
            writes.append((index, kind, event))
    kinds = {"add": 0, "scale": 0, "adapter": 0, "climb": 0}
    for _, kind, _ in writes:
        require(kind in kinds, "unexpected write kind")
        kinds[kind] += 1
    first_index, _, first_event = writes[0]
    last_index, _, last_event = writes[-1]
    return {
        "register": REGISTER,
        "fault_index": FAULT,
        "writes_before_fault": len(writes),
        "kinds": kinds,
        "first_index": first_index,
        "first_event": first_event,
        "last_index": last_index,
        "last_event": last_event,
        "cut_still_initial": False,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
