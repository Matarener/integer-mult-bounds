"""Direct shape-controlled sequential twiddle arithmetic. Nick Petalas, Apache-2.0."""

from dataclasses import dataclass


def require(condition, message):
    if not condition:
        raise ValueError(message)


@dataclass(frozen=True)
class Shape:
    ell: int
    width: int
    axes: tuple
    h: int
    opposite: bool = False

    def validate(self):
        require(type(self.ell) is int and 2 <= self.ell <= 256, 'invalid ell')
        require(type(self.width) is int and 1 <= self.width < self.ell, 'invalid width')
        require(type(self.axes) is tuple and 1 <= len(self.axes) <= 64, 'invalid axes')
        require(all(type(x) is bool for x in self.axes), 'non-Boolean axes')
        require(type(self.h) is int and 0 <= self.h < self.ell, 'invalid round')
        require(type(self.opposite) is bool, 'invalid direction')

    def dimensions(self):
        self.validate()
        active = tuple(i for i, long in enumerate(self.axes)
                       if self.h < self.ell - (not long))
        b = (self.ell - 1) % self.width
        a = b if b <= self.h < self.ell - 1 else 0
        return active, a, max(a, 1)

    def slots(self):
        """Generate shape-only control; no address or topology is retained here."""
        b, q = (self.ell - 1) % self.width, (self.ell - 1) // self.width
        for i, long in enumerate(self.axes):
            if long:
                yield i, self.ell - 1
        for v in range(b - 1, -1, -1):
            for i in range(len(self.axes)):
                yield i, v
        for chunk in range(q - 1, -1, -1):
            for i in range(len(self.axes)):
                for v in range(b + (chunk + 1) * self.width - 1,
                               b + chunk * self.width - 1, -1):
                    yield i, v


class Tape:
    """A preallocated Boolean tape. Only read/write/unit-step access is charged.

    Construction is boundary admission of an already supplied Boolean tape.
    Counts and Python representation are observations outside the machine bill.
    """

    def __init__(self, bits):
        require(type(bits) is tuple and 1 <= len(bits) <= 16384, 'invalid tape extent')
        require(all(type(x) is int and x in (0, 1) for x in bits), 'non-bit tape')
        self.cells = list(bits)
        self.head = 0
        self.reads = self.writes = self.moves = 0

    def move(self, direction):
        require(direction in (-1, 1), 'invalid unit step')
        require(0 <= self.head + direction < len(self.cells), 'head outside tape')
        self.head += direction
        self.moves += 1

    def seek(self, target):
        require(type(target) is int and 0 <= target < len(self.cells), 'bad target')
        direction = 1 if target >= self.head else -1
        for unused in range(abs(target - self.head)):
            self.move(direction)

    def read(self):
        self.reads += 1
        return self.cells[self.head]

    def write(self, bit):
        require(type(bit) is int and bit in (0, 1), 'non-bit write')
        self.cells[self.head] = bit
        self.writes += 1

    def erase(self):
        for target in range(len(self.cells)):
            self.seek(target)
            self.write(0)
        self.seek(0)

    def counts(self):
        return self.reads, self.writes, self.moves


class Machine:
    def __init__(self, shape, address):
        require(type(shape) is Shape, 'invalid shape')
        self.active, self.a, self.stride = shape.dimensions()
        extent = sum(shape.ell if x else shape.ell - 1 for x in shape.axes)
        require(type(address) is tuple and len(address) == extent, 'bad address extent')
        self.shape = shape
        self.address = Tape(address)
        self.bank = Tape((0,) * max(1, len(self.active) * self.stride))
        self.total = Tape((0,) * (shape.h + 1))
        self.output = Tape((0,) * (shape.ell + 1))
        self.ands = self.xors = 0

    def masked_add(self, branch, bit, v):
        carry = branch & bit
        self.ands += 1
        for target in range(v, self.shape.h + 1):
            self.total.seek(target)
            old = self.total.read()
            self.total.write(old ^ carry)
            carry = old & carry
            self.xors += 1
            self.ands += 1

    def consume(self, axis, v, bit):
        if axis not in self.active:
            return
        base = self.active.index(axis) * self.stride
        if v < self.a:
            self.bank.seek(base + v)
            self.bank.write(bit)
        elif v == self.shape.h:
            for low in range(self.a):
                self.bank.seek(base + low)
                pending = self.bank.read()
                self.bank.write(0)
                self.masked_add(bit, pending, low)
            self.bank.seek(base)
            self.bank.write(bit)
        elif self.a <= v < self.shape.h:
            self.bank.seek(base)
            self.masked_add(self.bank.read(), bit, v)

    def emit(self):
        if self.shape.h and self.active and not self.shape.opposite:
            carry = 1
            for target in range(self.shape.h + 1):
                self.total.seek(target)
                inverse = self.total.read() ^ 1
                self.total.write(inverse ^ carry)
                carry = inverse & carry
                self.xors += 2
                self.ands += 1
        for j in range(self.shape.ell + 1):
            self.output.seek(j)
            if j <= self.shape.h:
                self.total.seek(self.shape.h - j)
                self.output.write(self.total.read())
            else:
                self.output.write(0)
        self.output.seek(0)

    def execute(self):
        """Valid admitted tapes and immutable shape control; see PROOF.md."""
        try:
            for index, (axis, v) in enumerate(self.shape.slots()):
                self.address.seek(index)
                self.consume(axis, v, self.address.read())
            self.emit()
        except BaseException:
            self.output.erase()
            raise
        finally:
            self.address.seek(0)
            self.bank.erase()
            self.total.erase()

    def invoice(self):
        return {'address': self.address.counts(), 'bank': self.bank.counts(),
                'total': self.total.counts(), 'output': self.output.counts(),
                'and': self.ands, 'xor': self.xors,
                'cells': sum(len(t.cells) for t in
                             (self.address, self.bank, self.total, self.output))}
