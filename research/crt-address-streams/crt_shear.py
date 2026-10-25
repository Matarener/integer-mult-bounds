"""Complete variable-offset CRT field rotations with protected padding tails."""
import crt_sources
crt_sources.activate()
from cardinal_counts import positive
from encoded import compare, subtract
from crt_streams import copy_rows
from stream import Counter
from words import BLANK, need
from encoded_crt import read_offset


def shifted(source, offsets, before, modulus, padded, suffix, factory, inverse=False):
    """Borrow B*t*S bits and B encoded offsets; return a distinct owned image."""
    need(type(inverse) is bool, 'literal CRT shear direction')
    need(source is not offsets, 'separate CRT payload and offsets')
    for count in (before, modulus, padded, suffix):
        positive(count)
    need(compare(modulus, padded) <= 0, 'CRT valid field fits padded field')
    tail = left = right = invalid = output = None
    try:
        tail = subtract(padded, modulus)
        left = factory()
        right = factory()
        invalid = factory()
        output = factory()
        source.rewind()
        offsets.rewind()
        for merging in (False, True):
            outer = Counter(before)
            try:
                while not outer.finished:
                    amount = complement = None
                    try:
                        amount = read_offset(offsets, modulus)
                        complement = subtract(modulus, amount)
                        first, second = (amount, complement) if inverse else (complement, amount)
                        if merging:
                            copy_rows(right, output, second, suffix)
                            copy_rows(left, output, first, suffix)
                            copy_rows(invalid, output, tail, suffix)
                        else:
                            copy_rows(source, left, first, suffix)
                            copy_rows(source, right, second, suffix)
                            copy_rows(source, invalid, tail, suffix)
                        outer.decrement()
                    finally:
                        for count in (amount, complement):
                            if count is not None:
                                count.close()
                need(offsets.read() == BLANK, 'complete CRT prefix offset stream')
                offsets.rewind()
            finally:
                outer.close()
            if not merging:
                need(source.read() == BLANK, 'complete padded CRT shear source')
                source.rewind()
                for tape in (left, right, invalid):
                    tape.rewind()
        need(left.read() == right.read() == invalid.read() == BLANK, 'complete CRT shear buckets')
        output.rewind()
        result, output = output, None
        return result
    finally:
        source.rewind()
        offsets.rewind()
        for tape in (left, right, invalid, output):
            if tape is not None:
                tape.clear()
        if tail is not None:
            tail.close()
