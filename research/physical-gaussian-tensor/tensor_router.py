"""Complete full-support permutations through capped physical router batches."""
from tensor_sources import active
active()
from cardinal_counts import Count, positive
from compact_counts import Counter, append_bits, copy_bits, read_fixed
from compact_streams import stable_radix
from encoded import compare
from fourier_plan import batch_limit
from records import Tape
from retuned_native import build_native
from ring_words import power_two
from router_engine import Router
from router_metadata import Pairs, factor, owned, write_pair
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_count, borrowed_tape, erase_marker,
                     initialize_marker, sealed_constructors)
from words import BLANK, need


class FullRouter:
    def __init__(self, native=None):
        self.router = Router(build_native() if native is None else native)
        self.pool = ScratchPool(256)
        self.scope = OuterScope(self.pool)
        self.output = Tape()
        self.closed = True
        self.current = None
        self.calls = 0
        self.last_counts = None
        for tape in (*self.pool.tapes, self.output):
            erase_marker(tape)

    def idle(self):
        self.router.idle_child()
        need(self.router.closed and not self.router.pool.live and self.router.output.read() == BLANK,
             "consumed full-support router child return")

    def route(self, descriptor, edges, n, p, width, record_bits, rows):
        sorted_descriptor = stable_radix(descriptor, width, width, self.pool.acquire)
        returned = replacement = None
        try:
            with owned(Count(edges)) as (support,):
                support.multiply_small(2)
                with self.scope.suspended():
                    returned = self.router.run(borrowed_tape(self.current), borrowed_tape(sorted_descriptor),
                        *(borrowed_count(v) for v in (n, p, support, width, record_bits, rows)))
                replacement = self.pool.acquire()
                append_bits(returned, replacement)
                self.current.clear()
                self.current, replacement = replacement, None
                self.current.rewind()
                self.last_counts["batches"] += 1
                self.last_counts[self.router.last_mode] = self.last_counts.get(self.router.last_mode, 0)+1
        finally:
            if replacement is not None:
                replacement.clear()
            if returned is not None:
                returned.clear()
                erase_marker(returned)
            sorted_descriptor.clear()

    def run(self, payload, descriptor, n, precision, count, width, record_bits, rows):
        source, pairs = borrowed_tape(payload), borrowed_tape(descriptor)
        parameters = tuple(borrowed_count(v) for v in (n, precision, count, width, record_bits, rows))
        n, p, k, width, R, C = parameters
        forbidden = (*self.pool.tapes, self.output, *self.router.pool.tapes, self.router.output)
        need(source is not pairs and source not in forbidden and pairs not in forbidden
             and all(v.tape not in forbidden for v in parameters), "external full-support router ports")
        for value in (n, p, width, R, C):
            positive(value)
        need(self.closed and not self.pool.live and self.output.read() == BLANK,
             "consume prior full-support router output")
        self.idle()
        for tape in (*self.pool.tapes, self.output):
            initialize_marker(tape)
        self.closed = False
        self.last_counts = dict(batches=0, edges=0, involutions=0)
        first = second = first_count = second_count = limit = batch = None
        succeeded = False
        try:
            with sealed_constructors(), self.scope.installed():
                try:
                    with owned(Count.literal(2)) as (two,):
                        need(compare(p, two) >= 0, "full-support router precision at least two")
                    table = Pairs(pairs, k, width)
                    table.validate(n)
                    self.current = self.pool.acquire()
                    source.rewind()
                    with owned(power_two(n)) as (addresses,):
                        with owned(Count.product(addresses, R)) as (row_bits,):
                            with owned(Counter(C)) as (remaining,):
                                while not remaining.finished:
                                    copy_bits(source, self.current, row_bits)
                                    remaining.decrement()
                    need(source.read() == BLANK, "complete full-support router rectangle")
                    self.current.rewind()
                    limit = batch_limit(p)
                    positive(limit)
                    first, second = self.pool.acquire(), self.pool.acquire()
                    first_count, second_count = factor(table, first, second, self.pool.acquire)
                    for matching, matching_count in ((first, first_count), (second, second_count)):
                        matching.rewind()
                        with owned(Counter(matching_count)) as (remaining,):
                            edges = None
                            try:
                                edges = Count.literal(0)
                                while not remaining.finished:
                                    if batch is None:
                                        batch = self.pool.acquire()
                                    with owned(read_fixed(matching, width)) as (a,):
                                        with owned(read_fixed(matching, width)) as (b,):
                                            write_pair(batch, a, b, width)
                                            write_pair(batch, b, a, width)
                                    edges.increment()
                                    remaining.decrement()
                                    self.last_counts["edges"] += 1
                                    if compare(edges, limit) == 0 or remaining.finished:
                                        descriptor_owned, batch = batch, None
                                        self.route(descriptor_owned, edges, n, p, width, R, C)
                                        edges.close()
                                        edges = None
                                        edges = Count.literal(0)
                            finally:
                                if edges is not None:
                                    edges.close()
                        need(matching.read() == BLANK, "complete full-support matching")
                        self.last_counts["involutions"] += 1
                    self.idle()
                    append_bits(self.current, self.output)
                    self.calls += 1
                    succeeded = True
                finally:
                    for value in (first_count, second_count, limit):
                        if value is not None:
                            value.close()
                    for tape in (batch, first, second, self.current):
                        if tape is not None:
                            tape.clear()
                    self.current = None
                    source.rewind()
                    pairs.rewind()
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
