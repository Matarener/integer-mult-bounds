"""Exact finite corroboration for conditioned matching interpolation.

The quantified theorem is proved in README.md. This program uses only the
standard library and writes its hash-bound receipt to stdout.
"""

from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
import platform


Matrix = tuple[tuple[F, ...], ...]
MAX_DIM = 8


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def matrix(rows: list[list[int | F]]) -> Matrix:
    n = len(rows)
    require(1 <= n <= MAX_DIM, "dimension outside 1..8")
    require(all(len(row) == n for row in rows), "matrix must be square")
    require(all(type(x) in (int, F) for row in rows for x in row), "nonrational entry")
    return tuple(tuple(F(x) for x in row) for row in rows)


def identity(n: int) -> Matrix:
    require(1 <= n <= MAX_DIM, "dimension outside 1..8")
    return tuple(tuple(F(i == j) for j in range(n)) for i in range(n))


def add(a: Matrix, b: Matrix, scale: F = F(1)) -> Matrix:
    require(len(a) == len(b), "dimension mismatch")
    n = len(a)
    return tuple(tuple(a[i][j] + scale * b[i][j] for j in range(n)) for i in range(n))


def scaled(a: Matrix, scale: F) -> Matrix:
    return tuple(tuple(scale * x for x in row) for row in a)


def transpose(a: Matrix) -> Matrix:
    n = len(a)
    return tuple(tuple(a[j][i] for j in range(n)) for i in range(n))


def product(a: Matrix, b: Matrix) -> Matrix:
    require(len(a) == len(b), "dimension mismatch")
    n = len(a)
    return tuple(tuple(sum((a[i][k] * b[k][j] for k in range(n)), F(0))
                       for j in range(n)) for i in range(n))


def inverse(a: Matrix) -> Matrix:
    n = len(a)
    unit = identity(n)
    rows = [list(a[i] + unit[i]) for i in range(n)]
    for col in range(n):
        candidates = [i for i in range(col, n) if rows[i][col]]
        require(bool(candidates), "singular matrix")
        pivot = candidates[0]
        rows[col], rows[pivot] = rows[pivot], rows[col]
        divisor = rows[col][col]
        rows[col] = [x / divisor for x in rows[col]]
        for i in range(n):
            if i != col:
                factor = rows[i][col]
                rows[i] = [rows[i][j] - factor * rows[col][j] for j in range(2 * n)]
    result = tuple(tuple(row[n:]) for row in rows)
    require(product(a, result) == unit, "inverse postcondition")
    return result


def positive_semidefinite(a: Matrix) -> bool:
    """Exact symmetric Schur elimination, including zero pivots."""
    if a != transpose(a):
        return False
    n = len(a)
    rows = [list(row) for row in a]
    for k in range(n):
        pivot = rows[k][k]
        if pivot < 0:
            return False
        if pivot == 0:
            if any(rows[k][j] != 0 for j in range(k + 1, n)):
                return False
        else:
            for i in range(k + 1, n):
                for j in range(k + 1, n):
                    rows[i][j] -= rows[i][k] * rows[k][j] / pivot
    return True


def gram(a: Matrix) -> Matrix:
    return product(transpose(a), a)


def projection(n: int, selected: tuple[int, ...]) -> Matrix:
    require(len(set(selected)) == len(selected), "duplicate selected coordinate")
    require(all(0 <= i < n for i in selected), "selected coordinate outside matrix")
    return tuple(tuple(F(i == j and i in selected) for j in range(n)) for i in range(n))


def validate(g: Matrix, e: Matrix, q: F) -> None:
    require(type(q) is F and q >= 1, "squared gate cap must be rational and >=1")
    require(len(g) == len(e), "dimension mismatch")
    unit = identity(len(g))
    require(e == transpose(e) and product(e, e) == e, "not an orthogonal projection")
    require(product(g, e) == product(e, g), "projection splits a gate")
    require(positive_semidefinite(add(scaled(unit, q), gram(g), F(-1))), "upper cap fails")
    require(positive_semidefinite(add(scaled(gram(g), q), unit, F(-1))), "inverse cap fails")


def check_gram_bound(g: Matrix, e: Matrix, q: F) -> None:
    validate(g, e, q)
    unit = identity(len(g))
    other = add(unit, e, F(-1))
    h = add(product(e, g), other)
    gg = gram(g)
    c = q / (1 + q)
    slack = add(scaled(add(unit, gg), c), gram(h), F(-1))
    selected = product(e, add(scaled(unit, q), gg, F(-1)))
    unselected = product(other, add(scaled(gg, q), unit, F(-1)))
    require(slack == scaled(add(selected, unselected), 1 / (1 + q)), "slack identity fails")
    require(positive_semidefinite(slack), "conditioned Gram bound fails")


