#!/usr/bin/env python3
"""Boundary-order Schur bandwidth of the separated dyadic carve.

The one-interval cap bandwidth <= 2b-1 is the statement proved for a single
middle pivot in PR #4285. This verifier recomputes that witness and checks the
multi-interval extension used by the #4100 Gaussian carve: at least b retained
coordinates between successive interiors keep the same cap, while b-1 retained
coordinates do not.
"""

from fractions import Fraction
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent


def invert(matrix):
    size = len(matrix)
    work = [row[:] + [Fraction(int(i == j)) for j in range(size)]
            for i, row in enumerate(matrix)]
    for col in range(size):
        pivot = next((row for row in range(col, size) if work[row][col] != 0), None)
        if pivot is None:
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


def bandwidth(matrix):
    width = 0
    for i, row in enumerate(matrix):
        for j, entry in enumerate(row):
            if entry != 0:
                width = max(width, abs(i - j))
    return width


def schur(matrix, eliminated):
    kill = list(eliminated)
    kill_set = set(kill)
    keep = [index for index in range(len(matrix)) if index not in kill_set]
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


def banded_host(size, band, diagonal):
    matrix = [[Fraction(0) for _ in range(size)] for _ in range(size)]
    for i in range(size):
        matrix[i][i] = diagonal
        for step in range(1, band + 1):
            if i + step < size:
                matrix[i][i + step] = Fraction(1)
                matrix[i + step][i] = Fraction(1)
    return matrix


def symmetric_witness():
    """PR #4285's 7 by 7 bandwidth-2 host, rebuilt from the published ratios."""
    rho = Fraction(1, 2)
    band = 2
    value = rho / (2 * band)
    matrix = []
    for i in range(7):
        row = []
        for j in range(7):
            if i == j:
                row.append(Fraction(1))
            elif abs(i - j) <= band:
                row.append(-value)
            else:
                row.append(Fraction(0))
        matrix.append(row)
    return matrix, rho, band


def generic_host():
    matrix = [[Fraction(0) for _ in range(7)] for _ in range(7)]
    label = 1
    for i in range(7):
        for j in range(7):
            if abs(i - j) <= 2:
                matrix[i][j] = Fraction(1, label)
                label += 1
    return matrix


def layout(band, lengths, gap, margin):
    """Contiguous interiors separated by `gap` survivors, with `margin` survivors at each end."""
    blocks = []
    cursor = margin
    for length in lengths:
        blocks.append((cursor, cursor + length - 1))
        cursor += length + gap
    size = cursor - gap + margin
    eliminated = [index for start, stop in blocks for index in range(start, stop + 1)]
    return size, eliminated, blocks


def boundary_distance(left, right, eliminated):
    kill = set(eliminated)
    survivors = sum(1 for index in range(left, right + 1) if index not in kill)
    return survivors - 1


def support_pairs(size, band, blocks):
    """Pairs whose Schur entry is allowed to be nonzero under the direct-sum support."""
    eliminated = {index for start, stop in blocks for index in range(start, stop + 1)}
    survivors = [index for index in range(size) if index not in eliminated]
    pairs = set()
    for left in survivors:
        for right in survivors:
            if abs(left - right) <= band:
                pairs.add((left, right))
    for start, stop in blocks:
        rim = [index for index in list(range(start - band, start)) + list(range(stop + 1, stop + band + 1))
               if 0 <= index < size and index not in eliminated]
        for left in rim:
            for right in rim:
                pairs.add((left, right))
    return survivors, pairs


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def check_source_pins():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    by_path = {row["path"]: row for row in sources["files"]}
    gaussian = (ROOT / "research/unconditional-batched-crt/GAUSSIAN.md").read_bytes()
    gauge = (ROOT / "research/capped-phase-fusion/CAPPED-GAUGE-AUDIT.md").read_bytes()
    require(hashlib.sha256(gaussian).hexdigest() == by_path[
        "research/unconditional-batched-crt/GAUSSIAN.md"]["sha256"], "GAUSSIAN.md pin")
    require(hashlib.sha256(gauge).hexdigest() == by_path[
        "research/capped-phase-fusion/CAPPED-GAUGE-AUDIT.md"]["sha256"], "gauge pin")
    gaussian_text = gaussian.decode("utf-8")
    gauge_text = gauge.decode("utf-8")
    require("Interior neighbors are separated by W, so eliminating\n"
            "interiors leaves a Schur matrix of bandwidth O(W) in boundary order."
            in gaussian_text, "GAUSSIAN carve sentence")
    require("Batch right-hand sides in dyadic width between W and2W." in gaussian_text,
            "RHS batch sentence")
    require("7^16<2^45 gives exponent tau=45/16." in gaussian_text, "Strassen exponent sentence")
    require("retain the next B vertices as an interior, then the next W vertices as boundary"
            in gauge_text, "carve loop")
    require("two successive interiors are separated by at least W retained coordinates."
            in gauge_text, "separation sentence")
    require(7 ** 16 < 2 ** 45, "Strassen comparison")
    # Replacing W by the sharp width 2W-1 multiplies a pure power W**(29/16)
    # by less than 4, since (2W-1) < 2W and 2**29 < 2**32.
    require(2 ** 29 < 2 ** 32, "big-O room for the factor two")


