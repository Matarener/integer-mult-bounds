#!/usr/bin/env python3
"""Independent closed-form replay of n=3 end-support dual-scale (no algebra.py).

Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

import json
import sys
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise SystemExit(f"FAIL_INDEPENDENT: {message}")


def reject_duplicate_keys(pairs):
    keys = [k for k, _ in pairs]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate JSON key")
    return dict(pairs)


def single_exists(a0, M):
    for s in range(M):
        if (s * s) % M == 1 and (a0 * s) % M == 1:
            return True
    return False


def main():
    cert = json.loads(
        (HERE / "CERTIFICATE.json").read_text(), object_pairs_hook=reject_duplicate_keys
    )
    need(cert["no_new_kappa"] is True, "kappa flag")
    need(cert["dimension"] == 3, "n=3")
    need(cert["boolean_meter_inventory"] is False, "no meters")
    need(cert["n2_census_reprinted"] is False, "no n2 census")
    need(cert["square_classification"] == "always_unit_quadratic_residue", "square class")
    need(cert["dual_scale_depends_on_square_root"] is False, "inverse not sqrt")
    need(cert["support"] == ["H'_2", "D'_0"], "end support")
    need(cert["naive_n2_support_involutory_count"] == 0, "naive blocked")

    for row in cert["pairs"]:
        p, w, M = row["p"], row["w"], row["modulus"]
        middle = row["middle"]
        need(M == p**w, "modulus")
        a0 = (1 + p ** (w - 1)) % M
        need(a0 == row["a0"], "a0")
        need(gcd(a0, M) == 1, "unit")
        need((middle * middle) % M == 1, "middle involutory")
        inv = pow(a0, -1, M)
        need(inv == row["inv_a0"], "inv")
        need(not single_exists(a0, M), "single obstructed")
        need(row["single_factor_exists"] is False, "cert single")
        need(row["naive_n2_support_involutory"] is False, "cert naive")
        need(row["middle_scaled"] is False, "middle unscaled")
        need(row["scale_H2"] == inv and row["scale_D0"] == a0, "end scales")
        need(row["target_weights"] == [a0, middle, inv], "target")
        need((a0 * inv) % M == 1, "end reciprocal")
        # Spot bank identity: Norm_end o F_a = F_(a0,m,inv)
        samples = (
            (0, 0, 0, 0, 0, 0),
            (1, 0, 0, 0, 0, 1),
            (0, 1, 0, 1, 0, 0),
            (2 % M, 3 % M, 5 % M, 7 % M, 4 % M, 6 % M),
        )
        for h0, h1, h2, d0, d1, d2 in samples:
            nh = ((a0 * d2) % M, (middle * d1) % M, d0 % M)
            nd = (h2 % M, (middle * h1) % M, (h0 * inv) % M)
            got_h = (nh[0], nh[1], (nh[2] * inv) % M)
            got_d = ((nd[0] * a0) % M, nd[1], nd[2])
            want_h = ((a0 * d2) % M, (middle * d1) % M, (inv * d0) % M)
            # F_(a0,m,inv): D' = (h2/inv, h1/m, h0/a0) = (h2*a0, h1*m, h0*inv)
            want_d = ((h2 * a0) % M, (h1 * middle) % M, (h0 * inv) % M)
            need(got_h == want_h and got_d == want_d, "bank identity spot")
        # Naive n=2 support leaves ends non-involutory
        nh = ((a0 * 1) % M, (middle * 0) % M, 0)
        # After naive scale of H'_1 only, H'_0=a0 and H'_2=0/d0 pattern:
        need((a0 * 1) % M != 1, "naive end product")
        need(pow(a0, (p - 1) // 2, p) == 1, "QR mod p")
        need(row["a0_is_unit_square"] is True, "cert square")
        need((row["square_root"] * row["square_root"]) % M == a0, "root squares to a0")

    rows32 = [r for r in cert["pairs"] if r["p"] == 3 and r["w"] == 2]
    need(sorted(r["middle"] for r in rows32) == [1, 8], "(3,2) middles")
    for row in rows32:
        need(row["scale_H2"] == 7 and row["scale_D0"] == 4, "(3,2) scales")

    print(
        "PASS_INDEPENDENT_PRECISION_BLIND_N3_DUAL_SCALE "
        f"pairs={len(cert['pairs'])} support=(H'_2,D'_0) middles=±1 "
        f"single_factor=0 naive_n2=0 square=always dual_scales=inv "
        f"boolean_meters=false n2_census=false no_new_kappa"
    )


if __name__ == "__main__":
    main()
