"""All-size raw signed polynomial rotations with fixed reusable packet buffers."""

from fourier_sources import active
active()
from cardinal_counts import Count
from compact_counts import bit_at, bit_slice, copy_bits
from encoded import subtract
from router_metadata import indices, owned
from session import borrowed_tape
from stream import Counter
from words import BLANK, need


def component(source, target, width, negative, buffer):
    """Adapt the retained signed_phase rule to one reusable LSB component buffer."""
    lower_zero = True
    sign = 0
    with owned(Counter(width)) as (remaining,):
        while not remaining.finished:
            bit = source.read()
            need(bit in (0, 1), "complete Fourier Gaussian component")
            source.step(1)
            buffer.append(bit)
            remaining.decrement()
            if remaining.finished:
                sign = bit
            else:
                lower_zero = lower_zero and bit == 0
    try:
        need(not (negative and sign and lower_zero), "Fourier signed negation headroom")
        buffer.rewind()
        carry = 1
        with owned(Counter(width)) as (remaining,):
            while not remaining.finished:
                bit = buffer.read()
                need(bit in (0, 1), "complete Fourier component buffer")
                if negative:
                    value = 1-bit+carry
                    target.append(value & 1)
                    carry = value >> 1
                else:
                    target.append(bit)
                buffer.step(1)
                remaining.decrement()
        need(buffer.read() == BLANK, "exact Fourier component buffer extent")
    finally:
        borrowed_tape(buffer).clear()


def emit(source, target, coefficients, width, negative, buffer):
    source.rewind()
    for _ in indices(coefficients):
        component(source, target, width, negative, buffer)
        component(source, target, width, negative, buffer)
    need(source.read() == BLANK, "exact Fourier rotation segment")


def diagonal(source, plan, h, opposite, factory):
    """Consume an owned packet and return the exact J_h packet in natural order."""
    output, prefix, suffix, buffer = (factory() for _ in range(4))
    source.rewind()
    try:
        with owned(Count.literal(0)) as (zero,):
            for _ in indices(plan.rows):
                for address in indices(plan.addresses):
                    with owned(plan.exponent(address, h, opposite)) as (exponent,):
                        negative = bool(bit_at(exponent, plan.ell))
                        with owned(bit_slice(exponent, zero, plan.ell)) as (tail,):
                            with owned(subtract(plan.r, tail)) as (front,):
                                with owned(Count.product(front, plan.wide),
                                           Count.product(tail, plan.wide)) as (front_bits, tail_bits):
                                    front_bits.multiply_small(2)
                                    tail_bits.multiply_small(2)
                                    copy_bits(source, prefix, front_bits)
                                    copy_bits(source, suffix, tail_bits)
                                emit(suffix, output, tail, plan.wide, not negative, buffer)
                                emit(prefix, output, front, plan.wide, negative, buffer)
                    borrowed_tape(prefix).clear()
                    borrowed_tape(suffix).clear()
        need(source.read() == BLANK, "complete Fourier diagonal packet")
        source.clear()
        output.rewind()
        return output
    except BaseException:
        output.clear()
        raise
    finally:
        prefix.clear()
        suffix.clear()
        buffer.clear()
