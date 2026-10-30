#!/usr/bin/env python3
"""Exact sharp nearest-even normalized Walsh bound. Nick Petalas. Apache-2.0."""

from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import platform


def require(condition, message):
    if not condition:
        raise ValueError(message)


def half_even(numerator):
    quotient, remainder = divmod(numerator, 2)
    return quotient + (remainder & (quotient & 1))


def quantizer_checks():
    count = 0
    for numerator in range(-1024, 1025):
        value = half_even(numerator)
        require(value == round(Fraction(numerator, 2)), "independent signed nearest-even oracle")
        require(numerator % 2 == 0 or value % 2 == 0, "half-tie output is even")
        count += 1
    return count


def transform(values, rounded=True, reverse=False):
    """Input and output are integers in units of one common grid step."""
    n = len(values)
    require(1 <= n <= 4096 and n & (n - 1) == 0, "power-of-two size <=4096")
    require(all(type(v) is int and abs(v) <= 2**64 for v in values), "integer input bound")
    out = list(values)
    stages = list(range(n.bit_length() - 1))
    if reverse:
        stages.reverse()
    for bit in stages:
        width = 1 << bit
        for start in range(0, n, 2 * width):
            for i in range(start, start + width):
                left, right = out[i], out[i + width]
                if rounded:
                    out[i], out[i + width] = half_even(left + right), half_even(left - right)
                else:
                    out[i], out[i + width] = left + right, left - right
    return out


def bound(depth):
    require(type(depth) is int and 0 <= depth <= 64, "depth 0..64")
    return Fraction(depth, 3) + (1 - Fraction(-1, 2)**depth) / 9


def error_numerators(values, reverse=False):
    exact = transform(values, rounded=False)
    computed = transform(values, reverse=reverse)
    return [len(values) * y - z for y, z in zip(computed, exact)]


def literal_walsh(values):
    n = len(values)
    require(n <= 16, "literal Walsh oracle capacity")
    return [sum((-1 if (i & j).bit_count() % 2 else 1) * x
                for j, x in enumerate(values)) for i in range(n)]


def exhaustive_residue_checks():
    counts = []
    for depth in (1, 2):
        n = 1 << depth
        maximum, maximizing = -1, None
        for values in product(range(2 * n), repeat=n):
            exact = literal_walsh(values)
            require(transform(values, rounded=False) == exact, "closed Walsh formula")
            computed = transform(values)
            error = max(abs(n * y - z) for y, z in zip(computed, exact))
            require(error <= n * bound(depth), "complete residue-domain bound")
            if error > maximum:
                maximum, maximizing = error, values
        require(Fraction(maximum, n) == bound(depth), "complete residue-domain sharpness")
        counts.append({"depth": depth, "inputs": (2 * n)**n,
                       "maximum": str(Fraction(maximum, n)), "witness": maximizing})
    return counts


def tree_error_sets():
    """Enumerate attainable scaled errors by output parity, without the formula."""
    even, odd = {0}, {0}
    result = []
    for depth in range(1, 8):
        scale = 1 << (depth - 1)
        same = {x + y for group in (even, odd) for x in group for y in group}
        mixed = {x + y + sign * scale for x in even for y in odd for sign in (-1, 1)}
        even, odd = same | mixed, same
        expected = (1 << depth) * bound(depth)
        require(max(even) == -min(even) == expected, "even-output reachable extrema")
        require(max(odd) == -min(odd) == (1 << depth) * bound(depth - 1),
                "odd-output reachable extrema")
        result.append({"depth": depth, "even_errors": len(even), "odd_errors": len(odd),
                       "maximum_scaled_error": max(even)})
    return result


def witness_checks():
    even, odd = [0], [1]
    result = []
    for depth in range(13):
        n = 1 << depth
        for parity, values in enumerate((even, odd)):
            for reverse in (False, True):
                if reverse:
                    indices = [int(f"{i:0{depth}b}"[::-1], 2) if depth else 0 for i in range(n)]
                    current = [values[i] for i in indices]
                else:
                    current = values
                computed = transform(current, reverse=reverse)
                errors = error_numerators(current, reverse=reverse)
                target = bound(depth) if parity == 0 else bound(max(0, depth - 1))
                require(computed[0] == parity, "attaining output parity")
                require(Fraction(errors[0], n) == target, "constructive sharpness")
                require(max(map(abs, errors)) <= n * bound(depth), "all witness outputs")
                require(transform([-x for x in current], reverse=reverse) == [-y for y in computed],
                        "negative sharpness by oddness")
        require(min(even) >= -depth and max(even) == 0, "small attaining input range")
        result.append({"depth": depth, "sharp_error": str(bound(depth)),
                       "input_minimum": min(even), "input_maximum": max(even)})
        if depth < 12:
            even, odd = even + [x - 2 for x in odd], even + [x + 2 for x in even]
    return result


