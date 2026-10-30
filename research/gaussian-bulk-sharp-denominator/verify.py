"""Exact finite corroboration of the sharp central-bulk denominator theorem."""
from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
import json
from math import factorial, prod
from pathlib import Path
import platform

Gaussian = tuple[Fraction, Fraction]
ZERO: Gaussian = (Fraction(0), Fraction(0))
ONE: Gaussian = (Fraction(1), Fraction(0))
I: Gaussian = (Fraction(0), Fraction(1))
PI: Gaussian = (Fraction(1), Fraction(1))
MAX_N = 10


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def add(x: Gaussian, y: Gaussian) -> Gaussian:
    return x[0] + y[0], x[1] + y[1]


def mul(x: Gaussian, y: Gaussian) -> Gaussian:
    return x[0]*y[0] - x[1]*y[1], x[0]*y[1] + x[1]*y[0]


def scale(q: Fraction | int, x: Gaussian) -> Gaussian:
    return q*x[0], q*x[1]


def power(x: Gaussian, exponent: int) -> Gaussian:
    require(0 <= exponent <= 4*MAX_N, 'power bound')
    result = ONE
    for _ in range(exponent):
        result = mul(result, x)
    return result


def parameters(n: int, a: int, degree: int) -> None:
    require(type(n) is int and type(a) is int and type(degree) is int,
            'integer parameters required')
    require(1 <= n <= MAX_N, 'finite verifier dimension bound')
    require(0 <= degree <= n and 0 <= a <= n-degree, 'invalid band')


def choose(z: int, k: int) -> int:
    require(0 <= k <= MAX_N, 'binomial bound')
    return prod(z-j for j in range(k)) // factorial(k)


def value(k: int, a: int, degree: int) -> Gaussian:
    result = ZERO
    for h in range(degree+1):
        term = scale(choose(k-a, h), power(add(I, scale(-1, ONE)), h))
        result = add(result, term)
    return mul(power(I, a), result)


def coefficients(n: int, a: int, degree: int) -> list[Gaussian]:
    """Invert the complete exact Walsh spectrum, without a numerator compiler."""
    parameters(n, a, degree)
    data = [value(k.bit_count(), a, degree) for k in range(1 << n)]
    for level in range(n):
        half = 1 << level
        for start in range(0, 1 << n, 2*half):
            for j in range(half):
                x, y = data[start+j], data[start+j+half]
                data[start+j] = add(x, y)
                data[start+j+half] = add(x, scale(-1, y))
    return [scale(Fraction(1, 1 << n), z) for z in data]


def polynomial_coefficients(n: int, a: int, degree: int) -> list[Gaussian]:
    """Evaluate falling factorials directly in Q(i)[(Z/2)^n]."""
    parameters(n, a, degree)
    term = [ZERO for _ in range(1 << n)]
    term[0] = ONE
    result = term.copy()
    for h in range(1, degree+1):
        following = []
        for s in range(1 << n):
            z = scale(Fraction(n, 2)-a-h+1, term[s])
            for axis in range(n):
                z = add(z, scale(Fraction(-1, 2), term[s ^ (1 << axis)]))
            following.append(scale(Fraction(1, h), z))
        term = following
        factor = power(add(I, scale(-1, ONE)), h)
        result = [add(x, mul(factor, y)) for x, y in zip(result, term, strict=True)]
    return [mul(power(I, a), z) for z in result]


def integral(z: Gaussian) -> bool:
    return z[0].denominator == 1 and z[1].denominator == 1


def valuation(z: Gaussian) -> int | None:
    require(integral(z), 'valuation requires a Gaussian integer')
    if z == ZERO:
        return None
    real, imag = z[0].numerator, z[1].numerator
    bound = 2*max(abs(real).bit_length(), abs(imag).bit_length())+1
    for exponent in range(bound):
        if (real-imag) % 2:
            return exponent
        real, imag = (real+imag)//2, (imag-real)//2
    raise ValueError('Gaussian valuation bound exhausted')


