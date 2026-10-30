#!/usr/bin/env python3
"""Check private-drop operators and entry adapters, not a full decoder word.

Arham-Tahir64, with OpenAI Codex assistance. Apache-2.0.
Uses the credited retained Clifford compiler and separate Gaussian interpreter.
"""
import argparse
import copy
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


V = load("rank34_audit", HERE / "verify.py")


def rejected(fn):
    try:
        fn()
    except ValueError:
        return True
    return False


def compute():
    V.check_sources()  # Authenticate external executable bytes before importing.
    vendor = V.ROOT / "research/p104-native-channel/vendor"
    compiler = load("rank34_clifford", vendor / "clifford_exact.py")
    oracle = load("rank34_gaussian", vendor / "native_verify.py")
    labels = V.load_labels()
    certificate = json.loads((HERE / "PR3335-CERTIFICATE.json").read_text())
    result = V.evaluate(labels, certificate)
    drops, occurrences = {}, Counter()
    for channel in result["channels"]:
        key = tuple(sorted(channel["plane_basis"]))
        occurrences[key] += 1
        if key in drops:
            continue
        basis = V.binary_basis(key)
        record, _ = compiler.lower_child(compiler.canonical_frame(9, basis).adjoint())
        V.need(record["rank"] == channel["copy_rank"], "native complete-plane private-drop rank")
        expected = oracle.adjoint(oracle.frame(basis, 9))
        oracle.equal(oracle.recipe(record), expected, "rank34 private drop")
        drops[key] = (record, expected)
    # Each support carries an independent total. Equal operator recipes do
    # not identify those values, and therefore do not remove occurrences.
    charged = sum(drops[k][0]["rank"] * n for k, n in occurrences.items())
    distinct = sum(record["rank"] for record, _ in drops.values())
    V.need(charged == result["complete_plane_copy_invoice"], "native occurrence invoice")
    V.need(distinct < charged, "fixture exercises duplicate recipes on independent totals")
    adapters = Counter()
    for pair in certificate["pairs"]:
        basis = V.binary_basis(labels[i] for i in pair)
        plane = compiler.canonical_frame(9, basis)
        for port in pair:
            operator = compiler.cgate(9, labels[port]).adjoint().then(plane)
            record, _ = compiler.lower_child(operator)
            V.need(record["rank"] == 1, "old line entry to rematched plane costs rank one")
            expected = oracle.adjoint((("C", labels[port], 1),)) + oracle.frame(basis, 9)
            oracle.equal(oracle.recipe(record), expected, "line-to-rematched-plane adapter")
            adapters[record["rank"]] += 1
    key = max(drops, key=lambda k: drops[k][0]["rank"])
    record, expected = drops[key]
    for column in range(512):
        V.need(oracle.state(oracle.recipe(record), column) == oracle.state(expected, column),
               "highest-rank drop full Gaussian input basis")
    phase = copy.deepcopy(record)
    phase["left"]["phase"] = (phase["left"]["phase"] + 1) % 4
    V.need(rejected(lambda: oracle.equal(oracle.recipe(phase), expected, "phase control")),
           "wrong global phase rejected")
    half = copy.deepcopy(record)
    half["rank"] //= 2
    V.need(rejected(lambda: oracle.equal(oracle.recipe(half), expected, "rank control")),
           "singleton-rank native substitute rejected")
    V.need(rejected(lambda: V.need(distinct == charged, "deduplicated occurrence count")),
           "recipe deduplication cannot remove independent payloads")
    encoded = json.dumps([{"basis": k, "uses": occurrences[k], "recipe": drops[k][0]}
                          for k in sorted(drops)], sort_keys=True, separators=(",", ":")).encode()
    return {"status": "PASS_RANK34_NATIVE_DROPS", "distinct_drop_recipes": len(drops),
            "drop_occurrences": sum(occurrences.values()), "copy_rank_mass": charged,
            "incorrect_deduplicated_mass": distinct, "recipe_sha256": V.digest(encoded),
            "line_to_plane_adapters": dict(sorted(adapters.items())),
            "highest_drop_rank": record["rank"], "complete_gaussian_columns": 512,
            "rejection_controls": 3}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = json.dumps(compute(), indent=2, sort_keys=True) + "\n"
    if args.output:
        with args.output.open("x", encoding="utf-8") as handle:
            handle.write(payload)
    else:
        V.need(payload == (HERE / "NATIVE.json").read_text(), "exact native receipt")
    print("PASS_RANK34_NATIVE_DROPS recipes=17 occurrences=34 mass=224 adapters=112 columns=512")


if __name__ == "__main__":
    main()
