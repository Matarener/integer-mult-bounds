#!/usr/bin/env python3
"""Exact finite corroboration, produced by Nick Petalas. Apache-2.0."""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def eye(n):
    require(1 <= n <= 8, "dimension limit")
    return [[F(i == j) for j in range(n)] for i in range(n)]


def transpose(a):
    return [list(row) for row in zip(*a)]


def multiply(a, b):
    n = len(a)
    require(1 <= n <= 8 and len(b) == n, "matrix dimensions")
    require(all(len(row) == n for row in a + b), "square matrices")
    return [[sum(a[i][k] * b[k][j] for k in range(n))
             for j in range(n)] for i in range(n)]


def inverse(a):
    n = len(a)
    require(1 <= n <= 8, "inverse dimension")
    m = [list(row) + unit for row, unit in zip(a, eye(n))]
    for j in range(n):
        pivot = next((i for i in range(j, n) if m[i][j]), None)
        require(pivot is not None, "singular matrix")
        m[j], m[pivot] = m[pivot], m[j]
        divisor = m[j][j]
        m[j] = [x / divisor for x in m[j]]
        for i in range(n):
            if i != j:
                coefficient = m[i][j]
                m[i] = [x - coefficient * y for x, y in zip(m[i], m[j])]
    return [row[n:] for row in m]


def envelope(k):
    require(type(k) is F and k >= 1, "condition number must be Fraction >= 1")
    return (k + 1 / k) / 2


def coefficient_matrix(a, b):
    return [[[a, F(0)], [F(0), a]], [[F(0), b], [b, F(0)]]]


def regular(s):
    return [[s[x ^ y][i][j] for y in range(2) for j in range(2)]
            for x in range(2) for i in range(2)]


def coefficients(a):
    return [[[a[2 * x + i][j] for j in range(2)] for i in range(2)]
            for x in range(2)]


def pairings(s, inv, row):
    values = [s[g][row][j] * inv[g][j][row]
              for j in range(2) for g in range(2)]
    require(sum(values) == 1, "actual inverse row normalization")
    return values


def potential(s, inv):
    return sum(s[1][i][j] * inv[1][j][i]
               for i in range(2) for j in range(2))


def witness(v):
    require(type(v) is F and 1 <= v <= 16, "witness parameter limit")
    a, b = (v + 1 / v) / 2, (v - 1 / v) / 2
    s = coefficient_matrix(a, b)
    inv = coefficient_matrix(a, -b)
    dense = regular(s)
    require(inverse(dense) == regular(inv), "independent dense inverse")
    for sign in (-1, 1):
        block = [[s[0][i][j] + sign * s[1][i][j] for j in range(2)]
                 for i in range(2)]
        expected = [[inv[0][i][j] + sign * inv[1][i][j] for j in range(2)]
                    for i in range(2)]
        require(inverse(block) == expected, "Fourier inverse")
    # Unnormalized eigenvectors have norm squared two and form a basis.
    d = [[1, 0, 0, 0], [0, 0, 0, 1],
         [0, 0, 1, 0], [0, 1, 0, 0]]
    basis = [[1, 0, 1, 0], [1, 0, -1, 0],
             [0, 1, 0, 1], [0, 1, 0, -1]]
    u = multiply(d, basis)
    require(multiply(transpose(u), u) == [[2 * x for x in row] for row in eye(4)],
            "spectral basis")
    diagonal = [v, v, 1 / v, 1 / v]
    require(multiply(dense, u) == [[u[i][j] * diagonal[j] for j in range(4)]
                                  for i in range(4)], "exact spectrum")
    before = pairings(s, inv, 0)
    require(before == [a * a, 0, 0, -b * b], "signed pairing support")
    call = eye(4)
    call[0], call[2] = call[2], call[0]
    after = coefficients(multiply(call, dense))
    after_inv = coefficients(inverse(multiply(call, dense)))
    delta = potential(after, after_inv) - potential(s, inv)
    require(delta == a * a + b * b == envelope(v * v), "sharp increment")
    require(potential(s, inv) == -2 * b * b and potential(after, after_inv) == 1,
            "literal potential values")
    return delta


