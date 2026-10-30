#!/usr/bin/env python3
"""Bounded exact corroboration of README.md; no new kappa.

lee-phys, with substantial OpenAI Codex assistance; Apache-2.0.
The ring interpreter and bidirectional search adapt the credited #5259/#5514
verifiers. No predecessor package is imported or needed at runtime.
"""
from dataclasses import dataclass
from fractions import Fraction
from heapq import heappop, heappush
from itertools import permutations, product
from math import lcm
import json


def require(test, message):
    if not test:
        raise RuntimeError(message)


@dataclass(frozen=True)
class Ring:
    name: str
    n: int
    one: int
    add: tuple
    mul: tuple

    def neg(self, x):
        return self.add[x].index(0)

    def inv(self, x):
        return self.mul[x].index(self.one)


def ring_from_functions(name, n, one, add, mul):
    return Ring(name, n, one,
                tuple(tuple(add(x, y) for y in range(n)) for x in range(n)),
                tuple(tuple(mul(x, y) for y in range(n)) for x in range(n)))


def truncated_polynomials(modulus, variables):
    # Constant plus independent variables, with every variable product zero.
    # Modulus 4 retains 2*x != 0 and a non-square-zero maximal ideal.
    width = variables+1

    def digits(x):
        return tuple((x//modulus**k) % modulus for k in range(width))

    def add(x, y):
        a, b = digits(x), digits(y)
        return sum(((a[k]+b[k]) % modulus)*modulus**k for k in range(width))

    def mul(x, y):
        a, b = digits(x), digits(y)
        return (a[0]*b[0]) % modulus + sum(
            ((a[0]*b[k]+a[k]*b[0]) % modulus)*modulus**k for k in range(1, width))

    return ring_from_functions(f'Z/{modulus}[{variables} variables]/(variables)^2',
                               modulus**width, 1, add, mul)


def check_ring(r):
    es = range(r.n)
    require(r.one != 0, 'nonzero ring')
    for a, b in product(es, repeat=2):
        require(r.add[a][b] in es and r.mul[a][b] in es, 'closure')
        require(r.add[a][b] == r.add[b][a] and r.mul[a][b] == r.mul[b][a], 'commutativity')
    for a in es:
        require(r.add[a][0] == a and r.mul[a][r.one] == a and r.mul[a][0] == 0, 'identities')
        require(r.add[a][r.neg(a)] == 0, 'additive inverse')
    for a, b, c in product(es, repeat=3):
        require(r.add[r.add[a][b]][c] == r.add[a][r.add[b][c]], 'addition associativity')
        require(r.mul[r.mul[a][b]][c] == r.mul[a][r.mul[b][c]], 'multiplication associativity')
        require(r.mul[a][r.add[b][c]] == r.add[r.mul[a][b]][r.mul[a][c]], 'distributivity')


def local_data(r):
    radical = tuple(x for x in range(r.n) if r.one not in r.mul[x])
    m = set(radical)
    if r.one in m or any(r.add[x][y] not in m for x in m for y in m) or any(
            r.mul[x][y] not in m for x in m for y in range(r.n)):
        raise ValueError('the finite ring must be local')
    generators = {r.mul[x][y] for x in m for y in m}
    square = {0}
    for g in generators:
        principal = {r.mul[a][g] for a in range(r.n)}
        square = {r.add[x][y] for x in square for y in principal}
    covered, representatives = set(), []
    for x in range(r.n):
        if x not in covered:
            representatives.append(x)
            covered.update(r.add[x][y] for y in m)
    return radical, frozenset(square), tuple(representatives)


def validate_demand(r, d, data):
    m, square, representatives = data
    if len(d) != 3 or any(x not in m for x in d):
        raise ValueError('three demands in the maximal ideal required')
    for coefficients in product(representatives, repeat=3):
        if coefficients == (0, 0, 0):
            continue
        value = 0
        for a, x in zip(coefficients, d):
            value = r.add[value][r.mul[a][x]]
        if value in square:
            raise ValueError('demand classes must be independent modulo m^2')


def formula(mu, c):
    if len(mu) != 3 or len(c) != 3 or min((*mu, *c)) <= 0:
        raise ValueError('six strictly positive prices required')
    values = [sum(mu)]
    for k in range(3):
        i, j = [r for r in range(3) if r != k]
        values.append(2*mu[k]+2*c[i]+2*c[j])
        values.append(mu[i]+mu[j]+min(mu[i], mu[j])+2*c[k])
    return min(values)


def patterns():
    out = [('D', 0, 1, 2, (1, 1, 1, 0, 0, 0))]
    for i in range(3):
        j, k = [r for r in range(3) if r != i]
        v = [0]*6
        v[i], v[3+j], v[3+k] = 2, 2, 2
        out.append(('T', i, j, k, tuple(v)))
    for i, j, k in permutations(range(3)):
        v = [0]*6
        v[i], v[j], v[3+k] = 2, 1, 2
        out.append(('R', i, j, k, tuple(v)))
    return out


def construct(r, d, pattern):
    mode, i, j, k, _ = pattern
    if mode == 'D':
        return [(t, 3, d[t]) for t in range(3)]
    u = r.add[d[i]][r.neg(r.one)]
    if mode == 'T':
        a = r.mul[d[k]][r.inv(u)]
        return [(j, i, r.neg(d[j])), (i, 3, r.one), (j, i, d[j]),
                (k, i, r.neg(a)), (i, 3, u), (k, i, a)]
    if mode == 'R':
        return [(k, i, r.neg(d[k])), (i, 3, r.one), (k, i, d[k]),
                (i, 3, u), (j, 3, d[j])]
    raise ValueError('unknown construction')


def inverse(r, word):
    return [(i, j, r.neg(a)) for i, j, a in reversed(word)]


def execute(r, word, entry):
    out = list(entry)
    for i, j, a in word:
        out[i] = r.add[out[i]][r.mul[a][out[j]]]
    return tuple(out)


def target(r, d, entry):
    return tuple(r.add[entry[i]][r.mul[d[i]][entry[3]]] for i in range(3))+(entry[3],)


def endpoint(r, d, word):
    rev = inverse(r, word)
    for k in range(4):
        entry = tuple(r.one if j == k else 0 for j in range(4))
        want = target(r, d, entry)
        if execute(r, word, entry) != want or execute(r, rev, want) != entry:
            return False
    return True


def counts(word):
    return tuple(sum(i == k and j == 3 for i, j, _ in word) for k in range(3))+tuple(
        sum(i == k and j != 3 for i, j, _ in word) for k in range(3))


def bill(word, prices):
    return sum(prices[i if j == 3 else 3+i] for i, j, _ in word)


# Independent R16 arithmetic: four 4-bit coefficients per 16-bit row.
# Multiplying the constant-bit mask by a radical digit cannot carry across
# 4-bit lanes. No coordinate ring tables, constructors or formula are used.
def packed_product(a, row):
    return (row if a & 1 else 0) ^ ((a & 14)*(row & 0x1111))


def neighbors(state, weights):
    rows = [(state >> (16*i)) & 65535 for i in range(3)]
    for i in range(3):
        for a in range(1, 16):
            yield state ^ (a << (16*i+12)), weights[i], (i, 3, a)
        for j in range(3):
            if j != i:
                for a in range(1, 16):
                    yield state ^ (packed_product(a, rows[j]) << (16*i)), weights[3+i], (i, j, a)


def oracle(demand, prices):
    scale = lcm(*(Fraction(x).denominator for x in prices))
    weights = tuple(int(Fraction(x)*scale) for x in prices)
    require(min(weights) > 0, 'positive oracle weights')
    start = 1 | (16 << 16) | (256 << 32)
    goal = start | sum(x << (16*i+12) for i, x in enumerate(demand))
    ds = [{start: 0}, {goal: 0}]
    qs = [[(0, start)], [(0, goal)]]
    ps = [{start: None}, {goal: None}]
    best, meet = None, None
    settled = [0, 0]
    while qs[0] and qs[1]:
        for s in (0, 1):
            while qs[s] and qs[s][0][0] != ds[s][qs[s][0][1]]:
                heappop(qs[s])
        if not qs[0] or not qs[1]:
            break
        if best is not None and qs[0][0][0]+qs[1][0][0] >= best:
            break
        s = int(qs[1][0][0] < qs[0][0][0])
        du, u = heappop(qs[s])
        settled[s] += 1
        require(sum(settled) <= 50000 and len(ds[0])+len(ds[1]) <= 1000000,
                'oracle resource guard; query not certified')
        for v, cost, gate in neighbors(u, weights):
            dv = du+cost
            if v not in ds[s] or dv < ds[s][v]:
                ds[s][v] = dv
                ps[s][v] = (u, gate)
                heappush(qs[s], (dv, v))
                if v in ds[1-s]:
                    candidate = dv+ds[1-s][v]
                    if best is None or candidate < best:
                        best, meet = candidate, v
    require(meet is not None, 'oracle endpoints disconnected')
    forward, back = [], []
    u = meet
    while ps[0][u] is not None:
        u, gate = ps[0][u]
        forward.append(gate)
    u = meet
    while ps[1][u] is not None:
        u, gate = ps[1][u]
        back.append(gate)  # All nonzero-coefficient primitives are involutions here.
    return Fraction(best, scale), list(reversed(forward))+back, settled


def main():
    r16, r81, r64 = truncated_polynomials(2, 3), truncated_polynomials(3, 3), truncated_polynomials(4, 2)
    pats = patterns()
    vectors = [p[-1] for p in pats]
    require(len(vectors) == len(set(vectors)) == 10, 'ten distinct envelope vectors')
    total = dict(demands=0, words=0, formal_forward_inverse=0, literal_forward_inverse=0,
                 exposed_vectors=0, controls=0, oracle_queries=0, oracle_settled=0)
    fixtures = []
    for r, expected in ((r16, 168), (r81, 11232), (r64, 10752)):
        check_ring(r)
        data = local_data(r)
        accepted = 0
        for d in product(data[0], repeat=3):
            try:
                validate_demand(r, d, data)
            except ValueError:
                continue
            accepted += 1
            for pat in pats:
                word = construct(r, d, pat)
                require(all(a != 0 and i != j for i, j, a in word), 'nonzero legal gates')
                require(endpoint(r, d, word), 'constructed dirt endpoint/inverse')
                require(counts(word) == pat[-1], 'claimed counts')
                total['words'] += 1
                total['formal_forward_inverse'] += 8
        require(accepted == expected, 'exhaustive independent-class triple count')
        total['demands'] += accepted
        fixtures.append(dict(ring=r.name, independent_triples=accepted, maximal_ideal=len(data[0]),
                             square_ideal=len(data[1]), residue_field=len(data[2])))
        print('CHECK_RING', r.n, accepted, flush=True)

    d = (2, 4, 14)
    words = [construct(r16, d, p) for p in pats]
    for word in words:
        rev = inverse(r16, word)
        for entry in product(range(16), repeat=4):
            want = target(r16, d, entry)
            require(execute(r16, word, entry) == want and execute(r16, rev, want) == entry,
                    'literal R16 forward/inverse')
            total['literal_forward_inverse'] += 2

    representative_prices = [(1,1,1,1,1,1), (1,3,3,1,1,1), (1,2,5,1,2,1)]
    exposed = set()
    for prices in representative_prices:
        for perm in permutations(range(3)):
            p = tuple(prices[i] for i in perm)+tuple(prices[3+i] for i in perm)
            costs = [bill(word, p) for word in words]
            minimum = min(costs)
            require(costs.count(minimum) == 1, 'strict positive-price exposure')
            require(minimum == formula(p[:3], p[3:]), 'compressed envelope')
            exposed.add(costs.index(minimum))
    require(len(exposed) == 10, 'all ten terms strictly exposed')
    total['exposed_vectors'] = len(exposed)
    for mu, c in product(range(1, 13), repeat=2):
        require(formula((mu,)*3, (c,)*3) == min(3*mu, 2*mu+4*c), 'uniform-price specialization')

    # The lower rank zero-sum triple admits a cheaper predecessor M word.
    rank_two = (2,4,6)
    old_word = [(0,1,1), (2,0,1), (0,3,6), (1,3,4), (2,0,1), (0,1,1)]
    prices = (3,5,10,1,3,2)
    require(endpoint(r16, rank_two, old_word), 'rank-two predecessor word')
    require(bill(old_word, prices) == 14 < formula(prices[:3], prices[3:]) == 15,
            'rank-three hypothesis is essential')
    total['controls'] += 1
    for bad, fragment in [((0,4,14), 'independent'), (rank_two, 'independent'),
                           ((1,4,14), 'maximal ideal')]:
        try:
            validate_demand(r16, bad, local_data(r16))
        except ValueError as error:
            require(fragment in str(error), 'correct hypothesis rejection')
            total['controls'] += 1
        else:
            raise RuntimeError('accepted demand outside theorem')
    nonlocal_ring = ring_from_functions('F2 x F2', 4, 3, lambda x,y: x ^ y, lambda x,y: x & y)
    check_ring(nonlocal_ring)
    try:
        local_data(nonlocal_ring)
    except ValueError:
        total['controls'] += 1
    else:
        raise RuntimeError('accepted nonlocal ring')
    corrupt = words[1][1:]
    require(execute(r16, corrupt, (0,0,0,1)) == (*d,1), 'dirty-only corruption premise')
    require(not endpoint(r16, d, corrupt), 'missing preparation must fail on dirt')
    total['controls'] += 1
    d81 = (3,9,39)
    bad_sign = construct(r81, d81, pats[1])
    i, j, a = bad_sign[0]
    bad_sign[0] = (i, j, r81.neg(a))
    require(not endpoint(r81, d81, bad_sign), 'odd-characteristic sign control')
    total['controls'] += 1
    d64 = (4,2,22)
    bad_inverse = construct(r64, d64, pats[1])
    bad_inverse[3], bad_inverse[5] = (2,0,r64.neg(d64[2])), (2,0,d64[2])
    require(not endpoint(r64, d64, bad_inverse), 'unit inverse is necessary when m^2 is nonzero')
    total['controls'] += 1
    relator = [(0,1,1), (1,2,1), (0,1,1), (1,2,1), (0,2,1)]
    require(endpoint(r16, (0,0,0), relator), 'three-row identity control')
    require(sum((i,j) == (0,2) for i,j,_ in relator) == 1, 'row-return lemma is not per edge')
    total['controls'] += 1
    for bad_prices in [(0,1,1,1,1,1), (1,1,1,-1,1,1)]:
        try:
            formula(bad_prices[:3], bad_prices[3:])
        except ValueError:
            total['controls'] += 1
        else:
            raise RuntimeError('accepted nonpositive prices')

    for a in range(16):
        for row in range(65536):
            expected = sum(r16.mul[a][(row >> (4*k)) & 15] << (4*k) for k in range(4))
            require(packed_product(a, row) == expected, 'independent packed arithmetic')
    cases = [('D', (1,1,1,1,1,1)), ('T', (1,10,10,10,1,1)),
             ('R', (1,2,10,10,10,1)),
             ('rational', (Fraction(1,2),Fraction(2,3),Fraction(3,4),
                           Fraction(1),Fraction(4,3),Fraction(5,4)))]
    results = []
    for name, prices in cases:
        value, path, settled = oracle(d, prices)
        require(value == formula(prices[:3], prices[3:]), f'oracle mismatch: {name}')
        require(endpoint(r16, d, path) and bill(path, prices) == value, 'oracle path replay and bill')
        total['oracle_queries'] += 1
        total['oracle_settled'] += sum(settled)
        results.append(dict(case=name, optimum=str(value), settled=settled))
        print('CHECK_ORACLE', name, str(value), settled, flush=True)
    print(json.dumps(dict(fixtures=fixtures, counts=total, oracle=results), sort_keys=True))
    print('PASS_R16_RADICAL_TRIPLE_FANOUT no_new_kappa')


if __name__ == '__main__':
    main()
