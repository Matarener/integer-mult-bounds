#!/usr/bin/env python3
"""Exact bounded corroboration of the restricted Fourier-input theorem."""

from fractions import Fraction
from hashlib import sha256
from itertools import permutations, product
import json
from pathlib import Path


ROOTS = ((1, 0), (0, 1), (-1, 0), (0, -1))
ZERO = (0, 0)
ONE = (1, 0)
MAX_N = 16


def require(condition, message):
    if not condition:
        raise ValueError(message)


def add(left, right):
    return (left[0] + right[0], left[1] + right[1])


def multiply(left, right):
    a, b = left
    c, d = right
    return (a * c - b * d, a * d + b * c)


def conjugate(value):
    return (value[0], -value[1])


def validate(permutation, phases):
    n = len(permutation)
    require(1 <= n <= MAX_N, "permutation size")
    require(all(type(x) is int for x in permutation), "integer addresses")
    require(sorted(permutation) == list(range(n)), "bijection")
    require(len(phases) == n, "phase count")
    require(all(x in ROOTS for x in phases), "fourth-root phase")


def cycle_basis(permutation, phases):
    """Solve g[y] = h[y] g[tau(y)] with an explicitly bounded walk."""
    validate(permutation, phases)
    n = len(permutation)
    visited = set()
    basis, cycles = [], []
    for start in range(n):
        if start in visited:
            continue
        vector = [ZERO] * n
        cycle = []
        index, value = start, ONE
        for _ in range(n):
            require(index not in visited, "cycle intersects an earlier cycle")
            visited.add(index)
            cycle.append(index)
            vector[index] = value
            value = multiply(value, conjugate(phases[index]))
            index = permutation[index]
            if index == start:
                break
        require(index == start, "cycle did not close")
        cycles.append((tuple(cycle), value == ONE))
        if value == ONE:
            basis.append(tuple(vector))
    require(len(visited) == n, "incomplete cycle cover")
    return tuple(basis), tuple(cycles)


def residual(vector, permutation, phases):
    return tuple(add(vector[y], multiply((-1, 0),
                     multiply(phases[y], vector[permutation[y]])))
                 for y in range(len(vector)))


def vanishes(vector):
    return all(value == ZERO for value in vector)


def real_matrix(permutation, phases):
    """Independent realification of I - D_h P_tau."""
    n = len(permutation)
    rows = [[0] * (2 * n) for _ in range(2 * n)]
    for y in range(n):
        rows[y][y] += 1
        rows[y + n][y + n] += 1
        a, b = phases[y]
        z = permutation[y]
        rows[y][z] -= a
        rows[y][z + n] += b
        rows[y + n][z] -= b
        rows[y + n][z + n] -= a
    return rows


