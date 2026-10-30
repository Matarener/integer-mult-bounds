"""Exact corroboration of the two-role domain obstruction. Standard library only."""

import hashlib
import itertools
import json
from pathlib import Path


DEGREE_LIMIT = 8
TERM_LIMIT = 45
Poly = tuple[tuple[int, int, int], ...]
Matrix = tuple[Poly, Poly, Poly, Poly]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def polynomial(terms: dict[tuple[int, int], int], p: int) -> Poly:
    require(p in (0, 2, 3, 5, 7), "unsupported coefficient domain")
    require(len(terms) <= TERM_LIMIT, "polynomial capacity exceeded")
    result = []
    for (i, j), value in sorted(terms.items()):
        require(i >= 0 and j >= 0 and i + j <= DEGREE_LIMIT, "degree limit")
        value = value % p if p else value
        if value:
            result.append((i, j, value))
    return tuple(result)


def constant(value: int, p: int) -> Poly:
    return polynomial({(0, 0): value}, p)


def add(a: Poly, b: Poly, p: int) -> Poly:
    terms = {(i, j): value for i, j, value in a}
    for i, j, value in b:
        terms[i, j] = terms.get((i, j), 0) + value
    return polynomial(terms, p)


def scale(a: Poly, value: int, p: int) -> Poly:
    return polynomial({(i, j): value * c for i, j, c in a}, p)


def multiply(a: Poly, b: Poly, p: int) -> Poly:
    terms: dict[tuple[int, int], int] = {}
    for i, j, c in a:
        for k, ell, d in b:
            key = i + k, j + ell
            terms[key] = terms.get(key, 0) + c * d
    return polynomial(terms, p)


def identity(p: int) -> Matrix:
    one, zero = constant(1, p), constant(0, p)
    return one, zero, zero, one


def matmul(a: Matrix, b: Matrix, p: int) -> Matrix:
    entries = []
    for i, j in itertools.product(range(2), repeat=2):
        entries.append(add(multiply(a[2 * i], b[j], p),
                           multiply(a[2 * i + 1], b[2 + j], p), p))
    return tuple(entries)


def outer(a: tuple[Poly, Poly], b: tuple[Poly, Poly], p: int) -> Matrix:
    return tuple(multiply(x, y, p) for x in a for y in b)


def determinant(a: Matrix, p: int) -> Poly:
    return add(multiply(a[0], a[3], p), scale(multiply(a[1], a[2], p), -1, p), p)


def paid(u: tuple[Poly, Poly], v: tuple[int, int], p: int) -> Matrix:
    unit = identity(p)
    return tuple(add(unit[2 * i + j], scale(u[i], v[j], p), p)
                 for i, j in itertools.product(range(2), repeat=2))


def even_quadratics(p: int) -> tuple[Poly, ...]:
    require(p in (2, 3, 5), "finite search requires a declared prime")
    monomials = ((0, 0), (2, 0), (1, 1), (0, 2))
    return tuple(polynomial(dict(zip(monomials, values)), p)
                 for values in itertools.product(range(p), repeat=4))


def factor_singular(n: Matrix, v: tuple[int, int], p: int):
    require(v != (0, 0) and not determinant(n, p), "singular factor premise")
    if v[0]:
        a = constant(-v[1] * pow(v[0], -1, p), p), constant(1, p)
        b = n[2], n[3]
    else:
        a = constant(1, p), constant(0, p)
        b = n[0], n[1]
    require(outer(a, b, p) == n, "singular factor extraction")
    return a, b


def check_singular_factors(p: int) -> dict[str, int]:
    values = even_quadratics(p)
    count = tested = 0
    s2, st, t2 = (polynomial({m: 1}, p) for m in ((2, 0), (1, 1), (0, 2)))
    prefix = paid((s2, st), (0, 1), p)
    suffix = paid((t2, s2), (1, 0), p)
    free = (constant(0, p), constant(1, p), constant(-1, p), constant(1, p))
    for v in itertools.product(range(p), repeat=2):
        if v == (0, 0):
            continue
        for u in itertools.product(values, repeat=2):
            tested += 1
            n = paid(u, v, p)
            if determinant(n, p):
                continue
            a, b = factor_singular(n, v, p)
            left = matmul(free, suffix, p)
            right = matmul(prefix, free, p)
            endpoint = matmul(matmul(left, n, p), right, p)
            aa = tuple(add(multiply(left[2 * i], a[0], p),
                           multiply(left[2 * i + 1], a[1], p), p) for i in range(2))
            bb = tuple(add(multiply(b[0], right[j], p),
                           multiply(b[1], right[2 + j], p), p) for j in range(2))
            require(endpoint == outer(aa, bb, p), "full wrapped endpoint")
            count += 1
    require(count == (p * p - 1) * len(values), "complete singular-factor count")
    return {"p": p, "tested_parameter_choices": tested,
            "singular_parameter_choices": count, "wrapped_words": count}


