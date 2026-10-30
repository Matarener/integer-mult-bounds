#!/usr/bin/env python3
"""Enumerate new input/output reductions and exact certificate controls."""

import hashlib
import itertools
import json
import platform
import sys
from dataclasses import replace
from fractions import Fraction
from pathlib import Path

from model import (Divergent, Finite, Zero, certify, check, closure_relevant,
                   dot, identity_minus, multiply, require, restrict)


def matrix(rows):
    return tuple(tuple(Fraction(value) for value in row) for row in rows)


def vector(values):
    return tuple(Fraction(value) for value in values)


def determinant(rows):
    """Independent permutation formula, only used for orders at most three."""
    size = len(rows)
    require(size <= 3, "determinant oracle capacity")
    result = Fraction(0)
    for permutation in itertools.permutations(range(size)):
        inversions = sum(permutation[i] > permutation[j]
                         for i in range(size) for j in range(i + 1, size))
        term = Fraction((-1) ** inversions)
        for i in range(size):
            term *= rows[i][permutation[i]]
        result += term
    return result


def finite_oracle(a, b, c):
    kept = closure_relevant(a, b, c)
    reduced, _ = restrict(a, b, kept)
    m = identity_minus(reduced)
    for mask in range(1, 1 << len(kept)):
        indices = tuple(i for i in range(len(kept)) if mask & (1 << i))
        minor = tuple(tuple(m[i][j] for j in indices) for i in indices)
        if determinant(minor) <= 0:
            return False
    return True


def cramer_total(a, b, c, cert):
    reduced, beta = restrict(a, b, cert.retained)
    gamma = tuple(c[i] for i in cert.retained)
    m = identity_minus(reduced)
    denominator = determinant(m)
    values = []
    for column in range(len(m)):
        replaced = tuple(tuple(beta[i] if j == column else m[i][j]
                               for j in range(len(m))) for i in range(len(m)))
        values.append(determinant(replaced) / denominator)
    require(dot(gamma, tuple(values)) == dot(gamma, cert.total), "Cramer total")


