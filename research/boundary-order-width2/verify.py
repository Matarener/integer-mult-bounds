#!/usr/bin/env python3
"""One width-2 interior has boundary-order half-bandwidth 3."""

from fractions import Fraction
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GAUSSIAN = ROOT / "research/unconditional-batched-crt/GAUSSIAN.md"
FINE = ROOT / "research/unconditional-batched-crt/vendor/FINE-PRIME.md"
GAUSSIAN_SHA = "2f63c91c58f2d1cf31294812c75970ea390c61866a8da7ed700d4316a033a242"
FINE_SHA = "47d1b1b4df28aadda3cd6bdeb1fbc47290595e9208cd09c1a1f338520d33fdce"
WIDTH = 2
OFF = Fraction(1, 8)
CASES = (
    (8, (3, 4), (1, 6), Fraction(-1, 504), 5),
    (10, (3, 4, 5, 6), (1, 8), Fraction(-1, 1664), 7),
    (12, (3, 4, 5, 6, 7, 8), (1, 10), Fraction(-121, 887692), 9),
)
LENGTH4_UPPER = {
    (0, 1): Fraction(-1, 8),
    (0, 2): Fraction(-1, 8),
    (1, 2): Fraction(-239, 1664),
    (1, 7): Fraction(-5, 1664),
    (1, 8): Fraction(-1, 1664),
    (2, 7): Fraction(-121, 14976),
    (2, 8): Fraction(-5, 1664),
    (7, 8): Fraction(-239, 1664),
    (7, 9): Fraction(-1, 8),
    (8, 9): Fraction(-1, 8),
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


def host(size):
    matrix = [[Fraction(0) for _ in range(size)] for _ in range(size)]
    for i in range(size):
        matrix[i][i] = Fraction(1)
        for j in range(size):
            if i != j and abs(i - j) <= WIDTH:
                matrix[i][j] = -OFF
    return matrix


def schur(matrix, kill):
    killed = set(kill)
    keep = [index for index in range(len(matrix)) if index not in killed]
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


def half_bandwidth(matrix):
    found = 0
    for i, row in enumerate(matrix):
        for j, entry in enumerate(row):
            if i != j and entry != 0:
                found = max(found, abs(i - j))
    return found


def main():
    gaussian = GAUSSIAN.read_text(encoding="utf-8")
    fine = FINE.read_text(encoding="utf-8")
    assert hashlib.sha256(GAUSSIAN.read_bytes()).hexdigest() == GAUSSIAN_SHA
    assert hashlib.sha256(FINE.read_bytes()).hexdigest() == FINE_SHA
    assert "bandwidth O(W) in boundary order" in gaussian
    assert "Interior neighbors are separated by W" in gaussian
    assert "two neighboring O(W)-size separators" in fine

    length4 = None
    for size, interior, corner, entry, span in CASES:
        matrix = host(size)
        assert max(sum(abs(matrix[i][j]) for j in range(size) if j != i)
                   for i in range(size)) == Fraction(1, 2)
        keep, complement = schur(matrix, interior)
        assert keep == [index for index in range(size) if index not in interior]
        assert half_bandwidth(complement) == 2 * WIDTH - 1
        left, right = corner
        assert right - left == span
        assert keep.index(right) - keep.index(left) == 2 * WIDTH - 1
        assert complement[keep.index(left)][keep.index(right)] == entry
        assert complement[keep.index(right)][keep.index(left)] == entry
        for column, survivor in enumerate(keep):
            if survivor - keep[0] > WIDTH:
                assert complement[0][column] == 0
        if size == 10:
            length4 = (matrix, keep, complement)

    matrix, keep, complement = length4
    for i, first in enumerate(keep):
        for j, second in enumerate(keep):
            if i < j:
                assert complement[i][j] == LENGTH4_UPPER.get((first, second), 0)
            assert complement[i][j] == complement[j][i]
    inverse = invert(matrix)
    block = [[inverse[row][col] for col in keep] for row in keep]
    assert block == invert(complement)
    print("PASS boundary-order-width2")


if __name__ == "__main__":
    main()
