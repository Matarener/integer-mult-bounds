#!/usr/bin/env python3
"""Exact finite corroboration for the binary completion theorem.

Produced by Nick Petalas. Apache-2.0.
No predecessor verifier, external package, network or subprocess is used.
"""
import argparse
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import platform


MODELS = ((1, 0b11), (2, 0b111), (3, 0b1011), (4, 0b10011))
PACKAGE_FILES = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def multiply(a, b, n, polynomial):
    result = 0
    for _ in range(n):
        if b & 1:
            result ^= a
        b >>= 1
        a <<= 1
        if a & (1 << n):
            a ^= polynomial
    return result


def trace(a, n, polynomial):
    result = 0
    for _ in range(n):
        result ^= a
        a = multiply(a, a, n, polynomial)
    require(result in (0, 1), "trace is not binary")
    return result


def pairing(a, b, n, polynomial):
    mask = (1 << n) - 1
    cross = multiply(a & mask, b >> n, n, polynomial)
    cross ^= multiply(b & mask, a >> n, n, polynomial)
    return trace(cross, n, polynomial)


def validate_model(n, polynomial):
    size = 1 << n
    # A multiplication permutation for each nonzero element certifies the field.
    for a in range(1, size):
        require({multiply(a, b, n, polynomial) for b in range(size)}
                == set(range(size)), "nonfield model")
    for a in range(1, size * size):
        require(pairing(a, a, n, polynomial) == 0, "nonalternating model")
        require(any(pairing(a, b, n, polynomial) for b in range(size * size)),
                "degenerate model")


def is_lagrangian(points, n, polynomial):
    if len(points) != (1 << n) - 1 or 0 in points:
        return False
    space = points | {0}
    return (all((a ^ b) in space for a in space for b in space)
            and all(pairing(a, b, n, polynomial) == 0
                    for a in points for b in points))


def validate_spread(old, n, polynomial):
    require(1 <= n <= 4, "dimension outside finite verifier bounds")
    require(len(old) == (1 << n) - 1, "wrong deficiency")
    used = set()
    for line in old:
        require(all(isinstance(x, int) and 0 < x < (1 << (2 * n)) for x in line),
                "point outside ambient space")
        require(is_lagrangian(line, n, polynomial), "non-Lagrangian member")
        require(not used.intersection(line), "overlapping members")
        used.update(line)
    holes = tuple(sorted(set(range(1, 1 << (2 * n))) - used))
    require(len(holes) == 2 * ((1 << n) - 1), "wrong hole count")
    return holes


def field_puncture(n, polynomial):
    return tuple(frozenset(x | (multiply(slope, x, n, polynomial) << n)
                           for x in range(1, 1 << n))
                 for slope in range(1, 1 << n))


def hole_adjacency(holes, n, polynomial):
    return [[pairing(a, b, n, polynomial) for b in holes] for a in holes]


def signless(adjacency):
    size = len(adjacency)
    require(1 <= size <= 30, "matrix outside finite verifier bounds")
    require(all(len(row) == size for row in adjacency), "nonsquare adjacency")
    degrees = [sum(row) for row in adjacency]
    require(min(degrees) > 0 and len(set(degrees)) == 1, "not positive regular")
    require(all(adjacency[i][i] == 0 for i in range(size)), "loop")
    require(all(adjacency[i][j] in (0, 1)
                and adjacency[i][j] == adjacency[j][i]
                for i in range(size) for j in range(size)), "not simple symmetric")
    return [[adjacency[i][j] + (degrees[i] if i == j else 0)
             for j in range(size)] for i in range(size)]


def kernel(matrix):
    """Rational RREF, with a directly substituted basis for every free column."""
    size = len(matrix)
    require(1 <= size <= 30 and all(len(row) == size for row in matrix),
            "kernel matrix outside bounds")
    work = [list(map(Fraction, row)) for row in matrix]
    pivots = []
    for column in range(size):
        row = next((r for r in range(len(pivots), size) if work[r][column]), None)
        if row is None:
            continue
        target = len(pivots)
        work[target], work[row] = work[row], work[target]
        scale = work[target][column]
        work[target] = [v / scale for v in work[target]]
        for r in range(size):
            if r != target:
                scale = work[r][column]
                work[r] = [a - scale * b for a, b in zip(work[r], work[target])]
        pivots.append(column)
    basis = []
    for column in range(size):
        if column not in pivots:
            vector = [Fraction(i == column) for i in range(size)]
            for row, pivot in enumerate(pivots):
                vector[pivot] = -work[row][column]
            require(all(sum(a * b for a, b in zip(row, vector)) == 0
                        for row in matrix), "bad kernel substitution")
            basis.append(vector)
    return basis


def determinant(matrix):
    """Integer Bareiss elimination, separate from the rational kernel engine."""
    size = len(matrix)
    require(1 <= size <= 30 and all(len(row) == size for row in matrix),
            "determinant matrix outside bounds")
    work = [row[:] for row in matrix]
    previous, sign = 1, 1
    for column in range(size - 1):
        row = next((r for r in range(column, size) if work[r][column]), None)
        if row is None:
            return 0
        if row != column:
            work[column], work[row] = work[row], work[column]
            sign = -sign
        pivot = work[column][column]
        for r in range(column + 1, size):
            for c in range(column + 1, size):
                numerator = work[r][c] * pivot - work[r][column] * work[column][c]
                require(numerator % previous == 0, "inexact Bareiss division")
                work[r][c] = numerator // previous
            work[r][column] = 0
        previous = pivot
    return sign * work[-1][-1]


