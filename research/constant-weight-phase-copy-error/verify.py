#!/usr/bin/env python3
"""Exact constant-weight phase COPY projection. Apache-2.0.

Produced by Nick Petalas. No predecessor executable is imported.
"""

from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
import platform


ROOTS = ((1, 0), (0, 1), (-1, 0), (0, -1))
MAX_AXES = 128
MAX_WIDTH = 256
PACKAGE_FILES = (
    "PROOF.md", "README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py"
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def multiply(left, right):
    a, b = left
    c, d = right
    return a * c - b * d, a * d + b * c


def target_overlap(exponent):
    """Return ((1-i)/2)^exponent without a loop in the exponent."""
    require(type(exponent) is int and 0 <= exponent <= MAX_AXES * MAX_WIDTH,
            "unsupported overlap exponent")
    half, odd = divmod(exponent, 2)
    numerator = ROOTS[(-half) % 4]
    if odd:
        numerator = multiply(numerator, (1, -1))
    denominator = 1 << (half + odd)
    return F(numerator[0], denominator), F(numerator[1], denominator)


def layer_solution(n, k, width):
    require(all(type(v) is int for v in (n, k, width)), "integer parameters required")
    require(1 <= n <= MAX_AXES and 1 <= k <= n, "unsupported layer")
    require(1 <= width <= MAX_WIDTH, "unsupported width")
    radius = min(k, n - k)
    row_sum = sum((F(comb(k, j) * comb(n - k, j), 1 << (width * j))
                   for j in range(radius + 1)), F(0))
    overlap = target_overlap(k * width)
    coefficient = overlap[0] / row_sum, overlap[1] / row_sum
    error = 1 - F(comb(n, k), 1 << (width * k)) / row_sum
    require(row_sum > 0 and 0 < error < 1, "projection range invariant")
    return coefficient, error, row_sum


def literal_diagonals(n, k, width, phase=1):
    """Enumerate every entry of each literal tensor diagonal in the small domain."""
    require(1 <= n <= 6 and 0 <= k <= n and 1 <= width <= 8 and n * width <= 10,
            "literal enumeration domain exceeded")
    require(phase in (1, 2), "unsupported literal phase")
    masks = [sum(1 << bit for bit in subset) for subset in combinations(range(n), k)]
    diagonals = []
    for mask in masks:
        base = [(phase * (mask & address).bit_count()) % 4 for address in range(1 << n)]
        diagonal = [0]
        for _ in range(width):
            diagonal = [(left + right) % 4 for left in diagonal for right in base]
        require(len(diagonal) == 1 << (n * width), "tensor dimension invariant")
        diagonals.append(diagonal)
    return masks, diagonals


def literal_average(exponents):
    real = sum(ROOTS[value][0] for value in exponents)
    imag = sum(ROOTS[value][1] for value in exponents)
    return F(real, len(exponents)), F(imag, len(exponents))


def literal_gram(diagonals):
    size = len(diagonals)
    dimension = len(diagonals[0])
    gram = [[F(0) for _ in range(size)] for _ in range(size)]
    rhs = []
    for i, left in enumerate(diagonals):
        rhs.append(literal_average([(-value) % 4 for value in left]))
        for j, right in enumerate(diagonals):
            real, imag = literal_average([(right[a] - left[a]) % 4
                                          for a in range(dimension)])
            require(imag == 0, "literal fixed-layer Gram must be real")
            gram[i][j] = real
    return gram, rhs


def solve_positive_gram(gram, rhs):
    """Independent exact elimination of both real and imaginary normal equations."""
    size = len(gram)
    rows = [list(gram[i]) + list(rhs[i]) for i in range(size)]
    for column in range(size):
        pivot = rows[column][column]
        require(pivot > 0, "nonpositive exact Schur pivot")
        for i in range(column + 1, size):
            factor = rows[i][column] / pivot
            for j in range(column, size + 2):
                rows[i][j] -= factor * rows[column][j]
    solution = [(F(0), F(0)) for _ in range(size)]
    for i in range(size - 1, -1, -1):
        parts = []
        for part in range(2):
            remainder = sum((rows[i][j] * solution[j][part]
                             for j in range(i + 1, size)), F(0))
            parts.append((rows[i][size + part] - remainder) / rows[i][i])
        solution[i] = tuple(parts)
    return solution


def literal_error(diagonals, coefficients):
    dimension = len(diagonals[0])
    total = F(0)
    for address in range(dimension):
        real, imag = F(0), F(0)
        for diagonal, coefficient in zip(diagonals, coefficients, strict=True):
            a, b = multiply(coefficient, ROOTS[diagonal[address]])
            real += a
            imag += b
        total += (1 - real) ** 2 + imag ** 2
    return total / dimension


def verify_literal_cases():
    counts = {"interfaces": 0, "source_diagonal_entries": 0,
              "gram_entries": 0, "normal_equations": 0,
              "endpoint_basis_columns": 0}
    for n in range(1, 7):
        for width in range(1, min(8, 10 // n) + 1):
            for k in range(1, n + 1):
                masks, diagonals = literal_diagonals(n, k, width)
                gram, rhs = literal_gram(diagonals)
                solution = solve_positive_gram(gram, rhs)
                coefficient, error, row_sum = layer_solution(n, k, width)
                require(solution == [coefficient] * len(masks), "attaining coefficients differ")
                require(literal_error(diagonals, solution) == error, "literal distance differs")
                for i, left in enumerate(masks):
                    require(sum(gram[i], F(0)) == row_sum, "literal row sum differs")
                    for j, right in enumerate(masks):
                        swaps = (left ^ right).bit_count() // 2
                        require(gram[i][j] == F(1, 1 << (width * swaps)), "intersection kernel differs")
                    for part in range(2):
                        value = sum((gram[i][j] * solution[j][part]
                                     for j in range(len(masks))), F(0))
                        require(value == rhs[i][part], "literal residual not orthogonal")
                dimension = len(diagonals[0])
                counts["interfaces"] += 1
                counts["source_diagonal_entries"] += len(masks) * dimension
                counts["gram_entries"] += len(masks) ** 2
                counts["normal_equations"] += 2 * len(masks)
                counts["endpoint_basis_columns"] += verify_endpoints(diagonals, solution)
    return counts


def run_at_address(diagonals, coefficients, address, source, accumulator,
                   restore=True, erase=False):
    """Literal phase, accumulator ADD, inverse-phase execution at one address."""
    if erase:
        accumulator = (0, 0)
    for diagonal, coefficient in zip(diagonals, coefficients, strict=True):
        phase = ROOTS[diagonal[address]]
        source = multiply(phase, source)
        term = multiply(coefficient, source)
        accumulator = accumulator[0] + term[0], accumulator[1] + term[1]
        if restore:
            source = multiply((phase[0], -phase[1]), source)
    return source, accumulator


def verify_endpoints(diagonals, coefficients):
    """Check both input columns at every address, including the arbitrary dirty y column."""
    dimension = len(diagonals[0])
    for address in range(dimension):
        response = (F(0), F(0))
        for diagonal, coefficient in zip(diagonals, coefficients, strict=True):
            term = multiply(coefficient, ROOTS[diagonal[address]])
            response = response[0] + term[0], response[1] + term[1]
        for source, accumulator in (((1, 0), (0, 0)), ((0, 0), (1, 0))):
            returned_source, returned_accumulator = run_at_address(
                diagonals, coefficients, address, source, accumulator)
            expected = multiply(response, source)
            require(returned_source == source, "source return changed")
            require(returned_accumulator == (accumulator[0] + expected[0],
                                            accumulator[1] + expected[1]), "dirty endpoint differs")
    return 2 * dimension


def verify_large_formulas():
    count = 0
    for n in (8, 16, 32, 64, 128):
        for k in (1, n // 2, n - 1, n):
            for width in (1, 2, 3, 4, 8, 16, 64, 256):
                coefficient, error, row_sum = layer_solution(n, k, width)
                radius = min(k, n - k)
                integer_sum = sum(comb(k, j) * comb(n - k, j) << (width * (radius - j))
                                  for j in range(radius + 1))
                require(row_sum == F(integer_sum, 1 << (width * radius)), "integer row sum differs")
                magnitude = coefficient[0] ** 2 + coefficient[1] ** 2
                require(magnitude * row_sum * comb(n, k) == 1 - error, "projection mass differs")
                if k == 1:
                    require(error == F((1 << width) - 1, (1 << width) + n - 1),
                            "one-phase closed form differs")
                count += 1
    return count


def verify_controls():
    _, diagonals = literal_diagonals(2, 1, 2)
    coefficient, error, _ = layer_solution(2, 1, 2)
    wrong_phase = coefficient[0], -coefficient[1]
    require(literal_error(diagonals, [wrong_phase] * 2) > error, "conjugation control")
    squared = multiply(coefficient, coefficient)
    require(literal_error(diagonals, [squared] * 2) > error, "external coefficient power control")
    wrong_row = F(1) + F(1, 16)
    b = target_overlap(2)
    wrong = b[0] / wrong_row, b[1] / wrong_row
    require(literal_error(diagonals, [wrong] * 2) > error, "exchange distance control")
    wrong = b[0] / F(1, 4), b[1] / F(1, 4)
    require(literal_error(diagonals, [wrong] * 2) > error, "diagonal term control")
    _, identity = literal_diagonals(2, 0, 2)
    require(literal_error(identity, [(F(1), F(0))]) == 0 < error, "identity-history boundary")
    _, paulis = literal_diagonals(2, 1, 2, phase=2)
    gram, rhs = literal_gram(paulis)
    require(literal_error(paulis, solve_positive_gram(gram, rhs)) == 1, "phase alphabet boundary")
    _, one = literal_diagonals(1, 1, 1)
    require(literal_error(one, [(F(1, 2), F(0))]) == F(3, 4)
            > layer_solution(1, 1, 1)[1], "real coefficient boundary")
    clean_coefficient = [layer_solution(1, 1, 1)[0]]
    normal = run_at_address(one, clean_coefficient, 1, (0, 0), (1, 0))
    erased = run_at_address(one, clean_coefficient, 1, (0, 0), (1, 0), erase=True)
    require(normal != erased, "erasing the dirty accumulator must change its basis column")
    unrestored = run_at_address(one, clean_coefficient, 1, (1, 0), (0, 0), restore=False)
    require(unrestored[0] != (1, 0), "unreturned phase changes the source basis column")
    return 9


def verify_invalid_inputs():
    bad = ((0, 1, 1), (2, 0, 1), (2, 3, 1), (2, 1, 0), (-1, 1, 1),
           (True, 1, 1), (2, 1.0, 1), (2, 1, "1"), (129, 1, 1), (2, 1, 257))
    for parameters in bad:
        rejected = False
        try:
            layer_solution(*parameters)
        except ValueError:
            rejected = True
        require(rejected, "invalid parameters were accepted")
    return len(bad)


def main():
    results = {"literal": verify_literal_cases(), "large_formula_interfaces": verify_large_formulas(),
               "semantic_controls": verify_controls(), "invalid_input_controls": verify_invalid_inputs()}
    results["fixtures"] = {}
    for n, k, width in ((2, 1, 1), (4, 2, 1), (8, 4, 1), (8, 4, 2)):
        coefficient, error, row_sum = layer_solution(n, k, width)
        results["fixtures"][f"{n},{k},{width}"] = {
            "coefficient": [str(part) for part in coefficient],
            "squared_error": str(error), "row_sum": str(row_sum)}
    directory = Path(__file__).resolve().parent
    hashes = {name: sha256((directory / name).read_bytes()).hexdigest() for name in PACKAGE_FILES}
    print(json.dumps({"status": "PASS_CONSTANT_WEIGHT_PHASE_COPY_ERROR", "result": results,
                      "package_sha256": hashes, "python": platform.python_version()}, sort_keys=True))


if __name__ == "__main__":
    main()
