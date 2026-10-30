#!/usr/bin/env python3
"""Coset-wide one-point pair ceiling for n=7 weight splits.

The strict test "every one-point completion has pair product < need" deletes
no branch on a basic-identity survivor. This is a finite certificate plus one
equality witness. It does not decide f(7).

Apache-2.0. Prepared by unpaidmoon with substantial Cursor Grok assistance.
"""

from collections import Counter
from hashlib import sha256
import json
from math import comb
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MATH = "research/f7-weight-parity-census-correction/MATH.md"
MARKER = "PASS_F7_ONE_POINT_PAIR_CEILING"

# Parts at most 11. Columns are s, t, need, h, S_min.
# h is the coset-wide one-point lower bound with the missing point on the
# t side. Both orientations are rows.
FROZEN_PARTS_AT_MOST_11 = (
    (6, 11, 1, 3, 0),
    (7, 10, 3, 4, 0),
    (7, 11, 7, 7, 3),
    (8, 10, 8, 9, 4),
    (8, 11, 12, 13, 8),
    (9, 9, 9, 9, 4),
    (9, 10, 13, 15, 9),
    (9, 11, 18, 20, 13),
    (10, 7, 3, 5, 0),
    (10, 8, 8, 9, 3),
    (10, 9, 13, 15, 8),
    (10, 10, 18, 20, 13),
    (10, 11, 23, 26, 18),
    (11, 6, 1, 5, 0),
    (11, 7, 7, 7, 1),
    (11, 8, 12, 14, 7),
    (11, 9, 18, 20, 12),
    (11, 10, 23, 27, 18),
    (11, 11, 29, 33, 23),
)

# Equality witness for the completed split (9, 9): |E|=9, |O|=8.
# Outside f is identically 5, so every legal one-point completion has
# pair product 4+5=9=need. E is explicit. O is rebuilt by greedy_odd.
WITNESS_EVEN = (0, 3, 5, 9, 10, 33, 34, 40, 43)
WITNESS_ODD = (1, 4, 16, 21, 64, 69, 81, 84)

# Checksum of every n=7 survivor row with 0<=s<=64 and 1<=t<=64.
# A changed rounding rule or domain moves this value.
FULL_RECTANGLE_CHECKSUM = 7722612959244201139
FULL_RECTANGLE_SURVIVORS = 3820


class CheckFailure(Exception):
    """Explicit failure. Raised under -O as well as ordinary execution."""


def require(condition, message):
    if not condition:
        raise CheckFailure(message)


def popcount(value):
    return value.bit_count()


def even_odd(dimension):
    limit = 1 << dimension
    evens = tuple(x for x in range(limit) if popcount(x) % 2 == 0)
    odds = tuple(x for x in range(limit) if popcount(x) % 2 == 1)
    return evens, odds


def pair_counts(points):
    counts = Counter()
    for index, left in enumerate(points):
        for right in points[index + 1:]:
            counts[left ^ right] += 1
    return counts


def product_sum(even_points, odd_points):
    even_counts = pair_counts(even_points)
    odd_counts = pair_counts(odd_points)
    total = 0
    for mask, count in even_counts.items():
        total += count * odd_counts[mask]
    return total, even_counts