def check_veronese(p: int) -> dict[str, int]:
    values = even_quadratics(p)
    s2, st, t2 = (polynomial({m: 1}, p) for m in ((2, 0), (1, 1), (0, 2)))
    target = s2, st, st, t2
    require(not determinant(target, p), "target determinant")
    first_pairs = completions = 0
    for a1, b1 in itertools.product(values, repeat=2):
        if multiply(a1, b1, p) != s2:
            continue
        first_pairs += 1
        a2s = tuple(x for x in values if multiply(x, b1, p) == st)
        b2s = tuple(x for x in values if multiply(a1, x, p) == st)
        for a2, b2 in itertools.product(a2s, b2s):
            if multiply(a2, b2, p) == t2:
                completions += 1
    require(first_pairs == 2 * (p - 1), "complete first-entry divisor pairs")
    require(completions == 0, "unexpected Veronese factorization")
    return {"p": p, "first_entry_pairs_tested": len(values) ** 2,
            "first_entry_solutions": first_pairs, "factorizations": completions}


def three_factors(a: tuple[Poly, Poly], b: tuple[Poly, Poly], p: int):
    one, zero = constant(1, p), constant(0, p)
    factors = ((a[0], zero, a[1], one), (one, b[1], zero, zero),
               (b[0], zero, zero, one))
    us = ((add(a[0], scale(one, -1, p), p), a[1]),
          (b[1], scale(one, -1, p)),
          (add(b[0], scale(one, -1, p), p), zero))
    vs = ((1, 0), (0, 1), (1, 0))
    for n, u, v in zip(factors, us, vs):
        require(n == paid(u, v, p), "constructor factor legality")
    endpoint = matmul(matmul(factors[0], factors[1], p), factors[2], p)
    require(endpoint == outer(a, b, p), "outer-product word endpoint")
    return factors


def check_controls() -> dict[str, int]:
    constructors = deletions = specializations = 0
    larger_rings = determinant_mutations = 0
    for p in (0, 2, 3, 5, 7):
        one = constant(1, p)
        s, t = polynomial({(1, 0): 1}, p), polynomial({(0, 1): 1}, p)
        s2, st, t2 = multiply(s, s, p), multiply(s, t, p), multiply(t, t, p)
        a, b = (add(one, s2, p), st), (t2, add(one, st, p))
        factors = three_factors(a, b, p)
        constructors += 1
        for index in range(3):
            altered = list(factors)
            altered[index] = identity(p)
            require(matmul(matmul(altered[0], altered[1], p), altered[2], p)
                    != outer(a, b, p), "omitted paid factor went undetected")
            deletions += 1
        three_factors((s, t), (s, t), p)
        require(outer((s, t), (s, t), p) == (s2, st, st, t2), "larger-ring control")
        require(any((i + j) % 2 for i, j, c in s + t), "ring restriction control")
        constructors += 1
        larger_rings += 1
        require(determinant((s2, st, st, add(t2, one, p)), p) == s2,
                "determinant mutation control")
        determinant_mutations += 1
    for p in (2, 3, 5, 7):
        for s, t, x, y in itertools.product(range(p), repeat=4):
            actual = ((s * s * x + s * t * y) % p,
                      (s * t * x + t * t * y) % p)
            source = (s * x + t * y) % p
            require(actual == (s * source % p, t * source % p), "scalar action")
            specializations += 1
    invalid = 0
    for terms, p in (({(9, 0): 1}, 2), ({(-1, 0): 1}, 3), ({(0, 0): 1}, 4)):
        try:
            polynomial(terms, p)
        except ValueError:
            invalid += 1
    require(invalid == 3, "invalid polynomial accepted")
    return {"constructor_words": constructors, "omission_controls": deletions,
            "scalar_input_cases": specializations, "invalid_inputs": invalid,
            "larger_ring_controls": larger_rings,
            "determinant_mutations": determinant_mutations}


def check_bounds() -> dict[str, int]:
    maximum = {(i, j): 1 for i in range(9) for j in range(9 - i)}
    require(len(polynomial(maximum, 2)) == TERM_LIMIT, "capacity boundary")
    failures = 0
    try:
        polynomial({(i, 0): 1 for i in range(46)}, 2)
    except ValueError:
        failures += 1
    try:
        factor_singular(identity(2), (1, 0), 2)
    except ValueError:
        failures += 1
    require(failures == 2, "capacity or singular-premise guard missing")
    return {"accepted_capacity_boundaries": 1, "rejected_premises": failures}


def main() -> None:
    result = {
        "singular_factors": [check_singular_factors(p) for p in (2, 3)],
        "veronese_searches": [check_veronese(p) for p in (2, 3, 5)],
        "controls": check_controls(),
        "bound_controls": check_bounds(),
        "claim_type": "scoped written proof with finite corroboration",
        "all_field_obstruction": "written polynomial-divisibility proof, not finite evaluation",
    }
    package = Path(__file__).resolve().parent
    hashes = {}
    for name in ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py"):
        with (package / name).open("rb") as stream:
            payload = stream.read(128 * 1024 + 1)
        require(len(payload) <= 128 * 1024, "source receipt capacity")
        hashes[name] = hashlib.sha256(payload).hexdigest()
    print(json.dumps({"results": result, "source_sha256": hashes}, sort_keys=True))
    print("PASS_VERONESE_SINGULAR_OBSTRUCTION no_new_kappa")


if __name__ == "__main__":
    main()