def block_diagonal(blocks: tuple[Matrix, ...]) -> Matrix:
    n = sum(len(block) for block in blocks)
    require(1 <= n <= MAX_DIM, "block dimension outside 1..8")
    rows = [[F(0) for _ in range(n)] for _ in range(n)]
    start = 0
    for block in blocks:
        for i in range(len(block)):
            for j in range(len(block)):
                rows[start + i][start + j] = block[i][j]
        start += len(block)
    return tuple(tuple(row) for row in rows)


def rotate_coordinates(a: Matrix, shift: int) -> Matrix:
    n = len(a)
    order = tuple((i + shift) % n for i in range(n))
    return tuple(tuple(a[i][j] for j in order) for i in order)


def dense_context(n: int, seed: int) -> Matrix:
    """An explicit invertible context, unrelated to the gate decomposition."""
    rows = [list(row) for row in identity(n)]
    for i in range(n):
        j = (i + 1) % n
        if i != j:
            coefficient = F((-1) ** (i + seed), i + seed + 2)
            rows[i] = [rows[i][k] + coefficient * rows[j][k] for k in range(n)]
    return tuple(tuple(row) for row in rows)


def check_contexts(g: Matrix, e: Matrix, q: F) -> int:
    unit = identity(len(g))
    h = add(product(e, g), add(unit, e, F(-1)))
    hi = inverse(h)
    complement = product(g, hi)
    complement_inverse = inverse(complement)
    c = q / (1 + q)
    checks = 0
    for seed in range(2):
        p0, s1 = dense_context(len(g), seed), dense_context(len(g), seed + 2)
        p1, s0 = product(g, p0), product(s1, g)
        triples = ((p0, p1, product(h, p0)),
                   (transpose(inverse(p0)), transpose(inverse(p1)),
                    transpose(product(inverse(p0), hi))),
                   (transpose(s1), transpose(s0), transpose(product(s1, complement))),
                   (inverse(s1), inverse(s0), product(complement_inverse, inverse(s1))))
        for left, right, partial in triples:
            slack = add(scaled(add(gram(left), gram(right)), c), gram(partial), F(-1))
            require(positive_semidefinite(slack), "four-way context bound fails")
            checks += 1
    return checks


def finite_fixtures() -> dict[str, int]:
    rotation = matrix([[F(3, 5), F(-4, 5)], [F(4, 5), F(3, 5)]])
    shear = matrix([[1, 1], [0, 1]])
    # Realification of the complex shear [[1, 3/5+4i/5], [0,1]].
    complex_shear = matrix([[1, 0, F(3, 5), F(-4, 5)],
                            [0, 1, F(4, 5), F(3, 5)],
                            [0, 0, 1, 0], [0, 0, 0, 1]])
    families = ((rotation, F(1)), (shear, F(21, 8)), (complex_shear, F(21, 8)))
    fixtures = gram_checks = context_checks = 0
    for block, q in families:
        g0 = block_diagonal((block, block))
        width, n = len(block), 2 * len(block)
        for shift in range(n):
            g = rotate_coordinates(g0, shift)
            for mask in range(4):
                selected = tuple(i for b in range(2) if mask & (1 << b)
                                 for i in range(b * width, (b + 1) * width))
                e = rotate_coordinates(projection(n, selected), shift)
                other = add(identity(n), e, F(-1))
                for operator in (g, inverse(g), transpose(g), transpose(inverse(g))):
                    for projector in (e, other):
                        check_gram_bound(operator, projector, q)
                        gram_checks += 1
                context_checks += check_contexts(g, e, q)
                fixtures += 1
    return {"matching_fixtures": fixtures, "gram_checks": gram_checks,
            "four_way_context_checks": context_checks}


def frobenius_squared(a: Matrix) -> F:
    return sum((x * x for row in a for x in row), F(0))


def witness_ratio(a: Matrix, g: Matrix, h: Matrix) -> F:
    """Lower bound using the first input and upper Frobenius endpoint bounds."""
    partial = product(h, a)
    numerator = sum((row[0] ** 2 for row in partial), F(0))
    denominator = max(frobenius_squared(a), frobenius_squared(product(g, a)))
    require(denominator > 0, "zero witness")
    return numerator / denominator


