"""Canonical coarse/inner field order with the full physical support bill."""
from tensor_sources import active
active()
from cardinal_counts import Count, positive
from compact_counts import append_bits, read_fixed
from compact_streams import stable_radix
from encoded import compare, subtract
from expansion_records import Fields
from gaussian_rationals import read_count, write_count
from records import Tape
from router_metadata import indices, owned, position_width, write_pair
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_count, borrowed_tape, erase_marker,
                     initialize_marker, sealed_constructors)
from tensor_router import FullRouter
from words import BLANK, need


class GatherPlan(Fields):
    def __init__(self, flags, axes, ell, inner_bits, factory):
        super().__init__()
        self.widths = self.forward = self.inverse = None
        try:
            for value in (axes, ell, inner_bits):
                positive(value)
            with owned(Count.literal(2)) as (two,):
                need(compare(ell, two) >= 0, "gather axis exponent at least two")
            self.keep("dimensions", Count(axes))
            self.dimensions.increment()
            self.keep("inner", Count(inner_bits))
            self.keep("n", Count.literal(0))
            self.keep("g", Count.product(self.dimensions, inner_bits))
            self.widths = factory()
            flags.rewind()
            for index in indices(self.dimensions):
                bit = 1 if compare(index, axes) == 0 else flags.read()
                need(bit in (0, 1), "complete gather target-axis flags")
                if compare(index, axes) < 0:
                    flags.step(1)
                with owned(Count.literal(1)) as (one,):
                    with owned(Count(ell) if bit else subtract(ell, one)) as (width,):
                        need(compare(width, inner_bits) >= 0, "short inner field fits each original axis")
                        write_count(width, self.widths)
                        self.n.add(width)
            need(flags.read() == BLANK, "complete gather flags extent")
            self.widths.rewind()
            self.keep("position_width", position_width(self.n))
            self.forward = factory()
            self.inverse = factory()
            with owned(Count.literal(0), Count.literal(0), Count.literal(1)) as (old_base, coarse_base, one):
                for reverse_index in indices(self.dimensions):
                    with owned(subtract(self.dimensions, reverse_index)) as (after,):
                        with owned(subtract(after, one)) as (axis_index,):
                            with owned(self.axis_width(axis_index)) as (axis_width,):
                                with owned(subtract(axis_width, inner_bits), Count.product(reverse_index, inner_bits)) as (coarse_width, low_base):
                                    for bit in indices(inner_bits):
                                        with owned(Count(old_base), Count(low_base)) as (old, new):
                                            old.add(bit)
                                            new.add(bit)
                                            write_pair(self.forward, old, new, self.position_width)
                                            write_pair(self.inverse, new, old, self.position_width)
                                    for bit in indices(coarse_width):
                                        with owned(Count(old_base), Count(self.g)) as (old, new):
                                            old.add(inner_bits)
                                            old.add(bit)
                                            new.add(coarse_base)
                                            new.add(bit)
                                            write_pair(self.forward, old, new, self.position_width)
                                            write_pair(self.inverse, new, old, self.position_width)
                                    old_base.add(axis_width)
                                    coarse_base.add(coarse_width)
            self.forward.rewind()
            self.inverse.rewind()
            unsorted, self.inverse = self.inverse, None
            self.inverse = stable_radix(unsorted, self.position_width, self.position_width, factory)
        except BaseException:
            self.close()
            raise
        finally:
            flags.rewind()

    def axis_width(self, index):
        self.widths.rewind()
        try:
            for _ in indices(index):
                with owned(read_count(self.widths)):
                    pass
            return read_count(self.widths)
        finally:
            self.widths.rewind()

    def close(self):
        for tape in (self.widths, self.forward, self.inverse):
            if tape is not None:
                tape.clear()
        self.widths = self.forward = self.inverse = None
        super().close()


class Gather:
    def __init__(self, router):
        need(isinstance(router, FullRouter), "complete physical gather router")
        self.router = router
        self.pool = ScratchPool(256)
        self.scope = OuterScope(self.pool)
        self.output = Tape()
        self.closed = True
        self.calls = 0
        self.last_counts = None
        for tape in (*self.pool.tapes, self.output):
            erase_marker(tape)

    def idle(self):
        self.router.idle()
        need(self.router.closed and not self.router.pool.live and self.router.output.read() == BLANK,
             "consumed complete gather router return")

    def run(self, payload, flags, axes, ell, inner_bits, precision, record_bits, rows, inverse=False):
        need(type(inverse) is bool, "compiled coarse/inner gather direction")
        source, flags = borrowed_tape(payload), borrowed_tape(flags)
        parameters = tuple(borrowed_count(v) for v in (axes, ell, inner_bits, precision, record_bits, rows))
        axes, ell, inner_bits, p, R, C = parameters
        forbidden = (*self.pool.tapes, self.output, *self.router.pool.tapes, self.router.output)
        need(source is not flags and source not in forbidden and flags not in forbidden
             and all(v.tape not in forbidden for v in parameters), "external canonical gather ports")
        need(self.closed and not self.pool.live and self.output.read() == BLANK,
             "consume prior canonical gather output")
        self.idle()
        for tape in (*self.pool.tapes, self.output):
            initialize_marker(tape)
        self.closed = False
        plan = returned = None
        succeeded = False
        try:
            with sealed_constructors(), self.scope.installed():
                try:
                    plan = GatherPlan(flags, axes, ell, inner_bits, self.pool.acquire)
                    with self.scope.suspended():
                        returned = self.router.run(borrowed_tape(source),
                            borrowed_tape(plan.inverse if inverse else plan.forward),
                            *(borrowed_count(v) for v in (plan.n, p, plan.n, plan.position_width, R, C)))
                    append_bits(returned, self.output)
                    returned.clear()
                    erase_marker(returned)
                    returned = None
                    self.last_counts = dict(self.router.last_counts)
                    self.idle()
                    self.calls += 1
                    succeeded = True
                finally:
                    if returned is not None:
                        returned.clear()
                        erase_marker(returned)
                    if plan is not None:
                        plan.close()
                    source.rewind()
                    flags.rewind()
                    for value in parameters:
                        value.rewind()
                    self.pool.empty()
        finally:
            for tape in self.pool.tapes:
                erase_marker(tape)
            self.output.rewind()
            if not succeeded:
                self.output.clear()
                erase_marker(self.output)
            self.closed = True
        return self.output
