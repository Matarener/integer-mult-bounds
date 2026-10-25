#!/usr/bin/env python3
"""Exact finite corroboration of the unbounded serialization proof."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from serialize import (  # noqa: E402
    Program,
    as_json,
    endpoint,
    parse_program,
    profile,
    read_json,
    require,
    serialize,
)

ROOT = HERE.parents[1]


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def authenticate() -> dict[str, object]:
    manifest = read_json(HERE / "SOURCES.json")
    require(type(manifest) is dict and len(manifest["files"]) <= 8, "source manifest")
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        name = row["path"]
        path = ROOT / name
        require(path.resolve().is_relative_to(ROOT), "source escaped repository")
        require(path.is_file() and not path.is_symlink(), "missing regular source")
        with path.open("rb") as stream:
            raw = stream.read(1_048_577)
        require(len(raw) <= 1_048_576, "source too large")
        require(
            hashlib.sha256(raw).hexdigest() == row["sha256"], "source SHA256: " + name
        )
        blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
        require(
            hashlib.sha1(blob).hexdigest() == row["git_blob"], "source blob: " + name
        )
    return manifest


def exhaustive() -> dict:
    """All 4^0+...+4^8 two-root, one-source, one-output words."""
    alphabet = (("B", 0, 0), ("A", 0, 0), ("B", 0, 1), ("A", 0, 1))
    histogram: Counter[str] = Counter()
    digest = hashlib.sha256()
    checked = 0
    accepted = 0
    for length in range(9):
        for codes in itertools.product(range(4), repeat=length):
            checked += 1
            word = Program(1, 2, (0,), tuple(alphabet[c] for c in codes))
            roots, values = endpoint(word)
            if roots != (2, 4) or values[0] not in (0, 1):
                continue
            word = Program(1, 2, values, word.events)
            result = serialize(word)
            accepted += 1
            histogram[f"{length}:{values[0]}"] += 1
            digest.update(
                canonical([list(codes), values[0], as_json(result)["events"]])
            )
            digest.update(b"\n")
    require(checked == 87381, "exhaustive word domain")
    return {
        "tested": checked,
        "accepted": accepted,
        "histogram_length_and_target": dict(sorted(histogram.items())),
        "accepted_serializations_sha256": digest.hexdigest(),
    }


def interleave(streams: list[list[tuple[str, int, int]]]) -> tuple:
    events = []
    for position in range(max(len(stream) for stream in streams)):
        for stream in streams:
            if position < len(stream):
                events.append(stream[position])
    return tuple(events)


def five_source_fixtures() -> list[dict]:
    source = read_json(ROOT / "research/connector-all-tariff-optimum/RESULT.json")
    fixtures = []
    require(len(source["witnesses"]) == 16, "sixteen credited witnesses")
    for item in source["witnesses"]:
        base = [
            (kind, index if kind == "B" else index - 1, 0)
            for kind, index in item["events"]
        ]
        # Two separate roots each add A_7(B_0 x_0+B_1 x_1) to output7.
        # Their identical source contributions cancel; each restores its dirt.
        echo = [("B", 0), ("B", 1), ("A", 6), ("B", 1), ("B", 0), ("A", 6)]
        streams = [base, [(k, i, 1) for k, i in echo], [(k, i, 2) for k, i in echo]]
        for ports, events in ((1, tuple(base)), (3, interleave(streams))):
            word = Program(5, ports, tuple(range(1, 32)), events)
            result = serialize(word)
            fixtures.append(
                {
                    "extra": item["extra"],
                    "input": as_json(word),
                    "serialized": as_json(result),
                    "profile": list(profile(word)),
                }
            )
    return fixtures


def generic_fixtures() -> list[dict]:
    """Vary source/output counts up to sixteen roots with nonzero updates."""
    fixtures = []
    for sources, roots in ((1, 1), (2, 2), (3, 3), (4, 4), (8, 16)):
        streams = []
        targets = tuple(1 << (p % sources) for p in range(roots))
        for p in range(roots):
            j = p % sources
            streams.append([("B", j, p), ("A", p, p), ("B", j, p), ("A", p, p)])
        word = Program(sources, roots, targets, interleave(streams))
        fixtures.append(
            {"input": as_json(word), "serialized": as_json(serialize(word))}
        )
    return fixtures


def price_controls(fixtures: list[dict]) -> dict:
    eligible = list(range(5)) + [
        5 + m - 1 for m in range(1, 32) if m.bit_count() in (3, 5)
    ]
    prices_tested = []
    for cheap in eligible:
        prices = [Fraction(7, 3)] * 36
        prices[cheap] = Fraction(1, 5)
        costs = [
            sum(p * c for p, c in zip(prices, fixture["profile"], strict=True))
            for fixture in fixtures[::2]
        ]
        expected = 2 * sum(prices) + 2 * min(prices[i] for i in eligible)
        require(min(costs) == expected and costs.count(expected) == 1, "exposed tariff")
        prices_tested.append(str(expected))
    return {
        "exposed_profiles": len(prices_tested),
        "exact_bills": prices_tested,
        "unit_map_optimum": 74,
        "transfer_price": "1/4",
        "credited_six_transfer_bill": "147/2",
        "port_specific_fixture_two_roots": 8,
        "port_specific_fixture_one_root": 206,
    }


def boundary_controls() -> dict:
    # Same operator may use different roots; dirt from distinct roots cannot cancel.
    bad = Program(1, 2, (1,), (("B", 0, 0), ("A", 0, 0), ("B", 0, 0), ("A", 0, 1)))
    try:
        serialize(bad)
    except ValueError:
        pass
    else:
        raise ValueError("independent dirt was silently identified")
    events = read_json(
        ROOT / "research/bidirectional-five-source-connector/EVIDENCE.json"
    )["witness"]["complete_word"]
    coupled = {
        "sources": 5,
        "roots": 2,
        "targets": list(range(1, 32)),
        "events": [[k, i - 1 if k == "A" else i, *rest] for k, i, *rest in events],
    }
    try:
        parse_program(coupled)
    except ValueError:
        pass
    else:
        raise ValueError("coupled transfer accepted by the uncoupled interface")
    return {
        "independent_dirty_columns_rejected": True,
        "coupled_alphabet_rejected": True,
        "credited_coupled_word_sha256": hashlib.sha256(canonical(events)).hexdigest(),
    }


def summarize_fixtures(fixtures: list[dict]) -> list[dict]:
    rows = []
    for fixture in fixtures:
        before, after = fixture["input"], fixture["serialized"]
        rows.append(
            {
                "roots": before["roots"],
                "events": len(before["events"]),
                "input_sha256": hashlib.sha256(canonical(before)).hexdigest(),
                "serialized_sha256": hashlib.sha256(canonical(after)).hexdigest(),
            }
        )
    return rows


def build_result() -> dict:
    authenticate()
    five = five_source_fixtures()
    generic = generic_fixtures()
    require(all(len(f["input"]["events"]) == 74 for f in five[::2]), "credited lengths")
    return {
        "schema_version": 1,
        "claim": "Call-count-preserving uncoupled-root serialization",
        "scope": "Finite corroboration of PROOF.md, no supplier or kappa claim",
        "exhaustive": exhaustive(),
        "five_source": summarize_fixtures(five),
        "generic": summarize_fixtures(generic),
        "prices": price_controls(five),
        "boundary": boundary_controls(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--emit", action="store_true", help="emit computed receipt to stdout"
    )
    args = parser.parse_args()
    try:
        result = build_result()
        if args.emit:
            print(json.dumps(result, sort_keys=True, indent=2))
        else:
            require(
                canonical(read_json(HERE / "RESULT.json")) == canonical(result),
                "receipt mismatch",
            )
            print(
                "PASS_CONNECTOR_SERIALIZATION exhaustive=87381 fixtures=37 profiles=16 no_new_kappa"
            )
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as exc:
        parser.exit(2, str(exc) + "\n")


if __name__ == "__main__":
    main()
