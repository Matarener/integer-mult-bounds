"""Exact fixed-width old-bit/new-bit descriptors for the FullRouter port."""
import crt_sources
crt_sources.activate()
from cardinal_counts import Count, positive
from encoded import subtract
from stream import Counter
from words import RIGHT, need


def position_width(value):
    positive(value)
    one = Count.literal(1)
    current = result = None
    try:
        current = subtract(value, one)
        result = Count.literal(0)
        while not current.zero():
            current.divide_small(2)
            result.increment()
        if result.zero():
            result.increment()
        answer, result = result, None
        return answer
    finally:
        for count in (one, current, result):
            if count is not None:
                count.close()


def write_fixed(value, output, width):
    positive(width)
    counter = Counter(width)
    value.rewind()
    try:
        while not counter.finished:
            symbol = value.read()
            need(symbol in (0, 1, RIGHT), 'bounded router descriptor integer')
            output.append(0 if symbol == RIGHT else symbol)
            if symbol != RIGHT:
                value.step(1)
            counter.decrement()
        need(value.read() == RIGHT, 'router descriptor position fits')
    finally:
        value.rewind()
        counter.close()


def compile_descriptor(shape, factory, inverse=False):
    """Colex axes -> natural axes, or its separately sorted inverse map.

    Each axis retains its internal bit order. Unequal-width field reversal
    need not be an involution as a permutation of the fixed bit positions.
    """
    need(type(inverse) is bool, 'literal CRT descriptor direction')
    output = width = one = index = remaining = None
    try:
        output = factory()
        width = position_width(shape.bits)
        one = Count.literal(1)
        index = subtract(shape.dimensions, one) if inverse else Count.literal(0)
        remaining = Counter(shape.dimensions)
        while not remaining.finished:
            row = shape.axis(index)
            _s, _t, bits, _P, _mu, old_base = row
            new_base = leading = bit = loop = None
            try:
                leading = subtract(shape.bits, old_base)
                new_base = subtract(leading, bits)
                first_base, second_base = (new_base, old_base) if inverse else (old_base, new_base)
                bit = Count.literal(0)
                loop = Counter(bits)
                while not loop.finished:
                    first = second = None
                    try:
                        first = Count(first_base)
                        second = Count(second_base)
                        first.add(bit)
                        second.add(bit)
                        write_fixed(first, output, width)
                        write_fixed(second, output, width)
                    finally:
                        for count in (first, second):
                            if count is not None:
                                count.close()
                    bit.increment()
                    loop.decrement()
                remaining.decrement()
                if not remaining.finished:
                    if inverse:
                        following = subtract(index, one)
                        index.close()
                        index = following
                    else:
                        index.increment()
            finally:
                if loop is not None:
                    loop.close()
                for count in (*row, new_base, leading, bit):
                    if count is not None:
                        count.close()
        output.rewind()
        result = output, width
        output = width = None
        return result
    finally:
        if output is not None:
            output.clear()
        if remaining is not None:
            remaining.close()
        for count in (width, one, index):
            if count is not None:
                count.close()
