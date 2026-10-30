"""New tensor-capacity checks; no predecessor executable is imported."""

from fractions import Fraction
from hashlib import sha256
from itertools import combinations, permutations, product
import json
from math import gcd, prod
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def matrix(rows):
    require(isinstance(rows, (list, tuple)) and 1 <= len(rows) <= 32, "rows")
    require(all(isinstance(row, (list, tuple)) for row in rows), "row type")
    width = len(rows[0])
    require(1 <= width <= 32 and all(len(row) == width for row in rows), "shape")
    require(all(type(x) is int or isinstance(x, Fraction) for row in rows for x in row), "scalar")
    out = tuple(tuple(Fraction(x) for x in row) for row in rows)
    require(all(x.denominator & (x.denominator - 1) == 0 for row in out for x in row), "nondyadic")
    require(all(max(abs(x.numerator).bit_length(), x.denominator.bit_length()) <= 256
                for row in out for x in row), "scalar capacity")
    return out


def multiply(a, b):
    require(len(a[0]) == len(b), "product shape")
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(len(b)))
                       for j in range(len(b[0]))) for i in range(len(a)))


def identity(n):
    return tuple(tuple(Fraction(i == j) for j in range(n)) for i in range(n))


def tensor(a, b):
    require(len(a) * len(b) <= 32 and len(a[0]) * len(b[0]) <= 32, "tensor capacity")
    return tuple(tuple(x * y for x in row_a for y in row_b)
                 for row_a in a for row_b in b)


def determinant(a):
    n = len(a)
    require(n <= 4 and all(len(row) == n for row in a), "minor capacity")
    total = Fraction(0)
    for p in permutations(range(n)):
        inversions = sum(p[i] > p[j] for i in range(n) for j in range(i + 1, n))
        total += (-1) ** inversions * prod(a[i][p[i]] for i in range(n))
    return total


def minor_capacity(a):
    """Independent determinantal-ideal oracle, at most four by four."""
    require(max(len(a), len(a[0])) <= 4, "minor oracle capacity")
    capacity = 0
    for k in range(1, min(len(a), len(a[0])) + 1):
        divisor = 0
        for rows in combinations(range(len(a)), k):
            for columns in combinations(range(len(a[0])), k):
                minor = tuple(tuple(a[i][j] for j in columns) for i in rows)
                divisor = gcd(divisor, determinant(minor).numerator)
        if divisor and divisor & (divisor - 1) == 0:
            capacity = k
    return capacity


