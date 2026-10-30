#!/usr/bin/env python3
"""Independent check of the narrow Neumann bounds and their periodic sections.

The linear-band argument is the one written in INVERSE-CONDITIONING.md.
GAUSSIAN.md also applies those bounds on periodic axes and finite sections.
The compression sentence does not cover that caller. The arc count below does.
"""

from fractions import Fraction
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NOTE = ROOT / "research/unconditional-batched-crt/INVERSE-CONDITIONING.md"
CALLER = ROOT / "research/unconditional-batched-crt/GAUSSIAN.md"
NOTE_SHA = "be3e4b729481b15a5ccc286b297908e4f9cef94c0c9144a28ee1cf58950d142a"
CALLER_SHA = "2f63c91c58f2d1cf31294812c75970ea390c61866a8da7ed700d4316a033a242"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mul(a, b):
    n = len(a)
    p = len(b[0])
    m = len(b)
    out = [[Fraction(0) for _ in range(p)] for _ in range(n)]
    for i in range(n):
        for k in range(m):
            if a[i][k] == 0:
                continue
            for j in range(p):
                out[i][j] += a[i][k] * b[k][j]
    return out


def add(a, b):
    return [[a[i][j] + b[i][j] for j in range(len(a[0]))] for i in range(len(a))]


def eye(n):
    return [[Fraction(int(i == j)) for j in range(n)] for i in range(n)]


def norm_inf(a):
    return max(sum(abs(x) for x in row) for row in a)


def norm_1(a):
    n = len(a)
    m = len(a[0])
    return max(sum(abs(a[i][j]) for i in range(n)) for j in range(m))


def invert(a):
    n = len(a)
    m = [row[:] + eye(n)[i] for i, row in enumerate(a)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda row: abs(m[row][col]))
        if m[pivot][col] == 0:
            raise ZeroDivisionError("singular")
        m[col], m[pivot] = m[pivot], m[col]
        scale = m[col][col]
        m[col] = [entry / scale for entry in m[col]]
        for row in range(n):
            if row == col or m[row][col] == 0:
                continue
            factor = m[row][col]
            m[row] = [m[row][j] - factor * m[col][j] for j in range(2 * n)]
    return [row[n:] for row in m]


def geom_sum(n, r):
    return (1 - r ** (n + 1)) / (1 - r)


def weighted_sum(n, r):
    """Exact sum of k r^k from k=1 through n."""
    return r * (1 - (n + 1) * r ** n + n * r ** (n + 1)) / (1 - r) ** 2


def closed_bound(b, rho):
    delta = 1 - rho
    return 1 / delta + 2 * b * rho / delta ** 2


def width_of(matrix):
    width = 0
    for i, row in enumerate(matrix):
        for j, entry in enumerate(row):
            if entry != 0:
                width = max(width, abs(i - j))
    return width


def column_support(matrix):
    n = len(matrix)
    return max(sum(matrix[i][j] != 0 for i in range(n)) for j in range(n))


def power(matrix, k):
    out = eye(len(matrix))
    for _ in range(k):
        out = mul(out, matrix)
    return out


