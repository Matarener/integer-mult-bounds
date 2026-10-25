"""Binary-program sequential AND/XOR machine. Nick Petalas. Apache-2.0."""

from dataclasses import dataclass

MAX_WIRES = 4096
MAX_PROGRAM = 200_000


def require(condition, message):
    if not condition:
        raise ValueError(message)


class Tape:
    """All executed cell access is at the head; each move is one cell."""

    def __init__(self, text, borrowed=False):
        self.cells = list(text)
        self.head = 0
        self.borrowed = borrowed
        self.counts = [0, 0, 0]

    def read(self):
        self.counts[0] += 1
        return self.cells[self.head]

    def write(self, symbol):
        require(not self.borrowed and symbol in '^01$_', 'invalid tape write')
        self.counts[1] += 1
        self.cells[self.head] = symbol

    def move(self, step):
        require(step in (-1, 1), 'nonunit move')
        require(0 <= self.head + step < len(self.cells), 'tape capacity exceeded')
        self.counts[2] += 1
        self.head += step


def home(tape):
    for _ in range(len(tape.cells)):
        if tape.read() == '^':
            return
        tape.move(-1)
    raise ValueError('missing origin')


def blank(tape):
    for _ in range(len(tape.cells)):
        if tape.read() == '_':
            return
        tape.move(1)
    raise ValueError('missing blank')


def erase(tape):
    """Start at origin, erase the nonblank prefix, and finish blank at origin."""
    blank(tape)
    tape.move(-1)
    for _ in range(len(tape.cells)):
        symbol = tape.read()
        tape.write('_')
        if symbol == '^':
            return
        tape.move(-1)
    raise ValueError('erasure did not reach origin')


def operand(text, position, bound):
    start = position
    for _ in range(MAX_WIRES.bit_length() + 1):
        require(position < len(text), 'unterminated binary operand')
        symbol = text[position]
        if symbol == '#':
            bits = text[start:position]
            require(bits and (len(bits) == 1 or bits[-1] == '1'),
                    'noncanonical binary operand')
            value = int(bits[::-1], 2)
            require(value < bound, 'nonpreceding operand')
            return value, position + 1
        require(symbol in '01', 'invalid binary digit')
        position += 1
    raise ValueError('binary operand too long')


def admit(program, address):
    """Host admission is outside the tape invoice and precedes construction."""
    require(type(program) is str and 2 <= len(program) <= MAX_PROGRAM,
            'invalid program extent')
    require(type(address) is tuple and 1 <= len(address) <= MAX_WIRES - 2,
            'invalid address extent')
    require(all(type(x) is int and x in (0, 1) for x in address), 'nonbit address')
    require(program[0] == '^' and program[-1] == '$', 'invalid program markers')
    position, wires, outputs = 1, len(address) + 2, 0
    for _ in range(len(program)):
        if position == len(program) - 1:
            require(outputs > 0, 'no output')
            return wires, outputs
        op = program[position]
        require(op in 'AXO' and (op == 'O' or outputs == 0), 'invalid opcode order')
        position += 1
        for _ in range(1 if op == 'O' else 2):
            _, position = operand(program, position, wires)
        if op == 'O':
            outputs += 1
        else:
            wires += 1
            require(wires <= MAX_WIRES, 'wire capacity exceeded')
    raise ValueError('program did not terminate')


def encode(inputs, gates, outputs):
    require(type(inputs) is int and 1 <= inputs <= MAX_WIRES - 2, 'invalid inputs')
    require(type(gates) is tuple and len(gates) <= MAX_WIRES, 'invalid gates')
    require(type(outputs) is tuple and 1 <= len(outputs) <= MAX_WIRES,
            'invalid outputs')
    chunks = ['^']
    for j, row in enumerate(gates):
        require(type(row) is tuple and len(row) == 3, 'invalid gate row')
        op, a, b = row
        require(op in ('and', 'xor') and type(a) is int and type(b) is int
                and 0 <= a < inputs + 2 + j and 0 <= b < inputs + 2 + j,
                'invalid gate operands')
        chunks.extend(('A' if op == 'and' else 'X', bin(a)[2:][::-1], '#',
                       bin(b)[2:][::-1], '#'))
    for w in outputs:
        require(type(w) is int and 0 <= w < inputs + 2 + len(gates),
                'invalid output wire')
        chunks.extend(('O', bin(w)[2:][::-1], '#'))
    chunks.append('$')
    result = ''.join(chunks)
    admit(result, (0,) * inputs)
    return result


