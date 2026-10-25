"""Fixed-role encoded metadata and odd-modulus inverse for the CRT layout.

Tekalign, with substantial OpenAI Codex assistance. Apache-2.0.
Uses the retained Count algorithms; no unbounded cardinality is decoded.
"""
import crt_sources
crt_sources.activate()
from cardinal_counts import Count, positive
from encoded import compare, divide, subtract
from session import borrowed_tape
from words import BLANK, RIGHT, need


def write_count(value, target):
    value.rewind()
    try:
        while value.read() != RIGHT:
            bit = value.read()
            need(bit in (0, 1), 'binary CRT metadata count')
            target.append(bit)
            value.step(1)
        target.append(RIGHT)
    finally:
        value.rewind()


def read_count(source):
    result = Count.literal(0)
    first, multiple, last = True, False, 0
    try:
        borrowed_tape(result.tape).clear()
        while source.read() in (0, 1):
            last = source.read()
            multiple = not first
            first = False
            result.tape.append(last)
            source.step(1)
        need(not first and (not multiple or last == 1) and source.read() == RIGHT,
             'canonical complete CRT metadata count')
        source.step(1)
        result.tape.append(RIGHT)
        result.rewind()
        answer, result = result, None
        return answer
    finally:
        if result is not None:
            result.close()


def residue(value, modulus):
    quotient, remainder = divide(value, modulus)
    quotient.close()
    return remainder


def difference(first, second, modulus):
    if compare(first, second) >= 0:
        return subtract(first, second)
    delta = subtract(second, first)
    try:
        return subtract(modulus, delta)
    finally:
        delta.close()


def inverse(value, modulus):
    """Return a^(-1) mod m for odd m>=3, rejecting nonunits."""
    positive(modulus)
    need(modulus.read() == 1, 'odd CRT modulus')
    u = v = x = y = one = None
    try:
        one = Count.literal(1)
        need(compare(modulus, one) > 0, 'CRT modulus at least three')
        u = residue(value, modulus)
        v = Count(modulus)
        need(not u.zero(), 'coprime CRT prefix')
        x = Count.literal(1)
        y = Count.literal(0)
        while compare(u, one) != 0 and compare(v, one) != 0:
            need(compare(u, v) != 0, 'coprime CRT prefix')
            while u.read() == 0:
                u.divide_small(2)
                if x.read() == 1:
                    x.add(modulus)
                need(x.divide_small(2) == 0, 'exact CRT inverse halving')
            while v.read() == 0:
                v.divide_small(2)
                if y.read() == 1:
                    y.add(modulus)
                need(y.divide_small(2) == 0, 'exact CRT inverse halving')
            if compare(u, one) == 0 or compare(v, one) == 0:
                break
            need(compare(u, v) != 0, 'coprime CRT prefix')
            if compare(u, v) > 0:
                following = subtract(u, v)
                u.close()
                u = following
                following = difference(x, y, modulus)
                x.close()
                x = following
            else:
                following = subtract(v, u)
                v.close()
                v = following
                following = difference(y, x, modulus)
                y.close()
                y = following
        return Count(x if compare(u, one) == 0 else y)
    finally:
        for count in (u, v, x, y, one):
            if count is not None:
                count.close()


def read_offset(source, modulus):
    flag = source.read()
    need(flag in (0, 1), 'binary CRT prefix validity flag')
    source.step(1)
    value = read_count(source)
    try:
        need(compare(value, modulus) < 0 and (flag or value.zero()), 'bounded CRT prefix offset')
        result, value = value, None
        return result
    finally:
        if value is not None:
            value.close()
