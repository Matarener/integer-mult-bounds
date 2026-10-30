"""Framed original-axis Gaussian pages and their encoded global shape."""
from tensor_sources import active
active()
from cardinal_counts import Count, positive
from compact_counts import append_bits, copy_bits
from encoded import compare, subtract
from expansion_records import Fields, same_integer, write_integer
from expansion_tile_geometry import ProductionTile, advance, source_index, stencil_bounds
from expansion_tile_prepare import TilePreparation, copy_cells, measure_cells
from gaussian_axis import Axis
from gaussian_rationals import read_count, write_count
from gaussian_window import Window
from records import Tape
from ring_words import Signed, difference
from router_metadata import indices, owned
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_count, borrowed_tape, erase_marker,
                     initialize_marker, sealed_constructors)
from tensor_plan import AxisRow, TensorHeader, TensorPlan
from tensor_counts import exact_setup_arithmetic
from words import BLANK, RIGHT, need


STREAMS = ("expansion_windows", "compression_windows", "cores", "compression_sources",
           "expansion_pages", "compression_pages")


def write_frame(source, target):
    with owned(measure_cells(source)) as (length,):
        try:
            write_count(length, target)
            copy_cells(source, target, length)
            need(source.read() == BLANK, "complete tensor frame copy")
        finally:
            source.rewind()


def skip_frame(source):
    with owned(read_count(source)) as (length,):
        for _ in indices(length):
            need(source.read() in (0, 1, RIGHT), "complete tensor frame extent")
            source.step(1)


def read_frame(source, factory):
    result = factory()
    try:
        with owned(read_count(source)) as (length,):
            copy_cells(source, result, length)
        result.rewind()
        return result
    except BaseException:
        result.clear()
        raise


class Profile:
    def __init__(self, source, factory):
        self.axis = None
        self.streams = {}
        try:
            self.axis = AxisRow(source)
            for name in STREAMS:
                self.streams[name] = read_frame(source, factory)
            need(source.read() == BLANK, "exact six-stream tensor axis profile")
        except BaseException:
            self.close()
            raise

    def __getattr__(self, name):
        return self.streams[name]

    def close(self):
        for value in self.streams.values():
            value.clear()
        self.streams.clear()
        if self.axis is not None:
            self.axis.close()
            self.axis = None


class Catalogue:
    def __init__(self, source, factory):
        self.source, self.factory = borrowed_tape(source), factory
        self.plan = self.prefix = None
        header = flags = sources = None
        try:
            self.source.rewind()
            header = TensorHeader(self.source)
            flags, sources = factory(), factory()
            copy_bits(self.source, flags, header.axes)
            with owned(Count(header.axes)) as (dimensions,):
                dimensions.increment()
                with owned(Count.product(dimensions, header.ell)) as (bits,):
                    copy_bits(self.source, sources, bits)
            flags.rewind()
            sources.rewind()
            self.plan = TensorPlan(sources, flags, header.axes, header.ell, header.p,
                header.alpha, header.inner_bits, header.P, header.sigma, header.radius,
                header.expansion_capacity, header.halo, header.w, factory,
                production=not header.mode.zero())
            self.prefix = factory()
            TensorHeader.dump(self.plan, self.prefix)
            append_bits(self.plan.flags, self.prefix)
            append_bits(self.plan.sources, self.prefix)
            self.prefix.rewind()
            for _ in indices(self.plan.dimensions):
                skip_frame(self.source)
            need(self.source.read() == BLANK, "complete tensor catalogue axis count")
        except BaseException:
            self.close()
            raise
        finally:
            for value in (header,):
                if value is not None:
                    value.close()
            for value in (flags, sources):
                if value is not None:
                    value.clear()
            self.source.rewind()

    def profile(self, index):
        need(compare(index, self.plan.dimensions) < 0, "tensor axis index")
        self.source.rewind()
        self.prefix.rewind()
        isolated = result = None
        try:
            while self.prefix.read() != BLANK:
                need(self.source.read() == self.prefix.read(), "unchanged tensor catalogue prefix")
                self.prefix.step(1)
                self.source.step(1)
            for _ in indices(index):
                skip_frame(self.source)
            isolated = read_frame(self.source, self.factory)
            result = Profile(isolated, self.factory)
            with owned(self.plan.axis(index)) as (expected,):
                need(all(compare(getattr(result.axis, name), getattr(expected, name)) == 0
                         for name in AxisRow.names), "tensor profile binds its original global axis")
            return result
        except BaseException:
            if result is not None:
                result.close()
            raise
        finally:
            if isolated is not None:
                isolated.clear()
            self.source.rewind()
            self.prefix.rewind()

    def close(self):
        if self.prefix is not None:
            self.prefix.clear()
            self.prefix = None
        if self.plan is not None:
            self.plan.close()
            self.plan = None


def descriptor(target, start, length):
    write_integer(start, target)
    write_count(length, target)


