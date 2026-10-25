"""Encoded sequential twiddle controller. Nick Petalas, Apache-2.0."""

from collections import Counter as Tally


def require(ok, message):
    if not ok:
        raise ValueError(message)


LEFT, RIGHT = 2, 3
ROLES = ('address', 'bank', 'total', 'output')
REGISTERS = ('input', 'branch', 'pending', 'carry', 'old', 'inverse', 'zero', 'one')
# Every entry belongs to a fixed finite alphabet, independent of the shape.
OPS = tuple((kind, role, reg) for kind in ('read', 'write')
            for role in ROLES for reg in REGISTERS) + tuple(
                ('move', role, direction) for role in ROLES for direction in (-1, 1)) + (
    ('gate', 'mask', 0), ('gate', 'ripple', 0), ('gate', 'invert', 0),
    ('gate', 'negate', 0), ('gate', 'reset', 0), ('gate', 'carry-one', 0),
    ('gate', 'save-branch', 0), ('gate', 'save-pending', 0))
CODE = {op: i for i, op in enumerate(OPS)}


class Tape:
    """Current-cell operations only; the integer head is simulator state."""

    def __init__(self, cells):
        self.cells = list(cells)
        self.head = 0
        self.counts = Tally()

    def read(self):
        self.counts['read'] += 1
        return self.cells[self.head]

    def write(self, value):
        self.cells[self.head] = value
        self.counts['write'] += 1

    def move(self, direction):
        require(direction in (-1, 1), 'bad unit move')
        require(0 <= self.head + direction < len(self.cells), 'head out of bounds')
        self.head += direction
        self.counts['move'] += 1


class Binary:
    """A delimited little-endian counter. No decoded value controls execution."""

    def __init__(self, width, descriptor):
        self.width = width
        self.tape = Tape((0,) * (width + 2))
        self.tape.write(LEFT)
        self.tape.move(1)
        # One zero bit per actual borrowed symbol, including ^ and $.
        for _unused in range(width + 1):
            token = descriptor.read()
            self.tape.write(0)
            self.tape.move(1)
            if token == '$':
                break
            descriptor.move(1)
        else:
            raise ValueError('unterminated descriptor initialization')
        self.tape.write(RIGHT)
        self.home()
        for _unused in range(width + 1):
            if descriptor.read() == '^':
                return
            descriptor.move(-1)
        raise ValueError('descriptor return budget exhausted')

    def home(self):
        for _unused in range(self.width + 2):
            if self.tape.read() == LEFT:
                return
            self.tape.move(-1)
        raise ValueError('missing left delimiter')

    def zero(self):
        self.tape.move(1)
        for _unused in range(self.width + 1):
            if self.tape.read() == RIGHT:
                self.home()
                return
            self.tape.write(0)
            self.tape.move(1)
        raise ValueError('missing right delimiter')

    def change(self, decrement=False):
        carry = 1
        self.tape.move(1)
        for _unused in range(self.width + 1):
            bit = self.tape.read()
            if bit == RIGHT:
                self.home()
                require(not carry, 'counter overflow or underflow')
                return
            self.tape.write(bit ^ carry)
            carry &= (1 - bit) if decrement else bit
            self.tape.move(1)
        raise ValueError('missing right delimiter')

    def combine(self, other, operation):
        require(self is not other and self.width == other.width, 'counter alias')
        require(operation in ('copy', 'add', 'sub', 'compare'), 'bad counter operation')
        self.tape.move(1)
        other.tape.move(1)
        carry, relation = 0, 0
        for _unused in range(self.width + 1):
            a, b = self.tape.read(), other.tape.read()
            if a == RIGHT:
                require(b == RIGHT and not carry, 'counter width or arithmetic failure')
                self.home()
                other.home()
                return relation
            if operation == 'copy':
                self.tape.write(b)
            elif operation == 'compare':
                if a != b:
                    relation = 1 if a else -1
            else:
                self.tape.write(a ^ b ^ carry)
                if operation == 'add':
                    carry = (a & b) | ((a ^ b) & carry)
                else:
                    carry = ((1 - a) & b) | ((1 - (a ^ b)) & carry)
            self.tape.move(1)
            other.tape.move(1)
        raise ValueError('missing right delimiter')

    def copy(self, other):
        self.combine(other, 'copy')

    def add(self, other):
        self.combine(other, 'add')

    def sub(self, other):
        self.combine(other, 'sub')

    def compare(self, other):
        return self.combine(other, 'compare')

    def value(self):
        """Diagnostics only. The controller never calls this method."""
        return sum(bit << i for i, bit in enumerate(self.tape.cells[1:-1]))

    def erase(self):
        self.zero()
        self.tape.move(1)
        for _unused in range(self.width + 1):
            if self.tape.read() == RIGHT:
                self.tape.write(0)
                self.home()
                self.tape.write(0)
                return
            self.tape.move(1)
        raise ValueError('missing right delimiter during erasure')


