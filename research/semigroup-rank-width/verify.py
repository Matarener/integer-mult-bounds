#!/usr/bin/env python3
"""Exact finite checks for the valuation-projection width lemma.

Produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.
"""
import argparse
from fractions import Fraction
import hashlib
from itertools import combinations, product
import json
from math import prod
from pathlib import Path
import platform

MAX_GENERATORS = 16
MAX_GENERATOR = 1_000_000
MAX_CAP = 65_536


def require(condition, message):
    if not condition:
        raise ValueError(message)


def alphabet(values):
    require(isinstance(values, (list, tuple)), "alphabet must be a list or tuple")
    require(1 <= len(values) <= MAX_GENERATORS, "alphabet capacity")
    require(all(type(x) is int and 1 <= x <= MAX_GENERATOR for x in values),
            "generator range")
    return tuple(sorted(set(values)))


def factor(value):
    require(type(value) is int and 1 <= value <= MAX_GENERATOR, "factor range")
    result = {}
    remainder = value
    for divisor in range(2, 1001):
        if divisor * divisor > remainder:
            break
        for _ in range(20):
            if remainder % divisor:
                break
            result[divisor] = result.get(divisor, 0) + 1
            remainder //= divisor
    if remainder > 1:
        result[remainder] = result.get(remainder, 0) + 1
    require(prod(p ** e for p, e in result.items()) == value, "factorization")
    return result


def floor_log(base, value):
    require(type(base) is int and base >= 2, "log base")
    require(type(value) is int and 1 <= value <= MAX_CAP, "cap range")
    power = 1
    exponent = 0
    for _ in range(value.bit_length()):
        if power * base > value:
            break
        power *= base
        exponent += 1
    require(power <= value < power * base, "integer logarithm")
    return exponent


def pivots(matrix):
    """Return pivot columns of a rational row matrix."""
    require(len(matrix) <= MAX_GENERATORS, "matrix row capacity")
    width = len(matrix[0]) if matrix else 0
    require(width <= 7 * MAX_GENERATORS, "matrix column capacity")
    require(all(len(row) == width for row in matrix), "matrix shape")
    rows = [[Fraction(x) for x in row] for row in matrix]
    columns = []
    for col in range(width):
        start = len(columns)
        selected = next((i for i in range(start, len(rows)) if rows[i][col]), None)
        if selected is None:
            continue
        rows[start], rows[selected] = rows[selected], rows[start]
        scale = rows[start][col]
        rows[start] = [x / scale for x in rows[start]]
        for i in range(start + 1, len(rows)):
            multiplier = rows[i][col]
            rows[i] = [x - multiplier * y for x, y in zip(rows[i], rows[start])]
        columns.append(col)
    return tuple(columns)


def certificate(values):
    values = alphabet(values)
    factors = [factor(value) for value in values]
    primes = tuple(sorted({p for row in factors for p in row}))
    matrix = tuple(tuple(row.get(p, 0) for p in primes) for row in factors)
    coordinates = tuple(primes[i] for i in pivots(matrix))
    return primes, matrix, coordinates


def validate_projection(values, coordinates):
    primes, matrix, expected = certificate(values)
    require(isinstance(coordinates, tuple), "coordinate type")
    require(len(set(coordinates)) == len(coordinates), "duplicate coordinate")
    require(all(p in primes for p in coordinates), "coordinate outside support")
    require(len(coordinates) == len(expected), "coordinate count")
    selected = [[row[primes.index(p)] for p in coordinates] for row in matrix]
    require(len(pivots(selected)) == len(expected), "projection loses rank")
    return True


def exponent_at(value, prime):
    exponent = 0
    remainder = value
    for _ in range(value.bit_length()):
        if remainder % prime:
            break
        exponent += 1
        remainder //= prime
    return exponent


def semigroup(values, cap):
    """Enumerate by multiplying bounded powers of each generator."""
    values = alphabet(values)
    floor_log(2, cap)
    members = {1}
    for generator in values:
        if generator == 1:
            continue
        previous = tuple(members)
        for member in previous:
            value = member
            for _ in range(cap.bit_length()):
                if value > cap // generator:
                    break
                value *= generator
                members.add(value)
    require(len(members) <= cap, "semigroup capacity")
    return tuple(sorted(members))


