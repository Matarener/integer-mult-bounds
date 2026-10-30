"""Exact low-weight binary words. Ali Romman with OpenAI Codex. Apache-2.0."""


def require(condition, message):
    if not condition:
        raise ValueError(message)


def population_planes(values):
    """Add one-bit lanes without a carry between lanes."""
    buckets = [list(values)]
    output = []
    while buckets:
        current = buckets.pop()
        carry = []
        while len(current) >= 3:
            a, b, c = current.pop(), current.pop(), current.pop()
            parity = a ^ b
            current.append(parity ^ c)
            carry.append((a & b) | (parity & c))
        if len(current) == 2:
            a, b = current
            output.append(a ^ b)
            carry.append(a & b)
        else:
            output.append(current[0] if current else 0)
        if carry:
            buckets.append(carry)
    return output


def at_most(planes, bound, mask):
    """Return exactly the lanes whose nonnegative integer is at most bound."""
    if bound >= (1 << len(planes)) - 1:
        return mask
    equal, less = mask, 0
    for power in range(len(planes) - 1, -1, -1):
        bits = planes[power]
        if bound >> power & 1:
            less |= equal & ~bits
            equal &= bits
        else:
            equal &= ~bits
    return (less | equal) & mask


def low_weight_words(generators, width, maximum, batch_bits=16):
    """Yield every word once, including zero, from independent binary rows.

    Each row is a nonnegative integer with at most width bits. The memory for
    bit planes is O(width * 2^min(batch_bits, dimension)) bits. There are no
    cached results. Batch size changes storage and runtime, not the code.
    """
    require(type(width) is int and width >= 0, 'width must be a nonnegative integer')
    require(type(maximum) is int and 0 <= maximum <= width, 'invalid weight bound')
    require(type(batch_bits) is int and 1 <= batch_bits <= 20, 'batch bits must be in 1..20')
    rows = tuple(generators)
    pivots = {}
    for row in rows:
        require(type(row) is int and row >= 0 and row.bit_length() <= width,
                'invalid binary generator')
        reduced = row
        while reduced:
            pivot = reduced.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = reduced
                break
            reduced ^= pivots[pivot]
        require(reduced != 0, 'binary generators must be independent')
    count = min(batch_bits, len(rows))
    lanes = 1 << count
    mask = (1 << lanes) - 1
    patterns = []
    for bit in range(count):
        block = 1 << bit
        repetitions = mask // ((1 << (2 * block)) - 1)
        patterns.append(repetitions * (((1 << block) - 1) << block))
    columns = [0] * width
    for row, pattern in zip(rows[:count], patterns):
        while row:
            bit = row & -row
            columns[bit.bit_length() - 1] ^= pattern
            row ^= bit
    offset = 0
    for index in range(1 << (len(rows) - count)):
        if index:
            offset ^= rows[count + (index & -index).bit_length() - 1]
        values = list(columns)
        bits = offset
        while bits:
            bit = bits & -bits
            values[bit.bit_length() - 1] ^= mask
            bits ^= bit
        hits = at_most(population_planes(values), maximum, mask)
        while hits:
            bit = hits & -hits
            coefficient = bit.bit_length() - 1
            word = offset
            while coefficient:
                chosen = coefficient & -coefficient
                word ^= rows[chosen.bit_length() - 1]
                coefficient ^= chosen
            yield word
            hits ^= bit
