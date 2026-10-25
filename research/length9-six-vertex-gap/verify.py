#!/usr/bin/env python3
"""Six-vertex far directions vanish together only below diagonal dominance."""

from fractions import Fraction
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NOTE = ROOT / "research/unconditional-batched-crt/INVERSE-CONDITIONING.md"
NOTE_SHA = "be3e4b729481b15a5ccc286b297908e4f9cef94c0c9144a28ee1cf58950d142a"
SIZE = 9
WIDTH = 2
OFF = Fraction(1, 8)
KILL = [0, 1, 2, 3, 4, 5]
GAP_BOUND = Fraction(5, 8)
DIAGONAL_ROOTS = {
    0: Fraction(3821, 116272),
    1: Fraction(5773, 118224),
    2: Fraction(8653, 121104),
}
DIAGONAL_DETERMINANTS = {
    0: Fraction(-4020911, 952500224),
    1: Fraction(-117719, 13451264),
    2: Fraction(-46665, 6889472),
}


def invert(matrix):
    size = len(matrix)
    work = [row[:] + [Fraction(int(i == j)) for j in range(size)]
            for i, row in enumerate(matrix)]
    for col in range(size):
        pivot = max(range(col, size), key=lambda row: abs(work[row][col]))
        if work[pivot][col] == 0:
            raise ZeroDivisionError("singular")
        work[col], work[pivot] = work[pivot], work[col]
        scale = work[col][col]
        work[col] = [entry / scale for entry in work[col]]
        for row in range(size):
            if row == col or work[row][col] == 0:
                continue
            factor = work[row][col]
            work[row] = [work[row][j] - factor * work[col][j] for j in range(2 * size)]
    return [row[size:] for row in work]


def norm_inf(matrix):
    return max(sum(abs(entry) for entry in row) for row in matrix)


def norm_1(matrix):
    size = len(matrix)
    return max(sum(abs(matrix[i][j]) for i in range(size)) for j in range(size))


def circular(i, j):
    gap = abs(i - j)
    return min(gap, SIZE - gap)


def determinant(matrix):
    size = len(matrix)
    work = [row[:] for row in matrix]
    sign = 1
    product = Fraction(1)
    for col in range(size):
        pivot = next(row for row in range(col, size) if work[row][col] != 0)
        if pivot != col:
            work[col], work[pivot] = work[pivot], work[col]
            sign = -sign
        product *= work[col][col]
        scale = 1 / work[col][col]
        for row in range(col + 1, size):
            if work[row][col] == 0:
                continue
            factor = work[row][col] * scale
            for index in range(col, size):
                work[row][index] -= factor * work[col][index]
    return sign * product


def host(row, col, value):
    matrix = [[Fraction(0) for _ in range(SIZE)] for _ in range(SIZE)]
    for i in range(SIZE):
        matrix[i][i] = Fraction(1)
        for j in range(SIZE):
            if i != j and circular(i, j) <= WIDTH:
                matrix[i][j] = -OFF
    matrix[row][col] = Fraction(value)
    return matrix


def schur(matrix):
    killed = set(KILL)
    keep = [index for index in range(SIZE) if index not in killed]
    pivot = [[matrix[i][j] for j in KILL] for i in KILL]
    right = [[matrix[i][j] for j in keep] for i in KILL]
    left = [[matrix[i][j] for j in KILL] for i in keep]
    body = [[matrix[i][j] for j in keep] for i in keep]
    pivot_inverse = invert(pivot)
    width = len(KILL)
    height = len(keep)
    mixed = [[sum(left[i][t] * pivot_inverse[t][s] for t in range(width))
              for s in range(width)] for i in range(height)]
    update = [[sum(mixed[i][s] * right[s][j] for s in range(width))
               for j in range(height)] for i in range(height)]
    complement = [[body[i][j] - update[i][j] for j in range(height)]
                  for i in range(height)]
    return keep, complement, determinant(pivot)


