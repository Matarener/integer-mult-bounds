"""Independent kernel-code census for binary five-dimensional pair sums.

Prepared by apoursh with substantial OpenAI Codex assistance. Apache-2.0.
The partitioned-walk model and question retain Li/Petalas predecessor credit;
this module checks the separate finite point-set extremum without walk code.
"""

from collections import Counter
from fractions import Fraction
from itertools import combinations
from math import comb, factorial, prod


def check(condition, message):
    if not condition:
        raise ValueError(message)


def compositions(total, parts):
    """Every weak composition once, via its unique separator positions."""
    for bars in combinations(range(total + parts - 1), parts - 1):
        ends = (-1,) + bars + (total + parts - 1,)
        yield tuple(ends[i + 1] - ends[i] - 1 for i in range(parts))


def gl_order(d):
    return prod((1 << d) - (1 << i) for i in range(d))


def kernel_census(n, d):
    """Count n-point nonzero full-span sets through their relation codes.

    If H lists their columns, C=ker(H) has dimension k=n-d. Distinct,
    nonzero columns mean C has no word of weight one or two. Pair sums of
    {0} union columns(H) are the cosets represented by errors of weight
    one or two. An ordered generator basis of C is a k-by-n binary matrix;
    coordinate permutations let us enumerate its column multiplicities.

    For multiplicities a, there are n!/prod(a!) coordinate orderings.
    Divide by |GL(k,2)| generator bases and multiply by |GL(d,2)| quotient
    identifications, then divide by n! column orderings. This gives weight
    |GL(d,2)|/(|GL(k,2)| prod(a!)) for the unordered point-set histogram.
    Individual weights can be fractional; every final histogram bin is not.
    """
    check((n, d) in {(7, 5), (8, 5), (3, 2), (4, 3), (5, 3), (6, 3)},
          "kernel census outside its declared bounded domains")
    k = n - d
    errors = [1 << i for i in range(n)]
    errors += [(1 << i) | (1 << j) for i, j in combinations(range(n), 2)]
    histogram = Counter()
    weighted = Counter()
    examined = 0
    for multiplicities in compositions(n, 1 << k):
        examined += 1
        columns = [x for x, count in enumerate(multiplicities)
                   for _ in range(count)]
        code = tuple(sum(((x & u).bit_count() % 2) << i
                         for i, x in enumerate(columns))
                     for u in range(1 << k))
        if len(set(code)) != 1 << k:
            continue
        if min(x.bit_count() for x in code[1:]) < 3:
            continue
        representatives = {min(error ^ word for word in code)
                           for error in errors}
        size = len(representatives)
        histogram[size] += 1
        denominator = gl_order(k) * prod(factorial(a) for a in multiplicities)
        weighted[size] += Fraction(gl_order(d), denominator)
    check(examined == comb(n + (1 << k) - 1, (1 << k) - 1),
          "weak-composition inventory incomplete")
    check(weighted and all(count.denominator == 1 for count in weighted.values()),
          "kernel orbit weights do not count integral point sets")
    return {
        "generator_multiplicities": examined,
        "admissible_multiplicities": sum(histogram.values()),
        "multiplicity_histogram": dict(sorted(histogram.items())),
        "point_set_histogram": {size: int(count)
                                for size, count in sorted(weighted.items())},
        "maximum": max(weighted),
    }


def literal_histogram(n, d):
    """Tiny calibration by every point subset, with no code or orbit weights."""
    check((n, d) in {(3, 2), (4, 3), (5, 3), (6, 3)},
          "literal calibration outside its declared bounded domains")
    histogram = Counter()
    examined = 0
    for points in combinations(range(1, 1 << d), n):
        examined += 1
        span = {0}
        for point in points:
            span = span | {v ^ point for v in span}
        if len(span) != 1 << d:
            continue
        differences = {x ^ y for x, y in combinations((0,) + points, 2)}
        histogram[len(differences)] += 1
    check(examined == comb((1 << d) - 1, n), "point inventory incomplete")
    return dict(sorted(histogram.items()))


def run_oracle():
    """Return corroboration; the package's analytic proof needs no census."""
    rows = {str(n + 1): kernel_census(n, 5) for n in (7, 8)}
    expected = {
        "8": {20: 833280, 22: 1180480, 25: 416640},
        "9": {21: 234360, 22: 267840, 23: 2812320,
              25: 1874880, 27: 1874880, 28: 624960},
    }
    for size, row in rows.items():
        check(row["point_set_histogram"] == expected[size],
              "kernel histogram differs at point-set size " + size)

    # A rank-four subspace has 15 nonzero points. At n=7, remove its
    # 15 rank-three sets, then count those 155 three-spaces separately.
    # At n=8 no smaller subspace can hold the nonzero points.
    totals = {"8": comb(31, 7) - 31 * (comb(15, 7) - 15) - 155,
              "9": comb(31, 8) - 31 * comb(15, 8)}
    for size, row in rows.items():
        check(sum(row["point_set_histogram"].values()) == totals[size],
              "full-span point-set total differs at size " + size)

    calibration = []
    for n, d in ((3, 2), (4, 3), (5, 3), (6, 3)):
        kernel = kernel_census(n, d)
        literal = literal_histogram(n, d)
        check(kernel["point_set_histogram"] == literal,
              f"independent literal calibration differs at n={n}, d={d}")
        calibration.append({"nonzero_points": n, "dimension": d,
                            "point_set_histogram": literal})
    return {"maxima": {size: row["maximum"] for size, row in rows.items()},
            "kernel_censuses": rows, "literal_calibrations": calibration}
