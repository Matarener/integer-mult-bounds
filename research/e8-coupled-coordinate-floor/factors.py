"""Small exact constructions and hypothesis controls for the coupled theorem.

Prepared by conorholds with substantial OpenAI Codex assistance. Apache-2.0.
This primary implementation reuses retained PR3755 geometry. independent_model.py
constructs its roots and performs all scalar/binary calculations separately.
"""

from fractions import Fraction
from math import lcm

from vendor.pr3755 import geometry as g


def add(*vectors):
    return [sum(values) for values in zip(*vectors)]


def scale(value, vector):
    return [value * x for x in vector]


def unit(index):
    return [Fraction(i == index) for i in range(120)]


def frame(roots):
    chosen = []
    for pair in range(4):
        for sign in (1, -1):
            r = [0] * 8
            r[2 * pair], r[2 * pair + 1] = 2, 2 * sign
            chosen.append(next(i for i, row in enumerate(roots) if g.canonical(row) == tuple(r)))
    g.require(len(set(chosen)) == 8, "frame line identification")
    g.require(all(g.dot(roots[i], roots[j]) == 8 * int(i == j)
                  for i in chosen for j in chosen), "oriented orthogonal frame")
    return chosen


def construction(roots, k):
    g.require(1 <= k <= 8, "coordinate-family size")
    positions = frame(roots)
    evaluations = [[Fraction(g.dot(row, roots[i]), 4) for row in roots] for i in positions]
    a = positions[0]
    R = add(evaluations[0], scale(-4, unit(a)))
    H = add(evaluations[0], scale(-2, unit(a)))
    P, Q = [H], [unit(a)]
    for i in range(1, k):
        P.append(add(scale(Fraction(1, 2), evaluations[i]), scale(Fraction(-1, 4), R)))
        Q.append(unit(positions[i]))
    P.append(scale(Fraction(1, 4), R))
    Q.append(add(R, *[unit(positions[i]) for i in range(1, k)]))
    for i in range(1, k):
        P.append(scale(Fraction(-1, 2), evaluations[i]))
        Q.append(add(unit(positions[i]), scale(Fraction(-1, 2), evaluations[i])))
    for i in range(k, 8):
        P.append(scale(Fraction(1, 4), evaluations[i]))
        Q.append(evaluations[i])
    P.append(unit(a))
    Q.append(H)
    expected = [0] + [1] * (k - 1) + [9] + [8] * (k - 1) + [9] * (8 - k) + [0]
    return P, Q, positions[:k], expected


def reduce_scalar(value, prime):
    value = Fraction(value)
    return value if prime == 0 else value.numerator * pow(value.denominator, -1, prime) % prime


def reduce_columns(columns, prime):
    return [[reduce_scalar(x, prime) for x in column] for column in columns]


def scalar_rank(columns, prime):
    if prime == 0:
        return g.rational_rank(columns)
    rows = [list(column) for column in columns]
    rank = 0
    for j in range(len(rows[0]) if rows else 0):
        k = next((i for i in range(rank, len(rows)) if rows[i][j]), None)
        if k is None:
            continue
        rows[rank], rows[k] = rows[k], rows[rank]
        inv = pow(rows[rank][j], -1, prime)
        rows[rank] = [x * inv % prime for x in rows[rank]]
        for i in range(rank + 1, len(rows)):
            c = rows[i][j]
            if c:
                rows[i] = [(x - c * y) % prime for x, y in zip(rows[i], rows[rank])]
        rank += 1
        if rank == len(rows):
            break
    return rank


def normalize_left(P, Q, prime):
    groups = {}
    for p, q in zip(P, Q):
        if not any(p) or not any(q):
            continue
        first = next(x for x in p if x)
        reciprocal = Fraction(1, first) if prime == 0 else pow(first, -1, prime)
        ray = tuple(reduce_scalar(x * reciprocal, prime) for x in p)
        scaled_q = [reduce_scalar(first * x, prime) for x in q]
        if ray in groups:
            groups[ray] = [reduce_scalar(x + y, prime) for x, y in zip(groups[ray], scaled_q)]
        else:
            groups[ray] = scaled_q
    pairs = [(list(p), q) for p, q in groups.items() if any(q)]
    return [p for p, q in pairs], [q for p, q in pairs]


def product_check(roots, P, Q, prime):
    g.require(len(P) == len(Q) and all(len(x) == 120 for x in P + Q), "factor dimensions")
    if prime == 0:
        dp = lcm(*(x.denominator for p in P for x in p))
        dq = lcm(*(x.denominator for q in Q for x in q))
        pints = [[int(x * dp) for x in p] for p in P]
        qints = [[int(x * dq) for x in q] for q in Q]
        for i, r in enumerate(roots):
            for j, s in enumerate(roots):
                value = sum(p[i] * q[j] for p, q in zip(pints, qints))
                g.require(8 * value == g.dot(r, s) * dp * dq, "exact decoder product")
    else:
        inv8 = pow(8, -1, prime)
        for i, r in enumerate(roots):
            for j, s in enumerate(roots):
                value = sum(p[i] * q[j] for p, q in zip(P, Q)) % prime
                g.require(value == g.dot(r, s) * inv8 % prime, "exact decoder product")


