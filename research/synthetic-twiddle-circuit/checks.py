"""Independent arithmetic, layout, and full-round checks of bit-only headers."""

import hashlib
import itertools
import json
from dataclasses import replace


def oracle(physical, ell, h, opposite, long_axes, address):
    """Read named slots and use the original integer formula, without gates."""
    named = {slot: (address >> (len(physical) - 1 - j)) & 1
             for j, slot in enumerate(physical)}
    exponent = 0
    for i, long in enumerate(long_axes):
        if h < ell - (not long):
            k = sum((1 << v) * named[i, v] for v in range(h))
            exponent -= (2 * (1 << ell) // (1 << (h + 1))) * named[i, h] * k
    return (-exponent if opposite else exponent) % (2 << ell)


def small_circuits(c, physical):
    """Every address on a declared finite shape domain, every round/direction."""
    shapes, circuits, cases, gates = 0, 0, 0, 0
    digest = hashlib.sha256()
    for ell in range(2, 7):
        for axes in range(1, 4):
            for flags in itertools.product((False, True), repeat=axes):
                if sum(ell if x else ell - 1 for x in flags) > 9:
                    continue
                for width in range(1, ell):
                    schedule = physical.plan(ell, width, flags)
                    slots = tuple(schedule['slots'])
                    c.require(c.named_slots(ell, width, flags) == slots, 'layout differs')
                    shapes += 1
                    for h in range(ell):
                        for opposite in (False, True):
                            p = c.compile_round(ell, width, flags, h, opposite)
                            circuits += 1
                            gates += len(p.gates)
                            for address in range(1 << len(slots)):
                                word = c.encode_address(address, len(slots))
                                out = c.evaluate(p, word)
                                expected = oracle(slots, ell, h, opposite, flags, address)
                                c.require(c.decode_word(out) == expected, 'header differs')
                                c.require(out[h + 1:] == (0,) * (ell - h), 'shift differs')
                                digest.update(bytes(out))
                                cases += 1
    return dict(shapes=shapes, circuits=circuits, addresses=cases,
                compiled_gates=gates, digest=digest.hexdigest())


def large_circuits(c, physical):
    shapes, cases, maximum = 0, 0, 0
    for ell, width, flags in [
        (6, 2, (True, False)), (6, 3, (False, True, False)),
        (18, 5, (True, False, True, False, True)),
        (64, 7, (False, True) * 8), (256, 17, (True, False) * 32),
    ]:
        slots = tuple(physical.plan(ell, width, flags)['slots'])
        c.require(c.named_slots(ell, width, flags) == slots, 'wide layout differs')
        bits = len(slots)
        values = (0, 1, (1 << bits) - 1,
                  sum(1 << j for j in range(0, bits, 2)),
                  sum(1 << j for j in range(0, bits, 3)))
        for h in sorted({0, 1, ell // 2, ell - 2, ell - 1}):
            for opposite in (False, True):
                p = c.compile_round(ell, width, flags, h, opposite)
                maximum = max(maximum, len(p.gates))
                for address in values:
                    actual = c.decode_word(c.evaluate(p, c.encode_address(address, bits)))
                    c.require(actual == oracle(slots, ell, h, opposite, flags, address),
                              'wide header differs')
                    cases += 1
        shapes += 1
    return dict(shapes=shapes, addresses=cases, maximum_gates=maximum)


def joined_transform(c, physical, schedule, data, opposite):
    """Substitute circuit-produced headers into the canonical round structure."""
    ell, flags = schedule['ell'], schedule['long_axes']
    out = [list(row) for row in data] if opposite else physical.relocate(data, schedule)
    slots = tuple(schedule['slots'])
    masks = {s: 1 << (len(slots) - j - 1) for j, s in enumerate(slots)}
    for h in (range(ell) if opposite else range(ell - 1, -1, -1)):
        p = c.compile_round(ell, schedule['width'], flags, h, opposite)
        if opposite:
            for a, row in enumerate(out):
                e = c.decode_word(c.evaluate(p, c.encode_address(a, len(slots))))
                out[a] = physical.monomial(row, e)
        for i, long in enumerate(flags):
            if h >= ell - (not long):
                continue
            mask = masks[i, h]
            for a in range(len(out)):
                if not a & mask:
                    left, right = out[a], out[a | mask]
                    out[a] = [x + y for x, y in zip(left, right)]
                    out[a | mask] = [x - y for x, y in zip(left, right)]
        if not opposite:
            for a, row in enumerate(out):
                e = c.decode_word(c.evaluate(p, c.encode_address(a, len(slots))))
                out[a] = physical.monomial(row, e)
    return physical.relocate(out, schedule, inverse=True) if opposite else out


def complete_transforms(c, physical):
    comparisons, coefficients = 0, 0
    digest = hashlib.sha256()
    for ell, width, flags in [(2, 1, (True, False)), (3, 2, (False, True)),
                              (3, 1, (True, False)), (2, 1, (False, False, True))]:
        schedule = physical.plan(ell, width, flags)
        m, r = 1 << len(schedule['slots']), 1 << ell
        fixtures = [[[((a + 3) * (j + 5) % 17) - 8 for j in range(r)]
                     for a in range(m)]]
        for column in range(m):
            data = [[0] * r for _ in range(m)]
            data[column][0] = 1
            fixtures.append(data)
        for data in fixtures:
            for opposite in (False, True):
                actual = joined_transform(c, physical, schedule, data, opposite)
                expected = physical.execute(data, schedule, opposite=opposite)
                c.require(actual == expected, 'joined transform differs')
                digest.update(json.dumps(actual, separators=(',', ':')).encode())
                comparisons += 1
                coefficients += m * r
    return dict(comparisons=comparisons, coefficients=coefficients,
                digest=digest.hexdigest())


def rejection_controls(c):
    p = c.compile_round(4, 2, (True, False), 2)
    word = c.encode_address(33, len(p.slots))
    bad = [
        replace(p, gates=(('xor', 0, 100000),)),
        replace(p, gates=(('bad', 0, 0),)),
        replace(p, outputs=(True,) * 5),
        replace(p, slots=p.slots + (p.slots[0],)),
        replace(p, outputs=(0,)),
    ]
    rejected = 0
    for item in bad:
        try:
            c.evaluate(item, word)
        except ValueError:
            rejected += 1
    for address in (word[:-1], (2,) + word[1:], (True,) + word[1:]):
        try:
            c.evaluate(p, address)
        except ValueError:
            rejected += 1
    c.require(rejected == 8, 'invalid circuit/address accepted')
    invalid = [(True, 1, (True,), 0), (257, 1, (True,), 0),
               (4, 0, (True,), 0), (4, 2, (1,), 0),
               (4, 2, (True,) * 65, 0), (4, 2, (True,), 4)]
    for args in invalid:
        try:
            c.compile_round(*args)
        except ValueError:
            rejected += 1
    c.require(rejected == 14, 'invalid shape accepted')
    c.require(c.decode_word(c.evaluate(p, word)) ==
              oracle(p.slots, 4, 2, False, (True, False), 33), 'valid retry failed')
    return rejected


def nonlinear_witness(c):
    """The mixed difference excludes an additive affine exponent on these bits."""
    p = c.compile_round(4, 2, (True, False), 2)
    values = []
    for branch, lower in itertools.product((0, 1), repeat=2):
        bits = tuple(branch if slot == (0, 2) else lower if slot == (0, 0) else 0
                     for slot in p.slots)
        values.append(c.decode_word(c.evaluate(p, bits)))
    difference = (values[3] - values[2] - values[1] + values[0]) % 32
    c.require(values == [0, 0, 0, 28] and difference == 28,
              'quadratic mixed difference lost')
    return dict(ell=4, h=2, values=values, mixed_difference=difference)


def report(c, physical):
    return dict(schema_version=1, status='PASS_SYNTHETIC_TWIDDLE_CIRCUIT',
                small=small_circuits(c, physical), wide=large_circuits(c, physical),
                joined=complete_transforms(c, physical), rejections=rejection_controls(c),
                nonlinear_witness=nonlinear_witness(c))
