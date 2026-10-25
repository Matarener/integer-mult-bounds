"""Sequential unary-addressed AND/XOR interpreter. Nick Petalas. Apache-2.0."""

from dataclasses import dataclass

MAX_PROGRAM = 2_000_000
MAX_WIRES = 4096


def require(condition, message):
    if not condition:
        raise ValueError(message)


class Tape:
    """The only cell-access boundary; all execution access uses the current head."""

    def __init__(self, cells, borrowed=False):
        self.cells = list(cells)
        self.head = 0
        self.borrowed = borrowed
        self.reads = self.writes = self.moves = 0
        self.furthest = 0

    def read(self):
        self.reads += 1
        return self.cells[self.head]

    def write(self, symbol):
        require(not self.borrowed, 'write to borrowed tape')
        require(symbol in '^01$_', 'invalid cell symbol')
        self.writes += 1
        self.cells[self.head] = symbol

    def move(self, direction):
        require(direction in (-1, 1), 'nonunit head move')
        target = self.head + direction
        require(0 <= target < len(self.cells), 'tape extent exceeded')
        self.moves += 1
        self.head = target
        self.furthest = max(self.furthest, target)

    def tally(self):
        return {'read': self.reads, 'write': self.writes, 'move': self.moves,
                'extent': self.furthest + 1}


def unary(text, position, bound):
    start = position
    for _ in range(bound + 1):
        require(position < len(text), 'unterminated operand')
        if text[position] != '1':
            require(text[position] == '0' and position > start, 'invalid operand')
            return position - start - 1, position + 1
        position += 1
    raise ValueError('operand exceeds wire bound')


def inspect(program, address):
    """Uncharged host admission, before tape execution or private allocation."""
    require(type(program) is str and 2 <= len(program) <= MAX_PROGRAM,
            'program extent invalid')
    require(type(address) is tuple and 1 <= len(address) <= MAX_WIRES - 2,
            'address extent invalid')
    require(all(type(x) is int and x in (0, 1) for x in address), 'nonbit address')
    require(program[0] == '^' and program[-1] == '$', 'program markers invalid')
    position, wires, gates, outputs = 1, len(address) + 2, 0, 0
    for _ in range(len(program)):
        if position == len(program) - 1:
            require(outputs > 0, 'missing output')
            return wires, gates, outputs
        op = program[position]
        require(op in 'AXO' and (op == 'O' or outputs == 0), 'invalid opcode order')
        position += 1
        for _ in range(1 if op == 'O' else 2):
            operand, position = unary(program, position, wires)
            require(operand < wires, 'nonpreceding operand')
        if op == 'O':
            outputs += 1
        else:
            gates += 1
            wires += 1
            require(wires <= MAX_WIRES, 'wire capacity exceeded')
    raise ValueError('program parse did not terminate')


def encode(circuit):
    """Host lowering; its complete unary byte storage is invoiced separately."""
    require(type(circuit.slots) is tuple and 1 <= len(circuit.slots) <= MAX_WIRES - 2,
            'invalid compiler input extent')
    require(type(circuit.gates) is tuple and len(circuit.gates) <= MAX_WIRES,
            'invalid compiler gate extent')
    require(type(circuit.outputs) is tuple and 1 <= len(circuit.outputs) <= MAX_WIRES,
            'invalid compiler output extent')
    first = len(circuit.slots) + 2
    for j, row in enumerate(circuit.gates):
        require(type(row) is tuple and len(row) == 3, 'invalid compiler gate')
        op, a, b = row
        require(op in ('and', 'xor') and type(a) is int and type(b) is int
                and 0 <= a < first + j and 0 <= b < first + j,
                'invalid compiler operands')
    require(all(type(w) is int and 0 <= w < first + len(circuit.gates)
                for w in circuit.outputs), 'invalid compiler output wire')
    length = 2 + sum(3 + a + b + 2 for _, a, b in circuit.gates)
    length += sum(3 + w for w in circuit.outputs)
    require(first + len(circuit.gates) <= MAX_WIRES, 'wire capacity exceeded')
    require(length <= MAX_PROGRAM, 'program capacity exceeded')
    chunks = ['^']
    for op, a, b in circuit.gates:
        chunks.extend(('A' if op == 'and' else 'X', '1' * (a + 1), '0',
                       '1' * (b + 1), '0'))
    for wire in circuit.outputs:
        chunks.extend(('O', '1' * (wire + 1), '0'))
    chunks.append('$')
    result = ''.join(chunks)
    require(len(result) == length, 'encoded length invariant failed')
    return result


