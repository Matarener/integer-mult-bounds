# SPDX-License-Identifier: Apache-2.0
"""Independent signed-integer oracles and whole synthetic-transform fixtures."""

from fractions import Fraction
from hashlib import sha256
from itertools import product


def need(ok, message):
    if not ok:
        raise ValueError(message)


def encoded(values, width, packing):
    scalars = [v for row in values for z in row for v in z]
    need(all(int(v) == v for v in scalars), "integral packet grid")
    return bytes(packing.signed_words([int(v) for v in scalars], width))


def decoded(raw, records, r, width, packing):
    values = packing.read_signed(raw, width)
    return [[tuple(values[2 * (a * r + j):2 * (a * r + j) + 2])
             for j in range(r)] for a in range(records)]


def oracle(rows, exponents):
    r = len(rows[0])
    result = [[None] * r for _ in rows]
    for a, row in enumerate(rows):
        for j, z in enumerate(row):
            quotient, target = divmod(j + exponents[a], r)
            sign = (-1) ** (quotient % 2)
            result[a][target] = tuple(sign * v for v in z)
    return result


def apply(rows, exponents, width, packets, packing):
    raw = encoded(rows, width, packing)
    source = packets.Tape(len(raw), raw)
    machine = packets.MonomialPackets(len(rows), len(rows[0]), width)
    returned = machine.run(source, tuple(exponents))
    need(bytes(source.cells) == raw and source.head == 0, "borrowed source restoration")
    need(machine.closed and all(bit == packets.BLANK for tape in
         (machine.prefix, machine.suffix, machine.word) for bit in tape.cells),
         "all three private roles blank")
    ticks = machine.data_ticks(source)
    need(ticks <= machine.step_bound(), "proved data-step invoice")
    need(ticks <= 37 * len(raw) + 6 * machine.record_bits + 3 * width,
         "sharper proof bound including all head returns")
    output = bytes(returned.cells)
    return decoded(output, len(rows), len(rows[0]), width, packing), output, ticks


def packet_checks(packets, packing):
    digest, count, ticks, max_ratio = sha256(), 0, 0, Fraction(0)
    for width in range(3, 9):
        for value in range(-(1 << (width - 1)) + 1, 1 << (width - 1)):
            for r in (2, 4, 8):
                rows = [[(value, -value)] * r]
                for exponent in range(-2 * r - 1, 2 * r + 2):
                    result, raw, steps = apply(rows, [exponent], width, packets, packing)
                    need(result == oracle(rows, [exponent]), "all signable word/phase combinations")
                    count += 1
                    ticks += steps
                    max_ratio = max(max_ratio, Fraction(steps, len(raw)))
                    digest.update(raw)
    return {"word_phase_cases": count, "data_steps": ticks,
            "maximum_steps_per_bit": str(max_ratio), "sha256": digest.hexdigest()}


def mixed_checks(packets, packing):
    digest, cases = sha256(), 0
    for r, width, records in ((2, 3, 128), (4, 7, 3), (8, 17, 5), (64, 128, 2)):
        cap = 1 << (width - 2)
        rows = [[((a * r + j) % (2 * cap + 1) - cap,
                  (3 * a + j) % (2 * cap + 1) - cap) for j in range(r)]
                for a in range(records)]
        exponents = [(-1 if a % 2 else 1) * ((1 << 61) + 13 * a) for a in range(records)]
        out, raw, _ = apply(rows, exponents, width, packets, packing)
        need(out == oracle(rows, exponents), "mixed headers, spectators and wide components")
        back, _, _ = apply(out, [-e for e in exponents], width, packets, packing)
        need(back == rows, "two-sided signed monomial inverse")
        digest.update(raw)
        cases += 1
    return {"mixed_packets": cases, "sha256": digest.hexdigest()}


def failure_checks(packets, packing):
    failures = 0
    machine = packets.MonomialPackets(1, 2, 4)
    valid = encoded([[(1, -2), (3, -1)]], 4, packing)
    bad_word = encoded([[(-8, 0), (0, 0)]], 4, packing)
    invalid_bit = bytes([7]) + valid[1:]
    for raw, headers in ((bad_word, (0,)), (invalid_bit, (1,)),
                         (valid, (True,)), (valid, (1 << 63,)), (valid, ())):
        source = packets.Tape(len(raw), raw)
        try:
            machine.run(source, headers)
        except ValueError:
            failures += 1
        else:
            raise ValueError("invalid packet/header accepted")
        need(bytes(source.cells) == raw and source.head == 0 and machine.closed,
             "failed call borrowed restoration")
        need(all(bit == packets.BLANK for tape in
             (machine.output, machine.prefix, machine.suffix, machine.word) for bit in tape.cells),
             "failed call private and output rollback")
    source = packets.Tape(len(valid), valid)
    returned = machine.run(source, (1,))
    need(decoded(bytes(returned.cells), 1, 2, 4, packing) ==
         oracle([[(1, -2), (3, -1)]], [1]), "valid retry after rejection")
    for raw in (valid[:-1], valid + bytes([0])):
        other = packets.MonomialPackets(1, 2, 4)
        try:
            other.run(packets.Tape(len(raw), raw), (0,))
        except ValueError:
            failures += 1
        else:
            raise ValueError("incomplete/overlong extent accepted")
    return {"rejections": failures, "valid_retry": True}


