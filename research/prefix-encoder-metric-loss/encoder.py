"""Exact finite prefix-encoder tables and metric obstruction witnesses.

Produced by Nick Petalas. Apache-2.0.
"""

from fractions import Fraction as Q
from itertools import product


def require(condition, message):
    if not condition:
        raise ValueError(message)


def group(table):
    """Validate a small Cayley table, with identity labelled zero."""
    q = len(table)
    require(1 <= q <= 6, "group order outside 1..6")
    require(all(len(row) == q for row in table), "Cayley shape")
    require(all(type(x) is int and 0 <= x < q for row in table for x in row),
            "Cayley entries")
    require(all(table[0][a] == a == table[a][0] for a in range(q)), "identity")
    for a in range(q):
        require(any(table[a][b] == 0 == table[b][a] for b in range(q)), "inverse")
    for a, b, c in product(range(q), repeat=3):
        require(table[table[a][b]][c] == table[a][table[b][c]], "associativity")
    return q


def encode(word, q):
    result = 0
    for letter in word:
        result = q * result + letter
    return result


def prefixes(table, initial, word):
    current = initial
    output = []
    for letter in word:
        current = table[current][letter]
        output.append(current)
    return tuple(output)


def local_permutation(table, block):
    """Columns (final virtual state, input); rows (initial state, output)."""
    q = group(table)
    require(type(block) is int and 1 <= block <= 6, "positive block length <=6")
    m = q ** block
    require(q * m <= 216, "local state capacity 216")
    permutation = [-1] * (q * m)
    for initial in range(q):
        for word in product(range(q), repeat=block):
            output = prefixes(table, initial, word)
            column = output[-1] * m + encode(word, q)
            row = initial * m + encode(output, q)
            require(permutation[column] == -1, "duplicate physical column")
            permutation[column] = row
    require(sorted(permutation) == list(range(q * m)), "local unitarity")
    return tuple(permutation), m


def metric_relations(permutation, m, q):
    """All coefficient equations of L* (P tensor I) L = P tensor I."""
    n = len(permutation)
    require(n == q * m and n <= 216, "metric dimensions")
    require(sorted(permutation) == list(range(n)), "invalid permutation")
    relations = set()
    for i in range(n):
        ai, yi = divmod(permutation[i], m)
        bi, xi = divmod(i, m)
        for j in range(n):
            aj, yj = divmod(permutation[j], m)
            bj, xj = divmod(j, m)
            row = {}
            if yi == yj:
                row[ai * q + aj] = 1
            if xi == xj:
                key = bi * q + bj
                row[key] = row.get(key, 0) - 1
            nonzero = tuple(sorted((key, val) for key, val in row.items() if val))
            if nonzero:
                relations.add(nonzero)
    return tuple(sorted(relations)), n * n


def relation_rank(relations, variables):
    require(1 <= variables <= 36 and len(relations) <= 2592, "rank capacity")
    basis = {}
    for sparse in relations:
        row = [Q(0)] * variables
        for key, value in sparse:
            row[key] = Q(value)
        for pivot in sorted(basis):
            factor = row[pivot]
            row = [a - factor * b for a, b in zip(row, basis[pivot])]
        pivot = next((i for i, value in enumerate(row) if value), None)
        if pivot is not None:
            factor = row[pivot]
            basis[pivot] = tuple(value / factor for value in row)
    return len(basis)


def defect_entry(real, imaginary, permutation, m, i, j):
    """Entry of Q = P tensor I - L* (P tensor I) L."""
    bi, xi = divmod(i, m)
    bj, xj = divmod(j, m)
    ai, yi = divmod(permutation[i], m)
    aj, yj = divmod(permutation[j], m)
    re = real[bi][bj] if xi == xj else Q(0)
    im = imaginary[bi][bj] if xi == xj else Q(0)
    if yi == yj:
        re -= real[ai][aj]
        im -= imaginary[ai][aj]
    return re, im


def negative_witness(real, imaginary, permutation, m):
    """Return a rational Gaussian vector with negative contraction residual."""
    q = len(real)
    require(1 <= q <= 6 and len(imaginary) == q, "Hermitian metric dimension")
    require(all(len(row) == q for row in real + imaginary), "metric shape")
    for i, j in product(range(q), repeat=2):
        require(real[i][j] == real[j][i] and imaginary[i][j] == -imaginary[j][i],
                "metric must be Hermitian")
    n = len(permutation)
    require(n == q * m and n <= 216, "witness capacity")
    diagonal = [defect_entry(real, imaginary, permutation, m, i, i)[0]
                for i in range(n)]
    require(sum(diagonal) == 0, "unitary trace identity")
    for i, value in enumerate(diagonal):
        if value < 0:
            return ((i, Q(1), Q(0)),), value
    require(all(value == 0 for value in diagonal), "nonnegative trace zero")
    for i in range(n):
        for j in range(i + 1, n):
            re, im = defect_entry(real, imaginary, permutation, m, i, j)
            if re:
                sign = -1 if re > 0 else 1
                return ((i, Q(1), Q(0)), (j, Q(sign), Q(0))), -2 * abs(re)
            if im:
                sign = 1 if im > 0 else -1
                return ((i, Q(1), Q(0)), (j, Q(0), Q(sign))), -2 * abs(im)
    return (), Q(0)
