#!/usr/bin/env python3
"""The five-vertex far numerators do not share a positive root."""

from fractions import Fraction
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NOTE = ROOT / "research/unconditional-batched-crt/INVERSE-CONDITIONING.md"
NOTE_SHA = "be3e4b729481b15a5ccc286b297908e4f9cef94c0c9144a28ee1cf58950d142a"
SIZE = 9
WIDTH = 2
OFF = Fraction(1, 8)
KILL = [0, 1, 2, 3, 4]
INSIDE = Fraction(809, 1296)
OUTSIDE = Fraction(481, 36)
GAP_BOUND = Fraction(5, 8)


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
    forward = complement[keep.index(5)][keep.index(8)] * width
    reverse = complement[keep.index(8)][keep.index(5)] * width
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
            if matrix[i][j] != 0:
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
    assert constants == (Fraction(-481, 131072), Fraction(-809, 262144))
    assert slopes == (Fraction(9, 32768), Fraction(81, 16384))
    assert roots == (OUTSIDE, INSIDE)
    assert GAP_BOUND - INSIDE == Fraction(1, 1296)
    assert INSIDE > 0

    endpoint = affine(0, 1)[2]
    assert endpoint == (Fraction(953, 144), Fraction(881, 720))
    assert endpoint[0] > GAP_BOUND and endpoint[1] > GAP_BOUND

    matrix = host(1, 2, INSIDE)
    assert row_gap(matrix) == Fraction(3, 8) + INSIDE == Fraction(1295, 1296)
    keep, complement, width = schur(matrix)
    assert width == Fraction(587809, 589824)
    assert complement[keep.index(8)][keep.index(5)] == 0
    assert complement[keep.index(5)][keep.index(8)] == Fraction(-971, 276616)
    assert circular_bandwidth(keep, complement) == 3
    complement_inverse = invert(complement)
    rho = row_gap(matrix)
    delta = 1 - rho
    infinity_bound = 1 / delta
    one_bound = infinity_bound + 2 * WIDTH * rho / delta ** 2
    assert infinity_bound == 1296
    assert one_bound == 6714576
    assert norm_1(complement_inverse) == Fraction(419112, 257177)
    assert norm_inf(complement_inverse) == Fraction(1022468068, 626225995)
    assert norm_1(complement_inverse) <= one_bound
    assert norm_inf(complement_inverse) <= infinity_bound
    inverse = invert(matrix)
    block = [[inverse[row][col] for col in keep] for row in keep]
    assert block == complement_inverse

    for row in KILL:
        for col in KILL:
            pair_roots = affine(row, col)[2]
            if pair_roots[0] != pair_roots[1]:
                continue
            assert pair_roots[0] is None or pair_roots[0] <= 0
    print("PASS length9-five-vertex-gap")


if __name__ == "__main__":
    main()