def periodicity_checks():
    count = 0
    for depth in range(1, 9):
        n = 1 << depth
        for sample in range(16):
            values = [((i * 8191 + sample * 127) % 20001) - 10000 for i in range(n)]
            shifts = [((i * 11 + sample * 5) % 17) - 8 for i in range(n)]
            shifted = [x + 2 * n * z for x, z in zip(values, shifts)]
            for reverse in (False, True):
                require(error_numerators(values, reverse) == error_numerators(shifted, reverse),
                        "period 2^(J+1) in each input")
                count += 1
    return count


def deferred_echo_checks():
    """New all-grid application; no predecessor code is imported or executed."""
    count = 0
    for x in range(-256, 257):
        temporary = half_even(x)
        retained = x + 4 * temporary
        retained -= 4 * temporary
        temporary = half_even(2 * temporary - retained)
        require(retained == x and temporary == 0, "rounded echo endpoint")
        count += 1
    require(bound(2) / 4 == Fraction(3, 16), "normalized two-stage application")
    require(bound(2) == Fraction(3, 4), "raw two-stage application")
    return count


def deferred_model(values):
    """Integer-grid implementation of the stated eight-coordinate application."""
    require(len(values) == 8, "eight-coordinate application")
    permutation = [(i & 4) | ((i & 1) << 1) | ((i & 2) >> 1) for i in range(8)]
    work = [values[i] for i in permutation] + [0] * 4
    for i in range(4):
        work[i + 8] = half_even(work[i])
        work[i] += 4 * work[i + 8]
        work[i] -= 4 * work[i + 8]
        work[i + 8] = half_even(2 * work[i + 8] - work[i])
    require(work[8:] == [0] * 4, "application clean temporary row")
    for i in range(0, 12, 2):
        left, right = work[i], work[i + 1]
        work[i], work[i + 1] = half_even(left + right), half_even(left - right)
    out = [work[i] for i in permutation]
    for i in range(4):
        left, right = out[i], out[i + 4]
        out[i], out[i + 4] = half_even(left + right), half_even(left - right)
    return out


def application_checks():
    inputs = [[0, 0, -1, 0, -2, 0, 0, 0]]
    inputs += [[((i * 31 + sample * 17) % 257) - 128 for i in range(8)] for sample in range(64)]
    maximum = 0
    for values in inputs:
        exact = [sum((-1 if (i & j & 6).bit_count() % 2 else 1) * x
                     for j, x in enumerate(values) if (i ^ j) & 1 == 0) for i in range(8)]
        computed = deferred_model(values)
        error = max(abs(4 * y - z) for y, z in zip(computed, exact))
        require(error <= 3, "full application all-output bound")
        maximum = max(maximum, error)
    require(maximum == 3, "full application attaining witness")
    return {"fixtures": len(inputs), "sharp_normalized_error_at_h_quarter": str(Fraction(maximum, 16)),
            "sharp_raw_error_at_h_quarter": str(Fraction(maximum, 4))}


def semantic_controls():
    values = [Fraction(3, 4), Fraction(3, 4), Fraction(3, 2), Fraction(3, 2)]
    first = [round((values[0] + values[1]) / 2), round((values[2] + values[3]) / 2)]
    off_grid_error = abs(round(Fraction(sum(first), 2)) - sum(values) / 4)
    require(off_grid_error == Fraction(7, 8) > bound(2), "off-grid exclusion")
    for mode in ("away", "floor"):
        values = [0, 1, 1, 2]
        first = []
        for i in (0, 2):
            numerator = values[i] + values[i + 1]
            first.append((numerator + 1) // 2 if mode == "away" else numerator // 2)
        numerator = sum(first)
        result = (numerator + 1) // 2 if mode == "away" else numerator // 2
        require(abs(Fraction(result) - Fraction(sum(values), 4)) == 1 > bound(2),
                "different tie rule exclusion")
    require(bound(3) > bound(2), "two-stage value cannot be used at every depth")
    rejected = 0
    for values in ([], [0, 0, 0], [Fraction(1, 2), 0], [True, 0], [2**65, 0]):
        try:
            transform(values)
        except ValueError:
            rejected += 1
    require(rejected == 5, "invalid domains rejected")
    return {"semantic_exclusions": 4, "invalid_inputs": rejected, "off_grid_error": str(off_grid_error)}


def main():
    result = {"status": "PASS_NEAREST_EVEN_WALSH_ERROR", "signed_half_checks": quantizer_checks(),
              "residue_censuses": exhaustive_residue_checks(),
              "reachable_tree_errors": tree_error_sets(), "sharp_witnesses": witness_checks(),
              "periodicity_fixtures": periodicity_checks(), "echo_grid_values": deferred_echo_checks(),
              "application": application_checks(), "controls": semantic_controls(), "new_kappa_claimed": False}
    package = Path(__file__).resolve().parent
    files = sorted(p for p in package.iterdir() if p.is_file())
    require(len(files) <= 12 and all(p.stat().st_size <= 1024**2 for p in files), "package receipt capacity")
    receipt = {"python": platform.python_version(),
               "package_sha256": {p.name: sha256(p.read_bytes()).hexdigest() for p in files},
               "result": result}
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
