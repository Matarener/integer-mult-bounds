#!/usr/bin/env python3
"""Closed form of the nine-stage BIT row."""


def main():
    assert 2 * (64 * 64 + 1) + 367 * 27 + 9 * 28 == 18355
    assert 18355 < 20161
    print("PASS_BIT_ROW_ALLOWANCE_TEST")


if __name__ == "__main__":
    main()