def check_factorization(model, roots, P, Q, prime, actual_coordinates=None):
    g.require(all(any(p) and any(q) for p, q in zip(P, Q)), "inactive factor term")
    product_check(roots, P, Q, prime)
    costs = [g.copy_rank(model, p, q) for p, q in zip(P, Q)]
    ranks = [scalar_rank(P, prime), scalar_rank(Q, prime)]
    if actual_coordinates is not None:
        code = reduce_columns([[Fraction(row[j], 2) for row in roots] for j in range(8)], prime)
        declared = code + reduce_columns([unit(i) for i in actual_coordinates], prime)
        g.require(scalar_rank(declared, prime) == scalar_rank(Q + declared, prime) == ranks[1],
                  "actual right space differs from declared full coordinate space")
    return {"terms": len(P), "ranks": ranks, "costs": costs, "copy": sum(costs)}


def expect_failure(function, message):
    try:
        function()
    except ValueError as error:
        g.require(message in str(error), "failure control rejected for unrelated reason")
        return
    raise ValueError("deliberate mathematical fault was accepted: " + message)


def run(model, roots):
    result = {}
    for prime in (0, 3, 5, 7):
        cases = []
        for k in range(1, 9):
            p, q, A, expected = construction(roots, k)
            P, Q = reduce_columns(p, prime), reduce_columns(q, prime)
            record = check_factorization(model, roots, P, Q, prime, A)
            g.require(record["costs"] == expected and record["copy"] == 72,
                      "coordinate-family charge profile")
            g.require(record["ranks"] == [9, 8 + k], "coordinate-family actual ranks")
            left, right = normalize_left(P, Q, prime)
            swapped_q, swapped_p = normalize_left(Q, P, prime)
            g.require(len(left) == len(swapped_q) == len(P), "equality fixture collapses under a ray merge")
            g.require(scalar_rank(left, prime) == 9 and scalar_rank(right, prime) == 8 + k,
                      "merged equality fixture loses actual rank")
            record["k"] = k
            cases.append(record)
        p, q, A, expected = construction(roots, 2)
        P, Q = reduce_columns(p, prime), reduce_columns(q, prime)
        expect_failure(lambda: product_check(roots, P[:-1], Q[:-1], prime), "exact decoder product")
        broken = [list(x) for x in Q]
        broken[2] = reduce_columns([add(q[2], scale(-1, unit(A[1])))], prime)[0]
        expect_failure(lambda: product_check(roots, P, broken, prime), "exact decoder product")
        expect_failure(lambda: product_check(roots, [scale(2, x) for x in P], Q, prime),
                       "exact decoder product")
        p1, q1, A1, _ = construction(roots, 1)
        P1, Q1 = reduce_columns(p1, prime), reduce_columns(q1, prime)
        expect_failure(lambda: check_factorization(model, roots, P1, Q1, prime, A),
                       "actual right space")
        positions = frame(roots)
        code = [[Fraction(g.dot(row, roots[i]), 4) for row in roots] for i in positions]
        rawP = [scale(Fraction(1, 4), x) for x in code]
        rawQ = list(code)
        v = positions[0]
        b = next(i for i, r in enumerate(roots) if i != v and g.dot(r, roots[v]))
        free_hole_reader = add(code[0], scale(-2, unit(v)))
        for reader in (free_hole_reader, unit(b)):
            rawP += [unit(v), scale(-1, unit(v))]
            rawQ += [reader, reader]
        RP, RQ = reduce_columns(rawP, prime), reduce_columns(rawQ, prime)
        padded = check_factorization(model, roots, RP, RQ, prime, [v, b])
        g.require(padded["ranks"] == [9, 10] and padded["costs"] == [9] * 8 + [0] * 4,
                  "raw-rank cancellation counterexample")
        NP, NQ = normalize_left(RP, RQ, prime)
        collapsed = check_factorization(model, roots, NP, NQ, prime)
        g.require(collapsed["ranks"] == [8, 8] and collapsed["copy"] == 72,
                  "raw-rank control did not merge back to the frame")
        result[str(prime) if prime else "Q"] = {"coordinate_family": cases,
            "product_fault_controls": 3, "actual_space_contract_controls": 1,
            "raw_rank_counterexample": padded, "after_left_merge": collapsed}
    return result
