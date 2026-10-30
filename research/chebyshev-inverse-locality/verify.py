"""Exact finite corroboration of the new inverse-locality polynomial.

Produced by Nick Petalas. Apache-2.0. No predecessor verifier is imported.
"""

from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
import platform


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def coefficients(k, degree):
    """Return integer N_d, its scale denominator, and inverse coefficients."""
    if type(k) is not int or not 2 <= k <= 16:
        raise ValueError("the finite checker requires integer 2 <= K <= 16")
    if type(degree) is not int or not 1 <= degree <= 16:
        raise ValueError("the finite checker requires integer 1 <= degree <= 16")
    a, b, denominator = k**4 + 1, 2 * k**2, k**4 - 1
    previous, current = [1], [a, -b]
    for _ in range(1, degree):
        following = [0] * (len(current) + 1)
        for j, value in enumerate(current):
            following[j] += 2 * a * value
            following[j + 1] -= 2 * b * value
        for j, value in enumerate(previous):
            following[j] -= denominator**2 * value
        previous, current = current, following
    need(current[0] > 0, "positive normalization")
    inverse = tuple(F(-value, current[0]) for value in current[1:])
    return tuple(current), denominator**degree, inverse


def evaluate(poly, value):
    result = F(0)
    for coefficient in reversed(poly):
        result = result * value + coefficient
    return result


def chebyshev(value, degree):
    previous, current = F(1), value
    for _ in range(1, degree):
        previous, current = current, 2 * value * current - previous
    return current


def eye(n):
    return tuple(tuple(F(i == j) for j in range(n)) for i in range(n))


def transpose(a):
    return tuple(zip(*a, strict=True))


def combine(a, b, alpha=F(1), beta=F(1)):
    return tuple(tuple(alpha * x + beta * y for x, y in zip(u, v, strict=True))
                 for u, v in zip(a, b, strict=True))


def multiply(a, b):
    columns = transpose(b)
    return tuple(tuple(sum(x * y for x, y in zip(row, col, strict=True))
                       for col in columns) for row in a)


def matrix_poly(poly, a):
    identity = eye(len(a))
    result = combine(identity, identity, F(0), F(0))
    for coefficient in reversed(poly):
        result = combine(multiply(result, a), identity, F(1), coefficient)
    return result


def inverse(a):
    n = len(a)
    rows = [list(row) + list(unit) for row, unit in zip(a, eye(n), strict=True)]
    for col in range(n):
        pivot = next((r for r in range(col, n) if rows[r][col]), None)
        if pivot is None:
            raise ValueError("singular fixture")
        rows[col], rows[pivot] = rows[pivot], rows[col]
        divisor = rows[col][col]
        rows[col] = [value / divisor for value in rows[col]]
        for r in range(n):
            if r != col:
                factor = rows[r][col]
                rows[r] = [x - factor * y for x, y in
                           zip(rows[r], rows[col], strict=True)]
    result = tuple(tuple(row[n:]) for row in rows)
    need(multiply(a, result) == eye(n), "inverse identity")
    return result


def positive_definite(a):
    """Exact unpivoted LDL test, used only on real symmetric fixtures."""
    n = len(a)
    if transpose(a) != a:
        return False
    lower = [[F(i == j) for j in range(n)] for i in range(n)]
    diagonal = [F(0)] * n
    for j in range(n):
        diagonal[j] = a[j][j] - sum(lower[j][r]**2 * diagonal[r]
                                   for r in range(j))
        if diagonal[j] <= 0:
            return False
        for i in range(j + 1, n):
            lower[i][j] = (a[i][j] - sum(lower[i][r] * lower[j][r] * diagonal[r]
                                        for r in range(j))) / diagonal[j]
    return True


def approximation(h, k, degree):
    numerator, denominator, poly = coefficients(k, degree)
    gram = multiply(transpose(h), h)
    result = multiply(matrix_poly(poly, gram), transpose(h))
    residual = matrix_poly(tuple(F(c, numerator[0]) for c in numerator), gram)
    normalization = F(numerator[0], denominator)
    return result, residual, normalization, gram


