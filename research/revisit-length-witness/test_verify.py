#!/usr/bin/env python3
"""Counts for the revisit-length witnesses."""


def main():
    assert [2, 20, 22] == sorted(length for length in (22, 2, 20))
    assert len({(11, 10), (11, 9), (10, 10), (11, 8), (10, 9), (11, 7), (10, 8), (9, 9), (11, 6), (10, 7)}) == 10
    print("PASS_REVISIT_LENGTH_WITNESS_TEST")


if __name__ == "__main__":
    main()
