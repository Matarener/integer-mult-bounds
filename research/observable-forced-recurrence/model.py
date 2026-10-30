"""Exact reference certificates for an observed nonnegative recurrence.

The mathematical statement has arbitrary finite dimension. This reference
implementation accepts at most eight types and 16-bit rational input parts.
"""

from dataclasses import dataclass
from fractions import Fraction

Vector = tuple[Fraction, ...]
Matrix = tuple[Vector, ...]
MAX_TYPES = 8
INPUT_BITS = 16


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def dot(left: Vector, right: Vector) -> Fraction:
    require(len(left) == len(right) <= MAX_TYPES, "dot dimensions")
    return sum((x * y for x, y in zip(left, right)), Fraction(0))


def multiply(matrix: Matrix, vector: Vector) -> Vector:
    return tuple(dot(row, vector) for row in matrix)


def validate(matrix: Matrix, forcing: Vector, costs: Vector) -> None:
    size = len(matrix)
    require(1 <= size <= MAX_TYPES, "type capacity")
    require(len(forcing) == len(costs) == size, "vector dimensions")
    require(all(len(row) == size for row in matrix), "square matrix")
    entries = tuple(x for row in matrix for x in row) + forcing + costs
    for value in entries:
        require(isinstance(value, Fraction), "exact rational inputs required")
        require(value >= 0, "nonnegative inputs required")
        require(value.numerator.bit_length() <= INPUT_BITS, "numerator capacity")
        require(value.denominator.bit_length() <= INPUT_BITS, "denominator capacity")


def relevant(matrix: Matrix, forcing: Vector, costs: Vector) -> tuple[int, ...]:
    """Forward and backward closure, with edge j -> i for matrix[i][j]>0."""
    size = len(matrix)
    forward = {i for i in range(size) if forcing[i] > 0}
    backward = {i for i in range(size) if costs[i] > 0}
    for _ in range(size):
        forward |= {i for i in range(size)
                    if any(matrix[i][j] > 0 for j in forward)}
        backward |= {j for j in range(size)
                     if any(matrix[i][j] > 0 for i in backward)}
    return tuple(sorted(forward & backward))


def closure_relevant(matrix: Matrix, forcing: Vector, costs: Vector) -> tuple[int, ...]:
    """Checker's independent all-pairs reachability implementation."""
    size = len(matrix)
    paths = [[i == j or matrix[i][j] > 0 for j in range(size)]
             for i in range(size)]
    for middle in range(size):
        for end in range(size):
            for start in range(size):
                paths[end][start] |= paths[end][middle] and paths[middle][start]
    return tuple(i for i in range(size)
                 if any(forcing[j] > 0 and paths[i][j] for j in range(size))
                 and any(costs[j] > 0 and paths[j][i] for j in range(size)))


def restrict(matrix: Matrix, vector: Vector, indices: tuple[int, ...]) -> tuple[Matrix, Vector]:
    return (tuple(tuple(matrix[i][j] for j in indices) for i in indices),
            tuple(vector[i] for i in indices))


def identity_minus(matrix: Matrix) -> Matrix:
    return tuple(tuple(Fraction(i == j) - value for j, value in enumerate(row))
                 for i, row in enumerate(matrix))


def back_substitute(upper: list[list[Fraction]], rhs: list[Fraction]) -> Vector:
    size = len(rhs)
    result = [Fraction(0)] * size
    for i in reversed(range(size)):
        require(upper[i][i] != 0, "nonzero pivot")
        result[i] = (rhs[i] - sum(upper[i][j] * result[j]
                                  for j in range(i + 1, size))) / upper[i][i]
    return tuple(result)


def alternative(matrix: Matrix) -> tuple[bool, Vector]:
    """Classical sign-preserving M-matrix alternative, credited in PROOF.md."""
    size = len(matrix)
    upper = [list(row) for row in identity_minus(matrix)]
    rhs = [Fraction(1)] * size
    for pivot in range(size):
        if upper[pivot][pivot] <= 0:
            witness = [Fraction(0)] * size
            witness[pivot] = Fraction(1)
            for i in reversed(range(pivot)):
                witness[i] = -sum(upper[i][j] * witness[j]
                                  for j in range(i + 1, pivot + 1)) / upper[i][i]
            return False, tuple(witness)
        for i in range(pivot + 1, size):
            factor = upper[i][pivot] / upper[pivot][pivot]
            for j in range(pivot, size):
                upper[i][j] -= factor * upper[pivot][j]
            rhs[i] -= factor * rhs[pivot]
    return True, back_substitute(upper, rhs)


