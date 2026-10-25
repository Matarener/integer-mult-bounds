"""Actual Fourier/product/opposite composition with an explicit widened return."""

from ring_sources import active
active()
from cardinal_counts import Count
from compact_counts import append_bits
from encoded import compare
from fourier_engine import Fourier, production_fourier
from fourier_plan import FourierPlan
from grid_boundary import GridBoundary
from machine import copy_symbols
from records import Tape
from ring_engine import RingProduct
from router_metadata import owned
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_count, borrowed_tape, erase_marker,
                     initialize_marker, sealed_constructors)
from words import BLANK, need


class Convolution:
    def __init__(self, fourier=None):
        self.fourier = production_fourier() if fourier is None else fourier
        need(isinstance(self.fourier, Fourier), "authenticated complete Fourier owner")
        self.product = RingProduct()
        self.grid = GridBoundary()
        self.pool = ScratchPool(256)
        self.scope = OuterScope(self.pool)
        self.output, self.output_width = Tape(), Tape()
        self.a = self.b = self.current = None
        self.closed = True
        self.calls = dict(forward=0, product=0, opposite=0, scale=0)
        for item in (*self.pool.tapes, self.output, self.output_width):
            erase_marker(item)

    def idle(self):
        self.fourier.idle()
        self.product.idle()
        need(self.fourier.closed and not self.fourier.pool.live and self.fourier.output.read() == BLANK
             and self.product.closed and not self.product.pool.live and self.product.output.read() == BLANK
             and self.grid.closed and not self.grid.pool.live and self.grid.output.read() == BLANK,
             "consumed normalized-convolution children")

    def rearm(self):
        need(self.closed and self.a is self.b is self.current is None and not self.pool.live
             and self.output.read() == self.output_width.read() == BLANK,
             "consume both normalized-convolution output ports")
        self.idle()
        for item in (*self.pool.tapes, self.output, self.output_width):
            initialize_marker(item)
        self.closed = False

    def accept(self, returned):
        output = self.pool.acquire()
        try:
            append_bits(returned, output)
            output.rewind()
            return output
        except BaseException:
            output.clear()
            raise
        finally:
            returned.clear()
            erase_marker(returned)

    def transform(self, source, flags, axes, ell, precision, rows, opposite=False):
        self.idle()
        with self.scope.suspended():
            returned = self.fourier.run(borrowed_tape(source), borrowed_tape(flags),
                *(borrowed_count(value) for value in (axes, ell, precision, rows)), opposite=opposite)
        result = self.accept(returned)
        self.calls["opposite" if opposite else "forward"] += 1
        return result

    def run(self, first, second, flags, axes, ell, precision, rows):
        first, second, flags = (borrowed_tape(value) for value in (first, second, flags))
        need(len({id(first), id(second), id(flags)}) == 3
             and all(value not in (self.output, self.output_width) for value in (first, second, flags)),
             "distinct borrowed normalized-convolution ports")
        need(compare(ell, precision) < 0, "convolution polynomial degree below grid precision")
        self.rearm()
        shape = None
        succeeded = False
        try:
            with sealed_constructors(), self.scope.installed():
                try:
                    shape = FourierPlan(flags, axes, ell, precision, rows)
                    shape.compile()
                    self.a = self.transform(first, flags, axes, ell, precision, rows)
                    self.b = self.transform(second, flags, axes, ell, precision, rows)
                    self.idle()
                    with self.scope.suspended():
                        returned = self.product.run(borrowed_tape(self.a), borrowed_tape(self.b),
                            *(borrowed_count(value) for value in (shape.n, precision, ell, rows)))
                    self.current = self.accept(returned)
                    self.a.clear()
                    self.b.clear()
                    self.a = self.b = None
                    self.calls["product"] += 1
                    following = self.transform(self.current, flags, axes, ell, precision, rows, True)
                    self.current.clear()
                    self.current = following
                    self.idle()
                    with owned(Count.literal(0)) as (zero,):
                        with self.scope.suspended():
                            returned = self.grid.expand(borrowed_tape(self.current),
                                *(borrowed_count(value) for value in (shape.small, shape.n, zero, shape.gaussians)))
                    following = self.accept(returned)
                    self.current.clear()
                    self.current = following
                    self.calls["scale"] += 1
                    with owned(Count(shape.small)) as (width,):
                        width.add(shape.n)
                        copy_symbols(width.tape, self.output_width)
                    append_bits(self.current, self.output)
                    self.idle()
                    succeeded = True
                finally:
                    for value in (first, second, flags, axes, ell, precision, rows):
                        value.rewind()
                    for value in (self.a, self.b, self.current):
                        if value is not None:
                            value.clear()
                    self.a = self.b = self.current = None
                    if shape is not None:
                        shape.close()
                    self.pool.empty()
        finally:
            for item in self.pool.tapes:
                erase_marker(item)
            for item in (self.output, self.output_width):
                item.rewind()
                if not succeeded:
                    item.clear()
                    erase_marker(item)
            self.closed = True
        return self.output, self.output_width
