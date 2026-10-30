#!/usr/bin/env python3
"""Exact small Clifford/residual counts and rational tails; standard library only.

kumagi, with substantial OpenAI Codex assistance. Apache-2.0.
The all-dimension argument is in PROOF.md, not established by enumeration.
"""
from collections import Counter, defaultdict, deque
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path


def require(ok, message):
    if not ok:
        raise ValueError(message)


def expect_failure(action, message):
    try:
        action()
    except ValueError:
        return
    raise ValueError("negative control accepted: " + message)


def apply(columns, vector):
    result = 0
    for j, column in enumerate(columns):
        if vector >> j & 1:
            result ^= column
    return result


def reduced(vectors):
    pivots = {}
    for v in vectors:
        while v:
            p = v.bit_length() - 1
            if p in pivots:
                v ^= pivots[p]
            else:
                pivots[p] = v
                break
    for p in sorted(pivots):
        for q in pivots:
            if q != p and pivots[q] >> p & 1:
                pivots[q] ^= pivots[p]
    return tuple(pivots[p] for p in sorted(pivots))


def transpose(columns):
    return tuple(sum(((columns[j] >> i) & 1) << j
                     for j in range(len(columns)))
                 for i in range(len(columns)))


def inverse(columns):
    k = len(columns)
    rows = [r | (1 << (k + i)) for i, r in enumerate(transpose(columns))]
    for i in range(k):
        pivot = next((j for j in range(i, k) if rows[j] >> i & 1), None)
        require(pivot is not None, "singular residual form")
        rows[i], rows[pivot] = rows[pivot], rows[i]
        for j in range(k):
            if i != j and rows[j] >> i & 1:
                rows[j] ^= rows[i]
    return transpose(tuple(r >> k for r in rows))


def omega(u, v, n):
    mask = (1 << n) - 1
    return (((u & mask) & (v >> n)).bit_count()
            + ((v & mask) & (u >> n)).bit_count()) & 1


def generators(n):
    width = 2 * n
    result = []
    for kind, a, b in ([('H', j, None) for j in range(n)]
                       + [('S', j, None) for j in range(n)]
                       + [('CX', j, k) for j in range(n) for k in range(n) if j != k]):
        table = []
        for v in range(1 << width):
            x, z = v & ((1 << n) - 1), v >> n
            xa, za = x >> a & 1, z >> a & 1
            if kind == 'H':
                sign = xa & za
                x ^= (xa ^ za) << a
                z ^= (xa ^ za) << a
            elif kind == 'S':
                sign = xa & za
                z ^= xa << a
            else:
                xb, zb = x >> b & 1, z >> b & 1
                sign = xa & zb & (xb ^ za ^ 1)
                x ^= xa << b
                z ^= zb << a
            table.append(x | (z << n) | (sign << width))
        result.append((kind, a, b, tuple(table)))
    return result


def adjoint(matrix):
    return [list(map(complex.conjugate, row)) for row in zip(*matrix)]


