#!/usr/bin/env python3
"""Exact finite corroboration of PROOF.md; standard library, no writes."""

import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
FIELDS = (2, 3, 5, 7, 11)
BOUND_FILES = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
               "VERIFY.json", "verify.py")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def parameters(h, a, b):
    require(isinstance(h, Fraction) and 1 < h < 2, "tariff outside (1,2)")
    require(type(a) is int and type(b) is int and 1 <= a <= 1000
            and 1 <= b <= 1000, "multiplicity outside 1..1000")


def minimum_edges(h):
    parameters(h, 1, 1)
    return 2 * (1 // (2 - h)) + 1


def scalar_grid():
    tariffs = sorted({1 + Fraction(n, d) for d in range(2, 33)
                      for n in range(1, d)})
    cases = traps = ties = smaller = 0
    for h in tariffs:
        best = None
        for a in range(1, 41):
            for b in range(1, 41):
                parameters(h, a, b)
                initial, middle, final = a * h, a + b, b * h
                literal = middle > initial > final
                predicted = a > b and a * (2 - h) > a - b
                require(literal == predicted, "strict-trap predicate")
                cases += 1
                ties += int(middle == initial and initial > final)
                if literal:
                    traps += 1
                    best = a + b if best is None else min(best, a + b)
        optimum = minimum_edges(h)
        require(best == optimum, "bounded grid minimum")
        for total in range(2, optimum):
            for a in range(1, total):
                b = total - a
                require(not (a + b > a * h > b * h), "smaller graph")
                smaller += 1
        a = (optimum + 1) // 2
        require(a + a - 1 > a * h > (a - 1) * h, "attaining graph")
    return {"tariffs": len(tariffs), "pairs": cases, "strict_traps": traps,
            "ties_with_cheaper_zero": ties, "smaller_graph_pairs": smaller}


def multiply(a, b, p):
    return tuple(sum(a[2 * i + k] * b[2 * k + j] for k in range(2)) % p
                 for i in range(2) for j in range(2))


def image(a, vectors, p):
    return frozenset(((a[0] * x + a[1] * y) % p,
                      (a[2] * x + a[3] * y) % p) for x, y in vectors)


def projector(a, p):
    return (any(a) and (a[0] * a[3] - a[1] * a[2]) % p == 0
            and multiply(a, a, p) == a)


def profile(space, vectors, p, a=241, b=240):
    parameters(Fraction(3, 2), a, b)
    require(space <= frozenset(vectors) and (0, 0) in space, "bad frame")
    dimension = {1: 0, p: 1, p * p: 2}[len(space)]
    ranks = []
    for _ in range(a):
        ranks.append(dimension)
    for _ in range(b):
        ranks.append(2 - dimension)
    counts = Counter(ranks)
    require(sum(counts.values()) == a + b, "lost parallel edge")
    return tuple(counts[r] for r in range(3))


def field_checks(p):
    require(p in FIELDS, "unsupported field")
    vectors = tuple(product(range(p), repeat=2))
    lines = {frozenset(((k * x) % p, (k * y) % p) for k in range(p))
             for x, y in vectors if (x, y) != (0, 0)}
    require(len(lines) == p + 1, "projective line inventory")
    zero, full = frozenset({(0, 0)}), frozenset(vectors)
    frames = lines | {zero, full}
    profiles = {s: profile(s, vectors, p) for s in frames}
    require(profiles[zero] == (241, 0, 240), "zero profile")
    require(profiles[full] == (240, 0, 241), "full profile")
    require(all(profiles[s] == (0, 481, 0) for s in lines), "line profile")
    projectors = []
    matrices = 0
    for matrix in product(range(p), repeat=4):
        matrices += 1
        if projector(matrix, p):
            projectors.append(matrix)
            require(image(matrix, vectors, p) in lines, "projector image")
    require(len(projectors) == p * (p + 1), "projector inventory")
    zero_matrix = (0, 0, 0, 0)
    identity = (1, 0, 0, 1)
    orthogonal_pairs = 0
    pairs = 0
    for left in projectors:
        for right in projectors:
            pairs += 1
            lr, rl = multiply(left, right, p), multiply(right, left, p)
            if lr == zero_matrix and rl == zero_matrix:
                orthogonal_pairs += 1
                require(tuple((left[i] + right[i]) % p for i in range(4))
                        == identity, "complementary projectors")
                require(image(lr, vectors, p) == zero, "joint image")
    require(orthogonal_pairs == p * (p + 1), "joint escape inventory")
    return {"p": p, "frames": len(frames), "matrices": matrices,
            "projectors": len(projectors), "pairs": pairs,
            "joint_escapes": orthogonal_pairs,
            "literal_edges": 481 * len(frames)}


def power_sign(constant, coefficient, numerator, denominator):
    """Sign of constant+coefficient*2^(numerator/denominator), exactly."""
    require(type(numerator) is int and type(denominator) is int
            and 1 <= numerator <= denominator <= 1000, "bad power")
    require(type(constant) is int and type(coefficient) is int
            and abs(constant) <= 10000 and abs(coefficient) <= 10000,
            "bad linear power expression")
    if coefficient == 0:
        return (constant > 0) - (constant < 0)
    if constant == 0 or constant * coefficient > 0:
        return (coefficient > 0) - (coefficient < 0)
    difference = (2 ** numerator * abs(coefficient) ** denominator
                  - abs(constant) ** denominator)
    return ((coefficient > 0) - (coefficient < 0)) * (
        (difference > 0) - (difference < 0))


def power_checks():
    require(power_sign(479, -240, 997, 1000) == -1, "240 is too small")
    require(power_sign(481, -241, 997, 1000) == 1, "241 attains trap")
    require(power_sign(0, 1, 997, 1000) == 1, "joint improvement")
    small = 0
    for a in range(1, 241):
        for b in range(1, a):
            require(power_sign(a + b, -a, 997, 1000) < 0,
                    "smaller incoming multiplicity")
            small += 1
    require(Fraction(10940329, 3500000000) > Fraction(3, 1000),
            "pinned complex power is outside covered interval")
    require(power_sign(481, -241, 1, 1) == -1, "linear-tariff control")
    return {"exponent": "997/1000", "minimum_edges": 481,
            "a": 241, "b": 240, "smaller_a_pairs": small,
            "current_complex_C_provenance": "10940329/3500000000"}


def must_reject(kind, args):
    try:
        if kind == "parameters":
            parameters(*args)
        elif kind == "power":
            power_sign(*args)
        elif kind == "receipt":
            validate_receipt(*args)
        else:
            raise RuntimeError("unknown rejection control")
    except ValueError:
        return
    raise ValueError("control was accepted")


def validate_receipt(expected, actual):
    require(type(expected) is dict and expected == actual, "receipt mismatch")


def controls():
    names = []
    for bad in (Fraction(1), Fraction(2), Fraction(0), Fraction(3)):
        must_reject("parameters", (bad, 2, 1))
        names.append("invalid tariff " + str(bad))
    for a, b in ((0, 1), (1, 0), (1001, 1), (True, 1)):
        must_reject("parameters", (Fraction(3, 2), a, b))
        names.append("invalid multiplicity " + str((a, b)))
    require(not (3 > 2 * Fraction(3, 2) > Fraction(3, 2)), "tie is strict")
    names.append("non-strict boundary")
    require(minimum_edges(Fraction(3, 2)) == 5, "strict rounding control")
    names.append("integer reciprocal boundary")
    require(not projector((0, 1, 0, 0), 2), "nilpotent is a projection")
    names.append("non-idempotent rank-one map")
    require(multiply((1, 0, 0, 0), (1, 1, 0, 0), 2) != (0, 0, 0, 0),
            "noncomplementary pair is an escape")
    names.append("noncomplementary pair")
    must_reject("power", (1, -1, 1001, 1000))
    names.append("invalid power")
    must_reject("receipt", ({"count": 1}, {"count": 2}))
    names.append("changed receipt count")
    must_reject("receipt", ({"hash": "bad"}, {"hash": "good"}))
    names.append("changed receipt hash")
    return names


def receipt():
    return {
        "status": "PASS_PROJECTION_LOCAL_TRAP",
        "claim_type": "scoped proof with exact finite corroboration",
        "scalar_grid": scalar_grid(),
        "fields": [field_checks(p) for p in FIELDS],
        "power": power_checks(),
        "controls": controls(),
        "sha256": {name: sha256((PACKAGE / name).read_bytes()).hexdigest()
                   for name in BOUND_FILES},
        "new_kappa": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generate", action="store_true",
                        help="emit a new receipt without comparing RESULT.json")
    args = parser.parse_args()
    actual = receipt()
    if not args.generate:
        expected = json.loads((PACKAGE / "RESULT.json").read_text())
        validate_receipt(expected, actual)
    print(json.dumps(actual, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
