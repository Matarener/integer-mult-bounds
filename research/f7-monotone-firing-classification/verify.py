#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Firing-set monotonicity for the fixed L/2 word-budget substitution.

The walk is the PR943 singleton prefix walk: q_0 = 0 and
q_{i+1} = q_i XOR e_{w_i}. A word is simple when the L prefix states are
distinct, restored when it closes at 0 with even label counts, and universal
when those states sum to the whole space. The retained engines replace the
exact collision budget base + d^2 by the fixed balanced budget

    base(n, L) = (L/2) * (L/2 - 1) - (2^{n-1} - 1),

where d = (s - t) / 2 and s, t are the two functional class sizes. A
functional fires on a universal word when

    base < excess <= base + d^2.

Counts below are canonical first-occurrence words, the same normal form as
#3699 and #3733. No predecessor package is imported.
"""

import sys
from itertools import combinations

# Published per-mask false-prune counts. (4,8), (4,10) and (5,12) are #3699.
# (4,12) and (5,14) are #3733's committed RESULT.json.
PUBLISHED = {
    (4, 8): {1: 6, 2: 6, 3: 5, 4: 4, 5: 1, 6: 5, 8: 8, 9: 4, 12: 5},
    (4, 10): {1: 20, 2: 20, 3: 10, 4: 23, 5: 8, 6: 16, 8: 37, 9: 18,
              10: 10, 12: 28},
    (4, 12): {1: 16, 2: 16, 3: 9, 4: 18, 5: 10, 6: 11, 8: 22, 9: 11,
              10: 10, 11: 4, 12: 15, 13: 4, 14: 4},
    (5, 12): {1: 248, 2: 248, 3: 96, 4: 278, 5: 143, 6: 119, 7: 25,
              8: 221, 9: 41, 10: 105, 11: 15, 12: 175, 13: 10, 14: 26,
              16: 361, 17: 140, 18: 100, 19: 50, 20: 64, 21: 4, 22: 32,
              24: 241, 25: 44, 28: 70},
    (5, 14): {1: 4112, 2: 4112, 3: 2385, 4: 4197, 5: 1568, 6: 2574, 7: 356,
              8: 4434, 9: 1630, 10: 1552, 11: 492, 12: 3684, 13: 334, 14: 487,
              16: 8093, 17: 3013, 18: 2085, 19: 904, 20: 1677, 21: 309,
              22: 903, 24: 5326, 25: 917, 26: 170, 28: 1372},
}

# Frozen (5,16) receipt from this enumerator. The published rows above are the
# check that the same code still reproduces #3699 and #3733 before this row is
# trusted. Both excess routes must rebuild it.
EXPECTED_5_16 = {
    1: 35036, 2: 35036, 3: 17298, 4: 34635, 5: 13022, 6: 18872, 7: 2206,
    8: 38495, 9: 13005, 10: 12896, 11: 3325, 12: 25332, 13: 2270, 14: 2910,
    16: 65350, 17: 23887, 18: 18146, 19: 5547, 20: 15733, 21: 2747, 22: 6120,
    24: 40473, 25: 5741, 26: 1728, 28: 8102,
}

WITNESS_4_12 = (0, 1, 0, 2, 0, 1, 0, 3, 1, 2, 1, 3)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def base_budget(n, length):
    require(length % 2 == 0 and n >= 1, "even positive domain")
    half = length // 2
    return half * (half - 1) - ((1 << (n - 1)) - 1)


def flat_excess(points):
    """Collision excess of one subset of the model flat F_2^3."""
    points = list(points)
    size = len(points)
    if size < 2:
        return 0
    support = 0
    for i in range(size):
        left = points[i]
        for j in range(i + 1, size):
            support |= 1 << (left ^ points[j])
    return size * (size - 1) // 2 - support.bit_count()


def flat_maxima():
    """Maximum excess of a k-subset of an affine 3-flat, for every k."""
    maxima = {}
    for size in range(9):
        maxima[size] = max(
            (flat_excess(subset) for subset in combinations(range(8), size)),
            default=0,
        )
    return maxima


def prefix_states(word):
    state = 0
    states = []
    for label in word:
        states.append(state)
        state ^= 1 << label
    return tuple(states), state


def class_excesses(states, mask):
    """Both excess routes, plus the even and odd class sizes."""
    even = []
    odd = []
    for point in states:
        (odd if (point & mask).bit_count() & 1 else even).append(point)
    counter_excess = 0
    set_excess = 0
    for side in (even, odd):
        size = len(side)
        if size < 2:
            continue
        pairs = size * (size - 1) // 2
        bits = 0
        seen = set()
        for i in range(size):
            left = side[i]
            for j in range(i + 1, size):
                difference = left ^ side[j]
                bits |= 1 << difference
                seen.add(difference)
        counter_excess += pairs - bits.bit_count()
        set_excess += pairs - len(seen)
    return counter_excess, set_excess, len(even), len(odd)


def fires(n, length, states, mask):
    counter_excess, set_excess, even, odd = class_excesses(states, mask)
    require(counter_excess == set_excess, "excess routes disagree")
    require((even - odd) % 2 == 0, "class sizes")
    gap = (even - odd) // 2
    base = base_budget(n, length)
    return base < counter_excess <= base + gap * gap, counter_excess, even, odd, gap, base


def enumerate_canonical(n, length):
    words = []
    stack = [(0, 1, -1, 0, ())]
    while stack:
        state, visited, max_label, depth, word = stack.pop()
        if depth == length:
            if state == 0:
                words.append(word)
            continue
        top = min(max_label + 1, n - 1)
        if depth == length - 1:
            for label in range(top + 1):
                if state ^ (1 << label) == 0:
                    stack.append((0, visited, max(max_label, label), depth + 1, word + (label,)))
        else:
            for label in range(top + 1):
                nxt = state ^ (1 << label)
                if ((visited >> nxt) & 1) == 0:
                    stack.append((nxt, visited | (1 << nxt), max(max_label, label),
                                  depth + 1, word + (label,)))
    return words


def canonical_form(word):
    names = {}
    out = []
    for label in word:
        if label not in names:
            names[label] = len(names)
        out.append(names[label])
    return tuple(out)


def enumerate_unconstrained_forms(n, length):
    forms = set()
    stack = [(0, 1, 0, ())]
    while stack:
        state, visited, depth, word = stack.pop()
        if depth == length:
            if state == 0:
                forms.add(canonical_form(word))
            continue
        closing = depth == length - 1
        for label in range(n):
            nxt = state ^ (1 << label)
            if closing:
                if nxt == 0:
                    stack.append((0, visited, depth + 1, word + (label,)))
            elif ((visited >> nxt) & 1) == 0:
                stack.append((nxt, visited | (1 << nxt), depth + 1, word + (label,)))
    return forms


def is_universal(states, n):
    reached = 0
    full = (1 << (1 << n)) - 1
    for left in states:
        for right in states:
            reached |= 1 << (left ^ right)
    return reached == full


def classify(n, length):
    """Return closed count, universal count, and per-mask false-prune counts."""
    counts = {}
    closed = 0
    universal = 0
    masks = range(1, 1 << n)
    for word in enumerate_canonical(n, length):
        closed += 1
        states, end = prefix_states(word)
        require(end == 0, "canonical word did not close")
        require(len(set(states)) == length, "canonical word is not simple")
        if not is_universal(states, n):
            continue
        universal += 1
        for mask in masks:
            if fires(n, length, states, mask)[0]:
                counts[mask] = counts.get(mask, 0) + 1
    return closed, universal, counts


def firing_set(counts):
    return {mask for mask, hits in counts.items() if hits}


def check_flat_bound():
    maxima = flat_maxima()
    require(maxima == {0: 0, 1: 0, 2: 0, 3: 0, 4: 3, 5: 3, 6: 8, 7: 14, 8: 21},
            "flat excess maxima")
    # A 14-point set omits two points of F_2^4. They lie in one level set or
    # in both, so every functional splits the set as (8,6) or (7,7).
    require(maxima[8] + maxima[6] == 29, "fourteen-point excess cap")
    require(maxima[7] + maxima[7] == 28, "balanced fourteen-point excess cap")
    require(29 < base_budget(4, 14) == 35, "(4,14) cap is below the substituted budget")
    require(maxima[8] + maxima[8] == 42 < base_budget(4, 16) == 49,
            "(4,16) cap is below the substituted budget")
    return maxima


def check_published_and_new():
    found = {}
    for n, length in ((4, 8), (4, 10), (4, 12), (4, 14), (4, 16), (5, 12), (5, 14), (5, 16)):
        closed, universal, counts = classify(n, length)
        found[(n, length)] = (closed, universal, counts)
        if (n, length) in PUBLISHED:
            require(counts == PUBLISHED[(n, length)],
                    "per-mask counts disagree with the published receipt at %s" % ((n, length),))
    require(found[(4, 8)][:2] == (29, 22), "(4,8) census")
    require(found[(4, 10)][:2] == (110, 110), "(4,10) census")
    require(found[(4, 12)][:2] == (314, 314), "(4,12) census")
    require(sum(found[(4, 12)][2].values()) == 150, "(4,12) prune total")
    require(found[(4, 14)] == (392, 392, {}), "(4,14) census is universal and silent")
    require(found[(4, 16)] == (112, 112, {}), "(4,16) census is universal and silent")
    require(found[(5, 12)][:2] == (3695, 828), "(5,12) census")
    require(sum(found[(5, 12)][2].values()) == 2856, "(5,12) prune total")
    require(found[(5, 14)][:2] == (33922, 24787), "(5,14) census")
    require(sum(found[(5, 14)][2].values()) == 56686, "(5,14) prune total")
    require(found[(5, 16)][0] == 267890, "(5,16) closed count")
    require(found[(5, 16)][1] == 263140, "(5,16) universal count")
    require(found[(5, 16)][2] == EXPECTED_5_16, "(5,16) per-mask counts")
    require(sum(EXPECTED_5_16.values()) == 447912, "(5,16) prune total")
    return found


def check_monotonicity(found):
    sets = {key: firing_set(counts) for key, (_, _, counts) in found.items()}
    require(sets[(4, 8)] < sets[(4, 10)] < sets[(4, 12)],
            "n=4 firing sets grow through length 12")
    require(sets[(4, 14)] == set() and sets[(4, 16)] == set(),
            "n=4 firing sets are empty at lengths 14 and 16")
    require(not sets[(4, 12)] <= sets[(4, 14)],
            "the length-12 firing set was expected to escape length 14")
    weight_at_most_three = {mask for mask in range(1, 32) if mask.bit_count() <= 3}
    require(sets[(5, 12)] < sets[(5, 14)] == sets[(5, 16)] == weight_at_most_three,
            "n=5 firing set stabilises at weight at most 3")
    require(26 not in sets[(5, 12)] and 26 in sets[(5, 14)],
            "mask 11010 is the (5,12) exception and it fires at (5,14)")
    return sets


def check_witness_and_forms():
    states, end = prefix_states(WITNESS_4_12)
    require(end == 0 and states == (0, 1, 3, 2, 6, 7, 5, 4, 12, 14, 10, 8),
            "witness prefix states")
    require(is_universal(states, 4), "witness universality")
    fired, excess, even, odd, gap, base = fires(4, 12, states, 1)
    require(fired and (excess, even, odd, gap, base) == (24, 8, 4, 2, 23),
            "witness mask-1 bill")
    for n, length in ((4, 8), (4, 10), (4, 12), (4, 14), (4, 16)):
        forms = enumerate_unconstrained_forms(n, length)
        canonical = set(enumerate_canonical(n, length))
        require(forms == canonical, "enumerators disagree at %s" % ((n, length),))


def main():
    maxima = check_flat_bound()
    found = check_published_and_new()
    sets = check_monotonicity(found)
    check_witness_and_forms()
    print(
        "PASS_F7_MONOTONE_FIRING_CLASSIFICATION "
        "flat_max=%s "
        "n4_firing=%s "
        "n5_firing=%s "
        "witness=010201031213 "
        "mask1_fires_at_4_12=%s "
        "mask1_fires_at_4_14=%s "
        "no_new_kappa=true"
        % (
            [maxima[k] for k in range(9)],
            [len(sets[(4, length)]) for length in (8, 10, 12, 14, 16)],
            [len(sets[(5, length)]) for length in (12, 14, 16)],
            1 in sets[(4, 12)],
            1 in sets[(4, 14)],
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
