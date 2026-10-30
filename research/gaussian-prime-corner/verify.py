#!/usr/bin/env python3
"""A prime-scale truncated Gaussian keeps its separator corner positive."""

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
NEUMANN_TERMS = 7
GAMMA_SCALE = 10**80
DISTANCE_ONE_SCALE = 10**40
DISTANCE_TWO_SCALE = 10**80


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
    assert value < terms + 1
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


def matmul(left, right):
    size = len(left)
    return [
        [
            sum((left[row][mid] * right[mid][column] for mid in range(size)), Interval(0))
            for column in range(size)
        ]
        for row in range(size)
    ]


def interior_inverse_entry(distance_one, distance_two, norm):
    size = len(INTERIOR)
    factor = [[Interval(0) for _ in range(size)] for _ in range(size)]
    for row in range(size):
        for column in range(size):
            distance = abs(row - column)
            if distance == 1:
                factor[row][column] = distance_one
            elif distance == 2:
                factor[row][column] = distance_two
    power = [[Interval(int(row == column)) for column in range(size)] for row in range(size)]
    total = [[Interval(int(row == column)) for column in range(size)] for row in range(size)]
    sign = -1
    for _ in range(NEUMANN_TERMS):
        power = matmul(power, factor)
        step = power if sign > 0 else [[-entry for entry in row] for row in power]
        total = [
            [total[row][column] + step[row][column] for column in range(size)]
            for row in range(size)
        ]
        sign = -sign
    remainder = norm ** (NEUMANN_TERMS + 1) / (1 - norm)
    return total[0][3] + Interval(-remainder, remainder)


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
    assert "Interior neighbors are separated by W" in gaussian
    assert "bandwidth O(W) in boundary order" in gaussian
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
    gamma_floor = Fraction(math.floor(gamma_low * GAMMA_SCALE), GAMMA_SCALE)
    gamma_ceil = Fraction(math.ceil(gamma_high * GAMMA_SCALE), GAMMA_SCALE)
    assert gamma_floor < gamma_low <= gamma_high < gamma_ceil
    delta = gamma_ceil - gamma_floor
    assert delta < Fraction(1, 8)
    exp_low, exp_high = exp_bounds(gamma_floor, 180)
    tail_low, tail_high = exp_bounds(4 * gamma_floor, 360)
    distance_one = snap_outward(
        1 / (exp_high * (1 + 2 * delta)),
        1 / exp_low,
        DISTANCE_ONE_SCALE,
    )
    distance_two = snap_outward(
        1 / (tail_high * (1 + 8 * delta)),
        1 / tail_low,
        DISTANCE_TWO_SCALE,
    )
    assert distance_one.low > 0 and distance_two.low > 0
    norm = 2 * distance_one.high + distance_two.high
    assert norm < Fraction(1, 10**11)
    assert 2 * distance_one.high + 2 * distance_two.high < Fraction(1, 10**11)

    assert INTERIOR[0] == 3 and INTERIOR[3] == 6
    assert [vertex for vertex in range(SIZE) if vertex not in INTERIOR] == list(KEEP)
    assert abs(1 - 3) == WIDTH and abs(8 - 6) == WIDTH
    assert [vertex for vertex in INTERIOR if 0 < abs(1 - vertex) <= WIDTH] == [3]
    assert [vertex for vertex in INTERIOR if 0 < abs(8 - vertex) <= WIDTH] == [6]
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
        assert abs(left - right) > WIDTH
        assert not any(0 < abs(left - vertex) <= WIDTH for vertex in INTERIOR) or not any(
            0 < abs(right - vertex) <= WIDTH for vertex in INTERIOR
        )
    entry = interior_inverse_entry(distance_one, distance_two, norm)
    corner = -distance_two * entry * distance_two
    assert Fraction(1, 10**136) < corner.low and corner.high < Fraction(1, 10**135)
    assert order[8] - order[1] == 2 * WIDTH - 1


if __name__ == "__main__":
    main()
