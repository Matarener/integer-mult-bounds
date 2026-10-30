#!/usr/bin/env python3
"""Replay exact header counts; compare a generated receipt bound to source bytes."""

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import counts


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
SOURCE = "research/selected-bit-recursive-closure/vendor/controlled_normalizer.py"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def authenticate():
    pins = json.loads((PACKAGE/"SOURCES.json").read_text())
    live = {}
    for row in pins["files"]:
        if row["usage"] == "input":
            path = ROOT/row["path"]
            counts.need(digest(path) == row["sha256"], "live source digest mismatch")
            live[row["path"]] = row["sha256"]
    counts.need(SOURCE in live, "normalizer is not a live source")
    return live


def load_source():
    spec = importlib.util.spec_from_file_location("header_density_normalizer", ROOT/SOURCE)
    counts.need(spec is not None and spec.loader is not None, "source loader")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def controls(source):
    identity = ((1, 0), (0, 1))
    swap = ((0, 1), (1, 0))
    p = ((1, 0), (0, 0))
    counts.need(counts.good(p, 1, 3), "positive leading-minor fixture")
    counts.need(not counts.good(tuple(row[::-1] for row in p), 1, 3),
                "wrong-reversal control did not distinguish criteria")
    counts.need(counts.source_admits(source, identity, (0,), 3, 1), "identity header")
    counts.need(not counts.source_admits(source, swap, (0,), 3, 1), "bad header subset")
    p3 = counts.outer((1, 1, 1), (1, 1, 2), 3, True)
    counts.need(counts.determinant(tuple(row[:2] for row in p3[:2]), 3) != 0
                and not counts.good(p3, 2, 3), "final-minor-only control")
    bad_order_header = ((1, 2, 1), (1, 0, 1), (1, 2, 2))
    counts.need(not counts.source_admits(source, bad_order_header, (1, 2), 3, 1),
                "source must reject the earlier zero minor")
    pairs = tuple((u, v) for u in range(3) for v in range(3) if u*v % 3)
    dropped_zero_paths = 0
    for path in counts.product(pairs, repeat=3):
        state, admitted = 0, True
        for u, v in path:
            state = (state+u*v) % 3
            admitted = admitted and state != 0
        dropped_zero_paths += int(admitted and state == 1)
    complete_paths = counts.product_path_census(3, 3)["pairs_ending_at_one"]
    counts.need(dropped_zero_paths != complete_paths, "zero-product omission went undetected")
    bad_lifts = 0
    for high in counts.product(range(3), repeat=4):
        flat = tuple(x+3*y for x, y in zip((0, 1, 1, 0), high))
        g = counts.matrix(flat, 2)
        counts.need(not counts.source_admits(source, g, (0,), 3, 2), "bad high lift")
        bad_lifts += 1
    return {"wrong_reversal_rejected": True, "final_minor_only_rejected": True,
            "bad_restricted_header_subset": True, "bad_high_lifts": bad_lifts,
            "zero_coordinate_products_retained": True,
            "omitted_zero_product_paths": dropped_zero_paths,
            "complete_product_paths": complete_paths}


def scientific_result(source):
    vectors = [counts.vector_census(q, m) for q, m in counts.VECTOR_DOMAINS]
    matrices = [counts.matrix_census(q, w, m) for q, w, m in counts.MATRIX_DOMAINS]
    headers = [counts.header_census(q, w, m, source) for q, w, m in counts.HEADER_DOMAINS]
    paths = [counts.product_path_census(q, m) for q, m in counts.VECTOR_DOMAINS]
    aggregate_total = sum(v["total"] for row in matrices for v in row["ranks"].values())
    aggregate_good = sum(v["good"] for row in matrices for v in row["ranks"].values())
    return {"canonical_projectors": vectors, "all_matrix_census": matrices,
            "complete_header_census": headers, "independent_product_paths": paths,
            "small_ring_aggregate": {"projectors": aggregate_total, "good": aggregate_good},
            "controls": controls(source)}


def receipt():
    live = authenticate()
    source = load_source()
    result = scientific_result(source)
    files = {path.name: digest(path) for path in sorted(PACKAGE.iterdir())
             if path.is_file() and path.name != "RESULT.json"}
    return {"schema_version": 1, "claim_type": "scoped proof with finite certificate",
            "package_sha256": files, "live_input_sha256": live, "result": result}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-receipt", type=Path)
    args = parser.parse_args()
    if args.write_receipt:
        output = args.write_receipt.resolve()
        counts.need(not output.exists(), "receipt output already exists")
        counts.need(not output.is_relative_to(ROOT), "receipt output must be outside checkout")
    result = receipt()
    if args.write_receipt:
        with args.write_receipt.open("x") as handle:
            handle.write(json.dumps(result, indent=2, sort_keys=True)+"\n")
    else:
        expected = json.loads((PACKAGE/"RESULT.json").read_text())
        counts.need(result == expected, "receipt differs from recomputed source-bound result")
    summary = result["result"]["small_ring_aggregate"]
    print("PASS_PROJECTOR_HEADER_DENSITY", json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
