"""Exact setup division with a streamed quotient and bounded small divisors."""
from tensor_sources import active
active()
from cardinal_counts import Count, positive
from encoded import compare, subtract
from session import borrowed_tape
from words import LEFT, RIGHT, need

CONTROL_BITS = 32


def small_divisor(value):
    """Return only an admitted fixed-width control; larger values stay encoded."""
    value.rewind()
    result = 0
    try:
        for position in range(CONTROL_BITS):
            symbol = value.read()
            if symbol == RIGHT:
                return result
            need(symbol in (0, 1), "binary setup divisor")
            result |= symbol << position
            value.step(1)
        return result if value.read() == RIGHT else None
    finally:
        value.rewind()


def stream_divide(numerator, denominator):
    positive(denominator)
    control = small_divisor(denominator)
    divisor = quotient = remainder = reverse = None
    try:
        quotient = Count.literal(0)
        reverse = Count.literal(0)
        borrowed_tape(quotient.tape).clear()
        borrowed_tape(reverse.tape).clear()
        if control is None:
            divisor = Count(denominator)
            remainder = Count.literal(0)
        else:
            need(0 < control < 1 << CONTROL_BITS, "positive fixed-width divisor control")
            residue = 0
        numerator.msb()
        if control is None:
            divisor.msb()
            if divisor.read() == 1:
                divisor.step(-1)
                borrowed_tape(remainder.tape).clear()
                while divisor.read() != LEFT and numerator.read() != LEFT:
                    need(divisor.read() in (0, 1), "binary setup divisor")
                    bit = numerator.read()
                    need(bit in (0, 1), "binary setup division numerator")
                    quotient.tape.append(bit)
                    reverse.tape.append(0)
                    numerator.step(-1)
                    divisor.step(-1)
                quotient.tape.append(RIGHT)
                quotient.msb()
                while quotient.read() != LEFT:
                    remainder.tape.append(quotient.read())
                    quotient.step(-1)
                quotient.step(1)
                borrowed_tape(quotient.tape).clear()
                remainder.tape.append(RIGHT)
                remainder.normalize()
            if divisor.read() == LEFT:
                divisor.step(1)
            divisor.rewind()
        while numerator.read() != LEFT:
            bit = numerator.read()
            need(bit in (0, 1), "binary setup division numerator")
            if control is None:
                remainder.multiply_small(2)
                if bit:
                    remainder.increment()
                outgoing = int(compare(remainder, divisor) >= 0)
                if outgoing:
                    following = subtract(remainder, divisor)
                    remainder.close()
                    remainder = following
            else:
                residue = 2*residue+bit
                need(0 <= residue < 1 << (CONTROL_BITS+1), "bounded setup division carry")
                outgoing = int(residue >= control)
                if outgoing:
                    residue -= control
            reverse.tape.append(outgoing)
            numerator.step(-1)
        numerator.step(1)
        reverse.tape.append(RIGHT)
        reverse.msb()
        while reverse.read() != LEFT:
            quotient.tape.append(reverse.read())
            reverse.step(-1)
        reverse.step(1)
        quotient.tape.append(RIGHT)
        quotient.normalize()
        if control is not None:
            remainder = Count.literal(0)
            borrowed_tape(remainder.tape).clear()
            for position in range(CONTROL_BITS):
                remainder.tape.append((residue >> position) & 1)
            remainder.tape.append(RIGHT)
            remainder.normalize()
        result = quotient, remainder
        quotient = remainder = None
        return result
    finally:
        for value in (reverse, remainder, quotient, divisor):
            if value is not None:
                if value.read() == LEFT:
                    value.step(1)
                value.close()
        if numerator.read() == LEFT:
            numerator.step(1)
        numerator.rewind()
        denominator.rewind()
