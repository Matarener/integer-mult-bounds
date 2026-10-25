#!/usr/bin/env python3
"""A centred prime-scale chirp keeps both corners positive, with a row sum above 1."""

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
    return (Fraction(vertex) - Fraction(9, 2)) ** 2


def chirp_ratio(row, column, pi_low, pi_high):
    diff = t_square(row) - t_square(column)
    if diff == 0:
        return Interval(1)
    value = exp_of_pi(abs(diff) * 9 / 1444, pi_low, pi_high, 40)
    if diff > 0:
        return value
    return Interval(1) / value


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
    assert "Interior neighbors are separated by W" in gaussian
    assert "bandwidth O(W) in boundary order" in gaussian
    assert "log N_{ij} = -a rho h^2 - 2 a beta0 h + a theta (t_i^2 - t_j^2)" in gauge
    assert "e^{a theta t_i^2} k(j-i) e^{-a theta t_j^2}" in gauge
    assert "B^2/4 (centred)" in gauge
    assert "gamma = a rho, s = -beta0/rho" in gauge
    assert "|s| <= 1/(2 rho)" in gauge
    assert "1 - 2|s| >= 1 - 1/rho = theta/rho >= theta/2" in gauge
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
    assert rho / 1445 == Fraction(1, 1444)
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
    assert t_square(1) == t_square(8) == Fraction(49, 4)
    assert t_square(0) - t_square(1) == 8
    assert Fraction(7 * 9, 1444) == Fraction(63, 1444)
    assert Fraction(2 * 9, 1444) == Fraction(9, 722)

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
        step: negative_exponential(exponents[step], gamma_low, gamma_high)
        for step in (1, -1, 2, -2)
    }
    heavy = exp_of_pi(Fraction(63, 1444), pi_low, pi_high, 40)
    two_a_theta = exp_of_pi(Fraction(9, 722), pi_low, pi_high, 40)
    two_a = exp_of_pi(Fraction(18), pi_low, pi_high, 220)
    assert heavy.low > 1
    assert two_a_theta.low > Fraction(100, 99)
    assert two_a.low > 500
    assert 1 / two_a_theta.low + 5 / two_a.low < 1
    distance_two = chirp_ratio(0, 2, pi_low, pi_high) * weights[2]
    assert distance_two.low > 0

    size = len(INTERIOR)
    interior = [[Interval(0) for _ in range(size)] for _ in range(size)]
    for row in range(size):
        for column in range(size):
            step = column - row
            if step == 0:
                interior[row][column] = Interval(1)
            elif step in weights:
                ratio = chirp_ratio(INTERIOR[row], INTERIOR[column], pi_low, pi_high)
                interior[row][column] = ratio * weights[step]
    inverse = invert(interior)
    assert inverse[0][3].high < 0 and inverse[3][0].high < 0
    forward = (
        -chirp_ratio(1, 3, pi_low, pi_high)
        * weights[2]
        * inverse[0][3]
        * chirp_ratio(6, 8, pi_low, pi_high)
        * weights[2]
    )
    reverse = (
        -chirp_ratio(8, 6, pi_low, pi_high)
        * weights[-2]
        * inverse[3][0]
        * chirp_ratio(3, 1, pi_low, pi_high)
        * weights[-2]
    )
    assert Fraction(1, 10**50) < forward.low and forward.high < Fraction(1, 10**49)
    assert Fraction(1, 10**222) < reverse.low and reverse.high < Fraction(1, 10**221)
    assert forward.low > reverse.high

    assert INTERIOR[0] == 3 and INTERIOR[3] == 6
    assert [vertex for vertex in range(SIZE) if vertex not in INTERIOR] == list(KEEP)
    assert [vertex for vertex in INTERIOR if 0 < abs(1 - vertex) <= WIDTH] == [3]
    assert [vertex for vertex in INTERIOR if 0 < abs(8 - vertex) <= WIDTH] == [6]
    assert not any(0 < abs(0 - vertex) <= WIDTH for vertex in INTERIOR)
    assert 3 - 1 == 2 and 8 - 6 == 2 and 6 - 8 == -2 and 1 - 3 == -2
    order = {vertex: index for index, vertex in enumerate(KEEP)}
    far_pairs = [
        (left, right)
        for left_index, left in enumerate(KEEP)
        for right in KEEP[left_index + 1 :]
        if order[right] - order[left] > WIDTH
    ]
    assert far_pairs == [(0, 7), (0, 8), (0, 9), (1, 8), (1, 9), (2, 9)]
    for left, right in far_pairs:
        if (left, right) == (1, 8):
            continue
        assert not any(0 < abs(left - vertex) <= WIDTH for vertex in INTERIOR) or not any(
            0 < abs(right - vertex) <= WIDTH for vertex in INTERIOR
        )
    assert order[8] - order[1] == 2 * WIDTH - 1


if __name__ == "__main__":
    main()
