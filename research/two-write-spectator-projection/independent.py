"""Independent full-permutation group labels and dense scalar arithmetic."""
import importlib.util
import json
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('two_write_primary', HERE / 'verify.py')
primary = importlib.util.module_from_spec(spec)
spec.loader.exec_module(primary)
ONE = (1, 0, 0, 1)
ZERO = (0, 0, 0, 0)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def dense_product(a, b):
    return tuple(sum(a[2*i+k] * b[2*k+j] for k in range(2)) % 2
                 for i in range(2) for j in range(2))


def bit_tuple(value):
    return tuple((value >> bit) & 1 for bit in range(4))


def permutation(n, d, s):
    return tuple(x ^ (((x >> s) & 1) << d) for x in range(1 << n))


def compose(a, b):
    return tuple(a[x] for x in b)


def toggled(out, label, value):
    prior = out.get(label, ZERO)
    value = tuple(a ^ b for a, b in zip(prior, value))
    if value == ZERO:
        out.pop(label, None)
    else:
        out[label] = value


def oracle(word, n):
    current = {tuple(range(1 << n)): ONE}
    for d, s, encoded in word:
        N = bit_tuple(encoded)
        complement = tuple(a ^ b for a, b in zip(ONE, N))
        g = permutation(n, d, s)
        nxt = {}
        for p, value in current.items():
            toggled(nxt, p, dense_product(value, complement))
            toggled(nxt, compose(p, g), dense_product(value, N))
        current = nxt
    return current


def row_is(p, row, expected):
    return all(((p[x] >> row) & 1) == ((x >> expected) & 1) for x in range(len(p)))


def convert(poly):
    out = {}
    for rows, value in poly.items():
        p = tuple(sum(((r & x).bit_count() % 2) << i for i, r in enumerate(rows))
                  for x in range(1 << len(rows)))
        out[p] = bit_tuple(value)
    return out


def group_filter():
    cases = 0
    for rows in product(range(8), repeat=3):
        b = tuple(sum(((r & x).bit_count() % 2) << i for i, r in enumerate(rows)) for x in range(8))
        if len(set(b)) != 8:
            continue
        for k in range(3):
            if not row_is(b, k, k):
                continue
            for j, l in product([i for i in range(3) if i != k], repeat=2):
                gbh = compose(compose(permutation(3, k, j), b), permutation(3, k, l))
                need(row_is(gbh, k, k) == row_is(b, j, l), 'independent return filter')
                cases += 1
    need(cases == 288, 'complete GL3 filter inventory')
    return cases


def outer_contexts(Ns):
    n, k = 5, 4
    letters = [(d, s) for d in range(4) for s in range(5) if d != s]
    for index in range(72):
        N, M = Ns[(index // 6) % 6], Ns[index % 6]
        j, l = index % 4, (index // 4) % 4
        A = (letters[index % 16] + (Ns[(index + 1) % 6],),)
        C = (letters[(index + 7) % 16] + (Ns[(index + 3) % 6],),)
        B = tuple(letters[(index + 3*t) % 16] + (Ns[(index + t) % 6],) for t in range(2 + index % 2))
        word = A + ((k, j, N),) + B + ((k, l, M),) + C
        actual = oracle(word, n)
        need(actual == convert(primary.word_poly(word, n)), 'independent full formal coefficients')
        actual = {p: value for p, value in actual.items() if row_is(p, k, k)}
        center = primary.two_write_formula(B, n, k, j, l, N, M)
        expected = primary.multiply(primary.multiply(primary.word_poly(A, n), center), primary.word_poly(C, n))
        need(actual == convert(expected), 'projection with arbitrary outer contexts')
    return 72


def positive_endpoints(Ns):
    n = 5
    swaps = ((0, 1), (1, 0), (0, 1), (1, 2), (2, 1), (1, 2))
    word12 = tuple((d, s, N) for N in (1, 8) for d, s in swaps)
    c = tuple(range(1 << n))
    for d, s in swaps:
        c = compose(c, permutation(n, d, s))
    expected = {c: ONE}
    need(oracle(word12, n) == expected, 'twelve-call endpoint')
    for N in Ns:
        loop = ((3, 1, N), (0, 3, N), (3, 1, N), (0, 3, N), (0, 1, N))
        need(oracle(loop, n) == {tuple(range(1 << n)): ONE}, 'independent commutator')
        word17 = loop + word12
        need(oracle(word17, n) == expected, 'seventeen-call endpoint')
        need(sum(d == 3 for d, s, _ in word17) == sum(s == 3 for d, s, _ in word17) == 2,
             'seventeen-call live spectator')
    return 6


def main():
    primary.source_check()
    Ns = primary.projectors()
    counts = {'return_filter': group_filter(), 'outer_contexts': outer_contexts(Ns),
              'seventeen_call_endpoints': positive_endpoints(Ns)}
    print('PASS_TWO_WRITE_INDEPENDENT ' + json.dumps(counts, sort_keys=True))


if __name__ == '__main__':
    main()