def headers(schedule, h):
    bits, r = len(schedule["slots"]), 1 << schedule["ell"]
    masks = {slot: 1 << (bits - 1 - pos) for pos, slot in enumerate(schedule["slots"])}
    exponents = []
    for address in range(1 << bits):
        exponent = 0
        for axis, length in enumerate(schedule["lengths"]):
            if h < length:
                branch = bool(address & masks[axis, h])
                low = sum(1 << v for v in range(h) if address & masks[axis, v])
                exponent -= (2 * r // (1 << (h + 1))) * branch * low
        exponents.append(exponent)
    return exponents


def butterfly(rows, schedule, h):
    bits = len(schedule["slots"])
    positions = [pos for pos, (axis, v) in enumerate(schedule["slots"])
                 if v == h and h < schedule["lengths"][axis]]
    out = rows
    for pos in positions:
        mask = 1 << (bits - 1 - pos)
        new = [[None] * len(rows[0]) for _ in rows]
        for a in range(len(rows)):
            for j in range(len(rows[0])):
                new[a][j] = tuple((out[a & ~mask][j][c] +
                                  (-1 if a & mask else 1) * out[a | mask][j][c]) / Fraction(2)
                                 for c in range(2))
        out = new
    return out


def rounded_transform(rows, schedule, opposite, packets, packing, physical):
    out = physical.relocate(rows, schedule) if not opposite else rows
    width = 12
    for h in (range(schedule["ell"]) if opposite else
              range(schedule["ell"] - 1, -1, -1)):
        exponents = headers(schedule, h)
        if opposite:
            out, _, _ = apply(out, [-e for e in exponents], width, packets, packing)
        exact = butterfly(out, schedule, h)
        # int(Fraction) is exact truncation toward zero, once per completed round.
        out = [[tuple(int(v) for v in z) for z in row] for row in exact]
        if not opposite:
            out, _, _ = apply(out, exponents, width, packets, packing)
    return physical.relocate(out, schedule, inverse=True) if opposite else out


def transform_checks(packets, packing, physical):
    digest, cases, comparisons = sha256(), 0, 0
    for ell, flags in ((2, (True,)), (2, (True, False)), (3, (False, True))):
        for chunk in range(1, ell):
            schedule = physical.plan(ell, chunk, flags)
            size, r = 1 << len(schedule["slots"]), 1 << ell
            m = size
            rows = [[(Fraction((7 * a + 3 * j) % 17 - 8),
                      Fraction((5 * a + j) % 19 - 9)) for j in range(r)] for a in range(size)]
            for opposite in (False, True):
                actual = rounded_transform(rows, schedule, opposite, packets, packing, physical)
                exact_parts = [physical.execute([[z[c] for z in row] for row in rows],
                                               schedule, opposite=opposite) for c in range(2)]
                for a, j, c in product(range(size), range(r), range(2)):
                    need(abs(actual[a][j][c] - exact_parts[c][a][j] / m) < ell,
                         "source completed-round component error")
                    comparisons += 1
                # Inputs divisible by M make every completed-round truncation exact.
                integral = [[tuple(int(v * m) for v in z) for z in row] for row in rows]
                exact = rounded_transform(integral, schedule, opposite, packets, packing, physical)
                need(exact == [[tuple(int(exact_parts[c][a][j]) for c in range(2))
                                for j in range(r)] for a in range(size)],
                     "whole transform joins source engine exactly on divisible grid")
                digest.update(encoded(actual, 12, packing))
                cases += 1
    return {"rounded_transforms": cases, "component_error_checks": comparisons,
            "sha256": digest.hexdigest(), "root": "rational parallel-butterfly oracle"}


def run(packets, physical, packing):
    return {"schema": 1, "packets": packet_checks(packets, packing),
            "mixed": mixed_checks(packets, packing),
            "invalid": failure_checks(packets, packing),
            "transforms": transform_checks(packets, packing, physical)}


def smoke(packets, physical, packing):
    rows = [[(3, -2), (-1, 2)], [(0, -3), (2, 1)]]
    for exponent in (-5, -4, -2, -1, 0, 1, 2, 5):
        headers_ = [exponent, -exponent]
        out, _, _ = apply(rows, headers_, 4, packets, packing)
        need(out == oracle(rows, headers_), "smoke signed coefficient destination")
    return {"smoke_packets": 8, "transforms": transform_checks(packets, packing, physical)}
