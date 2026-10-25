#!/usr/bin/env python3
"""One positive entry cancels only one width-2 far-rim direction."""

from fractions import Fraction
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NOTE = ROOT / "research/unconditional-batched-crt/INVERSE-CONDITIONING.md"
NOTE_SHA = "be3e4b729481b15a5ccc286b297908e4f9cef94c0c9144a28ee1cf58950d142a"
SIZE = 9
WIDTH = 2
OFF = Fraction(1, 8)
FILL = OFF * OFF


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
        matrix[i][i] = 1
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


def touching_diameter(kill, width):
    killed = set(kill)
    touch = [index for index in range(SIZE)
             if index not in killed and any(circular(index, pivot) <= width
                                             for pivot in killed)]
    if len(touch) < 2:
        return 0
    return max(circular(i, j) for i in touch for j in touch)


def row_gap(matrix):
    return max(sum(abs(matrix[i][j]) for j in range(SIZE) if j != i)
               for i in range(SIZE))


def neumann_bounds(rho, bandwidth):
    delta = 1 - rho
    return 1 / delta, 1 / delta + 2 * bandwidth * rho / delta ** 2


def assert_inside(matrix, inverse, bandwidth):
    infinity_bound, one_bound = neumann_bounds(row_gap(matrix), bandwidth)
    assert norm_inf(inverse) <= infinity_bound
    assert norm_1(inverse) <= one_bound


def assert_block(matrix, keep, complement):
    inverse = invert(matrix)
    block = [[inverse[row][col] for col in keep] for row in keep]
    assert block == invert(complement)


def original_entry(first, second):
    if circular(first, second) <= WIDTH:
        return -OFF - FILL
    return -FILL


def main():
    note = NOTE.read_text(encoding="utf-8")
    assert hashlib.sha256(NOTE.read_bytes()).hexdigest() == NOTE_SHA
    assert "2 b rho/delta^2" in note
    assert FILL == Fraction(1, 64)

    matrix = host()
    keep, complement = schur(matrix, [0])
    touch = [1, 2, 7, 8]
    for first in touch:
        for second in touch:
            if first == second:
                continue
            assert complement[keep.index(first)][keep.index(second)] == original_entry(first, second)
    assert complement[keep.index(2)][keep.index(7)] == Fraction(-1, 64)
    assert circular_bandwidth(keep, complement) == touching_diameter([0], WIDTH) == 4
    complement_inverse = invert(complement)
    assert norm_1(complement_inverse) == norm_inf(complement_inverse) == Fraction(4772, 2435)
    assert_inside(matrix, complement_inverse, WIDTH)
    assert_block(matrix, keep, complement)

    # One body entry appears in only one direction.
    for first in touch:
        for second in touch:
            if first == second:
                continue
            changed = host([(first, second, FILL)])
            changed_keep, changed_complement = schur(changed, [0])
            assert changed_complement[changed_keep.index(first)][changed_keep.index(second)] == 0
            assert changed_complement[changed_keep.index(second)][changed_keep.index(first)] == original_entry(
                second, first)

    matrix = host([(2, 7, FILL)])
    keep, complement = schur(matrix, [0])
    assert complement[keep.index(2)][keep.index(7)] == 0
    assert complement[keep.index(7)][keep.index(2)] == Fraction(-1, 64)
    assert circular_bandwidth(keep, complement) == 4
    complement_inverse = invert(complement)
    assert norm_1(complement_inverse) == norm_inf(complement_inverse) == Fraction(371769784, 189854515)
    assert row_gap(matrix) == Fraction(33, 64)
    assert_inside(matrix, complement_inverse, 4)
    assert_block(matrix, keep, complement)

    # Both directions remove the distance-4 pair. Distance 3 remains.
    matrix = host([(2, 7, FILL), (7, 2, FILL)])
    keep, complement = schur(matrix, [0])
    assert complement[keep.index(2)][keep.index(7)] == 0
    assert complement[keep.index(7)][keep.index(2)] == 0
    assert complement[keep.index(1)][keep.index(7)] == Fraction(-1, 64)
    assert complement[keep.index(2)][keep.index(8)] == Fraction(-1, 64)
    assert circular_bandwidth(keep, complement) == 3
    assert touching_diameter([0], WIDTH) == 4
    complement_inverse = invert(complement)
    assert norm_1(complement_inverse) == norm_inf(complement_inverse) == Fraction(461, 236)
    assert row_gap(matrix) == Fraction(33, 64)
    assert_inside(matrix, complement_inverse, 4)
    assert_block(matrix, keep, complement)
    print("PASS length9-width2-entry")


if __name__ == "__main__":
    main()