def certify(n: int, a: int, degree: int, data: list[Gaussian]) -> int:
    parameters(n, a, degree)
    require(len(data) == 1 << n, 'coefficient count')
    numerator = [mul(power(PI, degree), z) for z in data]
    require(all(integral(z) for z in numerator), 'insufficient numerator grid')
    for s, z in enumerate(data):
        if s.bit_count() > degree:
            require(z == ZERO, 'Boolean degree exceeded')
        if s.bit_count() == degree:
            require(numerator[s] == power(I, a), 'wrong top coefficient')
    if degree:
        require(not integral(mul(power(PI, degree-1), data[(1 << degree)-1])),
                'claimed smaller grid has no obstruction')
    return sum(s.bit_count() == degree for s in range(1 << n))


def precision_cases(n: int, a: int, degree: int, data: list[Gaussian]) -> int:
    """Literal column response to two congruent numerator/input representatives."""
    numerator = [mul(power(PI, degree), z) for z in data]
    count = 0
    for p in range(1, 5):
        delta = power(PI, p+degree-1)
        for source in range(1 << n):
            output = source ^ ((1 << degree)-1)
            entry = numerator[output ^ source]
            difference = mul(entry, delta)
            require(valuation(difference) == p+degree-1, 'precision witness lost')
            # Division by pi^degree gives valuation p-1, so outputs differ mod pi^p.
            require(valuation(difference)-degree == p-1, 'wrong output modulus')
            count += 1
    return count


def expect_rejection(action) -> None:
    try:
        action()
    except ValueError:
        return
    raise ValueError('negative control accepted')


def controls() -> int:
    bad_parameters = [(0, 0, 0), (11, 0, 0), (3, -1, 1), (3, 0, -1),
                      (3, 1, 3), (3, 0, 4), (True, 0, 0)]
    for args in bad_parameters:
        expect_rejection(lambda args=args: parameters(*args))
    good = coefficients(4, 1, 2)
    mutations = []
    for index, replacement in [(3, ZERO), (3, scale(-1, good[3])),
                                (15, ONE), (0, add(good[0], (Fraction(1, 3), Fraction(0))))]:
        changed = good.copy()
        changed[index] = replacement
        mutations.append(changed)
    mutations.append(good[:-1])
    for changed in mutations:
        expect_rejection(lambda changed=changed: certify(4, 1, 2, changed))
    require(polynomial_coefficients(4, 1, 1) != good, 'omitted top term undetected')
    require(valuation(power(PI, 5)) == 5, 'valuation control')
    require(valuation(ZERO) is None, 'zero valuation control')
    expect_rejection(lambda: valuation((Fraction(1, 2), Fraction(0))))
    return len(bad_parameters)+len(mutations)+4


def main() -> None:
    counts = {'bands': 0, 'coefficients': 0, 'top_coefficients': 0,
              'independent_polynomial_coefficients': 0, 'precision_witnesses': 0,
              'literal_walsh_eigenvalues': 0}
    for n in range(1, MAX_N+1):
        for degree in range(n+1):
            for a in range(n-degree+1):
                data = coefficients(n, a, degree)
                counts['bands'] += 1
                counts['coefficients'] += len(data)
                counts['top_coefficients'] += certify(n, a, degree, data)
                if n <= 5:
                    require(data == polynomial_coefficients(n, a, degree),
                            'independent polynomial/Walsh disagreement')
                    counts['independent_polynomial_coefficients'] += len(data)
                if n <= 8:
                    counts['precision_witnesses'] += precision_cases(n, a, degree, data)
                if n <= 4:
                    for label in range(1 << n):
                        actual = ZERO
                        for s, z in enumerate(data):
                            actual = add(actual, scale((-1)**((s & label).bit_count()), z))
                        require(actual == value(label.bit_count(), a, degree),
                                'literal Walsh spectrum mismatch')
                        counts['literal_walsh_eigenvalues'] += 1
    counts['controls'] = controls()
    package = Path(__file__).resolve().parent
    names = ('README.md', 'TASK.json', 'SOURCES.json', 'VERIFY.json', 'verify.py')
    hashes = {name: sha256((package/name).read_bytes()).hexdigest() for name in names}
    print(json.dumps({'status': 'PASS', 'claim_type': 'scoped proof with finite corroboration',
                      'python': platform.python_version(), 'counts': counts,
                      'sha256': hashes}, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
