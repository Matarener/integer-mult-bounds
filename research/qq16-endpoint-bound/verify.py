#!/usr/bin/env python3
"""Read the stored QQ16 endpoint row sums.

The certificate records one absolute row sum per output coordinate. Its scope
says these are endpoint bounds and that no physical producer is implemented.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
DEFECT = ROOT / "research/qq16-producer-defect-transfer"
MARKER = "PASS_QQ16_ENDPOINT_BOUND F0=49 D=1923 no_producer no_new_kappa"
INTERIOR = "all-cut magnitude bounds or bounds on faults inside producer instructions."


def fail(message):
    raise SystemExit("FAIL_QQ16_ENDPOINT_BOUND " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def maximum(rows):
    return max(Fraction(row["l1"]) for row in rows)


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "research/qq16-producer-defect-transfer/README.md",
        "research/qq16-producer-defect-transfer/RESULT.json",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def evaluate():
    authenticate()
    readme = (DEFECT / "README.md").read_text(encoding="utf-8")
    result = json.loads((DEFECT / "RESULT.json").read_text(encoding="utf-8"))
    require("It does not implement the producer or admit a supplier." in readme, "the producer exclusion moved")
    require(INTERIOR in readme, "the interior exclusion moved")
    require(result["scope"] == "Conditional endpoint bounds; no physical producer implementation.", "the result scope moved")
    require(isinstance(result["events"], int), "the event count became a program")
    require("dirty" not in result, "a dirty-helper field appeared")
    f0 = maximum(result["operators"]["F0"])
    decoder = maximum(result["operators"]["D"])
    require(len(result["operators"]["F0"]) == len(result["operators"]["D"]) == 224, "the row count changed")
    require(f0 == 49 and decoder == 1923, "the stored maxima moved")
    require(result["controls"]["F0_sharp_witness"] == "49", "the sharp witness moved")
    return {
        "rows": 224,
        "F0_max_l1": "49",
        "D_max_l1": "1923",
        "sharp_witness": "49",
        "physical_producer": False,
        "dirty_helper_field": False,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
