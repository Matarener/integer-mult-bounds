# SPDX-License-Identifier: Apache-2.0
"""Encoded root reservations and precision for PR2287's layer construction."""
import cohort
cohort.activate()
from cardinal_counts import Count, positive
from compact_counts import power_two
from encoded import atom_width, compare, divide, fixed_power, subtract
from machine import copy_symbols
from records import Tape
from scratch_pool import ScratchPool
from session import OuterScope, sealed_constructors
from stream import Counter
from words import RIGHT, need


def floor_power(value, numerator, denominator):
    need(type(numerator) is int and type(denominator) is int and
         0 < numerator <= denominator, "fixed fractional exponent")
    ceiling = atom_width(value, numerator, denominator)
    target = fixed_power(value, numerator)
    cap = Count(target)
    cap.increment()
    power = one = None
    try:
        # Saturating at target would confuse a strict overshoot with equality.
        power = fixed_power(ceiling, denominator, cap)
        need(compare(power, target) >= 0, "upper integral root")
        if compare(power, target) > 0:
            one = Count.literal(1)
            return subtract(ceiling, one)
        return Count(ceiling)
    finally:
        for item in (ceiling, target, cap, power, one):
            if item is not None:
                item.close()


def ceil_log2(value):
    positive(value)
    digits = Count.literal(0)
    ones = 0
    value.rewind()
    try:
        while value.read() != RIGHT:
            bit = value.read()
            need(bit in (0, 1), "canonical logarithm digits")
            ones = min(2, ones + bit)
            digits.increment()
            value.step(1)
        if ones == 1:
            one = Count.literal(1)
            try:
                return subtract(digits, one)
            finally:
                one.close()
        return Count(digits)
    finally:
        value.rewind()
        digits.close()


def ceil_divide(numerator, denominator):
    quotient, remainder = divide(numerator, denominator)
    try:
        if not remainder.zero():
            quotient.increment()
        return quotient
    except BaseException:
        quotient.close()
        raise
    finally:
        remainder.close()


def coarse_depth(width, dimension, maximum_rank):
    current = Count(width)
    threshold = Count.literal(dimension)
    result = Count.literal(0)
    try:
        while compare(current, threshold) >= 0:
            current.divide_small(dimension)
            if maximum_rank > 1:
                current.multiply_small(maximum_rank)
            result.increment()
        return result
    except BaseException:
        result.close()
        raise
    finally:
        current.close()
        threshold.close()


FIELDS = ("precision", "selected", "left", "right", "coefficients", "outer_rows", "residue", "zero",
          "d", "K", "G", "H", "depth", "q0", "qF", "qB", "Q0", "delta",
          "input_bits", "work_bits", "gaussians", "prefixes", "original_rows",
          "padded_rows", "stock", "row_bits", "core_width", "core_front", "core_back")


