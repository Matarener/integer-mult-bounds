"""Replay both full censuses and compare the source-bound receipt. Apache-2.0."""

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

import census
import controls
import oracle
from algebra import require


def build_report():
    primary = [census.census(n) for n in (3, 5)]
    independent = [oracle.census(n) for n in (3, 5)]
    for actual, second in zip(primary, independent, strict=True):
        comparable = json.loads(json.dumps(actual))
        for shape in comparable["shapes"].values():
            shape.pop("label_lists")
        require(comparable == second, "independent full census mismatch")
        require(all(row["accepted"] == 0 for row in actual["shapes"].values()),
                "three/five-call exclusion falsified")
    return {"schema_version": 1, "claim": "all-negative three-target Q8 cost is at least seven",
            "scope": "positive i/j; full F2[Q8]; binary rank-one idempotents; arbitrary finite restored dirt",
            "censuses": primary, "independent_full_census": True,
            "controls": controls.small_replay(), "source_sha256": census.source_hashes()}


def check_receipt(actual, expected):
    require(actual == expected, "source-bound receipt mismatch")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="create a new receipt, refusing overwrite")
    args = parser.parse_args()
    if args.output is not None:
        require(not args.output.exists(), "output already exists")
    actual = build_report()
    if args.output is None:
        expected = json.loads(Path(__file__).with_name("RESULT.json").read_bytes())
        check_receipt(actual, expected)
    else:
        with args.output.open("x") as stream:
            stream.write(json.dumps(actual, indent=2) + "\n")
    print("PASS_Q8_SHORT_NEGATIVE_GRAM " + json.dumps(actual["controls"], sort_keys=True))


if __name__ == "__main__":
    main()
