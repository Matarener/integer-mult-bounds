"""Replay exact arithmetic and the opt-in literal padding adapter."""

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import runtime
import science
import tape_checks
from minimum import require


def result():
    runtime.authenticate()
    arithmetic = science.census()
    witness = science.selected_witness()
    volume_cases = science.check_padding_equivalence()
    with runtime.installed() as retained:
        encoded = tape_checks.plans(retained)
        endpoints = tape_checks.endpoints(retained)
    return {
        "schema_version": 1,
        "arithmetic": arithmetic,
        "selected": witness,
        "volume_cases": volume_cases,
        "encoded_plans": encoded,
        "endpoints": endpoints,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true", help="print recomputed receipt")
    args = parser.parse_args()
    observed = result()
    encoded = json.dumps(observed, sort_keys=True, separators=(",", ":"))
    if args.emit:
        print(json.dumps(observed, indent=2))
    else:
        expected = runtime.read_json(HERE / "RESULT.json")
        require(
            encoded == json.dumps(expected, sort_keys=True, separators=(",", ":")),
            "exact typed scientific receipt",
        )
        print(
            "PASS strict-padding borrowing, source pins, encoded plans and complete basis endpoints"
        )


if __name__ == "__main__":
    main()
