#!/usr/bin/env python3
"""Prefix pivots keep bandwidth. An interior pair does not."""

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


def schur(matrix, kill):
    kill = list(kill)
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
    complement = [[body[i][j] - update[i][j] for j in range(height)] for i in range(height)]
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
    return matrix, band


def scaled_off_norm(matrix):
    size = len(matrix)
    off = []
    for i in range(size):
        off.append([Fraction(0) if i == j else -matrix[i][j] / matrix[i][i]
                    for j in range(size)])
    return norm_inf(off)


def check_block(matrix, kill):
    keep, complement = schur(matrix, kill)
    inverse = invert(matrix)
    block = [[inverse[i][j] for j in keep] for i in keep]
    assert block == invert(complement)
    return keep, complement


def main():
    note = NOTE.read_text(encoding="utf-8")
    assert hashlib.sha256(NOTE.read_bytes()).hexdigest() == NOTE_SHA
    assert "the same inverse bounds hold for that Schur complement" in note

    matrix, rho, band = symmetric_host()
    assert bandwidth(matrix) == band
    for length in range(1, 7):
        _, complement = schur(matrix, range(length))
        assert bandwidth(complement) <= band
    generic, generic_band = generic_host()
    for length in range(1, 7):
        _, complement = schur(generic, range(length))
        assert bandwidth(complement) <= generic_band

    _, endpoint = check_block(matrix, (0, 1))
    assert bandwidth(endpoint) == 2
    assert scaled_off_norm(endpoint) == rho
    endpoint_inverse = invert(endpoint)
    assert norm_1(endpoint_inverse) == Fraction(42152, 23729)
    assert norm_inf(endpoint_inverse) == Fraction(42152, 23729)

    _, adjacent = check_block(matrix, (2, 3))
    assert bandwidth(adjacent) == 3
    # Survivors 0 and 5 land three apart after indices 2 and 3 are removed.
    assert adjacent[0][3] == Fraction(-1, 504)
    assert scaled_off_norm(adjacent) == Fraction(1, 3)
    adjacent_inverse = invert(adjacent)
    assert norm_1(adjacent_inverse) == Fraction(35536, 23729)
    assert norm_inf(adjacent_inverse) == Fraction(35536, 23729)

    _, split = check_block(matrix, (2, 4))
    assert bandwidth(split) == 4
    assert split[0][4] == Fraction(-1, 504)
    split_inverse = invert(split)
    assert norm_1(split_inverse) == Fraction(585, 389)
    assert norm_inf(split_inverse) == Fraction(585, 389)

    delta = 1 - rho
    one_bound = 1 / delta + 2 * band * rho / delta ** 2
    for complement in (endpoint, adjacent, split):
        inverse = invert(complement)
        assert norm_inf(inverse) <= 1 / delta
        assert norm_1(inverse) <= one_bound
    print("PASS schur-prefix-bandwidth")


if __name__ == "__main__":
    main()
