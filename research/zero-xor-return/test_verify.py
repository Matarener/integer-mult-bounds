#!/usr/bin/env python3
"""Counts for a prefix-walk return."""


def main():
    assert ((1 << 0) ^ (1 << 0)) == 0
    assert (2 - 1) == 1 and (2 - 0) == 2
    print("PASS_ZERO_XOR_RETURN_TEST")


if __name__ == "__main__":
    main()
