#!/usr/bin/env python3
"""Width 2 on the length-8 circle does not survive one arc."""

from fractions import Fraction
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NOTE = ROOT / "research/unconditional-batched-crt/INVERSE-CONDITIONING.md"
NOTE_SHA = "be3e4b729481b15a5ccc286b297908e4f9cef94c0c9144a28ee1cf58950d142a"
SIZE = 8
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


def host():
    matrix = [[Fraction(0) for _ in range(SIZE)] for _ in range(SIZE)]
    for i in range(SIZE):
        matrix[i][i] = 1
        for step in range(1, WIDTH + 1):
            matrix[i][(i + step) % SIZE] = -OFF
            matrix[i][(i - step) % SIZE] = -OFF
    return matrix


def schur(matrix, kill):
    kill = list(kill)
    keep = [index for index in range(SIZE) if index not in set(kill)]
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
    width = 0
    for i, first in enumerate(indices):
        for j, second in enumerate(indices):
            if matrix[i][j] != 0:
                width = max(width, circular(first, second))
    return width


def touching_diameter(kill):
    killed = set(kill)
    touch = [index for index in range(SIZE) if index not in killed and any(
        circular(index, pivot) <= WIDTH for pivot in killed)]
    if len(touch) < 2:
        return 0
    return max(circular(i, j) for i in touch for j in touch)


def main():
    note = NOTE.read_text(encoding="utf-8")
    assert hashlib.sha256(NOTE.read_bytes()).hexdigest() == NOTE_SHA
    assert "the same inverse bounds hold for that Schur complement" in note

    matrix = host()
    inverse = invert(matrix)
    for start in range(SIZE):
        for length in range(1, SIZE):
            kill = [(start + step) % SIZE for step in range(length)]
            keep, complement = schur(matrix, kill)
            assert circular_bandwidth(keep, complement) == touching_diameter(kill)
            killed = set(kill)
            for i, first in enumerate(keep):
                for j, second in enumerate(keep):
                    if complement[i][j] == 0 or circular(first, second) <= WIDTH:
                        continue
                    assert any(circular(first, pivot) <= WIDTH for pivot in killed)
                    assert any(circular(second, pivot) <= WIDTH for pivot in killed)
            block = [[inverse[row][col] for col in keep] for row in keep]
            assert block == invert(complement)

    _, one = schur(matrix, [0])
    # Survivors 2 and 6 are opposite and both lie at distance 2 from 0.
    assert one[1][5] == Fraction(-1, 64)
    assert circular(2, 6) == 4

    keep, complement = schur(matrix, [2, 3, 4])
    assert keep == [0, 1, 5, 6, 7]
    assert complement[1][2] == Fraction(-5, 216)
    assert circular(1, 5) == 4
    complement_inverse = invert(complement)
    assert norm_1(complement_inverse) == Fraction(2257, 1240)
    assert norm_inf(complement_inverse) == Fraction(2257, 1240)
    rho = Fraction(1, 2)
    delta = 1 - rho
    assert norm_inf(complement_inverse) <= 1 / delta
    assert norm_1(complement_inverse) <= 1 / delta + 2 * WIDTH * rho / delta ** 2
    print("PASS circular-width2-arc")


if __name__ == "__main__":
    main()
