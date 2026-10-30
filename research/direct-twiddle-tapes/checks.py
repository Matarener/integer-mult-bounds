"""Independent exact arithmetic and shape-only access bills. Nick Petalas, Apache-2.0."""

from itertools import product


def require(condition, message):
    if not condition:
        raise ValueError(message)


def decode(bits):
    value = 0
    for bit in bits:
        value = 2 * value + bit
    return value


def formula(shape, slots, bits):
    named = dict(zip(slots, bits))
    total = sum(named[i, shape.h] * sum((1 << v) * named[i, v]
                                      for v in range(shape.h))
                for i, long in enumerate(shape.axes)
                if shape.h < shape.ell - (not long))
    sign = 1 if shape.opposite else -1
    return sign * (1 << (shape.ell - shape.h)) * total % (1 << (shape.ell + 1))


def motion(visits):
    """An access list is a sequence of targets, never actual machine head state."""
    return sum(abs(right - left) for left, right in zip((0,) + visits, visits + (0,)))


def expected(shape, slots):
    """Derive accesses independently from named-bit arrival positions."""
    h = shape.h
    active = [i for i, long in enumerate(shape.axes) if h < shape.ell - (not long)]
    d, b = len(active), (shape.ell - 1) % shape.width
    a = b if b <= h < shape.ell - 1 else 0
    stride, extent, n = max(a, 1), len(slots), h + 1
    bank_cells = max(1, d * stride)
    times = {slot: j for j, slot in enumerate(slots)}
    events = []
    for rank, axis in enumerate(active):
        base = rank * stride
        for v in range(a):
            events.append((times[axis, v], -1, (base + v,), ()))
        for v in range(h):
            when = max(times[axis, h], times[axis, v])
            bank = (base + v, base + v) if v < a else (base,)
            events.append((when, v if v < a else -1, bank, tuple(range(v, n))))
        events.append((times[axis, h], a, (base,), ()))
    events.sort(key=lambda event: (event[0], event[1]))
    bank_visits = tuple(pos for event in events for pos in event[2]) + tuple(range(bank_cells))
    sum_visits = tuple(pos for event in events for pos in event[3])
    f = int(bool(h and d and not shape.opposite))
    sum_visits += tuple(range(n)) * f + tuple(range(h, -1, -1)) + tuple(range(n))
    length = d * h * (h + 3) // 2
    return {'address': (extent, 0, 2 * (extent - 1)),
            'bank': (d * h, 2 * d * a + d + bank_cells, motion(bank_visits)),
            'total': (length + (f + 1) * n, length + (f + 1) * n,
                      motion(sum_visits)),
            'output': (0, shape.ell + 1, 2 * shape.ell),
            'and': d * h + length + f * n, 'xor': length + 2 * f * n,
            'cells': extent + bank_cells + n + shape.ell + 1}


def closed_accumulator_moves(shape):
    active, a, unused = shape.dimensions()
    d, h = len(active), shape.h
    if not h or not d:
        return 4 * h
    f = int(not shape.opposite)
    b = (shape.ell - 1) % shape.width
    first = 0 if a else b - 1 if h == shape.ell - 1 and b else h - 1
    return d * h * (h + 1) + (2 * f + 2) * h + 2 * first


def one(tapes, canonical, shape, bits):
    slots = canonical.named_slots(shape.ell, shape.width, shape.axes)
    require(tuple(shape.slots()) == slots, 'physical layout differs')
    machine = tapes.Machine(shape, bits)
    machine.execute()
    require(decode(machine.output.cells) == formula(shape, slots, bits), 'formula differs')
    program = canonical.compile_round(shape.ell, shape.width, shape.axes, shape.h,
                                      shape.opposite)
    require(tuple(machine.output.cells) == canonical.evaluate(program, bits), 'circuit differs')
    require(tuple(machine.address.cells) == bits and machine.address.head == 0,
            'borrowed address/head differs')
    require(not any(machine.bank.cells + machine.total.cells), 'private tape not blank')
    require(machine.bank.head == machine.total.head == machine.output.head == 0,
            'private/output head differs')
    bill = machine.invoice()
    require(bill == expected(shape, slots), 'primitive invoice differs')
    require(bill['total'][2] == closed_accumulator_moves(shape), 'closed move formula differs')
    work = sum(sum(bill[name]) for name in ('address', 'bank', 'total', 'output'))
    work += bill['and'] + bill['xor']
    require(work <= 20 * (len(bits) + shape.ell + 1) ** 2, 'quadratic bound differs')
    return work, bill['cells']


