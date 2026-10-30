"""Iterative fixed-tape Karatsuba with shrinking canonical magnitude roles."""

from ring_sources import active
active()
from cardinal_counts import Count, positive
from compact_counts import bit_slice, write_fixed
from encoded import compare, subtract
from machine import copy_symbols
from parking import FRAME_END, FiniteFields, Parking, transfer
from records import Tape
from ring_words import fits, left_shift
from router_metadata import owned
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_count, erase_marker, initialize_marker,
                     sealed_constructors)
from words import BLANK, LEFT, need


class WordProduct:
    NAMES = ("a", "b", "n", "split", "a0", "a1", "b0", "b1", "z0", "z2", "header")

    def __init__(self, leaf_bits=16):
        need(type(leaf_bits) is int and leaf_bits >= 2, "fixed contracting Karatsuba leaf")
        self.leaf_bits = leaf_bits
        self.roles = {name: Tape() for name in self.NAMES}
        self.incoming = tuple(Tape() for _ in range(3))
        self.result = Tape()
        self.output = Tape()
        self.parking = Parking(tuple(self.roles.values()))
        self.header = FiniteFields((4, 2))
        self.pool = ScratchPool(128)
        self.scope = OuterScope(self.pool)
        self.canonical = (*self.roles.values(), *self.incoming, self.result,
                          self.parking.stack, self.parking.reverse)
        self.closed = True
        self.calls = dict(nodes=0, leaves=0, parks=0, restores=0)
        for tape in (*self.canonical, *self.pool.tapes, self.output):
            erase_marker(tape)

    def c(self, name):
        value = object.__new__(Count)
        value.tape = self.roles[name]
        return value

    def result_count(self):
        value = object.__new__(Count)
        value.tape = self.result
        return value

    def save(self, value, name):
        try:
            transfer(value.tape, self.roles[name])
        finally:
            value.close()

    def finish(self, value):
        try:
            transfer(value.tape, self.result)
        finally:
            value.close()

    def clear_active(self):
        for tape in self.roles.values():
            tape.clear()

    def rearm(self):
        need(self.closed and not self.pool.live and self.output.read() == BLANK,
             "consume prior word-product output")
        for tape in (*self.canonical, *self.pool.tapes, self.output):
            need(tape.read() == BLANK, "empty word-product owned role")
            initialize_marker(tape)
        self.closed = False

    def phase(self, phase, negative=False):
        self.roles["header"].clear()
        self.header.write(self.roles["header"], (phase, int(negative)))

    def descend(self, first, second, width):
        for source, target in zip((first, second, width), self.incoming):
            copy_symbols(source.tape, target)
        self.pool.empty()
        self.parking.park()
        self.calls["parks"] += 1
        for source, name in zip(self.incoming, ("a", "b", "n")):
            transfer(source, self.roles[name])

    def enter(self):
        self.calls["nodes"] += 1
        n, a, b = self.c("n"), self.c("a"), self.c("b")
        positive(n)
        fits(a, n)
        fits(b, n)
        with owned(Count.literal(self.leaf_bits)) as (leaf,):
            small = compare(n, leaf) <= 0
        if small:
            self.finish(Count.product(a, b))
            self.clear_active()
            self.calls["leaves"] += 1
            return False
        split = Count(n)
        if split.divide_small(2):
            split.increment()
        self.save(split, "split")
        with owned(Count.literal(0)) as (zero,):
            self.save(bit_slice(a, zero, self.c("split")), "a0")
            self.save(bit_slice(a, self.c("split"), self.c("split")), "a1")
            self.save(bit_slice(b, zero, self.c("split")), "b0")
            self.save(bit_slice(b, self.c("split"), self.c("split")), "b1")
        self.roles["a"].clear()
        self.roles["b"].clear()
        self.phase(1)
        self.descend(self.c("a0"), self.c("b0"), self.c("split"))
        return True

    def has_parent(self):
        self.parking.stack.step(-1)
        symbol = self.parking.stack.read()
        self.parking.stack.step(1)
        need(symbol in (LEFT, FRAME_END), "complete Karatsuba continuation boundary")
        return symbol == FRAME_END

    def resume(self):
        self.pool.empty()
        self.parking.restore()
        self.calls["restores"] += 1
        phase, negative = self.header.read(self.roles["header"])
        if phase == 1:
            transfer(self.result, self.roles["z0"])
            self.phase(2)
            self.descend(self.c("a1"), self.c("b1"), self.c("split"))
            return True
        if phase == 2:
            transfer(self.result, self.roles["z2"])
            order_a = compare(self.c("a1"), self.c("a0"))
            order_b = compare(self.c("b1"), self.c("b0"))
            a_first, a_second = ("a1", "a0") if order_a >= 0 else ("a0", "a1")
            b_first, b_second = ("b1", "b0") if order_b >= 0 else ("b0", "b1")
            self.save(subtract(self.c(a_first), self.c(a_second)), "a")
            self.save(subtract(self.c(b_first), self.c(b_second)), "b")
            self.phase(3, (order_a < 0) != (order_b < 0))
            self.descend(self.c("a"), self.c("b"), self.c("split"))
            return True
        need(phase == 3, "three completed Karatsuba children")
        cross = Count(self.c("z0"))
        try:
            cross.add(self.c("z2"))
            if negative:
                cross.add(self.result_count())
            else:
                following = subtract(cross, self.result_count())
                cross.close()
                cross = following
            with owned(left_shift(cross, self.c("split")), Count(self.c("split"))) as (middle, high_shift):
                high_shift.multiply_small(2)
                with owned(left_shift(self.c("z2"), high_shift)) as (high,):
                    middle.add(high)
                    middle.add(self.c("z0"))
                    self.finish(Count(middle))
        finally:
            cross.close()
        self.clear_active()
        return False

    def run(self, first, second, width):
        first, second, width = (borrowed_count(value) for value in (first, second, width))
        need(all(value.tape not in (*self.canonical, *self.pool.tapes, self.output)
                 for value in (first, second, width)), "borrowed external word-product ports")
        positive(width)
        self.rearm()
        succeeded = False
        try:
            with sealed_constructors(), self.scope.installed():
                try:
                    for source, name in zip((first, second, width), ("a", "b", "n")):
                        copy_symbols(source.tape, self.roles[name])
                    entering = True
                    while True:
                        if entering:
                            entering = self.enter()
                        elif self.has_parent():
                            entering = self.resume()
                        else:
                            break
                    self.parking.empty()
                    with owned(Count(width)) as (output_width,):
                        output_width.multiply_small(2)
                        write_fixed(self.result_count(), self.output, output_width)
                    self.result.clear()
                    self.pool.empty()
                    succeeded = True
                finally:
                    for value in (first, second, width):
                        value.rewind()
                    for tape in self.canonical:
                        tape.clear()
            self.pool.empty()
        finally:
            for tape in (*self.canonical, *self.pool.tapes):
                erase_marker(tape)
            self.output.rewind()
            if not succeeded:
                self.output.clear()
                erase_marker(self.output)
            self.closed = True
        return self.output