def encode(ell, k, h, axes, opposite=False):
    require(type(ell) is int and 2 <= ell <= 32, 'bad ell')
    require(type(k) is int and 1 <= k < ell, 'bad K')
    require(type(h) is int and 0 <= h < ell, 'bad h')
    require(type(axes) is tuple and 1 <= len(axes) <= 16, 'bad axes')
    require(all(type(x) is bool for x in axes), 'non-Boolean axis')
    require(type(opposite) is bool, 'bad direction')
    return '1' * ell + '#' + '1' * k + '#' + '1' * h + '#' + ''.join(
        'L' if x else 'S' for x in axes) + '#' + ('+' if opposite else '-') + '#'


def admit(text, address):
    """Reject malformed/excessive external inputs before private execution."""
    require(type(text) is str and len(text) <= 116, 'bad descriptor extent')
    parts = text.split('#')
    require(len(parts) == 6 and parts[-1] == '', 'bad descriptor framing')
    require(all(set(x) <= {'1'} for x in parts[:3]), 'bad unary field')
    ell, k, h = map(len, parts[:3])
    require(set(parts[3]) <= {'L', 'S'}, 'bad axis symbol')
    axes = tuple(x == 'L' for x in parts[3])
    require(parts[4] in ('+', '-'), 'bad direction symbol')
    require(encode(ell, k, h, axes, parts[4] == '+') == text, 'noncanonical descriptor')
    extent = sum(ell if x else ell - 1 for x in axes)
    require(type(address) is tuple and len(address) == extent, 'bad address extent')
    require(all(type(x) is int and x in (0, 1) for x in address), 'bad address bit')
    return ell, k, h, axes, parts[4] == '+'


