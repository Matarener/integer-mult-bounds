#!/usr/bin/env python3
"""Independent logarithm bound through 4096."""

from fractions import Fraction


def ceil_log2(number):
    floor = number.bit_length() - 1
    return floor if (1 << floor) == number else floor + 1


def main():
    total = Fraction(0)
    term = Fraction(1)
    for index in range(30):
        total += term
        term /= 2 * (index + 1)
    assert total + 2 * term < 2
    assert 4 * 2 * 3 == 24
    for number in range(1, 4097):
        ceiling = ceil_log2(number + 2)
        assert ceiling * ceiling <= 24 * number
        assert number + 2 <= 3 * number
    print("PASS_LOG_ABSORPTION_BOUND_TEST")


if __name__ == "__main__":
    main()
