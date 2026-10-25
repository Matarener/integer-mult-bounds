#!/usr/bin/env python3
"""A middle interval raises Schur bandwidth to at most 2b-1."""

from fractions import Fraction
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NOTE = ROOT / "research/unconditional-batched-crt/INVERSE-CONDITIONING.md"
NOTE_SHA = "be3e4b729481b15a5ccc286b297908e4f9cef94c0c9144a28ee1cf58950d142a"


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


def bandwidth(matrix):
    width = 0
    for i, row in enumerate(matrix):
        for j, entry in enumerate(row):
            if entry != 0:
                width = max(width, abs(i - j))
    return width


def schur(matrix, start, stop):
    kill = list(range(start, stop))
    keep = [index for index in range(len(matrix)) if index not in kill]
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


def symmetric_host():
    rho = Fraction(1, 2)
    band = 2
    value = rho / (2 * band)
    size = 7
    matrix = []
    for i in range(size):
        row = []
        for j in range(size):
            if i == j:
                row.append(Fraction(1))
            elif abs(i - j) <= band:
                row.append(-value)
            else:
                row.append(Fraction(0))
        matrix.append(row)
    return matrix, rho, band


def generic_host():
    size = 7
    band = 2
    matrix = [[Fraction(0) for _ in range(size)] for _ in range(size)]
    label = 1
    for i in range(size):
        for j in range(size):
            if abs(i - j) <= band:
                matrix[i][j] = Fraction(1, label)
                label += 1
    return matrix


def intervals(size):
    for start in range(size):
        for stop in range(start + 1, size + 1):
            if stop - start < size:
                yield start, stop


def main():
    note = NOTE.read_text(encoding="utf-8")
    assert hashlib.sha256(NOTE.read_bytes()).hexdigest() == NOTE_SHA
    assert "the same inverse bounds hold for that Schur complement" in note

    matrix, rho, band = symmetric_host()
    generic = generic_host()
    size = len(matrix)
    cap = 2 * band - 1
    inverse = invert(matrix)
    for start, stop in intervals(size):
        one_sided = start == 0 or stop == size
        for host in (matrix, generic):
            keep, complement = schur(host, start, stop)
            assert bandwidth(complement) <= (band if one_sided else cap)
        keep, complement = schur(matrix, start, stop)
        block = [[inverse[i][j] for j in keep] for i in keep]
        assert block == invert(complement)

    keep, complement = schur(matrix, 2, 5)
    assert keep == [0, 1, 5, 6]
    assert bandwidth(complement) == cap
    assert complement[0][3] == Fraction(-1, 432)
    scaled = [[Fraction(0) if i == j else -complement[i][j] / complement[i][i]
               for j in range(4)] for i in range(4)]
    assert norm_inf(scaled) == Fraction(37, 208)
    complement_inverse = invert(complement)
    assert norm_1(complement_inverse) == Fraction(488, 389)
    assert norm_inf(complement_inverse) == Fraction(488, 389)
    delta = 1 - rho
    assert norm_inf(complement_inverse) <= 1 / delta
    assert norm_1(complement_inverse) <= 1 / delta + 2 * band * rho / delta ** 2
    print("PASS schur-interval-bandwidth")


if __name__ == "__main__":
    main()
