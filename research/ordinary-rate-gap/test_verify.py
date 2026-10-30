#!/usr/bin/env python3
"""The two ordinary-rate coefficients."""


def main():
    assert 801 + 4 * 10 ** 6 * 17 // 16 + 32780 + 3 == 4283584
    assert 801 + 8 * 10 ** 6 + 32780 + 3 == 8033584
    print("PASS_ORDINARY_RATE_GAP_TEST")


if __name__ == "__main__":
    main()
