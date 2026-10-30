#!/usr/bin/env python3
"""Translating the prime-scale origin puts every row sum below 97/100."""

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
EXPONENT_SCALE = 10**40
VALUE_SCALE = 10**40


class Interval:
    def __init__(self, low, high=None):
        if high is None:
            high = low
        low, high = Fraction(low), Fraction(high)
        if low > high:
            low, high = high, low
        self.low = low
        self.high = high


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


def exp_of_pi(coefficient, pi_low, pi_high, terms):
    low = coefficient * pi_low
    high = coefficient * pi_high
    snapped = snap_outward(low, high, EXPONENT_SCALE)
    assert snapped.low <= low <= high <= snapped.high
    delta = snapped.high - snapped.low
    assert 0 <= delta < Fraction(1, 8)
    series_low, series_high = exp_bounds(snapped.low, terms)
    enclosed_high = series_high * (1 + 2 * delta)
    weight = snap_outward(series_low, enclosed_high, VALUE_SCALE)
    assert weight.low > 0
    assert weight.low <= series_low <= enclosed_high <= weight.high
    return weight


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
    assert len(counts) == SIZE
    assert counts[0] == (1, 1) and counts[9] == (0, 2)
    assert smallest_other == Fraction(6462, 361)
    assert -log_over_a_theta(0, 1) * Fraction(9, 1444) == Fraction(9, 722)

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
    heavy = exp_of_pi(Fraction(9, 722), pi_low, pi_high, 40)
    other = exp_of_pi(smallest_other, pi_low, pi_high, 220)
    assert heavy.low > Fraction(200, 193)
    assert other.low > 3000
    heavy_upper = 1 / heavy.low
    other_upper = 1 / other.low
    assert heavy_upper < Fraction(193, 200)
    assert 3 * other_upper < Fraction(1, 1000)
    assert Fraction(193, 200) + Fraction(1, 1000) < Fraction(97, 100)
    for index, (heavy_count, other_count) in enumerate(counts):
        assert heavy_count * heavy_upper + other_count * other_upper < Fraction(97, 100)
        if index == 9:
            assert other_count * other_upper < Fraction(1, 1000)


if __name__ == "__main__":
    main()
