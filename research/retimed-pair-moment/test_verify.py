#!/usr/bin/env python3
"""Counts for the retimed pair."""


def main():
    old = {1: 2439, 2: 726, 3: 224, 4: 102, 5: 20, 8: 8}
    new = {1: 2437, 2: 724, 3: 226, 4: 102, 5: 20, 8: 8}
    mass = lambda histogram: sum(rank * count for rank, count in histogram.items())
    assert mass(old) == mass(new) == 5135
    assert -2 * 1 - 2 * 2 + 2 * 3 == 0
    assert 3 > 2 and 3**3 > 2**3
    print("PASS_RETIMED_PAIR_MOMENT_TEST")


if __name__ == "__main__":
    main()