def scalar_checks():
    samples = 0
    for k in range(2, 9):
        for degree in range(1, 17):
            numerator, denominator, poly = coefficients(k, degree)
            c = F(k**4 + 1, k**4 - 1)
            need(F(numerator[0], denominator) == chebyshev(c, degree),
                 "independent normalization recurrence")
            z = F(k**2 + 1, k**2 - 1)
            need(chebyshev(c, degree) == (z**degree + z**(-degree)) / 2,
                 "closed-form normalization")
            need(sum(abs(x) for x in numerator) <= (3 * (k**2 + 1)**2)**degree,
                 "integer coefficient bound")
            for j in range(33):
                x = F(1, k**2) + F(j, 32) * (k**2 - F(1, k**2))
                t = (k**4 + 1 - 2 * k**2 * x) / (k**4 - 1)
                r = evaluate(numerator, x) / numerator[0]
                need(r == chebyshev(t, degree) / chebyshev(c, degree),
                     "independent scalar recurrence")
                need(abs(r) <= F(denominator, numerator[0]), "residual envelope")
                need(x * evaluate(poly, x) == 1 - r, "divisible residual")
                samples += 1
    return samples


def operator_checks():
    fixtures = (
        ((F(1), F(1)), (F(0), F(1))),
        ((F(1), F(1, 3), F(0)), (F(0), F(1), F(-1, 4)),
         (F(1, 5), F(0), F(1))),
        ((F(3, 4), F(1, 5)), (F(-1, 7), F(5, 4))),
    )
    count = 0
    for h in fixtures:
        h_inverse, identity = inverse(h), eye(len(h))
        for k in (2, 3, 5):
            for degree in (1, 2, 3, 4, 6):
                result, residual, normalization, gram = approximation(h, k, degree)
                need(positive_definite(combine(gram, identity, F(1), F(-1, k**2))),
                     "lower singular-value hypothesis")
                need(positive_definite(combine(identity, gram, F(k**2), F(-1))),
                     "upper singular-value hypothesis")
                error = combine(result, h_inverse, F(1), F(-1))
                expected = combine(multiply(residual, h_inverse), identity, F(-1), F(0))
                need(error == expected, "ordered error identity")
                ceiling = F(k**2) / normalization**2
                need(positive_definite(combine(identity, multiply(transpose(error), error),
                                               ceiling, F(-1))), "operator norm bound")
                wrong_order = combine(multiply(h_inverse, residual), identity, F(-1), F(0))
                need(error != wrong_order, "wrong residual order control")
                need(error != multiply(residual, h_inverse), "wrong residual sign control")
                count += 1
    return count


def cyclic_fixture(n):
    return tuple(tuple(F(i == j) + F(1, 8) * ((i - j) % n == 1)
                       + F(1, 10) * ((j - i) % n == 1)
                       for j in range(n)) for i in range(n))


def locality_checks():
    checked, different = 0, 0
    for degree in (1, 2, 3):
        n, radius = 21, 2 * degree - 1
        h = cyclic_fixture(n)
        selected = tuple(range(2, n - 2))
        section = tuple(tuple(h[i][j] for j in selected) for i in selected)
        full = approximation(h, 2, degree)[0]
        local = approximation(section, 2, degree)[0]
        omitted = tuple(i for i in range(n) if i not in selected)
        for r, i in enumerate(selected):
            distance = min(min((i - j) % n, (j - i) % n) for j in omitted)
            embedded = tuple(local[r][selected.index(j)] if j in selected else F(0)
                             for j in range(n))
            if distance > radius:
                need(embedded == full[i], "section row equality")
                checked += 1
            elif distance == radius:
                need(embedded != full[i], "too-small halo control")
                different += 1
        for i in range(n):
            for j in range(n):
                if min((i - j) % n, (j - i) % n) > radius:
                    need(full[i][j] == 0, "physical bandwidth")
    return checked, different


def controls_and_parameters():
    rejected = 0
    for k, degree in ((1, 1), (0, 1), (17, 1), (2.0, 1), (2, 0), (2, 17)):
        try:
            coefficients(k, degree)
        except ValueError:
            rejected += 1
    need(rejected == 6, "finite-domain rejection controls")
    for p in range(2, 129):
        degree = p**22
        need((2 * degree - 1) * (p - 1) < p**24, "new halo")
        need(degree < p**42 and p**24 < p**48, "strict parameter improvement")
    return rejected, 127


def main():
    scalar = scalar_checks()
    operators = operator_checks()
    rows, halo_controls = locality_checks()
    invalid, parameters = controls_and_parameters()
    root = Path(__file__).resolve().parent
    files = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    receipt = {
        "status": "PASS_CHEBYSHEV_INVERSE_LOCALITY", "python": platform.python_version(),
        "scalar_samples": scalar, "operator_fixtures": operators,
        "exact_section_rows": rows, "too_small_halo_rejections": halo_controls,
        "invalid_inputs_rejected": invalid, "parameter_instances": parameters,
        "sha256": {name: sha256((root / name).read_bytes()).hexdigest() for name in files},
    }
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
