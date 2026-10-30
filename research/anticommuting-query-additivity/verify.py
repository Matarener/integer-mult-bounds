#!/usr/bin/env python3
"""Exact finite corroboration of the two-type theorem. Nick Petalas, Apache-2.0."""
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


class VerificationError(Exception):
    """A mathematical comparison or bounded input contract failed."""


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def zero(rows, cols):
    return [[0] * cols for _ in range(rows)]


def mm(left, right, p):
    rows, inner, cols = len(left), len(right), len(right[0])
    require(all(len(row) == inner for row in left), "matrix dimensions")
    return [[sum(left[i][k] * right[k][j] for k in range(inner)) % p
             for j in range(cols)] for i in range(rows)]


def rref(matrix, p):
    work = [row[:] for row in matrix]
    rows, cols, pivots = len(work), len(work[0]), []
    for col in range(cols):
        candidates = [i for i in range(len(pivots), rows) if work[i][col] % p]
        if not candidates:
            continue
        row, found = len(pivots), candidates[0]
        work[row], work[found] = work[found], work[row]
        inv = pow(work[row][col], -1, p)
        work[row] = [(v * inv) % p for v in work[row]]
        for i in range(rows):
            if i != row:
                scale = work[i][col]
                work[i] = [(a - scale * b) % p
                           for a, b in zip(work[i], work[row], strict=True)]
        pivots.append(col)
    return work, pivots


def rank(matrix, p):
    return len(rref(matrix, p)[1])


def factor(matrix, middle, p):
    reduced, pivots = rref(matrix, p)
    require(len(pivots) <= middle, "insufficient factor capacity")
    left, right = zero(len(matrix), middle), zero(middle, len(matrix[0]))
    for j, col in enumerate(pivots):
        for i in range(len(matrix)):
            left[i][j] = matrix[i][col]
        right[j] = reduced[j][:]
    if middle:
        require(mm(left, right, p) == matrix, "rank factorization")
    else:
        require(not any(any(row) for row in matrix), "zero rank matrix")
    return left, right


def block(matrix, row, col, d):
    return [line[col*d:(col+1)*d] for line in matrix[row*d:(row+1)*d]]


def tariff(matrices, dimensions, p):
    return max((rank(a, p) + d - 1) // d
               for a, d in zip(matrices, dimensions, strict=True))


def validate_case(p, dimensions, n, m, a0, b, c):
    require(p in (3, 5, 7), "unsupported finite control field")
    require(1 <= len(dimensions) <= 2, "component capacity")
    require(all(d in (1, 2) for d in dimensions), "block capacity")
    require(1 <= n <= 3 and 1 <= m <= 3, "role capacity")
    for matrices in (a0, b, c):
        require(len(matrices) == len(dimensions), "component mismatch")
        for a, d in zip(matrices, dimensions, strict=True):
            require(len(a) == m*d and all(len(row) == n*d for row in a),
                    "response dimensions")
            require(all(type(v) is int and 0 <= v < p for row in a for v in row),
                    "noncanonical coefficient")


def emit(p, dimensions, n, m, a0, b, c):
    validate_case(p, dimensions, n, m, a0, b, c)
    scratch, word = n+m+1, []
    for i in range(m):
        for a in range(n):
            coeff = [block(v, i, a, d) for v, d in zip(a0, dimensions, strict=True)]
            word.append(("add", n+i, a, coeff))
    for label, matrices in (("Q", b), ("R", c)):
        count = tariff(matrices, dimensions, p)
        factors = [factor(v, count*d, p)
                   for v, d in zip(matrices, dimensions, strict=True)]
        for j in range(count):
            for a in range(n):
                coeff = [block(v, j, a, d)
                         for (_, v), d in zip(factors, dimensions, strict=True)]
                word.append(("add", scratch, a, coeff))
            word.append((label, scratch, -1, []))
            for i in range(m):
                coeff = [block(l, i, j, d)
                         for (l, _), d in zip(factors, dimensions, strict=True)]
                word.append(("add", n+i, scratch, coeff))
            word.append(("clear", scratch, -1, []))
    require(len(word) <= 57, "word capacity")
    return word


