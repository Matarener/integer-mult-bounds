"""Directed fixed-point Machin/Taylor setup on encoded integer tapes."""

from ring_sources import active
active()
from cardinal_counts import Count, positive
from encoded import compare, divide, subtract
from records import Tape
from ring_words import Signed, add, difference, left_shift, power_two, right_shift, write_signed
from router_metadata import ceiling_log, indices, owned
from scratch_pool import ScratchPool
from session import OuterScope, erase_marker, initialize_marker, sealed_constructors
from stream import Counter
from words import BLANK, need


def quotient(numerator, denominator, upward=False):
    result, remainder = divide(numerator, denominator)
    try:
        if upward and not remainder.zero():
            result.increment()
        return result
    except BaseException:
        result.close()
        raise
    finally:
        remainder.close()


def interval_sum(lower, upper, term_lower, term_upper, negative):
    with owned(Signed(Count(term_lower)), Signed(Count(term_upper))) as (lo, hi):
        if negative:
            return difference(lower, hi), difference(upper, lo)
        return add(lower, lo), add(upper, hi)


def padded(lower, upper, padding):
    with owned(Signed(Count(padding))) as (amount,):
        return difference(lower, amount), add(upper, amount)


def arctangent(unit, terms, denominator):
    need(denominator in (5, 239), "fixed Machin denominator")
    square = 25 if denominator == 5 else 57121
    lower, upper = Signed(Count.literal(0)), Signed(Count.literal(0))
    power, odd = Count.literal(denominator), Count.literal(1)
    negative = False
    try:
        for _ in indices(terms):
            with owned(Count.product(power, odd)) as (divisor,):
                with owned(quotient(unit, divisor)) as (lo,):
                    with owned(Count(lo)) as (hi,):
                        hi.increment()
                        following = interval_sum(lower, upper, lo, hi, negative)
            lower.close()
            upper.close()
            lower, upper = following
            negative = not negative
            power.multiply_small(square)
            odd.increment()
            odd.increment()
        with owned(Count.literal(1)) as (tail,):
            result = padded(lower, upper, tail)
        return result
    finally:
        lower.close()
        upper.close()
        power.close()
        odd.close()


def times_small(value, factor):
    result = value.copy()
    result.magnitude.multiply_small(factor)
    return result


def pi_interval(unit, terms):
    a = arctangent(unit, terms, 5)
    b = arctangent(unit, terms, 239)
    try:
        with owned(times_small(a[0], 16), times_small(a[1], 16),
                   times_small(b[0], 4), times_small(b[1], 4)) as (al, au, bl, bu):
            return difference(al, bu), difference(au, bl)
    finally:
        for item in (*a, *b):
            item.close()


def taylor_intervals(angle, plan):
    """Enclose cos/sin at one exact R-grid angle; pad for angle/tail error."""
    lo, hi = Count(plan.unit), Count(plan.unit)
    accumulators = [Signed(Count.literal(0)) for _ in range(4)]
    degree = Count.literal(1)
    phase = 0
    try:
        with owned(Count(plan.T)) as (total,):
            total.multiply_small(2)
            with owned(Counter(total)) as (remaining,):
                while not remaining.finished:
                    offset = 0 if phase in (0, 2) else 2
                    following = interval_sum(accumulators[offset], accumulators[offset+1],
                                             lo, hi, phase in (2, 3))
                    accumulators[offset].close()
                    accumulators[offset+1].close()
                    accumulators[offset:offset+2] = following  # Two of four fixed scalar roles.
                    remaining.decrement()
                    if not remaining.finished:
                        with owned(left_shift(degree, plan.R), Count.product(lo, angle),
                                   Count.product(hi, angle)) as (denominator, low_product, high_product):
                            next_lo = quotient(low_product, denominator)
                            next_hi = quotient(high_product, denominator, True)
                        lo.close()
                        hi.close()
                        lo, hi = next_lo, next_hi
                        with owned(subtract(hi, lo), Count.literal(16)) as (spread, bound):
                            need(compare(spread, bound) <= 0, "directed Taylor term width")
                        degree.increment()
                    phase = (phase+1) % 4
        cosine = padded(accumulators[0], accumulators[1], plan.padding)
        sine = padded(accumulators[2], accumulators[3], plan.padding)
        return (*cosine, *sine)
    finally:
        for item in (lo, hi, degree, *accumulators):
            item.close()


def inward(lower, upper, shift):
    with owned(difference(upper, lower)) as (spread,):
        need(not spread.negative, "ordered twiddle interval")
    if not lower.negative and not lower.magnitude.zero():
        return Signed(right_shift(lower.magnitude, shift))
    if upper.negative:
        return Signed(right_shift(upper.magnitude, shift), True)
    return Signed(Count.literal(0))


