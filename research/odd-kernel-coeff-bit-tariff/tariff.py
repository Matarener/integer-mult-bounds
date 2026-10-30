"""Coefficient-bit tariff for PR840 / odd-kernel ADDRESS query lowerings.

Tariff T_word(k) sums bit_length(|numerator|) + bit_length(denominator) over
every affine diagonal and control coefficient in address_word(k), reduced.

Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

from fractions import Fraction


def need(ok, message):
    if not ok:
        raise ValueError(message)


def odd_kernel_power(j, sign=1, kernel=1):
    need(type(j) is int and j >= 0, "nonnegative dyadic index")
    need(type(sign) is int and sign in (-1, 1), "integer sign")
    need(type(kernel) is int and kernel > 0 and kernel % 2 == 1, "positive odd kernel")
    return sign * kernel * (1 << j)


def address_word(k):
    """Seven events for M(k)=I+(k/4) s r^T; identical shape to odd-kernel-query-pair."""
    need(type(k) is int and k != 0, "nonzero integer query power")
    a = Fraction(k, 4)
    return (
        ("affine", 2, Fraction(1), ((0, Fraction(-1)),)),
        ("affine", 3, Fraction(1), ((0, Fraction(1)),)),
        ("affine", 5, a, ((0, 1 + a), (2, -a), (3, -a))),
        ("child", 0, 5),
        ("affine", 2, Fraction(1), ((0, Fraction(1)),)),
        ("affine", 3, Fraction(1), ((0, Fraction(-1)),)),
        ("affine", 5, -1 / a, ((0, 1 / a - 1), (2, Fraction(1)),
                              (3, Fraction(1)))),
    )


def coeff_bit_length(value):
    """Bits charged for one reduced rational coefficient."""
    value = Fraction(value)
    return abs(value.numerator).bit_length() + value.denominator.bit_length()


def word_coefficients(k):
    """All affine diagonal and control coefficients of address_word(k)."""
    out = []
    for event in address_word(k):
        if event[0] != "affine":
            continue
        out.append(Fraction(event[2]))
        for _, c in event[3]:
            out.append(Fraction(c))
    return tuple(out)


def T_word(k):
    """Named physical tariff: total numerator+denominator bit lengths."""
    return sum(coeff_bit_length(c) for c in word_coefficients(k))


def fused_powers(j, kernel=1, sign=1):
    a = odd_kernel_power(j, sign, kernel)
    return (-a, 2 * a, -a)


def baseline_powers(j, kernel=1, sign=1):
    a = odd_kernel_power(j, sign, kernel)
    return (-a, a, a, -a)


def T_program(powers):
    return sum(T_word(k) for k in powers)


def T_fused(j, kernel=1):
    return T_program(fused_powers(j, kernel))


def T_baseline(j, kernel=1):
    return T_program(baseline_powers(j, kernel))


def closed_form_T_word(k):
    """Independent closed form matching address_word's six variable coeffs + units.

    Unit (±1) coefficients contribute 10 * 2 = 20 bits. Variable coefficients
    are a, 1+a, -a, -a, -1/a, 1/a-1 with a = k/4.
    """
    need(type(k) is int and k != 0, "nonzero k")
    a = Fraction(k, 4)
    variable = (a, 1 + a, -a, -a, -1 / a, 1 / a - 1)
    return 20 + sum(coeff_bit_length(c) for c in variable)
