"""A protected short table of certified positive dyadic phase powers."""

from chirp_sources import active
active()
from cardinal_counts import Count, positive
from encoded import compare
from records import Tape
from ring_words import Signed, power_two, write_signed
from router_metadata import indices, owned
from scratch_pool import ScratchPool
from session import OuterScope, erase_marker, initialize_marker, sealed_constructors
from twiddle_setup import TwiddlePlan
from words import BLANK, need


class PhaseBasis:
    def __init__(self):
        self.pool = ScratchPool(256)
        self.scope = OuterScope(self.pool)
        self.output = Tape()
        self.closed = True
        for item in (*self.pool.tapes, self.output):
            erase_marker(item)

    def run(self, precision, ell):
        need(self.closed and not self.pool.live and self.output.read() == BLANK,
             "consume prior phase-basis output")
        for item in (*self.pool.tapes, self.output):
            initialize_marker(item)
        self.closed = False
        plan = None
        succeeded = False
        try:
            with sealed_constructors(), self.scope.installed():
                try:
                    positive(ell)
                    with owned(Count(ell)) as (length_log,):
                        length_log.increment()
                        with owned(power_two(length_log)) as (length,):
                            plan = TwiddlePlan(precision, length)
                            plan.compile()
                            with owned(Count.literal(1)) as (index,):
                                for _ in indices(ell):
                                    with owned(*plan.value(index)) as pair:
                                        with owned(Count.product(pair[0].magnitude, pair[0].magnitude),
                                                   Count.product(pair[1].magnitude, pair[1].magnitude),
                                                   Count.product(plan.grid, plan.grid)) as (real, imaginary, unit):
                                            real.add(imaginary)
                                            need(compare(real, unit) <= 0, "inward phase-basis norm")
                                        for value in pair:
                                            write_signed(value, self.output, plan.width)
                                    index.multiply_small(2)
                            with owned(Signed(Count(plan.grid), True), Signed(Count.literal(0))) as pair:
                                for value in pair:
                                    write_signed(value, self.output, plan.width)
                    succeeded = True
                finally:
                    if plan is not None:
                        plan.close()
                    for value in (precision, ell):
                        value.rewind()
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
