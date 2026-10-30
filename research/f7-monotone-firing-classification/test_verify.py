#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Failure controls for the monotone firing classification."""

import verify


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def test_flat_caps_are_sharp_and_the_budget_is_strict():
    maxima = verify.flat_maxima()
    require(verify.flat_excess(range(8)) == 21, "full flat")
    require(verify.flat_excess(range(7)) == 14, "codimension-one deletion")
    require(verify.flat_excess(range(6)) == 8, "six-point example")
    require(maxima[6] == 8 and maxima[7] == 14 and maxima[8] == 21, "maxima")
    capped = maxima[8] + maxima[6]
    require(not (35 < capped <= 35 + 1), "cap 29 does not fire against base 35")
    require(28 < capped <= 28 + 1, "the same cap would fire against base 28")


def test_known_words_keep_their_bills():
    states, end = verify.prefix_states((0, 1, 0, 2, 1, 3, 2, 3))
    require(end == 0 and states == (0, 1, 3, 2, 6, 4, 12, 8), "01021323 states")
    bit0 = verify.fires(4, 8, states, 1)
    high = verify.fires(4, 8, states, 0b1110)
    require(bit0[0] and bit0[1:] == (8, 6, 2, 2, 5), "bit 0 still falsely prunes")
    require(not high[0], "mask 1110 does not fire on 01021323")

    witness, end = verify.prefix_states(verify.WITNESS_4_12)
    require(end == 0, "witness closes")
    fired, excess, even, odd, gap, base = verify.fires(4, 12, witness, 1)
    require(fired and excess == 24 and gap == 2 and base == 23, "witness fires")
    require(excess > base, "witness exceeds the substituted budget")
    require(excess <= base + gap * gap, "witness remains inside the exact budget")
    require(not (excess > base + gap * gap),
            "a real collision would be a different predicate and misses this word")


def test_length_14_is_not_a_subset_of_length_12():
    _, _, short = verify.classify(4, 12)
    _, _, long = verify.classify(4, 14)
    require(1 in short and short[1] == 16, "mask 1 fires 16 times at length 12")
    require(1 not in long and long == {}, "mask 1 is silent at length 14")


def main():
    test_flat_caps_are_sharp_and_the_budget_is_strict()
    test_known_words_keep_their_bills()
    test_length_14_is_not_a_subset_of_length_12()
    print("PASS_F7_MONOTONE_FIRING_TESTS groups=3")
    return 0


if __name__ == "__main__":
    main()
