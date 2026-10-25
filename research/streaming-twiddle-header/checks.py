"""Independent physical/exponent and residual-function checks.

Nick Petalas. Apache-2.0.
"""

from itertools import product
import random

from stream import Shape, allocation, physical_slots, prefix_states, produce, require


def direct(shape, slots, address):
    named = dict(zip(slots, address))
    value = sum(named.get((i, shape.h), 0)
                * sum((1 << v) * named[i, v] for v in range(shape.h))
                for i in range(len(shape.long_axes)))
    signed = value if shape.opposite else -value
    return signed * (1 << (shape.ell - shape.h)) % (1 << (shape.ell + 1))


class Once:
    """A consumable bit iterator, with no indexing or rewind operation."""

    def __init__(self, values):
        self.values = iter(values)
        self.reads = 0
        self.eof = 0

    def __iter__(self):
        return self

    def __next__(self):
        try:
            bit = next(self.values)
        except StopIteration:
            self.eof += 1
            raise
        self.reads += 1
        return bit


def check_address(source, shape, slots, address, circuit=None):
    stream = Once(address)
    actual = produce(shape, stream)
    expected = direct(shape, slots, address)
    require(actual['header'] == expected, 'stream/direct exponent differs')
    require(stream.reads == len(slots) == actual['reads'] and stream.eof == 1,
            'read-once/EOF contract differs')
    if circuit is not None:
        require(source.decode_word(source.evaluate(circuit, address)) == expected,
                'circuit/stream exponent differs')
    active, pending, word, bits = allocation(shape)
    expected_bits = len(active) * max(pending, 1) + shape.h + 1
    require(bits == (expected_bits if shape.h and active else 0), 'data width differs')
    require(actual['data_bits'] == bits and word == max(pending, 1), 'receipt width differs')
    expected_additions = len(active) * (1 + shape.h - pending) if shape.h else 0
    require(actual['register_additions'] == expected_additions, 'addition schedule differs')
    expected_gates = 6 * (shape.h + 1) * expected_additions
    expected_gates += 3 * (shape.h + 1) if bits and not shape.opposite else 0
    require(actual['boolean_gates'] == expected_gates, 'Boolean gate bill differs')
    return actual


def exhaustive(source):
    rows = []
    for ell in range(2, 6):
        for width in range(1, ell):
            for axes in range(1, 4):
                for longs in product((False, True), repeat=axes):
                    for h in range(ell):
                        for opposite in (False, True):
                            shape = Shape(ell, width, longs, h, opposite)
                            slots = tuple(physical_slots(shape))
                            require(slots == source.named_slots(ell, width, longs),
                                    'physical layout differs')
                            if len(slots) > 10:
                                continue
                            circuit = source.compile_round(ell, width, longs, h, opposite)
                            for address in product((0, 1), repeat=len(slots)):
                                check_address(source, shape, slots, address, circuit)
                            rows.append({'ell': ell, 'K': width, 'long_axes': list(longs),
                                         'h': h, 'opposite': opposite,
                                         'addresses': 1 << len(slots),
                                         'data_bits': allocation(shape)[3]})
    return rows


def residuals():
    """Enumerate every physical prefix and every physical suffix, not the formula."""
    rows = []
    for ell in range(3, 7):
        for width in range(2, ell):
            low = (ell - 1) % width
            for axes in range(1, 4):
                for longs in product((False, True), repeat=axes):
                    for h in range(low, ell - 1):
                        shape = Shape(ell, width, longs, h)
                        slots = tuple(physical_slots(shape))
                        if not low or len(slots) > 10:
                            continue
                        cut = sum(longs) + axes * low
                        functions = set()
                        for prefix in product((0, 1), repeat=cut):
                            outputs = tuple(direct(shape, slots, prefix + suffix)
                                            for suffix in product((0, 1), repeat=len(slots) - cut))
                            functions.add(outputs)
                        require(len(functions) == prefix_states(shape), 'prefix residual count differs')
                        rows.append({'ell': ell, 'K': width, 'long_axes': list(longs),
                                     'h': h, 'cut': cut, 'addresses': 1 << len(slots),
                                     'residual_classes': str(len(functions)), 'required_bits': axes * low})
    return rows