def membership_oracle(values, cap):
    """Independent integer-by-integer divisibility recurrence."""
    reachable = [False] * (cap + 1)
    reachable[1] = True
    for value in range(2, cap + 1):
        reachable[value] = any(g > 1 and value % g == 0 and reachable[value // g]
                               for g in values)
    return tuple(i for i in range(1, cap + 1) if reachable[i])


def determinant(matrix):
    """Leibniz determinant, limited to minors of order at most three."""
    size = len(matrix)
    require(size <= 3 and all(len(row) == size for row in matrix), "minor size")
    result = 0
    for indices in product(range(size), repeat=size):
        if len(set(indices)) != size:
            continue
        inversions = sum(indices[i] > indices[j] for i in range(size)
                         for j in range(i + 1, size))
        result += (-1) ** inversions * prod(matrix[i][indices[i]] for i in range(size))
    return result


def minor_rank(matrix):
    require(len(matrix) <= 3, "minor oracle row capacity")
    width = len(matrix[0]) if matrix else 0
    result = 0
    for size in range(1, min(len(matrix), width) + 1):
        for rows in combinations(range(len(matrix)), size):
            for cols in combinations(range(width), size):
                if determinant([[matrix[i][j] for j in cols] for i in rows]):
                    result = size
    return result


def check_fixture(values, cap):
    primes, matrix, coordinates = certificate(values)
    require(validate_projection(values, coordinates), "projection validation")
    members = semigroup(values, cap)
    require(members == membership_oracle(values, cap), "semigroup oracle")
    images = {tuple(exponent_at(x, p) for p in coordinates) for x in members}
    require(len(images) == len(members), "projection collision")
    bound = prod(1 + floor_log(p, cap) for p in coordinates)
    full_box = prod(1 + floor_log(p, cap) for p in primes)
    require(len(members) <= bound <= full_box, "box bound")
    require(minor_rank(matrix) == len(coordinates), "independent minor rank")
    return len(members), len(coordinates) < len(primes)


def width_envelope(targets, paid, cap):
    require(isinstance(targets, dict) and isinstance(paid, dict), "profile type")
    alphabet(tuple(targets))
    alphabet(tuple(paid))
    require(min(targets) >= 2 and max(paid) < max(targets), "profile rank order")
    require(all(type(v) is int and 1 <= v <= 1000
                for v in (*targets.values(), *paid.values())), "multiplicity range")
    _, _, coordinates = certificate(tuple(targets) + tuple(paid))
    w, p = sum(targets.values()), sum(paid.values())
    height = floor_log(min(targets), cap)
    tau = max(targets) * (min(targets) - 1).bit_length()
    box = prod(1 + floor_log(prime, cap) for prime in coordinates)
    bits = tau * box * ((w - 1).bit_length() + height * (w + p - 1).bit_length())
    return {"prime_coordinates": list(coordinates), "rank": len(coordinates),
            "height": height, "tau": tau, "plateau_box": box, "log2_width_bound": bits}


def must_reject(operation, message):
    try:
        operation()
    except ValueError as exc:
        require(str(exc) == message, "unexpected rejection: " + str(exc))
        return
    raise ValueError("control accepted: " + message)


def check_controls():
    controls = [
        (lambda: alphabet([]), "alphabet capacity"),
        (lambda: alphabet([2] * 17), "alphabet capacity"),
        (lambda: alphabet([True]), "generator range"),
        (lambda: alphabet([0]), "generator range"),
        (lambda: alphabet([MAX_GENERATOR + 1]), "generator range"),
        (lambda: semigroup([2], MAX_CAP + 1), "cap range"),
        (lambda: floor_log(1, 2), "log base"),
        (lambda: validate_projection([6, 10], (3,)), "coordinate count"),
        (lambda: validate_projection([6, 10, 15], (2, 2, 3)), "duplicate coordinate"),
        (lambda: validate_projection([6, 10, 15], (2, 3, 7)), "coordinate outside support"),
        (lambda: validate_projection([2, 15], (3, 5)), "projection loses rank"),
        (lambda: width_envelope({2: 1}, {2: 1}, 16), "profile rank order"),
        (lambda: width_envelope({6: True}, {1: 1}, 16), "multiplicity range"),
    ]
    for operation, message in controls:
        must_reject(operation, message)
    require(exponent_at(1, 3) == exponent_at(10, 3), "bad-coordinate collision")
    require(len(certificate([2, 4])[2]) == 1 and
            len(certificate([2, 3, 4])[2]) == 2, "omitted paid rank control")
    return len(controls) + 2


def run_checks():
    fixtures = members = strict = 0
    for size in range(1, 4):
        for values in combinations(range(1, 13), size):
            for cap in (1, 7, 64, 257):
                count, reduction = check_fixture(values, cap)
                fixtures += 1
                members += count
                strict += reduction
    witnesses = []
    for values in ((1, 6, 36), (6, 10, 60), (12, 18), (6, 10, 15)):
        count, reduction = check_fixture(values, 46_656)
        primes, _, coordinates = certificate(values)
        witnesses.append({"generators": list(values), "cap": 46_656,
                          "members": count, "prime_count": len(primes),
                          "rank": len(coordinates), "coordinates": list(coordinates)})
        fixtures += 1
        members += count
        strict += reduction
    envelope = width_envelope({6: 1, 36: 1}, {1: 1, 6: 1}, 46_656)
    require(envelope["rank"] == 1 and envelope["plateau_box"] == 16,
            "width witness projection")
    require(envelope["height"] == 6 and envelope["tau"] == 108 and
            envelope["log2_width_bound"] == 22_464, "width envelope arithmetic")
    require(semigroup([1, 6, 36], 46_656) == tuple(6 ** i for i in range(7)),
            "rank-one exact semigroup")
    return {"fixtures": fixtures, "enumerated_members": members,
            "strict_rank_reductions": strict, "controls": check_controls(),
            "witnesses": witnesses, "width_witness": envelope}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=Path, help="create a new hash-bound receipt")
    args = parser.parse_args()
    result = run_checks()
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {name: hashlib.sha256((package / name).read_bytes()).hexdigest() for name in names}
    receipt = {"schema_version": 1, "python": platform.python_version(),
               "package_sha256": hashes, "result": result}
    if args.record is not None:
        with args.record.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print("PASS_SEMIGROUP_RANK_WIDTH " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
