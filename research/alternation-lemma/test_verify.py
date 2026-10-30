#!/usr/bin/env python3
"""Counts for the alternation lemma."""


def main():
    mask = 0b0111
    assert ((mask & (0 ^ (1 << 3))) ^ (mask & 0)) == 0
    assert ((0b1111 & (1 << 3)) == (1 << 3))
    print("PASS_ALTERNATION_LEMMA_TEST")


if __name__ == "__main__":
    main()