def wide(source):
    rng = random.Random(183559)
    rows = []
    fixtures = [(8, 4, (True,) * 3 + (False,) * 9, 5),
                (16, 8, (False, True) * 12, 11),
                (256, 128, (True, False) * 32, 200)]
    for _ in range(60):
        ell = rng.randrange(2, 80)
        longs = tuple(rng.choice((False, True)) for _ in range(rng.randrange(1, 17)))
        fixtures.append((ell, rng.randrange(1, ell), longs, rng.randrange(ell)))
    for j, (ell, width, longs, h) in enumerate(fixtures):
        for opposite in (False, True):
            shape = Shape(ell, width, longs, h, opposite)
            slots = tuple(physical_slots(shape))
            require(slots == source.named_slots(ell, width, longs), 'wide layout differs')
            circuit = source.compile_round(ell, width, longs, h, opposite)
            for values in (tuple(0 for _ in slots), tuple(1 for _ in slots),
                           tuple(rng.randrange(2) for _ in slots)):
                check_address(source, shape, slots, values, circuit)
            if j < 3 and not opposite:
                rows.append({'ell': ell, 'K': width, 'axes': len(longs), 'h': h,
                             'low_prefix_bits_per_axis': (ell - 1) % width,
                             'prefix_states': str(prefix_states(shape)),
                             'prefix_required_bits': len(longs) * ((ell - 1) % width),
                             'producer_data_bits': allocation(shape)[3],
                             'final_sum_bits': h + 1})
    return 6 * len(fixtures), rows


def rejects(call, message):
    try:
        call()
    except (ValueError, TypeError):
        return
    raise ValueError(message)


def boundaries():
    bad = [(True, 1, (True,), 0), (1, 1, (True,), 0), (257, 1, (True,), 0),
           (5, 0, (True,), 1), (5, 5, (True,), 1), (5, 1, (), 1),
           (5, 1, (1,), 1), (5, 1, (True,) * 65, 1),
           (5, 1, (True,), -1), (5, 1, (True,), 5), (5, 1, (True,), True)]
    for args in bad:
        rejects(lambda: Shape(*args), 'invalid shape accepted')
    shape = Shape(4, 2, (True,), 2)
    for address in [(0,) * 3, (0,) * 5, (0, 0, 2, 0), (0, 0, True, 0)]:
        rejects(lambda: produce(shape, iter(address)), 'invalid stream accepted')
    rejects(lambda: Shape(5, 2, (True,), 1, 1), 'invalid direction accepted')
    rejects(lambda: prefix_states(Shape(4, 1, (True,), 1)), 'empty low prefix accepted')
    rejects(lambda: prefix_states(Shape(6, 4, (True,), 0)), 'late-branch domain accepted')
    rejects(lambda: produce(None, iter(())), 'missing shape accepted')
    return len(bad) + 8


def failure_cleanup():
    """Inspect the real producer frame after input failure, including iterator failure."""
    shape = Shape(4, 2, (True,), 2)

    def broken_input():
        yield from (0, 1, 1)
        raise RuntimeError('deliberate iterator failure')

    for address in (iter((0, 1, 1, 2)), iter((0, 1, 1, 1, 0)), broken_input()):
        try:
            produce(shape, address)
        except (ValueError, RuntimeError) as error:
            traceback = error.__traceback__
            found = False
            for _ in range(16):
                if traceback is None:
                    break
                if traceback.tb_frame.f_code.co_name == 'produce':
                    frame = traceback.tb_frame.f_locals
                    require(not any(frame['bank']) and not any(frame['total']),
                            'failed producer retained private registers')
                    found = True
                traceback = traceback.tb_next
            require(found, 'producer failure frame missing')
        else:
            raise ValueError('deliberate failing input succeeded')
    return 3
