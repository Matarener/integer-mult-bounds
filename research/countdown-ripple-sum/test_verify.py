#!/usr/bin/env python3
"""Independent countdown sums through 4096."""


def trailing_zeros(number):
    count = 0
    while number % 2 == 0:
        number //= 2
        count += 1
    return count


def main():
    ripple = 0
    valuation = 0
    for number in range(1, 4097):
        zeros = trailing_zeros(number)
        ripple += zeros + 1
        valuation += zeros
        pop = number.bit_count()
        assert ripple == 2 * number - pop
        assert valuation == number - pop
    print("PASS_COUNTDOWN_RIPPLE_SUM_TEST")


if __name__ == "__main__":
    main()