def check_one_interval_cap():
    matrix, rho, band = symmetric_witness()
    require(rho == Fraction(1, 2), "witness normalization")
    generic = generic_host()
    cap = 2 * band - 1
    inverse = invert(matrix)
    for start in range(7):
        for stop in range(start + 1, 8):
            if stop - start == 7:
                continue
            one_sided = start == 0 or stop == 7
            limit = band if one_sided else cap
            for host in (matrix, generic):
                keep, complement = schur(host, range(start, stop))
                require(bandwidth(complement) <= limit,
                        "one-interval support failed at " + str((start, stop)))
            keep, complement = schur(matrix, range(start, stop))
            block = [[inverse[i][j] for j in keep] for i in keep]
            require(block == invert(complement), "Schur inverse identity")
    keep, complement = schur(matrix, range(2, 5))
    require(keep == [0, 1, 5, 6], "witness survivors")
    require(bandwidth(complement) == cap, "witness attains 2b-1")
    require(complement[0][3] == Fraction(-1, 432), "published far entry")
    # A later claim of bandwidth <= b is false on this witness.
    require(bandwidth(complement) > band, "cap is strictly above b")
    complement_inverse = invert(complement)
    infinity = max(sum(abs(entry) for entry in row) for row in complement_inverse)
    one = max(sum(abs(complement_inverse[i][j]) for i in range(4)) for j in range(4))
    require(infinity == Fraction(488, 389) and one == Fraction(488, 389),
            "published inverse norms")


def check_separated_cap():
    for band in (1, 2, 3):
        for lengths in ((1,), (2,), (1, 1), (2, 3), (1, 2, 1), (3, 1, 2)):
            for gap in (band, band + 2):
                size, eliminated, blocks = layout(band, lengths, gap, margin=band)
                host = banded_host(size, band, Fraction(4 * band + 3))
                # Pivot blocks do not touch.
                for left, right in zip(blocks, blocks[1:]):
                    require(right[0] - left[1] >= band + 1, "index gap")
                    require(host[left[1]][right[0]] == 0, "no cross-pivot entry")
                survivors, pairs = support_pairs(size, band, blocks)
                kill = set(eliminated)
                farthest = 0
                for left, right in pairs:
                    if left > right:
                        left, right = right, left
                    farthest = max(farthest, boundary_distance(left, right, kill))
                require(farthest <= 2 * band - 1, "support distance " + str((band, lengths, gap, farthest)))
                keep, complement = schur(host, eliminated)
                require(keep == survivors, "survivor order")
                require(bandwidth(complement) <= 2 * band - 1,
                        "matrix bandwidth " + str((band, lengths, gap, bandwidth(complement))))
    # Sharpness for two separated intervals, not only one.
    size, eliminated, blocks = layout(2, (2, 2), gap=2, margin=2)
    _, complement = schur(banded_host(size, 2, Fraction(11)), eliminated)
    require(bandwidth(complement) == 3, "two-interval witness attains 2b-1")


def check_underseparation_grows():
    """b=2 and one retained coordinate between singleton interiors."""
    band = 2
    previous = -1
    for count in range(1, 9):
        size, eliminated, _blocks = layout(band, (1,) * count, gap=band - 1, margin=0)
        # margin 0 places the first interior at 0, which is one-sided.
        # Shift by one survivor so every interior is two-sided, matching the
        # chain whose Schur complement is dense.
        eliminated = [index + 1 for index in eliminated]
        size = eliminated[-1] + 2
        host = banded_host(size, band, Fraction(5))
        _keep, complement = schur(host, eliminated)
        width = bandwidth(complement)
        require(width == count, "dense chain bandwidth " + str((count, width)))
        require(width >= previous, "bandwidth is nondecreasing in the chain")
        previous = width
        if count >= 4:
            require(width > 2 * band - 1, "cap fails once four interiors are chained")
    # The band hypothesis is also necessary: one entry at distance b+2 stays
    # outside the cap when no eliminated index lies between its endpoints.
    host = banded_host(8, 2, Fraction(11))
    host[0][4] = Fraction(1)
    host[4][0] = Fraction(1)
    _keep, complement = schur(host, [6])
    require(bandwidth(complement) > 3, "an out-of-band entry is not covered by the cap")


def check_singular_control():
    host = banded_host(5, 1, Fraction(0))
    try:
        schur(host, [2])
    except ZeroDivisionError:
        return
    raise AssertionError("a singular pivot must be rejected")


def main():
    check_source_pins()
    check_one_interval_cap()
    check_separated_cap()
    check_underseparation_grows()
    check_singular_control()
    print("PASS gaussian-carve-schur-bandwidth")


if __name__ == "__main__":
    main()
