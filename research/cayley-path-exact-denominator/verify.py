"""Exact Cayley path denominators. Produced by Nick Petalas. Apache-2.0."""

from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from math import comb, gcd, lcm
from pathlib import Path


MAX_DIMENSION = 32
PACKAGE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def scaled_parameter(parameter):
    require(type(parameter) is Fraction, "parameter must be a Fraction")
    require(0 < parameter <= Fraction(1, 4), "parameter outside (0,1/4]")
    require(parameter.denominator.bit_length() <= 256, "parameter capacity")
    common = gcd(parameter.numerator, 2 * parameter.denominator)
    return parameter.numerator // common, 2 * parameter.denominator // common


def continuant(n, a, b):
    require(type(n) is int and 0 <= n <= MAX_DIMENSION, "dimension capacity")
    require(type(a) is int and type(b) is int and a > 0 and b > 0,
            "positive integer parameters required")
    require(gcd(a, b) == 1, "parameters must be coprime")
    require(max(a.bit_length(), b.bit_length()) <= 257, "integer capacity")
    previous, current = 0, 1
    for _ in range(n):
        previous, current = current, b * current + a * a * previous
    return current


def block_denominator(n, parameter):
    a, b = scaled_parameter(parameter)
    require(type(n) is int and 1 <= n <= MAX_DIMENSION, "positive block dimension required")
    determinant = continuant(n, a, b)
    return determinant // gcd(determinant, 2 * b)


def path_denominator(edges, parameter):
    require(type(edges) is tuple and len(edges) < MAX_DIMENSION, "edge capacity")
    require(all(type(x) is int and x in (-1, 0, 1) for x in edges),
            "edges must be signed unit edges or absent")
    scaled_parameter(parameter)
    denominator, size = 1, 1
    for edge in edges:
        if edge:
            size += 1
        else:
            denominator = lcm(denominator, block_denominator(size, parameter))
            size = 1
    return lcm(denominator, block_denominator(size, parameter))


def inverse(matrix):
    n = len(matrix)
    require(1 <= n <= MAX_DIMENSION and all(len(row) == n for row in matrix),
            "square matrix capacity")
    rows = [[Fraction(x) for x in row] + [Fraction(i == j) for j in range(n)]
            for i, row in enumerate(matrix)]
    for column in range(n):
        pivot = next((i for i in range(column, n) if rows[i][column]), None)
        require(pivot is not None, "singular matrix")
        rows[column], rows[pivot] = rows[pivot], rows[column]
        divisor = rows[column][column]
        rows[column] = [x / divisor for x in rows[column]]
        for i in range(n):
            if i != column:
                factor = rows[i][column]
                rows[i] = [x - factor * y for x, y in zip(rows[i], rows[column])]
    return [row[n:] for row in rows]


def dense_cayley(edges, parameter):
    # The comparison uses I-tK/2 directly, without continuants or scaling.
    path_denominator(edges, parameter)
    n = len(edges) + 1
    matrix = [[Fraction(i == j) for j in range(n)] for i in range(n)]
    for i, edge in enumerate(edges):
        matrix[i][i + 1] = -parameter * edge / 2
        matrix[i + 1][i] = parameter * edge / 2
    solved = inverse(matrix)
    return [[2 * solved[i][j] - (i == j) for j in range(n)] for i in range(n)]


def common_denominator(matrix):
    return lcm(*(x.denominator for row in matrix for x in row))


def matvec(matrix, vector):
    require(len(matrix) == len(vector), "matrix/vector dimension mismatch")
    return [sum((x * y for x, y in zip(row, vector)), Fraction(0)) for row in matrix]


