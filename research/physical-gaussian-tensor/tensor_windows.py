"""Periodic monotone halo streams with bounded line and overlap buffers."""
from tensor_sources import active
active()
from cardinal_counts import Count, positive
from compact_counts import Counter, append_bits, copy_bits
from encoded import compare, subtract
from expansion_records import read_integer
from gaussian_page import skip_bits
from gaussian_rationals import read_count
from records import Tape
from ring_words import Signed, add
from router_metadata import owned
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_count, borrowed_tape, erase_marker,
                     initialize_marker, sealed_constructors)
from words import BLANK, need


def zeros(source, target, records, width, remove=False):
    with owned(Count.product(records, width)) as (bits,):
        with owned(Counter(bits)) as (remaining,):
            while not remaining.finished:
                if remove:
                    need(source.read() == 0, "zero tensor padding")
                    source.step(1)
                else:
                    target.append(0)
                remaining.decrement()


class PeriodicWindows:
    """[C][stored][R] to [C][window_count][capacity][R]."""
    def __init__(self):
        self.pool = ScratchPool(128)
        self.scope = OuterScope(self.pool)
        self.output = Tape()
        self.closed = True
        self.calls = 0
        self.last_counts = None
        for tape in (*self.pool.tapes, self.output):
            erase_marker(tape)

    def copy_records(self, source, target, records, width, counter):
        with owned(Counter(records)) as (remaining,):
            while not remaining.finished:
                copy_bits(source, target, width)
                self.last_counts[counter] += 1
                remaining.decrement()

    def skip_records(self, source, records, width, counter):
        with owned(Counter(records)) as (remaining,):
            while not remaining.finished:
                skip_bits(source, width)
                self.last_counts[counter] += 1
                remaining.decrement()

    def run(self, payload, windows, prefixes, period, stored, window_count, capacity, record_bits):
        source, windows = borrowed_tape(payload), borrowed_tape(windows)
        parameters = tuple(borrowed_count(v) for v in (prefixes, period, stored, window_count, capacity, record_bits))
        C, s, t, Q, q, R = parameters
        forbidden = (*self.pool.tapes, self.output)
        need(source is not windows and source not in forbidden and windows not in forbidden
             and all(v.tape not in forbidden for v in parameters), "external periodic-window ports")
        for value in parameters:
            positive(value)
        need(compare(s, t) <= 0, "period fits stored tensor axis")
        need(self.closed and not self.pool.live and self.output.read() == BLANK,
             "consume prior periodic-window output")
        for tape in (*self.pool.tapes, self.output):
            initialize_marker(tape)
        self.closed = False
        self.last_counts = dict(rows=0, windows=0, input_records=0, fresh_records=0,
                                overlap_records=0, initial_skipped=0, gaps_skipped=0,
                                retained_skipped=0, tail_skipped=0)
        line = triple = previous = current = source_padding = triple_length = None
        consumed = previous_start = None
        succeeded = False
        try:
            with sealed_constructors(), self.scope.installed():
                try:
                    source.rewind()
                    line, triple, previous, current = (self.pool.acquire() for _ in range(4))
                    source_padding = subtract(t, s)
                    triple_length = Count(s)
                    triple_length.multiply_small(3)
                    with owned(Counter(C)) as (rows,):
                        while not rows.finished:
                            for tape in (line, triple, previous, current):
                                borrowed_tape(tape).clear()
                            self.copy_records(source, line, s, R, "input_records")
                            zeros(source, None, source_padding, R, remove=True)
                            # Three copies cover [-s,2s). Production halos lie
                            # in this interval; each copy costs one full scan.
                            for _ in range(3):
                                append_bits(line, triple)
                            borrowed_tape(line).clear()
                            triple.rewind()
                            windows.rewind()
                            consumed = Count.literal(0)
                            with owned(Counter(Q)) as (remaining,):
                                while not remaining.finished:
                                    with owned(read_integer(windows)) as (start,):
                                        with owned(read_count(windows)) as (length,):
                                            positive(length)
                                            need(compare(length, q) <= 0, "complete halo fits its rectangular capacity")
                                            with owned(Signed(Count(s))) as (shift,):
                                                with owned(add(start, shift)) as (lifted,):
                                                    need(not lifted.negative, "periodic halo begins within triple lift")
                                                    with owned(Count(lifted.magnitude)) as (offset,):
                                                        with owned(Count(offset)) as (end,):
                                                            end.add(length)
                                                            need(compare(end, triple_length) <= 0,
                                                                 "periodic halo ends within triple lift")
                                                            need(previous_start is None or compare(previous_start, offset) <= 0,
                                                                 "monotone halo starts")
                                                            need(previous_start is None or compare(consumed, end) <= 0,
                                                                 "monotone halo ends")
                                                        borrowed_tape(current).clear()
                                                        if previous_start is None or compare(offset, consumed) >= 0:
                                                            with owned(subtract(offset, consumed)) as (gap,):
                                                                self.skip_records(triple, gap, R,
                                                                    "initial_skipped" if previous_start is None else "gaps_skipped")
                                                                consumed.add(gap)
                                                            self.copy_records(triple, current, length, R, "fresh_records")
                                                            consumed.add(length)
                                                        else:
                                                            previous.rewind()
                                                            with owned(subtract(offset, previous_start)) as (skip,):
                                                                self.skip_records(previous, skip, R, "retained_skipped")
                                                            with owned(subtract(consumed, offset)) as (overlap,):
                                                                need(compare(overlap, length) <= 0, "complete retained halo suffix")
                                                                self.copy_records(previous, current, overlap, R, "overlap_records")
                                                                need(previous.read() == BLANK, "exact retained overlap extent")
                                                                with owned(subtract(length, overlap)) as (fresh,):
                                                                    self.copy_records(triple, current, fresh, R, "fresh_records")
                                                                    consumed.add(fresh)
                                                        append_bits(current, self.output)
                                                        with owned(subtract(q, length)) as (padding,):
                                                            zeros(None, self.output, padding, R)
                                                        if previous_start is not None:
                                                            previous_start.close()
                                                        previous_start = Count(offset)
                                                        previous, current = current, previous
                                    self.last_counts["windows"] += 1
                                    remaining.decrement()
                            need(windows.read() == BLANK, "complete monotone halo descriptor extent")
                            with owned(subtract(triple_length, consumed)) as (tail,):
                                self.skip_records(triple, tail, R, "tail_skipped")
                            need(triple.read() == BLANK, "complete triple-lift source scan")
                            consumed.close()
                            consumed = None
                            previous_start.close()
                            previous_start = None
                            self.last_counts["rows"] += 1
                            rows.decrement()
                    need(source.read() == BLANK, "complete periodic-window input rectangle")
                    self.calls += 1
                    succeeded = True
                finally:
                    for value in (previous_start, consumed, triple_length, source_padding):
                        if value is not None:
                            value.close()
                    for tape in (line, triple, previous, current):
                        if tape is not None:
                            tape.clear()
                    source.rewind()
                    windows.rewind()
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


