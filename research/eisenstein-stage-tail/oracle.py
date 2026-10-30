"""Literal B_K stage schedule and exact integral lower sums.

Produced by Nick Petalas. Apache-2.0.
This module does not import the grouped profile or its polynomial proof.
"""

from collections import Counter
from fractions import Fraction

MAX_K = 128


def checked_k(k):
    if type(k) is not int or not 1 <= k <= MAX_K:
        raise ValueError("K must be an integer in 1..128")
    return k


def schedule(k):
    """Each inactive run is cut at the named pre-bridge read boundary."""
    checked_k(k)
    stages = 2 * k + 1
    slots = Counter()
    for _stage in range(stages):
        slots[3] += 6  # Two active bank wires each climb three.
        slots[4] += Fraction(5, 8)
    for pair in range(k):
        active = {0, 1, 2} if pair == 0 else {2 * pair + 1, 2 * pair + 2}
        run = 0
        for boundary in range(stages + 1):
            split = pair > 0 and boundary == 2 * pair
            stop = boundary == stages or boundary in active
            if (split or stop) and run:
                rank = 3 * run
                slots[max(4, rank)] += 2 * rank
                run = 0
            if boundary < stages and boundary not in active:
                run += 1
    return dict(slots)


def midpoint_log_lower(ratio, pieces=4):
    """Convexity of 1/t gives an exact lower Riemann sum for log."""
    ratio = Fraction(ratio)
    if ratio < 1 or type(pieces) is not int or not 1 <= pieces <= 16:
        raise ValueError("require ratio>=1 and 1..16 midpoint pieces")
    width = (ratio - 1) / pieces
    return sum(width / (1 + (Fraction(j) + Fraction(1, 2)) * width)
               for j in range(pieces))


def schedule_cost_lower(k):
    checked_k(k)
    width = 6 * k + 4
    return sum(mass * midpoint_log_lower(Fraction(width, cap))
               for cap, mass in schedule(k).items())


def weighted_reciprocal_gap(k):
    """Cauchy's inequality on the literal repeated idle lengths."""
    checked_k(k)
    if k == 1:
        return Fraction(0)
    width = 6 * k + 4
    weights = [24 * p for p in range(1, k)]
    lengths = [6 * p for p in range(1, k)]
    total = sum(weights)
    mean = Fraction(sum(w * r for w, r in zip(weights, lengths)), total)
    literal = sum(Fraction(2 * w * (width - r), width + r)
                  for w, r in zip(weights, lengths))
    bound = 2 * total * (width - mean) / (width + mean)
    return literal - bound
