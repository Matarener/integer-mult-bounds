"""Actual encoded original-lower-coordinate offsets for one triangular CRT step."""
import crt_sources
crt_sources.activate()
from cardinal_counts import Count
from encoded import compare
from stream import Counter
from encoded_crt import residue, write_count
from crt_shape import Address, power_two


def compile_offsets(shape, index, factory):
    """Return B,metadata for all padded prefixes in physical lower-axis order."""
    row = shape.axis(index)
    s, _t, _width, _prefix, mu, prior_bits = row
    before = address = output = None
    try:
        before = power_two(prior_bits)
        address = Address(prior_bits, factory)
        output = factory()
        while not address.finished:
            value = position = remaining = amount = None
            valid = True
            try:
                value = Count.literal(0)
                position = Count.literal(0)
                remaining = Counter(index)
                address.msb()
                while not remaining.finished:
                    lower = shape.axis(position)
                    digit = term = None
                    try:
                        source_length, _padded, width, prefix, _inverse, _bits = lower
                        digit = address.field(width, reverse=True)
                        valid = valid and compare(digit, source_length) < 0
                        term = Count.product(digit, prefix)
                        value.add(term)
                    finally:
                        for count in (digit, term, *lower):
                            if count is not None:
                                count.close()
                    position.increment()
                    remaining.decrement()
                address.reset()
                if valid:
                    product = Count.product(value, mu)
                    try:
                        amount = residue(product, s)
                    finally:
                        product.close()
                else:
                    amount = Count.literal(0)
                output.append(int(valid))
                write_count(amount, output)
                address.increment()
            finally:
                if remaining is not None:
                    remaining.close()
                for count in (value, position, amount):
                    if count is not None:
                        count.close()
        output.rewind()
        result = before, output
        before = output = None
        return result
    finally:
        for count in row:
            count.close()
        if before is not None:
            before.close()
        if address is not None:
            address.close()
        if output is not None:
            output.clear()
