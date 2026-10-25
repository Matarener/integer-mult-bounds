"""Signed data words with linear scans on the shared canonical binary tapes.

Count supplies the binary carrier, copy, addition and comparison primitives.
Unbounded online products use the separate recursive word engine.
"""

from ring_sources import active
active()
from cardinal_counts import Count, positive
from compact_counts import bit_at, read_fixed, write_fixed
from encoded import compare, subtract
from router_metadata import indices, owned
from session import borrowed_tape
from words import RIGHT, need


def left_shift(value, amount):
    result = Count.literal(0)
    borrowed_tape(result.tape).clear()
    value.rewind()
    try:
        for _ in indices(amount):
            result.tape.append(0)
        while value.read() != RIGHT:
            bit = value.read()
            need(bit in (0, 1), "canonical shifted data digit")
            result.tape.append(bit)
            value.step(1)
        result.tape.append(RIGHT)
        result.normalize()
        return result
    except BaseException:
        result.close()
        raise
    finally:
        value.rewind()


def right_shift(value, amount):
    result = Count.literal(0)
    borrowed_tape(result.tape).clear()
    value.rewind()
    try:
        for _ in indices(amount):
            if value.read() != RIGHT:
                need(value.read() in (0, 1), "canonical discarded data digit")
                value.step(1)
        while value.read() != RIGHT:
            bit = value.read()
            need(bit in (0, 1), "canonical retained data digit")
            result.tape.append(bit)
            value.step(1)
        result.tape.append(RIGHT)
        result.normalize()
        return result
    except BaseException:
        result.close()
        raise
    finally:
        value.rewind()


def power_two(amount):
    with owned(Count.literal(1)) as (one,):
        return left_shift(one, amount)


def fits(value, width):
    """Validate a declared unsigned extent without decoding it."""
    positive(width)
    value.rewind()
    with owned(Count.literal(0)) as (length,):
        try:
            while value.read() != RIGHT:
                need(value.read() in (0, 1), "canonical data-word digit")
                length.increment()
                value.step(1)
            need(compare(length, width) <= 0, "data magnitude fits declared word width")
        finally:
            value.rewind()


class Signed:
    def __init__(self, magnitude, negative=False):
        need(isinstance(magnitude, Count) and type(negative) is bool, "encoded magnitude and finite sign")
        self.magnitude = magnitude
        self.negative = negative and not magnitude.zero()

    def close(self):
        self.magnitude.close()

    def copy(self):
        return Signed(Count(self.magnitude), self.negative)

    def negated(self):
        return Signed(Count(self.magnitude), not self.negative)


def add(left, right):
    if left.negative == right.negative:
        result = Count(left.magnitude)
        try:
            result.add(right.magnitude)
            return Signed(result, left.negative)
        except BaseException:
            result.close()
            raise
    order = compare(left.magnitude, right.magnitude)
    if order >= 0:
        return Signed(subtract(left.magnitude, right.magnitude), left.negative)
    return Signed(subtract(right.magnitude, left.magnitude), right.negative)


def difference(left, right):
    with owned(right.negated()) as (negative,):
        return add(left, negative)


def scaled(value, amount):
    return Signed(left_shift(value.magnitude, amount), value.negative)


def truncate(value, amount):
    return Signed(right_shift(value.magnitude, amount), value.negative)


def nearest(value, amount):
    positive(amount)
    result = right_shift(value.magnitude, amount)
    try:
        with owned(Count.literal(1)) as (one,):
            with owned(subtract(amount, one)) as (position,):
                if bit_at(value.magnitude, position):
                    result.increment()
        return Signed(result, value.negative)
    except BaseException:
        result.close()
        raise


def read_signed(source, width):
    positive(width)
    raw = read_fixed(source, width)
    try:
        with owned(Count.literal(1)) as (one,):
            with owned(subtract(width, one)) as (sign_position,):
                negative = bool(bit_at(raw, sign_position))
        if not negative:
            result, raw = raw, None
            return Signed(result)
        with owned(power_two(width)) as (modulus,):
            return Signed(subtract(modulus, raw), True)
    finally:
        if raw is not None:
            raw.close()


def write_signed(value, destination, width):
    positive(width)
    with owned(Count.literal(1)) as (one,):
        with owned(subtract(width, one)) as (sign_position,):
            with owned(power_two(sign_position)) as (limit,):
                order = compare(value.magnitude, limit)
                need(order <= 0 if value.negative else order < 0, "signed data-word headroom")
    if value.negative:
        with owned(power_two(width)) as (modulus,):
            with owned(subtract(modulus, value.magnitude)) as (encoded,):
                write_fixed(encoded, destination, width)
    else:
        write_fixed(value.magnitude, destination, width)
