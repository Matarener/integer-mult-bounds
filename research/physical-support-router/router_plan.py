"""Compile the complete router into one binary instruction tape."""

from router_sources import active
active()
from cardinal_counts import Count, positive
from compact_counts import append_bits, read_fixed, reduced, write_fixed
from compact_streams import stable_radix
from encoded import compare, subtract
from router_metadata import (Pairs, block_image, ceiling_log, factor, indices,
                             owned, position_width, untouched_gap, write_pair)
from session import borrowed_tape
from words import BLANK, need

END, SWAP, GROUP, UNGROUP, CNOT, BATCH = range(6)


def opcode(tape, value):
    for shift in (0, 1, 2):
        tape.append((value >> shift) & 1)


def read_opcode(tape):
    result = 0
    for shift in (0, 1, 2):
        bit = tape.read()
        need(bit in (0, 1), "complete binary router opcode")
        result |= bit << shift
        tape.step(1)
    need(result <= BATCH, "fixed router instruction vocabulary")
    return result


class Plan:
    def __init__(self, n, p, k, width, factory, policy="standard"):
        need(policy in ("standard", "fixture-g1-k5"), "compiled router guard policy")
        positive(n)
        with owned(Count.literal(2)) as (two,):
            need(compare(p, two) >= 0, "router precision at least two")
        self.n, self.p, self.k, self.width = n, p, k, width
        self.factory, self.policy = factory, policy
        self.fields = {}  # Fixed vocabulary, independent of numerical inputs.
        self.program = factory()
        self.mode = "uncompiled"
        l = self.keep("l", ceiling_log(p))
        self.keep("ell", Count.product(l, l))
        G = self.keep("G", Count(l) if policy == "standard" else Count.literal(1))
        if policy == "standard":
            G.multiply_small(4)
            with owned(Count.literal(6)) as (six,):
                G.add(six)
        K = self.keep("K", Count(G) if policy == "standard" else Count.literal(5))
        if policy == "standard":
            K.multiply_small(64)

    def keep(self, name, value):
        need(name not in self.fields, "one fixed router metadata role")
        self.fields[name] = value
        return value

    def __getattr__(self, name):
        return self.fields[name]

    def emit(self, op, *values):
        opcode(self.program, op)
        for value in values:
            write_fixed(value, self.program, self.width)

    def placement(self, reservoir, slot):
        with owned(Count(self.H)) as (distance,):
            if 3*reservoir+slot+1 > 1:
                distance.multiply_small(3*reservoir+slot+1)
            source = subtract(self.N, distance)
            if slot == 2:
                target = Count.literal(0)
            else:
                with owned(Count(self.H)) as (front,):
                    if slot:
                        front.multiply_small(slot+1)
                    target = subtract(self.N, front)
        return (source, target) if compare(source, target) <= 0 else (target, source)

    def placed(self, position, reservoir):
        current = Count(position)
        try:
            for slot in range(3):
                with owned(*self.placement(reservoir, slot)) as (a, b):
                    following = block_image(current, a, b, self.H)
                current.close()
                current = following
            result, current = current, None
            return result
        finally:
            if current is not None:
                current.close()

    def avoids(self, a, b, reservoir):
        with owned(Count(self.H) if reservoir else Count.literal(0), Count(self.H)) as (high_distance, low_distance):
            if reservoir:
                high_distance.multiply_small(3*reservoir)
            low_distance.multiply_small(3*reservoir+3)
            with owned(subtract(self.N, low_distance), subtract(self.N, high_distance)) as (low, high):
                return all(compare(x, low) < 0 or compare(x, high) >= 0 for x in (a, b))

    def cohort(self, table, reservoir):
        result, count = self.factory(), Count.literal(0)
        try:
            for index in indices(table.count):
                with table.at(index) as (a, b):
                    selected = None
                    for choice in range(3):
                        if self.avoids(a, b, choice):
                            selected = choice
                            break
                    need(selected is not None, "an edge avoids one reservoir")
                    if selected == reservoir:
                        with owned(self.placed(a, reservoir), self.placed(b, reservoir)) as (pa, pb):
                            with owned(subtract(pa, self.H), subtract(pb, self.H)) as (ya, yb):
                                need(compare(ya, self.Y) < 0 and compare(yb, self.Y) < 0,
                                     "reindexed edge lies in middle field")
                                write_pair(result, ya, yb, self.y_width)
                        count.increment()
            result.rewind()
            return result, count
        except BaseException:
            result.clear()
            count.close()
            raise

    def guarded(self, target):
        with owned(Count(target)) as (end,):
            end.add(self.K)
            return compare(end, self.Y) <= 0

    def stage(self, table, reverse):
        for color in indices(self.K):
            temporary, count = self.factory(), Count.literal(0)
            sorted_pairs = None
            try:
                for index in indices(table.count):
                    with table.at(index) as (a, b):
                        source, target = (b, a) if reverse else (a, b)
                        if self.guarded(target):
                            with owned(reduced(target, self.K)) as (residue,):
                                if compare(residue, color) == 0:
                                    # Sort only metadata, with target as the key.
                                    write_pair(temporary, target, source, self.y_width)
                                    count.increment()
                if not count.zero():
                    temporary.rewind()
                    sorted_pairs = stable_radix(temporary, self.y_width, self.y_width, self.factory)
                    temporary = None
                    self.emit(BATCH, count)
                    for _ in indices(count):
                        with owned(read_fixed(sorted_pairs, self.y_width),
                                   read_fixed(sorted_pairs, self.y_width)) as (target, source):
                            write_pair(self.program, source, target, self.y_width)
                    need(sorted_pairs.read() == BLANK, "complete sorted batch metadata")
            finally:
                if temporary is not None:
                    temporary.clear()
                if sorted_pairs is not None:
                    sorted_pairs.clear()
                count.close()
        for index in indices(table.count):
            with table.at(index) as (a, b):
                source, target = (b, a) if reverse else (a, b)
                if not self.guarded(target):
                    with owned(Count(source), Count(target)) as (s, t):
                        s.add(self.H)
                        t.add(self.H)
                        self.emit(CNOT, s, t)

    def matching(self, table):
        for reservoir in range(3):
            edges, count = self.cohort(table, reservoir)
            try:
                if count.zero():
                    continue
                for slot in range(3):
                    with owned(*self.placement(reservoir, slot)) as (a, b):
                        if compare(a, b) != 0:
                            self.emit(SWAP, a, b, self.H)
                # a ^= b, b ^= a, a ^= b, with a/b labels chosen by the table.
                view = Pairs(edges, count, self.y_width)
                for reverse in (True, False, True):
                    self.stage(view, reverse)
                for slot in reversed(range(3)):
                    with owned(*self.placement(reservoir, slot)) as (a, b):
                        if compare(a, b) != 0:
                            self.emit(SWAP, a, b, self.H)
            finally:
                edges.clear()
                count.close()

    def compile(self, pairs):
        need(self.mode == "uncompiled", "compile router once")
        table = Pairs(pairs, self.k, self.width)
        if table.validate(self.n):
            self.mode = "identity"
            self.emit(END)
            self.program.rewind()
            return
        with owned(Count(self.k)) as (half,):
            half.divide_small(2)
            self.keep("H", Count.product(half, self.G))
        positive(self.H)
        fast = compare(self.n, self.ell) > 0
        if fast:
            self.keep("N", subtract(self.n, self.ell))
            with owned(Count(self.H)) as (required,):
                required.multiply_small(10)
                fast = compare(self.N, required) >= 0
        if fast:
            gap = untouched_gap(table, self.n, self.ell)
            fast = gap is not None
            if fast:
                self.keep("U", gap)
        conjugated = first = second = None
        counts = None
        try:
            if fast:
                self.mode = "fast"
                with owned(Count(self.H)) as (controls,):
                    controls.multiply_small(3)
                    self.keep("Y", subtract(self.N, controls))
                self.keep("y_width", position_width(self.Y))
                conjugated = self.factory()
                with owned(Count.literal(0)) as (zero,):
                    self.emit(SWAP, zero, self.U, self.ell)
                    for index in indices(self.k):
                        with table.at(index) as (a, b):
                            with owned(block_image(a, zero, self.U, self.ell),
                                       block_image(b, zero, self.U, self.ell)) as (pa, pb):
                                with owned(subtract(pa, self.ell), subtract(pb, self.ell)) as (sa, sb):
                                    write_pair(conjugated, sa, sb, self.width)
                conjugated.rewind()
                table = Pairs(conjugated, self.k, self.width)
                self.emit(GROUP)
            else:
                self.mode = "literal"
            first, second = self.factory(), self.factory()
            counts = factor(table, first, second, self.factory)
            for tape, count in zip((first, second), counts):
                view = Pairs(tape, count, self.width)
                if fast:
                    self.matching(view)
                else:
                    for index in indices(count):
                        with view.at(index) as (a, b), owned(Count.literal(1)) as (one,):
                            left, right = (a, b) if compare(a, b) < 0 else (b, a)
                            self.emit(SWAP, left, right, one)
            if fast:
                self.emit(UNGROUP)
                with owned(Count.literal(0)) as (zero,):
                    self.emit(SWAP, zero, self.U, self.ell)
            self.emit(END)
            self.program.rewind()
        finally:
            for tape in (conjugated, first, second):
                if tape is not None:
                    tape.clear()
            if counts is not None:
                for count in counts:
                    count.close()
            pairs.rewind()

    def close(self):
        self.program.clear()
        for value in self.fields.values():
            value.close()
