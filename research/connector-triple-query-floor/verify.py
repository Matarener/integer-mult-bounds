#!/usr/bin/env python3
"""Triple-source connector steps do not lower the five-source query floor.

The paired-readout contract needs 31 nonzero prefix differences and a closed
walk, so the prefix set P satisfies |P| <= L and C(|P|, 2) >= 31. Counting
gives |P| >= 9. An exhaustive census of the 7,888,725 nine-point sets that
contain 0 shows none have difference set F_2^5, so L >= 10 and the batch
costs at least 72 queries. Step weight never enters that argument: a
triple-source call is one more legal step, not a shorter prefix set.

A second census walks itertools combinations and must match the odometer
totals. Failure controls reject an 8-point cover, a deleted prefix of the
published length-10 set, and a leaf bill below 120 for any length-10 walk
that uses a step of weight at least 2.
"""

from itertools import combinations

PRICES = (1, 4, 10, 16, 28)
PUBLISHED_PREFIXES = (0, 2, 3, 5, 8, 10, 13, 15, 26, 30)
NONZERO = (1 << 32) - 2


def fail(message):
    raise SystemExit("FAIL " + message)


def nonzero_mask(points):
    seen = 0
    for i, left in enumerate(points):
        for right in points[i + 1:]:
            seen |= 1 << (left ^ right)
    return seen


def census_odometer():
    """Nine-point sets containing 0, as 8-subsets of {1,...,31}."""
    index = list(range(8))
    count = covering = max_nonzero = 0
    checksum = 0
    while True:
        points = (0,) + tuple(item + 1 for item in index)
        seen = nonzero_mask(points)
        count += 1
        width = seen.bit_count()
        if width > max_nonzero:
            max_nonzero = width
        if seen == NONZERO:
            covering += 1
        checksum = (checksum + seen) & 0xFFFFFFFFFFFFFFFF
        cursor = 7
        while cursor >= 0 and index[cursor] == 23 + cursor:
            cursor -= 1
        if cursor < 0:
            break
        index[cursor] += 1
        for follower in range(cursor + 1, 8):
            index[follower] = index[follower - 1] + 1
    return count, covering, max_nonzero, checksum


def census_combinations():
    count = covering = max_nonzero = 0
    checksum = 0
    for choice in combinations(range(1, 32), 8):
        seen = nonzero_mask((0,) + choice)
        count += 1
        width = seen.bit_count()
        if width > max_nonzero:
            max_nonzero = width
        if seen == NONZERO:
            covering += 1
        checksum = (checksum + seen) & 0xFFFFFFFFFFFFFFFF
    return count, covering, max_nonzero, checksum


def even_multiplicity_types(total):
    """Nondecreasing 5-tuples of even integers >= 2 that sum to total."""
    found = []

    def walk(remaining, slots, start, prefix):
        if slots == 1:
            if remaining >= start and remaining % 2 == 0:
                found.append(prefix + (remaining,))
            return
        value = start
        while value <= remaining - 2 * (slots - 1):
            if value % 2 == 0:
                walk(remaining - value, slots - 1, value, prefix + (value,))
            value += 2

    walk(total, 5, 2, ())
    return found


def leaf_bill(multiplicities):
    """Pair the largest incidence with the cheapest source price."""
    ordered = tuple(sorted(multiplicities, reverse=True))
    return sum(incidence * price for incidence, price in zip(ordered, PRICES))


def main():
    if (8 * 7) // 2 != 28 or 28 >= 31:
        fail("eight prefixes can cover 31 nonzero masks")
    if (9 * 8) // 2 < 31:
        fail("counting already excludes nine prefixes")

    hyperplane = [value for value in range(32) if value & 1 == 0]
    if nonzero_mask(hyperplane).bit_count() != 15:
        fail("a coordinate hyperplane was not limited to 15 nonzero differences")

    published = nonzero_mask(PUBLISHED_PREFIXES)
    if published.bit_count() != 31:
        fail("published length-10 prefix set does not cover F_2^5")
    for dropped in PUBLISHED_PREFIXES:
        shortened = tuple(point for point in PUBLISHED_PREFIXES if point != dropped)
        if len(shortened) != 9 or nonzero_mask(shortened) == NONZERO:
            fail("deleting one published prefix still covered every mask")

    odometer = census_odometer()
    combined = census_combinations()
    if odometer != combined:
        fail("odometer census %s disagrees with combinations %s" % (odometer, combined))
    count, covering, max_nonzero, _checksum = odometer
    if count != 7888725 or covering != 0 or max_nonzero != 28:
        fail("nine-point census returned %s" % (odometer,))

    # Masks including the automatic zero difference: 28 + 1 = 29 of 32.
    if max_nonzero + 1 != 29:
        fail("mask count including zero is not the predecessor's 29")

    types_12 = even_multiplicity_types(12)
    if types_12 != [(2, 2, 2, 2, 4)]:
        fail("weight 12 has unexpected multiplicity types %s" % (types_12,))
    if leaf_bill(types_12[0]) != 120:
        fail("minimum length-10 leaf bill is not 120")
    # Length 10 admits step weight at most 5, so W <= 50.
    for total in range(14, 51, 2):
        bills = [leaf_bill(item) for item in even_multiplicity_types(total)]
        if not bills or min(bills) <= 120:
            fail("weight %d undercuts the leaf floor: %s" % (total, bills))

    print(
        "PASS_CONNECTOR_TRIPLE_QUERY_FLOOR"
        " sets=%d covering=%d max_nonzero=%d max_masks=%d"
        " queries=72 leaves=120 no_new_kappa"
        % (count, covering, max_nonzero, max_nonzero + 1)
    )


if __name__ == "__main__":
    main()
