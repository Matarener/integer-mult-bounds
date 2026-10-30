"""Complete physical normalized polynomial Fourier transforms in natural order."""

from fourier_sources import active
active()
from cardinal_counts import Count
from compact_counts import append_bits, copy_bits, write_fixed
from compact_streams import stable_radix
from composed_engine import ComposedRoot, production_layer
from encoded import compare, subtract
from fourier_diagonal import diagonal
from fourier_plan import FourierPlan
from grid_boundary import GridBoundary
from records import Tape
from router_metadata import indices, owned, write_pair
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_count, borrowed_tape, erase_marker,
                     initialize_marker, sealed_constructors)
from words import BLANK, LEFT, need


class Fourier:
    def __init__(self, layer):
        need(isinstance(layer, ComposedRoot), "authenticated arbitrary-support Fourier child")
        self.layer = layer
        self.grid = GridBoundary()
        self.pool = ScratchPool(256)
        self.scope = OuterScope(self.pool)
        self.output = Tape()
        self.current = None
        self.closed = True
        self.calls = dict(roots=0, diagonals=0, reversals=0, lifts=0, truncations=0)
        for tape in (*self.pool.tapes, self.output):
            erase_marker(tape)

    def idle(self):
        self.layer.idle()
        need(self.layer.closed and self.layer.current is None and not self.layer.pool.live
             and self.layer.output.read() == BLANK and self.grid.closed
             and self.grid.output.read() == BLANK and not self.grid.pool.live,
             "consumed Fourier children")

    def rearm(self):
        need(self.closed and self.current is None and not self.pool.live
             and self.output.read() == BLANK, "consume prior Fourier output")
        self.idle()
        self.output.step(-1)
        need(self.output.read() in (LEFT, BLANK), "Fourier output origin")
        if self.output.read() == BLANK:
            self.output.write(LEFT)
        self.output.step(1)
        for tape in self.pool.tapes:
            initialize_marker(tape)
        self.closed = False

    def accept(self, returned):
        following = self.pool.acquire()
        try:
            append_bits(returned, following)
            following.rewind()
        except BaseException:
            following.clear()
            raise
        finally:
            returned.clear()
            erase_marker(returned)
        self.current.clear()
        self.current = following

    def root(self, plan, selected, count):
        selected.rewind()
        self.idle()
        with self.scope.suspended():
            returned = self.layer.run(
                borrowed_tape(self.current), borrowed_tape(selected),
                *(borrowed_count(value) for value in
                  (plan.n, plan.P, count, plan.width, plan.r, plan.rows)))
        self.accept(returned)
        self.calls["roots"] += 1

    def hadamard(self, plan, h):
        selected = self.pool.acquire()
        count = Count.literal(0)
        try:
            for offset, length in plan.natural_axes():
                if compare(h, length) < 0:
                    with owned(Count(offset)) as (position,):
                        position.add(h)
                        write_fixed(position, selected, plan.width)
                    count.increment()
                    if compare(count, plan.cap) == 0:
                        self.root(plan, selected, count)
                        borrowed_tape(selected).clear()
                        count.close()
                        count = Count.literal(0)
            if not count.zero():
                self.root(plan, selected, count)
        finally:
            count.close()
            selected.clear()

    def route_reversal_batch(self, plan, descriptor, edges):
        descriptor.rewind()
        sorted_descriptor = stable_radix(descriptor, plan.width, plan.width, self.pool.acquire)
        try:
            with owned(Count(edges)) as (count,):
                count.multiply_small(2)
                self.idle()
                with self.scope.suspended():
                    returned = self.layer.router.run(
                        borrowed_tape(self.current), borrowed_tape(sorted_descriptor),
                        *(borrowed_count(value) for value in
                          (plan.n, plan.P, count, plan.width, plan.record_bits, plan.rows)))
                self.accept(returned)
                self.calls["reversals"] += 1
        finally:
            sorted_descriptor.clear()

    def reversal(self, plan):
        descriptor = self.pool.acquire()
        count = Count.literal(0)
        try:
            with owned(Count.literal(1)) as (one,):
                for offset, length in plan.natural_axes():
                    with owned(Count(length), subtract(length, one)) as (half, last):
                        half.divide_small(2)
                        for position in indices(half):
                            with owned(Count(offset), subtract(last, position)) as (left, right):
                                left.add(position)
                                right.add(offset)
                                write_pair(descriptor, left, right, plan.width)
                                write_pair(descriptor, right, left, plan.width)
                            count.increment()
                            if compare(count, plan.cap) == 0:
                                self.route_reversal_batch(plan, descriptor, count)
                                descriptor = self.pool.acquire()
                                count.close()
                                count = Count.literal(0)
                if not count.zero():
                    self.route_reversal_batch(plan, descriptor, count)
                    descriptor = None
        finally:
            count.close()
            if descriptor is not None:
                descriptor.clear()

    def twiddle(self, plan, h, opposite):
        if not h.zero():
            self.current = diagonal(self.current, plan, h, opposite, self.pool.acquire)
            self.calls["diagonals"] += 1

    def execute(self, plan, opposite):
        with owned(Count.literal(0)) as (zero,):
            self.idle()
            with self.scope.suspended():
                returned = self.grid.expand(borrowed_tape(self.current),
                    *(borrowed_count(value) for value in (plan.small, plan.n, zero, plan.gaussians)))
            self.accept(returned)
        self.calls["lifts"] += 1
        if opposite:
            self.reversal(plan)
            for h in indices(plan.ell):
                self.twiddle(plan, h, True)
                self.hadamard(plan, h)
        else:
            with owned(Count.literal(1)) as (one,):
                with owned(subtract(plan.ell, one)) as (last,):
                    for index in indices(plan.ell):
                        with owned(subtract(last, index)) as (h,):
                            self.hadamard(plan, h)
                            self.twiddle(plan, h, False)
            self.reversal(plan)
        self.idle()
        with self.scope.suspended():
            returned = self.grid.truncate(borrowed_tape(self.current),
                *(borrowed_count(value) for value in (plan.wide, plan.n, plan.small, plan.gaussians)))
        self.accept(returned)
        self.calls["truncations"] += 1

    def run(self, payload, flags, axes, ell, precision, rows, opposite=False):
        need(type(opposite) is bool, "finite Fourier direction")
        source, descriptor = borrowed_tape(payload), borrowed_tape(flags)
        need(source is not descriptor and source is not self.output and descriptor is not self.output,
             "distinct borrowed Fourier ports")
        self.rearm()
        plan = None
        succeeded = False
        source.rewind()
        try:
            with sealed_constructors(), self.scope.installed():
                try:
                    plan = FourierPlan(descriptor, axes, ell, precision, rows)
                    plan.compile()
                    with owned(Count.product(plan.gaussians, plan.small)) as (bits,):
                        bits.multiply_small(2)
                        self.current = self.pool.acquire()
                        copy_bits(source, self.current, bits)
                    need(source.read() == BLANK, "complete Fourier Gaussian packet")
                    self.current.rewind()
                    self.execute(plan, opposite)
                    self.idle()
                    append_bits(self.current, self.output)
                    succeeded = True
                finally:
                    source.rewind()
                    descriptor.rewind()
                    if self.current is not None:
                        self.current.clear()
                        self.current = None
                    if plan is not None:
                        plan.close()
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


def production_fourier():
    return Fourier(production_layer())
