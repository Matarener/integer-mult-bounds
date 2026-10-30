#!/usr/bin/env python3
"""Alternating-series height certificate. Produced by Nick Petalas. Apache-2.0."""

from fractions import Fraction


def check(condition, message):
    if not condition:
        raise ValueError(message)


def mercator(value):
    """Two successive partial sums bracket ln(value) on [1, 3/2]."""
    check(Fraction(1) <= value <= Fraction(3, 2), "Mercator domain")
    x = value - 1
    partial = Fraction(0)
    power = x
    for index in range(1, 257):
        partial += (1 if index % 2 else -1) * power / index
        power *= x
    return partial, partial + power / 257


def log2(value):
    check(type(value) is int and 1 <= value <= 1 << 64, "positive bounded integer")
    exponent = value.bit_length() - 1
    unit = Fraction(value, 1 << exponent)
    three_low, three_high = mercator(Fraction(3, 2))
    four_low, four_high = mercator(Fraction(4, 3))
    base_low, base_high = three_low + four_low, three_high + four_high
    if unit > Fraction(3, 2):
        low, high = mercator(unit * Fraction(2, 3))
        low, high = low + three_low, high + three_high
    else:
        low, high = mercator(unit)
    check(base_low > 0, "positive base")
    return exponent + low / base_high, exponent + high / base_low


def main():
    height = 12040587444441491
    low, high = log2(height)
    before = Fraction(height - 1, 700000000000) - 322 * low
    check(before < 0, "preceding integer loses")
    low, high = log2(height + 1)
    after = Fraction(height, 700000000000) - 322 * high
    check(after > 0, "new integer wins")
    exact = 0
    for exponent in range(0, 65):
        low, high = log2(1 << exponent)
        check(low <= exponent <= high, "power-of-two logarithm")
        exact += 1
    rejected = 0
    for bad in [0, -1, True, 1 << 65]:
        try:
            log2(bad)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("malformed logarithm input accepted")
    print(f"PASS_INDEPENDENT_INTEGER_HEIGHT minimum={height} adjacent_signs=2 "
          f"exact_powers={exact} controls={rejected}")


if __name__ == "__main__":
    main()
