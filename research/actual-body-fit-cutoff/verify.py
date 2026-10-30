"""Authenticate sources and compare the full exact receipt. Nick Petalas. Apache-2.0."""

import hashlib
import json
import sys
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
from cutoff import certificate, need  # noqa: E402

INPUTS = (
    "research/bit2234-stock-threshold/README.md",
    "research/encoded-strict-borrowing/PR3503-PROOF.md",
    "research/encoded-strict-borrowing/PROOF.md",
    "research/ordinary-one-factor-stock/PROOF.md",
    "research/physical-ordinary-interchange/encoded.py",
    "research/selected-bit-recursive-caller/PROOF.md",
    "research/selected-bit-recursive-caller/node.py",
    "research/selected-body-depth-borrowing/PROOF.md",
    "research/selected-runtime-guard-stock/README.md",
)


def unique(pairs):
    need(len(pairs) <= 256, "JSON object capacity")
    result = {}
    for key, value in pairs:
        need(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def load(path):
    need(path.is_file() and not path.is_symlink(), "regular required JSON")
    need(path.stat().st_size <= 262144, "JSON byte capacity")
    return json.loads(path.read_bytes(), object_pairs_hook=unique)


def sources():
    manifest = load(PACKAGE / "SOURCES.json")
    rows = manifest["files"]
    need(type(rows) is list and len(rows) <= 16, "source inventory capacity")
    inputs = [row for row in rows if row["usage"] == "input"]
    need(tuple(sorted(row["path"] for row in inputs)) == INPUTS, "exact source closure")
    for row in inputs:
        path = PACKAGE.parent.parent / row["path"]
        need(path.is_file() and not path.is_symlink(), "regular proof input")
        need(path.stat().st_size <= 1048576, "proof input capacity")
        need(
            hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"],
            "source SHA256: " + row["path"],
        )


def main():
    sources()
    actual, expected = certificate(), load(PACKAGE / "RESULT.json")
    need(
        json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True),
        "complete typed RESULT receipt",
    )
    print("PASS_ACTUAL_BODY_FIT_CUTOFF cutoff=245767 boundary=245766 predicates=2")


if __name__ == "__main__":
    main()
