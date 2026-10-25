"""Read-only source-bound acceptance, including under optimized Python."""

import json
import sys
from hashlib import sha256
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from arithmetic import certificate, need

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
INPUTS = (
    "research/community-frontier1094-audit/ASSEMBLY.json",
    "research/selected-bit-recursive-caller/PROOF.md",
    "research/selected-bit-recursive-caller/node.py",
    "research/selected-lcm-stock-wrapper-fit/README.md",
    "research/selected-runtime-guard-stock/README.md",
)


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def read_json(path):
    need(path.is_file() and not path.is_symlink(), "regular JSON source required")
    need(path.stat().st_size <= 1048576, "JSON size capacity")
    return json.loads(path.read_text(), object_pairs_hook=unique_pairs)


def authenticate():
    source = read_json(PACKAGE / "SOURCES.json")
    rows = source["files"]
    need(type(rows) is list and len(rows) <= 16, "bounded source inventory")
    live = [row for row in rows if row["usage"] == "input"]
    need(sorted(row["path"] for row in live) == list(INPUTS), "complete live source inventory")
    for row in live:
        path = ROOT / row["path"]
        need(path.is_file() and not path.is_symlink(), "missing or aliased input")
        need(path.stat().st_size <= 1048576, "input size capacity")
        need(sha256(path.read_bytes()).hexdigest() == row["sha256"], "input hash mismatch")
    assembly = read_json(ROOT / INPUTS[0])
    need(assembly["bit_supplier"]["pr"] == 589, "selected BIT provenance")
    need(assembly["kappa"] == "836330098538459/500000000000000000", "selected record")
    return len(live)


def main():
    sources = authenticate()
    expected = read_json(PACKAGE / "RESULT.json")
    need(type(expected.get("coefficient")) is int, "typed coefficient receipt")
    actual = certificate()
    need(
        json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True),
        "complete typed certificate mismatch",
    )
    print(
        f"PASS_SELECTED_STOCK_SHARP_INTEGER coefficient=6741 sources={sources} "
        "witness_depth=262144 failure_margin=12644 no_new_kappa"
    )


if __name__ == "__main__":
    main()