class Controller:
    NAMES = ('ell', 'k', 'h', 'b', 'q', 'a', 'stride', 'upper', 'lower', 'v',
             'base', 'target', 'low', 'j', 'zero', 'address-pos', 'bank-pos',
             'total-pos', 'output-pos', 'bank-size', 'total-size')

    def __init__(self, descriptor, address, trace=False):
        ell, k, h, axes, opposite = admit(descriptor, address)
        b = (ell - 1) % k
        a = b if b <= h < ell - 1 else 0
        d = sum(h < ell - (not long) for long in axes)
        self.data = {'address': Tape(address), 'bank': Tape((0,) * max(1, d * max(a, 1))),
                     'total': Tape((0,) * (h + 1)), 'output': Tape((0,) * (ell + 1))}
        # Host arithmetic here admits exact tape extents, never a data schedule.
        self.descriptor = Tape('^' + descriptor + '$')
        self.width = len(descriptor) + 2
        self.c = {name: Binary(self.width, self.descriptor) for name in self.NAMES}
        self.bits = dict.fromkeys(REGISTERS, 0)
        self.bits['one'] = 1
        self.gates = Tally()
        self.trace = [] if trace else None
        self.first = True
        self.limit = len(address) + ell + 1

    def emit(self, kind, role, reg):
        opcode = CODE[kind, role, reg]
        if self.trace is not None:
            self.trace.append(opcode)
        if kind == 'move':
            self.data[role].move(reg)
        elif kind == 'read':
            self.bits[reg] = self.data[role].read()
        elif kind == 'write':
            self.data[role].write(self.bits[reg])
        else:
            self.gate(role)

    def gate(self, action):
        b = self.bits
        if action == 'mask':
            b['carry'] = b['branch'] & b['pending']
            self.gates['and'] += 1
        elif action == 'ripple':
            b['inverse'] = b['old'] ^ b['carry']
            b['carry'] &= b['old']
            self.gates['and'] += 1
            self.gates['xor'] += 1
        elif action == 'invert':
            b['inverse'] = b['old'] ^ 1
            self.gates['xor'] += 1
        elif action == 'negate':
            b['old'] = b['inverse'] ^ b['carry']
            b['carry'] &= b['inverse']
            self.gates['and'] += 1
            self.gates['xor'] += 1
        elif action == 'carry-one':
            b['carry'] = 1
        elif action == 'save-branch':
            b['branch'] = b['input']
        elif action == 'save-pending':
            b['pending'] = b['input']
        else:
            require(action == 'reset', 'unknown Boolean action')
            for name in REGISTERS:
                b[name] = int(name == 'one')

    def seek(self, role, target):
        position = self.c[role + '-pos']
        for _unused in range(self.limit + 1):
            relation = position.compare(target)
            if not relation:
                return
            direction = -1 if relation > 0 else 1
            self.emit('move', role, direction)
            position.change(direction < 0)
        raise ValueError('data seek budget exhausted')

    def input_slot(self):
        if self.first:
            self.first = False
        else:
            self.emit('move', 'address', 1)
            self.c['address-pos'].change()
        self.emit('read', 'address', 'input')

    def parse(self):
        self.descriptor.move(1)
        for field in ('ell', 'k', 'h'):
            for _unused in range(self.width):
                token = self.descriptor.read()
                self.descriptor.move(1)
                if token == '#':
                    break
                require(token == '1', 'invalid unary symbol')
                self.c[field].change()
            else:
                raise ValueError('unterminated unary field')
        # The finite direction flag is read from the actual descriptor.
        for _unused in range(self.width):
            if self.descriptor.read() == '#':
                self.descriptor.move(1)
                self.opposite = self.descriptor.read() == '+'
                break
            self.descriptor.move(1)
        else:
            raise ValueError('unterminated axes')
        self.c['upper'].copy(self.c['ell'])
        self.c['upper'].change(True)
        self.c['b'].copy(self.c['upper'])
        for _unused in range(self.width):
            if self.c['b'].compare(self.c['k']) < 0:
                break
            self.c['b'].sub(self.c['k'])
            self.c['q'].change()
        else:
            raise ValueError('division budget exhausted')
        if self.c['h'].compare(self.c['upper']) < 0 and self.c['b'].compare(self.c['h']) <= 0:
            self.c['a'].copy(self.c['b'])
        self.c['stride'].copy(self.c['a'])
        if self.c['stride'].compare(self.c['zero']) == 0:
            self.c['stride'].change()
        for long in self.axes():
            if self.c['h'].compare(self.c['upper']) < 0 or long:
                self.c['bank-size'].add(self.c['stride'])
        if self.c['bank-size'].compare(self.c['zero']) == 0:
            self.c['bank-size'].change()
        self.c['total-size'].copy(self.c['h'])
        self.c['total-size'].change()

    def axes(self):
        # Marker scans, not a retained axis/participation table.
        for _unused in range(self.width):
            if self.descriptor.read() == '^':
                break
            self.descriptor.move(-1)
        fields = 0
        for _unused in range(self.width):
            if self.descriptor.read() == '#':
                fields += 1
            self.descriptor.move(1)
            if fields == 3:
                break
        for _unused in range(self.width):
            token = self.descriptor.read()
            if token == '#':
                return
            yield token == 'L'
            self.descriptor.move(1)
        raise ValueError('axis scan budget exhausted')

    def add(self):
        self.emit('gate', 'mask', 0)
        self.c['j'].copy(self.c['v'])
        for _unused in range(self.width):
            self.seek('total', self.c['j'])
            self.emit('read', 'total', 'old')
            self.emit('gate', 'ripple', 0)
            self.emit('write', 'total', 'inverse')
            if self.c['j'].compare(self.c['h']) == 0:
                return
            self.c['j'].change()
        raise ValueError('ripple budget exhausted')

    def consume(self, active):
        self.input_slot()
        if not active:
            return
        c = self.c
        if c['v'].compare(c['a']) < 0:
            c['target'].copy(c['base'])
            c['target'].add(c['v'])
            self.seek('bank', c['target'])
            self.emit('write', 'bank', 'input')
        elif c['v'].compare(c['h']) == 0:
            self.emit('gate', 'save-branch', 0)
            c['low'].zero()
            for _unused in range(self.width):
                if c['low'].compare(c['a']) == 0:
                    break
                c['target'].copy(c['base'])
                c['target'].add(c['low'])
                self.seek('bank', c['target'])
                self.emit('read', 'bank', 'pending')
                self.emit('write', 'bank', 'zero')
                c['target'].copy(c['v'])
                c['v'].copy(c['low'])
                self.add()
                c['v'].copy(c['target'])
                c['low'].change()
            self.seek('bank', c['base'])
            self.emit('write', 'bank', 'branch')
        elif c['v'].compare(c['h']) < 0:
            self.seek('bank', c['base'])
            self.emit('read', 'bank', 'branch')
            self.emit('gate', 'save-pending', 0)
            self.add()

    def schedule(self):
        c = self.c
        c['v'].copy(c['upper'])
        c['base'].zero()
        for long in self.axes():
            if long:
                self.consume(True)
                c['base'].add(c['stride'])
        c['v'].copy(c['b'])
        for _unused in range(self.width):
            if c['v'].compare(c['zero']) == 0:
                break
            c['v'].change(True)
            c['base'].zero()
            for long in self.axes():
                active = c['h'].compare(c['upper']) < 0 or long
                self.consume(active)
                if active:
                    c['base'].add(c['stride'])
        c['upper'].change(True)
        for _unused in range(self.width):
            if c['q'].compare(c['zero']) == 0:
                return
            c['lower'].copy(c['upper'])
            c['lower'].change()
            c['lower'].sub(c['k'])
            c['base'].zero()
            for long in self.axes():
                c['v'].copy(c['upper'])
                for _step in range(self.width):
                    # Top-round participation is recovered without an axis index.
                    c['target'].copy(c['ell'])
                    c['target'].change(True)
                    active = c['h'].compare(c['target']) < 0 or long
                    self.consume(active)
                    if c['v'].compare(c['lower']) == 0:
                        break
                    c['v'].change(True)
                else:
                    raise ValueError('chunk budget exhausted')
                if active:
                    c['base'].add(c['stride'])
            c['q'].change(True)
            if c['q'].compare(c['zero']) > 0:
                c['upper'].sub(c['k'])
        raise ValueError('chunk count budget exhausted')

    def finish(self):
        c = self.c
        if not self.opposite and c['h'].compare(c['zero']) > 0:
            self.emit('gate', 'carry-one', 0)
            c['j'].zero()
            for _unused in range(self.width):
                self.seek('total', c['j'])
                self.emit('read', 'total', 'old')
                self.emit('gate', 'invert', 0)
                self.emit('gate', 'negate', 0)
                self.emit('write', 'total', 'old')
                if c['j'].compare(c['h']) == 0:
                    break
                c['j'].change()
        c['v'].copy(c['h'])
        c['j'].zero()
        for _unused in range(self.width):
            self.seek('output', c['j'])
            if c['j'].compare(c['h']) <= 0:
                self.seek('total', c['v'])
                self.emit('read', 'total', 'old')
                self.emit('write', 'output', 'old')
                if c['v'].compare(c['zero']) > 0:
                    c['v'].change(True)
            else:
                self.emit('write', 'output', 'zero')
            if c['j'].compare(c['ell']) == 0:
                return
            c['j'].change()
        raise ValueError('output budget exhausted')

    def execute(self):
        self.parse()
        self.schedule()
        self.finish()
        for role in ('bank', 'total'):
            self.c['j'].zero()
            for _unused in range(self.limit):
                if self.c['j'].compare(self.c[role + '-size']) == 0:
                    break
                self.seek(role, self.c['j'])
                self.emit('write', role, 'zero')
                self.c['j'].change()
            else:
                raise ValueError('erasure budget exhausted')
        for role in ROLES:
            self.seek(role, self.c['zero'])
        for _unused in range(self.width):
            if self.descriptor.read() == '^':
                break
            self.descriptor.move(-1)
        for counter in self.c.values():
            counter.erase()
        self.emit('gate', 'reset', 0)

    def invoice(self):
        return {'data': {role: dict(tape.counts) for role, tape in self.data.items()},
                'control_tape_actions': sum(sum(c.tape.counts.values()) for c in self.c.values()),
                'descriptor_actions': sum(self.descriptor.counts.values()),
                'data_cells': sum(len(t.cells) for t in self.data.values()),
                'control_cells': len(self.c) * (self.width + 2),
                'descriptor_cells': len(self.descriptor.cells), 'gates': dict(self.gates)}
