"""Small exact binary matrices. Nick Petalas, Apache-2.0."""

MAX_DIM = 16


def require(condition, message):
    if not condition:
        raise ValueError(message)


def matrix(rows, columns):
    require(0 <= len(rows) <= MAX_DIM and 0 <= columns <= MAX_DIM, "dimension")
    require(all(type(row) is int and 0 <= row < (1 << columns) for row in rows), "row")
    return tuple(rows)


def parity(value):
    return value.bit_count() & 1


def column(rows, index):
    return sum(((row >> index) & 1) << j for j, row in enumerate(rows))


def apply(rows, vector):
    return sum(parity(row & vector) << j for j, row in enumerate(rows))


def multiply(left, right):
    result = []
    for row in left:
        value = 0
        for j, other in enumerate(right):
            if (row >> j) & 1:
                value ^= other
        result.append(value)
    return tuple(result)


def identity(size):
    require(0 <= size <= MAX_DIM, "dimension")
    return tuple(1 << j for j in range(size))


def basis(vectors, ambient):
    require(0 <= ambient <= MAX_DIM and len(vectors) <= MAX_DIM, "basis dimension")
    pivots = [0] * ambient
    selected = []
    for vector in vectors:
        require(0 <= vector < (1 << ambient), "vector")
        reduced = vector
        for j in range(ambient - 1, -1, -1):
            if (reduced >> j) & 1:
                if pivots[j]:
                    reduced ^= pivots[j]
                else:
                    pivots[j] = reduced
                    selected.append(vector)
                    break
    return tuple(selected)


def rank(rows):
    # All matrices used here have at most MAX_DIM columns.
    return len(basis(rows, MAX_DIM))


def coordinates(independent, vector, ambient):
    require(len(independent) == len(basis(independent, ambient)), "dependent basis")
    pivots = [(0, 0)] * ambient
    for index, original in enumerate(independent):
        value, mask = original, 1 << index
        for j in range(ambient - 1, -1, -1):
            if (value >> j) & 1:
                if pivots[j][0]:
                    value ^= pivots[j][0]
                    mask ^= pivots[j][1]
                else:
                    pivots[j] = (value, mask)
                    break
    value, mask = vector, 0
    for j in range(ambient - 1, -1, -1):
        if (value >> j) & 1:
            require(pivots[j][0] != 0, "outside span")
            value ^= pivots[j][0]
            mask ^= pivots[j][1]
    require(value == 0, "outside ambient")
    return mask


def factor(rows):
    """Return X,Y with YX=M, X onto and Y injective."""
    n = len(rows)
    matrix(rows, n)
    independent = basis(tuple(column(rows, j) for j in range(n)), n)
    coordinate_columns = tuple(coordinates(independent, column(rows, j), n) for j in range(n))
    x = tuple(column(coordinate_columns, j) for j in range(len(independent)))
    y = tuple(column(independent, j) for j in range(n))
    require(multiply(y, x) == rows, "rank factorization")
    require(rank(x) == rank(y) == len(independent), "factor ranks")
    return x, y
