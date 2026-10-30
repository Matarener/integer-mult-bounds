#!/usr/bin/env python3
"""Exact, standard-library finite checks of the 2x2 Jordan callee count."""

import itertools
import json
import platform
from collections import Counter


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


class Field:
    """Polynomial-basis F_p[x]/(monic polynomial), encoded in base p."""

    def __init__(self, p, polynomial):
        self.p = p
        self.polynomial = polynomial
        self.degree = len(polynomial) - 1
        self.q = p ** self.degree
        digits = [tuple((a // p**i) % p for i in range(self.degree))
                  for a in range(self.q)]
        self.add = [[sum(((x + y) % p) * p**i
                         for i, (x, y) in enumerate(zip(a, b)))
                     for b in digits] for a in digits]
        self.mul = [[self.multiply(a, b) for b in digits] for a in digits]
        self.neg = [next(b for b in range(self.q) if self.add[a][b] == 0)
                    for a in range(self.q)]
        self.inv = [0] + [next(b for b in range(1, self.q)
                              if self.mul[a][b] == 1)
                          for a in range(1, self.q)]

    def multiply(self, a, b):
        d, p = self.degree, self.p
        coefficients = [0] * (2 * d - 1)
        for i, x in enumerate(a):
            for j, y in enumerate(b):
                coefficients[i + j] += x * y
        for k in range(2 * d - 2, d - 1, -1):
            value = coefficients[k] % p
            for j in range(d + 1):
                coefficients[k - d + j] -= value * self.polynomial[j]
        return sum((coefficients[i] % p) * p**i for i in range(d))

    def validate(self):
        a, m, q = self.add, self.mul, self.q
        for x, y, z in itertools.product(range(q), repeat=3):
            require(a[a[x][y]][z] == a[x][a[y][z]], "add associativity")
            require(m[m[x][y]][z] == m[x][m[y][z]], "mul associativity")
            require(m[x][a[y][z]] == a[m[x][y]][m[x][z]], "distributivity")
        for x, y in itertools.product(range(q), repeat=2):
            require(a[x][y] == a[y][x] and m[x][y] == m[y][x], "commutativity")
        for x in range(q):
            require(a[x][0] == x and m[x][1] == x, "identities")
            require(a[x][self.neg[x]] == 0, "additive inverse")
            if x:
                require(m[x][self.inv[x]] == 1, "multiplicative inverse")


ZERO = (0, 0, 0, 0)
IDENTITY = (1, 0, 0, 1)


def add(f, x, y):
    return tuple(f.add[a][b] for a, b in zip(x, y))


def sub(f, x, y):
    return tuple(f.add[a][f.neg[b]] for a, b in zip(x, y))


def mm(f, x, y):
    a, m = f.add, f.mul
    return tuple(a[m[x[2*i]][y[j]]][m[x[2*i+1]][y[2+j]]]
                 for i in range(2) for j in range(2))


def mv(f, x, y):
    a, m = f.add, f.mul
    return tuple(a[m[x[2*i]][y[0]]][m[x[2*i+1]][y[1]]]
                 for i in range(2))


def det(f, x):
    return f.add[f.mul[x[0]][x[3]]][f.neg[f.mul[x[1]][x[2]]]]


def inverse(f, x):
    d = det(f, x)
    require(d != 0, "attempt to invert singular matrix")
    return tuple(f.mul[f.inv[d]][a]
                 for a in (x[3], f.neg[x[1]], f.neg[x[2]], x[0]))


def rank(f, rows):
    rows = [list(row) for row in rows]
    result = 0
    for col in range(len(rows[0])):
        pivot = next((i for i in range(result, len(rows)) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[result], rows[pivot] = rows[pivot], rows[result]
        scale = f.inv[rows[result][col]]
        rows[result] = [f.mul[scale][v] for v in rows[result]]
        for i in range(result + 1, len(rows)):
            factor = rows[i][col]
            rows[i] = [f.add[x][f.neg[f.mul[factor][y]]]
                       for x, y in zip(rows[i], rows[result])]
        result += 1
        if result == len(rows):
            break
    return result


def wrapper_rank(f, p, pinv, q, qinv):
    """Execute the six literal operations on all four basis vectors."""
    columns = []
    for k in range(4):
        initial = tuple(int(k == j) for j in range(4))
        h, d = initial[:2], initial[2:]
        d = sub(f, d, h)
        h, d = mv(f, p, d), mv(f, pinv, h)
        d = add(f, d, h)
        h, d = mv(f, q, d), mv(f, qinv, h)
        d = tuple(f.neg[x] for x in d)
        d = add(f, d, h)
        columns.append(sub(f, h + d, initial[2:] + initial[:2]))
    return rank(f, list(zip(*columns)))


def check_parameters(f, lam, square_zero):
    q, a, m = f.q, f.add, f.mul
    p = (lam, 1, 0, lam)
    aa = sub(f, mm(f, p, p), IDENTITY)
    l2 = m[lam][lam]
    coefficient = a[l2][1]
    histogram, accepted = Counter(), set()
    for s in square_zero:
        candidate = add(f, p, mm(f, aa, s))
        determinant = det(f, candidate)
        require(determinant == a[l2][m[coefficient][s[2]]], "determinant identity")
        histogram[determinant] += 1
        if determinant:
            accepted.add(candidate)
    predicted = q*q if coefficient == 0 else q*q-q
    require(len(accepted) == predicted, "filtered cardinality")
    expected_histogram = ({l2: q*q} if coefficient == 0
                          else {value: q for value in range(q)})
    require(dict(histogram) == expected_histogram, "full determinant distribution")
    if coefficient:
        c = f.neg[m[l2][f.inv[coefficient]]]
        excluded = {(x, f.neg[m[m[x][x]][f.inv[c]]], c, f.neg[x])
                    for x in range(q)}
        actual = {s for s in square_zero if det(f, add(f, p, mm(f, aa, s))) == 0}
        require(actual == excluded and len(actual) == q, "exact rejection family")
    return accepted, histogram[0]


def check_field(f):
    f.validate()
    q = f.q
    square_zero = {s for s in itertools.product(range(q), repeat=4)
                   if mm(f, s, s) == ZERO}
    parameterized = {(a, b, c, f.neg[a])
                     for a, b, c in itertools.product(range(q), repeat=3)
                     if f.add[f.mul[a][a]][f.mul[b][c]] == 0}
    require(square_zero == parameterized and len(square_zero) == q*q,
            "square-zero parameterization")
    records, candidates = [], 0
    invertibles = ([(s, inverse(f, s))
                    for s in itertools.product(range(q), repeat=4) if det(f, s)]
                   if q <= 9 else [])
    for lam in range(1, q):
        p = (lam, 1, 0, lam)
        l2 = f.mul[lam][lam]
        if l2 == 1:
            predicted_set, rejected = {p}, None
        else:
            predicted_set, rejected = check_parameters(f, lam, square_zero)
        observed = None
        if invertibles:
            aa = sub(f, mm(f, p, p), IDENTITY)
            minimum = rank(f, [aa[:2], aa[2:]])
            pinv, optimal = inverse(f, p), set()
            for candidate, qinv in invertibles:
                error_rank = wrapper_rank(f, p, pinv, candidate, qinv)
                require(error_rank >= minimum, "known minimum error rank")
                if error_rank == minimum:
                    optimal.add(candidate)
            require(optimal == predicted_set, "literal wrapper optimal set")
            observed = len(optimal)
            candidates += len(invertibles)
        records.append({"lambda_encoding": lam, "lambda_squared": l2,
                        "optimal_count": len(predicted_set),
                        "singular_square_zero_parameters": rejected,
                        "literal_wrapper_optimal_count": observed})
    return {"q": q, "characteristic": f.p, "polynomial_low_to_high": f.polynomial,
            "square_zero_matrices": len(square_zero), "all_matrices_checked": q**4,
            "literal_wrapper_pairs": candidates, "cases": records}


def main():
    specifications = [(2, [0, 1]), (3, [0, 1]), (2, [1, 1, 1]),
                      (5, [0, 1]), (7, [0, 1]), (2, [1, 1, 0, 1]),
                      (3, [1, 0, 1]), (11, [0, 1]), (13, [0, 1]),
                      (2, [1, 1, 0, 0, 1])]
    results = [check_field(Field(p, polynomial)) for p, polynomial in specifications]
    receipt = {"status": "PASS_JORDAN_CALLEE_COUNT", "python": platform.python_version(),
               "field_count": len(results),
               "first_maps": sum(len(item["cases"]) for item in results),
               "all_matrices_checked": sum(item["all_matrices_checked"] for item in results),
               "literal_wrapper_pairs": sum(item["literal_wrapper_pairs"] for item in results),
               "fields": results}
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