def candidates_in_holes(holes, n, polynomial):
    """Enumerate closed isotropic spans, independently of the graph spectrum."""
    require(len(holes) <= 30, "hole inventory outside enumeration bound")
    allowed = frozenset(holes) | {0}
    spaces = {frozenset({0})}
    for _ in range(n):
        extended = set()
        for space in spaces:
            for point in holes:
                if point in space:
                    continue
                if any(pairing(point, x, n, polynomial) for x in space):
                    continue
                bigger = space | frozenset(x ^ point for x in space)
                if bigger <= allowed and bigger not in extended:
                    require(len(extended) < 4096, "isotropic-span capacity exceeded")
                    extended.add(bigger)
        spaces = extended
    return tuple(sorted((space - {0} for space in spaces), key=lambda s: sorted(s)))


def check_fixture(n, polynomial):
    validate_model(n, polynomial)
    old = field_puncture(n, polynomial)
    holes = validate_spread(old, n, polynomial)
    adjacency = hole_adjacency(holes, n, polynomial)
    degree = 1 << (n - 1)
    require(all(sum(row) == degree for row in adjacency), "wrong hole degree")
    matrix = signless(adjacency)
    basis = kernel(matrix)
    require(determinant(matrix) == 0 and len(basis) == 1, "wrong spectral decision")
    vector = basis[0]
    require(all(abs(v) == 1 for v in vector), "nonconstant kernel magnitude")
    recovered = frozenset(frozenset(h for h, v in zip(holes, vector) if v * sign > 0)
                          for sign in (-1, 1))
    require(len(recovered) == 2, "missing color class")
    require(all(is_lagrangian(s, n, polynomial) for s in recovered), "bad recovery")
    candidates = candidates_in_holes(holes, n, polynomial)
    completions = [frozenset((a, b)) for a, b in combinations(candidates, 2)
                   if not a.intersection(b)]
    require(completions == [recovered], "independent completion search disagrees")
    expected = frozenset((frozenset(range(1, 1 << n)),
                          frozenset(y << n for y in range(1, 1 << n))))
    require(recovered == expected, "wrong missing subspaces")
    return {"n": n, "old_members": len(old), "holes": len(holes), "degree": degree,
            "rank_Q": len(holes) - len(basis), "det_Q": 0,
            "candidate_lagrangians": len(candidates), "completion_pairs": len(completions)}


def expect_rejection(operation, message):
    try:
        operation()
    except ValueError as exc:
        require(str(exc) == message, "unexpected rejection: " + str(exc))
    else:
        raise ValueError("invalid input accepted: " + message)


def check_controls():
    n, polynomial = MODELS[1]
    old = field_puncture(n, polynomial)
    expect_rejection(lambda: validate_spread(old[:-1], n, polynomial), "wrong deficiency")
    expect_rejection(lambda: validate_spread((old[0], old[0], old[2]), n, polynomial),
                     "overlapping members")
    invalid = frozenset((1, 8, 9))
    expect_rejection(lambda: validate_spread((invalid, old[1], old[2]), n, polynomial),
                     "non-Lagrangian member")
    # K4,4 disjoint (K6 minus a perfect matching). Same N=14,k=4 as n=3.
    mixed = [[int((i < 4 <= j < 8 or j < 4 <= i < 8)
                  or (i >= 8 and j >= 8 and (i - 8) // 2 != (j - 8) // 2))
              for j in range(14)] for i in range(14)]
    mixed_kernel = kernel(signless(mixed))
    require(len(mixed_kernel) == 1 and determinant(signless(mixed)) == 0,
            "mixed abstract graph must be singular")
    require(sum(v == 0 for v in mixed_kernel[0]) == 6, "mixed kernel zero support")
    # The connected circulant with steps +/-1,+/-2 has a triangle.
    nonbipartite = [[int((i - j) % 14 in (1, 2, 12, 13))
                    for j in range(14)] for i in range(14)]
    nonsingular = signless(nonbipartite)
    det = determinant(nonsingular)
    require(not kernel(nonsingular) and det > 0, "odd-cycle graph must be nonsingular")
    return {"invalid_spreads_rejected": 3, "mixed_graph_vertices": 14,
            "mixed_graph_degree": 4, "mixed_graph_kernel_zeros": 6,
            "nonbipartite_graph_det_Q": det}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    package = Path(__file__).resolve().parent
    if args.receipt and args.receipt.resolve().is_relative_to(package.parents[1]):
        parser.error("receipt must be outside the checkout")
    result = {"status": "PASS_SYMPLECTIC_BINARY_COMPLETION",
              "fixtures": [check_fixture(n, p) for n, p in MODELS],
              "controls": check_controls()}
    print(json.dumps(result, sort_keys=True))
    if args.receipt:
        receipt = {"result": result, "python": platform.python_version(),
                   "files_sha256": {name: sha256((package / name).read_bytes()).hexdigest()
                                    for name in PACKAGE_FILES}}
        payload = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
        require(args.receipt.write_text(payload) == len(payload), "short receipt write")


if __name__ == "__main__":
    main()
