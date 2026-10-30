"""Positive, exhaustive small-domain and failure controls, including -O."""

import random
import sys
from copy import deepcopy
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import independent
import verify


def reject(function, message):
    try:
        function()
    except ValueError:
        return
    raise ValueError("accepted invalid control: " + message)


def brute_groups(labels):
    groups = []
    for mask in range(1, 1 << len(labels)):
        vertices = [i for i in range(len(labels)) if mask & (1 << i)]
        if (
            len(vertices) % 2 == 0
            and len(vertices) <= 8
            and all(
                (labels[i] & labels[j]).bit_count() % 2 == 0
                for i, j in combinations(vertices, 2)
            )
        ):
            groups.append(mask)
    return groups


def brute_cover(groups, n):
    best = [99] * (1 << n)
    best[0] = 0
    for mask in range(1, 1 << n):
        for group in groups:
            if group & mask == group:
                best[mask] = min(best[mask], 1 + best[mask ^ group])
    return best[-1] <= 4


def small_oracles(labels):
    rng = random.Random(2)
    outcomes = set()
    for index in range(36):
        subset = rng.sample(labels, index % 9)
        expected = brute_groups(subset)
        vectors = [tuple((q >> bit) & 1 for bit in range(9)) for q in subset]
        first = verify.even_groups(subset)
        second = independent.enumerate_groups(vectors)
        verify.need(
            set(first) == set(second) == set(expected), "powerset clique oracle"
        )
        wanted = brute_cover(expected, len(subset))
        actual, _, _ = verify.four_cover(subset)
        other, _ = independent.cover_exists(second, len(subset), 4)
        verify.need(actual == other == wanted, "exhaustive minimum-cover oracle")
        outcomes.add(wanted)
    verify.need(outcomes == {False, True}, "both oracle outcomes exercised")


def failures(labels, upper):
    duplicate = deepcopy(upper)
    duplicate[0][0] = duplicate[0][1]
    reject(lambda: verify.validate_partition(labels, duplicate, 16), "duplicate port")
    odd = deepcopy(upper)
    odd[0].pop()
    reject(lambda: verify.validate_partition(labels, odd, 16), "odd group")
    changed = labels.copy()
    changed[upper[0][0]] = labels[upper[0][1]]
    reject(lambda: verify.validate_partition(changed, upper, 16), "false Gram identity")
    reject(lambda: verify.even_groups([1] * 25), "domain capacity")
    reject(
        lambda: verify.two_group_unions([3] * (verify.MAX_GROUPS + 1)), "group capacity"
    )
    reject(lambda: independent.cover_exists([], 25, 4), "independent domain capacity")
    reject(lambda: independent.cover_exists([], 8, 5), "independent depth capacity")
    reject(
        lambda: verify.authenticate(b"altered", {"sha256": "0" * 64}),
        "source integrity",
    )
    old_limit = independent.MAX_STATES
    try:
        independent.MAX_STATES = 0
        reject(
            lambda: independent.cover_exists([3], 2, 4), "unknown on budget exhaustion"
        )
    finally:
        independent.MAX_STATES = old_limit


def main():
    labels, _, upper = verify.inputs()
    small_oracles(labels)
    failures(labels, upper)
    # A known complete cover must succeed; deleting its last required group must fail.
    groups = [3, 12, 48, 192]
    full = 255
    unions = verify.two_group_unions(groups)
    verify.need(
        any(full ^ mask in unions for mask in unions), "four-group positive fixture"
    )
    unions = verify.two_group_unions(groups[:-1])
    verify.need(
        not any(full ^ mask in unions for mask in unions), "missing-group fixture"
    )
    print("PASS_P112_REPAIR_CONTROLS small_oracles=36 failures=9 fixtures=2")


if __name__ == "__main__":
    main()
