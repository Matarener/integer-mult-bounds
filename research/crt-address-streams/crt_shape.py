"""Packed encoded CRT shape, checked units and fixed-width address control."""
import crt_sources
crt_sources.activate()
from cardinal_counts import Count, positive
from encoded import compare
from stream import Counter
from session import borrowed_tape
from words import BLANK, LEFT, RIGHT, need
from encoded_crt import inverse, read_count, write_count


def power_two(exponent):
    result = Count.literal(1)
    counter = Counter(exponent)
    try:
        while not counter.finished:
            result.multiply_small(2)
            counter.decrement()
        answer, result = result, None
        return answer
    finally:
        counter.close()
        if result is not None:
            result.close()


def binary_exponent(value):
    positive(value)
    result = Count.literal(0)
    try:
        value.msb()
        need(value.read() == 1, 'positive power-of-two CRT field')
        value.step(-1)
        while value.read() != LEFT:
            need(value.read() == 0, 'power-of-two CRT field')
            result.increment()
            value.step(-1)
        value.step(1)
        value.rewind()
        answer, result = result, None
        return answer
    finally:
        if value.read() == LEFT:
            value.step(1)
        value.rewind()
        if result is not None:
            result.close()


class Shape:
    """Six Count fields per axis on one tape; no growing host list of roles."""
    def __init__(self, source, dimensions, factory):
        self.dimensions = self.bits = self.source_total = self.padded_total = self.page = self.bounds = None
        positive(dimensions)
        outer = None
        source.rewind()
        try:
            self.dimensions = Count(dimensions)
            self.bits = Count.literal(0)
            self.source_total = Count.literal(1)
            self.padded_total = Count.literal(1)
            self.page = factory()
            self.bounds = factory()
            outer = Counter(dimensions)
            while not outer.finished:
                s = t = width = mu = one = None
                try:
                    s = read_count(source)
                    t = read_count(source)
                    one = Count.literal(1)
                    need(s.read() == 1 and compare(s, one) > 0, 'odd CRT source length at least three')
                    need(compare(s, t) < 0, 'CRT source fits strict padded field')
                    width = binary_exponent(t)
                    mu = inverse(self.source_total, s)
                    for count in (s, t, width, self.source_total, mu, self.bits):
                        write_count(count, self.page)
                    write_count(s, self.bounds)
                    write_count(width, self.bounds)
                    following = Count.product(self.source_total, s)
                    self.source_total.close()
                    self.source_total = following
                    following = Count.product(self.padded_total, t)
                    self.padded_total.close()
                    self.padded_total = following
                    self.bits.add(width)
                    outer.decrement()
                finally:
                    for count in (s, t, width, mu, one):
                        if count is not None:
                            count.close()
            need(source.read() == BLANK, 'complete CRT source shape')
            self.page.rewind()
            self.bounds.rewind()
        except BaseException:
            self.close()
            raise
        finally:
            if outer is not None:
                outer.close()
            source.rewind()

    def axis(self, index):
        need(compare(index, self.dimensions) < 0, 'CRT axis index in range')
        self.page.rewind()
        before = Counter(index)
        values = []
        try:
            while not before.finished:
                for _ in range(6):
                    read_count(self.page).close()
                before.decrement()
            for _ in range(6):
                values.append(read_count(self.page))
            result, values = tuple(values), []
            return result
        finally:
            before.close()
            for value in values:
                value.close()
            self.page.rewind()

    def close(self):
        if self.page is not None:
            self.page.clear()
            self.page = None
        if self.bounds is not None:
            self.bounds.clear()
            self.bounds = None
        for name in ('dimensions', 'bits', 'source_total', 'padded_total'):
            value = getattr(self, name)
            if value is not None:
                value.close()
                setattr(self, name, None)


class Address:
    """Fixed-width little-endian binary counter; only a carry enters control."""
    def __init__(self, width, factory):
        self.tape = None
        self.finished = False
        counter = Counter(width)
        try:
            self.tape = factory()
            while not counter.finished:
                self.tape.append(0)
                counter.decrement()
            self.tape.append(RIGHT)
            self.tape.rewind()
        except BaseException:
            self.close()
            raise
        finally:
            counter.close()

    def reset(self):
        if self.tape.read() == LEFT:
            self.tape.step(1)
        self.tape.rewind()

    def msb(self):
        self.reset()
        while self.tape.read() != RIGHT:
            self.tape.step(1)
        self.tape.step(-1)

    def increment(self):
        need(not self.finished, 'live CRT packed address')
        self.reset()
        while self.tape.read() == 1:
            self.tape.write(0)
            self.tape.step(1)
        if self.tape.read() == RIGHT:
            self.finished = True
        else:
            need(self.tape.read() == 0, 'binary CRT packed address')
            self.tape.write(1)
        self.reset()

    def field(self, width, reverse=False):
        result = Count.literal(0)
        counter = Counter(width)
        try:
            if not reverse:
                borrowed_tape(result.tape).clear()
            while not counter.finished:
                bit = self.tape.read()
                need(bit in (0, 1), 'complete CRT address field')
                if reverse:
                    result.multiply_small(2)
                    if bit:
                        result.increment()
                else:
                    result.tape.append(bit)
                self.tape.step(-1 if reverse else 1)
                counter.decrement()
            if not reverse:
                result.tape.append(RIGHT)
                result.normalize()
            answer, result = result, None
            return answer
        finally:
            counter.close()
            if result is not None:
                result.close()

    def close(self):
        if self.tape is not None:
            self.reset()
            self.tape.clear()
            self.tape = None