def cross_pair_collisions(even_points, odd_points):
    occupancy = Counter(left ^ right for left in even_points for right in odd_points)
    return sum(count * (count - 1) // 2 for count in occupancy.values())


def link_values(even_counts, odd_points, odd_universe):
    """f(p) = sum_{q in O} A_{p xor q}, for every odd universe point."""
    values = {}
    for point in odd_universe:
        total = 0
        for other in odd_points:
            total += even_counts[point ^ other]
        values[point] = total
    return values


def square_minimum(total, bins):
    """Minimum of sum r_i^2 for nonnegative integers summing to total."""
    quotient, remainder = divmod(total, bins)
    return remainder * (quotient + 1) * (quotient + 1) + (bins - remainder) * quotient * quotient


def integer_s_min(even_size, odd_size, half_dimension):
    """Ceil of (min sum r^2 - N) / 4. Valid even when the flat vector is not a legal S."""
    occupied = even_size * odd_size
    gap = square_minimum(occupied, half_dimension) - occupied
    require(gap >= 0, "sum of squares dropped below the occupation count")
    return (gap + 3) // 4


def basic_rows(even_size, odd_size, half_dimension):
    budget = comb(even_size, 2) + comb(odd_size, 2) - (half_dimension - 1)
    product = even_size * odd_size
    if product < half_dimension or budget < 0:
        return None
    need = (product - half_dimension + 1) // 2
    largest_product = (budget // 2) * ((budget + 1) // 2)
    if budget + largest_product < need:
        return None
    return budget, need


def one_point_bound(even_size, completed_odd, half_dimension, rounding):
    """Lower bound on max_p (S + f(p)) for |O| = completed_odd - 1.

    Returns None when no partial state can have a nonnegative outside sum.
    rounding is "ceil" for the theorem and "floor" for the failure control.
    """
    require(rounding in ("ceil", "floor"), "unknown rounding " + rounding)
    require(1 <= completed_odd <= half_dimension, "odd side is outside the coset")
    missing = completed_odd - 1
    outside = half_dimension - missing
    alpha = missing * comb(even_size, 2)
    smallest = integer_s_min(even_size, missing, half_dimension)
    largest_nonnegative = alpha // 2
    if smallest > largest_nonnegative:
        return None
    if outside >= 2:
        slack = alpha - 2 * smallest
        if rounding == "ceil":
            lift = (slack + outside - 1) // outside
        else:
            lift = slack // outside
        return smallest + lift, smallest, outside
    # One admissible completion point: its f equals the whole outside sum,
    # so the product is alpha - S and the weakest value uses the largest
    # conceivable S. The sum-of-squares maximum is one bin holding every cross pair.
    occupied = even_size * missing
    square_cap = (occupied * occupied - occupied) // 4
    cap = min(largest_nonnegative, square_cap)
    require(cap >= smallest, "square upper bound fell below S_min")
    # Floor versus ceil does not apply: f is exact. Both modes return alpha - cap.
    return alpha - cap, smallest, outside


def survivor_rows(dimension, part_limit, rounding):
    half = 1 << (dimension - 1)
    rows = []
    for even_size in range(part_limit + 1):
        for odd_size in range(1, part_limit + 1):
            basic = basic_rows(even_size, odd_size, half)
            if basic is None:
                continue
            bound = one_point_bound(even_size, odd_size, half, rounding)
            if bound is None:
                continue
            height, smallest, _outside = bound
            rows.append((even_size, odd_size, basic[1], height, smallest))
    return tuple(rows)


def rectangle_checksum(dimension, rounding):
    half = 1 << (dimension - 1)
    rows = survivor_rows(dimension, half, rounding)
    digest = 0
    for even_size, odd_size, need, height, smallest in rows:
        require(height >= need, "one-point bound fell below need at (%d,%d)" % (even_size, odd_size))
        digest = (digest * 1000003 + even_size * 1009 + odd_size * 17 + height + smallest) % (1 << 63)
    return len(rows), digest


def ceil_drop_at_most_one():
    """For M>=2 and T>=2, ceil(T/M) - ceil((T-2)/M) is 0 or 1.

    The difference depends on T mod M, so one full set of residues is a proof
    for every M that occurs at n<=7.
    """
    for outside in range(2, 65):
        for slack in range(2, outside + 3):
            current = (slack + outside - 1) // outside
            dropped = (slack - 2 + outside - 1) // outside
            gap = current - dropped
            require(0 <= gap <= 1, "ceil drop %d at T=%d M=%d" % (gap, slack, outside))


def check_math_input():
    manifest = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = None
    for row in manifest["files"]:
        if row["path"] == MATH and row["usage"] == "input":
            pinned = row["sha256"]
    require(pinned is not None, "MATH.md input pin missing from SOURCES.json")
    text = (ROOT / MATH).read_text(encoding="utf-8")
    require(sha256(text.encode("utf-8")).hexdigest() == pinned, "MATH.md sha256 does not match SOURCES.json")
    require("sum_y C(r_y,2) = 2 * sum_x A_x*B_x." in text, "pair identity line missing from MATH.md")
    require("sum_x A_x*B_x >= ceil((s*t-Q)/2) =: need." in text, "need definition missing from MATH.md")
    require("canonical word 01021323" in text, "01021323 fixture missing from MATH.md")
    return text


def check_word_fixture():
    dimension = 4
    state = 0
    seen = [state]
    for label in (0, 1, 0, 2, 1, 3, 2, 3):
        state ^= 1 << label
        seen.append(state)
    require(seen == [0, 1, 3, 2, 6, 4, 12, 8, 0], "01021323 prefix walk changed")
    points = set(seen)
    require(points == {0, 1, 2, 3, 4, 6, 8, 12}, "01021323 prefix set changed")
    even = sum(popcount(point) % 2 == 0 for point in points)
    odd = len(points) - even
    require((even, odd) == (4, 4), "weight split is not (4,4)")
    low_bit = sum(point & 1 for point in points)
    require((len(points) - low_bit, low_bit) == (6, 2), "bit-0 split is not (6,2)")
    half = 1 << (dimension - 1)
    balanced = comb(4, 2) + comb(4, 2) - (half - 1)
    actual_bit = comb(6, 2) + comb(2, 2) - (half - 1)
    require(balanced == 5 and actual_bit == 9, "documented budgets 5 and 9 were not recomputed")
    coverage = {left ^ right for left in points for right in points}
    require(coverage == set(range(1 << dimension)), "01021323 does not cover every mask")
    # The old prune compares bit-0 excess 8 with the balanced budget 5.
    kernel = [point for point in points if (point & 1) == 0]
    coset = [point for point in points if (point & 1) == 1]
    require((len(kernel), len(coset)) == (6, 2), "bit-0 classes drifted")
    kernel_pairs = pair_counts(kernel)
    coset_pairs = pair_counts(coset)
    bit_excess = (comb(6, 2) - len(kernel_pairs)) + (comb(2, 2) - len(coset_pairs))
    require(bit_excess == 8, "bit-0 collision excess is not 8")


def check_witness():
    dimension = 7
    _evens, odds = even_odd(dimension)
    even_points = list(WITNESS_EVEN)
    require(len(even_points) == len(set(even_points)) == 9, "witness even set is not 9 distinct points")
    require(all(popcount(point) % 2 == 0 and 0 <= point < 128 for point in even_points),
            "witness even set leaves the even coset")
    rebuilt = greedy_odd(even_points, 8)
    require(tuple(sorted(rebuilt)) == tuple(sorted(WITNESS_ODD)),
            "greedy odd extension did not rebuild the pinned witness")
    odd_points = list(rebuilt)
    require(all(popcount(point) % 2 == 1 for point in odd_points), "greedy left the odd coset")
    product, even_counts = product_sum(even_points, odd_points)
    values = link_values(even_counts, odd_points, odds)
    odd_set = set(odd_points)
    outside = [values[point] for point in odds if point not in odd_set]
    alpha = len(odd_points) * comb(len(even_points), 2)
    require(product == 4, "witness pair product is not 4")
    require(outside and min(outside) == max(outside) == 5, "witness outside f is not identically 5")
    require(sum(values.values()) == alpha, "sum of f over the odd coset is not |O|*C(|E|,2)")
    require(sum(values[point] for point in odd_points) == 2 * product, "sum of f over O is not 2S")
    require(cross_pair_collisions(even_points, odd_points) == 2 * product,
            "sum C(r_y,2) is not 2S on the witness")
    # Every one-point completion, recomputed from the enlarged odd set.
    for point in odds:
        if point in odd_set:
            continue
        enlarged, _counts = product_sum(even_points, odd_points + [point])
        require(enlarged == product + values[point] == 9,
                "completion product drifted at %d" % point)
    half = 1 << (dimension - 1)
    basic = basic_rows(9, 9, half)
    require(basic is not None and basic[1] == 9, "(9,9) need is not 9")
    bound = one_point_bound(9, 9, half, "ceil")
    require(bound is not None and bound[0] == 9 and bound[1] == 4, "(9,9) arithmetic bound is not 9")


def greedy_odd(even_points, target):
    """Increasing odd pool. Keep a candidate only on a strict improvement of (S, max f, index)."""
    _evens, odds = even_odd(7)
    chosen = []
    chosen_set = set()
    while len(chosen) < target:
        best = None
        best_key = None
        for point in odds:
            if point in chosen_set:
                continue
            trial = chosen + [point]
            product, even_counts = product_sum(even_points, trial)
            values = link_values(even_counts, trial, odds)
            present = set(trial)
            outside = [values[candidate] for candidate in odds if candidate not in present]
            peak = max(outside) if outside else 0
            key = (product, peak, point)
            if best_key is None or key < best_key:
                best_key = key
                best = point
        require(best is not None, "greedy found no odd candidate")
        chosen.append(best)
        chosen_set.add(best)
    return chosen


def exhaustive_small(dimension):
    """Every even/odd subset pair: pair identity, f-sums, and the averaging step."""
    half = 1 << (dimension - 1)
    evens, odds = even_odd(dimension)
    require(len(evens) == len(odds) == half, "coset split is not equal")
    subset_count = 1 << half
    for even_mask in range(subset_count):
        even_points = [evens[index] for index in range(half) if even_mask >> index & 1]
        even_counts = pair_counts(even_points)
        even_pairs = len(even_points) * (len(even_points) - 1) // 2
        for odd_mask in range(subset_count):
            odd_points = [odds[index] for index in range(half) if odd_mask >> index & 1]
            odd_counts = pair_counts(odd_points)
            product = sum(count * odd_counts[mask] for mask, count in even_counts.items())
            require(cross_pair_collisions(even_points, odd_points) == 2 * product,
                    "pair identity failed on n=%d" % dimension)
            values = link_values(even_counts, odd_points, odds)
            alpha = len(odd_points) * even_pairs
            require(sum(values.values()) == alpha, "coset sum of f failed")
            require(sum(values[point] for point in odd_points) == 2 * product, "inside sum of f failed")
            outside_points = [point for point in odds if point not in set(odd_points)]
            if not outside_points:
                continue
            outside_sum = alpha - 2 * product
            require(outside_sum == sum(values[point] for point in outside_points), "outside sum split failed")
            if outside_sum < 0:
                continue
            peak = max(values[point] for point in outside_points)
            require(peak >= (outside_sum + len(outside_points) - 1) // len(outside_points),
                    "averaging lower bound failed")
            # One fresh completion, the smallest outside point, recomputed from pairs.
            point = outside_points[0]
            enlarged, _counts = product_sum(even_points, odd_points + [point])
            require(enlarged == product + values[point], "completion increment failed")


def check_parts_and_rectangle():
    ceil_rows = survivor_rows(7, 11, "ceil")
    require(ceil_rows == FROZEN_PARTS_AT_MOST_11, "parts<=11 survivor table changed: %s" % (ceil_rows,))
    for even_size, odd_size, need, height, _smallest in ceil_rows:
        require(height >= need, "frozen row (%d,%d) has h < need" % (even_size, odd_size))
    # (8,9) and (9,8) are the length-20 basic-identity exclusions. They are not in the table.
    half = 64
    require(basic_rows(8, 9, half) is None and basic_rows(9, 8, half) is None,
            "(8,9) survived the basic identity")
    budget = comb(8, 2) + comb(9, 2) - 63
    require(budget == 1 and (8 * 9 - 64 + 1) // 2 == 4, "(8,9) budget/need drifted")
    count, digest = rectangle_checksum(7, "ceil")
    require(count == FULL_RECTANGLE_SURVIVORS, "survivor count %d" % count)
    require(digest == FULL_RECTANGLE_CHECKSUM, "rectangle checksum %d" % digest)
    # Same closed form on the smaller cubes, still only the arithmetic certificate.
    for dimension in (3, 4, 5, 6):
        small_count, _small_digest = rectangle_checksum(dimension, "ceil")
        require(small_count > 0, "no survivors at n=%d" % dimension)


def check_floor_control_is_real():
    """The theorem uses ceil. Floor drops (7,11) and (11,7) strictly below need."""
    floors = { (row[0], row[1]): row for row in survivor_rows(7, 11, "floor") }
    dropped = sorted(key for key, row in floors.items() if row[3] < row[2])
    require(dropped == [(7, 11), (11, 7)], "floor mutation did not fail exactly the two sharp rows")
    require(floors[(9, 9)][3] == 9, "exact division at (9,9) should be stable under floor")


def main():
    check_math_input()
    check_word_fixture()
    ceil_drop_at_most_one()
    check_witness()
    exhaustive_small(3)
    exhaustive_small(4)
    check_parts_and_rectangle()
    check_floor_control_is_real()
    print(MARKER)


if __name__ == "__main__":
    main()