def small(tapes, canonical):
    fixtures = addresses = 0
    max_work = max_cells = 0
    for ell in range(2, 7):
        for width in range(1, ell):
            for axes in ((False,), (True,), (False, True), (True, False),
                         (False, False), (True, True), (True, False, False)):
                extent = sum(ell if x else ell - 1 for x in axes)
                if extent > 10:
                    continue
                for h, opposite in product(range(ell), (False, True)):
                    shape = tapes.Shape(ell, width, axes, h, opposite)
                    for bits in product((0, 1), repeat=extent):
                        work, cells = one(tapes, canonical, shape, bits)
                        max_work, max_cells = max(max_work, work), max(max_cells, cells)
                        addresses += 1
                    fixtures += 1
    return {'fixtures': fixtures, 'addresses': addresses,
            'max_primitive_work': max_work, 'max_data_cells': max_cells}


def wide(tapes, canonical):
    rows = []
    for ell, width, axes, h in ((8, 4, (True,) * 3 + (False,) * 9, 5),
                                (16, 5, (False, True, False), 12),
                                (48, 17, (True, False, True, False), 35),
                                (128, 65, (True, False), 98),
                                (256, 128, (True, False), 200)):
        extent = sum(ell if x else ell - 1 for x in axes)
        for opposite in (False, True):
            shape = tapes.Shape(ell, width, axes, h, opposite)
            bills = []
            for bits in ((0,) * extent, (1,) * extent,
                         tuple((j * 13 + j // 7) % 2 for j in range(extent))):
                work, cells = one(tapes, canonical, shape, bits)
                bills.append(work)
            require(len(set(bills)) == 1, 'input-dependent primitive count')
            rows.append({'ell': ell, 'width': width, 'axes': list(axes), 'h': h,
                         'opposite': opposite, 'addresses': 3,
                         'work': bills[0], 'cells': cells})
    return rows


def boundaries(tapes):
    valid = tapes.Shape(4, 2, (True, False), 2)
    wrong = [tapes.Shape(True, 1, (True,), 0), tapes.Shape(257, 1, (True,), 0),
             tapes.Shape(4, 0, (True,), 0), tapes.Shape(4, 4, (True,), 0),
             tapes.Shape(4, 1, (), 0), tapes.Shape(4, 1, (True,) * 65, 0),
             tapes.Shape(4, 1, (1,), 0), tapes.Shape(4, 1, [True], 0),
             tapes.Shape(4, 1, (True,), -1), tapes.Shape(4, 1, (True,), 4),
             tapes.Shape(4, 1, (True,), 0, 1)]
    rejected = 0
    for shape in wrong:
        try:
            tapes.Machine(shape, (0,) * 7)
        except ValueError:
            rejected += 1
    for bits in ((0,) * 6, (0,) * 8, (0,) * 6 + (True,), (0,) * 6 + (2,)):
        try:
            tapes.Machine(valid, bits)
        except ValueError:
            rejected += 1
    require(rejected == len(wrong) + 4, 'boundary rejection differs')
    return rejected


def failures(tapes):
    """Inject actual primitive failure after private data becomes nonzero."""
    shape = tapes.Shape(8, 4, (True, False), 5)
    receipt = []
    for fail_after in (3, 9, 13):
        machine = tapes.Machine(shape, (1,) * 15)
        original = machine.address.read

        def fail():
            if machine.address.reads == fail_after:
                raise RuntimeError('injected borrowed-tape read failure')
            return original()

        machine.address.read = fail
        try:
            machine.execute()
        except RuntimeError:
            pass
        else:
            raise ValueError('injected failure not observed')
        require(not any(machine.bank.cells + machine.total.cells + machine.output.cells),
                'failure return not blank')
        require(machine.address.head == 0 and tuple(machine.address.cells) == (1,) * 15,
                'failure borrowed return differs')
        machine.address.read = original
        machine.execute()
        require(decode(machine.output.cells) == 16, 'same-machine retry differs')
        receipt.append(fail_after)
    return receipt
