#!/usr/bin/env python3
"""Exact constructive evidence for supplied dyadic affine regions. Apache-2.0."""

import hashlib
import itertools
import json
from fractions import Fraction as F
from pathlib import Path
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identity(n):
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))


def multiply(a, b):
    return tuple(tuple(sum(x * y for x, y in zip(row, col, strict=True))
                       for col in zip(*b, strict=True)) for row in a)


def apply(a, x):
    return tuple(sum(u * v for u, v in zip(row, x, strict=True)) for row in a)


def inverse(a):
    n = len(a)
    work = [list(map(F, row)) + list(unit)
            for row, unit in zip(a, identity(n), strict=True)]
    determinant = F(1)
    for j in range(n):
        pivot = next((i for i in range(j, n) if work[i][j]), None)
        require(pivot is not None, "singular chart")
        if pivot != j:
            work[j], work[pivot] = work[pivot], work[j]
            determinant = -determinant
        value = work[j][j]
        determinant *= value
        work[j] = [x / value for x in work[j]]
        for i in range(n):
            if i != j:
                value = work[i][j]
                work[i] = [x - value * y
                           for x, y in zip(work[i], work[j], strict=True)]
    return tuple(tuple(row[n:]) for row in work), determinant


def integer_matrix(a, rows, cols):
    require(len(a) == rows and all(len(row) == cols for row in a), "matrix shape")
    require(all(type(x) is int and abs(x).bit_length() <= 64
                for row in a for x in row), "integer matrix entry")


def smith_data(e, b, u, v):
    m, n = len(e), len(v)
    require(1 <= m <= 6 and 1 <= n <= 6, "dimension bound")
    integer_matrix(e, m, n)
    integer_matrix(u, m, m)
    integer_matrix(v, n, n)
    require(len(b) == m and all(type(x) is int and abs(x).bit_length() <= 64
                               for x in b), "integer right hand side")
    _, det_u = inverse(u)
    inv_v, det_v = inverse(v)
    require(abs(det_u) == 1 and abs(det_v) == 1, "unimodular charts required")
    d = multiply(multiply(u, e), v)
    diagonal = tuple(d[i][i] for i in range(min(m, n)))
    rank = sum(x != 0 for x in diagonal)
    require(all(d[i][j] == (diagonal[i] if i == j else 0)
                for i in range(m) for j in range(n)), "not diagonal")
    require(all(x > 0 for x in diagonal[:rank]) and
            all(x == 0 for x in diagonal[rank:]), "positive Smith prefix")
    require(all(diagonal[i + 1] % diagonal[i] == 0
                for i in range(rank - 1)), "Smith divisibility")
    return diagonal, apply(u, b), rank, inv_v


def dyadic_bits(x):
    denominator = x.denominator
    if denominator & (denominator - 1):
        return None
    return denominator.bit_length() - 1


def strict_power_bits(ratio):
    if ratio <= 0:
        return 0
    bits = max(0, ratio.numerator.bit_length() - ratio.denominator.bit_length())
    return bits + int(F(2**bits) <= ratio)


def construct(e, b, u, v, witness, rows=(), bounds=()):
    diagonal, c, rank, inv_v = smith_data(e, b, u, v)
    n = len(v)
    require(len(witness) == n and len(rows) == len(bounds) <= 32, "region shape")
    require(all(len(row) == n for row in rows), "inequality shape")
    values = (*witness, *bounds, *(x for row in rows for x in row))
    require(all(type(x) in (int, F) and abs(F(x).numerator).bit_length() <= 64
                and F(x).denominator.bit_length() <= 64 for x in values),
            "rational entry bound")
    require(apply(e, witness) == tuple(b), "false affine witness")
    margins = tuple(bound - value for bound, value in
                    zip(bounds, apply(rows, witness), strict=True))
    require(all(x > 0 for x in margins), "witness must be strict")
    fixed = tuple(F(c[i], diagonal[i]) for i in range(rank))
    for i, value in enumerate(fixed):
        if dyadic_bits(value) is None:
            return {"status": "obstructed", "index": i,
                    "forced_value": str(value)}
    bits = max((dyadic_bits(x) for x in fixed), default=0)
    equality_bits = bits
    transformed_rows = multiply(rows, v)
    for row, margin in zip(transformed_rows, margins, strict=True):
        seminorm = sum(abs(x) for x in row[rank:])
        bits = max(bits, strict_power_bits(F(seminorm, 2 * margin)))
    require(bits <= 4096, "executable precision bound exhausted")
    y = apply(inv_v, witness)
    scale = 2**bits
    rounded = fixed + tuple(F((scale * z + F(1, 2)).__floor__(), scale)
                            for z in y[rank:])
    point = apply(v, rounded)
    require(apply(e, point) == tuple(b), "constructed equality failed")
    require(all(value < bound for value, bound in
                zip(apply(rows, point), bounds, strict=True)), "constructed margin failed")
    return {"status": "constructed", "equality_bits": equality_bits,
            "bits": bits, "point": point}


