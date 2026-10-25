#!/usr/bin/env python3
"""Independent closed-form replay of the Boolean-norm invoice.

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
    "PASS_INDEPENDENT_WEIGHTED_CALLEE_BOOLEAN_NORM_INVOICE "
    "raw=9/81 normalized=81/81 "
    "scale=2268 inverse=2268 source_access=1134 "
    "restoration=1162 frame_copy=3402 "
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
    modulus, dimension = 3, 2
    weights = (2, 1)
    scale = 2
    address_volume = modulus ** (2 * dimension)
    planes = max(1, address_volume.bit_length())
    calls = planes * 2
    raw = (modulus**dimension) * prod(
        gcd(modulus, (weights[i] * weights[dimension - 1 - i] - 1) % modulus)
        for i in range(dimension)
    )
    need(raw == 9, "formula (5)")
    # Norm∘F_a identity on one address sample lattice
    for a0 in range(modulus):
        for a1 in range(modulus):
            # P
            y0 = weights[0] * a1 % modulus
            y1 = weights[1] * a0 % modulus
            # Norm on a single bank image used as H' or D' fragment
            # P' = T P: (2 a1, 2 a0)
            p0 = (scale * a1) % modulus
            p1 = (scale * a0) % modulus
            # (P')^2
            z0 = (scale * p1) % modulus
            z1 = (scale * p0) % modulus
            need((z0, z1) == (a0, a1), "(P')^2")
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
    need(scale_total == 2268, "scale closed form")
    need(inverse_total == 2268, "inverse closed form")
    need(source_access == 1134, "source closed form")
    need(restoration == 1162, "restoration closed form")
    need(frame_copy == 3402, "frame_copy closed form")
    c = cert["counts"]
    need(c["raw_agreements"] == raw, "cert raw")
    need(c["normalized_agreements"] == address_volume, "cert normalized")
    need(c["scale"] == scale_total, "cert scale")
    need(c["inverse"] == inverse_total, "cert inverse")
    need(c["source_access"] == source_access, "cert source")
    need(c["restoration"] == restoration, "cert restoration")
    need(c["frame_copy"] == frame_copy, "cert frame_copy")
    need(cert["no_new_kappa"] is True, "no new kappa")
    need(cert["kappa_decimal"] == "0.001672660197076918", "kappa")
    print(MARKER)


if __name__ == "__main__":
    main()
