#!/usr/bin/env python3
"""Match the cover-routing sentence with a constant width factor.

The stage-2 routing room is a published integer. This check asks whether the
pinned cover text names a constant c_R for its width-O(w) routing calls. It
does not recompute cutoff margins.
"""

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
COVER = ROOT / "notes/three-stage-cover-bit.tex"
PR185 = ROOT / "research/community-round8-audit/pr185-proof-reviewed.md"
PR387 = ROOT / "research/bootstrap-depth-audit/sources/pr387/PROOF.md"
MARGIN = ROOT / "research/stock-margin-chain/README.md"
ROUTING_SENTENCE = "a constant number of old width-$O(w)$ interchanges"
PR185_ROUTING = "a fixed number of ordinary width-`O(w)` calls"
HIGH_PART = "The parent high-part exchange has width `k=O(w log e)`"
PR387_MULTIPLIER = "does not need an external row multiplier"
ROOM_ROW = "| native | 2 | 2851485324488315 | 4777557234646 | published control |"
MARKER = "PASS_STOCK_ROUTING_FACTOR named_factor=false room=uninstantiated no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_STOCK_ROUTING_FACTOR " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def paragraph_containing(text, sentence):
    require(sentence in text, "routing sentence moved")
    chunks = text.split("\n\n")
    matches = [chunk for chunk in chunks if sentence in chunk]
    require(len(matches) == 1, "routing sentence is not in one paragraph")
    return matches[0]


def names_constant_factor(text):
    if re.search(r"c_R\s*=", text):
        return True
    if re.search(r"width at most \d+", text, re.IGNORECASE):
        return True
    if re.search(r"\d+\s*\*\s*w", text):
        return True
    return False


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "notes/three-stage-cover-bit.tex",
        "research/community-round8-audit/pr185-proof-reviewed.md",
        "research/bootstrap-depth-audit/sources/pr387/PROOF.md",
        "research/stock-margin-chain/README.md",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def evaluate():
    authenticate()
    cover = COVER.read_text(encoding="utf-8")
    pr185 = PR185.read_text(encoding="utf-8")
    pr387 = PR387.read_text(encoding="utf-8")
    margin = MARGIN.read_text(encoding="utf-8")
    paragraph = paragraph_containing(cover, ROUTING_SENTENCE)
    require(PR185_ROUTING in pr185, "PR185 routing sentence moved")
    require(HIGH_PART in pr185, "PR185 high-part sentence moved")
    require(PR387_MULTIPLIER in pr387, "PR387 row-multiplier sentence moved")
    require("252 allowance is unused slack" in pr387, "PR387 slack sentence moved")
    require(ROOM_ROW in margin, "published stage-2 routing room moved")
    require(names_constant_factor(paragraph) is False, "the routing paragraph names a constant")
    require("O(w)" in PR185_ROUTING and "O(w log e)" in HIGH_PART, "width phrases moved")
    return {
        "routing_phrase": "a constant number of old width-O(w) interchanges",
        "named_factor": False,
        "high_part_phrase": "k=O(w log e)",
        "native_stage2_routing_room": "4777557234646",
        "room_comparison": "uninstantiated",
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
