"""Stateful synthetic headers on four sequential Boolean data tapes.

Nick Petalas. Apache-2.0. Shape scheduling and observation are separate.
"""

from dataclasses import dataclass


def require(condition, message):
    if not condition:
        raise ValueError(message)


@dataclass(frozen=True)
class Shape:
    ell: int
    width: int
    long_axes: tuple
    h: int
    opposite: bool = False

    def __post_init__(self):
        require(type(self.ell) is int and 2 <= self.ell <= 256, 'invalid ell')
        require(type(self.width) is int and 1 <= self.width < self.ell, 'invalid width')
        require(type(self.long_axes) is tuple and 1 <= len(self.long_axes) <= 64,
                'invalid axes')
        require(all(type(x) is bool for x in self.long_axes), 'non-Boolean axis')
        require(type(self.h) is int and 0 <= self.h < self.ell, 'invalid round')
        require(type(self.opposite) is bool, 'invalid direction')

    def slots(self):
        """Supplied shape schedule in physical MSB order; contains no data."""
        b, q = (self.ell - 1) % self.width, (self.ell - 1) // self.width
        result = [(i, self.ell - 1) for i, long in enumerate(self.long_axes) if long]
        result += [(i, v) for v in range(b - 1, -1, -1)
                   for i in range(len(self.long_axes))]
        result += [(i, b + j * self.width + v) for j in range(q - 1, -1, -1)
                   for i in range(len(self.long_axes))
                   for v in range(self.width - 1, -1, -1)]
        return tuple(result)

    def participants(self):
        return tuple(i for i, long in enumerate(self.long_axes)
                     if self.h < self.ell - (not long))


class Tape:
    def __init__(self, size):
        require(type(size) is int and 1 <= size <= 16384, 'invalid tape extent')
        self.cells = [0] * size
        self.head = 0
        self.reads = self.writes = self.moves = 0

    def seek(self, target):
        require(type(target) is int and 0 <= target < len(self.cells), 'bad seek')
        for _ in range(abs(target - self.head)):
            self.head += 1 if target > self.head else -1
            self.moves += 1

    def read(self):
        self.reads += 1
        return self.cells[self.head]

    def write(self, bit):
        require(type(bit) is int and bit in (0, 1), 'non-bit write')
        self.writes += 1
        self.cells[self.head] = bit

    def clear(self):
        for j in range(len(self.cells)):
            self.seek(j)
            self.write(0)
        self.seek(0)

    def bill(self):
        return dict(reads=self.reads, writes=self.writes, moves=self.moves)


class Sweep:
    def __init__(self, shape):
        require(type(shape) is Shape, 'invalid shape')
        self.shape = shape
        self.slots = tuple(reversed(shape.slots()))
        self.offsets = {axis: j * (shape.h + 1)
                        for j, axis in enumerate(shape.participants())}
        self.address = Tape(len(self.slots))
        self.bank = Tape(max(1, len(self.offsets) * (shape.h + 1)))
        self.total = Tape(shape.h + 1)
        self.output = Tape(shape.ell + 1)
        self.ands = self.xors = self.flips = 0
        self.used = False

    def xor(self, left, right):
        self.xors += 1
        return left ^ right

    def and_(self, left, right):
        self.ands += 1
        return left & right

    def add_delta(self, base, position, old):
        """Add +/- low word for a branch flip, or +/- beta*2**v otherwise."""
        h, carry = self.shape.h, old
        beta = 0
        if position < h:
            self.bank.seek(base + h)
            beta = self.bank.read()
        for t in range(h + 1):
            bit = 0
            if position == h and t < h:
                self.bank.seek(base + t)
                bit = self.bank.read()
            elif position < h and t == position:
                bit = beta
            self.total.seek(t)
            z = self.total.read()
            addend = self.xor(bit, old)
            mixed = self.xor(z, addend)
            result = self.xor(mixed, carry)
            carry = self.xor(self.and_(z, addend), self.and_(mixed, carry))
            self.total.write(result)

    def advance(self):
        """One little-endian increment, including the last all-one wrap."""
        for j, (axis, v) in enumerate(self.slots):
            self.address.seek(j)
            old = self.address.read()
            self.address.write(self.xor(old, 1))
            self.flips += 1
            if axis in self.offsets and v <= self.shape.h:
                base = self.offsets[axis]
                self.bank.seek(base + v)
                cached = self.bank.read()
                require(cached == old, 'address/cache invariant failed')
                self.bank.write(self.xor(cached, 1))
                self.add_delta(base, v, old)
            if old == 0:
                break
        self.address.seek(0)

    def negate(self):
        carry = 1
        for t in range(self.shape.h + 1):
            self.total.seek(t)
            inverse = self.xor(self.total.read(), 1)
            result = self.xor(inverse, carry)
            carry = self.and_(inverse, carry)
            self.total.write(result)

    def emit(self, observe):
        if not self.shape.opposite:
            self.negate()
        for j in range(self.shape.ell + 1):
            bit = 0
            if j <= self.shape.h:
                self.total.seek(self.shape.h - j)
                bit = self.total.read()
            self.output.seek(j)
            self.output.write(bit)
        if not self.shape.opposite:
            self.negate()
        # Observation is a paused consumer boundary, outside this data bill.
        observe(tuple(self.output.cells))
        self.output.clear()

    def run(self, count, observe):
        require(type(count) is int and 1 <= count <= 4096
                and count <= 1 << len(self.slots), 'invalid record count')
        require(callable(observe), 'invalid observer')
        require(not self.used, 'sweep already used')
        self.used = True
        try:
            for _ in range(count):
                self.emit(observe)
                self.advance()
        finally:
            for tape in (self.address, self.bank, self.total, self.output):
                tape.clear()
        require(all(t.head == 0 and not any(t.cells)
                    for t in (self.address, self.bank, self.total, self.output)),
                'private return failed')
        return self.bill()

    def bill(self):
        tapes = dict(address=self.address.bill(), bank=self.bank.bill(),
                     total=self.total.bill(), output=self.output.bill())
        cells = sum(len(t.cells) for t in
                    (self.address, self.bank, self.total, self.output))
        work = sum(sum(b.values()) for b in tapes.values()) + self.ands + self.xors
        return dict(tapes=tapes, AND=self.ands, XOR=self.xors, flips=self.flips,
                    cells=cells, work=work)
