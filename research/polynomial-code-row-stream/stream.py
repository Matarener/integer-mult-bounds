"""Incremental exact XOR permutations. Produced by Nick Petalas; Apache-2.0."""

MAX_BITS = 1 << 21


def require(condition, message):
    if not condition:
        raise ValueError(message)


class PermutationStream:
    """Retain one preceding row; discard geometry when the width changes."""

    def __init__(self):
        self.width = 0
        self.masks = {}
        self.base = -1
        self.previous_index = 0
        self.previous_row = 0
        self.requests = 0
        self.swaps = 0
        self.direct_swaps = 0
        self.incremental_requests = 0

    def __call__(self, bits, index, n):
        require(type(n) is int and 1 <= n <= MAX_BITS and n & (n - 1) == 0
                and type(index) is int and 0 <= index < n
                and type(bits) is int and 0 <= bits < 1 << n,
                "Invalid bounded packed row or XOR permutation")
        if n != self.width:
            self.width, self.masks, self.base = n, {}, -1
        delta = index ^ self.previous_index
        use_previous = bits == self.base and delta.bit_count() < index.bit_count()
        start, change = (self.previous_row, delta) if use_previous else (bits, index)
        row = self._apply(start, change)
        self.base, self.previous_index, self.previous_row = bits, index, row
        self.requests += 1
        self.direct_swaps += index.bit_count()
        self.incremental_requests += int(use_previous)
        return row

    def _apply(self, bits, index):
        for bit in range(self.width.bit_length() - 1):
            if index >> bit & 1:
                stride = 1 << bit
                mask = self.masks.get(bit)
                if mask is None:
                    mask = ((1 << self.width) - 1) // ((1 << (2 * stride)) - 1)
                    mask *= (1 << stride) - 1
                    self.masks[bit] = mask
                bits = ((bits & mask) << stride) | ((bits >> stride) & mask)
                self.swaps += 1
        return bits