class TensorPreparation:
    """Prepare each axis once; reuse adjacent equal original axes byte for byte."""
    def __init__(self):
        self.tile = TilePreparation()
        self.pool = ScratchPool(2048)
        self.scope = OuterScope(self.pool)
        self.output = Tape()
        self.closed = True
        self.calls = 0
        self.last_counts = None
        for tape in (*self.pool.tapes, self.output):
            erase_marker(tape)

    def idle(self):
        self.tile.idle()
        need(self.tile.closed and not self.tile.pool.live and not self.tile.parameter_pool.live
             and self.tile.output.read() == BLANK, "consumed tensor preparation child")

    def prepare_profile(self, plan, row, target):
        streams = {}
        axis = None
        try:
            streams = {name: self.pool.acquire() for name in STREAMS}
            axis = Axis(row.s, row.t, plan.u, plan.w, plan.P, self.pool)
            self.last_counts["global_axes"] += 1
            for k in indices(row.tiles):
                with owned(Signed(Count.product(k, plan.L))) as (start,):
                    with owned(advance(start, plan.L)) as (end,):
                        with owned(source_index(row.s, row.t, start),
                                   source_index(row.s, row.t, end)) as (first, last):
                            with owned(difference(last, first), Signed(Count(plan.halo))) as (core, halo):
                                need(not core.negative and not core.magnitude.zero(), "positive tensor source core")
                                with owned(difference(start, halo)) as (halo_start,):
                                    window = Window(axis, halo_start, plan.target_halo, first,
                                                    core.magnitude, plan.p, self.pool)
                                    try:
                                        descriptor(streams["compression_windows"], halo_start, plan.target_halo)
                                        descriptor(streams["cores"], first, core.magnitude)
                                        descriptor(streams["compression_sources"], window.start, window.m)
                                        write_frame(window.page, streams["compression_pages"])
                                        self.prepare_expansion(plan, row, k, start, window, streams)
                                    finally:
                                        window.close()
                self.last_counts["tiles"] += 1
            for name in AxisRow.names:
                write_count(getattr(row, name), target)
            for name in STREAMS:
                write_frame(streams[name], target)
        finally:
            if axis is not None:
                axis.close()
            for tape in streams.values():
                tape.clear()

    def prepare_expansion(self, plan, row, k, start, window, streams):
        paired = first = last = length = None
        try:
            if not plan.mode.zero():
                paired = ProductionTile(row.s, row.t, plan.d, plan.alpha, plan.p, k)
                need(same_integer(paired.source_start, window.start)
                     and compare(paired.source_count, window.m) == 0,
                     "production expansion and compression use the same old-H window")
                first, length = paired.source_start.copy(), Count(paired.source_count)
            else:
                first, last = stencil_bounds(row.s, row.t, plan.radius, start, plan.L)
                with owned(difference(last, first)) as (distance,):
                    need(not distance.negative, "positive explicit tensor expansion window")
                    length = Count(distance.magnitude)
            descriptor(streams["expansion_windows"], first, length)
            with self.scope.suspended():
                returned = self.tile.run_explicit(row.s, row.t, plan.alpha, plan.radius,
                    first, length, plan.expansion_capacity, start, plan.L, plan.p, plan.P, plan.sigma)
            try:
                write_frame(returned, streams["expansion_pages"])
                self.last_counts["expansion_blocks"] += self.tile.last_counts["blocks"]
            finally:
                returned.clear()
                erase_marker(returned)
        finally:
            for value in (length, last, first, paired):
                if value is not None:
                    value.close()

    def run(self, sources, flags, axes, ell, p, alpha, inner_bits, P, sigma, radius,
            expansion_capacity, halo, w, production=False):
        with exact_setup_arithmetic():
            return self.execute(sources, flags, axes, ell, p, alpha, inner_bits, P, sigma,
                                radius, expansion_capacity, halo, w, production)

    def execute(self, sources, flags, axes, ell, p, alpha, inner_bits, P, sigma, radius,
                expansion_capacity, halo, w, production=False):
        sources, flags = borrowed_tape(sources), borrowed_tape(flags)
        parameters = tuple(borrowed_count(value) for value in
            (axes, ell, p, alpha, inner_bits, P, sigma, radius, expansion_capacity, halo, w))
        forbidden = (*self.pool.tapes, self.output)
        need(sources is not flags and sources not in forbidden and flags not in forbidden
             and all(value.tape not in forbidden for value in parameters), "external tensor preparation ports")
        need(self.closed and not self.pool.live and self.output.read() == BLANK,
             "consume previous tensor catalogue")
        self.idle()
        for tape in (*self.pool.tapes, self.output):
            initialize_marker(tape)
        self.closed = False
        self.last_counts = dict(global_axes=0, reused_axes=0, tiles=0, expansion_blocks=0)
        plan = previous_s = previous_t = profile = None
        succeeded = False
        try:
            with sealed_constructors(), self.scope.installed():
                try:
                    plan = TensorPlan(sources, flags, *parameters, self.pool.acquire, production=production)
                    TensorHeader.dump(plan, self.output)
                    append_bits(plan.flags, self.output)
                    append_bits(plan.sources, self.output)
                    profile = self.pool.acquire()
                    for index in indices(plan.dimensions):
                        with owned(plan.axis(index)) as (row,):
                            if previous_s is not None and compare(row.s, previous_s) == 0 and compare(row.t, previous_t) == 0:
                                self.last_counts["reused_axes"] += 1
                            else:
                                borrowed_tape(profile).clear()
                                self.prepare_profile(plan, row, profile)
                                for value in (previous_s, previous_t):
                                    if value is not None:
                                        value.close()
                                previous_s, previous_t = Count(row.s), Count(row.t)
                            write_frame(profile, self.output)
                    self.idle()
                    self.calls += 1
                    succeeded = True
                finally:
                    for value in (previous_s, previous_t, plan):
                        if value is not None:
                            value.close()
                    if profile is not None:
                        profile.clear()
                    sources.rewind()
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
