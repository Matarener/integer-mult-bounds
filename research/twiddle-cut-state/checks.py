"""Independent exhaustive physical-address and interval checks. Apache-2.0."""

import itertools

from states import bit_bound, constants, count_states, no_low_prefix, require, source_cut


def physical_slots(ell, width, long_axes):
    low, chunks = (ell - 1) % width, (ell - 1) // width
    result = [(i, ell - 1) for i, long in enumerate(long_axes) if long]
    for v in range(low - 1, -1, -1):
        result.extend((i, v) for i in range(len(long_axes)))
    for chunk in range(chunks):
        top = ell - 2 - chunk * width
        for i in range(len(long_axes)):
            result.extend((i, v) for v in range(top, top - width, -1))
    return tuple(result)


def exponent(address, slots, ell, h, long_axes):
    """Direct source formula, without using any cut or state-count formula."""
    axes = [0] * len(long_axes)
    for position, (axis, v) in enumerate(slots):
        bit = (address >> (len(slots) - 1 - position)) & 1
        axes[axis] += bit << v
    total = 0
    for i, value in enumerate(axes):
        if h < ell - (not long_axes[i]):
            total += ((value >> h) & 1) * (value % (1 << h))
    return (-(total << (ell - h))) % (1 << (ell + 1))


def physical_case(ell, width, axes, h, source):
    slots = physical_slots(ell, width, axes)
    require(slots == source.named_slots(ell, width, axes), 'physical layout differs')
    require(len(slots) <= 12, 'exhaustive address limit')
    cut, low, bottom = source_cut(ell, width, axes, h)
    require(0 <= cut <= len(slots), 'cut extent')
    suffix = len(slots) - cut
    functions = set()
    for prefix in range(1 << cut):
        functions.add(tuple(exponent((prefix << suffix) + tail, slots, ell, h, axes)
                            for tail in range(1 << suffix)))
    d = sum(h < ell - (not long) for long in axes)
    expected = count_states(d, h, low, bottom)
    require(len(functions) == expected, 'physical residual count differs')
    return {'ell': ell, 'width': width, 'long_axes': list(axes), 'h': h,
            'cut': cut, 'low': low, 'bottom': bottom, 'participants': d,
            'states': str(expected), 'bits': bit_bound(d, h, low, bottom),
            'addresses': 1 << len(slots)}


def physical_checks(source):
    rows = []
    for ell in range(2, 7):
        for width in range(1, ell):
            for axes_n in range(1, 4):
                for axes in itertools.product((False, True), repeat=axes_n):
                    if sum(ell - (not long) for long in axes) > 12:
                        continue
                    for h in range(ell):
                        rows.append(physical_case(ell, width, axes, h, source))
    return rows


def brute_constants(active, h, low, bottom):
    """Minkowski sums of literal allowed values, without interval formulas."""
    allowed = [small + (high << bottom) for small in range(1 << low)
               for high in range(1 << (h - bottom))]
    modulus, values = 1 << (h + 1), {0}
    for _ in range(active):
        values = {(left + right) % modulus for left in values for right in allowed}
    return len(values)


def interval_checks():
    cases = 0
    for h in range(8):
        for low in range(h + 1):
            for bottom in range(low, h + 1):
                for active in range(13):
                    actual = brute_constants(active, h, low, bottom)
                    require(actual == constants(active, h, low, bottom),
                            'reachable constant interval differs')
                    cases += 1
    return cases


def symbolic_checks():
    cases = 0
    for d in range(1, 65):
        for h in (1, 2, 7, 16, 64, 128, 256):
            for bottom in sorted({1, h, max(1, h // 2)}):
                actual = count_states(d, h, 0, bottom)
                require(actual == no_low_prefix(d, h, bottom), 'closed form differs')
                if bottom == h:
                    bits = d
                else:
                    bits = h - bottom + d + (d >= 3)
                require(bit_bound(d, h, 0, bottom) == bits, 'sharp bit bound differs')
                cases += 1
    return cases


def boundary_checks():
    rejected = 0
    for args in ((-1, 1, 0, 1), (257, 1, 0, 1), (1, 257, 0, 1),
                 (True, 1, 0, 1), (1, 1, 2, 2), (1, 1, 1, 0)):
        try:
            count_states(*args)
        except ValueError:
            rejected += 1
        else:
            raise ValueError('invalid parameters accepted')
    for args in ((1, 1, (True,), 0), (3, 3, (True,), 0),
                 (3, 1, (), 0), (3, 1, (1,), 0), (3, 1, (True,), 3)):
        try:
            source_cut(*args)
        except ValueError:
            rejected += 1
        else:
            raise ValueError('invalid shape accepted')
    require(count_states(0, 256, 0, 1) == 1, 'empty round differs')
    require(count_states(64, 0, 0, 0) == 1, 'zero round differs')
    return rejected


def examples():
    rows = []
    for d, h, low, bottom in ((2, 4, 1, 3), (12, 5, 1, 4),
                              (64, 48, 0, 32), (3, 5, 0, 3), (3, 5, 1, 1)):
        states = count_states(d, h, low, bottom)
        rows.append({'d': d, 'h': h, 'low': low, 'bottom': bottom,
                     'states': str(states), 'bits': (states - 1).bit_length()})
    require(rows[0]['states'] == '18', 'calibration example differs')
    require(rows[1]['states'] == '114439', 'mixed-prefix example differs')
    return rows
