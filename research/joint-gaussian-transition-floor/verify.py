#!/usr/bin/env python3
"""Joint Gaussian transition checks. Produced by Nick Petalas. Apache-2.0."""
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
from math import gcd
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parent
SOURCE_NAMES = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
MAX_DIM = 12
MAX_WORD = 256


def need(condition, message):
    if not condition:
        raise ValueError(message)


def identity(n):
    need(type(n) is int and 1 <= n <= MAX_DIM, "matrix dimension")
    return [[F(i == j) for j in range(n)] for i in range(n)]


def validate(specs, dirty):
    need(type(dirty) is int and 0 <= dirty <= 4, "dirty workspace bound")
    need(1 <= len(specs) <= 4 and 2 * len(specs) + dirty <= MAX_DIM, "helper bound")
    for a, b, epsilon in specs:
        need(type(a) is int and -8 <= a <= 8, "finite verifier exponent bound")
        need(type(b) is int and b in (0, 1), "Gaussian parity")
        need(b == 0 or a <= 7, "odd-block domain closed under inverse")
        need(type(epsilon) is int and epsilon in (-1, 1), "conjugation sign")


def endpoint(specs, dirty=0):
    validate(specs, dirty)
    matrix = identity(2 * len(specs) + dirty)
    for j, (a, b, epsilon) in enumerate(specs):
        x, y = 2 * j, 2 * j + 1
        scale = F(2) ** a
        matrix[x][x] = matrix[y][y] = scale
        matrix[x][y] = -epsilon * b * scale
        matrix[y][x] = epsilon * b * scale
    return matrix


def recipe(specs, dirty=0):
    validate(specs, dirty)
    word = []
    for j, (a, b, epsilon) in enumerate(specs):
        x, y = 2 * j, 2 * j + 1
        residual = a
        if b:
            word.append(("add", x, y, -epsilon))
            word.append(("scale", y if a >= 0 else x, 1 if a >= 0 else -1))
            word.append(("add", y, x, epsilon))
            residual = a if a >= 0 else a + 1
        for coordinate in (x, y):
            for _ in range(abs(residual)):
                word.append(("scale", coordinate, 1 if residual > 0 else -1))
    need(len(word) <= MAX_WORD, "word capacity")
    return word


def execute(word, matrix):
    need(len(word) <= MAX_WORD, "word capacity")
    n = len(matrix)
    need(1 <= n <= MAX_DIM and all(len(row) == n for row in matrix), "square matrix")
    rows = [row[:] for row in matrix]
    for gate in word:
        if gate[0] == "add":
            _, destination, source, sign = gate
            need(0 <= destination < n and 0 <= source < n and destination != source, "ADD roles")
            need(sign in (-1, 1), "signed unit ADD")
            rows[destination] = [x + sign * y for x, y in zip(rows[destination], rows[source])]
        else:
            need(gate[0] == "scale" and len(gate) == 3, "gate alphabet")
            _, destination, exponent = gate
            need(0 <= destination < n and exponent in (-1, 1), "unit scale")
            rows[destination] = [x * F(2) ** exponent for x in rows[destination]]
    return rows


def inverse_word(word):
    return [gate[:-1] + (-gate[-1],) for gate in reversed(word)]


def inverse_specs(specs):
    return [(-a - b, b, -epsilon) for a, b, epsilon in specs]


def floors(specs):
    return sum(abs(2 * a + b) for a, b, _ in specs), 2 * sum(b for _, b, _ in specs)


def counts(word):
    return sum(g[0] == "scale" for g in word), sum(g[0] == "add" for g in word)


def require_budget(specs, scales, adds):
    scale_floor, add_floor = floors(specs)
    need(scales >= scale_floor and adds >= add_floor, "insufficient transition budget")


def mixed_rows(matrix):
    return sum(sum(x != 0 for x in row) >= 2 for row in matrix)


def check_case(specs, dirty):
    target = endpoint(specs, dirty)
    word = recipe(specs, dirty)
    n = len(target)
    need(execute(word, identity(n)) == target, "literal attaining endpoint")
    need(counts(word) == floors(specs), "simultaneous scale and ADD optimum")
    need(mixed_rows(target) == floors(specs)[1], "mixed-row lower bound")
    need(execute(inverse_word(word), target) == identity(n), "all-input inverse restoration")
    need(execute(recipe(inverse_specs(specs), dirty), target) == identity(n), "separate inverse recipe")
    return len(word)


def power_log(value):
    need(type(value) is int and value > 0 and value & (value - 1) == 0, "positive power of two")
    return value.bit_length() - 1


def finite_lattice(specs):
    """Enumerate L/(2 Z^n) inside ((1/2) Z^n)/(2 Z^n)."""
    n = 2 * len(specs)
    need(1 <= len(specs) <= 2 and all(a in (-1, 0) for a, _, _ in specs), "finite lattice domain")
    matrix = endpoint(specs)
    inv = endpoint(inverse_specs(specs))
    need(all((2 * x).denominator == 1 for row in matrix for x in row), "L below half-grid")
    need(all((2 * x).denominator == 1 for row in inv for x in row), "L contains twice-grid")
    elements, integers = set(), set()
    for point in product(range(4), repeat=n):
        if all(v % 2 == 0 for v in point):
            integers.add(point)
        preimage = [sum(row[j] * F(point[j], 2) for j in range(n)) for row in inv]
        if all(x.denominator == 1 for x in preimage):
            elements.add(point)
    return elements, integers


