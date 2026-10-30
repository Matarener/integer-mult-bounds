"""Complete natural-order numerical chirp packets from encoded residues."""

from chirp_sources import active
active()
from cardinal_counts import Count
from chirp_odometer import Odometer
from chirp_plan import ChirpPlan
from compact_counts import append_bits
from fft_arithmetic import Arithmetic
from phase_basis import PhaseBasis
from records import Tape
from ring_words import Signed, power_two, read_signed, truncate, write_signed
from router_metadata import indices, owned
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_count, borrowed_tape, erase_marker,
                     initialize_marker, sealed_constructors)
from stream import Counter
from word_product import WordProduct
from words import BLANK, RIGHT, need


class ChirpKernel:
    def __init__(self):
        self.word, self.basis, self.odometer = WordProduct(), PhaseBasis(), Odometer()
        self.pool = ScratchPool(256)
        self.scope = OuterScope(self.pool)
        self.arithmetic = Arithmetic(self.word, self.scope)
        self.output = Tape()
        self.closed = True
        self.calls = dict(tables=0, phases=0)
        for item in (*self.pool.tapes, self.output):
            erase_marker(item)

    def idle(self):
        need(self.word.closed and not self.word.pool.live and self.word.output.read() == BLANK
             and self.basis.closed and not self.basis.pool.live and self.basis.output.read() == BLANK,
             "consumed chirp scalar children")

    def phase(self, exponent, table, grid, plan):
        table.rewind()
        exponent.rewind()
        real, imaginary = Signed(Count(grid)), Signed(Count.literal(0))
        try:
            for _ in indices(plan.key_width):
                ended = exponent.read() == RIGHT
                bit = 0 if ended else exponent.read()
                need(bit in (0, 1), "canonical chirp exponent digit")
                if not ended:
                    exponent.step(1)
                with owned(read_signed(table, plan.fine_width), read_signed(table, plan.fine_width)) as pair:
                    if bit:
                        following = self.arithmetic.pointwise(real, imaginary, *pair, plan)
                        real.close()
                        imaginary.close()
                        real, imaginary = following
            need(exponent.read() == RIGHT and table.read() == BLANK, "complete chirp exponent and basis")
            with owned(truncate(real, plan.fine_gap), truncate(imaginary, plan.fine_gap)) as result:
                for value in result:
                    write_signed(value, self.output, plan.small)
            self.calls["phases"] += 1
        finally:
            real.close()
            imaginary.close()
            exponent.rewind()
            table.rewind()

    def run(self, sources, flags, axes, ell, precision, rows):
        sources, flags = borrowed_tape(sources), borrowed_tape(flags)
        need(sources is not flags and sources is not self.output and flags is not self.output,
             "distinct borrowed chirp descriptors")
        need(self.closed and not self.pool.live and self.output.read() == BLANK,
             "consume prior chirp-kernel output")
        self.idle()
        for item in (*self.pool.tapes, self.output):
            initialize_marker(item)
        self.closed = False
        plan = table = None
        succeeded = False
        try:
            with sealed_constructors(), self.scope.installed():
                try:
                    plan = ChirpPlan(flags, axes, ell, precision, rows)
                    plan.compile()
                    self.odometer.open(sources, plan)
                    with self.scope.suspended():
                        returned = self.basis.run(borrowed_count(plan.Q), borrowed_count(ell))
                    table = self.pool.acquire()
                    try:
                        append_bits(returned, table)
                    finally:
                        returned.clear()
                        erase_marker(returned)
                    self.calls["tables"] += 1
                    with owned(power_two(plan.Q)) as (grid,):
                        for _ in indices(rows):
                            with owned(Counter(plan.cube)) as (remaining,):
                                while not remaining.finished:
                                    self.phase(self.odometer.phase, table, grid, plan)
                                    remaining.decrement()
                                    advanced = self.odometer.advance()
                                    need(advanced != remaining.finished, "one complete chirp cube and rollover")
                    self.idle()
                    succeeded = True
                finally:
                    self.odometer.close()
                    if table is not None:
                        table.clear()
                    if plan is not None:
                        plan.close()
                    for value in (sources, flags, axes, ell, precision, rows):
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