def rewind(tape):
    for _ in range(len(tape.cells)):
        if tape.read() == '^':
            return
        tape.move(-1)
    raise ValueError('missing origin')


def seek_blank(tape):
    for _ in range(len(tape.cells)):
        if tape.read() == '_':
            return
        tape.move(1)
    raise ValueError('missing blank')


def fetch(program, wires):
    """Consume one unary operand, starting the wire head at its origin."""
    for _ in range(len(wires.cells)):
        symbol = program.read()
        if symbol == '0':
            bit = wires.read()
            require(bit in '01', 'operand does not name a bit')
            program.move(1)
            rewind(wires)
            return int(bit)
        require(symbol == '1', 'invalid unary instruction')
        program.move(1)
        wires.move(1)
    raise ValueError('unary instruction exceeds tape')


def initialize(address, wires):
    wires.write('^')
    wires.move(1)
    wires.write('0')
    wires.move(1)
    wires.write('1')
    wires.move(1)
    address.move(1)
    for _ in range(len(address.cells)):
        bit = address.read()
        if bit == '$':
            rewind(address)
            rewind(wires)
            return
        wires.write(bit)
        address.move(1)
        wires.move(1)
    raise ValueError('address terminator absent')


def clear_private(tape):
    """Erase a contiguous written prefix and restore the original blank origin."""
    rewind(tape)
    seek_blank(tape)
    tape.move(-1)
    for _ in range(len(tape.cells)):
        symbol = tape.read()
        tape.write('_')
        if symbol == '^':
            return
        tape.move(-1)
    raise ValueError('private cleanup did not reach origin')


def interpret(program, wires, output):
    program.move(1)
    output.write('^')
    output.move(1)
    for _ in range(len(program.cells)):
        op = program.read()
        if op == '$':
            output.write('$')
            rewind(output)
            return
        require(op in 'AXO', 'invalid executed opcode')
        program.move(1)
        a = fetch(program, wires)
        if op == 'O':
            output.write(str(a))
            output.move(1)
        else:
            b = fetch(program, wires)
            seek_blank(wires)
            wires.write(str(a & b if op == 'A' else a ^ b))
            rewind(wires)
    raise ValueError('execution did not terminate')


@dataclass(frozen=True)
class Execution:
    bits: tuple
    counts: tuple
    program_cells: int
    wire_cells: int
    heads: tuple
    restored: bool
    blank_private: bool


def execute(program_text, address_bits):
    wire_count, _, outputs = inspect(program_text, address_bits)
    program = Tape(program_text, borrowed=True)
    address = Tape('^' + ''.join(map(str, address_bits)) + '$', borrowed=True)
    wires = Tape('_' * (wire_count + 2))
    output = Tape('_' * (outputs + 3))
    initialize(address, wires)
    interpret(program, wires, output)
    clear_private(wires)
    rewind(program)
    tapes = (program, address, wires, output)
    # These are post-execution observations, not machine instructions.
    bits = tuple(int(x) for x in output.cells[1:outputs + 1])
    restored = ''.join(program.cells) == program_text and address.head == 0
    blank = all(x == '_' for x in wires.cells)
    require(restored and blank and all(t.head == 0 for t in tapes),
            'tape return invariant failed')
    return Execution(bits, tuple(t.tally() for t in tapes), len(program.cells),
                     len(wires.cells), tuple(t.head for t in tapes), restored, blank)
