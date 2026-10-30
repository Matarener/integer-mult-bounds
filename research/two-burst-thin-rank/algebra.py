"""Bounded binary coefficient algebra for the fixed two-burst question."""

from itertools import product

SIZE = 8
MASK = (1 << 64) - 1
IDENTITY = sum(1 << (9 * i) for i in range(SIZE))
EXPONENTS = tuple(product(range(3), repeat=3))
ZERO = (0, 0, 0)
VARIABLES = 128


def require(condition, message):
    if not condition:
        raise ValueError(message)


def pack(rows):
    require(isinstance(rows, list) and len(rows) == SIZE, "matrix row count")
    require(all(type(r) is int and 0 <= r < 256 for r in rows), "binary row")
    return sum(r << (8 * i) for i, r in enumerate(rows))


def multiply(left, right):
    result = 0
    for i in range(SIZE):
        row = 0
        for j in range(SIZE):
            if (left >> (8 * i + j)) & 1:
                row ^= (right >> (8 * j)) & 255
        result |= row << (8 * i)
    return result


def rank(word):
    basis = [0] * SIZE
    result = 0
    for i in range(SIZE):
        row = (word >> (8 * i)) & 255
        for _ in range(SIZE):
            if row == 0:
                break
            pivot = row.bit_length() - 1
            if basis[pivot] == 0:
                basis[pivot] = row
                result += 1
                break
            row ^= basis[pivot]
    return result


def add_polynomials(left, right):
    require(len(left) <= 27 and len(right) <= 27, "polynomial capacity")
    out = dict(left)
    for exponent, value in right.items():
        out[exponent] = out.get(exponent, 0) ^ value
    return {exponent: value for exponent, value in out.items() if value}


def multiply_polynomials(left, right):
    require(len(left) <= 27 and len(right) <= 27, "polynomial capacity")
    out = {}
    for x, a in left.items():
        for y, b in right.items():
            exponent = tuple(x[i] + y[i] for i in range(3))
            require(all(v <= 2 for v in exponent), "coefficient degree")
            out[exponent] = out.get(exponent, 0) ^ multiply(a, b)
    return {exponent: value for exponent, value in out.items() if value}


def encode(polynomial):
    require(set(polynomial) <= set(EXPONENTS), "coefficient domain")
    return sum(polynomial.get(e, 0) << (64 * i) for i, e in enumerate(EXPONENTS))


def full_gate(call):
    stage = call["stage"]
    require(type(stage) is int and 0 <= stage < 3, "full stage")
    p, r = pack(call["p"]), pack(call["r"])
    exponent = tuple(int(i == stage) for i in range(3))
    return {ZERO: IDENTITY, exponent: p}, {ZERO: r, exponent: r}


def full_product(calls, order):
    base, error = {ZERO: IDENTITY}, {}
    for index in order:
        a, b = full_gate(calls[index])
        error = add_polynomials(multiply_polynomials(a, error),
                                multiply_polynomials(b, base))
        base = multiply_polynomials(a, base)
    return base, error


def build_system(calls, order, gaps):
    require(len(calls) == 6, "six full calls")
    require(order == [1, 3, 2, 4, 0, 5], "fixed full order")
    require(gaps == [2, 4], "fixed occupied gaps")
    base, error = full_product(calls, order)
    wanted = {ZERO: IDENTITY}
    for stage in range(3):
        p = pack(calls[2 * stage]["p"]) ^ pack(calls[2 * stage + 1]["p"])
        exponent = tuple(int(i == stage) for i in range(3))
        wanted = multiply_polynomials({ZERO: IDENTITY, exponent: p}, wanted)
    require(base == wanted, "pure stage endpoint")
    columns = []
    for gap in gaps:
        prefix, _ = full_product(calls, order[:gap])
        suffix, _ = full_product(calls, order[gap:])
        for j in range(64):
            column = multiply_polynomials(suffix, multiply_polynomials(
                {ZERO: 1 << j}, prefix))
            columns.append(encode(column))
    return columns, encode(add_polynomials(wanted, error))


def linear_image(columns, vector):
    require(len(columns) == VARIABLES and 0 <= vector < (1 << VARIABLES),
            "linear image domain")
    result = 0
    for j in range(VARIABLES):
        if (vector >> j) & 1:
            result ^= columns[j]
    return result


def affine_space(columns, target):
    require(len(columns) == VARIABLES, "system width")
    require(all(0 <= c < (1 << 1728) for c in columns), "system column")
    require(0 <= target < (1 << 1728), "system target")
    basis = [0] * VARIABLES
    for i in range(1728):
        row = sum(((c >> i) & 1) << j for j, c in enumerate(columns))
        row |= ((target >> i) & 1) << VARIABLES
        for j in range(VARIABLES):
            if (row >> j) & 1:
                if basis[j]:
                    row ^= basis[j]
                else:
                    basis[j] = row
                    break
        else:
            require(row == 0, "inconsistent coefficient system")
    for j in range(VARIABLES - 1, -1, -1):
        if basis[j]:
            for k in range(j):
                if (basis[k] >> j) & 1:
                    basis[k] ^= basis[j]
    free = [j for j, row in enumerate(basis) if row == 0]
    particular = sum(((row >> VARIABLES) & 1) << j for j, row in enumerate(basis))
    null = [(1 << f) | sum(((row >> f) & 1) << j
                           for j, row in enumerate(basis)) for f in free]
    require(linear_image(columns, particular) == target, "particular solution")
    for vector in null:
        require(linear_image(columns, vector) == 0, "homogeneous solution")
    return particular, null, free