class RootPlan:
    def __init__(self, dimension, maximum_rank, level_divisor, guard_exponent=210000):
        need(type(dimension) is int and 2 <= dimension <= 73 and
             type(maximum_rank) is int and 0 < maximum_rank < dimension and
             type(level_divisor) is int and level_divisor > 1 and
             type(guard_exponent) is int and guard_exponent >= 0, "fixed root construction constants")
        self.dimension, self.maximum_rank, self.level_divisor = dimension, maximum_rank, level_divisor
        self.guard_exponent = guard_exponent
        self.roles = {name: Tape() for name in FIELDS}
        self.pool = ScratchPool(256)
        self.scope = OuterScope(self.pool)
        self.fast = False
        self.closed = True

    def count(self, name):
        value = object.__new__(Count)
        value.tape = self.roles[name]
        return value

    def clear(self):
        need(not self.pool.live, "closed root planning scratch")
        for tape in self.roles.values():
            tape.clear()
        self.closed = True

    def compute(self, precision, selected, left, right, coefficients, outer_rows, residue):
        need(self.closed and not self.pool.live, "closed root planning entry")
        self.clear()
        self.closed = False
        inputs = dict(precision=precision, selected=selected, left=left, right=right,
                      coefficients=coefficients, outer_rows=outer_rows, residue=residue)
        need(all(isinstance(v, Count) for v in inputs.values()), "encoded root inputs")
        for name, value in inputs.items():
            copy_symbols(value.tape, self.roles[name])
        owned = []  # A fixed number of compiled expression results, independent of input widths.

        def keep(value):
            owned.append(value)
            return value

        def literal(value):
            return keep(Count.literal(value))

        def plus(*values, constant=0):
            result = literal(constant)
            for value in values:
                result.add(value)
            return result

        def times(a, b):
            return keep(Count.product(a, b))

        def scaled(value, constant):
            if constant == 0:
                return literal(0)
            result = keep(Count(value))
            if constant > 1:
                result.multiply_small(constant)
            return result

        def save(name, value):
            copy_symbols(value.tape, self.roles[name])
            return value

        try:
            with sealed_constructors(), self.scope.installed():
                save("zero", literal(0))
                two = literal(2)
                need(compare(precision, two) >= 0, "root precision at least two")
                positive(coefficients)
                positive(outer_rows)
                d = save("d", keep(floor_power(precision, 997, 1000)))
                need(compare(selected, d) <= 0, "selected width within root domain")
                K = save("K", keep(floor_power(d, 1, 500)))
                need(compare(residue, K) < 0, "selected root residue")
                logarithm = keep(ceil_log2(precision))
                G = save("G", plus(scaled(logarithm, 4), constant=6))
                H = save("H", times(d, G))
                depth = save("depth", keep(coarse_depth(d, self.dimension, self.maximum_rank)))
                q0 = save("q0", scaled(depth, (self.level_divisor - 1).bit_length()))
                qF = save("qF", keep(ceil_divide(scaled(H, 2), K)))
                qB = save("qB", keep(ceil_divide(H, K)))
                Q0 = save("Q0", plus(q0, qF, qB))
                delta = save("delta", scaled(d, 1 << self.guard_exponent))
                save("input_bits", plus(precision, constant=2))
                work_bits = save("work_bits", plus(precision, scaled(delta, 2), constant=3))
                active_bits = times(selected, K)
                addresses = keep(power_two(plus(left, active_bits, right)))
                save("gaussians", times(times(addresses, coefficients), outer_rows))
                self.fast = compare(selected, Q0) > 0
                if self.fast:
                    save("core_width", keep(subtract(selected, Q0)))
                    save("core_front", keep(subtract(times(qF, K), scaled(H, 2))))
                    save("core_back", plus(keep(subtract(times(qB, K), H)), right))
                    row_axes = times(q0, K)
                    original_rows = save("original_rows", keep(power_two(row_axes)))
                    prefix_count = save("prefixes", times(outer_rows, keep(power_two(left))))
                    stock = literal(1)
                    repetitions = keep(Counter(depth))
                    while not repetitions.finished:
                        stock.multiply_small(self.level_divisor)
                        repetitions.decrement()
                    save("stock", stock)
                    multiples = keep(ceil_divide(original_rows, stock))
                    save("padded_rows", times(multiples, stock))
                    rectangle = plus(keep(subtract(active_bits, row_axes)), right)
                    row_gaussians = times(keep(power_two(rectangle)), coefficients)
                    save("row_bits", scaled(times(row_gaussians, work_bits), 2))
                else:
                    for name in ("core_width", "core_front", "core_back", "row_bits"):
                        save(name, literal(0))
                    for name in ("prefixes", "original_rows", "padded_rows", "stock"):
                        save(name, literal(1))
        except BaseException:
            for tape in self.roles.values():
                tape.clear()
            raise
        finally:
            for value in reversed(owned):
                value.close()
            self.pool.empty()
            self.closed = True
        return self
