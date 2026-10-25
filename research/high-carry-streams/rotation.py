"""Encoded bounded cyclic rotation with complete spectator blocks.

Tekalign, with substantial OpenAI Codex assistance. Apache-2.0.
Uses the authenticated PR2915/PR2753 Count, Counter and copy operations.
No host integer is reconstructed from a tape.
"""
import bindings
bindings.activate()
from cardinal_counts import Count, positive
from routes import copy_rows
from stream import Counter
from words import BLANK, need


def split_lengths(modulus, amount):
    """Return Q-r,r where r=abs(amount) mod Q, using at most four decrements."""
    need(type(amount) is int and 0 < abs(amount) <= 4, "fixed selected carry")
    positive(modulus)
    remaining = Counter(modulus)
    small = Count.literal(0)
    try:
        for _ in range(abs(amount)):
            remaining.decrement()
            small.increment()
            if remaining.finished:
                remaining.close()
                small.close()
                remaining = Counter(modulus)
                small = Count.literal(0)
        large = Count(remaining.tape)
        result, small = (large, small), None
        return result
    finally:
        remaining.close()
        if small is not None:
            small.close()


def translated(source, ring, before, suffix, amount, factory):
    """Borrow B*Q*S bits, return a distinct owned x -> x+amount mod Q cube."""
    need(type(amount) is int and 0 < abs(amount) <= 4, "fixed selected carry")
    positive(before)
    positive(suffix)
    modulus = Count(ring.modulus)
    large = small = left = right = output = None
    try:
        large, small = split_lengths(modulus, amount)
        modulus.close()
        modulus = None
        output = factory()
        if small.zero():
            outer = Counter(before)
            try:
                while not outer.finished:
                    copy_rows(source, output, large, suffix)
                    outer.decrement()
            finally:
                outer.close()
        else:
            left = factory()
            right = factory()
            first, second = (large, small) if amount > 0 else (small, large)
            outer = Counter(before)
            try:
                while not outer.finished:
                    copy_rows(source, left, first, suffix)
                    copy_rows(source, right, second, suffix)
                    outer.decrement()
            finally:
                outer.close()
            need(source.read() == BLANK, "complete rotation input")
            source.rewind()
            left.rewind()
            right.rewind()
            outer = Counter(before)
            try:
                while not outer.finished:
                    copy_rows(right, output, second, suffix)
                    copy_rows(left, output, first, suffix)
                    outer.decrement()
            finally:
                outer.close()
            need(left.read() == right.read() == BLANK, "complete rotation buckets")
        # The general path already rewound its source. Check the identity path
        # at its actual end; never infer completeness from a known bit count.
        if small.zero():
            need(source.read() == BLANK, "complete identity rotation source")
        output.rewind()
        result, output = output, None
        return result
    finally:
        source.rewind()
        for value in (left, right, output):
            if value is not None:
                value.clear()
        for value in (large, small, modulus):
            if value is not None:
                value.close()
