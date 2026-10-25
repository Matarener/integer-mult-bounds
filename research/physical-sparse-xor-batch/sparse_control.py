"""Evaluate the retained late-source word on a borrowed encoded pair list."""

from contextlib import contextmanager
from sparse_sources import active
active()
from cardinal_counts import Count, positive
from compact_control import Control
from compact_counts import (add_mod, bit_at, bit_slice, bit_xor, negate_mod,
                            power_two, read_fixed, reduced, shifted)
from encoded import compare, subtract
from session import borrowed_tape
from stream import Counter
from words import BLANK, need

# Douglas Colkitt's late-source chronology, retained by PR1673/2250/3055.
# Source packing now reads listed positions of y after shuttling u to b.
FLIP = (
    ("rotate", "y", ("u", "t"), "first_compact", 1),
    ("swap", "t", "b"),
    ("rotate", "b", ("y",), "selected_y", 1),
    ("swap", "t", "b"),
    ("rotate", "y", ("u", "t"), "second_compact", 1),
    ("swap", "t", "b"),
    ("rotate", "b", ("u", "y"), "original_compact", -1),
    ("swap", "t", "b"),
)
LOAD = (("swap", "u", "b"), ("rotate", "b", ("y",), "selected_x", 1), ("swap", "u", "b"))
UNLOAD = (("swap", "u", "b"), ("rotate", "b", ("y",), "selected_x", -1), ("swap", "u", "b"))
WORD = FLIP + LOAD + FLIP + UNLOAD