def load(program, counter):
    counter.write('^')
    counter.move(1)
    any_one = False
    for _ in range(len(counter.cells)):
        symbol = program.read()
        if symbol == '#':
            counter.write('$')
            program.move(1)
            home(counter)
            return not any_one
        any_one = any_one or symbol == '1'
        counter.write(symbol)
        counter.move(1)
        program.move(1)
    raise ValueError('counter capacity exceeded')


def decrement(counter):
    """Keep canonical width; detect zero without a separate full-width scan."""
    counter.move(1)
    crossed_zero = False
    for _ in range(len(counter.cells)):
        symbol = counter.read()
        require(symbol in '01', 'counter underflow')
        counter.write('0' if symbol == '1' else '1')
        if symbol == '1':
            counter.move(1)
            last = counter.read() == '$'
            if last and crossed_zero:
                counter.write('_')
                counter.move(-1)
                counter.write('$')
            else:
                counter.move(-1)
            home(counter)
            return last and not crossed_zero
        crossed_zero = True
        counter.move(1)
    raise ValueError('counter decrement exceeded extent')


def fetch(program, wires, counter):
    zero = load(program, counter)
    wires.move(1)
    for _ in range(len(wires.cells)):
        if zero:
            bit = wires.read()
            require(bit in '01', 'wire is not a bit')
            home(wires)
            erase(counter)
            return int(bit)
        zero = decrement(counter)
        wires.move(1)
    raise ValueError('wire traversal exceeded extent')


def initialize(address, wires):
    wires.write('^')
    for symbol in '01':
        wires.move(1)
        wires.write(symbol)
    wires.move(1)
    address.move(1)
    for _ in range(len(address.cells)):
        bit = address.read()
        if bit == '$':
            home(address)
            home(wires)
            return
        wires.write(bit)
        address.move(1)
        wires.move(1)
    raise ValueError('address terminator missing')


def interpret(program, wires, counter, output):
    program.move(1)
    output.write('^')
    output.move(1)
    for _ in range(len(program.cells)):
        op = program.read()
        if op == '$':
            output.write('$')
            home(output)
            return
        program.move(1)
        a = fetch(program, wires, counter)
        if op == 'O':
            output.write(str(a))
            output.move(1)
        else:
            b = fetch(program, wires, counter)
            blank(wires)
            wires.write(str(a & b if op == 'A' else a ^ b))
            home(wires)
    raise ValueError('execution did not terminate')


@dataclass(frozen=True)
class Execution:
    bits: tuple
    counts: tuple
    cells: tuple
    heads: tuple
    borrowed_restored: bool
    private_blank: bool


def execute(text, bits):
    count, outputs = admit(text, bits)
    width = (count - 1).bit_length()
    program = Tape(text, True)
    address_text = '^' + ''.join(map(str, bits)) + '$'
    address = Tape(address_text, True)
    wires, counter = Tape('_' * (count + 2)), Tape('_' * (width + 3))
    output = Tape('_' * (outputs + 3))
    initialize(address, wires)
    interpret(program, wires, counter, output)
    erase(wires)
    home(program)
    tapes = (program, address, wires, counter, output)
    # Observation only. No numerical wire index or decoded operand executes above.
    result = tuple(int(x) for x in output.cells[1:outputs + 1])
    restored = ''.join(program.cells) == text and ''.join(address.cells) == address_text
    private_blank = all(x == '_' for t in (wires, counter) for x in t.cells)
    heads = tuple(t.head for t in tapes)
    require(restored and private_blank and heads == (0,) * 5, 'return invariant failed')
    return Execution(result, tuple(tuple(t.counts) for t in tapes),
                     tuple(len(t.cells) for t in tapes), heads, restored, private_blank)
