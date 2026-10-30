"""Exact all-chunk operator algebra for the minimal plane carrier.

N_i^2=-I, N_i commute, and plane ADDRESS permutations permute the N_i.
All operations are literal Gaussian-unit identities, not binary tableaux.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from fractions import Fraction


def need(condition, message):
    if not condition:
        raise ValueError(message)


class Algebra:
    def __init__(self, planes):
        self.p = planes
        self.idperm = tuple(range(planes))
        self.I = {(0, self.idperm): Fraction(1)}
        self.Z = {}

    def mono(self, bits=0, perm=None, coefficient=1):
        if not coefficient:
            return {}
        return {(bits, self.idperm if perm is None else tuple(perm)): Fraction(coefficient)}

    def n(self, i):
        return self.mono(1 << i)

    def swap(self, i, j):
        p = list(self.idperm)
        p[i], p[j] = p[j], p[i]
        return self.mono(perm=p)

    def add(self, a, b):
        c = dict(a)
        for g, v in b.items():
            c[g] = c.get(g, 0) + v
            if not c[g]:
                del c[g]
        return c

    @staticmethod
    def neg(a):
        return {g: -v for g, v in a.items()}

    def mul(self, a, b):
        c = {}
        for (x, p), v in a.items():
            for (y, q), w in b.items():
                py = sum(1 << p[i] for i in range(self.p) if y >> i & 1)
                sign = -1 if (x & py).bit_count() % 2 else 1
                r = tuple(p[q[i]] for i in range(self.p))
                c = self.add(c, self.mono(x ^ py, r, sign * v * w))
        return c

    def prod(self, *args):
        c = self.I
        for a in args:
            c = self.mul(c, a)
        return c

    def inv(self, a):
        need(len(a) == 1, 'literal inverse requires one group word')
        ((x, p), v), = a.items()
        pi = [0] * self.p
        for i, j in enumerate(p):
            pi[j] = i
        y = sum(1 << pi[i] for i in range(self.p) if x >> i & 1)
        sign = -1 if x.bit_count() % 2 else 1
        b = self.mono(y, pi, sign / v)
        need(self.mul(a, b) == self.mul(b, a) == self.I, 'exact phase inverse')
        return b

    def ad(self, a, b):
        return self.prod(a, b, self.inv(a))

    def native_arity(self, a):
        need(len(a) == 1, 'native arity only for a single actual operator')
        ((bits, _), _), = a.items()
        return 2 * bits.bit_count()

    def eye(self, n):
        return [[self.I if i == j else self.Z for j in range(n)] for i in range(n)]

    def mm(self, a, b):
        return [[self.sum(self.mul(x, y) for x, y in zip(r, c)) for c in zip(*b)] for r in a]

    def sum(self, terms):
        a = self.Z
        for b in terms:
            a = self.add(a, b)
        return a

    def es(self, n, dst, src, a):
        m = self.eye(n)
        m[dst][src] = self.add(m[dst][src], a)
        return m

    def serial(self, a):
        return [{'coefficient': str(c), 'N_planes': [i for i in range(self.p) if x >> i & 1],
                 'ADDRESS_plane_permutation': list(p)} for (x, p), c in sorted(a.items())]

