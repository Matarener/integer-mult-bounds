"""Whole target tiles with a monotone source stream and two short overlap banks."""
from expansion_sources import active
active()
from cardinal_counts import Count, positive
from compact_counts import copy_bits
from encoded import compare, subtract
from expansion_block import Block
from expansion_records import BlockHeader, same_integer
from expansion_tile_geometry import TileHeader, advance
from expansion_tile_prepare import copy_cells
from fft_arithmetic import Arithmetic
from gaussian_page import skip_bits
from gaussian_rationals import read_count
from records import Tape
from ring_words import difference, read_signed
from router_metadata import indices, owned
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_tape, erase_marker, initialize_marker,
                     sealed_constructors)
from words import BLANK, need


class Tile:
    def __init__(self):
        self.block = Block()
        self.word = self.block.word
        self.pool = ScratchPool(256)
        self.scope = OuterScope(self.pool)
        self.arithmetic = Arithmetic(self.word, self.scope)
        self.output = Tape()
        self.closed = True
        self.calls = 0
        self.last_counts = None
        for tape in (*self.pool.tapes, self.output):
            erase_marker(tape)

    def idle(self):
        self.block.idle()
        need(self.block.closed and not self.block.pool.live and self.block.output.read() == BLANK,
             "consumed expansion tile child return")

    def norm(self, real, imaginary, header):
        with owned(self.arithmetic.multiply(real, real, header.input_width)) as (first,):
            with owned(self.arithmetic.multiply(imaginary, imaginary, header.input_width)) as (second,):
                first.magnitude.add(second.magnitude)
                need(compare(first.magnitude, header.norm_bound) <= 0, "expansion tile disk-grid input")

    def validate(self, source, header):
        source.rewind()
        try:
            for index in indices(header.input_capacity):
                with owned(read_signed(source, header.input_width)) as (real,):
                    with owned(read_signed(source, header.input_width)) as (imaginary,):
                        self.norm(real, imaginary, header)
                        if compare(index, header.source_count) >= 0:
                            need(real.magnitude.zero() and imaginary.magnitude.zero(), "zero expansion source padding")
                        self.last_counts["validation_records"] += 1
            need(source.read() == BLANK, "complete padded expansion source extent")
        finally:
            source.rewind()

    def copy_records(self, source, target, length, width, counter):
        for _ in indices(length):
            copy_bits(source, target, width)
            self.last_counts[counter] += 1

    def skip_records(self, source, length, width, counter):
        for _ in indices(length):
            skip_bits(source, width)
            self.last_counts[counter] += 1

    def run(self, page, source):
        page, source = borrowed_tape(page), borrowed_tape(source)
        forbidden = (*self.pool.tapes, self.output, *self.block.pool.tapes, self.block.output,
                     *self.block.convolution.pool.tapes, self.block.convolution.output,
                     *self.word.pool.tapes, self.word.output, *self.word.canonical)
        need(page is not source and page not in forbidden and source not in forbidden,
             "external expansion tile ports")
        need(self.closed and not self.pool.live and self.output.read() == BLANK,
             "consume prior expansion tile output")
        self.idle()
        for tape in (*self.pool.tapes, self.output):
            initialize_marker(tape)
        self.closed = False
        self.last_counts = dict(blocks=0, validation_records=0, fresh_records=0,
                                overlap_records=0, initial_skipped=0, tail_skipped=0)
        plan = block_page = previous = current = previous_offset = consumed = emitted = next_target = None
        succeeded = False
        try:
            with sealed_constructors(), self.scope.installed():
                try:
                    page.rewind()
                    plan = TileHeader(page)
                    self.validate(source, plan)
                    block_page, previous, current = (self.pool.acquire() for _ in range(3))
                    consumed, emitted, next_target = Count.literal(0), Count.literal(0), plan.target_start.copy()
                    for _ in indices(plan.blocks):
                        borrowed_tape(block_page).clear()
                        with owned(read_count(page)) as (cells,):
                            positive(cells)
                            copy_cells(page, block_page, cells)
                        block_page.rewind()
                        with owned(BlockHeader(block_page)) as (header,):
                            for name in ("s", "t", "alpha", "radius", "p", "P", "sigma"):
                                need(compare(getattr(header, name), getattr(plan, name)) == 0,
                                     "one global expansion tile axis and precision")
                            need(same_integer(header.target_start, next_target), "ordered expansion target blocks")
                            with owned(subtract(plan.target_length, emitted)) as (remaining,):
                                wanted = plan.radius if compare(plan.radius, remaining) <= 0 else remaining
                                need(compare(header.m, wanted) == 0, "complete or clipped final expansion block")
                            with owned(difference(header.source_start, plan.source_start)) as (offset,):
                                need(not offset.negative, "expansion source block begins in supplied halo")
                                with owned(Count(offset.magnitude)) as (end,):
                                    end.add(header.n)
                                    need(compare(end, plan.source_count) <= 0,
                                         "expansion source block ends in supplied halo")
                                borrowed_tape(current).clear()
                                if previous_offset is None:
                                    self.skip_records(source, offset.magnitude, plan.record_width, "initial_skipped")
                                    consumed.add(offset.magnitude)
                                    self.copy_records(source, current, header.n, plan.record_width, "fresh_records")
                                    consumed.add(header.n)
                                else:
                                    need(compare(previous_offset, offset.magnitude) <= 0
                                         and compare(offset.magnitude, consumed) <= 0,
                                         "monotone overlapping expansion source windows")
                                    previous.rewind()
                                    with owned(subtract(offset.magnitude, previous_offset)) as (skip,):
                                        with owned(Count.product(skip, plan.record_width)) as (bits,):
                                            skip_bits(previous, bits)
                                    with owned(subtract(consumed, offset.magnitude)) as (overlap,):
                                        need(compare(overlap, header.n) <= 0,
                                             "monotone expansion source right endpoints")
                                        self.copy_records(previous, current, overlap, plan.record_width, "overlap_records")
                                        need(previous.read() == BLANK, "complete retained expansion overlap")
                                        with owned(subtract(header.n, overlap)) as (fresh,):
                                            self.copy_records(source, current, fresh, plan.record_width, "fresh_records")
                                            consumed.add(fresh)
                                current.rewind()
                                block_page.rewind()
                                with self.scope.suspended():
                                    returned = self.block.run(block_page, current)
                                try:
                                    with owned(Count.product(header.m, plan.record_width)) as (bits,):
                                        copy_bits(returned, self.output, bits)
                                    need(returned.read() == BLANK, "complete expansion block return in tile")
                                finally:
                                    returned.clear()
                                    erase_marker(returned)
                                if previous_offset is not None:
                                    previous_offset.close()
                                previous_offset = Count(offset.magnitude)
                                previous, current = current, previous
                            emitted.add(header.m)
                            following = advance(next_target, header.m)
                            next_target.close()
                            next_target = following
                            self.last_counts["blocks"] += 1
                    with owned(subtract(plan.input_capacity, consumed)) as (tail,):
                        self.skip_records(source, tail, plan.record_width, "tail_skipped")
                    need(source.read() == page.read() == BLANK and compare(emitted, plan.target_length) == 0,
                         "complete streamed expansion tile and catalogue")
                    self.idle()
                    self.calls += 1
                    succeeded = True
                finally:
                    for value in (block_page, previous, current):
                        if value is not None:
                            value.clear()
                    for value in (previous_offset, consumed, emitted, next_target, plan):
                        if value is not None:
                            value.close()
                    page.rewind()
                    source.rewind()
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
