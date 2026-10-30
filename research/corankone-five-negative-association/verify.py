#!/usr/bin/env python3
"""Exact finite component of five-indicator negative association.

Nick Petalas. Apache-2.0. The power-sum and Mobius routines adapt
Krzysztof Wojt's PR5093. Moment spectra are credited inputs from
Nick Petalas PR4227/4261/4275/4599 and Ryanson Jonathan PR4607.
No predecessor executable is imported. No files are written.
"""

from collections import defaultdict
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from math import comb, prod
from pathlib import Path
import platform

# Intersection spectra from the cited counting inputs, not a new spectrum claim.
SPECTRA = (
    {1: 1},
    {3: 1},
    {5: 1, 7: -2, 9: 1},
    {9: -2, 11: 9, 13: -18, 15: 16, 17: -6,
     19: 6, 21: -6, 27: 1},
    {17: 6, 19: -48, 21: 144, 23: -332, 25: 523,
     27: -548, 29: 502, 31: -444, 33: 399, 35: -336,
     37: 228, 39: -180, 41: 85, 43: -68, 45: 118,
     47: -48, 49: 18, 51: -24, 55: -8, 57: 24,
     63: -12, 81: 1},
    {33: -24, 35: 240, 37: -1080, 39: 2700, 41: -6620,
     43: 15154, 45: -24920, 47: 37380, 49: -54660, 51: 65830,
     53: -72884, 55: 76440, 57: -72900, 59: 71120, 61: -68780,
     63: 66112, 65: -58760, 67: 50225, 69: -45880, 71: 37000,
     73: -33560, 75: 30950, 77: -24720, 79: 22980, 81: -19520,
     83: 12535, 85: -10940, 87: 12040, 89: -7680, 91: 6600,
     93: -7740, 95: 4640, 97: -3740, 99: 4935, 101: -2200,
     103: 2200, 105: -3500, 107: 1020, 109: -1120, 111: 1680,
     113: -500, 115: 480, 117: -1320, 119: 360, 121: -120,
     123: 676, 125: -140, 127: 200, 129: -460, 131: 150,
     133: -120, 135: 460, 137: -40, 139: 20, 141: -240,
     147: 90, 153: -60, 163: 10, 165: -40, 171: 60,
     189: -20, 243: 1},
)

# B, c, b, C, N for the 37 gaps in exhaustive first-occurrence order.
TAILS = (
    (458752, 512, 327680, 46655488, 34),
    (344064, 512, 311296, 135826176, 125),
    (458752, 1024, 344064, 220461824, 43),
    (258048, 384, 233472, 913449728, 147),
    (344064, 1024, 311296, 1174723456, 140),
    (344064, 1536, 311296, 2218810240, 142),
    (458752, 512, 344064, 1090742784, 51),
    (458752, 1536, 344064, 1423748864, 48),
    (193536, 256, 175104, 13308763072, 178),
    (258048, 768, 233472, 15120260416, 168),
    (258048, 1152, 233472, 29334772288, 171),
    (344064, 512, 311296, 14324733568, 172),
    (344064, 1536, 311296, 16417920128, 162),
    (258048, 1536, 233472, 43549284160, 172),
    (344064, 512, 311296, 28530041344, 179),
    (344064, 1024, 311296, 13580415680, 164),
    (458752, 512, 327680, 14261167744, 51),
    (344064, 2048, 311296, 17454305728, 160),
    (344064, 2560, 311296, 32705203584, 164),
    (458752, 512, 344064, 16333939968, 61),
    (344064, 3072, 311296, 47956101440, 166),
    (458752, 512, 344064, 31584838336, 63),
    (458752, 1024, 327680, 15213572160, 50),
    (458752, 2048, 344064, 17868236992, 56),
    (258048, 512, 233472, 945765376, 145),
    (344064, 1024, 311296, 1207039232, 140),
    (458752, 2048, 344064, 1626164224, 48),
    (193536, 384, 175104, 13552200704, 174),
    (258048, 1024, 233472, 15425906176, 166),
    (258048, 1536, 233472, 29914959808, 168),
    (344064, 512, 311296, 14599275456, 172),
    (344064, 1536, 311296, 16754670272, 162),
    (258048, 768, 233472, 15363698176, 168),
    (344064, 2048, 311296, 17759951744, 160),
    (344064, 3072, 311296, 34321777088, 163),
    (458752, 1024, 344064, 16524500160, 58),
    (458752, 3072, 344064, 19578975040, 55),
)

