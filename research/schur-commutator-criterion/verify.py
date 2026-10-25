#!/usr/bin/env python3
"""Finite corroboration of the written one-step Schur criterion. Apache-2.0."""
from collections import Counter
import hashlib
from itertools import product
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def multiply(a, b, n, q):
    return tuple(sum(a[i*n+k] * b[k*n+j] for k in range(n)) % q
                 for i in range(n) for j in range(n))


def difference(a, b, q):
    require(len(a) == len(b), "matrix size mismatch")
    return tuple((x-y) % q for x, y in zip(a, b))


def outer(a, b, q):
    return tuple(x*y % q for x in a for y in b)


def matrix_rank(a, n, q):
    rows = [list(a[i*n:(i+1)*n]) for i in range(n)]
    rank = 0
    for col in range(n):
        pivot = next((i for i in range(rank, n) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inv = pow(rows[rank][col], -1, q)
        rows[rank] = [x*inv % q for x in rows[rank]]
        for i in range(n):
            if i != rank:
                scale = rows[i][col]
                rows[i] = [(x-scale*y) % q for x, y in zip(rows[i], rows[rank])]
        rank += 1
    return rank


def inverse(a, n, q):
    rows = [list(a[i*n:(i+1)*n]) + [int(i == j) for j in range(n)]
            for i in range(n)]
    for col in range(n):
        pivot = next((i for i in range(col, n) if rows[i][col]), None)
        if pivot is None:
            return None
        rows[col], rows[pivot] = rows[pivot], rows[col]
        inv = pow(rows[col][col], -1, q)
        rows[col] = [x*inv % q for x in rows[col]]
        for i in range(n):
            if i != col:
                scale = rows[i][col]
                rows[i] = [(x-scale*y) % q for x, y in zip(rows[i], rows[col])]
    return tuple(x for row in rows for x in row[n:])


def schur(a, n, q):
    inv = pow(a[0], -1, q)
    return tuple((a[i*n+j]-a[i*n]*a[j]*inv) % q
                 for i in range(1, n) for j in range(1, n))


def factors(a, b, n, q):
    h = multiply(a, b, n, q)
    pi, qi = pow(a[0], -1, q), pow(b[0], -1, q)
    u = tuple((a[i*n]*pi-b[i*n]*qi) % q for i in range(1, n))
    v = tuple((a[j]*pi-b[j]*qi) % q for j in range(1, n))
    x = tuple((h[i*n]-h[0]*b[i*n]*qi) % q for i in range(1, n))
    y = tuple((h[j]-h[0]*b[j]*qi) % q for j in range(1, n))
    return x, v, u, y


def zero_criterion(x, v, u, y, q):
    if not any(u):
        return not any(x) or not any(v)
    if not any(v):
        return not any(y)
    pivot = next(i for i, value in enumerate(u) if value)
    scalar = x[pivot]*pow(u[pivot], -1, q) % q
    return (all(a == scalar*b % q for a, b in zip(x, u))
            and all(a == scalar*b % q for a, b in zip(y, v)))


def independent(a, b, q):
    return any((a[i]*b[j]-a[j]*b[i]) % q
               for i in range(len(a)) for j in range(i+1, len(a)))


def inspect_pair(a, b, n, q, counts, witnesses):
    s, t = schur(a, n, q), schur(b, n, q)
    actual = difference(multiply(s, t, n-1, q), multiply(t, s, n-1, q), q)
    x, v, u, y = factors(a, b, n, q)
    predicted = difference(outer(x, v, q), outer(u, y, q), q)
    require(actual == predicted, "commutator identity")
    require(zero_criterion(x, v, u, y, q) == (not any(actual)), "zero criterion")
    rank = matrix_rank(actual, n-1, q)
    require(rank <= 2, "rank bound")
    require((rank == 2) == (independent(x, u, q) and independent(v, y, q)),
            "rank-two equivalence")
    counts[str(rank)] += 1
    if rank and str(rank) not in witnesses:
        witnesses[str(rank)] = {"q": q, "n": n, "P": a, "Q": b,
                                "S": s, "T": t, "commutator": actual}


def exhaustive_pairs(n, q, idempotents):
    matrices = list(product(range(q), repeat=n*n))
    if idempotents:
        matrices = [a for a in matrices if multiply(a, a, n, q) == a]
    admitted = [a for a in matrices if a[0]]
    ranks, witnesses = Counter(), {}
    for a in admitted:
        for b in admitted:
            if multiply(a, b, n, q) != multiply(b, a, n, q):
                continue
            inspect_pair(a, b, n, q, ranks, witnesses)
            if idempotents:
                s, t = schur(a, n, q), schur(b, n, q)
                require(multiply(s, s, n-1, q) == s, "first Schur idempotent")
                require(multiply(t, t, n-1, q) == t, "second Schur idempotent")
    return {"n": n, "q": q, "idempotents_only": idempotents,
            "matrices": len(matrices), "admitted_matrices": len(admitted),
            "commutator_ranks": dict(sorted(ranks.items())), "witnesses": witnesses}


def conjugate_projector(g, gi, mask, n, q):
    return tuple(sum(g[i*n+k]*gi[k*n+j] for k in range(n) if mask >> k & 1) % q
                 for i in range(n) for j in range(n))


def four_dimensional_orbit():
    n, q = 4, 2
    ranks, witnesses = Counter(), {}
    headers = 0
    for g in product(range(q), repeat=n*n):
        gi = inverse(g, n, q)
        if gi is None:
            continue
        headers += 1
        a = conjugate_projector(g, gi, 3, n, q)
        b = conjugate_projector(g, gi, 5, n, q)
        if a[0] and b[0]:
            require(multiply(a, b, n, q) == multiply(b, a, n, q), "orbit commute")
            inspect_pair(a, b, n, q, ranks, witnesses)
    require(headers == 20160, "complete GL4(F2) cover")
    return {"n": n, "q": q, "masks": [3, 5], "headers": headers,
            "commutator_ranks": dict(sorted(ranks.items())), "witnesses": witnesses}


def sharp_projector_witness():
    g = (1, 1, 1, 1, 4, 0, 1, 0, 4)
    gi = inverse(g, 3, 5)
    require(gi is not None, "sharp header is invertible")
    a = conjugate_projector(g, gi, 6, 3, 5)
    b = conjugate_projector(g, gi, 5, 3, 5)
    require(multiply(a, a, 3, 5) == a and multiply(b, b, 3, 5) == b, "sharp idempotents")
    require(multiply(a, b, 3, 5) == multiply(b, a, 3, 5), "sharp original commutation")
    require(matrix_rank(a, 3, 5) == matrix_rank(b, 3, 5) == 2, "sharp projector ranks")
    counts, witnesses = Counter(), {}
    inspect_pair(a, b, 3, 5, counts, witnesses)
    require(counts['2'] == 1, "sharp rank-two projector witness")
    return {"commutator_ranks": dict(counts), "witnesses": witnesses}


def factor_controls():
    checked = 0
    for q, d in ((2, 2), (3, 2), (5, 1)):
        vectors = list(product(range(q), repeat=d))
        for x, v, u, y in product(vectors, repeat=4):
            actual = not any(difference(outer(x, v, q), outer(u, y, q), q))
            require(zero_criterion(x, v, u, y, q) == actual, "degenerate criterion")
            checked += 1
    return checked


def negative_controls(domains, orbit):
    witnesses = [w for domain in domains+[orbit] for w in domain['witnesses'].values()]
    require(any(any(w['commutator']) for w in witnesses), "commutativity preservation control")
    detected_sign = detected_correction = False
    for w in witnesses:
        q, n = w['q'], w['n']
        x, v, u, y = factors(w['P'], w['Q'], n, q)
        wrong_sign = tuple((a+b) % q for a, b in zip(outer(x, v, q), outer(u, y, q)))
        detected_sign |= wrong_sign != tuple(w['commutator'])
        h = multiply(w['P'], w['Q'], n, q)
        xx = tuple(h[i*n] for i in range(1, n))
        yy = tuple(h[j] for j in range(1, n))
        wrong_correction = difference(outer(xx, v, q), outer(u, yy, q), q)
        detected_correction |= wrong_correction != tuple(w['commutator'])
    require(detected_sign, "minus-sign mutation must fail")
    require(detected_correction, "omitted product-pivot correction must fail")
    # Both scalar pivots are nonzero; these matrices do not commute.
    a, b = (1, 0, 1, 0, 1, 0, 0, 0, 0), (1, 0, 0, 0, 0, 0, 1, 0, 0)
    s, t = schur(a, 3, 3), schur(b, 3, 3)
    x, v, u, y = factors(a, b, 3, 3)
    require(multiply(a, b, 3, 3) != multiply(b, a, 3, 3), "noncommuting premise")
    require(difference(multiply(s, t, 2, 3), multiply(t, s, 2, 3), 3)
            != difference(outer(x, v, 3), outer(u, y, 3), 3), "premise control")
    return 4


def main():
    domains = [exhaustive_pairs(n, q, idem) for n, q, idem in
               ((3, 2, False), (2, 3, False), (3, 2, True), (3, 3, True), (2, 5, True))]
    orbit = four_dimensional_orbit()
    sharp = sharp_projector_witness()
    result = {"domains": domains, "four_atom_orbit": orbit,
              "factor_cases": factor_controls(), "negative_controls": negative_controls(domains+[sharp], orbit),
              "sharp_projector": sharp}
    package = Path(__file__).resolve().parent
    result['package_sha256'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in sorted(package.iterdir()) if p.is_file()}
    canonical = json.dumps(result, sort_keys=True, separators=(',', ':')).encode()
    result['receipt_sha256'] = hashlib.sha256(canonical).hexdigest()
    print('PASS_SCHUR_COMMUTATOR_CRITERION')
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