def charts(n):
    result = [identity(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                for sign in (-1, 1):
                    a = [list(row) for row in identity(n)]
                    a[i][j] = sign
                    result.append(tuple(map(tuple, a)))
    a = list(identity(n))
    a[0], a[-1] = a[-1], a[0]
    result.append(tuple(a))
    return tuple(dict.fromkeys(result))


def integral(a):
    require(all(F(x).denominator == 1 for row in a for x in row), "not integral")
    return tuple(tuple(int(x) for x in row) for row in a)


def coupled_cases():
    counts = {"coupled_regions": 0, "constructed": 0, "obstructed": 0}
    for n in (2, 3):
        profiles = ((0,) * n, (1,) + (0,) * (n - 1),
                    (2,) + (0,) * (n - 1), (3,) + (0,) * (n - 1),
                    (1,) * (n - 1) + (6,), (2,) * n)
        for u, v, ds, sign, denominator in itertools.product(
                charts(n), charts(n), profiles, (-1, 1), (3, 17)):
            inv_u, _ = inverse(u)
            inv_v, _ = inverse(v)
            d = tuple(tuple(ds[i] if i == j else 0 for j in range(n))
                      for i in range(n))
            e = integral(multiply(multiply(inv_u, d), inv_v))
            c = tuple(sign if x else 0 for x in ds)
            b = tuple(int(x) for x in apply(inv_u, c))
            y = tuple(F(sign, x) if x else F(sign, denominator) for x in ds)
            witness = apply(v, y)
            rows = tuple(identity(n)) + tuple(tuple(-x for x in row)
                                                 for row in identity(n))
            margins = (F(1, denominator),) * (2 * n)
            bounds = tuple(x + margin for x, margin in
                           zip(apply(rows, witness), margins, strict=True))
            got = construct(e, b, u, v, witness, rows, bounds)
            expected_obstruction = any(F(sign, x).denominator % 3 == 0 for x in ds if x)
            require((got["status"] == "obstructed") == expected_obstruction,
                    "wrong coupled classification")
            if got["status"] == "constructed":
                require(all((x * 2**got["bits"]).denominator == 1
                            for x in got["point"]), "point not on grid")
                expected_bits = max((F(sign, x).denominator.bit_length() - 1
                                     for x in ds if x), default=0)
                require(got["equality_bits"] == expected_bits, "wrong equality precision")
                counts["constructed"] += 1
            else:
                counts["obstructed"] += 1
            counts["coupled_regions"] += 1
    return counts


def exhaustive_grids():
    cases = points = 0
    for v, ds, sign in itertools.product(charts(2), ((0, 0), (1, 0), (2, 0),
                                                  (3, 0), (1, 2), (2, 4)), (-1, 1)):
        inv_v, _ = inverse(v)
        d = tuple(tuple(ds[i] if i == j else 0 for j in range(2)) for i in range(2))
        e = integral(multiply(d, inv_v))
        b = tuple(sign if x else 0 for x in ds)
        for bits in range(3):
            found = False
            for numerator in itertools.product(range(-8, 9), repeat=2):
                point = tuple(F(x, 2**bits) for x in numerator)
                found |= apply(e, point) == b
                points += 1
            expected = all((sign * 2**bits) % x == 0 for x in ds if x)
            require(found == expected, "literal grid disagrees with equality threshold")
            cases += 1
    return {"complete_grid_cases": cases, "grid_points": points}


def scalar_cases():
    count = 0
    for a, b in itertools.product(range(1, 33), range(-32, 33)):
        got = construct(((a,),), (b,), ((1,),), ((1,),), (F(b, a),))
        denominator = F(b, a).denominator
        odd = denominator
        for _ in range(denominator.bit_length()):
            if odd % 2 == 0:
                odd //= 2
        require((got["status"] == "obstructed") == (odd != 1), "scalar obstruction")
        if odd == 1:
            require(got["bits"] == denominator.bit_length() - 1, "scalar minimum")
        count += 1
    return {"scalar_equalities": count}


def controls():
    valid = [((2,),), (1,), ((1,),), ((1,),), (F(1, 2),)]
    invalid = []
    for position, value in ((0, ((3,),)), (1, (2,)), (2, ((2,),)),
                            (3, ((2,),)), (4, (F(1, 3),))):
        case = list(valid)
        case[position] = value
        invalid.append(case)
    invalid.extend([
        [((1, 1), (0, 1)), (1, 1), identity(2), identity(2), (0, 1)],
        [((2, 0), (0, 3)), (2, 3), identity(2), identity(2), (1, 1)],
        [((0,),), (1,), ((1,),), ((1,),), (0,)],
        [((True,),), (1,), ((1,),), ((1,),), (1,)],
    ])
    rejected = 0
    for case in invalid:
        try:
            construct(*case)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid input accepted")
    for bound in (F(1, 2), F(0)):
        try:
            construct(*valid, rows=((1,),), bounds=(bound,))
        except ValueError:
            rejected += 1
        else:
            raise ValueError("nonstrict witness accepted")
    edge = construct(((0,),), (0,), ((1,),), ((1,),), (F(1, 2),), ((1,),), (1,))
    require(edge["bits"] == 1 and edge["point"] == (F(1, 2),), "strict boundary")
    require(F((F(1, 2) + F(1, 2)).__floor__()) == 1, "midpoint witness")
    high = construct(((2**60,),), (1,), ((1,),), ((1,),), (F(1, 2**60),))
    require(high["equality_bits"] == 60 and high["bits"] == 60, "high precision")
    coupled = construct(((3, 1),), (1,), ((1,),), ((0, 1), (1, -3)),
                        (F(1, 3), 0), ((1, 0), (-1, 0)), (F(1, 2), F(-1, 4)))
    require(coupled["status"] == "constructed", "coupled cancellation")
    return {"rejected_inputs": rejected, "semantic_controls": 3}


def main():
    require(len(sys.argv) == 1, "this standalone replay takes no arguments")
    result = {"status": "PASS_DYADIC_AFFINE_FEASIBILITY"}
    result.update(scalar_cases())
    result.update(coupled_cases())
    result.update(exhaustive_grids())
    result.update(controls())
    package = Path(__file__).resolve().parent
    result["sha256"] = {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
                        for name in ("README.md", "TASK.json", "SOURCES.json",
                                     "VERIFY.json", "verify.py")}
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
