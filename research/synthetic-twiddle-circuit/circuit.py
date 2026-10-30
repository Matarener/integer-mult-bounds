"""Explicit bit circuits for the synthetic transform's address-dependent exponent.

Nick Petalas. Apache-2.0. The source transform and earlier physical layout audit
are credited in README.md. No coefficient arithmetic occurs in this module.
"""

from dataclasses import dataclass


def require(condition, message):
    if not condition:
        raise ValueError(message)


def named_slots(ell, width, long_axes):
    """Return physical MSB order directly, without simulating source bit moves."""
    require(type(ell) is int and 2 <= ell <= 256, 'ell outside 2..256')
    require(type(width) is int and 1 <= width < ell, 'invalid chunk width')
    require(type(long_axes) is tuple and 1 <= len(long_axes) <= 64,
            'axis count outside 1..64')
    require(all(type(x) is bool for x in long_axes), 'axes must be Boolean')
    b, q = (ell - 1) % width, (ell - 1) // width
    prefix = [(i, ell - 1) for i, long in enumerate(long_axes) if long]
    prefix += [(i, h) for h in range(b - 1, -1, -1) for i in range(len(long_axes))]
    chunks = [(i, b + (q - 1 - j) * width + t)
              for j in range(q) for i in range(len(long_axes))
              for t in range(width - 1, -1, -1)]
    return tuple(prefix + chunks)


@dataclass(frozen=True)
class Circuit:
    slots: tuple
    gates: tuple
    outputs: tuple
    ell: int
    h: int
    axes: int
    opposite: bool


def gate(gates, inputs, operation, left, right):
    """Append one gate; wires 0 and 1 are constants, then physical input bits."""
    result = inputs + 2 + len(gates)
    require(operation in ('and', 'xor') and 0 <= left < result and 0 <= right < result,
            'invalid gate operands')
    gates.append((operation, left, right))
    return result


def add_word(gates, inputs, left, right):
    """Fixed-width little-endian ripple adder; final overflow is discarded."""
    carry, result = 0, []
    require(len(left) == len(right), 'unequal adder widths')
    for a, b in zip(left, right):
        mixed = gate(gates, inputs, 'xor', a, b)
        result.append(gate(gates, inputs, 'xor', mixed, carry))
        both = gate(gates, inputs, 'and', a, b)
        incoming = gate(gates, inputs, 'and', mixed, carry)
        carry = gate(gates, inputs, 'xor', both, incoming)
    return tuple(result)


def negate_word(gates, inputs, word):
    """Two's complement modulo 2**len(word), expressed only with bit gates."""
    carry, result = 1, []
    for bit in word:
        inverse = gate(gates, inputs, 'xor', bit, 1)
        result.append(gate(gates, inputs, 'xor', inverse, carry))
        carry = gate(gates, inputs, 'and', inverse, carry)
    return tuple(result)


def compile_round(ell, width, long_axes, h, opposite=False):
    slots = named_slots(ell, width, long_axes)
    require(type(h) is int and 0 <= h < ell, 'invalid round')
    require(type(opposite) is bool, 'invalid direction')
    location = {slot: 2 + j for j, slot in enumerate(slots)}
    axes = [i for i, long in enumerate(long_axes) if h < ell - (not long)]
    gates, total = [], (0,) * (h + 1)
    if h and axes:
        for i in axes:
            branch = location[i, h]
            term = tuple(gate(gates, len(slots), 'and', branch, location[i, v])
                         for v in range(h)) + (0,)
            total = add_word(gates, len(slots), total, term)
        if not opposite:
            total = negate_word(gates, len(slots), total)
    outputs = tuple(reversed(total)) + (0,) * (ell - h)
    result = Circuit(slots, tuple(gates), outputs, ell, h, len(axes), opposite)
    require(len(outputs) == ell + 1, 'wrong output width')
    expected = (len(axes) * (6 * h + 5) + (0 if opposite else 3 * (h + 1))
                if h and axes else 0)
    require(len(gates) == expected, 'gate count differs')
    return result


def validate(program):
    """Validate an externally supplied topology before evaluating any gate."""
    require(type(program) is Circuit, 'invalid circuit')
    require(type(program.ell) is int and 2 <= program.ell <= 256, 'invalid ell')
    require(type(program.h) is int and 0 <= program.h < program.ell, 'invalid h')
    require(type(program.axes) is int and 0 <= program.axes <= 64, 'invalid axes')
    require(type(program.opposite) is bool, 'invalid direction')
    require(type(program.slots) is tuple and 1 <= len(program.slots) <= 16384,
            'invalid input width')
    require(all(type(s) is tuple and len(s) == 2
                and all(type(v) is int for v in s)
                and 0 <= s[0] < 64 and 0 <= s[1] < program.ell for s in program.slots),
            'invalid named slots')
    require(len(set(program.slots)) == len(program.slots), 'duplicate named slots')
    require(type(program.gates) is tuple and len(program.gates) <= 100000,
            'invalid gate extent')
    first = len(program.slots) + 2
    for j, row in enumerate(program.gates):
        require(type(row) is tuple and len(row) == 3, 'invalid gate row')
        op, a, b = row
        require(op in ('and', 'xor') and type(a) is int and type(b) is int
                and 0 <= a < first + j and 0 <= b < first + j, 'invalid topology')
    require(type(program.outputs) is tuple and len(program.outputs) == program.ell + 1,
            'invalid output extent')
    require(all(type(w) is int and 0 <= w < first + len(program.gates)
                for w in program.outputs), 'invalid output wire')


def evaluate(program, address):
    """Evaluate one complete MSB-first input word and return the residue bits.

    This is a random-access circuit interpreter, not a fixed-tape lowering.
    Its private wire cells are cleared before returning; the input is immutable.
    """
    validate(program)
    require(type(address) is tuple and len(address) == len(program.slots),
            'invalid address extent')
    require(all(type(x) is int and x in (0, 1) for x in address), 'non-bit address')
    first = len(address) + 2
    wires = [0] * (first + len(program.gates))
    wires[1] = 1
    wires[2:first] = address
    try:
        for j, (op, a, b) in enumerate(program.gates):
            wires[first + j] = wires[a] & wires[b] if op == 'and' else wires[a] ^ wires[b]
        result = tuple(wires[w] for w in program.outputs)
        require(all(x in (0, 1) for x in result), 'non-bit result')
        return result
    finally:
        for j in range(len(wires)):
            wires[j] = 0


def encode_address(value, bits):
    require(type(bits) is int and 1 <= bits <= 16384, 'invalid address width')
    require(type(value) is int and 0 <= value < 1 << bits, 'address out of range')
    return tuple((value >> shift) & 1 for shift in range(bits - 1, -1, -1))


def decode_word(word):
    require(type(word) is tuple and 1 <= len(word) <= 16384, 'invalid word extent')
    require(all(type(bit) is int and bit in (0, 1) for bit in word), 'non-bit word')
    result = 0
    for bit in word:
        result = 2 * result + bit
    return result
