"""Exact finite corroboration of the written nearest-even shear theorem."""

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import product
from math import lcm
from pathlib import Path
import json
import platform


def require(condition, message):
    if not condition:
        raise ValueError(message)


def matrix(rows):
    require(type(rows) is tuple and 1 <= len(rows) <= 8, "row bound")
    require(all(type(row) is tuple for row in rows), "row type")
    width = len(rows[0])
    require(1 <= width <= 6, "column bound")
    require(all(len(row) == width for row in rows), "ragged matrix")
    require(all(type(a) in (int, Fraction) for row in rows for a in row),
            "exact rational entries required")
    return tuple(tuple(Fraction(a) for a in row) for row in rows)


def vector(values, size):
    require(type(values) is tuple and len(values) == size, "vector shape")
    require(all(type(value) is int for value in values), "integer vector")


def nearest_even(a):
    """Integer division, including negative arguments and exact half ties."""
    floor, remainder = divmod(a.numerator, a.denominator)
    comparison = 2 * remainder - a.denominator
    return floor + int(comparison > 0 or (comparison == 0 and floor % 2 == 1))


def oracle_round(a):
    """Independent distance minimization; even parity breaks equal distances."""
    floor = a.numerator // a.denominator
    return min((floor, floor + 1), key=lambda z: (abs(a - z), z % 2))


def offsets(a, x):
    vector(x, len(a[0]))
    return tuple(sum((c * v for c, v in zip(row, x)), Fraction()) for row in a)


def forward(a, x, y):
    vector(y, len(a))
    return tuple(nearest_even(v + s) for v, s in zip(y, offsets(a, x)))


def encode(a, x, y):
    z = forward(a, x, y)
    history = 0
    used = 0
    for yi, zi, shift in zip(y, z, offsets(a, x)):
        if shift.denominator == 2:
            floor = shift.numerator // 2
            bit = yi - (zi - floor - 1)
            require(bit in (0, 1) and zi % 2 == 0, "tie encoding invariant")
            history |= bit << used
            used += 1
    return z, history, used


