#!/usr/bin/env python3
"""Exact two-write projection and projector constraints; no long-word census."""
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
I = 9  # Row-major 2x2 binary identity.


def require(ok, message):
    if not ok:
        raise ValueError(message)


def smul(a, b):
    out = 0
    for r in range(2):
        for c in range(2):
            bit = ((a >> (2*r) & 1) & (b >> c & 1)) ^ ((a >> (2*r+1) & 1) & (b >> (2+c) & 1))
            out |= bit << (2*r+c)
    return out


def identity(n):
    return tuple(1 << i for i in range(n))


def label(n, d, s):
    rows = list(identity(n))
    rows[d] ^= 1 << s
    return tuple(rows)


def gmul(a, b):
    return tuple(xor(b[j] for j in range(len(b)) if row >> j & 1) for row in a)


def xor(values):
    out = 0
    for value in values:
        out ^= value
    return out


def put(poly, group, coefficient):
    value = poly.get(group, 0) ^ coefficient
    if value:
        poly[group] = value
    else:
        poly.pop(group, None)


def multiply(a, b):
    out = {}
    for g, x in a.items():
        for h, y in b.items():
            put(out, gmul(g, h), smul(x, y))
    return out


def word_poly(word, n):
    e = identity(n)
    out = {e: I}
    for d, s, projector in word:
        out = multiply(out, {e: I ^ projector, label(n, d, s): projector})
    return out


def sandwich(poly, a, b):
    out = {}
    for group, coefficient in poly.items():
        put(out, group, smul(smul(a, coefficient), b))
    return out


def projected(poly, k):
    return {g: value for g, value in poly.items() if g[k] == 1 << k}


def two_write_formula(middle, n, k, j, l, N, M, relabel=True, select=True):
    B = word_poly(middle, n)
    g, h = label(n, k, j), label(n, k, l)
    out = sandwich(B, I ^ N, I ^ M)
    for b, value in B.items():
        if not select or b[j] == 1 << l:
            put(out, gmul(gmul(g, b), h) if relabel else b, smul(smul(N, value), M))
    return out


def augment(poly):
    return xor(poly.values())


def projectors():
    return [a for a in range(1, 16) if a != I and smul(a, a) == a and
            ((a & 1) * (a >> 3 & 1) ^ (a >> 1 & 1) * (a >> 2 & 1)) == 0]


def source_check():
    pins = json.loads((PACKAGE / 'SOURCES.json').read_text())
    for pin in pins['files']:
        if pin.get('usage') == 'input':
            require(sha256((ROOT / pin['path']).read_bytes()).hexdigest() == pin['sha256'], 'source mismatch')


def classify(Ns):
    restored, moved = set(), set()
    for N, M, S in product(Ns, Ns, range(16)):
        F = smul(I ^ N, I ^ M) ^ smul(smul(N, S), M)
        if F == I:
            restored.add((N, M))
            require(N == M and smul(smul(N, S), N) == N, 'restored classification')
        if F == 0:
            moved.add((N, M))
            require(smul(I ^ N, I ^ M) == 0, 'forward moved condition')
    both = {(N, M) for N, M in moved if (M, N) in moved}
    require(len(restored) == 6 and len(moved) == 12 and len(both) == 6, 'pair inventory')
    require(all(M == I ^ N for N, M in both), 'inverse moved condition')
    return moved


def check_formula(Ns):
    n, k = 3, 2
    middles = [()] + [((d, s, N),) for d in (0, 1) for s in range(3) if d != s for N in Ns]
    cases = 0
    for middle, j, l, N, M in product(middles, (0, 1), (0, 1), Ns, Ns):
        word = ((k, j, N),) + middle + ((k, l, M),)
        actual = projected(word_poly(word, n), k)
        expected = two_write_formula(middle, n, k, j, l, N, M)
        require(actual == expected, 'two-write projection')
        cases += 1
    require(cases == 3600, 'formula coverage')
    return cases


def commutator(N):
    # i=0,j=1,k=2; products act on column vectors from right to left.
    return ((2, 1, N), (0, 2, N), (2, 1, N), (0, 2, N), (0, 1, N))


def controls(Ns, moved):
    require(any(M != I ^ N for N, M in moved), 'forward-only strengthening control')
    for N in Ns:
        word = commutator(N)
        require(word_poly(word, 3) == {identity(3): I}, 'commutator identity')
        require(sum(d == 2 for d, s, _ in word) == sum(s == 2 for d, s, _ in word) == 2, 'live spectator')
        middle = (word[1],)
        good = two_write_formula(middle, 3, 2, 1, 1, N, N)
        require(good != two_write_formula(middle, 3, 2, 1, 1, N, N, relabel=False), 'relabel mutation')
        require(all(word_poly(word[:i]+word[i+1:], 3) != {identity(3): I} for i in range(5)), 'omission mutation')
    require(any(two_write_formula((), 3, 2, 0, 1, N, M) !=
                two_write_formula((), 3, 2, 0, 1, N, M, select=False)
                for N, M in product(Ns, repeat=2)), 'selection mutation')


def main():
    source_check()
    Ns = projectors()
    require(len(Ns) == 6, 'six projectors')
    moved = classify(Ns)
    count = check_formula(Ns)
    controls(Ns, moved)
    print('PASS_TWO_WRITE_PROJECTION cases=' + str(count) + ' restored_pairs=6 forward_pairs=12 inverse_pairs=6 commutators=6 no_length10_exclusion')


if __name__ == '__main__':
    main()