def rotation(n, seed):
    u = eye(n)
    for k in range(3 * n):
        i, j = k % n, (k + 1) % n
        if i == j:
            continue
        c, s = (F(3, 5), F(4, 5)) if (k + seed) % 2 else (F(5, 13), F(12, 13))
        r = eye(n)
        r[i][i], r[j][j], r[i][j], r[j][i] = c, c, -s, s
        u = multiply(r, u)
    require(multiply(u, transpose(u)) == eye(n), "orthogonal fixture")
    return u


def matrix_fixtures():
    matrices, rows, equality_rows = 0, 0, 0
    for n in range(1, 9):
        for seed in range(8):
            u, v = rotation(n, seed), rotation(n, seed + 3)
            spectrum = [F(1 + (i + seed) % 4) for i in range(n)]
            scaled = [[u[i][j] * spectrum[j] for j in range(n)] for i in range(n)]
            a = multiply(scaled, transpose(v))
            inv = inverse(a)
            require(multiply(a, inv) == eye(n), "dense inverse fixture")
            low, high = min(spectrum) ** 2, max(spectrum) ** 2
            for i in range(n):
                r = sum(x * x for x in a[i])
                l = sum(inv[j][i] ** 2 for j in range(n))
                require(4 * low * high * r * l <= (low + high) ** 2,
                        "Kantorovich fixture")
                rows += 1
                equality_rows += (4 * low * high * r * l == (low + high) ** 2)
            matrices += 1
    return {"matrices": matrices, "rows": rows, "equality_rows": equality_rows}


def controls():
    bad = [lambda: envelope(F(0)), lambda: envelope(F(1, 2)),
           lambda: envelope(True), lambda: envelope(2),
           lambda: witness(F(17)), lambda: witness(F(0)),
           lambda: inverse([[F(0)]]), lambda: eye(9)]
    rejected = 0
    for action in bad:
        try:
            action()
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid input accepted")
    s = coefficient_matrix(F(5, 4), F(3, 4))
    try:
        pairings(s, s, 0)
    except ValueError:
        rejected += 1
    else:
        raise ValueError("false inverse accepted")
    require(envelope(F(2)) > 1, "unitary-only false bound rejected")
    require(envelope(F(2)) < envelope(F(4)), "squared condition confusion")
    require(envelope(F(9, 8)) < F(9, 8), "old 9/8 threshold is strictly weaker")
    require(envelope(F(41, 25)) < F(9, 8), "strict rational threshold")
    return {"invalid_inputs_rejected": rejected, "semantic_controls": 4}


def bounded_bytes(path):
    require(path.stat().st_size <= 262144, "file capacity")
    return path.read_bytes()


def main():
    require(len(sys.argv) == 1, "no command line arguments")
    parameters = sorted({F(p, q) for q in range(1, 17) for p in range(q, 17)})
    total = F(0)
    for v in parameters:
        total += witness(v)
    require(witness(F(1)) == 1, "unitary boundary")
    result = {"status": "PASS_SHARP_RANK_CONDITIONING",
              "witness_parameters": len(parameters), "increment_sum": str(total),
              "matrix_fixtures": matrix_fixtures(), "controls": controls()}
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    result["sha256"] = {name: hashlib.sha256(bounded_bytes(package / name)).hexdigest()
                        for name in names}
    sources = json.loads(bounded_bytes(package / "SOURCES.json"))
    source = next(row for row in sources["files"] if row["usage"] == "input")
    expected_path = "research/signed-rank-transport/PROOF.md"
    require(source["path"] == expected_path, "exact mathematical source path")
    digest = hashlib.sha256(bounded_bytes(package.parents[1] / expected_path)).hexdigest()
    require(digest == source["sha256"], "cited proof source identity")
    result["source_sha256"] = digest
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