def check_connected():
    count = 0
    for denominator in range(4, 29):
        for numerator in range(1, denominator // 4 + 1):
            if gcd(numerator, denominator) != 1:
                continue
            parameter = Fraction(numerator, denominator)
            a, b = scaled_parameter(parameter)
            for n in range(1, 10):
                determinant = continuant(n, a, b)
                closed = sum(comb(n - k, k) * a ** (2 * k) * b ** (n - 2 * k)
                             for k in range(n // 2 + 1))
                require(determinant == closed, "continuant matching formula")
                require(gcd(determinant, a) == 1, "corner coprimality")
                matrix = dense_cayley((1,) * (n - 1), parameter)
                expected = block_denominator(n, parameter)
                require(common_denominator(matrix) == expected, "connected denominator")
                if n > 1:
                    require(matrix[0][-1].denominator == expected, "corner minimality")
                count += 1
    return count


def check_signed_supports():
    count = 0
    for parameter in (Fraction(1, 4), Fraction(2, 9), Fraction(3, 13)):
        for n in range(1, 7):
            for edges in product((-1, 0, 1), repeat=n - 1):
                matrix = dense_cayley(edges, parameter)
                expected = path_denominator(edges, parameter)
                require(common_denominator(matrix) == expected, "signed support denominator")
                backwards = inverse(matrix)
                require(backwards == [list(row) for row in zip(*matrix)],
                        "Cayley inverse must be its transpose")
                require(common_denominator(backwards) == expected, "inverse denominator")
                count += 1
    return count


def instructions():
    # Private fixtures have two independent roles and this fixed tuple grammar.
    return (
        ("linear", 0, ((0, Fraction(1, 2)), (1, Fraction(-2, 3)))),
        ("linear", 1, ((0, Fraction(0)), (0, Fraction(5, 7)))),
        ("apply", 0, 0, 1), ("apply", 1, 1, -1),
        ("query", 0, 1, 0, 1, Fraction(2, 5)),
        ("query", 1, 1, 1, -1, Fraction(-3, 11)),
    )


def product_denominators(coefficients):
    coefficients = tuple(coefficients)
    require(len(coefficients) <= 16, "coefficient capacity")
    result = 1
    for coefficient in coefficients:
        result *= coefficient.denominator
    return result


def exact_program(program, matrices, denominators, initial):
    require(len(program) <= 8 and len(initial) == 2, "fixture program capacity")
    require(all(ins in instructions() for ins in program), "unknown fixture instruction")
    registers = [row[:] for row in initial]
    bound = 1
    for ins in program:
        kind, dst = ins[:2]
        if kind == "linear":
            terms = ins[2]
            result = [sum((c * registers[src][j] for src, c in terms), Fraction(0))
                      for j in range(len(registers[dst]))]
            bound *= product_denominators(c for _, c in terms)
        else:
            src = dst if kind == "apply" else ins[2]
            label, direction = ins[2:4] if kind == "apply" else ins[3:5]
            matrix = matrices[label]
            if direction == -1:
                matrix = [list(row) for row in zip(*matrix)]
            value = matvec(matrix, registers[src])
            bound *= denominators[label]
            if kind == "query":
                coefficient = ins[5]
                bound *= coefficient.denominator
                result = [old + coefficient * new
                          for old, new in zip(registers[dst], value)]
            else:
                result = value
        registers[dst] = result
    require(all(bound % x.denominator == 0 for row in registers for x in row),
            "returned dirty-role denominators must divide the bound")
    return registers, bound


def check_registers():
    parameter, word = Fraction(1, 4), (0, 1, 0, 1)
    edges = [tuple(int(x == label) for x in word) for label in range(2)]
    matrices = [dense_cayley(edge, parameter) for edge in edges]
    denominators = [path_denominator(edge, parameter) for edge in edges]
    programs = [(ins,) for ins in instructions()] + list(product(instructions(), repeat=2))
    count = 0
    for program in programs:
        # Every column of the complete bank map, including every dirty input.
        for column in range(10):
            initial = [[Fraction(column == 5 * role + j) for j in range(5)]
                       for role in range(2)]
            returned, bound = exact_program(program, matrices, denominators, initial)
            require(all(bound % (new - old).denominator == 0
                        for row, oldrow in zip(returned, initial)
                        for new, old in zip(row, oldrow)), "endpoint difference lattice")
            count += 1
    return {"programs": len(programs), "independent_input_columns": count}


def truncate_ratio(numerator, denominator):
    require(denominator > 0, "positive truncation denominator required")
    return (1 if numerator >= 0 else -1) * (abs(numerator) // denominator)


def rounded_apply_sequence(matrices, order, bits, initial):
    require(0 <= bits <= 4096 and len(order) <= 32, "dyadic replay capacity")
    scale = 1 << bits
    tables = [[[truncate_ratio(x.numerator * scale, x.denominator) for x in row]
               for row in matrix] for matrix in matrices]
    values = [int(x * scale) for x in initial]
    for label in order:
        values = [truncate_ratio(sum(x * y for x, y in zip(row, values)), scale)
                  for row in tables[label]]
    return [Fraction(x, scale) for x in values]


def check_guard_fixture():
    parameter, word = Fraction(1, 4), (0, 1) * 4
    edges = [tuple(int(x == label) for x in word) for label in range(2)]
    matrices = [dense_cayley(edge, parameter) for edge in edges]
    require([path_denominator(edge, parameter) for edge in edges] == [65, 65],
            "alternating path denominators")
    order = (1, 0) * 4
    initial = [Fraction(j == 8) for j in range(9)]
    exact = initial
    for label in order:
        exact = matvec(matrices[label], exact)
    require(exact[0] == Fraction(16, 65) ** 8, "unique shortest propagation path")
    gain = 9 ** 8
    error_factor = 8 * gain * (9 * gain + 1)
    old_lattice, new_lattice = 12 ** 72, 65 ** 8
    old_bits = (4 * error_factor * old_lattice - 1).bit_length()
    new_bits = (4 * error_factor * new_lattice - 1).bit_length()
    require((old_bits, new_bits) == (318, 108), "sufficient precision fixture")
    for bits, lattice in ((old_bits, old_lattice), (new_bits, new_lattice)):
        computed = rounded_apply_sequence(matrices, order, bits, initial)
        error = Fraction(error_factor, 1 << bits)
        require(error <= Fraction(1, 4 * lattice), "funded error allowance")
        require(all(abs(x - y) <= error for x, y in zip(computed, exact)),
                "actual complete returned-vector error")
        require(abs(computed[0]) > Fraction(1, 2 * lattice), "nonzero verdict")
    return {"dimension": 9, "calls": 8, "coarse_bits": old_bits,
            "refined_bits": new_bits, "saved_bits": old_bits - new_bits,
            "endpoint": str(exact[0])}


def check_controls():
    count = 0
    for parameter in (Fraction(0), Fraction(-1, 4), Fraction(1, 3), 0.25):
        try:
            block_denominator(2, parameter)
        except ValueError:
            count += 1
        else:
            raise ValueError("invalid parameter accepted")
    for edges in ((2,), (True,), (1,) * MAX_DIMENSION):
        try:
            path_denominator(edges, Fraction(1, 4))
        except ValueError:
            count += 1
        else:
            raise ValueError("invalid edges accepted")
    parameter = Fraction(1, 4)
    actual = common_denominator(dense_cayley((1, 1), parameter))
    require(actual != continuant(3, 1, 8), "omitted gcd mutation must fail")
    count += 1
    # The deliberately unscaled b=18,a=2 formula gives 82 instead of 41.
    require(common_denominator(dense_cayley((1,), Fraction(2, 9))) !=
            (18 * 18 + 2 * 2) // gcd(18 * 18 + 2 * 2, 36),
            "omitted primitive scaling mutation must fail")
    count += 1
    require(path_denominator((1, 1, 0, 1, 1), parameter) == 33,
            "repeated runs use lcm, not product")
    require(path_denominator((1, 1, 0, 1), parameter) == 2145,
            "unequal runs use lcm, not maximum")
    count += 2
    scaled = [[x / 7 for x in row] for row in dense_cayley((1,), parameter)]
    require(any(65 % x.denominator != 0 for row in scaled for x in row),
            "scalar denominator omission must fail")
    count += 1
    return count


def authenticate_inputs():
    root = PACKAGE.parent.parent
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    rows = sources["files"]
    require(len(rows) <= 16, "source manifest capacity")
    for row in rows:
        if row["usage"] == "input":
            require(sha256((root / row["path"]).read_bytes()).hexdigest() == row["sha256"],
                    "source hash mismatch: " + row["path"])


def main():
    authenticate_inputs()
    result = {"schema": "cayley-path-exact-denominator/v1",
              "connected_matrices": check_connected(),
              "signed_support_matrices": check_signed_supports(),
              "register_fixtures": check_registers(),
              "guard_fixture": check_guard_fixture(),
              "rejection_and_boundary_controls": check_controls()}
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
             "VALIDATION.md", "verify.py")
    result["package_sha256"] = {name: sha256((PACKAGE / name).read_bytes()).hexdigest()
                                for name in names}
    print(json.dumps(result, indent=2, sort_keys=True))
    print("PASS_CAYLEY_PATH_EXACT_DENOMINATOR")


if __name__ == "__main__":
    main()
