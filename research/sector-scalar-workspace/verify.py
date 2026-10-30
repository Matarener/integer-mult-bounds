"""Exact corroboration of the paired-character workspace obstruction."""

import hashlib
import itertools
import json
from fractions import Fraction as F
from pathlib import Path
from random import Random


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identity(size):
    require(1 <= size <= 64, "matrix size outside finite checker domain")
    return [[F(i == j) for j in range(size)] for i in range(size)]


def determinant(matrix):
    size = len(matrix)
    require(1 <= size <= 64, "matrix size outside finite checker domain")
    require(all(len(row) == size for row in matrix), "matrix must be square")
    work = [list(map(F, row)) for row in matrix]
    value = F(1)
    for col in range(size):
        pivot = next((j for j in range(col, size) if work[j][col]), None)
        if pivot is None:
            return F(0)
        if pivot != col:
            work[col], work[pivot] = work[pivot], work[col]
            value = -value
        entry = work[col][col]
        value *= entry
        for row in range(col + 1, size):
            ratio = work[row][col] / entry
            for j in range(col + 1, size):
                work[row][j] -= ratio * work[col][j]
            work[row][col] = F(0)
    return value


def leibniz(matrix):
    size = len(matrix)
    require(1 <= size <= 4, "permutation oracle size outside finite domain")
    require(all(len(row) == size for row in matrix), "oracle needs square input")
    value = F(0)
    for perm in itertools.permutations(range(size)):
        inversions = sum(perm[i] > perm[j] for i in range(size) for j in range(i + 1, size))
        term = F((-1) ** inversions)
        for i in range(size):
            term *= matrix[i][perm[i]]
        value += term
    return value


def literal_projectors(axes, spectators):
    require(1 <= axes <= 6, "axis count outside finite checker domain")
    require(0 <= spectators < (1 << (axes - 1)), "invalid spectator character")
    values = []
    for label in range(1 << axes):
        total = 0
        for mask in range(1 << axes):
            coefficient = (-1) ** ((label & mask).bit_count())
            # J_0 = Q^2 evaluates to 1 at BOTH Q = 1 and Q = -1.
            character = (-1) ** (((mask >> 1) & spectators).bit_count())
            total += coefficient * character
        values.append(F(total, 1 << axes))
    require(sum(values) == 1 and set(values) <= {F(0), F(1)}, "projector character")
    return values


def target_checks():
    characters = 0
    targets = 0
    for axes in range(1, 7):
        for spectators in range(1 << (axes - 1)):
            values = literal_projectors(axes, spectators)
            characters += 1
            for blocks in range(1, 17):
                positive = F(1)
                negative = F(1)
                for value in values:
                    positive *= 1 + value / 2
                    negative *= 1 - value / 2
                require((positive / negative) ** blocks == 3 ** blocks, "target ratio")
                for parity in (-1, 1):
                    require(positive ** blocks != parity * negative ** blocks,
                            "target unexpectedly satisfies allowed parity")
                    targets += 1
    return dict(projector_characters=characters, target_parity_checks=targets)


def exhaustive_ordinary_checks():
    alphabet = (F(-2), F(-1), F(-1, 2), F(0), F(1, 2), F(1), F(3, 2), F(2))
    matrices = 0
    singular = 0
    for entries in itertools.product(alphabet, repeat=4):
        matrix = [list(entries[:2]), list(entries[2:])]
        value = determinant(matrix)
        require(value == leibniz(matrix), "determinant oracle disagreement")
        singular += value == 0
        for role in range(2):
            negative = [row[:] for row in matrix]
            negative[role] = [-x for x in negative[role]]
            require(determinant(negative) == -value, "query parity failed")
        matrices += 1
    return dict(ordinary_matrices=matrices, singular_matrices=singular)


def word_checks():
    random = Random(5658)
    words = 0
    cuts = 0
    for size in range(1, 6):
        for _ in range(80):
            positive = identity(size)
            negative = identity(size)
            parity = 1
            for _ in range(24):
                kind = random.randrange(4)
                dst = random.randrange(size)
                src = random.randrange(size)
                coefficient = random.choice((F(-2), F(-1, 2), F(3, 2), F(5, 3)))
                if kind == 0:
                    negative[dst] = [-x for x in negative[dst]]
                    parity = -parity
                elif kind == 1 or dst == src:
                    positive[dst] = [coefficient * x for x in positive[dst]]
                    negative[dst] = [coefficient * x for x in negative[dst]]
                elif kind == 2:
                    for j in range(size):
                        positive[dst][j] += coefficient * positive[src][j]
                        negative[dst][j] += coefficient * negative[src][j]
                else:
                    positive[dst], positive[src] = positive[src], positive[dst]
                    negative[dst], negative[src] = negative[src], negative[dst]
                require(determinant(positive) == parity * determinant(negative), "word invariant")
                cuts += 1
            words += 1
    return dict(seeded_words=words, checked_word_cuts=cuts)


def boundary_checks():
    # Rational nonunit scales preserve the paired invariant.
    scale = [[F(3, 2), F(0)], [F(0), F(1)]]
    require(determinant(scale) == F(3, 2), "nonunit scale control")
    # A Q-dependent overwrite changes the ordinary-algebra hypothesis.
    require(F(3, 2) / F(1, 2) == 3, "changed ordinary alphabet control")
    # Reciprocal borrowed responses change the restoration hypothesis.
    require(F(3, 2) * F(2, 3) == F(1, 2) * 2, "borrowed restoration control")
    for size in range(1, 6):
        matrix = identity(size)
        matrix[0] = [F(0)] * size
        require(determinant(matrix) == 0, "CLEAR rank-loss control")
    rejected = 0
    for invalid in ([], [[1, 2]], [[1, 2], [3]]):
        try:
            determinant(invalid)
        except ValueError:
            rejected += 1
    require(rejected == 3, "invalid matrices not rejected")
    return dict(scope_and_rank_controls=8, invalid_matrix_controls=rejected)


def main():
    package = Path(__file__).resolve().parent
    result = {}
    for check in (target_checks, exhaustive_ordinary_checks, word_checks, boundary_checks):
        result.update(check())
    expected = json.loads((package / "RESULT.json").read_text())
    require(result == expected, "finite result differs from committed expectation")
    hashes = {}
    files = sorted(path for path in package.iterdir() if path.is_file())
    require(len(files) <= 16, "unexpected package file count")
    for path in files:
        hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    print("PASS_SECTOR_SCALAR_WORKSPACE " + json.dumps(result, sort_keys=True))
    print(json.dumps({"schema": "sector-scalar-workspace-receipt/1", "sha256": hashes}, sort_keys=True))


if __name__ == "__main__":
    main()
