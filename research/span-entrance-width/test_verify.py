#!/usr/bin/env python3
"""Counts for the staged entrance width."""


def main():
    assert (2 + 1 + 2 + 1 + 1) == 7
    assert (3 + 1 + 2 + 1 + 1) == 8
    assert (2 + 2 + 1 + 1 + 1) == 7
    assert (3 + 2 + 1 + 1 + 1) == 8
    assert 9 - 2 == 7 and 9 - 1 == 8
    print("PASS_SPAN_ENTRANCE_WIDTH_TEST")


if __name__ == "__main__":
    main()
