#!/usr/bin/env python3
"""Three revised intake rows retain their original starting heads.

The checker reads the pinned receipts. It does not rewrite the ledger.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_INTAKE_INITIAL_HEADS records=3 heads_differ=true no_new_kappa"
REVISIONS = {
    3107: ("queue-next-20261017", "initial_archived_head", "queue-next-20261017"),
    3184: ("queue-tail-20261017", "previously_reviewed_head", "queue-tail-20261017"),
    3251: ("queue-refresh-20261017", "head", "queue-oct18-20261018"),
}


def fail(message):
    raise SystemExit("FAIL_INTAKE_INITIAL_HEADS " + message)


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
        "certificates/selected-result.json",
        "docs/research/pr-ledger.json",
        "docs/research/pr-intake-decisions.json",
        "docs/research/pr-intake-evidence/queue-next-20261017.json",
        "docs/research/pr-intake-evidence/queue-tail-20261017.json",
        "docs/research/pr-intake-evidence/queue-refresh-20261017.json",
        "docs/research/pr-intake-evidence/queue-oct18-20261018.json",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def one_row(rows, number):
    matches = [row for row in rows if row["number"] == number]
    require(len(matches) == 1, "ambiguous receipt " + str(number))
    return matches[0]


def evaluate():
    authenticate()
    selected = json.loads((ROOT / "certificates/selected-result.json").read_text(encoding="utf-8"))
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    ledger = json.loads((ROOT / "docs/research/pr-ledger.json").read_text(encoding="utf-8"))
    intake = json.loads((ROOT / "docs/research/pr-intake-decisions.json").read_text(encoding="utf-8"))
    ledger_rows = {row["number"]: row for row in ledger["pull_requests"]}
    intake_rows = {row["number"]: row for row in intake["pull_requests"]}
    receipts = {}
    for number, (original_name, _field, current_name) in REVISIONS.items():
        for name in (original_name, current_name):
            if name not in receipts:
                path = ROOT / "docs/research/pr-intake-evidence" / (name + ".json")
                receipts[name] = json.loads(path.read_text(encoding="utf-8"))["contributions"]
        original = one_row(receipts[original_name], number)
        current = one_row(receipts[current_name], number)
        starting = original[REVISIONS[number][1]]
        later = current["head"]
        require(starting != later, "the heads agree " + str(number))
        recorded = ledger_rows[number]
        decision = intake_rows[number]
        require(recorded["starting_head"] == starting, "the starting head moved " + str(number))
        require(recorded["current_head"] == recorded["reviewed_head"] == later, "the later head moved " + str(number))
        metadata = decision["metadata"]
        require(metadata["number"] == number, "the metadata number moved " + str(number))
        require(metadata["headRefOid"] == decision["current_head"] == decision["reviewed_head"] == later,
                "the metadata head moved " + str(number))
        require(metadata["author"] == original["author"] == current["author"], "attribution moved " + str(number))
    return {"records": 3, "heads_differ": True, "attribution_intact": True, "no_new_kappa": True}


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
