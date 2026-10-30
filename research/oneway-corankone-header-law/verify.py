"""One-way coupled corank-one full guards; bounded, read-only exact checks."""

import hashlib
import itertools
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path


FIELDS = (2, 3, 5, 7)
PAIR_DOMAINS = ((2, 2), (2, 3), (2, 4), (2, 5), (2, 6),
                (3, 2), (3, 3), (3, 4), (5, 2), (5, 3))
HEADER_DOMAINS = ((2, 2), (2, 3), (2, 4), (3, 2), (3, 3), (5, 2))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def denominator(q, m):
    return (q**m - 1) * (q**m - q) * q ** (2 * m - 4)


def binary_count(m):
    need(2 <= m <= 64, "binary replay dimension")
    value = 9 ** (m - 1) - 5 ** (m - 1)
    need(value > 0 and value % 4 == 0, "positive integral binary count")
    return value // 4


def factor_weight(a, q):
    if not any(a):
        return 2 * q * q - 1
    return 0 if (a[0] * a[3] - a[1] * a[2]) % q else q - 1


def transfer(q, maximum, endpoint=(1, 1, 0, 1)):
    need(q in FIELDS and 2 <= maximum <= 64, "transfer replay domain")
    states = [a for a in itertools.product(range(q), repeat=4)
              if a[0] != 1 and a[3] != 1]
    increments = [(a, factor_weight(a, q))
                  for a in itertools.product(range(q), repeat=4)
                  if factor_weight(a, q)]
    index = {a: i for i, a in enumerate(states)}
    edges = [[] for _ in states]
    for i, a in enumerate(states):
        for delta, weight in increments:
            b = tuple((x + y) % q for x, y in zip(a, delta, strict=True))
            if b in index:
                edges[i].append((index[b], weight))
    final = [factor_weight(tuple((x - y) % q
                                for x, y in zip(endpoint, a, strict=True)), q)
             for a in states]
    current = [0] * len(states)
    current[index[(0, 0, 0, 0)]] = 1
    counts = {}
    for length in range(1, maximum):
        following = [0] * len(states)
        for i, count in enumerate(current):
            for j, weight in edges[i]:
                following[j] += count * weight
        current = following
        counts[length + 1] = sum(x * y for x, y in zip(current, final, strict=True))
    need(len(states) == q * q * (q - 1)**2, "safe-state cardinality")
    return counts


def local_weights(q):
    vectors = list(itertools.product(range(q), repeat=2))
    observed = Counter()
    for y in vectors:
        for x in vectors:
            observed[tuple(a * b % q for a in y for b in x)] += 1
    for a in itertools.product(range(q), repeat=4):
        need(observed[a] == factor_weight(a, q), "rank-one factor multiplicity")
    return len(vectors)**2


def dot(u, v, q):
    return sum(x * y for x, y in zip(u, v, strict=True)) % q


def scalar_guard(u, a, q):
    total = 0
    for i in range(len(u) - 1):
        total = (total + u[i] * a[i]) % q
        if total == 1:
            return False
    return True


def enumerate_pairs(q, m):
    need((q, m) in PAIR_DOMAINS, "pair census domain")
    vectors = list(itertools.product(range(q), repeat=m))
    total = good = single = 0
    for u in vectors[1:]:
        multiples = {tuple(c * x % q for x in u) for c in range(q)}
        for v in vectors:
            if v in multiples:
                continue
            left, right = [], []
            for row in vectors:
                values = (dot(row, u, q), dot(row, v, q))
                if values == (1, 1):
                    left.append(scalar_guard(u, row, q))
                elif values == (0, 1):
                    right.append(scalar_guard(v, row, q))
            need(len(left) == len(right) == q ** (m - 2), "YX=B row fibers")
            for first in left:
                for second in right:
                    total += 1
                    single += first
                    good += first and second
    need(total == denominator(q, m), "exhaustive pair count")
    return {"total": total, "joint": good, "single": single}


def inverse(matrix, q):
    n = len(matrix)
    rows = [list(row) + [int(i == j) for j in range(n)]
            for i, row in enumerate(matrix)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if rows[i][j]), None)
        if pivot is None:
            return None
        rows[j], rows[pivot] = rows[pivot], rows[j]
        unit = pow(rows[j][j], -1, q)
        rows[j] = [unit * x % q for x in rows[j]]
        for i in range(n):
            if i != j:
                c = rows[i][j]
                rows[i] = [(x - c * y) % q
                           for x, y in zip(rows[i], rows[j], strict=True)]
    need(all(rows[i][j] == int(i == j) for i in range(n) for j in range(n)),
         "inverse endpoint")
    return [row[n:] for row in rows]


def multiply(a, b, q):
    n = len(a)
    return [[sum(a[i][k] * b[k][j] for k in range(n)) % q
             for j in range(n)] for i in range(n)]


def full_guard(matrix, q):
    """Literal no-pivot elimination, independent of the scalar-prefix test."""
    rows = [list(row) for row in matrix]
    n = len(rows)
    for j in range(n - 1):
        if not rows[j][j]:
            return False
        unit = pow(rows[j][j], -1, q)
        for i in range(j + 1, n):
            c = rows[i][j] * unit % q
            for k in range(j, n):
                rows[i][k] = (rows[i][k] - c * rows[j][k]) % q
    return True


