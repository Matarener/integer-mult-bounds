"""Separate row-oriented GF(2) and mathematical routing oracle. Apache-2.0."""
from itertools import product


def rows(columns):
    n = len(columns)
    return [[(columns[j] >> i) & 1 for j in range(n)] for i in range(n)]


def cols(a):
    return [sum(a[i][j] << i for i in range(len(a))) for j in range(len(a))]


def product_matrix(a, b):
    n = len(a)
    return [[sum(a[i][k] * b[k][j] for k in range(n)) % 2
             for j in range(n)] for i in range(n)]


def vector(a, v):
    return sum((sum(a[i][j] * ((v >> j) & 1) for j in range(len(a))) % 2) << i
               for i in range(len(a)))


def inverse_rows(a):
    n = len(a)
    out = [row[:] + [int(i == j) for j in range(n)] for i, row in enumerate(a)]
    for j in range(n):
        pivot = next(i for i in range(j, n) if out[i][j])
        out[j], out[pivot] = out[pivot], out[j]
        for i in range(n):
            if i != j and out[i][j]:
                out[i] = [x ^ y for x, y in zip(out[i], out[j])]
    return [row[n:] for row in out]


def all_invertible(n):
    for flat in product((0, 1), repeat=n*n):
        a = [list(flat[i*n:(i+1)*n]) for i in range(n)]
        try:
            inverse_rows(a)
        except StopIteration:
            continue
        yield cols(a)


def push(g, delta, owner, payload):
    h = inverse_rows(rows(g))
    destination = product_matrix(rows(owner), h)
    translation = vector(destination, delta)
    return cols(destination), [z ^ translation for z in payload]


def pull(g, delta, owner, payload):
    old = product_matrix(rows(owner), rows(g))
    translation = vector(rows(owner), delta)
    return cols(old), [z ^ translation for z in payload]


def key(owner, payload, n):
    return ''.join(str(owner[j] >> i & 1) for j in range(n) for i in range(n)) +            ''.join(str(z >> i & 1) for z in payload for i in range(n))
