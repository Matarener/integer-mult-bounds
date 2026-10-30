"""Exact, bounded finite censuses for the extreme-rank counting theorem."""

from itertools import product
from math import gcd


VECTOR_DOMAINS = ((3, 2), (3, 3), (3, 4), (3, 5), (5, 2),
                  (5, 3), (5, 4), (7, 2), (7, 3), (11, 2))
MATRIX_DOMAINS = ((3, 1, 2), (5, 1, 2), (7, 1, 2), (3, 2, 2),
                  (5, 2, 2), (3, 3, 2), (3, 1, 3))
HEADER_DOMAINS = ((3, 1, 2), (5, 1, 2), (3, 2, 2), (5, 2, 2), (3, 1, 3))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def matrix(flat, m):
    return tuple(tuple(flat[i*m:(i+1)*m]) for i in range(m))


def determinant(rows, q):
    a = [list(row) for row in rows]
    m = len(a)
    value = 1
    for k in range(m):
        pivot = next((i for i in range(k, m) if a[i][k] % q), None)
        if pivot is None:
            return 0
        if pivot != k:
            a[k], a[pivot] = a[pivot], a[k]
            value = -value
        value = value * a[k][k] % q
        inverse = pow(a[k][k], -1, q)
        for i in range(k+1, m):
            factor = a[i][k] * inverse % q
            for j in range(k+1, m):
                a[i][j] = (a[i][j] - factor*a[k][j]) % q
    return value % q


def good(projector, rank, q):
    return all(determinant(tuple(row[:k] for row in projector[:k]), q)
               for k in range(1, rank+1))


def formula(q, m, rank):
    need(m >= 2 and rank in (1, m-1), "extreme-rank formula domain")
    total = (q**m-1) * q**(m-1) // (q-1)
    if rank == 1:
        admitted = q**(m-2) * ((q-1)*q**(m-1)+1)
    else:
        admitted = (q*q-q+1)**(m-1)
    return total, admitted


def factorizations(q, m):
    """One representative per rank-one projector, with first nonzero u equal 1."""
    for pivot in range(m):
        for tail in product(range(q), repeat=m-pivot-1):
            u = (0,)*pivot + (1,) + tail
            for free in product(range(q), repeat=m-1):
                v = list(free[:pivot]) + [0] + list(free[pivot:])
                v[pivot] = (1-sum(u[i]*v[i] for i in range(m))) % q
                yield u, tuple(v)


def outer(u, v, q, complement=False):
    m = len(u)
    if complement:
        return tuple(tuple((int(i == j)-u[i]*v[j]) % q
                           for j in range(m)) for i in range(m))
    return tuple(tuple(u[i]*v[j] % q for j in range(m)) for i in range(m))


def vector_census(q, m):
    seen = set()
    counts = [0, 0]
    for u, v in factorizations(q, m):
        p = outer(u, v, q)
        need(p not in seen, "duplicate canonical rank-one projector")
        seen.add(p)
        counts[0] += int(good(p, 1, q))
        counts[1] += int(good(outer(u, v, q, True), m-1, q))
    for rank, admitted in zip((1, m-1), counts):
        need((len(seen), admitted) == formula(q, m, rank), "vector formula mismatch")
    return {"q": q, "m": m, "total_per_rank": len(seen),
            "good_rank_one": counts[0], "good_corank_one": counts[1]}


def idempotent(p, modulus):
    m = len(p)
    return all((sum(p[i][k]*p[k][j] for k in range(m))-p[i][j]) % modulus == 0
               for i in range(m) for j in range(m))