SPLITS = ((1, 1), (1, 2), (1, 3), (1, 4), (2, 2), (2, 3))
PACKAGE_FILES = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
                 "VERIFY.json", "verify.py")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def add(*terms):
    """Add integer multiples of finite power sums."""
    result = defaultdict(int)
    for multiplier, polynomial in terms:
        for base, coefficient in polynomial.items():
            result[base] += multiplier * coefficient
    return {base: value for base, value in result.items() if value}


def multiply(left, right):
    """Pointwise multiplication of finite exponential sequences."""
    result = defaultdict(int)
    for base, coefficient in left.items():
        for other, value in right.items():
            result[base * other] += coefficient * value
    require(len(result) <= 4096, "power-sum capacity exceeded")
    return {base: value for base, value in result.items() if value}


def evaluate(polynomial, n):
    return sum(coefficient * base**n for base, coefficient in polynomial.items())


def numerators():
    """p_k=A_k/Q with Q=32^n product_(j=0)^4 (2^(n+1)-2^j)."""
    result = []
    for k in range(6):
        polynomial = multiply(SPECTRA[k], {2**(5 - k): 1})
        for j in range(k, 5):
            polynomial = multiply(polynomial, {2: 2, 1: -(2**j)})
        result.append(polynomial)
    return tuple(result)


def gap_polynomial(f, g, nums):
    left = add(*[(a, nums[i]) for i, a in enumerate(f)])
    right = add(*[(b, nums[j]) for j, b in enumerate(g)])
    joint = add(*[(a * b, nums[i + j])
                  for i, a in enumerate(f) for j, b in enumerate(g)])
    return add((1, multiply(left, right)), (-1, multiply(nums[0], joint)))


def moments(m):
    require(type(m) is int and 5 <= m <= 513, "dimension outside finite checker")
    n, x = m - 1, 2**m
    return tuple(Fraction(evaluate(SPECTRA[k], n),
                          2**(k * n) * prod(x - 2**j for j in range(k)))
                 for k in range(6))


def gap_value(f, g, p):
    return (sum(a * p[i] for i, a in enumerate(f)) *
            sum(b * p[j] for j, b in enumerate(g)) -
            sum(a * b * p[i + j] for i, a in enumerate(f) for j, b in enumerate(g)))


def monotone_tables(size):
    """All nonconstant increasing Boolean functions on at most four bits."""
    require(type(size) is int and 1 <= size <= 4, "unsupported Boolean dimension")
    return tuple(table for table in range(1, (1 << (1 << size)) - 1)
                 if all(not (table >> x & 1) or (table >> (x | (1 << j)) & 1)
                        for x in range(1 << size) for j in range(size)))


def expectation_coefficients(table, size):
    coefficients = [table >> x & 1 for x in range(1 << size)]
    for j in range(size):
        for x in range(1 << size):
            if x >> j & 1:
                coefficients[x] -= coefficients[x ^ (1 << j)]
    # Check every truth value before discarding which variables occur.
    for x in range(1 << size):
        require(sum(coefficients[y] for y in range(1 << size) if y & x == y)
                == (table >> x & 1), "Mobius reconstruction differs")
    return tuple(sum(coefficients[x] for x in range(1 << size)
                     if x.bit_count() == k) for k in range(size + 1))


def classify(nums):
    tables = {s: monotone_tables(s) for s in range(1, 5)}
    require(tuple(len(tables[s]) for s in range(1, 5)) == (1, 4, 18, 166),
            "incomplete monotone-function list")
    coefficients = {(s, table): expectation_coefficients(table, s)
                    for s in range(1, 5) for table in tables[s]}
    cases, labelled = {}, 0
    for s, t in SPLITS:
        for left, right in product(tables[s], tables[t]):
            f, g = coefficients[s, left], coefficients[t, right]
            polynomial = gap_polynomial(f, g, nums)
            key = tuple(sorted(polynomial.items()))
            cases.setdefault(key, (s, t, f, g, polynomial))
            labelled += 1
    require(labelled == 277 and len(cases) == 37, "covariance coverage differs")
    return tables, coefficients, tuple(cases.values()), labelled


def verify_tail(polynomial, certificate):
    require(len(certificate) == 5 and all(type(v) is int for v in certificate),
            "five exact integer tail parameters required")
    bases = sorted(polynomial, reverse=True)
    B, c, b, C, N = certificate
    actual = (bases[0], polynomial[bases[0]], bases[1],
              sum(abs(polynomial[z]) for z in bases[1:]))
    require(actual == certificate[:4], "tail parameters differ")
    require(B > b > 0 and c > 0 and C > 0 and 4 <= N <= 256,
            "invalid tail domain")
    require(c * B**N > C * b**N, "strict tail dominance fails")