class CoreAssembly:
    """Concatenate contiguous source cores and restore the original axis pad."""
    def __init__(self):
        self.pool = ScratchPool(64)
        self.scope = OuterScope(self.pool)
        self.output = Tape()
        self.closed = True
        self.calls = 0
        for tape in (*self.pool.tapes, self.output):
            erase_marker(tape)

    def run(self, payload, cores, prefixes, period, stored, core_count, capacity, record_bits):
        source, cores = borrowed_tape(payload), borrowed_tape(cores)
        parameters = tuple(borrowed_count(v) for v in (prefixes, period, stored, core_count, capacity, record_bits))
        C, s, t, Q, q, R = parameters
        forbidden = (*self.pool.tapes, self.output)
        need(source is not cores and source not in forbidden and cores not in forbidden
             and all(v.tape not in forbidden for v in parameters), "external source-core assembly ports")
        for value in parameters:
            positive(value)
        need(compare(s, t) <= 0, "source core period fits dyadic axis")
        need(self.closed and not self.pool.live and self.output.read() == BLANK,
             "consume prior source-core assembly output")
        for tape in (*self.pool.tapes, self.output):
            initialize_marker(tape)
        self.closed = False
        succeeded = False
        try:
            with sealed_constructors(), self.scope.installed():
                try:
                    source.rewind()
                    with owned(Counter(C), subtract(t, s)) as (rows, source_padding):
                        while not rows.finished:
                            cores.rewind()
                            with owned(Count.literal(0), Counter(Q)) as (position, remaining):
                                while not remaining.finished:
                                    with owned(read_integer(cores)) as (start,):
                                        with owned(read_count(cores)) as (length,):
                                            positive(length)
                                            need(not start.negative and compare(start.magnitude, position) == 0,
                                                 "contiguous source cores in original order")
                                            need(compare(length, q) <= 0, "source core fits padded field")
                                            position.add(length)
                                            need(compare(position, s) <= 0, "source core ends within original period")
                                            with owned(Count.product(length, R), subtract(q, length)) as (bits, padding):
                                                copy_bits(source, self.output, bits)
                                                zeros(source, None, padding, R, remove=True)
                                    remaining.decrement()
                                need(compare(position, s) == 0 and cores.read() == BLANK,
                                     "complete original source-core partition")
                            zeros(None, self.output, source_padding, R)
                            rows.decrement()
                    need(source.read() == BLANK, "complete padded source-core input")
                    self.calls += 1
                    succeeded = True
                finally:
                    source.rewind()
                    cores.rewind()
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
