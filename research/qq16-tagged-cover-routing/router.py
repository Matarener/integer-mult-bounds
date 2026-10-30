"""Four-tape, cell-metered tagged cover routing. Apache-2.0.

Only Machine primitives inspect tape cells during execution; verification
observations are performed by verify.py after the controller returns. Controller loops depend on finite
symbols; n/lambda/map coefficients are compilation parameters, not free runtime
registers. This executable model is not a Lean proof of the tape compiler.
"""
from __future__ import annotations

BLANK = "_"
ALPHABET = set("_01^$:;")


def need(ok, message):
    if not ok:
        raise ValueError(message)


class Machine:
    def __init__(self, source, capacity, exterior="101;^$:_"):
        need(len(source) <= capacity, "source capacity")
        self.capacity = capacity
        self.tapes = [list(source + BLANK * (capacity - len(source)))] + [
            [BLANK] * capacity for _ in range(3)
        ]
        self.exterior = [exterior] * 4
        self.heads = [0] * 4
        self.steps = 0
        self.counts = dict(read=0, write=0, move=0, logic=0)
        self.low = [0] * 4
        self.high = [0] * 4

    def tick(self, kind):
        self.steps += 1
        self.counts[kind] += 1

    def read(self, tape):
        self.tick("read")
        return self.tapes[tape][self.heads[tape]]

    def write(self, tape, symbol):
        need(symbol in ALPHABET, "finite alphabet")
        self.tick("write")
        self.tapes[tape][self.heads[tape]] = symbol

    def move(self, tape, offset):
        # The loop is a sequence of unit moves, never a charged-one head jump.
        for _ in range(abs(offset)):
            self.tick("move")
            self.heads[tape] += 1 if offset > 0 else -1
            need(0 <= self.heads[tape] < self.capacity, "visited exterior")
            self.low[tape] = min(self.low[tape], self.heads[tape])
            self.high[tape] = max(self.high[tape], self.heads[tape])

    def rewind(self, tape):
        while self.read(tape) != "^":
            self.move(tape, -1)

    def next_is_end(self, tape):
        return self.read(tape) == "$"

    def copy_record(self, source, target, clear=False):
        while True:
            symbol = self.read(source)
            need(symbol in "01:;", "record alphabet")
            self.write(target, symbol)
            if clear:
                self.write(source, BLANK)
            self.move(source, 1)
            self.move(target, 1)
            if symbol == ";":
                return

    def relabel(self, coefficients):
        dimension = len(coefficients)
        need(self.read(0) == "^", "source fence")
        self.move(0, 1)
        self.write(1, "^")
        self.move(1, 1)
        while not self.next_is_end(0):
            for positions in coefficients:
                parity = 0
                for position in positions:
                    self.move(0, position)
                    bit = self.read(0)
                    need(bit in "01", "tag bit")
                    self.move(0, -position)
                    self.tick("logic")
                    parity ^= bit == "1"
                self.write(1, "1" if parity else "0")
                self.move(1, 1)
            self.move(0, dimension)
            need(self.read(0) == ":", "tag separator")
            self.move(0, 1)
            self.write(1, ":")
            self.move(1, 1)
            while True:
                symbol = self.read(0)
                need(symbol in "01;", "payload alphabet")
                self.write(1, symbol)
                self.move(0, 1)
                self.move(1, 1)
                if symbol == ";":
                    break
        self.write(1, "$")
        self.rewind(0)
        self.rewind(1)

    def partition(self, position):
        need(self.read(1) == "^", "working fence")
        self.move(1, 1)
        for queue in (2, 3):
            self.write(queue, "^")
            self.move(queue, 1)
        while not self.next_is_end(1):
            self.move(1, position)
            bit = self.read(1)
            need(bit in "01", "partition bit")
            self.move(1, -position)
            self.copy_record(1, 2 if bit == "0" else 3)
        for queue in (2, 3):
            self.write(queue, "$")
        for tape in (1, 2, 3):
            self.rewind(tape)
            self.move(tape, 1)
        for queue in (2, 3):
            while not self.next_is_end(queue):
                self.copy_record(queue, 1, clear=True)
            self.write(queue, BLANK)  # clear the right fence
            self.rewind(queue)       # keep the left fence until it is reached
            self.write(queue, BLANK)
        self.write(1, "$")
        self.rewind(1)

    def copy_back(self):
        need(self.read(0) == self.read(1) == "^", "copy-back origins")
        self.move(0, 1)
        self.move(1, 1)
        while True:
            symbol = self.read(1)
            self.write(0, symbol)
            self.write(1, BLANK)
            if symbol == "$":
                break
            self.move(0, 1)
            self.move(1, 1)
        while self.read(0) != "^":
            self.move(0, -1)
            self.move(1, -1)
        self.write(1, BLANK)

    def run(self, coefficients):
        self.relabel(coefficients)
        for position in range(len(coefficients) - 1, -1, -1):
            self.partition(position)
        self.copy_back()
        # Returning enters the halt state. Postconditions are checked externally.


def bound(dimension, payload_bits, records, reads):
    length = dimension + payload_bits + 2
    return records * ((2 * dimension + 2) * reads +
                      (32 * dimension + 32) * length) + 64 * (dimension + 1)


def apply(columns, vector):
    result = 0
    while vector:
        bit = vector & -vector
        result ^= columns[bit.bit_length() - 1]
        vector ^= bit
    return result


def multiply(left, right):
    return [apply(left, column) for column in right]


def inverse(columns):
    n = len(columns)
    rows = [sum(((column >> i) & 1) << j for j, column in enumerate(columns)) |
            (1 << (n + i)) for i in range(n)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if rows[i] >> j & 1), None)
        need(pivot is not None, "singular map")
        rows[j], rows[pivot] = rows[pivot], rows[j]
        for i in range(n):
            if i != j and rows[i] >> j & 1:
                rows[i] ^= rows[j]
    right = [row >> n for row in rows]
    result = [sum(((row >> j) & 1) << i for i, row in enumerate(right))
              for j in range(n)]
    need(multiply(columns, result) == multiply(result, columns) ==
         [1 << i for i in range(n)], "two-sided inverse")
    return result


def coefficients(n, depth, g, delta):
    need(n > 0 and depth > 0, "positive dimensions")
    need(len(g) == n and all(type(x) is int and 0 <= x < 1 << n for x in g),
         "binary matrix")
    need(type(delta) is int and 0 <= delta < 1 << n, "translation range")
    h = inverse(g)
    u = apply(h, delta)
    result = []
    for j in range(n):
        for i in range(n):
            result.append([b * n + i for b in range(n) if h[j] >> b & 1])
    for layer in range(depth):
        for i in range(n):
            result.append([n * n + layer * n + i] +
                          [b * n + i for b in range(n) if u >> b & 1])
    need(sum(map(len, result)) == n * sum(c.bit_count() for c in h) +
         depth * n * (1 + u.bit_count()), "read-count identity")
    return result


def tag(owner, payload, n):
    return "".join(str(column >> i & 1) for column in owner for i in range(n)) +         "".join(str(z >> i & 1) for z in payload for i in range(n))


def encode(records):
    return "^" + "".join(key + ":" + value + ";" for key, value in records) + "$"


def decode(stream):
    need(stream.startswith("^") and stream.endswith("$"), "closed stream")
    if stream == "^$":
        return []
    return [tuple(record.split(":")) for record in stream[1:-2].split(";")]