def verify_gaps(cases, nums):
    require(len(cases) == len(TAILS), "missing tail certificate")
    prefix, probes, rows = 0, 0, []
    maximum = max(certificate[4] for certificate in TAILS)
    p_by_m = {m: moments(m) for m in range(5, 2 * maximum + 2)}
    q_by_n = {n: evaluate(nums[0], n) for n in range(4, 2 * maximum + 1)}
    require(min(q_by_n.values()) > 0, "common denominator is not positive")
    for index, (s, t, f, g, polynomial) in enumerate(cases):
        certificate = TAILS[index]
        verify_tail(polynomial, certificate)
        cutoff = certificate[4]
        for n in range(4, cutoff):
            value = Fraction(evaluate(polynomial, n), q_by_n[n]**2)
            require(value == gap_value(f, g, p_by_m[n + 1]) and value > 0,
                    "finite-prefix sign or expansion differs")
            prefix += 1
        for n in (cutoff, cutoff + 1, 2 * cutoff):
            value = Fraction(evaluate(polynomial, n), q_by_n[n]**2)
            require(value == gap_value(f, g, p_by_m[n + 1]) and value > 0,
                    "tail-probe identity differs")
            probes += 1
        rows.append({"index": index, "split": [s, t], "f": f, "g": g,
                     "B_c_b_C_N": certificate, "terms": len(polynomial)})
    return rows, prefix, probes


def atom_probabilities(p):
    return tuple(sum((-1)**j * comb(5 - x.bit_count(), j) * p[x.bit_count() + j]
                     for j in range(6 - x.bit_count())) for x in range(32))


def literal_gap(left, s, right, t, atoms):
    ef = eg = joint = Fraction(0)
    for x, mass in enumerate(atoms):
        f = left >> (x & ((1 << s) - 1)) & 1
        g = right >> ((x >> s) & ((1 << t) - 1)) & 1
        ef += f * mass
        eg += g * mass
        joint += f * g * mass
    return ef * eg - joint


def verify_truth_tables(tables, coefficients):
    checks = 0
    for m in (5, 6, 8, 16):
        p = moments(m)
        atoms = atom_probabilities(p)
        require(sum(atoms) == 1 and min(atoms) >= 0, "invalid five-bit law")
        for s, t in SPLITS:
            for left, right in product(tables[s], tables[t]):
                value = literal_gap(left, s, right, t, atoms)
                require(value == gap_value(coefficients[s, left],
                                           coefficients[t, right], p) and value > 0,
                        "truth-table covariance differs")
                checks += 1
    return checks


def rejection_controls(cases):
    polynomial = cases[8][4]
    certificate = TAILS[8]
    invalid = (
        lambda: moments(4), lambda: moments(True),
        lambda: monotone_tables(5), lambda: monotone_tables(True),
        lambda: verify_tail(add((-1, polynomial)), certificate),
        lambda: verify_tail(polynomial, (*certificate[:4], 4)),
        lambda: verify_tail(polynomial, (*certificate[:3], certificate[3] - 1,
                                        certificate[4])),
        lambda: verify_tail(polynomial, (*certificate[:4], True)),
    )
    for operation in invalid:
        try:
            operation()
        except ValueError:
            continue
        raise ValueError("invalid proof input was accepted")
    atoms = (Fraction(1, 2),) + (Fraction(0),) * 30 + (Fraction(1, 2),)
    require(literal_gap(2, 1, 2, 1, atoms) == -Fraction(1, 4),
            "positive-covariance distribution control was missed")
    exact = moments(5)[1]
    require(exact != Fraction(3**4, 2**4 * 2**5), "finite-GL control ineffective")
    return len(invalid) + 2


def main():
    nums = numerators()
    tables, coefficients, cases, labelled = classify(nums)
    rows, prefix, probes = verify_gaps(cases, nums)
    truth_checks = verify_truth_tables(tables, coefficients)
    controls = rejection_controls(cases)
    package = Path(__file__).resolve().parent
    receipt = {"python": platform.python_version(),
               "sha256": {name: sha256((package / name).read_bytes()).hexdigest()
                          for name in PACKAGE_FILES}}
    result = {"claim_type": "scoped proof with exact finite component",
              "claim": "strict negative association for every integer m >= 5",
              "monotone_functions": [len(tables[s]) for s in range(1, 5)],
              "labelled_cases": labelled, "distinct_gaps": len(rows),
              "prefix_checks": prefix, "tail_probes": probes,
              "truth_table_checks": truth_checks, "rejection_controls": controls,
              "tails": rows, "receipt": receipt, "new_kappa": False}
    print("PASS_CORANKONE_FIVE_NEGATIVE_ASSOCIATION")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
