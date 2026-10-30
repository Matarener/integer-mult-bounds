#!/usr/bin/env python3
"""The normalized translated Schur row sums are strictly below 2."""

from fractions import Fraction
import hashlib
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GAUSSIAN = ROOT / "research/unconditional-batched-crt/GAUSSIAN.md"
GAUGE = ROOT / "research/unconditional-batched-crt/vendor/GAUGEFREE-INTERIORS.md"
FINE = ROOT / "research/unconditional-batched-crt/vendor/FINE-PRIME.md"
GAUSSIAN_SHA = "2f63c91c58f2d1cf31294812c75970ea390c61866a8da7ed700d4316a033a242"
GAUGE_SHA = "d1423ac0ea0003521797209f4396e6981a66994bbee4f8b48026e5b95f8c5116"
FINE_SHA = "47d1b1b4df28aadda3cd6bdeb1fbc47290595e9208cd09c1a1f338520d33fdce"
PRIME = 19
WIDTH = 2
SIZE = 10
INTERIOR = (3, 4, 5, 6)
KEEP = (0, 1, 2, 7, 8, 9)
EXPONENT_SCALE = 10**40
WEIGHT_SCALE = 10**120
CHIRP_SCALE = 10**40
CORRECTION_BOUNDS = {
    1: (Fraction(1, 10**99), Fraction(1, 10**98)),
    8: (Fraction(1, 10**99), Fraction(1, 10**98)),
    2: (Fraction(1, 10**25), Fraction(1, 10**24)),
    7: (Fraction(1, 10**25), Fraction(1, 10**24)),
}


class Interval:
    def __init__(self, low, high=None):
        if high is None:
            high = low
        low, high = Fraction(low), Fraction(high)
        if low > high:
            low, high = high, low
        self.low = low
        self.high = high

    def __add__(self, other):
        other = as_interval(other)
        return Interval(self.low + other.low, self.high + other.high)

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        other = as_interval(other)
        return Interval(self.low - other.high, self.high - other.low)

    def __neg__(self):
        return Interval(-self.high, -self.low)

    def __mul__(self, other):
        other = as_interval(other)
        values = (
            self.low * other.low,
            self.low * other.high,
            self.high * other.low,
            self.high * other.high,
        )
        return Interval(min(values), max(values))

    def __truediv__(self, other):
        other = as_interval(other)
        if other.low <= 0 <= other.high:
            raise ZeroDivisionError("interval contains zero")
        values = (
            self.low / other.low,
            self.low / other.high,
            self.high / other.low,
            self.high / other.high,
        )
        return Interval(min(values), max(values))

    def exact_zero(self):
        return self.low == 0 and self.high == 0


def as_interval(value):
    if isinstance(value, Interval):
        return value
    return Interval(value)


def alternating_bounds(first, ratio, terms):
    term = Fraction(first)
    total = Fraction(0)
    for _ in range(terms):
        total += term
        nxt = ratio(term)
        assert abs(nxt) < abs(term)
        term = nxt
    if term < 0:
        return total + term, total
    return total, total + term


def atan_bounds(value, terms):
    value = Fraction(value)
    square = value * value

    def ratio(term, index=[0]):
        step = index[0]
        index[0] += 1
        return -term * square * (2 * step + 1) / (2 * step + 3)

    return alternating_bounds(value, ratio, terms)


def log_two_bounds(terms):
    term = Fraction(2, 3)
    total = Fraction(0)
    for index in range(terms):
        total += term
        nxt = term * Fraction(1, 9) * Fraction(2 * index + 1, 2 * index + 3)
        assert nxt * 9 < term
        term = nxt
    return total, total + term * Fraction(9, 8)


def log_nineteen_over_sixteen(terms):
    slope = Fraction(3, 16)

    def ratio(term, index=[1]):
        step = index[0]
        index[0] += 1
        return -term * slope * step / (step + 1)

    return alternating_bounds(slope, ratio, terms)


def exp_bounds(value, terms):
    value = Fraction(value)
    assert 0 <= value < terms + 1
    term = Fraction(1)
    total = Fraction(0)
    for index in range(terms):
        total += term
        term *= value / (index + 1)
    return total, total + term / (1 - value / (terms + 1))


def snap_outward(low, high, scale):
    return Interval(
        Fraction(math.floor(low * scale), scale),
        Fraction(math.ceil(high * scale), scale),
    )


def term_count(factor):
    if factor < 1:
        return 40
    if factor < 3:
        return 220
    return 420


def negative_exponential(factor, gamma_low, gamma_high):
    low = factor * gamma_low
    high = factor * gamma_high
    snapped = snap_outward(low, high, EXPONENT_SCALE)
    assert snapped.low <= low <= high <= snapped.high
    delta = snapped.high - snapped.low
    assert 0 <= delta < Fraction(1, 8)
    exp_low, exp_high = exp_bounds(snapped.low, term_count(factor))
    enclosed_low = 1 / (exp_high * (1 + 2 * delta))
    enclosed_high = 1 / exp_low
    weight = snap_outward(enclosed_low, enclosed_high, WEIGHT_SCALE)
    assert weight.low > 0
    assert weight.low <= enclosed_low <= enclosed_high <= weight.high
    return weight


