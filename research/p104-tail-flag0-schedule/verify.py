#!/usr/bin/env python3
"""Ask whether the schedule named by the tail word cites event 5759.

Pull request 1940 is the chronological schedule in the tail readme. Its
merged package is research/p104-target-order-delivery. None of those files
name the tail event, and the schedule leaves side corrections unresolved.
"""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
TAIL = ROOT / "research/p104-tail-side-correction-seed749717"
SCHEDULE = ROOT / "research/p104-target-order-delivery"
PACKET = ROOT / "research/community-efficient900-audit/packets/1940.json"
MARKER = "PASS_P104_TAIL_FLAG0_SCHEDULE pr=1940 cites_5759=false no_new_kappa"
SCHEDULE_FILES = (
    "README.md",
    "RESULT.json",
    "SCHEDULE.json",
    "SELECTION.json",
    "SOURCES.json",
    "TASK.json",
    "VERIFY.json",
    "verify.py",
)


def fail(message):
    raise SystemExit("FAIL_P104_TAIL_FLAG0_SCHEDULE " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def cites_tail(text):
    return "5759" in text or "749717" in text


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "research/p104-tail-side-correction-seed749717/README.md",
        "research/community-efficient900-audit/packets/1940.json",
        *{f"research/p104-target-order-delivery/{name}" for name in SCHEDULE_FILES},
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def evaluate():
    authenticate()
    tail = (TAIL / "README.md").read_text(encoding="utf-8")
    require("https://github.com/CrocSwap/integer-mult-bounds/pull/1940" in tail, "the tail stopped naming pull request 1940")
    require("does not integrate with that schedule" in tail, "the tail began to integrate the schedule")
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    require(packet["number"] == 1940, "the packet left pull request 1940")
    files = {row["path"]: row["source"]["oid"] for row in packet["files"]}
    require(set(files) == {f"research/p104-target-order-delivery/{name}" for name in SCHEDULE_FILES}, "the merged file list changed")
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    blobs = {row["path"]: row["git_blob"] for row in sources["files"]}
    for path, oid in files.items():
        require(blobs[path] == oid, "a merged blob left the pinned file " + path)
    readme = (SCHEDULE / "README.md").read_text(encoding="utf-8")
    require("C_side_corrections + C_hosting_and_precision." in readme, "the cost formula moved")
    require("remain unresolved" in readme, "the schedule began to resolve side corrections")
    cited = [name for name in SCHEDULE_FILES if cites_tail((SCHEDULE / name).read_text(encoding="utf-8"))]
    require(cited == [], "the schedule cited the tail event")
    return {
        "schedule_pr": 1940,
        "schedule_package": "research/p104-target-order-delivery",
        "schedule_files": len(SCHEDULE_FILES),
        "cites_event_5759": False,
        "cites_tail_seed": False,
        "side_corrections_resolved": False,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
