#!/usr/bin/env python3
"""Equal-weight cycle arcs meet the touching diameter at every length."""

from fractions import Fraction
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NOTE = ROOT / "research/unconditional-batched-crt/INVERSE-CONDITIONING.md"
NOTE_SHA = "be3e4b729481b15a5ccc286b297908e4f9cef94c0c9144a28ee1cf58950d142a"
RHO = Fraction(1, 2)


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


def circular(i, j, size):
    gap = abs(i - j)
    return min(gap, size - gap)


def degree(size, width):
    return sum(1 for index in range(1, size) if circular(0, index, size) <= width)


def host(size, width):
    value = RHO / degree(size, width)
    matrix = [[Fraction(0) for _ in range(size)] for _ in range(size)]
    for i in range(size):
        matrix[i][i] = 1
        for j in range(size):
            if i != j and circular(i, j, size) <= width:
                matrix[i][j] = -value
    return matrix, value


def schur(matrix, kill):
    size = len(matrix)
    kill = list(kill)
    killed = set(kill)
    keep = [index for index in range(size) if index not in killed]
    pivot = [[matrix[i][j] for j in kill] for i in kill]
    right = [[matrix[i][j] for j in keep] for i in kill]
    left = [[matrix[i][j] for j in kill] for i in keep]
    body = [[matrix[i][j] for j in keep] for i in keep]
    pivot_inverse = invert(pivot)
    pivot_size = len(kill)
    height = len(keep)
    mixed = [[sum(left[i][t] * pivot_inverse[t][s] for t in range(pivot_size))
              for s in range(pivot_size)] for i in range(height)]
    update = [[sum(mixed[i][s] * right[s][j] for s in range(pivot_size))
               for j in range(height)] for i in range(height)]
    complement = [[body[i][j] - update[i][j] for j in range(height)]
                  for i in range(height)]
    return keep, complement, pivot_inverse


def circular_bandwidth(indices, matrix, size):
    found = 0
    for i, first in enumerate(indices):
        for j, second in enumerate(indices):
            if matrix[i][j] != 0:
                found = max(found, circular(first, second, size))
    return found


def touching_set(kill, width, size):
    killed = set(kill)
    return [index for index in range(size)
            if index not in killed and any(circular(index, pivot, size) <= width
                                            for pivot in killed)]


def touching_diameter(kill, width, size):
    touch = touching_set(kill, width, size)
    if len(touch) < 2:
        return 0
    return max(circular(i, j, size) for i in touch for j in touch)


def rim_routes(survivors, width, length):
    """Cycle routes between the inner left rim and the right survivor end."""
    along = survivors - width
    around = length + width
    return along, around


def prove_rim_identity():
    # Boundary survivor count 2*width+1 and a one-vertex arc. Both routes
    # then exceed the width by exactly one, for every positive width.
    for width in range(1, 41):
        survivors = 2 * width + 1
        along, around = rim_routes(survivors, width, 1)
        assert along + around == survivors + 1
        assert along - width == 1
        assert around - width == 1


def one_vertex_bounds(width):
    delta = 1 - RHO
    return 1 / delta, 1 / delta + 2 * width * RHO / delta ** 2


def census(limit):
    for size in range(3, limit + 1):
        for width in range(1, size // 2 + 1):
            matrix, value = host(size, width)
            assert value > 0
            inverse = invert(matrix)
            for start in range(size):
                for length in range(1, size):
                    kill = [(start + step) % size for step in range(length)]
                    keep, complement, pivot_inverse = schur(matrix, kill)
                    assert all(entry > 0 for row in pivot_inverse for entry in row)
                    assert touching_diameter(kill, width, size) == circular_bandwidth(
                        keep, complement, size)
                    block = [[inverse[row][col] for col in keep] for row in keep]
                    assert block == invert(complement)
                    touch = set(touching_set(kill, width, size))
                    for i, first in enumerate(keep):
                        if first not in touch:
                            assert [matrix[first][col] for col in keep] == complement[i]
                            continue
                        for j, second in enumerate(keep):
                            if i != j and second in touch:
                                assert complement[i][j] < 0
                    survivors = size - length
                    if survivors >= 2 * width + 1:
                        along, around = rim_routes(survivors, width, length)
                        assert along + around == size
                        assert min(along, around) >= width + 1
                        assert touching_diameter(kill, width, size) >= min(along, around)


def main():
    note = NOTE.read_text(encoding="utf-8")
    assert hashlib.sha256(NOTE.read_bytes()).hexdigest() == NOTE_SHA
    assert "the same inverse bounds hold for that Schur complement" in note
    assert "compression of the order can only reduce distances" in note
    prove_rim_identity()
    census(9)

    matrix, value = host(9, 1)
    assert value == Fraction(1, 4)
    keep, complement, _ = schur(matrix, [0])
    # Vertices 1 and 8 are the two survivors that meet vertex 0.
    assert complement[keep.index(1)][keep.index(8)] == -(value ** 2) == Fraction(-1, 16)
    assert circular_bandwidth(keep, complement, 9) == 2
    complement_inverse = invert(complement)
    assert norm_1(complement_inverse) == norm_inf(complement_inverse) == Fraction(528, 265)
    infinity_bound, one_bound = one_vertex_bounds(1)
    assert norm_inf(complement_inverse) <= infinity_bound
    assert norm_1(complement_inverse) <= one_bound

    matrix, value = host(9, 2)
    assert value == Fraction(1, 8)
    keep, complement, _ = schur(matrix, [0])
    # Vertices 2 and 7 meet vertex 0 and have no direct entry.
    assert complement[keep.index(2)][keep.index(7)] == -(value ** 2) == Fraction(-1, 64)
    assert circular_bandwidth(keep, complement, 9) == 4
    complement_inverse = invert(complement)
    assert norm_1(complement_inverse) == norm_inf(complement_inverse) == Fraction(4772, 2435)
    infinity_bound, one_bound = one_vertex_bounds(2)
    assert norm_inf(complement_inverse) <= infinity_bound
    assert norm_1(complement_inverse) <= one_bound
    print("PASS equal-weight-cycle-diameter")


if __name__ == "__main__":
    main()
