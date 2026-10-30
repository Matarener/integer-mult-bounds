"""Encode arbitrary-support exposure and persistent Gaussian record geometry."""

from contextlib import contextmanager
from composed_sources import active
active()
from cardinal_counts import Count, positive
from compact_counts import read_fixed, write_fixed
from compact_streams import stable_radix
from encoded import compare, subtract
from root_plan import floor_power
from router_metadata import (Pairs, block_image, ceiling_log, indices, owned,
                             position_width, untouched_gap, write_pair)
from words import BLANK, need


class Positions:
    def __init__(self, tape, count, width):
        self.tape, self.count, self.width = tape, count, width

    @contextmanager
    def at(self, ordinal):
        self.tape.rewind()
        value = None
        try:
            with owned(Count.product(ordinal, self.width)) as (distance,):
                for _ in indices(distance):
                    need(self.tape.read() in (0, 1), "complete selected-position prefix")
                    self.tape.step(1)
            value = read_fixed(self.tape, self.width)
            yield value
        finally:
            if value is not None:
                value.close()
            self.tape.rewind()

    def find(self, value):
        for index in indices(self.count):
            with self.at(index) as item:
                if compare(item, value) == 0:
                    return Count(index)
        return None

    def contains(self, value):
        found = self.find(value)
        if found is None:
            return False
        found.close()
        return True

    def difference_at(self, other, ordinal):
        with owned(Count.literal(0)) as (rank,):
            for index in indices(self.count):
                with self.at(index) as value:
                    if not other.contains(value):
                        if compare(rank, ordinal) == 0:
                            return Count(value)
                        rank.increment()
        raise ValueError("complete selected/target complement bijection")

    def validate(self, n):
        positive(n)
        need(isinstance(self.count, Count) and isinstance(self.width, Count), "encoded selected descriptor")
        with owned(position_width(n)) as (width,):
            need(compare(width, self.width) == 0, "canonical selected-position width")
        need(compare(self.count, n) <= 0, "selected count fits full rectangle")
        previous = None
        try:
            for index in indices(self.count):
                with self.at(index) as value:
                    need(compare(value, n) < 0, "selected coordinate inside rectangle")
                    need(previous is None or compare(previous, value) < 0, "sorted distinct selected coordinates")
                    if previous is not None:
                        previous.close()
                    previous = Count(value)
            self.tape.rewind()
            with owned(Count.product(self.count, self.width)) as (extent,):
                for _ in indices(extent):
                    need(self.tape.read() in (0, 1), "complete selected descriptor")
                    self.tape.step(1)
            need(self.tape.read() == BLANK, "exact selected descriptor extent")
        finally:
            if previous is not None:
                previous.close()
            self.tape.rewind()


def extend(sources, targets, n, output):
    """Map S_i to T_i and pair the sorted unused domains and images."""
    count = Count.literal(0)
    try:
        with owned(Count.literal(0)) as (extra,):
            # Visit address coordinates, never the exponentially many records.
            for coordinate in indices(n):
                source_index = sources.find(coordinate)
                if source_index is not None:
                    try:
                        with targets.at(source_index) as target:
                            write_pair(output, coordinate, target, sources.width)
                        count.increment()
                    finally:
                        source_index.close()
                elif targets.contains(coordinate):
                    with owned(sources.difference_at(targets, extra)) as (target,):
                        write_pair(output, coordinate, target, sources.width)
                    extra.increment()
                    count.increment()
        output.rewind()
        return count
    except BaseException:
        count.close()
        raise


class ExposurePlan:
    def __init__(self, n, p, g, width, factory, policy="standard"):
        need(policy in ("standard", "fixture-ell1"), "compiled persistent-record policy")
        self.n, self.p, self.g, self.width = n, p, g, width
        self.factory, self.policy = factory, policy
        self.fields = {}  # Fixed numerical vocabulary.
        self.forward = self.inverse = None
        self.mode = "uncompiled"

    def keep(self, name, value):
        need(name not in self.fields, "one composition numerical role")
        self.fields[name] = value
        return value

    def __getattr__(self, name):
        return self.fields[name]

    def compile(self, positions):
        need(self.mode == "uncompiled", "compile one support exposure")
        selected = Positions(positions, self.g, self.width)
        selected.validate(self.n)
        with owned(Count.literal(2)) as (two,):
            need(compare(self.p, two) >= 0, "composition precision at least two")
        if self.g.zero():
            self.mode = "identity"
            return
        with owned(floor_power(self.p, 997, 1000)) as (limit,):
            need(compare(self.g, limit) <= 0, "selected width inside actual-root domain")
        self.mode = "literal"
        with owned(ceiling_log(self.p)) as (logarithm,):
            self.keep("ell", Count.product(logarithm, logarithm)
                      if self.policy == "standard" else Count.literal(1))
        self.keep("K", floor_power(self.g, 1, 500))
        self.keep("span", Count.product(self.g, self.K))
        if compare(self.n, self.ell) <= 0:
            return
        self.keep("N", subtract(self.n, self.ell))
        if compare(self.span, self.N) > 0:
            return
        target_tape, permutation = self.factory(), self.factory()
        count = None
        forward = inverse = None
        try:
            with owned(Count(self.ell)) as (target,):
                for _ in indices(self.g):
                    write_fixed(target, target_tape, self.width)
                    target.add(self.K)
            target_tape.rewind()
            targets = Positions(target_tape, self.g, self.width)
            count = extend(selected, targets, self.n, permutation)
            table = Pairs(permutation, count, self.width)
            table.validate(self.n)
            gap = untouched_gap(table, self.n, self.ell)
            if gap is None:
                return
            self.keep("U", gap)
            self.keep("count", count)
            count = None
            self.keep("prefix_width", position_width(self.N))
            self.keep("left", subtract(self.N, self.span))
            forward, inverse = self.factory(), self.factory()
            with owned(Count.literal(0)) as (zero,):
                for index in indices(self.count):
                    with table.at(index) as (old, new):
                        with owned(block_image(old, zero, self.U, self.ell),
                                   block_image(new, zero, self.U, self.ell)) as (placed_old, placed_new):
                            with owned(subtract(placed_old, self.ell), subtract(placed_new, self.ell)) as (a, b):
                                write_pair(forward, a, b, self.prefix_width)
                                write_pair(inverse, b, a, self.prefix_width)
            forward.rewind()
            inverse.rewind()
            self.forward = stable_radix(forward, self.prefix_width, self.prefix_width, self.factory)
            forward = None
            self.inverse = stable_radix(inverse, self.prefix_width, self.prefix_width, self.factory)
            inverse = None
            Pairs(self.forward, self.count, self.prefix_width).validate(self.N)
            Pairs(self.inverse, self.count, self.prefix_width).validate(self.N)
            self.mode = "composed"
        finally:
            target_tape.clear()
            permutation.clear()
            if count is not None:
                count.close()
            if forward is not None:
                forward.clear()
            if inverse is not None:
                inverse.clear()
            positions.rewind()

    def close(self):
        for tape in (self.forward, self.inverse):
            if tape is not None:
                tape.clear()
        for value in self.fields.values():
            value.close()
