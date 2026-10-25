#!/usr/bin/env python3
"""Every width on the length-8 cycle meets the touching diameter."""

from fractions import Fraction
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NOTE = ROOT / "research/unconditional-batched-crt/INVERSE-CONDITIONING.md"
NOTE_SHA = "be3e4b729481b15a5ccc286b297908e4f9cef94c0c9144a28ee1cf58950d142a"
SIZE = 8


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


def degree(width):
    return sum(1 for index in range(1, SIZE) if circular(0, index) <= width)


def host(width):
    value = Fraction(1, 2) / degree(width)
    matrix = [[Fraction(0) for _ in range(SIZE)] for _ in range(SIZE)]
    for i in range(SIZE):
        matrix[i][i] = 1
        for j in range(SIZE):
            if i != j and circular(i, j) <= width:
                matrix[i][j] = -value
    return matrix, value


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
    found = 0
    for i, first in enumerate(indices):
        for j, second in enumerate(indices):
            if matrix[i][j] != 0:
                found = max(found, circular(first, second))
    return found


def touching_diameter(kill, width):
    killed = set(kill)
    touch = [index for index in range(SIZE) if index not in killed and any(
        circular(index, pivot) <= width for pivot in killed)]
    if len(touch) < 2:
        return 0
    return max(circular(i, j) for i in touch for j in touch)


def one_vertex_bounds(width):
    rho = Fraction(1, 2)
    delta = 1 - rho
    return 1 / delta, 1 / delta + 2 * width * rho / delta ** 2


def main():
    note = NOTE.read_text(encoding="utf-8")
    assert hashlib.sha256(NOTE.read_bytes()).hexdigest() == NOTE_SHA
    assert "the same inverse bounds hold for that Schur complement" in note

    for width in range(1, 5):
        matrix, _ = host(width)
        inverse = invert(matrix)
        for start in range(SIZE):
            for length in range(1, SIZE):
                kill = [(start + step) % SIZE for step in range(length)]
                keep, complement = schur(matrix, kill)
                assert circular_bandwidth(keep, complement) == touching_diameter(kill, width)
                block = [[inverse[row][col] for col in keep] for row in keep]
                assert block == invert(complement)

    matrix, value = host(3)
    assert value == Fraction(1, 12)
    _, complement = schur(matrix, [0])
    # Survivors 3 and 7 are opposite and both meet vertex 0.
    assert complement[2][6] == -(value ** 2) == Fraction(-1, 144)
    complement_inverse = invert(complement)
    assert norm_1(complement_inverse) == Fraction(27, 14)
    assert norm_inf(complement_inverse) == Fraction(27, 14)
    infinity_bound, one_bound = one_vertex_bounds(3)
    assert norm_inf(complement_inverse) <= infinity_bound
    assert norm_1(complement_inverse) <= one_bound

    matrix, value = host(4)
    assert value == Fraction(1, 14)
    _, complement = schur(matrix, [0])
    # Distance 4 is still inside width 4, so the direct entry survives the update.
    assert complement[0][4] == -value - value ** 2 == Fraction(-15, 196)
    complement_inverse = invert(complement)
    assert norm_1(complement_inverse) == Fraction(28, 15)
    assert norm_inf(complement_inverse) == Fraction(28, 15)
    infinity_bound, one_bound = one_vertex_bounds(4)
    assert norm_inf(complement_inverse) <= infinity_bound
    assert norm_1(complement_inverse) <= one_bound
    print("PASS length8-touching-diameter")


if __name__ == "__main__":
    main()