def sharp_witnesses() -> dict[str, object]:
    diagonal_checks = 0
    for k in (F(1), F(3, 2), F(2), F(3), F(5)):
        q = k * k
        target = 2 * q / (1 + q)
        previous = F(0)
        for power in range(2, 13):
            epsilon = F(1, 2 ** power)
            a = matrix([[1, 0], [k, epsilon]])
            g = matrix([[k, 0], [0, 1 / k]])
            h = matrix([[k, 0], [0, 1]])
            ratio = witness_ratio(a, g, h)
            require(previous < ratio < target, "diagonal witness convergence fails")
            require(target - ratio < epsilon * epsilon, "diagonal witness gap fails")
            require(product(a, inverse(a)) == identity(2), "witness is not invertible")
            previous = ratio
            diagonal_checks += 1
    r0, r1 = 1, 1
    shear_checks = 0
    final_ratio = F(0)
    g = block_diagonal((matrix([[1, 1], [0, 1]]),) * 2)
    h = block_diagonal((matrix([[1, 1], [0, 1]]), identity(2)))
    for power in range(2, 15):
        r0, r1 = r1, r0 + r1
        r = F(r1, r0)
        x = (F(1), r, r * r, -r)
        epsilon = F(1, 2 ** power)
        a = tuple(tuple(x[i] if j == 0 else epsilon * (i == j)
                        for j in range(4)) for i in range(4))
        final_ratio = witness_ratio(a, g, h)
        require(product(a, inverse(a)) == identity(4), "shear witness is not invertible")
        require(final_ratio <= 1 or 5 * (final_ratio - 1) ** 2 < 1,
                "unit-shear witness exceeds the exact sharp constant")
        shear_checks += 1
    require(final_ratio > F(1447, 1000), "unit-shear sharpness witness too weak")
    return {"diagonal_invertible_witnesses": diagonal_checks,
            "unit_shear_invertible_witnesses": shear_checks,
            "unit_shear_final_ratio_squared_lower_bound": str(final_ratio)}


def rejection_controls() -> int:
    unit = identity(2)
    e = projection(2, (0,))
    swap = matrix([[0, 1], [1, 0]])
    cases = (("cap", lambda: validate(unit, e, F(1, 2))),
             ("square", lambda: matrix([[1, 0]])),
             ("type", lambda: matrix([[True]])),
             ("orthogonal", lambda: validate(unit, matrix([[1, 1], [0, 0]]), F(1))),
             ("split gate", lambda: validate(swap, e, F(1))),
             ("upper", lambda: validate(matrix([[2, 0], [0, 1]]), e, F(1))),
             ("inverse", lambda: validate(matrix([[1, 0], [0, F(1, 2)]]), e, F(1))),
             ("singular", lambda: inverse(matrix([[1, 0], [0, 0]]))),
             ("duplicate", lambda: projection(2, (0, 0))),
             ("outside", lambda: projection(2, (2,))))
    for name, operation in cases:
        try:
            operation()
        except ValueError:
            continue
        raise ValueError("control accepted: " + name)
    require(not positive_semidefinite(matrix([[0, 1], [1, 0]])), "zero-pivot control")
    # Splitting a unitary two-wire gate can duplicate a row and cost sqrt(2).
    partial = add(product(e, swap), add(unit, e, F(-1)))
    require(not positive_semidefinite(add(unit, gram(partial), F(-1))), "split-unitary control")
    # An upper cap alone does not justify the new factor at K=2.
    a = matrix([[1, 0], [F(7, 4), F(1, 100)]])
    g = matrix([[2, 0], [0, F(1, 4)]])
    h = matrix([[2, 0], [0, 1]])
    require(witness_ratio(a, g, h) > F(8, 5), "missing inverse-cap control")
    a = matrix([[1, 0], [2, F(1, 100)]])
    g = matrix([[2, 0], [0, F(1, 2)]])
    require(witness_ratio(a, g, h) > F(159, 100), "undercut constant control")
    require(not positive_semidefinite(add(gram(a), gram(product(h, a)), F(-1))),
            "zero-loss control")
    return len(cases) + 5


def receipt() -> dict[str, object]:
    counts = finite_fixtures()
    counts.update(sharp_witnesses())
    counts["rejection_controls"] = rejection_controls()
    package = Path(__file__).resolve().parent
    names = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {name: sha256((package / name).read_bytes()).hexdigest() for name in names}
    return {"status": "PASS_CONDITIONED_MATCHING_SUBLAYERS", "counts": counts,
            "squared_factor": "2*K^2/(1+K^2)", "python": platform.python_version(),
            "package_sha256": hashes,
            "claim_type": "scoped written proof with exact finite corroboration"}


if __name__ == "__main__":
    print(json.dumps(receipt(), indent=2, sort_keys=True))
