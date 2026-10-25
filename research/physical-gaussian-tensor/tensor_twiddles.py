"""Exact inward radicals for fixed small orders, with retained general setup."""
from types import FunctionType
from tensor_sources import active
active()
from cardinal_counts import Count
from encoded import compare, subtract
from phase_basis import PhaseBasis
from ring_words import Signed, power_two
from router_metadata import owned
from twiddle_setup import TwiddlePlan, Twiddles
from words import BLANK, LEFT, RIGHT, need


def integer_sqrt(value):
    """Read binary digit pairs; keep the root and remainder on encoded tapes."""
    root = remainder = None
    value.rewind()
    try:
        parity = 0
        while value.read() != RIGHT:
            need(value.read() in (0, 1), "canonical square-root operand")
            parity ^= 1
            value.step(1)
        value.msb()
        root, remainder = Count.literal(0), Count.literal(0)
        first = True
        while value.read() != LEFT:
            digit = 0
            for _ in range(1 if first and parity else 2):
                need(value.read() in (0, 1), "complete square-root digit pair")
                digit = 2*digit+value.read()
                value.step(-1)
            first = False
            remainder.multiply_small(4)
            with owned(Count.literal(digit), Count(root)) as (incoming, candidate):
                remainder.add(incoming)
                candidate.multiply_small(4)
                candidate.increment()
                root.multiply_small(2)
                if compare(remainder, candidate) >= 0:
                    following = subtract(remainder, candidate)
                    remainder.close()
                    remainder = following
                    root.increment()
        result, root = root, None
        return result
    finally:
        if value.read() == LEFT:
            value.step(1)
        value.rewind()
        for item in (root, remainder):
            if item is not None:
                item.close()


class SmallOrderPlan(TwiddlePlan):
    def compile(self):
        self.order = None
        for order in (2, 4, 8, 16):
            with owned(Count.literal(order)) as (length,):
                if compare(self.length, length) == 0:
                    self.order = order
                    break
        if self.order is None:
            return super().compile()
        with owned(Count.literal(16)) as (minimum,):
            need(compare(self.Q, minimum) >= 0, "small-order twiddle precision at least sixteen")
        self.keep("half", Count(self.length))
        self.half.divide_small(2)
        self.keep("grid", power_two(self.Q))
        self.keep("width", Count(self.Q))
        self.width.increment()
        self.width.increment()
        self.keep("zero", Count.literal(0))
        if self.order >= 8:
            with owned(Count(self.Q), Count.literal(1)) as (exponent, one):
                exponent.multiply_small(2)
                with owned(subtract(exponent, one)) as (power,):
                    with owned(power_two(power)) as (U,):
                        self.keep("h", integer_sqrt(U))
                        if self.order == 16:
                            with owned(Count(self.Q), Count.literal(3)) as (large, three):
                                large.multiply_small(4)
                                with owned(subtract(large, three)) as (power,):
                                    with owned(power_two(power)) as (radicand,):
                                        m = integer_sqrt(radicand)
                            with owned(m, Count(U)) as (m, upper):
                                upper.add(m)
                                self.keep("c", integer_sqrt(upper))
                                with owned(subtract(U, m)) as (lower,):
                                    with owned(subtract(lower, one)) as (radicand,):
                                        self.keep("s", integer_sqrt(radicand))

    def value(self, index):
        if self.order is None:
            return super().value(index)
        # A fixed sixteen-state control selects a constant-order phase.
        states = (("grid", False, "zero"), ("c", False, "s"), ("h", False, "h"),
                  ("s", False, "c"), ("zero", False, "grid"), ("s", True, "c"),
                  ("h", True, "h"), ("c", True, "s"))
        for position in range(self.order//2):
            with owned(Count.literal(position)) as (candidate,):
                if compare(index, candidate) == 0:
                    real, negative, imaginary = states[position*(16//self.order)]
                    return Signed(Count(getattr(self, real)), negative), Signed(Count(getattr(self, imaginary)))
        raise ValueError("small-order twiddle index within its half table")


def specialized(function):
    namespace = dict(function.__globals__)
    namespace["TwiddlePlan"] = SmallOrderPlan
    return FunctionType(function.__code__, namespace, function.__name__, function.__defaults__, function.__closure__)


class SmallTwiddles(Twiddles):
    run = specialized(Twiddles.run)


class SmallPhaseBasis(PhaseBasis):
    run = specialized(PhaseBasis.run)


def adapt_twiddles(owner):
    old = owner.twiddles
    need(type(old) is Twiddles and old.closed and not old.pool.live and old.output.read() == BLANK,
         "fresh retained twiddle producer")
    owner.twiddles = SmallTwiddles()


def adapt_small_chirp(owner):
    need(owner.closed and all(value == 0 for value in owner.calls.values()), "fresh small-root chirp adaptation")
    for scalar in (owner.cyclic, owner.cyclic.convolution.product):
        adapt_twiddles(scalar)
    old = owner.kernel.basis
    need(type(old) is PhaseBasis and old.closed and not old.pool.live and old.output.read() == BLANK,
         "fresh retained phase-basis producer")
    owner.kernel.basis = SmallPhaseBasis()
    return owner
