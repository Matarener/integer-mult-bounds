#!/usr/bin/env python3
"""Read whether the tail word names an owner for the flag-0 source read.

Event 5759 adds X0 into Y34. The tail package's own result, task and readme
say that no global owner or host is assigned.
"""

import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
TAIL = ROOT / "research/p104-tail-side-correction-seed749717"
MARKER = "PASS_P104_TAIL_FLAG0_OWNER event=5759 owner=unbound no_new_kappa"
FULL = [1, 2, 4, 8, 16, 32, 64, 128, 256]
OBLIGATION = (
    "Prove a globally legal owner/host schedule for the appended source reads "
    "and rank-one transports, charge its copied information, and reassess complete supplier cost."
)
BLOCK = "No global owner/host assignment for the current 104-by-104 source reads has been established."
README_SENTENCE = "It does not assign global owners or hosts"


def fail(message):
    raise SystemExit("FAIL_P104_TAIL_FLAG0_OWNER " + message)


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
    expected = {
        "research/p104-tail-side-correction-seed749717/AUGMENTED-WITNESS.json.gz",
        "research/p104-tail-side-correction-seed749717/README.md",
        "research/p104-tail-side-correction-seed749717/RESULT.json",
        "research/p104-tail-side-correction-seed749717/TASK.json",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def evaluate():
    authenticate()
    tail = json.loads(gzip.decompress((TAIL / "AUGMENTED-WITNESS.json.gz").read_bytes()))
    event = tail["program"][5759]
    require(event == ["add", "Y34", "X0", "-1/2", FULL], "event 5759 changed")
    require(len(event) == 5, "the add gained a field")
    require(sorted(tail) == ["final_frames", "initial_frames", "program"], "the witness gained a section")
    result = json.loads((TAIL / "RESULT.json").read_text(encoding="utf-8"))
    task = json.loads((TAIL / "TASK.json").read_text(encoding="utf-8"))
    readme = (TAIL / "README.md").read_text(encoding="utf-8")
    require(result["remaining_obligation"] == OBLIGATION, "the remaining obligation moved")
    require("does not supply global chronological helper hosting" in result["scope"], "the scope began to supply hosting")
    require(task["open_questions"][0]["blocked_by"] == BLOCK, "the owner blocker moved")
    require(README_SENTENCE in readme, "the readme began to assign owners")
    return {
        "event": 5759,
        "add": ["Y34", "X0", "-1/2"],
        "fields": 5,
        "owner_field": False,
        "owner_assigned": False,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
