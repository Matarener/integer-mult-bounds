"""Named-bit arithmetic and a shape-only access invoice, independent of Tape.

Nick Petalas. Apache-2.0.
"""


def physical_slots(ell, width, axes):
    b = (ell - 1) % width
    top = [(i, ell - 1) for i in range(len(axes)) if axes[i]]
    early = sorted(((i, v) for i in range(len(axes)) for v in range(b)),
                   key=lambda x: (-x[1], x[0]))
    rest = sorted(((i, v) for i in range(len(axes)) for v in range(b, ell - 1)),
                  key=lambda x: (-((x[1] - b) // width), x[0], -x[1]))
    return tuple(top + early + rest)


def exponent(shape, address):
    slots = physical_slots(shape.ell, shape.width, shape.long_axes)
    named = {s: (address >> (len(slots) - 1 - j)) & 1
             for j, s in enumerate(slots)}
    total = sum(named[i, shape.h] * sum((1 << v) * named[i, v]
                                       for v in range(shape.h))
                for i, long in enumerate(shape.long_axes)
                if shape.h < shape.ell - (not long))
    sign = 1 if shape.opposite else -1
    return sign * (1 << (shape.ell - shape.h)) * total % (1 << (shape.ell + 1))


class Invoice:
    """Record access targets, without reading bits or simulating arithmetic."""
    def __init__(self):
        self.heads = dict.fromkeys(('address', 'bank', 'total', 'output'), 0)
        self.counts = {r: dict(reads=0, writes=0, moves=0) for r in self.heads}

    def access(self, role, target, reads=0, writes=0):
        self.counts[role]['moves'] += abs(target - self.heads[role])
        self.heads[role] = target
        self.counts[role]['reads'] += reads
        self.counts[role]['writes'] += writes

    def clear(self, role, size):
        for j in range(size):
            self.access(role, j, writes=1)
        self.access(role, 0)


def expected(shape, count):
    slots = tuple(reversed(physical_slots(shape.ell, shape.width, shape.long_axes)))
    axes = [i for i, long in enumerate(shape.long_axes)
            if shape.h < shape.ell - (not long)]
    bases = {axis: k * (shape.h + 1) for k, axis in enumerate(axes)}
    n, h, f = shape.h + 1, shape.h, int(not shape.opposite)
    sizes = dict(address=len(slots), bank=max(1, len(axes) * n), total=n,
                 output=shape.ell + 1)
    inv, relevant = Invoice(), 0
    for record in range(count):
        if f:
            for t in range(n):
                inv.access('total', t, reads=1, writes=1)
        for j in range(shape.ell + 1):
            if j < n:
                inv.access('total', h - j, reads=1)
            inv.access('output', j, writes=1)
        if f:
            for t in range(n):
                inv.access('total', t, reads=1, writes=1)
        inv.clear('output', shape.ell + 1)
        # Bit j flips on this increment iff 2**j divides record+1.
        for j, (axis, v) in enumerate(slots):
            if (record + 1) % (1 << j):
                break
            inv.access('address', j, reads=1, writes=1)
            if axis in bases and v <= h:
                relevant += 1
                base = bases[axis]
                inv.access('bank', base + v, reads=1, writes=1)
                if v < h:
                    inv.access('bank', base + h, reads=1)
                for t in range(n):
                    if v == h and t < h:
                        inv.access('bank', base + t, reads=1)
                    inv.access('total', t, reads=1, writes=1)
        inv.access('address', 0)
    for role, size in sizes.items():
        inv.clear(role, size)
    flips = sum(count // (1 << j) for j in range(len(slots)))
    ands = 2 * n * relevant + 2 * f * n * count
    xors = flips + relevant + 4 * n * relevant + 4 * f * n * count
    work = sum(sum(b.values()) for b in inv.counts.values()) + ands + xors
    return dict(tapes=inv.counts, AND=ands, XOR=xors, flips=flips,
                cells=sum(sizes.values()), work=work)
