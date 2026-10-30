#!/usr/bin/env python3
"""Bounded literal corroboration of the common scalar pivot theorem."""
from collections import Counter, deque
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import random


def require(ok, message):
    if not ok:
        raise ValueError(message)


class Ring:
    """A product of k copies of F_p[e]/e^ell, within fixed replay bounds."""

    def __init__(self, p, ell, k):
        require(p in (2, 3) and ell in (1, 2) and 1 <= k <= 3, 'ring bounds')
        self.p, self.ell, self.k = p, ell, k
        self.size = p ** ell
        self.zero, self.one = (0,) * k, (1,) * k
        self.add_table = tuple(tuple(self.local_add(a, b) for b in range(self.size))
                               for a in range(self.size))
        self.mul_table = tuple(tuple(self.local_mul(a, b) for b in range(self.size))
                               for a in range(self.size))
        self.neg_table = tuple(self.local_add(0, -a % p) if ell == 1 else
                               (-a % p) + p * (-(a // p) % p)
                               for a in range(self.size))
        self.inv_table = {}
        for a in range(self.size):
            if a % p:
                candidates = [b for b in range(self.size) if self.mul_table[a][b] == 1]
                require(len(candidates) == 1, 'local inverse')
                self.inv_table[a] = candidates[0]

    def local_add(self, a, b):
        return (a + b) % self.p if self.ell == 1 else (
            (a % self.p + b % self.p) % self.p
            + self.p * ((a // self.p + b // self.p) % self.p))

    def local_mul(self, a, b):
        if self.ell == 1:
            return a * b % self.p
        return ((a % self.p) * (b % self.p) % self.p
                + self.p * ((a // self.p * (b % self.p)
                             + b // self.p * (a % self.p)) % self.p))

    def scalar(self, a):
        return (a % self.p,) * self.k

    def add(self, a, b):
        return tuple(self.add_table[x][y] for x, y in zip(a, b, strict=True))

    def neg(self, a):
        return tuple(self.neg_table[x] for x in a)

    def mul(self, a, b):
        return tuple(self.mul_table[x][y] for x, y in zip(a, b, strict=True))

    def unit(self, a):
        return all(x % self.p for x in a)

    def inv(self, a):
        require(self.unit(a), 'nonunit inverse')
        return tuple(self.inv_table[x] for x in a)


def ident(r, n):
    return tuple(tuple(r.one if i == j else r.zero for j in range(n))
                 for i in range(n))


def scalar_matrix(r, a):
    return tuple(tuple(r.scalar(x) for x in row) for row in a)


def mm(r, a, b):
    n = len(a)
    require(1 <= n <= 4 and len(b) == n, 'matrix dimension')
    out = []
    for i in range(n):
        row = []
        for j in range(n):
            value = r.zero
            for h in range(n):
                value = r.add(value, r.mul(a[i][h], b[h][j]))
            row.append(value)
        out.append(tuple(row))
    return tuple(out)


def inverse(r, a):
    """Componentwise inversion is internal arithmetic, never a free map."""
    n = len(a)
    require(1 <= n <= 4, 'inverse dimension')
    components = []
    for c in range(r.k):
        rows = [[a[i][j][c] for j in range(n)]
                + [int(i == j) for j in range(n)] for i in range(n)]
        for j in range(n):
            pivot = next((i for i in range(j, n) if rows[i][j] % r.p), None)
            require(pivot is not None, 'singular component')
            rows[j], rows[pivot] = rows[pivot], rows[j]
            v = r.inv_table[rows[j][j]]
            rows[j] = [r.mul_table[v][x] for x in rows[j]]
            for i in range(n):
                if i != j:
                    v = rows[i][j]
                    rows[i] = [r.add_table[x][r.neg_table[r.mul_table[v][y]]]
                               for x, y in zip(rows[i], rows[j], strict=True)]
        components.append(rows)
    return tuple(tuple(tuple(components[c][i][n+j] for c in range(r.k))
                       for j in range(n)) for i in range(n))


def rref(rows, p, n):
    a = [list(row) for row in rows]
    require(len(a) <= 24 and n <= 4, 'scalar system bounds')
    pivots = []
    for j in range(n):
        h = len(pivots)
        pivot = next((i for i in range(h, len(a)) if a[i][j] % p), None)
        if pivot is None:
            continue
        a[h], a[pivot] = a[pivot], a[h]
        scale = pow(a[h][j], -1, p)
        a[h] = [x * scale % p for x in a[h]]
        for i in range(len(a)):
            if i != h:
                v = a[i][j]
                a[i] = [(x-v*y) % p for x, y in zip(a[i], a[h], strict=True)]
        pivots.append(j)
    return a, pivots


def nullspace(rows, p, n):
    a, pivots = rref(rows, p, n)
    out = []
    for j in range(n):
        if j not in pivots:
            v = [int(h == j) for h in range(n)]
            for i, h in enumerate(pivots):
                v[h] = -a[i][j] % p
            out.append(tuple(v))
    return out


def extend(vectors, p, n):
    out = list(vectors)
    require(len(rref(out, p, n)[1]) == len(out), 'dependent scalar basis')
    for i in range(n):
        v = tuple(int(i == j) for j in range(n))
        if len(rref(out+[v], p, n)[1]) > len(out):
            out.append(v)
    require(len(out) == n, 'basis extension')
    return out


def mv(r, a, v):
    """Literal action, separate from matrix multiplication."""
    result = []
    for row in a:
        value = r.zero
        for coefficient, datum in zip(row, v, strict=True):
            value = r.add(value, r.mul(coefficient, datum))
        result.append(value)
    return tuple(result)


def common_flag(r, a):
    d = len(a)
    require(r.k <= r.p, 'too many local components')
    q = ident(r, d)
    residual = a
    for h in range(d):
        m = d-h
        phi = None
        for v in product(range(r.p), repeat=m):
            pivot = r.zero
            for j in range(m):
                pivot = r.add(pivot, r.mul(r.scalar(v[j]), residual[j][0]))
            if r.unit(pivot):
                phi = v
                break
        require(phi is not None, 'no common scalar pivot')
        rows = extend([phi], r.p, m)
        transform = [list(row) for row in ident(r, d)]
        for i in range(m):
            for j in range(m):
                transform[h+i][h+j] = r.scalar(rows[i][j])
        q = mm(r, tuple(tuple(row) for row in transform), q)
        if m > 1:
            s = mm(r, scalar_matrix(r, rows), residual)
            ai = r.inv(s[0][0])
            residual = tuple(tuple(r.add(s[i][j], r.neg(r.mul(
                r.mul(s[i][0], ai), s[0][j]))) for j in range(1, m))
                             for i in range(1, m))
    return q


def scalar_columns(r, m):
    n = len(m)
    equations = []
    for i in range(n):
        for c in range(r.k):
            if c:
                equations.append(tuple((m[i][j][c]-m[i][j][0]) % r.p
                                       for j in range(n)))
            if r.ell == 2:
                equations.append(tuple(m[i][j][c] // r.p for j in range(n)))
    return nullspace(equations, r.p, n)


def construct(r, m):
    n = len(m)
    require(1 <= n <= 4 and r.k <= r.p, 'constructor domain')
    inverse(r, m)  # Reject a singular target before choosing scalar charts.
    fixed = scalar_columns(r, m)
    images = []
    for v in fixed:
        image = mv(r, m, tuple(r.scalar(x) for x in v))
        require(all(x == r.scalar(x[0]) for x in image), 'nonscalar image')
        images.append(tuple(x[0] for x in image))
    hb, bb = extend(fixed, r.p, n), extend(images, r.p, n)
    h = scalar_matrix(r, tuple(zip(*hb, strict=True)))
    b = scalar_matrix(r, tuple(zip(*bb, strict=True)))
    left = inverse(r, b)
    target = mm(r, mm(r, left, m), h)
    s, d = len(fixed), n-len(fixed)
    if d:
        active = tuple(tuple(target[i][j] for j in range(s, n))
                       for i in range(s, n))
        q = common_flag(r, active)
        full = [list(row) for row in ident(r, n)]
        for i in range(d):
            for j in range(d):
                full[s+i][s+j] = q[i][j]
        left = mm(r, tuple(tuple(row) for row in full), left)
        target = mm(r, mm(r, left, m), h)
    prefix = ident(r, n)
    factors = []
    for j in range(s, n):
        column = tuple(r.add(target[i][j], r.neg(r.one if i == j else r.zero))
                       for i in range(n))
        u = mv(r, inverse(r, prefix), column)
        f = [list(row) for row in ident(r, n)]
        for i in range(n):
            f[i][j] = r.add(f[i][j], u[i])
        f = tuple(tuple(row) for row in f)
        prefix = mm(r, prefix, f)
        inverse(r, prefix)  # Check that the replacement prefix is invertible.
        factors.append(f)
    require(prefix == target, 'column reconstruction')
    return inverse(r, left), tuple(factors), inverse(r, h), d


def word_matrix(r, word):
    left, factors, right, _ = word
    out = left
    for f in factors:
        out = mm(r, out, f)
    return mm(r, out, right)


def check_word(r, m, word, basis=False):
    left, factors, right, d = word
    require(len(factors) == d and d <= len(m), 'paid length')
    for index, f in enumerate(factors):
        column = len(m)-d+index
        require(all(f[i][j] == (r.one if i == j else r.zero)
                    for i in range(len(m)) for j in range(len(m))
                    if j != column), 'illegal paid right vector')
    for free in (left, right):
        require(all(x == r.scalar(x[0]) for row in free for x in row),
                'componentwise free map')
    require(word_matrix(r, word) == m, 'literal word mismatch')
    if not basis:
        return 0
    count = 0
    for role in range(len(m)):
        for component in range(r.k):
            for degree in range(r.ell):
                data = [r.zero] * len(m)
                value = [0] * r.k
                value[component] = r.p ** degree
                data[role] = tuple(value)
                actual = mv(r, right, data)
                for f in reversed(factors):
                    actual = mv(r, f, actual)
                actual = mv(r, left, actual)
                require(actual == mv(r, m, data), 'basis action mismatch')
                count += 1
    return count


def bmul(a, b):
    return tuple((b[0] if row & 1 else 0) ^ (b[1] if row & 2 else 0)
                 ^ (b[2] if row & 4 else 0) for row in a)


def binary_group():
    identity = (1, 2, 4)
    group = tuple(a for a in product(range(8), repeat=3)
                  if len({((a[0]&x).bit_count() % 2)
                          | (((a[1]&x).bit_count() % 2) << 1)
                          | (((a[2]&x).bit_count() % 2) << 2)
                          for x in range(8)}) == 8)
    inverses = {a: next(b for b in group if bmul(a, b) == identity) for a in group}
    paid = set()
    for y in range(1, 8):
        factors = []
        for u in range(8):
            a = tuple(identity[i] ^ (y if u >> i & 1 else 0) for i in range(3))
            if a in inverses:
                factors.append(a)
        for a in factors:
            for b in factors:
                paid.add(bmul(inverses[a], b))
    distance = {identity: 0}
    queue = deque([identity])
    for _ in range(len(group)):
        require(bool(queue), 'BFS queue exhausted early')
        a = queue.popleft()
        for f in paid:
            b = bmul(f, a)
            if b not in distance:
                distance[b] = distance[a]+1
                queue.append(b)
    require(not queue and len(distance) == len(group), 'BFS coverage')
    for a in group:
        for f in paid:
            require(distance[bmul(f, a)] <= distance[a]+1, 'paid edge lower bound')
        for t in group:
            require(distance[bmul(bmul(inverses[t], a), t)] == distance[a],
                    'free conjugation distance')
    return group, inverses, distance, len(paid)


def binary_census():
    r = Ring(2, 1, 2)
    group, inverses, distance, generators = binary_group()
    require(len(group) == 168, 'binary group coverage')
    words = {}
    basis = 0
    for a in group:
        m = tuple(tuple((int(i == j), a[i] >> j & 1) for j in range(3))
                  for i in range(3))
        word = construct(r, m)
        require(word[3] == distance[a], 'independent BFS cost mismatch')
        basis += check_word(r, m, word, basis=True)
        words[a] = word
    histogram = Counter()
    for a in group:
        scalar = scalar_matrix(r, tuple(tuple(a[i] >> j & 1 for j in range(3))
                                        for i in range(3)))
        for b in group:
            relative = bmul(inverses[a], b)
            left, factors, right, d = words[relative]
            word = (mm(r, scalar, left), factors, right, d)
            m = tuple(tuple((a[i] >> j & 1, b[i] >> j & 1) for j in range(3))
                      for i in range(3))
            check_word(r, m, word)
            histogram[d] += 1
    return {'targets': sum(histogram.values()), 'cost_histogram': dict(histogram),
            'normalized_targets': len(words), 'basis_actions': basis,
            'normalized_paid_generators': generators}, r, words


def sampled_products():
    rng = random.Random(102209)
    records = []
    for p, ell, k in ((2, 2, 2), (3, 1, 3), (3, 2, 3)):
        r = Ring(p, ell, k)
        units = tuple(x for x in range(r.size) if x % p)
        for n in (3, 4):
            seen, hist, actions, scalar_tests = set(), Counter(), 0, 0
            for nominal in range(n+1):
                for _ in range(16):
                    m = ident(r, n)
                    for j in range(n-nominal, n):
                        f = [list(row) for row in ident(r, n)]
                        for i in range(n):
                            f[i][j] = tuple(rng.randrange(r.size) for _ in range(k))
                        f[j][j] = tuple(rng.choice(units) for _ in range(k))
                        m = mm(r, m, tuple(tuple(row) for row in f))
                    for _ in range(2*n):
                        i, j = rng.sample(range(n), 2)
                        f = [list(row) for row in ident(r, n)]
                        f[i][j] = r.scalar(rng.randrange(1, p))
                        f = tuple(tuple(row) for row in f)
                        m = mm(r, f, m) if rng.randrange(2) else mm(r, m, f)
                    if m in seen:
                        continue
                    seen.add(m)
                    word = construct(r, m)
                    actions += check_word(r, m, word, basis=True)
                    scalar_count = 0
                    for v in product(range(p), repeat=n):
                        image = mv(r, m, tuple(r.scalar(x) for x in v))
                        scalar_count += all(x == r.scalar(x[0]) for x in image)
                        scalar_tests += 1
                    require(scalar_count == p ** (n-word[3]), 'literal scalar subspace')
                    hist[word[3]] += 1
            records.append({'p': p, 'ell': ell, 'components': k, 'roles': n,
                            'targets': len(seen), 'cost_histogram': dict(hist),
                            'basis_actions': actions, 'scalar_input_tests': scalar_tests})
    return records


def rejected(call):
    try:
        call()
    except ValueError:
        return
    raise ValueError('negative control was accepted')


def controls(r, words):
    candidates = [word for word in words.values() if word[3] == 3]
    word = next(w for w in candidates
                if word_matrix(r, (w[0], tuple(reversed(w[1])), w[2], w[3]))
                != word_matrix(r, w))
    m = word_matrix(r, word)
    left, factors, right, d = word
    rejected(lambda: check_word(r, m, (left, factors[:-1], right, d)))
    rejected(lambda: check_word(r, m, (left, tuple(reversed(factors)), right, d)))
    changed = [list(row) for row in factors[0]]
    changed[0][0] = r.add(changed[0][0], (1, 0))
    bad = (tuple(tuple(row) for row in changed),) + factors[1:]
    rejected(lambda: check_word(r, m, (left, bad, right, d)))
    changed = [list(row) for row in left]
    changed[0][0] = r.add(changed[0][0], (1, 0))
    rejected(lambda: check_word(r, m, (tuple(tuple(row) for row in changed),
                                     factors, right, d)))
    singular = tuple((r.zero,) * 3 for _ in range(3))
    rejected(lambda: construct(r, singular))
    rejected(lambda: construct(Ring(2, 1, 3), ident(Ring(2, 1, 3), 3)))
    rejected(lambda: r.inv((0, 1)))
    illegal = [list(row) for row in ident(r, 3)]
    illegal[0][1], illegal[1][2] = r.one, r.one
    illegal = tuple(tuple(row) for row in illegal)
    rejected(lambda: check_word(r, illegal,
                               (ident(r, 3), (illegal,), ident(r, 3), 1)))
    # The binary kernels x=0 and y=0 cover coordinate choices, not x+y.
    a = (((1, 0), (0, 1)), ((0, 1), (1, 0)))
    require(not r.unit(a[0][0]) and not r.unit(a[1][0]), 'row conflict fixture')
    q = common_flag(r, a)
    require(r.unit(mm(r, q, a)[0][0]), 'non-coordinate scalar pivot')
    require(q != ident(r, 2), 'required scalar basis change')
    # The q+1 hyperplanes really can cover, so the component bound matters.
    require(all(x == 0 or y == 0 or x == y
                for x, y in product(range(2), repeat=2)), 'cover boundary')
    return 8


def main():
    census, ring, words = binary_census()
    samples = sampled_products()
    control_count = controls(ring, words)
    root = Path(__file__).resolve().parent
    hashes = {p.name: sha256(p.read_bytes()).hexdigest()
              for p in sorted(root.iterdir()) if p.is_file()}
    receipt = {'claim_type': 'scoped proof with finite corroboration',
               'binary_pair_census': census, 'samples': samples,
               'rejection_controls': control_count, 'boundary_fixtures': 2,
               'file_sha256': hashes}
    print(json.dumps(receipt, sort_keys=True))
    print('PASS_RIGHT_VECTOR_SMALL_LOCAL_PRODUCTS',
          f"binary_pairs={census['targets']}",
          f"sampled_targets={sum(x['targets'] for x in samples)}",
          f'controls={control_count}', 'no_new_kappa')


if __name__ == '__main__':
    main()
