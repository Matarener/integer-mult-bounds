#!/usr/bin/env python3
"""Circular Schur bandwidth follows the arc length, not the width alone."""

from fractions import Fraction
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NOTE = ROOT / "research/unconditional-batched-crt/INVERSE-CONDITIONING.md"
NOTE_SHA = "be3e4b729481b15a5ccc286b297908e4f9cef94c0c9144a28ee1cf58950d142a"
SIZE = 8
OFF = Fraction(1, 4)


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


def host():
    matrix = [[Fraction(0) for _ in range(SIZE)] for _ in range(SIZE)]
    for i in range(SIZE):
        matrix[i][i] = 1
        matrix[i][(i + 1) % SIZE] = -OFF
        matrix[i][(i - 1) % SIZE] = -OFF
    return matrix


def schur(matrix, kill):
    kill = list(kill)
    keep = [index for index in range(SIZE) if index not in kill]
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
    return keep, complement, pivot_inverse


def circular_bandwidth(indices, matrix):
    width = 0
    for i, first in enumerate(indices):
        for j, second in enumerate(indices):
            if matrix[i][j] != 0:
                width = max(width, circular(first, second))
    return width


def main():
    note = NOTE.read_text(encoding="utf-8")
    assert hashlib.sha256(NOTE.read_bytes()).hexdigest() == NOTE_SHA
    assert "the same inverse bounds hold for that Schur complement" in note

    matrix = host()
    inverse = invert(matrix)
    for start in range(SIZE):
        for length in range(1, SIZE):
            kill = [(start + step) % SIZE for step in range(length)]
            keep, complement, _ = schur(matrix, kill)
            assert circular_bandwidth(keep, complement) == min(length + 1, SIZE - length - 1)
            block = [[inverse[i][j] for j in keep] for i in keep]
            assert block == invert(complement)

    kill = [2, 3, 4]
    keep, complement, pivot_inverse = schur(matrix, kill)
    assert keep == [0, 1, 5, 6, 7]
    assert circular(1, 5) == 4
    assert complement[1][2] == Fraction(-1, 224)
    assert -OFF * OFF * pivot_inverse[0][2] == Fraction(-1, 224)
    complement_inverse = invert(complement)
    assert norm_1(complement_inverse) == Fraction(163, 84)
    assert norm_inf(complement_inverse) == Fraction(163, 84)
    rho = Fraction(1, 2)
    delta = 1 - rho
    assert norm_inf(complement_inverse) <= 1 / delta
    assert norm_1(complement_inverse) <= 1 / delta + 2 * rho / delta ** 2

    _, one_vertex, _ = schur(matrix, [0])
    assert one_vertex[0][-1] == Fraction(-1, 16)
    assert circular_bandwidth(list(range(1, SIZE)), one_vertex) == 2
    print("PASS circular-schur-arc")


if __name__ == "__main__":
    main()
