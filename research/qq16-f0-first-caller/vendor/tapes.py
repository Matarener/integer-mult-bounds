"""Source-bound QQ16 Gaussian axis on six bit tapes.

Clear1nsight, with substantial OpenAI ChatGPT assistance. Apache-2.0.
The Python object store and loop indices simulate a nonuniform compiled
controller. Kernel payload access is exclusively read/write/unit-move.
"""
from collections import Counter


def need(condition, message):
    if not condition:
        raise ValueError(message)


class Tape:
    """One independently based owned interval, with dirty exterior sentinels."""

    def __init__(self, bits, origin=0, trace=False, discardable=False):
        need(type(origin) is int, "integer origin")
        need(all(type(x) is int and x in (0, 1) for x in bits), "binary cells")
        self.cells = list(bits)
        self.discardable = discardable
        self.origin = origin
        self.head = origin
        self.count = Counter()
        self.trace = [] if trace else None
        self.exterior = {origin - 1: 1, origin + len(bits): 1,
                         origin + len(bits) + 1: 0}

    def record(self, action):
        self.count[action] += 1
        if self.trace is not None:
            self.trace.append((action, self.head - self.origin))

    def read(self):
        pos = self.head - self.origin
        need(0 <= pos < len(self.cells), "read outside owned interval")
        self.record("read")
        return self.cells[pos]

    def write(self, value):
        pos = self.head - self.origin
        need(0 <= pos < len(self.cells), "write outside owned interval")
        need(type(value) is int and value in (0, 1), "binary write")
        self.record("write")
        self.cells[pos] = value

    def move(self, direction):
        need(type(direction) is int and direction in (-1, 1), "unit move")
        pos = self.head + direction - self.origin
        # One-past may be visited, never dereferenced.
        need(0 <= pos <= len(self.cells), "move outside allowed head interval")
        self.record("move")
        self.head += direction


def walk(tapes, direction, steps):
    """Every move below is charged, including closed-window head returns."""
    for _ in range(steps):
        for tape in tapes:
            tape.move(direction)


def axis_kernel(tapes, n, width, axis, sign=1):
    """Apply C_sign on coordinate pairs differing in bit axis.

    Preconditions: N=2**n with n>=1, width>=2, six separate supplied tapes,
    signed little-endian input components, and every Gaussian numerator even
    and in the signed width-bit range. No admission scan is hidden in the bill.
    Scratch is owned (its old contents may be destroyed), not borrowed.
    """
    need(type(n) is int and n >= 1, "positive dimension")
    need(type(width) is int and width >= 2, "component width")
    need(type(axis) is int and 0 <= axis < n, "axis range")
    need(type(sign) is int and sign in (-1, 1), "line sign")
    need(len(tapes) == 6 and len({id(t) for t in tapes}) == 6,
         "six distinct tapes")
    need(len({id(t.cells) for t in tapes}) == 6, "disjoint tape storage")
    size = 1 << n
    half = 1 << axis
    need([len(t.cells) for t in tapes] == [size * width] * 2
         + [size * width // 2] * 4, "tape lengths")
    need(all(t.head == t.origin for t in tapes), "entry heads")
    data, scratch = tapes[:2], tapes[2:]
    need(all(t.discardable is True for t in scratch), "owned scratch required")

    # Pack the low and high halves of every axis block in four streams.
    for coordinate in range(size):
        lane = (coordinate >> axis) & 1
        for _ in range(width):
            for component in range(2):
                src, dst = data[component], scratch[2 * lane + component]
                bit = src.read()
                dst.write(bit)
                src.move(1)
                dst.move(1)
    bit = 0
    walk(data, -1, size * width)
    walk(scratch, -1, size * width // 2)

    for _block in range(size // (2 * half)):
        for upper in (False, True):
            orientation = -sign if upper else sign
            for _pair in range(half):
                carry_r = carry_i = 0
                for bit_index in range(width):
                    a, b, c, d = (t.read() for t in scratch)
                    # Each sum is bounded finite-control arithmetic on four
                    # bits and a carry in {-1,0,1,2}, never a W-bit host add.
                    tr = carry_r + a - orientation * b + c + orientation * d
                    ti = carry_i + b + orientation * a + d - orientation * c
                    out_r, out_i = tr % 2, ti % 2
                    carry_r, carry_i = tr // 2, ti // 2
                    need(-1 <= carry_r <= 2 and -1 <= carry_i <= 2,
                         "finite carry range")
                    if bit_index == 0:
                        need(out_r == out_i == 0, "nonexact half")
                    else:
                        data[0].write(out_r)
                        data[1].write(out_i)
                        walk(data, 1, 1)
                    if upper:
                        # The second output is the last reader of this bit.
                        for tape in scratch:
                            tape.write(0)
                    walk(scratch, 1, 1)
                # Arithmetic right shift duplicates the numerator sign bit.
                data[0].write(out_r)
                data[1].write(out_i)
                walk(data, 1, 1)
                carry_r = carry_i = out_r = out_i = a = b = c = d = tr = ti = 0
            if not upper:
                walk(scratch, -1, half * width)
    walk(scratch, -1, size * width // 2)
    walk(data, -1, size * width)
    return (bit, carry_r, carry_i, out_r, out_i, a, b, c, d, tr, ti)


def encode(values, width):
    """Unmetered fixture preparation, not part of the kernel/caller claim."""
    need(all(type(v) is int and -(1 << (width - 1)) <= v < (1 << (width - 1))
             for v in values), "signed input range")
    return [(v >> bit) & 1 for v in values for bit in range(width)]


def decode(tape, width):
    """Unmetered test observation, not part of the physical implementation."""
    values = []
    for start in range(0, len(tape.cells), width):
        word = sum(tape.cells[start + bit] << bit for bit in range(width))
        values.append(word - ((word >> (width - 1)) << width))
    return values


def fixture(real, imag, width, dirty=1, origins=None, trace=False):
    size = len(real)
    need(size == len(imag), "component lengths")
    origins = origins or [0] * 6
    need(len(origins) == 6, "six origins")
    streams = [encode(real, width), encode(imag, width)]
    streams += [[dirty] * (size * width // 2) for _ in range(4)]
    return [Tape(bits, origin, trace, discardable=(index >= 2))
            for index, (bits, origin) in enumerate(zip(streams, origins))]