def far_numerators(row, col, value):
    matrix = host(row, col, value)
    keep, complement, width = schur(matrix)
    forward = complement[keep.index(6)][keep.index(8)] * width
    reverse = complement[keep.index(8)][keep.index(6)] * width
    return forward, reverse


def affine(row, col):
    zero = far_numerators(row, col, 0)
    one = far_numerators(row, col, 1)
    two = far_numerators(row, col, 2)
    slopes = (one[0] - zero[0], one[1] - zero[1])
    assert two[0] == zero[0] + 2 * slopes[0]
    assert two[1] == zero[1] + 2 * slopes[1]
    roots = []
    for constant, slope in zip(zero, slopes):
        if slope == 0:
            assert constant != 0
            roots.append(None)
        else:
            roots.append(-constant / slope)
    return zero, slopes, tuple(roots)


def circular_bandwidth(indices, matrix):
    found = 0
    for i, first in enumerate(indices):
        for j, second in enumerate(indices):
            if i != j and matrix[i][j] != 0:
                found = max(found, circular(first, second))
    return found


def row_gap(matrix):
    return max(sum(abs(matrix[i][j]) for j in range(SIZE) if j != i)
               for i in range(SIZE))


def main():
    note = NOTE.read_text(encoding="utf-8")
    assert hashlib.sha256(NOTE.read_bytes()).hexdigest() == NOTE_SHA
    assert "rho < 1" in note

    constants, slopes, roots = affine(1, 2)
    assert constants == (Fraction(-114917, 1048576), Fraction(-114521, 1048576))
    assert slopes == (Fraction(-1233, 65536), Fraction(-1035, 65536))
    assert roots == (Fraction(-114917, 19728), Fraction(-114521, 16560))
    assert roots[0] < 0 and roots[1] < 0

    for index, root in DIAGONAL_ROOTS.items():
        pair = affine(index, index)
        assert pair[0][0] == pair[0][1]
        assert pair[1][0] == pair[1][1]
        assert pair[2] == (root, root)
        assert root < Fraction(1, 2)
        mirror = 5 - index
        assert affine(mirror, mirror)[2] == (root, root)
        matrix = host(index, index, root)
        assert row_gap(matrix) == Fraction(1, 2)
        keep, complement, width = schur(matrix)
        assert width == DIAGONAL_DETERMINANTS[index]
        assert width != 0
        assert complement[keep.index(6)][keep.index(8)] == 0
        assert complement[keep.index(8)][keep.index(6)] == 0
        assert circular_bandwidth(keep, complement) == 1
        mirror_matrix = host(mirror, mirror, root)
        assert schur(mirror_matrix)[2] == width

    matrix = host(0, 0, DIAGONAL_ROOTS[0])
    keep, complement, width = schur(matrix)
    assert (Fraction(1, 2) / DIAGONAL_ROOTS[0]) == Fraction(58136, 3821)
    assert complement[keep.index(6)][keep.index(7)] == Fraction(-1095, 33128)
    assert complement[keep.index(7)][keep.index(8)] == Fraction(14169, 3884)
    complement_inverse = invert(complement)
    assert norm_1(complement_inverse) == Fraction(3986274320, 3731061379)
    assert norm_inf(complement_inverse) == Fraction(3986274320, 3731061379)
    inverse = invert(matrix)
    block = [[inverse[row][col] for col in keep] for row in keep]
    assert block == complement_inverse

    for row in KILL:
        for col in KILL:
            pair_roots = affine(row, col)[2]
            for root in pair_roots:
                if root is None or root <= 0:
                    continue
                if row == col:
                    assert root < Fraction(1, 2)
                else:
                    assert root > GAP_BOUND
            if pair_roots[0] == pair_roots[1] and pair_roots[0] is not None:
                if pair_roots[0] > 0:
                    assert row == col
    print("PASS length9-six-vertex-gap")


if __name__ == "__main__":
    main()