def canonical_requests(m, q):
    identity = [[int(i == j) for j in range(m)] for i in range(m)]
    u = [[int(i == 0 and j in (0, 1)) for j in range(m)] for i in range(m)]
    v = [[int(i == j == 1) for j in range(m)] for i in range(m)]
    need(multiply(u, u, q) == u and multiply(v, v, q) == v, "idempotents")
    need(not any(x for row in multiply(v, u, q) for x in row), "VU=0")
    need(any(x for row in multiply(u, v, q) for x in row), "UV nonzero")
    return [[[(identity[i][j] - kernel[i][j]) % q for j in range(m)]
             for i in range(m)] for kernel in (u, v)]


def gl_size(q, m):
    value = 1
    for i in range(m):
        value *= q**m - q**i
    return value


def enumerate_headers(q, m):
    need((q, m) in HEADER_DOMAINS, "header census domain")
    requests = canonical_requests(m, q)
    fibers = Counter()
    total = good = single = first_only = 0
    for flat in itertools.product(range(q), repeat=m * m):
        g = [flat[i * m:(i + 1) * m] for i in range(m)]
        gi = inverse(g, q)
        if gi is None:
            continue
        transformed = [multiply(multiply(g, r, q), gi, q) for r in requests]
        flags = [full_guard(r, q) for r in transformed]
        total += 1
        good += all(flags)
        single += flags[0]
        first_only += all(r[0][0] != 0 for r in transformed)
        x = tuple(g[i][j] for i in range(m) for j in range(2))
        y = tuple((gi[0][i] + gi[1][i]) % q for i in range(m)) + tuple(gi[1])
        fibers[x + y] += 1
    need(total == gl_size(q, m), "complete GL domain")
    need(len(fibers) == denominator(q, m), "all normalized-pair fibers")
    need(set(fibers.values()) == {gl_size(q, m - 2)}, "equal header fibers")
    return {"total": total, "joint": good, "single": single,
            "first_only": first_only, "fibers": len(fibers)}


def check_binary(counts):
    for m, count in counts.items():
        n = m - 1
        need(count == binary_count(m), "binary closed form")
        orthogonal = (9**n - 2 * 7**n + 5**n) // 4
        need(count - orthogonal == (7**n - 5**n) // 2 > 0, "strict coupling gain")
        joint = Fraction(count, denominator(2, m))
        marginal = Fraction(3**n, (2**m - 1) * 2**n)
        ratio = Fraction(2**m - 1, 2**m - 2) * (1 - Fraction(5, 9)**n)
        need(joint / marginal**2 == ratio < 1, "negative correlation")
    return len(counts)


def controls(transfers, headers):
    good = transfers[2][3]
    wrong_orthogonal = (9**2 - 2 * 7**2 + 5**2) // 4
    wrong_parity = (9**2 + 2 * 7**2 + 5**2) // 4
    wrong_zero_weight = (3**2 - (-1)**2) // 4
    need(good not in (wrong_orthogonal, wrong_parity, wrong_zero_weight),
         "coupling, parity and zero-weight controls")
    marginal = Fraction(9, 28)
    need(Fraction(good, denominator(2, 3)) != marginal**2, "independence control")
    need(headers['2,3']['first_only'] > headers['2,3']['joint'],
         "first-only admission control")
    need(Fraction(transfers[2][2], denominator(2, 2)) == Fraction(1, 6),
         "one-way m=2 boundary")
    return 5


def bindings(package):
    root = package.parents[1]
    sources = json.loads((package / 'SOURCES.json').read_text())
    result = {}
    for row in sources['files']:
        if row['usage'] == 'input':
            digest = hashlib.sha256((root / row['path']).read_bytes()).hexdigest()
            need(digest == row['sha256'], 'source binding: ' + row['path'])
            result[row['path']] = digest
    for path in sorted(package.iterdir()):
        if path.is_file():
            result[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def main():
    package = Path(__file__).resolve().parent
    hashes = bindings(package)
    transfers = {q: transfer(q, 64 if q == 2 else 8) for q in FIELDS}
    weights = {q: local_weights(q) for q in FIELDS}
    pairs, headers = {}, {}
    for q, m in PAIR_DOMAINS:
        row = enumerate_pairs(q, m)
        need(row['joint'] == transfers[q][m], "pair census vs transfer")
        marginal = Fraction((q*q - q + 1)**(m - 1) * (q - 1),
                            (q**m - 1) * q**(m - 1))
        need(Fraction(row['single'], row['total']) == marginal, "PR4227 marginal")
        pairs[f'{q},{m}'] = row
    for q, m in HEADER_DOMAINS:
        row = enumerate_headers(q, m)
        pair = pairs[f'{q},{m}']
        need(Fraction(row['joint'], row['total']) ==
             Fraction(pair['joint'], pair['total']), "literal matrix guard census")
        need(Fraction(row['single'], row['total']) ==
             Fraction(pair['single'], pair['total']), "literal marginal census")
        headers[f'{q},{m}'] = row
    for q in FIELDS:
        value = Fraction(transfers[q][2], denominator(q, 2))
        need(value == Fraction((q - 1)**3 + 1, q*q*(q + 1)), "PR4240 one-sided boundary")
    result = {"pairs": pairs, "headers": headers, "local_factorizations": weights,
              "transfer_cases": sum(len(x) for x in transfers.values()),
              "binary_cases": check_binary(transfers[2]),
              "controls": controls(transfers, headers), "sha256": hashes}
    print('PASS_ONEWAY_CORANKONE_HEADER_LAW ' + json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
