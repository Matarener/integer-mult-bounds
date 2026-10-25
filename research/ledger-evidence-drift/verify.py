#!/usr/bin/env python3
"""539 markdown ledger rows omit the intake-decisions path.

The checker reads the committed ledgers. It does not rewrite them.
"""

import hashlib
import json
import re
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_LEDGER_EVIDENCE_DRIFT rows=539 attribution_intact=true no_new_kappa"
INTAKE = "docs/research/pr-intake-decisions.json"
LABELS = {
    "incorporated": "incorporated",
    "partially_reviewed": "partially reviewed",
    "superseded": "superseded",
    "unreviewed": "unreviewed",
}


def fail(message):
    raise SystemExit("FAIL_LEDGER_EVIDENCE_DRIFT " + message)


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
        "docs/research/pr-ledger.md",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def markdown_rows(text):
    rows = {}
    for line in text.splitlines():
        if not line.startswith("| [#"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        require(len(cells) == 4, "a ledger row changed shape")
        match = re.search(r"\[#(\d+)\]", cells[0])
        require(match is not None, "a ledger row lost its number")
        rows[int(match.group(1))] = {
            "contributor": cells[1],
            "disposition": cells[2],
            "evidence": cells[3],
        }
    return rows


def markdown_counts(text):
    counts = {}
    for line in text.splitlines():
        match = re.fullmatch(r"\| (incorporated|partially reviewed|superseded|unreviewed) \| (\d+) \|", line)
        if match:
            counts[match.group(1)] = int(match.group(2))
    return counts


def evaluate():
    authenticate()
    selected = json.loads((ROOT / "certificates/selected-result.json").read_text(encoding="utf-8"))
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    ledger = json.loads((ROOT / "docs/research/pr-ledger.json").read_text(encoding="utf-8"))
    text = (ROOT / "docs/research/pr-ledger.md").read_text(encoding="utf-8")
    rows = markdown_rows(text)
    pulls = ledger["pull_requests"]
    require(len(rows) == len(pulls) == 3028, "the row count moved")
    shown = markdown_counts(text)
    require(shown == {LABELS[key]: value for key, value in ledger["counts"].items()}, "the disposition table moved")
    require(sum(shown.values()) == 3028, "the disposition table does not add up")
    stale = []
    for pull in pulls:
        number = pull["number"]
        require(number in rows, "a JSON pull is missing from Markdown")
        row = rows[number]
        require(row["contributor"] == pull["contributor"]["login"], "a contributor moved")
        require(row["disposition"] == LABELS[pull["disposition"]], "a disposition moved")
        evidence = pull.get("reconciliation_evidence") or []
        json_has = INTAKE in evidence
        markdown_has = INTAKE in row["evidence"]
        if json_has and not markdown_has:
            stale.append(number)
    require(len(stale) == 539 and min(stale) == 1365 and max(stale) == 3528, "the stale range moved")
    return {
        "rows": 3028,
        "stale_rows": 539,
        "attribution_intact": True,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
