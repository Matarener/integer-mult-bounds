"""Complete twist/ring-convolution/exact-narrowing/untwist consumer."""

from chirp_sources import active
active()
from cardinal_counts import Count
from chirp_packets import validate
from chirp_plan import ChirpPlan
from compact_counts import append_bits
from convolution_engine import Convolution
from encoded import compare
from fft_arithmetic import Arithmetic
from phase_streams import narrow, repeated
from records import Tape
from router_metadata import owned
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_count, borrowed_tape, erase_marker,
                     initialize_marker, sealed_constructors)
from twiddle_setup import Twiddles
from word_product import WordProduct
from words import BLANK, need


class Cyclic:
    def __init__(self, convolution=None):
        self.convolution = Convolution() if convolution is None else convolution
        need(isinstance(self.convolution, Convolution), "authenticated ring-convolution owner")
        self.word, self.twiddles = WordProduct(), Twiddles()
        self.pool = ScratchPool(256)
        self.scope = OuterScope(self.pool)
        self.arithmetic = Arithmetic(self.word, self.scope)
        self.output = Tape()
        self.a = self.b = self.current = self.table = None
        self.closed = True
        self.calls = dict(tables=0, twists=0, convolutions=0, narrowings=0, untwists=0)
        for value in (*self.pool.tapes, self.output):
            erase_marker(value)

    def idle(self):
        self.convolution.idle()
        need(self.convolution.closed and not self.convolution.pool.live
             and self.convolution.output.read() == self.convolution.output_width.read() == BLANK
             and self.word.closed and not self.word.pool.live and self.word.output.read() == BLANK
             and self.twiddles.closed and not self.twiddles.pool.live and self.twiddles.output.read() == BLANK,
             "consumed cyclic-convolution children")

    def accept(self, returned):
        result = self.pool.acquire()
        try:
            append_bits(returned, result)
            result.rewind()
            return result
        except BaseException:
            result.clear()
            raise
        finally:
            returned.clear()
            erase_marker(returned)

    def run(self, first, second, flags, axes, ell, precision, rows):
        first, second, flags = (borrowed_tape(v) for v in (first, second, flags))
        need(len({id(first), id(second), id(flags)}) == 3
             and all(v is not self.output for v in (first, second, flags)),
             "distinct borrowed cyclic-convolution ports")
        need(self.closed and not self.pool.live and self.output.read() == BLANK
             and self.a is self.b is self.current is self.table is None,
             "consume prior cyclic-convolution output")
        self.idle()
        for value in (*self.pool.tapes, self.output):
            initialize_marker(value)
        self.closed = False
        plan = None
        succeeded = False
        try:
            with sealed_constructors(), self.scope.installed():
                try:
                    plan = ChirpPlan(flags, axes, ell, precision, rows)
                    plan.compile()
                    validate(first, plan.packet_bits, "cyclic left payload")
                    validate(second, plan.packet_bits, "cyclic right payload")
                    with self.scope.suspended():
                        returned = self.twiddles.run(borrowed_count(precision),
                                                     borrowed_count(plan.modulus), opposite=True)
                    self.table = self.accept(returned)
                    self.calls["tables"] += 1
                    self.a = repeated(first, self.table, plan, self.pool, self.arithmetic)
                    self.b = repeated(second, self.table, plan, self.pool, self.arithmetic)
                    self.calls["twists"] += 2
                    self.idle()
                    with self.scope.suspended():
                        returned, width_port = self.convolution.run(
                            borrowed_tape(self.a), borrowed_tape(self.b), borrowed_tape(flags),
                            *(borrowed_count(v) for v in (axes, ell, precision, rows)))
                    try:
                        self.current = self.accept(returned)
                        with owned(Count(width_port), Count(plan.small)) as (width, expected):
                            expected.add(plan.n)
                            need(compare(width, expected) == 0, "exact ring-convolution return width")
                            following = narrow(self.current, width, plan, self.pool)
                    finally:
                        width_port.clear()
                        erase_marker(width_port)
                    self.current.clear()
                    self.current = following
                    self.a.clear()
                    self.b.clear()
                    self.a = self.b = None
                    self.calls["convolutions"] += 1
                    self.calls["narrowings"] += 1
                    following = repeated(self.current, self.table, plan, self.pool,
                                         self.arithmetic, conjugate=True)
                    self.current.clear()
                    self.current = following
                    self.calls["untwists"] += 1
                    self.idle()
                    append_bits(self.current, self.output)
                    succeeded = True
                finally:
                    for value in (first, second, flags, axes, ell, precision, rows):
                        value.rewind()
                    for value in (self.a, self.b, self.current, self.table):
                        if value is not None:
                            value.clear()
                    self.a = self.b = self.current = self.table = None
                    if plan is not None:
                        plan.close()
                    self.pool.empty()
        finally:
            for value in self.pool.tapes:
                erase_marker(value)
            self.output.rewind()
            if not succeeded:
                self.output.clear()
                erase_marker(self.output)
            self.closed = True
        return self.output