def field_rank(p, q):
    a = [list(row) for row in p]
    m, rank = len(a), 0
    for column in range(m):
        pivot = next((i for i in range(rank, m) if a[i][column] % q), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        inverse = pow(a[rank][column] % q, -1, q)
        a[rank] = [x*inverse % q for x in a[rank]]
        for i in range(rank+1, m):
            factor = a[i][column] % q
            a[i] = [(x-factor*y) % q for x, y in zip(a[i], a[rank])]
        rank += 1
    return rank


def matrix_census(q, w, m):
    modulus = q**w
    counts = {r: [0, 0] for r in sorted({1, m-1})}
    for flat in product(range(modulus), repeat=m*m):
        p = matrix(flat, m)
        if not idempotent(p, modulus):
            continue
        rank = field_rank(p, q)
        if rank in counts:
            counts[rank][0] += 1
            counts[rank][1] += int(good(p, rank, q))
    for rank, pair in counts.items():
        lift = q**(2*rank*(m-rank)*(w-1))
        need(pair == [x*lift for x in formula(q, m, rank)], "matrix formula mismatch")
    return {"q": q, "w": w, "m": m, "matrices": modulus**(m*m),
            "ranks": {str(r): {"total": v[0], "good": v[1]}
                      for r, v in counts.items()}}


def inverse(rows, modulus):
    m = len(rows)
    a = [list(row)+[int(i == j) for j in range(m)] for i, row in enumerate(rows)]
    for k in range(m):
        pivot = next((i for i in range(k, m) if gcd(a[i][k], modulus) == 1), None)
        need(pivot is not None, "invertible header")
        a[k], a[pivot] = a[pivot], a[k]
        unit = pow(a[k][k], -1, modulus)
        a[k] = [x*unit % modulus for x in a[k]]
        for i in range(m):
            if i != k:
                factor = a[i][k]
                a[i] = [(x-factor*y) % modulus for x, y in zip(a[i], a[k])]
    return tuple(tuple(row[m:]) for row in a)


def projector_from_header(g, gi, axes, modulus):
    m = len(g)
    return tuple(tuple(sum(g[i][k]*gi[k][j] for k in axes) % modulus
                       for j in range(m)) for i in range(m))


def source_admits(source, g, axes, q, w):
    m = len(g)
    prefix = source.ParentPrefix(q, w, tuple(tuple(x % q for x in row) for row in g),
                                 tuple(tuple(x // q for x in row) for row in g),
                                 (1,)*m, 1)
    try:
        # Only acceptance is consumed here; coefficient/operator auditing is separate.
        source.prepare(prefix, axes)
    except ValueError as error:
        if str(error) == "nongeneric low class":
            return False
        raise
    return True


def header_census(q, w, m, source):
    modulus = q**w
    counts = {r: 0 for r in sorted({1, m-1})}
    total = source_checks = 0
    for index, flat in enumerate(product(range(modulus), repeat=m*m)):
        g = matrix(flat, m)
        if not determinant(g, q):
            continue
        total += 1
        gi = inverse(g, modulus)
        for rank in counts:
            axes = tuple(range(rank))
            p = projector_from_header(g, gi, axes, modulus)
            accepted = good(p, rank, q)
            counts[rank] += int(accepted)
            if index % 97 == 0 or m == 3 or modulus <= 9:
                need(source_admits(source, g, axes, q, w) == accepted,
                     "actual northeast admission differs from minor criterion")
                source_checks += 1
    gl = 1
    for k in range(m):
        gl *= q**m-q**k
    need(total == gl*q**(m*m*(w-1)), "complete header count")
    for rank, admitted in counts.items():
        ptotal, pgood = formula(q, m, rank)
        need(admitted*ptotal == total*pgood, "complete header fraction")
    return {"q": q, "w": w, "m": m, "headers": total,
            "good": {str(r): v for r, v in counts.items()},
            "actual_source_admission_checks": source_checks}


def product_path_census(q, m):
    """Use actual scalar pairs, without matrix projectors or the closed formula."""
    pairs = tuple(product(range(q), repeat=2))
    weights = [0]*q
    weights[0] = 1
    for _ in range(m):
        following = [0]*q
        for state in range(q):
            for u, v in pairs:
                endpoint = (state+u*v) % q
                if endpoint:
                    following[endpoint] += weights[state]
        weights = following
    need(weights[1] == (q-1)*formula(q, m, m-1)[1], "pair-product path mismatch")
    return {"q": q, "m": m, "pairs_ending_at_one": weights[1]}
