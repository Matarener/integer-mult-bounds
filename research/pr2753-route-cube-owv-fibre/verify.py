#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact PR2753 route_cube fibre O(wV) invoice; read-only default.

Prepared by Wentao Li with substantial AI assistance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from model import EXPECTED, FIXTURES, predicted, run_suite  # noqa: E402

CERT_PATH = HERE / "CERTIFICATE.json"
SOURCES_PATH = HERE / "SOURCES.json"
PASS = "PASS_PR2753_ROUTE_CUBE_OWV_FIBRE"


def need(ok, message):
    if not ok:
        raise SystemExit(f"FAIL: {message}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json_reject_duplicates(path: Path):
    text = path.read_text(encoding="utf-8")

    def _hook(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError(f"duplicate JSON key {key!r} in {path}")
            out[key] = value
        return out

    return json.loads(text, object_pairs_hook=_hook)


def check_source_pins():
    sources = load_json_reject_duplicates(SOURCES_PATH)
    for rec in sources["files"]:
        if rec["usage"] != "input":
            continue
        live = ROOT / rec["path"]
        need(live.is_file(), f"missing input {rec['path']}")
        need(sha256(live) == rec["sha256"], f"source bytes mismatch: {rec['path']}")
    routes = next(r for r in sources["files"] if r["path"].endswith("/routes.py"))
    need(routes["sha256"] == EXPECTED["routes_sha256"], "routes.py digest")


def check_selected_decimal():
    selected = load_json_reject_duplicates(ROOT / "certificates/selected-result.json")
    need(selected["decimal"] == EXPECTED["selected_decimal"], "selected decimal")


def build_certificate():
    rows, cursor_checks = run_suite()
    need(len(rows) == len(FIXTURES), "fixture census")
    for row in rows:
        pred = predicted(row["q"], row["w"], row["dimension"], row["fibre_bits"])
        need(row["measured_partitions"] == pred["partition_count"], "row partitions")
        need(row["measured_fibre_copy_writes"] == pred["fibre_copy_writes"], "row writes")
        if row["cap"] > 1:
            need(row["OwV_coefficient_lower"] >= 2.0, "coefficient vs wV")
    for bits, passes in cursor_checks.items():
        need(passes == bits, f"cursor lemma bits={bits}")

    # Analytic lower bound vs stated O(wV): for every w>=2 fixture, writes >= 2*w*V.
    for row in rows:
        if row["w"] >= 2:
            need(
                row["fibre_copy_writes"] >= 2 * row["w"] * row["volume"],
                f"OwV lower match w={row['w']}",
            )

    return {
        "schema_version": 1,
        "kind": "exact_implementation_fibre_invoice",
        "claim": {
            "primitive": "routes.route_cube",
            "source_pr": EXPECTED["source_pr"],
            "source_head": EXPECTED["source_head"],
            "metric": "bitstream.copy_bits fibre bit writes inside route_cube",
            "formula_cap_gt_1": EXPECTED["formula_cap_gt_1"],
            "formula_cap_eq_1": EXPECTED["formula_cap_eq_1"],
            "partition_count_cap_gt_1": EXPECTED["partition_count_cap_gt_1"],
            "L_identity": EXPECTED["L_identity"],
            "V_identity": EXPECTED["V_identity"],
            "matches_stated_OwV_charge": True,
            "OwV_match_text": EXPECTED["OwV_match"],
            "no_new_kappa": True,
            "no_supplier_admission": True,
            "selected_decimal": EXPECTED["selected_decimal"],
            "not_algorithmic_optimality": True,
            "not_h2_admission": True,
        },
        "fixtures": rows,
        "cursor_pass_lemma": cursor_checks,
        "controls": [
            "scaled_chart_w2_d1",
            "cap_eq_1_w1_zero_partitions",
            "cursor_pass_counts_3_5_6_8",
            "d2_w2_partition_census",
        ],
    }


def compare_certificate(live, pinned):
    need(live["claim"] == pinned["claim"], "claim mismatch")
    live_cursor = {str(k): v for k, v in live["cursor_pass_lemma"].items()}
    pinned_cursor = {str(k): v for k, v in pinned["cursor_pass_lemma"].items()}
    need(live_cursor == pinned_cursor, "cursor lemma mismatch")
    need(len(live["fixtures"]) == len(pinned["fixtures"]), "fixture count")
    for got, want in zip(live["fixtures"], pinned["fixtures"]):
        for key in (
            "q", "w", "dimension", "fibre_bits", "arena_bits", "cap", "highs",
            "volume", "partition_count", "fibre_copy_writes",
            "measured_partitions", "measured_fibre_copy_writes",
        ):
            need(got[key] == want[key], f"fixture field {key}")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path, default=None,
                        help="write a new certificate path; refuses overwrite")
    args = parser.parse_args(argv)

    check_source_pins()
    check_selected_decimal()
    live = build_certificate()

    if args.write is not None:
        need(not args.write.exists(), "refusing to overwrite certificate")
        args.write.write_text(json.dumps(live, indent=2) + "\n", encoding="utf-8")
        print(f"WROTE {args.write}")
        return 0

    pinned = load_json_reject_duplicates(CERT_PATH)
    compare_certificate(live, pinned)
    n = len(live["fixtures"])
    print(f"{PASS} fixtures={n} cursor_bits={sorted(live['cursor_pass_lemma'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
