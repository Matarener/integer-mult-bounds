#!/usr/bin/env python3
"""Verify odd-n precision-blind dual-scale support classification.

Read-only by default; --write regenerates CERTIFICATE.json.
Admission uses need(); survives -O and -Werror.

Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from algebra import (  # noqa: E402
    KAPPA_DECIMAL,
    build_certificate,
    need,
)


def reject_duplicate_keys(pairs):
    keys = [k for k, _ in pairs]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate JSON key")
    return dict(pairs)


def load_json(path: Path):
    return json.loads(path.read_text(), object_pairs_hook=reject_duplicate_keys)


def check_sources():
    sources = load_json(HERE / "SOURCES.json")
    base = sources["base_commit"]
    need(base == "20ecf2891d80b5acf18d980b2164fb44ea7faa90", "pin CrocSwap/main tip")
    for row in sources["files"]:
        path = row["path"]
        raw = subprocess.check_output(["git", "show", f"{base}:{path}"], cwd=ROOT)
        digest = hashlib.sha256(raw).hexdigest()
        need(digest == row["sha256"], f"sha256 {path}")
        blob = subprocess.check_output(
            ["git", "rev-parse", f"{base}:{path}"], cwd=ROOT, text=True
        ).strip()
        need(blob == row["git_blob"], f"git_blob {path}")
        if row["usage"] == "input":
            live = (ROOT / path).read_bytes()
            need(hashlib.sha256(live).hexdigest() == row["sha256"], f"live sha256 {path}")
            live_blob = subprocess.check_output(
                ["git", "rev-parse", f"HEAD:{path}"], cwd=ROOT, text=True
            ).strip()
            need(live_blob == row["git_blob"], f"live git_blob {path}")


def check_kappa():
    selected = load_json(ROOT / "certificates/selected-result.json")
    need(selected["decimal"] == KAPPA_DECIMAL, "selected decimal kappa")
    need(
        selected["kappa"] == "836330098538459/500000000000000000",
        "selected fraction kappa",
    )


def canonical(data):
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    write = "--write" in argv
    check_sources()
    check_kappa()
    fresh = build_certificate()
    need(fresh["no_new_kappa"] is True, "no new kappa")
    need(fresh["dimensions"] == [5, 7], "n=5,7")
    need(fresh["boolean_meter_inventory"] is False, "no Boolean meters")
    need(fresh["n2_census_reprinted"] is False, "no n2 census")
    need(fresh["n3_grid_reprinted"] is False, "no n3 grid reprint")
    need(fresh["single_factor_exists_count"] == 0, "no single-factor")
    need(fresh["square_classification"] == "always_unit_quadratic_residue", "square")
    need(fresh["dual_scale_depends_on_square_root"] is False, "uses inverse")
    need(fresh["grid_n5"]["rows"] == len(fresh["rows_n5"]), "n5 grid size")
    need(fresh["grid_n7"]["rows"] == len(fresh["rows_n7"]), "n7 grid size")
    need(fresh["grid_n5"]["supports_classified_per_row"] == 25, "n5 classify 25")
    need(fresh["grid_n7"]["supports_classified_per_row"] == 49, "n7 classify 49")

    for row in fresh["rows_n5"] + fresh["rows_n7"]:
        need(row["good_supports"] == 2, "exactly two goods")
        need(row["single_factor_exists"] is False, "single obstructed")
        n = row["n"]
        need(row["far_end"]["support"] == [f"H'_{n-1}", "D'_0"], "far name")
        need(row["near_end"]["support"] == ["H'_0", f"D'_{n-1}"], "near name")
        need(row["far_end"]["scale_H"] == row["inv_a0"], "far s")
        need(row["far_end"]["scale_D"] == row["a0"], "far t")
        need(row["near_end"]["scale_H"] == row["inv_a0"], "near s")
        need(row["near_end"]["scale_D"] == row["a0"], "near t")
        need(row["far_end"]["target"][0] == row["a0"], "far p0")
        need(row["far_end"]["target"][-1] == row["inv_a0"], "far p_last")
        need(row["near_end"]["target"][0] == 1, "near p0")
        need(row["near_end"]["target"][-1] == 1, "near p_last")

    for row in fresh["illegal_middle_rows"]:
        need(row["good_supports"] == 0, "illegal zero")

    # Concrete (3,2) n=5 both supports.
    rows32 = [r for r in fresh["rows_n5"] if r["p"] == 3 and r["w"] == 2]
    need(len(rows32) == 4, "(3,2) four legal middles")
    for row in rows32:
        need(row["a0"] == 4 and row["inv_a0"] == 7, "(3,2) a0")
        need(row["far_end"]["scale_H"] == 7 and row["far_end"]["scale_D"] == 4, "far scales")
        need(row["near_end"]["target"][0] == 1 and row["near_end"]["target"][-1] == 1, "near ends")

    cert_path = HERE / "CERTIFICATE.json"
    if write:
        cert_path.write_text(canonical(fresh))
    else:
        committed = load_json(cert_path)
        need(committed == fresh, "certificate drift")

    print(
        "PASS_PRECISION_BLIND_ODD_N_SUPPORT "
        f"n5_rows={fresh['grid_n5']['rows']} n7_rows={fresh['grid_n7']['rows']} "
        f"goods=far+near supports_n5=25 supports_n7=49 "
        f"illegal_zero={len(fresh['illegal_middle_rows'])} "
        f"single_factor=0 boolean_meters=false "
        f"n2_census=false n3_grid=false no_new_kappa"
    )


if __name__ == "__main__":
    main()