def distance(left, right):
    common = len(left & right)
    need(common > 0 and len(left) % common == 0 and len(right) % common == 0, "lattice indices")
    return power_log(len(left) // common) + power_log(len(right) // common)


def lattice_checks():
    types = [(a, b, e) for a in (-1, 0) for b in (0, 1) for e in ((1,) if b == 0 else (-1, 1))]
    checked = 0
    for helpers in (1, 2):
        for specs in product(types, repeat=helpers):
            lattice, integers = finite_lattice(specs)
            need(distance(lattice, integers) == floors(specs)[0], "enumerated lattice floor")
            checked += 1
    one = [finite_lattice((spec,))[0] for spec in types]
    triangles = 0
    for left, middle, right in product(one, repeat=3):
        need(distance(left, right) <= distance(left, middle) + distance(middle, right), "triangle inequality")
        triangles += 1
    return checked, triangles


def two_dimensional_distance(matrix):
    """Classical 2x2 Smith invariants, only for short-word controls."""
    denominator = max(x.denominator for row in matrix for x in row)
    integers = [int(x * denominator) for row in matrix for x in row]
    divisor = gcd(*integers)
    determinant = abs(integers[0] * integers[3] - integers[1] * integers[2])
    first = power_log(divisor) - power_log(denominator)
    second = power_log(determinant // divisor) - power_log(denominator)
    return abs(first) + abs(second)


def short_word_checks():
    alphabet = [("add", i, 1 - i, e) for i in range(2) for e in (-1, 1)]
    alphabet += [("scale", i, e) for i in range(2) for e in (-1, 1)]
    checked = 0
    for length in range(5):
        for word in product(alphabet, repeat=length):
            matrix = execute(word, identity(2))
            scales, adds = counts(word)
            need(two_dimensional_distance(matrix) <= scales, "arbitrary short-word scale floor")
            need(mixed_rows(matrix) <= adds, "arbitrary short-word ADD floor")
            checked += 1
    return checked


def rejection_checks():
    rejected = 0
    invalid = [([(0, 2, 1)], 0), ([(0, 1, 0)], 0), ([(F(1, 2), 1, 1)], 0),
               ([(9, 1, 1)], 0), ([(8, 1, 1)], 0),
               ([(0, 1, 1)], -1), ([(0, 1, 1)] * 5, 0)]
    for specs, dirty in invalid:
        try:
            recipe(specs, dirty)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid boundary accepted")
    pair = [(0, 1, 1), (-1, 1, -1)]
    word, target = recipe(pair, 1), endpoint(pair, 1)
    need(floors(pair) == (2, 4), "reciprocal six-call fixture")
    need(abs(sum(2 * a + b for a, b, _ in pair)) == 0, "determinant-cancellation control")
    mutants = [word[1:], word[:-1], word + [("add", 4, 0, 1)],
               recipe([(0, 1, 1), (-1, 1, 1)], 1)]
    for mutant in mutants:
        need(execute(mutant, identity(5)) != target, "bad endpoint must reject")
        rejected += 1
    for scales, adds in ((0, 4), (1, 4), (2, 3)):
        try:
            require_budget(pair, scales, adds)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("false resource budget accepted")
    return rejected


def source_hashes():
    result = {}
    for name in SOURCE_NAMES:
        data = (ROOT / name).read_bytes()
        need(len(data) <= 1024 * 1024, "source size bound")
        result[name] = sha256(data).hexdigest()
    return result


def scientific_result():
    types = [(a, b, e) for a in range(-3, 4) for b in (0, 1) for e in ((1,) if b == 0 else (-1, 1))]
    cases, largest = 0, 0
    for helpers in (1, 2):
        for specs in product(types, repeat=helpers):
            for dirty in (0, 2):
                largest = max(largest, check_case(specs, dirty))
                cases += 1
    for specs in product(((-1, 1, -1), (0, 1, 1), (1, 0, 1)), repeat=4):
        largest = max(largest, check_case(specs, 2))
        cases += 1
    boundaries = [(-8, 0, 1), (8, 0, 1), (-8, 1, -1), (-8, 1, 1), (7, 1, -1), (7, 1, 1)]
    for spec in boundaries:
        largest = max(largest, check_case((spec,), 4))
        cases += 1
    lattices, triangles = lattice_checks()
    return {"claim_type": "scoped proof with exact finite corroboration", "attaining_cases": cases,
            "maximum_checked_word_length": largest, "finite_lattices": lattices,
            "lattice_triangles": triangles, "short_words": short_word_checks(),
            "rejecting_controls": rejection_checks(), "reciprocal_pair": {"scales": 2, "adds": 4, "total": 6},
            "source_sha256": source_hashes()}


def main():
    need(sys.argv[1:] in ([], ["--emit-result"]), "only --emit-result is supported")
    result = scientific_result()
    if sys.argv[1:]:
        print(json.dumps(result, sort_keys=True, indent=2))
        return
    raw = (ROOT / "RESULT.json").read_bytes()
    need(len(raw) <= 1024 * 1024, "receipt size bound")
    need(json.dumps(result, sort_keys=True) == json.dumps(json.loads(raw), sort_keys=True), "complete generated receipt")
    print(json.dumps(result, sort_keys=True))
    print("PASS_JOINT_GAUSSIAN_TRANSITION_FLOOR no_new_kappa")


if __name__ == "__main__":
    main()
