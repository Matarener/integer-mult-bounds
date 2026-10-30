#!/usr/bin/env python3
"""Predicate checks for the flag-0 relay window."""

from verify import forward_relays


def main():
    assert forward_relays({"Q3": [3798]}, {"Q3": [130]}) == 0
    assert forward_relays({"Q3": [100]}, {"Q3": [200]}) == 1
    assert not (3500 < 591)
    print("PASS_P104_FLAG0_RELAY_TEST")


if __name__ == "__main__":
    main()
