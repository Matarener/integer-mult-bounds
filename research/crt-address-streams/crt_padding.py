"""Actual source08 colex insertion/deletion with packed-address validity scans."""
import crt_sources
crt_sources.activate()
from cardinal_counts import Count, positive
from encoded import compare, subtract
from stream import Counter
from words import BLANK, need
from crt_streams import copy_record, zero_record
from encoded_crt import read_count, write_count
from crt_shape import Address


def reversed_bounds(shape, factory):
    output = one = index = remaining = None
    try:
        output = factory()
        one = Count.literal(1)
        index = subtract(shape.dimensions, one)
        remaining = Counter(shape.dimensions)
        while not remaining.finished:
            row = shape.axis(index)
            try:
                write_count(row[0], output)
                write_count(row[2], output)
            finally:
                for count in row:
                    count.close()
            remaining.decrement()
            if not remaining.finished:
                following = subtract(index, one)
                index.close()
                index = following
        output.rewind()
        result, output = output, None
        return result
    finally:
        if output is not None:
            output.clear()
        if remaining is not None:
            remaining.close()
        for count in (one, index):
            if count is not None:
                count.close()


def valid_address(shape, address, bounds):
    """One O(total address bits) bound scan, including its restoration."""
    address.reset()
    bounds.rewind()
    dimensions = Counter(shape.dimensions)
    valid = True
    try:
        while not dimensions.finished:
            source_length = width = digit = None
            try:
                source_length = read_count(bounds)
                width = read_count(bounds)
                digit = address.field(width)
                valid = valid and compare(digit, source_length) < 0
                dimensions.decrement()
            finally:
                for count in (source_length, width, digit):
                    if count is not None:
                        count.close()
        need(bounds.read() == BLANK, 'complete compact CRT bounds')
        return valid
    finally:
        dimensions.close()
        bounds.rewind()
        address.reset()


def padded(source, shape, rows, record_bits, factory, remove=False, natural=False):
    """Compact records <-> padded records in colex or natural axis order."""
    need(type(remove) is bool, 'literal CRT padding direction')
    need(type(natural) is bool, 'literal CRT padding axis order')
    positive(rows)
    positive(record_bits)
    output = address = outer = private_bounds = None
    source.rewind()
    try:
        output = factory()
        if natural:
            private_bounds = reversed_bounds(shape, factory)
        bounds = private_bounds if natural else shape.bounds
        outer = Counter(rows)
        while not outer.finished:
            address = Address(shape.bits, factory)
            while not address.finished:
                if valid_address(shape, address, bounds):
                    copy_record(source, output, record_bits)
                else:
                    zero_record(source, output, record_bits, remove)
                address.increment()
            address.close()
            address = None
            outer.decrement()
        need(source.read() == BLANK, 'complete CRT padding source extent')
        output.rewind()
        result, output = output, None
        return result
    finally:
        source.rewind()
        if address is not None:
            address.close()
        if outer is not None:
            outer.close()
        if output is not None:
            output.clear()
        if private_bounds is not None:
            private_bounds.clear()