def solve(matrix: Matrix, rhs: Vector) -> Vector:
    size = len(rhs)
    upper = [list(row) for row in matrix]
    values = list(rhs)
    for k in range(size):
        pivot = next((i for i in range(k, size) if upper[i][k] != 0), None)
        require(pivot is not None, "invertible finite system")
        upper[k], upper[pivot] = upper[pivot], upper[k]
        values[k], values[pivot] = values[pivot], values[k]
        for i in range(k + 1, size):
            factor = upper[i][k] / upper[k][k]
            for j in range(k, size):
                upper[i][j] -= factor * upper[k][j]
            values[i] -= factor * values[k]
    return back_substitute(upper, values)


@dataclass(frozen=True)
class Zero:
    retained: tuple[int, ...] = ()


@dataclass(frozen=True)
class Finite:
    retained: tuple[int, ...]
    weights: Vector
    total: Vector
    ratio: Fraction


@dataclass(frozen=True)
class Divergent:
    retained: tuple[int, ...]
    witness: Vector
    block_gain: Fraction


Certificate = Zero | Finite | Divergent


def activation(matrix: Matrix, forcing: Vector) -> Vector:
    result = (Fraction(0),) * len(forcing)
    term = forcing
    for _ in range(len(forcing)):
        result = tuple(x + y for x, y in zip(result, term))
        term = multiply(matrix, term)
    return result


def certify(matrix: Matrix, forcing: Vector, costs: Vector) -> Certificate:
    validate(matrix, forcing, costs)
    kept = relevant(matrix, forcing, costs)
    if not kept:
        return Zero()
    reduced, beta = restrict(matrix, forcing, kept)
    gamma = tuple(costs[i] for i in kept)
    finite, vector = alternative(reduced)
    if finite:
        weights = vector
        ratio = max(x / y for x, y in zip(multiply(reduced, weights), weights))
        total = solve(identity_minus(reduced), beta)
        return Finite(kept, weights, total, ratio)
    for _ in range(len(kept) - 1):
        vector = multiply(reduced, vector)
    z = activation(reduced, beta)
    delta = min(x / y for x, y in zip(z, vector) if y > 0)
    return Divergent(kept, vector, delta * dot(gamma, vector))


def check_vector(vector: Vector, size: int, positive: bool = False) -> None:
    require(len(vector) == size, "certificate vector dimensions")
    for value in vector:
        require(isinstance(value, Fraction), "rational certificate vector")
        require(value > 0 if positive else value >= 0, "certificate vector sign")
        require(max(value.numerator.bit_length(), value.denominator.bit_length())
                <= 8192, "certificate arithmetic capacity")


def check(matrix: Matrix, forcing: Vector, costs: Vector, cert: Certificate) -> None:
    """Verify using only graph closure and matrix-vector arithmetic, no solve."""
    validate(matrix, forcing, costs)
    kept = closure_relevant(matrix, forcing, costs)
    require(cert.retained == kept, "exact input-output support")
    if not kept:
        require(isinstance(cert, Zero), "zero certificate type")
        return
    reduced, beta = restrict(matrix, forcing, kept)
    gamma = tuple(costs[i] for i in kept)
    size = len(kept)
    if isinstance(cert, Finite):
        check_vector(cert.weights, size, positive=True)
        check_vector(cert.total, size)
        require(isinstance(cert.ratio, Fraction) and 0 <= cert.ratio < 1,
                "strict rational contraction")
        require(all(x <= cert.ratio * y for x, y in
                    zip(multiply(reduced, cert.weights), cert.weights)),
                "contraction inequality")
        fixed = tuple(x + y for x, y in zip(multiply(reduced, cert.total), beta))
        require(fixed == cert.total, "total fixed point")
        return
    require(isinstance(cert, Divergent), "nonempty certificate type")
    check_vector(cert.witness, size)
    require(any(cert.witness), "nonzero subeigenvector")
    require(all(x >= y for x, y in zip(multiply(reduced, cert.witness), cert.witness)),
            "subeigenvector inequality")
    require(dot(gamma, cert.witness) > 0, "observable subeigenvector")
    z = activation(reduced, beta)
    require(all(value > 0 for value in z), "positive reachable activation")
    delta = min(x / y for x, y in zip(z, cert.witness) if y > 0)
    require(isinstance(cert.block_gain, Fraction) and cert.block_gain > 0,
            "positive rational block gain")
    require(cert.block_gain == delta * dot(gamma, cert.witness), "exact block gain")
