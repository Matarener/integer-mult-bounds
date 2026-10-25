#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Chris R / Clear1nsight, with substantial OpenAI Codex assistance.
"""Fixed-support local-ring reduction, not a physical tape interpreter.

Generic split-projector conjugation is predecessor work (PR2234, PR1627).
This implementation normalizes only a kernel column, emits a fixed-support
SL word and exposes every reverse-order adapter in the caller invoice.
"""
from fractions import Fraction
from math import gcd


def need(ok, why):
    if not ok:
        raise ValueError(why)


def eye(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def mul(a, b, modulus):
    out = [[0] * len(b[0]) for _ in a]
    for i, row in enumerate(a):
        for k, x in enumerate(row):
            if x:
                for j, y in enumerate(b[k]):
                    if y:
                        out[i][j] = (out[i][j] + x * y) % modulus
    return out


def inverse(a, modulus):
    n = len(a)
    rows = [list(row) + unit for row, unit in zip(a, eye(n))]
    for j in range(n):
        k = next((i for i in range(j, n) if gcd(rows[i][j], modulus) == 1), None)
        need(k is not None, "unit pivot required")
        rows[j], rows[k] = rows[k], rows[j]
        inv = pow(rows[j][j], -1, modulus)
        rows[j] = [x * inv % modulus for x in rows[j]]
        for i in range(n):
            if i != j:
                c = rows[i][j]
                rows[i] = [(x - c * y) % modulus for x, y in zip(rows[i], rows[j])]
    return [row[n:] for row in rows]


def determinant(a, modulus):
    rows, value, n = [list(row) for row in a], 1, len(a)
    for j in range(n):
        k = next((i for i in range(j, n) if gcd(rows[i][j], modulus) == 1), None)
        need(k is not None, "invertible local-ring matrix")
        if k != j:
            rows[j], rows[k] = rows[k], rows[j]
            value = -value
        pivot = rows[j][j]
        value = value * pivot % modulus
        for i in range(j + 1, n):
            c = rows[i][j] * pow(pivot, -1, modulus) % modulus
            rows[i] = [(x - c * y) % modulus for x, y in zip(rows[i], rows[j])]
    return value % modulus


def independent_columns(a, q):
    """Column independence over the residue field, with original ordinals."""
    rows = [[x % q for x in row] for row in a]
    selected, pivot = [], 0
    for column in range(len(a[0])):
        k = next((i for i in range(pivot, len(a)) if rows[i][column]), None)
        if k is None:
            continue
        rows[pivot], rows[k] = rows[k], rows[pivot]
        inv = pow(rows[pivot][column], -1, q)
        rows[pivot] = [x * inv % q for x in rows[pivot]]
        for i in range(len(a)):
            if i != pivot:
                c = rows[i][column]
                rows[i] = [(x - c * y) % q for x, y in zip(rows[i], rows[pivot])]
        selected.append(column)
        pivot += 1
        if pivot == len(a):
            break
    return selected


def split_basis(p, rank, q, modulus):
    n = len(p)
    complement = [[(int(i == j) - p[i][j]) % modulus for j in range(n)] for i in range(n)]
    image = independent_columns(p, q)
    kernel = independent_columns(complement, q)
    need(len(image) == rank and len(kernel) == n - rank, "split ranks from residue field")
    basis = [[p[i][j] for j in image] + [complement[i][j] for j in kernel] for i in range(n)]
    e = [[int(i == j and i < rank) for j in range(n)] for i in range(n)]
    need(mul(p, basis, modulus) == mul(basis, e, modulus), "image/kernel basis")
    need(gcd(determinant(basis, modulus), modulus) == 1, "split basis is a unit")
    return basis


def normalize_kernel(s, rank, modulus):
    """Right multiplication in ker(E) commutes with the central interchange."""
    need(0 < rank < len(s), "nonempty image and kernel")
    out = [list(row) for row in s]
    value = determinant(s, modulus)
    multiplier = pow(value, -1, modulus)
    for row in out:
        row[rank] = row[rank] * multiplier % modulus
    need(determinant(out, modulus) == 1, "special linear normalization")
    return out


def support_bound(n):
    need(n >= 2, "factor dimension")
    return (n - 1) * (5 * n + 12) // 2


def row_add(rows, target, source, coefficient, modulus):
    rows[target] = [(x + coefficient * y) % modulus for x, y in zip(rows[target], rows[source])]


def factor_sl(s, modulus):
    """Chronological left actions, with identical (target,source) support.

Zero coefficients are deliberately emitted and charged. Pivot selection is
numeric preparation; the factor support and length never depend on it.
"""
    n = len(s)
    need(determinant(s, modulus) == 1, "SL input")
    rows, reduction = [list(row) for row in s], []

    def emit(i, j, c):
        c %= modulus
        row_add(rows, i, j, c, modulus)
        reduction.append((i, j, c))

    for j in range(n):
        pivot = next((i for i in range(j, n) if gcd(rows[i][j], modulus) == 1), None)
        need(pivot is not None, "local-ring elimination unit")
        for k in range(j + 1, n):
            chosen = int(pivot == k)
            emit(j, k, chosen)
            emit(k, j, -chosen)
            emit(j, k, chosen)
        inv = pow(rows[j][j], -1, modulus)
        for i in range(n):
            if i != j:
                emit(i, j, -rows[i][j] * inv)
    diagonal = [rows[i][i] for i in range(n)]
    need(all(rows[i][j] == (diagonal[i] if i == j else 0) for i in range(n) for j in range(n)), "diagonal endpoint")
    word = []
    for i, a in enumerate(diagonal[:-1]):
        last = n - 1
        # w(a)w(-1) = diag(a,a^-1); actions accumulate on the left.
        word.extend([(i, last, -1), (last, i, 1), (i, last, -1),
                     (i, last, a), (last, i, -pow(a, -1, modulus)), (i, last, a)])
    word.extend((i, j, -c) for i, j, c in reversed(reduction))
    word = [(i, j, c % modulus) for i, j, c in word]
    need(len(word) == support_bound(n), "fixed factor bound")
    return word


def word_matrix(word, n, modulus):
    out = eye(n)
    for i, j, c in word:
        need(i != j and 0 <= i < n and 0 <= j < n, "elementary support")
        row_add(out, i, j, c, modulus)
    return out


def projector(lines, indices):
    """Independent orthogonal elimination from the retained E8 root rows."""
    orthogonal = []
    for index in indices:
        v = list(map(Fraction, lines[index]))
        for b in orthogonal:
            c = sum(x * y for x, y in zip(v, b)) / sum(y * y for y in b)
            v = [x - c * y for x, y in zip(v, b)]
        if any(v):
            orthogonal.append(v)
    n = len(lines[0])
    p = [[sum((b[i] * b[j] / sum(y * y for y in b) for b in orthogonal), Fraction(0))
          for j in range(n)] for i in range(n)]
    return p, len(orthogonal)


def reduce_rational(a, modulus):
    return [[x.numerator * pow(x.denominator, -1, modulus) % modulus for x in row] for row in a]


def block_diagonal(a, b):
    n = len(a)
    return [row + [0] * n for row in a] + [[0] * n + row for row in b]


def residual(p, weights, modulus):
    """Tail is written in reflected coordinates; physical reversal is external."""
    n = len(p)
    out = [[0] * (2 * n) for _ in range(2 * n)]
    for i in range(n):
        for j in range(n):
            c = (int(i == j) - p[i][j]) % modulus
            out[i][j] = weights[i] * c * pow(weights[j], -1, modulus) % modulus
            out[i][n + j] = weights[i] * p[i][j] % modulus
            out[n + i][j] = p[i][j] * pow(weights[j], -1, modulus) % modulus
            out[n + i][n + j] = c
    return out


def compile_copy(p, rank, g, weights, q, modulus):
    n = len(p)
    need(all(gcd(a, modulus) == 1 for a in weights), "incoming diagonal units")
    basis = split_basis(p, rank, q, modulus)
    u = mul(g, basis, modulus)
    head = [[weights[i] * x % modulus for x in row] for i, row in enumerate(u)]
    head, tail = normalize_kernel(head, rank, modulus), normalize_kernel(u, rank, modulus)
    head_word, tail_word = factor_sl(head, modulus), factor_sl(tail, modulus)
    need(word_matrix(head_word, n, modulus) == head, "head word")
    need(word_matrix(tail_word, n, modulus) == tail, "tail word")
    k = block_diagonal(head, tail)
    e = [[int(i == j and i < rank) for j in range(n)] for i in range(n)]
    central = residual(e, [1] * n, modulus)
    endpoint = mul(mul(k, central, modulus), inverse(k, modulus), modulus)
    conjugate = mul(mul(g, p, modulus), inverse(g, modulus), modulus)
    expected = residual(conjugate, weights, modulus)
    need(endpoint == expected, "complete weighted conjugate, not a rank-only test")
    return dict(head=head_word, tail=tail_word, matrix=endpoint, conjugator=k)


def invoice(dimension=64, columns=1, prefixes=1):
    need(dimension > 7 and columns >= 1 and prefixes >= 1, "COPY invoice domain")
    length = support_bound(dimension)
    # Four words: head/tail and their inverses; all factors are paid.
    slots = 4 * length
    return dict(factor_slots=slots, ordered_shear_calls=slots * columns,
                reverse_factor_slots=2 * length,
                ordinary_block_swap_calls_upper=4 * length,
                ordinary_block_width_atoms=columns,
                coarse_calls=1, coarse_width_atoms=7 * columns,
                prefix_multiplier_on_coarse_calls=1,
                physical_prefixes=prefixes, clone_episodes=1, disposal_episodes=1,
                intermediate_disposals_upper=slots * columns + 4 * length + 1)
