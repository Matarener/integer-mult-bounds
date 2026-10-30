"""Exact signed butterfly numerators and one final grid truncation."""

from ring_sources import active
active()
from cardinal_counts import Count
from compact_counts import read_fixed
from ring_words import Signed, add, difference, scaled, truncate
from router_metadata import owned
from session import borrowed_count, erase_marker
from words import BLANK, need


class Arithmetic:
    def __init__(self, word, scope):
        self.word, self.scope = word, scope
        self.products = 0

    def multiply(self, left, right, width):
        with self.scope.suspended():
            returned = self.word.run(borrowed_count(left.magnitude),
                                     borrowed_count(right.magnitude), borrowed_count(width))
        magnitude = None
        try:
            with owned(Count(width)) as (size,):
                size.multiply_small(2)
                magnitude = read_fixed(returned, size)
            need(returned.read() == BLANK, "complete exact scalar product return")
            result = Signed(magnitude, left.negative != right.negative)
            magnitude = None
            self.products += 1
            return result
        finally:
            if magnitude is not None:
                magnitude.close()
            returned.clear()
            erase_marker(returned)

    def complex_product(self, a, b, c, d, width):
        with owned(self.multiply(a, c, width), self.multiply(b, d, width)) as (ac, bd):
            real = difference(ac, bd)
        try:
            with owned(self.multiply(a, d, width), self.multiply(b, c, width)) as (ad, bc):
                imaginary = add(ad, bc)
            return real, imaginary
        except BaseException:
            real.close()
            raise

    def dif(self, a, b, c, d, u, v, plan):
        with owned(add(a, c), add(b, d), difference(a, c), difference(b, d)) as (sr, si, dr, di):
            with owned(*self.complex_product(dr, di, u, v, plan.word_width)) as (real, imaginary):
                with owned(Count.literal(1)) as (one,):
                    return (truncate(sr, one), truncate(si, one),
                            truncate(real, plan.half_shift), truncate(imaginary, plan.half_shift))

    def dit(self, a, b, c, d, u, v, plan):
        with owned(*self.complex_product(c, d, u, v, plan.word_width)) as (real, imaginary):
            with owned(scaled(a, plan.Q), scaled(b, plan.Q)) as (ar, ai):
                with owned(add(ar, real), add(ai, imaginary),
                           difference(ar, real), difference(ai, imaginary)) as values:
                    return tuple(truncate(value, plan.half_shift) for value in values)

    def pointwise(self, a, b, c, d, plan):
        with owned(*self.complex_product(a, b, c, d, plan.word_width)) as (real, imaginary):
            return truncate(real, plan.Q), truncate(imaginary, plan.Q)
