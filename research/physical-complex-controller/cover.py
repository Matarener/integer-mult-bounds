# SPDX-License-Identifier: Apache-2.0
"""Exact lexicographic row indexing of the fixed binary orthogonal cover.

Dimension is a source constant, 73 for the selected caller. Matrix entries
and cover labels are bounded finite control; no runtime payload cardinality
or input width enters this arithmetic. The group-count formula is prior work.
"""


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def parity(value):
    return value.bit_count() & 1


def act(rows, value):
    return sum(parity(row & value) << i for i, row in enumerate(rows))


def transpose(rows):
    n = len(rows)
    return tuple(sum(((rows[i] >> j) & 1) << i for i in range(n)) for j in range(n))


def multiply(left, right):
    require(len(left) == len(right), "fixed matrix dimensions")
    out = []
    for row in left:
        value = 0
        for j, other in enumerate(right):
            if row >> j & 1:
                value ^= other
        out.append(value)
    return tuple(out)


def is_orthogonal(rows):
    n = len(rows)
    return all(type(r) is int and 0 <= r < 1 << n for r in rows) and all(
        parity(a & b) == (i == j) for i, a in enumerate(rows) for j, b in enumerate(rows))


def group_orders(n):
    values = [1]
    for remaining in range(1, n + 1):
        choices = (1 << (remaining - 1)) - int(remaining > 1 and remaining % 2 == 1)
        values.append(choices * values[-1])
    return tuple(values)


def solutions(equations, dimension):
    """Count one affine binary solution space by exact elimination."""
    pivots = {}
    for coefficients, rhs in equations:
        while coefficients:
            pivot = coefficients.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = coefficients, rhs
                break
            old, value = pivots[pivot]
            coefficients ^= old
            rhs ^= value
        if not coefficients and rhs:
            return 0
    return 1 << (dimension - len(pivots))


class OrthogonalCover:
    def __init__(self, dimension):
        require(type(dimension) is int and 1 <= dimension <= 73, "fixed cover dimension")
        self.dimension = dimension
        self.orders = group_orders(dimension)
        self.size = self.orders[-1]

    def _setup(self, prefix):
        n = self.dimension
        omega = (1 << n) - 1
        characteristic = omega
        for row in prefix:
            characteristic ^= row
        equations = [(row, 0) for row in prefix] + [(omega, 1)]
        remaining = n - len(prefix)
        # Choosing the characteristic vector would leave an alternating
        # complement, which has no norm-one next row. The last row is allowed.
        forbidden = characteristic if remaining > 1 and parity(characteristic) else None
        return equations, forbidden

    @staticmethod
    def _allowed(equations, value):
        return value is not None and all(parity(row & value) == rhs for row, rhs in equations)

    def _count(self, equations, forbidden):
        return solutions(equations, self.dimension) - int(self._allowed(equations, forbidden))

    def _row_unrank(self, prefix, index):
        equations, forbidden = self._setup(prefix)
        require(0 <= index < self._count(equations, forbidden), "cover row ordinal")
        result = 0
        for bit in reversed(range(self.dimension)):
            zero_count = self._count(equations + [(1 << bit, 0)], forbidden)
            value = int(index >= zero_count)
            if value:
                index -= zero_count
                result |= 1 << bit
            equations.append((1 << bit, value))
        require(index == 0, "complete cover row unrank")
        return result

    def _row_rank(self, prefix, row):
        equations, forbidden = self._setup(prefix)
        require(self._allowed(equations, row) and row != forbidden, "extendible orthogonal prefix")
        result = 0
        for bit in reversed(range(self.dimension)):
            value = (row >> bit) & 1
            if value:
                result += self._count(equations + [(1 << bit, 0)], forbidden)
            equations.append((1 << bit, value))
        return result

    def unrank(self, index):
        require(type(index) is int and 0 <= index < self.size, "finite cover label")
        rows = []
        for position in range(self.dimension):
            suffixes = self.orders[self.dimension - position - 1]
            ordinal, index = divmod(index, suffixes)
            rows.append(self._row_unrank(rows, ordinal))
        require(index == 0 and is_orthogonal(rows), "complete orthogonal cover value")
        return tuple(rows)

    def rank(self, rows):
        require(len(rows) == self.dimension and is_orthogonal(rows), "orthogonal cover matrix")
        index = 0
        for position, row in enumerate(rows):
            index += self._row_rank(rows[:position], row) * self.orders[self.dimension - position - 1]
        require(0 <= index < self.size, "ranked cover label")
        return index
