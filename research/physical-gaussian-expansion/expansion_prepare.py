"""Encoded real-Gaussian factor production and protected complete block pages."""
from expansion_sources import active
active()
from cardinal_counts import Count
from encoded import compare, subtract
from expansion_geometry import BlockGeometry, ProductionBlock, absolute
from expansion_records import BlockHeader
from gaussian_exponentials import Exponentials
from gaussian_page import skip_bits
from gaussian_rationals import read_rational, write_rational
from records import Tape
from ring_words import Signed, read_signed, right_shift, write_signed
from router_metadata import indices, owned
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_count, erase_marker, initialize_marker,
                     sealed_constructors)
from twiddle_setup import quotient
from words import BLANK, need


def reflected_kernel(plan, index, cache):
    if compare(index, plan.h_high.magnitude) <= 0:
        return None
    with owned(Count(plan.h_high.magnitude)) as (twice,):
        twice.multiply_small(2)
        if compare(index, twice) > 0:
            return None
        with owned(subtract(twice, index)) as (earlier,):
            cache.rewind()
            with owned(Count.product(earlier, plan.width)) as (prefix,):
                skip_bits(cache, prefix)
            value = read_signed(cache, plan.width)
            try:
                with owned(subtract(index, earlier), Count.literal(1)) as (distance, one):
                    with owned(subtract(distance, one)) as (remaining,):
                        with owned(Count.product(remaining, plan.width)) as (suffix,):
                            skip_bits(cache, suffix)
                need(cache.read() == BLANK, "complete reflected expansion kernel prefix")
                return value
            except BaseException:
                value.close()
                raise


def prepare_page(plan, target, pool):
    streams = {}
    bound = exponentials = kernel_cache = None
    exact_units = reflected = 0
    try:
        bound = Count.literal(1)
        for kind, length in (("A", plan.n), ("K", plan.nc), ("B", plan.m)):
            stream = pool.acquire()
            streams[kind] = stream
            for index in indices(length):
                with owned(plan.exponent(kind, index)) as (exponent,):
                    write_rational(exponent, stream)
                    with owned(absolute(exponent)) as (size,):
                        with owned(size.integer_part(True)) as (ceiling,):
                            if compare(ceiling.magnitude, bound) > 0:
                                following = Count(ceiling.magnitude)
                                bound.close()
                                bound = following
            stream.rewind()
        exponentials = Exponentials(plan.P, bound)
        kernel_cache = pool.acquire()
        BlockHeader.dump(plan, target)
        for kind, length in (("A", plan.n), ("K", plan.nc), ("B", plan.m)):
            stream = streams[kind]
            scale = None if kind == "K" else plan.sigma
            for index in indices(length):
                with owned(read_rational(stream)) as (exponent,):
                    if kind == "K":
                        need(not exponent.numerator.negative, "nonnegative expansion Gaussian kernel")
                    reused = reflected_kernel(plan, index, kernel_cache) if kind == "K" else None
                    if reused is not None:
                        with owned(reused):
                            write_signed(reused, target, plan.width)
                            write_signed(reused, kernel_cache, plan.width)
                        reflected += 1
                    elif exponent.numerator.magnitude.zero():
                        value = Count(plan.unit) if scale is None else right_shift(plan.unit, scale)
                        with owned(Signed(value)) as (coefficient,):
                            write_signed(coefficient, target, plan.width)
                            if kind == "K":
                                write_signed(coefficient, kernel_cache, plan.width)
                        exact_units += 1
                    else:
                        with owned(absolute(exponent)) as (argument,):
                            lower, upper = exponentials.grid_interval(argument, exponent.numerator.negative, scale)
                        with owned(Signed(lower), upper) as (coefficient, bound_upper):
                            need(compare(bound_upper, plan.unit) <= 0,
                                 "certified expansion factor within normalized unit interval")
                            write_signed(coefficient, target, plan.width)
                            if kind == "K":
                                write_signed(coefficient, kernel_cache, plan.width)
            need(stream.read() == BLANK, "complete prepared expansion factor family")
        with owned(Count(plan.alpha)) as (denominator,):
            denominator.multiply_small(2)
            with owned(Signed(quotient(plan.unit, denominator))) as (normalization,):
                need(not normalization.magnitude.zero(), "positive expansion normalization")
                write_signed(normalization, target, plan.width)
        return {"exponentials": exponentials.calls, "exact_unit_factors": exact_units,
                "reflected_kernel_factors": reflected,
                "taylor_steps": exponentials.taylor_steps, "early_stops": exponentials.early_stops}
    finally:
        if exponentials is not None:
            exponentials.close()
        if bound is not None:
            bound.close()
        for stream in streams.values():
            stream.clear()
        if kernel_cache is not None:
            kernel_cache.clear()


class Preparation:
    def __init__(self):
        self.pool = ScratchPool(256)
        self.scope = OuterScope(self.pool)
        self.parameter_pool = ScratchPool(64)
        self.parameter_scope = OuterScope(self.parameter_pool)
        self.output = Tape()
        self.closed = True
        self.calls = 0
        self.last_counts = None
        for tape in (*self.pool.tapes, *self.parameter_pool.tapes, self.output):
            erase_marker(tape)

    def run_explicit(self, s, t, alpha, radius, target_start, target_length, p, precision, sigma):
        s, t, alpha, radius, target_length, p, precision, sigma = (borrowed_count(value) for value in
            (s, t, alpha, radius, target_length, p, precision, sigma))
        target_start = Signed(borrowed_count(target_start.magnitude), target_start.negative)
        parameters = (s, t, alpha, radius, target_length, p, precision, sigma, target_start.magnitude)
        need(all(value.tape not in (*self.pool.tapes, self.output) for value in parameters),
             "external expansion preparation parameters")
        need(self.closed and not self.pool.live and self.output.read() == BLANK,
             "consume prior expansion prepared page")
        for tape in (*self.pool.tapes, self.output):
            initialize_marker(tape)
        self.closed = False
        self.last_counts = None
        plan = None
        succeeded = False
        try:
            with sealed_constructors(), self.scope.installed():
                try:
                    plan = BlockGeometry(s, t, alpha, radius, target_start, target_length, p, precision, sigma)
                    self.last_counts = prepare_page(plan, self.output, self.pool)
                    self.calls += 1
                    succeeded = True
                finally:
                    if plan is not None:
                        plan.close()
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

    def run_production(self, s, t, alpha, target_start, target_length, p):
        need(self.closed and not self.pool.live and not self.parameter_pool.live and self.output.read() == BLANK,
             "consume prior production expansion page")
        s, t, alpha, target_length, p = (borrowed_count(value) for value in (s, t, alpha, target_length, p))
        target_start = Signed(borrowed_count(target_start.magnitude), target_start.negative)
        parameters = (s, t, alpha, target_length, p, target_start.magnitude)
        need(all(value.tape not in (*self.pool.tapes, *self.parameter_pool.tapes, self.output)
                 for value in parameters), "external production expansion parameters")
        for tape in self.parameter_pool.tapes:
            initialize_marker(tape)
        plan = None
        try:
            with sealed_constructors(), self.parameter_scope.installed():
                try:
                    plan = ProductionBlock(p, alpha)
                    with self.parameter_scope.suspended():
                        return self.run_explicit(s, t, alpha, plan.radius, target_start,
                                                 target_length, p, plan.P, plan.sigma)
                finally:
                    if plan is not None:
                        plan.close()
                    for value in parameters:
                        value.rewind()
                    self.parameter_pool.empty()
        finally:
            for tape in self.parameter_pool.tapes:
                erase_marker(tape)
