"""Natural-axis metadata and modular twiddle exponents on encoded Count tapes."""

from fourier_sources import active
active()
from cardinal_counts import Count, positive
from compact_counts import bit_at, bit_slice, negate_mod, power_two, shifted
from encoded import compare, subtract
from router_metadata import indices, owned, position_width
from words import BLANK, need


def batch_limit(precision):
    """Return 2^floor(.997 floor(log2 precision)) using only encoded arithmetic."""
    with owned(Count(precision), Count.literal(1), Count.literal(0)) as (remaining, one, logarithm):
        while compare(remaining, one) > 0:
            remaining.divide_small(2)
            logarithm.increment()
        logarithm.multiply_small(997)
        logarithm.divide_small(1000)
        return power_two(logarithm)


class FourierPlan:
    def __init__(self, flags, axes, ell, precision, rows):
        self.flags, self.axes, self.ell, self.p, self.rows = flags, axes, ell, precision, rows
        self.fields = {}

    def keep(self, name, value):
        need(name not in self.fields, "one Fourier numerical role")
        self.fields[name] = value
        return value

    def __getattr__(self, name):
        return self.fields[name]

    def compile(self):
        positive(self.axes)
        positive(self.rows)
        with owned(Count.literal(2)) as (two,):
            need(compare(self.ell, two) >= 0 and compare(self.p, two) >= 0,
                 "Fourier precision and coefficient logarithm at least two")
        self.keep("n", Count.literal(0))
        self.flags.rewind()
        try:
            with owned(Count.literal(1), Count(self.ell)) as (one, length):
                # Reuse one encoded axis length; no decoded dimension or flags list.
                for _ in indices(self.axes):
                    bit = self.flags.read()
                    need(bit in (0, 1), "complete binary Fourier axis flags")
                    self.flags.step(1)
                    self.n.add(length)
                    if bit == 0:
                        smaller = subtract(self.n, one)
                        self.n.close()
                        self.fields["n"] = smaller
                need(self.flags.read() == BLANK, "exact Fourier axis descriptor extent")
        finally:
            self.flags.rewind()
        self.keep("P", Count(self.p))
        self.P.add(self.n)
        self.keep("width", position_width(self.n))
        self.keep("cap", batch_limit(self.P))
        self.keep("r", power_two(self.ell))
        self.keep("addresses", power_two(self.n))
        self.keep("small", Count(self.p))
        self.small.increment()
        self.small.increment()
        self.keep("wide", Count(self.P))
        self.wide.increment()
        self.wide.increment()
        with owned(Count.product(self.addresses, self.r)) as (fields,):
            self.keep("gaussians", Count.product(fields, self.rows))
        self.keep("record_bits", Count.product(self.wide, self.r))
        self.record_bits.multiply_small(2)

    def flag_at(self, ordinal):
        self.flags.rewind()
        try:
            for _ in indices(ordinal):
                need(self.flags.read() in (0, 1), "complete axis flag prefix")
                self.flags.step(1)
            bit = self.flags.read()
            need(bit in (0, 1), "named axis flag")
            return bit
        finally:
            self.flags.rewind()

    def natural_axes(self):
        """Visit axes from the right, yielding increasing LSB offsets."""
        with owned(Count.literal(0), Count.literal(1)) as (offset, one):
            with owned(subtract(self.axes, one)) as (last,):
                for ordinal in indices(self.axes):
                    with owned(subtract(last, ordinal)) as (index,):
                        length = Count(self.ell) if self.flag_at(index) else subtract(self.ell, one)
                        try:
                            yield offset, length
                            offset.add(length)
                        finally:
                            length.close()

    def exponent(self, address, h, opposite):
        need(type(opposite) is bool and compare(h, self.ell) < 0, "compiled Fourier direction and round")
        with owned(Count.literal(0), Count.literal(0), Count(h)) as (total, zero, residue_bits):
            residue_bits.increment()
            for offset, length in self.natural_axes():
                if compare(h, length) < 0:
                    with owned(Count(offset)) as (position,):
                        position.add(h)
                        if bit_at(address, position):
                            with owned(bit_slice(address, offset, h)) as (lower,):
                                total.add(lower)
            with owned(bit_slice(total, zero, residue_bits), subtract(self.ell, h)) as (residue, shift):
                result = shifted(residue, shift)
        if opposite:
            return result
        try:
            with owned(Count(self.r)) as (modulus,):
                modulus.multiply_small(2)
                return negate_mod(result, modulus)
        finally:
            result.close()

    def close(self):
        for value in reversed(tuple(self.fields.values())):
            value.close()
        self.fields.clear()
        self.flags.rewind()
