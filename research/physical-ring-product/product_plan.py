"""Complete packet geometry and exact-recovery precision on Count tapes."""

from ring_sources import active
active()
from cardinal_counts import Count, positive
from encoded import compare, subtract
from ring_words import power_two
from router_metadata import ceiling_log, owned
from words import need


class ProductPlan:
    def __init__(self, dimension, precision, ell, rows):
        self.A, self.p, self.ell, self.C = dimension, precision, ell, rows
        self.fields = {}

    def keep(self, name, value):
        need(name not in self.fields, "one normalized-product numerical role")
        self.fields[name] = value
        return value

    def __getattr__(self, name):
        return self.fields[name]

    def compile(self):
        positive(self.A)
        positive(self.ell)
        positive(self.C)
        with owned(Count.literal(2)) as (two,):
            need(compare(self.p, two) >= 0 and compare(self.ell, self.p) < 0,
                 "normalized-product precision and polynomial degree")
        self.keep("m", Count(self.ell))
        self.m.increment()
        self.keep("r", power_two(self.ell))
        self.keep("N", Count(self.r))
        self.N.multiply_small(2)
        with owned(power_two(self.A)) as (addresses,):
            self.keep("records", Count.product(addresses, self.C))
        self.keep("gaussians", Count.product(self.records, self.r))
        self.keep("fft_gaussians", Count.product(self.records, self.N))
        self.keep("Q", Count(self.p))
        self.Q.multiply_small(2)
        with owned(Count(self.m), Count(self.m), Count.literal(2), Count.literal(3)) as (twice, error, two, three):
            twice.multiply_small(2)
            self.Q.add(twice)
            error.multiply_small(12)
            error.add(two)
            self.keep("recovery_shift", ceiling_log(error))
            self.recovery_shift.add(three)
            self.Q.add(self.recovery_shift)
            self.keep("small", Count(self.p))
            self.small.add(two)
            self.keep("wide", Count(self.Q))
            self.wide.add(two)
            self.keep("word_width", Count(self.Q))
            self.word_width.add(three)
            self.keep("integer_width", Count(self.p))
            self.integer_width.multiply_small(2)
            self.integer_width.add(self.ell)
            self.integer_width.add(three)
        self.keep("lift", subtract(self.Q, self.p))
        self.keep("half_shift", Count(self.Q))
        self.half_shift.increment()
        self.keep("product_shift", Count(self.p))
        self.product_shift.add(self.ell)

    def close(self):
        for value in reversed(tuple(self.fields.values())):
            value.close()
        self.fields.clear()