def path_and_prefix_checks(a, b, c, cert):
    reduced, term = restrict(a, b, cert.retained)
    gamma = tuple(c[i] for i in cert.retained)
    full = b
    prefix = Fraction(0)
    for depth in range(7):
        value = dot(c, full)
        require(value == dot(gamma, term), "literal path reduction")
        prefix += value
        if isinstance(cert, Divergent):
            require(prefix >= ((depth + 1) // len(cert.retained)) * cert.block_gain,
                    "exhaustive finite-depth lower bound")
        elif isinstance(cert, Finite):
            require(prefix <= dot(gamma, cert.total), "observed finite prefix")
        full = multiply(a, full)
        term = multiply(reduced, term)


def census(size, alphabet):
    require(size in (2, 3) and 1 <= len(alphabet) <= 4, "census capacity")
    counts = {"zero": 0, "finite": 0, "divergent": 0}
    masks = tuple(vector((mask >> i) & 1 for i in range(size))
                  for mask in range(1 << size))
    for entries in itertools.product(alphabet, repeat=size * size):
        a = matrix(tuple(entries[size * i:size * (i + 1)] for i in range(size)))
        for b, c in itertools.product(masks, repeat=2):
            cert = certify(a, b, c)
            check(a, b, c, cert)
            path_and_prefix_checks(a, b, c, cert)
            finite = finite_oracle(a, b, c)
            require(finite == (not isinstance(cert, Divergent)), "minor oracle")
            if isinstance(cert, Zero):
                counts["zero"] += 1
            elif isinstance(cert, Finite):
                cramer_total(a, b, c, cert)
                counts["finite"] += 1
            else:
                counts["divergent"] += 1
    require(sum(counts.values()) == len(alphabet) ** (size * size) * 4 ** size,
            "exhaustive census size")
    return counts


def partial(a, b, c, depth):
    term = b
    total = Fraction(0)
    for _ in range(depth):
        total += dot(c, term)
        term = multiply(a, term)
    return total


def examples():
    fixtures = (
        (matrix(((Fraction(1, 2), 0), (0, 2))), vector((1, 1)), vector((1, 0))),
        (matrix(((2, 0), (0, Fraction(1, 2)))), vector((0, 1)), vector((1, 1))),
        (matrix(((0, 0, 0), (1, 1, 0), (0, 1, 0))), vector((1, 0, 0)), vector((0, 0, 1))),
        (matrix(((0, 0), (1, 0))), vector((1, 0)), vector((0, 1))),
    )
    for index, (a, b, c) in enumerate(fixtures):
        cert = certify(a, b, c)
        check(a, b, c, cert)
        if index < 2:
            require(isinstance(cert, Finite), "irrelevant unstable component")
            require(len(cert.retained) == 1 and dot(vector((1,)), cert.total) == 2,
                    "exact observed total two")
        for depth in range(25):
            observed = partial(a, b, c, depth)
            if isinstance(cert, Divergent):
                require(observed >= (depth // len(cert.retained)) * cert.block_gain,
                        "divergence bound")
            elif isinstance(cert, Finite):
                reduced, beta = restrict(a, b, cert.retained)
                gamma = tuple(c[i] for i in cert.retained)
                tail_vector = cert.total
                for _ in range(depth):
                    tail_vector = multiply(reduced, tail_vector)
                tail = dot(gamma, cert.total) - observed
                require(tail == dot(gamma, tail_vector), "exact tail identity")
                alpha = max(x / y for x, y in zip(cert.total, cert.weights))
                require(tail <= alpha * cert.ratio ** depth * dot(gamma, cert.weights),
                        "geometric tail bound")
    return len(fixtures)


def cycles():
    checked = 0
    for size in range(1, 9):
        a = matrix(tuple(tuple(int(i == (j + 1) % size) for j in range(size))
                         for i in range(size)))
        b = vector(int(i == 0) for i in range(size))
        c = vector(int(i == size - 1) for i in range(size))
        cert = certify(a, b, c)
        check(a, b, c, cert)
        require(isinstance(cert, Divergent) and cert.block_gain == 1,
                "critical cycle block gain")
        for depth in range(4 * size + 1):
            require(partial(a, b, c, depth) == depth // size,
                    "sharp all-depth cycle formula")
            checked += 1
    return {"cycles": 8, "depths": checked}


def rejected(call):
    try:
        call()
    except ValueError:
        return
    raise ValueError("forged certificate or invalid input accepted")


def controls():
    a = matrix(((Fraction(1, 2), 0), (0, 2)))
    b, c = vector((1, 1)), vector((1, 0))
    finite = certify(a, b, c)
    require(isinstance(finite, Finite), "finite control fixture")
    forged = (
        Zero(), replace(finite, retained=(0, 1)),
        replace(finite, weights=vector((0,))),
        replace(finite, total=vector((3,))),
        replace(finite, ratio=Fraction(1)),
        replace(finite, ratio=Fraction(0)),
        replace(finite, total=vector((-1,))),
    )
    for cert in forged:
        rejected(lambda: check(a, b, c, cert))
    d = matrix(((0, 0, 0), (1, 1, 0), (0, 1, 0)))
    db, dc = vector((1, 0, 0)), vector((0, 0, 1))
    divergent = certify(d, db, dc)
    require(isinstance(divergent, Divergent), "divergent control fixture")
    false = (
        replace(divergent, witness=vector((0, 0, 0))),
        replace(divergent, witness=vector((0, -1, 1))),
        replace(divergent, witness=vector((0, 1, 0))),
        replace(divergent, witness=vector((0, 0, 1))),
        replace(divergent, block_gain=2 * divergent.block_gain),
    )
    for cert in false:
        rejected(lambda: check(d, db, dc, cert))
    rejected(lambda: certify(matrix(((-1,),)), vector((1,)), vector((1,))))
    rejected(lambda: certify(matrix(((0,),)), vector((1, 0)), vector((1,))))
    rejected(lambda: certify(matrix(((2 ** 16,),)), vector((1,)), vector((1,))))
    rejected(lambda: certify(matrix(((0,) * 9,) * 9), vector((0,) * 9), vector((0,) * 9)))
    return {"certificate_mutants": len(forged) + len(false), "input_rejections": 4}


def main():
    require(sys.version_info[:2] == (3, 12), "registered CPython 3.12 required")
    result = {
        "status": "PASS_OBSERVABLE_FORCED_RECURRENCE",
        "claim_type": "scoped proof with exact finite corroboration",
        "python": platform.python_version(),
        "two_type_rational_census": census(2, (0, Fraction(1, 2), 1, 2)),
        "three_type_binary_census": census(3, (0, 1)),
        "tail_and_hidden_component_fixtures": examples(),
        "sharpness": cycles(),
        "controls": controls(),
    }
    package = Path(__file__).resolve().parent
    result["files_sha256"] = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                              for path in sorted(package.iterdir()) if path.is_file()}
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
