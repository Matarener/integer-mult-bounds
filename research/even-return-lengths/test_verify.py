#!/usr/bin/env python3
"""Counts for the even return lengths."""


def main():
    lengths = [4, 6, 8, 10, 12, 14, 16, 18]
    assert lengths == list(range(4, 19, 2))
    assert len(lengths) == 8
    print("PASS_EVEN_RETURN_LENGTHS_TEST")


if __name__ == "__main__":
    main()
