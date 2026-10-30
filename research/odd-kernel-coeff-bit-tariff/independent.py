#!/usr/bin/env python3
"""Independent replay of the coefficient-bit tariff lemma (no verify import).

Rebuilds T_word from the closed-form variable coefficients and checks that
every odd kernel on j=0..32 strictly exceeds the dyadic fused bill.
Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
MARKER = (
    "PASS_ODD_KERNEL_COEFF_BIT_TARIFF_INDEPENDENT "
    "kernels=[1, 3, 5, 7, 9, 15] j=0..32 "
    "odd_fused_exceeds_dyadic=165 no_new_kappa"
)
ODD = (3, 5, 7, 9, 15)
J_MAX = 32


def need(ok, message):
    if not ok:
        raise ValueError(message)


def bits(value):
    value = Fraction(value)
    return abs(value.numerator).bit_length() + value.denominator.bit_length()


def T_word(k):
    a = Fraction(k, 4)
    variable = (a, 1 + a, -a, -a, -1 / a, 1 / a - 1)
    return 20 + sum(bits(c) for c in variable)


def T_fused(j, q):
    a = q * (1 << j)
    return 2 * T_word(a) + T_word(2 * a)


def main():
    need(T_word(4) == 32 and T_word(2) == 38 and T_word(1) == 45,
         "non-monotone spot")
    exceeds = 0
    for j in range(0, J_MAX + 1):
        dy = T_fused(j, 1)
        for q in ODD:
            bill = T_fused(j, q)
            need(bill > dy, f"q={q} j={j}")
            exceeds += 1
    need(exceeds == 165, "165 comparisons")
    # Cross-check local tariff.py closed form without importing verify.
    import runpy

    tariff = runpy.run_path(str(HERE / "tariff.py"))
    for j in (0, 2, 8, 16, 32):
        for q in (1, 3, 15):
            need(T_fused(j, q) == tariff["T_fused"](j, q), "match tariff module")
    print(MARKER)


if __name__ == "__main__":
    main()