def decode(a, x, z, history):
    vector(z, len(a))
    shifts = offsets(a, x)
    used = sum(s.denominator == 2 for s in shifts)
    require(type(history) is int and 0 <= history < 2 ** used, "history range")
    y = []
    cursor = 0
    for zi, shift in zip(z, shifts):
        if shift.denominator == 2:
            require(zi % 2 == 0, "unreachable odd tie output")
            y.append(zi - shift.numerator // 2 - 1 + ((history >> cursor) & 1))
            cursor += 1
        else:
            y.append(zi - nearest_even(shift))
    require(cursor == used, "history consumption")
    return tuple(y)


def periodic_theorem(a):
    denominator = lcm(*(c.denominator for row in a for c in row))
    cases = denominator ** len(a[0])
    require(cases <= 4096, "finite corroboration source bound")
    maximum = 0
    source_cases = 0
    fiber_cases = 0
    for x in product(range(denominator), repeat=len(a[0])):
        ties = sum(s.denominator == 2 for s in offsets(a, x))
        counts = Counter()
        # Even modulus two preserves nearest-even parity and every whole fiber.
        for y in product(range(2), repeat=len(a)):
            literal = tuple(oracle_round(v + s) % 2
                            for v, s in zip(y, offsets(a, x)))
            counts[literal] += 1
            fiber_cases += 1
        require(set(counts.values()) == {2 ** ties}, "literal fiber size")
        require(len(counts) == 2 ** (len(a) - ties), "literal image size")
        maximum = max(maximum, ties)
        source_cases += 1
    odd_rows = all(c.denominator % 2 == 1 for row in a for c in row)
    require((maximum == 0) == odd_rows, "odd-denominator classification")
    return maximum, source_cases, fiber_cases


def binary_census():
    totals = Counter()
    for height in range(1, 4):
        for width in range(1, 4):
            for flat in product(range(2), repeat=height * width):
                b = tuple(flat[i * width:(i + 1) * width] for i in range(height))
                a = matrix(tuple(tuple(Fraction(c, 2) for c in row) for row in b))
                maximum, sources, fibers = periodic_theorem(a)
                code = {tuple(sum(c * v for c, v in zip(row, x)) % 2 for row in b)
                        for x in product(range(2), repeat=width)}
                require(maximum == max(map(sum, code)), "binary code weight")
                totals.update(matrices=1, source_cases=sources, fiber_cases=fibers)
    return totals


def rational_census():
    totals = Counter()
    for denominator in range(1, 13):
        for numerator in range(-6, 7):
            a = matrix(((Fraction(numerator, denominator),),))
            _, sources, fibers = periodic_theorem(a)
            totals.update(matrices=1, source_cases=sources, fiber_cases=fibers)
    menu = (Fraction(-1, 2), Fraction(1, 3), Fraction(1, 2), Fraction(2, 3))
    for flat in product(menu, repeat=4):
        a = matrix((flat[:2], flat[2:]))
        _, sources, fibers = periodic_theorem(a)
        totals.update(matrices=1, source_cases=sources, fiber_cases=fibers)
    for flat in product(range(4), repeat=4):
        a = matrix(tuple(tuple(Fraction(c, 4) for c in flat[i:i + 2])
                         for i in (0, 2)))
        _, sources, fibers = periodic_theorem(a)
        totals.update(matrices=1, source_cases=sources, fiber_cases=fibers)
    return totals


def signed_roundtrips():
    fixtures = (
        ((Fraction(1, 2),),) * 3,
        ((Fraction(1, 2), 0), (Fraction(1, 2), Fraction(1, 2)), (0, Fraction(1, 2))),
        ((Fraction(1, 2), 0), (0, Fraction(1, 2)), (0, Fraction(1, 2))),
        ((Fraction(-3, 4), Fraction(1, 3)), (Fraction(5, 6), Fraction(-1, 2))),
        ((Fraction(1, 3), Fraction(-2, 5)),),
    )
    checked = 0
    for rows in fixtures:
        a = matrix(rows)
        for x in product(range(-3, 4), repeat=len(a[0])):
            for y in product(range(-3, 4), repeat=len(a)):
                z, history, used = encode(a, x, y)
                require(z == tuple(oracle_round(v + s)
                                   for v, s in zip(y, offsets(a, x))), "round oracle")
                require(used == sum(s.denominator == 2 for s in offsets(a, x)),
                        "exact history length")
                require(decode(a, x, z, history) == y, "signed reconstruction")
                checked += 1
    return checked


def rejection_controls():
    bad_matrices = ((), ((1,), (1, 2)), ((True,),), ((0.5,),),
                    ((0,),) * 9, ((0,) * 7,), ([1],))
    rejected = 0
    for rows in bad_matrices:
        try:
            matrix(rows)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("malformed matrix accepted")
    a = matrix(((Fraction(1, 2),),))
    invalid = (((1,), (1,), 0), ((1,), (0,), 2), ((1,), (0,), -1),
               ((1,), (0,), True), ((True,), (0,), 0), ((1,), (False,), 0))
    for x, z, history in invalid:
        try:
            decode(a, x, z, history)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid history/image accepted")
    a = matrix(((Fraction(1, 2),),) * 3)
    preimages = [y for y in product((-1, 0), repeat=3) if forward(a, (1,), y) == (0, 0, 0)]
    require(len(preimages) == 8 and len(preimages) > 2 ** 2, "three-bit lower witness")
    require(forward(a, (1,), (-1, -1, -1)) != (-1, -1, -1), "whole-sum control")
    require(nearest_even(Fraction(-1, 2)) == nearest_even(Fraction(1, 2)) == 0,
            "signed half ties")
    return rejected


def main():
    binary = binary_census()
    rational = rational_census()
    roundtrips = signed_roundtrips()
    rejected = rejection_controls()
    triangle = matrix(((Fraction(1, 2), 0),
                       (Fraction(1, 2), Fraction(1, 2)), (0, Fraction(1, 2))))
    repeated = matrix(((Fraction(1, 2), 0), (0, Fraction(1, 2)), (0, Fraction(1, 2))))
    require(periodic_theorem(triangle)[0] == 2, "rank-two history two")
    require(periodic_theorem(repeated)[0] == 3, "rank-two history three")
    package = Path(__file__).resolve().parent
    files = ("README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
    hashes = {name: sha256((package / name).read_bytes()).hexdigest() for name in files}
    receipt = dict(status="PASS_NEAREST_EVEN_SHEAR_HISTORY", python=platform.python_version(),
                   binary=dict(binary), rational=dict(rational), signed_roundtrips=roundtrips,
                   rejected_inputs=rejected, same_rank_history_bits=[2, 3], package_sha256=hashes)
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
