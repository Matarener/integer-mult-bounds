"""Physical signed packet consumer; allocation dimensions never drive run().

SPDX-License-Identifier: Apache-2.0
Sagar Thakrar, with substantial OpenAI Codex assistance.
The borrowed header/descriptor protocol is Nick Petalas's PR3593 protocol.
"""
from collections import Counter


def require(ok, message):
    if not ok:
        raise ValueError(message)


class Tape:
    """Simulator storage: only these methods inspect storage/head in execution."""

    def __init__(self, cells):
        self.cells = list(cells)
        self.head = 0
        self.counts = Counter()

    def read(self):
        self.counts["read"] += 1
        return self.cells[self.head]

    def write(self, value):
        self.counts["write"] += 1
        self.cells[self.head] = value

    def move(self, direction):
        require(direction in (-1, 1), "unit move")
        require(0 <= self.head + direction < len(self.cells), "tape boundary")
        self.counts["move"] += 1
        self.head += direction


class Consumer:
    """One-shot consumer of a valid borrowed PR3593 twiddle header.

    Admission: matching unary descriptors and allocation dimensions; source has
    exactly r Gaussian coefficients, each two signed width-bit MSB words. All
    borrowed heads start at zero. A requested negation must be representable.
    Tape objects must have separate backing storage, as their constructors
    provide; manually sharing their diagnostic cells lists is not admitted.
    run() never reads the host allocation dimensions. Arithmetic endpoints here
    are exact signed rotations, not the rest of a recursive caller.
    """

    def __init__(self, ell, width):
        require(type(ell) is int and 2 <= ell <= 32, "allocation ell")
        require(type(width) is int and width >= 2, "allocation signed width")
        length = 2 * (1 << ell) * width
        self.capacities = dict(prefix=length+3, suffix=length+3, output=length+3,
                               word=width+3, a=ell+4, b=ell+4)
        self.tapes = {}
        self.invoice = Counter()
        self.gates = Counter()
        self.used = False
        # Blank simulator allocation only. Actual framing/initialization is
        # encoded-input driven in initialize(), and every such action is paid.
        for role, capacity in self.capacities.items():
            self.tapes[role] = Tape((0,) * capacity)

    def gate(self, name):
        self.gates[name] += 1
        self.invoice["gate"] += 1

    def test(self, condition):
        self.gate("test")
        return condition

    def read(self, role):
        self.invoice[role + ".read"] += 1
        return self.tapes[role].read()

    def write(self, role, value):
        self.invoice[role + ".write"] += 1
        self.tapes[role].write(value)

    def move(self, role, direction):
        self.invoice[role + ".move"] += 1
        self.tapes[role].move(direction)

    def home(self, role):
        while self.test(self.read(role) != "^"):
            self.move(role, -1)

    def initialize(self):
        """Frame scratch using borrowed extents, never host allocation sizes."""
        require(self.test(self.read("source") == "^"), "source origin")
        for role in ("prefix", "suffix", "output"):
            self.write(role, "^")
            self.move(role, 1)
        self.move("source", 1)
        while self.test(self.read("source") != "$"):
            require(self.test(self.read("source") in (0, 1)), "source bit")
            for role in ("prefix", "suffix", "output"):
                self.write(role, 0)
                self.move(role, 1)
            self.move("source", 1)
        for role in ("prefix", "suffix", "output"):
            self.write(role, 0)
            self.move(role, 1)
            self.write(role, "!")
            self.home(role)
        self.home("source")
        require(self.test(self.read("width") == "^"), "width origin")
        self.write("word", "^")
        self.move("word", 1)
        self.move("width", 1)
        while self.test(self.read("width") == "1"):
            self.write("word", 0)
            self.move("word", 1)
            self.move("width", 1)
        require(self.test(self.read("width") == "$"), "unary width delimiter")
        self.write("word", 0)
        self.move("word", 1)
        self.write("word", "!")
        self.home("word")
        self.home("width")
        require(self.test(self.read("descriptor") == "^"), "descriptor origin")
        for role in ("a", "b"):
            self.write(role, "^")
            self.move(role, 1)
        self.move("descriptor", 1)
        while self.test(self.read("descriptor") == "1"):
            for role in ("a", "b"):
                self.write(role, 0)
                self.move(role, 1)
            self.move("descriptor", 1)
        require(self.test(self.read("descriptor") == "#"), "unary ell delimiter")
        for role in ("a", "b"):
            # One extra binary digit, one endpoint delimiter, then guard.
            self.write(role, 0)
            self.move(role, 1)
            self.write(role, 0)
            self.move(role, 1)
            self.write(role, "!")
            self.home(role)
        self.home("descriptor")

    def clear(self, role):
        self.home(role)
        self.move(role, 1)
        while self.test(self.read(role) != "!"):
            self.write(role, 0)
            self.move(role, 1)
        self.write(role, 0)
        self.move(role, -1)
        while self.test(self.read(role) != "^"):
            self.write(role, 0)
            self.move(role, -1)
        self.write(role, 0)

    def mark_top(self, role):
        """Enter at '$'; mark highest one by digit 2, return at '^'."""
        self.move(role, -1)
        while self.test(self.read(role) == 0):
            self.move(role, -1)
        zero = self.test(self.read(role) == "^")
        if self.test(not zero):
            require(self.test(self.read(role) == 1), "binary counter")
            self.write(role, 2)
            self.home(role)
        return zero

    def decrement(self, role):
        """Positive counter only; top marker makes zero detection local."""
        self.move(role, 1)
        while self.test(self.read(role) == 0):
            self.write(role, 1)
            self.move(role, 1)
        top = self.test(self.read(role) == 2)
        require(self.test(top or self.read(role) == 1), "positive marked counter")
        self.write(role, 0)
        self.move(role, -1)
        zero = False
        if self.test(top):
            zero = self.test(self.read(role) == "^")
            if self.test(not zero):
                self.write(role, 2)
        self.home(role)
        return zero

    def counts_from_header(self):
        """The descriptor's first unary field bounds every raw header access."""
        require(self.test(self.read("descriptor") == "^"), "descriptor origin")
        epsilon = self.read("header")
        require(self.test(epsilon in (0, 1)), "header sign bit")
        self.move("descriptor", 1)
        self.move("a", 1)
        while self.test(self.read("descriptor") == "1"):
            self.move("header", 1)
            bit = self.read("header")
            require(self.test(bit in (0, 1)), "header exponent bit")
            self.write("a", bit)
            self.move("a", 1)
            self.move("descriptor", 1)
        require(self.test(self.read("descriptor") == "#"), "unary ell delimiter")
        self.write("a", "$")
        # Restore the raw header by the very same unary field, not a host size.
        self.move("descriptor", -1)
        while self.test(self.read("descriptor") == "1"):
            self.move("header", -1)
            self.move("descriptor", -1)
        require(self.test(self.read("descriptor") == "^"), "descriptor restored")
        # Reverse MSB staging into little-endian s, with an extra high zero.
        self.move("a", -1)
        self.move("b", 1)
        while self.test(self.read("a") != "^"):
            self.write("b", self.read("a"))
            self.move("b", 1)
            self.move("a", -1)
        self.write("b", 0)
        self.move("b", 1)
        self.write("b", "$")
        self.home("b")
        # Compute -s modulo 2r, then toggle its highest bit to obtain r-s.
        carry = 1
        self.move("a", 1)
        self.move("b", 1)
        while self.test(self.read("b") != "$"):
            bit = self.read("b")
            self.gate("complement-add")
            self.write("a", (1-bit) ^ carry)
            carry &= 1-bit
            self.move("a", 1)
            self.move("b", 1)
        self.write("a", "$")
        self.move("a", -1)
        self.gate("toggle-high")
        self.write("a", 1-self.read("a"))
        self.move("a", 1)
        a_zero = self.mark_top("a")
        b_zero = self.mark_top("b")
        require(self.test(not a_zero), "r-s is positive")
        return epsilon, a_zero, b_zero

    def copy_word(self, target):
        self.move("width", 1)
        while self.test(self.read("width") == "1"):
            bit = self.read("source")
            require(self.test(bit in (0, 1)), "complete source word")
            self.write(target, bit)
            self.move(target, 1)
            self.move("source", 1)
            self.move("width", 1)
        require(self.test(self.read("width") == "$"), "unary width delimiter")
        self.home("width")

    def split(self, counter, target, zero):
        self.move(target, 1)
        while self.test(not zero):
            # Exactly two components; this is a finite control sequence.
            self.copy_word(target)
            self.copy_word(target)
            zero = self.decrement(counter)
        self.write(target, "$")
        self.home(target)

    def emit_word(self, source, negate):
        self.move("word", 1)
        self.move("width", 1)
        sign = self.read(source)
        first, lower_nonzero = True, False
        while self.test(self.read("width") == "1"):
            bit = self.read(source)
            require(self.test(bit in (0, 1)), "complete segment word")
            self.gate("signed-minimum-flag")
            if not first:
                lower_nonzero |= bool(bit)
            first = False
            self.write("word", bit)
            self.move("word", 1)
            self.move(source, 1)
            self.move("width", 1)
        require(self.test(self.read("width") == "$"), "unary width delimiter")
        self.write("word", "$")
        self.home("width")
        if self.test(negate):
            require(self.test(not (sign == 1 and not lower_nonzero)), "signed minimum cannot be negated")
            carry = 1
            self.move("word", -1)
            while self.test(self.read("word") != "^"):
                bit = self.read("word")
                self.gate("signed-negate")
                self.write("word", (1-bit) ^ carry)
                carry &= 1-bit
                self.move("word", -1)
        else:
            self.home("word")
        self.move("word", 1)
        while self.test(self.read("word") != "$"):
            self.write("output", self.read("word"))
            self.move("output", 1)
            self.move("word", 1)
        self.home("word")

    def emit(self, source, negate):
        self.move(source, 1)
        while self.test(self.read(source) != "$"):
            self.emit_word(source, negate)
            self.emit_word(source, negate)
        self.home(source)

    def run(self, header, descriptor, width_descriptor, source):
        self.gate("entry")
        require(not self.used, "one-shot consumer")
        self.used = True
        # Fixed-arity identity admission, never a payload/descriptor decoding.
        self.gate("distinct-borrows")
        require(header is not descriptor and header is not width_descriptor and header is not source
                and descriptor is not width_descriptor and descriptor is not source
                and width_descriptor is not source, "distinct borrowed tapes")
        for borrowed in (header, descriptor, width_descriptor, source):
            for role in ("prefix", "suffix", "output", "word", "a", "b"):
                require(self.test(borrowed is not self.tapes[role]), "borrowed tape aliases private role")
        self.tapes.update(header=header, descriptor=descriptor, width=width_descriptor, source=source)
        success = False
        self.initialize()
        try:
            epsilon, a_zero, b_zero = self.counts_from_header()
            require(self.test(self.read("source") == "^"), "source origin")
            require(self.test(self.read("width") == "^"), "width origin")
            self.move("source", 1)
            self.split("a", "prefix", a_zero)
            self.split("b", "suffix", b_zero)
            require(self.test(self.read("source") == "$"), "complete source packet")
            self.home("source")
            self.move("output", 1)
            self.gate("segment-sign")
            self.emit("suffix", not epsilon)
            self.emit("prefix", bool(epsilon))
            self.write("output", "$")
            self.home("output")
            self.gate("success")
            success = True
            return self.tapes["output"]
        finally:
            # Guaranteed on valid admitted inputs, including signed-minimum
            # rejection. Malformed external tapes are outside this contract.
            self.home("source")
            self.home("width")
            self.clear("prefix")
            self.clear("suffix")
            self.clear("word")
            self.clear("a")
            self.clear("b")
            if self.test(not success):
                self.clear("output")
