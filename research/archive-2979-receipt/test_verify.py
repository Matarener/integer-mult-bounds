#!/usr/bin/env python3
"""Predicate check for a blob-identity count."""

from verify import count_matches


def main():
    assert count_matches([("a", "a"), ("b", "c")]) == 1
    assert count_matches([("a", "a"), ("b", "b")]) == 2
    print("PASS_ARCHIVE_2979_RECEIPT_TEST")


if __name__ == "__main__":
    main()
