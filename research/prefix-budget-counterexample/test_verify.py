#!/usr/bin/env python3
"""Independent reconstruction of the length-8 counterexample."""

from math import comb


def main():
    state = 0
    seen = [0]
    for bit in (0, 1, 0, 2, 1, 3, 2, 3):
        state ^= 1 << bit
        seen.append(state)
    prefixes = sorted(set(seen[:-1]))
    assert seen[-1] == 0 and prefixes == [0, 1, 2, 3, 4, 6, 8, 12]
    low = [point for point in prefixes if point % 2 == 0]
    high = [point for point in prefixes if point % 2 == 1]
    counts = {}
    for index, left in enumerate(low):
        for right in low[index + 1:]:
            counts[left ^ right] = counts.get(left ^ right, 0) + 1
    high_counts = {high[0] ^ high[1]: 1}
    excess = comb(len(low), 2) - len(counts) + comb(len(high), 2) - len(high_counts)
    assert excess == 8
    assert excess > comb(4, 2) + comb(4, 2) - 7
    assert excess <= comb(6, 2) + comb(2, 2) - 7
    print("PASS_PREFIX_BUDGET_COUNTEREXAMPLE_TEST")


if __name__ == "__main__":
    main()
