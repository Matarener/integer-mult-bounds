#!/usr/bin/env python3
"""Verify n=3 precision-blind dual-scale Norm on end support (H'_2,D'_0).

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
    need(fresh["dimension"] == 3, "n=3")
    need(fresh["support"] == ["H'_2", "D'_0"], "end support")
    need(fresh["single_factor_exists_count"] == 0, "no single-factor pair")
    need(fresh["naive_n2_support_involutory_count"] == 0, "naive n2 blocked")
    need(fresh["boolean_meter_inventory"] is False, "no Boolean meters")
    need(fresh["n2_census_reprinted"] is False, "no n2 census reprint")
    need(fresh["square_classification"] == "always_unit_quadratic_residue", "square class")
    need(fresh["dual_scale_depends_on_square_root"] is False, "existence uses inverse")
    need(fresh["grid"]["pairs"] == len(fresh["pairs"]), "grid size")
    need(fresh["grid"]["middles_per_modulus"] == 2, "both middles")
    need(all(not row["single_factor_exists"] for row in fresh["pairs"]), "all single obstructed")
    need(all(row["naive_n2_support_involutory"] is False for row in fresh["pairs"]), "all naive blocked")
    need(all(row["middle_scaled"] is False for row in fresh["pairs"]), "middle never scaled")
    need(all(row["a0_is_unit_square"] for row in fresh["pairs"]), "all a0 squares")
    need(all(row["support"] == ["H'_2", "D'_0"] for row in fresh["pairs"]), "row support")
    # Both middles at (3,2): target (4,±1,7).
    rows32 = [r for r in fresh["pairs"] if r["p"] == 3 and r["w"] == 2]
    need(len(rows32) == 2, "(3,2) both middles")
    middles = sorted(r["middle"] for r in rows32)
    need(middles == [1, 8], "(3,2) middles +1,-1")
    for row in rows32:
        need(row["scale_H2"] == 7 and row["scale_D0"] == 4, "(3,2) end scales")
        need(row["target_weights"][0] == 4 and row["target_weights"][2] == 7, "(3,2) ends")
        need(row["target_weights"][1] == row["middle"], "(3,2) middle weight")

    cert_path = HERE / "CERTIFICATE.json"
    if write:
        cert_path.write_text(canonical(fresh))
    else:
        committed = load_json(cert_path)
        need(committed == fresh, "certificate drift")

    primes = fresh["grid"]["primes"]
    widths = fresh["grid"]["widths"]
    print(
        "PASS_PRECISION_BLIND_N3_DUAL_SCALE "
        f"pairs={fresh['grid']['pairs']} primes={primes} widths={widths} "
        f"support=(H'_2,D'_0) middles=±1 single_factor=0 naive_n2=0 "
        f"square=always dual_scales=inv boolean_meters=false "
        f"n2_census=false no_new_kappa"
    )


if __name__ == "__main__":
    main()
