"""Sequential catalogue of complete real-Gaussian expansion block pages."""
from expansion_sources import active
active()
from cardinal_counts import Count
from encoded import compare, subtract
from expansion_prepare import Preparation
from expansion_records import BlockHeader, same_integer
from expansion_tile_geometry import ProductionTile, TileGeometry, TileHeader, advance
from gaussian_rationals import write_count
from records import Tape
from ring_words import Signed, difference
from router_metadata import indices, owned
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_count, erase_marker, initialize_marker,
                     sealed_constructors)
from words import BLANK, RIGHT, need


def copy_cells(source, target, length):
    for _ in indices(length):
        value = source.read()
        need(value in (0, 1, RIGHT), "complete expansion catalogue cell")
        target.append(value)
        source.step(1)


def measure_cells(source):
    result = Count.literal(0)
    source.rewind()
    try:
        while source.read() != BLANK:
            need(source.read() in (0, 1, RIGHT), "canonical expansion catalogue alphabet")
            result.increment()
            source.step(1)
        return result
    except BaseException:
        result.close()
        raise
    finally:
        source.rewind()


class TilePreparation:
    def __init__(self):
        self.block = Preparation()
        self.pool = ScratchPool(256)
        self.scope = OuterScope(self.pool)
        self.parameter_pool = ScratchPool(256)
        self.parameter_scope = OuterScope(self.parameter_pool)
        self.output = Tape()
        self.closed = True
        self.calls = 0
        self.last_counts = None
        for tape in (*self.pool.tapes, *self.parameter_pool.tapes, self.output):
            erase_marker(tape)

    def idle(self):
        need(self.block.closed and not self.block.pool.live and not self.block.parameter_pool.live
             and self.block.output.read() == BLANK, "consumed expansion catalogue child page")

    def run_explicit(self, s, t, alpha, radius, source_start, source_count, input_capacity,
                     target_start, target_length, p, precision, sigma):
        values = tuple(borrowed_count(value) for value in
            (s, t, alpha, radius, source_count, input_capacity, target_length, p, precision, sigma))
        s, t, alpha, radius, source_count, input_capacity, target_length, p, precision, sigma = values
        source_start = Signed(borrowed_count(source_start.magnitude), source_start.negative)
        target_start = Signed(borrowed_count(target_start.magnitude), target_start.negative)
        parameters = (*values, source_start.magnitude, target_start.magnitude)
        need(all(value.tape not in (*self.pool.tapes, self.output) for value in parameters),
             "external expansion tile preparation parameters")
        need(self.closed and not self.pool.live and self.output.read() == BLANK,
             "consume prior expansion tile page")
        self.idle()
        for tape in (*self.pool.tapes, self.output):
            initialize_marker(tape)
        self.closed = False
        self.last_counts = dict(blocks=0, exponentials=0, exact_unit_factors=0,
                                reflected_kernel_factors=0, taylor_steps=0, early_stops=0)
        plan = next_target = emitted = None
        succeeded = False
        try:
            with sealed_constructors(), self.scope.installed():
                try:
                    plan = TileGeometry(s, t, alpha, radius, source_start, source_count, input_capacity,
                                        target_start, target_length, p, precision, sigma)
                    TileHeader.dump(plan, self.output)
                    next_target, emitted = target_start.copy(), Count.literal(0)
                    for _ in indices(plan.blocks):
                        with owned(subtract(target_length, emitted)) as (remaining,):
                            with owned(Count(radius if compare(radius, remaining) <= 0 else remaining)) as (length,):
                                with self.scope.suspended():
                                    returned = self.block.run_explicit(s, t, alpha, radius, next_target,
                                                                       length, p, precision, sigma)
                                try:
                                    with owned(BlockHeader(returned)) as (header,):
                                        need(same_integer(header.target_start, next_target)
                                             and compare(header.m, length) == 0, "complete ordered expansion catalogue block")
                                        with owned(difference(header.source_start, source_start)) as (offset,):
                                            need(not offset.negative, "expansion block begins within source halo")
                                            with owned(Count(offset.magnitude)) as (end,):
                                                end.add(header.n)
                                                need(compare(end, source_count) <= 0,
                                                     "expansion block ends within source halo")
                                    with owned(measure_cells(returned)) as (cells,):
                                        write_count(cells, self.output)
                                        copy_cells(returned, self.output, cells)
                                        need(returned.read() == BLANK, "complete catalogue page copy")
                                    self.last_counts["blocks"] += 1
                                    for key, value in self.block.last_counts.items():
                                        self.last_counts[key] += value
                                finally:
                                    returned.clear()
                                    erase_marker(returned)
                                emitted.add(length)
                                following = advance(next_target, length)
                                next_target.close()
                                next_target = following
                    need(compare(emitted, target_length) == 0, "complete expansion catalogue target extent")
                    self.idle()
                    self.calls += 1
                    succeeded = True
                finally:
                    for value in (next_target, emitted, plan):
                        if value is not None:
                            value.close()
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

    def run_production(self, s, t, d, alpha, p, tile_index):
        need(self.closed and not self.pool.live and not self.parameter_pool.live and self.output.read() == BLANK,
             "consume prior production expansion tile page")
        parameters = tuple(borrowed_count(value) for value in (s, t, d, alpha, p, tile_index))
        need(all(value.tape not in (*self.pool.tapes, *self.parameter_pool.tapes, self.output)
                 for value in parameters), "external production expansion tile parameters")
        for tape in self.parameter_pool.tapes:
            initialize_marker(tape)
        plan = None
        try:
            with sealed_constructors(), self.parameter_scope.installed():
                try:
                    plan = ProductionTile(*parameters)
                    with self.parameter_scope.suspended():
                        return self.run_explicit(plan.s, plan.t, plan.alpha, plan.radius,
                            plan.source_start, plan.source_count, plan.input_capacity, plan.target_start,
                            plan.target_length, plan.p, plan.P, plan.sigma)
                finally:
                    if plan is not None:
                        plan.close()
                    for value in parameters:
                        value.rewind()
                    self.parameter_pool.empty()
        finally:
            for tape in self.parameter_pool.tapes:
                erase_marker(tape)
