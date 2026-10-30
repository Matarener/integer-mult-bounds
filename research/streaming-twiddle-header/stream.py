"""Read-once register transducer for physical twiddle addresses.

Nick Petalas. Apache-2.0. This is a register model, not a tape interpreter.
"""

from dataclasses import dataclass


def require(condition, message):
    if not condition:
        raise ValueError(message)


@dataclass(frozen=True)
class Shape:
    ell: int
    width: int
    long_axes: tuple
    h: int
    opposite: bool = False

    def __post_init__(self):
        require(type(self.ell) is int and 2 <= self.ell <= 256, 'ell limit')
        require(type(self.width) is int and 1 <= self.width < self.ell, 'width limit')
        require(type(self.long_axes) is tuple and 1 <= len(self.long_axes) <= 64
                and all(type(x) is bool for x in self.long_axes), 'axis limit')
        require(type(self.h) is int and 0 <= self.h < self.ell, 'round limit')
        require(type(self.opposite) is bool, 'direction must be Boolean')


def physical_slots(shape):
    """Generate slots with shape-only loop indices; retain no input bits."""
    axes = len(shape.long_axes)
    low = (shape.ell - 1) % shape.width
    chunks = (shape.ell - 1) // shape.width
    for i in range(axes):
        if shape.long_axes[i]:
            yield i, shape.ell - 1
    for v in range(low - 1, -1, -1):
        for i in range(axes):
            yield i, v
    for j in range(chunks - 1, -1, -1):
        for i in range(axes):
            for offset in range(shape.width - 1, -1, -1):
                yield i, low + j * shape.width + offset


def allocation(shape):
    active = tuple(i for i, long in enumerate(shape.long_axes)
                   if shape.h < shape.ell - (not long))
    low = (shape.ell - 1) % shape.width
    pending = low if low <= shape.h < shape.ell - 1 else 0
    word = max(pending, 1)
    bits = len(active) * word + shape.h + 1 if active and shape.h else 0
    return active, pending, word, bits


class Gates:
    """Count actual logical gate evaluations; the count is shape-dependent."""

    def __init__(self):
        self.count = 0

    def xor(self, left, right):
        self.count += 1
        return left ^ right

    def and_(self, left, right):
        self.count += 1
        return left & right


def add_bits(total, word, enabled, ops, shift=0):
    """Fixed-width full adders, six AND/XOR gates per accumulator bit.

    word reads an existing bank word, or the current input bit. No separate
    word-sized term register is required. Overflow is discarded.
    """
    carry = 0
    for v in range(len(total)):
        left = total[v]
        source_bit = (word >> (v - shift)) & 1 if v >= shift else 0
        right = ops.and_(source_bit, enabled)
        mixed = ops.xor(left, right)
        total[v] = ops.xor(mixed, carry)
        carry = ops.xor(ops.and_(left, right), ops.and_(mixed, carry))


def advance(shape, pending, bank, axis, position, bit, total, ops):
    """One input-symbol transition; axis is the dense participating index."""
    if position == shape.h:
        add_bits(total, bank[axis], bit, ops)
        bank[axis] = bit
    elif position < shape.h:
        if position < pending:
            bank[axis] |= bit << position
        else:
            add_bits(total, bit, bank[axis], ops, position)


def finish(total, shape, ops):
    """Negate in place if needed, then write the final output register."""
    if not shape.opposite:
        carry = 1
        for v in range(len(total)):
            inverse = ops.xor(total[v], 1)
            total[v] = ops.xor(inverse, carry)
            carry = ops.and_(inverse, carry)
    header = 0
    for v in range(len(total) - 1, -1, -1):
        header = 2 * header + total[v]
    return header << (shape.ell - shape.h)


def produce(shape, address):
    """Consume one iterator, including an EOF check, and clear private registers.

    Bit counts describe mathematical register widths between input symbols.
    Python object sizes, receipt fields and arithmetic temporaries are not those
    register widths. PROOF.md supplies a separate bit-level space bound.
    """
    require(type(shape) is Shape, 'Shape required')
    active, pending, word, bits = allocation(shape)
    indices = {axis: j for j, axis in enumerate(active)}
    bank = [0] * len(active) if bits else []
    total = [0] * (shape.h + 1) if bits else []
    reads, additions = 0, 0
    ops = Gates()
    source = iter(address)
    sentinel = object()
    try:
        for axis, position in physical_slots(shape):
            bit = next(source, sentinel)
            require(type(bit) is int and bit in (0, 1), 'missing or non-bit input')
            reads += 1
            if shape.h and axis in indices:
                j = indices[axis]
                advance(shape, pending, bank, j, position, bit, total, ops)
                additions += position == shape.h or pending <= position < shape.h
                require(0 <= bank[j] < 1 << word, 'bank register overflow')
                require(all(x in (0, 1) for x in total), 'non-bit accumulator')
        require(next(source, sentinel) is sentinel, 'trailing input')
        header = finish(total, shape, ops)
        result = {'header': header, 'reads': reads, 'eof_probes': 1,
                  'bank_bits': len(active) * word if bits else 0,
                  'accumulator_bits': len(total), 'data_bits': bits,
                  'register_additions': additions, 'boolean_gates': ops.count}
    finally:
        for j in range(len(bank)):
            bank[j] = 0
        for v in range(len(total)):
            total[v] = 0
    require(not any(bank) and not any(total), 'private registers not clear')
    return result


def prefix_states(shape):
    """Exact residual count at the complete early low-prefix cut."""
    low = (shape.ell - 1) % shape.width
    require(1 <= low <= shape.h < shape.ell - 1, 'early-prefix theorem domain')
    axes = len(shape.long_axes)
    return 1 << (axes * low)