def exp_of_pi(coefficient, pi_low, pi_high, terms):
    low = coefficient * pi_low
    high = coefficient * pi_high
    snapped = snap_outward(low, high, EXPONENT_SCALE)
    assert snapped.low <= low <= high <= snapped.high
    delta = snapped.high - snapped.low
    assert 0 <= delta < Fraction(1, 8)
    series_low, series_high = exp_bounds(snapped.low, terms)
    enclosed_high = series_high * (1 + 2 * delta)
    weight = snap_outward(series_low, enclosed_high, CHIRP_SCALE)
    assert weight.low > 0
    assert weight.low <= series_low <= enclosed_high <= weight.high
    return weight


def t_square(vertex):
    return Fraction(vertex) ** 2


def invert(matrix):
    size = len(matrix)
    work = [
        row[:] + [Interval(int(row_index == column)) for column in range(size)]
        for row_index, row in enumerate(matrix)
    ]
    for column in range(size):
        pivot_row = max(
            range(column, size),
            key=lambda row: abs(work[row][column].low + work[row][column].high),
        )
        work[column], work[pivot_row] = work[pivot_row], work[column]
        scale = work[column][column]
        assert scale.low > 0
        work[column] = [entry / scale for entry in work[column]]
        for row in range(size):
            if row == column:
                continue
            factor = work[row][column]
            if factor.exact_zero():
                continue
            work[row] = [
                work[row][index] - factor * work[column][index] for index in range(2 * size)
            ]
    return [row[size:] for row in work]


def matmul(left, right):
    rows = len(left)
    cols = len(right[0])
    mid = len(right)
    return [
        [
            sum((left[row][index] * right[index][column] for index in range(mid)), Interval(0))
            for column in range(cols)
        ]
        for row in range(rows)
    ]


def magnitude_upper(entry):
    if entry.low > 0:
        return entry.high
    if entry.high < 0:
        return -entry.low
    return max(-entry.low, entry.high)


