#!/usr/bin/env python3
"""Independent pair identity on every subset of F_2^3."""

from math import comb


def agrees(even, odd):
    within_even = {}
    for left in range(len(even)):
        for right in range(left + 1, len(even)):
            mask = even[left] ^ even[right]
            within_even[mask] = within_even.get(mask, 0) + 1
    within_odd = {}
    for left in range(len(odd)):
        for right in range(left + 1, len(odd)):
            mask = odd[left] ^ odd[right]
            within_odd[mask] = within_odd.get(mask, 0) + 1
    cross = {}
    for left in even:
        for right in odd:
            mask = left ^ right
            cross[mask] = cross.get(mask, 0) + 1
    collisions = sum(comb(count, 2) for count in cross.values())
    product = sum(
        within_even.get(mask, 0) * within_odd.get(mask, 0)
        for mask in set(within_even) | set(within_odd)
    )
    return collisions == 2 * product


def main():
    checks = 0
    for bits in range(1 << 8):
        points = [point for point in range(8) if (bits >> point) & 1]
        for mask in range(1, 8):
            even = [point for point in points if (point & mask).bit_count() % 2 == 0]
            odd = [point for point in points if (point & mask).bit_count() % 2 == 1]
            assert agrees(even, odd)
            checks += 1
    assert checks == 256 * 7
    print("PASS_PAIR_COLLISION_IDENTITY_TEST")


if __name__ == "__main__":
    main()
