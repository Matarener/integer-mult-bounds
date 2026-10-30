"""Paid n-bit boundary around a completed CRT/Tensor Sandwich child.

Produced by Nick Petalas. Apache-2.0.
Load only inside the authenticated physical Tape cohort.
"""
from cardinal_counts import Count, positive
from encoded import divide, subtract
from records import Tape
from router_metadata import owned
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_count, borrowed_tape, erase_marker,
                     initialize_marker, sealed_constructors)
from stream import Counter
from words import BLANK, LEFT, need


def validate_bits(source, length):
    """Read exactly length cells; the next cell must be the terminator."""
    source.rewind()
    try:
        with owned(Counter(length)) as (remaining,):
            while not remaining.finished:  # At most the encoded length.
                need(source.read() in (0, 1), "exact binary input extent")
                source.step(1)
                remaining.decrement()
        need(source.read() == BLANK, "no extra input cells")
    finally:
        source.rewind()


def pack(source, length, padding, target):
    """Reverse a validated MSB-first operand, then append high zeroes."""
    validate_bits(source, length)
    with owned(Counter(length)) as (remaining,):
        while not remaining.finished:
            source.step(1)
            remaining.decrement()
    source.step(-1)
    try:
        with owned(Counter(length)) as (remaining,):
            while not remaining.finished:
                target.append(source.read())
                source.step(-1)
                remaining.decrement()
        need(source.read() == LEFT, "complete reversed input")
        source.step(1)
        with owned(Counter(padding)) as (remaining,):
            while not remaining.finished:
                target.append(0)
                remaining.decrement()
        target.rewind()
    finally:
        # The LEFT case occurs if a later target append fails.
        if source.read() == LEFT:
            source.step(1)
        source.rewind()


def normalize(source, discarded, length, target):
    """Check the high zero prefix and copy the exact requested return."""
    source.rewind()
    with owned(Counter(discarded)) as (remaining,):
        while not remaining.finished:
            need(source.read() == 0, "zero discarded product prefix")
            source.step(1)
            remaining.decrement()
    with owned(Counter(length)) as (remaining,):
        while not remaining.finished:
            symbol = source.read()
            need(symbol in (0, 1), "exact binary product extent")
            target.append(symbol)
            source.step(1)
            remaining.decrement()
    need(source.read() == BLANK, "no extra product cells")
    target.rewind()


class ArbitraryBits:
    """Own fixed boundary banks and borrow one completed Sandwich child.

    The child exposes private, output, closed, pending, run and consume.
    It must restore all borrowed ports and clear its own work on failure.
    It retains responsibility for catalogue admission and exact recovery.
    """

    def __init__(self, child):
        need(child.closed and not child.pending, "idle completed child")
        self.child = child
        self.pool = ScratchPool(32)
        self.scope = OuterScope(self.pool)
        self.packed = (Tape(), Tape())
        self.output = Tape()
        self.resident = (*self.pool.tapes, *self.packed, self.output)
        self.private = (*self.resident, *child.private)
        need(len({id(t) for t in self.private}) == len(self.private),
             "disjoint boundary and child inventories")
        for tape in self.resident:
            erase_marker(tape)
        self.closed = True
        self.pending = False

    def preflight(self, first, second, catalogue, n, b):
        need(self.closed and not self.pending and not self.pool.live,
             "consume prior boundary return")
        need(self.child.closed and not self.child.pending, "idle completed child")
        need(isinstance(n, Count) and isinstance(b, Count), "encoded n and b")
        ports = tuple(borrowed_tape(t) for t in
                      (first, second, catalogue, n.tape, b.tape))
        need(len({id(t) for t in ports}) == 5, "five distinct boundary ports")
        need(all(all(t is not private for private in self.private) for t in ports),
             "external boundary ports")
        return ports

    def invoke(self, first, second, catalogue, n, b):
        """Run with the metadata pool installed; release every child return."""
        with owned(*divide(n, b)) as (q, remainder):
            if not remainder.zero():
                q.increment()
            with owned(Count.product(q, b)) as (padded,):
                with owned(subtract(padded, n), Count(n)) as (padding, twice_n):
                    with owned(Count(padding)) as (discarded,):
                        twice_n.multiply_small(2)
                        discarded.multiply_small(2)
                        for source, target in zip((first, second), self.packed):
                            pack(source, n, padding, target)
                        try:
                            with self.scope.suspended():
                                result = self.child.run(*self.packed, catalogue, b, q)
                            need(result is self.child.output and self.child.pending,
                                 "completed borrowed child return")
                            normalize(result, discarded, twice_n, self.output)
                        finally:
                            if self.child.pending:
                                with self.scope.suspended():
                                    self.child.consume()

    def run(self, first, second, catalogue, n, b):
        ports = self.preflight(first, second, catalogue, n, b)
        first, second, catalogue = ports[:3]
        n, b = borrowed_count(n), borrowed_count(b)
        positive(n)
        positive(b)
        for tape in self.resident:
            initialize_marker(tape)
        self.closed = False
        succeeded = False
        try:
            with sealed_constructors(), self.scope.installed():
                try:
                    self.invoke(first, second, catalogue, n, b)
                    succeeded = True
                finally:
                    for tape in (first, second, catalogue):
                        tape.rewind()
                    n.rewind()
                    b.rewind()
                    for tape in self.packed:
                        tape.clear()
                    for lease in tuple(self.pool.live.values()):
                        lease.clear()
                    self.pool.empty()
        finally:
            for tape in (*self.pool.tapes, *self.packed):
                erase_marker(tape)
            self.output.rewind()
            if not succeeded:
                self.output.clear()
                erase_marker(self.output)
            self.closed = True
        self.pending = True
        return self.output

    def consume(self):
        """Clear the borrowed 2n-bit return, including its owned marker."""
        need(self.closed and self.pending, "pending boundary return")
        self.output.clear()
        erase_marker(self.output)
        self.pending = False
