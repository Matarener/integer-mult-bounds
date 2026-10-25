#!/usr/bin/env python3
"""Match the flag-0 tail transports to the compiled side-transport records.

Event 5758 and event 5807 are compared with the compressed columns. The
Clifford recipe is not executed.
"""

import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
TAIL = ROOT / "research/p104-tail-side-correction-seed749717"
MARKER = "PASS_P104_TAIL_FLAG0_TRANSPORT target=34 promote=5758 restore=5807 no_new_kappa"
FULL = [1, 2, 4, 8, 16, 32, 64, 128, 256]
RANK8 = [499, 23, 232, 32, 112, 15, 7, 2]


def fail(message):
    raise SystemExit("FAIL_P104_TAIL_FLAG0_TRANSPORT " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def matches(record, direction, old, new):
    return (
        record["direction"] == direction
        and record["old_compressed"] == old
        and record["new_compressed"] == new
        and record["rank"] == 1
        and record["recipe"]["rank"] == 1
    )


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "research/p104-tail-side-correction-seed749717/AUGMENTED-WITNESS.json.gz",
        "research/p104-tail-side-correction-seed749717/SIDE-TRANSPORTS.json.gz",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def evaluate():
    authenticate()
    tail = json.loads(gzip.decompress((TAIL / "AUGMENTED-WITNESS.json.gz").read_bytes()))
    compiled = json.loads(gzip.decompress((TAIL / "SIDE-TRANSPORTS.json.gz").read_bytes()))
    records = compiled["transports"]
    require(compiled["rank_one_transport_count"] == len(records) == 208, "the transport count changed")
    require(tail["program"][5758] == ["transport", "Y34", RANK8, FULL, 1], "event 5758 changed")
    require(tail["program"][5807] == ["transport", "Y34", FULL, RANK8, 1], "event 5807 changed")
    promote = [row for row in records if matches(row, "promote", RANK8, FULL)]
    restore = [row for row in records if matches(row, "restore", FULL, RANK8)]
    require(len(promote) == 1 and promote[0]["target"] == 34, "the promotion is not target 34")
    require(len(restore) == 1 and restore[0]["target"] == 34, "the restoration is not target 34")
    require(promote[0]["old_physical"] != RANK8, "the physical column repeated the witness list")
    return {
        "records": 208,
        "promote": {"event": 5758, "target": 34, "rank": 1, "old_compressed": RANK8, "new_compressed": FULL},
        "restore": {"event": 5807, "target": 34, "rank": 1, "old_compressed": FULL, "new_compressed": RANK8},
        "recipe_replayed": False,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
