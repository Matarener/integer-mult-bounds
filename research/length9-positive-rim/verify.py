#!/usr/bin/env python3
"""One positive entry cancels only one length-9 rim direction."""

from fractions import Fraction
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NOTE = ROOT / "research/unconditional-batched-crt/INVERSE-CONDITIONING.md"
NOTE_SHA = "be3e4b729481b15a5ccc286b297908e4f9cef94c0c9144a28ee1cf58950d142a"
SIZE = 9
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


def host(replacements=()):
    matrix = [[Fraction(0) for _ in range(SIZE)] for _ in range(SIZE)]
    for i in range(SIZE):
        matrix[i][i] = 1
        for j in range(SIZE):
            if i != j and circular(i, j) == 1:
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


def touching_diameter(kill):
    killed = set(kill)
    touch = [index for index in range(SIZE)
             if index not in killed and any(circular(index, pivot) == 1 for pivot in killed)]
    if len(touch) < 2:
        return 0
    return max(circular(i, j) for i in touch for j in touch)


def row_gap(matrix):
    return max(sum(abs(matrix[i][j]) for j in range(SIZE) if j != i) for i in range(SIZE))


def neumann_bounds(rho, bandwidth):
    delta = 1 - rho
    return 1 / delta, 1 / delta + 2 * bandwidth * rho / delta ** 2


def assert_bounds(matrix, inverse, bandwidth):
    rho = row_gap(matrix)
    infinity_bound, one_bound = neumann_bounds(rho, bandwidth)
    assert norm_inf(inverse) <= infinity_bound
    assert norm_1(inverse) <= one_bound
    return rho


def sign_flip_census():
    for source in range(SIZE):
        target = (source + 1) % SIZE
        matrix = host([(source, target, OFF)])
        assert row_gap(matrix) == Fraction(1, 2)
        full_inverse = invert(matrix)
        for start in range(SIZE):
            for length in range(1, SIZE):
                kill = [(start + step) % SIZE for step in range(length)]
                keep, complement = schur(matrix, kill)
                block = [[full_inverse[row][col] for col in keep] for row in keep]
                assert block == invert(complement)
                assert circular_bandwidth(keep, complement) == touching_diameter(kill)
                killed = set(kill)
                touch = [index for index in keep
                         if any(circular(index, pivot) == 1 for pivot in killed)]
                for first in touch:
                    for second in touch:
                        if first != second:
                            assert complement[keep.index(first)][keep.index(second)] != 0


def main():
    note = NOTE.read_text(encoding="utf-8")
    assert hashlib.sha256(NOTE.read_bytes()).hexdigest() == NOTE_SHA
    assert "2 b rho/delta^2" in note
    sign_flip_census()

    # The edge {0,1} is opposite vertex 5. One sign flip does not meet that rim.
    matrix = host([(0, 1, OFF)])
    keep, complement = schur(matrix, [5])
    assert complement[keep.index(4)][keep.index(6)] == -OFF * OFF == Fraction(-1, 16)
    assert complement[keep.index(6)][keep.index(4)] == Fraction(-1, 16)
    assert circular_bandwidth(keep, complement) == touching_diameter([5]) == 2
    complement_inverse = invert(complement)
    assert norm_1(complement_inverse) == norm_inf(complement_inverse) == Fraction(25756, 13515)
    assert assert_bounds(matrix, complement_inverse, 1) == Fraction(1, 2)

    # One interior sign flip on a three-vertex arc changes the corner sign.
    matrix = host([(0, 1, OFF)])
    keep, complement = schur(matrix, [0, 1, 2])
    assert complement[keep.index(8)][keep.index(3)] == Fraction(1, 256)
    assert complement[keep.index(3)][keep.index(8)] == Fraction(-1, 256)

    # The one-vertex fill is exactly 1/16. One positive body entry cancels one direction.
    matrix = host([(1, 8, Fraction(1, 16))])
    keep, complement = schur(matrix, [0])
    assert complement[keep.index(1)][keep.index(8)] == Fraction(1, 16) - OFF * OFF == 0
    assert complement[keep.index(8)][keep.index(1)] == -OFF * OFF == Fraction(-1, 16)
    assert circular_bandwidth(keep, complement) == 2
    assert touching_diameter([0]) == 2
    complement_inverse = invert(complement)
    assert norm_1(complement_inverse) == norm_inf(complement_inverse) == Fraction(224944, 112943)
    assert assert_bounds(matrix, complement_inverse, 2) == Fraction(9, 16)
    block = [[invert(matrix)[row][col] for col in keep] for row in keep]
    assert block == complement_inverse

    # Both directions at +1/16 remove the pair and drop the bandwidth below the diameter.
    matrix = host([(1, 8, Fraction(1, 16)), (8, 1, Fraction(1, 16))])
    keep, complement = schur(matrix, [0])
    assert complement[keep.index(1)][keep.index(8)] == 0
    assert complement[keep.index(8)][keep.index(1)] == 0
    assert circular_bandwidth(keep, complement) == 1
    assert touching_diameter([0]) == 2
    complement_inverse = invert(complement)
    assert norm_1(complement_inverse) == norm_inf(complement_inverse) == Fraction(1136, 571)
    assert assert_bounds(matrix, complement_inverse, 2) == Fraction(9, 16)
    print("PASS length9-positive-rim")


if __name__ == "__main__":
    main()
