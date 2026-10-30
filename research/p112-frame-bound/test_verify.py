#!/usr/bin/env python3
"""Arithmetic checks for the P112 frame bound."""


def tariff(size):
    return 72 + 2 * (112 - size)


def main():
    assert 2 * 4 <= 9 < 2 * 5
    assert 4 * 14 == 56
    assert tariff(32) == 232
    assert [tariff(size) for size in range(33, 37)] == [230, 228, 226, 224]
    assert tariff(56) == 184
    print("PASS_P112_FRAME_BOUND_TEST")


if __name__ == "__main__":
    main()
