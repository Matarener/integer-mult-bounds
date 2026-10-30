# SPDX-License-Identifier: Apache-2.0
"""Park fixed complex roles on one physical stack without a Python continuation.

I use the fixed-role protocol of PR2809. Complex numerical descriptors are
Count bodies, so this stack does not need the BIT caller's second Arena bank.
"""
import cohort
cohort.activate()
from records import Tape
from words import BLANK, LEFT, need

BODY = (0, 1, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13)
# Body symbols use four binary digits; these two existing record symbols
# therefore remain unambiguous delimiters without extending Tape's alphabet.
ROLE_END = 13
FRAME_END = 12


class Parking:
    def __init__(self, roles):
        self.roles = tuple(roles)
        need(self.roles and len({id(t) for t in self.roles}) == len(self.roles), "fixed distinct parked roles")
        self.stack = Tape()
        self.reverse = Tape()

    def park(self):
        need(self.stack.read() == BLANK and self.reverse.read() == BLANK, "canonical parking ports")
        for tape in self.roles:
            tape.rewind()
            while tape.read() != BLANK:
                symbol = tape.read()
                need(symbol in BODY, "dense complex role alphabet")
                for bit in range(4):
                    self.stack.write((symbol >> bit) & 1)
                    self.stack.step(1)
                tape.write(BLANK)
                tape.step(1)
            self.stack.write(ROLE_END)
            self.stack.step(1)
            tape.rewind()
        self.stack.write(FRAME_END)
        self.stack.step(1)

    def restore(self):
        need(self.stack.read() == BLANK and self.reverse.read() == BLANK, "canonical restoration ports")
        need(all(t.read() == BLANK for t in self.roles), "child closes roles before restoration")
        self.stack.step(-1)
        need(self.stack.read() == FRAME_END, "one parent frame available")
        self.stack.write(BLANK)
        for tape in reversed(self.roles):
            self.stack.step(-1)
            need(self.stack.read() == ROLE_END, "fixed parent role delimiter")
            self.stack.write(BLANK)
            while True:
                self.stack.step(-1)
                symbol = self.stack.read()
                if symbol in (ROLE_END, FRAME_END, LEFT):
                    self.stack.step(1)
                    break
                need(symbol in (0, 1), "complete parked role bits")
                self.reverse.append(symbol)
                self.stack.write(BLANK)
            # Reversing twice restores the original order. The physical head
            # finds LEFT; no role length or stack position enters control.
            self.reverse.step(-1)
            while self.reverse.read() != LEFT:
                symbol = 0
                for bit in range(4):
                    digit = self.reverse.read()
                    need(digit in (0, 1), "complete reverse port")
                    symbol |= digit << bit
                    self.reverse.write(BLANK)
                    self.reverse.step(-1)
                need(symbol in BODY, "restored fixed role symbol")
                tape.append(symbol)
            self.reverse.step(1)
            tape.rewind()
        need(self.stack.read() == BLANK and self.reverse.read() == BLANK, "restored canonical ports")

    def empty(self):
        """Check the root boundary without consuming an ancestor frame."""
        need(self.stack.read() == BLANK and self.reverse.read() == BLANK, "closed parking ports")
        self.stack.step(-1)
        value = self.stack.read()
        self.stack.step(1)
        need(value == LEFT, "empty root continuation stack")


class FiniteFields:
    """Only bounded source/PC/cover labels; widths and cardinalities stay on tapes."""
    def __init__(self, bounds):
        self.bounds = tuple(bounds)
        need(all(type(b) is int and b > 0 for b in self.bounds), "finite continuation alphabet")
        self.widths = tuple(max(1, (b - 1).bit_length()) for b in self.bounds)

    def write(self, tape, values):
        need(len(values) == len(self.bounds) and tape.read() == BLANK, "empty finite header")
        for value, bound, width in zip(values, self.bounds, self.widths):
            need(type(value) is int and 0 <= value < bound, "bounded continuation value")
            for bit in range(width):
                tape.append((value >> bit) & 1)
        tape.rewind()

    def read(self, tape):
        tape.rewind()
        result = []
        for bound, width in zip(self.bounds, self.widths):
            value = 0
            for bit in range(width):
                symbol = tape.read()
                need(symbol in (0, 1), "complete finite header")
                value |= symbol << bit
                tape.step(1)
            need(value < bound, "finite header value")
            result.append(value)
        need(tape.read() == BLANK, "exact finite header extent")
        tape.rewind()
        return tuple(result)


def transfer(source, target):
    need(source is not target, "distinct owned transfer ports")
    source.rewind()
    target.clear()
    while source.read() != BLANK:
        symbol = source.read()
        need(symbol in BODY, "dense transferred packet or Count")
        target.append(symbol)
        source.write(BLANK)
        source.step(1)
    source.rewind()
    target.rewind()
