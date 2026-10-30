"""Binary-distance refinement of Mihir Srivastava's PR5364 contract.

New construction produced by Nick Petalas. Apache-2.0.
The inherited tape actions and descriptor/cleanup recipe retain PR5364 credit.
Only symbols, fixed role indices and a sixteen-bit mask are controller state.
"""

from stack import (
    BITS, BLANK, LEFT, ROLES, Controller as UnaryController,
    clear, emit, need, rewind, take,
)


def increment(counter):
    """Increment a little-endian count and return to its local beginning."""
    while True:
        symbol = counter.read()
        need(symbol in BITS or symbol == BLANK, 'counter alphabet')
        if symbol != '1':
            counter.write('1')
            break
        counter.write('0')
        counter.move(1)
    rewind(counter)


def store_count(counter, control):
    """Emit most-significant-first u/: digits and erase the counter."""
    while counter.read() != BLANK:
        counter.move(1)
    while True:
        counter.move(-1)
        symbol = counter.read()
        if symbol == LEFT:
            counter.move(1)
            return
        need(symbol in BITS, 'stored counter alphabet')
        emit(control, 'u' if symbol == '0' else ':')
        counter.write(BLANK)


def load_count(control, counter):
    """Consume reversed count digits; return the separate presence bit."""
    leading = BLANK
    symbol = take(control)
    while symbol in ('u', ':'):
        emit(counter, '0' if symbol == 'u' else '1')
        leading = symbol
        symbol = take(control)
    need(leading in (BLANK, ':'), 'canonical binary distance')
    need(symbol in BITS, 'role presence flag')
    rewind(counter)
    return symbol


def decrement(counter):
    """Subtract one, or erase the fixed-width zero word and return false."""
    while True:
        symbol = counter.read()
        need(symbol in BITS or symbol == BLANK, 'counter alphabet')
        if symbol == '1':
            counter.write('0')
            rewind(counter)
            return True
        if symbol == BLANK:
            break
        counter.write('1')
        counter.move(1)
    while True:
        counter.move(-1)
        symbol = counter.read()
        if symbol == LEFT:
            counter.move(1)
            return False
        need(symbol == '1', 'zero-count cleanup')
        counter.write(BLANK)


class Controller(UnaryController):
    """The same nineteen tapes and nine symbols, with binary distance fields."""

    def push(self):
        need(self.reverse.read() == BLANK, 'counter scratch empty')
        emit(self.control, '[')
        while True:
            symbol = self.descriptor.read()
            if symbol == BLANK:
                break
            need(symbol in BITS, 'binary descriptor')
            emit(self.control, symbol)
            self.descriptor.write(BLANK)
            self.descriptor.move(1)
        rewind(self.descriptor, erased=True)
        emit(self.control, ':')
        for role in range(ROLES):
            present = (self.occupied >> role) & 1
            emit(self.control, '1' if present else '0')
            tape = self.payload[role]
            while True:
                symbol = tape.read()
                if symbol == BLANK:
                    break
                need(symbol in BITS, 'binary parent payload')
                need(present, 'absent role must be empty')
                tape.move(1)
                increment(self.reverse)
            store_count(self.reverse, self.control)
            tape.write(LEFT)
            tape.move(1)
            emit(self.control, ';')
        emit(self.control, ']')
        self.occupied = 0

    def pop(self):
        for tape in self.payload:
            clear(tape)
        clear(self.descriptor)
        need(self.reverse.read() == BLANK, 'counter scratch empty')
        need(take(self.control) == ']', 'frame top delimiter')
        self.occupied = 0
        for role in reversed(range(ROLES)):
            need(take(self.control) == ';', 'role terminator')
            tape = self.payload[role]
            tape.move(-1)
            need(tape.read() == LEFT, 'payload suspension delimiter')
            tape.write(BLANK)
            flag = load_count(self.control, self.reverse)
            while decrement(self.reverse):
                tape.move(-1)
                need(tape.read() in BITS, 'return distance within parent')
            if flag == '1':
                self.occupied |= 1 << role
        need(take(self.control) == ':', 'descriptor terminator')
        symbol = take(self.control)
        while symbol in BITS:
            emit(self.reverse, symbol)
            symbol = take(self.control)
        need(symbol == '[', 'frame beginning delimiter')
        while True:
            self.reverse.move(-1)
            symbol = self.reverse.read()
            if symbol == LEFT:
                break
            need(symbol in BITS, 'reverse scratch alphabet')
            self.reverse.write(BLANK)
            emit(self.descriptor, symbol)
        self.reverse.move(1)
        rewind(self.descriptor)


def action_bound(descriptor_bits, return_distance, child_bits):
    """Complete matched-boundary bound, including all child cleanup."""
    need(min(descriptor_bits, return_distance, child_bits) >= 0, 'bound domain')
    return 22 * descriptor_bits + 46 * return_distance + 613 + 7 * child_bits
