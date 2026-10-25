"""Exact free operators N^2=-I and arbitrary invertible noncommuting P_j.

Apache-2.0; substantial OpenAI Codex assistance. Derived from this lane's
frozen coded caller verifier; no native admission is inferred here.
"""
from fractions import Fraction


def need(x, why):
    if not x:
        raise ValueError(why)


def reduce_word(w):
    a, sign = [], 1
    for x in w:
        if a and x == a[-1] == 0:
            a.pop()
            sign = -sign
        elif a and x != 0 and x == -a[-1]:
            a.pop()
        else:
            a.append(x)
    return tuple(a), sign


def mono(w=(), c=1):
    w, sign = reduce_word(w)
    return {w: Fraction(c) * sign} if c else {}


Z, I, N = {}, mono(), mono((0,))


def add(a, b):
    c = dict(a)
    for w, v in b.items():
        c[w] = c.get(w, 0) + v
        if not c[w]:
            del c[w]
    return c


def neg(a):
    return {w: -v for w, v in a.items()}


def mul(a, b):
    c = {}
    for w, x in a.items():
        for v, y in b.items():
            c = add(c, mono(w + v, x * y))
    return c


def prod(*args):
    a = I
    for b in args:
        a = mul(a, b)
    return a


def inv(a):
    need(len(a) == 1, 'invert one literal word')
    (w, c), = a.items()
    b = mono((), 1 / c)
    for x in reversed(w):
        b = mul(b, neg(N) if x == 0 else mono((-x,)))
    need(mul(a, b) == mul(b, a) == I, 'literal phase inverse')
    return b


def summ(args):
    a = Z
    for b in args:
        a = add(a, b)
    return a


def eye(n):
    return [[I if i == j else Z for j in range(n)] for i in range(n)]


def mm(a, b):
    return [[summ(mul(x, y) for x, y in zip(r, c)) for c in zip(*b)] for r in a]


def es(n, dst, src, coefficient):
    a = eye(n)
    a[dst][src] = add(a[dst][src], coefficient)
    return a


def unary(n, b, coefficient):
    a = eye(n)
    a[b][b] = coefficient
    return a


def serial(a):
    return [{'coefficient': str(c),
             'word': ['N' if x == 0 else 'P' + str(abs(x)) + ('^-1' if x < 0 else '') for x in w]}
            for w, c in sorted(a.items())]


def sm(a):
    return [[serial(x) for x in r] for r in a]