def linear_band(n, b, value):
    matrix = [[Fraction(0) for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if 0 < abs(i - j) <= b:
                matrix[i][j] = value
    return matrix


def circular_band(n, w, value):
    matrix = [[Fraction(0) for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for step in range(1, w + 1):
            matrix[i][(i + step) % n] = value
            matrix[i][(i - step) % n] = value
    return matrix


def principal(matrix, indices):
    return [[matrix[i][j] for j in indices] for i in indices]


def check_series():
    for raw in (1, 2, 3, 4, 5):
        rho = Fraction(raw, raw + 1)
        for n in range(0, 13):
            direct = sum(rho ** k for k in range(n + 1))
            weighted = sum(k * rho ** k for k in range(1, n + 1))
            assert direct == geom_sum(n, rho)
            assert weighted == weighted_sum(n, rho)
        delta = 1 - rho
        assert sum(rho ** k for k in range(0, 40)) < 1 / delta
        assert sum(k * rho ** k for k in range(1, 40)) < rho / delta ** 2
        for b in (1, 2, 5):
            partial = sum((2 * k * b + 1) * rho ** k for k in range(0, 30))
            assert partial < closed_bound(b, rho)
            assert closed_bound(b, rho) == 1 / delta + 2 * b * rho / delta ** 2


def check_linear_support():
    rho = Fraction(3, 5)
    b = 2
    n = 11
    # Equal split keeps the row sum at most rho. Interior rows have 2b entries.
    value = rho / (2 * b)
    matrix = linear_band(n, b, value)
    assert norm_inf(matrix) <= rho
    assert width_of(matrix) == b
    for k in range(0, 5):
        powered = power(matrix, k)
        assert norm_inf(powered) <= rho ** k
        assert width_of(powered) <= k * b
        assert column_support(powered) <= 2 * k * b + 1
        assert max(abs(entry) for row in powered for entry in row) <= rho ** k
    host = [[eye(n)[i][j] - matrix[i][j] for j in range(n)] for i in range(n)]
    inverse = invert(host)
    assert norm_inf(inverse) <= 1 / (1 - rho)
    assert norm_1(inverse) <= closed_bound(b, rho)


def saturate_one_column():
    """The k=1 support count is achieved, so the factor 2b is the count's factor."""
    b = 2
    rho = Fraction(2, 3)
    n = 2 * b + 1
    matrix = [[Fraction(0) for _ in range(n)] for _ in range(n)]
    for i in range(n):
        matrix[i][b] = rho
    assert width_of(matrix) == b
    assert norm_inf(matrix) == rho
    assert norm_1(matrix) == (2 * b + 1) * rho


def bandwidth_free_column():
    """A row gap alone does not give an N-independent 1-norm bound."""
    rho = Fraction(1, 2)
    n = 12
    matrix = [[Fraction(0) for _ in range(n)] for _ in range(n)]
    for i in range(1, n):
        matrix[i][0] = rho
    assert norm_inf(matrix) == rho
    assert all(sum(matrix[i][k] * matrix[k][j] for k in range(n)) == 0
               for i in range(n) for j in range(n))
    inverse_norm = 1 + (n - 1) * rho
    delta = 1 - rho
    assert inverse_norm == Fraction(13, 2)
    assert inverse_norm > 1 / delta
    assert inverse_norm > closed_bound(1, rho)


def sections_obey(n, w, rho):
    ambient = circular_band(n, w, rho / (2 * w))
    assert norm_inf(ambient) == rho
    for mask in range(1, 1 << n):
        chosen = [i for i in range(n) if mask >> i & 1]
        block = principal(ambient, chosen)
        for k in range(0, 4):
            powered = power(block, k)
            assert column_support(powered) <= 2 * k * w + 1
            assert norm_inf(powered) <= rho ** k
        lifted = [[(1 if i == j else 0) - block[i][j]
                   for j in range(len(chosen))] for i in range(len(chosen))]
        inverse = invert(lifted)
        assert norm_inf(inverse) <= 1 / (1 - rho)
        assert norm_1(inverse) <= closed_bound(w, rho)


def check_circular_sections():
    # Neighbors on the circle become the ends of this ordered section.
    ambient = circular_band(8, 1, Fraction(1, 4))
    section = principal(ambient, [0, 1, 7])
    assert width_of(section) == 2
    sections_obey(8, 1, Fraction(1, 2))
    sections_obey(7, 2, Fraction(1, 2))


def check_permutation_invariance():
    rho = Fraction(2, 5)
    matrix = linear_band(5, 1, rho / 2)
    host = [[(1 if i == j else 0) - matrix[i][j] for j in range(5)] for i in range(5)]
    order = [2, 0, 4, 1, 3]
    permuted = [[host[order[i]][order[j]] for j in range(5)] for i in range(5)]
    assert norm_1(invert(host)) == norm_1(invert(permuted))
    assert norm_inf(invert(host)) == norm_inf(invert(permuted))


def plug_in_p10():
    """Under the caller's stated numerical hypotheses, both 2-norms are below p^10."""
    for p in range(2, 401):
        delta = Fraction(1, 16 * p * p)
        w = p - 1
        rho = 1 - delta
        inverse_inf = 1 / delta
        inverse_1 = closed_bound(w, rho)
        loose = Fraction(16 * p * p) + 512 * (p - 1) * p ** 4
        assert inverse_1 <= loose
        assert loose * inverse_inf < p ** 20
        # Strict row norm < 2 and at most 2w+1 entries, each strictly below 2.
        assert 4 * (2 * p - 1) < p ** 20
    for p in (3, 4, 17, 73):
        assert 8192 * p < p ** 14


def check_sources():
    assert sha256(NOTE) == NOTE_SHA
    assert sha256(CALLER) == CALLER_SHA
    note = NOTE.read_text(encoding="utf-8")
    caller = CALLER.read_text(encoding="utf-8")
    assert "2 b rho/delta^2" in note
    assert "compression of the order can only reduce distances" in note
    assert "periodic axes and finite sections" in caller
    assert "less than p^10 eventually" in caller
    assert "delta>=1/(16p^2)" in caller.replace(" ", "")


def main():
    check_sources()
    check_series()
    check_linear_support()
    saturate_one_column()
    bandwidth_free_column()
    check_circular_sections()
    check_permutation_invariance()
    plug_in_p10()
    print("PASS narrow-neumann-section")


if __name__ == "__main__":
    main()
