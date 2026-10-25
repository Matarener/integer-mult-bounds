#!/usr/bin/env python3
"""Independent closed-form replay of the precision-blind Boolean-norm invoice.

Does not import invoice.py meters; recomputes algebraic identities and the
plane×call closed forms, then compares to CERTIFICATE.json.

Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

import json
from math import gcd, prod
from pathlib import Path

HERE = Path(__file__).resolve().parent
MARKER = (
    "PASS_INDEPENDENT_PRECISION_BLIND_BOOLEAN_NORM_INVOICE "
    "raw=729/6561 normalized=6561/6561 "
    "dual_scales=(7,4) "
    "scale=341172 inverse=341172 source_access=170586 "
    "restoration=170638 frame_copy=511758 "
    "single_factor_obstructed "
    "no_new_kappa"
)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def pairs_unique(pairs):
    value = {}
    for key, item in pairs:
        need(key not in value, "duplicate JSON key")
        value[key] = item
    return value


def main():
    cert = json.loads(
        (HERE / "CERTIFICATE.json").read_text(), object_pairs_hook=pairs_unique
    )
    q, w_exp, dimension = 3, 2, 2
    modulus = q**w_exp
    weights = (4, 1)
    scale_h1, scale_d0 = 7, 4
    target = (4, 7)
    address_volume = modulus ** (2 * dimension)
    planes = max(1, address_volume.bit_length())
    calls = planes * 2
    raw = (modulus**dimension) * prod(
        gcd(modulus, (weights[i] * weights[dimension - 1 - i] - 1) % modulus)
        for i in range(dimension)
    )
    need(raw == 729, "formula (5)")
    need(address_volume == 6561, "volume")
    need(planes == 13 and calls == 26, "planes/calls")
    # Single shared factor never involutory
    single_ok = False
    for s in range(modulus):
        if (s * s) % modulus == 1 and (4 * s) % modulus == 1:
            single_ok = True
    need(not single_ok, "single-factor obstruction")
    # Dual-scale Norm∘F_a = F_(4,7) on bank images
    for d0 in range(modulus):
        for d1 in range(modulus):
            nh0 = weights[0] * d1 % modulus
            nh1 = (weights[1] * d0 * scale_h1) % modulus
            need((nh0, nh1) == (target[0] * d1 % modulus, target[1] * d0 % modulus), "H'")
    for h0 in range(modulus):
        for h1 in range(modulus):
            nd0 = (h1 * pow(weights[1], -1, modulus) * scale_d0) % modulus
            nd1 = (h0 * pow(weights[0], -1, modulus)) % modulus
            # P'^{-1}(h0,h1) = (inv(p1)*h1, inv(p0)*h0)
            expect0 = h1 * pow(target[1], -1, modulus) % modulus
            expect1 = h0 * pow(target[0], -1, modulus) % modulus
            need((nd0, nd1) == (expect0, expect1), "D'")
    # (P')^2 = I
    for x0 in range(modulus):
        for x1 in range(modulus):
            y0 = target[0] * x1 % modulus
            y1 = target[1] * x0 % modulus
            z0 = target[0] * y1 % modulus
            z1 = target[1] * y0 % modulus
            need((z0, z1) == (x0, x1), "(P')^2")
    scale_total = 2 * address_volume * calls
    inverse_total = 2 * address_volume * calls
    source_access = address_volume * calls
    callee_copy = address_volume * calls
    restoration_payload = address_volume * calls
    restoration_rowcount = 2 * calls
    restoration = restoration_payload + restoration_rowcount
    pad_in = address_volume * calls
    pad_out = address_volume * calls
    frame_copy = pad_in + pad_out + callee_copy
    need(scale_total == 341172, "scale closed form")
    need(inverse_total == 341172, "inverse closed form")
    need(source_access == 170586, "source closed form")
    need(restoration == 170638, "restoration closed form")
    need(frame_copy == 511758, "frame_copy closed form")
    c = cert["counts"]
    need(c["raw_agreements"] == raw, "cert raw")
    need(c["normalized_agreements"] == address_volume, "cert normalized")
    need(c["scale"] == scale_total, "cert scale")
    need(c["inverse"] == inverse_total, "cert inverse")
    need(c["source_access"] == source_access, "cert source")
    need(c["restoration"] == restoration, "cert restoration")
    need(c["frame_copy"] == frame_copy, "cert frame_copy")
    need(cert["fixture"]["scale_H1"] == scale_h1, "cert scale_H1")
    need(cert["fixture"]["scale_D0"] == scale_d0, "cert scale_D0")
    need(cert["fixture"]["single_factor_norm_involutory"] is False, "obstruction")
    need(cert["no_new_kappa"] is True, "no new kappa")
    need(cert["kappa_decimal"] == "0.001672660197076918", "kappa")
    print(MARKER)


if __name__ == "__main__":
    main()