def main():
    assert hashlib.sha256(GAUSSIAN.read_bytes()).hexdigest() == GAUSSIAN_SHA
    assert hashlib.sha256(GAUGE.read_bytes()).hexdigest() == GAUGE_SHA
    assert hashlib.sha256(FINE.read_bytes()).hexdigest() == FINE_SHA
    gaussian = GAUSSIAN.read_text()
    gauge = GAUGE.read_text()
    fine = FINE.read_text()
    assert "theta=t/s-1 in [1/(4p^2),1/p^2], rho=1+theta" in gaussian
    assert "alpha=ceil(sqrt((4/pi)log(16p)))" in gaussian
    assert "a=pi alpha^2" in gaussian
    assert "Eventually 4log(16p)<=a<=5log(16p)" in gaussian
    assert "k(h)=exp(-a rho h^2-2a beta0 h)" in gaussian
    assert "|beta0/rho|<1/2" in gaussian
    assert "||N-I||_infinity <= exp(-2a theta)+5exp(-2a)" in gaussian
    assert "diagonal1" in gaussian
    assert "row gap delta>=1/(16p^2) and row norm<2" in gaussian
    assert "All principal restrictions retain the row gap" in gaussian
    assert "log N_{ij} = -a rho h^2 - 2 a beta0 h + a theta (t_i^2 - t_j^2)" in gauge
    assert "e^{a theta t_i^2} k(j-i) e^{-a theta t_j^2}" in gauge
    assert "gamma = a rho, s = -beta0/rho" in gauge
    assert "|s| <= 1/(2 rho)" in gauge
    assert "exp(-gamma u^2 + 2 gamma s u)" in gauge
    assert "has G'_s(0) = 1" in gauge
    assert "Scalar Schur bandwidth stays O(W)" in fine
    assert "two neighboring O(W)-size separators" in fine

    assert all(PRIME % divisor for divisor in range(2, PRIME))
    theta = Fraction(1, 4 * PRIME * PRIME)
    rho = 1 + theta
    assert theta == Fraction(1, 1444) and rho == Fraction(1445, 1444)
    shift = Fraction(1, 2) / rho
    beta0 = -shift * rho
    assert shift == Fraction(722, 1445) and beta0 == -Fraction(1, 2)
    assert abs(beta0) / rho == shift < Fraction(1, 2)
    assert 1 - 2 * shift == theta / rho == Fraction(1, 1445)
    assert Fraction(2 * 9, 1444) == Fraction(9, 722)
    assert t_square(0) == 0 and t_square(1) == 1 and t_square(8) == 64
    exponents = {
        1: 1 - 2 * shift,
        -1: 1 + 2 * shift,
        2: 4 - 4 * shift,
        -2: 4 + 4 * shift,
    }
    assert exponents[1] == Fraction(1, 1445)
    assert exponents[-1] == Fraction(2889, 1445)
    assert exponents[2] == Fraction(2892, 1445)
    assert exponents[-2] == Fraction(8668, 1445)

    def log_over_a_theta(vertex, step):
        neighbor = vertex + step
        kernel = step * step - 2 * shift * step
        return Fraction(vertex * vertex - neighbor * neighbor) - 1445 * kernel

    counts = []
    smallest_other = None
    for vertex in range(SIZE):
        heavy_count = 0
        other_count = 0
        for step in (1, -1, 2, -2):
            if not 0 <= vertex + step < SIZE:
                continue
            coefficient = -log_over_a_theta(vertex, step) * Fraction(9, 1444)
            assert coefficient > 0
            if step == 1:
                heavy_count += 1
                assert coefficient >= Fraction(9, 722)
            else:
                other_count += 1
                if smallest_other is None or coefficient < smallest_other:
                    smallest_other = coefficient
        assert heavy_count <= 1 and other_count <= 3
        counts.append((heavy_count, other_count))
    assert smallest_other == Fraction(6462, 361)
    assert Fraction(18) - smallest_other == Fraction(36, 361)
    assert -log_over_a_theta(0, 1) * Fraction(9, 1444) == Fraction(9, 722)
    assert [vertex for vertex in KEEP if not any(0 < abs(vertex - interior) <= WIDTH for interior in INTERIOR)] == [0, 9]

    log_two_low, log_two_high = log_two_bounds(40)
    log_ratio_low, log_ratio_high = log_nineteen_over_sixteen(20)
    log_low = 8 * log_two_low + log_ratio_low
    log_high = 8 * log_two_high + log_ratio_high
    atan_five_low, atan_five_high = atan_bounds(Fraction(1, 5), 60)
    atan_large_low, atan_large_high = atan_bounds(Fraction(1, 239), 20)
    pi_low = 16 * atan_five_low - 4 * atan_large_high
    pi_high = 16 * atan_five_high - 4 * atan_large_low
    assert pi_high < log_low < Fraction(9, 4) * pi_low
    assert 4 * log_high <= 9 * pi_low and 9 * pi_high <= 5 * log_low
    gamma_low = 9 * pi_low * rho
    gamma_high = 9 * pi_high * rho
    weights = {
        step: negative_exponential(exponents[step], gamma_low, gamma_high) for step in exponents
    }
    heavy = exp_of_pi(Fraction(9, 722), pi_low, pi_high, 40)
    other = exp_of_pi(smallest_other, pi_low, pi_high, 220)
    growth = exp_of_pi(Fraction(36, 361), pi_low, pi_high, 40)
    two_a = exp_of_pi(Fraction(18), pi_low, pi_high, 220)
    assert growth.high < Fraction(5, 3)
    heavy_upper = 1 / heavy.low
    other_upper = 1 / other.low
    displayed_lower = 1 / heavy.high + 5 / two_a.high
    assert 3 * other_upper < 5 / two_a.high
    majorants = []
    for heavy_count, other_count in counts:
        majorant = heavy_count * heavy_upper + other_count * other_upper
        assert majorant < displayed_lower
        majorants.append(majorant)

    def chirp_ratio(row, column):
        diff = t_square(row) - t_square(column)
        if diff == 0:
            return Interval(1)
        value = exp_of_pi(abs(diff) * 9 / 1444, pi_low, pi_high, 40)
        if diff > 0:
            return value
        return Interval(1) / value

    def entry(row, column):
        step = column - row
        if step == 0:
            return Interval(1)
        if step not in weights:
            return Interval(0)
        return chirp_ratio(row, column) * weights[step]

    def block(rows, columns):
        return [[entry(row, column) for column in columns] for row in rows]

    inverse = invert(block(INTERIOR, INTERIOR))
    boundary = block(KEEP, KEEP)
    correction = matmul(matmul(block(KEEP, INTERIOR), inverse), block(INTERIOR, KEEP))
    schur = [
        [boundary[row][column] - correction[row][column] for column in range(len(KEEP))]
        for row in range(len(KEEP))
    ]
    normalized = []
    for index, vertex in enumerate(KEEP):
        gap = correction[index][index]
        diagonal = Interval(1) - gap
        assert diagonal.low > 0 and diagonal.high <= 1
        if vertex in (0, 9):
            assert all(correction[index][column].exact_zero() for column in range(len(KEEP)))
            assert diagonal.low == 1 and diagonal.high == 1
            # The Schur row is the original width-2 row, and dividing by 1
            # leaves the exponent majorant in place.
            upper = majorants[vertex]
        else:
            lower, upper_gap = CORRECTION_BOUNDS[vertex]
            assert lower < gap.low and gap.high < upper_gap
            assert 1 - upper_gap < diagonal.low and diagonal.high < 1 - lower
            off_sum = sum(
                magnitude_upper(schur[index][column])
                for column in range(len(KEEP))
                if column != index
            )
            upper = off_sum / diagonal.low
        assert upper < displayed_lower
        normalized.append(upper)
    assert len(normalized) == 6
    target = Fraction(1, 16 * PRIME * PRIME)
    assert target == Fraction(1, 5776)
    assert displayed_lower < 1 - target
    for upper in normalized:
        assert 1 - upper > target
        assert 1 + upper < 2 - target


if __name__ == "__main__":
    main()
