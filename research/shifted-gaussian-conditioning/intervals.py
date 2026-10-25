"""Directed decimal enclosures with rational input and explicit transcendental widening.

Jose Manuel (jmbarrancoml), with substantial OpenAI Codex assistance.
Apache-2.0. Exp/sqrt rely on Python Decimal's correctly-rounded contract.
"""
from decimal import (Decimal as D, Context, ROUND_FLOOR, ROUND_CEILING,
                     ROUND_HALF_EVEN, Underflow, Subnormal, Clamped, FloatOperation)
from fractions import Fraction as Q
from math import factorial

PRECISION = 80
DOWN = Context(prec=PRECISION, rounding=ROUND_FLOOR)
UP = Context(prec=PRECISION, rounding=ROUND_CEILING)
NEAR = Context(prec=PRECISION, rounding=ROUND_HALF_EVEN)
for context in (DOWN, UP, NEAR):
    for signal in (Underflow, Subnormal, Clamped, FloatOperation):
        context.traps[signal] = True


def need(ok, message):
    if not ok:
        raise ValueError(message)


class I:
    __slots__ = ("lo", "hi")

    def __init__(self, value, upper=None):
        if isinstance(value, D):
            lo, hi = value, value if upper is None else upper
        else:
            need(type(value) in (int, Q), "exact rational interval input")
            q = Q(value)
            lo = DOWN.divide(D(q.numerator), D(q.denominator))
            hi = UP.divide(D(q.numerator), D(q.denominator))
            need(upper is None, "single rational input")
        need(isinstance(lo, D) and isinstance(hi, D)
             and lo.is_finite() and hi.is_finite() and lo <= hi, "finite ordered interval")
        self.lo, self.hi = lo, hi

    @staticmethod
    def wrap(value):
        return value if isinstance(value, I) else I(value)

    def __add__(self, other):
        other = I.wrap(other)
        return I(DOWN.add(self.lo, other.lo), UP.add(self.hi, other.hi))

    __radd__ = __add__

    def __neg__(self):
        return I(self.hi.copy_negate(), self.lo.copy_negate())

    def __sub__(self, other):
        return self + -I.wrap(other)

    def __rsub__(self, other):
        return I.wrap(other) + -self

    def __mul__(self, other):
        other = I.wrap(other)
        pairs = [(x, y) for x in (self.lo, self.hi) for y in (other.lo, other.hi)]
        return I(min(DOWN.multiply(x, y) for x, y in pairs),
                 max(UP.multiply(x, y) for x, y in pairs))

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = I.wrap(other)
        need(other.lo > 0, "positive interval divisor")
        pairs = [(x, y) for x in (self.lo, self.hi) for y in (other.lo, other.hi)]
        return I(min(DOWN.divide(x, y) for x, y in pairs),
                 max(UP.divide(x, y) for x, y in pairs))

    def __rtruediv__(self, other):
        return I.wrap(other) / self

    def power(self, n):
        need(type(n) is int and n >= 0, "nonnegative integer power")
        value, factor = I(1), self
        while n:
            if n & 1:
                value = value * factor
            factor = factor * factor
            n //= 2
        return value

    def square(self):
        upper = max(UP.multiply(x, x) for x in (self.lo, self.hi))
        lower = D(0) if self.lo <= 0 <= self.hi else min(
            DOWN.multiply(x, x) for x in (self.lo, self.hi))
        return I(lower, upper)

    def exp(self):
        if self.lo == self.hi == 0:
            return I(1)
        # Decimal exp/sqrt round to nearest. One adjacent value on each side
        # encloses the exact endpoint before monotonicity propagates the interval.
        return I(DOWN.next_minus(NEAR.exp(self.lo)), UP.next_plus(NEAR.exp(self.hi)))

    def sqrt(self):
        need(self.lo >= 0, "nonnegative square root")
        lower = D(0) if self.lo == 0 else DOWN.next_minus(NEAR.sqrt(self.lo))
        return I(lower, UP.next_plus(NEAR.sqrt(self.hi)))

    def widen(self, error):
        error = I.wrap(error)
        need(error.lo >= 0, "nonnegative enclosure radius")
        return I(DOWN.subtract(self.lo, error.hi), UP.add(self.hi, error.hi))

    def intersect(self, other):
        return I(max(self.lo, other.lo), min(self.hi, other.hi))

    def record(self):
        return [str(self.lo), str(self.hi)]


def atan_rational(x, terms=80):
    need(0 < x < 1, "alternating arctangent domain")
    total = sum(((-1) ** k * x ** (2 * k + 1) / (2 * k + 1) for k in range(terms)), Q(0))
    adjacent = total + (-1) ** terms * x ** (2 * terms + 1) / (2 * terms + 1)
    return min(total, adjacent), max(total, adjacent)


def pi_interval():
    a, b = atan_rational(Q(1, 5)), atan_rational(Q(1, 239))
    lower, upper = 16 * a[0] - 4 * b[1], 16 * a[1] - 4 * b[0]
    need(Q(3) < lower < upper < Q(4), "Machin enclosure")
    return I(I(lower).lo, I(upper).hi)


def cos_interval(x, terms=100):
    x = I.wrap(x)
    total, term = I(1), I(1)
    square = x.square()
    for n in range(1, terms):
        term = -term * square / ((2 * n - 1) * (2 * n))
        total = total + term
    radius = max(x.lo.copy_abs(), x.hi.copy_abs())
    # The alternating tail decreases from this index; bound its first term.
    need(Q(radius) ** 2 < (2 * terms + 1) * (2 * terms + 2),
         "decreasing cosine tail")
    error = I(radius).power(2 * terms) / factorial(2 * terms)
    return total.widen(error)


def arithmetic_controls():
    for x in (Q(1, 8), Q(1, 2), Q(1)):
        total = sum(((-x) ** k / factorial(k) for k in range(200)), Q(0))
        adjacent = total + (-x) ** 200 / factorial(200)
        interval = I(-x).exp()
        need(Q(interval.lo) <= min(total, adjacent) <= max(total, adjacent) <= Q(interval.hi),
             "exp against independent rational alternating bounds")
    for x in (Q(1, 4), Q(2), Q(17, 3)):
        root = I(x).sqrt()
        need(Q(root.lo) ** 2 <= x <= Q(root.hi) ** 2, "sqrt endpoint squares")
    for x in (Q(-7, 3), Q(0), Q(5, 7)):
        for y in (Q(2, 9), Q(11, 4)):
            for candidate, exact in ((I(x) + I(y), x + y),
                                     (I(x) * I(y), x * y),
                                     (I(x) / I(y), x / y)):
                need(Q(candidate.lo) <= exact <= Q(candidate.hi), "directed rational arithmetic")
    return {"exp_cases": 3, "sqrt_cases": 3, "rational_operations": 18,
            "decimal_digits": PRECISION}
