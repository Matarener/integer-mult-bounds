#!/usr/bin/env python3
"""Read the intake packet for the tail pull request.

Packet 2089 lists the tail files and says owner scheduling remains unproved.
It does not mention event 5759.
"""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
PACKET = ROOT / "research/community-efficient1100-audit/packets/2089.json"
MARKER = "PASS_P104_TAIL_FLAG0_INTAKE packet=2089 owner=unproved no_new_kappa"
SENTENCE = (
    "Global owner/host scheduling and copied-information delivery for the "
    "source reads remain unproved"
)
TAIL_FILES = {
    "research/p104-tail-side-correction-seed749717/AUGMENTED-WITNESS.json.gz",
    "research/p104-tail-side-correction-seed749717/CORRECTION-ROWS.json",
    "research/p104-tail-side-correction-seed749717/README.md",
    "research/p104-tail-side-correction-seed749717/RESULT.json",
    "research/p104-tail-side-correction-seed749717/SIDE-TRANSPORTS.json.gz",
    "research/p104-tail-side-correction-seed749717/SOURCES.json",
    "research/p104-tail-side-correction-seed749717/TASK.json",
    "research/p104-tail-side-correction-seed749717/VERIFY.json",
    "research/p104-tail-side-correction-seed749717/verify.py",
}


def fail(message):
    raise SystemExit("FAIL_P104_TAIL_FLAG0_INTAKE " + message)


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
    expected = {"research/community-efficient1100-audit/packets/2089.json"}
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def evaluate():
    authenticate()
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    require(packet["number"] == 2089, "the packet left pull request 2089")
    require(packet["decision"] is None, "the packet gained a decision")
    files = {row["path"] for row in packet["files"]}
    require(files == TAIL_FILES, "the archived file list changed")
    body = packet["body"]
    require(SENTENCE in body, "the owner sentence moved")
    require("5759" not in body and "5759" not in json.dumps(packet["files"]), "the packet cited event 5759")
    return {
        "packet": 2089,
        "decision": None,
        "archived_files": len(TAIL_FILES),
        "cites_event_5759": False,
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