def rank(a, prime=0):
    """Elimination over Q or a specified prime field, independent of minors."""
    require(prime == 0 or prime in (3, 5, 7, 11), "prime")
    rows = [list(row) for row in a]
    if prime:
        rows = [[x.numerator * pow(x.denominator, -1, prime) % prime for x in row]
                for row in rows]
    pivot_row = 0
    for column in range(len(rows[0])):
        pivot = next((i for i in range(pivot_row, len(rows)) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        value = rows[pivot_row][column]
        scale = pow(value, -1, prime) if prime else 1 / value
        rows[pivot_row] = [x * scale % prime if prime else x * scale
                           for x in rows[pivot_row]]
        for i in range(pivot_row + 1, len(rows)):
            scale = rows[i][column]
            rows[i] = [(x - scale * y) % prime if prime else x - scale * y
                       for x, y in zip(rows[i], rows[pivot_row])]
        pivot_row += 1
        if pivot_row == len(rows):
            break
    return pivot_row


def bezout(a, b):
    require(0 <= a < 2**256 and 0 <= b < 2**256 and a + b > 0, "gcd input")
    old_r, r, old_s, s, old_t, t = a, b, 1, 0, 0, 1
    for _ in range(1024):
        if r == 0:
            require(old_s * a + old_t * b == old_r, "Bezout identity")
            return old_r, old_s, old_t
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t
    raise ValueError("Euclidean iteration capacity")


def diagonal_witness(values):
    """Construct X diag(values) Y = I_c by integral two-pivot Smith steps."""
    require(1 <= len(values) <= 32, "diagonal capacity")
    require(all(type(x) is int and 0 <= x < 2**64 for x in values), "diagonal value")
    n = len(values)
    diagonal = list(values)
    left, right = [list(row) for row in identity(n)], [list(row) for row in identity(n)]
    for i in range(n):
        for j in range(i + 1, n):
            a, b = diagonal[i], diagonal[j]
            if b == 0 or (a and b % a == 0):
                continue
            g, s, t = bezout(a, b)
            first, second = left[i][:], left[j][:]
            left[i] = [s * x + t * y for x, y in zip(first, second)]
            left[j] = [-(b // g) * x + (a // g) * y for x, y in zip(first, second)]
            for row in right:
                x, y = row[i], row[j]
                row[i], row[j] = x + y, -(t * b // g) * x + (s * a // g) * y
            diagonal[i], diagonal[j] = g, a * b // g
    positions = [i for i, x in enumerate(diagonal) if x and x & (x - 1) == 0]
    x = tuple(tuple(value / diagonal[i] for value in left[i]) for i in positions)
    y = tuple(tuple(row[i] for i in positions) for row in right)
    return x, y, tuple(diagonal)


def diagonal_matrix(values):
    return tuple(tuple(Fraction(values[i] if i == j else 0)
                       for j in range(len(values))) for i in range(len(values)))


def pair_census():
    lefts = [matrix((v[:2], v[2:])) for v in product((0, 1, 3), repeat=4)]
    rights = [matrix((v[:2], v[2:])) for v in product((0, 1, 5), repeat=4)]
    profiles = {}
    for a in lefts + rights:
        profiles[a] = (rank(a), *(rank(a, p) for p in (3, 5)))
        require(minor_capacity(a) == min(profiles[a]), "factor oracle disagreement")
    count = strict = 0
    for a in lefts:
        for b in rights:
            actual = minor_capacity(tensor(a, b))
            predicted = min(x * y for x, y in zip(profiles[a], profiles[b]))
            ca, cb = min(profiles[a]), min(profiles[b])
            upper = min(ca * profiles[b][0], cb * profiles[a][0])
            require(ca * cb <= actual == predicted <= upper, "tensor capacity law")
            if ca * cb:
                common = any(x == ca and y == cb for x, y in zip(profiles[a], profiles[b]))
                require((actual == ca * cb) == common, "common-prime equality law")
            count += 1
            strict += actual > ca * cb
    return {"ordered_matrix_pairs": count, "strict_compositions": strict,
            "factor_checks": len(lefts) + len(rights)}


def extremal_census():
    count = witnesses = entries = 0
    for factors in range(1, 4):
        for ranks in product((1, 2, 3), repeat=factors):
            if prod(ranks) > 12:
                continue
            for capacities in product(*(range(1, r + 1) for r in ranks)):
                low = prod(capacities)
                high = min(capacities[i] * prod(ranks[j] for j in range(factors) if j != i)
                           for i in range(factors))
                for distinct, expected in ((False, low), (True, high)):
                    diagonals = [([1] * c + [(3, 5, 7)[i] if distinct else 3] * (r - c))
                                 for i, (r, c) in enumerate(zip(ranks, capacities))]
                    values = [prod(v) for v in product(*diagonals)]
                    a = diagonal_matrix(values)
                    actual = min(rank(a, p) for p in (3, 5, 7, 11))
                    require(actual == expected, "sharp envelope")
                    x, y, smith = diagonal_witness(values)
                    require(len(x) == expected, "unit block size")
                    require(multiply(multiply(x, a), y) == identity(expected), "unit block endpoint")
                    require(all(smith[i + 1] % smith[i] == 0 for i in range(len(smith) - 1)),
                            "Smith divisibility")
                    witnesses += 1
                    entries += expected * expected
                count += 1
    return {"rank_capacity_tuples": count, "attaining_unit_blocks": witnesses,
            "unit_block_entries": entries}


def rectangular_and_oblique():
    count = 0
    for height, width in ((1, 2), (2, 1), (1, 3), (3, 1)):
        for values in product((0, 3, 5), repeat=height * width):
            a = matrix(tuple(values[i * width:(i + 1) * width] for i in range(height)))
            b = matrix(((1, 0), (0, 5))) if max(height, width) == 2 else matrix(((3,),))
            actual = minor_capacity(tensor(a, b))
            require(actual == min(rank(a, p) * rank(b, p) for p in (3, 5, 7)), "rectangular")
            count += 1
    for i in range(-3, 4):
        for j in range(-3, 4):
            a = multiply(matrix(((1, i), (0, 1))), matrix(((1, 0), (0, 3))))
            a = multiply(a, matrix(((1, 0), (j, 1))))
            b = matrix(((Fraction(1, 2), 0), (0, 5)))
            require(minor_capacity(a) == minor_capacity(b) == 1, "oblique factors")
            require(minor_capacity(tensor(a, b)) == 2, "oblique dyadic activation")
            count += 1
    return {"rectangular_oblique_cases": count}


def controls():
    count = 0
    for bad in ([], [[], []], [[1], [1, 2]], [[Fraction(1, 3)]], [["1"]], [[2**257]]):
        try:
            matrix(bad)
        except ValueError:
            count += 1
        else:
            raise ValueError("invalid matrix accepted")
    for values in ((0, 3), (0, 0), (2, 0), (3, 5), (3, 3)):
        a = diagonal_matrix(values)
        x, y, _ = diagonal_witness(values)
        expected = minor_capacity(a)
        require(len(x) == expected, "zero/unit boundary")
        if expected:
            require(multiply(multiply(x, a), y) == identity(expected), "boundary witness")
        count += 1
    a, b = diagonal_matrix((1, 3)), diagonal_matrix((1, 5))
    displayed_x = matrix(((1, 0, 0, 0), (0, -1, 2, 0)))
    displayed_y = matrix(((1, 0), (0, 1), (0, 1), (0, 0)))
    require(multiply(multiply(displayed_x, tensor(a, b)), displayed_y) == identity(2),
            "displayed witness")
    require(minor_capacity(tensor(a, b)) != minor_capacity(a) * minor_capacity(b),
            "product-only mutant escaped")
    require(minor_capacity(tensor(a, a)) != 2, "separate-minimizers mutant escaped")
    require(minor_capacity(diagonal_matrix((0, 3))) == 0, "rational-rank mutant escaped")
    x, y, _ = diagonal_witness((1, 5, 3, 15))
    broken = tuple(tuple(0 for _ in row) for row in x)
    require(multiply(multiply(broken, tensor(a, b)), y) != identity(2), "witness mutant escaped")
    return {"boundary_rejection_mutation_controls": count + 5}


def main():
    results = pair_census() | extremal_census() | rectangular_and_oblique() | controls()
    package = Path(__file__).resolve().parent
    names = ("verify.py", "README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json")
    results["source_sha256"] = {name: sha256((package / name).read_bytes()).hexdigest() for name in names}
    results["status"] = "PASS_TENSOR_HELPER_CAPACITY"
    print(json.dumps(results, sort_keys=True))


if __name__ == "__main__":
    main()
