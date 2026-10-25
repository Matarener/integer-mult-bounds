"""Replay an independent two-transfer exclusion. Nick Petalas. Apache-2.0."""

import argparse
import json
import sys
from hashlib import sha256
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from census import census, require

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def read_json(path):
    with path.open("rb") as stream:
        raw = stream.read((1 << 20) + 1)
    require(len(raw) <= 1 << 20, "JSON exceeds one MiB")
    return json.loads(raw)


def check_sources():
    manifest = read_json(HERE / "SOURCES.json")
    require(len(manifest["files"]) <= 32, "source inventory exceeds capacity")
    for entry in manifest["files"]:
        if entry["usage"] == "input":
            source = ROOT / entry["path"]
            require(source.resolve().is_relative_to(ROOT), "source escapes root")
            with source.open("rb") as stream:
                raw = stream.read((1 << 20) + 1)
            require(len(raw) <= 1 << 20, "source exceeds one MiB")
            require(
                sha256(raw).hexdigest() == entry["sha256"],
                "source bytes changed: " + entry["path"],
            )


def result():
    rows = [census(n, triple) for n in (2, 3, 4, 5) for triple in (False, True)]
    for row in rows[-2:]:
        require(
            row["universal_paired"] == row["three_read_repairs"] == 0,
            "five-source exclusion failed",
        )
    require(any(row["first_positive"] for row in rows[:-2]), "positive domain empty")
    native = read_json(ROOT / "research/bidirectional-connector/COST-RECEIPT.json")[
        "native"
    ]
    require(len(native) <= 16, "native receipt row capacity exceeded")
    for row in rows[-2:]:
        previous = next(
            x
            for x in native
            if x["transfers"] == 2 and x["triple"] == row["triple_source"]
        )
        factor = 12 + int(row["triple_source"])
        histogram = [
            factor * row["paired_coverage_histogram"].get(str(i), 0) for i in range(33)
        ]
        require(histogram == previous["histogram"], "full native histogram mismatch")
        require(
            factor * row["restoring_assignments"] == previous["assignments"],
            "rooted-cycle assignment multiplicity mismatch",
        )
    return {"schema": "two-phase-connector-audit-v1", "rows": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="compute receipt on stdout")
    args = parser.parse_args()
    check_sources()
    observed = result()
    if args.emit:
        print(json.dumps(observed, indent=2, sort_keys=True))
    else:
        require(
            observed == read_json(HERE / "RESULT.json"),
            "computed census differs from committed receipt",
        )
        print(
            "PASS_TWO_TRANSFER_INDEPENDENT_AUDIT domains=8 exclusion=both "
            "no_new_tariff_or_kappa"
        )


if __name__ == "__main__":
    main()