def rational_rank(matrix):
    require(1 <= len(matrix) <= 2 * MAX_N, "row bound")
    width = len(matrix[0])
    require(1 <= width <= 2 * MAX_N, "column bound")
    require(all(len(row) == width for row in matrix), "rectangular matrix")
    rows = [[Fraction(x) for x in row] for row in matrix]
    rank = 0
    for column in range(width):
        pivot = next((r for r in range(rank, len(rows)) if rows[r][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        divisor = rows[rank][column]
        rows[rank] = [x / divisor for x in rows[rank]]
        for r in range(rank + 1, len(rows)):
            scalar = rows[r][column]
            rows[r] = [x - scalar * y for x, y in zip(rows[r], rows[rank])]
        rank += 1
        if rank == len(rows):
            break
    return rank


def elements(moduli):
    require(moduli in ((), (2,), (4,), (2, 2), (4, 4)), "group domain")
    return tuple(product(*(range(q) for q in moduli)))


def character(left, right, moduli, sign=1):
    exponent = sum((4 // q) * x * y for x, y, q in zip(left, right, moduli))
    return ROOTS[(sign * exponent) % 4]


def transform(vector, group, moduli, sign):
    require(len(vector) == len(group) <= MAX_N, "transform domain")
    result = []
    for x in group:
        value = ZERO
        for y, coefficient in zip(group, vector):
            value = add(value, multiply(character(x, y, moduli, sign), coefficient))
        result.append(value)
    return tuple(result)


def convolution(left, right, group, moduli):
    """Direct group addition, without any Fourier or cycle routine."""
    result = [ZERO] * len(group)
    positions = {x: i for i, x in enumerate(group)}
    for a, x in enumerate(group):
        for b, y in enumerate(group):
            z = tuple((s + t) % q for s, t, q in zip(x, y, moduli))
            i = positions[z]
            result[i] = add(result[i], multiply(left[a], right[b]))
    return tuple(result)


def convolution_identity(left, right, permutation, phases, group, moduli):
    first = transform(left, group, moduli, -1)
    second = transform(right, group, moduli, -1)
    alpha = tuple(ROOTS[y % 4] for y in range(len(group)))
    beta = tuple(multiply(h, conjugate(a)) for h, a in zip(phases, alpha))
    mixed = tuple(multiply(multiply(a, u), multiply(b, second[z]))
                  for a, b, u, z in zip(alpha, beta, first, permutation))
    actual = transform(mixed, group, moduli, 1)
    target = tuple(multiply((len(group), 0), v)
                   for v in convolution(left, right, group, moduli))
    return actual == target


def delta(n, index):
    return tuple(ONE if j == index else ZERO for j in range(n))


def check_fourier_fixture(permutation, phases, basis, moduli, counts):
    group = elements(moduli)
    n = len(group)
    for spectral in basis:
        right = transform(spectral, group, moduli, 1)
        for x in range(n):
            require(convolution_identity(delta(n, x), right, permutation,
                    phases, group, moduli), "attaining convolution basis")
            counts["convolution_basis_pairs"] += 1
        dense = tuple((y + 1, 1 - y) for y in range(n))
        require(convolution_identity(dense, right, permutation, phases,
                group, moduli), "dense first operand")
        counts["dense_first_operands"] += 1
    for x in range(n):
        spectral = delta(n, x)
        if not vanishes(residual(spectral, permutation, phases)):
            right = transform(spectral, group, moduli, 1)
            require(not convolution_identity(delta(n, 0), right, permutation,
                    phases, group, moduli), "forbidden direction must fail")
            counts["forbidden_direction_witnesses"] += 1


def exhaustive(counts):
    digest = sha256()
    groups = {1: ((),), 2: ((2,),), 4: ((4,), (2, 2))}
    for n in range(1, 5):
        for permutation in permutations(range(n)):
            for phases in product(ROOTS, repeat=n):
                basis, cycles = cycle_basis(permutation, phases)
                rank = rational_rank(real_matrix(permutation, phases))
                require(rank == 2 * (n - len(basis)), "independent rank formula")
                for vector in basis:
                    require(vanishes(residual(vector, permutation, phases)),
                            "cycle vector fails its equations")
                counts["weighted_permutations"] += 1
                counts["balanced_cycle_vectors"] += len(basis)
                counts["cycles"] += len(cycles)
                digest.update(bytes((n, *permutation, len(basis))))
                digest.update(bytes(ROOTS.index(h) for h in phases))
                for moduli in groups.get(n, ()):
                    check_fourier_fixture(permutation, phases, basis, moduli, counts)
                    counts["fourier_layouts"] += 1
    return digest.hexdigest()


def translations(counts):
    for moduli in ((2,), (4,), (2, 2), (4, 4)):
        group = elements(moduli)
        positions = {x: j for j, x in enumerate(group)}
        for shift in group:
            permutation = tuple(positions[tuple((x + b) % q
                                for x, b, q in zip(y, shift, moduli))] for y in group)
            for phase in ROOTS:
                phases = (phase,) * len(group)
                basis, _ = cycle_basis(permutation, phases)
                support = tuple(x for x in group
                                if character(shift, x, moduli) == phase)
                require(len(basis) == len(support), "translation dimension")
                for x in group:
                    time = delta(len(group), positions[x])
                    spectral = transform(time, group, moduli, -1)
                    accepted = vanishes(residual(spectral, permutation, phases))
                    require(accepted == (x in support), "character-level support")
                    counts["translation_time_columns"] += 1
                counts["translation_layouts"] += 1
    moduli = (4, 4)
    group = elements(moduli)
    permutation = tuple(group.index(((y[0] + 1) % 4, y[1])) for y in group)
    for x in group:
        if x[0] == 1:
            for u in range(len(group)):
                require(convolution_identity(delta(16, u), delta(16, group.index(x)),
                        permutation, ((0, 1),) * 16, group, moduli), "sparse example")
                counts["sparse_example_basis_pairs"] += 1


def controls(counts):
    malformed = [((0, 0), (ONE, ONE)), ((1,), (ONE,)),
                 ((True,), (ONE,)), ((), ()), ((0,), ()),
                 ((0,), ((2, 0),)), (tuple(range(17)), (ONE,) * 17)]
    for permutation, phases in malformed:
        try:
            cycle_basis(permutation, phases)
        except ValueError:
            counts["rejection_controls"] += 1
        else:
            raise ValueError("malformed boundary accepted")
    permutation = (1, 2, 0)
    basis, _ = cycle_basis(permutation, (ONE, ONE, (-1, 0)))
    require(not basis, "unbalanced cycle counted")
    basis, _ = cycle_basis(permutation, ((0, 1), (-1, 0), (0, 1)))
    require(len(basis) == 1 and len(set(basis[0])) > 1,
            "nonconstant balanced weights lost")
    require(not vanishes(residual((ONE, ONE, ONE), permutation,
                ((0, 1), (-1, 0), (0, 1)))), "constant cycle-vector mutant")
    counts["rejection_controls"] += 3


def source_hashes():
    package = Path(__file__).resolve().parent
    paths = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    result = {}
    for name in paths:
        path = package / name
        require(path.stat().st_size <= 1024 * 1024, "package file bound")
        result[name] = sha256(path.read_bytes()).hexdigest()
    manifest = json.loads((package / "SOURCES.json").read_text())
    require(len(manifest["files"]) <= 8, "source manifest bound")
    for row in manifest["files"]:
        if row["usage"] == "input":
            path = package.parents[1] / row["path"]
            require(path.stat().st_size <= 1024 * 1024, "source file bound")
            require(sha256(path.read_bytes()).hexdigest() == row["sha256"], "source drift")
    return result


def main():
    hashes = source_hashes()
    counts = dict.fromkeys(("weighted_permutations", "balanced_cycle_vectors", "cycles",
                           "fourier_layouts", "convolution_basis_pairs", "dense_first_operands",
                           "forbidden_direction_witnesses", "translation_layouts",
                           "translation_time_columns", "sparse_example_basis_pairs",
                           "rejection_controls"), 0)
    digest = exhaustive(counts)
    translations(counts)
    controls(counts)
    require(counts["weighted_permutations"] == sum(
            len(tuple(permutations(range(n)))) * 4 ** n for n in range(1, 5)),
            "exhaustive domain coverage")
    print(json.dumps({"status": "PASS_FOURIER_INPUT_DEFECT", "counts": counts,
                      "classification_sha256": digest, "package_sha256": hashes,
                      "claim_type": "scoped proof with finite corroboration"}, sort_keys=True))


if __name__ == "__main__":
    main()
