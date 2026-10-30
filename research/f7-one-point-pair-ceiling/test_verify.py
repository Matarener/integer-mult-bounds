#!/usr/bin/env python3
"""Failure controls for the one-point pair ceiling. Explicit exceptions, not assert."""

import importlib.util
from pathlib import Path


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("one_point_ceiling", HERE / "verify.py")
ceiling = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ceiling)

MARKER = "PASS_F7_ONE_POINT_PAIR_CEILING_CONTROLS"


def require(condition, message):
    if not condition:
        raise ceiling.CheckFailure(message)


def hand_arithmetic():
    """Literals only, so a bug copied into verify.py is not the sole source."""
    # (9, 9), one odd point missing.
    need = (81 - 64 + 1) // 2
    require(need == 9, "(9,9) need")
    # N=9*8=72 over 64 bins: eight 2s and fifty-six 1s.
    sum_squares = 8 * 4 + 56 * 1
    smallest = (sum_squares - 72 + 3) // 4
    require(sum_squares == 88 and smallest == 4, "(9,9) flattening")
    height = smallest + (8 * 36 - 2 * smallest + 56 - 1) // 56
    require(height == 9, "(9,9) ceiling")
    # (7, 11). Floor loses the integer lift; ceil meets need.
    need_711 = (77 - 64 + 1) // 2
    require(need_711 == 7, "(7,11) need")
    # |O|=10, N=70 = 64+6: six 2s and fifty-eight 1s.
    sum_squares = 6 * 4 + 58 * 1
    smallest = (sum_squares - 70) // 4
    require(sum_squares == 82 and smallest == 3, "(7,11) flattening")
    slack = 10 * 21 - 2 * smallest
    require(slack == 204, "(7,11) outside sum")
    ceil_lift = (slack + 54 - 1) // 54
    floor_lift = slack // 54
    require(ceil_lift == 4 and smallest + ceil_lift == 7, "(7,11) ceil bound")
    require(floor_lift == 3 and smallest + floor_lift == 6, "(7,11) floor bound falls below need")


def corrupted_witness():
    even_points = list(ceiling.WITNESS_EVEN)
    odds = [point for point in range(128) if point.bit_count() % 2 == 1]
    odd_points = [point for point in ceiling.WITNESS_ODD if point != 84] + [2]
    require(2 not in ceiling.WITNESS_ODD and 2 in odds, "edit point 2 is not a fresh odd point")
    product, even_counts = ceiling.product_sum(even_points, odd_points)
    values = ceiling.link_values(even_counts, odd_points, odds)
    present = set(odd_points)
    peak = max(values[point] for point in odds if point not in present)
    require(product + peak != 9, "replacing 84 by 2 still met the (9,9) equality")


def direct_completion():
    """S + f(p) equals the pair product of the enlarged set, on a 3-point example."""
    even_points = [0, 3]
    odd_points = [1]
    added = 2
    product, even_counts = ceiling.product_sum(even_points, odd_points)
    odds = [point for point in range(128) if point.bit_count() % 2 == 1]
    values = ceiling.link_values(even_counts, odd_points, odds)
    enlarged, _counts = ceiling.product_sum(even_points, odd_points + [added])
    require(product == 0 and values[added] == 1 and enlarged == 1,
            "three-point completion did not increase the product by f(p)")


def floor_rows_match_the_hand_calculation():
    floors = {(row[0], row[1]): row for row in ceiling.survivor_rows(7, 11, "floor")}
    require(floors[(7, 11)][3] == 6 and floors[(7, 11)][2] == 7, "module floor row drifted")
    require(floors[(11, 7)][3] < floors[(11, 7)][2], "(11,7) floor row still meets need")
    require(ceiling.basic_rows(8, 9, 64) is None, "(8,9) was treated as a survivor")


def main():
    hand_arithmetic()
    corrupted_witness()
    direct_completion()
    floor_rows_match_the_hand_calculation()
    print(MARKER)


if __name__ == "__main__":
    main()
