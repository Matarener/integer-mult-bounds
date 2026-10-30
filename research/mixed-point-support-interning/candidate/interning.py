"""Exact support interning with XOR-linear lookup keys."""
MASK = (1 << 64) - 1
MAX_INPUTS = 25000
MAX_NODES = 4000000


def seed(index):
    value = (index + 0x9E3779B97F4A7C15) & MASK
    value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & MASK
    value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & MASK
    return value ^ (value >> 31)


def initialize(c, bits=64):
    if not 0 <= bits <= 64:
        raise ValueError('fingerprint bits outside 0..64')
    if not 1 <= len(c.support) <= MAX_INPUTS + 1:
        raise ValueError('input capacity exceeded')
    if c.support != [0] + [1 << i for i in range(len(c.support) - 1)]:
        raise ValueError('independent basis inputs required')
    mask = (1 << bits) - 1
    c.fingerprint = [0] + [seed(i) & mask for i in range(len(c.support)-1)]
    c.lookup = {}
    for node, key in enumerate(c.fingerprint):
        previous = c.lookup.get(key)
        if previous is None:
            c.lookup[key] = node
        elif isinstance(previous, int):
            c.lookup[key] = [previous, node]
        else:
            previous.append(node)


def add(self, a, b):
    if not a:
        return b
    if not b:
        return a
    left, right = self.support[a], self.support[b]
    if left & right:
        raise ValueError('Cancellation is forbidden')
    value = left | right
    key = self.fingerprint[a] ^ self.fingerprint[b]
    previous = self.lookup.get(key)
    if previous is not None:
        if isinstance(previous, int):
            if self.support[previous] == value:
                return previous
        else:
            for node in previous:
                if self.support[node] == value:
                    return node
    node = len(self.support)
    if node >= MAX_NODES:
        raise ValueError('node capacity exceeded')
    if previous is None:
        self.lookup[key] = node
    elif isinstance(previous, int):
        self.lookup[key] = [previous, node]
    else:
        previous.append(node)
    self.support.append(value)
    self.args.append((a, b))
    self.fingerprint.append(key)
    return node
