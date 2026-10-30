#!/usr/bin/env python3
"""Predicate checks for the one-by-one connector instance."""

from verify import realizes


def main():
    assert realizes(("D",))
    assert not realizes(("B",))
    print("PASS_CONNECTOR_DIRECT_CALL_TEST")


if __name__ == "__main__":
    main()
