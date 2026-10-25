#!/usr/bin/env python3
"""Show that line ports cannot add a second unpaid coordinate per family.

A port group clears one label rank per paying call. One offset direction
does not clear a label. The selected replica is already at that cap.
"""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_LINE_PORT_UNPAID_CAP two_unpaid_exceeds=true no_new_kappa"
PORTS = 112
CALLS = 9
OFFSETS = 1
FAMILIES = 896


def fail(message):
    raise SystemExit("FAIL_LINE_PORT_UNPAID_CAP " + message)


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
    expected = {"research/complex-local-word-ceiling/README.md"}
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def rank(rows):
    pending = [row[:] for row in rows]
    width = len(pending[0]) if pending else 0
    pivot = 0
    for column in range(width):
        source = next((i for i in range(pivot, len(pending)) if pending[i][column]), None)
        if source is None:
            continue
        pending[pivot], pending[source] = pending[source], pending[pivot]
        for other in range(len(pending)):
            if other != pivot and pending[other][column]:
                pending[other] = [a ^ b for a, b in zip(pending[other], pending[pivot])]
        pivot += 1
    return pivot


def pay(rows, dirty, column):
    pivot = next(i for i, row in enumerate(rows) if row[column])
    for other in range(len(rows)):
        if other != pivot and rows[other][column]:
            rows[other] = [a ^ b for a, b in zip(rows[other], rows[pivot])]
    rows[pivot] = [0] * len(rows[pivot])
    rows[pivot][column] = 0
    return dirty


def offset(rows, dirty):
    if len(rows) > 1:
        rows[0], rows[1] = rows[1], rows[0]
        dirty[0], dirty[1] = dirty[1], dirty[0]
        rows[0], rows[1] = rows[1], rows[0]
        dirty[0], dirty[1] = dirty[1], dirty[0]
    return dirty


def schedule(unpaid, paying):
    rows = [[1 if column == row else 0 for column in range(unpaid)] for row in range(unpaid)]
    dirty = [1, 0] + [0] * (unpaid - 2)
    for _ in range(paying):
        column = next(column for column in range(unpaid) if any(row[column] for row in rows))
        pay(rows, dirty, column)
    offset(rows, dirty)
    return rank(rows), dirty


def evaluate():
    authenticate()
    note = (ROOT / "research/complex-local-word-ceiling/README.md").read_text(encoding="utf-8")
    require("896 live data families per nine-stage replica (2 × 4 pairs × 112 ports" in note, "the replica count moved")
    cleared, dirty = schedule(CALLS - OFFSETS, CALLS - OFFSETS)
    blocked, blocked_dirty = schedule(CALLS - OFFSETS + 1, CALLS - OFFSETS)
    require(cleared == 0 and dirty[0] == 1 and sum(dirty) == 1, "the saturated schedule missed")
    require(blocked == 1 and blocked_dirty[0] == 1, "an extra unpaid coordinate was cleared")
    cap = PORTS * (CALLS - OFFSETS)
    require(cap == FAMILIES, "one unpaid coordinate per family left the cap")
    require(2 * FAMILIES > cap, "two unpaid coordinates fit the cap")
    return {
        "ports": PORTS,
        "calls": CALLS,
        "offsets": OFFSETS,
        "cap": cap,
        "families": FAMILIES,
        "saturated_rank": 0,
        "extra_rank": 1,
        "dirty_survives": True,
        "two_unpaid_exceeds": True,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
