#!/usr/bin/env python3
"""Exact finite corroboration of the written equal-energy radix theorem."""
import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
import platform


def require(condition, message):
    if not condition:
        raise ValueError(message)


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def mul(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def energy(row):
    return sum(a * a + b * b for a, b in row)


def pack(row, radix):
    value = (0, 0)
    for a, b in reversed(row):
        value = (value[0] * radix + a, value[1] * radix + b)
    return value


def safe_radix(bound):
    require(type(bound) is int and 1 <= bound <= 1 << 64, "energy bound outside 1..2^64")
    radix = max(2, math.isqrt(2 * bound))
    radix += radix % 2
    if radix * radix - radix + 1 <= 2 * bound:
        radix += 2
    require(radix * radix - radix + 1 > 2 * bound, "radix construction failed")
    require(radix == 2 or (radix - 2) ** 2 - (radix - 2) + 1 <= 2 * bound,
            "not the smallest even radix satisfying this criterion")
    return radix


def admitted_pair(left, right, radix, bound):
    require(type(radix) is int and radix >= 2 and radix % 2 == 0, "invalid even radix")
    require(type(bound) is int and 1 <= bound <= 1 << 64, "invalid energy bound")
    require(radix * radix - radix + 1 > 2 * bound, "unproved radix")
    require(1 <= len(left) == len(right) <= 16, "invalid row lengths")
    for row in (left, right):
        for z in row:
            require(isinstance(z, tuple) and len(z) == 2 and
                    all(type(x) is int and abs(x) <= 1 << 32 for x in z), "invalid digit")
    require(energy(left) == energy(right) <= bound, "unequal or excessive row energy")
    return pack(left, radix) == pack(right, radix)


def quotient_checks():
    alphabet = ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1))
    counts = dict(quotients=0, even_kernel_vectors=0, sharp_vectors=0)
    for length in range(1, 5):
        for q in itertools.product(alphabet, repeat=length):
            if energy(q) == 0:
                continue
            padded = ((0, 0),) + q + ((0, 0),)
            variation = sum(energy((sub(b, a),)) for a, b in zip(padded, padded[1:]))
            require(variation >= 2, "finite path variation")
            for radix in (2, 4, 6, 10):
                d = tuple(sub(a, (radix * b[0], radix * b[1]))
                          for a, b in zip(padded, padded[1:]))
                e = energy(d)
                require(pack(d, radix) == (0, 0), "quotient not in kernel")
                require(e == (radix - 1) ** 2 * energy(q) + radix * variation,
                        "discrete energy identity")
                require(e % 2 == energy(q) % 2, "parity identity")
                counts['quotients'] += 1
                if e % 2 == 0:
                    require(e >= 2 * (radix * radix - radix + 1), "even kernel bound")
                    counts['even_kernel_vectors'] += 1
    for radix in range(2, 130, 2):
        for phase in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            d = tuple(mul(phase, (x, 0)) for x in (radix, radix - 1, -1))
            require(pack(d, radix) == (0, 0), "sharp witness packing")
            require(energy(d) == 2 * (radix * radix - radix + 1), "sharp energy")
            counts['sharp_vectors'] += 1
    return counts


def direct_kernel_checks():
    counts = dict(real_digit_words=0, real_even_kernels=0,
                  complex_digit_words=0, complex_even_kernels=0)
    for radix in (2, 4, 6):
        for digits in itertools.product(range(-radix, radix + 1), repeat=3):
            value = sum(digits[j] * radix ** j for j in range(3))
            e = sum(x * x for x in digits)
            counts['real_digit_words'] += 1
            if value == 0 and e > 0 and e % 2 == 0:
                require(e >= 2 * (radix * radix - radix + 1), "direct real kernel")
                counts['real_even_kernels'] += 1
        for digits in itertools.product(range(-2, 3), repeat=4):
            value = (digits[0] + radix * digits[2], digits[1] + radix * digits[3])
            e = sum(x * x for x in digits)
            counts['complex_digit_words'] += 1
            if value == (0, 0) and e > 0 and e % 2 == 0:
                require(e >= 2 * (radix * radix - radix + 1), "direct complex kernel")
                counts['complex_even_kernels'] += 1
    return counts


def sphere_checks():
    counts = dict(sphere_candidates=0, admitted_sphere_vectors=0)
    for bound in (2, 6, 10):
        radius = math.isqrt(bound)
        radix = safe_radix(bound)
        for length in range(1, 5):
            seen = set()
            for digits in itertools.product(range(-radius, radius + 1), repeat=2 * length):
                counts['sphere_candidates'] += 1
                e = sum(x * x for x in digits)
                if e != bound:
                    continue
                row = tuple((digits[2 * j], digits[2 * j + 1]) for j in range(length))
                key = (e, pack(row, radix))
                require(key not in seen, "equal-energy packing collision")
                seen.add(key)
                counts['admitted_sphere_vectors'] += 1
    return counts