def matmul(a, b):
    return [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def pauli(n, v):
    d = 1 << n
    x, z = v & (d - 1), v >> n
    out = [[0j] * d for _ in range(d)]
    for y in range(d):
        out[y ^ x][y] = (1j ** ((x & z).bit_count())) * (-1) ** ((z & y).bit_count())
    return out


def validate_generator(n, entry):
    kind, a, b, table = entry
    d, signbit = 1 << n, 1 << (2 * n)
    g = [[0j] * d for _ in range(d)]
    denominator = 2 if kind == 'H' else 1
    for y in range(d):
        if kind == 'H':
            for bit in range(2):
                g[(y & ~(1 << a)) | (bit << a)][y] = complex((-1) ** (bit * (y >> a & 1)))
        elif kind == 'S':
            g[y][y] = 1j ** (y >> a & 1)
        else:
            g[y ^ ((y >> a & 1) << b)][y] = 1 + 0j
    for v, image in enumerate(table):
        actual = matmul(matmul(g, pauli(n, v)), adjoint(g))
        expected = pauli(n, image & (signbit - 1))
        factor = -denominator if image & signbit else denominator
        require(actual == [[factor * x for x in row] for row in expected],
                "literal generator conjugation/sign mismatch")


def signed_cliffords(n):
    width, signbit = 2 * n, 1 << (2 * n)
    mask = signbit - 1
    entries = generators(n)
    for entry in entries:
        validate_generator(n, entry)
    identity = tuple(range(signbit))
    seen, queue = {identity}, deque([identity])
    while queue:
        current = queue.popleft()
        for _, _, _, gen in entries:
            nxt = tuple(gen[v & mask] ^ (v & signbit) for v in current)
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    require(len(seen) == {1: 24, 2: 11520}[n], "projective Clifford group order")
    lifts = defaultdict(list)
    for table in seen:
        columns = tuple(table[1 << j] & mask for j in range(width))
        trace_adjoint = sum(-1 if image & signbit else 1
                            for v, image in enumerate(table) if image & mask == v)
        k = len(reduced(tuple(col ^ (1 << j) for j, col in enumerate(columns))))
        require(trace_adjoint in (0, 1 << (width - k)), "trace magnitude")
        lifts[columns].append(trace_adjoint)
    histogram, nonzero, zeros = Counter(), Counter(), 0
    for columns, values in lifts.items():
        k = len(reduced(tuple(col ^ (1 << j) for j, col in enumerate(columns))))
        require(len(values) == signbit, "Pauli fiber size")
        good = sum(v != 0 for v in values)
        require(good == 1 << k, "nonzero trace lifts")
        histogram[k] += 1
        nonzero[k] += good
        zeros += len(values) - good
    return set(lifts), histogram, nonzero, zeros


def subspaces(width):
    layer = {()}
    result = []
    for k in range(width + 1):
        result.extend(layer)
        layer = {basis for e in layer for v in range(1, 1 << width)
                 if len(basis := reduced(e + (v,))) == k + 1}
    return result


def forms(e, n):
    k = len(e)
    coordinates = [(i, j) for j in range(k) for i in range(j + 1)]
    for bits in range(1 << len(coordinates)):
        columns = [0] * k
        for b, (i, j) in enumerate(coordinates):
            value = bits >> b & 1
            columns[j] |= value << i
            if i != j:
                columns[i] |= (value ^ omega(e[i], e[j], n)) << j
        if len(reduced(columns)) == k:
            yield tuple(columns)


def reconstruct(e, b, n, wrong_transpose=False):
    inv = inverse(b if wrong_transpose else transpose(b))
    columns = []
    for j in range(2 * n):
        x = 1 << j
        rhs = sum(omega(x, w, n) << i for i, w in enumerate(e))
        a = apply(inv, rhs)
        require(all(((a & b[i]).bit_count() & 1) == omega(x, w, n)
                    for i, w in enumerate(e)), "residual reconstruction relation")
        columns.append(x ^ apply(e, a))
    return tuple(columns)


def residual_symplectics(n):
    found, counts = set(), Counter()
    spaces = subspaces(2 * n)
    require(len(spaces) == {1: 5, 2: 67}[n], "binary subspace inventory")
    for e in spaces:
        k = len(e)
        for b in forms(e, n):
            s = reconstruct(e, b, n)
            require(len(reduced(tuple(v ^ (1 << j) for j, v in enumerate(s)))) == k,
                    "displacement rank")
            require(all(omega(s[i], s[j], n) == omega(1 << i, 1 << j, n)
                        for i in range(2 * n) for j in range(2 * n)), "symplecticity")
            require(s not in found, "residual correspondence duplicate")
            found.add(s)
            counts[k] += 1
    return found, counts


def tail_upper(s, cutoff=5):
    require(isinstance(s, int) and s >= 0, "width increment must be nonnegative")
    require(cutoff >= 1, "positive tail cutoff")
    partial = sum((Q(1, 2 ** (k * (k + 1) // 2 + s * k))
                   for k in range(1, cutoff + 1)), Q(0))
    first = Q(1, 2 ** ((cutoff + 1) * (cutoff + 2) // 2 + s * (cutoff + 1)))
    ratio = Q(1, 2 ** (cutoff + 2 + s))
    return partial + first / (1 - ratio)


def check_sources():
    package = Path(__file__).resolve().parent
    root = package.parent.parent
    sources = json.loads((package / 'SOURCES.json').read_text())
    checked = 0
    for source in sources['files']:
        if source['usage'] == 'input':
            digest = sha256((root / source['path']).read_bytes()).hexdigest()
            require(digest == source['sha256'], "source digest: " + source['path'])
            checked += 1
    require(checked == 1, "expected one predecessor proof input")


def main():
    check_sources()
    evidence = {}
    for n in (1, 2):
        signed, counts, nonzero, zeros = signed_cliffords(n)
        residual, other_counts = residual_symplectics(n)
        require(signed == residual and counts == other_counts, "independent enumerations differ")
        for k, count in counts.items():
            require(count <= 2 ** (2 * n * k - k * (k - 1) // 2), "new rank count bound")
        row = sum((Q(count, 2 ** (k * (2 * n + 2)))
                   for k, count in nonzero.items() if k), Q(0))
        require(row < tail_upper(0) < Q(2, 3), "Gram row envelope")
        evidence[str(n)] = {'symplectic_rank_counts': dict(sorted(counts.items())),
                            'nonzero_trace_counts': dict(sorted(nonzero.items())),
                            'zero_trace_classes': zeros, 'row_sum_at_4n_plus_4': str(row)}
    lower = 1 - tail_upper(0)
    require(lower > Q(358367, 1000000), "sharper rational constant")
    require(tail_upper(2) < Q(3, 20) and tail_upper(6) < Q(1, 126), "later width comparison")
    require(all(tail_upper(s + 1) < tail_upper(s) for s in range(8)), "monotone envelope")

    # Failures exercise actual validation paths, and remain active under python -O.
    expect_failure(lambda: inverse((0,)), "singular residual accepted")
    expect_failure(lambda: reconstruct((1, 2), (3, 2), 1, wrong_transpose=True),
                   "B inverse used in place of B inverse transpose")
    h = generators(1)[0]
    bad_table = tuple(v & 3 for v in h[3])
    expect_failure(lambda: validate_generator(1, (*h[:3], bad_table)), "lost Y sign")
    expect_failure(lambda: require(nonzero[1] == counts[1], "missing Pauli lift factor"),
                   "missing Pauli lift multiplicity")
    expect_failure(lambda: tail_upper(-1), "width below sufficient threshold")
    print(json.dumps({'status': 'PASS_CLIFFORD_RESIDUAL_COUNT_BOUND',
                      'scope': 'finite corroboration for n=1,2; all-n proof in PROOF.md',
                      'enumeration': evidence, 'uniform_row_upper': str(tail_upper(0)),
                      'uniform_gram_lower': str(lower), 'negative_controls': 5},
                     indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
