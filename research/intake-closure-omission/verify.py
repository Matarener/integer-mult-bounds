#!/usr/bin/env python3
"""Omitted intake closures split into inherited nulls, one recorded null, and absences.

The checker walks the published family order. It does not rewrite the ledger.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_INTAKE_CLOSURE_OMISSION omitted=24 inherited_null=4 no_new_kappa"
OPTIONAL = ("closure", "review_completion", "verification_evidence")
FAMILIES = (
    "research/community-family533-audit/DISPOSITIONS.json",
    "research/community-family588-audit/DISPOSITIONS.json",
    "research/community-hyperplane599-audit/DISPOSITIONS.json",
    "research/community-cold617-audit/DISPOSITIONS.json",
    "research/community-k492-audit/DISPOSITIONS.json",
    "research/community-frontier741-audit/DISPOSITIONS.json",
    "research/community-frontier799-audit/DISPOSITIONS.json",
    "research/community-frontier890-audit/DISPOSITIONS.json",
    "research/community-batch932-audit/DISPOSITIONS.json",
    "research/community-batch952-audit/DISPOSITIONS.json",
    "research/community-batch970-audit/DISPOSITIONS.json",
    "research/community-batch1047-audit/DISPOSITIONS.json",
    "research/community-batch1099-audit/DISPOSITIONS.json",
    "research/pr-reconciliation100-20261013/DISPOSITIONS.json",
    "research/community-historical-five-audit/DISPOSITIONS.json",
    "research/community-reconciliation92-audit/DISPOSITIONS.json",
    "research/community-reconciliation-next100-audit/DISPOSITIONS.json",
    "research/community-reconciliation-third100-audit/DISPOSITIONS.json",
    "research/community-reconciliation-fourth100-audit/DISPOSITIONS.json",
    "research/community-pilot20-audit/DISPOSITIONS.json",
    "research/community-efficient100-audit/DISPOSITIONS.json",
    "research/community-efficient200-audit/DISPOSITIONS.json",
    "research/community-efficient300-audit/DISPOSITIONS.json",
    "research/community-efficient400-audit/DISPOSITIONS.json",
    "research/community-efficient500-audit/DISPOSITIONS.json",
    "research/community-efficient600-audit/DISPOSITIONS.json",
    "research/community-efficient700-audit/DISPOSITIONS.json",
    "research/community-efficient800-audit/DISPOSITIONS.json",
    "research/community-efficient900-audit/DISPOSITIONS.json",
    "research/community-efficient1000-audit/DISPOSITIONS.json",
    "research/community-efficient1100-audit/DISPOSITIONS.json",
    "research/community-efficient1200-audit/DISPOSITIONS.json",
    "research/community-efficient1300-audit/DISPOSITIONS.json",
    "research/community-efficient1400-audit/DISPOSITIONS.json",
    "research/community-efficient1500-audit/DISPOSITIONS.json",
    "research/community-efficient1600-audit/DISPOSITIONS.json",
    "research/community-efficient1700-audit/DISPOSITIONS.json",
    "research/community-efficient1800-audit/DISPOSITIONS.json",
    "research/community-efficient1900-audit/DISPOSITIONS.json",
    "research/community-efficient2000-audit/DISPOSITIONS.json",
    "research/community-efficient2100-audit/DISPOSITIONS.json",
    "research/community-efficient2200-audit/DISPOSITIONS.json",
    "research/community-efficient2300-audit/DISPOSITIONS.json",
    "research/community-efficient2400-audit/DISPOSITIONS.json",
    "research/community-efficient2500-audit/DISPOSITIONS.json",
    "research/community-efficient2600-audit/DISPOSITIONS.json",
    "docs/research/pr-intake-decisions.json",
)


def fail(message):
    raise SystemExit("FAIL_INTAKE_CLOSURE_OMISSION " + message)


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
    pinned = [row for row in sources["files"] if row["usage"] == "input"]
    expected = ["certificates/selected-result.json", "docs/research/pr-ledger.json", *FAMILIES]
    require([row["path"] for row in pinned] == expected, "input inventory changed")
    for row in pinned:
        require(sha256(ROOT / row["path"]) == row["sha256"], "input drift " + row["path"])


def project(previous, decision):
    projected = dict(decision)
    for field in OPTIONAL:
        if field not in projected and field in previous:
            projected[field] = previous[field]
    return projected


def evaluate():
    authenticate()
    selected = json.loads((ROOT / "certificates/selected-result.json").read_text(encoding="utf-8"))
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    ledger = json.loads((ROOT / "docs/research/pr-ledger.json").read_text(encoding="utf-8"))
    by_number = {row["number"]: row for row in ledger["pull_requests"]}
    projections = {}
    inherited_null = []
    recorded_null = []
    field_absent = []
    intake_rows = 0
    for path in FAMILIES:
        family = json.loads((ROOT / path).read_text(encoding="utf-8"))
        numbers = [row["number"] for row in family["pull_requests"]]
        require(len(numbers) == len(set(numbers)), "duplicate family row " + path)
        intake = path == FAMILIES[-1]
        for row in family["pull_requests"]:
            previous = projections.get(row["number"], {})
            if intake:
                intake_rows += 1
                require("review_completion" in row and "verification_evidence" in row, "an intake companion field is absent")
                if "closure" not in row:
                    item = by_number[row["number"]]
                    if "closure" in previous and previous["closure"] is None:
                        require("closure" in item and item["closure"] is None, "an inherited null left the ledger")
                        inherited_null.append(row["number"])
                    elif "closure" not in previous and "closure" in item and item["closure"] is None:
                        recorded_null.append(row["number"])
                    elif "closure" not in previous and "closure" not in item:
                        field_absent.append(row["number"])
                    else:
                        fail("an omitted closure left the partition")
            projections[row["number"]] = project(previous, row)
    return {
        "intake_rows": intake_rows,
        "omitted": len(inherited_null) + len(recorded_null) + len(field_absent),
        "inherited_null": inherited_null,
        "recorded_null": recorded_null,
        "field_absent": field_absent,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
