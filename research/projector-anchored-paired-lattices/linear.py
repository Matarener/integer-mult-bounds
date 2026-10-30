"""Small exact matrix operations for the paired-lattice certificate.

Produced by Nick Petalas. Apache-2.0.
"""

from fractions import Fraction

MAX_DIM = 16
MAX_INPUT_BITS = 64


def require(condition, message):
    if not condition:
        raise ValueError(message)


def matrix(rows, size):
    require(type(size) is int and 1 <= size <= MAX_DIM, "unsupported dimension")
    require(isinstance(rows, (list, tuple)) and len(rows) == size, "row count")
    result = []
    for row in rows:
        require(isinstance(row, (list, tuple)) and len(row) == size, "column count")
        converted = []
        for value in row:
            require(type(value) in (int, Fraction), "exact rational entries required")
            value = Fraction(value)
            require(max(abs(value.numerator).bit_length(), value.denominator.bit_length())
                    <= MAX_INPUT_BITS, "input coefficient too large")
            converted.append(value)
        result.append(tuple(converted))
    return tuple(result)


def identity(size):
    return tuple(tuple(Fraction(i == j) for j in range(size)) for i in range(size))


def zero(size):
    return tuple(tuple(Fraction(0) for _ in range(size)) for _ in range(size))


def multiply(left, right):
    size = len(left)
    require(size == len(right), "matrix size mismatch")
    return tuple(tuple(sum((left[i][k] * right[k][j] for k in range(size)), Fraction(0))
                       for j in range(size)) for i in range(size))


def inverse(value):
    size = len(value)
    rows = [[Fraction(entry) for entry in value[i]] + list(identity(size)[i])
            for i in range(size)]
    for column in range(size):
        pivot = next((i for i in range(column, size) if rows[i][column]), None)
        require(pivot is not None, "singular basis")
        rows[column], rows[pivot] = rows[pivot], rows[column]
        divisor = rows[column][column]
        rows[column] = [entry / divisor for entry in rows[column]]
        for i in range(size):
            if i != column:
                factor = rows[i][column]
                rows[i] = [x - factor * y for x, y in zip(rows[i], rows[column])]
    result = tuple(tuple(row[size:]) for row in rows)
    require(multiply(value, result) == identity(size), "inverse identity")
    return result


def valuation(value):
    require(value != 0, "zero has no finite valuation")
    numerator, denominator = abs(value.numerator), value.denominator
    return ((numerator & -numerator).bit_length()
            - (denominator & -denominator).bit_length())


def power_two(exponent):
    return Fraction(2 ** exponent) if exponent >= 0 else Fraction(1, 2 ** -exponent)


def paired(basis):
    size = len(basis)
    return tuple(tuple(basis[i % size][j % size] if i // size == j // size else Fraction(0)
                       for j in range(2 * size)) for i in range(2 * size))


def upper(block):
    size = len(block)
    return tuple(tuple(Fraction(i == j) + (block[i][j - size]
                       if i < size <= j else 0)
                       for j in range(2 * size)) for i in range(2 * size))


def block_at(value, row, column, size):
    return tuple(tuple(value[row * size + i][column * size + j]
                       for j in range(size)) for i in range(size))
