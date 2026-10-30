#!/usr/bin/env python3
"""Predicate checks for a map that omits a replay path."""

from verify import omitted


def main():
    assert omitted("the live map", "research/p104-pooled-cut-independent")
    assert not omitted("see research/p104-pooled-cut-independent", "research/p104-pooled-cut-independent")
    print("PASS_P104_OBSTRUCTION_INDEX_TEST")


if __name__ == "__main__":
    main()
