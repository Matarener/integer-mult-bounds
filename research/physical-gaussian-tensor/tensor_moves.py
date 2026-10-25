"""Move one short mixed-radix field across complete arbitrary spectators."""
from tensor_sources import active
active()
from cardinal_counts import Count, positive
from compact_counts import Counter, append_bits, copy_bits
from records import Tape
from ring_words import power_two
from root_streams import RowPadding
from router_metadata import ceiling_log, owned
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_count, borrowed_tape, erase_marker,
                     initialize_marker, sealed_constructors)
from words import BLANK, need


class FieldMove:
    """[C][A][q][R bits] to [C][q][A][R bits], or its exact inverse."""
    def __init__(self):
        self.padding = RowPadding()
        self.pool = ScratchPool(64)
        self.scope = OuterScope(self.pool)
        self.output = Tape()
        self.closed = True
        self.calls = 0
        self.last_counts = None
        for tape in (*self.pool.tapes, self.output):
            erase_marker(tape)

    def idle(self):
        need(self.padding.closed and not self.padding.pool.live and self.padding.output.read() == BLANK,
             "consumed mixed-radix padding return")

    def pad(self, source, destination, prefixes, q, Q, width, remove):
        with self.scope.suspended():
            returned = self.padding.run(source, prefixes, q, Q, width, remove)
        try:
            append_bits(returned, destination)
        finally:
            returned.clear()
            erase_marker(returned)

    def stage(self, source, target, zero, one, prefixes, spectator, suffix, right):
        source.rewind()
        with owned(Counter(prefixes), Count.product(spectator, suffix)) as (rows, half):
            while not rows.finished:
                borrowed_tape(zero).clear()
                borrowed_tape(one).clear()
                if right:
                    copy_bits(source, zero, half)
                    copy_bits(source, one, half)
                    zero.rewind()
                    one.rewind()
                with owned(Counter(spectator)) as (records,):
                    while not records.finished:
                        if right:
                            copy_bits(zero, target, suffix)
                            copy_bits(one, target, suffix)
                        else:
                            copy_bits(source, zero, suffix)
                            copy_bits(source, one, suffix)
                        self.last_counts["complete_blocks"] += 2
                        records.decrement()
                if right:
                    need(zero.read() == one.read() == BLANK, "complete mixed-radix interleave halves")
                else:
                    append_bits(zero, target)
                    append_bits(one, target)
                self.last_counts["prefixes"] += 1
                rows.decrement()
        need(source.read() == BLANK, "complete mixed-radix stage input")
        self.last_counts["interleaves" if right else "splits"] += 1

    def run(self, payload, prefixes, spectator, field, record_bits, right=False):
        need(type(right) is bool, "compiled mixed-radix direction")
        source = borrowed_tape(payload)
        parameters = tuple(borrowed_count(v) for v in (prefixes, spectator, field, record_bits))
        C, A, q, R = parameters
        forbidden = (*self.pool.tapes, self.output, *self.padding.pool.tapes, self.padding.output)
        need(source not in forbidden and all(v.tape not in forbidden for v in parameters),
             "external mixed-radix ports")
        for value in parameters:
            positive(value)
        need(self.closed and not self.pool.live and self.output.read() == BLANK,
             "consume prior mixed-radix output")
        self.idle()
        for tape in (*self.pool.tapes, self.output):
            initialize_marker(tape)
        self.closed = False
        self.last_counts = dict(splits=0, interleaves=0, prefixes=0, complete_blocks=0)
        logarithm = Q = outer = width = current = following = zero = one = stage_prefixes = suffix = passes = None
        succeeded = False
        try:
            with sealed_constructors(), self.scope.installed():
                try:
                    logarithm = ceiling_log(q)
                    Q = power_two(logarithm)
                    outer = Count.product(C, A)
                    width = Count.product(A, R)
                    current, following, zero, one = (self.pool.acquire() for _ in range(4))
                    self.pad(source, current, C if right else outer, q, Q, width if right else R, False)
                    current.rewind()
                    stage_prefixes, suffix = Count(C), Count(R)
                    if not logarithm.zero():
                        with owned(Count(Q)) as (half,):
                            need(half.divide_small(2) == 0, "dyadic mixed-radix half extent")
                            if right:
                                stage_prefixes.close()
                                stage_prefixes = Count.product(C, half)
                            else:
                                suffix.close()
                                suffix = Count.product(half, R)
                    passes = Counter(logarithm)
                    while not passes.finished:
                        borrowed_tape(following).clear()
                        self.stage(current, following, zero, one, stage_prefixes, A, suffix, right)
                        borrowed_tape(current).clear()
                        current, following = following, current
                        current.rewind()
                        passes.decrement()
                        if not passes.finished:
                            if right:
                                need(stage_prefixes.divide_small(2) == 0, "exact inverse prefix halving")
                                suffix.multiply_small(2)
                            else:
                                stage_prefixes.multiply_small(2)
                                need(suffix.divide_small(2) == 0, "exact forward suffix halving")
                    self.pad(current, self.output, outer if right else C, q, Q, R if right else width, True)
                    self.idle()
                    self.calls += 1
                    succeeded = True
                finally:
                    for value in (passes, suffix, stage_prefixes, width, outer, Q, logarithm):
                        if value is not None:
                            value.close()
                    for tape in (current, following, zero, one):
                        if tape is not None:
                            tape.clear()
                    source.rewind()
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