class SparseControl:
    operations = WORD
    execute_state = Control.execute_state

    def __init__(self, pairs, pair_count, position_bits, K, G):
        self.pairs = borrowed_tape(pairs)
        self.n, self.position_bits, self.K, self.G = pair_count, position_bits, K, G

    @contextmanager
    def pair(self, ordinal):
        """Read one pair with bounded scratch; nested scans share one tape."""
        self.pairs.rewind()
        distance = Count.product(ordinal, self.position_bits)
        distance.multiply_small(2)
        remaining = Counter(distance)
        distance.close()
        source = target = None
        try:
            while not remaining.finished:
                need(self.pairs.read() in (0, 1), "complete binary pair descriptor")
                self.pairs.step(1)
                remaining.decrement()
            source = read_fixed(self.pairs, self.position_bits)
            target = read_fixed(self.pairs, self.position_bits)
            yield source, target
        finally:
            if source is not None:
                source.close()
            if target is not None:
                target.close()
            remaining.close()
            self.pairs.rewind()

    def validate(self, layout):
        need(layout.names == ("u", "t", "y", "b"), "fixed sparse field schema")
        for value in (self.position_bits, self.K, self.G, layout.width("y"), layout.width("u")):
            positive(value)
        need(isinstance(self.n, Count), "encoded pair count")
        capacity = power_two(self.position_bits)
        half, one = Count(capacity), Count.literal(1)
        half.divide_small(2)
        used = Count.product(self.n, self.G)
        previous_end, index, remaining = Count.literal(0), Count.literal(0), Counter(self.n)
        try:
            need(compare(layout.width("y"), capacity) <= 0
                 and (compare(self.position_bits, one) == 0 or compare(half, layout.width("y")) < 0),
                 "canonical position field width")
            need(all(compare(layout.width(name), layout.width("u")) == 0 for name in ("t", "b"))
                 and compare(used, layout.width("u")) <= 0, "complete equal controls with active digits")
            for operation in self.operations:
                if operation[0] == "rotate":
                    need(all(layout.names.index(name) < layout.names.index(operation[1]) for name in operation[2]),
                         "sparse rotation reads only preceding fields")
            while not remaining.finished:
                with self.pair(index) as (source, target):
                    need(compare(source, layout.width("y")) < 0 and compare(target, previous_end) >= 0,
                         "bounded source and ordered disjoint target guards")
                    following = Count(target)
                    following.add(self.K)
                    previous_end.close()
                    previous_end = following
                    need(compare(previous_end, layout.width("y")) <= 0, "complete final target guard")
                    other, others = Count.literal(0), Counter(self.n)
                    try:
                        while not others.finished:
                            with self.pair(other) as (other_source, other_target):
                                need(compare(source, other_target) != 0, "source outside target set")
                                need(compare(index, other) == 0 or compare(source, other_source) != 0,
                                     "distinct sparse sources")
                            other.increment()
                            others.decrement()
                    finally:
                        other.close()
                        others.close()
                index.increment()
                remaining.decrement()
            # Re-read the end with no Python-indexed descriptor length.
            extent = Count.product(self.n, self.position_bits)
            extent.multiply_small(2)
            tail = Counter(extent)
            extent.close()
            self.pairs.rewind()
            try:
                while not tail.finished:
                    need(self.pairs.read() in (0, 1), "complete binary pair descriptor")
                    self.pairs.step(1)
                    tail.decrement()
                need(self.pairs.read() == BLANK, "exact pair descriptor extent")
            finally:
                tail.close()
        finally:
            for value in (capacity, half, one, used, previous_end, index, remaining):
                value.close()
            self.pairs.rewind()

    def selected(self, value, sources=False):
        result, index, weight = Count.literal(0), Count.literal(0), Count.literal(1)
        remaining = Counter(self.n)
        try:
            while not remaining.finished:
                with self.pair(index) as (source, target):
                    if bit_at(value, source if sources else target):
                        result.add(weight)
                following = shifted(weight, self.G)
                weight.close()
                weight = following
                index.increment()
                remaining.decrement()
            return result
        except BaseException:
            result.close()
            raise
        finally:
            for value in (index, weight, remaining):
                value.close()

    def mask(self, state, compact=False):
        result, index, position = Count.literal(0), Count.literal(0), Count.literal(0)
        remaining = Counter(self.n)
        try:
            while not remaining.finished:
                with self.pair(index) as (source, target):
                    if bit_at(state["u"] if compact else state["y"], position if compact else source):
                        weight = power_two(target)
                        try:
                            result.add(weight)
                        finally:
                            weight.close()
                index.increment()
                position.add(self.G)
                remaining.decrement()
            return result
        except BaseException:
            result.close()
            raise
        finally:
            for value in (index, position, remaining):
                value.close()

    def offset(self, state, operation, layout):
        _tag, target, _controls, kind, sign = operation
        modulus = layout.radices[target]
        result = None
        if kind in ("selected_x", "selected_y"):
            result = self.selected(state["y"], sources=kind == "selected_x")
        elif kind == "original_compact":
            mask = self.mask(state, compact=True)
            original = bit_xor(state["y"], mask)
            mask.close()
            try:
                result = self.selected(original)
            finally:
                original.close()
        else:
            need(kind in ("first_compact", "second_compact"), "fixed sparse rotation kind")
            index, position, remaining = Count.literal(0), Count.literal(0), Counter(self.n)
            one, result = Count.literal(1), Count.literal(0)
            try:
                while not remaining.finished:
                    with self.pair(index) as (_source, destination):
                        if bit_at(state["u"], position):
                            digit = bit_slice(state["t"], position, self.G)
                            negative = kind == "second_compact" and not digit.zero()
                            if kind == "first_compact":
                                term = Count(digit)
                                term.multiply_small(2)
                            elif digit.zero():
                                term = Count.literal(1)
                            else:
                                twice = Count(digit)
                                twice.multiply_small(2)
                                term = subtract(twice, one)
                                twice.close()
                            digit.close()
                            following = shifted(term, destination)
                            term.close()
                            term = reduced(following, modulus)
                            following.close()
                            if negative:
                                following = negate_mod(term, modulus)
                                term.close()
                                term = following
                            following = add_mod(result, term, modulus)
                            result.close()
                            term.close()
                            result = following
                    position.add(self.G)
                    index.increment()
                    remaining.decrement()
            except BaseException:
                result.close()
                raise
            finally:
                for value in (index, position, remaining, one):
                    value.close()
        try:
            canonical = reduced(result, modulus)
        finally:
            result.close()
        if sign < 0:
            result = negate_mod(canonical, modulus)
            canonical.close()
            canonical = result
        return canonical

    def ideal_state(self, state):
        mask = self.mask(state)
        try:
            following = bit_xor(state["y"], mask)
        finally:
            mask.close()
        state["y"].close()
        state["y"] = following

    def bad(self, state):
        if self.n.zero():
            return False
        one = Count.literal(1)
        guard_width = subtract(self.K, one)
        base, guard_radix = power_two(self.G), power_two(guard_width)
        maximum = subtract(base, one)
        lower, twice_lower = Count(base), Count(base)
        lower.multiply_small(2)
        twice_lower.multiply_small(4)
        upper = index = position = remaining = None
        try:
            if compare(guard_radix, twice_lower) <= 0:
                return True
            upper = subtract(guard_radix, lower)
            index, position, remaining = Count.literal(0), Count.literal(0), Counter(self.n)
            while not remaining.finished:
                for name in ("u", "t"):
                    digit = bit_slice(state[name], position, self.G)
                    saturated = compare(digit, maximum) == 0
                    digit.close()
                    if saturated:
                        return True
                with self.pair(index) as (_source, target):
                    start = Count(target)
                    start.increment()
                    guard = bit_slice(state["y"], start, guard_width)
                    start.close()
                    outside = compare(guard, lower) < 0 or compare(guard, upper) >= 0
                    guard.close()
                    if outside:
                        return True
                index.increment()
                position.add(self.G)
                remaining.decrement()
            return False
        finally:
            for value in (one, guard_width, base, guard_radix, maximum, lower, twice_lower,
                          upper, index, position, remaining):
                if value is not None:
                    value.close()
