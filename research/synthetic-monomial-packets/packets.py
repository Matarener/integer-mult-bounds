# SPDX-License-Identifier: Apache-2.0
"""Sequential data-tape interpreter for externally supplied monomial headers.

The header tuple and loop counters are host control, not an encoded Count
producer. Every data read, write and head step is charged by Tape.
"""

BLANK = 2
MAX_RECORDS, MAX_R, MAX_WIDTH = 128, 64, 128


def need(condition, message):
    if not condition:
        raise ValueError(message)


class Tape:
    def __init__(self, capacity, data=None):
        need(type(capacity) is int and 0 <= capacity <= 2 * MAX_RECORDS * MAX_R * MAX_WIDTH,
             "bounded data tape capacity")
        self.cells = bytearray([BLANK]) * capacity
        if data is not None:
            need(len(data) == capacity, "complete source extent")
            self.cells[:] = data
        self.head, self.ticks = 0, 0

    def move(self, direction):
        need(direction in (-1, 1), "unit head step")
        need(-1 <= self.head + direction <= len(self.cells), "data head extent")
        self.head += direction
        self.ticks += 1

    def rewind(self):
        for _ in range(abs(self.head)):
            self.move(-1 if self.head > 0 else 1)

    def read(self):
        need(0 <= self.head < len(self.cells), "read within data extent")
        self.ticks += 1
        return self.cells[self.head]

    def write(self, value):
        need(value in (0, 1, BLANK), "data alphabet")
        need(0 <= self.head < len(self.cells), "write within data extent")
        self.cells[self.head] = value
        self.ticks += 1

    def take(self):
        value = self.read()
        self.move(1)
        return value

    def put(self, value):
        self.write(value)
        self.move(1)

    def clear(self):
        self.rewind()
        for _ in range(len(self.cells)):
            self.put(BLANK)
        self.rewind()

    def blank(self):
        self.rewind()
        result = True
        for _ in range(len(self.cells)):
            result &= self.take() == BLANK
        self.rewind()
        return result


def copy_bits(source, target, count):
    for _ in range(count):
        bit = source.take()
        need(bit in (0, 1), "binary component")
        target.put(bit)


def signable(word):
    """Reject the sole signed word whose negation does not fit."""
    word.rewind()
    sign = word.take()
    nonzero = False
    for _ in range(len(word.cells) - 1):
        nonzero |= bool(word.take())
    need(not sign or nonzero, "minimum signed component cannot be negated")
    word.rewind()


def negate(word):
    """Complement plus one, scanning the actual MSB-first word backwards."""
    for _ in range(len(word.cells) - 1):
        word.move(1)
    carry = 1
    for _ in range(len(word.cells)):
        digit = 1 - word.read() + carry
        word.write(digit & 1)
        carry = digit >> 1
        word.move(-1)
    word.rewind()


def emit(buffer, output, word, components, negative):
    buffer.rewind()
    for _ in range(components):
        copy_bits(buffer, word, len(word.cells))
        signable(word)
        if negative:
            negate(word)
        copy_bits(word, output, len(word.cells))
        word.clear()


class MonomialPackets:
    """Five data roles including borrowed source and returned output.

    Construction is the allocation boundary. run() never grows a data tape.
    Full-width integer coefficients are confined to the independent oracle.
    """

    def __init__(self, records, r, width):
        need(type(records) is int and 1 <= records <= MAX_RECORDS, "record bound")
        need(type(r) is int and 2 <= r <= MAX_R and r & (r - 1) == 0,
             "power-of-two polynomial extent")
        need(type(width) is int and 3 <= width <= MAX_WIDTH, "signed width bound")
        self.records, self.r, self.width = records, r, width
        self.record_bits = 2 * r * width
        self.output = Tape(records * self.record_bits)
        self.prefix, self.suffix = Tape(self.record_bits), Tape(self.record_bits)
        self.word = Tape(width)
        self.closed = True

    def run(self, source, exponents):
        need(isinstance(source, Tape) and self.closed and
             all(source is not tape and source.cells is not tape.cells for tape in
                 (self.output, self.prefix, self.suffix, self.word)),
             "closed distinct borrowed source")
        need(len(source.cells) == len(self.output.cells) and source.head == 0,
             "aligned complete packet")
        need(type(exponents) is tuple and len(exponents) == self.records
             and all(type(e) is int and abs(e) < 1 << 63 for e in exponents),
             "bounded compiled exponent headers")
        need(self.output.blank(), "consumed output")
        self.closed = False
        succeeded = False
        try:
            for exponent in exponents:
                parity, shift = divmod(exponent % (2 * self.r), self.r)
                front = 2 * (self.r - shift)
                back = 2 * shift
                copy_bits(source, self.prefix, front * self.width)
                copy_bits(source, self.suffix, back * self.width)
                emit(self.suffix, self.output, self.word, back, not parity)
                emit(self.prefix, self.output, self.word, front, bool(parity))
                self.prefix.clear()
                self.suffix.clear()
            self.output.rewind()
            succeeded = True
            return self.output
        finally:
            for tape in (self.prefix, self.suffix, self.word):
                tape.clear()
            if not succeeded:
                self.output.clear()
            source.rewind()
            self.closed = True

    def data_ticks(self, source):
        return sum(tape.ticks for tape in
                   (source, self.output, self.prefix, self.suffix, self.word))

    def step_bound(self):
        n = len(self.output.cells)
        return 64 * n + 16 * self.record_bits + 16 * self.width + 8 * self.records
