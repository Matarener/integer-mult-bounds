#!/usr/bin/env python3
"""Arithmetic of the normalized COPY floor."""


def main():
    for excess_p in (0, 1):
        for excess_q in (0, 1):
            terms = 8 + excess_p + excess_q
            assert 9 * (terms - excess_p - excess_q) == 72
    assert 8 * 9 == 72
    print("PASS_COPY_FLOOR_ARITHMETIC_TEST")


if __name__ == "__main__":
    main()
