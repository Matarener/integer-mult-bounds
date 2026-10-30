"""Encoded Count-to-word boundary, derived from PR2809 PhysicalArena.

The logical caller allocates managed checker objects. No physical C0 claim.
"""

from contextlib import ExitStack, contextmanager
from dataclasses import dataclass

import strict_selector
from cardinal_counts import Count
from records import Tape
from words import BLANK, ONE, RIGHT, ZERO, Arena, Meter, Ring, Word, need


class TapeWord:
    def __init__(self, arena, slot):
        self.arena, self.slot, self.tape = arena, slot, Tape()

    @property
    def head(self):
        return self.tape.head

    @property
    def cells(self):
        return self.tape.cells

    def read(self):
        return self.tape.read()

    def write(self, symbol):
        self.tape.write(symbol)

    def step(self, direction):
        self.tape.step(direction)

    rewind, msb, zero, erase = Word.rewind, Word.msb, Word.zero, Word.erase


class EncodedArena(Arena):
    def __init__(self, maximum):
        self.capacity, self.meter = 256, Meter()
        self.words, self.available, self.live = [], [], set()
        self.template = TapeWord(self, -1)
        maximum.rewind()
        try:
            while maximum.read() != RIGHT:
                need(maximum.read() in (ZERO, ONE), "binary template bound")
                self.template.write(ZERO)
                self.template.step(1)
                maximum.step(1)
            self.template.write(ZERO)
            self.template.step(1)
            self.template.write(RIGHT)
            self.template.rewind()
        finally:
            maximum.rewind()

    def zero(self):
        if not self.available:
            need(len(self.words) < self.capacity, "bounded numerical roles")
            self.available.append(len(self.words))
            self.words.append(TapeWord(self, len(self.words)))
        return super().zero()

    def load(self, value):
        result = self.zero()
        value.rewind()
        try:
            while value.read() != RIGHT:
                need(result.read() != RIGHT, "encoded input fits template")
                result.write(value.read())
                result.step(1)
                value.step(1)
            need(result.read() != RIGHT, "one high zero margin")
            result.rewind()
            return result
        except BaseException:
            self.free(result)
            raise
        finally:
            value.rewind()

    def close(self):
        need(not self.live, "all numerical words released")
        self.template.erase()
        need(self.template.read() == BLANK, "template erased")


def ring(value, work):
    arena = EncodedArena(value)
    work.callback(arena.close)
    modulus = arena.load(value)
    work.callback(arena.free, modulus)
    result = Ring(modulus)
    work.callback(result.close)
    return result


def power(exponent, q, work):
    base = Count.literal(q)
    try:
        result = strict_selector.power(base, exponent)
    finally:
        base.close()
    work.callback(result.close)
    return result


@dataclass(frozen=True)
class Geometry:
    atoms: object
    ring: object
    high: object
    remainder: object
    gap: Count
    suffix: Count


@contextmanager
def fitted(plan, q, spectators, suffix):
    with ExitStack() as work:
        atom = ring(power(plan["width"], q, work), work)
        high = ring(plan["rows"], work)
        residual = power(plan["remainder"], q, work)
        tail = None if plan["remainder"].zero() else ring(residual, work)
        # Retained NODE uses literal 64 and fixed labels up to 128.
        # Its consumer must fit all index intermediates below this bound.
        maximum = Count(plan["body"])
        work.callback(maximum.close)
        maximum.increment()
        maximum.multiply_small(128)
        indices = EncodedArena(maximum)
        work.callback(indices.close)
        atoms = indices.load(plan["body"])
        work.callback(indices.free, atoms)
        partial = Count.product(residual, spectators)
        work.callback(partial.close)
        gap = Count.product(partial, plan["rows"])
        end = Count.product(residual, suffix)
        work.callback(gap.close)
        work.callback(end.close)
        yield Geometry(atoms, atom, high, tail, gap, end)
