#!/usr/bin/env python3
"""The canonical word payload drops the gauge annihilator.

Two words that differ only in that private list decompress to the same bytes,
so the payload comparison accepts them. A changed public gauge dimension does
not. Container mtimes are not part of the comparison.
"""

import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
PRODUCER = ROOT / "research/paired-cube-bit-fast/paired_cube_bit_word.py"
NOTE = ROOT / "research/gzip-container-reproducibility/README.md"
MARKER = "PASS_CANONICAL_GAUGE_FIELD omitted=true no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_CANONICAL_GAUGE_FIELD " + message)


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
        "research/paired-cube-bit-fast/paired_cube_bit_word.py",
        "research/gzip-container-reproducibility/README.md",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def canonical_word(word):
    public = {key: value for key, value in word.items() if not str(key).startswith("_")}
    return (json.dumps(public, sort_keys=True, separators=(",", ":")) + "\n").encode()


def payload_equal(left, right):
    return gzip.decompress(left) == gzip.decompress(right)


def evaluate():
    authenticate()
    producer = PRODUCER.read_text(encoding="utf-8")
    note = NOTE.read_text(encoding="utf-8")
    require("if not k.startswith('_')" in producer, "the private-key filter moved")
    require("_gauge_ann=[z['ann'] for z in selected]" in producer, "the annihilator list moved")
    require("gzip.decompress(old), gzip.decompress(data)" in producer, "the payload comparison moved")
    require("compare the compressed content" in note, "the payload convention moved")
    shared = {"ops": [], "gauges": [{"role": 1, "first": 0, "targets": [0], "dim": 2}]}
    first = dict(shared, _gauge_ann=[3])
    second = dict(shared, _gauge_ann=[4])
    changed = dict(shared, _gauge_ann=[3])
    changed["gauges"] = [{"role": 1, "first": 0, "targets": [0], "dim": 3}]
    left = gzip.compress(canonical_word(first), mtime=0)
    right = gzip.compress(canonical_word(second), mtime=0)
    shifted = gzip.compress(canonical_word(first), mtime=1)
    public_change = gzip.compress(canonical_word(changed), mtime=0)
    require(payload_equal(left, right), "the annihilator change reached the payload")
    require(first["_gauge_ann"] != second["_gauge_ann"], "the annihilators agreed")
    require(hashlib.sha256(left).digest() != hashlib.sha256(shifted).digest(), "the mtime left the container")
    require(payload_equal(left, shifted), "the mtime reached the payload")
    require(payload_equal(left, public_change) is False, "a public dimension change was ignored")
    return {
        "payloads_equal": True,
        "annihilators_equal": False,
        "mtime_changes_container": True,
        "public_field_detected": True,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
