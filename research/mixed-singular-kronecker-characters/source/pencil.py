"""Bounded exact witnesses for the written Kronecker determinant theorem.

The implementation is deliberately limited to small fixtures; PROOF.md supplies
the arbitrary-field/dimension argument. apoursh with OpenAI Codex; Apache-2.0.
"""
from itertools import product


def require(ok, message):
    if not ok:
        raise ValueError(message)


class Field:
    """F2, F3, F5, or F4=F2[w]/(w^2+w+1), encoded 0,1,w,w+1."""
    def __init__(self, order):
        require(type(order) is int and order in (2, 3, 4, 5), 'unsupported field')
        self.q = order
        self.p = 2 if order == 4 else order

    def add(self, a, b):
        return a ^ b if self.q == 4 else (a + b) % self.q

    def neg(self, a):
        return a if self.q == 4 else -a % self.q

    def sub(self, a, b):
        return self.add(a, self.neg(b))

    def mul(self, a, b):
        if self.q != 4:
            return a * b % self.q
        value = 0
        for bit in range(2):
            if (b >> bit) & 1:
                value ^= a << bit
        return value ^ 7 if value & 4 else value

    def power(self, a, exponent):
        if exponent < 0:
            require(a != 0, 'inverse of zero')
            exponent %= self.q - 1
        value = 1
        for _ in range(exponent):
            value = self.mul(value, a)
        return value

    def inv(self, a):
        require(a != 0, 'inverse of zero')
        return self.power(a, self.q - 2)


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def transpose(a):
    return [list(row) for row in zip(*a)]


def multiply(a, b, field):
    require(len(a[0]) == len(b), 'matrix dimension mismatch')
    result = [[0] * len(b[0]) for _ in a]
    for i, row in enumerate(a):
        for k, value in enumerate(row):
            if value:
                for j, other in enumerate(b[k]):
                    result[i][j] = field.add(result[i][j], field.mul(value, other))
    return result


def mix(a, b, x, y, field):
    return [[field.add(field.mul(x, u), field.mul(y, v))
             for u, v in zip(row, other)] for row, other in zip(a, b)]


def determinant(a, field):
    rows = [row[:] for row in a]
    result = 1
    for col in range(len(rows)):
        pivot = next((i for i in range(col, len(rows)) if rows[i][col]), None)
        if pivot is None:
            return 0
        if pivot != col:
            rows[col], rows[pivot] = rows[pivot], rows[col]
            result = field.neg(result)
        result = field.mul(result, rows[col][col])
        inv = field.inv(rows[col][col])
        for i in range(col + 1, len(rows)):
            scale = field.mul(rows[i][col], inv)
            rows[i] = [field.sub(x, field.mul(scale, y))
                       for x, y in zip(rows[i], rows[col])]
    return result


def inverse(a, field):
    n = len(a)
    rows = [row[:] + unit for row, unit in zip(a, identity(n))]
    for col in range(n):
        pivot = next((i for i in range(col, n) if rows[i][col]), None)
        require(pivot is not None, 'singular matrix')
        rows[col], rows[pivot] = rows[pivot], rows[col]
        inv = field.inv(rows[col][col])
        rows[col] = [field.mul(inv, value) for value in rows[col]]
        for i in range(n):
            if i != col:
                scale = rows[i][col]
                rows[i] = [field.sub(x, field.mul(scale, y))
                           for x, y in zip(rows[i], rows[col])]
    return [row[n:] for row in rows]


def tensor(a, b, field):
    return [[field.mul(x, y) for x in row for y in other]
            for row in a for other in b]


def slices(e, r):
    require(type(e) is int and type(r) is int and 1 <= e <= 5 and 1 <= r <= 3,
            'outside bounded positive-index fixture domain')
    return ([[int(j == i) for j in range((e + 1) * r)] for i in range(e * r)],
            [[int(j == i + r) for j in range((e + 1) * r)] for i in range(e * r)])


def symmetric_power(k, action, field):
    """Ordinary monomial substitution, using convolution without factorials."""
    require(type(k) is int and 0 <= k <= 5, 'unsupported degree')
    columns = []
    for i in range(k + 1):
        coefficients = [1]
        for linear in [action[0]] * (k - i) + [action[1]] * i:
            result = [0] * (len(coefficients) + 1)
            for j, value in enumerate(coefficients):
                result[j] = field.add(result[j], field.mul(value, linear[0]))
                result[j + 1] = field.add(result[j + 1], field.mul(value, linear[1]))
            coefficients = result
        columns.append(coefficients)
    return transpose(columns)


def general_linear_two(field):
    for entries in product(range(field.q), repeat=4):
        action = [list(entries[:2]), list(entries[2:])]
        if determinant(action, field):
            yield action


def lift(e, r, action, multiplicity, field):
    slices(e, r)
    require(len(action) == 2 and all(len(row) == 2 for row in action),
            'slice action dimension mismatch')
    require(len(multiplicity) == r and all(len(row) == r for row in multiplicity),
            'multiplicity dimension mismatch')
    require(all(type(x) is int and 0 <= x < field.q
                for matrix in (action, multiplicity) for row in matrix for x in row),
            'matrix entry outside field')
    require(determinant(action, field) != 0, 'singular slice action')
    require(determinant(multiplicity, field) != 0, 'singular multiplicity action')
    p = tensor(transpose(symmetric_power(e - 1, action, field)), multiplicity, field)
    q = tensor(inverse(symmetric_power(e, action, field), field),
               transpose(inverse(multiplicity, field)), field)
    return p, q, action


def fixes(first, second, witness, field):
    p, q, action = witness
    for row, target in zip(action, (first, second)):
        mixed = mix(first, second, *row, field)
        if multiply(multiply(p, mixed, field), transpose(q), field) != target:
            return False
    return True


def character(e, r, triple, field, left=False):
    x, y, z = triple
    if left:
        x, y = y, x
    return field.mul(field.mul(field.power(x, e + 1), field.power(y, e)),
                     field.power(z, r * e * (e + 1) // 2))


def witness_for_triple(e, r, triple, field, left=False):
    slices(e, r)
    require(len(triple) == 3, 'determinant triple dimension mismatch')
    require(all(type(x) is int and 0 < x < field.q for x in triple),
            'determinants must be nonzero field elements')
    require(character(e, r, triple, field, left) == 1, 'character excludes triple')
    x, y, z = triple
    if left:
        x, y = y, x
    u = field.mul(field.inv(field.mul(x, y)), field.power(z, -r * e))
    d = identity(r)
    d[0][0] = u
    p, q, action = lift(e, r, [[z, 0], [0, 1]], d, field)
    return (q, p, action) if left else (p, q, action)
