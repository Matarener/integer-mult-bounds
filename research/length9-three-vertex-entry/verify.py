#!/usr/bin/env python3
"""The entry 17/8 zeros both directions of one far pair."""

from fractions import Fraction
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NOTE = ROOT / "research/unconditional-batched-crt/INVERSE-CONDITIONING.md"
NOTE_SHA = "be3e4b729481b15a5ccc286b297908e4f9cef94c0c9144a28ee1cf58950d142a"
SIZE = 9
WIDTH = 2
OFF = Fraction(1, 8)
ROOT_VALUE = Fraction(17, 8)
KILL = [0, 1, 2]


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


def host(row, col, value):
    matrix = [[Fraction(0) for _ in range(SIZE)] for _ in range(SIZE)]
    for i in range(SIZE):
        matrix[i][i] = Fraction(1)
        for j in range(SIZE):
            if i != j and circular(i, j) <= WIDTH:
                matrix[i][j] = -OFF
    matrix[row][col] = value
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


def det2(matrix):
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def prove_cofactors(value):
    # Pivot with H[0][1] = value. Vertices 4 and 8 meet opposite ends.
    scale = OFF
    adj_02 = det2([[value, -scale], [1, -scale]])
    adj_12 = -det2([[1, -scale], [-scale, -scale]])
    adj_20 = det2([[-scale, 1], [-scale, -scale]])
    adj_21 = -det2([[1, value], [-scale, -scale]])
    assert adj_02 + adj_12 == scale * (2 + scale - value)
    assert adj_20 + adj_21 == scale * (2 + scale - value)
    numerator = -(scale ** 2) * (adj_20 + adj_21)
    assert numerator == (value - ROOT_VALUE) / 512
    determinant = (1 - scale ** 2) + value * scale * (1 + scale) - (scale ** 2) * (1 + scale)
    assert determinant == (495 + 72 * value) / 512
    return numerator, determinant


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


def far_numerators(row, col, value, pair):
    matrix = host(row, col, value)
    pivot = [[matrix[i][j] for j in KILL] for i in KILL]
    width = determinant(pivot)
    keep, complement = schur(matrix)
    first = entry(complement, keep, pair[0], pair[1]) * width
    second = entry(complement, keep, pair[1], pair[0]) * width
    return first, second


def common_root(row, col, pair):
    zero = far_numerators(row, col, 0, pair)
    one = far_numerators(row, col, 1, pair)
    two = far_numerators(row, col, 2, pair)
    slopes = (one[0] - zero[0], one[1] - zero[1])
    assert two[0] == zero[0] + 2 * slopes[0]
    assert two[1] == zero[1] + 2 * slopes[1]
    roots = []
    for constant, slope in zip(zero, slopes):
        if slope == 0:
            roots.append(None if constant != 0 else "any")
        else:
            roots.append(-constant / slope)
    if roots[0] != roots[1]:
        return None
    return roots[0]


def entry(complement, keep, first, second):
    return complement[keep.index(first)][keep.index(second)]


def main():
    note = NOTE.read_text(encoding="utf-8")
    assert hashlib.sha256(NOTE.read_bytes()).hexdigest() == NOTE_SHA
    assert "rho < 1" in note
    assert 2 + OFF == ROOT_VALUE
    assert OFF ** 3 == Fraction(1, 512)

    for value in (Fraction(0), Fraction(1), ROOT_VALUE, Fraction(3, 7)):
        numerator, determinant = prove_cofactors(value)
        assert numerator == (value - ROOT_VALUE) * OFF ** 3
    _, determinant = prove_cofactors(ROOT_VALUE)
    assert determinant == Fraction(81, 64)

    matrix = host(0, 1, ROOT_VALUE)
    assert row_gap(matrix) == ROOT_VALUE + 3 * OFF == Fraction(5, 2)
    keep, complement = schur(matrix)
    assert entry(complement, keep, 4, 8) == 0
    assert entry(complement, keep, 8, 4) == 0
    assert entry(complement, keep, 3, 7) == Fraction(-1, 288)
    assert entry(complement, keep, 7, 3) == Fraction(1, 36)
    assert entry(complement, keep, 3, 8) == Fraction(-1, 72)
    assert entry(complement, keep, 8, 3) == Fraction(1, 72)
    assert circular_bandwidth(keep, complement) == 4
    complement_inverse = invert(complement)
    assert norm_1(complement_inverse) == Fraction(12680, 6931)
    assert norm_inf(complement_inverse) == Fraction(6178688, 3375397)
    inverse = invert(matrix)
    block = [[inverse[row][col] for col in keep] for row in keep]
    assert block == complement_inverse

    for row, col, pair in ((1, 0, (4, 8)), (1, 2, (3, 7)), (2, 1, (3, 7))):
        changed_keep, changed = schur(host(row, col, ROOT_VALUE))
        assert entry(changed, changed_keep, pair[0], pair[1]) == 0
        assert entry(changed, changed_keep, pair[1], pair[0]) == 0
        assert circular_bandwidth(changed_keep, changed) == 4

    assert common_root(0, 1, (4, 8)) == ROOT_VALUE
    assert common_root(1, 0, (4, 8)) == ROOT_VALUE
    assert common_root(1, 2, (3, 7)) == ROOT_VALUE
    assert common_root(2, 1, (3, 7)) == ROOT_VALUE
    for pair in ((3, 7), (3, 8), (4, 8)):
        for row, col in ((0, 2), (2, 0)):
            root = common_root(row, col, pair)
            assert root is None or root <= 0
        for index in KILL:
            root = common_root(index, index, pair)
            assert root is None or root <= 0
    print("PASS length9-three-vertex-entry")


if __name__ == "__main__":
    main()
