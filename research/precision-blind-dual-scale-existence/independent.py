#!/usr/bin/env python3
"""Independent closed-form replay of dual-scale existence (no algebra.py import).

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
    need(cert["boolean_meter_inventory"] is False, "no meters")
    need(cert["square_classification"] == "always_unit_quadratic_residue", "square class")
    need(cert["dual_scale_depends_on_square_root"] is False, "inverse not sqrt")

    for row in cert["pairs"]:
        p, w, M = row["p"], row["w"], row["modulus"]
        need(M == p**w, "modulus")
        a0 = (1 + p ** (w - 1)) % M
        need(a0 == row["a0"], "a0")
        need(gcd(a0, M) == 1, "unit")
        inv = pow(a0, -1, M)
        need(inv == row["inv_a0"], "inv")
        need(not single_exists(a0, M), "single obstructed")
        need(row["single_factor_exists"] is False, "cert single")
        # Dual-scale closed form
        need(row["scale_H1"] == inv and row["scale_D0"] == a0, "scales")
        need(row["target_weights"] == [a0, inv], "target")
        need((a0 * inv) % M == 1, "involutory")
        # Spot bank identity without importing algebra.py
        for h0, h1, d0, d1 in ((0, 0, 0, 0), (1, 0, 0, 1), (0, 1, 1, 0), (2 % M, 3 % M, 5 % M, 7 % M)):
            nh = ((a0 * d1) % M, d0 % M)
            nd = (h1 % M, (h0 * inv) % M)
            got_h = (nh[0], (nh[1] * inv) % M)
            got_d = ((nd[0] * a0) % M, nd[1])
            want_h = ((a0 * d1) % M, (inv * d0) % M)
            want_d = ((h1 * a0) % M, (h0 * inv) % M)  # inv1 = a0 since p1=inv
            # F_(a0,inv): nd = (h1 / inv, h0 / a0) = (h1 * a0, h0 * inv)
            need(got_h == want_h and got_d == want_d, "bank identity spot")
        # Square mod p
        need(pow(a0, (p - 1) // 2, p) == 1, "QR mod p")
        need(row["a0_is_unit_square"] is True, "cert square")
        need((row["square_root"] * row["square_root"]) % M == a0, "root squares to a0")

    # #4063 cross-check
    row32 = next(r for r in cert["pairs"] if r["p"] == 3 and r["w"] == 2)
    need(row32["scale_H1"] == 7 and row32["scale_D0"] == 4, "4063 scales")
    need(row32["target_weights"] == [4, 7], "4063 target")

    print(
        "PASS_INDEPENDENT_PRECISION_BLIND_DUAL_SCALE_EXISTENCE "
        f"pairs={len(cert['pairs'])} single_factor=0 square=always "
        f"dual_scales=inv crosscheck_4063=(7,4) boolean_meters=false no_new_kappa"
    )


if __name__ == "__main__":
    main()
