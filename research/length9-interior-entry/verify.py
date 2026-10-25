#!/usr/bin/env python3
"""No positive entry inside arc {0,1} zeros both far directions."""

from fractions import Fraction
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NOTE = ROOT / "research/unconditional-batched-crt/INVERSE-CONDITIONING.md"
NOTE_SHA = "be3e4b729481b15a5ccc286b297908e4f9cef94c0c9144a28ee1cf58950d142a"
SIZE = 9
WIDTH = 2
OFF = Fraction(1, 8)


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


def host(replacements=()):
    matrix = [[Fraction(0) for _ in range(SIZE)] for _ in range(SIZE)]
    for i in range(SIZE):
        matrix[i][i] = Fraction(1)
        for j in range(SIZE):
            if i != j and circular(i, j) <= WIDTH:
                matrix[i][j] = -OFF
    for row, col, value in replacements:
        matrix[row][col] = value
    return matrix


def schur(matrix, kill):
    kill = list(kill)
    killed = set(kill)
    keep = [index for index in range(SIZE) if index not in killed]
    pivot = [[matrix[i][j] for j in kill] for i in kill]
    right = [[matrix[i][j] for j in keep] for i in kill]
    left = [[matrix[i][j] for j in kill] for i in keep]
    body = [[matrix[i][j] for j in keep] for i in keep]
    pivot_inverse = invert(pivot)
    width = len(kill)
    height = len(keep)
    mixed = [[sum(left[i][t] * pivot_inverse[t][s] for t in range(width))
              for s in range(width)] for i in range(height)]
    update = [[sum(mixed[i][s] * right[s][j] for s in range(width))
               for j in range(height)] for i in range(height)]
    complement = [[body[i][j] - update[i][j] for j in range(height)]
                  for i in range(height)]
    return keep, complement


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


def form(adjugate, left, right):
    mixed = [sum(adjugate[row][col] * right[col] for col in range(2)) for row in range(2)]
    return sum(left[row] * mixed[row] for row in range(2))


def prove_off_diagonal():
    # H[0][1] = x and H[1][0] = -1/8. Far direct entries are zero.
    # The adjugate is [[1, -x], [1/8, 1]]. Its first column does not contain x.
    left_2 = (-OFF, -OFF)
    left_3 = (0, -OFF)
    left_7 = (-OFF, 0)
    left_8 = (-OFF, -OFF)
    toward_7 = (-OFF, -OFF * OFF)
    assert toward_7 == (-OFF * 1, -OFF * OFF)
    assert sum(left_2[row] * toward_7[row] for row in range(2)) == Fraction(9, 512)
    for value in (Fraction(0), Fraction(1), Fraction(3, 5), Fraction(-2)):
        adjugate = [[1, -value], [OFF, 1]]
        assert -form(adjugate, left_2, left_7) == Fraction(-9, 512)
        assert -form(adjugate, left_7, left_2) == (value - 1) * Fraction(1, 64)
        assert -form(adjugate, left_3, left_7) == Fraction(-1, 512)
        assert -form(adjugate, left_7, left_3) == value * Fraction(1, 64)
        assert -form(adjugate, left_3, left_8) == Fraction(-9, 512)
        assert -form(adjugate, left_8, left_3) == (value - 1) * Fraction(1, 64)
    # H[1][0] = x swaps which direction carries the factor.
    for value in (Fraction(0), Fraction(1), Fraction(3, 5)):
        adjugate = [[1, OFF], [-value, 1]]
        assert -form(adjugate, left_7, left_2) == Fraction(-9, 512)
        assert -form(adjugate, left_2, left_7) == (value - 1) * Fraction(1, 64)
        assert -form(adjugate, left_8, left_3) == Fraction(-9, 512)
        assert -form(adjugate, left_3, left_8) == (value - 1) * Fraction(1, 64)


def prove_diagonal():
    # H[0][0] = y. Pair (2,7) reads only the y-free first column.
    left_2 = (-OFF, -OFF)
    left_3 = (0, -OFF)
    left_7 = (-OFF, 0)
    left_8 = (-OFF, -OFF)
    toward_7 = (-OFF, -OFF * OFF)
    assert sum(left_2[row] * toward_7[row] for row in range(2)) == Fraction(9, 512)
    for value in (Fraction(1), Fraction(2), Fraction(-1, 8)):
        adjugate = [[1, OFF], [OFF, value]]
        assert -form(adjugate, left_2, left_7) == Fraction(-9, 512)
        assert -form(adjugate, left_7, left_2) == Fraction(-9, 512)
        assert -form(adjugate, left_3, left_7) == Fraction(-1, 512)
        assert -form(adjugate, left_7, left_3) == Fraction(-1, 512)
        pair = -form(adjugate, left_3, left_8)
        assert pair == -form(adjugate, left_8, left_3)
        assert pair == Fraction(-1, 512) - value * Fraction(1, 64)
    # The opposite diagonal swaps the two sides of the arc.
    for value in (Fraction(1), Fraction(2), Fraction(-1, 8)):
        adjugate = [[value, OFF], [OFF, 1]]
        assert -form(adjugate, left_3, left_8) == Fraction(-9, 512)
        assert -form(adjugate, left_8, left_3) == Fraction(-9, 512)
        pair = -form(adjugate, left_2, left_7)
        assert pair == -form(adjugate, left_7, left_2)
        assert pair == Fraction(-1, 512) - value * Fraction(1, 64)
    # The common root is negative, and the pivot determinant is not zero there.
    root = Fraction(-1, 8)
    assert Fraction(-1, 512) - root * Fraction(1, 64) == 0
    assert root * 1 - OFF * OFF == Fraction(-9, 64)


def main():
    note = NOTE.read_text(encoding="utf-8")
    assert hashlib.sha256(NOTE.read_bytes()).hexdigest() == NOTE_SHA
    assert "rho < 1" in note
    prove_off_diagonal()
    prove_diagonal()

    matrix = host([(0, 1, Fraction(1))])
    assert row_gap(matrix) == Fraction(11, 8)
    keep, complement = schur(matrix, [0, 1])
    assert complement[keep.index(2)][keep.index(7)] == Fraction(-1, 64)
    assert complement[keep.index(7)][keep.index(2)] == 0
    assert complement[keep.index(3)][keep.index(7)] == Fraction(-1, 576)
    assert complement[keep.index(7)][keep.index(3)] == Fraction(1, 72)
    assert complement[keep.index(3)][keep.index(8)] == Fraction(-1, 64)
    assert complement[keep.index(8)][keep.index(3)] == 0
    assert circular_bandwidth(keep, complement) == 4
    complement_inverse = invert(complement)
    assert norm_1(complement_inverse) == norm_inf(complement_inverse) == Fraction(54382596, 28735435)
    inverse = invert(matrix)
    block = [[inverse[row][col] for col in keep] for row in keep]
    assert block == complement_inverse

    matrix = host([(1, 0, Fraction(1))])
    assert row_gap(matrix) == Fraction(11, 8)
    keep, complement = schur(matrix, [0, 1])
    assert complement[keep.index(2)][keep.index(7)] == 0
    assert complement[keep.index(7)][keep.index(2)] == Fraction(-1, 64)
    assert complement[keep.index(3)][keep.index(8)] == 0
    assert complement[keep.index(8)][keep.index(3)] == Fraction(-1, 64)
    assert circular_bandwidth(keep, complement) == 4
    print("PASS length9-interior-entry")


if __name__ == "__main__":
    main()
