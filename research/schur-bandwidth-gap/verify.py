#!/usr/bin/env python3
"""One filled Schur complement keeps the inverse bound and loses bandwidth b."""

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


def host():
    """I-E with bandwidth 2 and infinity norm 1/2."""
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


def schur(matrix, pivot):
    keep = [index for index in range(len(matrix)) if index != pivot]
    diagonal = matrix[pivot][pivot]
    complement = []
    for i in keep:
        row = []
        for j in keep:
            row.append(matrix[i][j] - matrix[i][pivot] * matrix[pivot][j] / diagonal)
        complement.append(row)
    return keep, complement


def main():
    note = NOTE.read_text(encoding="utf-8")
    digest = hashlib.sha256(NOTE.read_bytes()).hexdigest()
    assert digest == NOTE_SHA
    assert "the same inverse bounds hold for that Schur complement" in note
    assert "compression of the order can only reduce distances" in note

    matrix, rho, band = host()
    assert bandwidth(matrix) == band
    off_diagonal = [[(0 if i == j else -matrix[i][j]) for j in range(7)] for i in range(7)]
    assert norm_inf(off_diagonal) == rho

    keep, complement = schur(matrix, 3)
    assert keep == [0, 1, 2, 4, 5, 6]
    assert bandwidth(complement) == 3
    # Survivors 1 and 5 are positions 1 and 4 after the pivot is removed.
    assert complement[1][4] == Fraction(-1, 64)
    assert abs(1 - 4) > band
    assert any(complement[i][i] != 1 for i in range(len(complement)))

    scaled = [[complement[i][j] / complement[i][i] for j in range(len(complement))]
              for i in range(len(complement))]
    scaled_off = [[(0 if i == j else -scaled[i][j]) for j in range(len(scaled))]
                  for i in range(len(scaled))]
    assert bandwidth(scaled) == 3
    assert norm_inf(scaled_off) == Fraction(3, 7)
    assert norm_inf(scaled_off) < rho

    inverse = invert(matrix)
    complement_inverse = invert(complement)
    block = [[inverse[i][j] for j in keep] for i in keep]
    assert block == complement_inverse
    delta = 1 - rho
    infinity_bound = 1 / delta
    one_bound = 1 / delta + 2 * band * rho / delta ** 2
    assert norm_inf(complement_inverse) == Fraction(648, 389)
    assert norm_1(complement_inverse) == Fraction(648, 389)
    assert norm_inf(complement_inverse) <= infinity_bound
    assert norm_1(complement_inverse) <= one_bound
    assert norm_inf(complement_inverse) <= norm_inf(inverse)
    assert norm_1(complement_inverse) <= norm_1(inverse)
    print("PASS schur-bandwidth-gap")


if __name__ == "__main__":
    main()