def matrix_fixtures():
    counts = dict(unitary_matrices=0, gram_entries=0, matrix_pairs=0, phase_mutants=0)
    for width in (2, 4, 8):
        rows = tuple(tuple((int(i == j), 0) for j in range(width)) for i in range(width))
        matrices = [(0, rows)]
        for step in range(9):
            mask = 1 << (step % (width.bit_length() - 1))
            rows = tuple(tuple(add(mul((1, 1), rows[i][j]), mul((1, -1), rows[i ^ mask][j]))
                               for j in range(width)) for i in range(width))
            matrices.append((step + 1, rows))
        for k, matrix in matrices:
            for i in range(width):
                require(energy(matrix[i]) == 4 ** k, "scaled row energy")
                for j in range(width):
                    gram = (0, 0)
                    for a, b in zip(matrix[i], matrix[j]):
                        gram = add(gram, mul(a, (b[0], -b[1])))
                    require(gram == (4 ** k if i == j else 0, 0), "scaled unitarity")
                    counts['gram_entries'] += 1
            counts['unitary_matrices'] += 1
        for (k, left), (ell, right) in itertools.product(matrices, repeat=2):
            top = max(k, ell)
            a = tuple(tuple((x << (top - k), y << (top - k)) for x, y in row) for row in left)
            b = tuple(tuple((x << (top - ell), y << (top - ell)) for x, y in row) for row in right)
            same = all(admitted_pair(u, v, safe_radix(4 ** top), 4 ** top) for u, v in zip(a, b))
            require(same == (a == b), "packed versus full matrix equality")
            counts['matrix_pairs'] += 1
        for k, matrix in matrices:
            mutant = tuple(mul((0, 1), z) for z in matrix[0])
            require(not admitted_pair(matrix[0], mutant, safe_radix(4 ** k), 4 ** k),
                    "absolute phase mutant")
            counts['phase_mutants'] += 1
    return counts


def controls():
    odd = ((3, 0), (-1, 0))
    require(pack(odd, 3) == (0, 0) and energy(odd) < 2 * (9 - 3 + 1), "odd radix control")
    low = ((2, 0), (-1, 0))
    require(energy(low) % 2 == 1 and energy(low) < 2 * (4 - 2 + 1), "odd energy control")
    unequal = (((6, 0), (0, 0)), ((-6, 0), (1, 0)))
    require(pack(unequal[0], 12) == pack(unequal[1], 12), "unequal-energy collision")
    require(energy(unequal[0]) != energy(unequal[1]) and
            max(map(energy, unequal)) <= 64 and 12 ** 2 - 12 + 1 > 128,
            "unequal-energy control must satisfy the other hypotheses")
    collision = (((1, 1), (0, -1)), ((-1, -1), (1, 0)))
    require(energy(collision[0]) == energy(collision[1]) == 3 and
            pack(collision[0], 2) == pack(collision[1], 2), "unsafe equal-energy control")
    zero = ((0, 0),)
    cases = [(zero, zero, 3, 1), (zero, zero, True, 1), (zero, zero, 2, 3),
             (*unequal, 12, 64), (*collision, 2, 3), (zero, (), 2, 1),
             (zero, zero, 2, -1), (zero, zero, 2, True), (((True, 0),), zero, 2, 1)]
    for args in cases:
        try:
            admitted_pair(*args)
        except ValueError:
            continue
        raise ValueError("invalid pair admitted")
    for bound in (0, -1, True, 1 << 65):
        try:
            safe_radix(bound)
        except ValueError:
            continue
        raise ValueError("invalid energy bound admitted")
    return dict(discriminating_controls=4, rejection_controls=len(cases) + 4)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt', type=Path, help='write generated JSON outside checkout')
    args = parser.parse_args()
    counts = {}
    counts.update(quotient_checks())
    counts.update(direct_kernel_checks())
    counts.update(sphere_checks())
    counts.update(matrix_fixtures())
    counts.update(controls())
    for bound in range(1, 4097):
        safe_radix(bound)
    counts['minimal_even_criterion_radices'] = 4096
    radix = safe_radix(512 ** 2)
    require(radix == 726 and (radix ** 511).bit_length() == 4857, 'application arithmetic')
    counts.update(R512_radix=radix, N512_largest_input_bits=4857,
                  old_N512_largest_input_bits=(1024 ** 511).bit_length())
    root = Path(__file__).resolve().parent
    hashes = {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
              for name in ('README.md', 'TASK.json', 'SOURCES.json', 'VERIFY.json', 'verify.py')}
    report = dict(status='PASS_EQUAL_ENERGY_RADIX_PARITY', python=platform.python_version(),
                  counts=counts, sha256=hashes)
    encoded = json.dumps(report, sort_keys=True, indent=2) + '\n'
    if args.receipt:
        args.receipt.write_text(encoded, encoding='utf-8')
    print(encoded, end='')


if __name__ == '__main__':
    main()