def formal_run(word, component, d, originals, fields, p):
    bank = [[zero(d, originals*d) for _ in range(4)] for _ in range(fields)]
    for slot in range(originals):
        for i in range(d):
            bank[slot][0][i][slot*d+i] = 1
    for op, dest, src, coeff in word:
        if op == "add":
            for t in range(4):
                delta = mm(coeff[component], bank[src][t], p)
                bank[dest][t] = [[(a+b) % p for a, b in zip(x, y, strict=True)]
                                 for x, y in zip(bank[dest][t], delta, strict=True)]
        elif op == "clear":
            bank[dest] = [zero(d, originals*d) for _ in range(4)]
        else:
            require(op in ("Q", "R"), "unknown query")
            order = (1, 0, 3, 2) if op == "Q" else (2, 3, 0, 1)
            signs = (1, 1, 1, 1) if op == "Q" else (1, -1, 1, -1)
            old = bank[dest]
            bank[dest] = [[[(signs[t]*v) % p for v in row] for row in old[order[t]]]
                          for t in range(4)]
    return bank


def kron_query(coeff, label):
    small = {"I": ((1, 0), (0, 1)), "Q": ((0, 1), (1, 0)),
             "R": ((1, 0), (0, -1))}[label]
    return [[coeff[i//2][j//2] * small[i % 2][j % 2]
             for j in range(2*len(coeff[0]))] for i in range(2*len(coeff))]


def literal_run(word, component, d, originals, fields, p):
    size = 2*d
    bank = [zero(size, originals*size) for _ in range(fields)]
    ident = [[int(i == j) for j in range(d)] for i in range(d)]
    for slot in range(originals):
        for i in range(size):
            bank[slot][i][slot*size+i] = 1
    for op, dest, src, coeff in word:
        if op == "clear":
            bank[dest] = zero(size, originals*size)
        elif op == "add":
            delta = mm(kron_query(coeff[component], "I"), bank[src], p)
            bank[dest] = [[(a+b) % p for a, b in zip(x, y, strict=True)]
                          for x, y in zip(bank[dest], delta, strict=True)]
        else:
            bank[dest] = mm(kron_query(ident, op), bank[dest], p)
    return bank


def expected_formal(d, n, m, a0, b, c):
    originals, fields = n+m+1, n+m+2
    bank = [[zero(d, originals*d) for _ in range(4)] for _ in range(fields)]
    for slot in range(originals):
        for i in range(d):
            bank[slot][0][i][slot*d+i] = 1
    for i in range(m):
        for t, matrix in enumerate((a0, b, c)):
            for u in range(d):
                for v in range(n*d):
                    bank[n+i][t][u][v] = matrix[i*d+u][v]
    return bank


def expected_literal(d, n, m, a0, b, c, p):
    size, originals, fields = 2*d, n+m+1, n+m+2
    bank = [zero(size, originals*size) for _ in range(fields)]
    for slot in range(originals):
        for i in range(size):
            bank[slot][i][slot*size+i] = 1
    for i in range(m):
        for a in range(n):
            terms = [kron_query(block(v, i, a, d), label)
                     for v, label in ((a0, "I"), (b, "Q"), (c, "R"))]
            for u in range(size):
                for v in range(size):
                    bank[n+i][u][a*size+v] = sum(t[u][v] for t in terms) % p
    return bank


def endpoints(word, p, dimensions, n, m, a0, b, c):
    for j, d in enumerate(dimensions):
        got = formal_run(word, j, d, n+m+1, n+m+2, p)
        require(got == expected_formal(d, n, m, a0[j], b[j], c[j]), "formal endpoint")
        literal = literal_run(word, j, d, n+m+1, n+m+2, p)
        require(literal == expected_literal(d, n, m, a0[j], b[j], c[j], p),
                "literal arbitrary-input endpoint")


def check_case(p, dimensions, n, m, a0, b, c):
    word = emit(p, dimensions, n, m, a0, b, c)
    require(sum(op == "Q" for op, *_ in word) == tariff(b, dimensions, p), "Q count")
    require(sum(op == "R" for op, *_ in word) == tariff(c, dimensions, p), "R count")
    endpoints(word, p, dimensions, n, m, a0, b, c)
    return len(word), sum((n+m+1)*2*d for d in dimensions)


def scalar_exhaustive():
    matrices = [[list(v[:2]), list(v[2:])] for v in product(range(3), repeat=4)]
    counts = [0, 0, 0]
    for b, c in product(matrices, repeat=2):
        steps, columns = check_case(3, (1,), 2, 2, [zero(2, 2)], [b], [c])
        counts = [counts[0]+1, counts[1]+steps, counts[2]+columns]
    return counts


def block_exhaustive():
    matrices = [[list(v[:2]), list(v[2:])] for v in product(range(3), repeat=4)]
    counts = [0, 0, 0]
    for b, c in product(matrices, repeat=2):
        steps, columns = check_case(3, (2,), 1, 1, [zero(2, 2)], [b], [c])
        counts = [counts[0]+1, counts[1]+steps, counts[2]+columns]
    return counts


def rectangular_cases():
    counts = [0, 0, 0]
    for p, dims, n, m, seed in product((3, 5, 7), ((1, 2), (2,)),
                                      range(1, 4), range(1, 4), range(4)):
        matrices = []
        for family in range(3):
            parts = []
            for component, d in enumerate(dims):
                parts.append([[(i*i+3*i*j+7*j+seed*(i+1)+family*(j+2)
                                +component+family*seed) % p for j in range(n*d)]
                              for i in range(m*d)])
            matrices.append(parts)
        steps, columns = check_case(p, dims, n, m, *matrices)
        counts = [counts[0]+1, counts[1]+steps, counts[2]+columns]
    return counts


def feedback_controls():
    ident = [[1]]
    alphabet = [("add", 0, 1, [ident]), ("add", 1, 0, [ident])]
    alphabet += [(label, slot, -1, []) for label in ("Q", "R") for slot in (0, 1)]
    checked = 0
    for length in range(5):
        for word in product(alphabet, repeat=length):
            bank = formal_run(word, 0, 1, 2, 2, 3)
            for label, t in (("Q", 1), ("R", 2)):
                count = sum(op == label for op, *_ in word)
                for sign in (1, -1):
                    projected = [[(bank[i][t][0][j]+sign*bank[i][3][0][j]) % 3
                                  for j in range(2)] for i in range(2)]
                    require(rank(projected, 3) <= count, "mixed feedback type cut")
            checked += 1
    return checked


def packed_example():
    matrix = zero(4, 4)
    matrix[0][0] = matrix[2][2] = 1
    word = emit(3, (2,), 2, 2, [zero(4, 4)], [matrix], [matrix])
    endpoints(word, 3, (2,), 2, 2, [zero(4, 4)], [matrix], [matrix])
    require(sum(op in ("Q", "R") for op, *_ in word) == 2, "packed example")
    return 1


def rejection_controls():
    dims, a0, b, c = (1, 1), [[[0]], [[0]]], [[[1]], [[0]]], [[[0]], [[1]]]
    word = emit(3, dims, 1, 1, a0, b, c)
    endpoints(word, 3, dims, 1, 1, a0, b, c)
    require(tariff(b, dims, 3)+tariff(c, dims, 3) == 2, "sector conflict total")
    require(max(rank(x, 3)+rank(y, 3) for x, y in zip(b, c, strict=True)) == 1,
            "sector conflict comparison")
    queries = [i for i, step in enumerate(word) if step[0] in ("Q", "R")]
    mutants = [word[:queries[0]]+word[queries[0]+1:]]
    wrong_type = word[:]
    wrong_type[queries[0]] = ("R", word[queries[0]][1], -1, [])
    mutants.append(wrong_type)
    mutants.append(word[:-1])
    mutants.append(word+[("add", 2, 0, [[[1]], [[1]]])])
    for changed in mutants:
        failed = False
        try:
            endpoints(changed, 3, dims, 1, 1, a0, b, c)
        except VerificationError:
            failed = True
        require(failed, "endpoint mutant escaped")
    bad_args = [(2, dims, 1, 1, a0, b, c), (3, (0,), 1, 1, a0, b, c),
                (3, dims, 4, 1, a0, b, c), (3, dims, 1, 1, a0, [], c)]
    for args in bad_args:
        failed = False
        try:
            emit(*args)
        except VerificationError:
            failed = True
        require(failed, "invalid model accepted")
    return len(mutants)+len(bad_args)


def main():
    result = {"scalar_exhaustive": scalar_exhaustive(),
              "matrix_block_exhaustive": block_exhaustive(),
              "rectangular_product_cases": rectangular_cases(),
              "feedback_words": feedback_controls(),
              "packed_example": packed_example(),
              "rejection_controls": rejection_controls()}
    root = Path(__file__).resolve().parent
    hashes = {}
    for name in ("verify.py", "PROOF.md", "README.md", "TASK.json", "SOURCES.json", "VERIFY.json"):
        payload = (root / name).read_bytes()
        require(len(payload) <= 65536, "receipt source capacity")
        hashes[name] = sha256(payload).hexdigest()
    result["source_sha256"] = hashes
    print("PASS_ANTICOMMUTING_QUERY_ADDITIVITY")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
