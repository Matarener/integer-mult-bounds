"""Encoded natural tensor geometry and fine-grid phase precision."""

from chirp_sources import active
active()
from cardinal_counts import Count
from encoded import compare, subtract
from fourier_plan import FourierPlan
from ring_words import power_two
from router_metadata import ceiling_log, owned
from words import need


class ChirpPlan(FourierPlan):
    def compile(self):
        super().compile()
        with owned(Count.literal(16), Count.literal(13)) as (minimum, gap):
            need(compare(self.p, minimum) >= 0 and compare(self.ell, self.p) < 0,
                 "chirp precision and degree admission")
            need(compare(self.p, self.n) >= 0, "chirp precision covers outer scale")
            self.keep("scale_gap", subtract(self.p, self.n))
            need(compare(self.scale_gap, gap) >= 0, "chirp norm margin requires p-A at least thirteen")
        self.keep("dimensions", Count(self.axes))
        self.dimensions.increment()
        self.keep("key_width", Count(self.ell))
        self.key_width.increment()
        self.keep("modulus", power_two(self.key_width))
        self.keep("fine_gap", ceiling_log(self.key_width))
        with owned(Count.literal(4), Count.literal(2), Count.literal(3)) as (guard, two, three):
            self.fine_gap.add(guard)
            self.keep("Q", Count(self.p))
            self.Q.add(self.fine_gap)
            self.keep("fine_width", Count(self.Q))
            self.fine_width.add(two)
            self.keep("word_width", Count(self.Q))
            self.word_width.add(three)
            self.keep("small_word_width", Count(self.p))
            self.small_word_width.add(three)
        self.keep("records", Count.product(self.addresses, self.rows))
        self.keep("cube", Count.product(self.addresses, self.r))
        self.keep("packet_bits", Count.product(self.gaussians, self.small))
        self.packet_bits.multiply_small(2)
        self.keep("source_bits", Count.product(self.dimensions, self.ell))
        self.keep("state_row_bits", Count(self.key_width))
        self.state_row_bits.multiply_small(5)


class GridPlan:
    """Two borrowed numerical ports needed by the retained exact arithmetic."""
    def __init__(self, precision, word_width):
        self.Q, self.word_width = precision, word_width
