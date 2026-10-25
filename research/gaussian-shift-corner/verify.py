#!/usr/bin/env python3
"""A shifted truncated Gaussian keeps both separator corners positive."""

from fractions import Fraction
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GAUSSIAN = ROOT / "research/unconditional-batched-crt/GAUSSIAN.md"
GAUGE = ROOT / "research/unconditional-batched-crt/vendor/GAUGEFREE-INTERIORS.md"
FINE = ROOT / "research/unconditional-batched-crt/vendor/FINE-PRIME.md"
GAUSSIAN_SHA = "2f63c91c58f2d1cf31294812c75970ea390c61866a8da7ed700d4316a033a242"
GAUGE_SHA = "d1423ac0ea0003521797209f4396e6981a66994bbee4f8b48026e5b95f8c5116"
FINE_SHA = "47d1b1b4df28aadda3cd6bdeb1fbc47290595e9208cd09c1a1f338520d33fdce"
WIDTH = 2
SIZE = 10
INTERIOR = (3, 4, 5, 6)
SERIES_TERMS = 40
SHIFT = Fraction(1, 4)


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


def exp_neg(argument, terms):
    term = Fraction(1)
    total = Fraction(0)
    for index in range(terms):
        total += term
        term = -term * argument / (index + 1)
    if term > 0:
        return Interval(total, total + term)
    return Interval(total + term, total)


def invert(matrix):
    size = len(matrix)
    work = [row[:] + [Interval(int(i == j)) for j in range(size)]
            for i, row in enumerate(matrix)]
    for col in range(size):
        pivot = max(range(col, size),
                    key=lambda row: abs(work[row][col].low + work[row][col].high))
        scale = work[pivot][col]
        if scale.exact_zero() or scale.low <= 0 <= scale.high:
            raise ZeroDivisionError("singular")
        work[col], work[pivot] = work[pivot], work[col]
        work[col] = [entry / scale for entry in work[col]]
        for row in range(size):
            if row == col or work[row][col].exact_zero():
                continue
            factor = work[row][col]
            work[row] = [work[row][j] - factor * work[col][j] for j in range(2 * size)]
    return [row[size:] for row in work]


def kernel(step):
    exponent = step * step - SHIFT * 2 * step
    return exp_neg(exponent, SERIES_TERMS)


def host():
    matrix = [[Interval(0) for _ in range(SIZE)] for _ in range(SIZE)]
    for i in range(SIZE):
        matrix[i][i] = Interval(1)
        for j in range(SIZE):
            step = j - i
            if 0 < abs(step) <= WIDTH:
                matrix[i][j] = kernel(step)
    return matrix


def schur(matrix):
    killed = set(INTERIOR)
    keep = [index for index in range(SIZE) if index not in killed]
    pivot = [[matrix[i][j] for j in INTERIOR] for i in INTERIOR]
    right = [[matrix[i][j] for j in keep] for i in INTERIOR]
    left = [[matrix[i][j] for j in INTERIOR] for i in keep]
    body = [[matrix[i][j] for j in keep] for i in keep]
    pivot_inverse = invert(pivot)
    width = len(INTERIOR)
    height = len(keep)
    mixed = [[sum((left[i][t] * pivot_inverse[t][s] for t in range(width)), Interval(0))
              for s in range(width)] for i in range(height)]
    update = [[sum((mixed[i][s] * right[s][j] for s in range(width)), Interval(0))
               for j in range(height)] for i in range(height)]
    complement = [[body[i][j] - update[i][j] for j in range(height)]
                  for i in range(height)]
    return keep, complement


def half_bandwidth(matrix):
    found = 0
    for i, row in enumerate(matrix):
        for j, entry in enumerate(row):
            if i != j and not entry.exact_zero():
                found = max(found, abs(i - j))
    return found


def main():
    gaussian = GAUSSIAN.read_text(encoding="utf-8")
    gauge = GAUGE.read_text(encoding="utf-8")
    fine = FINE.read_text(encoding="utf-8")
    assert hashlib.sha256(GAUSSIAN.read_bytes()).hexdigest() == GAUSSIAN_SHA
    assert hashlib.sha256(GAUGE.read_bytes()).hexdigest() == GAUGE_SHA
    assert hashlib.sha256(FINE.read_bytes()).hexdigest() == FINE_SHA
    assert "k(h)=exp(-a rho h^2-2a beta0 h)" in gaussian
    assert "bandwidth O(W) in boundary order" in gaussian
    assert "exp(-gamma u^2 + 2 gamma s u)" in gauge
    assert "has G'_s(0) = 1" in gauge
    assert "two neighboring O(W)-size separators" in fine

    forward_weight = kernel(1)
    backward_weight = kernel(-1)
    assert forward_weight.low > backward_weight.high > 0
    matrix = host()
    off_sum = max(sum((matrix[i][j] for j in range(SIZE) if j != i), Interval(0)).high
                  for i in range(SIZE))
    assert off_sum < Fraction(9, 10)

    keep, complement = schur(matrix)
    assert keep == [0, 1, 2, 7, 8, 9]
    assert half_bandwidth(complement) == 2 * WIDTH - 1
    forward = complement[keep.index(1)][keep.index(8)]
    reverse = complement[keep.index(8)][keep.index(1)]
    assert Fraction(1, 1600) < forward.low and forward.high < Fraction(1, 1500)
    assert Fraction(5, 10000000) < reverse.low and reverse.high < Fraction(6, 10000000)
    for column, survivor in enumerate(keep):
        if survivor > WIDTH:
            assert complement[0][column].exact_zero()
    corners = [(i, j) for i in range(len(keep)) for j in range(len(keep))
               if abs(i - j) == 3 and not complement[i][j].exact_zero()]
    assert corners == [(keep.index(1), keep.index(8)), (keep.index(8), keep.index(1))]
    print("PASS gaussian-shift-corner")


if __name__ == "__main__":
    main()