class TwiddlePlan:
    def __init__(self, precision, length):
        self.Q, self.length = precision, length
        self.fields = {}

    def keep(self, name, value):
        need(name not in self.fields, "one twiddle setup role")
        self.fields[name] = value
        return value

    def __getattr__(self, name):
        return self.fields[name]

    def compile(self):
        with owned(Count.literal(16), Count.literal(2), Count.literal(1)) as (minimum, two, one):
            need(compare(self.Q, minimum) >= 0 and compare(self.length, two) >= 0,
                 "twiddle precision and nontrivial dyadic stage")
            with owned(Count(self.length), Count.literal(0)) as (value, logarithm):
                while compare(value, one) > 0:
                    need(value.divide_small(2) == 0, "dyadic twiddle stage length")
                    logarithm.increment()
                    need(compare(logarithm, self.Q) <= 0, "twiddle address width fits precision")
        self.keep("half", Count(self.length))
        self.half.divide_small(2)
        self.keep("T", Count(self.Q))
        self.keep("J", Count(self.Q))
        self.keep("width", Count(self.Q))
        with owned(Count.literal(64), Count.literal(8), Count.literal(2), Count.literal(12)) as (a, b, two, guard):
            self.T.add(a)
            self.J.add(b)
            self.width.add(two)
            with owned(ceiling_log(self.T)) as (logarithm,):
                self.keep("R", Count(self.Q))
                self.R.add(logarithm)
                self.R.add(guard)
        self.keep("shift", subtract(self.R, self.Q))
        self.keep("unit", power_two(self.R))
        self.keep("grid", power_two(self.Q))
        self.keep("padding", Count(self.T))
        self.padding.multiply_small(24)
        with owned(Count.literal(2)) as (two,):
            if compare(self.half, two) > 0:
                lo, hi = pi_interval(self.unit, self.J)
                self.keep("pi_lower", lo)
                self.keep("pi_upper", hi)
                with owned(Count(self.unit), Count(self.unit)) as (three, four):
                    three.multiply_small(3)
                    four.multiply_small(4)
                    need(not lo.negative and not hi.negative
                         and compare(three, lo.magnitude) < 0 and compare(hi.magnitude, four) < 0,
                         "certified positive Machin interval inside (3,4)")

    def value(self, index):
        if index.zero():
            return Signed(Count(self.grid)), Signed(Count.literal(0))
        with owned(Count(index)) as (twice,):
            twice.multiply_small(2)
            if compare(twice, self.half) == 0:
                return Signed(Count.literal(0)), Signed(Count(self.grid))
        with owned(Count.product(self.pi_lower.magnitude, index)) as (numerator,):
            angle = quotient(numerator, self.half)
        try:
            endpoints = taylor_intervals(angle, self)
            try:
                with owned(Count(self.T)) as (bound,):
                    bound.multiply_small(64)
                    for offset in (0, 2):
                        with owned(difference(endpoints[offset+1], endpoints[offset])) as (spread,):
                            need(not spread.negative and compare(spread.magnitude, bound) <= 0,
                                 "complete directed twiddle interval width")
                return inward(endpoints[0], endpoints[1], self.shift), inward(endpoints[2], endpoints[3], self.shift)
            finally:
                for item in endpoints:
                    item.close()
        finally:
            angle.close()

    def close(self):
        for item in reversed(tuple(self.fields.values())):
            item.close()
        self.fields.clear()


class Twiddles:
    def __init__(self):
        self.pool = ScratchPool(256)
        self.scope = OuterScope(self.pool)
        self.output = Tape()
        self.closed = True
        for item in (*self.pool.tapes, self.output):
            erase_marker(item)

    def run(self, precision, length, opposite=False):
        need(type(opposite) is bool, "finite twiddle direction")
        need(self.closed and not self.pool.live and self.output.read() == BLANK,
             "consume prior twiddle output")
        for item in (*self.pool.tapes, self.output):
            initialize_marker(item)
        self.closed = False
        plan = None
        succeeded = False
        try:
            with sealed_constructors(), self.scope.installed():
                try:
                    plan = TwiddlePlan(precision, length)
                    plan.compile()
                    for index in indices(plan.half):
                        real, imaginary = plan.value(index)
                        try:
                            if not opposite:
                                imaginary.negative = not imaginary.negative and not imaginary.magnitude.zero()
                            with owned(Count.product(real.magnitude, real.magnitude),
                                       Count.product(imaginary.magnitude, imaginary.magnitude),
                                       power_two(precision)) as (norm, other, bound):
                                norm.add(other)
                                with owned(Count.product(bound, bound)) as (squared,):
                                    need(compare(norm, squared) <= 0, "inward twiddle disk bound")
                            write_signed(real, self.output, plan.width)
                            write_signed(imaginary, self.output, plan.width)
                        finally:
                            real.close()
                            imaginary.close()
                    succeeded = True
                finally:
                    if plan is not None:
                        plan.close()
                    precision.rewind()
                    length.rewind()
                    self.pool.empty()
        finally:
            for item in self.pool.tapes:
                erase_marker(item)
            self.output.rewind()
            if not succeeded:
                self.output.clear()
                erase_marker(self.output)
            self.closed = True
        return self.output
