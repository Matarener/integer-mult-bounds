#!/usr/bin/env python3
"""Arithmetic of the q-adic row term."""


def main():
    assert 64 * 64 * 80 == 327680
    assert 2 * 327680 == 655360
    assert 655360 > 20161
    print("PASS_QADIC_ROW_EXCESS_TEST")


if __name__ == "__main__":
    main()
